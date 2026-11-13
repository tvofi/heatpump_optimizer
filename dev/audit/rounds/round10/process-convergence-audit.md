# Process convergence audit, round 10 (read-only)

The question, from tvofi on 2026-11-13: does the agentic process converge on
quality (Q), lead time (L) and token effectiveness (T), (i) across rounds and
(ii) within a round? Where it does not, what has to change before round 11?
Two scope additions followed the same day: the orchestrator's long-horizon
stability, and how well it follows its plan. Both are in section 8.

This report extends two earlier pieces of work and does not repeat them:

- `dev/audit/rounds/round10/dimension-coverage-audit.md`, section B.4, at
  commit 6ca3bfb7 on `handoff-wip/r10-dimension-coverage-audit`. It covers
  convergence of the product defect count.
- The out-of-tree machinery convergence study at
  `$HPO_STATE_DIR/s14/study/machinery-convergence.md`, written 2026-11-11 over
  the window v7.0.0..61afd4f2. The parent's brief did not name it, but it is
  the closest earlier work. Its figures are cited as `[study row N]` and were
  not re-taken. Where this audit re-measured one, it says so.

**Basis.**

- Read at `origin/main` e23124ff6e (2026-11-13T17:56:43Z).
- The roster at `origin/handoff/audit-r10-roster` 868b2c26.
- The plan state ref `origin/handoff/audit-r10-plan` c57a0141.
- The session state under `$HPO_STATE_DIR`, read only.
- The orchestrator's session transcripts, read for usage counts and
  `compact_boundary` markers only.
- One REST read: `gh run list --branch main --event push --workflow ci.yml
  --limit 40`.
- Clock read with `date -u`: 2026-11-13T18:06Z at the start, 18:25Z before
  writing.

**Labels.**

- **[M]** a measurement. Every one names its command and window.
- **[R]** a quote from a file.
- **[J]** judgement.
- **NO-READ** a figure that could not be taken, with the reason.

Scratch scripts are under `$HPO_STATE_DIR/s14/seat/process-convergence/work/`,
called `W/` below:

- `merges.py` classifies every first-parent merge by `machinery_ratchet.py`'s
  own `diff_stats`, written to `merges.tsv`.
- `agg.py` aggregates per round and per week.
- `closure_series.txt` is the planned closure in each of 498 `PLAN.html`
  commits.
- `roster_daily.txt` is the roster at the last commit of each day.

**Round windows [J].** The tags and stamp subjects give:

| Round | From | To | Tag at the boundary |
|---|---|---|---|
| R8 | 2026-09-24T08:49Z | 2026-09-26T04:26Z | v6.6.11 ("round-8 opens") to v6.7.0 |
| R9 | 2026-09-26T04:26Z | 2026-10-14T13:27Z | v6.7.0 to v7.0.0 |
| R10 | 2026-10-14T13:27Z | 2026-11-13T18:00Z | v7.0.0 to now, still open |

R10's weeks w1 to w5 start at v7.0.0 plus 7k days. w5 is 2.2 days, so it is
censored. The companion audit's "round-9 window v6.0.0..v7.0.0" is wider; this
audit uses the stamp subjects.

---

## Headline

1. **It does not converge on L or T, within round 10 or across rounds 8 to 10. On Q it removes defects faster than it injects them, but the injection rate is rising and nothing measures escapes per dimension.**
   - The production median lead time went from 13.3 h (R8) to 8.1 h (R9) to 21.7 h (R10).
   - Inside R10 it moved by week: 15.4, 24.3, 16.2, 25.5, 27.4 h.
   - The production share of merges went 33%, 26%, 13%.
   - The change-failure proxy went 0%, 2.2%, 7.2%.
2. **Within the round, scope arrives as fast as it is removed.**
   - flow_metrics: 513 groups added and 505 closed in 724.5 h (0.71/h against 0.70/h).
   - The planned closure moved 13.6 days later in 12.9 days of plan history (444 of 496 changes later). The forecast horizon held at 3 to 7 days the whole time.
   - The groups the baseline did schedule mostly finished *early* (median 19.6 h early, 15 of 66 late). The slip is added scope and tail, not slow execution [M, section 8d].
3. **The coordination layer, not the fix work, consumes the measured tokens.**
   - In session 14 the orchestrator's own context used 4.34 B tokens (cache read plus create plus input plus output).
   - Its 428 local sub-seats used 2.14 B. Of those, 66% went to standing seats (dispatch, merge, triage, tick) and 5% to fix or repair seats [M; classification heuristic].
   - Cloud seats, where most fixers run, have no token record at all: NO-READ.
4. **Several self-feeding loops are open or self-amplifying.**
   - The scorecard has never run on the beat: its inputs have no producer, and the running job file omits the row.
   - The machinery ratchet has never bound: 488 measured against a cap of 521, with 0 exemptions ever.
   - Triage accepts 61% (450 of 739). 63 of the 73 R10 hotfix merges repair machinery. A main-push CI run has not succeeded since at least 06:34Z today (0 of 36 concluded).
   - The bottleneck alert replays the first value of a trip verbatim, so it printed "merge-wait 2.1 h" while the metric stood at 4.2 h.
5. **The orchestrator's long-horizon memory is lossy by construction.**
   - The memory index is truncated at line 200. 112 entries are cut, 49 of them owner rulings, among them the current mandate, the coordinator cap and every 11-13 ruling.
   - 108 topic files are not indexed at all.
   - Three slips in the record are a settled ruling re-asked of the owner.
   - Session 14 compacted 36 times in 66 h, one every 1.9 h.

---

## 1. Definitions and enumerators for Q, L and T

