# Root-cause seat brief RC2: v6.6.12 bug 5 (toggles back on after reboot; mode not persisted)

Before doing any work, read `CLAUDE.md` in the repository and all related rules files (`.claude/rules/`, and the role contract for your seat under `tools/audit/briefs/`), and follow them. Pass this rule on in every sub-agent brief you write.

Never refer to the project owner as "Tim" anywhere, especially on the public repository (PR bodies, commits, comments, issues, delivery notes). Call them "tvofi". A PR body's attribution line is `_Requested by **tvofi**_` and carries no claude.ai project link. Pass this rule on in every sub-agent brief you write.

Role and mechanics as RC1 (root-cause.md; cloud seat; countermeasure on handoff/r9-rc2-<topic>; report back through the coordinator to the round-9 orchestrator).

## The defect (reached a release: defect-root-cause.md first trigger)
tvofi's v6.6.12 bug 5: "Away, boost DHW, optimizer active and boost space heating ... flip back on in a few seconds", and "all toggles on after reboot". #1621 fixed the flip-back half. The fixer of R6 (branch handoff/r9-r6-reboot-toggles, code head df50ab42, body tools/audit/handoff/r9-r6-reboot-toggles.md on that branch) found and fixed: a mode change was persisted only at the end of a completed update cycle, so a restart (or failed cycle) before that restored the old mode — reproduced for Optimizer active at the merge base and at v6.6.12. Away and both boosts were NOT reproduced coming back on after a stored off, on real HA 2026.2.3 and the stub; one timing-dependent ordering (a turn-off before the spawned restores land) does return Away and Optimizer active on; an untested hypothesis: at v6.6.12 PARALLEL_UPDATES = 1 held queued turn-offs behind a 33–73 s solve, so a restart could cancel them. Read the body's probes and sha1s.

## Owed
root-cause.md §1–5 for the mode-persistence cause, and a verdict on whether the unexplained remainder has a cause you can establish (test the PARALLEL_UPDATES/service-queue hypothesis if you can drive it). Process state with evidence: which process let "state persisted only at end of cycle" ship and survive #1621's own startup-writer check? Class reach: every user-set state (switch/select/number/time entities) and where it is persisted relative to its setter — this is likely a round-9 class candidate; list every seam with its disposition. Cost test and countermeasure (or the recorded decision, with numbers). If the class has ≥3 instances, say so: round 9 then owes a class-eliminating barrier (defect-root-cause.md).
