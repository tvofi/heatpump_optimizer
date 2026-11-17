R11-RCA-SELFTEST-TABLE-DRIFT: root cause of main's recurring self-test read-set drift red

Root-cause seat beside R11-HOTFIX-MAIN-SELFTEST-DRIFT (`142926ec66`), under `defect-root-cause.md`. This PR adds the analysis `dev/audit/rca/R11-RCA-SELFTEST-TABLE-DRIFT.md` and the harness behind its measurements, `dev/audit/harnesses/r11_selftest_static_edge.py`. It changes no production code, tool or policy.

**Defect:** main's `governance / instrument-self-tests` step "Refuse a self-test read set the committed table misses" goes red one merge after a pull request adds a read to a gated step. The fix each time has been a hand re-record hotfix: #3589, #3595, #3606, #3629, #3652, and now `142926ec66`.

**Cause:** the table is measured only on a push to main (`SELFTEST_TRACE` is set only on a push). The repair is a hand re-record measured at one main SHA, which merges 1 to 2.5 hours later while main merges about 1.6 pull requests an hour. The drift step concluded 55 times in main's 80 push runs from 2026-11-14T14:59Z, and failed 54 of those. #3629 and #3652 were both red at their own merges.

**Attribution correction:** the hotfix body names #3644, #3625 and #3651. Read paths actually added by merge: #3622 14, #3644 8, #3625 7, #3640 6, #3627 3, #3641 2, and #3651 none. #3622 merged four minutes before #3652.

**Process state: (c).** The check and the hotfix process existed and were followed every time; the hotfix unit cannot outrun the merge rate. The barriers of `R10-SELFTEST-TABLE-SHRINK` (union record, which stops drops) and `R10-SELFTEST-RED-INTRODUCED` (head against base, while the drift step never runs on a pull request) do not reach additions.

**Detectors judged** over the 15 merges `5aaf9c112f..e352724335`, against the 67 reads `142926ec66` adds:

| detector | result | verdict |
|---|---|---|
| static PR-time detector, as proposed | caught 14 of 67 reads (21%); 333 flags, 14 true (4%); about 22 flags per merge | refused |
| directory-listing variant of it | caught 8 of 45 file reads; 384 flags | refused |
| Darwin approximation | no strace on Darwin; `precheck` skips there (rc 3); an audit hook sees Python processes only | not recommended |
| `precheck` (built, unmerged, on `fix/r11-pre-shared-files`) | reaches 6 of the 20 drifting steps, at most 22 of 67 reads | stays as built |
| traced pull-request CI | job wall 18.9-23.8 min untraced against 38.5-71.7 min traced on a push, over the 30-min pull-request cap; it also edits a gate file in pull requests | refused |

**Cost test:** 6 instances in 48 h, about 1 per 13 merges. Each one is a hotfix pull request (median 105 min open), a fixer, a reviewer and a FULL CI run.

**Recommended:** proposal P-R11-41:
- C5, the main-side absorb bot (P748 part 1's unbuilt half, placement D1/D2 owner-pending), as one standing union pull request;
- C6 as the interim: stop per-red hotfixes and commit main's latest `selftest-closures` artifact once per record batch.

The bugclasses.json entry for this class and C5's demonstration (red on a planted read, green after the bot commit; a green push writes nothing) are written into P-R11-41 as owed by its building group.

## Head

aaf3c780f126b2268e009a00734d2cc9976ef70f, the pull request's head, unchanged by this repair: its code is `de8325b325` plus two merges of `origin/main` (`034438c671`, `aaf3c780f1`) and the delivery row `af67d6a221`. No commit was owed: both reds below are inherited, and `git merge-tree --write-tree origin/main HEAD` at `origin/main` `8f39313a44` reports no conflict (rc 0; `tests/closures.json` resolved by the ledger merge driver).

prepr: passed rc=0 at aaf3c780f126b2268e009a00734d2cc9976ef70f

## Mutation proof

n/a: an analysis document, a measurement harness for a refused detector, and its INERT-read classification in tests/closures.json (ci_predict --apply-inert); no production or tool code changes. Scoped prepr (PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1) refused only the INERT read this commit records.

## Null control

`selftest_scope.drift` against run 43884631892's artifact: the table at `e352724335` gives 27 refusals, and `142926ec66`'s table gives 0. The artifact against itself gives 0.

## Figures

none

## Red checks

Reds at aaf3c780f1 (run 43986301702, attempt 2), against the set `python3 tools/audit/seat/merge_train.py owed-reds` prints:

- `codeql / Analyze (python)`: **inherited**, not caused by this diff. The job was cancelled at its 75-minute timeout (`timeout: 75` in the job log; step "Perform CodeQL Analysis" cancelled, 00:49:43Z to 02:04:50Z). Main carries the same: the check on `origin/main`'s last 8 commits (`git log -8 origin/main`, check-runs API, `check_name=codeql / Analyze (python)`) concluded cancelled on `fc9e24c089`, `174e78cebf` and `69053da4f9`, each at the 75-minute mark, and its successes there took up to 71 minutes. The diff adds one 76-line `.py` file under `dev/audit/harnesses/`. Root-cause trigger: this red is not caused by the branch, so `defect-root-cause.md`'s second trigger does not apply.
- `gate`: **inherited**. Its only failing line is `FAIL codeql / Analyze (python): cancelled (this run)`. This is the cancelled check above, not a separate failure.
- `governance / instrument-self-tests` (outside the owed set; recorded for the reviewer): red on `tools/audit/product_reads.py --self-test`, `enumerate.Refuse: const.py PUMP_DUTY_MODES ['control', 'off'] are not the duty modes STATES names ['control', 'observe', 'off']`. **Inherited**: the same refusal at the merge base `2d7161a4b7`, and the head's diff touches neither file. `origin/main` `8f39313a44` passes (`SELF-TEST passed (86 arms)`). `merge_train.py classify aaf3c780f1 --pr 3684` prints no INTRODUCED line.

## Forward-carry

none

## Friction

none
