Fix review: blocked 4fc6a4c51ad990b04f7911807c83b245df3a2141 mutation-survivor: config_flow.py:3490 RETURN_DEL survives at this head and keeps tests / mutation red; it is equivalent and needs a survivor_triage record

bus-nonce: 862cd00f1142db22558875efc10f5190

## Round

Delta review of #2912. The prior verdict was `merge` at `cc0510ee2a25444363251df640509b3034bca4f6` (probe/rev-2912-ff2ea98c). I measured head `4fc6a4c51ad990b04f7911807c83b245df3a2141`, which is still the PR head at the time of writing. `git diff eab04d0eb...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Block

The delta itself is clean. The bot commit only adds pin rows, and the carry predicate holds. The block is the condition the prior verdict set for the merge: `tests / mutation` had to be green at `4fc6a4c51`. It concluded `failure` at this head (check run 123016889009).

- `python3 -I tools/pr/ci_predict.py --base origin/main` at this head lists one site the diff adds that is still unpinned: `config_flow.py:3490 RETURN_DEL: return errors`. This is the `return errors` after `tibber_token_required` in `HeatPumpOptimizerOptionsFlow._entities_errors` (ev/ci_predict_head.txt). The pin commit pinned every other predicted site.
- I replaced that line with `pass` in a fresh `git archive` copy of the head. `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` (venv-ci, Python 3.14) then still prints `ALL 531 checks PASSED` with rc 0 (ev/mut_3490.txt). Unmutated, it also prints `ALL 531 checks PASSED` (ev/head_config_flow_steps.txt). The mutant survives, and `mutation-autofix` (`--pin-killed`) cannot pin a survivor.
- The mutant is equivalent. That branch runs only when neither `submit` nor `current` holds a token. Then `submitted = submit.get(CONF_TIBBER_TOKEN)` is falsy, so validation is skipped and the final `return errors` returns the same dict. No test can kill it.
- The body's `## Red checks` `mutation` line covers only the predicted sites that autofix pins. It does not cover a survivor. The pin made that line stale, as ci-autofix.md L81 says it would.
- I could not read the lane's own log: the Actions log and artifact blob host returned 403 through the proxy (ev/mutation_job_log_403.txt). So I infer from ci_predict and my mutant that 3490 is the only survivor. The log itself does not confirm this.

To clear the block, the fixer adds `tests/mutation_ledger/survivor_triage/config_flow.py/HeatPumpOptimizerOptionsFlow._entities_errors.RETURN_DEL.<hash>.json` with `verdict: equivalent` and the reasoning above. ci-autofix.md L81 forbids automating survivor triage, so this has to be a seat's judgement. The fixer then updates the `## Red checks` `mutation` and `## Unpinned sites` lines. The pushed commit then needs a fresh review.

## Findings

- 3490 is an equivalent surviving mutant and needs a triage record (see Block). Carry: R10-CONFIGFLOW-PAGES
- From the prior verdict, still open at this head: `view = {**current, **submit}` -> `view = dict(submit)` in `_entities_errors` is equivalent under Home Assistant's form semantics. `config_flow.py` is byte-identical between `cc0510ee` and this head. Carry: dismissed: equivalent mutant, the `current` merge is defensive only
- From the prior verdict, still open at this head: the PR body still repeats `## Mutation proof` and `## Unpinned sites` under the broken heading `## Null control\` and \`## Figures\` was measured ...` (body lines 73-120). Carry: R10-CONFIGFLOW-PAGES
- Main has moved since the prior verdict (`beb570c81`, #2873). GitHub reports the PR `dirty`, because its merge cannot run the `ledgermerge` driver. The merge needs the orchestrator's driver-equipped merge, and the gate must be re-run on the merged tree. Carry: R10-CONFIGFLOW-PAGES

## Evidence

- Delta: `cc0510ee..4fc6a4c51ad990b04f7911807c83b245df3a2141` is one commit by `github-actions[bot]`, `ci: pin killed mutants` (ev/delta_log.txt). It adds 32 files under `tests/mutation_ledger/killed_by/config_flow.py/`, +192/-0, and touches no other path: the count of other paths is 0 (ev/delta_stat.txt). `config_flow.py` is byte-identical between the two heads. So the prior verdict's mutation proof, harness RESULT lines, archscore and structure figures carry unchanged.
- Body `## Head` names `4fc6a4c51ad990b04f7911807c83b245df3a2141` as the current head, and `cc0510ee` as the reviewed head under it (step 7). Both are correct.
- Claims and versions: `VERSION` and both claim files at this head equal origin/main `beb570c81`.
- Merge with main `beb570c817c4efcae0d5f6f4bba52f3383baf8db` (ev/merge-tree.txt, ev/merge-tree_nodriver.txt, ev/structure_merged.txt, ev/merged_config_flow_steps.txt):
  - With the repo's drivers installed, `git merge-tree --write-tree origin/main 4fc6a4c51ad990b04f7911807c83b245df3a2141` exits 0 with tree `fe660e9a837e98772486202240ed93afa36f307b`.
  - In that run, `LEDGER-MERGE: resolved tests/structure_budgets.json` (`class_excess_loc` 17991) and `LEDGER-MERGE: resolved tests/closures.json`.
  - Without the `ledgermerge` driver, it conflicts in exactly those two files, which is why GitHub reports `dirty`.
  - On the merged tree, `tests/structure.py` prints `STRUCTURE RATCHET PASSED` (`class_excess_loc 17991 <= 17991`), and `tests/config_flow_steps.py` prints `ALL 531 checks PASSED`.
- CI at 4fc6a4c51ad990b04f7911807c83b245df3a2141, from the check-runs API at writing (ev/checks_live.tsv):
  - `tests / mutation` is `failure` (see Block).
  - `tests / closures`, `tests / coverage`, `tests / fast (3.14)`, `governance / instrument-self-tests` and `codeql / Analyze (python)` are still `in_progress`.
  - Every other check succeeded, was skipped or was neutral.
  - Branch protection on main returns 404, so no check is marked required at the API level.
- Review packet rendered at this head (ev/review-packet.md): Refusals none, `CARRY-AUDIT: 1 finding item(s): 1 routed`, `FIGURES: 12 resolved, 4 not verified, 0 refused`.
