# F10.6 resume note (comparison-bound mutation operator)

- branch@commit: handoff/r9-f10-gate-infra-6@bdc14972515b7bbca4175159acb644860928e5c9
- merge base: 68b8cb97 (origin/main; merged at edac88f4, #1856/#1857/#1858)
- last completed step: round 3 for the #1861 review round 2 (null-control): equiv_probe.py tie-only controls (17/17 away, 6/11 dhw_planner, 5 with last == 0), triage rows re-quoted; _dhw_planner_draws row re-keyed after #1858 moved it to dhw_planner.py. entities 2078/2078, prepr clean.
- next step: orchestrator re-adds the delivery row; same reviewer judges the round-3 delta.
- state: CMP_BOUND enabled (5466 sites, 4853 unpinned vs 4855 at base). R6/R9 survive and are equivalent per the review. Multi-line comparisons (C7) deferred, now held by a check.
- local runs: entities.py, harness_headers.py, structure.py, equiv_probe.py via ~/hpo-seats/R9-F11.4-venv; everything else with hpo-seats/bin/python3.
