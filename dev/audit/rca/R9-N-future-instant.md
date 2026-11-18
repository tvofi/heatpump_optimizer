# RCA: persisted future instant trusted without bound

Seat: round-9 RCA, class `persisted-future-instant-trusted-without-bound` (N-future-instant).
Baseline `1936d5ca` (v6.7.1); prototype cut from `origin/main` `db878b29`.
Prototype branch: `handoff/r9-rca-persisted-future-instant-trusted-without-bound` (commit named in the report).
Evidence scripts (not in the tree; run from a checkout's root with `PYTHONPATH=tests/hastub`):
`evidence/repro_loaders.py`, `evidence/repro2.py`, `evidence/usetime_clamp.py`, `evidence/time_arm.py`.

## Root cause

### Cause, reproduced on production code

An instant written into a store by the clock that ran at write time is read back by a later clock and
compared with that clock's `now`. No layer checks that the stored instant is not ahead of that clock.
When the writing clock ran ahead, every `now - stamp` window the stamp opens stays open for the
clock's whole error. The store-load boundary, `QuarantiningStore.async_load`, checks each leaf, but
its predicate is non-finite numbers only: `store.py`'s `_sanitize` docstring says it "refuses only
what is non-finite and never rewrites a healthy payload". So each loader, or each later parse of the
kept string, decides for itself, and none of them bounds the value.

S7's probes copy guard expressions. I reproduced each instance through its **real store and loader**
instead (`evidence/repro_loaders.py`). The stamp is written 400 days ahead, the restart is at T0 and
the gate is read at T0+30 d, except where a row says otherwise. Null means the same run with an
honest stamp.

| instance | baseline `1936d5ca` null / skewed | prototype null / skewed |
|---|---|---|
| legionella `due_in_hours` at d30 (**new, not in S7**) | -1032.0 / **168.0** (never due) | -1032.0 / -552.0 |
| boost `active` at d30 (D1-s3-05) | False / **True** | False / False |
| a legitimate boost, 1 h left, at T0+30 min | True / True | True / True |
| pump-arbiter echo grace open at d30 (FI-sw5) | False / **True** | False / False |
| heavy-snow damping at d30 (FI-sw2) | False / **True** | False / False |
| immersion margin at d30, 3 events (FI-sw4) | 0.0 / **2.0** | 0.0 / 0.0 |
| fuse cooldown at d10, 5-day skew, same month (FI-sw1) | False / **True** | False / False |
| outage flagged after a real 6 h cut (FI-sw3) | True / **False** | True / **False** |

For D1-s1-04 (drift, snapshots, curve, comfort), I measured the gates on production classes in
`evidence/usetime_clamp.py`: 60 days, stamp 400 d ahead, 8 snapshot takes honest against 0 skewed.
The prototype's arm drives their stores (`thermal_learning`, `snapshots`) through the boundary.

**Three corrections to S7, measured:**

1. **FI-sw1 does not hold "indefinitely".** The cooldown also requires
   `self._fuse_advisor.get("month") == month_key(now)`, and the ahead clock writes the month too.
   Measured with `evidence/repro2.py`:
   - 400-day skew: at day 30 the advisor runs, because the months differ.
   - 5-day skew: the cooldown is still held at day 10, and the advisor runs on Feb 1.

   So the stretch is at most min(skew, rest of the month). S7's `probe_fuse_advisor.py` hard-codes
   `same_month=True`.
2. **FI-sw3 is not fixed by any bound.** S7's perturbation arm clamps at NOW0 but reads at NOW0+6 h,
   which uses two clocks. In production, restore and read share one `now`
   (`_async_load_energy_totals` calls `_detect_outage` immediately). Clamping at that `now` gives
   gap 0 and the outage is still masked: `outage_flagged_clamped_same_now=False` in
   `evidence/repro.py`, and the prototype row above. When the stored `last_tick` is ahead, the gap
   is unknowable. This seam owes a decision, not a clamp:
   - treat a stored `last_tick` ahead of `now` as an outage (open the staggered window), or
   - accept one masked recovery per clock-corrected restart.
3. **A use-time clamp is a no-op at the three parse-at-use seams.** These are
   `SnapshotRing.due`, `CurveLearner._step_down` and `_immersion_dhw_margin`. The stored string is
   kept, and it is rewritten only by the action the gate blocks. I built an in-memory mutant that
   clamps inside the parse (`min(parsed, now)`, in `evidence/usetime_clamp.py`):
   - over 60 days, snapshot takes: honest 8, unfixed 0, use-time clamp 0, load-time clamp 8;
   - curve steps: honest 57, unfixed 0, use-time clamp 0, load-time clamp 57;
   - over 500 days, the use-time clamp equals unfixed (14 = 14).

   F1.9's fix note, "clamp each restored instant to the moment it is read back, at the restore
   site", is correct only if "read back" means the store load. S7's lint keys on `fromisoformat`
   call sites, and that key would accept the use-time clamp.

### Class search: what else the same cause reaches

- **Parser coverage.** S7's enumerator greps `fromisoformat` only. The sweep sees 24 sites and is
  blind to `dt_util.parse_datetime`.
  - `legionella.py:121` and `:127` restore `last_cycle` and `last_attempt` that way. This is the
    legionella row above: with a 400-day-ahead stamp, anti-legionella disinfection is postponed for
    the whole skew. `hours_since` clamps the age with `max(0.0, …)`, so the timer never runs down.
  - `binary_sensor.py:230` and `services.py:875` also call `parse_datetime`. They parse fresh plan
    steps and a service input, so they are not this class.
- **`manual_plan.py:236` and `:246`** are a persisted expiry and creation stamp, with the same
  mechanism at load. S7 assigned them to N-service-clamp (D1-s2-54, F1.4). In the prototype that
  store opts out (`lead=None`, listed with its reason) until F1.4 sets its lead.
- **`accuracy.py:406` (`lead_pending`)** holds targets that are legitimately up to
  `max(LEAD_BUCKETS)` = 24 h ahead. A skewed entry occupies one of 512 slots until it is pruned by
  position. This is not a now-gated window. The prototype bounds it at now + 24 h.
- **Guarded, not an instance.**
  - `coordinator.py:2962` (`_snow_accum_last`): `max(0.0, …)`, and it is overwritten with `now`
    every cycle.
  - `sysid.py` `last_run`: `as_dict` is diagnostics only and nothing restores it.
- **Other class.** The live-input stamps ahead of the host clock are #775, fixed by `a1bdb11c`, and
  inputs.age_of is D1-s5-01 (F4.1).
- **Beyond the boundary.** Nothing in the package persists an instant through RestoreEntity extra
  data or entry options: `git grep async_get_last_extra_data` returns nothing.
- **Introduction rate, which gives P below.** The enumerator is
  `git grep -n -E "fromisoformat|parse_datetime\(" <tag> -- 'custom_components/heatpump_optimizer/*.py'`
  diffed between `v4.0.0` and `v6.7.1`.
  - Seams added in that span: boost `until`, pump-arbiter `written`, the fuse advisor and
    legionella `last_attempt`.
  - The legionella `last_cycle` parse moved there from `coordinator.py:2829`.
  - 8 of the 10 seams already existed at `v4.0.0`.

### Process state: (c) followed and did not produce the intended result

The processes that should have caught this existed, were run, and each produced a seam-local answer.

- **Audit detection.** `tools/audit/briefs/D1.md` has carried these two steps since `58a1f2a7`
  (2026-09-02), and rounds before 9 ran them:
  - step 3: *"a frozen clock jump forward/back … `last_reported` in the future"*, applied to live
    staleness;
  - step 2: store fuzzing with *"type swaps, missing keys, `NaN`/`inf`, negative or huge numbers"*.

  Neither step's perturbation set carries a stamp across a restart under a changed clock, and that
  is the only way to reach these seams.
- **The one prior sighting was pinned the wrong way.** #1532 (R8-D3-s2-01, merged in #1598, in
  v6.6.12) found `LegionellaGuard.hours_since` fed a future `last_cycle`. The test-gap fix pinned
  *"a last cycle stamped in the future is 0 h ago, not a negative age (#1532)"*
  (`tests/features.py`, from `e0720a4c`). That pin asserts the defect: an age of 0 for the whole
  skew is the stuck disinfection timer above. The fixer, review and mutation processes were
  followed and were wrong in the direction that matters.
