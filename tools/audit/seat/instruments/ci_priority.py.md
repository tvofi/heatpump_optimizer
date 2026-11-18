# `ci_priority.py`

- `ci_priority.py` — the one CI-priority rule (owner, tvofi 2026-10-28 and
  2026-11-11): `tier(group, crit, roster, setting)` puts a pull request in
  main-push, cp-hotfix (critical path, hotfix, accepted outside group), tier1
  (production, or a recorded saving at or above `major_savings_h`) or
  instrument, reading each group's mapping only through `roster_lib`
  (`is_hotfix`, `is_outside`, `savings_h`, `group_class`); `rank()` is the
  sort key (tier, then the setting's tiebreaks). `dev/audit/config/ci_priority.json`
  holds the order and knobs only. Imported by `ci_pause.py`,
  `tools/pr/cancel_superseded.py` and `orchestrator_tick.py` (owed lines).
  When: by hand only for `queue-wait` (before and after `priority_cancel` is
  switched), otherwise `--self-test`. Refusal: a setting that keys
  data by group, drops a `never_pause`/`never_cancel` floor member, demotes
  `main-push`, or has a knob of the wrong type (`SettingError` naming the key).
  `queue-wait --since <iso> --until <iso> [--ref <ref>]` is carry 4's measure:
  per workflow run created in the window, the minutes to its first job's start,
  split by the roster tier of its head branch (main counted, not measured; a run
  with no started job counted unstarted). Read in hour slices (a filtered
  listing stops at 1000 runs).
