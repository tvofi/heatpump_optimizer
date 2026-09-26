# D5 round 9 leads unit — verifier V1 (reproduce)

Box G4-V1. This unit covers the leads findings of dimension D5, read from `origin/handoff/audit-r9-evidence` at 96b89163 in a separate worktree. It was not merged into this output branch.

- Interpreter: `/home/claude/venv/bin/python` (CPython 3.14.0rc2) with `PYTHONPATH=tests/hastub`, and node 22.
- Load: load1 0.95–1.61, thread_factor 1.000. Every metric is a count.
- Only the finders' leads harnesses were re-run, under `tools/audit/round9/<dim>/leads/`. No harness was written, and no production or test file was edited.
- There is no independent (step 2) measurement beyond code reads and greps. That lens belongs to V2.

## D5-s2-51 — verify, low
- **Metric:** (a) index offset between the handed _prev_shipped_plan and the previous plan re-aligned to the new solve's clock after one 30-min re-plan; (b) sequence-valued ThermalModel attribute writes during one valved solve
- **Number:** handed_offset_steps=0 (elapsed_steps=2), model_sequence_writes=0 (finder same); --shift --plant -> 2 / 1
- **Method:** Re-ran dataflow_comments.py baseline and --shift --plant (the harness's perturbation/control arm); grep confirmed optimizer.py:3100 and :1088 comments live
- **Attacks:** Counts, contention-immune (load1 0.95-1.11, tf 1.000); single scenario, no aggregate; production path
- **Note:** The harness exposes its perturbation and null arm together as `--shift --plant`.
