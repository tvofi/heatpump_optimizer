# R10-RCA-GATE-STALE-JOBS: `gate` reads a finished job as unfinished from a lagging jobs listing

Root-cause seat, `dev/governance/roles/root-cause.md`, 2026-11-04. Measured at origin/main
`d7582ed40`. The fix is the fixer's (R10-HOTFIX-GATE-STALE-JOBS). This seat edited nothing
in `tools/ci/`. The fixer's handoff `a6305aa29` was read and driven, not changed.

## Result

- **Cause:** the Actions jobs listing lags the run graph. `gate` reads it once and treats
  "not completed" as a verdict. The ordering is sound, and no upstream wait lags.
- **Process state: (d).** The sound design rests on an unstated external precondition,
  which fails during GitHub Actions incidents, and nothing notices when it does.
- **Cost test: passes** for a bounded re-read over every reason of this shape.
- **Countermeasure:** that re-read, plus a printed lag line. The handoff as read covers
  3 of the 14 measured false reds. The other 11 are `prelude: None` (10) and `ABSENT` (1).
- **Refused:** a status-page read, an API-health lane, a second endpoint and a train
  re-run of this red.

## 1. Cause

**Reproduced.** `gate()` at `d7582ed40`, over a listing with `tests / mutation` and
`tests / closures` in progress, returns the printed reasons:
`(False, ['tests / mutation: PENDING (this run)', 'tests / closures: PENDING (this run)'])`.
With a fresh listing it returns `(True, [])`.

**The ordering holds.** `gate` needs `[prelude, pr-contract]`, and `pr-contract` needs every
caller with `!cancelled()`. `tests/entities.py` pins both edges. On run 41870314676:

| event | time (Z) | source |
|---|---|---|
| `tests / mutation` log ends | 17:35:05.86 | job 126716534322 log |
| `tests / mutation` `completed_at`; `mutation-autofix` created 17:35:08 | 17:35:07 | jobs API |
| `tests / closures` log ends | 17:36:49.97 | job 126717058202 log |
| `tests / closures` `completed_at`; `closures-autofix` created 17:36:52 | 17:36:51 | jobs API |
| `pr-contract` skipped, `gate` created | 17:36:52 | jobs API |
| `gate` started | 17:37:25 | jobs API |
| `gate` printed both PENDING lines | 17:37:43 | job 126746152523 log |

The orchestrator had acted on both results before `gate` was created, so the graph was not
late. The listing was. In all 28 reason lines of this shape found (section 3), the job's
`completed_at` is earlier than the read. None was unfinished. On attempts after the first,
`completed_at` is inherited from an earlier attempt, so that check is strongest on attempt 1.

**The upstream trigger is GitHub's.** Declared incidents, from
`https://www.githubstatus.com/api/v2/incidents.json`, read 2026-11-04:

| start (Z) | resolved (Z) | name |
|---|---|---|
| 10-30 17:50:54 | 10-30 19:23:40 | Incident with Actions, Pages, and Webhooks |
| 11-04 16:05:31 | 11-04 17:01:11 | Incident with Actions and Pages |
| 11-04 17:40:33 | 11-04 18:16:08 | Incident with Actions |

The two 11-04 incidents both state: "Customers may observe delayed status updates for their
jobs."

**Corrections to the defect as reported.**

- Main run 41870522291 was not only stale. `tests / ci-ratchet` (job 126746954095) really
  failed at 17:42:04Z with `GREW critical_path_minutes: 29.067 (budget 21.983, band 1.3)`,
  and the listing showed it PENDING 171 s later. Attempt 2 of that job passed. That red was
  true and its printed reason was wrong.
- The "64-minute proof" was not reproduced. Run 41870314676 was created at 16:43:40Z, its
  `gate` ended at 17:37:45Z (54 min 5 s) and the run ended at 17:45:36Z (61 min 56 s). The
  eight-PR count comes from the brief and was not checked here.

