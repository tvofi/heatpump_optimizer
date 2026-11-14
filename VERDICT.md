Fix review: merge 9c658de26cc2f3bb5cd8c55a65ec5bbf64d11dc0

bus-nonce: 296ffcc2f9bb6689a9e96d22141ef853
pending-ci: gate, tests / fast (3.14), pr-contract / pr-contract
## Scope

This is a delta review: round 2 over the reviewed head `ea298df445835b20bb2f7d3e85dd1036f26b8ab1` (blocked `evidence-comment`). The PR's own commits since then are `7ad404eeb2`, `60f2a069e1`, `4eace767c3`, `d718d4e086`, `88859d2774`, `381d7d2b7b` and `6104263618`, plus three merges of origin/main (`2f5f5e40a5`, `d0fc820fa4`, `9c658de26c`). The production delta is three English fallback literals: `services.py` factory_reset_not_applied and apply_topology_unsupported, and `coordinator.py` process_worker_unusable. Each is only the first positional message of a raise, whose `str()` reaches logs, traces and API callers. Nothing reads them for control flow, so no already-reviewed code is put at a non-obvious risk, and the review was not widened.

## Prior findings

1. **evidence-comment (4 rows on a comment or blank line, 132 out-of-tree paths): resolved.**
   - At the head, `verdicts.json` holds no `/home/user` path (count 0).
   - Each of the four rows now cites code at `90c6bc3b`, the commit RECORD.md now names as the one its evidence is read at. I read the lines there:
     - `optimizer.py:6306` is `heat_pump_on = plan_step_runs(result, i)`.
     - `6314-6315` is `if not heat_pump_on: mode = "off"`.
     - `2029-2030` is the `0.08 * n_steps` terminal branch.
     - `2012` is the 35th-percentile `cheap_cut`.
     - `2035-2036` is `prices[i] <= cheap_cut` -> `REASON_CHEAP_PRICE`.
     - `draw_range.py:656-665` is the `configured(...)` returns.
   - Each line decides its row's `true` verdict.
   - The new class rule `enumerate.py --evidence verdicts.json 90c6bc3b` prints `evidence: every row cites a code line at a repository path`, rc 0 (`ev/evidence-rule-head.txt`).
   - On the ea298df record it refuses all 132 citations, rc 1 (`ev/evidence-rule-control-ea298df.txt`).
   - My own perturbation re-pointed two head rows at `optimizer.py:6312` (comment) and `2043` (blank). It printed `every cited line is ['comment']` / `['blank']`, rc 1 (`ev/evidence-rule-planted-comment-blank.txt`).
2. **class-open services.py:1196-1197 "nothing was changed": resolved.**
   - The fallback now equals the catalogue sentence.
   - The catalogue sentence is the same in strings.json and en.json, with matching de and sv.
   - A new AST rule in `tests/entities.py` (`_ut_fallback_findings`) reads every raise that passes `translation_key`. It also reads them through the parameters of `_raise_update_failed` and its siblings. It finds two more drifted fallbacks (process_worker_unusable, apply_topology_unsupported), and both are corrected.
   - Mutant `factory-reset-fallback-back`: KILLED by two checks, `every raise that passes a translation key falls back ...` (`services.py:1195`) and `a refused factory_reset raises factory_reset_not_applied ...` (`ev/mutant-factory-reset-fallback.txt`, 2 of 2723 failed).
   - Mutant `worker-unusable-fallback-back`: KILLED by the class rule at `coordinator.py:2343` (`ev/mutant-worker-unusable-fallback.txt`).
   - The rule's null control (three planted findings) is in the file and passes at the head.
   - The separate config-flow `options.abort.factory_reset_not_applied` stays with R10-CONFIG-FLOW-TEXT-VERIFY, as round 1 noted.
3. **Round 1's two findings** (behavioural pins for the rain thresholds and the four price steps; the unpinned narrative.py revert) are carried in the body's `## Forward-carry` to R11-INTAKE-R10-RESIDUE. carry_audit at the head reports 6 routed, 0 unrouted.

## Evidence

- RESULT head: `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2723 ENTITY CHECKS PASSED`, rc 0 (`ev/entities-head.txt`). That equals the body's null count. The only FAIL lines are the planted `a3`-`a13`/`hb` controls.
- Hand-resolved merges of strings.json, en, de and sv: I ran a per-key three-way over the flattened JSON for each of the three merges in range (`ev/m3.py`, `ev/merge-3way-translations.txt`).
  - `d0fc820fa4` (main changed 6 keys per file), `a1e0a4d2fb` (29) and `2f5f5e40a5` (0): every leaf main changed is main's at the merge result, every leaf the branch changed is the branch's, and no key was changed by both sides. That is 0 issues in each file.
  - The body's union resolution of `quiet_silent_not_enforced` with main's new `dhw_minimum_above_start` holds.
- Catalogue at the head: strings.json and en.json `factory_reset_not_applied`, `process_worker_unusable` and `apply_topology_unsupported` equal the code fallbacks, and de and sv carry the same content.
- `git merge-tree --write-tree origin/main 9c658de2` exits 0 with one tree at origin/main `c987209cc7a8` (`ev/merge-tree.txt`).
- Body figures re-derived:
  - The 2723 count.
  - The evidence-rule output at `90c6bc3b`.
  - The control's 132 refusals.
  - Both fallback mutants' FAIL lines (text matches the body).
- Not re-derived: the `topology-quotes-back` mutant (the body discloses its whole-script run was cut; its rule alone reports the finding), archscore `dS +0.0000`, `structure.py` and the scoped gate. CI runs those.
- Policy: VERSION, the manifest and the RELEASE_NOTES heading are untouched in `git diff $(merge-base)...HEAD`.
- A style note, no finding: sv `apply_topology_unsupported` keeps `"{layout}"` quoted where en and de dropped the quotes. That is wording only and makes no false claim.
- CI at this head: `merge_train.py classify 9c658de2 --pr 3567` read WAIT from 03:11:56Z, then `RED 9c658de26cc2f3bb5cd8c55a65ec5bbf64d11dc0 pending: none red: gate` at 03:15:46Z (`ev/classify-log.txt`). The red required contexts are `tests / fast (3.14)`, `pr-contract / pr-contract` and `gate`. `tests / nightly-status` is also red but is not in the owed-reds set.
  - `tests / fast (3.14)` (job 132300573517) ended with `1 TEST SCRIPT(S) FAILED`. I ran `PYTHONPATH=tests/hastub python3 tests/features.py` at the head: `1 of 5571 FEATURE CHECKS FAILED`, rc 1. Its only FAIL is "a charge-start dip that recovers is learned as neither a draw nor usage, and a draw that does not recover keeps what main booked" (`ev/features-head.txt`). That is the weekend-clock check the dispatch names. This head's CI ran before hotfix `c987209c` reached main (02:41Z), so the failure is not this PR's. `tests/entities.py`, the other script this diff reaches, passes at the head (above).
  - `pr-contract / pr-contract` (job 132310539432) has one refusal: `check tests / fast (3.14) is red and ## Red checks does not name it`. It follows from the fast red and clears once fast is green on a re-run over current main. Its carry-audit, figures (12 resolved, 0 refused), version-edit and figure_block steps are clean.
  - `gate` aggregates the two above.
  - Because the only failure is the inherited check, this verdict is `merge` with the `pending-ci:` line, as the dispatch directs. The relay posts it once CI is green at this head, and refuses it over a red or if the head moves.
