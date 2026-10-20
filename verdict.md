Fix review: blocked d2d361a449f0356f877e49a7ff59521f33739c37 claim-false: a git gc --auto that update_pr.sh's fetch/merge/commit detaches inherits lock fd 9 and holds the branch lock after the run exits (false BUSY naming a dead pid); pr-contract is also red on this head (carry-audit UNROUTED ## Forward-carry), against a body saying "Red checks: none"

bus-nonce: 0536df20a88febd26c99c2562b2d8147

Round 1. Measured head d2d361a449f0356f877e49a7ff59521f33739c37 (still the PR head and branch tip at posting; main at 2bd48adfa). Worktrees at the merge base d5cd00311 and at the head; my own probes are disclosed as mine (ev/probe.sh, ev/run2.sh).

## RESULT lines

- RESULT update_pr.sh --self-test @head: delivery_row 5/0, pr_args 49 checks 0 failed -- matches body (ev/update_pr_selftest.txt)
- RESULT update_pr.sh --self-test @base d5cd00311: pr_args 46 checks 0 failed -- matches body (ev/base_update_pr.txt)
- RESULT cloud_relay.sh --self-test @head: 72 checks 0 failed; @base 69/0 -- matches body (ev/cloud_relay_selftest.txt, ev/base_cloud_relay.txt)
- RESULT test-first (head pr_args.sh + base update_pr.sh): 49 checks, 1 failed, the BUSY arm -- matches body (ev/testfirst_pr_args_base_update_pr.txt)
- RESULT mutant "if [ \"$urc\" = 75 ]" line deleted: cloud_relay 72 checks, 3 failed (the three named arms) -- matches body (ev/mutant_75_cloud_relay.txt)
- RESULT mutant # mut:lock: pinned by the harness's own arm "ok mutant mut:lock ... removes the in-flight run's worktree" (ev/update_pr_selftest.txt)
- RESULT mutant "9>&-" removed from the push: 49/0, nothing fails -- the fd-close is unpinned (ev/mutant_fdclose_update_pr.txt). Not blocking by itself: the self-test has no app_push.sh, so it cannot pin it.
- RESULT null control (dead-pid lock file, no holder): passes -- the run reaches its push (brief item 3 holds)
- RESULT git merge-tree --write-tree origin/main d2d361a449f0356f877e49a7ff59521f33739c37: rc=0, clean, no claim-file driver involved (ev/merge_tree.txt)
- RESULT VERSION / manifest / notes heading: untouched (pr-contract's own version-edit step: "no version edit")
- RESULT CI on d2d361a449f0356f877e49a7ff59521f33739c37 (check-runs API, 49 runs): pr-contract FAILURE x2 (jobs 118384716655, 118384845043); every other completed gate check success or skipped; "Analyze (python)" (CodeQL) still in_progress at read time.

## Blocking 1 -- brief item (2) refuted: children inherit the lock fd

The body says "The push runs with `9>&-`, so no long-lived grandchild can inherit the lock." Only the push closes fd 9. `exec 9>>"$WT.lock"` sets no close-on-exec, so every command before the push inherits it: `git fetch` (l.39, l.42), `git worktree add` (l.46), both `$G merge` (l.49, l.51), ensure_row's commit (l.57). Each of these can run `gc --auto` / `maintenance run --auto`, which by default daemonizes (gc.autoDetach=true; git's daemonize() closes only fds 0-2). The detached gc keeps the open file description, so the flock outlives the run.

Probe (mine, ev/probe.sh + ev/run2.sh: update_pr.sh l.29-30 verbatim, then one `git gc --auto` over 20000 loose objects, git 2.43): after "run exits" -> "probe: lock HELD after the run exited", with /proc showing `git gc --auto` and its child `git prune --expire 2.weeks.ago` holding l3.lock; free one second later (ev/probe_gc_inherits_lock.txt). In the real store the hold lasts as long as a repack of the shared object store, and the frequent small fetches update_pr does (below unpackLimit, so loose) are what accumulate toward gc.auto.

