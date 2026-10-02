# F10.6 resume note (comparison-bound mutation operator)

- branch@commit: handoff/r9-f10-gate-infra-6@307ecf6cb77f931460a6312c90fcf42d781e724f
- merge base: aa7a8119 (origin/main, #1859 hotfix), merged via the orchestrator's 9a639794
- last completed step: round 2 answering the #1861 review (blocked mutation-vacuous): `<` case and multi-line case in the fixture (R8, R5 now killed), two equivalent sites triaged (away.py _holiday_span, optimizer.py _dhw_planner_draws) via equiv_probe.py, refusal text names comparison bounds, drain-nights figure corrected, scan scope stated. entities 2075/2075, prepr clean.
- next step: orchestrator re-adds the delivery row and requests the same reviewer for the round-2 delta (fix-review.md step 12).
- state: CMP_BOUND enabled (5466 sites, 4853 unpinned vs 4855 at base). R6/R9 survive and are equivalent per the review. Multi-line comparisons (C7) deferred, now held by a check.
- local runs: entities.py, harness_headers.py, structure.py, equiv_probe.py via ~/hpo-seats/R9-F11.4-venv; everything else with hpo-seats/bin/python3.
