The record beat in `.github/workflows/tests.yml` auto-merges record pull requests on its own schedule, so a record pull request can land while a merge train is waiting on CI and move `main` under it: #2291, #2295 and #2299 each merged mid-train on 2026-10-15, stopping or re-carrying #2284 and #2290. CI cannot see the train's local pidfile. This makes the train publish a ref while a real run is live, and makes the record beat's automerge step skip while that ref is younger than its bound.

**The train half** (`tools/audit/seat/merge_train.py`). A real run (`base: main`; a `batch/` rehearsal merges nothing into `main` and publishes nothing) calls `hold_refresh()` before anything can merge and again at the start of each queue item, and `hold_release()` before its closing line on every path (`TRAIN DONE`, `TRAIN STOPPED`, and a `finally` backstop). The ref is `refs/heads/train-hold`, and it points at a commit created at publication through the API (`POST /git/commits`, then `POST /git/refs`, or `PATCH` for a refresh or to adopt a stale ref a crashed train left), so its committer date is the publication time the beat reads as the hold's age. It is created through the API and never `git push`, because the API starts no push-triggered run. A refused hold is logged `NOT held: …` and the train runs on: the hold guards a bookkeeping beat, and stopping a merge train for it is the worse failure.

**The beat half** (`.github/workflows/tests.yml`, automerge step). After the step's token masks and before it reads the pull request's head, it reads `GET /repos/{repo}/commits/train-hold` and computes the age of `commit.committer.date`. Younger than `HOLD_MAX_AGE_S` is a live train: `say skip-train-hold; exit 0`, leaving the open record pull request for a later beat. At or past the bound is stale (a crashed train moved nothing, so no rows went overdue — `STALE_AFTER_COMMITS` is commit-based). A date ahead of the runner's clock is unknowable, never young (#775), and is treated as stale; an unreadable or absent hold leaves the pre-fix behaviour. `record_row.py --automerge-check` is untouched.

The bound is derived, not chosen: the train's own constants bound one queue item — a CI wait is at most `polls` (24) sleeps of `min(POLL_SECONDS, HEARTBEAT_SECONDS)` = 5760 s, and a `--main-moved-tries` recovery re-runs that wait (the constant's comment budgets ~40 min each), so one item stays under ~3.6 h; `HOLD_MAX_AGE_S=14400` (4 h) is above it. Because the train refreshes per item, a long run never ages a live item stale; because a crashed train blocks records at most 4 h and merges nothing, its rows are late, not overdue.

What the owner is approving, and the rollback, are under `## Approval`.

Fixes #2302.

## Head

`17197336f0128a60cb454b641f15b6192ec0d715`

## Mutation proof

Train half, `python3 -I tools/audit/seat/merge_train.py --self-test` (each mutant applied, the suite run, the line restored; the restored file re-runs at 194/194):

- Delete the start-of-run `hold_refresh()` — `FAIL the hold is refreshed once per queue item, so one long item cannot age it stale`.
- Delete the `hold_release()` before `TRAIN DONE` so only the `finally` releases — `FAIL a real train holds the record beat before its first merge and releases it before the closing line (issue #2302)`.
- Delete `if not self.real: return` — `FAIL a batch/ rehearsal publishes no hold (null control: it merges nothing into main)`.
- Delete the per-item `hold_refresh()` in `one()` — `FAIL the hold is refreshed once per queue item, so one long item cannot age it stale`.
- Change `if code or not is_sha(sha):` to `if code:` — `FAIL an unreadable hold commit does not stop the train: logged, no ref, no delete`.

Workflow half: `tests/entities.py`'s TRAIN-HOLD block (executed over a stubbed API) run against each mutant of the step:

- `-lt "$HOLD_MAX_AGE_S"` → `-gt` — `FAIL tests.yml's automerge skips while a live merge train holds the record beat (executed, issue #2302) [status='refused']` and `FAIL … null controls`.
- `say skip-train-hold; exit 0` → `say skip-train-hold` (falls through to the guard) — `FAIL … skips while a live merge train holds the record beat … [status='refused']`.
- `HOLD_REF=train-hold` → `HOLD_REF=train-holds` — `FAIL the beat's hold ref and the train's hold ref name the same branch [beat=train-holds, train=train-hold]`.
- `if [ "$hold_age" -lt 0 ]` → `if false` — `FAIL … null controls` (a future-dated stamp then reads young).

