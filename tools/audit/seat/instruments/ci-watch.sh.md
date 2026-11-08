# `ci-watch.sh`

- `ci-watch.sh` — watches open PRs' check states and alerts only on NEW
  states (per-PR signature file): reds, CONFLICTING/DIRTY, STALLED zero-runs,
  and required contexts ABSENT at a settled head — a bot GITHUB_TOKEN push's
  `pull_request` runs are held `action_required`, so until one is approved the
  governance family does not report at such a head and it sits unmergeable
  looking green (R9-RC-AUTOFIX-GOVERNANCE). A red `gate` is re-read through
  `merge_train.py classify` (`Train.classify_at`): an edit run's deferral while
  gate.py's `busy` names a code run reads WAIT and raises no RED; a refusing
  read keeps the red (R10-HOTFIX-TRAIN-DEFER-WAIT).
  When: a long fix wave where red-on-main or a fresh failure must interrupt
  work. Refusal: state already seen prints nothing — the exit-1 report is the
  alert, not the log; an unreadable ruleset alerts BLIND once rather than
  silently skipping the ABSENT arm. `--self-test` grades every arm offline on
  the recorded defect shape; `CI_WATCH_ONCE=1` runs a single cycle.
