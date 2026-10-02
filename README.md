# Scoped Correspondence Formalism

[![PyPI](https://img.shields.io/pypi/v/scoped-correspondence)](https://pypi.org/project/scoped-correspondence/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23099384.svg)](https://doi.org/10.5281/zenodo.23099384)
[![License](https://img.shields.io/badge/code-GPLv3--or--later-blue)](LICENSE)
[![Docs License](https://img.shields.io/badge/docs-CC%20BY%204.0-lightgrey)](LICENSE-DOCS)
[![Verify](https://github.com/GenesisAeon/scoped-correspondence-formalism/actions/workflows/verify.yml/badge.svg)](.github/workflows/verify.yml)

**A Python library and research methodology for stating formal
correspondences between mathematical models — instead of claiming two
things are "the same" across domains, it makes you state exactly how,
under what transformation, and within what scope they correspond, then
checks that claim against an independently reproduced control case.**

## What is this?

Most cross-domain modeling claims ("this ecological system behaves like
that climate system") never get made precise enough to be wrong. This
repo's core idea — the `Correspondence` contract in
`correspondence/contract.py` — forces the claim into an explicit shape:
a state map, a time map, a declared scope, and a residual that is either
small or isn't. From that core, `src/scoped_correspondence/` has grown
into a large, largely independent set of modules spanning dynamical
systems, information theory (including directed information / temporal
information flow — not general causal inference), thermodynamics,
viability theory, and more — each one a small, formally checkable model
plus a `verify_*.py` that tries to break it, not just confirm it. See the
module table below for the current, exact set (a headline count here
would just go stale).

It is simultaneously:
- a **usable Python library** (`pip install -e .`) for anyone who wants
  a correspondence-contract pattern for their own model-linking work,
  and
- a **living record of how far AI-assisted formal/scientific work holds
  up under adversarial review** — most modules have an audit trail of
  independent reproduction and fixes, several with a full external
  review cycle, kept in [`HISTORY.md`](HISTORY.md) rather than lost to
  chat logs.

## Quickstart

Install the package from PyPI:

```bash
pip install scoped-correspondence
```

To work on the repository and run the verification suites, install it from
a checkout instead:

```bash
pip install -e .
python -m pip install -r verification/requirements.txt
```

```python
from scoped_correspondence.dynamics.core import fixed_points

# Cubic normal form tau*dx/dt = -x^3 + a*x + b at b=0, a=3:
# fixed points are 0 and +-sqrt(a).
print(fixed_points(3.0, 0.0))
# [-1.7320508075688774, ~0.0, 1.7320508075688774]
```

A fuller example (a `Correspondence` contract with residual, scope, and
an optional state-dependent time map) is in
[docs/correspondence_core.md](docs/correspondence_core.md).

## Using AI (or anyone new) on this repo

The project's actual differentiator isn't any one module — it's the
discipline that keeps ~70 of them independently trustworthy at once:
hand-derive control cases before writing code, verify external claims
against the real code before fixing anything, one reviewed "Paket" per
commit with a full regression run first. **[`CLAUDE.md`](CLAUDE.md)**
states this discipline as concrete, followable steps — read it before
extending anything here, whether you're an AI agent or a new human
contributor. It also doubles as the honest answer to "how was this
built": that file describes the actual process, not an idealized one.

## Module overview (`src/scoped_correspondence/`)

| Package | Contains |
|---|---|
| `correspondence/` | Core contract: `Correspondence`, conjugacy residual, approximation certificates |
| `observation/` | Channel capacity, information retention, Arimoto–Blahut, directed information |
| `dynamics/` | Cubic normal form, contraction, Landau/Ising, GSPT, Floquet, panarchy, early warning |
| `coupling/` | Coupling layers, Casimir/Dirac composition, dissipativity, GENERIC↔Navier-Stokes, generalized synchronization |
| `closure/` | `PC=CQ` macro closure, generator lumpability, error bounds, Chapman–Enskog |
| `viability/` | Viability kernels, Nagumo tangent cone, control barrier functions |
| `membership/` | Membership matrices, formal concept analysis |
| `identifiability/` | Profile likelihood, Fisher-information sloppiness |
| `validation/` | Real-data pilots (COVID, NOAA temperature, USGS earthquakes, SPARC galaxies), sequential-information and buffer pilots |
| `contextuality/` | Sheaf contextuality, Čech cohomology, CSW graph invariants |
| `information_decomposition/` | PID/redundancy bottleneck, BROJA |
| `thermo/` | Schnakenberg network thermodynamics, Crooks/Jarzynski |
| `chemical_organization/` | Chemical organization theory (reaction closure, self-maintenance) |
| `percolation/` | Bethe-tree percolation / Kesten branching |
| `pattern_formation/` | Turing instability / dispersion relation |
| `free_boundary/` | Stefan–Neumann similarity solution |
| `astrophysics/` | Galaxy rotation-curve profiles (Burkert/NFW), MOND acceleration relations |
| `epistemic/` | Assumption/evidence auditing layer: finite claim status, minimal supports, observation-dependent identification, decisions under declared uncertainty (also wraps `correspondence/controlled_markov.py`'s controlled-Markov lumpability under declared actions) |
| `metarules/` | Repo-wide meta-rules |
| `legacy/` | Adapters to the original Revision-2/3 check scripts |
| `assurance/` | `ProofReport` result axes; exact rational interval certificates over whole boxes |
| `dimensions/` | Exact dimension checks, units (incl. affine scales), Buckingham-Π basis |
| `causal/` | Finite SCMs, exact interventional abstraction, d-separation, one checked transport rule |
| `muonium/` | Muonium-gravity measurement model, identifiability counterexamples, design (synthetic only) |
| `validation/modular_networks/` | Adaptive modular networks: observation vs. readout vs. information, synthetic organoid-motivated benchmark |

## Scope, composition and evidence

Since the J-series ([SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md](SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md)),
SCF can state *under which assumptions, on which domain and with which
error* a relation between models may be used, chained or transferred:
typed composition with exact scopes, clocks and separate flow/field error
bounds; universal bounds over whole rational boxes with re-checkable
certificates; exact affine identifiability; paired forecast comparisons
whose inference is gated by declared applicability; joint sensitivity;
weighted conformal calibration with an explicit guarantee status; exact
finite causal abstraction and one checked transport rule; existing Markov
reduction bounds as contracts. Each result separates what is proved,
numerically sampled or empirically evaluated, and states what is **not**
claimed (closing matrix in the roadmap). `python scripts/run_scope_evidence_demo.py`
prints the six reference demonstrations as JSON.

Follow-up series built on this layer (all synthetic or exact unless stated):
[muonium gravity measurement model](MUONIUM_GRAVITY_ROADMAP.md) (MU0–MU7;
real beam data deferred for licence reasons),
[candidate pilots](CANDIDATE_PILOTS_ROADMAP.md) (polyhedral observation
fibres, stellar pulse measurement operator, Saturn quantity register) and
[adaptive modular networks](ORGANOID_NETWORK_ROADMAP.md) (ON0–ON7: when do
coupling and adaptation improve input discriminability, and how much of that
is observation and decoder; real organoid data blocked behind data gates).
A targeted mutation run (`scripts/run_targeted_mutations.py`,
[report](verification/targeted_mutations_report.json)) checks that the
verification scripts actually catch registered errors.

## Status

`0.42.0` (alpha status, first public release; [release notes](RELEASE_NOTES.md)) — the formal-hooks/stable-release milestone from
[ARCHITECTURE_ROADMAP.md](ARCHITECTURE_ROADMAP.md) is the one open
original milestone before a SemVer `1.0`. All checked-in `verify_*.py`
suites currently pass:

```bash
python scripts/run_verification_suite.py --category all    # math + data
python scripts/run_verification_suite.py --category links  # doc link check
```

See [docs/capability_overview.md](docs/capability_overview.md) for a
per-module question/assumptions/evidence/limits table, and
[VERIFICATION.md](VERIFICATION.md) for what each check actually proves.
**[`HISTORY.md`](HISTORY.md)** has the full dated narrative: every
external audit, every review-fix cycle, every real-data pilot result
(including the ones where the model lost to the baseline — reported
either way).

## Further reading

| File | Content |
|---|---|
| [CLAUDE.md](CLAUDE.md) | How this repo is actually built and extended (AI or human) |
| [HISTORY.md](HISTORY.md) | Full chronological audit trail and project history |
| [docs/capability_overview.md](docs/capability_overview.md) | Per-module question/assumptions/evidence/limits |
| [FORMALISM.md](FORMALISM.md) | Coherent overview and binding notation |
| [GLOSSARY.md](GLOSSARY.md) | Vocabulary (Observation/Dynamics/Coupling/Correspondence) and legacy-name mapping |
| [ARCHITECTURE_ROADMAP.md](ARCHITECTURE_ROADMAP.md) | Longer-term library architecture roadmap |
| [GALAXY_DYNAMICS_ROADMAP.md](GALAXY_DYNAMICS_ROADMAP.md) | Galaxy rotation-curve module (G0–G7 + review fixes) |
| [EPISTEMIC_AUDIT_ROADMAP.md](EPISTEMIC_AUDIT_ROADMAP.md) | Assumption/evidence auditing layer (H0–H7 + review fix) |
| [SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md](SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md) | Scopes, composition and evidence (J0–J12) |
| [MUONIUM_GRAVITY_ROADMAP.md](MUONIUM_GRAVITY_ROADMAP.md) | Muonium gravity measurement model (MU0–MU7) |
| [CANDIDATE_PILOTS_ROADMAP.md](CANDIDATE_PILOTS_ROADMAP.md) | Candidate pilots: polyhedra, stellar pulse, Saturn (TP/SK/SA) |
| [ORGANOID_NETWORK_ROADMAP.md](ORGANOID_NETWORK_ROADMAP.md) | Adaptive modular networks and observable information (ON0–ON7) |
| [DEEP_RESEARCH_BACKLOG.md](DEEP_RESEARCH_BACKLOG.md) | Open full-text / source questions and pending decisions |
| [RELEASE_NOTES.md](RELEASE_NOTES.md) | Release notes, behaviour changes and migration notes per version |

## Citing

Please cite SCF through its Zenodo concept DOI, which resolves to the latest
version:
[10.5281/zenodo.23099384](https://doi.org/10.5281/zenodo.23099384).

For a specific version, use its version DOI. The DOI for `0.42.0` is
[10.5281/zenodo.23099385](https://doi.org/10.5281/zenodo.23099385).

Machine-readable citation metadata is in [CITATION.cff](CITATION.cff).

## License

This repository is **dual-licensed**:

- **Source code** (`src/`, `verification/*.py`, `scripts/`) —
  [GNU General Public License v3.0 or later (GPLv3+)](LICENSE).
- **Documentation** (all Markdown/prose content) —
  [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-DOCS).

If you use this work in academic writing, see
[`CITATION.cff`](CITATION.cff).
