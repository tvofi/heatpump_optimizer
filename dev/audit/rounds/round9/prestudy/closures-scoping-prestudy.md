# Pre-study: scoping the closures re-derivation — where the ~55 minutes go, and what may be cut

Round-9 pre-study seat `r9-closures-scoping-prestudy`, dispatched by the
orchestrator on tvofi's request ("dispatch a pre-study on how to safely scope
closures to save time ... then prioritize that PR before the instrument
series"). Study only — no fix PRs from this seat. Baseline
**`origin/main` = `969c3a5c84`** (2026-10-10, the merge of #2109). Worktree
`/Users/timmalmstrom/hpo-seats/r9pre-closures/wt`; run logs fetched read-only
via `gh api` from this macOS box. `tests/derive_closures.sh` was NOT run
anywhere (forbidden off Linux, `dev/governance/rules/gate-scoping.md`); every
timing below is either read out of a CI log (cited by job id) or out of the
committed `tests/closures.json` (cited by key). No number below is estimated;
the few that could not be measured are marked **unmeasured** in §7.

## The safety property, verbatim (CLAUDE.md rule 1)

> The gate is scoped by measured dependency closures. `GATE_SCOPE=auto` runs
> only the scripts your diff can reach ... A push to `main` forces `full`: if
> a closure is ever wrong, main goes red within one merge instead of never.

Any alternative that lets a wrong closure survive longer than one merge is
refused whatever it saves. That sentence is applied to every option in §4.

## 1. Where the time goes (measured)

### 1.1 The job is one step

The `closures` job (`.github/workflows/tests.yml`) has: checkout+python+node
setup, `pip install`, `apt-get install strace` (16:28:36→16:29:09, **33 s**),
then **"Re-record the closures"** (16:29:09→17:22:44, **53 m 35 s**), then
`closure.py check` (**0.2 s**), `closure.py no-copies` (**~0.1 s**) and the
artifact upload. Job total **54 m 10 s** — the re-record step is 98.9 % of it.
Source: job `114258919874` (run `38067806307`, event `push`, branch `main`,
head `969c3a5c84`, started 16:28:36Z, failed 17:22:46Z).

The orchestrator's "~70 minutes" on the day's batch proof was **not
reproduced**: the batch branch `batch/20261010-152646-1` (run `38064024146`,
workflow_dispatch) ran its `closures` job 15:32:29→16:27:14 = **54 m 45 s**
(job `114247906174`), failing on the same `INERT READS UNDER-APPROXIMATED`.
54–55 min is what the logs show; the 70 remains unexplained (§7).

### 1.2 Per-script decomposition (the re-record step's own log)

`derive_closures.sh` runs three parallel lanes: lane 1 `stress.py` alone,
lane 2 `features.py`+`entities.py`, lane 3 everything else sequentially (with
`plan_view.py` ordered before the card scripts that read its payload). From
job `114258919874`'s `[HH:MM:SS] record/done` lines:

| item | wall | share |
|---|---|---|
| **`boost_drift_replay.py`** (lane 3) | **29 m 26 s** | **55 % of job wall** |
| `arch_score.py --smoke` (lane 3) | 6 m 16 s | 12 % |
| `harness_headers.py` (lane 3) | 3 m 45 s | 7 % |
| `optimality.py` (lane 3) | 3 m 08 s | 6 % |
| `dst_checks.py` (lane 3, driven child of features.py) | 2 m 43 s | 5 % |
| `backtest.py` (lane 3) | 2 m 23 s | 4 % |
| `finite_boundary.py` (lane 3) | 1 m 35 s | 3 % |
| remaining 24 lane-3 items | ~4 m combined | 8 % |
| lane 1 `stress.py` (parallel) | 14 m 53 s | off path |
| lane 2 `features.py`+`entities.py` (parallel) | 21 m 22 s | off path |

**Lane 3 is the critical path at 53 m 35 s; lanes 1 and 2 are idle after 15
and 21 minutes.** The committed `recorded` table in `tests/closures.json`
(34 entries, sum **4480 s = 74.7 min** of recorded work; largest:
`boost_drift_replay.py` 1489.6 s, `stress.py` 760.6 s, `features.py` 730.5 s)
confirms the shape on an independent, faster run — the same job on the 14:25Z
push to main (run `38059574126`) completed in **30 m 22 s**, so the full arm's
duration is a 30–55 min range, not a constant.

**What dominates is one script, not strace and not the long tail**:
`boost_drift_replay.py` alone is 55 % of the wall. How much of any item is
strace overhead versus the test itself is **unmeasured** (§7).

### 1.3 When the full arm runs at all (the premise, corrected)

The CI job is **not** unscoped on pull requests. `closure-scope`
(`tests/closure.py affected`) derives `skip` / `scoped` / `full` per PR, and
the `closures` job already re-derives only the scoped scripts there — the
same three-dot diff `GATE_SCOPE=auto` uses. The full arm runs on:

1. **every push to `main`** — rule 1's detector, by design;
2. **every `workflow_dispatch`** (the merge train's batch proofs) — a
   dispatch has no PR base/head, so `SCOPE_CASE` is empty and the full arm
   runs (job `114247906174` above);
3. the nightly, and PRs whose diff touches a gate file or a file no closure
   has ever measured (`affected`'s `full` cases).

Measured frequency: **7 push-to-main `Tests` runs on 2026-10-10 alone**
(runs `38067806307`, `38059574126`, `38057162868`-lineage; list via
`gh api .../actions/runs?branch=main&event=push`), plus the batch dispatch —
**~8 full arms today ≈ 4–7 h of the 100-minute-timeout lane**, at the round's
merge cadence (12 merge commits on main today, 686 commits since 2026-10-07).
The workflow's own comment still says "~40 s an entry against 12-22 minutes
for the table" — stale by roughly 2.5x; the table is now 30–55 min.

## 2. Today's failure, cause exactly (the check working)

PR **#2109** (branch `fix/r9-prestudy`, merged 16:28:30Z) added
`dev/audit/rounds/round9/prestudy/boost_drift_refit.py` and 22 sibling files,
all under INERT prefixes → `affected` derived **`skip`** → the fast arm ran
**16 seconds** and passed (PR run `38058204083`, `closures` job
14:05:48→14:06:04, `success`). But `tests/harness_headers.py`'s
`_scope_paths()` **rglobs every `dev/audit/rounds/round*` directory**
(`tests/harness_headers.py:318`), so a real recording opens any new `.py`
there; the committed `inert_reads` for that script (540 files) did not list
it. The `INERT READS UNDER-APPROXIMATED` check can only fire where a
recording exists — and on a `skip` PR no recording is made. The error
surfaced on the next full arm: the main push, **54 minutes after merge**,
`exit 1`. Rule 1 held exactly — red within one merge — and the repair
(`derive_closures.sh --single tests/harness_headers.py` + merge, then a full
re-run to confirm) cost on the order of two more full arms.

So the incident class is: **a diff that is INERT by prefix but readable by a
discovery glob or an inert_read reaches the `skip` fast lane, and its only
detector is the full arm**, at 30–55 min, after the merge.

## 3. What the check steps cost

`closure.py check` on the full recordings: 0.2 s. `no-copies`: ~0.1 s.
Upload: seconds. Confirmed the orchestrator's reading — the re-derivation is
the entire cost; no alternative that only touches the checking steps can save
anything.

## 4. The alternatives

### (a) Diff-scoped re-derivation, full checks kept — two extensions to what already exists

**a1 — scope the dispatch/batch lane.** In the `workflow_dispatch` arm,
compute the batch branch's three-dot diff against `main` in-job (exactly the
code the fast arm already runs) and feed it through `closure.py affected`,
taking `scoped` when derived, **fail-closed to `full`** when no diff can be
derived. Soundness is the same argument PR scoping already rests on, printed
by `print_affected` itself: every closure the union diff can reach is
re-derived; the untouched ones were validated by main's last full arm against
a tree that differs from the batch tree only by that same diff — and the next
push to main re-checks everything regardless. Rule 1 preserved unchanged.
Measured saving: up to **54 min per batch dispatch** when scoped (today's
dispatch re-derived all 33 for a diff whose PRs had each already been
scoped-checked); a typical scoped batch costs the sum of the selected
recordings — minutes. New failure mode: none beyond the existing fail-closed
default; the diff-derivation bug class is guarded by the same
"no changed files could be determined → full" refusal `affected` already has.

**a2 — make `inert_reads` visible to `affected`'s skip rule.** Today a
changed file that sits in some script's committed `inert_reads` is still
counted as INERT for the skip decision, and a NEW file under a prefix that
recordings demonstrably rglob (`dev/audit/rounds/round*`) is invisible to the
table entirely. Extend the skip rule: a changed file listed in any script's
`inert_reads` selects that script; a new file whose parent directories
contain recorded `inert_reads` for some script selects those scripts (coarse
prefix match, strictly over-selecting). Today's PR #2109 would then have been
`scoped` for `tests/harness_headers.py` (220.7 s recorded) and **red on the
PR in ~4 minutes, before the merge**. This *strengthens* rule 1 (detection
moves earlier than one merge, not later) at the cost of some `skip` PRs
becoming `scoped`. The one hazard is the mirror of the `_is_header_corpus`
design note: an encoded prefix shape can over-select (cost) but the rule must
fail toward selection, never toward skip — the default for an unknown shape
stays `full`, which is `affected`'s existing default.

**What (a) deliberately does not save:** the push-to-main full arm. That run
*is* rule 1's detector and stays untouched by both extensions.

### (b) Content-addressed recording cache — REFUSED

To trust a stored recording without re-taking it, the cache key must cover
the script, every file it opens — closure **and** `inert_reads` — and the
tracked-file listing (glob discovery reaches files by existence, not by
content). But `inert_reads` is precisely what you re-record to learn: the key
must contain the answer before the measurement that produces it. A key built
from the *previous* recording's answer is sound only while nothing outside
the key changed, and GitHub's actions cache is freely evicted, mutable state
restored by your own key string — one stale restore or key collision is a
wrong closure that **stays green**, the exact event rule 1 exists to make
impossible. The committed file's own header (`CLOSURES_COMMENT`) states the
principle the cache would break: "MEASURED, not written by hand." The one
narrow sound use — reusing recordings across re-runs of a byte-identical
head — saves little (re-runs are rare) and still adds a soundness obligation.
**Refused.**

### (c) Split the job: cheap per PR-head, full re-derivation on push-to-main only

This is the **current design**: `closure-scope` + the fast arm + the scoped
arm on PRs, full on main, dispatched by the same table it checks (landed
through #353's lineage and the #201 docs-only fast lane). Its residual costs
are exactly the three items elsewhere in this list — the batch dispatch (a1),
the skip blind spot (a2), and the lane layout (e). No further split exists
that does not move the full re-derivation off main, which is (d). Rule 1
verdict: as it stands, preserved; nothing to change here but the three
deltas.

### (d) Nightly full, per-PR static — REFUSED

A wrong closure would survive from its merge until the next nightly — up to
a day, at this round's cadence roughly five merges — and today's incident
class (`inert_reads` under-approximation) would be entirely invisible to a
static per-PR check, since detecting it requires a recording. This violates
"main goes red within one merge instead of never" directly, whatever it
saves. **Refused.**

### (e) Rebalance the derivation lanes — found by this study, no safety change

The three-lane layout in `tests/derive_closures.sh` predates
`boost_drift_replay.py`'s 29-minute entry: lane 3 serialises 31 items for 53
minutes while lanes 1–2 sit idle after 15 and 21. Shard lane 3 by descending
recorded seconds across the existing background lanes (or two more), keeping
the documented ordering constraints inside one lane — `plan_view.py` before
the card scripts that read its payload, and the driven-child pairs beside
their drivers. That a script's lane changes *when* it is recorded, not *what*
it opens, is already established in-tree (R9-F10.15, comment at the lane-2
definition). Wall-clock floor is the longest single recording
(`boost_drift_replay.py`: 24 m 50 s committed / 29 m 26 s today), so a
balanced layout lands at **~30–33 min**, a saving of **21–24 min (~40–45 %)
on every full arm** — main pushes, nightly, full-case PRs and batches alike.
Rule 1 untouched: same recordings, same checks, only scheduling. New failure
mode: CPU contention on the shared runner inflating recordings — bounded by
the job's existing `timeout-minutes: 100`, and **measured, not assumed, by
the first landed run** (acceptance test below). A follow-up question inside
(e), flagged not assumed: `boost_drift_replay.py` replays a fixed week; the
`golden.py`/`env_drift.py` precedent (cheap invocation recorded, closure
widened by rule) suggests checking on Linux CI whether a cheaper recording
invocation opens the same read set — that would cut the floor below 15 min.

## 5. Cost test (root-cause.md §4)

`cost(countermeasure) < cost(defect) × P(recurrence)`.

The recurring defect being attacked is full-arm closures time: **30–55 min
per run, ~8 runs measured today (7 main pushes + 1 batch dispatch) ≈ 4–7 h
of lane time per day**, and each main red of this class costs a repair cycle
(today's: fast-arm green 16 s → 54 min red on main → `--single` repair →
another full arm to confirm).

| option | engineering cost | measured / bounded saving | risk cost |
|---|---|---|---|
| (e) lane rebalance | one lane-layout edit in `tests/derive_closures.sh` + one CI proof | ~22 min × ~8 full arms/day ≈ **~3 h/day** | none to the guarantee; contention bounded and observable |
| (a2) inert_reads scoping | extend `affected`'s skip rule + `tests/entities.py` controls | removes a class of post-merge main-reds (recurrence measured today and in the R9-F10.9d/#1886 lineage); each avoided incident ≈ 2 full arms + a repair PR + orchestrator attention | none — strictly more conservative than `skip` |
| (a1) batch-lane scoping | generalise the fast arm's diff derivation to the dispatch arm | up to **54 min per batch dispatch** when scoped | none beyond existing fail-closed default |
| (b) cache | high (soundness proof per key) | small | unbounded: wrong closure green — refused |
| (d) nightly | small | large | unbounded: wrong closure survives ~5 merges — refused |

## 6. Recommendation, and the smallest first PR

**Do (e) first, then (a2), then (a1). Refuse (b) and (d).** (e) is the
smallest change, carries zero risk to the guarantee, and benefits *every*
full arm including the ones (a1)/(a2) cannot avoid — main pushes are rule
1's price and stay. (a2) kills today's incident class at its PR instead of
on main. (a1) removes the one remaining unscoped lane. (b) and (d) trade the
safety property itself and are refused on the brief's own terms.

**Smallest first PR (described, not written):**

- Files changed: `tests/derive_closures.sh` only — lane layout. Move
  `boost_drift_replay.py` to a lane of its own; distribute the remaining
  lane-3 items by descending `recorded` seconds across four background
  lanes, preserving the `plan_view.py` → card-scripts order and the
  driver/child adjacencies in a single lane.
- Acceptance test: the next push-to-main `closures` job is green with all 33
  recordings present (no "NO recording this run"), `closure.py check` and
  `no-copies` unchanged, and the re-record step's wall clock is **measured
  ≤ 35 min on at least two runs** before the change is called done. The
  scoped `--single` path and `GATE_SCOPE=auto` are untouched.
- Drivability (`pr-contract`): the check family still runs from the same
  workflow file with the same inputs and the same `--record-only` /
  `--single` / `--out-dir` interface; no check, lane or hook changes what a
  seat or CI must invoke, so nothing is left undrivable.

## 7. What could not be measured, and why

- **strace-vs-test decomposition per script.** This box is macOS and a full
  `derive_closures.sh` is forbidden off Linux (`gate-scoping.md`); a Darwin
  recording is additionally unsound in the shrink direction. The committed
  `recorded.seconds` are honest for the invocations run but cannot be split
  into instrumentation overhead versus test work. All per-script figures
  above are therefore **Linux CI wall-clock measurements, bounds for any
  decomposition claim**.
- **The "~70 min" batch figure.** Not reproduced; the cited batch's job
  measured 54 m 45 s. Possibly a colder/earlier run or queue-inclusive
  counting; reported as the orchestrator's number, not confirmed.
- **Contention cost of >3 parallel lanes** (option e). Cannot be measured
  off the CI runner; the acceptance test above exists precisely to convert
  this bound into a measurement on the first landed run.
- **How much of `boost_drift_replay.py`'s 25–29 min is irreducible.** The
  cheap-invocation question (§4e) needs a Linux recording to answer; flagged
  as follow-up, not assumed.

## 8. Every figure's provenance

- Job timings, per-script record/done lines, failure text: `gh api
  .../actions/jobs/114258919874/logs` (push to main, run `38067806307`,
  head `969c3a5c84`); `.../jobs/114247906174` (batch
  `batch/20261010-152646-1`, run `38064024146`); `.../jobs` of run
  `38059574126` (14:25Z push, 30 m 22 s); `.../jobs` of run `38058204083`
  (PR #2109, fast arm, 16 s) — each read back from the API, not from an
  echo.
- Full-arm frequency: `gh api
  ".../actions/runs?branch=main&event=push&per_page=100"` filtered
  `name=="Tests"` — 7 on 2026-10-10.
- Recording seconds and inert_reads counts: `tests/closures.json` keys
  `recorded` (34 entries, Σ 4480 s) and `inert_reads`
  (`tests/harness_headers.py`: 540 files) at `969c3a5c84`.
- Merge cadence: `git log --merges --since=2026-10-10T00:00:00Z origin/main`
  → 12 today; 686 commits on main since 2026-10-07.
- Cause chain (§2): `tests/harness_headers.py` `_scope_paths()` at :318
  (`rounds.iterdir()` + `rglob("*")`), `closure.py affected`'s skip return,
  and the workflow's fast-arm/scoped-arm conditions in
  `.github/workflows/tests.yml` (jobs `closure-scope`, `closures`).
