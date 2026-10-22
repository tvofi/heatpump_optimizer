Roster group R10-NIGHTLY-ABSENT-NEW. `nightly-status` (`tests/nightly_status.py`) turned every pull request and `main` red with `NIGHTLY ABSENT: no scheduled run of the workflow was found at all ... GitHub disables schedules on repositories with no recent activity`. That diagnosis was false. `nightly.yml` (cron `17 2 * * *`) reached `main` with #2585 at 2026-10-22T08:05Z, after that day's 02:17Z slot, and GitHub reports the workflow `active`. The workflow had no scheduled run yet because it was younger than its first slot. The no-run arm named a cause it had never read.

**The fix.** `verdict()`'s no-run arm moves into a new pure function, `never_ran(workflow, now)`, which decides on GitHub's own record of the workflow (`state`, `created_at`):
- (b) any `state` other than `active` (`disabled_inactivity`, `disabled_manually`, `disabled_fork`, `deleted`) reads **ABSENT**, quoting GitHub's word for it, with the re-enable command.
- (a) an `active` workflow registered less than `NEW_WINDOW` ago reads **NEW**. NEW exits 0 and says why: no run is owed yet, and this is not a pass. `NEW_WINDOW` is one cron period (`SCHEDULE_PERIOD`, one day) plus one hour (`SCHEDULE_LATENCY`).
- (c) an `active` workflow older than that, with still no run, reads **ABSENT**, worded with the state and age it read and without the inactivity claim.
- No record (the `--run` path, or a caller that passes none) stays **ABSENT**, which fails closed.
- A missing `state` or a `created_at` ahead of the reading clock raises `Unreadable` (exit 2), per fixer.md step 16.

`collect()` makes the one extra GET (`/actions/workflows/<file>`) only when discovery and its corroboration found no run at all, and never under `--run`. So a run that finds a nightly spends nothing extra.

**Alternatives, and why each lost** (fixer.md step 17):
- *Compute the actual first cron slot from the cron expression.* That needs a cron parser and a YAML read in a stdlib-only, `-I -S` grader. The first slot always falls within one period of `created_at`, so the period alone bounds it. That is the brief's own "first slot plus a grace" bound, and it needs no cron arithmetic.
- *The first-parent commit that added the file.* That reads git history in a job that restores one file from the base, and it cannot see `state`. The API record answers both questions in one read.
- *Reading the record on every run.* That spends the API on every pull request for an answer only the no-run arm uses.

**What the window rests on.** The period is pinned, not trusted. A new `tests/entities.py` check reads `nightly.yml`'s own `cron:` and refuses unless there is exactly one cron, of the daily shape `M H * * *`, and `SCHEDULE_PERIOD == 1 day`.

**Design choice, stated:** NEW is green. The brief asks for it not to be red, and its bound is what keeps a dead schedule from hiding. GitHub stamps a workflow's `created_at` with the server's offset (`+02:00` live), unlike a run's `Z`. The fixture uses the live shape.

## Head

`66cec3f9b8f8d28c372232c69aad61ad3ab99a6f`, merge base `008ad15bbba4df3dc6cb3afaee4ef7120557739d` (origin/main at dispatch, 2026-10-22). The mutants ran at `af9face2d`, whose two code files are byte-identical to this head's. The only later commit is the roster carry. `entities.py`, `doc_claims.py`, `structure.py` and the agreement lane were re-run at this head.

## Mutation proof

The full suite was run as `PYTHONPATH=tests/hastub python3 tests/entities.py` in a detached worktree for each mutant:
- **M0, the base's `tests/nightly_status.py` with this branch's `entities.py`** (failing test first): it fails with `ValueError: not enough values to unpack (expected 4, got 3)` at the `collect()` call. The base reporter has no workflow record. Its classification of the 9 h fixture is the defect itself: `verdict(None, None, [], now)` at the base gives `ABSENT`, exit 1.
- **M1, the grace bound dropped** (`if now - created < NEW_WINDOW:` changed to `if True:`): `1 of 2400 ENTITY CHECKS FAILED`, which was `FAIL a workflow younger than its first cron slot reads NEW and green, the same one 26 h on with no run reads ABSENT, and a disabled one names its state [9 h -> ('NEW', 0); 26 h -> ('NEW', 0) ...]`.
- **M2, the state read dropped** (`if state != ACTIVE_STATE:` changed to `if False:`): the same check FAILS with `disabled -> ('NEW', 0)`. That run's second failure, `gate lease priority: concurrency control ... overlaps=1`, is a timing check from running four suites side by side. It is not in M1's list or in the head's, and this diff does not touch the lease.

## Unpinned sites

`n/a: every production line this diff adds is reached by the three new entities checks. M1 and M2 are the predicate mutants of the two decisions, and the read-count check pins collect()'s new GET (once with no run, zero with one).`

## Null control

