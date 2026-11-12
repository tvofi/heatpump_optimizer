Fix review: merge 05158ac25eba0015cc0eb365592a11711f9b249e

bus-nonce: 13c2753779072ff27e53850f3ab2f174

## Prior verdict answered

The only verdict at this head was `blocked ... body-not-applied`: the live PR body still dismissed carry 16 whole. The body now on PR #3492 (updated 06:31:54Z) splits it. Part (1), judge every loop, stays open with `Carry: R10-STANDING-CONTRACTS-P2 | dismissed: not this part, its own part of the group answers it`. Part (2), hooks, is dismissed as implemented at f0c6bbfd7. Its `## Red checks` now answers `tests / nightly-status`. The live body equals BODY.md at handoff-body 6b5bdd4d plus one head note (ev/body_vs_BODYmd.diff). On the roster (handoff/audit-r10-roster c90f0634), carry[16] is unmarked, so part (1) really is open there. A `pr-contract / pr-contract` run started at 06:33:07Z, after the body update, and passed. Round: this is the third verdict at this group's code (e199f727 blocked, 05158ac blocked for the body only, this one), so no re-cut is owed.

## Findings

- Survivor: the self-test pins only step (3). Restoring merge-base text for step (2), (4) or (6) on its own still leaves `sweep_render.py --self-test` at 37 checks, 0 failed (ev/mutant_steps_2_4_6.txt). The carry's control names a single mutant (step 3), and that mutant is killed. Carry: dismissed: the carry's control names one mutant; optional hardening at the fixer's discretion

## Evidence

- Head reviewed: 05158ac25eba0015cc0eb365592a11711f9b249e (ev/HEAD.txt), and it is still refs/pull/3492/head at posting. Diff: 3 files, sweep_render.py, sweep_template.md and delivery/3492.md (ev/diff_stat.txt). VERSION, the manifest, RELEASE_NOTES and both claim files are untouched.
- Role contract read from main 14f227c5 (fix-review.md has drifted since the merge base; main's text applied).
- RESULT self-test at head: `sweep_render self-test: 37 checks, 0 failed`, rc 0 (ev/selftest_head.txt). This matches the body's null control.
- RESULT mutation proof (step 3 restored to a `merge_train.py sweep` launch): 35 checks, 2 failed, rc 1. Both new checks fail (ev/mutant_step3_launch.txt). With the whole template reverted to merge base, the same 2 checks fail (ev/mutant_template_at_base.txt).
- The removed `orch_scratch` placeholder has no remaining reference in the tree at head (ev/claims_check.txt).
- Carry dismissals checked at head. f0c6bbfd7, 0a98a0173, 1b174e9b3 and b16084794 are ancestors of origin/main. The hook files and hooks_setup.py with its instrument doc exist. standing.md L47-50 names `$HPO_STATE_DIR/alive/`. beatd.jobs.json carries tick-digest, roster-drain, plan-beat, pulse, cancel-sweep, disk and opener (ev/claims_check.txt). Roster carries 15-19 are unmarked at c90f0634 (ev/roster_carry16.txt, read by a scout subagent).
- Merge with main: `git merge-tree --write-tree origin/main <head>` exits 0 (ev/merge_tree.txt).
- CI: `merge_train.py classify ... --pr 3492` printed `GREEN 05158ac25eba0015cc0eb365592a11711f9b249e pending: none red: none`, rc 0 (ev/classify.txt). The only red at head is `tests / nightly-status`. It is not in the `owed-reds` set (ev/owed_reds.txt), so it is owed no answer and blocks nothing. The body answers it anyway.
- Figures: the body quotes none; figure_lint 0/0/0. The body's `## Head` section holds a leftover line naming e199f727 under the stated head 05158ac. The stated head is the one measured, and pr-contract passed.
- Finder's harness: none named. The carry's harness is the self-test's own null control, rebuilt here as above.
