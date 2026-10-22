Fix review: blocked a01627177715d6f363eee2f8add5b19f7a97945d mutation-vacuous: tools/audit/seat/cloud_relay.sh:234, the production update launch the body names as closed with update_pr as the lead -- dropping its `&`, or not naming it PR_REAP_LEAD, leaves cloud_relay 83/0 and pr_args 90/0, because every relay arm takes the HPO_RELAY_UPDATE stub branch

bus-nonce: 41f2df2235057fbd131463f9f71a70c2

This is the third fix review of PR #2524. review/2524 holds the blocks at c071fa5f and 9629ae17. A fourth round owes a re-cut under `fixer.md`, not a repair.
- Head measured: a01627177715d6f363eee2f8add5b19f7a97945d. It was still the PR head at 05:08:50Z (ev/head_at_post.txt).
- Contract: `dev/governance/roles/fix-review.md` from origin/main. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- The PR's 10 files are byte-identical between the code head f1e7b889 and this head (ev/head_chain.txt). Figures the body measured at f1e7b889 therefore apply here.
- Finder's harness: the block's `evidence/harness_reviewer/train/` from origin/review/2524. Its sha1s are 35c7d548 (run_train.sh), 64758b0b (stub.sh) and 04cc1898 (merge_train.py stub), which match the body.
- Reviewer-built, and disclosed as mine: the INT and HUP variants of that driver (ev/harness_finder/), the mutant runner (ev/mut/muts.sh, mut.py), and the production-route probe below.

## Block

- mutation-vacuous: tools/audit/seat/cloud_relay.sh:233-235.
  - The PR splits the relay's update launch into two lines. The stub branch is `"$HPO_RELAY_UPDATE" … >&2 &`. The production branch is `else bash "$HERE/update_pr.sh" … >&2 & fi`. `PR_REAP_LEAD=$!` follows both.
  - The body names the production line as closed: "Line `bash "$HERE/update_pr.sh" … >&2 &` runs update_pr: **closed in this diff**, with update_pr as the lead (the lead arm)".
  - Every cloud_relay self-test arm sets `HPO_RELAY_UPDATE`, which line 416 exports for the rest of the test. So no arm ever runs the production line.
  - Two one-line mutants of that line survive the whole closure (ev/mut/F-CR-ELSEFG.txt, ev/mut/F-CR-ELSELEAD.txt, ev/mutlogs/):
    - F-CR-ELSEFG, the production `&` dropped: `cloud_relay self-test: 83 checks, 0 failed` and `pr_args self-test: 90 checks, 0 failed`. A stopped relay would then wait behind a foreground update_pr.sh, the deferral this class exists to remove.
    - F-CR-ELSELEAD, the production branch not named `PR_REAP_LEAD`: cloud_relay 83/0. The relay's reap would again TERM update_pr.sh's lock holder beside the push. That is the #2502 defect one level up, and the body says this round fixes it.
  - The mutants are not equivalent. In a scratch worktree, my probe routed the committed lead arm through the production branch: `HPO_RELAY_UPDATE=` empty, with `lead.sh` copied over `update_pr.sh` (ev/mut/prodroute_*.diff).
    - Unmutated head: 83/0 in 3 of 3 runs.
    - F-CR-ELSEFG and F-CR-ELSELEAD: each 83/1, `FAIL a relay TERMed mid-update TERMs the update alone first …`, in 3 of 3 runs (ev/mut/prodroute.txt).
  - At the base 9629ae17 the stub and production commands shared one `{ if …; fi; } >&2 &`, so the stub arms exercised the production `&`. This round's split created the unpinned line.
  - Repair: launch both branches through one line, so the stub arms run the production launch. For example, `upd=(bash "$HERE/update_pr.sh"); [ -n "${HPO_RELAY_UPDATE:-}" ] && upd=("$HPO_RELAY_UPDATE"); "${upd[@]}" "$br" "$hs" "$body" $iss >&2 & PR_REAP_LEAD=$!`. Then re-run CR-LEAD and the two mutants above.

## Findings

