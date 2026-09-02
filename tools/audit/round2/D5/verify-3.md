# D5 — verifier seat 3 of 3 (perturbation and fix scope)

Baseline `c398fc84eec25fc44b60d74aae05b9a2da205884`, export
`audit-r2-baseline` (read-only; this file is the one write). Harnesses re-run
once from the export root with `PYTHONPATH=tests/hastub` and the
`tvofi-claude/.venv` interpreter: every RESULT matched the finder's header
exactly (`load1` 1.92, `thread_factor` 1.000–1.005; all counts, so contention
is informational). Perturbations were applied to a full copy of the export at
`/tmp/verify-D5-3/tree`, one file at a time, restored after each run; a
source-level `diff -r` (excluding `__pycache__`) between export and copy is
empty at the end. My own harness is `/tmp/verify-D5-3/verify3.py` (ast/json/
regex only; reads the export, writes nothing). No solver, test suite or timing
was run. Noted in passing: `tools/audit/round2/quiet/D0-race_grid.log` in the
export changed during this session — another agent's write, not mine.

Vote key: verify | weaken(severity) | refute, each with the executed number.

## D5-01 · tests/README.md drift — **verify (low)**, 7 → 6 as predicted

- **Harness re-run:** `tests_readme_drift=7` (`doc_fact_checks_failed=15`,
  `dead_ends_developer=8`).
- **My number: 7.** Metric: number of the seven cited tests/README.md
  statements (l.129, 221, 228/457, 285, 355, 487, 505) whose stated path, count
  or roster differs from the value computed independently from
  `closure.py:INERT`/`NOT_A_TEST` (ast literal), `closures.json` readers,
  `tests/golden/*.json` (55; `coord_*` 5), `golden.py:SCENARIOS` keys (49),
  `plan_view.py`'s `plandata-%s.json`, `validate.py` `^run(` sites (22) and
  `tests.yml`'s `card_browser.mjs` job. All seven differ (T1: README.md and
  RELEASE_NOTES.md are read by `entities.py`, the three brand images by
  `env_drift.py` and `golden.py`, and none of the five is in INERT).
- **Perturbation (executed):** `53 fixtures (47 plan scenarios` →
  `55 fixtures (49 plan scenarios` on the copy: T2 passes,
  `tests_readme_drift` **7 → 6**, `doc_fact_checks_failed` 15 → 14,
  `dead_ends_developer` 8 → 7 (T3 "all 53 scenarios" still fails, as it
  should). Finder's negative control also holds: adding `"README.md"` to
  `closure.py:INERT` leaves T1 failing and the count at 7.
- **Scope — incomplete by two statements.** The harness (T1–T7) misses two
  same-class rosters in the "What it actually saves" table, verified with
  `closure.py select --files …` on the copy (pure computation over
  `closures.json`, no scripts run):
  - l.103 "a change to `tests/card.mjs` → 2 — `plan_view.py`, `card.mjs`":
    select runs **3** (`card.mjs`, `card_drift.mjs`, `plan_view.py`).
  - l.104 "a change to the card's JavaScript → 6 — …": select runs **7**
    (adds `card_drift.mjs`).
  Consistent with `closure.py`'s own note that `card_drift.mjs`/`dom_stub.mjs`
  wiring changed between v6.1.2 and v6.2.7. Rows l.102 (1 — `entities.py`),
  l.105 (4), l.106 (14, everything but `frontend.py`/`open_meteo.py`),
  l.164/167 (`stress.py` closure 61 files), l.224/398 (48/17), l.448 (300
  perturbations), the "five sensitive fixtures" and "1 of 16" are correct.
  Minor: the "Four files" section runs l.487–503 (the `closure.py` and
  `derive_closures.sh` bullets), not l.487–495. Fixing exactly the finder's
  listed lines clears the harness (7 → 0) but leaves l.103–104 wrong; the fix
  should add them. The CI-seconds column is not checkable here.

## D5-02 · ECL110 "leave blank" vs non-empty defaults — **verify (low)**, 1 → 0 as predicted

