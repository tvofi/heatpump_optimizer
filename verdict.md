Fix review: merge 8c45afd38f2378350bd2e532b68da28e7f682f0e

bus-nonce: 03ea31f2c4341f147b76c35c8093f9ba

Round: fourth review (repair round 3, a merge repair). Scope is the delta over the merge-verdicted head 82e14f6d8fb87fc65dd993d1cadbd35883090f07, which is the hand resolution in merge 8c45afd38f2378350bd2e532b68da28e7f682f0e of origin/main d72963a719438f2dcf370de92a71f6630804ff2e. Measured head: 8c45afd38f2378350bd2e532b68da28e7f682f0e, reviewed from a detached worktree at that SHA. `fixer.md` owes a re-cut from the fourth round. This round is a merge repair that changes none of the PR's own lines (see below), so I do not count it as a fourth fix round. The orchestrator decides whether that holds.

## Findings

none

## Evidence

- Delta scope. `tools/audit/seat/review_carry.py 82e14f6d… 8c45afd3…` printed `FRESH-REVIEW` (why: `not the automatic merge of its parents`) (`ev/review_carry.txt`), so I reviewed the delta. `git show --remerge-diff 8c45afd3` (`ev/remerge_diff.txt`) shows the hand resolution touches only two files: `tests/card_browser.mjs` and `tests/golden/card_claimed_drift.txt`. No production file (`custom_components/`) was hand-resolved, so the delta does not widen (fix-review step 12).
- The PR's patch is unchanged by the merge. Two comparisons were byte-identical, diff rc 0:
  - The sorted `--stat` of `git diff ceb3070…(old merge base) 82e14f6d` against that of `git diff d72963a7 8c45afd3` (`ev/patch_stat_compare.txt`, empty).
  - The `-U0` added and removed lines of the same two diffs (`ev/patch_lines_compare.txt`, empty).
  
  So the PR changes exactly the same lines over the new main as it did over the old base. Every finding and mutant settled at 82e14f6d/bbad7959 stands on the same code.
- `tests/card_browser.mjs` resolution. I extracted each function from the files:
  - `cardCollapse` at the head is identical to the branch's (82e14f6d).
  - `blockerHide` is identical to main's (d72963a7).
  - Both are called from the runner (lines 3182 and 3186).
  
  `node tests/card_browser.mjs` at the head printed `ALL BROWSER CHECKS PASSED`, rc 0, with 106 `ok` lines (`ev/card_browser.txt`). These include the ten `collapse (light|dark)` checks and main's two `R10 every text-bearing element … keeps a layout box` checks (the null control and the `##.adv-text ##.adv-label` injection). So both sides' cells run and pass in the merged file.
- `tests/golden/card_claimed_drift.txt` resolution. `diff origin/main:… head:…` shows 53 lines added and 0 removed: main's file verbatim (`claims-for: 7.1.11`, which matches `VERSION` 7.1.11 at the head) plus this branch's R10-CARD-COLLAPSE block, unchanged (44 claim lines).
  - `node tests/card_drift.mjs` (after `tests/plan_view.py`, rc 0) printed `card_drift: origin/main = 289c9b996832, tree = 8c45afd38f23, 45 states`, `44 state(s) moved and claimed, 1 identical`, rc 0 (`ev/card_drift.tail.txt`, tail of a 17 MB log).
  - Null control: I deleted the branch's block from the merged file and re-ran. It printed `card_drift: 45 problem(s)` with rc 1 (`ev/ctl_drop_branch_block.tail.txt`), so main's inherited R10-HOTFIX lines excuse nothing for this diff. The file was restored and the worktree is clean (`git checkout`).
  - `python3 tests/env_drift.py --claims-only origin/main` printed `claims hygiene: origin/main ok`, rc 0 (`ev/env_drift_claims.txt`).
- Merge with main. `git merge-tree --write-tree origin/main 8c45afd3` against origin/main 289c9b996832e50da330335deb3432836759ad2c (which has moved past the body's d72963a7) exits rc 0 with tree 35ffb65c6c3a5ac2902ecde1fefe5a6d0cfd5b40 and no `MERGE-CLAIM` line (`ev/merge_tree.txt`). There is no conflict.
- Body figures I re-derived at the head against merge base d72963a7, with `PYTHONPATH=tests/hastub GOLDEN_MODE=drift`:
  - `node tests/card.mjs`: `ALL CARD CHECKS PASSED`, rc 0 (`ev/card_head.txt`).
  - `tests/closure.py select --diff d72963a7…`: `MODE: SCOPED -- 12 script(s) run, 21 scoped out.`, rc 0 (`ev/closure_select.txt`).
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`, rc 0 (`ev/structure.txt`).
  - `archscore/score.py --diff d72963a7…`: `Architecture score: dS +0.0000 NULL`, rc 0 (`ev/archscore.txt`).
  - VERSION, RELEASE_NOTES.md and manifest are untouched in the three-dot diff (`ev/version_untouched.txt`).
  - `tests/features.py`: `ALL 5294 FEATURE CHECKS PASSED`, rc 0, the same in two independent runs (`ev/features_head.txt`, `ev/features_head2.txt`). At this base main's combi census red (#3466) is gone, as the body states.
- Figures I did not re-derive: the body's `closure.py selftest` (`ALL 118 closure shrink pins PASSED`) and `tests/layout.py` rc 0 lines. I also did not re-run each remaining script in `scope.run` individually. CI's gate runs those once the PR head moves here.
- Mutation proof. The PR's patch lines are identical to those at 82e14f6d (above), and the previous verdict re-ran NULL/R1/M4/M2 there (killed as the body states; probe/revt-r10-card-collapse-c031750f@f7bc92519c7a2311dad6ab21d3967f70cd6ba843). The card file is not in the resolution, so I did not re-run them.
- CI. No pull request head is at this SHA yet, so there is no review packet and no CI to wait on before the PR opens. Every check, `pr-contract` included, runs then, and the train re-proves it. `merge_train.py owed-reds` prints `tests / typing`, `validate / validate-hacs` (`ev/owed_reds.txt`). No run exists, so no red is owed an answer at this head.
- Body: `## Head` names 8c45afd38f2378350bd2e532b68da28e7f682f0e, the head I measured (`ev/BODY.md`). Its `## Repair round 3` account of both resolutions matches the read-backs above.
- Role contracts are unchanged between the head's merge base and origin/main (`git diff …...origin/main -- dev/governance/roles/` empty).
