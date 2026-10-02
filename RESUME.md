# F10.6 resume note (comparison-bound mutation operator)

- branch@commit: handoff/r9-f10-gate-infra-6@cd04771a17bdc6df6c91e9d9a852f211fec63de0
- merge base: 8fa06663 (origin/main at 2026-10-02T17:08Z)
- last completed step: tvofi ruled "enable now" (2026-10-02); CMP_BOUND added to RATCHETED at cd04771a, check inverted, steps 2-8 re-run, body re-taken, prepr clean; handed off again.
- next step: orchestrator opens the PR from cd04771a; fix review (opus, another session) from a detached worktree at that head.
- state: CMP_BOUND enabled in the ratchet (5466 sites, 4855 unpinned; ratchet base equal, no added site). Multi-line comparisons (C7) stay deferred.
- open: main red at 8fa06663 (#1854 x #1848, always() check); hotfix #1859. Do not merge main until the orchestrator says it is green.
- local runs: entities.py, harness_headers.py, structure.py via ~/hpo-seats/R9-F11.4-venv; everything else with hpo-seats/bin/python3.
