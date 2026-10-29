# `judge_batch.py`

- `judge_batch.py` — re-runs every finding's harness, perturbation and null
  control serially under the gate lease, one row per finding. When: a judge
  grades a batch of findings and wants the mechanical half scripted. Refusal:
  a perturbation that does not move the number in the stated direction prints
  `void`; what it cannot run prints `by-hand`, never a pass.