| | Definition (judgement where marked) | Enumerator in the tree | Per round | Per day | Gap (a finding when "none") |
|---|---|---|---|---|---|
| **Q1** escapes | product defects found outside the finders (owner, outside, RCA, CI on main), attributed to the owning dimension | none. `scorecard.py` line `E` counts roster groups with `source: outside` plus product-touching hotfix and bug groups, with no attribution and no date window. The companion's B.2 table was built by hand. | no | no | **finding Q-E1**: no `caused_by` or `found_by` field, no per-dimension split, no window. |
| **Q2** injected defects | defects whose root cause is a merged PR of the same or a prior round | none. Hotfix branch token as a proxy (`W/agg.py`: `hotfix_production`). | proxy | proxy | **finding Q-E2**: no `caused_by` PR field. |
| **Q3** change-failure rate (DORA) | production hotfix merges / production merges | proxy as Q2, over `machinery_ratchet.py` classes | proxy | proxy | |
| **Q4** verified findings removed | judged `verified` or `weakened` findings whose group merged | `JUDGE.json`, `CATCHUP-JUDGE.json`, roster `findings` | R8 and R10 only | no | R9 has no JUDGE.json (companion B.4(e)). |
| **Q5** main availability | share of concluded main CI push runs that succeed (product jobs separately) | `scorecard.py` `A_gate` and `A_run`, but its `runs.json` has no producer. Study C13 is out of tree. | no | no | **finding Q-E3**: the inputs are never refreshed. |
| **Q6** review real-catch incidence | reviewed PRs with ≥ 1 real-class block / reviewed PRs | `review_strength.py --window` | yes | yes | counts duplicate verdict commits ([study 0 defect 1]). |
| **L1** lead time for changes | first branch-only commit to the merge on main, per class | `flow_metrics.py` prints merge hours only. The planner's `size_durations.py` uses p75 of active hours per size. `W/` recomputed the rest. | reconstructed | reconstructed | **finding L-E1**: no tracked enumerator prints per-class lead-time percentiles per round. |
| **L2** time to deploy | merge to the tag that ships it | none | no | no | NO-READ in this audit (not computed). |
| **L3** closure lead | round start to the closure stamp; the forecast against the actual | `replan.py` summary `closure`; history only as `PLAN.html` commits | reconstructed | yes (each render) | **finding L-E2**: closure history is not recorded as data, only inside rendered HTML. |
| **L4** flow | groups added and closed per hour, first-pass yield, absorbs, merge-hour share | `flow_metrics.py`, `merge_throughput.py flow`, `bottleneck_check.py` | yes | yes | exists |
| **T1** tokens per merged production change | (orchestrator + local seats + cloud seats) tokens / production merges | **none**. Local sessions write `usage` in their transcript JSONL. Cloud sessions are not read. | NO-READ before session 12 | reconstructable for local only | **finding T-E1**: no token ledger. The dispatch ledger records a `PROMPT` hash, not usage. |
| **T2** tokens per group | as T1, keyed by roster group | none. Sub-seat `.meta.json` carries a free-text `description`, not a group id. | no | no | **finding T-E2**: the seat-to-group key is missing. |
| **T3** coordination share | orchestrator plus standing seats over all tokens | none | no | no | |

**What a per-group token record needs [J].**

1. Every dispatch (`cloud_dispatch.py`, the local Agent spawn) writes `group`, `role` and `model` into the seat's metadata or prompt header.
2. A beat row sums `usage` from the local transcripts under the Claude projects directory, keyed by that header. For cloud sessions the run log or API usage per session id is the source; `trig_` and `cse_` ids are already in the ledger.
3. The figures append to a TSV beside the dispatch ledger.

Cost: one parser plus one header line per brief, about 150 lines. Without
this, T cannot be a controlled variable.

---

## 2. Trends

### 2.1 Across rounds

Sources:

- `python3 W/merges.py <wt> 2026-09-20` (`diff_stats` per first-parent merge), aggregated by `W/agg.py`.
- Tags: `git for-each-ref refs/tags/v*`.
- Lead time: first author date in `M^1..M^2` to the merge commit time, all merges.

| Measure [M] | R8 (1.7 d) | R9 (18.3 d) | R10 (30.1 d, open) | Denominator |
|---|---|---|---|---|
| merges | 64 | 344 | 1 089 | first-parent two-parent commits |
| production / machinery / record | 21 / 43 / 0 | 91 / 236 / 17 | 139 / 488 / 462 | `machinery_ratchet` classes |
| production share | 32.8% | 26.5% | **12.8%** | merges |
| production merges per day | 12.1 | 5.0 | **4.6** | calendar days first to last merge |
| hotfix-branch merges (production) | 0 (0) | 5 (2) | **73 (10)** | branch name contains `hotfix` |
| change-failure proxy (production hotfix / production) | 0/21 | 2/91 = 2.2% | **10/139 = 7.2%** | Q3 |
| releases (`v*` tags) | 2 | 18 | 22 | 0.98 per day in R9, 0.73 in R10 |
| lead time, production p50 / p90 (h) | 13.3 / 22.0 | **8.1** / 49.9 | **21.7** / 49.3 | per merge |
| lead time, machinery p50 / p90 (h) | 3.2 / 11.7 | 3.3 / 23.0 | **10.7** / 35.1 | |
| judged verified findings | 29 of 43 | NO-READ (no JUDGE.json) | 72 + 39 catch-up | companion B.4 |
| review real-catch incidence | NO-READ (no bus) | 19/76 = 0.25 | weekly in 2.2 | `review_strength.py`; the R9 bus starts 10-06, so R9 is partial |
| first-pass yield (first verdict merge) | NO-READ | 28/76 = 0.37 | 412/817 = 0.50 | flow_metrics over R10 |
| local tokens per production merge | NO-READ | NO-READ | session 12: 368 M; session 13: 343 M; session 14: 249 M (§2.2) | transcripts exist only from session 12 |

**[J] What the data can support.**

- R8 is 1.7 days and 64 merges, so it is a fix wave, not a round. Its row is
  context, not a trend point.
- Across R9 and R10 the following worsened:
  - production share (26.5% to 12.8%)
  - production lead time p50 (8.1 h to 21.7 h)
  - the change-failure proxy (2.2% to 7.2%)
  - production throughput per day (5.0 to 4.6)
- First-pass yield improved (0.37 to 0.50), but the R9 denominator starts
  mid-round.
- Q across rounds **cannot be trended**. Escapes are not enumerated per round
  (finding Q-E1), and R9 has no judge record. "Fewer findings" cannot be told
  from "smaller examined set" (companion B.4(e)).
- T across rounds: **NO-READ**. No token record exists before session 12
  (2026-11-04), and none for cloud seats in any session.

### 2.2 Within round 10, by week

Same sources, plus `review_strength.py --window R10wN=… --guardrail` (2 640
verdict commits on the bus, 0 outside the grammar).

| Week (start) | merges | prod | prod share | hotfix (prod) | prod lead p50 / p90 h | first-pass (rs) | real/PR | book/PR |
|---|---|---|---|---|---|---|---|---|
| w1 10-14 | 245 | 26 | 10.6% | 0 (0) | 15.4 / 35.2 | 56/133 | 0.53 | 0.48 |
| w2 10-21 | 297 | 25 | 8.4% | 4 (0) | 24.3 / 44.6 | 111/228 | 0.28 | 0.58 |
| w3 10-28 | 219 | 32 | 14.6% | 7 (4) | 16.2 / 44.4 | 144/215 | 0.36 | 0.51 |
| w4 11-04 | 218 | 33 | 15.1% | **35 (4)** | 25.5 / 57.4 | 90/216 | 0.43 | 0.62 |
| w5 11-11 (2.2 d) | 110 | 23 | 20.9% | **27 (2)** | 27.4 / 55.4 | 42/77 | 0.33 | 0.31 |

