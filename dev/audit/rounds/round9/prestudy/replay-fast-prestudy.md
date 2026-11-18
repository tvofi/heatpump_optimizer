# PRE-STUDY: making boost drift replay faster (round-9 commission, 2026-10-12)

Owner's commission: "making boost drift replay faster, a wide and creative
study where the result must not be byte identical, it should just fill the
same purpose as the original script in a more efficient way". The
bit-identical constraint that bound vi-b is **lifted for this script only**;
production's bitwise contracts (goldens, `batchmath.row_sums`, the
scalar/batch parity in `simulate_trajectory_batch`) are untouched by
everything proposed here except where explicitly marked a *production* lever.

Study tree: `/private/tmp/r9-main` at `origin/main` = `4878463cb`
(2026-10-12). This document and its experiment driver
(`replay-experiments.py`, landed beside it) are in the tree; the rest of
the study scratch (`/private/tmp/r9-prestudy-replay` — the per-condition
module copies `bdr_*.py`, the run log `experiments.log`,
`profile/full.{log,prof}`) stayed scratch. READ-ONLY on r9-main
respected: every experiment imports the module, copies its source into the
scratch dir and edits the copy (`replay-experiments.py`), or calls its
functions.

---

## 0. Executive summary

| # | lever | measured / estimated effect on the gate run | purpose risk | verdict |
|---|---|---|---|---|
| L0 | skip `replay({})`'s empty-arms prefix | **−91 s measured** (native), zero behaviour change | none | build first, trivially |
| L1 | 12 h solve horizon (harness-only) | **−59 % measured** on an arm (260→107 s); gate est. ~630→~190 s native, CI pool 1573–2401 s → est. ~700–1000 s | settled-scale anchor moves 1.0416→1.0480; fold/tag counts byte-identical | build second |
| L2 | smoke/nightly split (freeze-unit + vent checks on PR, full replay nightly) | PR lane −~95 % of this script; nightly unchanged | PR-time detection latency only; the 11 pinned mutants stay killed (mutation lane is nightly anyway) | build third, only if L1 is judged insufficient |
| L3 | warm start `_prev_shipped_plan` | **+30 % measured** (260→339 s) — SLOWER | low, but pointless | do not build (measured) |
| L4 | `maxiter` cap in harness | **−2 % measured** (260→255 s) | low | do not build (measured) |
| L5 | exact-float reassociation of solver arithmetic for this script | not reachable: solver is production code; harness is 0.3 % of wall | — | not buildable inside this study |
| L6 | production bit-identical hot-path hoists (defrost factor memo, ~16 % of profiled wall; `_two_zone_rates` array work) | est. −10–15 % of *every* solve everywhere (Pi target too) | none if values are bit-identical (pure cache/hoist) | file as a lead / separate commission, not this study's PR |

Smallest falsifying experiment (already run): §4.4 — a 20-line source
patch of the arm replay under four conditions, timing each. It falsified
the warm-start and maxiter levers outright and validated the horizon lever
with all 12 arm assertions green.

---

## 1. Purpose inventory — what `tests/boost_drift_replay.py` exists to catch

The script (#1935, R9-DIAG-1) replays **9 days × 30-min cycles** (432
cycles; 254 pre-boost shared + 3 × 178 post-fork per arm = **788 real
production solves** per default gate run, plus 1 in `check_fork`) of the
production coordinator loop — frozen clock, fake sensors reading a *true*
house (a second `ThermalModel` with the true heat loss), real
`_update_current_state` interval learners, a real `HeatPumpOptimizer`
multi-start solve each cycle, `boost.adopt_plan`, the real
`set_channel`/`apply`/`async_set_mode` surfaces, `_record_accuracy`, and the
daily `_async_watch_learning_drift` — against two boost days through two
different surfaces. 33 `R.check` sites execute as **44 assertions** in the
default gate run (loops multiply: the band check runs per day per arm).

Grouped, with the fault class each catches and why a cheaper check cannot:

