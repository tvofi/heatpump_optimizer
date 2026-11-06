Fix review: merge 33a345901352189f67afe91df1db27970b25aa46

bus-nonce: 0d9b4c08d4e20af00e645c58cd6276be

Round 4 of this PR (re-check of the round-3 block `f16841b1`, figures-uncited, which was on the PR body only). The head is unchanged at `33a34590`; the body was rewritten. Every round-3 block item is cleared at this head, so no re-cut is owed.

## Findings
- Residual: the R10-RCA-SAV-ESTIMATE roster carry ends `triage: dev/programme/triage/s6-batch122.md#P387 at 8439f738e`, and `8439f738e` holds the withdrawn text of the ruling (it prints `wood-full` 7.70, not 8.25; ev/review-packet.md has the current text). The carry's own wording matches the ruling. Whoever routes the next roster edit should repoint it to the merged ruling. Carry: R10-RCA-SAV-ESTIMATE
- Residual: the restated R10-HOTFIX-SAV-ESTIMATE carry is now in the roster (`handoff/audit-r10-roster` at `174417fa3`, carry index 1, ev/hotfix-carry.txt), and the round-3 residual about its withdrawn text is settled. It does not end with the `triage:` pointer the ruling gives it. The R10-SAV-METER-FLOOR brief still has no `triage:` pointer either (ev/roster-fields.txt). Both are routing, not this diff. Carry: R10-SAV-METER-FLOOR

## Evidence
- Head reviewed: 33a345901352189f67afe91df1db27970b25aa46 (ev/HEAD.txt). It merges with origin/main `b88684a21`: `git merge-tree --write-tree` rc 0, no conflict (ev/merge-tree.txt). The three-dot diff is 2 files with 99 insertions: delivery row 1, ruling 98 (ev/diffstat.txt). The body says the same. VERSION, the manifest and RELEASE_NOTES are untouched.
- (a) `## Head` names `33a345901352189f67afe91df1db27970b25aa46`. The PR body was read live from the PR (GitHub API, `updated_at` 2026-11-06T03:11:58Z), not from a copy.
- (b) I re-derived every figure in the body myself:
  - Arm table: I re-ran it from a `git archive 750a6001a` export, all eight arms with `--quick` (ev/arms.txt). Booked reference is 72.28 on every arm. Plan kWh are 67.47, 66.51, 66.89, 63.35, 41.76, 40.63, 40.70 and 8.76, so R = 1.07, 1.09, 1.08, 1.14, 1.73, 1.78, 1.78 and 8.25, matching the body and the ruling. The row % values are 29.84, 0.47, 0.34, 6.84, 38.48, 45.71, 42.32 and 89.04, matching the ruling's table. `valve-vary` and `valve-flat` read SOUND. `wood-unforeseen` prints calibration 1.0 and uncalibrated 49.10 %, as the ruling says. Only `wood-full` is above 2.0 and no arm is below 0.5.
  - Wood floor: `git show 750a6001a:.../ledger.py | sed -n 458,466p` shows `if wood_configured and calibration is not None:` ... `calibration = max(1.0, calibration)` (ev/ledger-floor.txt).
  - Roster: `"group": "R10-SAV-METER-FLOOR"` is at `wave-r10-groups.json:17024` at `7cfdd9cc1`, as cited, and at :17029 at the current roster head (ev/roster-grep.txt). Its fields are kind fix, size S, lane C, files ledger/payload/notifier, `after` ⊇ [R10-HOTFIX-SAV-ESTIMATE], resume not-started.
  - RCA at `d8eeae8f8`: line 38 and line 162 read 0.18, line 273 reads 3.30 and 0.18, line 217 reads 6.8 h, and line 270 holds `METER_BAND` 0.5 to (ev/rca-lines.txt).
  - `node tools/policy/brief_lint.mjs` at the head prints 0 error(s), 0 warning(s) on every section (ev/brief_lint.txt).
- SHAs: `750a6001a`, `d8eeae8f8`, `7cfdd9cc1` and `c679f4b69` resolve as commits on origin. `4fff42664`, `39143c38f`, `e1ee044cc` and `77af298ef` do not, and none of the four appears in the body or the ruling (ev/cat-file.txt). The phrase "the figures are the seat's" is gone.
- (c) Red checks. I read all 81 check runs of the head on one page of 100. The only concluded red is `tests / nightly-status` (job 127676643712). I read its log (ev/nightly-status-log.txt): "NIGHTLY FAILED: slow failed 1 night ago", scheduled run 41943946464 at head 499162c. The body quotes this correctly and names it, and the diff (markdown under dev/programme/) reaches nothing nightly-status reads. So it is not this PR's red (fix-review.md 11). The body says "not this diff's" and does not call it inherited, so no comparison with main's head is owed.
- The body's line that `instrument-self-tests` and two `prelude` runs "had not concluded" is stale but harmless. All three have since concluded success: job 127676643584 at 03:11:09, jobs 127679214025 and 127676501118. A `pr-contract` run (127689158112, 03:18) started after the last red concluded (02:43) and is success.
- CI: `merge_train.py classify 33a34590 --pr 3212` prints `GREEN 33a345901352189f67afe91df1db27970b25aa46 pending: none red: none`, rc 0 (ev/classify.txt).
- Hotfix carry (check 3) is restated against the wood floor on main, both in the ruling and in the roster. Check 4: the struck benefit figure (1.1 h, 1 of 3) carries no number in either place.
- No mutation applies: the diff is markdown and writes no production line. The finder's harness is `dev/audit/harnesses/r10_sav_wood_reference.py`, re-run above.
