#!/usr/bin/env python3
"""Hand-checkable verification for structural bridges B1 and B2.

Package 9/10 of AUDIT_ROADMAP.md; docs/structural_relations.md carries the
full derivation. Uses ONLY existing repo APIs, no new production module:
  - chemical_organization.core.is_reaction_closed
  - membership.formal_concept_analysis.derive_up / derive_down
  - membership.core.MembershipMatrix
  - closure.core.is_exact_closure

Checks (all numbers from this script run):
  B1: reaction closure on {a,b,c} with a->b, b->c represented exactly by
      the FCA double-derivation on a purpose-built context (attributes =
      all reaction-closed subsets); an arbitrary (identity) context does
      NOT reproduce the same closure for {a}.
  B2: a 4-state Markov chain aggregated to 2 macro-states satisfies
      PC=CQ (checked via is_exact_closure) and P^n C = C Q^n for
      n in {0,1,2,5,10}; perturbing one micro-row breaks row-wise
      agreement (non-lumpable counter-example).

JSON {count, passed, failed, report}; numbers from this run. Does not
mutate chemical_organization/, membership/, or closure/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scoped_correspondence.chemical_organization.core import is_reaction_closed  # noqa: E402
from scoped_correspondence.closure.core import is_exact_closure  # noqa: E402
from scoped_correspondence.membership.core import MembershipMatrix  # noqa: E402
from scoped_correspondence.membership.formal_concept_analysis import (  # noqa: E402
    derive_down,
    derive_up,
)


def require(ok, msg):
    if not bool(ok):
        raise AssertionError(msg)


def near(a, b, atol=1e-12):
    if abs(float(a) - float(b)) > atol:
        raise AssertionError(f"{a!r} != {b!r}")


def _powerset(items):
    items = tuple(items)
    return [
        frozenset(s)
        for n in range(len(items) + 1)
        for s in itertools.combinations(items, n)
    ]


def check_b1_reaction_fca_representation():
    """Reaction closure on {a,b,c} (0,1,2) with 0->1, 1->2, represented
    exactly by the FCA double-derivation on a purpose-built context."""
    U = frozenset(range(3))
    reactions = [(frozenset([0]), frozenset([1])), (frozenset([1]), frozenset([2]))]

    def reaction_hull(A):
        A = frozenset(A)
        while True:
            additions = frozenset().union(*(p for r, p in reactions if r <= A)) if reactions else frozenset()
            next_A = A | additions
            if next_A == A:
                return A
            A = next_A

    subsets = _powerset(sorted(U))
    closed_sets = [A for A in subsets if is_reaction_closed(A, reactions)]
    require(len(closed_sets) >= 1, "at least one reaction-closed set (U itself)")

    # Purpose-built context: attributes = all reaction-closed subsets.
    context = MembershipMatrix(
        np.array([[int(i in A) for A in closed_sets] for i in sorted(U)], dtype=float)
    )
    agree = 0
    for A in subsets:
        fca_closure = derive_down(derive_up(A, context), context)
        require(fca_closure == reaction_hull(A), f"FCA double-derivation != reaction_hull for {sorted(A)}")
        require(A <= reaction_hull(A), f"reaction_hull must be extensive for {sorted(A)}")
        require(
            reaction_hull(reaction_hull(A)) == reaction_hull(A),
            f"reaction_hull must be idempotent for {sorted(A)}",
        )
        agree += 1
    for A in subsets:
        for B in subsets:
            if A <= B:
                require(
                    reaction_hull(A) <= reaction_hull(B),
                    f"reaction_hull must be monotone: {sorted(A)} <= {sorted(B)}",
                )

    # Arbitrary (identity) context does NOT reproduce the same closure.
    arbitrary_context = MembershipMatrix(np.eye(3))
    arbitrary_closure_of_0 = derive_down(derive_up({0}, arbitrary_context), arbitrary_context)
    hull_of_0 = reaction_hull({0})
    require(
        arbitrary_closure_of_0 != hull_of_0,
        "arbitrary context must NOT coincidentally reproduce reaction_hull({0})",
    )

    return {
        "species": [0, 1, 2],
        "reactions": "0->1, 1->2",
        "closed_sets": [sorted(A) for A in closed_sets],
        "subsets_checked": agree,
        "constructed_context_matrix": context.matrix.astype(int).tolist(),
        "arbitrary_context_counterexample": {
            "input": [0],
            "fca_closure_on_identity_context": sorted(arbitrary_closure_of_0),
            "true_reaction_hull": sorted(hull_of_0),
            "differ": True,
        },
        "closure_axioms_checked": ["extensive", "monotone", "idempotent"],
    }


def check_b2_markov_operator_intertwining():
    """4-state chain aggregated to 2 macro states: PC=CQ, P^n C = C Q^n."""
    P = np.array(
        [
            [0.4, 0.3, 0.2, 0.1],
            [0.1, 0.6, 0.15, 0.15],
            [0.2, 0.2, 0.3, 0.3],
            [0.3, 0.1, 0.1, 0.5],
        ]
    )
    C = np.array([[1, 0], [1, 0], [0, 1], [0, 1]], dtype=float)
    Q = np.array([[0.7, 0.3], [0.4, 0.6]])
    require(np.allclose(P.sum(axis=1), np.ones(4)), "P rows must sum to 1")
    require(np.allclose(Q.sum(axis=1), np.ones(2)), "Q rows must sum to 1")
    require((P >= 0).all() and (Q >= 0).all(), "P, Q must be nonnegative")

    exact = is_exact_closure(P, C, Q)
    require(exact, "PC=CQ must hold for this constructed pair")

    residual = float(np.abs(P @ C - C @ Q).max())
    require(residual < 1e-12, f"PC=CQ residual too large: {residual!r}")

    powers_checked = [0, 1, 2, 5, 10]
    for n in powers_checked:
        Pn = np.linalg.matrix_power(P, n)
        Qn = np.linalg.matrix_power(Q, n)
        d = float(np.abs(Pn @ C - C @ Qn).max())
        require(d < 1e-9, f"P^{n} C != C Q^{n} (defect {d!r})")

    for g in np.eye(2):
        d = float(np.abs(P @ (C @ g) - C @ (Q @ g)).max())
        require(d < 1e-12, f"P(Cg) != C(Qg) for basis observable {g!r}")

    # Non-lumpable counter-example: perturb one micro-row.
    P_bad = P.copy()
    P_bad[0, 0] -= 0.05
    P_bad[0, 2] += 0.05
    require((P_bad >= -1e-15).all(), "perturbed row must stay a valid distribution")
    require(np.allclose(P_bad.sum(axis=1), np.ones(4)), "perturbed P rows must still sum to 1")
    row_diff = float(np.abs((P_bad @ C)[0] - (P_bad @ C)[1]).max())
    require(row_diff > 1e-6, "perturbed micro-row must break row-wise macro agreement")
    require(not is_exact_closure(P_bad, C, Q), "perturbed P must no longer satisfy any exact closure with the same Q")

    return {
        "P": P.tolist(),
        "C": C.tolist(),
        "Q": Q.tolist(),
        "is_exact_closure": exact,
        "PC_CQ_residual": residual,
        "powers_checked": powers_checked,
        "observable_basis_checked": True,
        "nonlumpable_counterexample": {
            "perturbed_entries": {"P_bad[0,0]": float(P_bad[0, 0]), "P_bad[0,2]": float(P_bad[0, 2])},
            "row_wise_macro_difference": row_diff,
            "is_exact_closure_after_perturbation": False,
        },
    }


CHECKS = [
    ("B1_reaction_closure_FCA_representation", check_b1_reaction_fca_representation),
    ("B2_markov_operator_intertwining", check_b2_markov_operator_intertwining),
]


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--json-out",
        type=Path,
        default=Path(__file__).with_name("verify_structural_bridges_b1_b2_results.json"),
    )
    args = p.parse_args(argv)

    report = {
        "package": "AUDIT_ROADMAP.md items 9-10 (structural relations language + schema)",
        "source_document": "docs/structural_relations.md",
        "concept_origin": "prompts/Answers/SCF_Strukturelle_Bruecken_Konzept.md",
        "timestamp": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "platform": platform.platform(),
        "checks": {},
        "disclaimer": (
            "Two pilot bridges only (B1, B2); B3-B6 and the follow-on "
            "research program are deferred (see docs/structural_relations.md "
            "section 6). Uses only existing repo APIs; no new production "
            "module; does not mutate chemical_organization/, membership/, "
            "or closure/."
        ),
    }
    passed = 0
    failed = 0
    errors = []
    for name, fn in CHECKS:
        try:
            report["checks"][name] = {"status": "passed", "detail": fn()}
            passed += 1
            print(f"PASS  {name}")
        except Exception as exc:  # noqa: BLE001
            failed += 1
            errors.append({"check": name, "error": f"{type(exc).__name__}: {exc}"})
            report["checks"][name] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            print(f"FAIL  {name}: {exc}")

    summary = {"count": len(CHECKS), "passed": passed, "failed": failed, "errors": errors, "report": report}
    args.json_out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(f"\n{passed}/{len(CHECKS)} passed; wrote {args.json_out}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
