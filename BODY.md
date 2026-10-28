#2814: a diagnostics download labelled its last-cycle sections with the moment they were published, not the moment the download was taken. Three residues were left by #2824, which already measured the plan's age at the export and carried the export time:

- **the input ages.** `InputReader` now stamps `InputHealth.read_at` — the instant it measured the ages from — and the payload publishes it as `input_ages_at`. `diagnostics._inputs_at` adds the time from that instant to the export clock to `input_ages_minutes` and to every `input_problems[].age_minutes`. A missing instant, or one ahead of the export clock, leaves them as published: an instant the clock cannot place is unknowable, never zero.
- **`plan_stale`.** `plan_stale_limit_minutes(config)` is one total module function — three intervals floored at 90 minutes, `None` when the config carries no readable `optimization_interval`. The coordinator's `_plan_is_stale` uses it, and the download re-judges at the export with the coordinator's live config, keeping the payload's verdict only when the limit is unreadable.
- **the stored self-tests' run time.** `DebugCollector` sets `self_tests_at` when `_async_finish` stores the results, persists it beside them in the debug document (`store.py`'s DOMAINS gains `self_tests_at`), clears it when a collection restarts, and `async_bundle`'s manifest states both it and `self_tests_age_hours` at the export.

`_plan_is_stale` also loses its early return — an unknown age and an unknown limit are one comparison — which is one class line fewer than before this branch (the ratchet below). `diagnostics._stale_limit`, the first cut's `try/except` wrapper, is gone: the limit's totality lives in the one function both callers use.

Of the two consistent answers the brief allowed, the third pass took the export instant, because the module's own contract already states it (`diagnostics.py`'s module docstring: "the input watchdog's view is judged at the export — every age, `problem_messages`, `input_health` and `stale_inputs`; `plan_stale` is judged at the export by the coordinator's own limit"). `_judged_inputs` now re-renders `problem_messages` from the re-based entries, promotes a class to `stale` when its re-based age passes its own published `max_age_minutes` (`_over_age`, `_aged_problem`) unless the class is in `inputs.OUTRANKS_STALE`, and renders `input_health` from those sets. `inputs.health_summary` gives the wording one owner, shared with the diagnostic entity's `stale_summary`.

This pass closes the round-3 review's block, `mutation-vacuous` on `_over_age`'s implausible exception, and its non-blocking note that the harness was not landed. Mutant N1 (`problem.get("problem") != "implausible"` replaced by `True`) passed all 153 checks at `df1ee7b43`. Writing the failing check for it found the cause one level down. The reader states the precedence of a fault code over staleness twice and inconsistently. `InputReader.read` sets `implausible` after the age gate, so it replaces `stale`. `InputReader.read_flow_kg_s` sets it only on a reading not already stale. So a polling flow meter reading negative past its 30-minute limit read `stale` while a -127 degC temperature read `implausible`, and the export, which re-judged by `read`'s rule alone, disagreed with a re-read of the same flow-meter state. The ordering (age gate first) is not the defect. Recording the age before the fault is found is what puts an implausible input's age into `input_ages_minutes`, and reordering would drop it. The defect is a precedence stated by statement order in each arm. `inputs.OUTRANKS_STALE` now names it once (`frozenset({"implausible"})`). `inputs._set_problem` applies it at both arms that set `implausible`, and `diagnostics._over_age` reads the same constant instead of restating the literal. The flow meter's reading feeds `thermal_output_kw` only through `flow.value if flow.ok`, and `ok` is False in both classes, so no numeric path moves; only the class the watchdog publishes for a stale negative flow does (`stale` → `implausible`, counted missing rather than stale). That class was pinned by R9-UX-9's `tests/features.py` check ("a stale negative reading stays \"stale\" (the age outranks the value)"), which recorded the flow arm's order when the flow arm landed (`5ea502bc8`, after D1-s5-52's rule in `read`, `3e9f1878b`). No ruling chose it, so this pass moves the pin to the one precedence and keeps `stale` pinned through a class that defers (a stale unknown unit). The reversal is flagged to the orchestrator as a decision.

## Re-cut