- **The correct answer was already in the tree for live inputs.** #775 (`a1bdb11c`, 2026-09-11)
  wrote: *"A stamp ahead of now is not freshness. Clamping to 0.0 made a … fail-open."* I
  considered state (b), because `finding-propagation.md` existed from `e4a388af` (2026-09-08) and
  no brief carries #775 (`git grep -w 775 -- tools/audit/briefs '.claude/workflows/*.json'` is
  empty). I rejected (b) as the class's state. The class has 12 seams: S7's 10 plus legionella's
  `last_cycle` and `last_attempt`. 8 existed at `v4.0.0`. Of the other 4, three came from feature
  work, which no fixer brief governs:
  - legionella `last_attempt`, `fab90cd4`, 2026-08-28;
  - boost, `07bdc557`, 2026-09-10;
  - the pump arbiter, `3b320405`, 2026-09-24.

  A carry into `fixer.md` could have reached only two things: 1 of the 12 seams, the fuse advisor
  (`1cc21935`, #840, a fix PR merged 2026-09-11T13:54, five hours after #775), and #1532's pin. So
  (b) does not explain the class.
- **The structural precedent was built with too narrow a predicate.** #1425 (round 6) closed P1 "by
  construction" at this same boundary, but only for non-finite numbers. #1518 widened it to
  wrong-type leaves, whose refusal is left to the loader. An implausible but well-formed instant is
  outside both.

A countermeasure that fits (c) extends the mechanism that was followed: widen the boundary's
predicate to cover instants relative to the reading clock. It is not a firmer instruction.

### Cost test

`cost(countermeasure, recurring) < cost(defect) × P(recurrence)`, wall-clock per release.

- **Standing cost.** The new arm adds 0.05 s median per `tests/finite_boundary.py` run
  (`evidence/time_arm.py`, 5 runs, 0.04–0.13 s). The closure of `finite_boundary.py` already
  covers all 97 package files, so the arm adds no selection and no closure change.
  - At runtime, `_bound_instants` over all 13 healthy stores takes 0.304 ms once per startup. The
    existing `_sanitize` pass takes 0.252 ms (200 iterations, same script).
  - Even at 20 gate runs per release, the arm costs 1 s per release.
- **P(recurrence).** 4 new seams in the 106 tags from `v4.0.0` to `v6.7.1` (enumerator above), so
  P = 0.038 new instances per release. The one fix attempt, #1532, sealed the defect rather than
  fixing it.
- **cost(defect).** No per-finding wall-clock is recorded for round 9 (`judge/yield.json` counts
  findings only). The lower bound is the precedent boundary PR's own wall-clock, first commit to
  merge: #1425 took 5.7 h (`f4911008`, 12 commits) and #1595 took 3.5 h (`be9a9d58`, 13 commits).
  This bound excludes finder, verify, judge and sweep seats, and it excludes field impact.
- **Verdict.** 0.038 × 3.5 h = 8.0 min = 480 s per release, against 1 s. The countermeasure passes
  by more than two orders of magnitude.
- **Field trigger.** Field trigger rates are unmeasured; the judge rated the class low. The worst
  instance is legionella, where disinfection is postponed for the length of the skew.

### The barrier

**Form:** the store-load boundary bounds every stored instant (`QuarantiningStore(…, lead=)`), and a
new arm in the existing `tests/finite_boundary.py` holds it closed.

The cost test chose this form over both alternatives:

- **S7's AST data-flow lint.**
  - It is keyed on parse call sites, so it accepts the no-op use-time clamp at 3 seams (correction
    3).
  - It must trace a raw string from `async_load` through `self` attributes to a later parse,
    thousands of lines away (`_immersion_events`).
  - It misses `parse_datetime`, as S7 did.
- **A parser helper plus a chokepoint check** (every stored parse through one helper). It needs a
  second rule, "called only from loaders", to refuse the use-time clamp, and it restructures the
  three parse-at-use seams.

The boundary rewrites the string in the payload before any loader sees it. That covers parse-at-use,
the fuse advisor's lazy read (`_maybe_run_fuse_advisor` calls `_ledger_store.async_load()`),
legionella's `parse_datetime`, and every future store and field, by construction. No raw `Store` can
bypass it: finite_boundary arm 1 already refuses one.

Prototype (`git diff --numstat` against `db878b29`):

- **`store.py`, +61 / −1.** `_bound_instants(value, bound, where)` walks the payload. A string leaf
  is an instant when it has a date and a time: `len >= 16` and a `T` or space at index 10. So a
  date-only day key is untouched.
  - A leaf later than `now + lead` is rewritten to the bound, in the leaf's own zone form, with one
    WARNING. Every other leaf passes through unchanged.
  - The default is `lead=timedelta(0)`. `None` opts a store out.
- **`boost.py`, +1:** `lead=timedelta(hours=BOOST_HOURS)`.
- **`away.py`, +1:** `lead=None`, because the return time is user-set.
- **`coordinator.py`, +4 / −6.** The accuracy store gets `lead=timedelta(hours=max(LEAD_BUCKETS))`
  and the manual-plan store gets `lead=None`. The argument lists are joined, so `coordinator_loc`
  falls 2 below its budget. The branch re-records that at 9032 in `tests/structure_budgets.json`,
  with the reason in the commit message.
- **`tests/finite_boundary.py`, +155 / −1:** Arm 5 `_instant_arm` and `LEAD_OPT_OUTS`.
  - Every loader in `LOADERS` is fed its healthy payload with every instant leaf, plus a naive and
    an aware probe leaf, set 400 d ahead.
  - What `QuarantiningStore.async_load` returns is recorded. No instant may exceed now plus that
    store's lead.
  - Null controls:
    - an honest payload comes back byte-identical;
    - an instant one minute inside the lead survives;
    - the real boost and accuracy writers at their longest lead round-trip unchanged.
  - Opt-outs must equal the reasoned `LEAD_OPT_OUTS` list, in both directions.

Demonstrated. Each run is `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py`, rc as shown:

| run | rc | what fired |
|---|---|---|
| fix reverted (`custom_components` stashed, arm kept) | 1 | `instant_escaped_total=32`, and the opt-out list mismatches |
| fixed tree | 0 | `instant_escaped_total=0`, 46 of 46 checks |
| fixed tree under `HASTUB_TZ=Europe/Stockholm` | 0 | 46 of 46 |
| M1: boost lead set to 0 | 1 | `lead_lost=['boost (writer round trip)']` |
| M2: accuracy lead set to 0 | 1 | `lead_lost=['accuracy (writer round trip)']` |
| M3: boundary default off (`lead=None`) | 1 | non-vacuity (`instants_checked=4`) and the opt-out list |
| M4: aware leaves never bounded | 1 | 11 aware probes escaped |
| M5: ledger store opted out, unlisted | 1 | opt-out list mismatch |

Null control on a healthy tree: the fixed tree passes all 46 checks, and the honest-payload arm
proves nothing is rewritten. The arm does not go green by skipping: `driven == len(LOADERS)`, the
instants checked must be at least 2 × the stores that are not opted out, and M3 shows that check
firing.

Regression runs on the branch:

- `tests/features.py`: 3374 of 3374 passed, 887 s.
- `tests/entities.py`: 1958 of 1958.
- `tests/dst_checks.py`: 51 of 51 under `HASTUB_TZ`. Without it, one check fails, and the same
  failure occurs on `origin/main`.
- `tests/rolling.py`: 33 of 33, 856 s.
- `tests/structure.py`: passes after the recorded −2.

The full scoped gate and the mutation lane were **not** run. The mutation job will list the new
guard sites in `store.py`. M1–M5 are the in-memory mutants the brief allows.

**Residuals the barrier does not close:**

- FI-sw3 (`_detect_outage`) owes the decision in correction 2.
- An in-process clock step backwards is not a persisted instant. Boost `until` moves with it
  (D1-s3-05's first half), and so does legionella's in-memory `last_cycle` (#1532's scenario).
- A store opted out with `lead=None` is unbounded by design, and the arm lists it.

## Plan fold

- **Landing PR: F3.1, not F1.9.** The boundary is the fix for F3.1's own class findings, D1-s1-04
  and D1-s3-05. It also closes FI-sw1, FI-sw2, FI-sw4 and FI-sw5 and the new legionella seam in one
  place, so it belongs in the wave-1 PR the RCA starts beside.
  - F3.1's planned "shared stored-instant parser (… a future instant is clamped)" should then
    decide the time zone only. The future bound is the boundary's job, with no second parser.
  - Measured: a parser that clamps expiries to `now` ends a legitimate boost at restart.
    `boost_legit_clamped_to_now_active_T0+30min=False` against `True` unclamped (`evidence/repro.py`).
  - If the orchestrator keeps the lane's file ownership strict (F3.1 does not touch
    `coordinator.py`), the fallback is to land the barrier in F1.9 as planned. D1-s1-04 and
    D1-s3-05 then stay open until wave 11.
- **Files.** `custom_components/heatpump_optimizer/store.py`, `boost.py`, `away.py`, `coordinator.py`
  (the two store constructions only, line-neutral or better), `tests/finite_boundary.py` and
  `tests/structure_budgets.json` (re-recorded down).
  - None is code-owned per `.github/CODEOWNERS`, and none is policy.
  - `coordinator.py` is F1's file, so F3.1 touching it adds a rebase point for F1.1 and later
    (two lines).
- **Lines.** Production is about +64 / −7 (store 61, boost 1, away 1, coordinator +4 / −6). The test
  is about +155. No `*_budgets.json` raise is needed.
- **PR set and `after` edges.**
  - **F3.2 (FI-sw5):** closed by the boundary. It adds its failing test (the echo-grace row) or
    records the instance as closed by F3.1.
  - **F1.9 shrinks to three items:**
    - the FI-sw3 decision (correction 2);
    - FI-sw1 re-dispositioned as month-bounded (correction 1), with the stretch at most
      min(skew, rest of month);
    - FI-sw2 and FI-sw4 as tests only.

    It could fold into F1.10 or F1.4. Its `after: F3.2` edge becomes `after: F3.1`.
  - **F1.4 (D1-s2-54):** sets the manual-plan store's lead once `expires_at` is bounded, and removes
    `manual_plan` from `LEAD_OPT_OUTS`.
  - **F1.6 (the P1 barrier):** extends "the helper F3.1 introduced". It should extend the boundary's
    predicate in the same module rather than add a per-site helper for instants.
- **Carries owed** (finding-propagation.md; this seat writes no briefs, so the orchestrator
  delivers them):
  - **F3.1 brief:**
    - the future bound lives at the boundary, and expiries need a lead (measured above);
    - the legionella seam is an instance;
    - `tests/features.py`'s #1532 comment and check call "0 h ago" correct. Re-read them: they stay
      valid only for an in-process step back.
  - **F1.9 brief:**
    - corrections 1–3: the use-time clamp is a no-op, FI-sw3 is a decision, FI-sw1 is
      month-bounded;
    - S7's probes are not the failing tests for FI-sw1 or FI-sw3. Use `evidence/repro_loaders.py`,
      which runs the real loaders.
  - **F3.2 brief:** FI-sw5 is closed by F3.1's boundary.

## Needs tvofi (policy proposals only; nothing landed)

1. **`tools/audit/briefs/D1.md` step 2 (addresses (c)).** Add one perturbation to the store-fuzz set:
   an instant written by a clock ahead of the one that reads it back, driven across a restart. This
   is the combination steps 2 and 3 each missed.
2. **`tools/audit/briefs/fixer.md` (addresses the (b)-shaped contributor).** Carry #775's refusal:
   an age computed from a stamp ahead of the reading clock is unknowable, never 0. #1532 pinned the
   technique #775 had refused.
3. **No budget raise is needed.**