- **Harness re-run:** `ecl110_guidance_contradiction=1`.
- **My number: 1** (contradiction), with **8 places** carrying the guidance.
  Metric: 1 if both `DEFAULT_ECL110_*_TOPIC` literals are non-empty AND
  `coordinator.py` awaits `async_publish_current_action(reason="scheduled_update")`
  in the per-cycle actuation step AND `async_publish_ecl110_command` returns
  early only when both topics are empty AND at least one user-facing text tells
  a non-owner to leave the topics blank / rely on the defaults; the number of
  such texts is reported beside it. Reachability checked by reading:
  `_apply_action` (coordinator.py:6519) is awaited at :4403 in the update
  cycle; `_current_action` is assigned on every path (:4372/4382/4392/4785)
  so the only early return in `async_publish_current_action` does not fire
  after the first cycle; the options form pre-fills both fields with the
  non-empty defaults (config_flow.py:2343–2352), so "leave blank" describes a
  field that is not blank. The runtime consequence (`ServiceNotFound` caught by
  `except Exception` → `_LOGGER.error` every interval without MQTT) is D6/D10's,
  not scored here.
- **Perturbation (executed):** both defaults set to `""` on the copy: E1
  passes, `ecl110_guidance_contradiction` **1 → 0**, `doc_fact_checks_failed`
  15 → 14. (Cosmetic: the harness's E1 detail string still prints "(non-empty)"
  beside the empty literals.)