`rs` is review_strength's first-pass count over PRs with a first verdict in
the week. That tool counts re-committed verdicts twice ([study 0.1]), so its
absolute verdict and real/PR figures are inflated. The first-pass shares are
not affected.

**Tokens by session [M].** Python over each orchestrator transcript plus its
`subagents/*.jsonl`, deduplicated by message id, summing every integer
`usage` field. Production merges are taken from `W/merges.tsv` in each
session's window.

| Session (window) | orchestrator | local sub-seats | merges | production | tokens / merge | tokens / production merge | output tokens (orch + seats) |
|---|---|---|---|---|---|---|---|
| s12 11-04T19:44..11-07T19:43 | 2.92 B | 1.49 B (113 seats) | 91 | 12 | 48 M | 368 M | 2.4 M + 6.0 M |
| s13 11-07T19:54..11-10T20:29 | 3.90 B | 1.58 B (216) | 102 | 16 | 54 M | 343 M | 3.9 M + 6.8 M |
| s14 11-11T00:00..11-13T18:21 | 4.34 B | 2.14 B (428) | 132 | 26 | 49 M | 249 M | 5.7 M + 13.1 M |

More than 95% of every total is cache reads. Cloud seats are excluded, and
NO-READ: no usage is recorded for them.

**[J] Within the round:**

- **L worsened week over week.** The production p90 went from 35 h to 57 h, and the p50 trended up with noise.
- **The hotfix share rose from 0 to 25% of merges in w5.**
- **The production share rose late (w4 to w5).** That came with the owner's 11-07 to 11-13 production-first rulings, not with less machinery: there were 66 machinery merges in w5's 2.2 days.
- **Tokens per merge are flat at about 50 M.** Per production merge they fell, because the production count rose.
- The orchestrator alone takes 60 to 70% of measured local tokens in every session.

---

## 3. The self-feeding loops

Each loop's trigger, output and round-10 yield, from a round-10 instance
where one exists.

