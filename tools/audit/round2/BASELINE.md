# Round 2 baseline

- baseline: c398fc84eec25fc44b60d74aae05b9a2da205884
- export (read-only finders): /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-baseline
- worktrees (instrumenting finders): D0 /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-D0, D3 /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-D3, D9 /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/audit-r2-D9
- python: /Users/timmalmstrom/copilot-worktrees/heatpump_optimizer/tvofi-claude/.venv/bin/python (run from the directory root with PYTHONPATH=tests/hastub)
- node: /Users/timmalmstrom/.nvm/versions/node/v20.10.0/bin/node
- chromium: /Users/timmalmstrom/.cache/pw-browsers/chromium-1148 (PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/pw-browsers)
- playwright module: install into a scratch prefix, e.g. `npm i --prefix /tmp/pw playwright@1.49.0`, then NODE_PATH=/tmp/pw/node_modules
- gate lock: take it only when tests/closure.py select reports MODE: FULL or names
  tests/stress.py -- that one script is what the lock exists for. Use
  tests/gate_lock.py, never mkdir and a shell pid (#404 replaced that: no lease, so
  tests/run.sh cannot renew it, and no flock, so a crashed holder holds it forever).

      python3 tests/gate_lock.py take --label <your-label>
      HPO_GATE_LOCK_LABEL=<your-label> GATE_SCOPE=auto GOLDEN_MODE=drift \
        GOLDEN_REF=<a ref that is not HEAD> ./tests/run.sh
      python3 tests/gate_lock.py renew --label <your-label>   # between commands
      python3 tests/gate_lock.py release --label <your-label>

- thread pin: OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
