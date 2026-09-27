# Working with AI on this repository

This repo is built almost entirely through iterative AI-assisted
development, but its trustworthiness comes from a specific discipline,
not from the AI itself. Follow this discipline; don't shortcut it even
when a task looks simple.

## The core rule: verify, don't trust

Never take a claim at face value — not a plan document's stated control
values, not an external review's findings, not your own prior output.
Reproduce it independently against the actual running code (or a small
standalone script using bool/int/`Fraction` arithmetic, no SCF import)
before writing a single line of production code or fix. If a plan cites
existing functions or file locations, grep/read them yourself — don't
assume the plan got it right.

## Implementing a new plan document

1. Read the plan fully. Independently hand-derive **every** named
   control/reference case before writing any code. Record the exact
   values you get.
2. Write a roadmap `.md` (mirror the style of an existing
   `*_ROADMAP.md`): a package table, a table of confirmed-existing APIs
   (with file:line references you actually checked), and the hand-traced
   control-case table. Commit this alone as the first package.
3. One package ("Paket") per commit. For each package:
   - Write a `docs/*.md` file first if the plan calls for one.
   - Write the production module(s). Additive by default — don't modify
     an existing verified module unless the task specifically requires
     it.
   - Write `verification/verify_<name>.py` with an explicit assertion
     for every "Pflichtprüfung" (required check) the plan names,
     including targeted violation/negative-control cases, not just
     happy-path checks. Run it standalone until green.
   - Re-run every previously-committed `verify_*.py` for this plan to
     confirm no regression.
   - Run `python scripts/run_verification_suite.py --category all`
     (background it — a full run commonly takes 5–15 minutes) **and**
     `--category links`.
   - Only then commit, as `Paket <id>: <description>`, and push.
4. Register each new `verify_*.py` explicitly in
   `scripts/run_verification_suite.py`'s `_EXPLICIT_CATEGORY` as
   `"math"` or `"data"` — even where the text-heuristic classifier would
   already get it right. Explicit beats implicit here.

## Handling an external review

Reviews land as Markdown files under
`prompts/Answers/nicht_stationäre_Treiber/` (sometimes with an
accompanying reproduction ZIP). Before fixing anything:

1. Independently reproduce **every** finding's concrete counterexample
   against the actual code at the reviewed commit. A review this
   project takes seriously states exact inputs and exact expected vs.
   actual values — use them verbatim.
2. Fix in the review's own recommended priority order when one is
   given.
3. Give every fix its own regression test that reproduces the review's
   exact counterexample — not just a generic "does it still pass"
   check.
4. Run the full suite + link check, then commit the whole batch as one
   `Followup-Review-Fix: <review-id> (<finding-ids>)` package and push.

## Result-vocabulary discipline

Once you're touching the `epistemic/` layer (or anything reporting a
logical/statistical result), keep these axes **separate fields** —
never collapse them into one confidence number or one boolean:

- `evidence_kind` (`exhaustive_finite` / `numerical_sample` /
  `analytic_argument` / `empirical_evaluation` / `not_evaluated`) vs.
  `empirical_status` (`not_tested` / `synthetic_only` /
  `evaluated_on_declared_data`).
- `search_complete` (this specific conclusion is certain) vs.
  `all_candidates_scanned` (the whole declared domain was actually
  scanned) — a two-witness early exit can make the first `True` while
  the second is `False`.
- A budget abort (`search_complete=False`) never implies minimality,
  completeness, or universal validity. Say so explicitly in the result.
- A `numerical_sample`/`grid_of_continuous_space` result is never
  silently upgraded to `exhaustive_finite`/`entire_finite_space`.
- Underdetermined and contradictory results are expected scientific
  outcomes, not bugs — a passing regression test can (and should)
  assert one of these on purpose.

## Practical notes

- `python scripts/run_verification_suite.py --category {math,data,all,links}`
  is the single source of truth for "does the repo still work" — it's
  also what CI runs (`.github/workflows/verify.yml`).
- Dual license: source code is GPLv3+, documentation is CC BY 4.0 (see
  `LICENSE` / `LICENSE-DOCS`). Keep new files consistent with whichever
  they are.
- Full chronological project history and every past audit/review
  outcome lives in [`HISTORY.md`](HISTORY.md) — read it for context, but
  don't grow the README back into it.
