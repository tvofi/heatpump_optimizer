# `probe_bridge.py`

- `probe_bridge.py` — re-derives tests/ci_ratchet.py's `PROBE_REFERENCE_S`
  (the host probe's seconds on the reference host, the unit
  `critical_path_minutes` is priced in) from probed push runs on the hosted
  fleet itself: each probed `tests / fast (3.14)` job runs the probe and the
  13 scripts whose 60-run medians
  (`dev/audit/harnesses/r10_hotfix_ci_critpath_4/fast_scripts.json`) define
  its runner's speed, so the run implies the reference with no cross-machine
  bridge. `--repo O/N [--last 16]` prints the implied 3.14 and 3.13 values,
  their spread and the tree's; it changes nothing. When: once probed push
  runs exist, to replace the one-machine bridge PROBE_REFERENCE_S was set by
  (R10-HOTFIX-CI-CRITPATH-4), and after any runner-image or interpreter
  change. Refusal: no probed fast (3.14) run with its script lines.
