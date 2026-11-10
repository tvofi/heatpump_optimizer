Fix review: merge 55dfa880d1cd779356cef493eb59cf73ca7818bc

bus-nonce: 553142a29591e83af3b2f190f26f50c8

## Summary

This is round 2. Round 1 was the blocked verdict at f0b7564596d2725f87090f921e0d3ceb51ceec8b (comment 6758409766). I measured head 55dfa880d1cd779356cef493eb59cf73ca7818bc in a detached worktree and re-read it before returning; it had not moved. The scope is the owner ruling of 2026-11-09: the delta `git diff f0b7564596d2725f87090f921e0d3ceb51ceec8b 55dfa880d1cd779356cef493eb59cf73ca7818bc`, the previous findings, and the live required checks. The delta is one added line, `    from pathlib import Path`, inside the inlined `repo_root` of `dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py`. It does not touch `custom_components/`, so the review is not widened.

The previous block is resolved. The harness's `repo_root` is now byte-identical to the canonical one, `tests/harness_headers.py` passes, and `tests / fast (3.14)` is green at this head. Every check in the head's required set concluded success or skipped. The five null controls the brief names still PARK at both the pre-flight and the real path, and my differential harness finds no world where the pre-flight admits a PR that the real gate refuses.

## Evidence

- Repair, step 1. `diff` between the `def repo_root` through `raise` span of `tools/audit/repo_root.py` and the same span of the harness is empty, `diff-rc=0` (`ev/repo_root_diff.txt`). Local `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` at this head printed `ok   every inlined walk matches the canonical helper and no depth root remains`, then `ALL 112 HARNESS HEADER CHECKS PASSED`, rc 0 (`ev/harness_headers_local.txt`). Round 1 got `1 of 112 ... FAILED` at f0b75645.
- Repair mutant. I deleted the added line in place and ran `harness_headers.inline_scan()`: rc went from 0 to 1. The file was then restored and `git status --porcelain` was empty (`ev/repair_mutant.txt`). The check is not vacuous.
- The receipt round changed no code. `git diff --stat 593a28c96e54a64c3ce25d99dfd4850be6094e4b 55dfa880d1cd779356cef493eb59cf73ca7818bc` is empty: the merge commit's tree equals the authored head's. The parents of 55dfa880 are f0b75645 and 593a28c9, so there is no main merge in this round. The only tree change since f0b75645 is the one harness line (`ev/delta.txt`). I found no `Prepr:` trailer on either new commit. The body's `## Head` names 55dfa880 as merging the authored code head 593a28c9, and that matches the graph. I verified that no code changed by tree comparison, not by a trailer.
- Null controls at this head. Command: `python3 tools/audit/seat/_rev3401_pf.py --self-test`. This is round 1's reviewer harness `ev/reviewer_differential_inject.py`, the reviewer's own and not the finder's, disclosed in `ev/reviewer_harness_README.txt`. I spliced it into a throwaway copy of `queue_pre_flight.py`, then deleted the copy; the tree was clean after (`ev/reviewer_differential.txt`):
  - `SCEN N1 no --mandate: preflight=PARK(policy) real=PARK posted=0`
  - `SCEN N2 revoked mandate: preflight=PARK(policy) real=PARK posted=0`
  - `SCEN N3 mandate scope code-owned: preflight=PARK(policy) real=PARK posted=0`
  - `SCEN N4 expired mandate: preflight=PARK(policy) real=PARK posted=0`
  - `SCEN N5 owner CHANGES_REQUESTED at head: preflight=PARK(policy) real=PARK posted=1`. The `posted=1` is in the real path, which is round 1's pre-existing finding. Its carry is checked below.
  - 18 attack worlds (A1 to A16, P1, P2) agree between the pre-flight and the real path.
  - `ok   REVIEWER: no world where the pre-flight PASSes and the real path parks (0 slips)`, then `queue_pre_flight self-test: 54 checks, 0 failed`, rc 0.
