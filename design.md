# Design: R11-CI-3885-QUEUE (#3885, owner-directed 2026-11-25)

This is the architect note, extended per `dev/governance/roles/designer.md`.
- Base: `origin/main` 91f6e91bea926777d03fc23de1c21e5247abf290.
- Predecessor: none. The fast-lane sharding fixer (`fix/r11-ci-fast-shards`) had no ref pushed when this was read. This note never touches `tests / fast` sharding.
- This ref carries no production code.
- Harness: `dev/audit/harnesses/ci3885_queue.py`, which is on this ref and lands with the first PR. `fetch DAY` caches every run and every job attempt. `report DAY` answers every arm from that cache.
- Figures are for 2026-11-25, the busy day (288 CI runs). The null control is 2026-11-24 (6 CI runs).

## 1. What the measurement says (this changes the brief's premise)

**The cited 65 minutes held no runner.** On main run 45683745493, the run was created at 19:17:40. Its first job was *created* at 20:22:41 and started at 20:22:44, so it queued for a runner for 3 s. The 65 minutes were the `CI-main` concurrency group (CI-5) holding the run pending behind the previous main run.

The harness `decompose_p50_p90` arm splits a run's wall-clock time into three parts:
- **pending:** run created to first job created. A concurrency group causes this, and no runner is held.
- **queue:** the longest job's wait from created to started. This is the runner cap.
- **longest job:** the run time of the run's longest job.

| run kind (n) | pending p50/p90 | queue p50/p90 | longest job p50/p90 | e2e p50/p90 |
|---|---|---|---|---|
| PR code (56) | 0/0 | 10/56 | 60/136 | 106/194 |
| PR edit (105) | 0/0 | 6/36 | 2/2 | 14/66 |
| review (28) | 0/0 | 5/30 | 1/2 | 12/76 |
| push main (11) | 27/65 | 2/26 | 100/120 | 131/203 |
| null 11-24, PR code (1) | 0 | 0 | 18 | 22 |

**Daily load.** Demand was about 39.3k runner-min.
- CI: 37,713 runner-min, after dropping 1,341 copied re-run listings (see L7).
- Nightly: 1,225.
- Gate sweep: 204.
- Pages: 58.

**Slots.** The observed peak was 62 concurrent jobs. Mean concurrency was 41-46 over 11-16Z. The runner-queue p90 was 36-47 min in those hours and about 0 overnight. On the 11-24 null day the queue p90 was 0.1 min.

**Consequence.** Even with a zero queue, a PR code run's p50 is 60 min, and that is its longest job (`tests / mutation`, `closures`, `fast`, `coverage`). Main's FULL run is 100-120 min plus up to one previous run pending. The ≤40-min target is reachable only if the sharding fixer brings the longest job under about 30 min. The levers below cut the queue term, which is p90 56 min on PR code runs.

## 2. Owning seam

Every lever is CI machinery outside the package. `tests/seam_map.json` maps package seams only. There is one owner per concern:
- `.github/workflows/ci.yml` owns the triggers and concurrency.
- `tools/ci/prelude.py` owns waits before units.
- `tools/ci/sweep.py` owns re-judging after a completion.
- `tools/pr/cancel_superseded.py` and `tools/audit/seat/merge_train.py` own re-run calls.

`tests/entities.py` only pins these. No concern needs two owners.

## 3. Levers, ranked by runner-min saved per effort

The base for every figure is 11-25. Each lever ships as its own small PR, and every ci.yml change carries its `tests/entities.py` pin.