- F-TR-RC survives. In train.sh, `rc=0; wait "$PR_REAP_LEAD" || rc=$?` turned into `|| :` (merge_train.py's exit status never reaches TRAIN_RC, `$state/rc` or train.sh's own exit) leaves `train.sh self-test: ok` (ev/mut/F-TR-RC.txt). The gap predates this PR: the same mutant at 9629ae17 (`rc=$?` → `rc=0`) also passes (ev/mut/F-TR-RC_at_base.txt). This PR rewrote the line, though, and an arm asserting a failing stub's rc reaching `$state/rc` would pin it. Carry: R10-UPDATE-PR-SIGNALS
- TR-EXEC survives, as the body discloses: train.sh's `exec ` deleted leaves all three self-tests green (ev/mut/TR-EXEC.txt). On this container's bash 5.2.21, `( cd /tmp || exit 2; sleep 3 ) &` shows `sleep 3` as the pid itself with 0 children (ev/exec_equiv.txt), which confirms the body's equivalence claim here. The macOS bash 3.2 case is not measured here. Carry: dismissed: equivalent on bash 5.2 (measured); the body names the bash 3.2 case it is for, and no test on a bash that execs anyway can separate the two
- #2502's SIGKILL clause is not met at this head. The body routes it under `## Forward-carry` and does not close #2502 (no closing keyword in the body). The group's roster carry on origin/handoff/audit-r10-roster already states it as owed (the #2469 round-4 carry). Carry: R10-UPDATE-PR-SIGNALS
- The roster's Revision-12 self-test isolation ("every self-test runs under a timeout in its own process group, reaped on exit") is not built here. The body routes it under `## Forward-carry`. The group's roster carry already holds it. Carry: R10-UPDATE-PR-SIGNALS

## Evidence

- The earlier blocks at this head:
  - 9629ae17 harness: class-open tools/audit/seat/train.sh is cleared. The finder's harness, run against each end's train.sh beside that end's pr_args.sh, 3 of 3 runs per cell (ev/finder_harness_train.txt):
    - TERM: base `survivors=5/5 pidfile=removed`; head `survivors=0/5 pidfile=removed`.
    - INT: base `launcher=alive pidfile=present survivors=5/5`; head `launcher=gone pidfile=removed survivors=0/5`.
    - HUP: base 5/5; head 0/5.
  - Null control: with a `sleep 60` outside the tree, the head run prints `survivors=0/5 bystander=alive` in 3 of 3 runs (ev/null_bystander.txt).
  - Failing test first: a69446c35's `train.sh --self-test` prints `left 5 of 5 pids of its tree alive (pidfile removed, early)` in 3 of 3 runs (ev/failing_test_first_a69446c35.txt).
  - c071fa5f class-rule-missing stays cleared: the census and level-2 rules are named and re-run below.
  - The 9629ae17 findings (SIGKILL, Revision-12) are now routed by the body. carry_audit counts them as 2 routed.
