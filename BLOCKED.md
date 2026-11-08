# BLOCKED: r10-fly-no-self-carry

The policy edits are done and verified at the head of this ref: fixer.md, finding-propagation.md and fix-review.md,
plus regenerated mirrors. `rules_sync --check` is ok, and `policy_lint.mjs` and `--budgets` report 0 errors.

`tools/pr/prepr.sh` returns rc=1 and so is not a clean run:
`REFUSE closures: failed while being recorded: tests/entities.py (exit 1)`.
`tests/entities.py` dies on `ModuleNotFoundError: No module named 'homeassistant'` under venv-ci's python3.
Under /opt/hpo/venv-ha it dies on `No module named 'paho'` (homeassistant mqtt import).
This container's toolchain cannot run entities.py, and the diff touches no Python.

Question for the orchestrator: provide a container whose python can import homeassistant and paho, or rule that a
prepr whose only refusal is this environment gap may hand off. I did not work around the refusal, and opened no handoff.