Replaced at the fourth review round (`fixer.md`, "Past three rounds"): the round-3 review blocked `df1ee7b43` `mutation-vacuous` on `_over_age`'s implausible exception and noted the reviewer's harness was not landed. This body carries the template's headings, the arms that fire, and only figures re-taken in this pass at `da84ae83aa8d16f0ea6cdc4cadf94a8bd5a6ac46` and `c4c29bf100504b5ab67f505061a05a61f35dd5ab`; the earlier rounds' figures are deleted, not restated, and their heavy-run results are CI's at this head.

## Head

`c4c29bf100504b5ab67f505061a05a61f35dd5ab` is this pass's code head, pushed to `handoff/r10-diag-ages`. It is three commits on the reviewed head `df1ee7b4326fc721546c332d6587be28733f2ceb`: `a3a4a78c92831679c21cb596fdd2496489d5a679` (the fix, the census and the landed harness) and `da84ae83aa8d16f0ea6cdc4cadf94a8bd5a6ac46` (`ci_predict --apply-inert`'s `tests/closures.json` entry for the harness, and the deletion of the flow guard's stale `killed_by` pin), and `c4c29bf100504b5ab67f505061a05a61f35dd5ab` (`tests/features.py`'s R9-UX-9 flow pin, the one red the local scope runs found; it touches no other file, `git diff --stat da84ae83a..c4c29bf10` prints `tests/features.py` alone). Every figure below was measured at `da84ae83aa8d16f0ea6cdc4cadf94a8bd5a6ac46` unless it names `c4c29bf10` or another head; the code `c4c29bf10` adds is a test file, so the production and `tests/debug_collect.py` figures hold at it. The merge base is `e8cb7e68302b1d350bb8219fea99e911170af030` (`git merge-base origin/main HEAD`); all comparisons are three-dot against it. origin/main was `53c4b9cb0de45bbfadb19ea6adbe15dd7d7034e1` at `2026-10-28T03:33Z` (`git rev-parse origin/main` after `git fetch`, `date -u`); `git merge-tree --write-tree origin/main HEAD` reported no conflict, so this head does not merge main and `update_pr.sh` does.

## Mutation proof

This pass, driver `tests/debug_collect.py`, each mutant applied to a copy of the tree (`mutants.py <tree> <out> <name>`, sha1 `d9f69e21b385c8cfaeb0a3725845b7e89719186d`, out of tree), the suite run with `PYTHONPATH=tests/hastub`, the copy deleted. The seven `FAIL a16:*` lines in every run are the suite's own planted-defect controls; the counts below exclude them.

| mutant | tree | result | the checks that go red |
|---|---|---|---|
| NULL (unmutated copy) | `da84ae83a` | `ALL 158 DEBUG COLLECT CHECKS PASSED` | none |
| the reviewer's N1, `!= "implausible"` → `True` | `df1ee7b43`'s production files plus this pass's `tests/debug_collect.py` | `2 of 158` FAILED | "an implausible input re-based past its own limit stays implausible at the export…", the census's re-read check |
| N1 on this head's text, `not in OUTRANKS_STALE` → `True` | `da84ae83a` | `2 of 158` FAILED | the same two |
| M2, `OUTRANKS_STALE = frozenset()` | `da84ae83a` | `2 of 158` FAILED | the same two (the census also asserts its exported classes are exactly `{implausible, stale}`, so an empty rule is not read as agreement) |
| M3, `_set_problem`'s `or problem in OUTRANKS_STALE` dropped | `da84ae83a` | `1 of 158` FAILED | the census's re-read check |
| M4, `read_flow_kg_s` reverted to `if reading.problem is None:` | `da84ae83a` | `1 of 158` FAILED | the census's re-read check: flow row `exported implausible, reread stale` |
| M5, the export's exception keyed on a class no reader sets | `da84ae83a` | `2 of 158` FAILED | the same two as N1 |
| L1, the ledger's `GUARD_OFF` at the site this diff adds (`_set_problem`'s guard → `if False:`) | `da84ae83a` | `3 of 158` FAILED | the census's coverage, re-read and null checks |
| the reviewer's N2 (never promoted to stale) | `da84ae83a` | `2 of 158` FAILED | the limit-boundary check, the census's re-read check |
| the reviewer's N3 (age not re-based) | `da84ae83a` | `6 of 158` FAILED | the re-base, one-age, limit-boundary and implausible checks |

