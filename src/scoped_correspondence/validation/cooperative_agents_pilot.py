"""Finite cooperative-agent communication tasks (DOMAIN_EXPANSION_ROADMAP.md Paket B6a).

Response to prompts/Answers/nicht_stationäre_Treiber/
SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md, section 12: connect the
EXISTING bivariate PID module (``information_decomposition.broja``, no new
information-theory library built here) to three small, EXACTLY ENUMERABLE
communication tasks that isolate when extra information helps a decision,
when it is redundant, and how a noisy channel changes the answer.

Every task below is over a FULLY enumerated finite state space (never a
Monte Carlo sample standing in for these small exact cases, per the plan's
explicit requirement) and reports success rate, communication cost, and the
task's PID atoms as SEPARATE fields -- high mutual information alone does
not certify a good policy, and a policy's success rate says nothing about
its information-theoretic decomposition (plan section 12.5, point 5).

**A. Complementary information (XOR).** Independent fair bits ``A, B``,
target ``Y = A XOR B``. Agent 2 decides, seeing only ``B``. Individually,
neither source carries any information about ``Y`` (``I(A;Y)=I(B;Y)=0``),
yet jointly they determine it completely (``I(A,B;Y)=1`` bit) -- the
textbook SYNERGY signature, confirmed here via the existing BROJA PID
solver on the exact joint distribution, not asserted from the formula.

**B. Redundancy.** ``A=B=Y``, fair. Agent 2 is already perfect without any
message; communicating cannot raise the success rate here (PID atoms:
pure redundancy, zero synergy).

**C. Error channel.** The XOR task's message is corrupted by an
independent bit-flip with probability ``epsilon``. An unchanged (naive)
decoder gets ``1-epsilon``; a decoder informed of ``epsilon`` can do
``max(epsilon, 1-epsilon)`` by inverting when ``epsilon>0.5`` -- exactly
recovering full information from a systematically-inverted channel.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np

from scoped_correspondence.errors import ScopeViolationError
from scoped_correspondence.information_decomposition.broja import BivariatePIDReport, broja_pid_bivariate


@dataclass(frozen=True)
class TaskEvaluation:
    task_name: str
    success_no_communication: float
    success_with_communication: float
    bits_sent_no_communication: float
    bits_sent_with_communication: float
    pid: BivariatePIDReport

    def net_utility(self, communicate: bool, lam: float) -> float:
        if communicate:
            return self.success_with_communication - lam * self.bits_sent_with_communication
        return self.success_no_communication - lam * self.bits_sent_no_communication

    def communication_helps(self, lam: float) -> bool:
        """True iff sending strictly beats silence at communication cost `lam` per bit.
        The sending decision itself is FIXED across all states (plan section 12.3's
        simplest control case) -- never state-dependent, so silence cannot itself
        leak information for free."""
        return self.net_utility(True, lam) > self.net_utility(False, lam)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_name": self.task_name,
            "success_no_communication": self.success_no_communication,
            "success_with_communication": self.success_with_communication,
            "bits_sent_no_communication": self.bits_sent_no_communication,
            "bits_sent_with_communication": self.bits_sent_with_communication,
            "pid": self.pid.as_dict(),
        }


def _best_success_rate_no_message(rows: List[Tuple[int, int, int, float]]) -> float:
    """Exhaustively enumerates ALL 4 possible decision functions f: B in {0,1} -> guess
    in {0,1} (there are only 4 -- constant-0, constant-1, identity, negation) and
    returns the best achievable weighted success rate. Full enumeration, not a search
    heuristic -- there are exactly 4 candidates for a binary decision on a binary input.
    """
    best = 0.0
    for f0 in (0, 1):
        for f1 in (0, 1):
            f = {0: f0, 1: f1}
            success = sum(prob for (_, b, y, prob) in rows if f[b] == y)
            best = max(best, success)
    return best


def _pid_joint(rows: List[Tuple[int, int, int, float]]) -> np.ndarray:
    joint = np.zeros((2, 2, 2))
    for a, b, y, prob in rows:
        joint[a, b, y] += prob
    return joint


def evaluate_xor_task(*, rng_seed: int = 20260924) -> TaskEvaluation:
    """Task A: independent fair A, B; Y=A^B; agent 2 decides from B (+ optional message)."""
    rows = [(a, b, a ^ b, 0.25) for a in (0, 1) for b in (0, 1)]
    success_no_comm = _best_success_rate_no_message(rows)
    # Perfect message m=A: decision = m^b = a^b = y, always correct, by full enumeration.
    success_with_comm = sum(prob for (a, b, y, prob) in rows if (a ^ b) == y)
    pid = broja_pid_bivariate(_pid_joint(rows), rng=np.random.default_rng(rng_seed))
    return TaskEvaluation("xor_complementary_information", success_no_comm, success_with_comm, 0.0, 1.0, pid)


def evaluate_redundancy_task(*, rng_seed: int = 20260924) -> TaskEvaluation:
    """Task B: A=B=Y, fair. Agent 2 is already perfect from B alone."""
    rows = [(a, a, a, 0.5) for a in (0, 1)]
    success_no_comm = _best_success_rate_no_message(rows)
    # Message m=A=B=Y; decision=m still correct, but adds nothing new.
    success_with_comm = sum(prob for (a, b, y, prob) in rows if a == y)
    pid = broja_pid_bivariate(_pid_joint(rows), rng=np.random.default_rng(rng_seed))
    return TaskEvaluation("redundancy", success_no_comm, success_with_comm, 0.0, 1.0, pid)


def evaluate_noisy_xor_task(epsilon: float, decoder: str) -> float:
    """Task C: XOR task, message m = A XOR (independent bit-flip with prob `epsilon`).

    ``decoder='naive'``: unchanged decoding ``guess = m^b`` regardless of ``epsilon``.
    ``decoder='optimal'``: informed of ``epsilon``; inverts (``guess = (m^b)^1``) when
    ``epsilon > 0.5`` (a systematically-inverted channel is fully informative once you
    know to invert it), otherwise identical to the naive decoder. Full enumeration over
    all 8 weighted (A, B, error) outcomes -- no sampling.
    """
    if not (0.0 <= epsilon <= 1.0):
        raise ScopeViolationError(f"epsilon must be in [0,1]; got {epsilon!r}")
    if decoder not in ("naive", "optimal"):
        raise ScopeViolationError(f"decoder must be 'naive' or 'optimal'; got {decoder!r}")

    invert = decoder == "optimal" and epsilon > 0.5
    total = 0.0
    for a in (0, 1):
        for b in (0, 1):
            y = a ^ b
            for err in (0, 1):
                prob = 0.25 * ((1.0 - epsilon) if err == 0 else epsilon)
                m = a ^ err
                guess = (m ^ b) ^ (1 if invert else 0)
                if guess == y:
                    total += prob
    return total


__all__ = [
    "TaskEvaluation", "evaluate_xor_task", "evaluate_redundancy_task", "evaluate_noisy_xor_task",
]
