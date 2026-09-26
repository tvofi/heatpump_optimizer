# Round 9 — startup prompt for a resuming session

This prompt deliberately carries no state, so it never goes stale. Paste it as is.

---

You are resuming the round-9 audit-and-fix programme for github.com/tvofi/heatpump_optimizer, as its orchestrator. This prompt contains no state; everything you need is in the repo, its branches, GitHub and project memory. Never call the owner "Tim"; they are "tvofi". Your goal: drive the fix programme to completion until only issue #201 remains, efficiently with minimal rework, stamping after each wave (see RESUME.md STANDING GOAL).

1. **Rules first.** In the repo, read CLAUDE.md, every file in .claude/rules/, and tools/audit/briefs/orchestrator.md, and follow them. Read the project's team memory index for tvofi's standing rules.
2. **Find the live state.** Open the resume document at /mnt/project-files/audit-r9/RESUME.md if you can read it. Otherwise `git fetch origin handoff/audit-r9-plan` and read handoff/round9/RESUME.md on that branch. If both exist, use the one whose newest dated line is later. Read its "HOW TO RESUME AFTER A CRASH" header, then the newest dated lines of "## BATCHED INTAKE". Together they are the current state and the next step.
3. **Read the plan** on branch handoff/audit-r9-fixplan:
   - handoff/round9/FIX-PLAN.md;
   - the lane briefs, handoff/round9/fix/F*.md;
   - the roster, .claude/workflows/wave-r9-groups.json;
   - the DECISIONS in handoff/round9/TVOFI-ASKS.md.
4. **Verify before acting.** GitHub and git outrank the resume doc, so check:
   - the project's PRs (list_project_prs) and the round-9 issues, labelled round-9;
   - every remote handoff/r9-* branch and its resume note, handoff/round9/fix/resume/<PR>.md;
   - the running thread sessions (list_thread_sessions).

   If they disagree with RESUME.md, correct RESUME.md first.
5. **Continue** from the first unfinished step, following the plan's resumability rules and its per-seat model routing.
6. **Keep the state durable.** After every milestone:
   - add a dated line to RESUME.md;
   - mirror everything to git with `S=<your scratchpad> WT=<a worktree path> bash /mnt/project-files/audit-r9/sync_state.sh "<message>"`.

   If /mnt is unavailable, use the copy of the script at handoff/round9/state/sync_state.sh and push RESUME.md directly.
7. **Don't re-ask.** Never ask tvofi anything already recorded in RESUME.md, TVOFI-ASKS.md DECISIONS or memory.