Failing first: the round-2 production files (`diagnostics.py`, `inputs.py` from `df1ee7b43`) with this pass's tests and no mutation read `1 of 158 DEBUG COLLECT CHECKS FAILED`, the census's re-read check on `implausible/flow_meter_entity` (`exported implausible`, `reread stale`). The fix is what turns it green.

## Null control

This pass, at `da84ae83a`:

- The implausible check's null is the same entry exported inside its limit (`timedelta(minutes=10)`, age 20 against 30). It reads `implausible`, `stale_inputs []`, `1 missing` and "sensor.indoor: outside its plausible range", the same as 40 minutes late (age 50), so the check is about the crossing. N1 moves only the past-limit arm.
- The census's null is each row exported at its publish instant. Every row reads the class it was published with.
- The census asserts its own preconditions and refuses on them. Each row must publish its class with age 5.0 and a numeric limit, and a row without a limit must be in `_UNBOUNDED_ROWS`, which is empty. The class literals `ast` finds assigned to `.problem`, or passed to `_set_problem`, in `inputs.py` must equal the driven classes plus `{not_configured, missing_entity, unavailable, not_numeric}` (set before the age gate) plus `stale`. They must also include every key of `PROBLEM_WORDS`. A new class therefore turns the census red until it is driven. The first run showed the preconditions working: four rows on keys with no limit (on-change sources) were refused by the precondition check before any comparison counted.
- The landed harness's R9 null: the flow meter and the temperature read one minute after the last report both read `implausible` at the base, at `df1ee7b43` and at this head.

## Figures

This pass, measured at `da84ae83aa8d16f0ea6cdc4cadf94a8bd5a6ac46` unless a line names another head (`PATH` with `$HOME/.local/state/hpo/venv-ci/bin` first, Python 3.14.7):

