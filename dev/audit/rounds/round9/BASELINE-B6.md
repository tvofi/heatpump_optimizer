# Round 9 baseline — box B6

- baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (v6.7.1)
- export: /home/claude/audit-r9-baseline (git archive; docs/audit-*.md and docs/backlog.md deleted; tools/audit/ copied from the checkout at origin/main = baseline)
- checkout: /home/claude/heatpump_optimizer
- worktrees: none (no isolated seat in B6)
- python: /home/claude/venv/bin/python (CPython 3.14.0rc2; tests/requirements-ci.txt hash-pinned: numpy 2.4.6, scipy 1.17.1; orjson 3.11.9 at the tests/requirements-typing.txt pin)
- node: /usr/bin/node v22.22.2
- chromium: /opt/pw-browsers/chromium (no ~/.cache/pw-browsers on this container)
- box: 4 CPUs, 15 GiB RAM
- check_scopes.py --ref 1936d5ca exit 0 (42 seats)
- driver: run by hand, not through the Workflow tool (the brief's fallback). Prepare done by hand as audit-find.js describes; rotation and scopes read from the committed files at the baseline, so the step-5/6 comparisons are identities; the r9-prepare-patch.sh fix to the driver's step 5 was not needed and not applied. Finder prompts generated from audit-find.js's own finder() template (node, same DISPATCH block) and given to one Agent sub-seat per seat, all five at once (three heavy).
- earlier rounds stripped after the seats started (orchestrator's r9-strip-rounds.sh, prepare_baseline.sh logic), at 2026-09-26T09:16:11Z: `RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235 dir=/home/claude/audit-r9-baseline`
- drift cache warmed: env_drift.py --all 1936d5ca^1 with DRIFT_WARM_CACHE=1 exited 0 (the self-comparison against 1936d5ca is refused by design)
