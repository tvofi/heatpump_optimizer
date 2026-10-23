Fix review: merge 5d5e49e6f29e90dd33dffebe3a07319c4965132f

bus-nonce: d3cd9a10806840907be88beaa06c1e7b

Round 2 (round 1 blocked 1270ba9b9 `root-cause-detectable: instrument-self-tests`). Measured head 5d5e49e6f29e90dd33dffebe3a07319c4965132f = merge of origin/main fd7e289d0 into f44173a95 (which merges the fixer's 989ee1190 into 1270ba9b9). `git diff 989ee1190 HEAD -- tools dev/audit/harnesses/r10_seat_selftests_mutants.py` is empty: the code under review is 989ee1190's. Contract currency: merge base = origin/main fd7e289d0, so `git diff <mb>...origin/main -- dev/governance/roles/` is empty.

## The block is cured

- `instrument-self-tests` concluded **success** on this head (17:10:30Z to 17:20:19Z), including step 23 and the steps 24-26 and 63-66 that round 1 saw skipped.
- `python3 -I tools/audit/seat/ref_privacy.py --check` at the head: `25 file(s) with a push site, 12 guarded, 300 line(s) added since fd7e289d0a09 judged, 0 refused`, rc 0, 1.3 s wall (ev/ref_privacy_head.txt).
- The fix: the self-test stub now places `review/<pr>` with `git -C "$o" fetch -q "$gd" "$c:refs/heads/review/$1"` into the temp bare origin, no push site. A fetch can write only a local path, so this opens no route to the host that ref_privacy guards. The net diff does not touch `ref_privacy.py` (3ff74e439 added a PUSHERS entry, 989ee1190 reverts it).
- Fixer's rejection of a whole-file PUSHERS entry, reproduced in a throwaway `--shared` clone at the head, with a committed `relay_extra() { git push -q origin "HEAD:refs/heads/review/$USER"; }` appended to cloud_relay.sh: no entry gives `REFUSE tools/audit/seat/cloud_relay.sh:840 ... 1 refused`, rc 1; with `"tools/audit/seat/cloud_relay.sh": ("fixture", ...)` added to PUSHERS, 0 refused, rc 0 (ev/pushers_claim.txt). So the entry round 1 proposed would have blinded the check to production pushes in that file, and the fixer's route is the sounder one. A caveat for later use: `--check` reads committed HEAD, so an uncommitted appended push gives rc 0 at either state.
- The `## Red checks` section now answers `instrument-self-tests`: the cheaper detector is `ref_privacy.py --check` (~5 s claimed; I measured 1.3 s), process state (a). `rg -n ref_privacy tools/pr/prepr.sh tools/pr/ci_predict.py` matches nothing, which I confirmed. `pr-contract` at 1270ba9b9 is answered as downstream of that red. I checked that the trigger is answered, not the answer itself.

## Re-measured at this head

- `bash tools/audit/seat/cloud_relay.sh --self-test`: 230 checks, 0 failed, rc 0. `bash tools/audit/seat/tick_loop.sh --self-test`: 12 checks, 0 failed, rc 0 (ev/*_selftest.txt).
- Null control for the stub fix: with the stub's fetch replaced by `true`, the self-test gives 230 checks, 21 failed, rc 1 (ev/null_no_stub_fetch.txt), which matches the body's 21/230. File restored, tree clean.
- Named mutants: `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py cloud_relay-12 … cloud_relay-21 tick_loop-3` gives all 11 KILLED, `RESULT survivors=0`, rc 0 (ev/mutants_named.txt). The cloud_relay rows show a bash `Terminated` job line as the step's last line, not the summary line. The harness keys on the step's rc=1 and runs the unmutated step first.
- Round 1's own P-O harness, null controls, cause coverage and no-force findings were measured on af21edb9e. The production functions of `cloud_relay.sh` are unchanged since then, because the only cloud_relay.sh hunk in 1270ba9b9..989ee1190 is inside `self_test()`. Those findings stand and were not re-run.
- Merge: `git merge-tree --write-tree origin/main HEAD` gives tree 42a8de22e, rc 0. No claim file is touched, and VERSION, the manifest and the notes heading are untouched (three-dot file list: cloud_relay.sh, tick_loop.sh, r10_seat_selftests_mutants.py, INSTRUMENTS.md, delivery/2664.md).

## CI (ev/check_runs.txt, 41 check runs, all concluded)

- Only red: `delivery-status` (17:10:48Z). It is not this PR's. Locally, `python3 -I -S tests/delivery_status.py --check` lists OVERDUE rows #2650 and #2639, which are main's batch (ev/delivery_status_head.txt). The diff's only delivery file is its own added row 2664.md, so by defect-root-cause.md the body owes no answer. Main's push run of delivery-status was skipped.
- `pr-contract` ran 17:40:52Z, after the last red concluded, and passed. `mutation` passed. No production code line is in the diff, so it drew no mutant. This verdict does not rely on it.

## Round-1 findings, re-checked

- The `## Head` section now names 5d5e49e6f, 989ee1190, f44173a95's merge into 1270ba9b9 and main fd7e289d0 correctly.
- The retry wording now says the arm's tries are counted apart from the relay's own confirm, "one confirm call more than that bound". That matches round 1's `bound_calls63=4`.
- Non-blocking, for the orchestrator at the merge record: this group's unbuilt carries (P-B / 07:10Z stale-checkout restart, P-E "SEAT ENDED NO RETURN", `http.postBuffer` with an ev/ size cap) lose their owner when `resume` goes to done. They need re-homing or the group kept open. Carry: R10-FLY-RELAY-REVIEW-FF
- Non-blocking: handoff/r10-orch-ledger overlaps relay() and dispose(). Whichever merges second re-cuts. Carry: R10-ORCH-LEDGER

## Commits

The fixer's 3ff74e439 and 989ee1190 carry `Co-authored-by: Cursor <cursoragent@cursor.com>`. The owner accepted these under decision 2026-10-23T17:08Z, and ref_privacy and pr-contract pass. No Claude footer or session trailer.
