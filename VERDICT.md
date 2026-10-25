Fix review: merge 6e4e274a4afc889228f867b8ac41edd2adc646c8

bus-nonce: 19e7e009a1766fd36dd58a65d37f4e02

Round: second review of #2762 (delta review after fixer round r2). The first was `Fix review: merge c851f2a8d464bff58730c5351698eba8cffffff1`.
Head measured: 6e4e274a4afc889228f867b8ac41edd2adc646c8. I re-read it on origin after CI concluded (05:13Z) and it had not moved. fix-review.md was read from origin/main, and `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty.

## Findings

- The body's `## Red checks` says the 413 was "hand-carried" by the 2f5bf7257 merge. The cause is in fact the `ledgermerge` driver (`tools/merge/ledger_merge.py`), which runs without anyone touching the file. Re-running `git merge-tree --write-tree origin/main c851f2a8d` reproduces it: `LEDGER-MERGE: resolved tests/structure_budgets.json ... seam_cut_total: 710 + both deltas = 413` (`ev/merge_and_delta.txt`). The driver's base-plus-both-deltas rule for counts has no way to see that #2711 re-recorded seam_cut_total under a new definition, so it applies an old-definition branch delta to a new-definition value. Any branch in flight that recorded a seam_cut_total delta before #2711 will get the same wrong value on its next merge of main. The driver does print "re-run the gate that owns this file before pushing", and `tests/structure.py` catches the result (planted 413 → `FAIL seam_cut_total 420 > 413 (+7)`). So the body's countermeasure, re-running the existing check on the merged tree, is still correct; only its wording of the cause is wrong. Under step 11 I check that the trigger was answered, not the answer, so this does not block. Carry: dismissed: one-off for a definition change. The driver's docstring already says a resolved ledger "is a merge of two measurements, not a measurement" and prints the re-run instruction, and `structure.py` catches it before merge in every case. The two earlier findings from the first review (m6, m7 → #2232) are not settled by this delta and stay carried there.

## Evidence

- Delta since the last reviewed head (`ev/merge_and_delta.txt`). I merged c851f2a8d with origin/main ab00437c9 in a merge-tree (tree 8db08e9de) and diffed that tree against the head's tree 6b564197d. The only difference is `tests/structure_budgets.json`: `seam_cut_total` 413 → 420 and `recorded_at` e463e95e2 → 662a3809c. The head adds no behaviour and no code beyond the stated budget restore. The code was already reviewed at c851f2a8d, and the main merges have no other resolution delta.
- RESULT structure, head (`ev/structure_head.txt`): `seam_cut_total = 420`, `ok seam_cut_total 420 <= 420`, STRUCTURE RATCHET PASSED, rc=0.
- RESULT structure, origin/main ab00437c9, null control (`ev/structure_main.txt`): `seam_cut_total = 420`, PASSED, rc=0. The RESULT lines differ only in class_excess_loc 18202→18103, coordinator_attrs 146→143, coordinator_multiassigned_attrs 114→110 and max_class_loc 8442→8343, all downward. In the seam table only the attrs column moves (learning 37→36, grid 27→24). xattr, xmeth and cut are equal per seam, which matches the body.
- Mutation proof for the restore (step 1/14): I planted the original 413 at the head and `structure.py` printed `FAIL seam_cut_total 420 > 413 (+7)`, rc=1 (`ev/structure_head_planted413.txt`). Restoring the file left `git status` clean. The 420 is main's own measurement and the branch's too, so it is earned by neither change.
- No raise: the three-dot diff of `tests/structure_budgets.json` against the merge base does not touch `seam_cut_total`, and every key it moves goes down. No Raise justification is owed. `budget-raise-gate` passed on this head, twice.
- Figure note: the body's budget figures (18209→18110, 8449→8350) are taken against base 662a3809c, as its `## Head` section states. Against the current base ab00437c9 they read 18202→18103 and 8442→8343. The deltas are the same (−99 each).
- RESULT architecture score (the finder's ARCH2-s2 instrument, per the first review): `score.py --diff ab00437c9 6e4e274a4` gives `dS +0.0611 IMPROVES`; null control `--diff ab00437c9 ab00437c9` gives `dS +0.0000 NULL` (`ev/archscore.txt`). This matches the body and the first review.
- RESULT features: `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/features.py` at the head printed ALL 4374 FEATURE CHECKS PASSED, rc=0 (`ev/features_head.txt`).
- Steps 4/5: the three-dot diff touches none of `VERSION`, the manifest, `RELEASE_NOTES.md` or `tests/golden/` (claim files included) (`ev/version_golden_diff.txt`, empty).
- Step 11 (`ev/checkruns.json`): every check on this head concluded success or skipped, including `tests / fast (3.14)` (121074124483), `gate` ×2, `tests / mutation`, `budget-raise-gate`, `arch-score` and codeql. `pr-contract` 121083039211 (05:11:44Z) succeeded, which settles the body. The earlier reds at 2f5bf7257 (`tests / fast (3.14)`, `gate`, `pr-contract`) are each named and answered in the body's `## Red checks`, with a cheaper detector named: `structure.py` on the merged tree.
- Step 13: `git merge-tree --write-tree origin/main 6e4e274a4` gives rc=0 against ab00437c9 (tree equals the head tree). After main moved to 1afbbceae, rc=0 again (tree 52099a4f3). No claim-file driver ran.
- Step 10: Forward-carry is "none", which is right for a budget restore. The Friction carry routes to R10-POLICY-FIXER-MD, as in the first review.
- Step 7: the body's `## Head` names 6e4e274a4afc889228f867b8ac41edd2adc646c8.
- I did not re-derive the body's local scoped-gate run or its `ci_predict.py` line. CI's own runs on this head stand in for them, as the role requires.

## UNCERTAINTIES

- I re-derived the archscore figure but did not re-run the finder's ARCH2-s2 harness files themselves (they are off main, on handoff/audit-r10-arch2-s2). The first review established that the archscore diff is the re-derivation they prescribe.