| # | lever | measured cost today | expected saving | effort |
|---|---|---|---|---|
| L1 | supersede at creation | 655 runner-min ran after a newer head's run existed; 106 jobs started after it (null, same-head code twins: 1/1) | ~650 runner-min/day; slots freed at creation instead of after `cancel-superseded` waits its own queue (p90 24 min) | S |
| L2 | stop duplicate verified dispatches (carry 1) | `ci3885_light.py dup`: 6 runs, 2,252 runner-min (null 11-24: 0/0); sole graders 6/1,140 | ≤1,214 runner-min/day: `stalepin` attributes all 6 to `sweep.py` STALE-PIN, and this tree's `code_red` already leaves 3 (1,038) | M |
| L3 | no runner held while waiting (owner rule, §4) | wait-bearing jobs: excess over their own p10 floor is about 570 runner-min (NULL `typing` reads 165, so that is noise) | about 400-570 runner-min/day; edit/review e2e p90 (66/76) bounded by the decider rather than by a slot | M |
| L4 | record-branch runs | 16 runs, 456 runner-min (null 11-24: 4 runs, 93) | ≤456 runner-min/day | S |
| L5 | fold `refresh` into the `cancel-superseded` job | 329 + 143 runner-min over 254 + about 150 jobs | about 150-200 runner-min/day (one allocation and checkout fewer per PR event) | S |
| L6 | cheaper Gate sweep: (a) dropped at revise 1; (b) coalescing, design only | 408 runs, 403 jobs, 204 runner-min, queue p90 48 min | ≤204 runner-min/day, (b) only; its value is re-judge latency (p90 48 min) | M (b), not built here |
| L7 | failed-only re-runs | re-executed jobs that had succeeded before: 4 jobs, 5 runner-min (null attempt-1: 0; `--keep-copies` perturbation reads the 1,307/6,636 copies) | ≤5 runner-min/day | S |

### L1. Supersede at creation

**Shape.** In `ci.yml` `concurrency`, `group` becomes `CI-pr-<number>` when all of these hold:
- the event is `pull_request`;
- the action is `synchronize`;
- the run attempt is 1;
- the sender is not `github-actions[bot]`.

In that case `cancel-in-progress` is true. Every other run keeps its run-id group. That includes every push to main, once `handoff/r11-ci-3885-ci5-drop` removes the `CI-main` group (see §6). L1 is written against that tree.

The same PR rewrites the comment at `.github/workflows/ci.yml:66-68` ("Supersession is cancel-superseded's alone") and the `tests/entities.py` concurrency pin, which today refuses any `cancel-in-progress` (`concurrency ... cancels in progress`). The new pin has one row per event, action, attempt and sender, and keeps push and re-runs in run-id groups.

**Why it is safe.**
- A `synchronize` run always heads a new SHA, so the same-SHA twin rule (R9-CI-2a) holds.
- Re-runs keep the run-id group, so a re-run never cancels a pending run (the reason for rev2 N1).
- Bot heads stay exempt.
- `cancel_superseded.py` stays as the fallback for opened, reopened and dispatched runs.

**Test.**
- `tests/entities.py` concurrency pin, with one row per event, action, attempt and sender.
- A mutant that drops `synchronize` from the expression must fail the pin.
- After merge, the harness `supersede` arm on a busy day reads about 0 for synchronize pairs. The `supersede_null_same_head_code` arm must stay at 0-1.

**Risk.** A `synchronize` run whose gate a sweep is polling gets cancelled. Its gate is for a superseded head and no reader reads it.

### L2. Duplicate verified dispatches (carry 1)

All 11 of the day's PR-naming dispatches had `github-actions[bot]` as actor. That makes the dispatcher either `sweep.py` STALE-PIN or a `tests.yml` autofix. `ci3885_light.py stalepin 2026-11-25` attributes all 6 duplicates to STALE-PIN and none elsewhere (unattributed 0). This tree's `code_red` leaves 3 of them and still dispatches 3 (1,214 runner-min, each with `tests / fast` red or cancelled at the head). The carry's brief is followed as written:
1. Narrow STALE-PIN at its source, in `sweep.py` (for example, no dispatch while a code-unit job at the head is still running or was cancelled), with a `sweep_selftest.py` row per case.
2. Compare unit sets before counting.

Reusing another run's verdict in `gate.py` is a trust-model change. It stays out of this group unless step 1 finds the dispatch necessary.

### L4. Record branches

The `record/*` PR runs stay graded, because `gate` is required. Extend the `prelude.light` stand-down so that a changed list held wholly under the record paths stands down every lane whose closure it cannot reach. The fixer reads `tests/closures.json`. `gate` judges a stood-down unit as it does today.

**Test.** A prelude self-test row with a record-only list, and a null row adding one product file.

### L5. One housekeeping job

`refresh` and `cancel-superseded` need the same grant (`actions: write`, `pull-requests: read`) and both act at the event. Make them two steps of one job, keeping their order and conditions. `refresh` keeps running on review events.

