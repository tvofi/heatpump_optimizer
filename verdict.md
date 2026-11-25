Design review: revise e50b4a1f8b4befd9c3cb0e0865d7b4f1fc11f016 architecture-unsound, harness

Group R11-CI-CASE-SELECT, note design.md at e50b4a1f (one commit, one file), base origin/main 34c7a3f610.
Seams checked at the base: 248 and 64 top-level R.section spans (features.py, entities.py); features_block.py
run/--emit-prelude; closure.py _exec_record and select(); harness.Results.section; .gitattributes ledgermerge
on tests/closures.json; CI Python 3.14 (sys.monitoring available). The seam (a new case_select module, select()
unchanged, FULL on main/nightly) is sound. Three points block:

1. architecture-unsound -- design.md:88 (fail-safe, header): "blob matches neither the merge base nor the head,
   AND the header hash moved" fails open. On an ordinary PR the table was recorded on main, so its blob equals the
   merge base and the conjunction is false; a PR that edits the header (imports, shared fixtures, patches before
   the first R.section) then runs only the diff-selected spans, and rule (ii) covers spans, not the header. Fix
   wanted: the header hash differing from the table's header_hash alone forces CASES: FULL for that script
   (or runs every span), independent of the blob test; evidence 4 adds that trigger as a mutation target.

2. architecture-unsound -- design.md:74 and :79 (rule iii, needs* runs predecessors only). A span whose outcome
   changes through an earlier span is not selected: (a) an edited span E (rule ii) that rebinds a global or patch
   a later unchanged span L reads leaves L unrun, and E's new bindings are not in the base-recorded needs at all;
   (b) a span S selected by (i) computes data that a later L consumes without calling into the changed file, so
   L's own files miss it and L is skipped while its outcome moves. Fix wanted: add the forward closure
   (every span whose needs* reaches a span in i or ii also runs), and compute the static half of needs from the
   head's AST at plan time rather than from the table; state the hidden-state classes the id() snapshot cannot see
   (stdlib module state such as the global random RNG -- features.py seeds _random at :20867 and :23302 -- and
   in-place mutation of shared objects, 44 top-level mutating calls in features.py, 11 in entities.py) and route
   them to a FULL trigger or to needs, rather than to the risk list at :144.

3. harness -- design.md:121 (evidence 5, soundness replay) has no null control and is likely vacuous: merged PRs
   were green at parent and head, so "spans whose outcome differs" is almost always just the edited spans that
   rule (ii) selects trivially; the replay would pass with needs* and (i) both deleted. Fix wanted: drive the
   soundness harness from the mutation ledger -- tests/mutation_ledger/killed_by holds 5968 pins naming the
   killing script; for a sample of pins killed by features.py or entities.py, apply the mutant, plan with the
   mutant's file as the diff and the sample fraction at 0, run the plan, and require the script to fail. Null
   control: the same mutants with the plan restricted to spans that do not read the mutated file must pass (or
   with rule (i) disabled must miss), so the harness is shown to move. The measurement table (:130) states its
   null too: the FULL script-level seconds measured in the same run on the same host as each scoped figure.

Not blocking (carries for the designer to fold, or the fixer): CASE UNDER-SCOPED printed on main without a commit
(:106) needs an owner of the repair (the next closures-autofix or a nightly re-derive), or rule 1's backstop is a
print nobody acts on; the selection decision itself should be logged per run (selected ids) so a miss found later is
replayable. The #3885 case_sample.pick shape is not on origin; the note's adapt-the-call-site rule covers it.
Routed: none.