## 2. Process state: (d)

The process was the gate design and its pins. The precondition appears in the code:

- `tools/ci/gate.py:157`: "this run's own unit always counts (its needs ran it)".
- `tests/entities.py:20060`: "`gate`, needing only it, would judge them pending". PENDING is
  read as a broken graph, the only cause the pin contemplates.

The unstated premise is that once `needs` releases, the listing shows what `needs` saw.
Evidence for (d) over the alternatives:

- **Not (b).** The design was followed: the API read is the last step (R3-1), the needs
  edges are pinned, and the predicate is a line-for-line port.
- **Not (a) or (c), on the timing.** The precondition mostly holds and then fails with the
  platform. There were no such reds on 10-28, 10-29, 10-31, 11-02 or 11-03. 19 of 21
  attempts sit inside or within 66 min of a declared incident (section 3). The other 2 lagged
  20 s and 23 s.
- **Nothing noticed.** 10 of the 14 false reds went green on a later attempt of the same run.
  `git grep` at `d7582ed40` finds `prelude: None` nowhere in `dev/`, so the 10-30 cluster
  left no record. `gate.py`'s self-test has no PENDING case, only the `bad.append` line.
  The replay oracles read settled runs, which cannot show a lag.

Per `defect-root-cause.md`, the countermeasure for (d) makes the process notice the
precondition change. It is not a firmer rule.

## 3. How far the class reaches

**Commands**, from `dev/audit/harnesses/r10_gate_stale_jobs/`, which also holds the recorded
`reasons.jsonl`. `scan.py` reads each candidate run's
`jobs?filter=all` and each red `gate` job's log, and keeps the Judge step's stdout.

    gh api --paginate "repos/tvofi/heatpump_optimizer/actions/workflows/ci.yml/runs?created=<day>&per_page=100" ...   # runs.tsv
    python3 -I scan.py runs.tsv reasons.jsonl 2600 2500
    python3 -I tally.py reasons.jsonl
    python3 -I recover.py

**Coverage.** 2520 CI runs, created 2026-10-28 to 2026-11-04. Candidates are runs whose latest
conclusion is `failure` or whose `run_attempt` exceeds 1: 1037. Read: 1000. Unread: 37, all
jobs-listing read errors after one retry pass, during the 5xx responses the scan logged. First-attempt cancelled runs were not read, so the
counts below are floors. 0 log reads failed.

**Red `gate` attempts: 383.**

| reasons | attempts | really non-success job | false red |
|---|---|---|---|
| **only `PENDING (this run)`** | **6** | 3 | 3 |
| only `FAIL prelude: None` | 12 | 2 | 10 |
| only `ABSENT (this run)` | 1 | 0 | 1 |
| PENDING beside a real red line | 2 | 2 | 0 |
| deferral | 40 | | |
| other | 322 | | |

The class is 21 attempts, 14 of them false reds. `prelude: None` is the same read: gate.py:113
tests the listing's prelude conclusion, and `gate` needs prelude directly. It also conflates
"listed unfinished" with "not listed", because of `(jobs.get("prelude") or (None, None))[1]`.

**By day:** 10-30 has 15, 11-01 has 1, 11-04 has 5, and the other five days have 0.
**By incident:** 11 inside a declared window, 8 within 66 min of one, 2 outside.

**Lag.** Read time minus `completed_at`, 22 attempt-1 lines: 20 to 704 s. The largest are
704 s (`prelude`, 41876634563), 670 s (`coverage-ratchet`, 41870522291) and 375 s (`closures`,
same run). **These are lower bounds:** each is the time of a read that was still stale, not
when the listing caught up. Six lines on attempts after the first carry inherited timestamps
(up to 7141 s) and measure nothing. Their mechanism, a re-run's rows being re-recorded, is
inferred from the listing and not demonstrated.

**Other readers of the same data:**