1. **Shared-prefix integrity (3 assertions, `check_fork`)** — the fork at
   cycle 254 is exactly the first boosting cycle, and every surface's
   pre-fork trace equals the surface-free arm's. Fault class: *harness
   unsoundness* — a boost surface acting before its window would be
   silently erased by the shared prefix. A cheaper check: the fork-parity
   harness (`dev/audit/harnesses/boost_replay_fork_parity.py`, ~70 solves)
   already covers the sharing equality, but only nightly; the arithmetic
   half is free.
2. **Scenario precondition (3)** — the learner had converged/settled
   before the boost days (`|pre − 1.0424| < 0.01` single-zone; day-over-day
   < 2.5 % two-zone). Fault class: the test scenario quietly stopping being
   the corruption scenario (learner changes, e.g. replay-path drift in the
   thermal model, moving the settled level out of tolerance). This is the
   one assertion group that is *sensitive to plan quality* — see §4.2.
3. **The #1935 defect itself (12)** — daily `house_heat_loss_scale` stays
   within 5 % of pre-boost across both boost days and two recovery days,
   per boosted arm and the null control. Unfixed, the scale walked to the
   0.5 trust-region floor (−50 %). No unit check can catch this: it needs
   the *closed loop* — real heat entering the true house, the learners
   replaying intervals the model did not plan, across days.
4. **Freeze suppression, scoping and resumption (9)** — zero folds inside
   window+settling-tail spans, ≥100 folds outside them, ≥20 after the last
   tail. Fault class: the freeze reason failing to fire, over-freezing
   (learning silently switched off), or never ending. Unit checks on
   `_learning_frozen` cover the predicate; only the replay proves the
   predicate is *consulted* on the real learner path at the real cycles.
5. **Accuracy-record tagging (4, `check_record`)** — boost intervals
   tagged (`boost_space`), plan prediction suppressed on exactly the
   tagged ones, untagged ones still predicted, tag survives the store
   round trip. Fault class: money/memory receipt errors specific to boost
   intervals (a mis-apportioned draw or a swallowed prediction).
6. **Freeze predicate units (16, `check_freeze_units`)** — pure unit-level
   semantics: mode/channel parity, ventilation outranking boost, the
   settling tail on expiry *and* cancel, DHW not freezing space learning,
   the tag's exact interval boundaries, the apportionment floor booking the
   whole metered draw to space, no second tail on re-select. **These need
   no replay at all** — sub-second; they are the smoke candidate.
7. **Ventilation pass-through (2, `check_vent_feed`)** — with vent tripped
   AND an overlay live, the learner still replays and feeds the CUSUM while
   folding nothing. Cheap (no replay).
8. **Follow-up two-zone arms (argv-only, not in the gate)** — the #42
   alarm never fires on the zone split; `two_zone_boost` /
   `two_zone_null`, run by hand for measurements.

**Wall-clock structure (measured, cProfile over the full default run,
native macOS, wall 1354 s under profiler; recorded solo 525–800 s, CI pool
1573–2401 s):** `cycle()` is 99.97 % of wall; `optimize()` alone is
**99.7 %**. Inside it 9,106 L-BFGS-B runs over 544,501 batched-gradient
evaluations; `simulate_trajectory_batch` 901 s (67 % cumulative), the
batched cost terms 191 s (14 %), the *scalar* `simulate_trajectory` path
128 s (9 % — the per-candidate scoring and the final trajectory replay),
`defrost._decide` 223 s cumulative under the empty defrost learner (16 %,
pure Python bucket interpolation returning 1.0), `_two_zone_rates` 137 s.
The harness's own work (asyncio, `FakeState` formatting, `day_arrays`,
`deepcopy`) is **noise** — every lever that is not "fewer solves" or
"cheaper solves" is a dead end, measured.

