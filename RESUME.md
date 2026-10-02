# R9-EG-B5 seat resume (handoff)

- stage: handed off for review; code head cb7cd281a9dd01ee7ff58efc5bbca90baa458020 on handoff/r9-eg-dhw-planner,
  merge base origin/main 948671af1dcb63b1e3ceebb0154ba5c5b9c2911e. The branch is frozen; only the orchestrator moves it.
- cap_exception (tvofi 2026-10-02, roster 6ddb9225): one verbatim-move PR. Proof: tools/audit/round9/EG-B5/provenance.py BASE HEAD.
- Expected first-CI reds: closures UNDER-SCOPED for dhw_planner.py, and three tests/entities.py closure checks; wait for the closures-autofix bot commit.
- Owed: the architecture-score delta (score.py --diff, R9-EG-A1 #1851); the pinned mypy census and stress/optimality, which run on CI only.
- After any merge from main, re-run: provenance.py, tests/structure.py, ledger_check.py, a three-dot diff of custom_components and tests.
