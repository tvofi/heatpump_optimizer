Main's `tests / ci-ratchet` (and so `gate`) has refused on every push to main since `d5dc3e26a` (CI runs 40052726602, 40053766565, 40053884407, 40064461053, 40064549797). The job logs show two separate causes. This PR fixes both, in `tests/ci_ratchet.py` alone (plus one stub in `tests/entities.py`).

1. **The grade's push-run window keyed on the run's title (the persistent red).** `run_minutes` and `gather_runs` treated a run as an umbrella run when `.name == "CI"`. The API's `.name` is the run's display title, and ci.yml's `run-name:` makes it `CI code pr=- base=- sha=<sha>`. So every umbrella run read as some other workflow's run. While the newest `PUSH_WINDOW` (8) push runs still included pre-umbrella `Tests` runs, those carried the median. From `d5dc3e26a` on, the newest 8 are all umbrella runs (`gh api 'repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?event=push&branch=main&per_page=8'`). That leaves no measurable run, and the grade step refuses with `no completed push CI or Tests runs in runs.json; cannot derive critical_path_minutes (fail closed)`: CI jobs 120791448344, 120790459972 and 120758947611. In each of those runs the artifacts fetch was rescued by its retry (`window: 43` / `window: 42` in the log). A run's kind is now its workflow file: `run_kind(r)` reads `.path`, which `run-name:` does not rewrite, and strips a ref suffix. A missing or foreign path is not in the window, as before.
2. **The repo-wide artifacts listing.** `GET actions/artifacts?per_page=100` returns 0 bytes (`unexpected end of JSON input`) intermittently. It failed 4 of 4 attempts in CI job 120763639214 (run 40053884407) and 1 of 5 single attempts from this seat (`## Figures`). The name-filtered listing answers. `fetch_window` (resumed from the s5 seat's `e7b73728a`) reads `ci-metrics-<lane>` per lane in `WINDOW_LANES`, with retries per lane, and refuses per lane once its attempts are spent. Three things are added on top of `e7b73728a`:
   - **Each lane keeps its own newest `WINDOW_PER_LANE` (15) runs** (`window_entries(..., per_name=)`). The union cut in `(run, name)` order kept the union's lowest run ids. When this run's own copy is not listed, that cut dropped each lane's newest run.
   - **The listing page is `WINDOW_FETCH_PER_LANE = 2 * WINDOW_PER_LANE`** per lane. This run's own copy, and a re-run's second copy of one (run, lane), therefore never shorten the window.
   - **A lane listing that carries another artifact name refuses.** That means the server ignored `name=`. Read as a window, it would triple-count one mixed listing, or grade on a short one.

**What the window now selects, against the old read.** The old window was whatever `ci-metrics-*` artifacts the newest 100 artifacts **of any name** held, so its size and lane balance depended on unrelated uploads. Live at `2026-10-24T07:47Z`: 42 entries, closures 18 / coverage 10 / fast 14. The new window is what tests.yml's gather-step comment has always said it is: the newest copy per lane per run of each lane's newest 15 runs that are not this one. Live at the same time: 45 entries, 15 / 15 / 15, with this run excluded. The rest is unchanged and still pinned by the existing self-test arms: dedupe on (run, name) keeping the newest copy, undated copies sorting last, expired / other-name / this-run exclusion, the `.run_id` fallback, and the `(run, name)` output order.

## Head

`078fb5a71f52fdf64c23df78cf4181cc6a7bc6ef`. Merge base and origin/main tip `50af6174f53c0f9bec3f705c3a4bb99615f71acc` (merged into the branch at `27b0cf4a3`; checked 2026-10-24T10:16Z). Everything below was measured at this head, except the base arms, which load `git show 50af6174f:tests/ci_ratchet.py`.

## Mutation proof

Each mutant is the head's `tests/ci_ratchet.py` with one predicate changed, run as a copy with `--self-test`. The harness is `/Users/timmalmstrom/hpo-seats/r10s6/fix-ci-ratchet/mutate.py` (seat-local, cited for the commands; its output is reproduced here).

| # | mutant | checks that go red |
|---|---|---|
| M0 | none (null) | `31 checks, 0 failed` |
| M1 | `_lane_listing`'s `if stray:` -> `if False:` | `a lane listing carrying another name refuses (the filter was ignored)` |
| M2 | `window_entries`'s `if per_name is not None:` -> `if False:` | `each lane keeps its newest WINDOW_PER_LANE runs, not the union's oldest` (fast keeps runs 1-15, want 2-16) |
| M3 | the (run, name) dedupe `if key in seen: continue` deleted | 7, among them `one listing read three times still counts each (run, name) once` and `a duplicate (run, name) keeps the newest copy` |
| M4 | `run_kind` keyed on `.name` (the base's rule) | 8, among them `an all-umbrella window, titled `CI code ...` by run-name, is measured by workflow path (34.5)` (`no completed push CI or Tests runs`) and `a ci.yml run is kind CI whatever its title, a ref suffix included` |
| M5 | a lane's spent attempts `continue` instead of refusing | 3, among them `one lane's spent attempts refuse naming that lane (not a two-lane window)` |
| M6 | `ARTIFACTS_URL` back to the repo-wide `actions/artifacts?per_page=100` | 6, among them `the window is each lane's name-filtered listing, one call per lane, no retry` |

Failing test first, base against head under identical stubs (`/Users/timmalmstrom/hpo-seats/r10s6/fix-ci-ratchet/ftf.py`):
- (A) The repo-wide URL answers rc 1 with 0 bytes and `unexpected end of JSON input`; the name-filtered URL answers. Base: `REFUSED: ci-ratchet: the artifacts fetch failed after 4 attempt(s): gh exited 1 after 0 byte(s): unexpected end of JSON input`. Head: `window 9 entries`.
- (B) A runs.json of 8 completed umbrella runs titled `CI code pr=- base=- sha=...`. Base: `REFUSED: ci-ratchet: no completed push CI or Tests runs in runs.json; cannot derive critical_path_minutes (fail closed)`. Head: `critical_path_minutes 34.5`.

## Null control

- M0 above: the unmutated head passes all 31 self-test checks.
- `and the same listing, name-filtered, is a window (the null control)` is the null for M1's refusal: the same `good` listing, served name-filtered, yields `[7, 3, 1]`.
- `a pre-umbrella Tests push run is measured as before: created to updated (the null: 50)` and `a window across the cut-over is the median of both kinds (45)` still pass. They show the path key leaves pre-umbrella runs as they were.
- `tests/entities.py`'s `and a good response still yields the same window (the null control)` passes (`ok` in the scoped gate log).

## Figures

Seat interpreter `seat-python3` (Python 3.14, `tools/audit/seat/shims`).

- `seat-python3 -I tests/ci_ratchet.py --self-test`: `ci-ratchet self-test: 31 checks, 0 failed`. The merge base has `23 checks, 0 failed`.
- Live, read-only, `fetch_window('tvofi/heatpump_optimizer', '40064549797')` at 2026-10-24T07:47Z. Head: `entries 45 {'ci-metrics-closures': 15, 'ci-metrics-coverage': 15, 'ci-metrics-fast': 15}`. Base (repo-wide), same minute: `entries 42 {'ci-metrics-closures': 18, 'ci-metrics-coverage': 10, 'ci-metrics-fast': 14}`. Base, five single-attempt calls in a row (`attempts=1`): 4 answered and 1 `REFUSED: ... gh exited 1 after 0 by[tes]`. A per_page=100 repo-wide `gh api` at 07:45Z returned `rc=1 bytes=0 secs=8 unexpected end of JSON input`, and an earlier one in the same minute answered 69883 bytes. The fault is intermittent from here; in CI it was 4 of 4 in job 120763639214.
- Live `gather_runs` then `critical_path_minutes` at 07:49Z. Head: `push runs: 8 (8 CI)`, `critical_path_minutes 32.683`. Base on the same runs.json: `REFUSED: ci-ratchet: no completed push CI or Tests runs in runs.json`.
- End-to-end grade, live, head code, standing in for CI's ci-ratchet job at run 40064549797. That job's three `gh run download --name ci-metrics-<lane>` calls, then `GITHUB_RUN_ID=40064549797 seat-python3 -I tests/ci_ratchet.py --gather --metrics-dir <M>` (`window: 45 ci-metrics artifact(s)`, 0 expired skipped), then `seat-python3 tests/ci_ratchet.py --metrics-dir <M> --runs-json <runs>`: `ci-ratchet: every metric at or under its budget`, rc 0. That includes `critical_path_minutes: 32.68333333333334 (budget 54.825)` and `script_runs_per_push: 54 (budget 54)`. The archscore rows were measured on this seat's tree; this diff touches no file they read.
- Seam census for the run-name class: `git grep -n -E '(\["name"\]|\.get\("name"\)|\.name)\s*(==|!=|in)\s*\(?"(CI|Tests)"|select\(\.name ?== ?"(CI|Tests)"\)|workflowName|--workflow[= ](CI|Tests)\b' -- . ':!dev/audit/rounds' ':!tests/ci_ratchet.py'` returns one seam, `tools/ci/ruleset_cutover.py:187`. That seam keys on `r.get("path") in MAIN_RUN_PATHS` first and on `name == "Tests"` only as a fallback. `tests.yml` has no `run-name:`, so it is already guarded. Inside `tests/ci_ratchet.py`, the four `.name` sites (`run_minutes` twice, `gather_runs` twice) all read `run_kind` now.
- Callers of the changed symbols: `git grep -n -E 'fetch_window|window_entries|ARTIFACTS_URL|WINDOW_LIMIT|WINDOW_LANES|WINDOW_PER_LANE|_listing\(' -- . ':!dev/audit/rounds' ':!tests/ci_ratchet.py'`. It returns `tests/entities.py` (the `_CIR_*` block; its retry stub now answers per lane as the server does) and a comment in `.github/workflows/tests.yml` (unchanged: it names `window_entries` as the owner of the selection, which still holds). The other hits are `pr_from_listing` in `tools/pr/*.sh` (unrelated) and round-9/10 `fetch_window.py` harness files (unrelated scripts of the same name).
- Scoped gate: `seat-python3 tests/closure.py select --diff 50af6174f` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (`tests/entities.py`, `tests/harness_headers.py`). Then `GATE_SCOPE=auto PREPR_SKIP_CLOSURES=1 PYTHONPATH=tests/hastub bash tests/run.sh`:
  - `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `tests/entities.py`: `5 of 2425 ENTITY CHECKS FAILED`. Every `the CI ratchet ...` check reads `ok`. The failures are `the lease has one winner, a dead gate is stolen, a live one is not, and run.sh runs unleased` (gate_lock) and the heartbeat-control checks `and a try whose sample misses the spin ... is retried`, `the control rests between tries ... (two tries took 0.81s against a 1.0s rest)`, `the control survives two hung samples` and one `hb:` check. All are wall-clock checks of subjects this diff does not touch, run under host load (1/5/15-min load averages 7.56 / 24.90 / 55.03 at the end). They were not re-run at the merge base here; CI's `fast` runs `tests/entities.py` on this PR.
- `seat-python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `seat-python3 -I tests/layout.py --guard --base 50af6174f`: `layout: GUARD: 0 refusal(s) against 50af6174f53c`.
- `seat-python3 -I tools/audit/seat/ref_privacy.py guard --ref handoff/r10-ci-ratchet-artifacts --commits HEAD --over origin/main`: rc 0.

## Red checks

- `tests / ci-ratchet` and `gate` on main's push runs from `d5dc3e26a` (the subject of this PR; jobs above). Root-cause trigger (`defect-root-cause.md`), per cause:
  - **(1) run-name / `.name` key: a cheaper detector existed in shape and was blind.** `--self-test` runs in about 1 s on every PR that touches `tests/ci_ratchet.py` (its own CI step, and `tests/entities.py` pins it). Its push-run stubs named an umbrella run `"CI"`. The API never returns that title while ci.yml has `run-name:`. So the stub pinned the stub, not the API, which is `fixer.md` step 13's class applied to an API fixture. The defect was latent from P2b (`85d13b859` / `9262e6f43`, 2026-10-22) until the eighth umbrella push run pushed the last `Tests` run out of the window. The countermeasure in this diff is the self-test arm built on the real title shape (`an all-umbrella window, titled `CI code ...` by run-name ...`; M4 kills it). Process state and whether a wider countermeasure pays (stubs derived from a recorded API response) are owed to a root-cause seat, requested from the orchestrator (`SEAT-OWED root-cause`).
  - **(2) repo-wide artifacts listing: none exists.** This is an external API regression: the server times out the unfiltered listing. No check in the tree can see it before a live call. The retry and the per-lane refusal make it a named refusal rather than a traceback.

## Forward-carry

none

## Friction

- brief-diagnosis: unclear: the dispatch brief diagnosed the red as the artifacts listing alone, but the job logs of 4 of the 5 red runs show the fetch rescued by its retry and the grade refusing on `runs.json`. This was found by reading the failing step's log rather than the job's first error line. Carry: dismissed: diagnosis corrected and both causes fixed in this PR; reported to the orchestrator in to-main.txt.

## Unpinned sites

The new predicates (`_lane_listing`'s stray-name refusal, `window_entries`' `per_name` cap, `run_kind`'s path key, the per-lane refusal) are each killed by a named self-test check (`## Mutation proof`, M1-M6). They are in `tests/ci_ratchet.py`, a NOT_A_TEST script outside the production mutation ledger. This is a written triage, not a ledger pin.
