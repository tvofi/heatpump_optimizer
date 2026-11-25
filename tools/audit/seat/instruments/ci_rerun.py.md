# `ci_rerun.py`

- `ci_rerun.py` — reruns only the failed jobs of a pull request's head runs, and
  only where a failed job is required by an active ruleset (CI-6). When: a
  required red at a PR's live head that a rerun can clear (a runner loss, a
  flake), instead of a whole-run rerun or a fresh dispatch. Per workflow and run
  name it judges the newest run at the head: `WAIT` while active, `OK` when
  green, `CAP` at attempt 6, `SKIP non-required <job>` when every failed job is
  outside the required set, else `RERUN` (POST `rerun-failed-jobs`); `NORUN`
  with `--dispatch` starts `ci.yml` naming the PR and its base. `--dry-run` (or
  `DRY=1`) posts nothing. The required set is read live, cached ten minutes in
  `$HPO_STATE_DIR`. Refusal: an unreadable pull request, ruleset or run listing
  reruns nothing and says so; a push run on main is never read. `--record DIR`
  writes a PR's reads as the self-test's fixture.
