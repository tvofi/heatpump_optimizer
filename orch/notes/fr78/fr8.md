_Requested by **tvofi**_

Part of #201.

## The ask

The orchestrator's record work (plan tables, roster edits, resume docs, handover prompts) is manual and error-prone (two JSON breakages from string splices; stale-worktree lint phantom errors; body-file location refusals). Make it reusable, generalized and stateless, in `tools/` per decision 0013.

## The four tools

1. **plan-table** — swimlane table (lane × wave), mermaid gantt with the critical path highlighted (the graphical layout of the previous session's artifact, durable in markdown), per-group detail rows, ETA block, live overlay flag.
2. **roster-edit** — safe JSON load→modify→dump; ops set-stage/wire-issue/append-group/edit-brief/append-carry; checkout-B worktree branch pattern; refuses to push unless brief_lint from a FRESH MAIN checkout prints TOTAL 0.
3. **resume-doc** — regenerates RESUME-CURRENT.md sections within its 10 KB budget.
4. **handover-prompt** — emits NEXT-SESSION-PROMPT.md from the resume doc + roster.

Each stateless, each with a self-test, reusing the existing roster-generator and rev-3 plan-table parsing.

## Sources

Roster: `origin/handoff/audit-r9-fixplan` (group R9-FR-8). Precedent: #1879 (instruments live in the tree); the orchestrator's manual patterns 2026-10-04.
