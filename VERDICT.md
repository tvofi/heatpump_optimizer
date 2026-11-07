Fix review: blocked 55a2753a6d64703f90347dd0a7d9ef9d30d08cbd harness: the cure's after-figure is unmeasured, and the body's route to it does not exist: the head's codeql / Analyze (python) job was a stand-in that extracted nothing, while a workflow_dispatch of ci.yml at the head analyzes

bus-nonce: 88c248cf4efce4831d609a69d71b8960

Round: first (fix-review round 1 for #3266).

## Block

The group brief's acceptance (roster `R10-HOTFIX-CODEQL-HEADROOM`) is a measurement: "Measure first, at your merge base, the CodeQL python log line 'Extracted file ... in N ms' for features.py and entities.py on the last main runs, and again after the change on a CI run at your head; report the job duration before and after and a null control". The body reports only the before-figures and hands the after-figure to this review: "the PR's own `codeql / Analyze (python)` job is the first measurement at this head ... The reviewer reads the same `grep` on that job".

That job (check run 128217073827, run 42312418316) took 16 s and did not analyze. Its steps `Initialize CodeQL` and `Perform CodeQL Analysis` are `skipped`; its log reads `codeql_scope: python: stand-in is analysis 2115741747 at main's newest (28482eceeb6b)`. By design (`tools/pr/codeql_scope.py` `decide`, R10-CI-SLIM C7(b)), a pull request whose diff touches nothing under `custom_components/` or `.github/` skips the python leg. Run over this diff's 8 files: `pull_request: skip: none of 8 changed file(s) is under custom_components/ or .github/`. So no extraction line for either file exists at this head, and none will before the merge.

The body's reason for not measuring is also wrong: "CodeQL runs on a pull request or `main` only (`ci.yml` `on:`)". `ci.yml`'s `on:` carries `workflow_dispatch`, and `decide` over the same files returns `workflow_dispatch: analyze: event 'workflow_dispatch' always analyzes`. A dispatched CI run at the head was the cheaper route to the figure the brief asks for.

Without that figure the PR's one effect, lower extraction time, is a prediction. The extractor might be slow on a `try` in any scope, not only module scope. Then 4,700 changed lines and a permanent guard would buy nothing, and they would block a later file from using a module-scope `try`. Everything else checks out (Evidence). The code is behaviour-neutral as far as I can measure.

Remedy (cheap; nothing in the code need change): dispatch `ci.yml` at the head (`workflow_dispatch`, inputs `pr=3266`, `base=main`) and wait for `codeql / Analyze (python)` to conclude. Grep its log for `Extracted file .*tests/(features|entities|closure|structure)\.py in` and put those lines and the job duration in `## Figures`, set against the main figures, with closure.py/structure.py as the null control. Then correct the `on:` sentence and the "first measurement" sentence. If the figures fall, this review's other checks carry (the code is unchanged).

## Findings

- Finding: the body's `## Figures` after-figure is missing, and its account of how CodeQL is triggered is false (`workflow_dispatch` exists and analyzes). This is the block above, settled when the dispatched run's extraction lines and job duration are in the body. Carry: R10-HOTFIX-CODEQL-HEADROOM
- Follow-up: a CI-cost hotfix whose diff is under `tests/` can never show its own effect on a pull request, because `codeql_scope.py` skips the python leg for any non-product diff. The next fixer for a CodeQL-cost group has to know to dispatch (`workflow_dispatch` analyzes), or the gap repeats. Built here: stated in this verdict for the fixer of this group, whose re-cut owns the dispatch. Carry: R10-HOTFIX-CODEQL-HEADROOM
- Residual: the guard's detector skips a `ClassDef` body. A class body runs at module import, not in a function, so a module-scope class holding a `try` is not refused. No such class exists in either file today, and whether CodeQL's cost applies there is unmeasured. Carry: dismissed: no instance in either file; the measurement this block asks for is the place to learn whether it matters

## Evidence

- HEAD measured: `55a2753a6d64703f90347dd0a7d9ef9d30d08cbd`, the PR's head at read (`ev/HEAD.txt`); `## Head` names it. Merge base `80016a71f567d936450d8708abcbb79d9e8071d7`.
- Roles: read from origin/main (`git diff <mb>...origin/main -- dev/governance/roles/` is non-empty, 28 lines, so main's copy was used).
- Merge: `git merge-tree --write-tree origin/main 55a2753a6` rc=0, `LEDGER-MERGE: resolved tests/closures.json`, tree `539b7dcb4205`.
- CI: `merge_train.py classify` -> `GREEN 55a2753a6d64703f90347dd0a7d9ef9d30d08cbd pending: none red: none`, rc=0 (`ev/classify.txt`). Every check run read: 68 runs (one page of 100), none concluded failure, cancelled or timed_out. `## Red checks` ("No check has run at this head") is stale, but no red exists to answer.
- codeql / Analyze (python) at the head: a stand-in, not an analysis (Block); `ev/codeql_decide.txt` holds `decide` for pull_request/workflow_dispatch/push.
- Cap and scan file set untouched: the three-dot diff touches no `.github/` file (8 files: delivery row, closures.json, entities.py, features.py, layout.py, INSTRUMENTS.md, the instrument note, wrap_module_tries.py).
- VERSION, manifest and RELEASE_NOTES.md: not in the diff. Delivery row `dev/programme/delivery/3266.md` is in the diff. The new tool is classified (closures.json line, `tests / closures` green). `STRUCTURE RATCHET PASSED` at the head (`ev/structure.txt`); no `*_budgets.json` in the diff.
- Transform, my own instrument (`verify_wrap.py`, disclosed as mine; `ev/verify_wrap.txt`): unwrapping every `_module_block_N` def+call at the head gives back the base's top-level statement list.
  - features.py: 15623 = 15623 statements, 169 wrapped, the one differing statement is `_ep_inits`/`_ep_builds` losing `: list`.
  - entities.py: 5835 base statements are an identical prefix, the last statement (`sys.exit`) is identical, and 7 guard statements are inserted.
  - Module-scope try: 171 -> 0 (features), 116 -> 0 (entities).
  - symtable: 0 wrappers bind any non-global local, so every bound name is declared `global`.
  - No `locals()`/`exec`/`eval`/frame access inside a wrapper; three `vars(obj)` calls take one argument and are not frame-sensitive.
  - No duplicate wrapper names.
- Tool reproduces the head: `wrap_module_tries.py` on the base features.py (after the two annotation edits) is byte-identical to the head's (`cmp`). On the base entities.py it equals the head less the 60-line appended guard.
- Suite at both ends (`ev/base_features.log`, `ev/head_features.log`, `ev/head_entities.log`):
  - `ALL 4876 FEATURE CHECKS PASSED` at base and head, with a name-column diff of 0 lines over 5010 lines (`ev/features_namediff.txt`).
  - `ALL 2642 ENTITY CHECKS PASSED` at the head, matching the body.
  - Entities at the base: not re-run by me; the body's 2637/2639 at earlier commits is not re-derived.
- Guard mutants (`ev/mut_guard.txt`, the guard block executed with a stub `R` against the real tests/ dir):
  - Restoring the base features.py fails the guard with `features.py: [782, 1676, 2416, 4902, 8321]`, the body's exact lines.
  - drop `ast.Try` from the detector: the null-control check fails `([], [], [])`.
  - drop the scope skip: both checks fail.
  - raise the threshold to 200000: the guard fails `{}`.
  - comment-only null: both checks ok.
- layout.py mutant (`ev/mut_layout_exactkey.txt`): reverting the stripped key to the exact line fails `guard self-test: an old citation re-indented: {'new-reference': 1 ...}`, rc=1. The comment-only null reads `layout self-test: ok` (`ev/null_layout.txt`). The head's self-test reads ok.
- Pins (`ev/pins.txt`, `tests/mutation_table.py --anchor <ledger anchor> --scripts <script>` at the head): all six sampled pins read `PIN RE-VERIFICATION: 1 reproduced, 0 not reproduced, 0 not re-verified`, each with its `NULL_COMMENT` null control surviving: `__init__.py:_async_remove_retired_entities GUARD_OFF c2a1a50d` and `sensor.py:PredictedIndoorTempSensor.native_value RETURN_DEL bac5a8f4` (killed by tests/entities.py); `coordinator.py:HeatPumpOptimizerCoordinator._async_learn_house_heat_loss GUARD_OFF 414442b6`, `coordinator.py:HeatPumpOptimizerCoordinator._indoor_humidity_value BOOLOP 1717f87a`, `coordinator.py:_aware_instant_iso RETURN_DEL a8227ccf`, `drift.py:Cusum.release_if_starved GUARD_OFF 0ec150d6` (killed by tests/features.py). The head did not move during the review (re-read at the end: `refs/pull/3266/head` = 55a2753a6).
- Not re-derived: main's extraction figures (817/967/1389 s, 350/343/688 s, jobs 127952679731, 127954661976, 127995766058) and the null-control file times. The job logs could not be fetched in full here (the blob host is refused by the proxy), so they are quoted, not verified.
- A local CodeQL CLI download was refused by this environment's permission classifier, as the fixer's was; I did not work around it.
