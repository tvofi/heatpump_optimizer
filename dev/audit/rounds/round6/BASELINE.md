# Round 6 baseline

- **baseline SHA**: `e336cc2c530882a142ef298de6420706d96a6300` (v6.6.9, the round-5 completion stamp)
- **main checkout (repo)**: `~/heatpump_optimizer`
- **export (no .git; finders D1, D2, D4, D5, D6, D7, D8, D10, D12)**: `~/audit-r6-baseline`
- **isolated worktrees (with .git)**: D0, D3, D9, D11, D13 under `~/audit-r6-<dim>` (detached at `e336cc2c`)
- **python**: `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` — 3.11.5, numpy 2.4.6, scipy 1.17.1, aiohttp 3.14.3, voluptuous, threadpoolctl (the CI-pinned stack in `tests/requirements-ci.txt`); orjson 3.12.0 also present
- **node**: `~/.nvm/versions/node/v20.10.0/bin/node` (v20.10.0)
- **Chromium**: `~/.cache/pw-browsers` (chromium-1148 = Playwright 1.49.0)
- **drift cache**: `~/.cache/heatpump_optimizer/drift-baseline/` (warm for round-5 SHAs; re-capture `e336cc2c` on first miss)
- **machine**: 8-core Apple M1, 8 GB RAM (darwin, arm64)

Run every harness from the export/worktree root with `PYTHONPATH=tests/hastub`.
