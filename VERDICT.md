Fix review: merge 3e936f0c2f4eb4dc8e07abc735b14fa6cac59edc

bus-nonce: 98427e905bee3d16322d52e0a802809b

Round 5 (delta review) of #2825, R10-UPDATE-PR-SIGNALS. Measured at head `3e936f0c2f4eb4dc8e07abc735b14fa6cac59edc`, which `git ls-remote origin refs/pull/2825/head` still returns at 2026-10-26T04:04:19Z. Baseline `5e83e3d8897aeb3661aa20278c2fd872284f04fb`. Reviewed from detached worktrees at both SHAs. `dev/governance/roles/` matches origin/main (the three-dot diff is empty).

## Findings

- The body has no closing keyword. #2502 (open, `[R10-UPDATE-PR-SIGNALS] Signal-safe update_pr.sh ...`) is this group's only issue, and this PR does the work that issue states. The roster entry's `fixes` is `[]`, so no keyword is mandated and the body did not break a rule. The cost is that a merge leaves #2502 open: whoever merges must close it by hand, or the body must add `Closes #2502` before the merge. Carry: #2502
- `stuck_arm` takes no position on a lock aged exactly 900 s. The mutant `if now - start <= lim` -> `if now - start < lim` survives the self-test and my own fixture alike, because the controls the carry prescribes are 901 and 899. Carry: dismissed: the carry's own controls are 901/899 and "older than 900" is met by `<=`; a 1 s boundary on an hourly-scale report-only trial is not worth a third fixture
- `carry_audit.py pr 2825` prints 3 unrouted items. All three sit in the `## Evidence` sections of earlier reviewers' verdicts (reviews 6402890433, 6404048457 and 6406256342, each the line "Quiet output: deferred to R10-FLOW-JIDOKA"). Each one repeats a Findings bullet that is already routed to R10-FLOW-JIDOKA. The PR body contributes 0 unrouted items. Carry: dismissed: these are the wording of past verdicts the fixer cannot edit, and each restates a finding already carried to R10-FLOW-JIDOKA

## Evidence