- Mutants, each in a fresh detached worktree at this head with an exact-once anchor, the worktree removed afterwards (ev/mut/, logs in ev/mutlogs/):
  - M0: train ok, cloud_relay 83/0, pr_args 90/0.
  - TR-TRAP: train refuses, `left 5 of 5 … (pidfile present, none)`.
  - TR-AFTER: train refuses, `left 0 of 5 … (pidfile present, none)`.
  - TR-LEAD: train refuses at arm 10, `marks 'G early '`.
  - TR-FG: train refuses at arm 4, `the stubbed --ignore-red run did not succeed`. It is killed, but by an earlier arm than the stop arms, as the body states.
  - PA-LEAD: train refuses at arm 10; cloud_relay 83/1; pr_args 90/2 (the lead arm and the leadwalk arm).
  - PA-LEADTERM: train refuses; cloud_relay 83/1; pr_args 90/1.
  - PA-LEADWALK: pr_args 90/1, the stale-lead arm.
  - CR-LEAD: cloud_relay 83/1.
  - Fresh mutant F-PA-TENTHS (`PR_REAP_LEAD_TENTHS` default 300 → 0): train refuses, cloud_relay 83/1, pr_args 90/1. Killed.
  - Fresh mutants F-CR-ELSEFG and F-CR-ELSELEAD survive (## Block). F-TR-RC and TR-EXEC survive (## Findings).
  - Each of the body's figures for TR-*, PA-* and CR-LEAD is re-derived.
- Not re-derived: the earlier rounds' mutant list re-run at f1e7b889 (STOP, RECURSE, GRACE, SIGIGN, EXITREAP, SPARE, ORDER, M1–M9, OPENFG, UPDFG). The 9629ae17 review re-ran its own set at 86 checks. I did not repeat it at 90.
- Self-tests at this head, `PREPR_SKIP_CLOSURES=1` (ev/selftests_head.txt). Every row matches the body's table, re-derived:
  - open_pr and update_pr: 90/0 each.
  - handoff_push: 2/0, with delivery_row 5/0.
  - app_push: 186/0.
  - cloud_relay: 83/0.
  - merge_train: 200/0.
  - train.sh: ok.
  - tick_loop: 8/0.
- Class rules (ev/rules.txt), re-derived:
  - Census at HEAD: `16 ok`, rc 0. OPEN is 0 at f1e7b889 and 9629ae17, and 6 at 07fcbee2 and dcf12f49.
  - Level-2 rule: 28 lines in 9 files at this head and at f1e7b889, 27 lines in 9 files at 9629ae17, and 24 lines in 9 files at 07fcbee2. The per-file counts match the body's dispositions.
  - Level-2-py rule: 153 lines in 20 files at this head and at 9629ae17. The long-lived test per module gives merge_train 6, gate_lock 28, closure 1, layout 1 and contract_rerun 1. ci_predict, ref_privacy, pr_cap, orchestrator_tick and gh_comment each give 0. Every value matches the body.
  - My own enumeration is every mention of a runner or launcher name in tools/ that the level-2 rule does not match (ev/enum_unmatched.txt, 98 lines). It holds no further launch site: they are docstrings, self-test fixtures, the `tool()` table entry and messages. No tool launches train.sh: INSTRUMENTS.md, sweep_template.md and governance.yml name it for a person or seat.
  - The relay's production branch is the open seam (## Block).
- Merge: `git merge-tree --write-tree origin/main a01627177715` exits 0 against origin/main 1602f934 (ev/merge_tree.txt; re-checked at post time, rc 0). No absorb is asked for.
- Cheap figures at this head (ev/cheap_checks.txt), each re-derived:
  - STRUCTURE RATCHET PASSED.
  - `Architecture score: dS +0.0000 NULL`.
  - tmp_paths: 0 refused, 0 stale.
  - throwaway_git: 0 refused, 0 stale.
  - `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and scope.run names tests/entities.py.
  - The rule 3/4 grep finds nothing.
  - `10 files changed, 734 insertions(+), 77 deletions(-)`.
  - No added `git init` or `git clone` line.
  - ci_predict reports no closures and no fast red.
  - policy_lint at this head: `TOTAL: 0 error(s) across 43 policy file(s)`. The orchestrator.md cap red the body predicted was main's, and #2595 at dcf12f49 fixed it. This head merges dcf12f49.
- carry_audit.py `--roster-ref origin/handoff/audit-r10-roster check` over the body: `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit_body.txt). carry_audit.py is identical to origin/main's. R10-UPDATE-PR-SIGNALS is on origin/main's roster at stage `in-progress`, so it is a live destination.
- Figures not re-derived:
  - The body's entities 3.13 run (`1 of 2382`), and the prepr `PRE-PR` line and its FIGURES counts. This container has Python 3.11.
  - The CI `fast (3.14)` run at this head concluded success, which settles entities.
- CI at this head, from the check-runs API at 05:08Z (ev/check_runs_final.json): failure 1, skipped 16, success 32.
  - The one red is `nightly-status`. It grades main, and this diff (tools/ scripts and one delivery row) does not reach what it reads.
  - `pr-contract`, `closures`, `fast (3.14)` and `mutation` concluded success.
- Red checks across the range since 9629ae17 (ev/red_per_commit.txt):
  - a69446c35, dabd93cfc, 7d732e31d, 2c9cc6815, 8cd8c89a2, 174333c88, f1e7b8895 and d8af5fcb6 have no check runs, as the body says.
  - 9629ae17's only red is `nightly-status`, which the body answers.
- The body's `## Head` claims, re-derived (ev/head_chain.txt):
  - The parents of a0162717, d8af5fcb6, f1e7b8895 and 8cd8c89a2 are as stated.
  - Both `git diff --quiet` checks across the round's main merges exit 0.
