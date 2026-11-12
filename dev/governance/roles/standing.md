# The standing seats' shared terms

Binds `standing-merge.md` and `standing-dispatch.md`.

## Wait

End a turn only when nothing is owed. Otherwise wait in a `run_in_background`
shell loop that touches your alive file, and its `FILE.d/<id>` entry, every
25 s while your pid answers `kill -0`, and exits on a queue change or at the
window's end, so its exit wakes the turn. A detached `nohup` wakes nothing. No
tracked loop script (P51); the loop writes no pid into the alive file.

## Reads

Each Bash call starts in the seat's original directory, so every read names
its cwd-safe instrument:

| read | instrument |
|---|---|
| a PR body | `tools/policy/policy_lint.mjs --pr-body` and `tools/audit/carry_audit.py check --body` |
| a PR's state | `pull_request_read` (`web-fragments.md`); print `UNREADABLE` on an error or an empty answer |
| handoff refs | `tools/audit/seat/bus.sh orphans`, or `git -C <worktree>` |

A hand-written pipeline (`| wc -l`, `grep -c`, a bare `git` or `gh`) is never a
check result.

## Autofix hold

Dispatch a reviewer at a pull request's head H, or start a merge at H, only
when no `mutation-autofix`, `closures-autofix` or `claims-autofix` job at H is
queued or in_progress, and either a bot commit has moved the head (act at the
new head) or every autofix job concluded with no push; a red one pushes
nothing (`ci-autofix.md`). Read it with `tools/audit/seat/failure_logs.sh` or
`pull_request_read` (`get_check_runs`). A dispatch at the handoff, before a
pull request exists, has no check-runs and is outside the hold.

## Recycle

Recycle (tvofi, 2026-10-31) once your context passes about 150k tokens or you
have run 4 h, whichever comes first, and only at a quiet point: no op of your
own mid-step, no train, push or open you own in flight. Write a
`STATE-HANDOFF` file in your seat directory (pending waits with targets,
in-flight ops, queue positions, held lines and their release conditions, next
actions), stop only your own loops by PID, and reply `HANDED`. A fresh seat
starts from its brief plus that file.

## Alive files

`$HPO_STATE_DIR/alive/`, the directory `tools/audit/seat/hooks/liveness.py`
reads; `HPO_ALIVE_STALE_MIN` sets staleness.
