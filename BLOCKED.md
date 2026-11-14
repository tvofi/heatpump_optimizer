# BLOCKED: r11-outside-honest-starts-runs (fixer seat, no code written)

Question: R10-ADVISOR-STEADY-START is not on main, and the brief's `After:` line and the approved design both make its merge a precondition of this fixer. Do I wait for pull request 3481 to merge and for the note to be revalidated against its merged diff, or does the orchestrator (or owner) lift that precondition in the brief and name the base I build on?

Question: Ruling c1 (a priced start engages on a modulating install too) is `decision: owner` in design.md at 0c692c86d2 and "still open" in the verdict at caab288c05. It sets the engaged predicate and whether three goldens are claimed or none. Has the owner ruled, and which arm do I build?

## Measured, 2026-11-14, origin/main 237fad44532d1927cf65612d395cc5833c60ce99

- `git merge-base --is-ancestor origin/handoff/r10-advisor-steady-start origin/main` (9fe5ad9fbc) and the same for `origin/fix/r10-advisor-steady-start` (5543479d3c): both exit 1. Control: the same command on 6251038ff3, a parent of main's tip merge, exits 0.
- Pull request 3481: `state open`, `draft true`, `merged false`, head 5543479d3c (the GitHub pull-request read); the roster on handoff/audit-r10-roster f38e4a33d1 has the group at `resume.stage: in-progress`.
- `git diff --stat origin/main...origin/fix/r10-advisor-steady-start` touches this group's hot files: `optimizer.py` (hunks at `SolveInputs` and inside `HeatPumpOptimizer`), `coordinator.py`, `tests/features.py`, `tests/closures.json`, `tests/deployment_shape.py`, `tests/structure_budgets.json`, `docs/architecture.md`.

## What refuses the start

- PROMPT.md at 46e1a8b27a: "the fixer starts only on Design review: approve, after ... R10-ADVISOR-STEADY-START have merged, because each of them conflicts with the pull request's text"; Carry 0 supersedes only "after the v10.0.0 stamp" ("Nothing else in the brief changes").
- design.md at 0c692c86d2, "Hot files, position, carries": "After R10-ADVISOR-STEADY-START merges: it adds a held-start field to `SolveInputs` ... so this note is revalidated against its merged diff before the fixer dispatches." The verdict routes the same re-anchoring to the orchestrator.
- A build cut from main today would take its structure, closure and deployment-shape measurements against a base 3481 moves in the same files (`fixer.md` step 6: steps 2 to 8 re-execute after any merge).

Setup ran clean (`cloud-setup.sh --check`: OK; role pack rendered). Nothing else was pushed.
