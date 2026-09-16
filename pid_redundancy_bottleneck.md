# PID and Redundancy Bottleneck (F09) — optional module beside EI_q

Revision package F08/F09, 16 September 2026 (Europe/Berlin). **Does not mutate** `FORMALISM.md`. Channel `EI_q` remains; this module adds a **decomposition** into redundancy / unique / synergistic atoms and a Blackwell / Redundancy-Bottleneck reading of shared predictive information.

Basis: **Williams–Beer \(I_{\min}\)** atoms. Modern redundancy: **Kolchinsky Redundancy Bottleneck** with \(\mathrm{RB}(0)=I_{\cap}\) (Blackwell). **Not** Rosas O-information as main metric. Canonical first `(sources, target)`: **micro → macro** (see [`worked_example_causal_emergence.md`](worked_example_causal_emergence.md)).

Definitions and checks: [`verification/verify_pid_rb.py`](verification/verify_pid_rb.py). Numbers below are **from that script run** only ([`verification/verify_pid_rb_results.json`](verification/verify_pid_rb_results.json)).

## 1. Primary sources

| Role | Work | Identifiers |
|---|---|---|
| Classical PID atoms | Williams & Beer, *Nonnegative Decomposition of Multivariate Information* | [arXiv:1004.2515](https://arxiv.org/abs/1004.2515) |
| Redundancy Bottleneck | Kolchinsky, *Partial information decomposition: redundancy as information bottleneck* | [arXiv:2405.07665](https://arxiv.org/abs/2405.07665); Entropy 26(7):546 (2024); **PMC11276267** |
| Orientation only | Reference implementation ideas | [github.com/artemyk/pid-as-ib](https://github.com/artemyk/pid-as-ib) (rewritten cleanly here; not vendored) |

Rosas et al. (PLOS 2020 / O-information) remain cited in `LITERATURE_CONNECTIONS.md` but are **not** the operational metric of this module.

## 2. Formulas

**Two sources \(R_1,R_2\), target \(S\):**

\[
I(S;R_1,R_2)
=
\operatorname{Red}(S;\{R_1\}\{R_2\})
+ \operatorname{Unq}(S;R_1)
+ \operatorname{Unq}(S;R_2)
+ \operatorname{Syn}(S;\{R_1 R_2\}).
\]

**Williams–Beer redundancy** (expected minimum specific information):

\[
I_{\min}(S;\{\mathbf{A}_1,\ldots,\mathbf{A}_k\})
=
\sum_s p(s)\,\min_i I(S=s;\mathbf{A}_i).
\]

Atoms via Möbius inversion on the redundancy lattice; for two sources:

\[
\begin{aligned}
\operatorname{Red} &= \Pi(S;\{1\}\{2\}) = I_{\min}(S;\{1\}\{2\}),\\
\operatorname{Unq}(R_1) &= I(S;R_1)-\operatorname{Red},\\
\operatorname{Syn} &= I(S;R_1,R_2)-\operatorname{Unq}(R_1)-\operatorname{Unq}(R_2)-\operatorname{Red}.
\end{aligned}
\]

**Blackwell redundancy / RB** (Kolchinsky):

\[
I_{\cap}
=
\max_Q I(Q;Y)
\quad\text{s.t.}\quad
Q\preceq_Y X_s\ \forall s,
\]

\[
I_{\mathrm{RB}}(R)
=
\max_{Q:\,Q-(Z,S)-Y}
I(Q;Y|S)
\quad\text{s.t.}\quad
I(Q;S|Y)\le R,
\]

with \(I_{\mathrm{RB}}(0)=I_{\cap}\). This package verifies \(\mathrm{RB}(0)=I_{\cap}\) on small binary-\(Y\) systems via the intersection of convex hulls of source posteriors (exact for the toys below). Full RB curves are Phase 2.

## 3. Mapping to `EI_q` (report beside, never equate)

| Status quo | PID/RB module |
|---|---|
| `EI_q(P)=I_q(Z_t;Z_{t+1})` scalar | Red / Unq / Syn atoms (or RB(0)) |
| “Synergy” only verbal | Syn atom under declared sources/target |
| Rosas named, not operational | API + `verify_pid_rb.py` |

**Hard rule:** report `EI_q` **beside** PID; never claim `EI = Syn`.

Canonical pair for first applications: microscopic predictors / micro variables → macroscopic target (as in the causal-emergence worked example’s micro→macro channel).

## 4. Minimal API

```text
pid_atoms(sources, target, measure="williams_beer") -> {Red, Unq1, Unq2, Syn, I_joint}
rb0_blackwell(joint) -> float                 # RB(0)=I_cap on small systems
assert_nonnegative_atoms(atoms)
compare_to_EI_q(channel, q, joint) -> {EI_q, pid_summary, claim}
# rb_curve(...) reserved Phase 2
```

## 5. Worked numbers (from script run)

Fixed seeds for Monte Carlo gates: UNIQUE `901`, XOR `902`, RB UNIQUE/XOR `905`/`906`. Exact joints for AND and full-copy redundancy. Nonnegativity tolerance: \(10^{-8}\).

### Williams–Beer atoms

| Gate | Red | Unq1 | Unq2 | Syn | I_joint |
|---|---|---|---|---|---|
| UNIQUE (R1=Y, R2 independent; n=4000) | 6.844e-06 | 0.999947 | ~0 | ~0 | 0.999954 |
| XOR (R1⊕R2=Y; n=4000) | 7.094e-05 | ~0 | 0.000136 | 0.999775 | 0.999982 |
| AND (exact fair bits) | 0.311278 | 0.0 | 0.0 | 0.5 | 0.811278 |
| FULL COPY (R1=R2=Y) | 1.0 | 0.0 | 0.0 | 0.0 | 1.0 |

For AND: \(\operatorname{Red}=I(Y;R_i)=h(1/4)-1/2\) under \(I_{\min}\) (Unq atoms vanish). For FULL COPY: \(\operatorname{Red}=H(Y)=1\).

### RB(0) = Blackwell \(I_{\cap}\)

| System | RB(0) | Reference |
|---|---|---|
| UNIQUE | 5.836e-05 (~0) | expected ~0 |
| XOR | 5.152e-05 (~0) | expected ~0 |
| AND | **0.31127812445913283** | exact \(h(1/4)-1/2\) |
| FULL COPY | **1.0** | \(H(Y)=1\) |

### EI_q beside PID (smoke)

On the closed micro→macro channel from the causal-emergence style example (preparation \(q_M\Lambda\)): **EI_q = 1.0**. PID summary on a separate XOR toy (not equated): Syn ≈ 0.9998. Claim recorded in JSON: *“EI_q reported beside PID; Syn is not identified with EI_q”*.

JSON summary printed by the verify script:

```json
{"count": 7, "passed": 7, "failed": []}
```

## 6. Relation to CREP-UTAC-AFET

Use PID when a scalar `EI_q` cannot separate redundant collective prediction from synergistic prediction under a declared micro→macro (or multi-part→task) pair. Keep metric identifiers distinct: `EI_q`, `PID_Red`, `PID_Unq`, `PID_Syn`, `RB0`.
