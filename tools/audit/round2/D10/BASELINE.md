# Round 2 — D10 pass baseline

- baseline (this pass): b39fc6f01f4caee9d3ef17bce5f0b4561392fdb9 (origin/main HEAD, 2026-09-02)
- round-2 original pin c398fc8 superseded for D10: it predates the round-1 fix wave (v6.2.15–v6.3.3, incl. #206 #207 #209 #210); re-pinning to avoid re-reporting fixed rules
- export (read-only finder): /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-D10-export
- python: /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python (run from the export root with PYTHONPATH=tests/hastub)
- gate at pin time: Hassfest success, Validate success, CodeQL success, Tests in_progress (parent e729182 Tests success 23m)
- thread pin: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
