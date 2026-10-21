The record beat in `.github/workflows/tests.yml` auto-merges record pull requests on its own schedule, so a record pull request can land while a merge train is waiting on CI and move `main` under it: #2291, #2295 and #2299 each merged mid-train on 2026-10-15, stopping or re-carrying #2284 and #2290. CI cannot see the train's local pidfile. This makes the train publish a ref while a real run is live, and makes the record beat's automerge step skip while that ref is younger than its bound.

**The train half** (`tools/audit/seat/merge_train.py`). A real run (`base: main`; a `batch/` rehearsal merges nothing into `main` and publishes nothing) arms the hold and calls `hold_refresh()` before anything can merge; it refreshes at the start of every queue item (`one()`), before every recarry (`recarry()`, where a recarry begins inside `app_push`'s prepr), and before every sleep inside `wait_ci()`. `hold_release()` runs before the closing line on every path (`TRAIN DONE`, `TRAIN STOPPED`, and a `finally` backstop). The ref is `refs/heads/train-hold`, pointing at a commit created at publication through the API (`POST /git/commits`, then `POST /git/refs`, or `PATCH` for a refresh or to adopt a stale ref a crashed train left), so its committer date is the publication time the beat reads as the hold's age. It is created through the API and never `git push`, because the API starts no push-triggered run. A refused hold is logged `NOT held: …` and the train runs on: the hold guards a bookkeeping beat, and stopping a merge train for it is the worse failure. Only a train or batch arms the ref; the bare `wait-ci` subcommand never publishes one, because it has no closing line to release it.

**The beat half** (`.github/workflows/tests.yml`, automerge step). After the step's token masks and before it reads the pull request's head, it reads `GET /repos/{repo}/commits/train-hold` and computes the age of `commit.committer.date`. Younger than `HOLD_MAX_AGE_S` is a live train: `say skip-train-hold; exit 0`, leaving the open record pull request for a later beat. At or past the bound is stale (a crashed train moved nothing, so no rows went overdue — `STALE_AFTER_COMMITS` is commit-based). A date ahead of the runner's clock is unknowable, never young (#775), and is treated as stale. The endpoint answers **422** `No commit found for SHA: train-hold` for an absent ref (measured live 2026-10-20), not 404, so both 404 and 422 are the silent absence and the pre-fix behaviour; any other code is logged and treated as absent. `record_row.py --automerge-check` is untouched.

**Why the bound prices a refresh gap, not a wait.** The longest gap between two refreshes is one phase, not one wait: a recarry (5–15 min inside `app_push`'s prepr, and `--overlap` runs one per serial entry before any wait), one poll of `min(POLL_SECONDS, HEARTBEAT_SECONDS)` = 240 s, or a queue item's work between the per-item refresh and its first wait (a `land`: preflight plus at most `merge_tries` 8 × 30 s). Every long wait — a serial CI wait, a `--batch` proof, a re-proof, a `main_green` read — goes through `wait_ci`, so it refreshes from the wait loop; every up-front `--overlap` recarry goes through `recarry()`. `HOLD_MAX_AGE_S=3600` is above the longest named phase (a 15-minute recarry) by more than 3× and does not depend on how many waits a run contains; a crashed train unholds records within 1 h, and its rows are late, not overdue.

What the owner is approving, the rollback and the recorded seams are under `## Approval`.

Fixes #2302.

## Head

`0c216ecc288ef47243bb0fde13ea0c97a17c1df9` merges origin/main `10d423c28` into the authored code head `ddfbf8ac730f5e9b2c6e5ca1bc142fff4e764cd0` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`ddfbf8ac730f5e9b2c6e5ca1bc142fff4e764cd0`

## Mutation proof

Train half, `python3 -I tools/audit/seat/merge_train.py --self-test` (each mutant applied, the suite run, the line restored; the restored file re-runs at 197/197):

- Delete the start-of-run `hold_refresh()` (the arming stays) — the per-item refresh still creates the ref, so the counts shift and T1 reds these two, **not** the first-merge check: `FAIL the hold is refreshed once per queue item, so one long item cannot age it stale` and `FAIL a recarry refreshes the hold, so --overlap's up-front recarry loop cannot age it`.
- Delete the `hold_release()` before `TRAIN DONE` so only the `finally` releases — `FAIL a real train holds the record beat before its first merge and releases it before the closing line (issue #2302)`.
- Widen the arming guard back to `if not self.real: return` — `FAIL a bare wait-ci publishes no hold: only a train or batch arms the ref`.
- Delete the per-item `hold_refresh()` in `one()` — `FAIL the hold is refreshed once per queue item…` and `FAIL a recarry refreshes the hold…`.
- Change `if code or not is_sha(sha):` to `if code:` — `FAIL an unreadable hold commit does not stop the train: logged, no ref, no delete`.
- Delete the `hold_refresh()` inside `wait_ci()` — `FAIL a CI wait that outlives one poll refreshes the hold mid-wait, so the bound can be shorter than a wait`.
- Delete the `hold_refresh()` before a recarry — `FAIL a recarry refreshes the hold, so --overlap's up-front recarry loop cannot age it`.

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

- `python3 -I tools/audit/seat/merge_train.py --self-test` → `merge_train self-test: 197 checks, 0 failed`.
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
- Box load across the local runs: `load1=83.74` at `2026-10-20T15:22:48Z` and `load1=58.08` at `2026-10-20T18:25:11Z` (`uptime`; the box is shared), so no wall-clock figure here is attributable to this change.

## Red checks

`none` at handoff: the branch's checks are CI's to run (the diff is a gate file, so every scoped/test lane runs).

## Forward-carry

`none`

## Friction

`none`.

## Approval

Code-owned path (`.github/workflows/`); this pull request needs tvofi's approving review. Approving it approves one behaviour change: **while a merge train is live, the record beat does not auto-merge a record pull request.** It is off when no train runs (no ref), off after a train's closing line (the ref is deleted), and off after 1 h without a refresh (a crashed train). No `VERSION`, manifest version, `RELEASE_NOTES.md` heading, golden fixture or claim file changes; `record_row.py` is untouched, so the guard that decides what may auto-merge is the same predicate as before — only *when* it runs changes.

The rollback is a two-file revert (`git revert` of this merge): the beat's default (no ref read) is the pre-change behaviour, and the train's `hold_refresh`/`hold_release` calls go with it. If a ref is left behind, it is inert once 1 h old and can be deleted with `gh api -X DELETE repos/tvofi/heatpump_optimizer/git/refs/heads/train-hold`.

Known residual, stated for the review: a record pull request whose only trigger (a `main` push from the train, or the nightly) falls inside a hold lands at the next trigger after the hold ends, not immediately. `OVERDUE` is commit-based (`STALE_AFTER_COMMITS` 12) and a held beat follows at most one train's merges, so this is a delay, not a red. Carry: dismissed: bounded delivery delay, no downstream action.

Known seam, recorded not fixed: the hold ref is one global name while a train's liveness is per state directory, so two trains running at once share the ref and whichever ends first deletes it, unholding the other. One orchestrator runs one train at a time; a per-run ref name would need the beat to discover it, and a tip-ownership check in `hold_release` would avoid the unhold and is the option to take if concurrent trains ever become real. Until then the overlap degrades to today's behaviour (a record PR may land mid-train), never to corruption. Carry: dismissed: concurrent trains are not a supported state; the unhold degrades to the pre-fix behaviour.