**Golden/claim interplay:** the script has **no golden fixtures**; neither
`tests/golden/claimed_drift.txt` nor `card_claimed_drift.txt` names it
(grep: zero hits; the claim files govern `env_drift.py`'s plan-payload
fixtures only). Its one value-bearing figure is the in-script anchor
`converged_near = 1.0424` plus the `BAND = 0.05`. So the claim-path cost of
this study is **zero claim-file churn, ever** — a one-time re-anchoring of
`converged_near` (and re-deriving the two-zone expectations if commissioned)
inside the script itself. The claim protocol's machinery (`claims-for:`,
direction, `env_drift` refusal of claimed+may-drift) is not engaged.

**Mutation obligations:** the ledger pins **11 mutants killed solely by
this script** (8 in `boost.py` — `space_boost_active`, `space_learning_frozen`,
`interval_boosted`, `BoostState.set/expire`; 3 in `coordinator.py` —
`_predicted_next_room_temp`, `async_set_mode`, `_settle_interval_diag`;
`tests/mutation_ledger/killed_by/…`, recorded against `82d1f47f`). Any
replacement must flip all 11 from rc 0 to rc ≥ 1 — that is the
mutation-equivalence acceptance test (§4.6).

### "Same purpose", operationally

A replacement fills the same purpose iff, for **each group 1–7** above, it
still catches the planted fault of that group. Concretely, the acceptance
suite a fixer runs:

- **P-1935** (group 3+4): revert the #1935 fix (e.g. `GUARD_OFF` on
  `boost.space_learning_frozen`, one of the pinned mutants) → the new
  script must go red with folds inside spans and/or the band blown.
- **P-tag** (group 5): `RETURN_DEL` on `boost.space_boost_active` (pinned)
  → red.
- **P-units** (groups 6–7): the 18 unit assertions unchanged, since the
  smoke half is the same code.
- **P-null** (the null control): the no-boost arm still converges and
  stays flat — a gain measured only on the boost arms is an artefact.
- **M-11**: `mutation_table.py --pin-killed` re-run for the 11 anchors;
  all 11 must still be killed by the new script.

The fault classes the script catches that **no cheaper arrangement
catches**: the closed-loop corruption (group 3), the consultation of the
freeze predicate on the real learner path (group 4), and the boost-interval
receipt record (group 5). Everything else is already unit-shaped.

---

## 2. Cost structure

- Default gate run: `check_fork` (3 × 254 cheap `_OneSolve` cycles + 1 real
  solve) + `replay(3 arms)` = 254 + 534 = **788 real solves** + **254 real
  solves thrown away** by `replay({})` (the follow-up call whose arm dict
  is empty on the default argv — it still runs the whole shared prefix and
  returns nothing; **measured 91.1 s native**), + 1 = 1,043 production
  `optimize` calls (profile count confirms exactly).
- Per solve (native, un-profiled): ~0.60 s (432 solves / 260.1 s measured,
  channel arm). CI's box is ~2.5–3× slower (solo 525–800 s).
- The script is `tests/closures.json`'s **most expensive row (1,489.6 s
  recorded)** — nearly 2× the next (`stress.py` 760.6). Its closure covers
  essentially every production file, so **any production diff re-runs it**
  in the scoped PR gate; and it is a mutation-pin driver at 1,573–2,401 s
  pool cost (RCA-1565: it *timed out* the lane at the 2,401 s bound on
  2026-10-08, three seconds of margin the night before).
- Levers keyed to that structure:
  - **(a) numerics** — horizon (n_steps 48→24 halves both the FD batch
    B=97→49 and the trajectory length; ~4× less work per gradient eval),
    `maxiter`, warm start. Measured below.
  - **(b) harness** — drive physics directly: irrelevant, measured — the
    harness is 0.3 % of wall; the solves *are* the scenario. "Two days
    instead of a season" is already done (9 days, was a season); the
    pre-boost prefix is already shared across arms (this script's own
    vi-era win).
  - **(c) structure** — the 18 unit assertions (groups 6–7) + the
    3 fork assertions are ≤ 5 % of wall; the split point exists in the
    code already (`check_freeze_units`/`check_vent_feed` are separate
    functions).
  - **(d) claim path** — zero (§1).
  - **(e) acceleration** — no new deps possible anyway (CI
    `--require-hashes`, Pi-class target); the only numpy-shape lever that
    matters is inside production (L6).

