# Information Decomposition Core (Milestone 7 — optional module hardening)

**Status:** review package only — not yet linked from README/GLOSSARY as accepted "core".
Johann-OK required before any core promotion.

## What this is

Typed Python port of F09 Williams–Beer \(I_{\min}\) PID + Kolchinsky Blackwell
RB(0) from `verification/verify_pid_rb.py`, plus **F12 TWO_BIT_COPY**: Blackwell
RB(0) for finite non-binary \(Y\) via `scipy.optimize.linprog`, reporting
Williams–Beer Red **beside** Blackwell RB(0) (same "beside, not equated" rule
as EI_q beside PID).

```text
src/scoped_correspondence/
  information_decomposition/
    __init__.py
    core.py
```

## Mapping to pid_redundancy_bottleneck.md / F09 / F12

| Document | Claim / formula | API | Legacy |
|---|---|---|---|
| F09 | Williams–Beer \(I_{\min}\) atoms | `pid_atoms_williams_beer`, `i_min_two_sources` | p01–p04 |
| F09 | EI_q beside PID (not Syn=EI) | `ei_q_channel`, `compare_to_EI_q` | p06 |
| F09 | Blackwell RB(0) binary \(Y\) | `blackwell_redundancy_binary_y`, `rb0_blackwell` | p05 |
| **F12** | TWO_BIT_COPY: \(I_{\min}\) Red=1 misleading; Blackwell RB(0)=0 | `two_bit_copy_joint`, `two_bit_copy_report`, `blackwell_redundancy_finite_y` | new |
| F09 | Sources | arXiv:1004.2515, arXiv:2405.07665 | p07 |

## F12 TWO_BIT_COPY

Independent fair bits \(A,B\); target \(Y=(A,B)\) four-valued. Expected
(Harder/Salge/Polani 2013; Kolchinsky arXiv:2405.07665):

| Measure | Value |
|---|---|
| Williams–Beer \(I_{\min}\) Red | `1` bit (misleading) |
| Blackwell / Kolchinsky RB(0) | `0` (correct) |

Both appear side by side in the verify report — do not drop either.

Non-binary Blackwell: directional LPs recover vertices of the intersection of
source-posterior convex hulls; a second linprog mixes those vertices to match
\(p(Y)\) while minimising \(H(Y\mid Q)\). Binary \(Y\) keeps the legacy closed form.

## Exact legacy targets (from verify_pid_rb_results.json)

p01–p07 evidence keys must match the historical JSON **exactly** (same seeds /
formulas as `verify_pid_rb.py`).

## Hand-checkable verification

`verification/verify_information_decomposition_core.py` matches p01–p07 against
`verification/verify_pid_rb_results.json` and adds TWO_BIT_COPY
(`Red_williams_beer=1`, `RB0_blackwell=0`).

## Out of scope

Mutation of `pid_redundancy_bottleneck.md` / `FORMALISM.md`; N-source PID;
Rosas O-information as main metric; edits to legacy `verify_pid_rb.py`;
changes to other layer packages.
