Fix review: merge 00d07210bd41a89c38f477f60490b3be091d4f72
bus-nonce: 50386d57bb47156502b6b1bb38871acb

Round 1, full scope (first round). Merge base fe6f06c337. Role contracts unchanged on main since that base.

RESULT step1 mutation: the fix is data, so the mutant is the base table. `selftest_scope.drift` against main's measurement (the selftest-closures artifact from run 44451107719, byte-identical to the head table) gives 5 refusals on the base table, the same five UNDER-SCOPED steps the body names, and 0 at the head (127 gated steps both times). Not vacuous.
RESULT step2/9 harness: no finder harness. The finder is the CI drift step, and it is green at the head: governance / instrument-self-tests succeeded in job 135360674833. My replay, which I built, is in evidence/drift-replay.txt.
RESULT step3 null: `select --change M:docs/x.md` at the head prints MODE: SCOPED -- 22 step(s) run, so the table is not stale.
RESULT step4 claims: no claim file or fixture is touched.
RESULT step5 version: VERSION, the manifest and RELEASE_NOTES.md are untouched.
RESULT step6 class: `git ls-tree -r -d` finds no directory new on origin/main (8ab5dc566f) since the merge base, so no further miss is pending at merge. P-R11-87 already covers the general class (a new data directory reddens drift); it is out-of-tree and rides round-end triage.
RESULT step8 figures: the body's 5 to 0 refusals and 127 gated steps re-derive exactly.
RESULT step11 reds: gate 135369725903 fails with "run(s) [44464951527] at this head are still being judged". That is a wait, not a code red. env-matrix was cancelled, not failed, and the body answers that. instrument-self-tests is green at the head, so nothing is INTRODUCED.
RESULT prepr: PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1 prepr rc=0 at the head; CI predict shows no instrument red against 8ab5dc566f.
RESULT step13 conflict: `git merge-tree --write-tree origin/main head` exits 0.
RESULT step14 earned: removing the added entries brings back exactly the 5 refusals. The added entries are a verbatim copy of the instrument's own artifact. No budget moves.

Note: instrument-duplicates: the head table carries 13 duplicate list entries across 6 steps' probes (base: 0), e.g. tools/audit/round4/** twice. Cause: selftest_scope.compact_probes concatenates collapse(keep), which can emit a D/** entry, with the D/** entries already in probes, and never dedups. Every reader (covers, drift, select) builds sets, so selection and drift are unaffected. A copy only reaches 2 because the next union re-reads probes as a set. Carry: dismissed: no behaviour effect and tooling freeze; the orchestrator folds it into P-R11-87's round-end proposal (out-of-tree)
