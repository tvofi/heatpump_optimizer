# R11-OWNER-STEP-KICK: blocked before code

Question: none of the four predecessors that design 09fecb1b orders before this group (FLOWCAP, FROST-HOLD, FAULT-HOLD, MODE-LEGS) is on origin/main 1207ee13b0e439a4acefccabace691785af2ebad. Should this seat (a) wait until MODE-LEGS lands and cut from that main, or (b) build on 1207ee13b0e439a4acefccabace691785af2ebad now, deferring T11 and the MODE-LEGS-based harness baseline, with the orchestrator merging the four predecessors into the frozen head later?

Measured at origin/main 1207ee13b0e439a4acefccabace691785af2ebad, 2026-11-22T19:03Z:
- `git merge-base --is-ancestor <ref> origin/main` returned non-zero for handoff/r11-owner-flowcap (0d1cae21a6) and handoff/r11-owner-mode-legs (81db193f15); `git ls-remote origin refs/heads/handoff/r11-owner-frost-hold refs/heads/handoff/r11-owner-fault-hold` returned no refs.
- Control: the same ancestry check returns zero for origin/main's own parent.

Why this is a departure (fixer.md step 17, "a departure is raised, not made"), from design 09fecb1b:
- §6: "FLOWCAP lands first, then FROST-HOLD, then FAULT-HOLD, then MODE-LEGS, then STEP-KICK. This group rebases onto all of them."
- §5 T11 pins FROST-HOLD's entry setting swap_at; FROST-HOLD's hold row exists on no ref.
- §5 Payment: module_excess_loc's net must be measured at the merge base with the predecessors' pump_arbiter.py lines already in; a figure measured at 1207ee13b0e439a4acefccabace691785af2ebad would be stale once they land.
- §6 MODE-LEGS: the served note sits on the same _arbitrate lines MODE-LEGS rewrites, and the harness's "before" baseline is taken on MODE-LEGS' merged code.

No code was written. Carry: R11-OWNER-STEP-KICK (pending orchestrator ruling on dispatch order)
