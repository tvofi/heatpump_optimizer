Fix review: blocked 802b38503eb5de20e87c278ba7923508a50c0f1f body-stale: the body enumerates the diff at code head 31e162fd and calls it the authored code head, but this head carries 2c76c312; at the head done=52 (body 51), carries=257 (body 254), and R10-MERGE-PR-MANDATE to done plus 3 carries are undescribed

Round 5 review of PR #2559 (roster PR, group none: no group entry matched, so reviewed against the PR body as the brief directs), from a detached worktree at 802b38503eb5de20e87c278ba7923508a50c0f1f. Live PR head when finished: 802b38503 (unchanged). Role file current (`git diff merge-base...origin/main -- dev/governance/roles/` empty).

Harness: the brief's finder harness, jq over dev/programme/rosters/wave-r10-groups.json at two ends; no committed script exists, so I built `ev/harness.sh` myself from that description and disclose it as mine (stage is `.resume.stage`).

RESULT origin/main(5d433771) groups=91 done=43 carries=201
RESULT head(802b3850) groups=108 done=52 carries=257
RESULT 03b49e15 vs 31e162fd (the body's own ends): groups 91->108, done 43->51, carries 201->254, new groups 17, stage changes on existing groups 18, carries appended 32 over 14 groups + 21 on new groups, text-edited 16 -- every body figure re-derives at the body's ends
RESULT origin/main vs head: stage changes 19, appended 33 over 14 groups + 23 on new groups, text-edited 16, carries removed 0
RESULT 31e162fd vs head: R10-MERGE-PR-MANDATE in-progress->done (commit -> 22615537 = #2555 merge on main, earned); R10-BRIEFS-FOLD 20->21; R10-CI-LAYOUT-P1 2->3; R10-CI-LAYOUT-P2 1->2; R10-OPENPR-SILENT resume.commit 7ab3030b->dbea71db only (stage already done on main, no stage change)
RESULT roster at 03b49e15 == roster at origin/main 5d433771 (byte-identical), so the base moved nothing

Why blocked (steps 7-8): the body's "## Head" names 802b3850 merging code head 2c76c312, yet the next paragraph says "The authored code head is 31e162fd" and the whole enumeration (done 43 to 51, carries 201 to 254, 18 stage changes, 32+21 carries) is measured there. None of those figures holds at the head under review, and the head's MERGE-PR-MANDATE done, the BRIEFS-FOLD 617ce131 carry and both CI-LAYOUT P1/P2 carries appear nowhere in the body. Also "R10-BRIEFS-FOLD 19 to 20": it is 18 at 03b49e15 and origin/main, 20 at 31e162fd, 21 at head. Remedy is a body edit only: re-enumerate at 2c76c312/802b3850 (done 43->52, carries 201->257, 19 stage changes, 33+23 carries) and correct the BRIEFS-FOLD range; the tree itself I found sound.

Tree checks, all pass:
- Step 1 mutation proof: n/a, no production or test code (4 files, all dev/programme/).
- Step 4/5: VERSION, manifest, RELEASE_NOTES.md, tests/golden/ untouched (0 diff lines); no claim file touched.
- New file critical-path.json is under the `dev/programme/` INERT prefix of tests/closure.py (line 273); all three JSON files parse. tests/entities.py could not run locally (no homeassistant in this container); CI's closure-scope is green, `fast (3.14)` still running at review time.
- Step 10 carries: 617ce131's BRIEFS-FOLD carry states its control as a precondition (converged heat-loss level, genuine gain; gains.converged.rel_dev > 0.05 with gains.unconverged.rel_dev 0.0000, head 1.9800), as the brief says. CI-LAYOUT-P1/-P2 carries state control "deleting any wired line turns the check rc 1". Their figures (71/70/1, rc 1, 1.9800) are quoted from #2529/#2563 and I did not re-derive them (step 8).
- Noted, not blocking: R10-MERGE-PR-MANDATE's resume.note still says "has no pull request. Owed: recarry and open" beside stage done; set-stage did not refresh it.
- Step 13: `git merge-tree --write-tree origin/main 802b3850` rc 0, tree 68b7a57d, no conflict.
- Step 11: only red check is nightly-status, which grades main; the diff does not reach what it reads. Body "Red checks: none" stands. coverage and fast (3.14) were in progress when read.
- Step 6 class: roster state, one seam; no enumeration rule is named, and none is owed.

bus-nonce: 3b1255fa5a49d4c6524da1bfde40756b
