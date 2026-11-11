# D3-s2 report — mutation candidates for the "everything but coordinator/optimizer/thermal_model/sysid" modules, plus resource use

Baseline: `cdf82daabcfe3777d98b31489f36df5555ec9d82`. Tree: this worktree
(`/home/claude/audit-r8/seats/D3-s2`), a detached git worktree, kept
byte-identical to baseline on exit (verified with `git status --porcelain`
after every mutation, restored in a `finally`).

Box: shared 4-vCPU cloud container running up to 13 other seats concurrently
during this fan-out. `load1` was observed in the 20-26 range throughout
(quoted per-RESULT, not gated, per `tests/README.md`). This made the
behavioural pre-screen scripts (`entities.py`, `features.py`,
`config_flow_steps.py`) run far slower than their unloaded times
(`config_flow_steps.py` 40.0s/13.5s CPU unloaded vs multi-minute observed;
`entities.py` ~2min unloaded, 7min+ and counting observed), which bounded
how many of the 13 mutants below got a full behavioural confirmation inside
the ~90-minute budget. Two (D3-s2-01, D3-s2-02) got one; the rest are
candidates, per the method's own step 3 ("report candidates, not findings...
the quiet window runs the full gate for the top six survivors").

## Exposure

None: no `docs/` or GitHub reads.

## Method

Step 1 (candidate list): grepped every module in this seat's focus list for
guards (`if`, `raise`, `min`/`max`/clip, boundary comparisons) that gate a
user-facing claim (config validation, service errors, published sensor
values). 13 mutants recorded below. No module got more than 3 mutants.
`sensor.py`, `config_flow.py`, `price_model.py`, `curve_learning.py`,
`dhw_learning.py`, `comfort_learning.py`, `drift.py` were read but yielded no
mutant this seat had time to also pre-screen; flagged under Unfinished for a
continuation seat.

Step 2 (pre-screen): `tools/audit/round8/D3/s2_mutate.py` ran
`tests/structure.py` against all 13 mutants first (fast, ~5-20s each even
under contention) — all 13 survive it, expected: `structure.py` measures
structural budgets, not behaviour. Two mutants got hand-built direct-call
harnesses (`s2_finding01_hours_since.py`, `s2_finding02_deadband_boundary.py`)
that import the real production module and drive the real function with a
minimal stub, avoiding the multi-minute full-suite cost while still hooking
the real symbol and getting a same-session confirmation. `env_drift.py --all`
was not run against any mutant (budget; also see resource-use note on
`golden.py`).

Step 5 (resource use): see below.

## Findings

### D3-s2-01 — `LegionellaGuard.hours_since()`'s negative-elapsed clamp is untested

Harness: `tools/audit/round8/D3/s2_finding01_hours_since.py`. A direct call
with `last_cycle` set 2h in the *future* (a backward clock step, NTP
correction, or a restored-from-backup stamp) returns `0.0` at baseline
(clamped) and `-1.999999996...` with `max(0.0, ...)` removed from
`hours_since()` — the perturbation moves the reading by exactly the expected
2h, sign-flipped (`RESULT clamp_moves_future_reading=True`), while the
ordinary (past) case is untouched within 1e-4h (0.36s) of two-`now()`-calls
timing jitter (null control holds). No test in the tree ever sets
`last_cycle` or `attempt` to a time after "now" — grepped every assignment
across `tests/features.py`, `tests/dst_checks.py`, `tests/entities.py`; every
one sets `dt_util.now() - timedelta(...)` — so this branch is provably never
exercised in either direction by the committed suite. `due_in_hours()`
consumes `hours_since()` directly (`interval_days*24 - since`), so an
unclamped negative reading would silently push the anti-legionella
disinfection's due time *later* than correct after a backward clock step —
a wrong-comfort/wrong-safety-margin defect class if it ever fired for real
(Home Assistant's own clock can step backward on an NTP resync or an RTC
battery replacement; `#1299`'s neighbouring comment in the same file already
documents one clock-related bug class here).

Confirmation against the fast suite (`tests/entities.py`) was started but did
not complete inside this seat's time budget under contention (RESULT lines
above are exact/not wall-time-sensitive; the suite-kill confirmation is the
part still running). The finding rests on the harness's own before/after,
which independently satisfies instrumented-symbol + perturbation + metric +
null-control per COMMON.md's requirements without needing the suite-kill
number. Reproduction: `PYTHONPATH=tests/hastub <thread pins> python3
tools/audit/round8/D3/s2_finding01_hours_since.py`.

