Fix review: blocked 9629ae174f1099e11c6b17f80fe935ae6cba698b harness: class-open tools/audit/seat/train.sh -- the body dispositions train.sh as a caller that "stops a child that now reaps its own tree"; it does not: TERM to the pid in train.sh's own pidfile ends the launcher, removes the pidfile, and leaves 5 of 5 pids of the train's tree alive, 3 of 3 runs

bus-nonce: cd011a9bf3abe01097887890ee40fefd

Fixer round fix2524c. This is the second fix review of PR #2524 (review/2524 holds one earlier verdict, blocked at c071fa5f). Head measured: 9629ae174f1099e11c6b17f80fe935ae6cba698b. It was still the PR head when I posted (ev/head_at_post.txt). Its tree is byte-identical to the code head 6978fe22 the body measured (`git diff --stat 6978fe22 9629ae17` is empty). Contract: dev/governance/roles/fix-review.md from origin/main. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

Finder harness: the earlier verdict's ev/ tree (stub.sh and the hp_shape.sh shape). The reviewer before me built it and disclosed it as theirs. I re-ran it against the real `push_app` body extracted from each revision. My copies and drivers are in ev/harness_reviewer/. The train.sh harness (ev/harness_reviewer/train/) is mine, and I disclose it as reviewer-built.

## Block

- harness: class-open tools/audit/seat/train.sh. The body's level-2 rule greps for callers of handoff_push, open_pr, update_pr and remerge_main, plus `tool("remerge_main"|"app_push")`. It does not return callers of the runner-py `merge_train.py`. The body covers that gap in prose: "Callers above level 2 stop a child that now reaps its own tree: `train.sh` runs `merge_train.py`, and `tick_loop.sh` runs `cloud_relay.sh`."
  - For train.sh this is false. train.sh runs `merge_train.py batch` as a foreground child of a subshell (train.sh:239-250). It installs only `trap 'rm -f "$pidfile"' EXIT` (train.sh:214) and forwards no signal.
  - Measured with the head's train.sh verbatim, a seat-venv shim and a `merge_train.py` stub that runs the finder's two-level stub tree. I sent TERM to the pid recorded in `$state/train.pid`, which is the launcher's own pid. Result: the launcher is gone, the pidfile is removed, and 5 of 5 tree pids are alive (non-zombie) after 4 s, in 3 of 3 runs (ev/train_sh_term.txt).
  - The real merge_train.py receives no signal in this shape, so its `stop_on_signal()` never runs. The train goes on pushing, and the removed pidfile lets a second train.sh start on the same state dir. train.sh's own header names that as a hazard: "two concurrent trains on one state dir have corrupted a queue mid-run".
  - train.sh is live: INSTRUMENTS.md:617 and sweep_template.md:58 name it as the batch-merge launcher. The PR does not change train.sh, so base and head behave the same.
  - Repair: forward the stop to the child (the same `pr_exit_trap` and asynchronous `wait` shape this PR uses, or an exec), add train.sh to the census's enumeration, and correct the prose.
  - The same sentence is also wrong about `tick_loop.sh`, which leaves the relay running when stopped. There that is a documented choice: "A relay still in flight then is left running, never killed (its update_pr.sh may be mid-push)" (tick_loop.sh:11-12). It needs only a correct disposition in the body, not code.

## Findings

- #2502's own title and brief require that "a TERM, INT, HUP or SIGKILL of a running update must not free the branch lock while its push still runs". At this head the SIGKILL clause is not met. The body says "SIGKILL is out of scope, because no trap runs on it", and pr_branch_lock's comment says "a SIGKILLed run's holder exits once its parent is gone". The KILL arm (pr_args.sh:673) asserts only that no stale lock is left. The body's ## Forward-carry is "none", so this scope cut is routed nowhere, and carry_audit does not read "out of scope" as a deferral. The body should route it, or the merge must not close #2502. Carry: #2502
- The roster's Revision-12 carry on this group (origin/handoff/audit-r10-roster, R10-UPDATE-PR-SIGNALS) says the group owns prevention, including "every self-test runs under a timeout in its own process group, reaped on exit". At this head, open_pr.sh, update_pr.sh and pr_args.sh contain no `timeout` and no `setsid`, and the body neither does nor routes this item. Carry: #2502

## Evidence