**Test.** The entities caller-set pin, plus a run that shows both steps' lines.

### L6. Gate sweep

(a) **Dropped** (design review, revise 1). A `workflow_run.conclusion != 'cancelled'` skip would also drop `settle` (`tools/ci/sweep.py` `settle`). `settle` acts on a decider that ended red or cancelled at the live head, for example a cancel by hand, or a priority-held run that `cancel_superseded.py` drops unrun after `HELD_MAX_AGE_S`. The gates that deferred to that decider would stay red until a new event.

The narrower skip (a cancelled V whose head is no longer the PR's head) cannot be decided in a job `if:`. `workflow_run.pull_requests[].head.sha` is not the live head, so deciding it needs the runner the skip was meant to save. Every completed CI run therefore keeps its sweep, including runs L1 cancels. That is the hook W1 relies on (§4).

(b) Coalescing. A `sweep-<workflow_run.head_sha>` group with `cancel-in-progress: false` would let GitHub replace pending sweeps at one head. That needs `sweep.py` to judge from the head's state (the newest green covering gate) instead of from V, which changes R4-4. It is a separate design-review item and is not built in this group. The coalescable count is unmeasured, because a sweep run's `head_sha` is main's. The fixer reads the trigger id from the first log line.

No hosted runner is avoidable. A `workflow_run` job needs one, and a self-hosted runner is a runner the owner ruled out.

### L7. Re-runs

Re-runs are already job-scoped: `ci_rerun.py`, `ci_pause.py`, and the gate re-runs in `gate.py` and `sweep.py`. Two whole-run `POST .../rerun` calls remain:
- `merge_train.py` `unstale`;
- `cancel_superseded.py` priority re-run.

Both become `rerun-failed-jobs`, which also re-runs cancelled jobs. Each file's self-test gets a fixture row.

## 4. Waits while a runner is held (owner requirement, 2026-11-25)

Inventory: `grep -n "sleep\|POLL\|WAIT_MAX" tools/ci/*.py .github/workflows/*.yml`. Runner-min are the harness `waits` arm for 11-25. Each value is the job's total, with the excess over that job's own p10 floor in brackets. The null rows (`hassfest`, `validate`, `typing`) read 9, 17 and 165 excess.

| wait | bound today | runner-min (excess) | replacement holding no runner | cap kept |
|---|---|---|---|---|
| W1 `prelude.wait_sources` (edit run beside a code run whose pr-contract started) | 8,700 s | prelude 486 (300); edit max 19 min; review p90 28, max 97 | Read once. If busy, the prelude step `Defer: sources still running` fails at once and names the runs. On a decider's completion, whether it concluded success, failure or cancelled (no sweep skip exists; L6a dropped), `sweep.py` takes each run at the head whose prelude failed on that step and which is no longer busy. It routes each one through the stale-pin rule (`stale_pin`, then `fresh`): a pin where the base has changed `tools/ci/*.py` gets ONE `STALE-PIN` dispatch and no re-run; a current pin gets `rerun-failed-jobs`, which replays the same event at the same head and re-runs prelude, pr-contract and gate. | `ATTEMPT_CAP` 45; an API error or rate limit fails closed (prelude red, so gate red); acyclic because code runs never wait (`waits_on`) |
| W1, API vs sleep (#3885 ask) | — | each poll does 1 run listing plus 2 job reads per busy run, then sleeps `POLL_S` 60 s, so sleep is ≥95% by construction | the replacement removes the sleep; the fixer prints per-poll API seconds from step timestamps | — |
| W2 sweep/sweep-self poll and settle | 600 s | 204 (124) + 39 (11) | Symmetric completion arm: the sweep of a run whose gate completed red re-runs that gate when another run at the head holds a green gate covering the newest event. The polled run's own completion then does what the poll did. Settle polls are removed the same way. | once per source change (`settled`); `ATTEMPT_CAP` |
| W3 gate own-jobs listing lag | 120 s absent / 720 s | 368 (85), 1 job >5 min | **Irreducible**: GitHub lists a job about 20 s late (41289450679). Cap: lower `GATE_WAIT_MAX_S` to `GATE_ABSENT_MAX_S` (120 s) once W1 removes every source wait. | 120 s |
| W4 `codescan_wait` in pr-contract | 600 s | 156 (37) | **Irreducible**: no workflow trigger fires when a code-scanning analysis is processed. | 600 s |
| W5 autofix and merge-main approval polls | 60 s | in tests/merge-main totals | **Irreducible**: a held run is listed with lag. | 60 s |
| W6 hassfest docker pull; ghapi 5xx backoff | 30 s; 8 s | transient only | **Irreducible**: retry after an infrastructure fault. | as now |
| `needs:` chains, CI-main pending | — | 0 | Not a wait on a runner. A job is created when its needs end (`coverage-ratchet` created 20:51:44, the moment `coverage` completed). | — |

`governance` `bg_wait` waits on the job's own background steps, so it is not an external wait.

**Tests.**
- W1: `prelude.py --self-test` rows. A busy head returns the defer reason with no sleep. The null row, an idle head, returns `''`.
- W1: `sweep_selftest.py` rows. The deferred run is re-run once per decider completion and never past `ATTEMPT_CAP`.
- W1 stale pin: a deferred run whose base pin predates a `tools/ci/*.py` change on the base gets one `workflow_dispatch` POST and no `rerun-failed-jobs`. Its null row is the same run at a current pin, which gets the `rerun-failed-jobs` POST and no dispatch.
- W1 cancelled decider: a decider cancelled at the live head still triggers the W1 re-run of the run that deferred to it. Beside it, the existing `settle` row stays green: a decider cancelled at the live head still has the gate that deferred to it re-run.
- W2: the existing poll rows become completion rows, with the same POST set.

## 5. Order, PRs, hot files

**Ship order:** L1 (after `handoff/r11-ci-3885-ci5-drop` merges, since both edit `ci.yml` `concurrency`), L7, L5 and L4, as four small separate PRs. L2 next. Then L3 W1+W2, one PR touching `tools/ci/prelude.py`, `sweep.py` and `sweep_selftest.py`.

**Hot files:** `ci.yml` and `tests/entities.py` (the CI-5 drop, then L1, then L5, serially) and `tools/ci/sweep.py` (L2, then L3).

The sharding fixer owns `tests.yml`, and none of these levers edits it.

The carries in `dev/programme/carries/carry-3885.json` are owed here:
- Carry 1 is L2.
- Carry 2 (env_drift cache after a light push) is measured by its remeasure clause in the L4 PR, because both read `prelude.light`.

## Notes for the fixer

- Gate-sweep runs report main's `head_sha`. Attribute a sweep by the trigger id in its log, never by the run object.
  Carry: R11-CI-3885-QUEUE (item sweep-head)
- Long review preludes after c0dcc352f9 (2026-11-25T00:21Z) are consistent with PR base pins that predate it. Check each run's `base.sha` before counting it against W1.
  Carry: R11-CI-3885-QUEUE (item stale-pin-preludes)
- L1 rewrites the `ci.yml:66-68` comment and its `tests/entities.py` pin in the same PR.
  Carry: R11-CI-3885-QUEUE (item l1-comment)
- A one-job re-run lists every job again under the new attempt. Count a job as executed only when its timestamps differ from the previous attempt's.
  Carry: R11-CI-3885-QUEUE (item rerun-copies)

## 6. CI-5 (settled)

The owner has made CI-5 obsolete. `handoff/r11-ci-3885-ci5-drop` removes the `CI-main` group, so main push runs are no longer serialized. The pending term in §1 (p50 27 / p90 65 min) goes away, and every main push is graded at its own tip.

No lever here assumes serialization:
- L1's group applies to `pull_request synchronize` only. Push runs keep run-id groups.
- `cancel_superseded.py` never touches main except through its by-hand `main` mode.
- `gate-sweep.yml` already skips push runs.
- L4 and L5 act on PR events.
- L2 and W1 key on a PR head.

What changes is main's share of runner demand. 11 main pushes cost 3,783 runner-min on 11-25. Without coalescing, a burst of merges now runs one run per tip, but a light push still stands down its lanes (`prelude.light`). The fixer re-reads the harness `census` and `queue` arms on the first busy day after the drop, before counting L1-L5's savings against the queue. Main reaches ≤40 min end to end only when the sharding fixer brings the FULL run's longest job under 40 min.
