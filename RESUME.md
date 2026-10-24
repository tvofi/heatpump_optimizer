r10-sav-comfort repair r1 (fixer-sav). Code head 51021b4a6, which merges origin/main 73b69fe0a into 8e18704ef and moves no production or check file.
- Closing keyword dropped: the body says `Part of #2492`, so open_pr runs with an empty intended list. #2492 stays open for carry 5's seam 2 (`Carry: #2492 (item ea7e7a49)`), per the orchestrator's ruling. The orchestrator adds the actuation-seam group before R10-SAV-COMFORT goes done.
- `mutation` is named under Red checks. All 14 sites (16 operator mutants) were driven at 51021b4a6, and every one was killed by mutation_table's rule. mutation-autofix pins them after the push. There is no survivor and no code change.
- The 5193 GUARD_OFF triage was corrected: the mutant is killed by the DHW and buffer COP checks, so it is not equivalent.