Consequence: a run started in that window prints "update_pr: BUSY: another update_pr.sh run (pid N)" naming the dead pid of a run that has ended. Fail-safe for the relay (it retries), but the orchestrator is told a run is in flight that is not, and the obvious operator response to a lock held by a dead pid is to delete the lock file -- which, when a real run does hold it, re-opens exactly the race this PR closes (a new inode, a second lock). The failure direction is safe; the claim is false, and the brief named this property explicitly.

Fix options (fixer's call): disable auto-detach for this script's git (e.g. `export GIT_CONFIG_COUNT=2 GIT_CONFIG_KEY_0=gc.autoDetach GIT_CONFIG_VALUE_0=false GIT_CONFIG_KEY_1=maintenance.autoDetach GIT_CONFIG_VALUE_1=false` right after the lock, so a gc runs inside the run and holds the lock only legitimately), or `-c gc.auto=0`; or have the BUSY message check whether the recorded pid is alive and say "held by a descendant of dead run N" instead of "another run". Either needs an arm (a detached child holding fd 9) and a body sentence that is true.

## Blocking 2 -- pr-contract red, body says "Red checks: none"

Both pr-contract runs on d2d361a449f0356f877e49a7ff59521f33739c37 fail at `carry_audit.py check`: "UNROUTED body item 316165bb (## Forward-carry) [section]: 'none. The BUSY retry is documented in ...'". Reproduced locally (ev/carry_audit_body_forward_carry.txt: rc=1); the same section reading only `none` passes (rc=0). This is the post-prepr body edit the brief warned of: the trailing sentence turned the section into an item. Not a roster artefact. The body's `## Red checks: none` is therefore false at this head. Fix: `## Forward-carry` reads `none` alone (move the INSTRUMENTS.md sentence elsewhere), then name pr-contract under Red checks with its cheaper detector (prepr's carry_audit run, which the post-prepr edit bypassed) per defect-root-cause.md.

## Roster

R10-UPDATE-PR-LOCK is not on origin/main's roster (git grep: no hit); it is on origin/handoff/audit-r10-roster (04842e752 "roster: +R10-UPDATE-PR-LOCK", wave-r10-groups.json:4861). It is not what turned pr-contract red here. If the fixer routes a Forward-carry item to that group instead of writing `none`, carry_audit reads the newest roster via roster_lib and may refuse it as unknown until the roster PR merges -- so `none` is the safe repair.

## Brief items

1. Lock before every mutation: holds. Before l.29 only `mkdir -p $P` and read-only argument checks run; fetch, worktree remove/add and the $WT.log write all follow l.33. Released on every exit path, SIGKILL included, by fd close -- subject to Blocking 1 (inherited copies).
2. No child inherits the fd: refuted (Blocking 1).
3. Stale lock from a dead run does not block: holds (null control; flock is on the description, not the file's content).
4. 75 cannot mask a real failure: holds in practice. No other `exit 75`/sys.exit(75) exists under tools/; a signal death is 128+n; pr_refuse and pr_push_failed exit 1. Residual, not blocking: under errexit any external command exiting 75 (EX_TEMPFAIL) would be read as BUSY; and a hung holder makes the relay retry forever with only a stderr line and no OWED ledger entry. The relay's other non-zero codes are unchanged and still OWED (existing arms pass).
5. open_pr.sh / app_push.sh shared fixed paths: app_push.sh uses mktemp only -- no finding. open_pr.sh has fixed per-topic paths ($D/body.md, $D/wt, p1.log, p2.log), but no automated caller runs it (cloud_relay only runs update_pr.sh), and a concurrent second run fails at `git worktree add -b` instead of removing anything. Its one overlap with this race is $D/body.md being rewritten (l.31) before that failure: two manual open_pr.sh on one topic. No finding owed under this class; noted for the fixer.

## Other steps

- Step 6 class: the body's class is "a fixed per-branch path removed under a concurrent run"; I checked the other writers under $HPO_STATE_DIR/pr (open_pr.sh) and found no automated second runner.
- Step 7: body's ## Head names d2d361a449f0356f877e49a7ff59521f33739c37 -- matches.
- Step 14: no budget, closure, claim or golden file moves.
