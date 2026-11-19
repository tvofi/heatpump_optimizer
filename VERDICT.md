Fix review: merge 5e10f99bc84d7ecef0d5dbdc4e3451ed27cc2c4c
bus-nonce: 77f3aa5f33b016d1280d625ab04016ef

Round: 1 (replacement reviewer for the stalled one; no earlier verdict on verdict/3801).
Scope: data-file record, tools/ci/selftest_closures.json +4 and the delivery row. No custom_components/, no VERSION/manifest/notes, no claim files, no budgets.

RESULT harness (finder's: selftest_scope.drift over red main push run 44408012370's selftest-closures artifact, the CI step "Refuse a self-test read set the committed table misses"): base table at main 1723f9fd (byte-identical at ed7025dc) 4 UNDER-SCOPED, exactly the four CI printed; head table 0.
RESULT perturbation: each of the four added items dropped alone brings back 1 UNDER-SCOPED; the harness moves under its own perturbation.
RESULT null control re-run: matches the body (4 -> 0, no STALE/UNMEASURED/EXTRA); static 127 gated / 0 problems; --self-test 118 checks / 0 failed.
RESULT class: every one of the 39 survivor_triage/* directories at head and at main is in the dirs of the three dirs-steps and its .gitattributes in temp-or-machine-path's probes; no other directory of the class is missing. Lists stay sorted; no line removed.
RESULT mutation proof: n/a, no production line; the perturbation above stands in for it (data file).
RESULT checks: classify --pr GREEN (pending none, red none); head check runs all success/skipped/neutral, gate success. The earlier gate red ("still being judged") was a pending-run wait, now concluded green.
RESULT merge: git merge-tree --write-tree origin/main(ed7025dc) head exits 0.
RESULT head: PR body names 5e10f99bc84d7ecef0d5dbdc4e3451ed27cc2c4c, the head measured.
RESULT carry: the body's Carry: R11-RCA-SELFTEST-TABLE-DRIFT names #3684, merged; its section 7 recommends C5 (P-R11-41) with C6 as interim, which this record is consistent with.
RESULT harness provenance: the packet names no finder's harness; the one used is the committed CI drift check (tools/ci/selftest_scope.py drift(), the step that went red on main) fed the red run's own artifact. The four-line wrapper evidence/harness.py is the reviewer's, disclosed here; it adds no logic beyond loading the two files.
