Fix review: merge e52f597075ede9a3559aadee0fc8c2caa979891a

Round 2 of PR #1809 (F10.1d). The PR head is the code head, e52f5970, on main 787fe137. The transport tip is b59454dd and the branch had not moved at posting.

## RESULT lines
- RESULT head: HASTUB_TZ=Europe/Stockholm tests/dst_checks.py at e52f5970: ALL 96 DST / QUARTER-GRID CHECKS PASSED.
- RESULT hold-echo revert (pump_arbiter.hold): 1 of 96 FAILED. Killed.
- RESULT write-gate revert (pump_arbiter._write): 1 of 96 FAILED. Killed.
- RESULT heavy-snow revert (coordinator._update_snow_memory): 1 of 96 FAILED. Killed.
- RESULT throttled revert (power_guard): 2 of 96 FAILED, the fold check and the new spring-gap check. Killed.
- Round-1 null control: 11 of 92 checks fail on main's tree. It still holds for the 10 sites it covered.

## Round-1 findings, resolved
- The three unpinned sites are now pinned (above).
- open_meteo.py is reverted to main. barrier_gap records _should_refresh as clean because its caller passes utcnow. The fast, closures, closures-autofix and coverage-ratchet reds at e8cef66b are named and answered in the body: one cause, process state b, no countermeasure. That answers step 11.
- The census-missed sites have a forward carry. barrier_gap marks P7 STILL OPEN, owned by R9-F10.1e, and quotes the widened rule. Roster commit d4776d37 on handoff/audit-r9-fixplan adds R9-F10.1e after R9-F10.1d, pointing at the barrier_gap list and the evidence folder 1809-f10-1e-probes.

## Checks
- git merge-tree against origin/main, #1806 and #1808 at e52f5970: rc 0 for all three.
- VERSION, manifest and notes are untouched. No budget moved. No resume files.
- CI at e52f5970 when this verdict was written: typing, briefs, policy-docs, pr-contract, budget-raise-gate, closure-scope, env-matrix, browser, hassfest, validate-hacs, delivery-status, nightly-status and instrument-self-tests are green. fast (3.14), mutation, closures and coverage are still running; they are cited, not re-run, and the merge seat merges only on green. The fixer's scoped gate at the code head reports 19 passed, including tests/open_meteo.py. Real-HA, as relayed: 61/61 contracts and 22/22 probes.

## Not blocking
- Round 1's transport commit e2e88ee0 is now in the code-head ancestry, because the round-2 commits were built on it. Merging therefore lands tools/audit/handoff/r9-f10-gate-infra-1d/BODY.md on main in its round-1 text. That text is stale and still says "Closes #1756's carry" in a file, though a file cannot close an issue. Other handoff folders already live on main, and entities.py is in CI. A later PR can delete or refresh the file if the record wants that.
