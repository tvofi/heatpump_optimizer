The record beat in `.github/workflows/tests.yml` auto-merges record pull requests on its own schedule, so a record pull request can land while a merge train is waiting on CI and move `main` under it: #2291, #2295 and #2299 each merged mid-train on 2026-10-15, stopping or re-carrying #2284 and #2290. CI cannot see the train's local pidfile. This makes the train publish a ref while a real run is live, and makes the record beat's automerge step skip while that ref is younger than its bound.

**The train half** (`tools/audit/seat/merge_train.py`). A real run (`base: main`; a `batch/` rehearsal merges nothing into `main` and publishes nothing) arms the hold and calls `hold_refresh()` before anything can merge; it refreshes at the start of every queue item (`one()`), before every recarry (`recarry()`, where a recarry begins inside `app_push`'s prepr), and before every sleep inside `wait_ci()`. `hold_release()` runs before the closing line on every path (`TRAIN DONE`, `TRAIN STOPPED`, and a `finally` backstop). The ref is `refs/heads/train-hold`, pointing at a commit created at publication through the API (`POST /git/commits`, then `POST /git/refs`, or `PATCH` for a refresh or to adopt a stale ref a crashed train left), so its committer date is the publication time the beat reads as the hold's age. It is created through the API and never `git push`, because the API starts no push-triggered run. A refused hold is logged `NOT held: …` and the train runs on: the hold guards a bookkeeping beat, and stopping a merge train for it is the worse failure. Only a train or batch arms the ref; the bare `wait-ci` subcommand never publishes one, because it has no closing line to release it.

**The beat half** (`.github/workflows/tests.yml`, automerge step). After the step's token masks and before it reads the pull request's head, it reads `GET /repos/{repo}/commits/train-hold` and computes the age of `commit.committer.date`. Younger than `HOLD_MAX_AGE_S` is a live train: `say skip-train-hold; exit 0`, leaving the open record pull request for a later beat. At or past the bound is stale (a crashed train moved nothing, so no rows went overdue — `STALE_AFTER_COMMITS` is commit-based). A date ahead of the runner's clock is unknowable, never young (#775), and is treated as stale. The endpoint answers **422** `No commit found for SHA: train-hold` for an absent ref (measured live 2026-10-20), not 404, so both 404 and 422 are the silent absence and the pre-fix behaviour; any other code is logged and treated as absent. `record_row.py --automerge-check` is untouched.

**Why the bound prices a refresh gap, not a wait.** The longest gap between two refreshes is one phase, not one wait: a recarry (5–15 min inside `app_push`'s prepr, and `--overlap` runs one per serial entry before any wait), one poll of `min(POLL_SECONDS, HEARTBEAT_SECONDS)` = 240 s, or a queue item's work between the per-item refresh and its first wait (a `land`: preflight plus at most `merge_tries` 8 × 30 s). Every long wait — a serial CI wait, a `--batch` proof, a re-proof, a `main_green` read — goes through `wait_ci`, so it refreshes from the wait loop; every up-front `--overlap` recarry goes through `recarry()`. `HOLD_MAX_AGE_S=3600` is above the longest named phase (a 15-minute recarry) by more than 3× and does not depend on how many waits a run contains; a crashed train unholds records within 1 h, and its rows are late, not overdue.

What the owner is approving, the rollback and the recorded seams are under `## Approval`.

Fixes #2302.

## Head

`a8c8287f57e09c808e47597910bd9791c93a3579`

`prepr.sh` ran with `PREPR_SKIP_CLOSURES=1` (the owner's ruling for this wave), so prepr's closures step was skipped here; CI's `closures` job is the authority for it.

## Mutation proof

Train half, `python3 -I tools/audit/seat/merge_train.py --self-test` (each mutant applied, the suite run, the line restored; the restored file re-runs at 198/198):

- Delete the start-of-run `hold_refresh()` (the arming stays) — the per-item refresh still creates the ref, so the counts shift and T1 reds these two, **not** the first-merge check: `FAIL the hold is refreshed once per queue item, so one long item cannot age it stale` and `FAIL a recarry refreshes the hold, so --overlap's up-front recarry loop cannot age it`.
- Delete the `hold_release()` before `TRAIN DONE` so only the `finally` releases — `FAIL a real train holds the record beat before its first merge and releases it before the closing line (issue #2302)`.
- Widen the arming guard back to `if not self.real: return` — `FAIL a bare wait-ci publishes no hold: only a train or batch arms the ref`.
- Delete the per-item `hold_refresh()` in `one()` — `FAIL the hold is refreshed once per queue item…` and `FAIL a recarry refreshes the hold…`.
- Change `if code or not is_sha(sha):` to `if code:` — `FAIL an unreadable hold commit does not stop the train: logged, no ref, no delete`.
- Delete the `hold_refresh()` inside `wait_ci()` — `FAIL a CI wait that outlives one poll refreshes the hold mid-wait, so the bound can be shorter than a wait`.
- Delete the `hold_refresh()` before a recarry — `FAIL a recarry refreshes the hold, so --overlap's up-front recarry loop cannot age it`.
- **The batch arm** (`_batch` is the `train.sh` path): delete its start `hold_refresh()` with the arming kept — rc 1, `198 checks, 1 failed`, `FAIL a real-base batch publishes the record-beat hold before it merges anything (the primary path is armed, not only the serial one)`.
- Delete both `_batch`'s `hold_armed = True` and its start `hold_refresh()` — rc 1, `198 checks, 1 failed`, the same `FAIL a real-base batch publishes the record-beat hold…`. Before this repair both of these mutants left the suite green; the new check reads the stub's call order (commit → ref → first merge) on a `--base main` batch of one, where no wait sleeps and no proof refreshes, so the start publish is the only hold write before the merge.

Workflow half: `tests/entities.py`'s TRAIN-HOLD block (executed over a stubbed API) run against each mutant of the step:

- `-lt "$HOLD_MAX_AGE_S"` → `-gt` — `FAIL tests.yml's automerge skips while a live merge train holds the record beat (executed, issue #2302) [status=('refused', False)]` and `FAIL … null controls`.
- `say skip-train-hold; exit 0` → `say skip-train-hold` (falls through to the guard) — `FAIL … skips while a live merge train holds the record beat … [status=('refused', False)]`.
- `HOLD_REF=train-hold` → `HOLD_REF=train-holds` — `FAIL … skips while a live merge train holds the record beat…`, `FAIL … null controls`, `FAIL the beat's hold ref and the train's hold ref name the same branch [beat=train-holds, train=train-hold]`.
- `if [ "$hold_age" -lt 0 ]` → `if false` — `FAIL … null controls` (a future-dated stamp then reads young).
- Drop the `&& [ "$hold_code" != 422 ]` absence arm — `FAIL … null controls` (the API's own absence code then warns on every idle beat).

The *previous* head also surfaced a test-harness defect, fixed here: `hung_run` in the heartbeat check returned `(0, (0, ""))` for any non-check-runs call (the conditional bound to the second element), which only the arming mutant reached; it now returns a proper pair, and the arming mutant reds the named check instead of crashing.

## Null control

At the merge base (`2dadcdc8cbcc2da860e5043b54d0c899038da506`) with the fix's original tests added, `python3 -I tools/audit/seat/merge_train.py --self-test` printed `merge_train self-test: 194 checks, 4 failed`:

```
FAIL a real train holds the record beat before its first merge and releases it before the closing line (issue #2302)
FAIL a train stopped mid-queue still releases the hold before its closing line (a stopped train must not block the record beat)
FAIL the hold is refreshed once per queue item, so one long item cannot age it stale
FAIL an unreadable hold commit does not stop the train: logged, no ref, no delete
```

and `PYTHONPATH=tests/hastub python3 tests/entities.py` printed `3 of 2362 ENTITY CHECKS FAILED`:

```
FAIL tests.yml's automerge skips while a live merge train holds the record beat (executed, issue #2302)  [bound=0, status='skip-unread']
FAIL and a hold at the bound, one dated ahead of the runner's clock, an absent one and an unreadable one do not skip (null controls)
FAIL the beat's hold ref and the train's hold ref name the same branch  [beat=None, train=None]
```

For the two findings this repair adds, the null control is the pre-repair head `17197336f0128a60cb454b641f15b6192ec0d715` with the repair's tests added: `merge_train self-test: 196 checks, 2 failed` (`a CI wait that outlives one poll refreshes the hold mid-wait…`, `a recarry refreshes the hold…`) and the entities null-control check red on the 422 arm. With no hold code the automerge step proceeds for every hold read, including a fresh one, i.e. it merges exactly as today; a `batch/` rehearsal publishes nothing; the unreadable-commit arm creates no ref and still merges.

## Figures

- `python3 -I tools/audit/seat/merge_train.py --self-test` → `merge_train self-test: 198 checks, 0 failed`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` → `ALL 2362 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED` (no row moved: the diff touches no `custom_components/` file).
- `python3 tests/closure.py select --diff 2dadcdc8cbcc2da860e5043b54d0c899038da506 --workdir <dir>`; `scope.txt` → `MODE: FULL -- every test script runs, nothing is scoped out.` (the diff touches `tests.yml`, a gate file), and `scope.run` is empty.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only 2dadcdc8cbcc2da860e5043b54d0c899038da506` → `claims hygiene: 2dadcdc8cbcc2da860e5043b54d0c899038da506 ok`; both claim files are byte-identical to the base.
- `PYTHONPATH=tests/hastub python3 tests/closure.py selftest` → `ALL 124 closure shrink pins PASSED`; `PYTHONPATH=tests/hastub python3 tests/layout.py` → `layout self-test: ok`.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` (a `run_always` script, under the exclusive gate lease through `tests/gate_lock.py`) → `ALL 109 HARNESS HEADER CHECKS PASSED`.
- `python3 -I tools/audit/seat/tmp_paths.py --check --ref HEAD` → `0 refused, 0 stale allow entries`.
- `printf 'not json' | gh api --method POST repos/tvofi/heatpump_optimizer/git/commits --input - --jq .sha` → `HTTP 400`, `Problems parsing JSON`: the payload travels over stdin into GitHub's JSON parser, which is what `hold_refresh()` needs.
- `printf '{}' | gh api --method POST repos/tvofi/heatpump_optimizer/git/commits --input - --jq .sha` → `HTTP 422`, `"message", "tree" weren't supplied`: the payload keys are the endpoint's.
- `gh api repos/tvofi/heatpump_optimizer/git/ref/heads/main --jq .object.sha` → a 40-hex sha: the ref route resolves (the alternative F2 repair, if the commits route is ever changed).
- `gh api repos/tvofi/heatpump_optimizer/commits/train-hold` → `HTTP 422`, `No commit found for SHA: train-hold` (measured live with no hold published): the absence code the step now treats as silent.
- The bound: `merge_train.py`'s `polls` default 24, `HEARTBEAT_SECONDS` 240, `POLL_SECONDS` 300, and a recarry's 5–15 min; the refresh sites are `one()`, `recarry()`, `wait_ci()`'s pre-sleep line, and the run's opening. Re-derive by reading those constants and call sites.
- `GH_TOKEN=$(gh auth token) PYTHONPATH=tests/hastub python3 tests/nightly_status.py --repo tvofi/heatpump_optimizer` → `NIGHTLY FAILED: slow failed last night. scheduled run 39387919507 … failing jobs: slow failure …`: the instrument reproduces the `## Red checks` red and names the lane, which is main's.
- `./tests/derive_closures.sh --single tests/entities.py` → `done tests/entities.py (exit 0)`, `closure: updated 1 closure(s)`, `tests/entities.py 335 files` (the +1 is `tools/audit/seat/merge_train.py`; the 3 files the new read set would have dropped were kept by the union). The recorded `seconds` moved 324.8 → 670.4 with the local re-derive (a Darwin box under load; a timing-only change, the closure set is what the gate reads).
- `python3 tests/closure.py selftest` → `ALL 124 closure shrink pins PASSED` after the change; `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- Box load across the local runs: `load1=83.74` at `2026-10-20T15:22:48Z` and `load1=58.08` at `2026-10-20T18:25:11Z` (`uptime`; the box is shared), so no wall-clock figure here is attributable to this change.

## Red checks

- `nightly-status` (red at the PR head; run 39493172097). It names main's scheduled run 39387919507 (`2026-10-20T07:39:11Z`, head `0c298f6`), whose `slow` job failed `tests/replay.py`: `synthetic-dhw-only.json: cycle_cost [1 offender: loop_cpu_ratio 0.1114 over its budget 0.111]`, `1 of 93 replay checks FAILED`. That is main's run, measured at 07:45Z, before this branch's first commit (`17197336f`, 16:52Z), and none of this diff's files is an input to the replay lane (the diff is the `record-autofix` job in `tests.yml`, `tools/audit/seat/merge_train.py`, `tests/entities.py`, and the closure recording). Cheaper detector: none exists for the failure itself — `loop_cpu_ratio` is a property of that runner's loop, and the slow lane's own run is the only thing that computes it; `tests/nightly_status.py --repo tvofi/heatpump_optimizer` (run here, one API read) names the lane and the run in seconds but cannot compute the ratio, so it separates "which lane" only. The fix and its proof belong to the nightly lane's owner (the orchestrator drains main's reds): re-record the fixture or re-budget `loop_cpu_ratio` in `tests/replay.py`'s own cycle-cost table (not a `*_budgets.json`; a raise is the owner's, 0013), then dispatch `tests.yml` on `main` and name that run id here, as the job itself instructs. This branch does not touch `tests/replay.py` or its recording.
- `closures` (run 39493172097, job 118884971127): `INERT READS UNDER-APPROXIMATED … tests/entities.py: tools/audit/seat/merge_train.py`. This diff makes `tests/entities.py` open `merge_train.py` — the TRAIN-HOLD block reads its `HOLD_REF` constant so the two halves cannot name different branches — and `tools/audit/` keeps `merge_train.py` INERT, which would have the merge fast path treat a change to it as unread for that script (the #357 INERT-and-recorded contradiction). **The classification moved, and why**: `merge_train.py` leaves the `tools/audit/` prefix via `tests/closure.py`'s `INERT_EXCEPT` and lands in `tests/entities.py`'s recorded closure, so an edit to the train selects that script; the recording is re-derived with `./tests/derive_closures.sh --single tests/entities.py` and merged into `tests/closures.json` in this branch. The first merge refused the pair (`closure: files on the INERT list are actually read by tests`), which is the mechanism working; after `merge_train.py` joined `INERT_EXCEPT`, `--single` exited 1 on exactly one check, `every tracked file is either measured or deliberately classified` — the chicken-and-egg `gate-scoping.md` documents — so the two-step route recorded and merged (`--record-only --out-dir`, then `merge --in-dir … --partial --allow-failures`; the raw record names `merge_train.py` in its 332 files), and a clean `--single` then exited 0 with the classification satisfied. `tests/closures.json` carries both the read and `rc: 0`. Cheaper detector: it exists and was skipped — `prepr.sh`'s closures step is the local check that records a script's reads, and this wave's `PREPR_SKIP_CLOSURES=1` ruling skipped it (the cost the ruling buys); its standing cost is one script's re-derive (~16 min here) against the gate's ~20-minute full pass.
- `closures-autofix` (job 118895327353): `AUTOFIX: skip-merge-failed — THE REPAIR DID NOT HAPPEN`, nothing pushed. It repairs only a run it may trust, and the same head's `closures` job was red; the repair is the same recorded read, committed here, so no autofix is owed once the check re-runs.
- `pr-contract` (run 39493177280): red because this body's previous `## Red checks` did not name `nightly-status`; this body names it and the closures pair, and the check re-runs at the new head. Step-11 timing does not apply — the missing text was the body's own, not a check reading an artifact it does not name.

## Forward-carry

`none`

## Friction

`none`.

## Approval

Code-owned path (`.github/workflows/`); this pull request needs tvofi's approving review. Approving it approves one behaviour change: **while a merge train is live, the record beat does not auto-merge a record pull request.** It is off when no train runs (no ref), off after a train's closing line (the ref is deleted), and off after 1 h without a refresh (a crashed train). No `VERSION`, manifest version, `RELEASE_NOTES.md` heading, golden fixture or claim file changes; `record_row.py` is untouched, so the guard that decides what may auto-merge is the same predicate as before — only *when* it runs changes.

The rollback is a two-file revert (`git revert` of this merge): the beat's default (no ref read) is the pre-change behaviour, and the train's `hold_refresh`/`hold_release` calls go with it. If a ref is left behind, it is inert once 1 h old and can be deleted with `gh api -X DELETE repos/tvofi/heatpump_optimizer/git/refs/heads/train-hold`.

Known residual, stated for the review: a record pull request whose only trigger (a `main` push from the train, or the nightly) falls inside a hold lands at the next trigger after the hold ends, not immediately. `OVERDUE` is commit-based (`STALE_AFTER_COMMITS` 12) and a held beat follows at most one train's merges, so this is a delay, not a red. Carry: dismissed: bounded delivery delay, no downstream action.

Known seam, recorded not fixed: the hold ref is one global name while a train's liveness is per state directory, so two trains running at once share the ref and whichever ends first deletes it, unholding the other. One orchestrator runs one train at a time; a per-run ref name would need the beat to discover it, and a tip-ownership check in `hold_release` would avoid the unhold and is the option to take if concurrent trains ever become real. Until then the overlap degrades to today's behaviour (a record PR may land mid-train), never to corruption. Carry: dismissed: concurrent trains are not a supported state; the unhold degrades to the pre-fix behaviour.