---

## 3. The experiments (all measured, 2026-10-12, native macOS, sequential,
box load1 2.7–4.2; identical conditions across arms)

Driver: `replay-experiments.py` (landed beside this document) — copies the
module source, applies one edit, runs the **channel_boost arm**
(prefix 254 + post-fork 178 cycles) with the arm's own 12 assertions.

| condition | wall | assertions | daily scale (day 0→8) | folds frz/out/after | tagged/untagged | hh_final |
|---|---|---|---|---|---|---|
| base (verbatim) | **260.1 s** | 12/12 ok | .9799, 1.0108, 1.0314, 1.0401, **1.0416**, 1.0425, 1.0420, 1.0420, 1.0238 | 0 / 334 / 80 | 24 / 407 | 1.0600 |
| warm (`_prev_shipped_plan`, as production's coordinator hands it) | **338.9 s** | 12/12 ok | …, **1.0419**, 1.0425, 1.0422, 1.0422, 1.0187 | 0 / 334 / 80 | 24 / 407 | 1.0578 |
| maxiter60 | **255.4 s** | 12/12 ok | identical to base | identical | identical | 1.0600 |
| **h12** (horizon_hours 24→12) | **107.4 s** | 12/12 ok | .9829, 1.0168, 1.0365, 1.0447, **1.0480**, 1.0504, 1.0430, 1.0430, 1.0283 | **0 / 334 / 80** | **24 / 407** | 1.0611 |

Readings:

- **Fold and tag counts are plan-invariant** — byte-identical across all
  four conditions including the 59 %-faster h12. Groups 4 and 5 (the
  freeze-consultation and receipt faults) do not depend on solve quality
  at all; they are functions of the schedule geometry and the freeze
  predicate. This is the strongest purpose-fidelity evidence in the study.
- **The settled scale level is plan-sensitive**: h12 moves it
  1.0416 → 1.0480 (+0.6 %). The `converged_near` anchor must move with it
  (|1.0480 − 1.0424| = 0.0056 still inside the old ±0.01, but with less
  than half the margin left — re-anchor, do not ride the tolerance).
- **Warm start is falsified as a speed lever** here: the extra candidate
  costs a 5th L-BFGS run per solve and buys fewer iterations than it
  adds. (It also *changes* numerics for no purpose gain.)
- **maxiter is falsified**: L-BFGS-B converges well below 60 iterations on
  this horizon; capping buys 2 %.
- The empty-prefix waste: `replay({})` measured **91.1 s** returning
  nothing.

---

## 4. Levers, fidelity tests, cost/risk, ranking

### 4.1 L0 — skip the empty-arms prefix (build first)

`main()` calls `replay({})` for the follow-up arms whenever none are
selected; `replay` runs the full 254-cycle shared prefix regardless of
`arms`. Guard `if not arms: return {}`. **−91 s measured** (−15 % of a
native gate run; ~−300 s of the CI pool cost), zero behavioural change,
zero claim churn, no review burden beyond reading the two-line diff.
Fidelity test: the default run's assertions and figures are *unchanged
bytes* (this is the one lever that is still byte-identical, deliberately);
`--two_zone_boost` argv path unchanged (prefix still runs when arms are
non-empty).

### 4.2 L1 — 12 h solve horizon inside the replay harness (build second)

The replay's solve is **state setup, not the thing under test**: nothing in
groups 3–5 measures plan optimality, and the measured fold/tag invariance
plus the null control's convergence show the scenario survives a shorter
horizon. Changes: `OptimizationConfig(horizon_hours=12.0)` in
`start_state`, re-anchor `converged_near` to the measured 1.0480 (and
re-derive the two-zone follow-up expectations if those arms are ever
re-measured). **−59 % measured** on an arm; gate estimate native ~630 s →
~230 s with L0, CI pool 1,573–2,401 s → est. ~650–1,000 s (comfortably
inside the RCA-1565 bound machinery either way).

Purpose-fidelity acceptance tests (the fixer runs all):
1. All 44 gate assertions green at the new anchor (measured already for
   the channel arm; mode and null arms must be re-measured — the mode
   arm's surface is plan-adjacent through the comfort ceiling).
2. **P-1935**: plant the original defect (GUARD_OFF on
   `boost.space_learning_frozen`) → script must go red (folds inside
   spans > 0 and/or band blown). The defect's mechanism — boost heat
   warming every replay residual — is plan-insensitive; measured support:
   fold counts did not move under h12.
3. **P-tag**: `RETURN_DEL` on `space_boost_active` → red.
4. **M-11**: `--pin-killed` re-run for the 11 ledger anchors; 11/11
   killed.
5. **P-null**: the no-boost arm still converges (day-over-day < 1 %) and
   stays flat — measured: h12 daily rows converge 0.9829→1.0480 with the
   same shape.
6. Document the anchor move in the PR body's figures with both old and new
   values and the mechanism sentence (plan-quality sensitivity of the
   settled level), per `fixer.md`.

Risks: the settled level's *distance to the band edges* changes (1.0480 vs
1.0424 — both far from ±5 %); a future production change that shifts the
settled level would now fault at a different place — acceptable, the
anchor is re-derivable in one run. Review burden: small; the PR must say
loudly that outputs differ (the commission licenses exactly this).
Claim-file churn: none.

### 4.3 L2 — smoke/nightly split (build only if L1 is judged insufficient)

`check_freeze_units` + `check_vent_feed` + `check_fork`'s arithmetic half
run on every PR (~5 s); the full replay moves to the nightly `slow` lane
beside `rolling.py` (`SLOW=1`). Honest cost: a PR that breaks the closed
loop reddens **hours later** (nightly), not at the PR gate; the scoped
gate's closure for production diffs loses its end-to-end check entirely on
PRs. Mitigating: the 11 pinned mutants stay killed — the mutation lane
that pins them is nightly already, so mutation equivalence survives the
split by construction. Interaction with L1: L1 alone takes the CI pool
cost under every bound the lane has ever measured; L2's residual value is
PR-lane wall time, bought with detection latency — recommend L2 only if
the owner wants PR-gate minutes back and accepts nightly latency for
groups 3–5. Structure-budget note: a split is a new tracked file → must be
classified (closure or INERT) per `entities.py`.

### 4.4 The smallest falsifying experiment (this study's own)

`experiments.py` (already run, §3): one 20-line source patch per
condition, one arm, 12 assertions, four timings on one box in one
sequential batch. It **falsified** the two levers the profile suggested
most (warm start: +30 %; maxiter: −2 %) and **validated** the horizon
lever (−59 %, all green) in ~30 minutes of wall clock. A fixer's cheaper
first step: re-run it for the mode and null arms before writing the PR.

### 4.5 L6 — production hot-path hoists (lead, not this study)

The profile's second-biggest entry is `defrost.factor`/`_decide` at ~16 %
of profiled wall — 30 M calls that all return 1.0 because the learner is
empty, each paying four bucket `_decide`s of Python. A memo keyed on the
exact `(outdoor_temp, humidity)` floats (the learner is immutable within a
solve) returns **bit-identical** values, needs no reassociation, keeps
every golden byte, and speeds *every* solve on the Pi target, not just
this script. Same family: `_two_zone_rates`' 15.6 M calls. This is a
production PR with its own mutation/golden acceptance (golden drift gate
green is the whole proof), worth a separate commission or a lead to D9.
It is NOT part of this study's deliverable because it does not need the
lifted constraint — it must stay byte-identical.

### 4.6 What this study would NOT do, with reasons

- **Warm start (L3)** — measured 30 % slower; falsified.
- **maxiter caps (L4)** — measured 2 %; the solver converges far below
  the cap; falsified.
- **Exact-float reassociation in the solver for this script (L5)** — not
  reachable: `simulate_trajectory_batch`, `row_sums` and the cost terms
  are production code shared with the goldens; the harness cannot
  reassociate them without editing production, and editing them breaks the
  golden gate the claim protocol refuses to excuse. The lifted constraint
  covers the *script's outputs*, not production's.
- **New dependencies / BLAS tuning / process parallelism inside the
  harness** — CI is `--require-hashes` pinned, the Pi target forbids heavy
  deps, and the box discipline (gate lease, shared machine) makes
  thread-count games contention-hostile; also measured-irrelevant while
  the harness is 0.3 % of wall.
- **Rewriting the replay as a physics-direct harness (drive
  `ThermalModel` + learners without the coordinator)** — would delete the
  consultation faults (group 4) and the receipt faults (group 5), i.e.
  exactly what the script exists to catch; the profile shows there is no
  harness time to save anyway.
- **Touching the claim files** — nothing to claim; a branch that claims
  nothing leaves them byte-identical (`claim-files.md`).

### 4.7 Ranking

1. **L0** (trivial, measured −91 s, zero risk) — same day.
2. **L1** (measured −59 %, re-anchor one constant, acceptance suite in
   §4.2) — the commissioned replacement.
3. **L2** (only if the owner wants PR-lane minutes and accepts nightly
   latency for the closed-loop groups).
4. **L6** as a separate production commission (bit-identical, benefits
   everything, needs no lifted constraint).

Falsification of the top candidate (L1), cheaply, before any fixer starts:
re-run `replay-experiments.py` for `mode` and `null` arms under `h12`; if either
arm's assertions fail or its fold/tag counts move, the plan-invariance
argument collapses and L1 is dead. ~20 minutes.

## Every figure's provenance

- **§3's four-condition table** (each `WALL`, the 12/12 assertion verdicts,
  the daily-scale rows, the fold and tag counts, `hh_final`): one sequential
  run per condition of the landed `replay-experiments.py`
  (`python3 replay-experiments.py <base|warm|maxiter60|h12>`), 2026-10-12,
  native macOS, identical conditions across arms; raw output in the study
  scratch's `experiments.log`. The **91.1 s** `replay({})` empty-arms figure
  (§2, §4.1) was timed in the same session against the same tree; it is
  **not** a driver output — the driver runs the `channel_boost` arm.