- `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` → `ALL 158 DEBUG COLLECT CHECKS PASSED` (153 at `df1ee7b43` plus the five this pass adds: the implausible check, its null, the census's coverage, re-read and null checks).
- Mutants: the table in `## Mutation proof`; runner `mutants.py` sha1 `d9f69e21b385c8cfaeb0a3725845b7e89719186d`, its printed `RESULT` lines kept out of tree beside it (`mut/results-head.txt`, `mut/results-oldprod.txt`).
- The landed harness `dev/audit/harnesses/r10_diag_ages_export.py`, run as `PYTHONPATH=tests/hastub python3 <harness>` from each tree. The tree is a `git archive` export at the merge base `e8cb7e683`, `df1ee7b43`'s production files, or this head. The source is the reviewer's `harness.py`, sha1 `bb7436b6c4db85b7e7121ffee16cbd197545a4a1`. Its `RESULT R1`–`R8` lines are byte-identical to the round-3 reviewer's recorded runs at `e8cb7e683` and at `df1ee7b43`, and identical between `df1ee7b43` and this head (`diff <(grep '^RESULT R[1-8]' a) <(grep '^RESULT R[1-8]' b) && echo IDENTICAL`, each printed `IDENTICAL`). R9 reads:
  - `R9.flow_negative.read_past_limit`: `stale` at `e8cb7e683` and at `df1ee7b43`, `implausible` at this head; `R9.temperature_minus_127.read_past_limit` `implausible` at all three;
  - `R9.implausible_exported_past_limit`: `{"problem": "implausible", "stale_inputs": [], "input_health": "1 missing"}` at all three, and `{"problem": "stale", "stale_inputs": ["flow"], "input_health": "1 stale"}` under N1 at `df1ee7b43`;
  - `RESULT checks: 34` at all three.
- Seam enumeration (step 8): `git grep -n -E 'problem *= *"|_set_problem\(|"problem": *"stale"|== *"implausible"|!= *"implausible"|OUTRANKS_STALE' -- custom_components` returns 16 sites in `inputs.py` and `diagnostics.py`, plus `config_flow.py:2111`, an unrelated local named `problem`:
  - `not_configured`, `missing_entity`, `unavailable` (in `_begin`) and `not_numeric` are set before the age gate. They carry no age, so the export has nothing to re-base. Already guarded: `_over_age` needs a numeric age.
  - `stale` (both `_age_gate` arms) is the class itself.
  - `implausible` in `read` and in `read_flow_kg_s`: closed in this diff, both through `_set_problem`.
  - `unknown_value` (`read_state`), `not_boolean` (`read_bool`) and `unknown_unit` (`read_power_kw`, and the flow arm's other branch) defer to `stale` by their `reading.problem is None` guard, which is `_set_problem`'s rule for a class outside `OUTRANKS_STALE`. Already consistent, and pinned by the census rows that drive each.
  - `diagnostics._over_age` and `_aged_problem` are the one re-judging site, closed in this diff.
  The census is the standing instrument for the class: it re-runs this enumeration as an `ast` scan and refuses a class it does not drive.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED` (recorded_at `6fe5170cd7ce`); no budget file is touched.
- `python3 tools/audit/archscore/score.py --diff e8cb7e683` → `Architecture score: dS +0.0012 IMPROVES`, `coord_footprint 2412 -> 2410`, rc 0. `--diff df1ee7b43` → `dS +0.0000 NULL`: this pass's delta is score-neutral.
- `python3 tools/pr/ci_predict.py --base origin/main` → `no closures, fast, wave-script or instrument red predicted against e8cb7e68302b`, one `ADDED UNPINNED` warning (`## Unpinned sites`). Before the second commit it predicted the `INERT READS` entry for the harness and a `STALE PIN` on `InputReader.read_flow_kg_s GUARD_OFF 1d38d74f`. The second commit repairs both.
- `python3 tests/closure.py select --diff e8cb7e683 --workdir $D` → `MODE: SCOPED -- 27 script(s) run, 6 scoped out`. The scope scripts run locally at this head are in `## Red checks`. Every script in `scope.run` that is not named there is left to CI's heavy runs at this head.
- `python3 tests/env_drift.py --claims-only e8cb7e683` → `claims hygiene: e8cb7e683 ok`. `git diff --quiet e8cb7e683...HEAD -- VERSION RELEASE_NOTES.md tests/golden custom_components/heatpump_optimizer/manifest.json && echo UNTOUCHED` printed `UNTOUCHED`.

## Architecture score

This pass at `da84ae83a`: `--diff e8cb7e683` → `dS +0.0012 IMPROVES`, and `--diff df1ee7b43` → `dS +0.0000 NULL`. The constant and the 3-line `_set_problem` replace a literal restated in `diagnostics.py` and a nested guard in `read_flow_kg_s`. No coordinator method is added (`tests/seam_map.json` untouched). Alternatives considered:
- reorder `read` so the plausibility check runs before the age gate: refused, because it drops an implausible input's age from `input_ages_minutes` and leaves the flow arm's reverse precedence in place;
- keep the export's literal and only add the check: refused, because the reader would still state two precedences for one class name, and the export can follow only one of them;
- withhold the age on an implausible reading so the export cannot relabel it: refused, because it loses evidence a user reads.

Measured at `796146175`: `python3 tools/audit/archscore/score.py --diff 67178dc6a589cf95d2ce7cff36d8bbf17343e8dc` → `Architecture score: dS +0.0012 IMPROVES`, `coord_footprint 2412 -> 2410`, rc 0. No rise to explain: the three helpers this pass split `_inputs_at` into are charged as functions, and `_inputs_at`'s own complexity fell with them; `health_summary` replaces the wording `stale_summary` used to hold, so the coordinator footprint does not grow. The gate's `tests/arch_score_head.py` at the same head prints `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`.

## Red checks

This pass: no check has run on these heads before this push. Scope scripts run locally (`PYTHONPATH=tests/hastub python3 tests/<s>.py`, at `da84ae83a` unless named), each with its last line:

- `tests/debug_collect.py` (rc=0, 2s): `ALL 158 DEBUG COLLECT CHECKS PASSED`
- `tests/guard_pins.py` (rc=0, 1s): `ALL 61 GUARD PIN CHECKS PASSED`
- `tests/finite_boundary.py` (rc=0, 108s): `ALL 108 FINITE BOUNDARY CHECKS PASSED`
- `tests/harness_headers.py` (rc=0, 582s): `ALL 112 HARNESS HEADER CHECKS PASSED`
- `tests/validate.py` (rc=0, 64s): `NO ISSUES`
- `tests/typing_ruler.py` (rc=0, 0s): `ALL 11 typing-ruler source checks PASSED`
- `tests/edge.py` (rc=0, 41s): `ALL EDGE CASES PASS`
- `tests/config_flow_steps.py` (rc=0, 27s): `ALL 505 checks PASSED`
- `tests/deployment_shape.py` (rc=0, 4s): `ALL DEPLOYMENT SHAPE CHECKS PASSED`
- `tests/doc_claims.py` (rc=0, 10s): `ALL 203 checks PASSED`
- `tests/features.py` at `da84ae83a`: `1 of 4519 FEATURE CHECKS FAILED`, "a refused flow reading's health record keeps its first reason (stale, implausible, unknown unit) and no value", reading `(('implausible', None), ('implausible', None), ('unknown_unit', None))`: R9-UX-9's pin of the flow arm's old order, the defect this pass removes (see the intro). Re-run at `c4c29bf10` with the pin moved: `ALL 4519 FEATURE CHECKS PASSED`, rc 0, 590 s. Its null control is out-of-tree probe `flow_pin_probe.py` (sha1 `83c31efe9b98590510d81a7265e0d8d54180ed76`), which is the block's `_fm_reader` and the checks through the moved pin, copied verbatim. At `c4c29bf10` it reads `ALL 11 FLOW PIN PROBE CHECKS PASSED`. Under M4 (the flow arm reverted) it reads `1 of 11`, the moved pin, red with `(('stale', None), ('implausible', None), …`. This red fired locally, on no pushed commit. The cheaper detector is the one that caught it: the local scope run, before the push.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` at `da84ae83a`: `no refusal`, `PRE-PR: da84ae83aa8d16f0ea6cdc4cadf94a8bd5a6ac46`, rc 0, 780 s; its one `WARN` is the unpinned site below.
- Not run locally at this head, left to CI's heavy runs: `tests/arch_score_head.py`, `tests/backtest.py`, `tests/block_duty.py`, `tests/boost_drift_replay.py`, `tests/entities.py`, `tests/env_drift.py`, `tests/golden.py`, `tests/manual_plan.py`, `tests/optimality.py`, `tests/plan_view.py`, `tests/card.mjs`, `tests/card_drift.mjs`, `tests/solar_alignment.py`, `tests/stress.py`, `tests/wood_advisor.py` (`tests/structure.py` is in `## Figures`).

Reds that fired on earlier commits of this branch, each answered (`defect-root-cause.md`'s second trigger):

- `governance / wave-script` at an earlier head: a transient checkout error in its own runner, green on its immediate re-run at `e73ff68ca`. Cheaper detector: none — the failure was the runner's, not the tree's.
- `pr-contract` at an earlier head: body staleness after a head moved, the arm `body_push.sh`'s ordering and `update_pr.sh`'s `## Head` prefix exist for. Cheaper detector: `prepr.sh` step 7, run before this push.
- `tests / closures` `INERT READS` and `tests / mutation` unpinned sites at earlier heads: answered by naming them (`ci-autofix.md`); this pass repaired its own before the push (`ci_predict.py`, `## Figures`).

## Unpinned sites

This pass adds one site against merge base `e8cb7e683`:

- `custom_components/heatpump_optimizer/inputs.py:139 GUARD_OFF` (`_set_problem`'s guard, `if reading.problem is None or problem in OUTRANKS_STALE:`): killed by `tests/debug_collect.py`, which reads `3 of 158` red (mutant L1, `## Mutation proof`). It is pinned by `mutation-autofix` on this push; `--pin-killed` is that lane's (`ci-autofix.md`), not run here.

It removes one pin. `tests/mutation_ledger/killed_by/inputs.py/InputReader.read_flow_kg_s.GUARD_OFF.1d38d74f.json` pinned the line `if reading.problem is None:` in `read_flow_kg_s`, which this diff replaces with the `_set_problem` call. `ci_predict.py` predicted it as a `STALE PIN`, which `mutation-autofix` never drops, so it is deleted by hand. The same guard now lives at the site above.

The eight sites the earlier passes added are pinned under `tests/mutation_ledger/killed_by/` by `--pin-killed`, each killed by `tests/debug_collect.py`; no `survivor_triage` exists for any:
- `custom_components/heatpump_optimizer/diagnostics.py:_over_age CMP_BOUND d78a836d`: pinned by the limit-boundary check "an input's own limit is the boundary…".
- `custom_components/heatpump_optimizer/diagnostics.py:_aged_problem RETURN_DEL 010d6d58`: pinned by the same boundary check and the one-age check.
- `custom_components/heatpump_optimizer/inputs.py:health_summary BOOLOP d691c829`: pinned by "the shared summary wording names each class present and ok for neither".
- `custom_components/heatpump_optimizer/inputs.py:health_summary GUARD_OFF d691c829`, `GUARD_OFF 387cd81c`, `GUARD_OFF 998e1ddb`, `RETURN_DEL 66df18ca`: pinned by the same shared-wording check, and the two class arms by the diagnostic entity's summary check too.
- `custom_components/heatpump_optimizer/inputs.py:stale_summary RETURN_DEL 1a761154`: pinned by "the diagnostic entity's summary counts each failure class, and reads ok with neither".

## Forward-carry

1. `tests/entities.py`'s py-spy stub sizes its call log with `case $(wc -l < calls) in 1)`, and BSD `wc -l` reading stdin pads the count to eight columns, so on macOS the `1)` arm never matches and four `hb:positive_control` checks read red. Control: `printf 'x\n' | wc -l` on this host prints `       1`; the same four checks read red at merge base `6fe5170cd` in the round-1 session's baseline log, so the branch under review is not the cause. Precondition for any fix: compare a trimmed count (`tr -d ' '`) so GNU and BSD agree, and keep a planted-defect control that still reads red, so the check is not merely silenced. Re-measure at your own merge base. `tests/entities.py` is outside this group's seam; the group that owns it is open. Carry: R10-FLY-SUITE-ENV-FLAKES

## Friction

- dev/governance/roles/fixer.md#3: unclear: "an instant ahead of the clock is unknowable, never 0" fixes the age arithmetic but says nothing about the `plan_stale` verdict at such an instant; this branch keeps the payload's verdict where the limit is readable and the age is not, which follows the payload rather than the clock. Carry: dismissed: the payload's `plan_stale` was computed by the coordinator at publish, so it is the only defensible answer when the export clock cannot date the plan.
- gate-scoping.md: cost: four wedged `prepr` runs held every heavy-slot lease for the pass at `37e10fa4b` (`prepr-72444`, `prepr-91597`, `prepr-99026`, `run.sh-39229`), so `harness_headers.py`, `golden.py` and the scoped gate could not run locally there. Carry: dismissed: the orchestrator's `PREPR WEDGE` directive clears the leases and runs the pushes serially; a local re-run behind them would queue, not measure.
- gate-scoping.md: cost: the scoped gate at `796146175` ran `5857s`, and the exclusive lease is 30 minutes; `run.sh` renews per script only while a lease is live, so `stress.py` and `harness_headers.py` found none and refused, and each had to be re-run by hand at this head. Measured: `gate_lock: flock-wrap refused, fix-2873-r2-blocked holds no lease: no live gate lease to renew` on both. Carry: dismissed: the re-runs are the cheaper detector and were paid once — `ALL 112 HARNESS HEADER CHECKS PASSED` and `1 of 113` — so the cost is one re-run of two scripts on a gate longer than the lease, not a mechanism worth building for a lane that runs the suite in a fraction of that time on CI.

- dev/governance/roles/fixer.md#2: unclear: the reviewer counted its block as round 3 and `bus.sh three_rounds` counts the blocked commits on `verdict/2873` (1 at `8e5accc3c`), so the two disagree on whether this pass owes a re-cut; this body re-cuts, which satisfies both. Carry: dismissed: a re-cut body is valid under either count.
