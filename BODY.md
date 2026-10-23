Closes #2234.

A source that reports only on change writes nothing while its value holds, so
its age measures how still the value is, not whether the source is alive.
`InputReader` held every source to `const.INPUT_MAX_AGE_MINUTES`, a polling
limit, so an idle power meter at 0 W read stale on 39 of 48 replay cycles and
an unchanged mode select on 47 (D14-s3-02). The R10 sweep
(`dev/audit/rounds/round10/sweep-N-staleness.md`) found five more instances:
energy, supply, return, flow meter and the coordinator's humidity limit.

The fix is one freshness rule keyed on how the source reports, as the
architect note asks:

- `inputs.source_polls(owner, entity_id, state)` is True once the entity has
  been seen re-reporting an unchanged value (`last_reported` past
  `last_updated`, which Home Assistant only writes for a repeat; the manifest
  floor is 2025.2, so `last_reported` always exists). `hass` remembers it in a
  `WeakKeyDictionary` side table (boost.py's precedent). A polling source whose
  last write was a change therefore keeps its polling limit.
- `inputs.age_limit_for` picks `INPUT_MAX_AGE_MINUTES` for a polling source and
  `const.INPUT_ON_CHANGE_MAX_AGE_MINUTES` for any other. `InputReader._begin`
  calls it whenever the caller did not pass its own limit. An explicit limit
  and `UNBOUNDED` behave as before.
- `INPUT_ON_CHANGE_MAX_AGE_MINUTES` copies the polling table and overrides the
  keys whose value can hold indefinitely: power, energy, mode, supply, return
  and flow get `inf` (no age limit; `unavailable` still refuses). Indoor
  humidity gets the room's quiet-store bound of 360 min, because it is the room
  probe's own channel. `max_age_for` maps `inf` to `None`, so diagnostics and
  the card show "no limit" rather than a huge number.
- Humidity moves into the tables (polling limit 120, unchanged) and
  `_indoor_humidity_value` reads through `InputReader`. This deletes the
  coordinator's own state lookup, age check, float parse and finiteness test,
  along with `coordinator.HUMIDITY_MAX_AGE_MINUTES`.
- Every other key keeps its polling limit as its on-change limit. Those keys
  are the quiet stores (R9's 6 h bound), outdoor and house power (they move
  within their bound), the fail-safe signals (pump signals, wood-side probes,
  flue, solar) and PV (no reader applies it; class P6).
  `tests/features.py`'s `_r10st_same` names each of them with its reason. The
  check refuses an undeclared key, an equal key left unnamed, and a named key
  that is not equal. This is the RCA's countermeasure
  (`dev/audit/rca/R10-N-staleness.md` at d23205d13): a declared quantity a
  check compares, not a comment.

Alternatives rejected:

- (a) Raising the polling limits to the quiet interval. That blinds the dead
  polling sensor the watchdog exists for, and the null control says that
  bound must hold.
- (b) A per-key quiet table with no reporting-kind test. It still declares a
  quiet idle power meter dead at whatever finite number it picks.
- (c) Judging the kind from the current state alone, without memory. That
  fails open on a dead polled meter whose last write was a change. The census
  arm "remembered past a changing write" pins it.

The carry's comment fix also lands: the `_RANGE_KEYS` comment in `inputs.py`
no longer names `ATTR_MIN_TEMP`/`ATTR_MAX_TEMP`.

Behaviour change, stated: an on-change source of an `inf` key that dies
without going `unavailable` is never aged out. That is the brief's rule ("stale
only when its source is unavailable"). A polled source still ages out, and so
does a source seen re-reporting even once since Home Assistant started. The
residual case is a polled source whose value has changed on every write since
start (no repeat ever seen), and it reads as on-change until its first repeat.

Thirteen older checks modelled a dead sensor with an on-change stamp
(`FakeState(last_updated=old)`) and asserted it stale. They encoded the defect.
Each now re-reports before going silent, as a polled source does:

- `_ps_state` and `_um_read` (pump mode; "polled, as the reference integration
  polls the Tuya cloud every 3 min");
- the flow-lift supply/return pair, `_sp_write`'s stale rung, `_fm_reader` and
  `_fm_plant`;
- the two `read_state` mode checks ("an over-age string ...", "staleness outranks an unrecognised value") and `_g_hstale` (humidity);
- `tests/dst_checks.py`'s mode outage.

None of them lost an assertion.

## Head

7668a4d0974444c9806fe83ae0656b0b6bd1e50a on merge base
a6620c30adcdf0d9529ee66977694bfa2a06d5c3 (origin/main's tip,
`git rev-parse origin/main`, 2026-10-23 UTC).

## Mutation proof

Run from a worktree at the head with `PYTHONPATH=tests/hastub python3 tests/features.py`,
one mutant at a time, restored between runs (scratch driver, not in the tree):

- M1: delete the `if max_age_minutes is None: reading.max_age_minutes = age_limit_for(...)`
  wiring in `InputReader._begin` -> FAIL "all 26 age-limited keys: a quiet
  on-change source is stale only on a key named equal ...", FAIL "an on-change
  power meter idle at 0 W for 10 h reads 0 kW with no limit ...", FAIL
  "humidity: an on-change probe quiet 121 min keeps the mold floor ...".
- M2: the predicate `reported > updated` in `source_polls` -> `>=` (every
  source counts as polling: the old rule) -> the same three FAIL.
- M3: `known.add(entity_id)` -> `pass` (no source is ever remembered as polling) -> 18 FAIL, among them the census, the humidity check, "an over-age string is rejected exactly like an over-age number", "a flow reading 45 min old is stale and gives no estimate" and "a mode read minutes ago still acts, one read hours ago does not". (A first M3 that deleted the line left an empty `if` and died on an IndentationError: vacuous, discarded.)
- M4: delete the `CONF_POWER_ENTITY: math.inf` row -> FAIL "every age-limited key declares its on-change limit ...", FAIL the census, FAIL the idle power meter check.
- M0, the same driver with no mutation -> `ALL 4336 FEATURE CHECKS PASSED`, rc=0.

At the merge base a6620c30a, the first version of this PR's test (the
`tests/features.py` hunk of 61d9fdb09, applied alone) fails all four of its
checks: declaration, census, idle power meter and humidity. The census arm
names flow, energy, mode, power, return and supply as stale when quiet. The
two value checks added in 7668a4d09 call `inputs.source_polls`, which the base
does not define.

## Null control

The finder's harness at both ends,
`PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/s3/staleness_on_change.py`
(in tree, sha1 6fa091e3760cf5e4e843bc763ceba27a2d4b1973):

- base a6620c30a: `polling_stale_cycles=0`, `heat_pump_power_entity_stale_cycles=39`,
  `heat_pump_power_entity_newly_unavailable_entity_cycles=78`,
  `heat_pump_mode_entity_stale_cycles=47`, `seams=2`; its unbounded arm
  `perturb_unbounded_*_stale_cycles=0` for both.
- head 61d9fdb09 (production code identical to the head; later commits
  touch tests only): `polling_stale_cycles=0`, power 0, mode 0, `seams=0`; dhw, indoor and
  outdoor 0 at both ends.

The polling day reads 0 at both ends, but its sources never die, so it cannot
show that a dead polling source still goes stale (the carry's null control).
That control is the census in `tests/features.py`. For every key of
`INPUT_MAX_AGE_MINUTES` (26 at the head, 25 at the base; the rule is
`len(INPUT_MAX_AGE_MINUTES)`), it drives the real `InputReader` and checks
three cases:

- a source that re-reported and then fell silent one minute past its polling
  limit is stale on every key;
- the same holds when the source's last write was a change, given polling
  evidence earlier on the same `hass`;
- a quiet on-change source is stale exactly on the keys `_r10st_same` names.

At the base the census fails with the six instance keys listed (above); at the
head it passes.

## Figures

- power 39, mode 47, polling 0 stale cycles at the base; power 0, mode 0,
  polling 0 at the head: `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/s3/staleness_on_change.py`
  (null control: its `perturb_unbounded` arm, 0 and 0 at the base).
- Instance probe, `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round10/D14/sweep-N-staleness/probe.py <KEY>`
  (sha1 311f0e029f449ce180f569b1f515ba245daea59a): CONF_POWER, MODE, ENERGY,
  SUPPLY, RETURN and FLOW rc=1 (stale) at the base and rc=0 at the head.
  The controls stay rc=1 at both ends: CONF_INDOOR_TEMP held 361 min,
  CONF_HEAT_PUMP_DEFROST held 31 min and CONF_WOOD_TANK_TOP held 61 min, keys
  that keep their bound. The `HUMIDITY` arm reads the deleted
  `coordinator.HUMIDITY_MAX_AGE_MINUTES` and raises at the head. The humidity
  census check stands in for it: 121 min on-change keeps the floor, while
  121 min polled and 361 min on-change both drop it.
- Class enumerator (step 8), `python3 dev/audit/rounds/round10/D14/sweep-N-staleness/enumerate.py`
  (sha1 2028e7571822cdeac46e414cf8adb1226a57ea83): `RESULT seams=29 flagged=20`
  at both ends, with `--controls` `RESULT controls_ok=True` at both. It reads
  only the polling table, which this fix rightly leaves alone, so it reads flat.
  The companion that reads the defect at the base and not at the head is the
  census above. Every flagged seam is dispositioned:

  | seam | disposition |
  |---|---|
  | power | closed in this diff |
  | mode | closed in this diff |
  | energy | closed in this diff |
  | supply | closed in this diff |
  | return | closed in this diff |
  | flow | closed in this diff |
  | humidity | closed in this diff |
  | MODE_LAST_GOOD | part of the mode instance; it acts only after the mode is unreadable, still bounded |
  | the six pump signals | already guarded; named in `_r10st_same` |
  | the four wood/flue probes | already guarded; named in `_r10st_same` |
  | solar | already guarded; named in `_r10st_same` |
  | PV | no reader applies the limit, a distinct finding of class P6 |
  | DHW inlet (1440) | unflagged |
  | Open-Meteo observed (90) | unflagged, and an HTTP payload, not an entity |

  The census asserts its own precondition: the declaration check fails if a
  key is added to the polling table without an on-change decision.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`
  printed `MODE: SCOPED -- 29 script(s) run, 4 scoped out` at 61d9fdb09. The
  run: `GATE_SCOPE=auto GOLDEN_MODE=drift PYTHONPATH=tests/hastub bash tests/run.sh`
  at the head -> `31 TEST SCRIPT(S) PASSED; 3 SCOPED OUT AND NOT RUN`, rc=0 (`tests/arch_score.py`, `tests/ha_contract.py`, `tests/md_tables.mjs` scoped out).
- `python3 tests/structure.py`: rc=0 after `--record`. `class_excess_loc` and
  `max_class_loc` are both down 8 (the humidity read). The reason is in commit
  "structure: record class_excess_loc and max_class_loc down 8 (#2234)".
- `python3 tools/pr/ci_predict.py --base origin/main`: "no closures or fast red
  predicted", and 10 unpinned sites (below).

## Architecture score

`python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`:
`Architecture score: dS +0.3221 IMPROVES`; `duplication_copies 40 -> 39 +0.3180`
(the humidity read's hand-rolled float/finite/age copy is gone);
`coord_footprint 2471 -> 2464 +0.0041`.

## Unpinned sites

- custom_components/heatpump_optimizer/coordinator.py:8911 BOOLOP: pinned by mutation-autofix (killed by "an unusable humidity reading disarms the guard": an unavailable reading reaches `0.0 < None`)
- custom_components/heatpump_optimizer/coordinator.py:8911 CMP_BOUND*2: pinned by mutation-autofix (the "0" humidity check kills `0.0 <=`; the new "100 % is a reading" value check kills `< 100.0`)
- custom_components/heatpump_optimizer/coordinator.py:8911 RETURN_DEL: pinned by mutation-autofix (every humidity floor check)
- custom_components/heatpump_optimizer/inputs.py:259 GUARD_OFF: pinned by mutation-autofix (the idle power meter check asserts `max_age_minutes is None`; without the guard it reads inf)
- custom_components/heatpump_optimizer/inputs.py:285 CMP_BOUND: pinned by mutation-autofix (M2 above, three checks red)
- custom_components/heatpump_optimizer/inputs.py:287 GUARD_OFF: pinned by mutation-autofix (the new "source_polls with no owner" value check: `setdefault(None)` raises)
- custom_components/heatpump_optimizer/inputs.py:290 GUARD_OFF: pinned by mutation-autofix (the census: every entity becomes polling on its first read, so a quiet on-change key reads stale)
- custom_components/heatpump_optimizer/inputs.py:292 RETURN_DEL: pinned by mutation-autofix (the census)
- custom_components/heatpump_optimizer/inputs.py:306 RETURN_DEL: pinned by mutation-autofix (the census)
- custom_components/heatpump_optimizer/inputs.py:874 GUARD_OFF: pinned by mutation-autofix (M1 above, three checks red)

## Red checks

none. Locally the first gate run at 61d9fdb09 had `tests/features.py` and `tests/entities.py` red. These were 13 checks that aged an on-change stamp as a dead sensor, plus the P2 `state_age` registry, which did not yet disposition `source_polls`. Both were repaired before the handoff (the third commit), and no CI check ran on this branch.

## Forward-carry

The seat writes no branch but its return refs, so the orchestrator lands each
of these into the named brief:

1. R10-HEAT-METER (next on `const.py`) adds a delivered-heat energy entity. A
   new key in `INPUT_MAX_AGE_MINUTES` now needs its on-change decision in the
   same PR. Either it overrides `INPUT_ON_CHANGE_MAX_AGE_MINUTES` (a
   total_increasing counter holds while idle: `math.inf`, like
   `CONF_ENERGY_ENTITY`), or it is named in `tests/features.py`'s `_r10st_same`
   with its reason. The declaration check refuses anything else. Control: the
   check is red at a6620c30a and green at this head. A test of a dead meter
   must re-report before going silent (`last_reported` past `last_updated`).
   An aged on-change stamp now reads as a quiet value, not a dead sensor.
   Carry: roster `wave-r10-groups.json` group R10-HEAT-METER, carry.
2. R10-ARCH-SHAPES (later on `inputs.py`) adds a power-kW reader there. The
   default age limit is now chosen per read by `age_limit_for` inside
   `InputReader._begin`, and a new stamp reader in `inputs.py` is refused by
   `tests/entities.py`'s P2 `state_age` registry unless it is dispositioned
   (`source_polls` is, as the re-report fact). The `_RANGE_KEYS` comment that
   group also holds is fixed here (`git grep -n ATTR_MIN_TEMP custom_components`
   returns nothing at the head). Carry: roster group R10-ARCH-SHAPES, carry.

## Friction

- dev/governance/roles/fixer.md#5: unclear: the environment's `python3` on PATH lacks the
  suite's dependencies (no voluptuous); the seat venv is `/opt/hpo/venv-ci`,
  and a first harness run failed on it before `PATH` named it. Carry: none
  (environment; `tools/audit/seat/cloud-setup.sh` owns PATH).
- dev/governance/roles/fixer.md#3: stale: the sweep's `probe.py HUMIDITY` arm reads a
  module constant this fix deletes, so it cannot run at the head; the
  in-tree census replaces it. Carry: none (a round record recounts and stays
  as written).
