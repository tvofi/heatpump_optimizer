Fix review: blocked e62be31de2c3d80217d6d855b59f7d27f5392826 merge-conflict: tools/audit/seat/cloud_relay.sh conflicts with origin/main 50808a75 (#2580, R10-FLOW-RELAY-HOLD), one hunk in relay()'s local list; every other item passes at this head

bus-nonce: 2323f58f7847338368024f6c55dff26b

Fourth fix review of PR #2524 (blocks at c071fa5f, 9629ae17, a01627177715 on review/2524). Head measured: e62be31de2c3d80217d6d855b59f7d27f5392826, still the PR head at 18:30Z (ev/HEAD.txt). Contract: dev/governance/roles/fix-review.md from origin/main; `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. Harness: the body's dev/audit/harnesses/r10_pusher_reap_launch_mutants.sh (sha1 5a4a1925, matches the body), the fixer's committed instrument, run by me at each end; the a01627177715 block's own mutants (F-CR-ELSEFG, F-CR-ELSELEAD) are rows in it.

## Block

- merge-conflict: `git merge-tree --write-tree origin/main e62be31de2c3d80217d6d855b59f7d27f5392826` exits 1 against origin/main 50808a755ce300fac4b19b7cfe7f89c795b8387b, which merged #2580 (R10-FLOW-RELAY-HOLD) after this head was cut (ev/merge_tree_final.txt). The conflict is `CONFLICT (content): Merge conflict in tools/audit/seat/cloud_relay.sh`, one hunk at relay()'s `local` line: main adds `held_prs`, this PR adds `upd` (ev/cloud_relay_conflict.txt). No claim file is involved. Against the dispatch base a9db47846 the merge was clean (ev/cheap_checks.txt). The likely resolution is the union (`... nonce urc held_prs upd`), but the merged relay() then runs #2580's hold check beside this PR's single update launch, and its self-test has not been run merged. Repair: merge origin/main, resolve, re-run `cloud_relay.sh --self-test` and the launch-mutant harness's CR rows on the merge. Every other check below passed, so the re-review owes only that resolution delta.

## Findings

- TR-EXEC (train.sh's `exec ` deleted) stays unpinned. The body discloses it: equivalent on bash 5.2, as the a01627177715 review measured, and kept for macOS bash 3.2. Carry: dismissed: equivalent on bash 5.2 (measured last round); no test on a bash that execs anyway can separate the two
- #2502's SIGKILL clause is not met here. The body says so under `## Forward-carry`, writes "Part of #2502" with no closing keyword, and the group roster carry on origin/main and origin/handoff/audit-r10-roster already states it (the #2469 round-4 carry: holder frees the lock within 2 s, drain of the process group, PID 1 reaping late). resume.stage is in-progress. The carry is honest: no arm or body line claims SIGKILL. Carry: R10-UPDATE-PR-SIGNALS
- The roster's self-test isolation ("every self-test runs under a timeout in its own process group, reaped on exit") is not built here. The body routes it under `## Forward-carry`, and the roster carry already holds it. Carry: R10-UPDATE-PR-SIGNALS
- The body's `## Head` holds a stale paragraph naming `5f6a432cc3f9754b4dc1db4401efe3d5ce6cfe57`, which is no object in the repository, beside the line for e62be31de2c3d80217d6d855b59f7d27f5392826. That line says the head "merges the authored code head 2d5d6be11 and then merges origin/main a9db47846"; the head's parents are c3bafaf88 and a9db47846, with 2d5d6be11 reached through c3bafaf88. Carry: dismissed: body prose only; the absorb push that clears the block rewrites `## Head`

## Evidence

- Item 1, the a01627177715 block, is answered. Failing test first:
  - At a01627177715 (ev/fail_first_a01627177.txt): `MUTANT F-CR-ELSEFG: CR rc=0 cloud_relay self-test: 83 checks, 0 failed` and the same for F-CR-ELSELEAD. The block reproduces.
  - At af7eb2d9a, the production-route arm with the split launch unchanged (ev/killed_af7eb2d9a.txt): both mutants give `84 checks, 1 failed`, `FAIL with no stub, the relay runs update_pr.sh beside it as the lead, asynchronously: a TERM ends it in that order`.
  - At this head, cloud_relay.sh:233-235 is one launch line for the stub and the production route (`upd=(bash "$HERE/update_pr.sh"); [ -z "${HPO_RELAY_UPDATE:-}" ] || upd=(...)`, then `PR_REAP_LEAD=$!`). That is the block's own suggested repair. The production-route arm resets marks per arm (stoprelay, line 487), so its `G ` is its own.
- The launch-mutant sweep at this head, every row (ev/launch_mutants_head.txt). Each matches the body's table:
  - M0: CR 84/0, TR ok, PA 93/0, AP 197/0, MT 221/0.
  - CR-FG: rc=1, no summary. CR-FG-BOUND: 84/4. CR-LEADNAME: 84/2. CR-PRODPATH: 84/1, the production-route arm alone. F-CR-ELSEFG: NOT APPLIED. F-CR-ELSELEAD: 84/1.
  - TR-FG, TR-LEAD and TR-RC: refused, with the body's wording. TR-RC pins the a01627177715 finding F-TR-RC.
  - OP-FG1 and UP-FG: rc=124, with the failing arms the body names. OP-FG2, HP-FG and RM-FG: 93/3.
  - AP-FG: 197/2. AP-PUSHFG: 197/16. AP-MINTTRAP: 197/2. MT-KILL: 221/1.
  - OP-FG2 is killed by the static census arms and an unrelated mutants arm, with no behavioural stop arm. The body states exactly that.
- Item 2, merge_train.py. `git grep -nE 'def (ci_state|_state|classify)'` returns `classify` (line 309) and `_state_self_test` alone. The PR's merge_train diff against base a9db47846 (ev/merge_train_diff.txt) adds only `stop_on_signal`, `TOOL_STOP_SECONDS`, the Popen-based `Train._run`, `_stop_self_test` and one `stop_on_signal()` call in main(). It touches no CI-state line, so nothing is duplicated. #2584's arms pass at this head: every `K15 (a)`, `(b)`, `(c)`, `(d)` line is `ok`, and the self-test prints `merge_train self-test: 221 checks, 0 failed` (ev/merge_train_selftest_head.txt).
- The PR's 13 files are byte-identical between code head 2d5d6be11 and this head, except tests/closures.json, whose two added lines are main's (review_strength.py, r10_review_strength_mutants.py). Figures measured at 2d5d6be11 therefore apply here.
- Cheap figures, each re-derived (ev/cheap_checks.txt):
  - Rule 3/4 grep: empty, rc 1.
  - STRUCTURE RATCHET PASSED.
  - `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`
  - `pr_args.sh --pushers HEAD`: 18 ok, none other.
- CI at this head (check-runs API, 41 runs). Every run concluded. The only red is `nightly-status` (119987022027), which the body names and answers as main's scheduled run, outside this diff's reach. `pr-contract` succeeded twice, the later run (120004432273) starting 18:19Z, after nightly-status concluded at 17:45Z. pr-contract runs carry_audit on the body, so I take its success as carry_audit's 0 unrouted, 0 bad; I did not run carry_audit offline. `mutation`, `closures`, `fast (3.14)`, `instrument-self-tests` and `coverage` all succeeded (ev/ci_e62be31de_1st.txt, first read).
- Not re-derived: the full gate run (`ALL 2397 ENTITY CHECKS`, `5 TEST SCRIPT(S) PASSED`), score.py dS, tmp_paths, throwaway_git, policy_lint and ci_predict. I cite CI's green runs for those, as step 11 says.