| reader | a stale read means | direction |
|---|---|---|
| `gate.py` own-run source (157, 168) | false or wrongly reasoned red | **this defect** |
| `gate.py` prelude read (113) | false or wrongly reasoned red | **this defect** |
| `gate.py` other run as source (156), `busy` | not a source, or waits to the bound | safe |
| `prelude.py` `wait_sources` / `judging` | waits; bound 8700 s | safe, slower |
| `prelude.py` `proof_scope` legs (245) | a leg not proven, so analysed again | safe, costs a leg |
| `sweep.py` `gate_of` | polls to 600 s, then leaves it red | safe |
| `merge_train.py` infra re-run | no failed job seen, no re-run | safe, leaves red |
| `ruleset_cutover.py` | refuses non-success | safe |
| `ci-watch.sh`, `merge_pr.sh`, `failure_logs.sh` | keep polling, or miss a red this pass | self-heals |
| `ci_critpath.py`, `autofix_statuses.sh` | analysis only | none |
| **`codescan_wait.py` `source` own-run path (75-76) then `legs_uploaded`** | no poll; a leg whose step is not yet listed success reads as "stood down", and is neither waited for nor read | **may fail open** |
| **`pr-contract.yml` red list (306)** | keeps only `completed` and `failure`, so a lagging red is left off what the body must answer | **may fail open** |

The two fail-open rows come from reading the code. Neither was measured live: no instance was
sought in logs, and it is not established that check-runs or step rows lag the same way. They
need a measurement before anything is built.

**Adjacent, not this class:** 6 red attempts read `.../jobs: HTTP 502 Server Error`, which is
after `ghapi`'s two retries. `tests / ci-ratchet` went red with an incident-inflated critical
path on 41870522291.

**Live probe.** `probe.py` made 143 listings of in-progress runs over 18 polls, from about
18:02Z to about 18:22Z, and found 0 listings with a job unfinished under a created dependent.
So **whether `GET /actions/jobs/<id>` or check-runs are fresher than the listing is unknown.**
A fix must not assume another endpoint escapes the lag.

## 4. Cost test

Unit: wall-clock over the measured 8 days, which stand in for a release cycle.

**cost(defect) x P(recurrence), measured: at least 224 min** over 14 false reds.

- 10 false reds, in 9 runs, went green later in the same run, totalling **170 min 4 s**: 49:54,
  48:36, 31:38 (two reds, 41091328895), 17:10, 7:39, 6:08, 3:44, 3:00, 2:15.
- 1 proof lost, **54 min 5 s** from run start to `gate` end, plus the re-proof, not priced.
- 3 with no later green in the same run (41289450679, 41863133083, 41831302984): not priced.
- These overlap incidents that would have slowed the work anyway, so this is the gate's
  added delay at most on those heads, and it excludes merges held behind them.

**cost(countermeasure, recurring):**

- **Healthy run: 0 s.** The re-read fires only on these reasons. The harness null waits 0 s.
- **Stale run:** one lag, rounded up to the 60 s poll. Summing the attempt-1 lower bounds gives
  about 47 min over the 13 attempts that would re-read; re-run attempts add time unmeasured.
- **Ceiling:** 21 attempts x 720 s = 252 min, reached only if every lag outlasts the bound.
- A wait is runner time, and it delays one verdict that would otherwise be a red.
- Per occurrence, a typical wait of 1 to 3 min compares with a mean 16 min recovery
  (224 min over 14 false reds, so a floor) and 54 min for a lost proof.

**Verdict: build.** About 47 min expected against at least 224 min. The 252 min ceiling needs
every lag to exceed 12 min, and only 2 of the 22 measured lines exceed 11 min.

**The trigger's question.** No cheaper detector exists. The lag exists only at read time on the
live service, so no local or earlier check can reach it. Record this finding on the PR.

## 5. Countermeasure

