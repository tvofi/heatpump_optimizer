# BLOCKED: r10-body-contract-p3-bootstrap

Change is done and committed at the wip head: one `pinned tools/pr/figure_block.py` entry with `pending:` in DECLARED of tools/policy/field_coverage.mjs.
`node tools/policy/field_coverage.mjs --self-test` ok; the full run prints the entry as pending, dead=0 refused=0.

`tools/pr/prepr.sh` rc=1. Its one REFUSE: `closures  failed while being recorded: tests/entities.py (exit 1)`.
`tests/entities.py` ends "3 of 2655 ENTITY CHECKS FAILED" at this head AND at an unmodified checkout of 53273de4d449 (same three):
- the coverage job reuses only an entry main's push run saved, keyed on the runner's OS
- the release ZIP holds the integration folder at its root ...
- the Pages workflow deploys on a release tag ...
So the red is inherited from this environment (interim toolchain behind the locks), not from the diff.

Not handed off: the brief allows a handoff only on a clean prepr run, and I did not work around the refusal.
Question for the orchestrator: hand off at this head anyway (CI on a proper toolchain decides), or re-run in a repaired environment?
