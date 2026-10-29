# `roster_edit.py`

- `roster_edit.py` — the safe roster edit: every op loads the whole roster,
  validates, and dumps with the file's own formatting; ops `set-stage`
  (with `--at-sha`), `wire-issue [--field fixes|issues]`, `unwire-issue <group> <N> [--field
  fixes|issues]` (refuses an absent N), `append-group`, `edit-brief`,
  `append-carry`, `drop-carry <group> <index|--match TEXT>` (0-based index,
  or the one entry containing TEXT; the last drop leaves `"carry": []`, the
  key kept),
  `set-after <group> <G1,G2,...|->` (replaces the after-edges whole, `-` for
  none), and `set-resume <group> --field
  <stage|commit|branch|last_step|next_step|note>` for the resume free-text
  fields a session restarts from. When: any roster change — never a string
  splice, which unbalanced the file twice. Refusals: the lint gate (run from
  a fresh origin/main checkout — a stale `--lint-cwd` is refused itself), an
  unknown group, a duplicate issue or carry, for `set-after` an unknown
  after-group, a self-edge, a repeated edge and a cycle in the resulting
  after-graph, for `drop-carry` an absent carry, an out-of-range index, no
  match and an ambiguous match, and for `set-resume` an empty
  value on the non-null fields (`stage`, `branch`) or a non-sha on
  `--field commit`; an empty value on a nullable field clears it to null.
  `--roster-ref` defaults to `main` and `--branch` to the round's
  `handoff/audit-r<N>-roster`, never main itself; `--roster-path` overrides
  the newest roster.
  A no-op edit reproduces the roster's bytes exactly and reports `no change`
  instead of an empty commit — the round-trip the self-test pins, because a
  dump that misses the file's formatting rewrites all 7503 lines on any edit.
  The edit is committed in a detached worktree and pushed as
  `<sha>:refs/heads/<branch>`, never by a local branch name another run of
  the same `--checkout` can reset. A push lost to a rival re-applies the op
  on the new tip, at most `PUSH_ATTEMPTS` times, then refuses with rc 2; a
  `--worktree` whose HEAD is on no origin ref is not reused.
