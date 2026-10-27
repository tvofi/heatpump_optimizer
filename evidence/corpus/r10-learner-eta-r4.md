R10-LEARNER-ETA (G-ID-4, STUDY R10-IDENT Q3). Part of #2260: the roster's
`fixes` is empty for this group, so it does not close here; the orchestrator
verifies it after the merge.

The study found no honest "days until converged" while a learner is settling:
its count and drift ETAs, scored against the true settle day on synthetic
plants, were weeks early. The learning view now publishes `learner_progress`,
one entry per thermal learner (`house`, `lower`, `solar`, `gains`):

- `phase`: `off` (disabled, or not measurable here: `lower` without a
  two-zone model and a lower-floor sensor), `counting`, `settling` or
  `waiting`;
- `progress`: while counting, `samples / samples_needed`; while settling, the
  fraction of the learner's EWMA walk traversed (`house_loss_confidence` for
  the house and lower learners, their shared `HOUSE_LOSS_ALPHA` law; one
  `SOLAR_APERTURE_ALPHA` step per sample past its gate for the aperture);
  `None` for the gains profile once settling, which keeps no count of its own;
- `waiting_for`: `colder` (the folds' own ΔT gate, `HOUSE_LOSS_MIN_DELTA`, on
  the reading in force) or `sunnier` (`SOLAR_APERTURE_MIN_IRRADIANCE`); set
  only in `waiting`, which needs a blocked gate now and nothing counted over
  the rate window;
- `eta_days`: **only while counting**, `(samples_needed - samples) / rate`,
  the rate measured since the newest weekly snapshot at least a day old
  (`MIN_RATE_WINDOW_DAYS`); a stamp ahead of the clock is passed over (fixer.md
  step 16), and a count below the snapshot's (a restore) reads as nothing
  counted.

