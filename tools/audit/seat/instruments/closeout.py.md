# `closeout.py`

- `closeout.py` — the round's final act, composing `prune_refs.py`,
  `worktree_gc.sh`, `state_docs.py` and `brief_lint.mjs`. When: after every
  other roster group is done, just before the closure stamp (the orchestrator's
  step; the dry plan runs at any time). A dry plan by default: it writes
  nothing. `--apply` refuses first, naming each group other than
  R10-CLOSEOUT-CLEANUP that is not done, then runs five gated steps: (1) roster
  and the four state docs in main, no policy path citing a doomed ref bare,
  brief_lint green; (2) archive tags then deletes by batched `git push`;
  (3) seat worktrees removed (one with an unpushed commit or uncommitted work is
  kept and reported), orchestrator scratch cleared, local branches reduced,
  a final worktree_gc; (4) open issues beyond `--successor` block (it closes
  none); (5) the report with counts before and after under `--report-dir`.
  Archiving merged cloud sessions stays the orchestrator's. `--self-test` runs
  every control against a throwaway bare remote.
