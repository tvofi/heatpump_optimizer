# Round 7 baseline

- **baseline SHA**: `f9d6f78243fa65f6fa128d2357752a2ae7f60648` (the round-6 fix wave fully merged — all 38 round-6 issues closed; the v6.6.10 stamp runs in parallel and is not part of this baseline)
- **main checkout (repo)**: `/Users/timmalmstrom/heatpump_optimizer`
- **export (no .git; finders D1, D2, D4, D5, D6, D7, D8, D10, D12)**: `/Users/timmalmstrom/audit-r7-baseline`
- **isolated worktrees (with .git, locked)**: D0, D3, D9, D11, D13 under `/Users/timmalmstrom/audit-r7-<dim>` (detached at `f9d6f782`)
- **python**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` — 3.11.5, numpy 2.4.6, scipy 1.17.1, aiohttp 3.14.3, voluptuous, threadpoolctl (the CI-pinned stack in `tests/requirements-ci.txt`)
- **node**: `/Users/timmalmstrom/.nvm/versions/node/v20.10.0/bin/node` (v20.10.0)
- **Chromium**: `~/.cache/pw-browsers` (chromium-1148 = Playwright 1.49.0)
- **drift cache**: `~/.cache/heatpump_optimizer/drift-baseline/` (re-capture `f9d6f782` on first miss)
- **machine**: 8-core Apple M1, 8 GB RAM (darwin, arm64)

Run every harness from the export/worktree root with `PYTHONPATH=tests/hastub`.

Earlier audit rounds were stripped from both the export and the worktrees before the
finders were dispatched (the round-6 register's exposure-contamination note).