- instrumented_symbol: `custom_components.heatpump_optimizer.legionella:LegionellaGuard.hours_since`
- perturbation: delete `max(0.0, ...)` around the elapsed-hours computation; expected_direction: sign_flip on a future-dated `last_cycle`
- metric_definition: `hours_since()`'s return value with `last_cycle` 2h in the future, baseline vs mutant
- null_control: same call with `last_cycle` 2h in the past — unaffected by the clamp in both arms
- severity: medium (silent scheduling drift after a clock-backward event; not the common case, no data loss, comfort/hygiene-adjacent not acute safety)
- stop_rule_class: bug

### D3-s2-02 — the dhw-min/setpoint deadband check's exact boundary is untested at both call sites

Harness: `tools/audit/round8/D3/s2_finding02_deadband_boundary.py`.
`services.py` enforces "hot water minimum must leave a
`DHW_MIN_TEMP_SETPOINT_MARGIN` (5°C) deadband below the setpoint" in two
near-identical, independently-written blocks: `handle_set_thermal_params`
(`if float(minimum) > ceiling:`) and `handle_apply_schedule` (`if wanted >
ceiling:`). At baseline, `minimum == ceiling` (exactly zero deadband) is
**accepted** by both (`RESULT set_thermal_params_baseline_at_boundary=None`,
`RESULT apply_schedule_baseline_at_boundary=None`). Flipping either `>` to
`>=` (tightening the guard to reject exact equality) moves the outcome
cleanly: `RESULT set_thermal_params_mutant_at_boundary=
'ServiceValidationError:set_thermal_params_dhw_min_no_deadband'`,
`RESULT apply_schedule_mutant_at_boundary=
'ServiceValidationError:apply_schedule_dhw_min_no_deadband'`, while the null
control 0.01° below the boundary is accepted identically in both baseline
and mutant on both call sites (`RESULT ..._null_control_holds=True` x2). The
harness drives the real `handle_set_thermal_params` / `handle_apply_schedule`
coroutines (not a recomputation of the arithmetic) with a minimal
`_loaded_entries` stub. Every call site in the whole test tree
(`grep -n 'dhw_min_temperature' tests/*.py`) uses a value well clear of the
computed ceiling (e.g. flat `51`, `45.0` against unrelated setpoints), never
the boundary itself, so the gap is real and not an artefact of this harness's
own setpoint choice.

Severity: low/hygiene as a live bug (exact-zero-deadband at the boundary is
an edge a real user is unlikely to hit exactly in a UI-driven °C value), but
it is precisely the "duplicated coverage the suite never distinguishes"
shape D3's method step 5 asks about: two independently-maintained copies of
one invariant, tested twice from two service entry points, neither test
reaching the one input value that would show the copies disagree if a future
edit touched one and not the other.

- instrumented_symbol: `custom_components.heatpump_optimizer.services:handle_set_thermal_params` and `:handle_apply_schedule`
- perturbation: `if float(minimum) > ceiling:` → `>=` (line ~485) and `if wanted > ceiling:` → `>=` (line ~822); expected_direction: accepted→rejected (to_zero on "accepted") at the exact boundary
- metric_definition: whether the real service coroutine raises `ServiceValidationError` for `minimum == ceiling` exactly
- null_control: same call at `minimum == ceiling - 0.01` — accepted under both baseline and mutant, both call sites
- severity: low
- stop_rule_class: hygiene

## Prescreened candidates (not promoted — no full-suite kill/survive confirmation obtained inside budget; static grep evidence given where found)

