# Pre-study: scoping and speeding `coverage` and `fast (3.14)` — where the ~50–60 minutes go, and what may be cut

Round-9 pre-study seat `r9-covfast-scoping-prestudy`, dispatched by the
orchestrator on tvofi's request (investigate whether the `coverage` and
`fast (3.14)` CI gates could be safely sped up and/or scoped; alternatives
and a recommendation for a decision; the fixes then become a prioritized
instrument pull request). Study only — no fix PRs from this seat, no
production file changed. Baseline **`origin/main` = `6be88834e`** (2026-10-10,
the merge of #2125) — the same head whose push run the orchestrator watched.
Worktree `/Users/timmalmstrom/hpo-seats/r9pre-covfast/wt`; run logs fetched
read-only via `gh api` from this macOS box. The suite was NOT run locally
(the brief forbids a local timing; it is not comparable anyway) and
`tests/derive_closures.sh` was not run at all; every timing below is read out
of a CI log cited by job id, or out of committed data files. No number is
estimated; what could not be measured is marked **unmeasured** in §7.

## The safety property, stated and held

Two gates, two properties, both applied to every alternative in §4:

1. **`coverage` → `coverage-ratchet`.** Every pull-request head and every
   push to main produces a `coverage.json` — the union of executed-line sets
   of `custom_components/heatpump_optimizer` over the default-gate scripts —
   and the base's pinned `tests/coverage_ratchet.py` grades it against
   `tests/coverage_budgets.json`: a package floor with a ceiling, a
   **per-module** floor (a module dropping is caught where the ratio was
   blind, #1401), the config flow pinned at exactly full, and a pragma count
   that only falls. A coverage drop, a new `# pragma: no cover`, or a module
   falling below its record must redden the head that caused it — on the PR
   when the measurement sees it, at the latest on the push that merges it.
   The budgets file is a `*_budgets.json`: loosening it is a raise and merges
   only on the owner's approving review (`budget-raise-gate`, 0013). **This
   study touches no budgets file.**
2. **`fast (3.14)`.** The suite's pass/fail verdict on the interpreter
   reported installations run (3.14), uninstrumented, drift mode. A behaviour
   regression reachable by the diff must be caught on the PR (scoped) or on
   the push (full) — the CLAUDE.md rule-1 pattern.

A change that lets a regression land green — a coverage drop unmeasured, a
behaviour change untested on the pinned interpreter — is refused whatever it
saves. tvofi's standing direction of 2026-10-10 (gate lease up to four
concurrent heavy scripts locally) is noted: local parallelism is not the
constraint here; everything below is about CI.

## 1. Where the time goes (measured)

### 1.1 The run the orchestrator watched

Push run `38076804408` (main `6be88834e`, started 18:41:36Z), job timings
from the API:

| job | started | finished | wall |
|---|---|---|---|
| `fast (3.14)` | 18:41:39Z | 19:33:56Z | **52 m 17 s** |
| `coverage` | 18:41:39Z | 19:42:40Z | **61 m 01 s** |
| `coverage-ratchet` | 19:42:43Z | 19:42:51Z | 8 s |
| `closures` | 18:41:39Z | 19:27:27Z | 45 m 48 s |

The orchestrator's "~46 min and counting" at 19:27Z was real but not the
end: **`coverage` finished at 19:42:40Z — 61 m 01 s**, and it, not `closures`
(45 m 48 s) or `fast` (52 m 17 s), was the run's critical path. The three ran
in parallel from one checkout event; the workflow's wall was `coverage`'s.

### 1.2 `fast (3.14)` decomposition (job `114285379973`)

`tests/run.sh` runs three lanes in parallel (units, golden, e2e), then
`stress.py` alone after all lanes (its CPU-time budgets need the box quiet).
The manifest at the end of the log:

| lane | contents (wall) | lane total |
|---|---|---|
| units (off path) | `arch_score.py` 912 s, `features.py` 711 s, `harness_headers.py` 193 s, `entities.py` 125 s, 19 more ≤ 64 s | ≈ 2103 s |
| golden (off path) | `env_drift.py --all` 505 s (`golden.py` skipped in drift mode) | 505 s |
| **e2e (critical)** | **`boost_drift_replay.py` 2323 s**, `optimality.py` 170 s, `backtest.py` 92 s, `validate.py` 45 s, `edge.py` 34 s, card trio 24 s, `plan_view.py` 1 s | **2689 s** |
| stress (serial, after lanes) | `stress.py` | 410 s |

The printed `TOTAL (3 lane(s))` of 3100 s is the critical path — e2e lane +
stress — and the suite step (18:42:12→19:33:51) is 3099 s of the 3137 s job:
setup is noise. **`boost_drift_replay.py` is 86 % of the critical lane.**
`arch_score.py` (912 s) is large but off-path.

### 1.3 `coverage` decomposition (job `114285380026`)

The "Measure the tree" step runs `tools/coverage/coverage_tree.sh fast` —
every default-gate Python script except `env_drift`/`rolling`/`stress` and
the four end-to-end solvers (`validate`, `edge`, `backtest`, `optimality`;
`arch_score*` dropped with a byte-identical-coverage proof, R9-F10.14) —
under the coverage tracer on **3.13**, in two lanes (`W5P_LANES=2`:
`features.py` alone, everything else together). From the step's own
`ran tests/X wall=Ns` lines:

| lane | contents (wall) | lane total |
|---|---|---|
| features (off path) | `features.py` 995 s | 995 s |
| **rest (critical)** | **`boost_drift_replay.py` 2925 s**, `golden.py` 259 s (strict mode; exit 1 is not judged here), `entities.py` 190 s, `finite_boundary.py` 133 s, `config_flow_steps.py` 51 s, `structure.py` 31 s, 13 more ≤ 15 s | ≈ 3623 s |

Job 3661 s; the measurement is ≈ 3630 s of it — **99 % of the job is the
measurement**; the keying, restore, marker check, installs and combine are
seconds. `boost_drift_replay.py` is **81 % of the critical lane**. On a push
there is no reuse by design (the push *produces* the per-script base the
next PRs restore).

### 1.4 The overlap, answered precisely

The two jobs do **not** run the same suite twice. `fast` adds `stress`,
`arch_score` ×2, `harness_headers`, `env_drift --all` (drift), the four e2e
solvers and the card lanes, untraced on 3.14; `coverage` runs a strictly
smaller script set, traced on 3.13, with `golden.py` in strict mode. What
they do share is every unit-shape script (`features`, `entities`,
`config_flow_steps`, `structure`, `finite_boundary`, `manual_plan`,
`plan_view`, …) — and the **single most expensive script runs in both**:
`boost_drift_replay.py`, 2323 s untraced + 2925 s traced = **87 min of lane
time per push**, plus a third run in `closures`' re-derivation (29 m 26 s
measured in the closures pre-study; 1489.6 s committed `recorded`). One test
script is ≈ 2 h of the ≈ 2 h 40 m combined critical path of the three heaviest
jobs on every push to main.

