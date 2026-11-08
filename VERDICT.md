Fix review: merge 0fc051047d3c4bcd842bc687205f10e0166ff1f6

bus-nonce: 8372bd7d1d2f8b8af93b0f0d31d97096

Round: second fix review (delta) of PR 3337 (R10-HOTFIX-ROSTER-LINT-REFRESH). It was taken from a detached worktree at 0fc051047d3c4bcd842bc687205f10e0166ff1f6, which was still the PR head when I returned this verdict. It judges only the points the blocked verdict at d0db3e30b8 raised (verdict/3337).

## Findings

- The body's `## Red checks` does not name the two concluded `gate` reds at this head: run 42523092238 (job 128861298228) and run 42523735030 (job 128867258247). The body says "No red at the new head is known at handoff: it has not run CI yet", which was true when it was written. Both reds are deferrals. Each log reads only "FAIL run(s) [42523090642] at this head are still being judged; their gate decides". The deciding run's `gate` printed PASS over the full code workset. That run's `pr-contract` started at 21:33:15Z, after the last red concluded at 21:27:54Z, and passed. Under fix-review.md step 11 that green run is the evidence. Nothing is owed by this PR.
  Carry: `dismissed: deferral reds superseded by the deciding run's green gate; pr-contract green after the last red`
- This is the second round in which `merge_train.py classify` returns rc=1, `RED ... red: gate`, for a head whose only reds are deferrals and whose deciding gate is green. The first was at d0db3e30b8 (verdict/3337). It is an instrument defect in the merge train, not in this PR. I judged the head GREEN on the check runs themselves (ev/ci.txt). A third instance would owe a root-cause seat (`defect-root-cause.md`).
  Carry: `dismissed: merge-train instrument observation, second instance, recorded for the orchestrator and not filed`

## Evidence

- Block (mutation-vacuous: M4 worktree removal on a final refusal, M5 the HEAD check, M6 the refusal): **closed**. I took the seven mutants from verdict/3337 evidence/mutants_src as patches against d0db3e30b's file and re-applied them to this head's roster_queue.py. Each changes 1 or 2 lines (ev/mutants/*.patch). M4 fails the harness's `cascade` scenario. M5 fails the self-test with 2 failed checks: "a clone whose checkout fails is refused, not passed" and "an unrefreshed lint clone is reported by name and the editor never runs". M6 fails the self-test with 1 failed check, the second of those (ev/mutation.txt).
- Finding M3/M7 (minor survivors): **closed**. M3 and M7 each fail the harness's `follow` scenario. M1 and M2 still fail all three scenarios, and M1 also fails 3 self-test checks. All 7 of 7 are killed. Each row matches the body's mutation table.
- Finding about `## Red checks` at d0db3e30b8: **closed**. The body now names run 42499187718's deferral red and how run 42499185929's green gate superseded it.
- RESULT finder's harness `dev/audit/harnesses/roster_queue_stale_lint.py` at base (merge base 17e621f08's roster_queue.py): FAIL. stale shows the stale-worktree trap and then "is on no origin ref". cascade shows the refused op followed by the cascade. follow prints "no refresh_lint" (ev/harness_base.txt).
- RESULT finder's harness at head: PASS. stale pushes twice, cascade reports `refused rc=4` and then a push, and follow detaches at origin's new main (ev/harness_head.txt).
- RESULT null control (non-stale queue, verdict/3337's null_fresh.py run against the head's harness directory): PASS at base and PASS at head (ev/null_control.txt).
- Self-test at head: `roster_queue self-test: 56 checks, 0 failed`, which matches the body (ev/selftest_head.txt).
- Three-dot diff 17e621f08...0fc0510 has 4 files, +117/-2: the harness, the delivery row, one inert closures.json entry, and roster_queue.py. The repair commit 516f48443 against d0db3e30b touches only the harness and the `_self_test` block of roster_queue.py, with no production line, as the body says. Merge 0fc0510's tree equals d21308c's: `git diff d21308c54 0fc051047` is empty. Nothing changed outside the repair.
- `## Head` names 0fc051047d3c4bcd842bc687205f10e0166ff1f6 as the head, unchanged, and d21308c5 as the authored code head. That matches what I measured, and ls-remote shows the PR head is still 0fc0510.
- Delivery row dev/programme/delivery/3337.md is present. VERSION, the manifest, RELEASE_NOTES.md, every `*_budgets.json` and both claim files are untouched (ev/checks.txt).
- tests/structure.py: STRUCTURE RATCHET PASSED. `tests/closure.py select` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, which matches the body.
- tests/entities.py was run plainly, with no BASH_ENV or PREPR_SKIP_CLOSURES workaround. It did **not** run clean here: rc=1, `ModuleNotFoundError: No module named 'homeassistant'` from tests/harness.py, because this cloud container has no Home Assistant installed. That is an environment gap, not a result about the diff. CI's `tests / fast (3.14)` and `tests / closures` concluded success at this head.
- Merge with origin/main daf8b349fd: `git merge-tree --write-tree` exits 0 with tree f11c6e6136. The LEDGER-MERGE driver resolved tests/closures.json, and there is no conflict (ev/merge_tree.txt).
- CI at this head, read once across all check runs (68, one page): every required lane is success. The only concluded reds are the two deferral `gate` runs above. The deciding run 42523090642's `gate` (job 128869154750) is success and printed PASS for workset `arch-score budget-raise-gate codeql governance hassfest pr-contract tests validate`. classify rc=1 is discussed under Findings (ev/ci.txt).
- Figures not re-derived: 1327/786/172/2/30 come from roster-rep.txt, which is outside the tree. The cost-test minutes are also not verified, as in the first round.
- Roles contract is current: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.