- (a) Pusher enumeration, checked independently.
  - The census (`pr_args.sh --pushers <rev>`) returns 16 paths at HEAD, 93e6a63d and c071fa5f. It reports 0 OPEN with rc 0 at HEAD, and 6 OPEN with rc 1 at both of the others, as the body states (ev/census.txt).
  - My enumeration is `git grep -lE '(app_)?push\.sh'` over every tracked file: 80 paths (ev/enum_all_mentions.txt). The tools/ paths outside the census are body_push.sh, bus.sh, cloud_dispatch.py, record_row.py, state_docs.py, tmp_paths.py, r9_rc_bus_fetchhead.sh, prepr.sh, INSTRUMENTS.md and cloud_relay.sh. Each one names body_push.sh or handoff_push.sh, or carries a comment, prompt text or fixture.
  - cloud_relay.sh is level 2 and is closed in this diff.
  - body_push.sh pushes with `git push` and runs only `ci_predict.py` in the foreground, which forks nothing but git (ci_predict.py:61). It is not an app_push caller and carries no CPU-bound subtree, so I do not count it a seam of this class.
  - Outside tools/, the only callers are agent prompt text (.claude/workflows/audit-verify.js:284), self-test steps in governance.yml, and audit harnesses.
  - Above level 2, ev/level2_mine.txt returns train.sh (see ## Block) and tick_loop.sh (detached by design).
- TERM/INT/HUP harness on handoff_push.sh's real `push_app`, extracted per revision (ev/term_harness_handoff_push*.txt):
  - Head: TERM, INT and HUP each leave 0 of 4 survivors (3 of 3 runs each).
  - Base 93e6a63d (null control): 4 of 4 survivors under every signal.
  - An unrelated sleeper survives every run.
  - My first INT run showed 4 of 4 at both ends. That was a harness artifact: a background job inherits SIGINT ignored, so the INT never reached the pusher. The re-run with SIGINT reset to the default (ev/term_harness_handoff_push_sigdfl.txt) is the measurement.
- (b) carry_audit against this body with `--roster-ref origin/handoff/audit-r10-roster` prints `CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit_body.txt). Both pr-contract runs at this head concluded success.
- (c) The earlier survivors, each mutated at this head in a separate detached worktree and restored, with `git status` clean after each (ev/mut/):
  - M0 (no change): 86/0.
  - app_push `pr_exit_trap cleanup` → `trap cleanup EXIT`: app_push 186/1 (prepr tree survives, got 3).
  - `# mut:grace` KILL loop emptied: 86/1.
  - `# mut:exitreap` trap line emptied: 86/11.
  - `# mut:sigign` emptied: 86/1.
  - handoff_push push in the foreground: 86/2 (both census arms).
  - remerge_main push in the foreground: 86/2 (both census arms).
  - cloud_relay `pr_exit_trap` removed: 82/1.
  - merge_train `p.terminate()` → `p.kill()`: 200/1.
  - `PR_REAP_SPARE=$LKP` removed: 86/2.
  - Every mutant is killed. `pr_signal_traps` no longer appears in the tree (git grep returns 0 lines). The foreground mutants are killed by the static census arms. The behavioural kill for the handoff_push shape is my harness run above.
- Self-tests at this head with PREPR_SKIP_CLOSURES=1, matching the body's table (ev/selftests_head.txt):
  - open_pr and update_pr: 86/0 each.
  - handoff_push: 2/0, with delivery_row 5/0.
  - app_push: 186/0.
  - cloud_relay: 82/0.
  - merge_train: 200/0.
- Conflict resolution.
  - Every `# mut:` anchor main carries in update_pr.sh, handoff_push.sh and pr_args.sh is present at this head, among them rowonly, unpushed, prtopic, push-update/open/row, lock, unlock, watch and stop.
  - app_push.sh keeps main's `row_only_checks` gate (app_push.sh:472).
  - Against main, the only main lines the PR removes are pr_branch_lock's own two traps and main's TERM/KILL stoprun block. The lock's TERM property is now the `heldrun` arm (pr_args.sh:667). The KILL "no stale lock" and `mut:watch` arms are still present (pr_args.sh:673, 675). Diffs: ev/diff_conflict_files_vs_main.txt and ev/diff_pr_args_vs_main.txt.
- Merge: `git merge-tree --write-tree origin/main 9629ae17` exits 0 against 93e6a63d (ev/merge_tree.txt). It also exits 0 against origin/main 3976515a, which main moved to during the review.
- Cheap figures at this head (ev/cheap_checks.txt):
  - STRUCTURE RATCHET PASSED.
  - tmp_paths: 0 refused, 0 stale.
  - throwaway_git: 0 refused, 0 stale.
  - `Architecture score: dS +0.0000 NULL`.
  - `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, with scope.run naming tests/entities.py.
  - No VERSION, manifest, notes-heading or claim file in the diff.
  - 9 files changed.
- Figures I could not re-derive:
  - "ALL 2382 ENTITY CHECKS PASSED": this container has Python 3.11 and entities.py needs 3.14. Not verified here.
  - The seat-selftest harness `RESULT survivors=0`, S01–S38: not re-run (heavy).
- CI on this head, from the check-runs API (ev/check_runs_final.json):
  - nightly-status is red. It grades main, and this diff (tools/ scripts plus one delivery row) does not reach what it reads.
  - `closures` and `Analyze (python)` were still in progress when I posted.
  - Every other completed run is success, skipped or neutral.
- Red checks across the range (ev/red_per_commit.txt):
  - pr-contract was red at 6fd073c9, 50571afa and c071fa5f. The 50571afa log shows the same carry_audit refusal of 3 unrouted items that the body's ## Red checks answers. The body names only c071fa5f, but the cause is the same.
  - The other non-success runs at 6fd073c9 were cancelled by a newer push.
- Group naming: the dispatch calls the group R10-PUSHER-REAP, but no roster group has that name. The roster entry and the delivery row are R10-UPDATE-PR-SIGNALS (#2502). Its resume note records the pusher-reap deliverable.
