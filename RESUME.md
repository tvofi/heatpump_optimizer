# R9-EG-B5 seat resume (handoff)

- stage: round 2 handed off; code head eed5ac3fa3ed0b2d4df7680800b097217a90acc2 (merge of main aa7a8119 into 2b6cd5cfa) on handoff/r9-eg-dhw-planner (PR #1858),
  merge base 5f87e25a1. Round 1 blocked root-cause-unanswered; D6 header, closures (hand merge of CI recordings), deployment_shape note fixed. The branch is frozen; only the orchestrator moves it.
- cap_exception (tvofi 2026-10-02, roster 6ddb9225): one verbatim-move PR. Proof: tools/audit/round9/EG-B5/provenance.py BASE HEAD.
- Closures were re-recorded by hand: closures-autofix cannot repair while stress.py records rc=1 (instrumentation overhead).
- Owed: the architecture-score delta (score.py --diff, R9-EG-A1 #1851); the pinned mypy census and stress/optimality, which run on CI only.
- After any merge from main, re-run: provenance.py, tests/structure.py, ledger_check.py, a three-dot diff of custom_components and tests.