`tests/boost_drift_replay.py` (#1935, R9-DIAG-1, landed 2026-10-05/07)
replays two boost days at 30-minute resolution against the real learners and
a real `optimize()` solve per cycle — ~288 real solves. Two facts belong to
the record: `run.sh`'s own comment prices it "Three ~2-minute arms plus unit
checks" while it measures **38 m 43 s untraced** — 4–6× the documented
intent; and its closure in `tests/closures.json` lists **83 files** (most of
the package: coordinator, optimizer, thermal_model, boost, the switch and
button surfaces), so essentially **every production-code diff reaches it**
and pays it in the scoped PR gate too.

### 1.5 The variance, explained

The orchestrator's two puzzles — "35–46 min on every head today" and "24 min
on a separate head" — are the same work on different runners. Same day, same
job type, same script list (push arms, no reuse):

| | 06:38Z push (job `114153557235`) | 18:41Z push (job `114285380026`) |
|---|---|---|
| `boost_drift_replay.py` traced | 1442 s | 2925 s |
| `features.py` traced | 468 s | 995 s |
| `golden.py` traced | 130 s | 259 s |
| `coverage` job total | 1846 s | 3661 s |

A uniform ~2× across every script — shared-runner speed, not different work.
Every duration in this document carries that ×2 band.

## 2. The premise, corrected: which heads pay the full price

"Every PR head pays all of this" is not what the workflow does. On
pull requests: `fast` runs `GATE_SCOPE=auto` (the scoped gate), and
`coverage` restores main's push-run per-script data (exact key, `.measured-by`
marker refused unless it is main's push run) and **reuses every script the
gate's scope skips** (`closure.py coverage-split`), measuring only the
scripts whose closures the diff reaches. Measured PR `coverage` jobs today:
223 s (run `38073939251`), 673 s (`38073004857`), 2802 s (`38069955370` — a
cache miss, "measuring every script"), 3639 s (`38076465867` — a diff whose
closure reaches the heavy scripts; it measured `boost_drift_replay.py` at
2918 s and `features.py` at 987 s).

The full price is paid by: **(a)** every push to main — 8 measured today —
which is deliberate: it is both the detector (red within one merge) and the
producer of the per-script base the next PRs reuse; and **(b)** PRs whose
diff reaches an 83-file closure — with `boost_drift_replay.py`'s closure
covering most of the package, that is most production-code PRs, in `fast`
and `coverage` both. The merge queue does not pay the pair at all (the
workflow keeps the non-required coverage pair off `merge_group`, running it
on the PR head and again on the merge's push).

## 3. What the checks themselves cost

`coverage-ratchet` grades in **8 s**; the keying, restore, marker check and
installs inside `coverage` are ~30 s combined; `fast`'s ref-resolution and
cache-key steps are seconds. Confirmed the orchestrator's reading for this
pair too: no alternative that touches the grading or setup steps can save
anything. The whole cost is executing the suite, and one script is most of
it.

## 4. The alternatives

### (i) Deduplicate `coverage` and `fast` into one run — REFUSED, and bounded anyway

The shared scripts besides `boost_drift_replay.py` sum to ≈ 700 s of
critical lane in each job, so the maximum saving is ~12 min per run — the
dominant cost would still run, once, traced (and the tracer costs 1.26×:
2925/2323). The costs of merging are real and documented in-tree: the
verdict lane must be uninstrumented — `features.py`'s #525 heartbeat pair
reads ZERO ticks in both arms under any tracer (`tools/coverage/coverage_tree.sh`
header; judged in `fast`, never under coverage) — so a traced verdict would
either fail spuriously or, worse, teach someone to weaken the check;
`golden.py` strict (coverage's choice) and drift (fast's choice) answer
different questions; and the pair already spans two interpreters (3.14
verdict, 3.13 measurement) where a single run leaves one. **Refused: the
overlap is not where the time is.**

### (ii) Scope by diff — already the design; the remaining full arm is the detector

Both jobs already scope on PRs (§2). The only unscoped arm left is the push
to main, which is rule 1's price and — specific to `coverage` — also the
**origin of the data every PR reuses** (the cache key is the base commit's
push-run measurement; a scoped push would starve the PRs' restore into
permanent misses, making PRs *slower*). Scoping it fails the safety property
and is counterproductive. **Refused.**

### (iii) Split cadence (per-PR narrow, full nightly) — REFUSED

Also already the design, one level down: per-PR scoped, per-push full.
Moving the full coverage arm to nightly breaks the reuse chain (PR keys
point at a base commit whose push run never measured — every PR a miss,
measuring everything, at a higher total cost than today) and lets a coverage
drop survive from merge to nightly — up to ~5 merges at this round's
cadence. The same verdict, and the same "red within one merge" argument, as
the closures pre-study's option (d). **Refused.**

### (iv) Shard the lanes — real, small, zero safety change

`coverage` runs two lanes with `boost_drift_replay.py` inside the "rest"
lane. A third lane for it alone (the lane split only decides *when* a script
runs; the per-script data and final combine are unchanged — the argument
already in-tree at R9-F10.15) takes the wall from ≈ 3623 s to
max(2925, 995, ~700) ≈ 2960 s: **~12 min per coverage run**, on pushes and
reach-PRs alike. `fast`: a fourth lane for `boost_drift_replay.py` takes
3099 s to max(2103, 505, 366, 2323) + 410 ≈ 2733 s: ~6 min. New failure
mode: contention inflating recordings on a 4-core runner — bounded, and
measured by the first landed run, exactly as the closures pre-study argued
for its lane rebalance. **Keep, as the cheap second item.**

### (v) Interpreter matrix — closed, not a lever

The 3.13 suite leg was retired with the tradeoff written in the workflow (a
3.13-only break in production code now reaches a user — the narrowed #514
hole, accepted once, and `tests/entities.py` keeps the README honest about
it). What remains is minimal and deliberate: one suite lane on 3.14 (what
installations run) and the coverage measurement on 3.13 (what every other
job pins). Removing either leg reopens a documented hole for no dominant
saving. **Nothing to do.**

### (vi) Make the dominant script cheaper on the lanes that do not judge it — found by this study; the real lever

- **(vi-a) A cheap recorded invocation for `coverage`** (and, flagged in the
  closures pre-study §4e, for `closures`). Coverage needs only the
  executed-line set of production code, not the verdict. The precedent is
  `golden.py`/`env_drift.py`, which get cheap recorded invocations by rule
  (`tests/closure.py`). Candidate: a documented short-replay knob (fewer
  cycles, assertions skipped — they are test-file lines, outside the
  measured source) that still drives all three arms' production surfaces and
  crosses at least one day boundary (`_async_watch_learning_drift` fires
  once per calendar day). **Proof, not assumption:** byte-identical
  per-script line set against the full invocation on Linux CI at the same
  head — the R9-F10.14 shape. The in-tree backstop makes the failure mode
  loud, not silent: a cheap invocation that stops exercising lines *lowers*
  the measured union, and the per-module floor and package floor redden.
  Saving: the 2925 s becomes the cheap invocation's wall (**unmeasured until
  proven**; bounded below by the ~700 s non-`boost` remainder). Touches
  `tools/coverage/coverage_tree.sh` and `tests/closure.py`'s recorded-argv
  rule — gate files, **not** `*_budgets.json` and not policy.
- **(vi-b) Speed the script itself.** This is the only lever that helps
  `fast`'s verdict lane, every scoped PR, and `closures` too. Evidence of
  headroom is in the tree's own words: `run.sh` prices the replay at "three
  ~2-minute arms" (≈ 6–8 min) against a measured 38 m 43 s — 4–6× over
  documented intent, uniform across runners after the ×2 variance band.
  Root shape: ~288 real `optimize()` solves (2 days × 30-min cycles × 3
  arms). Whether warm starts, batching or a shorter replay preserves every
  assertion is a **fixer's** question under `fixer.md` (failing test,
  mutation proof, null control) — flagged as the prioritized follow-up, not
  assumed here. New failure mode: a shortened replay that stops covering a
  behaviour — in `fast` nothing downstream catches that, which is exactly
  why vi-b must land as a proven fix and never as a quiet gate change.

