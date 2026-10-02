# Release notes

License: CC BY 4.0.

## 0.42.0 (first public release, 2026-10-02)

This is the first public release: the repository is public, the package is
on PyPI and Zenodo archives the release. The **content is that of
`0.42.0a1`** below; this version only adds the release infrastructure.

- Install with `pip install scoped-correspondence`. No pre-release flag is
  needed, so other projects can declare SCF as a normal dependency. The
  development status stays *Alpha*.
- `.zenodo.json` holds the Zenodo metadata (creator, licence, keywords,
  `isPartOf` GenesisAeon 10.5281/zenodo.19645351, community `genesisaeon`).
- `.github/workflows/release.yml`: a tag `v*` runs, in order:
  1. the math suite, the link check and a tag = package-version check;
  2. the build and `twine check`;
  3. the PyPI upload (`PYPI_API_TOKEN`);
  4. the GitHub release, which Zenodo then archives.

  Trusted Publishing can replace the token after the first release.
- `pyproject.toml` now uses an SPDX licence expression and explicit
  `license-files`, replacing the deprecated TOML table form (setuptools
  warned that builds would break from February 2027).
- Checked before release:
  - the wheel and sdist pass `twine check`;
  - the sdist contains only `src/`, the licences, the README and
    `pyproject.toml`, without `data/` or `prompts/`;
  - the installed wheel imports all 166 modules in a fresh Python 3.13
    environment.
- `verify_version_metadata.py` now also checks the version in
  `.zenodo.json`.

## 0.42.0a1 (internal integration tag, 2026-10-02; not published)

This release integrates the branch `j-series` (36 commits since
`0.41.0a1`). Every package was built in its own commit with hand-derived
controls, a registered `verify_*.py`, a full regression run and a link
check. Three external reviews were reproduced and fixed:
`SCF_REVIEW_J_SERIES_6b3a331`, `SCF_FOLLOWUP_REVIEW_637bc1c` and
`SCF_PMF_REVIEW_51b1a38`. The last one gave the merge GO for `5c3054f`.

### New capabilities

- **Scope, composition and evidence (J0–J12).** See
  [SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md](SCOPE_COMPOSITION_EVIDENCE_ROADMAP.md).
  - typed composition of correspondences with exact scopes, clocks and error bounds;
  - exact interval certificates over whole rational boxes;
  - exact affine identifiability;
  - paired forecast comparisons;
  - joint sensitivity analysis;
  - weighted conformal calibration;
  - finite causal abstraction and transport;
  - Markov reduction bounds as contracts;
  - the CLI `scripts/run_scope_evidence_demo.py`.
- **Muonium gravity measurement model (MU0–MU7)**, synthetic only. Real beam
  data are deferred because the licence is InC-NC. See
  [MUONIUM_GRAVITY_ROADMAP.md](MUONIUM_GRAVITY_ROADMAP.md).
- **Candidate pilots (TP/SK/SA).** See
  [CANDIDATE_PILOTS_ROADMAP.md](CANDIDATE_PILOTS_ROADMAP.md).
  - polyhedral observation fibres;
  - stellar pulse measurement operator;
  - Saturn quantity register.
- **Adaptive modular networks (ON0–ON7).** The synthetic core is complete;
  the real organoid data branch is blocked. See
  [ORGANOID_NETWORK_ROADMAP.md](ORGANOID_NETWORK_ROADMAP.md) and the CLI
  `scripts/run_organoid_network_pilot.py`.
- **Targeted mutation run.** `scripts/run_targeted_mutations.py` reports to
  [verification/targeted_mutations_report.json](verification/targeted_mutations_report.json).
- **Oracle cross-check.** The delivered MU/candidate oracle is checked
  against production in `verify_mu_candidate_oracle_crosscheck.py`.

### Behaviour changes and migration notes

- **`validation.conformal.calibrate_split_conformal`: α semantics**
  - `Fraction`, `int` and decimal strings (e.g. `"0.7"`) are now used
    exactly.
  - A float α means its exact binary value, and the rank is computed exactly
    (no float rounding, no epsilon).
  - Compared with the old float pipeline, 825 of 99,000 (α, n) pairs change
    rank (α = 0.01–0.99, n ≤ 1000), in both directions. Examples: 0.3 with
    n = 9 goes 7 → 8; 0.44 with n = 24 goes 15 → 14.
  - The new rank is always the minimal valid rank for the given value.
  - Coverage still requires exchangeability.
  - The repository's own callers give identical results.
  - Give decimal levels as `Fraction` or string.
- **`closure.error_bounds.transient_reduction_bound`**
  - The general CTMC branch no longer returns a zero bound when the reduced
    dynamics vanish: φ(t, 0) = t, evaluated with `expm1`.
  - The full dynamics must be Markov (P row-stochastic, Q a generator);
    otherwise `ScopeViolationError` is raised.
  - `norm="TV"` requires a probability contract.
  - The source version is now cited as arXiv:2403.07618 **v3**.
- **`epistemic.reporting.report_to_json`**
  - Output is strict JSON.
  - ±∞ become `{"__nonfinite__": "+inf" | "-inf"}`.
  - NaN raises `ValueError`; previously a bare `NaN`/`Infinity` token was
    written.
- **`observation.directed_information` and
  `information_decomposition.broja_pid_bivariate`**
  - Non-finite masses and overflowing totals are refused early.
  - New optional `input_mode="pmf"`: exact total 1 for `int`/`Fraction`
    input, 1 ± 1e-12 for floats, and every original mass must be
    non-negative.
  - The default `input_mode="weights"` keeps its documented behaviour.
  - Reports carry `input_mode` and `input_total_mass`.
- **ON evaluation protocol**
  - Protocol `paired_v2`: frozen and refitted decoders are scored on the
    same test trials, and split ids are recorded.
  - The configuration ID changed to `e5017540ea171f9d`.
  - Frozen-decoder values changed (e.g. 0.55 → 0.59); Δ and refitted values
    did not.
- **Input validation of the ON helpers**
  - `sign_flip_test` refuses NaN, ±∞ and bool, and converts NumPy integers to
    exact `int`.
  - `NearestMeanDecoder.predict` requires a fit, finite input and the exact
    feature count.
  - `hebb_update` validates the mask, weights, activities and γ.
- **`scoped_correspondence.__version__`** now matches the package metadata.
  It was stale at `0.10.0a1`.

### Verification status

- `--category all`: 140/140 under Python 3.11.
- Math suite under Python 3.13: 121/121.
- Link check: 0 broken.
- CI includes a Python 3.12 job for version-sensitive scripts.
- Targeted mutants: 121; 120 killed by content assertion, 1 pre-registered
  as equivalent.

### Open, documented limits (not merge conditions)

These are listed in [DEEP_RESEARCH_BACKLOG.md](DEEP_RESEARCH_BACKLOG.md):

- real-data branches MU6 and ON6b;
- full-text source audits;
- the oracle groups without a production API;
- the SA options.
