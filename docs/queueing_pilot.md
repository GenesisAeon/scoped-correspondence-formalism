# Queueing pilot: from load averages to event risk

DOMAIN_EXPANSION_ROADMAP.md Paket B2 — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md`,
section 8. Modules:
[`dynamics/queueing.py`](../src/scoped_correspondence/dynamics/queueing.py) (B2a),
[`viability/first_passage_ctmc.py`](../src/scoped_correspondence/viability/first_passage_ctmc.py) (B2b),
[`validation/queueing_pilot.py`](../src/scoped_correspondence/validation/queueing_pilot.py) (combined).
Verification:
[`verify_queueing.py`](../verification/verify_queueing.py) (5/5),
[`verify_queueing_first_passage.py`](../verification/verify_queueing_first_passage.py) (7/7),
[`verify_queueing_pilot.py`](../verification/verify_queueing_pilot.py) (3/3).

## The question (B2a, deterministic)

When does a time-averaged load description lose the information needed for
a short-term capacity event? For piecewise-constant arrival/service rates,
the reflected fluid backlog `dq/dt = a(t)-s(t)` (reflecting lower barrier
at `q=0`) is exact per-segment via `q(t+Δ)=max(0, q(t)+(a-s)Δ)`, and — since
each constant-rate segment is provably **monotonic** once reflection is
accounted for — every level crossing and the global peak are found exactly,
with no grid search anywhere in the module.

**Astra's fixed worked example** (`q0=0`, `s=1`, `H=10`, `K=5`, same total
arrivals `8` in both scenarios):

| Scenario | Arrivals | Peak backlog | First hit of `K=5` |
|---|---|---:|---:|
| Uniform | `a=0.8` constant | **0** (stays empty) | never |
| Spike | `a=4` on `[0,2]`, then `0` | **6** at `t=2` | `t=5/3≈1.667` |

Identical total load, only the temporal shape differs — isolating exactly
the information a time-average discards, with no nonlinearity anywhere.

The **stock/reserve bridge** `R(t)=K-q(t)` is exact up to the first
capacity breach; past that point a bounded physical reservoir (which
cannot serve demand once empty) and an unbounded queue's backlog (which
keeps growing) diverge — `stock_reserve_bridge` reports
`first_capacity_breach_time` explicitly rather than silently extending
past it (plan section 4.2, "Negativtest").

## The question (B2b, stochastic)

**The stationary tail `P(N>=K)` is not `P(max_{t<=H} N_t>=K)`.** For an
M/M/1 queue restricted to states `{0,...,K}` with `K` made absorbing, the
row-vector construction `P(τ_K<=H) = [p_0·exp(H·Q_abs)]_K` gives the exact
finite-horizon first-passage probability for the UNBOUNDED chain's
first-reaching event — no artificial upper truncation needed, since states
above `K` are irrelevant to "when is `K` first reached."

Reference values (hand-derived independently, matched to the module to
`<1e-12`): `λ=1, μ=2, K=2, n₀=0, H=1` → `0.1777365760981911`;
arrivals-only (`μ=0`) reduces exactly to the closed-form Poisson tail
`1-2/e ≈ 0.2642411176571153`. Both edge reductions — `H=0`, already-at-`K`,
`λ=0`, `μ=0` — fall out of the **same** matrix-exponential construction
with no special-case branches beyond an "already reached" shortcut.

An independent second implementation (event-driven Gillespie-style
simulation, fixed seed) agrees with the exact value within a
pre-declared 5σ Monte Carlo tolerance. A piecewise-rate construction
multiplies matrix exponentials **in time order** — splitting one
constant-rate interval into equal sub-segments reproduces the single-
segment answer exactly, while a genuinely time-varying rate schedule does
**not** equal the naively rate-averaged answer (generators for different
rates don't commute in general).

## The combined pilot's point, in one number

For `λ=0.5, μ=1` (`ρ=0.5<1`, i.e. stable on average), `q0=0`, `H=10`,
`K=5`:

- **Deterministic fluid model:** peak backlog **exactly 0** — arrival rate
  never exceeds service rate, so the reflected mean trajectory never even
  moves off zero. Reported `deterministic_boundary_crossed = False`.
- **Stochastic M/M/1 first-passage, same mean rates:** `P(τ_5≤10) ≈ 5.6%`.

A mean/fluid model here would be, on its own, reported as unconditionally
"safe" — while the same average rates carry a genuine ~1-in-18 chance of
touching the capacity boundary within the horizon. `QueueingPilotReport`
keeps these two numbers in separate fields deliberately (plan section
3.2): a fluid safety statement is never allowed to stand in for a
stochastic risk statement, even when both describe the "same" queue.

## Scope

B2a: deterministic only, single server/stock, piecewise-constant rates.
B2b: single-server M/M/1 (Poisson arrivals, exponential service) only;
general phase-type service, multiple servers, and priority/network queues
are not addressed. Both are synthetic/analytic — a real trace-driven pilot
(plan section 8.4) is explicitly deferred, not part of this package.
