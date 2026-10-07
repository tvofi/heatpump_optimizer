# Round 9 baseline, box B4

- Baseline: 1936d5ca72a06556eeed4e8e5bf3dea520e517e1 (v6.7.1)
- Export (no .git; docs/audit-*.md and docs/backlog.md removed; tools/audit/ copied from the checkout): /home/claude/audit-r9-baseline
- Checkout (read-only for seats): /home/claude/heatpump_optimizer
- Isolated worktree, D9-s1: /home/claude/audit-r9-D9-s1
- Python: /home/claude/venv-r9/bin/python (3.14.0rc2; tests/requirements-ci.txt with --require-hashes and --build-constraint tests/requirements-build.txt; numpy 2.4.6, scipy 1.17.1; orjson 3.11.9 at the tests/requirements-typing.txt pin)
- Node: /opt/node22/bin/node (v22.22.2)
- Chromium: /opt/pw-browsers/chromium (PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers; there is no ~/.cache/pw-browsers on this container)
- Drift cache: not warmed. `env_drift.py --all <baseline>` refuses from the checkout because HEAD is the baseline (SELF-COMPARISON, rc 1); a seat that compares a mutated tree against the baseline captures it on first use.
- check_scopes.py --ref 1936d5ca: exit 0.
- Driver: run by hand (Prepare, one Agent seat per seat with the prompt audit-find.js's finder() builds, extracted verbatim from the file at 1936d5ca, then the collector), not through the Workflow tool. The orchestrator's r9-prepare-patch.sh changes only the Prepare prompt (step 5's rotation {steps, rounds} comparison and step 4's Chromium path); the by-hand Prepare compared against the committed rotation.json and scopes.json directly and used /opt/pw-browsers, so the patch changes nothing this box ran. Not applied, committed or pushed.
- Earlier rounds stripped mid-fan-out (orchestrator's r9-strip-rounds.sh = prepare_baseline.sh strip_earlier_rounds), about 12 minutes after the seats started:
  - RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235 dir=/home/claude/audit-r9-baseline
  - RESULT stripped_earlier_rounds=9 files_removed=498 files_kept=235 dir=/home/claude/audit-r9-D9-s1
