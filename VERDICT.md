Fix review: merge 51c662da7907b2ce591e9fe7bba2b12260132fd9

bus-nonce: 25ce2fe45b5c77ca93a10f1d8419afef

Round 1 review, head 51c662da7907b2ce591e9fe7bba2b12260132fd9 measured and still the PR head at read.

## Evidence
- CI at this head: `merge_train.py classify` GREEN rc 0 (pending: none, red: none). The packet digest shows no red check, so no red-check answer is owed (body says none).
- Merge: `git merge-tree --write-tree origin/main <head>` rc 0, no conflict.
- Diff against the merge base: two files, the ruling and this PR's own delivery row. The body's "one file" is the authored code head; the body states the delivery-row commit. VERSION, manifest and RELEASE_NOTES untouched.
- Triage gate re-run (ev/gate.txt): RESULT P419/P420/P422/P423 ACCEPT, P421 DEFER, P424 None. Binding texts of P419-P423 pass `triage_refusal` (P421 refused as DEFER). Null control: file absent refuses "not on the roster branch or origin/main". Mutant: P422 flipped to REJECT is refused.
- Cited code facts re-read at 53273de4d: cloud_dispatch.py:247 renders the re-merge text, fixer.md 93-95 says merge only on conflict/DIRTY, replan.py:390 dispatch_tier, open_driver.py:111 default_class, merge_train.py:3261 drain key, gate.py:303 reruns gate job only, mutant_run.py:65 operators, beat_jobs.py:301 roster_drain. All match.
- `tests/structure.py` STRUCTURE RATCHET PASSED; `closure.py select` prints MODE: SCOPED -- 0 script(s) run (a scoped mode line, not FULL).
- Not re-derived (host-local logs and roster branch figures: 621 marks, 35 mispairs, 11 blocks in 24 h, the 3 h 10 min red at #3252): the file itself states they are host-local. I could not verify them.
- Brief_lint of the roster edits at badbae55a was not re-run here (roster branch edit is the orchestrator's op).