Check 1, carry 6 (the STUCK andon), against the real files:
- `pr_branch_lock` writes `<run pid> <holder pid> <start epoch>`, and adds `drain` as a fourth field. The run's taken-test now compares fields 1, 2 and 4. `pr_lock_busy` reads `drain` from field 4. The self-test arm `the held lock records its holder's start epoch beside the pids` passes 6 of 6 under par6 load.
- `stuck_arm` is wired into every `pass` after the confirm arm. It is report-only: it prints `cloud_relay: STUCK <b> <pid> <age>s` and sets `push-stuck` on the level, and it removes nothing. `ledger.py` adds `push-stuck` as a derived kind. Locks of both open_pr.sh and update_pr.sh live under `$HPO_STATE_DIR/pr/upd-*.lock`, the directory the arm scans.
- My own harness is `ev/stuck_fixture.sh`. I built it and it is not the finder's. It extracts `STUCK_PY`, `relay_log`, `level_line`, `level_set` and `stuck_arm` from the file under test and runs them against fixtures held by a real flock holder. At the head (`ev/stuck_fixture.head.out`):
  `RESULT head held901 reported` (`STUCK fix-old 111 901s`), `held899 not-reported`, `released5000 not-reported`, `oldmtime-freshstart not-reported` (mtime 5000 s old, recorded start 10 s ago), `level push-stuck-line`, `all-released nothing-reported`.
- Mutants on copies, run through the same harness (`ev/stuck_fixture.mutants.out`):
  - mtime-for-start (`cloud_relay-30`'s text): `held901 NOT-reported`, `oldmtime-freshstart reported`, `level NO-line`. This is the touched-later fixture, killed both ways.
  - age bound deleted: `held899 reported`. Killed.
  - held test deleted: `released5000 reported`, and `all-released REPORTED: STUCK fix-gone 555 5001s`. Killed.
- The fixer's mutation harness, `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py M0 cloud_relay-29 cloud_relay-30 cloud_relay-31 cloud_relay-32 cloud_relay-33 ledger-1 pr_args-1`, gives `RESULT survivors=0`, and every M0 step passes (`ev/mutants.log`). `cloud_relay-30`, `-29` and `-32` each fail 2 checks, `-31` fails 1, `-33` fails on the missing level file, and `ledger-1` and `pr_args-1` are KILLED. The worktree was clean afterwards.
- `git grep -nE 'STUCK|HPO_PUSH_STUCK' HEAD -- tools/audit/seat` returns 17 lines, and the fixture is among them.

Check 2, the wait is wall clock:
- `untilfree` waits on `end=$(($(date +%s) + N))`, and `pr_branch_lock` on `k=$(($(date +%s) + 20))`. The drain/pushhold wait is 10 s against the stub's `sleep 30` push. `bndkill`/`bndgrp` wait 5 s against the child's 20 s sleep.
- Finder's par6 load (round 3: six parallel `pr_args.sh --self-test` runs, `nproc` 4, red counted by exit status; driver at `par6.sh` beside this verdict's evidence, logs `ev/par6-*.log`):
  `RESULT par6 head 3e936f0c2f4eb4dc8e07abc735b14fa6cac59edc red=0 runs=6` (each run `125 checks, 0 failed`)
  `RESULT par6 prev 5e83e3d8897aeb3661aa20278c2fd872284f04fb red=0 runs=6` (each run `123 checks, 0 failed`)
- Null control: `null control: an unmutated SIGKILLed run's lock still reads held after the mutants' 10 s wall-clock wait` passes in 6 of 6 head runs. My own mutant shortened `untilfree`'s deadline to 1 s (`local end=$(($(date +%s) + 1))`). It is killed by exactly that check, `FAIL null control: ...`, `125 checks, 1 failed` (`ev/nullctl-mutant-untilfree1s.log`).
- Round-2 finder's grpkill harness (`ev/grpkill.sh`, sha1 `4f547e9ed3995f81f7ade7ad3ff880b07c534bc0`, taken from `probe/rev-2825-4ba59ff1`), run as `grpkill.sh tools/audit/seat/pr_args.sh 15`: `RESULT grpkill head 2 zero-sessions, 0 nonzero` and `RESULT grpkill prev 2 zero-sessions, 0 nonzero`. Each session had 0 live processes 3 s after the group KILL.

Check 3, the body:
- The headings are exactly the template's seven (Head, Mutation proof, Null control, Figures, Red checks, Forward-carry, Friction), with a short preamble above them.
- The figures are stamped `2026-10-26T02:00Z–02:53Z`, origin/main `7d2056970`. I re-took two of them:
  - par6 gives 0/6 red at both ends with 125 and 123 checks, as above. Matches the body.
  - The self-tests at the head give `cloud_relay self-test: 275 checks, 0 failed` and `ledger self-test: 56 checks, 0 failed`, plus pr_args 125/0. All match the body.
- The body names `governance / delivery-status` as red on main, not a required context, and not this diff's. At this head the check is green.
- CI on the head: all 55 check runs had completed by 04:04Z. None concluded failure. Every one is success, skipped or neutral (CodeQL, later success). Among them are `gate` (runs 40263374123 and 40263374760), `pr-contract / pr-contract` (both runs, the later starting 03:56:08Z), `governance / instrument-self-tests`, `tests / closures`, `tests / mutation`, `tests / coverage`, `codeql / Analyze (python)` and `budget-raise-gate`, all success. No red check is owed an answer.
- `python3 -I tools/audit/carry_audit.py pr 2825`: the body has 0 unrouted items (5 NOTE lines, all routed). The 3 unrouted items are from earlier verdicts; see Findings (`ev/carry_audit.txt`).

Check 4, the merge:
- `git merge-tree --write-tree origin/main 3e936f0c` exits 0 against `d181d014a` and against the newer main `f6784210c9c2c89cfe82ec8bf6acb8b412629055` (`ev/merge-tree.txt`). Main's newer commits do not touch `tools/audit/seat`, the harness or the claim files.
- `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical to origin/main (cmp). `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched in the three-dot diff. `tests/structure_budgets.json` is identical to main, so there is no budget raise. `dev/programme/delivery/2825.md` is in the three-dot diff (`ev/files.txt`).
- The three-dot diff covers 8 files, all of them this group's (seat scripts, INSTRUMENTS.md, harness, delivery row). The 111-file two-dot delta 5e83e3d8..head is main's own merges.

Check 5: the delta leaves the answers to carries 1-5 unchanged. Field 3 is now the start epoch and `drain` moves to field 4, and every reader was updated with it (`pr_lock_busy`, `sigrun`, the taken-test). The rest of carries 1-5 and the accepted dispositions (R10-FLOW-JIDOKA for quiet output and the 12 outside self-tests, the PR_BOUND_PY startup window and the /proc skip as dismissed) stay settled as the prior round recorded them.
