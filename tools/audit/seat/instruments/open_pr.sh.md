# `open_pr.sh`

- `open_pr.sh` — opens a draft PR from `handoff/<topic>` as `hpo-author`,
  adds its own delivery row, re-pushes, prints N and the head. When: the
  orchestrator opens a seat's handed-off branch. Refusal, each an
  `open_pr: REFUSE:` line before anything is written (`pr_args.sh`): fewer
  than four arguments; a code sha that is not 40-hex or names no commit; one
  that is not an ancestor of `origin/handoff/<topic>`, saying whether it is the
  tip of `handoff-body/<topic>` ("that is the BODY sha; pass the CODE sha" —
  twice on 2026-10-18 that sha stopped the script silently); a missing
  `handoff/<topic>` or `handoff-body/<topic>`; no BODY.md at the body ref — the
  body is the transport, not an afterthought. The soft cap gates only
  dispatching a new roster group, and never refuses opening or updating a pull
  request for an owed handoff (tvofi, 2026-10-20): a leading `--over-cap
  "<reason>"` is still accepted and prints that it is advisory; `pr_cap.py
  info` prints the open count as information, and a count gh cannot read says
  so and still opens. Any later stop prints `open_pr: STOPPED: line N exited S: <command>` (an ERR trap), and a
  refused push names its log. It holds the branch's `upd-<branch>.lock` from
  before its worktree to its second push, so a concurrent `update_pr.sh` is BUSY
  (75) and cannot detach the worktree under the PR's row (#2547-#2549).
  Once the PR exists, any exit before its row is pushed -- a refused second
  (row) push, a step errexit stops between the two pushes, a stop signal --
  runs one EXIT-trap path (`op_close_unrowed`): it returns the worktree to the
  pushed head, closes the draft, and only then posts a comment, read back by
  `gh_comment.py`, quoting the refusal or the `STOPPED` line
  (`open_pr: CLOSED: #N`), so no PR stays open without its row (#2625, #2629,
  #2719); only a close that fails prints `ROWLESS`, for `update_pr.sh`'s
  `ensure_row`. The PR is created only after the body
  contract passes: `app_push.sh` runs `prepr.sh` and the `ref_privacy` guard
  before its push. A main merge that conflicts is aborted and refused
  (`merging origin/main into <sha> conflicts`), so the clean worktree is
  released instead of kept as dirty.
  `--self-test` runs `delivery_row.sh`'s, then
  `pr_args.sh`'s.
