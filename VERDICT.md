Fix review: blocked 94da32128301b896241a0d38d8c8904b7181b199 carry-missing: not carried to R10-FLOW-AUTOTRAIN

bus-nonce: e76120c1f46eb4ce430ae27671fbf7be

Round 2 of this group's review (the first since the depth-root repair). Measured head: 94da32128301b896241a0d38d8c8904b7181b199, which is still the branch tip at write time.

## Block

- The body's `## Forward-carry` names roster SHA 4937d60fe on `handoff/audit-r10-roster` as the carry to R10-FLOW-AUTOTRAIN. It carries four items: no policy exclusion to lift, `Train.admit_add` as the seam the builder extends, `launch_detached` replacing `launch_train`, and AUTOTRAIN's live-train check reading `queue.open` as well as `train.pid`. Commit 4937d60fe (`roster_edit append-carry R10-FLOW-AUTOTRAIN`) does not append that text. It appends one literal string, an absolute file path on the orchestrator's host. `roster_edit.py append-carry` takes `<text | @file>`, and the path was passed without the `@`, so the path itself became the carry. The text exists only in an untracked scratch copy, at `orch/r10s6/carries/carry-train-upgrade-autotrain.md` on `wip-sync/orchestrator-scratch` (commit 0aaff447a). No seat reads that as the group's brief. The roster tip still holds only the path.
- Without that text, the `queue.open` precondition is not stated anywhere AUTOTRAIN's fixer reads. That precondition is what stops AUTOTRAIN's live-train check from starting a second train beside a closing one. The roster's earlier TRAIN-UPGRADE carry (`train.sh add` into the live train) and the owner's re-scope do not state it. Under fix-review.md step 10 and finding-propagation.md, this is `carry-missing`.
- Repair (orchestrator, roster only; nothing in this PR's code changes): run `roster_edit.py append-carry R10-FLOW-AUTOTRAIN @<that file>` (or pass the text), drop the path entry with `drop-carry`, and amend the body's Roster SHA. The path entry also puts a home path into a tracked policy file and needs dropping regardless. Everything under `## Evidence` stands at this head and carries to a body-only re-cut.

## Findings

- The roster carry for R10-FLOW-AUTOTRAIN at 4937d60fe is a host file path rather than the carry text. The `admit_add` / `launch_detached` / `queue.open` preconditions are therefore unrouted (the Block above). Carry: R10-FLOW-AUTOTRAIN
- The cheaper detector for round 1's `tests / fast (3.14)` red: `prepr.sh` does not run the lease-free static part of `tests/harness_headers.py` (`depth_root_seams`, ~0.7 s). The body records process state (c) and defers the countermeasure to the root-cause seat beside this fix. Carry: R10-TRAIN-UPGRADE
- `roster_edit.py append-carry` accepts a bare absolute path as carry text, with no refusal of a string that is only a path, so the `@` slip passed silently. This is an instrument gap behind the Block, not this PR's defect. Carry: dismissed: orchestrator tooling outside this PR; a root-cause seat decides whether a refusal is worth building once this recurs

## Evidence

- `RESULT mutants: python3 dev/audit/harnesses/r10_train_upgrade_mutants.py` at this head prints `M0 PASS: the unmutated head` and `MUTANTS: 28 run, 0 not as required`, with 27 `KILLED` lines (M1 to M27). It ran in 5 min 28 s and left no `_mutant_*` copies (`ev/mutants.txt`).
- `RESULT merge_train self-test: 283 checks, 0 failed`, rc 0. This includes `ok RACE: two concurrent adds with no train live start exactly ONE train (one launch, one train.pid) and spool exactly the other entry` (`ev/merge_train_selftest.txt`).
- `RESULT train.sh self-test: ok (5 refusals shown, ... add takes no pidfile)`, rc 0 (`ev/train_sh_selftest.txt`).
- Round-2 repair: the harness now defines `repo_root(start)` and sets `ROOT = repo_root(__file__)`. At c8219f601, line 23 was `ROOT = Path(__file__).resolve().parents[3]`. `depth_root_seams()` returns `[]` at this head. `tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED`, rc 0 (`ev/harness_headers.txt`).
- `Train.policy_approve` guard, with my own mutants on a copy of `merge_train.py`, each running `--self-test` (`ev/reviewer_guard_mutants.txt`):
  - R0 null control (all conditions hold, unmutated): 283 checks, 0 failed.
  - R1 `mandate_id` accepts a label with two ids: KILLED, `mandate_id: ... two, or none, are no id`.
  - R2 the in-force refusal removed: KILLED, both `policy post null` arms (out-of-window mandate; scope code-owned).
  - R3 the owner approval at the head ignored: KILLED, `policy post: an owner approval already at the head is not re-posted` and the batch policy post arm.
  - R4 the `*_budgets.json` exclusion removed: KILLED, `policy post null: a budget file beside the policy ...`.
  - The exactly-one, in-force, no-owner-approval and no-budget-file conditions are each pinned.
- Merge: `git merge-tree --write-tree origin/main 94da32128` exits 0 (tree f4a359fb5e80) with no conflict. The merge base is origin/main 5c0ee1093.
- Head: the body names authored head 4a1e41af5 and states that 94da32128 adds only the automatic merge of origin/main 5c0ee1093. `git diff 4a1e41af5 94da32128` touches none of the PR's six files, so the resolution delta is main's content only. The body's figures were taken at 4a1e41af5; mine were taken at 94da32128 and agree: 283 checks, 28 mutant runs, 112 header checks.
- Claim files, `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched in the three-dot diff (`ev/untouched.txt`). The diff is six files: the mutants harness, delivery row 2772, `tests/closures.json`, `INSTRUMENTS.md`, `merge_train.py` and `train.sh` (`ev/diffstat.txt`).
- Red checks: the body names round 1's reds at c8219f601 (`tests / fast (3.14)`, `pr-contract`, `gate`) and answers each, including the root-cause trigger (process state (c), cheaper detector named and costed, countermeasure carried). Answered, per step 11.
- CI at this head (`ev/check_runs.txt`, check-runs API) was not concluded when this verdict was written. `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `governance / instrument-self-tests`, `codeql / Analyze (python)` and one `prelude` were still in progress. No check had concluded red, and every concluded check was success, skipped or neutral. This block does not turn on CI.
- Figures I did not re-derive: the P86 review-run durations (66 to 76 s in runs 40124449022, 40129950489 and 40130190054), the 0.67-s scan timing and the entities count of 2429.
