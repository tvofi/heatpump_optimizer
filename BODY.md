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
  fraction of the learner's EWMA walk traversed (for the house and lower
  learners `house_loss_confidence`, their shared `HOUSE_LOSS_ALPHA` law; for
  the aperture one `SOLAR_APERTURE_ALPHA` step per sample past its gate);
  `None` for the gains profile once settling, which keeps no count of its own;
- `waiting_for`: `colder` (the folds' own ΔT gate, `HOUSE_LOSS_MIN_DELTA`, on
  the reading in force) or `sunnier` (`SOLAR_APERTURE_MIN_IRRADIANCE`); set
  only in `waiting`, which needs both a blocked gate now and nothing counted
  over the rate window;
- `eta_days`: **only while counting**, `(samples_needed - samples) / rate`,
  the rate measured since the newest weekly snapshot at least a day old
  (`MIN_RATE_WINDOW_DAYS`); a stamp ahead of the clock is passed over (fixer.md
  step 16), and a count below the snapshot's (a restore) reads as nothing
  counted. A settling learner never carries one: the ETA is computed inside
  the counting branch alone.

The counting gates are the learners' own predicates, never a second
threshold (the R10-SCORES forward-carry): `house_loss_converged` for the house
(the Health tab's "learned"), the aperture's `SOLAR_APERTURE_MIN_SAMPLES`, and
`internal_gains_gate_open` -- the gains fold's `INTERNAL_GAINS_MIN_UA_CONFIDENCE`
gate on the house count, extracted so `_fold_internal_gains` and the view read
one function. `gate_count` finds the target count by searching the predicate
itself, so no count is re-spelled.

**Architecture.** A read-only view, no new state (the architect note). The
rule lives in a new pure module, `learner_progress.py` (no `homeassistant`
import); `coordinator.learner_progress_view` is a module-level adapter handed
explicit values -- state, parameters, config, the snapshot ring and the three
counts -- never the coordinator, so it is outside the class and the seam cut.
Its one call site in `_learning_view` is paid for by binding the snapshot ring
once (four `self._snapshot_ring` reads to one), which lowered
`seam_cut_total`, re-recorded in `b6c2a5ab7` with the reason in its message.
Alternatives, and why each lost:
- the helper handed the coordinator (round one of this branch):
  `class_excess_loc` +51, `max_class_loc` +1, `seam_cut_total` +6;
- passing `_thermal_learning_payload()` so the counts now and in a snapshot
  are read by one path: it builds the whole store payload every cycle and
  imported its NaN refusal (#773's check `a non-finite aperture n does not
  wedge _learning_view` went red on a NaN cop-baseline count);
- a "settled" phase: no value history exists without new state, and the
  study's own SETTLED flag was false most of the time it was raised.

`dev/audit/harnesses/r10_learner_eta.py` is this PR's instrument: the
finder's harness scores estimators the tree never shipped, so it reads flat at
both ends (fixer.md step 3); the companion drives the same plants and reads
the published view.

## Head

`681db9f0f96f678543d35e4b2601fa1faaef216c` is the measured code head; every
figure below was taken at it unless it names another commit.
- Merge base `e97f5749b441b282e43bd99dbcbb762e9d10a369`, origin/main's tip
  when `681db9f0f` merged it; at 2026-10-24T15:05Z (`date -u`) origin/main
  was `73b69fe0a`, which `git merge-tree --write-tree` merges with this head
  cleanly; `681db9f0f` merged `e97f5749b` (clean; main's delta
  since `145bfe197`, which `a7971ec3c` merged, touches `coordinator.py`,
  `inputs.py`, `const.py`, `tests/features.py`, `tests/entities.py` and
  lowered `class_excess_loc` and `max_class_loc` -- none of this diff's
  hunks).
- At the head: the scoped gate, `structure.py`, `archscore`, `ci_predict`
  and the body check. At `a562000d9` (this diff's last production commit;
  `git diff a562000d9 HEAD` moves only main's files): the S mutants, the
  harnesses and the companion. Mutants M1-M11 ran at `37607e5ad`;
  `a562000d9` then bounded the gate search and dropped two unreachable
  guards, and every M text but those is unchanged at the head.

## Mutation proof

Failing test first: the head's `tests/features.py` on the merge base's
production files stops at `ImportError: cannot import name
'internal_gains_gate_open'`.

Each mutant is one production text in a detached worktree (M at
`37607e5ad`, S at `a562000d9`), driven by the script named; every one went red:

| mutant | production text replaced | script | red checks |
|---|---|---|---|
| M1 | `if needed is not None and needed > n:` -> `if needed is not None:` (a learner past its gate keeps counting) | `tests/features.py` | `R10-LEARNER-ETA: no settling learner carries a day count, on any weather or rate`; `... settling progress is the learner's own EWMA walk, never a time`; `... off when disabled or unmeasurable; zero evidence counts with no ETA` |
| M2 | `if days < MIN_RATE_WINDOW_DAYS:` -> `if False:` | `tests/features.py` | `R10-LEARNER-ETA: no rate from a future stamp, a count rolled back or a window under a day` |
| M3 | `blocked_by is not None and rate is None` -> `blocked_by is not None` | `tests/features.py` | `R10-LEARNER-ETA: no settling learner carries a day count, on any weather or rate` |
| M4 | the `colder` return -> `return None` | `tests/features.py` | `R10-LEARNER-ETA: a stalled learner says what weather it waits for, with no day count` |
| M5 | `internal_gains_gate_open` -> `house_loss_converged(house_samples)` | `tests/features.py` | `#2223: a heat-loss level exactly on the confidence threshold has converged`; `R10-LEARNER-ETA: the gates are counted on the learners' own predicates` |
| M6 | the house gate `house_loss_converged` -> `None` | `tests/features.py` | `... a counting gate's ETA is its remaining count at the measured rate`; `... a stalled learner says what weather it waits for ...`; `... off when disabled ...`; `... no rate from a future stamp ...` |
| M7 | the aperture walk's `samples - SOLAR_APERTURE_MIN_SAMPLES` -> `samples` | `tests/features.py` | `R10-LEARNER-ETA: settling progress is the learner's own EWMA walk, never a time` |
| M8 | `int(n) if np.isfinite(n) else 0` -> `int(n)` | `tests/features.py` | `a non-finite aperture n does not wedge _learning_view` (`ValueError: cannot convert float NaN to integer`) |
| M9 | `solar_wait = "sunnier" if ... else house_wait` -> `solar_wait = house_wait` | `tests/features.py` | `R10-LEARNER-ETA: a stalled learner says what weather it waits for, with no day count` |
| M10 | the rate clamp `(rate_per_day or 0.0) > 0.0` -> `rate_per_day is not None` | `tests/features.py` | stops at `ZeroDivisionError: division by zero` (a zero rate reaches the ETA) |
| M11 | `_snapshot_count`'s `if not isinstance(value, Mapping): return None` deleted | `tests/finite_boundary.py` | `no single-leaf malformation of a store raises, or installs a non-finite, naive, absurd-magnitude or wrong-type value anywhere the coordinator owns (class P1)` (`seams=3`) |
| S2 | `zone - outdoor < HOUSE_LOSS_MIN_DELTA` -> `<=` | `tests/features.py` | `R10-LEARNER-ETA: the ΔT and irradiance edges admit a sample, and the gate count settles` |
| S3 | `"sunnier" if irradiance < ...` -> `<=` | `tests/features.py` | the same edge check |
| S4 | `two_zone_enabled and bool(config.lower_floor_temp_entity)` -> `or` | `tests/features.py` | `R10-LEARNER-ETA: the lower learner is off unless both the two-zone model and its sensor exist` |
| S5 | `MIN_RATE_WINDOW_DAYS = 1.0` -> `2.0` | `tests/features.py` | `R10-LEARNER-ETA: no rate from a future stamp, a count rolled back or a window under a day` |
| S6 | `if taken is None: continue` deleted | `tests/features.py` | `R10-LEARNER-ETA: a malformed or count-less snapshot gives no rate and never raises` (`AttributeError`) |
| S7 | `if days < MIN_RATE_WINDOW_DAYS:` -> `<=` | `tests/features.py` | `... no rate from a future stamp, a count rolled back or a window under a day` |
| S8 | `if then is not None:` -> `if True:` | `tests/features.py` | stops at `TypeError: unsupported operand type(s) for -: 'int' and 'NoneType'` |
| S9 | `_snapshot_count`'s bool/number type guard deleted | `tests/features.py` | stops at `TypeError: must be real number, not NoneType` |
| S10 | `needed > n` -> `needed >= n` | `tests/features.py` | `... no settling learner carries a day count ...`; `... settling progress ...`; `... off when disabled ...`; `... the ΔT and irradiance edges admit a sample, and the gate count settles` |
| S11 | `walk = max(0, samples - SOLAR_APERTURE_MIN_SAMPLES)` -> no clamp | `tests/features.py` | `... the ΔT and irradiance edges admit a sample, and the gate count settles` |
| S12 | the rate clamp `> 0.0` -> `>= 0.0` | `tests/features.py` | stops at `ZeroDivisionError: division by zero` |
| S13 | `lambda n: n >= SOLAR_APERTURE_MIN_SAMPLES` -> `>` | `tests/features.py` | `R10-LEARNER-ETA: a counting gate's ETA is its remaining count at the measured rate` |

`tests/mutation_table.py --pin-killed --base origin/main` (drivers: the
defaults less `tests/entities.py`, red at the merge base, and `tests/stress.py`,
never run per mutant locally; `--jobs 3`) was started at `a7971ec3c` and
stopped at this seat's two-hour job limit having finished the drivers'
baselines -- every baseline rc=0 and the null mutant `coordinator.py:511
NULL_COMMENT` survived every driver -- and no mutant. The pins are left to
`mutation-autofix`; `## Unpinned sites` names, per site, the check that kills
it, from the M and S runs above or, where marked, by reading.

## Unpinned sites

Each is pinned by `mutation-autofix` on the PR; the killing check is named,
from the M/S runs above or, marked "(read)", from the code path:

- custom_components/heatpump_optimizer/coordinator.py:1388 CMP_BOUND: `#2223: a heat-loss level exactly on the confidence threshold has converged` (read; M5 turns it red the same way)
- custom_components/heatpump_optimizer/coordinator.py:1388 RETURN_DEL: the gate answers None: `R10-LEARNER-ETA: the gates are counted on the learners' own predicates` (read)
- custom_components/heatpump_optimizer/coordinator.py:1393 CLAMP_DROP: S11
- custom_components/heatpump_optimizer/coordinator.py:1394 RETURN_DEL: settling progress None: `R10-LEARNER-ETA: settling progress is the learner's own EWMA walk, never a time` (read)
- custom_components/heatpump_optimizer/coordinator.py:1419 CMP_BOUND: S2
- custom_components/heatpump_optimizer/coordinator.py:1424 CMP_BOUND: S3
- custom_components/heatpump_optimizer/coordinator.py:1431 BOOLOP: S4
- custom_components/heatpump_optimizer/coordinator.py:1437 CMP_BOUND: S13
- custom_components/heatpump_optimizer/coordinator.py:1447 RETURN_DEL: the view is None and the first `["learner_progress"]["house"]` raises, stopping `tests/features.py` (read)
- custom_components/heatpump_optimizer/learner_progress.py:36 CONST: S5
- custom_components/heatpump_optimizer/learner_progress.py:80 GUARD_OFF: S6
- custom_components/heatpump_optimizer/learner_progress.py:83 CMP_BOUND: S7
- custom_components/heatpump_optimizer/learner_progress.py:83 GUARD_OFF: M2
- custom_components/heatpump_optimizer/learner_progress.py:87 GUARD_OFF: S8
- custom_components/heatpump_optimizer/learner_progress.py:90 RETURN_DEL: `rates["house"]` on None raises in the view, stopping `tests/features.py` (read)
- custom_components/heatpump_optimizer/learner_progress.py:97 GUARD_OFF: M11 (`tests/finite_boundary.py`), and `R10-LEARNER-ETA: a malformed or count-less snapshot gives no rate and never raises` (read)
- custom_components/heatpump_optimizer/learner_progress.py:100 GUARD_OFF: S9
- custom_components/heatpump_optimizer/learner_progress.py:102 RETURN_DEL: no snapshot count ever reads, so no rate: `R10-LEARNER-ETA: a counting gate's ETA is its remaining count at the measured rate` (read)
- custom_components/heatpump_optimizer/learner_progress.py:114 RETURN_DEL: no gate count, so nothing counts: the same check, and `... the gates are counted on the learners' own predicates` (read)
- custom_components/heatpump_optimizer/learner_progress.py:119 GUARD_OFF: a disabled learner is reported: `R10-LEARNER-ETA: off when disabled or unmeasurable; zero evidence counts with no ETA` (read)
- custom_components/heatpump_optimizer/learner_progress.py:123 CMP_BOUND: S12
- custom_components/heatpump_optimizer/learner_progress.py:127 BOOLOP: `or` keeps a learner past its gate counting, as M1: `... no settling learner carries a day count, on any weather or rate` (read)
- custom_components/heatpump_optimizer/learner_progress.py:127 CMP_BOUND: S10
- custom_components/heatpump_optimizer/learner_progress.py:127 GUARD_OFF: M1 (its text is this guard's effect for every gated learner)
- custom_components/heatpump_optimizer/learner_progress.py:129 GUARD_OFF: a counting learner with no rate divides by None, stopping `tests/features.py` at the zero-evidence arm (read)
- custom_components/heatpump_optimizer/learner_progress.py:134 BOOLOP: `or` makes a fresh, unblocked learner wait: `... off when disabled or unmeasurable; zero evidence counts with no ETA` (read)
- custom_components/heatpump_optimizer/learner_progress.py:134 GUARD_OFF: every learner waits: `R10-LEARNER-ETA: a counting gate's ETA is its remaining count at the measured rate` (read)
- custom_components/heatpump_optimizer/learner_progress.py:136 RETURN_DEL: the view's entries are None, stopping `tests/features.py` (read)

## Null control

- The companion at the merge base reads `field=absent`; at the head
  `eta_on_settling=0`. Its own detector: under mutant M1 (a learner past its gate keeps
  counting) it reads `eta_on_settling=853`.
- The finder's harness at the base and at the head prints the same lines
  bar `wall_s`/`load1`/`thread_factor` (the `diff ... && echo` line under
  `## Figures`): it measures estimators the tree never shipped, so flat is the
  expected reading, and the companion carries the measurement.
- Plant E0 (prior = truth): the house gate still opens at a count; the view
  counts toward it and publishes no ETA once past it.
- `--alpha-scale 2`: the house gate's count falls with HOUSE_LOSS_ALPHA and
  `gate_err` stays within a day of zero.
- The scoped gate at the head (`MODE: SCOPED`) ran every script the diff
  reaches; the two `tests/entities.py` failures it shows are red at the merge
  base too (`## Red checks`).

## Figures

Instruments; the figures they print are in their output at the head named.

- Companion, `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_learner_eta.py --study "$X/dev/audit/rounds/round10/study-ident"`
  (`$X` = `git archive 4f2d513c9 dev/audit/rounds/round10/study-ident`;
  harness sha1 `3c60bc36a4aa21adef7245b0ced2f6192ece22e8`), all seven plants:
  `eta_on_settling=0`; `gate_err`
  p10/p50/p90 `-0.0/+0.1/+0.1` d (n=8); `settle_err` `-36.2/-35.8/-35.8` d
  (n=7) -- the same ETAs read as convergence are five weeks early, which is
  why the figure names the gate; phases `counting=22 settling=1147
  waiting=7`. At `50af6174f`: `field=absent`. `--alpha-scale 2`:
  `eta_on_settling=0`, `gate_err` `-0.2` d (n=1). `--plants E0`:
  `eta_on_settling=0`, `gate_err` `+0.1` d (n=1). Under mutant M1:
  `eta_on_settling=853`.
- Finder's harness, `$X/dev/audit/rounds/round10/study-ident/eta_rolling.py`
  (sha1 `ea7de4d76e3a698650b4b2be9608efa8f918b48a`, with `ident_rolling.py`
  sha1 `3755ee80dd71a8d05e2ea2a4c6b317c63fa4ed79`), all plants:
  `diff <(grep -v "wall_s\|load1\|thread_factor" base.txt) <(grep -v "wall_s\|load1\|thread_factor" head.txt) && echo IDENTICAL_EXCEPT_TIMING`
  printed `IDENTICAL_EXCEPT_TIMING` (base `50af6174f`, head as above); its
  pooled house `err_count` reads p50 `-28.7` d at both.
- Step 8, the class's seams. Rule:
  `grep -noE '"[a-z_]*days[a-z_]*"\s*:' custom_components/heatpump_optimizer/*.py`
  (every published key naming days). Of what it returns, `learner_progress`'s
  `eta_days` is the one forward day figure, closed in this diff; the rest are
  elapsed-evidence counts or settings, not ETAs: `accuracy.settled_days` /
  `required_days` (a counting gate published as counts, no forward figure),
  `curve_learning.comfortable_days`, `price_model` `days`/`days_seen` and
  their quarter twins, `snapshots`/`store` `bias_days`, the tariff and
  grid-fee peak-day settings, `legionella` `interval_days`/`overdue_days`,
  `config_flow`/`thermal_model` interval settings, `open_meteo.forecast_days`,
  `optimizer` `window_days`/`distinct_days`, `price_tiles` `days`/
  `horizon_days`, `debugger.days`, `dhw_schedule.weekdays`. No other ETA.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`;
  `seam_cut_total` re-recorded `710 -> 707` (`b6c2a5ab7`).
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture
  score: dS +0.0006 IMPROVES` (`coord_footprint 2463 -> 2462`).
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`:
  `CI PREDICT: no closures or fast red predicted against e97f5749b441` and
  `28 unpinned site(s) the diff adds`.
- Scoped gate, `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh`:
  `MODE: SCOPED -- 28 script(s) run, 5 scoped out.`; every script in scope
  passed (`ALL 4367 FEATURE CHECKS PASSED`, `ALL 113 STRESS CHECKS PASSED`,
  `ALL 112 HARNESS HEADER CHECKS PASSED`, `tests/env_drift.py --all` and
  `tests/typing_ruler.py` under `HPO_TYPING_PYTHON` among them) but
  `tests/entities.py`, `2 of 2425 ENTITY CHECKS FAILED`, the two base-red
  checks under `## Red checks`.
- `GOLDEN_MODE=drift` (`tests/env_drift.py --all` against the merge base):
  exactly the five `coord_*` fixtures move, one leaf path each,
  `data.learner_progress: present on one side only`; claimed in
  `tests/golden/claimed_drift.txt`, the committed files patched in that path
  alone (24 leaves each) from a head recording. A head recording here also
  moves 83-97 float leaves per fixture, which is why nothing else was
  re-recorded.
- Closures: the 21 scripts whose closure holds `coordinator.py` recorded on
  Linux with strace (`tests/derive_closures.sh --scripts-from ... --record-only`,
  merged `--partial --allow-failures`): `tests/entities.py` exits 1 on the two
  base-red checks below, so its entry carries `rc: 1`.
- `tests/typing_ruler.py` under `HPO_TYPING_PYTHON`: the census at 0 errors
  (mypy --strict read 4 before `f0fc3bedd`).

## Red checks

- `tests/entities.py` (`tests / fast`): `gate-sweep.yml: on CI's completion,
  no concurrency, ...` and `graders-head-copy's delivery_status step is red
  only when this copy's exit differs from the base copy's, ...` fail here and
  at the merge base `50af6174f` alike (`2 of 2425 ENTITY CHECKS FAILED` there),
  so they are this environment's or main's, not this diff's; this diff touches
  neither workflow. No cheaper detector is owed by this PR.
- Red on this branch before the handoff, each repaired in it, with the
  trigger's answer: `typing_ruler` (4 mypy errors): the cheaper detector is
  mypy on the changed module, seconds, already reachable through the gate this
  seat ran -- no new detector; `finite_boundary` (a malformed snapshot leaf
  raised): the census is the cheapest detector of that class, none cheaper;
  `entities`/`doc_claims`/`harness_headers` (module counts in
  `docs/architecture.md`, the D6 header, the deployment-shape note):
  `ci_predict.py` names neither, and the cheaper detector is `doc_claims.py`
  (7 s), already in the scoped gate -- none cheaper; `env_drift --all` (the
  coord fixtures): the drift gate is the detector, none cheaper.

## Forward-carry

- R10-UX-HEALTH renders this field: a day figure from `eta_days` alone,
  labelled as the gate, and a settling learner shows progress and no day
  figure; control `r10_learner_eta.py`'s `eta_on_settling` and a card fixture.
  Landed in the roster's carry list for the group by
  `tools/audit/seat/roster_edit.py append-carry` (lint gate `TOTAL: 0
  error(s)`), commit `80ae03fbf` on this branch,
  `dev/programme/rosters/wave-r10-groups.json`. Carry: R10-UX-HEALTH

## Friction

- gate-scoping: unclear: `HPO_GATE_LOCK_LABEL` set without holding the lease
  made run.sh refuse `stress.py` and `harness_headers.py` (`flock-wrap
  refused, ... holds no lease`) after 25 minutes of the other lanes; the rule
  says run.sh renews itself under that label but not that the label must name
  a lease already held. Carry: dismissed: one seat's misreading, the refusal
  names the cause