## 5. Cost test (root-cause.md §4)

`cost(countermeasure) < cost(defect) × P(recurrence)`. The recurring cost is
lane time per push and per reach-PR. Measured today (2026-10-10, 8 push
arms, durations summed from the jobs API): `coverage` **Σ 23 823 s = 6.6 h**,
`fast` **Σ 20 005 s = 5.6 h**, `closures` **Σ 20 682 s = 5.7 h** — ≈ 17.9 h
of heavy-lane time in push arms alone, at ~5 merges/day. Per push arm,
`boost_drift_replay.py` costs ≈ 2925 + 2323 + ~1766 s ≈ **117 min ≈ 2 h**
(the 06:38-class arms half that — the ×2 runner band). PR-side total is
**unmeasured** (71 PR runs today, 4 sampled: `coverage` 223–3639 s).

| option | engineering cost | measured / bounded saving | risk |
|---|---|---|---|
| (vi-a) cheap coverage invocation | small PR + a Linux byte-identity proof | up to **~45 min per coverage run** (push + reach-PR), bounded below by ~700 s remainder | loud on failure (ratchet floor reddens); proof is the acceptance test |
| (iv) coverage third lane | one lane-split edit | **~12 min per coverage run** | contention, bounded and measured on landing |
| (vi-b) speed the replay | a fixer PR with mutation proof + null control | up to **~35 min/fast, ~40 min/coverage, ~25 min/closures per arm**, and the PR lane too | a shortened replay must be proven, not assumed |
| (i) dedupe | medium (tracer-verdict conflicts) | ≤ ~12 min | weakens the verdict lane — refused |
| (ii)/(iii) scope or nightly the push arm | small | large | breaks the detector and the PR reuse chain — refused |
| (v) drop an interpreter | small | none dominant | reopens the documented #514-class hole |