## Null control

At the merge base (`2dadcdc8cbcc2da860e5043b54d0c899038da506`) with only the tests added, `python3 -I tools/audit/seat/merge_train.py --self-test` printed `merge_train self-test: 194 checks, 4 failed`, the four being:

```
FAIL a real train holds the record beat before its first merge and releases it before the closing line (issue #2302)
FAIL a train stopped mid-queue still releases the hold before its closing line (a stopped train must not block the record beat)
FAIL the hold is refreshed once per queue item, so one long item cannot age it stale
FAIL an unreadable hold commit does not stop the train: logged, no ref, no delete
```

and `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `3 of 2362 ENTITY CHECKS FAILED`, the three being:

```
FAIL tests.yml's automerge skips while a live merge train holds the record beat (executed, issue #2302)  [bound=0, status='skip-unread']
FAIL and a hold at the bound, one dated ahead of the runner's clock, an absent one and an unreadable one do not skip (null controls)
FAIL the beat's hold ref and the train's hold ref name the same branch  [beat=None, train=None]
```

With no hold code, the automerge step proceeds for every hold read — including a fresh one — i.e. it merges exactly as today. The rehearsal arm is the null control for the train: a `batch/` base publishes nothing. The unreadable-commit arm is the null control for the fail-open path: no ref is created and the pull request still merges.

## Figures

- `python3 -I tools/audit/seat/merge_train.py --self-test` → `merge_train self-test: 194 checks, 0 failed`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` → `ALL 2362 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED` (no row moved: the diff touches no `custom_components/` file).
- `python3 tests/closure.py select --diff 2dadcdc8cbcc2da860e5043b54d0c899038da506 --workdir <dir>`; `scope.txt` → `MODE: FULL -- every test script runs, nothing is scoped out.` (the diff touches `tests.yml`, a gate file), and `scope.run` is empty.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only 2dadcdc8cbcc2da860e5043b54d0c899038da506` → `claims hygiene: 2dadcdc8cbcc2da860e5043b54d0c899038da506 ok`; both claim files are byte-identical to the base.
- `PYTHONPATH=tests/hastub python3 tests/closure.py selftest` → `ALL 124 closure shrink pins PASSED`; `PYTHONPATH=tests/hastub python3 tests/layout.py` → `layout self-test: ok`.
- `python3 -I tools/audit/seat/tmp_paths.py --check --ref HEAD` → `0 refused, 0 stale allow entries`.
- The bound: `merge_train.py`'s `polls` default 24 and `HEARTBEAT_SECONDS` 240 → one CI wait ≤ 5760 s; `HOLD_MAX_AGE_S=14400` is above that plus a `--main-moved-tries` recovery. Re-derive by reading the four constants.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` (a `run_always` script; run under the exclusive gate lease through `tests/gate_lock.py`) → `ALL 109 HARNESS HEADER CHECKS PASSED`.

Box load during the local runs: `load1=83.74` at `2026-10-20T15:22:48Z` (`uptime`), so no wall-clock figure here is attributable to this change.

## Red checks

`none` at handoff: the branch's checks are CI's to run (the diff is a gate file, so every scoped/test lane runs).

## Forward-carry

`none`

## Friction

`none`.

## Approval

Code-owned path (`.github/workflows/`); this pull request needs tvofi's approving review. Approving it approves one behaviour change: **while a merge train is live, the record beat does not auto-merge a record pull request.** It is off when no train runs (no ref), off after a train's closing line (the ref is deleted), and off after 4 h from publication (a crashed train). No `VERSION`, manifest version, `RELEASE_NOTES.md` heading, golden fixture or claim file changes; `record_row.py` is untouched, so the guard that decides what may auto-merge is the same predicate as before — only *when* it runs changes.

The rollback is a two-file revert (`git revert` of this merge): the beat's default (no ref read) is the pre-change behaviour, and the train's `hold_refresh`/`hold_release` calls go with it. If a ref is left behind, it is inert once 4 h old and can be deleted with `gh api -X DELETE repos/tvofi/heatpump_optimizer/git/refs/heads/train-hold`.

Known residual, stated for the review: a record pull request whose only trigger (a `main` push from the train, or the nightly) falls inside a hold lands at the next trigger after the hold ends, not immediately. `OVERDUE` is commit-based (`STALE_AFTER_COMMITS` 12) and a held beat follows at most one train's merges, so this is a delay, not a red.
