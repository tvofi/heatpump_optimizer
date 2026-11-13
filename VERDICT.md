Fix review: blocked 740e6074cf5bace0302c7f2896b72149c918f010 mutation-survivors: four new predicates in cloud_relay.sh survive mutation (redsecs-validate-off, nr-rev-window-off, nr-rev-revt-off, nr-rev-lsremote-fail-continue) and carry_audit gives them no destination but this PR

bus-nonce: 7c9edde1b2ef69ba1e816e06e887afab

Round 1 (first review, full scope). Measured head 740e6074cf5bace0302c7f2896b72149c918f010; it matches the PR body's `## Head` line.

## Block

The PR's named mutants are all killed, so the fix is not vacuous, and CI is GREEN at this head. Four predicates the PR adds to `tools/audit/seat/cloud_relay.sh` still survive my own mutants: no self-test check fails when they are removed. `python3 -I tools/audit/carry_audit.py check --pr-group R10-REVIEW-DISPATCH-RESIDUE` refuses R10-REVIEW-DISPATCH-RESIDUE as a destination (it is carries-open) and finds "none live after R10-REVIEW-DISPATCH-RESIDUE": the producing group keeps the fix, so they are owed in this PR. The body's "one mutant per new predicate and branch" missed these four. Each needs one self-test arm plus its null control, and each mutant below must then be KILLED. The exact old/new edits are in ev/mutants.json under the same names.

- surviving mutant redsecs-validate-off. Removing the non-numeric HPO_RELAY_PENDING_RED_SECS guard in relay()'s pending-ci block kills no self-test check, so the new `case $redsecs` refusal is unpinned.
- surviving mutant nr-rev-window-off. Dropping `[ "$age" -le "$win" ]` from noreturn_arm's reviewer branch kills nothing, so a reviewer dispatch older than HPO_RELAY_NORETURN_WINDOW_SECS is not pinned silent.
- surviving mutant nr-rev-revt-off. Dropping `refs/heads/probe/revt-*-$rn8` from the reviewer return lookup kills nothing. No arm returns a reviewer via a handoff `probe/revt-<topic>-<n8>`, though the body claims that form. If it regresses, every handoff-returned reviewer would be owed a false SEAT ENDED NO RETURN.
- surviving mutant nr-rev-lsremote-fail-continue. Turning the reviewer branch's `ls-remote ... || continue` into `|| :` kills nothing. That breaks the arm's own "unknown is not owed" rule: a failed return listing would owe a reviewer, and nothing pins it. The body's "one mutant per new predicate and branch" therefore missed these four predicates.

What survives a re-cut that leaves the rest of the patch unchanged: the self-test figures, the 16 kills, merge-tree clean and the spec conformance in Evidence. Those only need re-checking on the delta.

## Evidence

- RESULT: `bash tools/audit/seat/cloud_relay.sh --self-test` at the head printed `cloud_relay self-test: 482 checks, 0 failed` (ev/selftest-head.log); at the body's cut base caacd43b4ee1b1ce849fbc92590e0b2191e6c02c it printed `cloud_relay self-test: 452 checks, 0 failed` (ev/selftest-base.log). Both figures in the body's `## Figures` re-derived.
- RESULT: `python3 tests/structure.py` at the head printed `STRUCTURE RATCHET PASSED` (ev/structure.log). No budget file in the diff.
- Diff (three-dot from the merge base): `tools/audit/seat/cloud_relay.sh` and the delivery row `dev/programme/delivery/3541.md` only. VERSION, manifest, RELEASE_NOTES heading and both claim files are untouched, so step 4 has nothing to compare.
- Merge with main: `git merge-tree --write-tree origin/main 740e6074cf5bace0302c7f2896b72149c918f010` exited 0 with empty stderr (ev/merge-tree.err), so there is no conflict.
- Mutation proof. I wrote 20 mutants of my own over every new predicate and branch, independent of the fixer's spec (ev/mutants.json, ev/mutants.py). I ran them with `python3 tools/audit/seat/mutant_run.py --spec <part> --cmd 'bash tools/audit/seat/cloud_relay.sh --self-test' --copy-tree` in four parts, each with its own NULL (ev/mutant_run.{0..3}.log). All four NULL runs SURVIVED. 16 mutants were KILLED, including the carries' named mutants: carry-off (Carry 21), red-hold-rc2 (Carry 23, the RED die restored), probe-dispose-off (Carry 30) and nr-rev-ret-off / nr-rev-moved-off / nr-rev-age-zero (Carry 7). Also killed: carry-classifies-drafted, red-bound-never, red-refuses-first, red-default-bound, wait-no-clear, green-no-clear, rkey-no-head, owed-line-moved-off, nr-rev-level-off and nr-rev-default-bound. 4 SURVIVED; they are listed under Block. The PR's named lines are not vacuous.
- I did not re-run the fixer's failing-first figure (19 of 482 failing with the production hunks reverted). The production text and its self-test share one file, so I could not reproduce the fixer's split. My own kills above stand in for it.
- Spec conformance against the roster carries on origin/main (dev/programme/rosters/wave-r10-groups.json, group R10-REVIEW-DISPATCH-RESIDUE, carry indices 7, 21, 23 and 30):
  - Carry 21's "RED at the live head still refuses" is superseded by Carry 23, which holds RED. The implementation follows 23 and the self-test pins it.
  - Carry 23's "no check running" is read as a WAIT/GREEN read clearing the record. That matches classify, which reports pending ahead of red: the first packet showed `gate` failure while classify read WAIT.
  - In probe_arm, rc 75 skips the tries counter, so a held RED cannot exhaust HPO_RELAY_TRIES before the 6 h bound.
- The Carry 7 PROMPT.md parse was checked on a real prompt: this seat's own PROMPT.md first line yields head=740e6074cf5bace0302c7f2896b72149c918f010 and n8=7c9edde1.
- CI: `python3 tools/audit/seat/merge_train.py classify 740e6074cf5bace0302c7f2896b72149c918f010 --pr 3541` read WAIT five times, then exited 0 at 08:04:39Z with `GREEN 740e6074cf5bace0302c7f2896b72149c918f010 pending: none red: none` (ev/classify.txt, ev/classify-poll.log).
- Packet: re-rendered at the head with rc 0 and `Refusals: none` (ev/review-packet-final.md). The first render's `introduced-red` refusal was `instrument-self-tests` still in progress; job 131759522277 has since concluded success.
- Red checks (step 11):
  - `gate` job 131763921410 read failure in the first render, while lanes were still running. Every later `gate` run at this head concluded success (131767857033, 131767844306, 131767282164).
  - `pr-contract / pr-contract` 131766945685 concluded success at 08:01:26Z. That is after the last lane concluded (`tests / closures` at 08:00:39Z), so it is the run that checked the body.
  - `tests / nightly-status` 131759522273 is failure. It is outside merge_train.py's owed-reds set (it grades main), so it is owed nothing here.
  - The body's `## Red checks: none` stands under that run.
- tests/entities.py could not run in this container. With `env -u BASH_ENV`, venv-ci's python lacks homeassistant, and venv-ha lacks paho (ev/entities.log). The new tracked file's classification therefore rests on CI's green `tests / closure-scope` and `gate`, not on my run.
- No finder's harness is named. This is instrument work built from roster carries, and the self-test arms are the carries' specified controls (step 9: the harness is the fixer's, built to the carry text).
