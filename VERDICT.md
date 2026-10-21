Fix review: blocked a8a2778e155e0f13527ec2864f856d8ddd942e31 mutation-vacuous: the self-test check "a last line without a newline is read" passes with that read removed (R6), so a hold file without a trailing newline silently holds none; the OWED handoff-hold-malformed log line (R3) and the `held` CLI arm (R4) also survive deletion

bus-nonce: d81197b47dc8c4f3a8b76b9d08ceb8b3

Round: first review of this head (fixer round 2). Measured head a8a2778e155e0f13527ec2864f856d8ddd942e31 (code tip 0ddbc0c21 + delivery row); re-read live at post time: still the head (ev/head_at_post.txt). Merge base origin/main 49c222280 (0 behind). Worktrees detached at the head and at the base. Roles diff merge-base...origin/main empty: contract current.

## What holds
- RESULT selftest_head=137 checks, 0 failed; selftest_base=74 checks, 0 failed (body: 137 / 74 — confirmed). ev/selftest_*.txt
- RESULT finder_harness_head survivors=0 (42 KILLED incl. M0, S01..S38, W1..W3, S04U), exit 0; base survivors=0 (38 KILLED), exit 0. ev/harness_{head,base}_all.txt
- RESULT S35 KILLED (crash: stub path absent), S36 KILLED 18 failed, S37 KILLED 28 failed, S38 KILLED 2 failed — body's figures confirmed.
- RESULT delete-all-hold-lines (body's grep) = 134 checks, 31 failed — confirmed. ev/body_delete_all_hold_lines.txt
- Main's S31..S34 (tick_loop.sh) rows byte-identical to origin/main; the only removed line in the harness is the docstring range S01..S34 -> S01..S38. All four KILLED at head. ev/s31_s34.txt
- Null control: base self-test 74/0 and no HELD; in-head controls (#99 hold, #141 vs #41, empty/comment/no file, nine malformed variants) all pass.
- Step 5: VERSION, manifest, RELEASE_NOTES.md, tests/golden untouched (ev/untouched.txt). Step 4: no claim files moved, no fixture touched.
- Step 13: `git merge-tree --write-tree origin/main a8a2778e155e0f13527ec2864f856d8ddd942e31` exit 0, tree 12653d04c (ev/merge_tree.txt).
- Step 6 class: the body's rule (grep cloud-handoff-hold|hold_list over tools/ .github/ dev/) returns only cloud_relay.sh, INSTRUMENTS.md and harness S36 (ev/class_rule.txt). The only automatic update_pr.sh driver besides the relay is tick_loop.sh, which runs it through `cloud_relay.sh pass`, so it inherits the hold. Class is one seam; closed.

## Why blocked (step 1, my own mutants on production lines the PR adds; ev/reviewer_mutants*.txt)
- RESULT R6 SURVIVED 137 checks, 0 failed: `while IFS= read -r l || [ -n "$l" ]` -> `while IFS= read -r l`. The check named "a last line without a newline is read" writes `41\n99` and greps HELD #41, which line 1 already supplies; the unterminated line is never asserted. Impact, measured (ev/reviewer_mutant_R6_impact.txt): hold file bytes `41` (no newline, e.g. `printf 41 >` or an editor) -> head `held 41` rc 0, mutant rc 1: a silent hold-none, exactly what the spec forbids. The production line is right; its pinning check is vacuous. Fix: make the unterminated line the held one (e.g. `printf '99\n41'` and expect HELD #41).
- RESULT R3 SURVIVED 137/0: deleting `logline OWED "handoff-hold-malformed $(hold_file)";`. The body and INSTRUMENTS.md both state the refusal logs `OWED handoff-hold-malformed`; no check reads $LOG for it. Since `pass` returns 0 regardless of handoff_arm's rc 2, that log line is the refusal's only durable signal in a daemonized relay.
- RESULT R4 SURVIVED 137/0: deleting the dispatcher line `held) shift; held "$@"; exit $?;;` -> `cloud_relay.sh held 41` falls to usage, rc 2 (head: rc 0/1 correct). The self-test calls the function, never the CLI that INSTRUMENTS.md documents and the body names as R10-ORCH-MACHINERY's interface.
- Notes, not blocking: R12 (hold checked after the failed-ledger) and R13 (hold checked before the is-ancestor test) also survive; both are body-stated design choices ("a hold outranks a recorded failure", "a held PR with nothing to apply prints nothing") with no check. R5 (dropping the -f/-r guard) survives but is equivalent: a directory still fails the read loop and refuses. Killed: R1, R2, R7, R8, R9, R10, R11.

## Other items
- Step 10 carry: the body's Notes says R10-ORCH-MACHINERY's handoff job must read the hold through `cloud_relay.sh held`; R10-ORCH-MACHINERY is on the roster (main and handoff/audit-r10-roster f424d993d) and its brief does not mention cloud-handoff-hold; the seam lives only in the pack (STUDY K17 / this group's carry). Body says "n/a". Put it on that group's brief (finding-propagation.md) or name where it is carried. R10-FLOW-ROSTER-FREEZE is unregistered: verdict note only, per brief.
- Brief's "cloud_relay-1..4 per-file mutant ids, the P6 convention": no such convention exists in r10_seat_selftests_mutants.py on main, the pack pin f89bfb4e, or any origin branch (searched all refs for cloud_relay-1 / P6 convention). The PR's S35..S38 follow the file's actual S-numbering and no other branch adds S35. Not held against the PR.
- Roster registration pending (roster PR-B): note only.
- Step 11 CI at a8a2778e155e0f13527ec2864f856d8ddd942e31 (read 17:07Z, ev/check_runs_final.tsv): pending Analyze (python), closures; nightly-status red (grades main, not this diff; body names it); all others success/skipped/neutral, including instrument-self-tests.
- Steps 2/3: the finder's harness is r10_seat_selftests_mutants.py (main's instrument, extended by the PR); I ran it at both ends myself. No golden/claims/budget/score instrument moved (step 14 n/a). Step 15: added lines stay within the relay's handoff arm; no breach seen.