| id | file:guard | perturbation | structure.py | static coverage evidence |
|---|---|---|---|---|
| m01 | grid_fee.py: `rule.rate < 0.0` (negative-rate refusal) | widen threshold to -999 | survives | `tests/features.py:10743-10758`, `tests/entities.py:10570-10605` call `spec_problem` on a negative rate and assert `ERROR_NEGATIVE` directly — very likely killed by the closure's own scripts; not independently executed here |
| m02 | grid_fee.py: `rule.rate > IMPLAUSIBLE_FEE_SEK_PER_KWH` | widen 1000x | survives | `tests/features.py:18417+` covers the store-layer sibling of #169/D4-05 (the negative-rate case specifically); the implausible-magnitude case not directly grepped — unexamined |
| m03 | grid_fee.py: `min_component`'s `rule.rate < lowest` → `<=` | tie-break source attribution | survives | no direct grep hit; genuine unexamined candidate |
| m04 | legionella.py: cycle debounce `< 3600` → `< 0` | effectively disables the anti-flap debounce | survives | not executed; a real behaviour change (disables debounce almost entirely) that several `features.py` legionella-cycling arms would plausibly notice as a side effect, but not confirmed |
| m06 | tariff.py: `offpeak_factor` clamp to `[0,1]` removed | unclamped passthrough | survives | `tests/features.py` constructs `offpeak_factor=0.5` (in-range) repeatedly; no out-of-range construction found by grep — plausible gap, unexamined |
| m07 | tariff.py: `house_power_kw < 0` rejection removed (isfinite check kept) | negative sample now accepted | survives | no grep hit for a negative `house_power_kw` sample anywhere in `tests/*.py` — plausible gap, unexamined |
| m08 | tariff.py: `_window_factor <= 0.0` → `< 0.0` | zero factor no longer short-circuited | survives | `tests/features.py` checks specific factor values (0.5, 1.0) but not the zero-boundary transition itself — plausible gap, unexamined |
| m09 | ledger.py: `baseline_sek <= 0.01` → `<= -0.01` | near-zero-baseline percentage guard narrowed | survives | not executed; `savings_pct` is the ledger's own copy of `optimizer._savings_percentage`'s clip (a possible D7 duplication note) |
| m10 | ledger.py: `max(0, len(months) - KEEP_MONTHS)` removed from `_prune` | — | survives, **equivalent mutant** | see Non-findings |
| m13 | `__init__.py`: `_take_fresh_handover`'s `age_min > interval_minutes` widened 1000x | a very stale handover would be reused after reload | survives structure.py | `tests/dst_checks.py:774-782` (driven by `features.py`, per `tests/closure.py:DRIVEN_BY_OTHERS`) calls `_take_fresh_handover(_h, "e1", 60.0)` with a 2h-old stamp and asserts `is None`; a 1000x widening (60min→60000min) would still accept a 2h-old stamp as fresh, so this existing test would catch it — high-confidence non-finding, see below |

m11/m12 are covered above as D3-s2-02, not repeated here.

## Non-findings

- **m10 is an equivalent mutant.** `sorted(x)[:n-K]` and
  `sorted(x)[:max(0,n-K)]` are identical in Python for every `n`, because
  list slicing clamps an out-of-range stop index rather than erroring or
  wrapping negative. Verified directly:
  `python3 -c "print(sorted(['a','b'])[:2-24], sorted(['a','b'])[:max(0,2-24)])"`
  → `[] []`, and again for a 5-element list against the same negative stop.
  `_prune()` is only ever called immediately after inserting one new month
  key or after loading a store of arbitrary size, so `len(months)-KEEP_MONTHS`
  is exactly the case this identity covers. Not a finding.
