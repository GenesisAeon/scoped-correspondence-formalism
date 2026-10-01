"""Decoders and hierarchical comparison (Paket ON4, plan §7.1, §7.5).

Readout and conclusion are separate from the system: a score drop is not
information loss (ON-C09), accuracy without balance hides a constant decoder
(ON-C10), a single affine threshold cannot solve XOR (ON-C13).

Protocol rules enforced here:
- every preprocessing step (standardisation) is fitted on TRAINING trials only;
  train and test trial IDs must be disjoint (ON-C20);
- the unit of replication is the PREPARATION / simulation run, not the trial:
  group statistics use one summary value per preparation (ON-C17);
- the group comparison uses an exact sign-flip test over preparation-level
  differences (ON-C18) and reports the mean difference with its own scope
  (ON-C19). No universal threshold, no "trios win" default.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, Hashable, List, Optional, Sequence, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError


# --- scores -------------------------------------------------------------

def accuracy(y_true: Sequence, y_pred: Sequence) -> float:
    if len(y_true) != len(y_pred) or not y_true:
        raise ScopeViolationError("need equally long, non-empty label sequences")
    return sum(int(a == b) for a, b in zip(y_true, y_pred)) / len(y_true)


def balanced_accuracy(y_true: Sequence, y_pred: Sequence) -> float:
    classes = sorted(set(y_true))
    if len(classes) < 2:
        raise ScopeViolationError("balanced accuracy needs at least two classes in the test set")
    recalls = []
    for c in classes:
        idx = [i for i, t in enumerate(y_true) if t == c]
        recalls.append(sum(int(y_pred[i] == c) for i in idx) / len(idx))
    return sum(recalls) / len(recalls)


# --- decoders (fitted on training data only) ----------------------------

@dataclass
class Standardiser:
    mean: np.ndarray
    scale: np.ndarray

    @classmethod
    def fit(cls, X: np.ndarray) -> "Standardiser":
        X = np.asarray(X, dtype=float)
        s = X.std(axis=0)
        return cls(X.mean(axis=0), np.where(s > 0, s, 1.0))

    def transform(self, X):
        return (np.asarray(X, dtype=float) - self.mean) / self.scale


@dataclass
class NearestMeanDecoder:
    """Nearest class mean after standardisation fitted on training trials."""
    std: Standardiser = None
    means: Dict[Hashable, np.ndarray] = field(default_factory=dict)

    def fit(self, X, y):
        X = np.asarray(X, dtype=float)
        if X.ndim != 2 or len(X) != len(y) or not np.all(np.isfinite(X)):
            raise ScopeViolationError("training features must be a finite (n, d) matrix")
        if len(set(y)) < 2:
            raise ScopeViolationError("training needs both classes")
        self.std = Standardiser.fit(X)
        Z = self.std.transform(X)
        self.means = {c: Z[[i for i, t in enumerate(y) if t == c]].mean(axis=0) for c in sorted(set(y))}
        return self

    def predict(self, X):
        Z = self.std.transform(X)
        keys = list(self.means)
        return [keys[int(np.argmin([np.sum((z - self.means[k]) ** 2) for k in keys]))] for z in Z]


class ConstantDecoder:
    def __init__(self, label):
        self.label = label

    def predict(self, X):
        return [self.label] * len(X)


def best_single_affine_threshold_accuracy_xor(grid: Sequence[int] = range(-3, 4)) -> Fraction:
    """Best accuracy of a single affine threshold sign(a x + b y + c) on the
    four XOR points (integer coefficient scan; the impossibility of 1 is
    proved in the roadmap)."""
    pts = {(0, 0): 0, (1, 1): 0, (0, 1): 1, (1, 0): 1}
    best = 0
    for a, b, c in itertools.product(grid, grid, grid):
        for sign in (1, -1):
            best = max(best, sum(int(int(sign * (a * x + b * y + c) > 0) == lab) for (x, y), lab in pts.items()))
    return Fraction(best, 4)


def xor_feature_decoder(r1: int, r2: int) -> int:
    """Threshold on the non-linear feature r1 + r2 - 2 r1 r2."""
    return int(r1 + r2 - 2 * r1 * r2 > 0)


# --- protocol -----------------------------------------------------------

def check_split(train_ids: Sequence[Hashable], test_ids: Sequence[Hashable]) -> None:
    overlap = set(train_ids) & set(test_ids)
    if overlap:
        raise ScopeViolationError(f"train/test leakage: trial ids {sorted(map(str, overlap))[:5]} in both sets")


@dataclass(frozen=True)
class SplitEvaluation:
    decoder_mode: str  # "refitted" | "frozen"
    n_train: int
    n_test: int
    accuracy: float
    balanced_accuracy: float


def evaluate_split(train_ids: Sequence[Hashable], X_train, y_train, test_ids: Sequence[Hashable], X_test, y_test,
                   *, frozen: Optional[NearestMeanDecoder] = None) -> SplitEvaluation:
    """Production split: refuses overlapping trial ids, then fits the
    standardiser and decoder on the training trials ONLY (or applies a frozen
    decoder unchanged) and scores the test trials."""
    check_split(train_ids, test_ids)
    if len(train_ids) != len(X_train) or len(test_ids) != len(X_test):
        raise ScopeViolationError("trial ids must match the feature rows")
    dec = frozen if frozen is not None else NearestMeanDecoder().fit(X_train, y_train)
    pred = dec.predict(X_test)
    return SplitEvaluation("frozen" if frozen is not None else "refitted", len(X_train), len(X_test),
                           accuracy(y_test, pred), balanced_accuracy(y_test, pred))


def preparation_summaries(trial_scores: Dict[Hashable, Sequence[float]]) -> Dict[Hashable, float]:
    """One summary (mean over trials) per preparation; trials are NOT units."""
    if not trial_scores:
        raise ScopeViolationError("no preparations")
    return {p: float(np.mean(v)) for p, v in trial_scores.items() if len(v)}


def group_mean_and_sem2(values: Sequence) -> Tuple:
    n = len(values)
    if n < 2:
        raise ScopeViolationError("need at least two preparations per group")
    m = sum(values) / n
    s2 = sum((v - m) ** 2 for v in values) / (n - 1)
    return m, s2 / n


def sign_flip_test(differences: Sequence) -> Fraction:
    """Exact two-sided sign-flip p-value for paired preparation-level
    differences (all 2^n sign patterns; n <= 20)."""
    n = len(differences)
    if n == 0 or n > 20:
        raise ScopeViolationError("sign-flip test needs 1..20 preparation-level differences")
    obs = abs(sum(differences))
    hits = sum(1 for signs in itertools.product((1, -1), repeat=n) if abs(sum(s * d for s, d in zip(signs, differences))) >= obs)
    return Fraction(hits, 2 ** n)


@dataclass(frozen=True)
class GroupComparison:
    group_a: str
    group_b: str
    n_a: int
    n_b: int
    mean_a: float
    mean_b: float
    difference: float
    sem2_a: float
    sem2_b: float
    unit: str = "preparation"
    scope: str = "this decoder, window, observation and preparation set only"


def compare_groups(name_a: str, prep_a: Dict[Hashable, float], name_b: str, prep_b: Dict[Hashable, float]) -> GroupComparison:
    if set(prep_a) & set(prep_b):
        raise ScopeViolationError("a preparation cannot belong to both groups")
    ma, sa = group_mean_and_sem2(list(prep_a.values()))
    mb, sb = group_mean_and_sem2(list(prep_b.values()))
    return GroupComparison(name_a, name_b, len(prep_a), len(prep_b), ma, mb, ma - mb, sa, sb)


__all__ = ["accuracy", "balanced_accuracy", "Standardiser", "NearestMeanDecoder", "ConstantDecoder",
           "best_single_affine_threshold_accuracy_xor", "xor_feature_decoder", "check_split", "preparation_summaries",
           "group_mean_and_sem2", "sign_flip_test", "SplitEvaluation", "evaluate_split", "GroupComparison", "compare_groups"]
