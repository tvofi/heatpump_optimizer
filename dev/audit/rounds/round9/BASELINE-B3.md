# Round 9 baseline, box B3

- Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (v6.7.1)
- Checkout (repo): /home/claude/heatpump_optimizer (detached at the baseline)
- Export: /home/claude/audit-r9-baseline (git archive; docs/audit-*.md and docs/backlog.md deleted; tools/audit/ copied from origin/main)
- Seat worktrees: D0-s3 /home/claude/audit-r9-D0-s3, D3-s3 /home/claude/audit-r9-D3-s3, D11-s1 /home/claude/audit-r9-D11-s1, D11-s2 /home/claude/audit-r9-D11-s2, D13-s1 /home/claude/audit-r9-D13-s1
- Python: /home/claude/venv314/bin/python (CPython 3.14.0rc2, the only 3.14 uv offers here; tests/requirements-ci.txt installed with --require-hashes and the build constraint; orjson 3.11.9 from tests/requirements-typing.txt; numpy 2.4.6, scipy 1.17.1)
- Node: /opt/node22/bin/node (v22.22.2)
- Chromium: /opt/pw-browsers/chromium (no ~/.cache/pw-browsers on this container)
- Drift cache: ~/.cache/heatpump_optimizer/drift-baseline, warmed from a local scratch commit on top of the baseline (/home/claude/audit-r9-warm; never pushed)
- Machine: 4 CPUs, 15 GiB RAM
- check_scopes.py --ref <baseline>: exit 0
- Driver: run by hand (Prepare done by the box host, one Agent sub-seat per seat with the prompt audit-find.js's finder() builds, then the collector step), not through the Workflow runtime. The rotation and scopes compared in Prepare were the committed files at origin/main themselves, so the orchestrator's r9-prepare-patch.sh (step 5 rounds maps) was not needed and not applied. Chromium: /opt/pw-browsers.
- Earlier rounds stripped mid-run (orchestrator's r9-strip-rounds.sh, prepare_baseline.sh logic), while seats were running: RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235 dir=/home/claude/audit-r9-baseline
