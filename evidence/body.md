#2814: a diagnostics download labelled its last-cycle sections with the moment they were published, not the moment the download was taken. Three residues were left by #2824, which already measured the plan's age at the export and carried the export time:

- **the input ages.** `InputReader` now stamps `InputHealth.read_at` — the instant it measured the ages from — and the payload publishes it as `input_ages_at`. `diagnostics._inputs_at` adds the time from that instant to the export clock to `input_ages_minutes` and to every `input_problems[].age_minutes`. A missing instant, or one ahead of the export clock, leaves them as published: an instant the clock cannot place is unknowable, never zero.
- **`plan_stale`.** `plan_stale_limit_minutes(config)` is one total module function — three intervals floored at 90 minutes, `None` when the config carries no readable `optimization_interval`. The coordinator's `_plan_is_stale` uses it, and the download re-judges at the export with the coordinator's live config, keeping the payload's verdict only when the limit is unreadable.
- **the stored self-tests' run time.** `DebugCollector` sets `self_tests_at` when `_async_finish` stores the results, persists it beside them in the debug document (`store.py`'s DOMAINS gains `self_tests_at`), clears it when a collection restarts, and `async_bundle`'s manifest states both it and `self_tests_age_hours` at the export.

`_plan_is_stale` also loses its early return — an unknown age and an unknown limit are one comparison — which is one class line fewer than before this branch (the ratchet below). `diagnostics._stale_limit`, the first cut's `try/except` wrapper, is gone: the limit's totality lives in the one function both callers use.

Of the two consistent answers the brief allowed, the third pass took the export instant, because the module's own contract already states it (`diagnostics.py`'s module docstring: "the input watchdog's view is judged at the export — every age, `problem_messages`, `input_health` and `stale_inputs`; `plan_stale` is judged at the export by the coordinator's own limit"). `_judged_inputs` now re-renders `problem_messages` from the re-based entries, promotes a class to `stale` when its re-based age passes its own published `max_age_minutes` (`_over_age`, `_aged_problem`) unless the class is in `inputs.OUTRANKS_STALE`, and renders `input_health` from those sets. `inputs.health_summary` gives the wording one owner, shared with the diagnostic entity's `stale_summary`.

The fourth pass closed the round-3 review's block, `mutation-vacuous` on `_over_age`'s implausible exception, and its non-blocking note that the harness was not landed. Mutant N1 (`problem.get("problem") != "implausible"` replaced by `True`) passed all 153 checks at `df1ee7b43`. Writing the failing check for it found the cause one level down. The reader states the precedence of a fault code over staleness twice and inconsistently. `InputReader.read` sets `implausible` after the age gate, so it replaces `stale`. `InputReader.read_flow_kg_s` sets it only on a reading not already stale. So a polling flow meter reading negative past its 30-minute limit read `stale` while a -127 degC temperature read `implausible`, and the export, which re-judged by `read`'s rule alone, disagreed with a re-read of the same flow-meter state. The ordering (age gate first) is not the defect. Recording the age before the fault is found is what puts an implausible input's age into `input_ages_minutes`, and reordering would drop it. The defect is a precedence stated by statement order in each arm. `inputs.OUTRANKS_STALE` now names it once (`frozenset({"implausible"})`). `inputs._set_problem` applies it at both arms that set `implausible`, and `diagnostics._over_age` reads the same constant instead of restating the literal. The flow meter's reading feeds `thermal_output_kw` only through `flow.value if flow.ok`, and `ok` is False in both classes, so no numeric path moves; only the class the watchdog publishes for a stale negative flow does (`stale` → `implausible`, counted missing rather than stale). That class was pinned by R9-UX-9's `tests/features.py` check ("a stale negative reading stays \"stale\" (the age outranks the value)"), which recorded the flow arm's order when the flow arm landed (`5ea502bc8`, after D1-s5-52's rule in `read`, `3e9f1878b`). No ruling chose it, so this pass moves the pin to the one precedence and keeps `stale` pinned through a class that defers (a stale unknown unit). The reversal is flagged to the orchestrator as a decision.

This pass (round 5) closes the round-4 review's block, `root-cause-detectable` on `tests / fast (3.14)`. `tests/card.mjs` enumerated the published problem codes with a regex over one assignment form, `reading.problem = "(\w+)"`, and needed at least 8. Round 4 moved `implausible` behind `_set_problem(reading, "implausible")`, so the census read 7 codes and the card's two "every published problem code has words in en / sv-SE" checks stopped covering `implausible`; the floor check was the only one that went red. The repair makes the card enumerate the codes from the authoritative source instead of from a spelling of the assignment: `inputs.PROBLEM_WORDS`, the reader's one table of published classes. Three parts:

- **`tests/card.mjs`** reads `PROBLEM_WORDS`' keys from `inputs.py` as its codes, and refuses any class literal set by either route (`reading.problem = "…"` or `_set_problem(reading, "…")`, `not_configured` excepted) that the table lacks. It then reads each code's own key (`health.stale` for `stale`, `health.p_<code>` otherwise, the card's own mapping in `healthInputsHtml`) from the card's `STRINGS.en` and `STRINGS.sv` tables directly, one check per language. The existing render checks cannot see a missing Swedish word, because `L()` falls back to the English table and the English word is not a raw token.
- **`tests/debug_collect.py`**'s `ast` census, which already finds every class `inputs.py` sets by assignment or through `_set_problem`, now holds `set(PROBLEM_WORDS) == found - {"not_configured"}` (it held `<=`). So the table the card enumerates by cannot drift from the classes the reader sets, by any route: a new class, or a class moved behind a helper, turns the census red until it is worded.
- **`inputs.PROBLEM_WORDS`** gains `"stale": "stale"`, the one published class it lacked. `describe_problem` rendered `stale` through its fallback (`PROBLEM_WORDS.get(problem, problem)`) as the same word, so no output moves; the comment states the table's new role.

## Re-cut

Replaced at the fourth review round (`fixer.md`, "Past three rounds") and re-cut again at this fifth: the round-4 review blocked `75ae7b26f` `root-cause-detectable` on `tests / fast (3.14)` (`tests/card.mjs`'s problem-code census). This body carries the template's headings, the arms that fire, and only figures re-taken in this pass at `060c9bef5`, its test-only parent `d05d521ff`, and the previous PR head `d00790305`; the earlier rounds' figures are deleted, not restated. The production change this pass adds is one dictionary entry and a comment (`git diff --stat d00790305 060c9bef5` prints `inputs.py | 8`, `tests/card.mjs | 23`, `tests/debug_collect.py | 9`), and its heavy-run results are CI's at this head.

## Head

`2fbc91c40c17429702fd0c44a3a80080b3157c60` merges the authored code head `060c9bef5c4b77adc5ee77d50f21bd5c06393fb8` and then merges origin/main `0b8f8b585` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`060c9bef5c4b77adc5ee77d50f21bd5c06393fb8` is this pass's code head, pushed to `handoff/r10-diag-ages`. It is two commits on the previous PR head `d00790305910b5c821c778df00131cdec0deac4f` (round 4's code head `c4c29bf10` plus `mutation-autofix`'s pin, `record-autofix`'s nightly kills and a merge of main): `d05d521ff` (the failing tests: `tests/card.mjs` and `tests/debug_collect.py`) and `060c9bef5` (the fix: `inputs.PROBLEM_WORDS` gains `stale`). The merge base is `edd7e0e14e08279d0ddc53ec4fcc983570edf12a` (`git merge-base origin/main HEAD`); all comparisons are three-dot against it. origin/main was `6349205b6` at `2026-10-28T08:54Z` (`git rev-parse origin/main` after `git fetch`, `date -u`); `git merge-tree --write-tree origin/main HEAD` reported no conflict, so this head does not merge main and `update_pr.sh` does.

## Mutation proof

**Failing first.** At the test-only commit `d05d521ff` (the round-4 production `inputs.py`, this pass's tests):

- `node tests/card.mjs` (after `tests/plan_view.py`): `FAIL inputs.py publishes problem codes the card can be enumerated against`, detail `implausible,missing_entity,not_boolean,not_numeric,unavailable,unknown_unit,unknown_value | set but not in PROBLEM_WORDS: stale`. Both new per-language checks read `ok` there: `implausible` is enumerated again and both tables word it. (That run then aborted on this host's 2 GB default node heap, `FATAL ERROR: … JavaScript heap out of memory`, rc 134, after the census checks; every later card run here sets `NODE_OPTIONS=--max-old-space-size=8192`.)
- `PYTHONPATH=tests/hastub python3 tests/debug_collect.py`: `1 of 158 DEBUG COLLECT CHECKS FAILED`, the precedence census, with `PROBLEM_WORDS ^ published` = `['stale']`.

The fix commit turns both green (the NULL row below).

**This pass's mutants.** Each is applied in place to the committed head `060c9bef5`, both suites are run, and the file is restored by `git checkout` (driver `card_mutants.sh`, out of tree, sha1 `28864e616a8feb472a551a33628499a3935fb28f`). The seven `FAIL a16:*` lines in every `debug_collect.py` run are the suite's own planted-defect controls; the counts exclude them.

| mutant | `tests/card.mjs` | `tests/debug_collect.py` |
|---|---|---|
| NULL (unmutated) | `ALL CARD CHECKS PASSED` | `ALL 158 DEBUG COLLECT CHECKS PASSED` |
| K1, `"implausible"` deleted from `PROBLEM_WORDS` | `1 CARD CHECK(S) FAILED`: the census, `… \| set but not in PROBLEM_WORDS: implausible` | `3 of 158`: the precedence census, the implausible-past-limit check and its null (both read the worded message) |
| K2, the Swedish `health.p_implausible` deleted from the card | `1 CARD CHECK(S) FAILED`: "every published problem code has its own words in the card's sv table", detail `implausible`. The pre-existing "… has words in sv-SE, none prints as a raw token" reads `ok` under it: `L()` falls back to English, which is why the per-table check exists | `ALL 158` (it reads no card file) |
| K3, the English `health.p_implausible` deleted | `2 CARD CHECK(S) FAILED`: "… its own words in the card's en table" and the pre-existing "… has words in en, none prints as a raw token", each detail `implausible` | `ALL 158` |
| K4, `"stale"` deleted from `PROBLEM_WORDS` (the round-4 table) | `1 CARD CHECK(S) FAILED`: the census, `implausible,missing_entity,not_boolean,not_numeric,unavailable,unknown_unit,unknown_value | set but not in PROBLEM_WORDS: stale` (the failing-first reading, reproduced) | `1 of 158`: the precedence census |

**Round 4's mutants, re-taken at `060c9bef5`.** The round-4 reviewer's driver `mutants_r4.py` (sha1 `b301586de6ee1853778ea9be51a4c95d7b82d45d`, unchanged, on a `git archive` copy of `060c9bef5`), against `tests/debug_collect.py`; its RESULT lines equal the reviewer's round-4 table row for row:

| mutant | result |
|---|---|
| NULL | `ALL 158 DEBUG COLLECT CHECKS PASSED` |
| N1, `_over_age`'s `not in OUTRANKS_STALE` → `True` | `2 of 158`: the implausible-past-limit check, the census re-read |
| N1b, `OUTRANKS_STALE = frozenset()` | `2 of 158`: the same two |
| N4, `_set_problem` drops `or problem in OUTRANKS_STALE` | `1 of 158`: the census re-read |
| N5, `_set_problem`'s guard → `if True` | `ALL 158` on `debug_collect.py`; on `tests/features.py`: `FAIL a refused flow reading's health record keeps its reason by one precedence, and no value…`, reading `(('implausible', None), ('implausible', None), ('unknown_unit', None), ('unknown_unit', None))`: killed. Its other FAIL, `recorded_at = 'unknown'`, is the copy having no `.git` (the #363 runner artifact of `fixer.md` step 2) |
| N2, never promoted to stale | `2 of 158`: the limit-boundary check, the census re-read |
| N3, age not re-based | `6 of 158`: the re-base, one-age, limit-boundary and implausible checks |

## Null control

- The card census's null is NULL above: the unmutated head reads `ok` on the census and both per-table checks, so each check's red under K1–K4 is the mutant's. A probe running the card's two regexes over `inputs.py` at `060c9bef5` (`census-probe.txt`, out of tree) prints `PROBLEM_WORDS keys: implausible,missing_entity,not_boolean,not_numeric,stale,unavailable,unknown_unit,unknown_value` and `set by either route: implausible,…,not_configured,…` (the same eight plus `not_configured`), while the round-4 regex over the same file prints the seven without `implausible` plus `not_configured`: the census sees `implausible` again, and the old one would not.
- The `debug_collect.py` census's preconditions are unchanged from round 4 and run in NULL: each row publishes its class with age 5.0 and a numeric limit, `_UNBOUNDED_ROWS` is empty, and the `ast` scan's classes equal the driven classes plus the pre-gate four plus `stale`. Its new equality is what K1 and K4 turn red (a published class the table lacks); NULL is the same check reading `ok` with every class worded.
- The landed harness `dev/audit/harnesses/r10_diag_ages_export.py` (round 4's), run unchanged at `d00790305` and `060c9bef5`: its 36 `RESULT` lines are identical between the two heads but for the `RESULT tree:` path line, the one pair `diff <(grep '^RESULT' harness-prev.txt) <(grep '^RESULT' harness-head.txt)` prints; `RESULT checks: 34` at both, `R9.implausible_exported_past_limit` reading `implausible` at both. The production change moves no export..

## Figures

This pass, measured at `060c9bef5c4b77adc5ee77d50f21bd5c06393fb8` unless a line names another head (`PATH` with `$HOME/.local/state/hpo/venv-ci/bin` first, Python 3.14.7, node v24.22.1 with `NODE_OPTIONS=--max-old-space-size=8192`):

- `PYTHONPATH=tests/hastub python3 tests/plan_view.py && node tests/card.mjs` → `ALL CARD CHECKS PASSED` (NULL row). At `d05d521ff` → the census FAIL above.
- `PYTHONPATH=tests/hastub python3 tests/debug_collect.py` → `ALL 158 DEBUG COLLECT CHECKS PASSED`. At `d05d521ff` → `1 of 158`.
- Mutants: the tables in `## Mutation proof`; drivers `card_mutants.sh` (sha1 `28864e616a8feb472a551a33628499a3935fb28f`) and the round-4 reviewer's `mutants_r4.py` (sha1 `b301586de6ee1853778ea9be51a4c95d7b82d45d`), their RESULT lines kept out of tree beside them (`mut-results.txt`, `mut4-results.txt`, `mut4-n5-features.txt`).
- Seam enumeration (step 8) for the class "a check that enumerates published problem codes by spelling": `git grep -n -E 'reading\.problem = |_set_problem\(reading|PROBLEM_WORDS|p_\$\{' -- tests custom_components/heatpump_optimizer/www` returns 9 lines:
  - `tests/card.mjs`'s census and the three checks under it: closed in this diff; it reads `PROBLEM_WORDS` and refuses a class either route sets that the table lacks.
  - `tests/debug_collect.py`'s `_literal_classes` `ast` census: already route-complete (`.problem =` and `_set_problem(` both), now also the owner of `PROBLEM_WORDS`' equality.
  - the card's advisor line (`advisor.optin_${id}`) is an unrelated key family.
  - the card's `healthInputsHtml` maps `p.problem` to `health.p_<code>` at render; the new per-table check reads the same keys.
  The standing instrument for the class is the `debug_collect.py` census: it re-runs this enumeration as an `ast` scan, so the card inherits route-completeness from it rather than restating the routes.
  A wider probe for any other enumeration, `git grep -l unknown_unit -- tests custom_components`, names only `card.mjs`, `debug_collect.py`, `inputs.py`, the card, `coordinator.py` (a comment) and `tests/features.py`, whose hits pin named classes (`bad.problem == "unknown_unit"`, the R9-UX-9 flow pin), not a census: no other enumeration to lose.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`; no budget file is touched.
- `python3 tools/audit/archscore/score.py --diff edd7e0e14` → `Architecture score: dS +0.0012 IMPROVES`, `coord_footprint 2410 -> 2408`. `--diff d00790305` → `dS +0.0000 NULL`: this pass is score-neutral.
- `python3 tools/pr/ci_predict.py --base origin/main` → `CI PREDICT: no closures, fast, wave-script or instrument red predicted against edd7e0e14e08`.
- `python3 tests/closure.py select --diff edd7e0e14 --workdir $D` → `MODE: SCOPED -- 27 script(s) run, 6 scoped out`.

## Architecture score

This pass at `060c9bef5`: `python3 tools/audit/archscore/score.py --diff edd7e0e14` → `Architecture score: dS +0.0012 IMPROVES`, `coord_footprint 2410 -> 2408`. `--diff d00790305` → `dS +0.0000 NULL`: this pass is score-neutral. The whole branch's mechanism is unchanged from round 4: `inputs.OUTRANKS_STALE` and the 3-line `_set_problem` replace a literal restated in `diagnostics.py` and a nested guard in `read_flow_kg_s`; no coordinator method is added (`tests/seam_map.json` untouched).

This pass's alternatives for the card census, and why each lost:
- widen `card.mjs`'s regex to `_set_problem\(reading, "(\w+)"` as well (the reviewer's first suggestion): satisfies the check, but restates in a second language the routes `debug_collect.py`'s `ast` census already enumerates, and the next helper or keyword argument loses a class again; kept only as the cross-check that a set class is in the table, with `debug_collect.py` as the owner;
- derive the codes from `OUTRANKS_STALE`: names one class, not the published set;
- spawn Python from `card.mjs` to import `PROBLEM_WORDS`: couples the node suite to an importable package and the `tests/hastub` path for one set of keys; the literal table is a file read, and `debug_collect.py` is the check that imports the real symbol and holds the table to the reader;
- a new constant listing the codes: a second table beside `PROBLEM_WORDS`, a duplicated concept (`fixer.md` step 17). `PROBLEM_WORDS` already had to name every worded class; giving it `stale` makes it the complete set at the cost of one entry.

The per-table check encodes a design choice: a published code owes its own word in each of the card's tables, rather than an English fallback in Swedish. That is the card's rule already (the sv table words all eight); the check states it.
## Red checks

This pass: no check has run on this head before this push. Scope scripts this pass's three files reach, run locally at `060c9bef5` (`PYTHONPATH=tests/hastub`), each with its last line:

- `tests/plan_view.py` then `node tests/card.mjs` (with `NODE_OPTIONS=--max-old-space-size=8192`): `ALL CARD CHECKS PASSED`.
- `tests/debug_collect.py`: `ALL 158 DEBUG COLLECT CHECKS PASSED`.
- `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <this body>` at `060c9bef5`: `no refusal`, `PRE-PR: 060c9bef5c4b77adc5ee77d50f21bd5c06393fb8`, rc 0, 3728 s (host load average about 268); `unpinned sites` skipped, "the diff adds no unpinned mutation site".
- Not run locally at this head, left to CI's heavy runs: the other scripts in `scope.run` (`tests/features.py` ran under mutant N5 only, `## Mutation proof`).

Reds at the previous heads of this branch, each answered (`defect-root-cause.md`'s second trigger):

- `tests / fast (3.14)` at `75ae7b26f` (job 122634417080), from `node tests/card.mjs`: `FAIL inputs.py publishes problem codes the card can be enumerated against`, detail `missing_entity,unavailable,stale,not_numeric,unknown_value,not_boolean,unknown_unit`. Cause: round 4's `a3a4a78c9` moved `reading.problem = "implausible"` into `_set_problem(reading, "implausible")`, and the card's census was a regex over the first spelling only, so `implausible` left it and its en / sv-SE wording checks. Repaired in this pass (intro; `## Mutation proof`). **Cheaper detector: `node tests/card.mjs`, run after `tests/plan_view.py`**, which is in this PR's `scope.run`; it costs 118 s in CI's lane (and about five minutes on this host, where it also needs a node heap above the 2 GB default). Round 4's body listed it as not run locally. This pass ran it at both commits before the push; and the census it read is now derived from `PROBLEM_WORDS`, which `tests/debug_collect.py` (2 s, `ast`, route-complete) holds equal to every class `inputs.py` sets, so the next route change goes red in the 2 s script first.
- `pr-contract` at `75ae7b26f` (122644704843, 122645950269) and `gate` (122645294082, 122646219172): the consequence of the red above going unnamed in `## Red checks`. Cheaper detector: `prepr.sh --body-check` names an unnamed red only once CI has produced it; this body names it.
- `tests / mutation` at `75ae7b26f` (122634276677): `ADDED UNPINNED inputs.py:139 GUARD_OFF`, named under `## Unpinned sites` and pinned by `mutation-autofix` in `f77650fc5` (`ci-autofix.md`).
- `tests / nightly-status` at `75ae7b26f`: main's `record-autofix` 403 (run 40595637258), not this PR's: the diff touches no file nightly-status reads.
- Earlier rounds' reds (`governance / wave-script` transient checkout, `pr-contract` body staleness, `tests / closures` `INERT READS`) were answered in their rounds and do not recur at this head.

## Unpinned sites

This pass adds no mutation site (`ci_predict.py` above predicts no `ADDED UNPINNED`): its production change is one dictionary entry. Round 4 added one, `custom_components/heatpump_optimizer/inputs.py:139 GUARD_OFF` (`_set_problem`'s guard), killed by `tests/debug_collect.py` and pinned by `mutation-autofix` in `f77650fc5` (`tests/mutation_ledger/killed_by/inputs.py/_set_problem.GUARD_OFF.de541d53.json`).

Round 4 also removed one pin. `tests/mutation_ledger/killed_by/inputs.py/InputReader.read_flow_kg_s.GUARD_OFF.1d38d74f.json` pinned the line `if reading.problem is None:` in `read_flow_kg_s`, which this diff replaces with the `_set_problem` call. `ci_predict.py` predicted it as a `STALE PIN`, which `mutation-autofix` never drops, so it is deleted by hand. The same guard now lives at the site above.

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