- **`tests/golden.py --only coord_minimal` already reports 1 of 1 scenario
  changed against the committed fixture on a clean, unmutated baseline
  checkout** (`data.battery.components: length 3 -> 2`,
  `sensors.thermal_battery.native_value: 69.2 -> 69.8`, several more numeric
  fields drifted — full diff in harness stdout, reproducible with
  `PYTHONPATH=tests/hastub python3 tests/golden.py --only coord_minimal`).
  This is the documented solver-float non-reproducibility across BLAS builds
  (CLAUDE.md rule 3 / `env_drift.py`'s claimed-drift mechanism), not a suite
  gap in this seat's method — `golden.py` in strict mode is therefore *not*
  a usable pre-screen signal on this box and was excluded from every
  mutant's pre-screen here.
- **`tests/entities.py` on this checkout fails 9 of 1732 checks with zero
  mutation applied.** This matches BASELINE.md's documented count exactly
  (1 unstripped-checkout artefact + 8 stripped-earlier-rounds artefacts = 9),
  reproduced by rerunning the identical command a second time on a clean
  tree with the same count both times. Not a finding.
- m13's staleness-guard widening is, per static reading, directly covered by
  an existing test (`tests/dst_checks.py:774-782`); treated as a
  high-confidence non-finding though not independently executed to
  completion here (features.py, which drives dst_checks.py, did not finish
  inside this seat's time budget under contention — see Resource use).

## Resource use (method step 5)

- **Box contention dominated the fan-out, and is itself the largest
  resource-use fact this seat can report with numbers.**
  `tests/config_flow_steps.py` measured 40.0s wall / 13.5s user CPU running
  alone early in this session, versus repeatedly-observed multi-minute
  (still running past 10+ minutes in one case) completions once ~10+ other
  seats' processes were concurrently live — `ps aux` during this session
  showed 2-3 concurrent `config_flow_steps.py`/`features.py`/`entities.py`
  processes from other seats at `load1` 20.0-26.0 throughout (quoted per
  RESULT line; the round-2 judge's own floor for this box was 1.86,
  best-of-ten 1.55 per `tests/README.md` — this fan-out ran at roughly
  13-15x that floor). Because the method's own step 2 asks for the full
  closure's fast scripts *plus* `env_drift.py --all` per mutant, the
  practical per-mutant cost of a faithful pre-screen on this box was
  minutes, not seconds — which is why only 2 of 13 candidates got a full
  behavioural confirmation instead of all 13. This is a fan-out capacity
  fact, not a suite defect; worth recording so a future round's D3 seat
  count or mutant budget is sized against observed (not assumed-quiet)
  contention.
- **`tests/golden.py` in its default (strict, `--only`) mode is worse than
  useless as a differential pre-screen signal on this box** (see
  non-findings): it reports drift with zero mutation applied. Any pre-screen
  budget spent running it in that mode here would have been wasted on every
  one of the 13 mutants; the `--all <sha>` differential mode (which reads
  the claimed-drift file instead of comparing raw values) is the only mode
  this seat can recommend for the pre-screen step, and even that mode was
  not run against any mutant here (time budget, and it takes an
  `env_drift.py`-owned worktree that had to be `flock`ed against D3-s1's
  concurrent use of the same mechanism per the task brief).
- **Duplicated coverage without duplicated depth (D3-s2-02).** The two
  `dhw_min_no_deadband` guards are textually near-identical and each has its
  own hand-written `tests/features.py` assertion
  (`set_thermal_params_dhw_min_no_deadband`, `apply_schedule_dhw_min_no_deadband`)
  checking the *same* shape of error from two different service entry
  points. That duplication is deliberate (two real services, each needs the
  guard) rather than wasteful, but the resource-use observation is that the
  suite pays for breadth (two call sites covered) without buying depth (the
  one edge value — the boundary — that would show the two copies have
  silently diverged is untested by either).

## Unfinished

- 11 of 13 mutants (all but D3-s2-01/02) lack a full-suite kill/survive
  number; see the prescreen table for static-evidence confidence per mutant.
  `env_drift.py --all <baseline-sha>` was not run against any mutant.
- `sensor.py`, `config_flow.py`, `price_model.py`, `curve_learning.py`,
  `dhw_learning.py`, `comfort_learning.py`, `drift.py` were read for
  candidates but none were promoted into the 13 mutants that got even a
  structure.py pre-screen; a continuation seat focused on those seven would
  be the natural next step, since this seat's nominal in-scope module list
  is wider than what 13 mutants (no module over four) could cover in the
  time available.
- The `tests/entities.py` confirmation run for D3-s2-01 was started
  (`s2_finding01_hours_since.py`, background) but its completion could not
  be waited for inside this seat's turn budget; if it completed, its
  `RESULT mutant_survives_entities=` line (written to this same harness's
  stdout on rerun) settles whether D3-s2-01 is also suite-confirmed or
  remains resting on the harness-only evidence given above.

## Note: finding-id / schema mismatch

The task brief for this seat specifies finding ids `D3-s2-01`, `-02`, ...
(seat-scoped, since two finders share dimension D3 this round).
`tools/audit/finding.schema.json`'s `id` pattern is
`^D(1[0-3]|[0-9])-[0-9]{2}$`, which does not admit a seat infix and so
rejects `D3-s2-01`/`D3-s2-02` (confirmed: `jsonschema.validate` raises
`'D3-s2-02' does not match ...` against the two ids used here). This looks
like the schema not yet having been updated for a multi-seat-per-dimension
round; not fixed here (out of this seat's assigned scope, and the schema is
shared with every other seat this round) — flagged per the toolkit's own
"a defect in an instrument is a finding, filed only after the panel/judge"
rule rather than edited unilaterally.
