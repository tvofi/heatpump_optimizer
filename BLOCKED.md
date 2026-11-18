# R11-INTAKE-R10-RESIDUE part 1/7 (carries 0, 19, 27, 29, 30): blocked before building

Question: The dispatch says to build carries 0, 19, 27, 29 and 30 to the approved note design/R11-INTAKE-R10-RESIDUE at af8f7048ad, but that note approves no shape. Its "Notes for the fixer" say "No fixer is owed: this note approves no shape", and its outcome is "stop, reported", which leaves each carry to the round-11 architect's triage (architect-planner.md). Building any of the five carries would depart from the approved note, and the brief says a departure is raised, not made. Should this part (a) wait for the architect to re-home these carries and a design to approve a shape for each re-homed cluster, or (b) go ahead under a new or revised approved design that names the shape for these five carries?

## What was read

- Base: origin/main 7c2f4c30cab5610cf8f5b040c326836ab544d27d (the dispatch head).
- Design: af8f7048ada2e3d951537a07e94d713abe856fff `design.md`, approved by design-verdict 89755fd4. It says: "No fixer is owed: this note approves no shape." It also says: "Re-homing a carry is `architect-planner.md`'s act; a design note that picks owners would pre-empt it."
- Roster: `dev/programme/rosters/wave-r11-groups.json` at handoff/audit-r10-roster 595979dc2c. `resume.next_step` reads "p1/7 fired 06:35Z (carries 0,19,27,29,30) on approved design af8f7048". `files` still names only `tools/audit/seat/merge_train.py` and `tools/audit/seat/orchestrator_tick.py`, which no carry in this part touches.

## Where the note and the dispatch disagree

- All five carries: the note approves no shape, but the dispatch asks for a build.
- Carry 29 (the boost settling-tail formula): the brief says to follow the note's disposition for it. The note gives it no disposition of its own; it sends every open carry to the architect, which matches the roster's "architect P3 input" route and not a build.
- Carry 30 lists seven items across `tools/pr/prepr.sh`, `tools/policy/policy_lint.mjs`, `tools/audit/seat/carry_audit.py`, `ci_predict` and `open_prepr_receipts`. Carry 0 touches the cancel path and `ci_pause.py`. Carry 19 touches `dev/audit/harnesses/r10_advisor_steady_bracket.py`, and carry 29 touches `BoostState` in product code. These seams share no owner. That is the stop the note recorded under designer.md step 2.

No code was written and no carried figure was re-measured, because the measurement would only feed a build that the approved note does not authorize.
