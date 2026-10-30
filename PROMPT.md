CLOUD FIXER seat for PR #2992 of tvofi/heatpump_optimizer, at head e456ff01323580d4390f964483a17dbdb6cff5bf. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch e456ff01323580d4390f964483a17dbdb6cff5bf for the base you were given.
Output: push the code to refs/heads/handoff/r10-train-overlap-grade-p3, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-train-overlap-grade-p3 <body.md>`, which pushes refs/heads/handoff-body/r10-train-overlap-grade-p3; that second push is the return signal. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
FIXER seat (round 2), group R10-TRAIN-OVERLAP-GRADE, PR #2992, branch fix/r10-train-overlap-grade-p3, live head e456ff01323580d4390f964483a17dbdb6cff5bf. Contract: dev/governance/roles/fixer.md at origin/main.
Read the blocked verdict in full, with its ev/ files: git show 2b0a5407ce4cd3e52be4fcc6c4adf1da0b9da0db:VERDICT.md
The block: governance / instrument-self-tests is red, with queue_pre_flight self-test reporting 1 failed of 43, and this diff caused it. Its new merge-base --is-ancestor probe in Train.freeable meets queue_pre_flight's fixture stub, which answers any merge-base argv rc 0. So the "HEAD is not origin/<branch> still PARKs" arm frees the holder.
Do exactly this:
- Update queue_pre_flight.py's fixture so that --is-ancestor answers non-ancestor for that arm. Add the twin arm, where an ancestor holder passes under --free-holders, mirroring merge_train's P184 pair.
- Add queue_pre_flight, the second caller of Train.freeable, to the body's P184 class rule.
- Run python3 tools/audit/seat/queue_pre_flight.py --self-test and merge_train.py --self-test. Both must have 0 failed.
- Name the red check and its answer in ## Red checks, per defect-root-cause.md's second trigger. The cheaper detector is that local self-test, which takes seconds.
- Optional, only if cheap: pin the new survivors, carrying them as before. These are: land's `if approval and not carried`; policy_refusal's SKIPPED/NEUTRAL green set; and the --ignore'd red context. Otherwise leave them as findings with Carry: R10-TRAIN-OVERLAP-GRADE.
- Update ## Head and ## Figures, re-deriving every figure.
Return handoff/r10-train-overlap-grade-p3, descending from e456ff01, plus handoff-body via body_push.sh. Never open or edit the PR. If a hook refuses you, stop and report.
