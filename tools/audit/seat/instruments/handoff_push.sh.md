# `handoff_push.sh`

- `handoff_push.sh` — the legacy one-shot: pushes a handoff branch as
  `hpo-author` with body, title and its own delivery row (`delivery_row.sh`;
  its update path adds a row a refused earlier push left out). When: only where
  `dev/programme/HANDOVER.md` still names it; new work uses `open_pr.sh`/`update_pr.sh`.
  `--self-test` runs `delivery_row.sh`'s and its own: the three push calls
  (open, update, row) over a scratch origin with a stub `app_push.sh`, so a
  push line replaced by `true` reddens it (#2444). Every commit the code head
  adds over `origin/main` passes `ref_privacy.py guard --over` before any
  worktree or push, so a trailer the cloud harness pushed is refused there.
