# BLOCKED: r10-ci-priority-pause

Question: Where does the priority-pause live? The dispatch message says the home is tools/pr/cancel_superseded.py plus the beat's cancel-sweep row "as your brief states", but PROMPT.md (f1d4c7b3) and the roster brief for R10-CI-PRIORITY-PAUSE place the pause/resume in tools/audit/seat/merge_train.py (wait_ci, paused.json, rerun-failed-jobs) and state "Not carried: pausing inside cancel_superseded.py". Neither the roster brief nor PROMPT.md mentions cancel_superseded.py or cancel-sweep as a home. Which governs? Also: the dispatch's rule (cancel queued runs of non-priority PRs while a priority PR has a queued run, re-run on release) differs from the brief's (cancel the lowest-ranked PR's active runs when a head/main job has queued >= 5 min).

Measured at 61afd4f2d: tools/audit/seat/ci_priority.py and dev/audit/config/ci_priority.json do not exist; roster_lib.py has is_hotfix (kind=="bug" or HOTFIX in name) but no savings_h, group_class or touches_production; the group has no source/hotfix/savings fields; its roster `after` is R10-TICK-LEVELS, R10-OUTSIDE-FIRST (not checked whether merged).

No code written. Waiting on a ruling before building either shape.