- **The window does not hide a dead schedule.** The same `active` record 26 h after `created_at`, with no run, reads `ABSENT` with exit 1, and its text carries `'active'` and not `inactivity` (the first new check). A scratch probe of the edges gave 24.9 h NEW, 25.0 h ABSENT and 26 h ABSENT.
- **No record still reads ABSENT.** `verdict(None, None, [], now)` with no workflow argument gives `ABSENT`. The existing check "no run, a stale run and a run whose lanes were skipped are all ABSENT" is unchanged and passes.
- **The extra read is not spent on a found run.** A discovery that finds a run makes 0 reads of `/workflows/nightly.yml`; a discovery that finds none makes exactly 1 (the third new check).

## Figures

- **The finder's harness, live, both ends.** The reporter ran against the GitHub API at 2026-10-22T21:11Z:
  - the base copy, `python3 -I -S <git show origin/main:tests/nightly_status.py>`, printed `NIGHTLY ABSENT: no scheduled run of the workflow was found at all.` and `GitHub disables schedules on repositories with no recent activity`, rc 1;
  - the head copy, `python3 -I -S tests/nightly_status.py`, printed `NIGHTLY NEW: the workflow is active and GitHub registered it 13.1 h ago (2026-10-22T10:05:56+02:00)`, rc 0. That run predates the UTC normalisation, which now prints `08:05:56+00:00`.
  - Both readings hold only until the first scheduled Nightly concludes (due about 2026-10-23T02:17Z). After that, both copies take the run arms and this harness reads flat.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at this head: `ALL 2400 ENTITY CHECKS PASSED`, with the three new checks `ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`, with no budget touched.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/closure.py select --diff 008ad15bb`: `MODE: SCOPED -- 3 script(s) run, 30 scoped out` (`doc_claims.py`, `entities.py`, `harness_headers.py`):
  - `doc_claims.py`: `ALL 203 checks PASSED`;
  - `harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `run_always`:
  - `env_drift.py --claims-only origin/main`: `claims hygiene: origin/main ok`;
  - `closure.py selftest`: `ALL 112 closure shrink pins PASSED`;
  - `layout.py`: `layout self-test: ok`.
- **The agreement lane, both copies:**
  - Branch copy (`prepr.sh` step 3f4's commands, at this head): `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`.
  - Base copy, the way wave-script runs it: governance.yml's `wave-script` steps "Restore the check source from the base commit" and "Refuse two readers of one concept that disagree", extracted with PyYAML and run in a detached worktree at this head with `PINNED=008ad15bb`. The restore reported `1 file(s) differ` (`tests/entities.py`), then `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`.
  - No `agreement.mjs` concept names the nightly reporter: `grep -n nightly tools/policy/agreement.mjs tools/policy/agreement_py.py` matches nothing.
- **The class's seams** (fixer.md step 8): the class is a reporter that states a cause it did not read about a scheduled workflow with no run. The rule: `grep -rlI "event=schedule\|actions/workflows/" tests tools .claude .github` returns 8 files.
  - `nightly_status.py`: closed in this diff.
  - `entities.py`: this diff's pins.
  - `budget_raise_gate.py`, `contract_rerun.py`, `cancel_superseded.py`, `run_twins.py`, `autofix_statuses.sh` and `tests.yml`'s ci-ratchet step: each lists runs by PR, head or push event and states no schedule cause. Already outside the class.
  - `grep -rnI "disables schedule\|no recent activity" --exclude-dir=dev .` matches only this diff's own docstring and comment.
- Production lines, from `git diff --stat 008ad15bb...HEAD`: `tests/nightly_status.py` +133/-26 (the docstring included), `tests/entities.py` +89/-2, and the roster +2/-1.

## Red checks

- **nightly-status**: this pull request is graded by the base's copy (the step restores `tests/nightly_status.py` from `PINNED`). Until the first scheduled Nightly concludes, about 2026-10-23T02:17Z, it reads the false ABSENT this diff fixes. The answer is this pull request; the head's copy is driven by `fast` through `tests/entities.py`. The cheaper detector for the defect is the one this diff lands, a NEW/ABSENT fixture pair. Its standing cost is milliseconds in `entities.py`.

## Forward-carry

- **The NEW window's precondition on `nightly.yml`'s schedule.** A second cron, or a non-daily one, turns the period pin red and must re-derive the window. A new scheduled workflow is watched by no reporter until one names it, because `DEFAULT_WORKFLOW` is `nightly.yml` alone. The control and a re-measure instruction are carried with it. Carry: R10-CI-LAYOUT (appended to its `carry` in `dev/programme/rosters/wave-r10-groups.json` in this diff, with `roster_edit.dump`'s canonical bytes)

## Friction

- `fixer: cost`: the brief names `classify()`, but the function is `verdict()`; the no-run arm is now `never_ran()`. Carry: R10-NIGHTLY-ABSENT-NEW
- `gate-scoping: cost`: the cloud container's default `python3` is 3.11 and cannot parse `tests/entities.py` (`SyntaxError: f-string`). The seat venv's 3.14 is required, and the dispatch prompt's "venv python is on PATH" was not true for the default shell. Carry: R10-NIGHTLY-ABSENT-NEW

🤖 Generated with [Claude Code](https://claude.com/claude-code)
