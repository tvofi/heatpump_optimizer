# D5 — verify-v3-leads (V3: reach and class)

## D5-s2-51 — optimizer comments describing a data flow the code does not have

**Executed numbers.** Re-ran `tools/audit/round9/D5/leads/dataflow_comments.py`: baseline `handed_offset_steps=0` vs `elapsed_steps=2`, `model_sequence_writes=0` (buffer_is_store=1, trajectory len=97); `--shift --plant` perturbation: `2` / `1`. Exact match to the finder's recorded values. load1 1.08, thread_factor 1.000.

**Independent measurement.** Wrote `tools/audit/round9/D5/verify-v3-leads/v3_dataflow_comments_recheck.py`: a direct source read (not through the finder's instrumentation) confirming both cited sentences are present verbatim (`both_sentences_present=2 of 2`) and that `coordinator._warm_seeded` copies `result.power_schedule` with `np.asarray(...).copy()` and no index shift (`warm_seeded_copies_verbatim=1`, `warm_seeded_shifts=0`). Also read `optimizer.py:3100` ("the same problem one step later") and `:1084-1089` ("the model stashes the series on itself for the terminal-cost term") directly.

**Attacks.** Reachability: `_warm_seeded`'s only caller is `coordinator.py:4772`, a real solve path — production, not test-only; `ThermalModel.__setattr__` fires during every `HeatPumpOptimizer.optimize` call. Not a stub-only artifact. Null control (both counters move together only when planted) holds. No gate-mode or aggregate concerns (exact, non-grid counts). Severity: the underlying behavior is already correct (cited by D0-s3 and D7-s2's non-findings) — only the comment is wrong, so hygiene/low is earned, not inflated.

**Class.** `I5` (docs/comments drift stale against code) — exact match: the mechanism is precisely "a comment describes a data flow the code does not have."

**Metric definition.** (a) shift aligning the handed plan to the previous plan after one 30-min re-plan; (b) sequence-valued ThermalModel attribute writes during one valved solve.

**Vote: verify.** Severity low, class I5, seam_rule_enumerates true.
