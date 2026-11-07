Fix review: merge 6f9cfc894303c59552e21bc594cc57f6cf4674c5

bus-nonce: 14eee5df33f779ec0be48407cca8147c

## Evidence
- Head measured: 6f9cfc894303c59552e21bc594cc57f6cf4674c5 (ev/HEAD.txt); it is the dispatched head and the PR head.
- RESULT file identity: against handoff/triage-s12-batch127 (1f2ab016f) the harness, s6-batch127.md and tests/closures.json are byte-identical (blob ids equal); the only tree difference is dev/programme/delivery/3271.md, +1 line, the delivery row. The body's "three files" omits that row; four files are in the diff.
- RESULT carries: 5eff4cbb5, f91d0eb9e (P393 to R10-TRAIN-MERGE-LOOP-2), 517d5a28f (P395 to R10-COMBI-TANK), 649f3ed84 (P398 to R10-POLICY-ROLE-PACK) all exist and are ancestors of origin/handoff/audit-r10-roster; git show of each shows the carry text citing s6-batch127.md#P393/P395/P398 at 5eff4cbb52e9. P394/P397 DEFER and P396 REJECT owe none.
- RESULT triage gate: python3 -I tools/audit/seat/roster_edit.py --self-test: "roster_edit self-test: 242 checks, 0 failed", rc 0. ruling_verdict on the batch file: P393 ACCEPT, P394 DEFER, P395 ACCEPT, P396 REJECT, P397 DEFER, P398 ACCEPT, P399 None.
- RESULT mutation: P393 flipped to DEFER in a copy: triage_refusal refuses the P393 carry ("is not an ACCEPT ruling (DEFER)"); unmutated copy accepts it (null control).
- RESULT version: git diff merge-base...HEAD touches no VERSION, manifest or RELEASE_NOTES.md; delivery row present.
- RESULT merge: git merge-tree --write-tree origin/main HEAD exit 0 (clean tree a8be4c903).
- RESULT CI: merge_train.py classify 6f9cfc894303c59552e21bc594cc57f6cf4674c5 --pr 3271: "GREEN ... pending: none red: none", rc 0. Packet digest green, incl. tests / fast (3.14).
- RESULT harness_headers: 56 of 112 checks fail in this seat (ev/harness_headers_full.txt); all 56 are executed-harness checks of six other harnesses, each rooted in ModuleNotFoundError: No module named 'scipy' (this seat's environment); none concerns r10_triage_p393 or the repo-root/depth-seam checks, which are ok. The body states the same 56. CI's fast (3.14) is green, the authority for 112/112.
- Not verified: the stale arm's figures (1 stale, 21 later, 4 same) need the host-local events log. Run with an empty log (ev/stale_noevents.txt) it prints "verdict refs=648 instances=59 stale=0 later=0 same=4 unknown=55": the 59 instances and 4 same are re-derived, stale/later cannot be. The repair changes only how ROOT is found (verified by the harness_headers depth-seam check and the identical blob), so the arm's logic is unchanged.
- Red checks: the body's ## Red checks names tests / fast (3.14) and the detector tests/harness_headers.py with its cause and countermeasure; no record file changed beyond the harness since the previous head.
- Forward-carry: body says none; the carries were landed on the roster as above.
