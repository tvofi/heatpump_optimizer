# Round 9 baseline — box B10

- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1` (v6.7.1), exported with `git archive`; `docs/audit-*.md` and `docs/backlog.md` deleted; `tools/audit/` copied from origin/main (same SHA).
- Export: `/home/claude/audit-r9-baseline`
- Checkout: `/home/claude/heatpump_optimizer`
- Python: `/home/claude/venv314/bin/python` (CPython 3.14.0rc2 via uv; `tests/requirements-ci.txt` with `--require-hashes --build-constraint tests/requirements-build.txt`; orjson 3.11.9 from `tests/requirements-typing.txt`). numpy 2.4.6, scipy 1.17.1.
- Node: `/usr/bin/node` v22.22.2
- Playwright: `npm ci` of `tests/pwlane/` into `/home/claude/pwlane` → `NODE_PATH=/home/claude/pwlane/node_modules`, playwright 1.56.1.
- Chromium: `PLAYWRIGHT_BROWSERS_PATH=~/.cache/pw-browsers` (symlink to the container's `/opt/pw-browsers`); executable `/root/.cache/pw-browsers/chromium-1194/chrome-linux/chrome`, Chromium 141.0.7390.37.
- Drift cache key for the baseline (`tests/env_drift.py --cache-key … --all`): `8dbf208698081bd6f4e0dc1b2f06119e50391beed6beb62b06f79420e1df0041`.
- `check_scopes.py --ref 1936d5ca…` exit 0 (42 seats); D4-s1 resolves to M1+M2+M3 on `custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js`.
- Driver: this box ran `.claude/workflows/audit-find.js` by hand (the brief's fallback), not through the Workflow tool: Prepare done directly, one Agent sub-seat with the driver's `finder()` prompt, then the collector step. The orchestrator's `r9-prepare-patch.sh` (rotation rounds check, step 4 browsers path) was therefore not needed and not applied; the args were the committed `rotation.json` and `scopes.json` at 1936d5ca, so steps 5–6 hold by construction.
- Earlier-round strip (orchestrator's `r9-strip-rounds.sh`, prepare_baseline.sh logic), applied at ~09:17Z while D4-s1 was running: `RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235 dir=/home/claude/audit-r9-baseline`
