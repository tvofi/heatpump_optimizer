Fix review: merge 802b38503eb5de20e87c278ba7923508a50c0f1f

bus-nonce: ac5fc7de21c9800a844568dec61b4152

This is the sixth verdict posted on PR #2559; the brief calls it round 5. It is the roster PR with group none, so I reviewed it against the PR body as the brief says. I measured from a detached worktree at 802b38503eb5de20e87c278ba7923508a50c0f1f (ev/HEAD.txt). The live head was unchanged when I posted (ev/head-at-post.txt), and origin/main is still 5d433771a. The roles contract is current: `git diff merge-base...origin/main -- dev/governance/roles/` is empty. The previous round blocked on body-stale; the body has since been re-taken at code head 2c76c3128, and the head roster is byte-identical to the one at 2c76c3128.

## Harness
The brief names the finder harness: jq over dev/programme/rosters/wave-r10-groups.json at origin/main and at the head. Stage means `.resume.stage`. No script for it is committed, so the jq invocation in ev/roster-measure.txt is mine, and I disclose it as mine (step 9).

RESULT main(5d433771) groups=91 done=43 carries=201
RESULT head(802b3850) groups=108 done=52 carries=257
RESULT new groups 17 (none removed); their stages and names match the body exactly; they hold 23 carries
RESULT stage changes on existing groups 19: 9 to done (including R10-MERGE-PR-MANDATE in-progress->done), 8 to in-progress, 2 done->in-progress. Each list matches the body, and 43+2+9-2=52
RESULT carries appended to existing groups: 33 over 14 groups, and each per-group pair matches the body (R10-CI-LAYOUT 14->27, BRIEFS-FOLD 18->21, POLICY-LINT-FAMILY 3->5, REPLAY-LANE 3->5, ROSTER-OPS 3->6, REGISTRY-LEAK 1->3, and 8 groups +1). 33+23=56=257-201
RESULT no existing carry is rewritten: every head group's carry list keeps main's list as a prefix
RESULT text edits (brief/issues/fixes/findings) on 16 groups; resume edits at an unchanged stage on 12 groups, including R10-OPENPR-SILENT and R10-REGISTRY-LEAK. Both counts match the body.

## Other checks
- R10-MERGE-PR-MANDATE set to done is earned. Its resume.commit 22615537a is the merge of #2555 and is an ancestor of origin/main. That move carries no new carries.
- The new BRIEFS-FOLD carry from #2521 is correct. tests/README.md:272 cites tools/audit/harnesses/k1725_blas_kernel_gap.py, which does not exist, and dev/audit/harnesses/k1725_blas_kernel_gap.py does (ev/carries-detail.txt).
- carry-201.json: one carry is added (the nightly-ha py-spy positive control, from #2479), and the stage text names it. This matches the body.
- Step 1 mutation proof, steps 2–3 null control and step 6 class: n/a. The diff is roster and record state only, in 4 files under dev/programme/ (ev/diffstat.txt), and the body names no enumeration rule. I found nothing that needed one.
- Steps 4–5: VERSION, the manifest, RELEASE_NOTES.md and both claim files are untouched.
- Step 10 forward-carry: the body says none, which holds for a roster PR.
- Step 11: every check run on the head has concluded (ev/check-runs.tsv). The only red is `nightly-status`, which grades main's nightly run; this diff does not reach what it reads, and the body answers it. pr-contract passed 4 times, the last run starting at 14:32Z, after the body edit at 14:23Z. closures and composed-proof passed, and CodeQL is neutral.
- Step 13: `git merge-tree --write-tree origin/main 802b3850` exits 0 with tree 68b7a57d and no conflict (ev/merge-tree.txt).
- Step 14: no budget, closure, golden or score file moves.

## Notes (none blocks the merge)
- The Head section repeats its first paragraph verbatim. This is cosmetic.
- R10-MERGE-PR-MANDATE's resume.note and next_step still say "has no pull request. Owed: recarry and open" beside stage done, because set-stage did not refresh them. This is roster hygiene for R10-ROSTER-OPS.
- The round-4 note still applies: the BRIEFS-FOLD carry taken from #2563 cites its harness at a path that exists in no tree. Carry: R10-BRIEFS-FOLD.