The counting gates are the learners' own predicates, never a second
threshold: `house_loss_converged` for the house (the Health tab's "learned"),
the aperture's `SOLAR_APERTURE_MIN_SAMPLES`, and `internal_gains_gate_open`,
the gains fold's `INTERNAL_GAINS_MIN_UA_CONFIDENCE` gate extracted so
`_fold_internal_gains` and the view read one function. `gate_count` finds the
target count by searching the predicate itself, so no count is re-spelled.

**Architecture.** A read-only view, no new state (the architect note). The
rule lives in a new pure module, `learner_progress.py` (no `homeassistant`
import); `coordinator.learner_progress_view` is a module-level adapter handed
explicit values (state, parameters, config, the snapshot ring, the three
counts), never the coordinator, so it is outside the class and its seam
table. Alternatives, and why each lost:
- the helper handed the coordinator: `class_excess_loc` +51, `max_class_loc`
  +1 and more seam crossings, measured on this branch's first round;
- passing `_thermal_learning_payload()` so the counts now and in a snapshot
  are read by one path: it builds the whole store payload every cycle and
  imports its NaN refusal (#773's `a non-finite aperture n does not wedge
  _learning_view` went red on a NaN cop-baseline count);
- a "settled" phase: no value history exists without new state, and the
  study's own SETTLED flag was false most of the time it was raised.

**The `seam_cut_total` red, and why no payment is owed.** The branch once
recorded `710 -> 707` for binding the snapshot ring once in `_learning_view`
(four `self._snapshot_ring` reads to one). #2711 (R10-STRUCTURE-ALIAS)
re-defined the metric to price distinct pairs, under which four reads of one
attribute and one read are the same pair: under main's `tests/structure.py`
this branch's previous code head `33418e1e8` and its old base `50af6174f`
both read `seam_cut_total=420`. The merge-main bot's `5a8b029f5` resolved
`tests/structure_budgets.json` through `tools/merge/ledger_merge.py`, which
by design takes base plus both deltas on a count (`710 + (-3) + (420 - 710)
= 417`), so the row asked for a gain the code under the new rule never made.
`b6dad803a` restores the row to main's own 420, with the reason in its commit
message: `git diff origin/main HEAD -- tests/structure_budgets.json` is
empty, so no budget moves against main and no raise is made. Every other
`RESULT` line `tests/structure.py` prints is identical at the head and at
origin/main (`## Figures`). Payments considered and not taken: re-binding
more coordinator attributes to locals in `_learning_view` moves no
distinct pair under the new rule; any other cut of 3 would be a payment for
a growth this branch does not make, which is the step-17 shape fixer.md
refuses ("never move a metric by a change that does not improve the code").

`dev/audit/harnesses/r10_learner_eta.py` is this PR's instrument: the
finder's harness scores estimators the tree never shipped, so it reads flat at
both ends (fixer.md step 3); the companion drives the same plants and reads
the published view.

## Head

`b6dad803a2fe8184a0e5cd3d80f36d3eb0ac0182` is the code head, measured
throughout: the PR head `5a8b029f55ea7cc893f115cbb49737ba8c9d4931` (the
previous handoff head `33418e1e8` plus the bot's merge of main and the
delivery row), one merge of origin/main
`662a3809ced43b41dba2166f04277f2d3c95e991` (`a78d34bd9`, now the merge base;
main's tip when merged). At 2026-10-25T03:30Z (`date -u`) main had moved to
`ab00437c9`; `git merge-tree --write-tree origin/main HEAD` reports no
conflict, so the branch is not re-merged before the handoff (fixer.md step 6), and the budget commit
`b6dad803a`. The merge was clean; main's delta since the PR head's base
touches no file under `custom_components/`, no `tests/features.py`,
`tests/finite_boundary.py`, fixture or harness. Every figure below was
re-taken at `b6dad803a` (or at `662a3809c` where named) in this pass.

## Mutation proof

Failing test first: the head's `tests/features.py` on the merge base's
production files stops at `ImportError: cannot import name
'internal_gains_gate_open'`.

Each mutant is one exact production-text replacement in a fresh detached
worktree at `b6dad803a`, driven by the script named with
`PYTHONPATH=tests/hastub`; every one exited 1. The null mutant (a comment
appended to `MIN_RATE_WINDOW_DAYS = 1.0`, same driver) exited 0 with `ALL
4367 FEATURE CHECKS PASSED`.

| mutant | production text replaced | script | red checks |
|---|---|---|---|
| M1 | `if needed is not None and needed > n:` -> `if needed is not None:` | `tests/features.py` | `R10-LEARNER-ETA: no settling learner carries a day count, on any weather or rate`; `... settling progress is the learner's own EWMA walk, never a time`; `... off when disabled or unmeasurable; zero evidence counts with no ETA`; `... the ΔT and irradiance edges admit a sample, and the gate count settles` |
| M2 | `if days < MIN_RATE_WINDOW_DAYS:` -> `if False:` | `tests/features.py` | `R10-LEARNER-ETA: no rate from a future stamp, a count rolled back or a window under a day` |
| M3 | `learner.blocked_by is not None and rate is None` -> `learner.blocked_by is not None` | `tests/features.py` | `R10-LEARNER-ETA: no settling learner carries a day count, on any weather or rate` |
| M4 | `return "colder" if zone - outdoor < HOUSE_LOSS_MIN_DELTA else None` -> `return None` | `tests/features.py` | `R10-LEARNER-ETA: a stalled learner says what weather it waits for, with no day count` |
| M5 | `internal_gains_gate_open`'s body -> `return house_loss_converged(house_samples)` | `tests/features.py` | `#2223: a heat-loss level exactly on the confidence threshold has converged`; `R10-LEARNER-ETA: the gates are counted on the learners' own predicates` |
| M6 | the house gate `house_loss_converged` -> `None` | `tests/features.py` | `... a counting gate's ETA is its remaining count at the measured rate`; `... a stalled learner says what weather it waits for, with no day count`; `... off when disabled ...`; `... no rate from a future stamp ...`; `... a malformed or count-less snapshot gives no rate and never raises`; `... the ΔT and irradiance edges ...` |
| M7 | `walk = max(0, samples - SOLAR_APERTURE_MIN_SAMPLES)` -> `walk = max(0, samples)` | `tests/features.py` | `R10-LEARNER-ETA: settling progress is the learner's own EWMA walk, never a time`; `... the ΔT and irradiance edges ...` |
| M8 | `name: int(n) if np.isfinite(n) else 0` -> `name: int(n)` | `tests/features.py` | `a non-finite aperture n does not wedge _learning_view`, then stops at `ValueError: cannot convert float NaN to integer` |
| M9 | `solar_wait = "sunnier" if ... else house_wait` -> `solar_wait = house_wait` | `tests/features.py` | `R10-LEARNER-ETA: a stalled learner says what weather it waits for, with no day count` |
| M10 | `(learner.rate_per_day or 0.0) > 0.0` -> `learner.rate_per_day is not None` | `tests/features.py` | stops at `ZeroDivisionError: division by zero` |
| M11 | `_snapshot_count`'s `if not isinstance(value, Mapping): return None` deleted | `tests/finite_boundary.py` | `no single-leaf malformation of a store raises, or installs a non-finite, naive, absurd-magnitude or wrong-type value anywhere the coordinator owns (class P1)` (`seams=3`) |
| S2 | `zone - outdoor < HOUSE_LOSS_MIN_DELTA` -> `<=` | `tests/features.py` | `R10-LEARNER-ETA: the ΔT and irradiance edges admit a sample, and the gate count settles` |
| S3 | `"sunnier" if irradiance < SOLAR_APERTURE_MIN_IRRADIANCE` -> `<=` | `tests/features.py` | the same edge check |
| S4 | `params.two_zone_enabled and bool(config.lower_floor_temp_entity)` -> `or` | `tests/features.py` | `R10-LEARNER-ETA: the lower learner is off unless both the two-zone model and its sensor exist` |
| S5 | `MIN_RATE_WINDOW_DAYS = 1.0` -> `2.0` | `tests/features.py` | `R10-LEARNER-ETA: no rate from a future stamp, a count rolled back or a window under a day` |
| S6 | `if taken is None: continue` deleted | `tests/features.py` | `R10-LEARNER-ETA: a malformed or count-less snapshot gives no rate and never raises` |
| S7 | `if days < MIN_RATE_WINDOW_DAYS:` -> `<=` | `tests/features.py` | `R10-LEARNER-ETA: no rate from a future stamp, a count rolled back or a window under a day` |
| S8 | `if then is not None:` -> `if True:` | `tests/features.py` | stops at `TypeError: unsupported operand type(s) for -: 'int' and 'NoneType'` |
| S9 | `_snapshot_count`'s bool/number type guard deleted | `tests/features.py` | stops at `TypeError: must be real number, not NoneType` |
| S10 | `needed > n` -> `needed >= n` | `tests/features.py` | `... no settling learner carries a day count ...`; `... settling progress ...`; `... off when disabled ...`; `... the ΔT and irradiance edges ...` |
| S11 | `walk = max(0, samples - SOLAR_APERTURE_MIN_SAMPLES)` -> no clamp | `tests/features.py` | `R10-LEARNER-ETA: the ΔT and irradiance edges admit a sample, and the gate count settles` |
| S12 | the rate clamp `> 0.0` -> `>= 0.0` | `tests/features.py` | stops at `ZeroDivisionError: division by zero` |
| S13 | `lambda n: n >= SOLAR_APERTURE_MIN_SAMPLES` -> `>` | `tests/features.py` | `R10-LEARNER-ETA: a counting gate's ETA is its remaining count at the measured rate` |

The ledger: `python3 tests/mutation_table.py --scope changed --base
origin/main --max 0` at the head prints `3990 unpinned site(s) of 6326
candidate sites, 3990 at the ratchet base 662a3809c...` and `MUTATION TABLE
PASSED (empty pool)`: this diff adds no unpinned site (its 28 sites were
pinned under `killed_by` by `tests/features.py` in `70292720d`).

## Null control

- The null mutant above: same driver, a comment-only change, exit 0.
- The companion at the merge base `662a3809c` reads `field=absent`; at the
  head `eta_on_settling=0`. Its own detector, mutant M1 at the head: it reads
  `eta_on_settling=853`.
- The finder's harness at the base and at the head prints the same lines bar
  `wall_s`/`load1`/`thread_factor` (the `diff ... && echo` line under
  `## Figures`): it measures estimators the tree never shipped, so flat is the
  expected reading, and the companion carries the measurement.
- Plant E0 (prior = truth): the house gate still opens at a count; the view
  counts toward it and publishes no ETA once past it.
- `--alpha-scale 2`: the house gate's count falls with `HOUSE_LOSS_ALPHA`
  (`phase_counting` 22 -> 8 checkpoints) and `gate_err` stays within a day.
- `seam_cut_total`: the null control for "the branch moves no distinct pair"
  is origin/main itself, which reads the same 420 as the head; under the
  retired rule (`tests/structure.py` at `50af6174f`) the same two trees'
  predecessors read 710 and 707, so the instrument does separate them when
  the rule counts occurrences.
- The step-8 census at origin/main returns 36 keys, at the head 37: the
  added one is `learner_progress.py`'s `eta_days`.

## Figures

Instruments; the figures they print are in their output at the head named.

- Companion,
  `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_learner_eta.py --study "$X/dev/audit/rounds/round10/study-ident"`
  (`$X` = `git archive 4f2d513c9 dev/audit/rounds/round10/study-ident`
  extracted; harness sha1 `3c60bc36a4aa21adef7245b0ced2f6192ece22e8`), all
  seven plants, at `b6dad803a`: `field=present`, `eta_on_settling=0`;
  `gate_err` p10/p50/p90 `-0.0/+0.1/+0.1` d (n=8); `settle_err`
  `-36.2/-35.8/-35.8` d (n=7) -- the same ETAs read as convergence are five
  weeks early, which is why the figure names the gate; phases `counting=22
  settling=1147 waiting=7`. At `662a3809c` (the same harness file, run from
  that tree's root): `field=absent`. `--alpha-scale 2`: `eta_on_settling=0`,
  `gate_err` `-0.2` d (n=1). `--plants E0`: `eta_on_settling=0`, `gate_err`
  `+0.1` d (n=1). Under mutant M1: `eta_on_settling=853`.
- Finder's harness, `$X/dev/audit/rounds/round10/study-ident/eta_rolling.py`
  (sha1 `ea7de4d76e3a698650b4b2be9608efa8f918b48a`, with `ident_rolling.py`
  sha1 `3755ee80dd71a8d05e2ea2a4c6b317c63fa4ed79`), all plants:
  `diff <(grep -v "wall_s\|load1\|thread_factor" base.txt) <(grep -v "wall_s\|load1\|thread_factor" head.txt) && echo IDENTICAL_EXCEPT_TIMING`
  printed `IDENTICAL_EXCEPT_TIMING` (base `662a3809c`, head `b6dad803a`, 99
  lines each); its `pooled.house.err_count` reads p50 `-28.7` d at both.
- Step 8, the class's seams. Rule:
  `grep -noE '"[a-z_]*days[a-z_]*"\s*:' custom_components/heatpump_optimizer/*.py`
  (every published key naming days). Of what it returns, `learner_progress`'s
  `eta_days` is the one forward day figure, closed in this diff; the rest are
  elapsed-evidence counts or settings, not ETAs: `accuracy` `settled_days` /
  `required_days` (a counting gate published as counts, no forward figure),
  `curve_learning.comfortable_days`, `price_model` `days`/`days_seen` and
  their quarter, weekday and weekend twins, `snapshots`/`store` `bias_days`,
  the tariff and grid-fee peak-day settings (`peak_days`,
  `peak_distinct_days`, `peak_tariff_distinct_days`, `*_weekdays_only`),
  `legionella` `interval_days`/`overdue_days`, the `config_flow` and
  `thermal_model` interval settings, `open_meteo.forecast_days`, `optimizer`
  `window_days`/`distinct_days`, `price_tiles` `days`/`horizon_days`,
  `debugger.days`, `dhw_schedule.weekdays`. No other ETA.
- `python3 tests/structure.py` at `b6dad803a`: exit 0, `seam_cut_total=420`
  against the budget 420; at `a78d34bd9` (before the budget commit):
  `FAIL seam_cut_total 420 > 417 (+3)`. The `RESULT` lines at the head and
  at `662a3809c` are identical
  (`diff <(python3 tests/structure.py | grep RESULT) <(cd "$MAIN" && python3 tests/structure.py | grep RESULT) && echo IDENTICAL`,
  `$MAIN` a worktree at `662a3809c`). Main's `tests/structure.py` copied over
  `50af6174f` and over `33418e1e8` reads `seam_cut_total=420` on both.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture
  score: dS +0.0006 IMPROVES` (`coord_footprint 2463 -> 2462`).
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`
  at `b6dad803a`: `CI PREDICT: no closures, fast, wave-script or instrument
  red predicted against 662a3809ced4`.
- Scoped gate at `b6dad803a`,
  `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`
  (`HPO_TYPING_PYTHON` set): `MODE: SCOPED -- 28 script(s) run, 5 scoped
  out.`; every script ran green (`ALL 4367 FEATURE CHECKS PASSED`,
  `tests/env_drift.py --all 662a3809c...`, `tests/stress.py`,
  `tests/harness_headers.py`, `tests/finite_boundary.py`,
  `tests/typing_ruler.py` and `tests/structure.py` among them) but
  `tests/entities.py`, `2 of 2429 ENTITY CHECKS FAILED`, the two base-red
  checks under `## Red checks`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` at `662a3809c`: `2 of
  2429 ENTITY CHECKS FAILED`, the same two non-self-test names.
- `GOLDEN_MODE=drift`: the five `coord_*` fixtures' one moved leaf path,
  `data.learner_progress`, stays claimed in `tests/golden/claimed_drift.txt`;
  `tests/env_drift.py --all` and `--claims-only` against `662a3809c` pass.

## Red checks

- `tests / fast (3.14)`: `python3 tests/structure.py` refused
  `seam_cut_total 420 > 417 (+3)` at `5a8b029f5`. The cause is the merge, not
  the code: `tools/merge/ledger_merge.py` summed this branch's `-3` (recorded
  under the retired occurrence rule) onto main's re-defined 420, which its
  own docstring accepts ("the driver can be wrong only loudly", re-checked by
  `tests/structure.py`). The cheaper detector named by the rule,
  `tests/structure.py` in `prepr.sh` before the handoff, did run, at the
  previous handoff head `33418e1e8`, and passed there (707 against 707): the
  red was born in a commit no seat's prepr runs, the merge-main bot's
  `5a8b029f5`, and the fast lane, ~30 s of `tests/structure.py`, is the
  detector that fired one cycle later. A cheaper one would be the merge-main
  bot running `tests/structure.py` whenever the driver merged a
  `structure_budgets.json` count numerically, at ~30 s on such merges only;
  it is not built in this PR (outside its scope), and the root-cause seat
  owns that call. Repaired by `b6dad803a`.
- `pr-contract`: the previous body's `## Red checks` did not name
  `tests / fast (3.14)`; this body names it above.
- `gate` ("still being judged"): the codescan wait race
  (R10-RCA-CODESCAN-WAIT #2756, R10-GATE-DEFER #2770), not this diff.
- `tests/entities.py` (locally, `tests / fast`): `gate-sweep.yml: on CI's
  completion, no concurrency, ...` and `graders-head-copy's delivery_status
  step is red only when this copy's exit differs from the base copy's, ...`
  fail here and at origin/main `662a3809c` alike, so they are this
  environment's or main's, not this diff's; this diff touches neither
  workflow. No cheaper detector is owed by this PR.

## Forward-carry

- R10-UX-HEALTH renders this field: a day figure from `eta_days` alone,
  labelled as the gate, and a settling learner shows progress and no day
  figure; control `r10_learner_eta.py`'s `eta_on_settling` and a card
  fixture. Landed in the roster's carry list for the group by
  `tools/audit/seat/roster_edit.py append-carry`, commit `80ae03fbf` on this
  branch (an ancestor of the head),
  `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-UX-HEALTH

## Friction

none
