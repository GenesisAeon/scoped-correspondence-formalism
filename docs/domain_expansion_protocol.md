# Domain expansion: shared experiment conventions

DOMAIN_EXPANSION_ROADMAP.md Paket B1 — response to
`prompts/Answers/nicht_stationäre_Treiber/SCF_DOMAIN_EXPANSION_IMPLEMENTATION_PLAN.md`,
sections 4.4 and 5, and to
[SCF_Review_fcc9a43.md](../prompts/Answers/nicht_stationäre_Treiber/SCF_Review_fcc9a43.md)
finding R6 ("B1 ist nur teilweise umgesetzt"). This document is the
concrete protocol that `DOMAIN_EXPANSION_ROADMAP.md` alone did not supply:
measurement/event/time conventions and a shared report schema for every
pilot in Pakete B2–B6.

## 1. Event report fields (plan section 4.4)

Any module reporting a first-passage / boundary event states, explicitly,
all of the following — either as literal fields or as clearly documented
function behavior:

| Field | Meaning | Where it lives in this repo |
|---|---|---|
| `event_definition` | e.g. "first `t` with `X_t <= boundary`" | module docstring (e.g. `first_passage_ctmc.py`, `first_passage_diffusion.py`) |
| `boundary` | the threshold value | a function argument (`threshold`, `c_eol`, `capacity`) |
| `comparison` | `<=` (closed) vs `<` (strict) | fixed to `<=` throughout this expansion (a "reaching" event, plan section 4.4) |
| `horizon` | the checked time window | a function argument (`horizon`, `max_cycles`, `t_max`) |
| `time_resolution` | continuous-exact vs. discrete-cycle | continuous-exact for `queueing`/`first_passage_ctmc`/`first_passage_diffusion`; discrete-cycle (integer-valued) for `capacity_degradation` (enforced by `predict_capacity_distribution`'s integer-cycle check, R2 fix) |
| `initial_status` | already past the boundary at `t=0`? | handled as an explicit shortcut in every hitting-probability/crossing function (`initial_count>=threshold`, `x0<=0`, `C0<=c_eol` at `n=0`) |
| `event_observed` | did the event occur within the horizon? | the boolean/`Optional[float]` return itself (`None` = not observed within horizon) |
| `first_event_time` | when, if observed | the returned float, or the dataclass field (`CellPilotResult.observed_first_eol_cycle`) |
| `censoring` | right-censored if not observed | `CellPilotResult.censored` (battery pilot); `None` return already IS the censoring signal for the single-value functions |
| `numerical_method` | exact closed form vs. simulation | stated in every module's docstring (e.g. "exact matrix exponential", "exact reflection-principle formula", "Euler–Maruyama simulation, fixed seed") |
| `error_statement` | known numerical limits | each module's "Correction" docstring blocks and this file's §4 below |

## 2. Time conventions

- **Continuous-time modules** (`queueing`, `first_passage_ctmc`,
  `first_passage_diffusion`, `linear_reservoirs`'s convolution): time is a
  real number, `t=0` is the modeled origin, all events are dated exactly
  (no time-grid rounding in the reported event time itself — only the
  OPTIONAL sampled trajectory arrays for plotting use a grid).
- **Discrete-cycle modules** (`capacity_degradation`): a "cycle" is an
  integer count of discharge cycles. `predict_capacity_distribution`
  REQUIRES `origin_cycle` and every entry of `future_cycle_indices` to be
  numerically integer-valued and strictly increasing (enforced since the
  R2 fix) — a continuous or irregularly-spaced notion of cycle "time"
  needs a different model, not a silent reinterpretation of this one.
- **`available_at` / information availability:** every pilot in this
  expansion round is either (a) fully synthetic (no availability question
  applies), or (b) uses a TEMPORAL prefix/holdout split on data already
  fully in hand at development time (`battery_aging_pilot.run_cell_pilot`)
  — this is a legitimate retrospective holdout, but NOT a test of
  historically-real information availability (plan section 5.1's
  distinction between `conditional_hindcast` and `forecast_as_of_origin`).
  No pilot in this round claims the latter; this is stated explicitly
  rather than left implicit.

## 3. Report schema

Every `verify_*.py` script in this expansion (`verify_queueing.py`,
`verify_queueing_first_passage.py`, `verify_queueing_pilot.py`,
`verify_linear_reservoirs.py`, `verify_first_passage_diffusion.py`,
`verify_capacity_degradation.py`, `verify_battery_aging_pilot.py`,
`verify_cooperative_agents_pilot.py`) writes the SAME minimal JSON schema,
matching the repo-wide convention already used by every other
`verify_*.py` script (not a new, incompatible format):

```json
{
  "package": "<human-readable package/paket label>",
  "timestamp": "<ISO 8601, local timezone>",
  "python": "<python version>",
  "checks": {"<check_name>": {"status": "pass|fail|error", "detail": {...}}}
}
```

`schema_version`, commit hash, and package versions are NOT embedded
per-file: they are already recorded once, repo-wide, by `git log` and
`pyproject.toml` — duplicating them into 74+ individual JSON files would
create 74+ places that can silently drift out of sync with the actual
commit, which is a worse failure mode than the (small) convenience lost.
Missing/undefined values in any `detail` field are JSON `null` with an
adjacent status string, never a bare `NaN` (Python's `json.dumps(...,
default=str)` already used throughout this expansion enforces this).

## 4. Known numerical limits carried over from this round's fixes

- AR(1) forecasts (`capacity_degradation.predict_capacity_distribution`)
  require integer, strictly-increasing cycle indices (R2 fix) — a
  non-integer or non-monotonic request is a `ScopeViolationError`, not a
  silently-reinterpreted one.
- `convolution_discharge` (`linear_reservoirs.py`) integrates each
  reservoir's kernel via a substitution capped at `min(k*t, 745)` (R3 fix)
  — this is exact to double precision for the tested range, not a
  universal claim for pathological `inflow_fn` with singularities near
  `t`.
- `_analytic_component_critical_times`'s (`transient_amplification.py`)
  discriminant branch choice is exact and scale-invariant, but the
  repeated-root classification near `D/scale≈0` still rests on a fixed
  relative tolerance, not a certified proof of an exactly repeated
  eigenvalue (see that module's docstring, response to
  SCF_Review_fcc9a43.md's B0 follow-up).

## 5. Test-group registration

`scripts/run_verification_suite.py` classifies `verify_*.py` scripts as
`math` or `data` via a text-marker heuristic
(`_DATA_MARKERS`). Every new script from this expansion round is now ALSO
explicitly registered in `_EXPLICIT_CATEGORY` (checked BEFORE the
heuristic), so a future edit that happens to add or remove a marker
substring cannot silently reclassify an already-reviewed script.
`verify_battery_aging_pilot.py` in particular runs entirely against a
synthetic fixture (no real NASA data, no network access) and is registered
as `math` explicitly, rather than relying on it happening not to contain
any of the current data-marker strings.
