R10-HOTFIX-CODEQL-HEADROOM. Main's `codeql / Analyze (python)` job runs at 28 to 43 minutes against its 45-minute cap. Most of that time is CodeQL's Python **extraction** of `tests/features.py` and `tests/entities.py`, and a `try` executed at module scope is what the extractor is slow on. #3232's 364-line module-level try/finally took `features.py`'s extraction from 817–1389 s to 2146–2211 s, about 1000 s for 387 lines, where the rest of the file costs about 0.01–0.02 s a line. That cancelled the job.

This cures the cause. It leaves the cap and the scan's file set alone:
- Each module-level statement holding a `try` (169 in `features.py`, 110 in `entities.py`) now runs inside `def _module_block_<line>():`, called once at its old place.
- The function declares `global` every name the statement binds, so module state is unchanged.
- Each wrapped statement's AST is identical to the original, and so is the order of everything else (the rewrite asserts both).
- No module-scope `try` remains in either file.
- The only source edit apart from the wrapping is that `_ep_inits: list = []` and `_ep_builds: list = []` lose their annotation. A `global` name cannot be annotated, and nothing reads the module's `__annotations__`.

`tests/entities.py` gains the guard: no test script past `_GIANT_SCRIPT_LINES` (20000; the next-largest script, `config_flow_steps.py`, has 7803 lines) runs a `try` at module scope. The guard carries its detector's own null control. The rewrite is landed as `tools/audit/seat/wrap_module_tries.py` (with its `INSTRUMENTS.md` entry), so the guard's refusal names a remedy a later seat reruns.

#3232 is not merged (open, `fix/r10-ext-3226`), so its blocks are left to f-3232-reshape. Its reshaped head moves its section into `tests/worker_deadlines.py` and adds an 8-line call to `features.py`, which holds no `try`. If it merges first, a merge here leaves the guard green. If it ever puts a module-scope `try` back into `features.py`, the guard refuses it.

Alternatives considered:
- Raising the 45-minute cap, or excluding the two files from the scan: forbidden by the owner's ruling, and neither removes the cost.
- One wrapper function around each whole file: it keeps one giant scope and changes every name's binding.
- Splitting `features.py` into several scripts: raises `tests/ci_budgets.json`'s every-script-once count, a budget raise (#3232's first cut read `budget 54, every-script-once count 56`).

The per-statement wrapper is the smallest change that removes every module-scope `try`.

Two repairs the move needed, each found by `tools/pr/prepr.sh`:
- `tests/layout.py`'s guard keyed each base citation of a retired path on its exact line. The re-indent read `entities.py`'s deny-list line (`for _bad in ("docs/plan-2026-09-open-issues.md", "docs/HANDOVER.md", ...`) as a new citation. The guard now keys on the stripped line, with two self-test cases: a re-indented old citation reads 0, and a re-indented second copy still reads 1.
- `tests/closures.json` records `entities.py`'s inert read of the new tool (its `tools/audit/seat/` listing; `ci_predict.py --apply-inert`).

## Head

