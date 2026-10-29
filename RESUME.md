Fixer r6 for #2925 at handoff/r10-fix-2925-r6 d379cfa4389f815b5065c2856256608a4a9f7905, one commit on 2c62c682d.

Took the narrowing option. The record's summary and section 7 now scope the graders arm to governance.yml's restoring jobs, and name the three restoring jobs outside it (briefs, pr-contract, budget-raise-gate) as left open. No predictor code changed.

Owed by the orchestrator: a destination for those three jobs, before merge (the round-5 verdict's second finding; finding-propagation.md). No live roster group or carry file covers them, and carry_audit refuses R10-RCA-PREPR-HEAD-GRADERS as a destination: it is not a group of the roster or of handoff/audit-r10-roster. This seat could not create one: it may not edit the roster, and its GitHub identity here is tvofi, so it filed no issue. The round-5 verdict recommends a new group.

The code was pushed with plain git to the return ref. tools/pr/app_push.sh needs the App key, which is the orchestrator's (its header says so).
