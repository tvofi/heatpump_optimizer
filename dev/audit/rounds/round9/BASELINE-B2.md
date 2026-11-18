# Round 9 baseline — box B2

- baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (v6.7.1)
- export (light seats D5-s2, D6-s2, D10-s2): /home/claude/audit-r9-baseline
- worktree D0-s2: /home/claude/audit-r9-D0-s2
- worktree D3-s2: /home/claude/audit-r9-D3-s2
- repo checkout: /home/claude/heatpump_optimizer
- python: /home/claude/venv314/bin/python (CPython 3.14.0rc2; tests/requirements-ci.txt hash-pinned: numpy 2.4.6, scipy 1.17.1; orjson 3.11.9 from tests/requirements-typing.txt)
- node: /opt/node22/bin/node (v22.22.2)
- chromium: /opt/pw-browsers/chromium-1194 (PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers; no ~/.cache/pw-browsers on this box)
- check_scopes.py --ref baseline: exit 0
- drift cache: NOT warmed. `env_drift.py --all <baseline>` refuses when HEAD is the baseline (identical captures), and origin/main is the baseline, so there is no ref to compare against here; the first comparison against the baseline fills it (cold run).
- driver: run BY HAND (Agent sub-seats), not through the Workflow tool. Prepare was done by the box host; finder prompts are byte-for-byte what `finder()` in audit-find.js at 1936d5ca builds, plus a host suffix (policy rules, no GitHub/pushing, BLAS pin, write report.json). The orchestrator's r9-prepare-patch.sh (Prepare step 5 rotation {steps, rounds} check; Chromium via $PLAYWRIGHT_BROWSERS_PATH) touches only the Prepare prompt: here rotation/scopes were read from the committed files at the baseline (identical by construction) and Chromium is recorded at $PLAYWRIGHT_BROWSERS_PATH above, so this box ran with the patch's semantics; the file itself was not edited, committed or pushed.
- earlier rounds stripped at ~09:17Z while seats ran (orchestrator's r9-strip-rounds.sh = prepare_baseline.sh strip_earlier_rounds):
  - RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235 dir=/home/claude/audit-r9-baseline
  - RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235 dir=/home/claude/audit-r9-D0-s2
  - RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235 dir=/home/claude/audit-r9-D3-s2