| Loop | Trigger → output | R10 instances [M] | Changes merged / metric moved | Lead time | Cost bounded? | State [J] |
|---|---|---|---|---|---|---|
| **Root-cause seats** (`root-cause.md`) | release defect or red check → RCA doc plus countermeasure or refusal | 57 `dev/audit/rca/R10-*.md` on main (`ls`); one more today on a handoff-wip (setpoint latch) | merged countermeasures per RCA: NO-READ (no RCA→PR link field). Recurrence: 12 of 18 barriered R9 classes have R10 instances (companion B.4(c)). | today's setpoint RCA ran 16:17Z → 16:33Z (16 min) [sweep.md] | no cap on RCA count | **open on effect**: nothing measures whether a countermeasure lowered its class's rate |
| **Proposal triage plus the bar** | sweep or seat proposal → ACCEPT, DEFER, REJECT or LOG | 739 rulings in 248 batch files: ACCEPT 450 (61%), DEFER 129, REJECT 134, unparsed 26 (Python over `dev/programme/triage/*.md`) | REJECTs mentioning a 10% or 20% bar: 34 at most. ACCEPTs that cite a bar-skip route (severity, owner directive, RCA countermeasure): 107. Proposals returning to an already-patched instrument: 88% ([study 23]) | rulings land in hours; proposals per code merge in w4: 2.53 ([study 22]) | **no**: the bar is per proposal, and high severities skip it | **self-amplifying** |
| **Scorecard** (`scorecard.py`, beat row `scorecard`) | daily → ten report lines | **0 beat runs.** `beatd.jobs.local.json` (the running job list) has 14 rows and no `scorecard`. `$HPO_STATE_DIR/scorecard/` does not exist. No program in the tree writes its inputs (grep). | none | n/a | yes | **open: produced by nothing, consumed by nothing**. Run by hand here with the study's 11-11 inputs, in the table below. |
| **Bottleneck alert** | each beat → `BOTTLENECK:` lines in the digest | 6 lines acted on in `s14/sweep.md` (e.g. 11-13T06:27Z class-open 32% → RCA seat; 12:22Z yield 0.59 → rule (h) in fixer briefs) | yield stayed at 0.58 to 0.59 (alerts at 10:28Z and 12:22Z; my run at 18:13Z: 0.59) | same turn | yes | **wired, weak effect**. The digest holds `merge-wait 2.1 h` while the metric reads 4.2 h (`bottleneck_check.py` at 18:13Z), because `--memory` replays the first line of a trip verbatim. **A worsening trip is invisible.** |
| **Class barriers** (`bugclasses.json`) | ≥ 3 instances → barrier | companion: 55 classes, 30 barriered, 5 detector | recurrence after a barrier: not separable from pre-existing (no instance dates) | — | — | **open on effect** |
| **Forward-carries / R11 intake** | finding for a later stage → its brief | `R11-INTAKE-R10-RESIDUE` takes carries; about 100 unmarked carries at 11-13T06:34Z (`sweep.md:1473`) | — | — | grows with no cap | **sink, not a loop**: about 100 items deferred |
| **Machinery ratchet** | each merge → refuse past the cap | `machinery_ratchet.py --measure` at e23124ff: nonproduction 488 of 580 (production 92, machinery 305, record 183), churn 13 046 per kilo product line. Caps 521 (band 5) and 14 797. Exemptions: `[]`. | **never bound**: the cap was recorded at 521 of 580 (90%) | — | — | **non-binding**. The cap measures the status quo; it does not set a target. |
| **Policy budgets** | per-file and corpus caps | corpus 16 009 words at v7.0.0 → 37 480 ([study 25]); a raise approved under mandate 11-11 (`sweep.md:333`) | — | — | partly | ratchets, raised under mandate |
| **Re-plan** (`replan.py`, plan-beat) | every 30 min → closure date and order | 498 `PLAN.html` commits 10-31..11-13. `replan.py` changed by 62 main commits in R10; the duration model re-fit 4 times (`git log tools/plan/durations.json`). | changed dispatch: 11-12T13:21Z RE-CHAIN, 11-12T04:39Z chain restart, 10-25T16:35Z ordering ruling (11 such lines in the logs) | — | yes | **mostly a date mover**. One jump (11-12T14:20Z, +2 days) was caused by a change to `replan.py` itself (#3428, `sweep.md` 14:26Z). |

**`scorecard.py report`, run by hand [M]** (`--dir W/sc-1111`: the study's
inputs, data to 11-11T19:35Z; train log `merge_train/train.log`; sweep record
s14):

| Line | Value |
|---|---|
| `A_gate` | 0/0 read (20 runs, no job listings) |
| `A_run` | 0/20 |
| `Y_rev` | 25/50 = 50% |
| `M_first` | unread (no family map) |
| `Y_train` | 25/50 = 50% |
| `H` | 18/50 hotfix (production 10 among them) |
| `S` (merges) | 488/580 |
| `S` (lines) | machinery 189 345 / product 102 033 = **1.86** |
| `E` | 24 outside groups, 12 product hotfix or bug groups |
| `C` | 6 |
| `K` | 32 |

With an empty `--dir`, every line but `S` and `K` prints `unread`.

**Self-amplification, measured [M]:**

- The hotfix share of merges rose 0% → 1.3% → 3.2% → 16.1% → 24.5% (w1 to w5). 63 of the 73 R10 hotfixes are machinery.
- The non-production share is 87% for R10 as a whole.
- Machinery lines per product line rose from 0.89 at the round start ([study 4]) to 1.86 now (scorecard `S`).
- Main CI right now: `gh run list … --limit 40` over 11-13T06:34Z..17:56Z gives **0 success, 19 failure, 17 cancelled, 4 in progress**.

**Introduced defects (machinery), lower bound:**

- 35 of 52 hotfix groups repaired the machinery ([study 18]).
- Today's chain: #3520 broke `tick_loop.sh` under bash 3.2 (merged 14:14Z). The relay arm was skipped until hotfix #3558 merged at ~17:56Z.

**[J]** The loops that would damp this (scorecard, ratchet, triage bar) are
open or non-binding. The loops that add to it (RCA countermeasures, accepted
proposals, hotfixes) have no budget. The machinery is a positive-feedback
system with no working limiter.

---

## 4. Rework and waiting, ranked

| # | Source [M] | Figure | Command and window | Cost estimate [J] |
|---|---|---|---|---|
| 1 | **CI queue and main red** | 40 latest main push runs: 0 green; 2.5 days with 0 of 64 green after #3315 ([study 1]); queue 83 queued and 7 running at 11-13T04:11Z, after which batch b2's proof timed out with nothing merged (`sweep.md:1412-1413`) | `gh run list` today; sweep record | every merge waits; the train's proof needs a run |
| 2 | **Review repair rounds** | planner model: review rounds per group L 4.0, M 3.47, S 2.47, at 5.65 h per round (`plan-live.json` `generated.model`, 348 done groups) | `replan.py` output | (rounds − 1) × 5.65 h ≈ 8 to 17 h per group |
| 3 | **Merge wait** | median merge-verdict-to-merge 4.2 h (51 PRs, 24 h; worst #3388 71.7 h); the train ended rc 0 in 51 of 199 runs (rc 1: 139; killed: 9) | `bottleneck_check.py` 18:13Z; `grep TRAIN_RC merge_train/train.log` | |
| 4 | **Train skips and parks** | 357 SKIP lines on 160 PRs (ci 198, recarry 66, merge 53, carry 21); 148 PARK (policy 70, findings 56) | `grep` of `merge_train/train.log`, whole log from 10-16 | each skip ≈ a later batch |
| 5 | **Head churn from main** | main absorbs per fix branch: mean 3.61, max 27, over 835 PRs; production 6.51 ([study 14]) | `flow_metrics.py --window 2026-10-14T13:27Z..2026-11-13T18:00Z` | each absorb is a CI cycle (p50 57 min) and often a re-review |
| 6 | **First-pass review yield** | 0.50 (412/817) for the round; 0.59 over the last 24 h (alert); first blocks on production: test strength 35%, carry bookkeeping 20%, class-open 14%, CI state 10%, product defect 8% ([study 2.4]) | flow_metrics; bottleneck; study | 42% of blocks are bookkeeping ([study 3]) |
| 7 | **Re-reviews of unchanged code** | 619 (flow_metrics; inflated by duplicate verdict commits; 204 after deduplication [study 0.1]) | flow_metrics | |
| 8 | **Relay serial arm** | 99 STUCK, 83 BUSY, 260 HELD-VERDICT, 1 128 POSTED in `cloud-relay.log`; one stall of 57 min and one of 1 h 34 min on 11-13 (`sweep.md:1522, 1790`) | `grep -c` | verdicts wait behind updates |
| 9 | **Seat recycles and compactions** | 32 recycle lines (scorecard `K`, s14); orchestrator compactions s12 19, s13 31, s14 36 | transcripts | each costs a full corpus re-read, about 64 k tokens ([study 25]) |
| 10 | **Body and record refusals** | 65% of PR bodies name a red check; 30% carry friction ([study 26]); `UNHELD` and `UNACTIONED` in §8 | study | |

**[J] Ranking by wall-clock effect.**

1. CI starvation and main red.
2. Review rounds.
3. Merge and train waits.
4. Head churn. This multiplies items 1 and 2: shared files are touched by 94% of production merges ([study 2.2]).

---

## 5. Benchmarks (gap tables)

Every row is from memory and unverified against the current edition. No
clause numbers are given.

### 5.1 DORA four keys

| Key | What the reference asks | What the programme has [M] | Gap |
|---|---|---|---|
| Deployment frequency | on demand, many per day for elite | 0.73 releases per day in R10 (22 tags); stamped every 3 production groups | adequate for a HACS integration [J] |
| Lead time for changes | under a day for elite | production p50 21.7 h, p90 49.3 h (commit to merge only; merge to tag is NO-READ) | rising; not tracked per round by a tool |
| Change failure rate | 0–15% for elite | proxy 7.2% product; machinery 63 hotfixes / 488 = 12.9% | no `caused_by`, so the proxy may under-count |
| Time to restore | under an hour | main CI red 2.5 days (11-09 to 11-11) and red all of 11-13 so far; setpoint latch shipped v7.1.12 at 11-12T10:48Z, owner report 11-13T16:17Z, unfixed at 18:00Z | **no MTTR enumerator** |

### 5.2 ISO/IEC/IEEE 12207 process groups against capability levels (ISO/IEC 33000 series, CMMI-like)

Capability levels: 1 performed, 2 managed, 3 defined, 4 measured, 5 optimising.

| Process | Level [J] | Evidence | Gap |
|---|---|---|---|
| Project planning and control | 2–3 | `replan.py`, gantt acks | not 4: the estimate and closure are not stable against model churn (62 planner commits) |
| Measurement | 2 | many instruments | not 4: no baseline is carried round over round; the scorecard is not running |
| Quality assurance (review) | 3 | `fix-review.md`, guardrail | reviewer effectiveness: one would-trip (sonnet 0/20 incidence, p = 0.0014) at report-only |
| Verification | 3 | gate, mutation | the RCA shows tests pinning a defect as intended (companion row 1) |
| Configuration management | 3 | tags, stamp | the toolchain is unpinned: machinery is live on merge ([study 2.1a]) |
| Infrastructure management | 1–2 | beat, relay | outages recur (§8c) |
| Process improvement | 5 in form, 1 in effect | RCA, triage, ratchets | improvement is not measured against a target (§3) |
| Knowledge management | 1 | memory index, HANDOVER | truncated index (§8b) |

### 5.3 ISO/IEC 25010 against the dimensions

The companion's B.1 covers the attribute map. Not repeated here.

### 5.4 AI-specific controls: ISO/IEC 42001, ISO/IEC 5338, NIST AI RMF

| Control | Asks | Has | Gap |
|---|---|---|---|
| Human oversight | defined points where a person approves | code-owner review, but mandate 6715477401 lets an agent post the owner's approving review (memory *mandate-review-as-tvofi*) | the setpoint latch was accepted by agent approval under the mandate (`sweep.md` 16:26Z RCA) |
| Traceability of AI decisions | log of inputs, model and decision | dispatch ledger (`PROMPT` hash, model, trig id), verdict bus | prompt *text* and token use are not retained for cloud seats |
| Evaluation of the agents | measured performance per agent and model, with drift monitoring | `review_strength.py --guardrail` per model | report-only; no planted-defect audit has run in response to the sonnet would-trip; fixer effectiveness per model is unmeasured |
| Risk management of the AI system | risk register for agent failure modes | RCAs and bugclasses | no register of agent-specific failure modes (re-asking, lost rulings, a seat writing outside its lane) |
| Data and resource management (5338) | resource accounting | none for tokens | T-E1 |

### 5.5 Supply chain: NIST SSDF SP 800-218, SLSA, OpenSSF Scorecard

| Practice | Has | Gap |
|---|---|---|
| Protect the software (signed and provenance builds) | deploy-key stamps, App identities | SLSA provenance for releases: NO-READ (not checked) |
| Produce well-secured software (review, test) | strong | — |
| Respond to vulnerabilities | Dependabot (#3483) | D11 runs Scorecard; product manifest pins unbounded (companion B.3 item 9) |
| Pinned dependencies (Scorecard) | partially | the toolchain itself is the unpinned dependency of every seat |

### 5.6 IEC 61508 and functional-safety practice for actuator control

| Practice | Has | Gap |
|---|---|---|
| Hazard and risk analysis of outputs | none per write site | 8 `services.async_call` sites and 32 hold sites (companion B.3 item 1); three actuator escapes in R10 |
| Safe state and release of interlocks | refusals exist; no auto-release requirement | setpoint latch: refusal with person-only release |
| State-space coverage of tests | idle-plan tests only in places | boost-flow defect latent since v6.7.17 |
| Independence of verification | separate reviewer seat | same model family; reviewer ≥ fixer model rule (memory) |

### 5.7 Statistical process control, defect removal efficiency, capture-recapture

| Practice | Has | Gap |
|---|---|---|
| Control charts on stable measures | the bottleneck thresholds are fixed numbers | no centre line or limits; the alert replays a stale value |
| DRE = removed / (removed + escaped) | R10 ≈ 111 / (111 + 25) ≈ 0.82 [J; companion's 25 escapes] | not computed by any tool |
| Capture-recapture of remaining defects | two independent finders on one universe would give the overlap | finders are partitioned by dimension, so there is no overlap to estimate from. **[J]** A two-seat overlap on D1 and D2 would give the first estimate. |

### 5.8 Lean flow

| Practice | Has | Gap |
|---|---|---|
| WIP limit | cap of 20 open PRs; dispatch gate | 16 over-cap fires logged, e.g. "ALL 52 open PRs" (11-11) |
| Takt | 1 group per hour (owner) | arrival 0.71/h ≈ completion 0.70/h, so the queue never drains |
| First-pass yield | 0.50 | rolled production FPY 16% ([study 10]) |
| Stop the line (jidoka) | hotfix priority | main red all day with merges continuing by override (v7.1.11 `--allow-red`) |

---

## 6. Necessary changes before round 11

Ranked by expected effect on Q, L and T per unit of cost. **[J]** throughout;
each names its measured basis.

### (a) Must precede round 11's finders

| # | Measured problem | Change | Metric and enumerator that shows it worked | Standing cost | Touches |
|---|---|---|---|---|---|
| a1 | Main red: 0 of 36 concluded main runs green today; 2.5 days red 11-09..11; machinery live on merge | **Pin the toolchain and split main's status** (study D2 and D3): seats and the beat run tools from a promoted `toolchain/stable` ref; product status separate from machinery status; no stamp on a product red | product-green share of the last 20 main runs ≥ 90%; `scorecard A_gate` once fed | one ref, one promotion step | `.github/workflows/*`, `beat_jobs.py`, `stamp.py`, `orchestrator.md` |
| a2 | Machinery grows with no limiter: ratchet at 90% of the window, never bound; triage ACCEPT 61% with bar-skips | **Make the ratchet a target, not a record.** Re-record `nonproduction_merges` to a declining schedule (e.g. −10% per week of the round). Remove the severity skip from the 20% bar for machinery. One in, one out for gates. | `machinery_ratchet.py --measure` falling each week; triage ACCEPT share for machinery | none extra | `machinery_budgets.json`, `proposal-triage.md`, `ratchet-budgets.md` |
| a3 | The scorecard has never run; no Q, L or T series exists across rounds | **Feed and run the scorecard on the beat.** Add the input producer (runs, jobs, verdicts, merges, roster), add the row to the running job list, and add lead-time percentiles per class and a token line. Land `W/merges.py` and `W/agg.py` as a tracked `round_metrics.py` (per round and per week). | `beatd/scorecard.txt` exists and is dated today; the round-11 report quotes it | one daily job, about 1 REST batch | `scorecard.py`, `beat_jobs.py`, `beatd.jobs.json`, new `tools/audit/seat/round_metrics.py` |
| a4 | No token record; coordination takes about 89% of measured local tokens | **Token ledger keyed by group and role** (§1 T): dispatch writes `group/role/model` in a header; a beat row sums transcript `usage` per header and per cloud session | tokens per production merge per day; coordination share | about 150 lines; a daily job | `cloud_dispatch.py`, seat spawn brief, new ledger row |
| a5 | The memory index is cut at 200 lines: 112 entries hidden, 49 of them rulings incl. the live mandate; 3 re-asked rulings | **Rewrite the memory index**: standing rulings first, superseded entries removed (30 topic files say "supersed"), the index under 150 lines, the 108 unindexed files reviewed or deleted; a hook check that fails when the index exceeds its load limit | `wc -l MEMORY.md` < 200; re-asked rulings in sweep logs = 0 | about an hour once, then a check | memory dir (out of tree); `policy-corpus` hook |
| a6 | Escapes not attributed, so Q cannot be trended (Q-E1, Q-E2) | **`caused_by` and `found_by` on every hotfix and outside group**, scorecard `E` split by owning dimension per round (companion change 7) | per-dimension escape counts in the R11 scorecard | one roster field | `roster_lib.py`, `scorecard.py`, `fixer.md` |
| a7 | The bottleneck alert hides a worsening metric | replay the trip line but print the current value when it is worse by more than 25% | the digest line equals the live value | trivial | `bottleneck_check.py` |

### (b) Can land during round 11

| # | Problem | Change | Metric | Touches |
|---|---|---|---|---|
| b1 | Shared files couple PRs (94% of production merges; 3.61 absorbs per PR) | generate `closures.json`, `structure_budgets.json` and the instruments index after merge, not in PRs; split `features.py` by module (study §4) | absorbs per PR (`flow_metrics.py`) ≤ 2 | tests layout |
| b2 | Bookkeeping blocks 42% of verdicts | the handoff check decides carry, body and red-check items mechanically; reviewer vocabulary limited to product classes (study D4) | M_first share; review rounds per size in `plan-live.json` | `fix-review.md`, `fixer.md`, prepr |
| b3 | Closure forecast does not converge | record closure, scope and capacity per replan as data (TSV); freeze scope at the round's register except production defects and owner orders; machinery proposals go to the next round | slope of closure against the date it was planned on < 0.2 day/day | `replan.py`, `orchestrator.md` |
| b4 | Relay serial arm stalls | concurrent per-branch updates; verdict posting never queued behind updates (proposal candidate already logged 11-13T08:49Z) | relay posting gap p90 | `cloud_relay.sh` |
| b5 | Reviewer drift per model is unmonitored in effect | act on a guardrail would-trip with a planted-defect audit within one day | guardrail lines with an action | `review_strength.py`, dispatch |

### What to REMOVE [J]

- **Standing seats as LLM agents for mechanical roles.** Standing seats use
  66% of local seat tokens (1.42 B in s14) for roles the contracts describe
  as mechanical: queue draining, merge operation, relay. The roster seat was
  already retired for `roster_drain.py`. Retire the merge and dispatch agents
  the same way, wherever a script can do the work.
- **The 30-minute PLAN.html commits**: 498 commits in 13 days. Keep one
  render per change in scope or order, and log closure as data (b3).
- **OWED-ACK re-acks**: 2 368 lines in the ledger; 134 keys acked ≥ 5 times,
  one 142 times. An ack that is re-written every sweep is a level, not a
  decision. Cap re-acks at 2, then escalate.
- **The policy corpus re-read on every compaction**: about 64 k tokens × 36
  compactions in s14. Read the diff since the last proof instead. The corpus
  proof already hashes it.
- **The machinery ratchet in its current recording.** It binds nothing (a2),
  so either make it a target or delete it.

---

## 7. Convergence conditions for the process

A control loop needs four things:

1. a measured target;
2. a sensor that reads it;
3. a feedback path shorter than the disturbance;
4. a controller whose own cost is bounded.

| Variable | Target | Sensor | Feedback faster than the disturbance? | Controller cost bounded? | Met? |
|---|---|---|---|---|---|
| Q (product defects) | 0 objective bugs (owner) | none per round (Q-E1); judge counts in R8 and R10 only | no: escapes reach the owner first (owner caught 3 actuator defects on 11-13) | RCA per defect is bounded; RCA count is not | **no** |
| Q (main green) | 100% gate green | scorecard `A_*` (not fed); hand reads | no: 2.5 days red; today all day | hotfix loop unbounded (73 hotfix merges) | **no** |
| L (lead time) | 1 group per hour takt | flow_metrics, bottleneck | partly: the alert fires within 24 h; actions did not move yield | yes | **partial** |
| L (closure) | owner dates (11-01, then 11-11, then 11-15) | replan every 30 min | no: the forecast horizon held at 3–7 days for 13 days while scope was added at the completion rate | planner changed 62 times | **no** |
| T | none stated | none | — | standing seats and the orchestrator are unbounded (re-reads, re-acks) | **no** |
| Machinery size | ratchet caps | `machinery_ratchet.py` | the cap sits at the status quo | — | **sensor yes, target no** |

**[J]** None of the three variables meets all four conditions. The most
leveraged single fix is to give each of them a target that declines over the
round and a sensor fed every day (a2, a3, a4). Every other change in section
6 then becomes measurable.

---

## 8. Orchestrator long-horizon stability and plan adherence

Sources are under `$HPO_STATE_DIR`:

- `seat-ledger.md`: orchestrator log 10-24..11-11; 6 411 lines.
- `s14/sweep.md`: session-14 log 11-11..11-13; 1 801 lines. No sweep logs for
  sessions 9 to 13 exist as `sweep.md`; their lines are in `seat-ledger.md`.
- `digest/`
- `s10/gantt/`
- `s7/plan-live.json`
- the plan ref
- transcripts

### 8a. Task slips

| Measure [M] | Value | Command |
|---|---|---|
| Owed items standing now (`owed-unactioned.json`, board 11-13T17:40Z) | 62 keys: median age 11.7 h; 50 over 4 h; 10 over 24 h; max 90.7 h (`r10-body-contract-p3-bootstrap`, 119 sweeps); `triage-s14-batch203` 49.6 h | Python over `digest/state/owed-unactioned.json` |
| `UNACTIONED` lines in the digest now | 59 | `grep -c` |
| OWED-ACK lines | 2 368 over 10-31..11-13; peak 567 on 11-11; 794 keys, median 2 acks per key, 134 keys ≥ 5, max 142 | `grep -o 'OWED-ACK …' seat-ledger.md` |
| Whether the acked action happened within its ttl | **NO-READ**: an ack names no completion event, so ack → done is not joinable | finding |
| Slip and correction lines the orchestrator logged | 139 (10-24..11-13); by day: 11-07 29, 11-12 29, 11-13 26, 11-02 12, the rest ≤ 7 | `grep SLIP|OWNER CORRECTION|owner finding|OWNER REPORT` over both logs |
| Who caught them (keyword heuristic [J]) | machinery 65 (47%); seat 33 (24%); self or unattributed 21 (15%); **owner 20 (14%)** | same, by keywords |
| Owner-caught, read by hand | about 14 genuine (lane slips 10-27 ×3, release tag 11-04, Pages and Pi 11-07, nudge.md scope 11-12, re-asked rulings ×3, the three actuator and product reports 11-13) | hand |
| Seat no-return lines | 33 | `grep -c 'no return|ended with no'` |
| Time to detect / time to act | **NO-READ systematically**. Instances: #2736 merge verdict unqueued 46 min (10-24); bash 3.2 relay outage 64 min to detect, found after an owner question (11-13) | finding: the slip has no onset stamp |

### 8b. Loss of the high-level objective

| Measure [M] | Value |
|---|---|
| Compactions (`"compact_boundary"` count per orchestrator transcript) | s11: 3; kapitsa (11-01..03): 7; s12: 19; s13: 31; **s14: 36 in 66 h (one per 1.9 h)** |
| Compaction to corpus proof (s14 instances) | 04:07:01 → 04:07:34; 07:03:50 → 07:04:34; 11:35:45 → 11:36:07; 14:46:41 → 14:47:07; 16:00:52 → 16:01:28; 13:26:21 → 13:27:35. **Under 2 minutes every time.** |
| Proof refusals | 1 recorded (11-13T15:36Z: stale relay log, caused by the bash 3.2 outage) |
| Re-read cost | the corpus is about 3 900 lines, about 64 k tokens ([study 25]); × 36 ≈ 2.3 M context tokens re-read in s14 [J estimate] |
| Memory index | 313 lines; the load cuts at 200; **112 entries cut, 49 naming tvofi, an owner or a ruling**, among them mandate 6715477401, coordinator cap 3, local seat cap 7, every 11-12 and 11-13 ruling, and "Frugal-off group dropped, tvofi told me 3x" |
| Unindexed memory files | 108 of 406 (`ls` against links in the index) |
| Entries marked superseded but kept | 30 files contain "supersed" |
| Rulings violated or re-asked after a context change | 3 logged: FLY-CLOUD-FRUGAL-OFF re-asked (11-12, "3rd"); soak length re-asked (11-13T10:58Z, "did not grep memory before asking"); nudge.md cited as binding (owner finding 11-12T19:03Z) |
| HANDOVER, plan page | the plan page is current every 30 min (498 renders); `HANDOVER.md` not measured, NO-READ |

**[J]** The proof machinery restores the policy corpus reliably and fast. It
does **not** restore owner rulings: those live in memory, and the memory
index silently drops everything after line 200. Every re-asked ruling in the
record is a ruling stored in memory, not in the corpus.

### 8c. Adaptation to roadblocks

| Blockage (round 10) | Onset → detect → workaround → permanent fix | Workaround kind | Became an instrument or proposal? | Recurred? |
|---|---|---|---|---|
| Main red after #3315 (instrument-self-tests) | 11-09T08:16Z → hours → stamped v7.1.11 `--allow-red` → 4 hotfix merges, 59 h ([study 1]) | manual override | yes (hotfix groups) | yes: main is red again 11-13 (check_scopes "owned twice", `sweep.md:1629`) |
| Tick relay arm skipped (bash 3.2 parse, #3520) | 14:14Z → 15:18Z (after an owner question) → manual relay loop → #3558 merged ~17:56Z (3 h 42 m) | local manual | yes: `bare_array.py` rule | first of its kind |
| Relay serial `update_pr` stall | 11-11 (hold-all), 11-12T11:27Z (36 min), 11-13T08:49Z (57 min), 11-13T17:56Z (1 h 34 m) | parallel update seat, hand relay | proposal candidate ×3, unbuilt | **4 times** |
| CI queue starvation | 11-11T20:17Z (83 queued), 11-12T23:58Z (69), 11-13T04:11Z (83) → train b2 timeout | cancel sweep, priority shim | `cancel_superseded.py`, R10-CI-PRIORITY-PAUSE (open #3560) | **3 times** |
| macOS `/proc` (#3475) breaking prepr | → 11-12T12:02Z diagnosed | local | hotfix | — |
| Opener blind to new handoffs | 11-13T16:48Z | hand open | proposal candidate | — |

- Proposal candidates logged in s14 only: 104 (`grep -c 'PROPOSAL CANDIDATE' s14/sweep.md`). Their conversion to rulings is NO-READ, since candidates carry no id.
- **Turn budget [estimate, keyword classes over the 1 719 entry lines of `s14/sweep.md`]:**

| Class | Share |
|---|---|
| dispatch fire records | 35% |
| machinery upkeep (restarts, workarounds, relay, CI, stuck, proof) | 21% |
| merge and stamp flow | 21% |
| programme decisions and plan | **19%** |
| other | 4% |

**[J]** Adaptation is fast at the local workaround level (minutes to hours).
It is slow to become permanent: the same relay stall and CI starvation
recurred 3 to 4 times inside 3 days with the proposal unbuilt. Detection
still depends on the owner for outages that silence the detector itself
(bash 3.2).

### 8d. Plan adherence

**Schedule [M].**

- Planned closure in each `PLAN.html` commit on `origin/handoff/audit-r10-plan`, 10-31T20:03Z..11-13T17:59Z (498 commits, 497 with a closure): `W/closure_series.txt`.
- The closure moved in 496 renders, **444 of them later**.
- First and last closures: 2026-11-03T10:30Z, then 2026-11-17T01:28Z. **+13.6 days of slip in 12.9 days of history.**
- Earlier forecasts, from the ledger:

| Logged at | Closure | Source |
|---|---|---|
| 10-25T16:48Z | 10-30T10:30 | replan v49 |
| 11-01T22:49Z | 11-08T23:18 | |
| 11-04 | 11-11 | |
| 11-11 | 11-15 | |
| 11-12 | 11-16 | |
| 11-13 | 11-17 to 11-18 | |

**Against each date the owner stated:**

| Owner date | When stated | Slip of the 11-13 forecast |
|---|---|---|
| 11-01 | 10-28 (memory *away-drive-to-completion*) | **+16.1 days** |
| 11-11, "the plan's closure" | 11-05 | +6.1 days |
| 11-15 | 11-13 | +1.6 days |

**Against the first plan:** +17.6 days, from replan v49's 10-30T10:30.

**Re-baselines:** 4 CLOSURE acks (3 act, 1 accept). The accept was 11-05T06:31Z:
"the six-entry serial batch and the CI job cap set this slip of about a day".
The gantt baseline's `accepted_closure` is 2026-11-14T14:51Z, so the live plan
is 2.4 days past it. One known false re-baseline: a 11-05 accept line
re-baselined CLOSURE on every pass, so a closure slip was absorbed silently
(`sweep.md:1098`).

**Estimates [M]:** the 66 groups that baseline.json planned, against the
first roster snapshot (every 3rd commit from 11-09) showing
done/absorbed/deferred.

| Group | n | median lateness (negative = early) | late share |
|---|---|---|---|
| all | 66 (60 closed, 6 open) | −19.6 h | 15 of 66 |
| size S | 28 | −11.9 h | 25% |
| size M | 30 | −23.2 h | 23% |
| size L | 8 | −17.3 h | 12% |
| kind instrument | 30 | −34.8 h | 10% |
| kind production | 7 | −14.0 h | 0% |
| kind policy | 3 | +35.2 h | 100% |

- The bias is towards over-estimating. That is expected from a p75 model (`size_durations.py`, 348 groups).
- The duration model was re-fit 4 times: commits on `tools/plan/durations.json`, 10-20, 11-01, and twice on 11-11.
- `replan.py` changed 62 times.
- One plan jump of +2 days came from a planner change (#3428), not from the work.

**Scope [M]:** `W/roster_daily.txt`, the roster at the last commit of each
day.

- 52 groups at the register (10-15); **516 now**: 464 added after the register, 11 of all groups now `deferred`.
- All 516 groups by intake class (the register's 52 included; class from the id token, then `kind`):

| Class | Added |
|---|---|
| instrument | 151 |
| hotfix | 71 |
| fly-in (accepted proposal) | 70 |
| RCA | 38 |
| defect | 31 |
| production | 31 |
| outside | 29 |
| fix | 23 |
| owner | 19 |
| policy | 14 |
| feature | 14 |
| other (arch, study, docs, tooling, chore, record) | 25 |

- Daily peaks: 10-21 +41, 11-01 +44, 11-11 +44 (17 outside).
- Deferred to round 11: 11 groups at stage `deferred` now; about 100 unmarked carries were sent to round-11 sorting on 11-13 (`sweep.md:1473`).
- Carries per day: **NO-READ** in the roster JSON (the carries field read 0–1; carries live elsewhere, 1 882 per [study 24]).

**[J] Slip decomposition.** Baseline groups finished early, and arrivals
equalled completions over the round (flow_metrics: 0.71 against 0.70 per
hour). So almost all of the 11-04..11-13 closure slip is **added scope**
(+120 groups since the 396-group baseline) plus **waiting** (CI and merge,
§4). Slower-than-planned execution does not contribute. An exact split needs
a counterfactual replan with a frozen roster: **NO-READ**. The closure-fit
simulator (`s14/seat/closure-fit/sim`) could produce it.

**Following the plan [M].**

- GANTT-SLIP acks in `s10/gantt/acks.txt`: 250 lines.

| Ack kind | Count | Breakdown |
|---|---|---|
| IDLE | 107 | act 62, defer 35, accept 8, merged 2 |
| LATE | 105 | act 80, accept 21, defer 4 |
| CLOSURE | 4 | |

- How long each IDLE stood, and slip-to-decision lead time: **NO-READ**. The gantt row's output `beatd/gantt.out` is empty, and a slip's first appearance is not logged.
- Over-cap dispatch logged 16 times (owner 9, production 6, hotfix 4, critical path 8; a line can carry several reasons).
- Dispatch order against plan order: NO-READ, since the ledger does not record the plan rank at fire.
- A critical-path group waiting behind other work: instances exist, e.g. 10-26T14:05Z "CP head R10-ORCH-DISPATCH-REG not-started (~3.7 h slip)", but no enumerator counts them.

**Replanning:** about 38 renders a day. A replan changed what was dispatched
in 11 logged instances (re-chain, chain restart, ordering ruling). The rest
moved dates only.

**What the machinery measures today, and what had to be reconstructed:**

| Measured by the machinery | Reconstructed by this audit (each a finding) |
|---|---|
| the live closure | closure history |
| the gantt slip lines | estimate against actual |
| the acks | scope growth by class |
| the owed ages | slip decomposition |
| — | ack-to-done |
| — | slip time-to-decision |
| — | dispatch-against-plan order |

### 8 → section 6

Section 8 supports a5 (the memory index), a2 (scope and machinery limiter)
and b3 (closure as data and frozen scope). It adds:

- **a8, must precede R11.** An owner-rulings file **in the tree**
  (`dev/programme/RULINGS.md`, read with the corpus and proven by the same
  hook), so that a ruling survives compaction without depending on the memory
  index. Metric: re-asked rulings = 0.
- **b6.** An `OWED-ACK` must name its completion event, and an ack is capped
  at 2 renewals.

**Mechanisms that do not pay for themselves here [J]:**

- OWED-ACK re-acks (2 368 lines).
- 30-minute PLAN.html commits.
- Gantt `accept` lines without a ttl (the false re-baseline).
- `PROPOSAL CANDIDATE` lines with no id: 104 in 3 days, none traceable.

---

## NO-READ register

- T before session 12, and T for every cloud seat: no usage record.
- R9 judged findings: no JUDGE.json.
- R8 and R9 first-pass yield, R8 real-catch incidence: no verdict bus before 10-06.
- Merge-to-tag lead time (L2): not computed.
- RCA countermeasure merge and effect rate: no RCA-to-PR link.
- Ack completion within ttl: an ack carries no completion event.
- Slip time-to-detect and time-to-act, systematically: no onset stamp.
- IDLE duration and slip-to-decision time: `gantt.out` empty; first appearance not logged.
- Dispatch against plan order: plan rank not in the ledger.
- Carries per day: not in the roster JSON.
- Slip split by counterfactual: needs a frozen-roster replan.
- `HANDOVER.md` freshness: not measured.
- SLSA provenance: not checked.
- Proposal-candidate conversion: candidates carry no id.
