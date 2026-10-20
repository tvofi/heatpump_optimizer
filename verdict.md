Fix review: blocked 89f329f6ba7928b51feb29e7a8d4ac7e7c14b0fc mutant-survives: the background push (update_pr.sh:118-119) and the holder's killpg (update_pr.sh:57) are claimed fix mechanisms, yet reverting either leaves pr_args 56/0

Round 3 of R10-UPDATE-PR-LOCK, so the next round is the fourth, where `fixer.md` owes a re-cut rather than a repair. Measured at head 89f329f6ba7928b51feb29e7a8d4ac7e7c14b0fc, which merges code head a3af24fc and origin/main bb5b21a88. The head is unchanged at ls-remote. The role files are current: `git diff merge-base...origin/main -- dev/governance/roles/` is empty.

## What holds
RESULT pr_args-head runs=3 checks=56 failed=0 (ev/pr_args_run{1,2,3}.txt), plus 3 instrumented runs at 56/0 (ev/timed-*.txt). Those runs were under concurrent load, and I saw no flake.
RESULT cloud_relay-head checks=74 failed=0 (ev/cloud_relay.txt)
RESULT named-mutants mut:lock mut:unlock mut:stop mut:drain mut:pgrp each fail their arm in the head's own self-test runs (`ok   mutant ...` lines).
RESULT reviewer-mutant holdgrp (holder stays in the run's group; os.setpgid removed at :48) = 2 failed (the TERM and SIGKILL arms). Killed.
RESULT reviewer-mutant zombie (zombie filter removed at :54) = 1 failed (the TERM arm). Killed.
RESULT reviewer-mutant whiletrue (round 2's: the parent watch becomes `while not stop`) = 3 failed, including the SIGKILL arm. Killed, which confirms the body's claim.
RESULT reviewer-mutant noack (upd_stop does not wait for the .stopping ack) = 0 failed. Benign: the holder keeps the flock whatever the run does, so the ack is cosmetic.
RESULT daemonize-variant (my own instrument, ev/daemonize-variant.diff): every stoprun launches through the real `daemonize.py`, then `kill <pid>`. With TERM and with KILL, run 2 is BUSY and run 3 takes the lock. The round-2 finding is fixed. Under the variant only `mutant mut:pgrp` fails, as expected: a daemonize session already leads its group, so that mutant cannot bite there. This confirms the body's "a daemonize.py session already leads one".
RESULT merge-tree origin/main(bb5b21a88) 89f329f6 = clean, rc=0, tree dc5406c5 (ev/merge-tree.txt)
RESULT CI 89f329f6 = no red. 49 runs: success, skipped, or CodeQL neutral, with Analyze (python) still in progress (ev/ci-check-runs.txt). The round-0 red pr-contract runs are named and answered in the body (step 7a2 is the detector).
RESULT VERSION, manifest, notes heading, budgets and claim files = untouched.
The body's figures are re-derived: 56 against main's 46 (10 new arms enumerated, which I counted from the diff), and 74 against main's 69 (5 new checks in the diff).

## Why blocked: two claimed mechanisms are unpinned
The body names two mechanisms as part of the round-3 fix:
- "The push runs in the background under `wait`, so a trapped signal reaches the run at once. Without that, it would wait for a foreground push to finish."
- "The holder TERMs the run's group (`killpg`)."

Reverting either leaves the whole self-test green. I added timings to the stop arms (ev/trace-*.txt and ev/instr.py, an instrument of my own, disclosed per fix-review step 9):

| tree | kill→run1 exits | push ends after kill | run2 BUSY | pr_args |
|---|---|---|---|---|
| head | 0.055 s | 2.00 s (TERMed) | yes | 56/0 |
| mutant fg: push in foreground, `& PUSHP=$!`/`wait` removed (ev/mut-fg.diff) | 6.04 s (push already over) | 5.98 s | yes | 56/0 |
| mutant nokillpg: `os.killpg` → `pass` (ev/mut-nokillpg.diff) | 0.054 s | 5.98 s (never TERMed: a stopped update pushes on) | yes | 56/0 |

So the mechanisms behave as claimed at the head, but no check pins them:
- **Under fg,** the TERM arm passes only because run 2 lands inside the holder's 0.5 s poll and drain tail after run 1 exits. The push had already ended, so the arm's BUSY is a timing artefact, not evidence that the lock covers a live push.
- **Under nokillpg,** `kill <pid>` no longer stops the push: it runs to completion and could still push to the PR. The arm cannot see that.

Fixer.md step 2 says to delete the fix's production lines and paste the failing check names. The brief asks to revert each part and confirm its arm fails. Neither holds for these two parts.

A repair that would close this: in `stoprun - TERM`, assert that run 1 exits within about 1 s of the signal (this kills fg), and that the stub reached its TERM path, i.e. `ended` within about 3 s of the kill and not 6 s (this kills nokillpg). Then add `# mut:` tags on those lines. The lock-safety property, the finding itself, is pinned and sound. This block is about the stop-promptness claims only.

## Behaviour change (judged; not a block)
A run started from a script now leads its own group, so a group kill or Ctrl-C aimed at its caller (cloud_relay or tick_loop in a foreground terminal) no longer reaches it. The run finishes its push and frees the lock.
- This is bounded, and arguably safer than a half-done update.
- Under daemonize.py's documented stop (`kill <pid>` of tick_loop), nothing changes, because a single-pid TERM never reached the child before either.
- It is acceptable as disclosed.

Note, not blocking: both the leader test at :22 and the holder's `group()` depend on `ps`. With no `ps`, :22 never matches, so the run would re-exec forever, and `group()` returns 1, so the holder would hold the lock forever after a stop. Linux and macOS seats have `ps`. Worth a guard if the repair touches these lines.

Evidence: ev/ (self-test outputs, mutant diffs and outputs, timing traces, daemonize variant and trace, merge-tree, CI read).

bus-nonce: 2ac07f8612e3f55e4d7ed81753c89e5d
