Fix review: merge 8cda32e8d81bce8d0106f00e9f5d18a67063834a

bus-nonce: 817054e56b0af72c4bd24afe2afa33b6
pending-ci: classify prints "WAIT 8cda32e8d81bce8d0106f00e9f5d18a67063834a pending: gate red: none" (no context names printed); no red; a governance / instrument-self-tests or combi census red here would be main's old red (head lacks main 6cc15e9b), cured by the remerge

Round 2, a delta review of 0c556627..8cda32e8d81bce8d0106f00e9f5d18a67063834a (repair commit cb30b77f plus remerge and a record). Resumed from verdict/3470 at 0c8575925c49.

## Evidence

- Mutants re-run through the full `--self-test` at the head with the round-1 driver, anchors adapted to the repaired lines (ev/mut_driver.py, output ev/mutants.txt). Each is KILLED with a named FAIL: M4 (batch `record_drafts(queue)` -> pass): "P609 a batch records the draft key on a key-less entry before admission"; M7 (`pending.add` -> pass): "P608 an unfinished entry older than a SUCCESS still makes the context pending"; M8 (zero-time filter dropped): "P608 a zero-time completedAt falls back to startedAt"; M9 (startedAt dropped from the stamp tuple): that case and "P608 an entry with only startedAt is ordered by it". Controls M1 (last-listed wins, 3 FAILs) and M5 (read -> pass, KeyError 'draft', as the body says) still die.
- Unplanted head: `merge_train.py --self-test` rc 0, "623 checks, 0 failed", matching the body (ev/selftest-head.txt).
- The delta in production code is one tidy in `rollup_states` (zero-time dropped per field before the `or`); the rest is test cases. The new M4 test drives `_batch` itself with `preflight` stubbed, so it pins the route, not just the unit.
- The body's Head section names the authored code tip cb30b77fbf14333a3f1a358548bb17771a2d8dc8 and its merge head 8cda32e8d81bce8d0106f00e9f5d18a67063834a; its mutation list matches what I measured.
- Merge: `git merge-tree --write-tree origin/main 8cda32e8d81bce8d0106f00e9f5d18a67063834a` rc 0, tree 43dc750f755dd1e9490871397c0c9d65ccf46206 (ev/merge-tree.txt).
- CI: classify rc 3 (WAIT) on repeated runs, "gate red: none" (ev/classify.txt). Owed-reds set in ev/owed-reds.txt (23 names); none is red.
- Round-1 residual (any-red rule) stays carried by R10-TRAIN-RESIDUE-P2 carry 14; unchanged by this delta.
- Not re-derived: prepr.sh rc 0 (heavy, CI's job).