- **§1's profile shares** (99.97 % / 99.7 % of wall, 9,106 L-BFGS-B runs,
  544,501 batched-gradient evaluations, and the 901 s / 191 s / 128 s /
  223 s / 137 s entries): read from one `cProfile` run of the script's full
  default gate run, wall 1354 s under the profiler; artifacts
  `profile/full.log` and `profile/full.prof` in the study scratch.
- **Recorded closure seconds** (`1489.6 s`, `760.6 s`, §2): the
  `tests/closures.json` key `recorded` at `4878463cb`
  (`python3 -c "import json;d=json.load(open('tests/closures.json'))['recorded'];print(d['tests/boost_drift_replay.py']['seconds'],d['tests/stress.py']['seconds'])"`).
- **The 11 ledger mutants** (§1): `ls tests/mutation_ledger/killed_by |
  grep -c boost_drift_replay` at `4878463cb` → 11.
- **The in-script anchor** (`converged_near` default `1.0424`,
  `BAND = 0.05`, §1): `grep -n "BAND = \|converged_near: float"
  tests/boost_drift_replay.py` at `4878463cb`.
- **The CI pool 1,573–2,401 s and the 2,401 s bound** (§0, §2, RCA-1565):
  quoted from the #1565 root-cause record, not re-measured in this study.
