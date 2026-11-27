Fix review: merge f19754c88fa47f61acb5c4db2e5ae60e1db40983
bus-nonce: ebbce85ec169131a1a0feca3179e40ca

Round: 2 (delta review from the reviewed head aeb563a713aa0b9d3587604c51dc7fb64397ec6a, verdict 007cfa62). review_carry.py prints FRESH-REVIEW because d60a2319 changed the branch's own diff. The delta is five one-line call-site edits under dev/audit/rounds/round11/ and the structure_budgets.json rows re-based by the main merge. The delta touches no custom_components/ line, so the review does not widen.

Prior findings:
1. harness-broken: resolved. m5_sysid.py, m2_sysid_plant.py and probe_46021727.py each give rc 0 at the merge base e8485652 and at the head, and their RESULT lines are identical once load1, swapins, wall and thread are excluded (ev/harnesses_base_head.txt). At aeb563a7 the same three exited 1 with a TypeError (007cfa62's evidence), which serves as the null control.
2. harness-drift note: resolved. fl183_nonfinite.py and probe_3885e472.py now call observe_temps with one argument. Both give rc 0 with identical RESULT lines at base and head.

Verified: a search of the head tree finds no remaining caller that uses a removed signature. The only hits are the archscore perturb scripts, which edit the pinned tree. tests/structure.py exits 0 at the head. git merge-tree --write-tree origin/main HEAD exits 0, and LEDGER-MERGE resolved tests/closures.json. VERSION, the manifest and the release notes are untouched. The role contracts have not changed since the merge base. Live checks: every check is success or skipped except tests / nightly-status, which is not in the owed set and which the body answers.
Note: delta-only round. Mutation proof, figures and CI's heavy runs are taken from the body and CI. The production diff is byte-identical to the one reviewed at aeb563a7.
RESULT prior_findings_resolved=2 count
RESULT harnesses_rc0_both_ends=5 count
