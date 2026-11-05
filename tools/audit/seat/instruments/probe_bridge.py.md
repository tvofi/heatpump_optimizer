# `probe_bridge.py`

- `probe_bridge.py` — derives tests/ci_ratchet.py's `PROBE_REFERENCE_S`
  (the host probe's seconds on the reference host, the fleet's fast class:
  the unit `critical_path_minutes` is priced in) from probed runs on the
  hosted fleet itself: each probed `tests / fast (3.14)` job runs the probe
  and the 13 scripts whose 60-run medians
  (`dev/audit/harnesses/r10_hotfix_ci_critpath_4/fast_scripts.json`) define
  its runner's speed, so the run implies the reference with no cross-machine
  bridge; 3.13 is 3.14's times the heavy jobs' rank-paired probe ratio. With
  no argument it derives from the committed fleet record (`fleet.json`
  beside fast_scripts.json) and prints the tree's value beside it;
  `--repo O/N [--last 16]` derives from live push runs (job logs' `ok`
  lines or wall-clock table). `--self-test`, run by governance's
  `instrument-self-tests` on every pull request, refuses a tree value the
  committed record does not re-derive. When: after any runner-image or
  interpreter change, and once probed push runs exist, to re-derive from
  them in a pull request that replaces fleet.json and the constant
  together (a change of the budget's unit: CLAUDE.md rule 2). Refusal: no
  probed fast (3.14) run with its script seconds.