## 6. Recommendation, and the smallest first PR

**Do (vi-a) first, then (iv), then commission (vi-b) as the prioritized
fixer PR. Refuse (i), (ii), (iii); (v) is closed.** (vi-a) attacks the
measured dominant cost with a proof obligation the tree has already met once
(R9-F10.14), touches no budgets file, and its failure mode is loud. (iv) is
nearly free and stacks with anything. (vi-b) is the only thing that helps
`fast` itself and is the fix the docstring's own arithmetic asks for.

**Smallest first PR (described, not written):**

- Files changed: `tests/boost_drift_replay.py` (a documented cheap-invocation
  knob — e.g. `HPDR_SHORT_REPLAY=1` — driving all three arms and one day
  boundary, assertions skipped under it), `tools/coverage/coverage_tree.sh`
  (select the cheap invocation for this one script, the way `golden.py` gets
  strict mode), and `tests/closure.py`'s recorded-argv rule + the
  re-recording the autofix chain produces for it.
- Acceptance test: on Linux CI, at one head, the full invocation and the
  cheap invocation produce **byte-identical** `per/.coverage.boost_drift_replay`
  line sets (same combine), and the landed `coverage` job's next push run is
  green through `coverage-ratchet` with the measure step's wall measured —
  the two-run measurement the closures pre-study's acceptance test uses as
  its model. If the line sets differ, the knob is refused, not widened.