**Addresses state (d).** `gate` must tell "the listing has not caught up" from "the job is not
green", and say so. Owner: the fixer. No policy change and no budget is asked for here.

1. Re-read, bounded, when every reason is a listing-lag reason: own `PENDING`, `prelude: None`,
   and own `ABSENT`. A real line beside them stays an immediate red.
2. **Never read a lagging job as passed.** Three of the six PENDING-only attempts hid a real
   failure. Re-reading surfaced the true `failure` reason in the harness.
3. Give `ABSENT` a shorter bound than PENDING. Its one measured lag is 20 s, and a structural
   ABSENT such as a renamed job would otherwise wait 12 min on every run.
4. Print one line when a re-read clears, naming the job and the seconds waited, for example
   `listing lag: tests / mutation cleared after 300 s`. That is the "noticing": the 10-30
   cluster passed unrecorded, and this line needs no further instrument.

**Demonstration.** `dev/audit/harnesses/r10_gate_stale_jobs/harness.py <tree with tools/ci>` drives `gate.judge` over a world whose listing catches up at a
set time. It uses the lags above and the finder's shapes, not the fixer's self-test.

| shape | want | main `d7582ed40` | handoff `a6305aa29` |
|---|---|---|---|
| 41870314676 proof, stale 285 s and 181 s | PASS | **FAIL** PENDING | PASS, waited 300 s |
| 41870522291 shape, real red hidden, stale 171 s | FAIL | FAIL, wrong reason | FAIL `failure`, waited 180 s |
| 41876634563 prelude stale 704 s | PASS | **FAIL** `prelude: None` | **FAIL** `prelude: None` |
| 41863133083 prelude stale 134 s | PASS | **FAIL** `prelude: None` | **FAIL** `prelude: None` |
| 41094975103 prelude really failed, stale 357 s | FAIL | FAIL, wrong reason | FAIL, wrong reason |
| 41289450679 pr-contract absent 20 s | PASS | **FAIL** ABSENT | **FAIL** ABSENT |
| past the bound, stale 800 s | FAIL | FAIL, waited 0 s | FAIL, waited 720 s |
| null: fresh listing | PASS | PASS, waited 0 s | PASS, waited 0 s |
| null: real red, fresh listing | FAIL | FAIL `failure`, waited 0 s | FAIL `failure`, waited 0 s |

Main mismatches 4 of 9. The handoff mismatches 3 of 9, all outside its `lagging()` predicate.
The harness detects the defect, and its nulls show it neither fires on a fresh listing nor
passes by skipping. **The "passes once fixed" run for the prelude and ABSENT shapes is still
owed:** that code does not exist yet. The fix review should re-run this harness at the fix head.

**The bound.** `GATE_WAIT_MAX_S` (720) sits inside the 15-min job. Because the lags are lower
bounds, a read past 720 s can still go red. That is safe: it stays FAIL for the sweep. Do not
widen it on these numbers.

**Refused, with numbers:**

- **Status-page read or API-health lane.** 10 of the 21 attempts were outside a declared
  window, so it would miss them, and it adds an external read to every gate.
- **Switching to another endpoint.** Its freshness is unmeasured (section 3).
- **Train auto-re-run of a PENDING red.** It reaches only train proofs, 1 of the 14 false reds,
  and the re-read makes it redundant.
- **A new `bugclasses.json` class.** A word search of its 53 entries found no match, and there
  is one mechanism, removed at one read. The search was by keyword, not a judged review.

**Carried, not built:** the two possibly fail-open readers in section 3. The next step is a
measurement of their logs inside the three incident windows. Cost test not run: no instance
has been measured.

- `codescan_wait.py` own-run path: stale step rows may drop a leg unread. Carry: R10-HOTFIX-GATE-STALE-JOBS
- `pr-contract.yml:306` red list: a lagging red may go unlisted. Carry: R10-HOTFIX-GATE-STALE-JOBS