- `python3 tools/audit/seat/queue_pre_flight.py --self-test` at this head printed `queue_pre_flight self-test: 53 checks, 0 failed`, rc 0. That run includes the body's null-control checks, lines 37 to 42 of `ev/pf_selftest.txt`.
- Mutation proof: `python3 dev/audit/harnesses/r10_hotfix_train_policy_mandate_mutants.py` at this head printed `8 mutant(s), 0 not as required`, rc 0. P1 to P7 were KILLED. The tree was clean afterwards, `porcelain:[]` (`ev/mutants.txt`). This matches the body's figure at 593a28c9, and the production code is identical between the two.
- Merge with main: `git merge-tree --write-tree origin/main 55dfa880...` against origin/main 699f4d9e printed `LEDGER-MERGE: resolved tests/closures.json` and tree `641717b8...`, rc 0. The merge is clean (`ev/merge_tree.txt`).
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` are untouched in the three-dot diff. `dev/governance/roles/` has no drift between the merge base and origin/main, so the contract is current (`ev/delta.txt`).
- Previous findings:
  - The block (harness_headers) is resolved, as above.
  - The `ci_predict` follow-up and the two train follow-ups are now in the body's `## Forward-carry` with `Carry: R10-PREPR-RESIDUE` / `R10-TRAIN-RESIDUE`. The packet's carry_audit reports `3 routed, 0 unrouted` and each one `resolved on origin/handoff/audit-r10-roster`. The roster at that ref holds the `[moved: R10-PREPR-RESIDUE]` entries.
  - The `fast` red at f0b75645 is answered under `## Red checks` (cheaper detector `harness_headers.py`, about 188 s), and `pr-contract / pr-contract` is green at this head.
  - The class-rule count now reads 5 lines, which matches round 1's count.
- Owed reds: `merge_train.py owed-reds` at this head (`ev/owed_reds.txt`) lists 23 contexts. On the latest run of each (`ev/ci_latest_runs.tsv`, 111 check runs), every one that ran concluded success, and `tests / ci-ratchet` was skipped. This includes `gate` success (job 129721985443, started 08:40:07Z), `pr-contract / pr-contract` success (129721624350, started 08:39:15Z, after the last required job concluded), `tests / fast (3.14)` success (129707027507), `tests / closures`, `tests / coverage`, `tests / coverage-ratchet` and `tests / mutation` success. Earlier `gate` failures, 129687180717 and 129704030104, printed `FAIL run(s) [...] at this head are still being judged; their gate decides`, which is the early-judging pass and not a red outcome.
- `governance / instrument-self-tests` failed on the first run (129686057277, `FAIL the live job parses (118 steps) and its gating is consistent`, a workflow-level check this diff does not touch). It passed on the re-run (129705081494). It is not in `owed-reds`, so it is not a blocking reason.
- CI classify: `merge_train.py classify 55dfa880... --pr 3401` printed `WAIT` (rc 3) until 08:03:52Z. From 08:05:08Z it printed `REFUSE ci: the check runs at 55dfa880d1cd could not be read`, rc 2 (unreadable), and kept doing so through the final run (`ev/classify.txt`). The cause is this session's proxy, not CI. Once the head passed 100 check runs, the API's `Link` header points page 2 at `repositories/1341087606/...`, and the proxy refuses that with HTTP 403 `Numeric-ID repository paths ... are not supported` (`ev/pagination_link.txt`). I read both pages through `repos/tvofi/heatpump_optimizer/...?page=N` instead (`ev/ci_poll.txt`, which ends `pending_owed=0 red_owed=[]`) and judged the owed set from that. classify's own GREEN is therefore not available as evidence. The train re-reads it on its own host.
- Head: `git ls-remote origin refs/pull/3401/head` returned 55dfa880d1cd779356cef493eb59cf73ca7818bc at return time (`ev/HEAD.txt`).

## Findings

- Follow-up: `merge_train.py classify` (and so the cloud reviewer's CI wait) returns rc 2 unreadable on any head with more than 100 check runs when run behind the cloud agent proxy. `gh api --paginate` follows GitHub's `Link` header to `repositories/<id>/...`, which the proxy refuses with HTTP 403. Reading `repos/<owner>/<repo>/commits/<sha>/check-runs?per_page=100&page=N` explicitly works. Control: classify on a head with more than 100 check runs, behind the proxy, returns GREEN, RED or WAIT, not REFUSE. Carry: R10-TRAIN-RESIDUE

## Friction

- My first CI waiter was stopped at the harness's 30-minute background bound, so I re-armed it. classify then went unreadable for the reason above, and I polled the owed set by hand.