- **Scope — incomplete: the options page itself is missing.** The finder's fix
  scope names configuration.md l.70 and l.457 plus one README sentence. The
  same guidance is shipped in the product text the non-owner actually reads on
  the pre-filled form: `strings.json:464` ("Leave these blank if you do not
  have one") and `:477` ("Leave blank if you do not have a Danfoss ECL110"),
  mirrored in `translations/en.json:464,477` and `translations/sv.json:464,477`
  ("Lämna tomt om du inte har en sådan / … ECL110"). Six strings in three
  files (two source strings and their translations) must change with the docs,
  or the contradiction survives in the UI. README's ECL110 section (l.599–606)
  carries no leave-blank claim — the README sentence is an addition, not a
  repair. `docs/ecl110.md:79–82` is correct as the finder says.

## D5-03 · unreachable documents — **verify (low)**, 3 → 2 as predicted; fix scope corrected

- **Harness re-run:** `unreachable_docs_from_readme=3`.
- **My number: 3.** Metric: `.md` files outside `tools/` (11 in the export —
  the same 11 the finder used, so the set is complete) not reachable from
  README.md following inline, reference-style, `<…>` autolink and `href=`
  links, each resolved relative to the linking file. Unreachable:
  `docs/plan-card-decomposition.md`, `docs/plan-open-issues.md`,
  `tests/README.md`.
- **Perturbation (executed):** one `tests/README.md` row in README's
  Documentation table on the copy: R1 passes, **3 → 2** (R2 still fails on the
  two plan documents), `failed_in[README.md]` 2 → 1.
- **Scope — the finder's "→ 0" step is wrong; three links are needed.** With
  the `tests/README.md` row *and* a `docs/plan-card-decomposition.md` link the
  count is **1**, not 0: `plan-open-issues.md` stays orphaned. It reaches 0
  only with a third link to `docs/plan-open-issues.md`. Neither plan document
  contains a markdown link to any `.md` (out-links: none), and neither links
  `tests/README.md` — they name it in backticks
  (plan-card-decomposition.md:252,267; plan-open-issues.md:113,220). So the
  mechanism sentence "the only inbound links to tests/README.md are from the
  two plan documents" is inaccurate: in-links to tests/README.md are **0**.
  The number (3) is unaffected. architecture.md names `tests/features.py`
  (l.147) and `tests/entities.py` (l.211) without a link to tests/README.md,
  as claimed.

## D5-04 · five content defects — **verify (low)**, 5 → 4 as predicted

- **Harness re-run:** `content_defects_user_docs=5`.
- **My number: 5.** Metric: five independent checks — H1: prose lines > 100
  chars outside fences in how-it-works.md (one: l.1189, 134 chars); H2: the
  fragment "may move within follow" present; S1: highest version cited under
  "## Project status" (v5.0.0) has a major below `VERSION` (6.2.14); C6:
  "throttling" used 8× in configuration.md with no defining sentence in any of
  the eight user docs; ST1: heading depth skip, fence-aware, over all eight
  docs (one: dashboard-card.md:31 h1→h3). All five fail. Read l.1185–1192: the
  finder's reading that "Without it" now points at the fall-through rather
  than the reason code holds.
- **Perturbation (executed):** sentence repair at how-it-works.md:564 on the
  copy (moving "the" so the clause reads "the range the learning may move
  within / follow the tank's surface area", both lines under 80 chars): H2
  passes, `content_defects_user_docs` **5 → 4**, `doc_fact_checks_failed`
  15 → 14; H1 unchanged, as it should be.
- **Scope — one more instance of the H1 class outside the finder's scan.**
  The finder's H1 scans how-it-works.md only; the same fence-aware scan over
  all eight user docs adds `tests/README.md:155` (101 chars, prose in a
  paragraph wrapped at ~76) — marginal, developer path. Heading skips across
  all docs: 1 (the finder's). A doubled-word probe (`\b(\w+)\s+\1\b`) over all
  eight docs: 0. The proposed C6 clause ("any mixing-valve mode other than *No
  mixing valve*") satisfies both the finder's regex and mine; a `## ` heading
  before dashboard-card.md:31 clears ST1. Caveat on S1: the check is satisfied
  by any v6.x.y string under Project status, so the fix must actually revise
  the paragraph rather than mention a version.

## D5-05 · comment precision — **verify (low)**, 1 → 0 as predicted (and 1 → 0 secondary)

- **Harness re-run:** `constant_comment_mismatches_vetted=1` (raw 17),
  `loose_missing_vetted=1` (raw 7), `redundant_single_line_comments=11`.
- **My numbers: 1 + 1 + 3.** Metric: (a) `_MAX_PLAUSIBLE_GHI` (1400.0) against
  the 3–4-digit numbers in its attached comment block {1200, 1361}: no match →
  1; (b) `<snake_case> service` phrases in production `.py` text naming a
  service absent from `services.yaml` (11 services): 1
  (thermal_model.py:191 `set_thermal_params`); (c) the three restating
  comments at the stated lines, read directly: coordinator.py:4353 above
  `await self._fetch_tibber_prices()`, optimizer.py:671 inline on
  `savings_percentage: float  # savings as percentage`, thermal_model.py:1830
  above `self.solar_gain_per_zone(...)` — all three present (my script's
  "next-line" test missed the inline one; settled by reading).
- **Perturbations (executed):** `_MAX_PLAUSIBLE_GHI = 1361.0` on the copy →
  `constant_comment_mismatches_vetted` **1 → 0**, raw 17 → 16.
  `set_thermal_params` → `set_thermal_parameters` in the comment →
  `loose_missing_vetted` **1 → 0**, raw 7 → 6.
- **Attack on the vetting:** read all 16 constant ALLOW entries and both
  docstring ALLOW entries against the quoted lines; each reason holds. Two
  (defrost.py:93 "less than half" beside 0.55; :120 "a third" beside 0.3) are
  the same class as the GHI item — a bound stated in prose that the constant
  does not enforce — and the finder disclosed them as roundings not counted.
  A stricter reading gives 3 rather than 1; the class and severity do not
  change. Of the 11 redundancy hits, the 8 not counted are section labels or
  `#:` attribute docs — agreed by reading.
- **Scope — complete.** `set_thermal_params` (short form) appears nowhere else
  in production, tests, docs or the card (only in the audit's own files); no
  other `<name> service` phrase names a missing service. Five edits in four
  files clear everything measured.

## Summary

| id | harness re-run | my number | perturbation | scope | vote |
|---|---|---|---|---|---|
| D5-01 | 7 | 7 (9 with l.103–104) | 7 → 6 ✓; control held | incomplete: add tests/README.md l.103–104 | verify (low) |
| D5-02 | 1 | 1; 8 places | 1 → 0 ✓ | incomplete: strings.json:464,477 + en/sv translations | verify (low) |
| D5-03 | 3 | 3 | 3 → 2 ✓ | fix needs 3 links, not 2; "→ 0" claim and in-link sentence wrong, number right | verify (low) |
| D5-04 | 5 | 5 | 5 → 4 ✓ | one more H1-class line at tests/README.md:155 | verify (low) |
| D5-05 | 1 (+1, 11) | 1 + 1 + 3 | 1 → 0 ✓; 1 → 0 ✓ | complete | verify (low) |

No harness was void: every number moved in the predicted direction under the
finder's stated edit on a copy, and every number was reproduced by an
independently written check.
