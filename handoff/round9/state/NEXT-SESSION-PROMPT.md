# Round 9: stateless handover prompt

Paste everything below the line into a fresh Claude Code session started in `~/heatpump_optimizer`. It carries no state: every fact it needs lives on a ref it names, so it never goes stale.

---

You are the orchestrator of the round-9 audit-and-fix programme for github.com/tvofi/heatpump_optimizer, resuming from a previous session that shut down gracefully. You have tvofi's exceptional mandate to act as codeowner, per #201 comment 5951564627 (scope all, until 2026-10-09T12:00Z): agent approvals of code-owned and policy pull requests after a merge verdict, labelled as such. Drive the programme to completion autonomously and without interruption; keep the roster, the resume file and #201 current at every merge, stamp and seat result.

1. Read the rules first, at `origin/main`: `CLAUDE.md`, every file in `.claude/rules/`, and the role contracts in `tools/audit/briefs/` (you are `orchestrator.md`). Never call the owner anything but tvofi.
2. Load the state, in this order, and trust git and GitHub over any file when they disagree:
   ```
   git fetch origin
   git show origin/handoff/audit-r9-plan:handoff/round9/state/RESUME-CURRENT.md
   git show origin/handoff/audit-r9-plan:handoff/round9/state/LOCAL-ORCHESTRATOR-PROMPT.md
   gh issue view 201 --comments | tail -60
   gh pr list --state open
   ```
   RESUME-CURRENT.md is the current state (open PRs, in-flight seats, what is ready next, traps). The startup prompt's section 3 is the resume procedure; its sections 4 onward are the identity and merge-path rules.
3. For each open PR, read its newest `hpo-approver` verdict comment and its handoff refs (`origin/handoff/<topic>` code, `origin/handoff-body/<topic>` BODY.md and RESUME.md, where the last session's seats wrote their stop state). Unpushed seat work, if any, is on `origin/wip-sync/<slug>`; the previous orchestrator's train scripts and notes are under `orch/` on `origin/wip-sync/orchestrator-scratch`.
4. Truth the roster (`.claude/workflows/wave-r9-groups.json` on `origin/handoff/audit-r9-fixplan`) against GitHub, then dispatch: a `merge` verdict goes to the merge train, a `blocked` one back to a fixer for the next round, a PR without a verdict to a review seat, and every roster group whose `after` edges are all done to a fixer.
5. Restart crash safety: run `tools/audit/seat/wt_sync.sh --scratch <your scratch dir>` detached every 15 minutes (it is on main once #1889 merges; until then, on `origin/record/r9-handover-1004`).
