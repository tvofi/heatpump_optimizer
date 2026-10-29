# `plan_table.py`

- `plan_table.py` — renders the plan artifact from a wave-groups roster:
  swimlanes, mermaid gantt (critical path tagged `crit`), per-group detail,
  ETA. When: regenerating the plan table after a roster edit. Refusal: none —
  but the gantt's grammar checks run in `--self-test`, not at render time.
