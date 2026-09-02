# Round 2 baseline

- baseline: c398fc84eec25fc44b60d74aae05b9a2da205884
- export (read-only finders): /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline
- worktrees (instrumenting finders): D0 /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-D0, D3 /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-D3, D9 /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-D9
- python: /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python (run from the directory root with PYTHONPATH=tests/hastub)
- node: /Users/timmalmstrom/.nvm/versions/node/v20.10.0/bin/node
- chromium: /Users/timmalmstrom/.cache/pw-browsers/chromium-1148 (PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers)
- playwright module: install into a scratch prefix, e.g. `npm i --prefix /tmp/pw playwright@1.49.0`, then NODE_PATH=/tmp/pw/node_modules
- gate lock: mkdir /tmp/hpo-gate.lock before any tests/run.sh; rmdir after
- thread pin: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
