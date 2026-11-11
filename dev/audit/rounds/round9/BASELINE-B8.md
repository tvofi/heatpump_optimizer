# Round 9 baseline, box B8

- baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (v6.7.1)
- repository checkout: /home/claude/heatpump_optimizer
- export (no .git; docs/audit-*.md, docs/backlog.md removed): /home/claude/audit-r9-baseline
- worktrees: D14-s1 /home/claude/audit-r9-D14-s1, D14-s2 /home/claude/audit-r9-D14-s2, D14-s3 /home/claude/audit-r9-D14-s3
- python: /home/claude/venv314/bin/python (CPython 3.14.0rc2 via uv; tests/requirements-ci.txt --require-hashes with --build-constraint tests/requirements-build.txt; orjson 3.11.9 per tests/requirements-typing.txt; numpy 2.4.6, scipy 1.17.1)
- node: /opt/node22/bin/node (v22.22.2)
- chromium: /opt/pw-browsers (PLAYWRIGHT_BROWSERS_PATH); no ~/.cache/pw-browsers on this container
- drift cache: cold. env_drift.py --cache-key printed dc8ba1b5ae1c1cf82be260075a58348bb6062e77709d900cfa1872fec73ed997; ~/.cache/heatpump_optimizer/ does not exist, and no capture was taken because every tree here sits at the baseline, which env_drift.py refuses as the ref.
- check_scopes.py --ref baseline: exit 0 (42 seats)
- driver: run by hand (the Workflow tool was not used), so the r9-prepare-patch.sh edit to audit-find.js was not needed and not applied; Prepare's steps were executed directly, rotation.json and scopes.json read from the committed files at the baseline, and each seat got exactly the prompt finder() builds.
- earlier rounds stripped after the seats started (orchestrator's r9-strip-rounds.sh, prepare_baseline.sh strip_earlier_rounds logic): RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235 dir=/home/claude/audit-r9-baseline