- Drivability (`pr-contract`): the `coverage` job runs the same instrument
  with the same `W5P_*` interface and still uploads the artifact the pinned
  grader reads; no check, hook or lane changes what a seat or CI must invoke.
  The PR body names `coverage` as the check it makes faster, and the gate
  still runs drivably per `gate-a-push-on-every-instrument`.

## 7. What could not be measured, and why

- **How much of `boost_drift_replay.py`'s 38–49 min is irreducible.** Needs
  Linux profiling of ~288 real solves (the box here is macOS; a local run is
  neither allowed nor comparable). The 4–6× gap to the documented "~2-minute
  arms" bounds the headroom from above, not the achievable saving from below.
- **The cheap invocation's actual wall (vi-a).** Exists only after the knob
  is written and proven; everything before that is a bound, not a number.
- **The PR-side daily total.** 71 PR runs today; job durations were sampled
  for 4 (223–3639 s). Summing a sample would be an estimate, so it is not
  summed.
- **Why the 17:00Z PR's `coverage` cache missed** (`38069955370`, base
  `969c3a5c84`) when that base's push-run `coverage` job had succeeded and
  should have saved the entry (`38067806307`): eviction, 10 GB cache
  pressure or a save-path failure — the log does not say; **unmeasured**, and
  worth one look before the reuse chain is leaned on harder.
- **Runner-speed attribution.** The ×2 band (§1.5) is measured as an
  outcome; GitHub does not publish the runner model in the job log, so its
  cause (CPU generation vs. noisy neighbour) is not distinguishable here.

## 8. Every figure's provenance

- Job timings and per-script walls, push run `38076804408` (main `6be88834e`,
  18:41:36Z): `gh api .../actions/jobs/{114285379973,114285380026,114297351597,114285380030}/logs`
  and `/runs/38076804408/jobs` — `fast` manifest lines (`13343–13375` of the
  log), `coverage` `ran tests/… wall=Ns` lines, both read back from the API.
- 06:38Z variance pair: job `114153557235` (run `38031613597`) logs, same
  extraction.
- PR-side durations and reuse/miss lines: jobs of runs `38076465867`
  (`114284404870` — reuse lines and `boost_drift_replay` 2918 s),
  `38073939251`, `38073004857`, `38069955370` (`114265227002` — the miss).
- Push-arm count and Σ durations for 2026-10-10: `gh api
  ".../actions/workflows/343082712/runs?per_page=100"` filtered `event==push
  && head_branch==main`, then `/runs/<id>/jobs` for each of the 8 (71 PR
  runs same listing).
- Suite/lane shape, stage script lists, two-lane split, tracer-blindness of
  the #525 pair, reuse mechanism and marker check: `tests/run.sh` (lanes,
  `JOBS = min(nproc, 3)`, the "#1935 … ~2-minute arms" comment),
  `tools/coverage/coverage_tree.sh` (DERIVED pattern, R9-F10.14/F10.15/F10.9b
  comments), `.github/workflows/tests.yml` (`fast`, `coverage`,
  `coverage-ratchet` jobs, merge-group exclusion comment),
  `tests/coverage_ratchet.py` (the four rows), `tests/closures.json`
  (`boost_drift_replay.py`: closure 83 files, `recorded` 1489.6 s) — all at
  `6be88834e`.
- `closures` 29 m 26 s `boost_drift_replay` recording: the closures
  pre-study (job `114258919874`), cited not re-derived.