`402b18da98cc70758ae6589fd83cff4be25db05d`. It merges `origin/main` `80016a71f567d936450d8708abcbb79d9e8071d7` (read at 2026-11-06T23:01:15Z; unmoved since, so this prepr run is the last). It descends from the fix commits `e50ec5403` and the layout-guard repair `53488c834`, with two merges of main. Main's delta since the fix's base `198b8f7ed` (#3253, #3234) touches neither `tests/features.py` nor `tests/entities.py`. It reaches both through their closures, so the five scoped scripts ran again at this head, along with structure and prepr. The base-vs-head suite comparison and the six mutant re-verifications ran at `e50ec5403`, with the merge base `198b8f7ed` as the other end, where named.

## Mutation proof

- The guard: with `tests/features.py` restored to main's text at this head (`git checkout origin/main -- tests/features.py`), `PYTHONPATH=tests/hastub python3 tests/entities.py` reads `1 of 2639 ENTITY CHECKS FAILED`. The one failure is `FAIL no test script past _GIANT_SCRIPT_LINES runs a try at module scope (CodeQL extraction cost)  [module-scope try lines -> {'entities.py': [], 'features.py': [782, 1676, 2416, 4902, 8321]}]`. At this head the same check is `ok`, with 2639 passed.
- The move must not lose a kill. 2439 ledger rows are `killed_by` `tests/features.py` and 210 are `tests/entities.py`, and no CLI re-drives pins by killing script, so a seeded sample was re-verified (`random.seed(20261106)`, 4 + 2 rows) with `PYTHONPATH=tests/hastub python3 tests/mutation_table.py --anchor <anchor> --scripts <script>`. All six read `PIN RE-VERIFICATION: 1 reproduced, 0 not reproduced, 0 not re-verified`:
  - coordinator.py `_async_learn_house_heat_loss GUARD_OFF 414442b6`, `_indoor_humidity_value BOOLOP 1717f87a`, `_aware_instant_iso RETURN_DEL a8227ccf` and drift.py `Cusum.release_if_starved GUARD_OFF 0ec150d6`, each killed by `tests/features.py`;
  - `__init__.py` `_async_remove_retired_entities GUARD_OFF c2a1a50d` and sensor.py `PredictedIndoorTempSensor.native_value RETURN_DEL bac5a8f4`, each killed by `tests/entities.py`.

  The remainder holds by construction: each moved statement's AST is unchanged and runs in the same order, against the same globals.

## Null control

- Each mutant run's own: `null control <module>:<line> NULL_COMMENT survived` and `baseline tests/features.py: rc=0 failed=0` (`tests/entities.py` alike).
- Check counts at both ends: `ALL 4876 FEATURE CHECKS PASSED` at the merge base and at this head, with the sequence of `ok`/`FAIL` check names identical (`diff` of the name column empty).
- `ALL 2637 ENTITY CHECKS PASSED` at the merge base and at the transform's commit. Their line diff is two inner reports alone: a set-ordered `__dup` name list and the `hb:positive_control` timings, both of which vary between runs. The head adds the 2 guard checks: `ALL 2639 ENTITY CHECKS PASSED`.
- The `entities.py` self-read (`_PUBLISHED_ATTRS_HOLES_PROSE`, a split on two comment markers) returns byte-identical text before and after the rewrite (`cmp` of the two extracts).
- Extraction null control: `tests/closure.py` and `tests/structure.py`, files this diff leaves alone, extract in 2.1–3.2 s and 2.5–4.1 s across the three main jobs below. A runner-wide slowdown would have moved them too.

## Figures

- Main, `tests/features.py` extraction: 817 s, 967 s, 1389 s; `tests/entities.py`: 350 s, 343 s, 688 s. Jobs 127952679731, 127954661976, 127995766058. Whole job 28, 31, 43 min (#3232's measurement of the same jobs) — `gh api repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs | grep -E "Extracted file .*tests/(features|entities|closure|structure)\.py in"`
- After: not yet measured. CodeQL runs on a pull request or `main` only (`ci.yml` `on:`), and running the CodeQL CLI here was refused by the environment, so the PR's own `codeql / Analyze (python)` job is the first measurement at this head. Prediction, not a measurement: both files' extraction falls and the job ends well inside its cap. The reviewer reads the same `grep` on that job and compares it with the main figures above, `closure.py` and `structure.py` serving as the null control.
- Module-scope `try` statements wrapped, `features.py` / `entities.py`: 171 / 116 `try` nodes at the merge base (some nested in one wrapped `for`/`with`/`if`), 0 / 0 at this head — the guard's detail line (Mutation proof); `ok` at this head
- Statements wrapped: 169 (1863 lines) and 110 (1905 lines); `features.py` 78350 → 78839 lines, `entities.py` 41407 → 41731 before the guard — `python3 tools/audit/seat/wrap_module_tries.py <file> --dry` on main's copy (for `features.py` after the two annotation edits), and `wc -l`
- Scope at this head: `MODE: SCOPED -- 5 script(s) run, 28 scoped out` (`doc_claims.py`, `entities.py`, `features.py`, `harness_headers.py`, `layout.py`), all run at this head: `ALL 296 checks PASSED`, `ALL 2642 ENTITY CHECKS PASSED` (2639 at `53488c834`; main's #3234 adds 3), `ALL 4876 FEATURE CHECKS PASSED`, `ALL 112 HARNESS HEADER CHECKS PASSED`, `layout self-test: ok` (each `PYTHONPATH=tests/hastub python3 tests/<script>`) — `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`
- `layout self-test` first read `FAIL guard self-test: an old citation re-indented: {'new-reference': 1, ...}` with the new case and the old key, and `ok` with the stripped key; the guard over this diff reads `layout: GUARD: 0 refusal(s) against 28482eceeb6b` — `python3 tests/layout.py --self-test`, `python3 tests/layout.py --guard`
- `STRUCTURE RATCHET PASSED` — `python3 tests/structure.py`

## Red checks

No check has run at this head. Before the handoff, `prepr.sh`'s `layout guard` and `ci predict` refused the re-indent (the two repairs above), so CI's `tests / fast (3.14)` and `tests / closures` would have gone red. The detector was `prepr.sh` itself, and it caught both here. The cause this fixes, CodeQL's cost on a module-scope `try`, had no cheaper detector; the guard in `tests/entities.py` is one now, costing the AST walk of two files inside that script's run.

## Forward-carry

- `tools/audit/seat/features_block.py` runs a block from a marker line to the script's close. A marker line inside a now-wrapped statement starts indented and fails to compile. That was already true of a marker inside a module-level `try` before this change, and the section markers are top-level statements. Carry: dismissed: no behaviour change for a top-level marker

## Friction

- fixer-codeql-measure: cost: the after-figure the brief asks for needs a CodeQL run at the head, which only the PR's checks provide, and a local CodeQL CLI run was refused by the environment. Carry: dismissed: the PR's own check-run is the measurement; the reviewer reads it
