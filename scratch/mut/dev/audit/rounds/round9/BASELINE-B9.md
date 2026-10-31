# Round 9 baseline, box B9

- baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (v6.7.1)
- repo checkout: /home/claude/heatpump_optimizer
- export (light seats): /home/claude/audit-r9-baseline
- worktrees (isolated seats): D14-s4 /home/claude/audit-r9-D14-s4, D14-s5 /home/claude/audit-r9-D14-s5
- python: /home/claude/venv314/bin/python (CPython 3.14.0rc2; tests/requirements-ci.txt hash-pinned: numpy 2.4.6, scipy 1.17.1; orjson 3.11.9 from tests/requirements-typing.txt)
- node: /opt/node22/bin/node v22.22.2
- chromium: /opt/pw-browsers/chromium-1194 (PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers; ~/.cache/pw-browsers does not exist on this container)
- check_scopes.py --ref baseline: exit 0 (42 seats)
- drift cache: warming in the background from a local scratch commit on top of the baseline (/home/claude/drift-warm), started before the seats; entry under ~/.cache/heatpump_optimizer/drift-baseline/
- driver: run by hand (Prepare done directly, one Agent sub-seat per seat with the prompt finder() builds, then the collector), not through the Workflow tool, so the orchestrator's r9-prepare-patch.sh for audit-find.js was not needed and not applied. The rotation check of Prepare step 5 was satisfied by construction: rotation and scopes were read from the committed files at the baseline (rotation.json parses; every rounds map is {}).
- strip_earlier_rounds (orchestrator's r9-strip-rounds.sh, applied while seats ran): RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235 dir=/home/claude/audit-r9-baseline
