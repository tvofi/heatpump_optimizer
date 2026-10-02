# F10.6 resume note (comparison-bound mutation operator)

- branch@commit: handoff/r9-f10-gate-infra-6@c117c2b3c3b1e6b97a79248589abbfc946aff50c
- merge base: 8fa06663 (origin/main at 2026-10-02T17:08Z)
- last completed step: fixer.md steps 1-8 done; body drafted; prepr clean (PREPR_SKIP_CLOSURES=1); handed off.
- next step: orchestrator opens the PR from c117c2b3; fix review (opus, another session) from a detached worktree at that head.
- state: CMP_BOUND lands in list mode only (LISTED, not RATCHETED). Enabling it = adding "CMP_BOUND" to RATCHETED in tests/mutation_table.py, a one-word edit, after tvofi prices it on the body's Figures.
- open questions / waiting on whom:
  - tvofi: enable CMP_BOUND in the ratchet at the measured cost (stock +946 sites/+946 unpinned; per-merge burden mean 1.01, max 15 over 121 merges; nightly minutes unchanged at --max 40, drain about +24 nights)? If yes, a follow-up commit flips RATCHETED and updates the "stays out of the ratcheted inventory" check.
  - orchestrator: main is red at 8fa06663 on tests/entities.py "no job-level if leads with always(): a cancelled run stops (CI cancel)" (tests.yml:mutation-ledger, mutation-ledger-push), from #1854 x #1848; not this lane's file.
- local runs: tests/entities.py via R9-F10.5/venv interpreter (numpy); everything else with hpo-seats/bin/python3.
