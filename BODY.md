Root-cause seat for the Dependabot pip stale-hash class, beside R10-DEPENDABOT-3414-COMPAT (`root-cause.md`). It changes no production code and no lock. The analysis is `dev/audit/rca/r10-rca-dependabot-stale-hash.md`, registered as `_rca` `R10-RCA-DEPENDABOT-STALE-HASH` in `dev/audit/config/bugclasses.json`. The instrument is `dev/audit/harnesses/dependabot_stale_hash.py`.

Cause: a pin goes stale exactly when its `name==oldversion` also appears in a comment of the same lock, and Dependabot rewrites that comment. Dependabot rewrites the version in both places, but the hash block keeps the old version's hashes. Over #3088, #3323 and #3414, 9 of 9 stale pins have this shape and 0 of 61 freshly hashed pins do. Process state: (c). #3147 and #3408 followed the re-apply process in `.github/dependabot.yml`; #3147's own `name==version` comments planted 5 of the later 6 stale pins. Cost test: build A, the comment convention plus the `--tree` guard, at 0.05 s per run. Refused: B (a lower schedule or limit) and C (a recompile workflow). D (a PyPI checker) stays refused by P544.

## Head

`a1d062e3a7f074331cc8666f70e1b1b80e9713d6` on `origin/main` `d08ed31049`, measured 2026-11-11T01:32Z.

## Mutation proof

The countermeasure built here is a detector, so the proof is the detector failing on the defect and passing once the defect is gone, with no mutant needed:
- `--tree` exits 1 at `d08ed31049` (17 exposed) and at #3414's parent `699f4d9ef4` (17). It exits 0 on a scratch worktree of `d08ed31049` where every comment line of `tests/requirements*.txt` has `==` replaced by a space (`exposed=0`).
- The census exits 1 at the Dependabot heads `bffd45a03a`, `da3a5cfb8b` and `4182e75d77`. It exits 0 at the re-apply commits `20fc628eee`, `b9c009a6b3` and `a555d52ae8`.
- `--self-test` prints `self-test FAIL`, exit 1, under each mutant: `stale_pins`'s `hashes == before[name][1]` replaced by `False`, and `exposed`'s `re.search` guarded by `False and`. It exits 0 at the head.

## Null control

- The 61 moved pins with no comment occurrence: 0 stale.
- Dependabot's npm and github-actions heads in the window (#3087, #3321, #3322, #3413): census `files=0 stale=0`, exit 0. They carry no hash lock.
- The boundary case: `pyjwt==2.15.0.` (a full stop follows) was not rewritten by Dependabot and got fresh hashes. `--tree` lists it anyway, by design (1 extra, 0 missed over the three).

## Figures

- stale per PR 3, 5, 1; moved 46, 17, 7: `python3 dev/audit/harnesses/dependabot_stale_hash.py <head>` at the three Dependabot heads (`git fetch origin +refs/pull/<N>/head`)
- 9 of 9 stale versus 0 of 61 fresh, and stale set = comment-rewritten set: `git diff -U0 <head>^ <head> -- 'tests/requirements*.txt' | grep -E '^[-+]\s*#'` per PR, against the census
- exposed=17 at `d08ed31049`: `python3 dev/audit/harnesses/dependabot_stale_hash.py --tree`
- guard runtime real 0m0.052s: `time python3 dev/audit/harnesses/dependabot_stale_hash.py --tree`
- planted-by commits: `git log --reverse --format=%H -S'<comment text>' origin/main -- tests/`
- red hours, re-apply open time, CI runs and review rounds: GitHub API, pull request created, closed and merged times; workflow runs listed per re-apply branch with automerge `skipped` excluded; reviews on #3147 and #3408. All stated in the RCA's section 5 table.
- P(recurrence) 3 of 3 pip PRs against 0 of 4 npm and actions PRs: PRs by `dependabot[bot]` created from 2026-11-01 to 2026-11-10, census per head

## Red checks

none

## Forward-carry

- Reword every lock comment that `--tree` lists so no pinned package is spelled `name==`. In the same diff, correct `.github/dependabot.yml`'s "Dependabot leaves some hash lines stale" to name this cause, and run `dependabot_stale_hash.py --tree` from the suite that reads the locks (exit 1 at its parent, exit 0 at its head). Its diff already edits `tests/requirements-typing.txt`; this seat may not edit a lock. Carry: R10-DEPENDABOT-3414-COMPAT

## Friction

none
