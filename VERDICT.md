Fix review: blocked 5756617f185bbed71852ed1273c19b1e45787c9d head-moved: measured 5756617f185bbed71852ed1273c19b1e45787c9d, head is 2e77ed3e6aa2f03565bd02274ac847227bc619b5

bus-nonce: a8bfe1057ec1aa34a14f6aae1d415383

Round 3 (cloud reviewer seat). Roster PR, group none: reviewed against the PR body, as the brief says.

## Head
- Measured 5756617f185bbed71852ed1273c19b1e45787c9d from a detached worktree. Roles contract current (`git diff merge-base...origin/main -- dev/governance/roles/` empty; merge base = origin/main 22615537a).
- While the review ran, the PR head moved to 2e77ed3e6 = 5756617f1 + 617ce1316 (`roster_edit append-carry R10-BRIEFS-FOLD`, 15:40:52 +0200), a merge of authored roster content, not a main merge. Under step 12 that is a re-review rather than a carry, and the Tests run on 5756617f1 (39608256723) was cancelled as superseded, so coverage, ci-ratchet, closures, lane-proofs, composed-proof, coverage-ratchet and graders-head-copy never concluded on the measured head. ev/head-moved.txt, ev/head-move-617ce1316.diff.

## What survives for the re-review (all measured at 5756617f1)
RESULT groups main=91 head=108 (+17 new, 0 removed)
RESULT stage=done main=43 code-head=51; stage changes 18
RESULT carries main=201 31e162fd=254 head=256; appended to existing groups 32 over 14 groups; new groups' carries 21 at 31e162fd, 23 at head
RESULT text edits (brief/issues/fixes/findings) on 16 existing groups (my definition: any of those four keys differs)
RESULT delta a6e0530d4->8afd645da: R10-OPENPR-SILENT resume.commit 7ab3030bbfff -> dbea71db7 (on main), stage done -> done; delta 31e162fd->a6e0530d4: R10-CI-LAYOUT-P1 2->3, -P2 1->2
- Finder harness: jq over `dev/programme/rosters/wave-r10-groups.json` at origin/main vs the head (ev/d.jq, ev/d2.jq, ev/counts.txt, ev/body-figures.txt). Main's roster is byte-identical at 03b49e15 and 22615537a, so the body's figures apply to current main as well.
- Body minor: "R10-BRIEFS-FOLD 19 to 20" reads as 18->20 measured from main (two appends, 02e96a915 and 4908d97ea); the sentence may mean only the #2521 one. Not blocking, but it should say 18 to 20. The new head adds a third BRIEFS-FOLD carry, so this line has to be re-stated anyway.
- R10-OPENPR-SILENT "set to its stage": the stage stays `done` and only the commit pin moves; its `next_step` ("PR #2422 is open ... review and merge it") is stale against `done`. This predates the PR and does not block it.
- P1/P2 carry texts (ev/new-carries.txt): both state a precondition and a control. Wired: `selftest_wiring.py --check` at the head reads 37/37/0 rc 0; deleting the `tmp_paths.py --self-test` line in governance.yml gives 37/36/1 rc 1 (control reproduced). The quoted "71 self-testing / 70 wired" is #2529's widened check, which I could not re-derive here.
- merge-tree with origin/main: clean, exit 0 (ev/merge-tree.txt). VERSION, manifest, RELEASE_NOTES and goldens are untouched; no claim files are touched.
- Mutation proof, null control, figures: n/a, as the body says (roster state only).
- Red checks: `nightly-status` is red, and the body answers it. The job restores the base's `tests/nightly_status.py` and reads Actions metadata, and the diff touches neither. pr-contract on the head: success (both runs). ev/check-runs.tsv.
