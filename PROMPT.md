CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-update-pr-signals, at head 5e83e3d8897aeb3661aa20278c2fd872284f04fb. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The toolchain (venv python, node, gh) is on PATH from the environment. Run anything heavy in the background with Monitor and no timeout.
Role: read dev/governance/roles/fixer.md and CLAUDE.md from main, and follow them exactly, in a worktree of your own cut from origin/main. Fetch 5e83e3d8897aeb3661aa20278c2fd872284f04fb for the base you were given.
Output: push the code to refs/heads/handoff/r10-update-pr-signals, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-update-pr-signals <body.md>`, which pushes refs/heads/handoff-body/r10-update-pr-signals; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
PRIOR VERDICT (blocked): #2825 at head 5e83e3d8897aeb3661aa20278c2fd872284f04fb, comment 6406256342 (2026-10-26T01:33:14Z), carry-missing: roster carry 6 (triage P163, the lock-age STUCK andon) is neither implemented nor dispositioned in the body. The reviewer found the code otherwise sound: round 3's block is closed (8 of 8 head runs of pr_args.sh --self-test green under 6-way load). Fix what is below at this same branch, then re-check every carry.

IDENTITY: this pull request is authored by the hpo-author App through tools/pr/app_push.sh. Never push.sh, never tvofi.

ROUND 5 FIXER for R10-UPDATE-PR-SIGNALS (topic r10-update-pr-signals, branch fix/r10-update-pr-signals). Start from the PR head 5e83e3d8897aeb3661aa20278c2fd872284f04fb (handoff/r10-update-pr-signals is 37bd04858, an ancestor of it): fetch origin, continue from the PR head, merge origin/main (merge, never rebase; install the merge drivers first: python3 tests/env_drift.py --install-merge-driver and python3 tools/merge/ledger_merge.py --install).

git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com   (run this first, before any commit)

THREE-ROUND RULE: this is the fifth round, so the body is RE-CUT wholesale, not repaired: only the headings .github/PULL_REQUEST_TEMPLATE.md requires (derive them from the file), the arms that fire, and only figures you re-take in this pass, each stamped with the origin/main tip and date -u. Delete narrative, round history and self-criticism. It answers every roster carry below item by item and keeps the routing so that python3 -I tools/audit/carry_audit.py pr 2825 prints 0 unrouted.

THE BLOCKS TO CLOSE:
1. CARRY 6 (P163), implement it, with its three controls (the reviewer named implementation first; do not re-route it without the orchestrator's word): pr_branch_lock writes its start epoch next to the pid; cloud_relay.sh reports any lock older than HPO_PUSH_STUCK_SECS (default 900) as STUCK <branch> <pid> <age>s. Controls: a lock aged 901 s is reported and one aged 899 s is not; a released lock is never reported; a mutant that reads the file mtime fails (a mutant-killing check for each, run against the real file with the one line deleted). Report-only. A git grep -nE 'STUCK|HPO_PUSH_STUCK' tools/audit/seat must be non-empty at your head, with a fixture.
2. Round 4's wait counts ticks, not seconds (200 ticks measured 15.4-15.5 s under 6-way load on 4 CPUs; each tick spawns Python so the bound grows with load). Replace it with a wall-clock deadline (date +%s) shorter than the stub push, so the comment ("bounded at 10 s") becomes true. Keep pr_args.sh --self-test at 0 red of 6 parallel runs on a 4-CPU box (print red count beside run count) and null-control it: a correct holder must still read held at the bound.
3. The body is stale for round 4 (describes rounds 1-3, figures at cfc707961, Red checks says no CI run). The re-cut answers this.
Carry dispositions already accepted by the reviewer, restate as lines: quiet output (carry 4 below) and the 12 outside seat self-tests: Carry: R10-FLOW-JIDOKA. The millisecond startup window of PR_BOUND_PY and the /proc skip on macOS: Carry: dismissed: with the reasons the verdict gave (a group KILL timed to the first millisecond; every runner that runs this self-test has /proc, the skip is printed not silent).
## Red checks: governance / delivery-status is red on main's overdue rows (not a required context; the diff does not touch them). Name it, and answer anything else red at YOUR head.
Run the finder's harness at both ends: the reviewer's par6 load (six pr_args.sh --self-test runs in parallel) at your head and at 5e83e3d8, and the round-2 grpkill harness under probe/rev-2825-4ba59ff1.
Push handoff/r10-update-pr-signals then body_push.sh r10-update-pr-signals <body.md> (handoff-body/r10-update-pr-signals is the return signal). Do not move the head once pushed; a delta review follows.

CARRIES (6, from the live roster; each must be answered item by item):

CARRY 1 of 6:
Carried from #2469 (R10-UPDATE-PR-LOCK) at 931e9a0f, round-4 split under the three-round rule:
- A SIGKILLed run's holder frees the lock within 2 s while the push that run started may still be running in the worktree. Holding it until that push ends needs a drain of the run's process group, and in a container whose PID 1 reaps orphans late that drain's arm failed 7 of 7 runs (#2469 round 4).
- A signal to the run's whole process group, such as `kill -TERM -- -<pgid>` or SIGHUP when its terminal closes, also reaches the holder. The holder has no handler, so it exits before the push it covers. This is reasoned from the code, not measured here. (SIGINT does not reach it: bash starts the holder in the background, with SIGINT ignored.)
- Under `set -e`, any command inside `update_pr.sh` that exits 75 reads to the relay as BUSY and is retried rather than recorded. Today only the lock path exits 75.

CARRY 2 of 6:
Revision 12 (orchestrator, 2026-10-21): a stale upd-fix-r10-ci-layout-g.lock held dead pids and stalled the relay's handoff arm on PR G for over 30 minutes, and an orphaned update_pr.sh self-test spun 8.6 h at about 67% CPU. This group owns prevention: a lock records its owner's pid and start time and is broken, with a logged line, when that pid is dead or was reused; every self-test runs under a timeout in its own process group, reaped on exit. R10-FLOW-ANDON owns detection.

CARRY 3 of 6:
update_pr.sh leaves its upd-fix-<branch> worktree checked out on the branch after it exits; the merge train's recarry then parks the PR (3 instances: #2513, #2544, #2547). train --free-holders now cures clean holders; the source fix is that update_pr.sh detaches or removes its own worktree on exit.

CARRY 4 of 6:
tvofi 2026-10-24 recommendation (a) (owner accepted; CARDS.json (prestudy-mech, r10s6 scratch, not in the tree)): quiet output by default for tools/audit/seat/update_pr.sh, tools/audit/seat/open_pr.sh and the per-car progress of tools/audit/seat/merge_train.py, with the same convention as tools/pr/prepr.sh (R10-FLOW-JIDOKA owns that script): one result line per step, the failing step's tail, the full output in a printed log, a verbose switch to restore the stream, and every key line kept (mode, the failing check names, the final summary). merge_train.py is also edited by R10-FLOW-AUTOTRAIN: touch only its output calls and merge the other group's branch before yours. Control: a seeded failure shows its tail in quiet mode; the exit codes agree across quiet and verbose; each rule has a mutant.

CARRY 5 of 6:
From #2549 (review 6319952656, item 01ce8b81), routed by routing audit 1 (2026-10-24): it carried no Carry: marker and is not implemented (real residual; `git grep -iE 'setsid|pgid|process group' origin/main -- tools/audit/seat/cloud_relay.sh tools/audit/seat/update_pr.sh` is empty). Residual, not blocking: the detached holder is a child of the loop's process group, so a group-wide signal to a stopped loop (e.g. `timeout`, or a daemonizer killing the pgid) still takes an in-flight relay with it. That is the same exposure the serial base had, not a regression.

CARRY 6 of 6:
Trial (triage P163): lock-age andon (V84, narrowed to the push run). Report-only; remove it if it reports no STUCK line in its first 48 h. `pr_branch_lock` (`pr_args.sh:66`) writes its start epoch beside the pid. `cloud_relay.sh` reports any lock older than `HPO_PUSH_STUCK_SECS` (default 900) as `STUCK <branch> <pid> <age>s` on its level, where the tick reads it. It reports only, and the reap stays this group's. Seat and beat SLOs are R10-ORCH-BEATD's carries 8, 15, 17 and 21. Controls: a fixture lock aged 901 s is reported and one aged 899 s is not; a released lock is never reported; a mutant that reads the lock file's mtime instead of the recorded start fails a fixture whose file was touched later. triage: dev/programme/triage/s6-batch29.md#P163

GROUP BRIEF:
Signal-safe update_pr.sh: a TERM, INT, HUP or SIGKILL of a running update must not free the branch lock while its push still runs. Split from #2469 round 4, whose SIGKILL arm failed 7/7 in the cloud container because PID 1 reaps orphans late and the holder counted the zombie. Every arm must be deterministic across containers: wait on a condition, never a fixed window. Also covers the ps dependency of the leader check and the holder (carry on R10-ROSTER-OPS).

FINISH: before the push, run the ratchet (tests/structure.py) and prepr as the roles say; no budget raise without the orchestrator's confirmation (stop and ask via SendMessage-equivalent: state it in the handoff body). No Claude footers, no host paths in anything pushed.
