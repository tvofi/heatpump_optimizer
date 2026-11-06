# BLOCKED: r10-sweep-template-sync

The brief asks to diff the orchestrator's out-of-tree sweep-runner directory against tools/audit/seat/. That directory is not present in this cloud container, and no ref or commit carries it (searched the filesystem, all remote refs, and history for verdict_audit.py, UNHELD, and --fired).

Tracked state at origin/main: sweep_render.py has no --fired option and no Gantt inputs (the only Gantt code is in plan_table.py); sweep_template.md has no verdict-audit, UNHELD, or manual roster-drain text; the plan republish is described only in step (4b). verdict_audit.py has no tracked counterpart.

Question for the owner/orchestrator: supply the four out-of-tree changes (a)-(d) as a diff or as files on a ref (for example under a brief/ or handoff-in/ branch). Without them the fold would be invented, which the brief forbids.
