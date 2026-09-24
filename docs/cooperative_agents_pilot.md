# Cooperative agents: when does extra information help a decision?

DOMAIN_EXPANSION_ROADMAP.md Paket B6a — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md`,
section 12. Module:
[`validation/cooperative_agents_pilot.py`](../src/scoped_correspondence/validation/cooperative_agents_pilot.py),
reusing the EXISTING BROJA bivariate PID solver
(`information_decomposition/broja.py`) — no new information-theory library
was built. Verification:
[`verify_cooperative_agents_pilot.py`](../verification/verify_cooperative_agents_pilot.py)
(6/6 checks).

## Three fully enumerated control tasks

All three tasks are small enough to enumerate EVERY state exactly (never a
Monte Carlo sample standing in for these cases):

### A. Complementary information (XOR)

Independent fair bits `A, B`, target `Y = A XOR B`. Agent 2 decides, seeing
only `B`.

| | Success rate |
|---|---:|
| No communication (best of all 4 possible decision rules on `B`) | **0.5** |
| Perfectly transmitted bit from Agent 1 | **1.0** |

The repo's own, unmodified BROJA PID solver, run on the exact joint
distribution, confirms the textbook synergy signature — not asserted from
a formula: `redundancy=0`, `unique₁=0`, `unique₂=0`, `synergy=1 bit`,
`I(A,B;Y)=1 bit`. Individually neither source carries any information
about `Y`; jointly they determine it completely.

### B. Redundancy

`A=B=Y`, fair. Agent 2 is already perfect from `B` alone (success `1.0`
with or without communication) — additional communication cannot raise
accuracy here. PID atoms: pure redundancy (`1` bit), zero synergy, zero
uniques — confirmed by the same solver.

### C. Error channel

The XOR task's message is corrupted by an independent bit-flip with
probability `epsilon`. Two decoders, checked over the full 8-outcome
enumeration:

| `epsilon` | Naive decoder (`guess=m⊕b`) | `epsilon`-informed optimal decoder |
|---:|---:|---:|
| 0.0 | 1.0 | 1.0 |
| 0.1 | 0.9 | 0.9 |
| 0.5 | 0.5 | 0.5 |
| **1.0** | **0.0** | **1.0** |

The `epsilon=1` row is the interesting one: a systematically-inverted
channel is *fully* informative once you know to invert it back
(`guess=(m⊕b)⊕1`) — this separates a merely noisy channel from a
correlated-but-unrecognized one, so a systematically flipped message is
never mistaken for a useless one.

## Communication cost threshold

For reward `J = P(Ŷ=Y) - λ·E[bits sent]`, with the sending decision FIXED
across all states (never conditioned on the observation — otherwise
"send or stay silent" could itself leak information for free, plan
section 12.3): communicating strictly beats silence in the XOR task iff
`λ < 0.5`, is exactly indifferent at `λ=0.5` (checked as an EXACT equality
of net utilities, not merely "close"), and never helps in the redundancy
task for any `λ>0` (checked for `λ ∈ {0.01, 0.1, 0.5, 1.0}`).

## Scope

These control tasks establish precise answers about the specific
manipulated game environment — not human cognition, consciousness, or a
general intelligence measure (plan section 12.2's explicit caveat).
Repeated/dynamic tasks with delayed feedback (plan section 12.4) and
LLM-agent extensions are deliberately deferred, not part of this package.
