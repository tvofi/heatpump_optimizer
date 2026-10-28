Fix review: blocked fa6eb482bcaf1900ad3f86b994e31e8731f69c62 class-open: optimizer.py _thermostat_demand_single (the savings reference) still drives the single-zone step as a pass-through; on the finder's flat-price 750 L valve cell the reference charges its tank to 70 C, pays for 27.8 kWh refused, and predicted savings go 0.74 -> 32.33 (5.6% -> 73.6%)
bus-nonce: 1a3cb33c1e169790c6c1be2d08d363b5

# Fix review -- PR #2887, R10-BUFFER-STORE, round 1 (first review of this PR)

Reviewed head: `fa6eb482bcaf1900ad3f86b994e31e8731f69c62` (GitHub's `headRefOid`
at the start of the review and again before publishing). It is the authored
code head `a5f40d84c` plus `fdf33f466`, a merge of main `07295d4ea`. That
merge adds five mutation-ledger files and no production line (`git diff
a5f40d84c fa6eb482b -- custom_components` is empty), so the body's `at
a5f40d84c` figures apply at this head. Worktree: detached at the head under
`~/hpo-seats/r10s6/rev-prod-s8/2887/`, plus `2887-at55bb` at `55bbe8b62` for the
body's own figure head. Base: `07295d4ea` (`git merge-base origin/main HEAD`).

## Finder's harness (both ends)

The roster entry says the finding came from R10-SETPOINT-BOOST's census, so the
harness is `dev/audit/harnesses/r10_setpoint_boost.py`. It is on main and the
diff does not touch it. `r10_buffer_store.py` is the fixer's own, added by
`a2edb02b8`. I ran the finder's harness from an out-of-tree copy against each
tree:

- RESULT base `07295d4ea`: in **16 of 16** cells the 750 L buffer plan is
  byte-identical to its no-buffer twin. The finding reproduces.
- RESULT head: **0 of 16** identical. The 16 no-buffer arms are
  byte-identical between base and head (null).
- RESULT the harness's own `savings` column moves on every buffer cell at the
  head: spread (0.6, no DHW) 8.95 -> 42.79, flat 1.34 -> 32.10, (1.7) flat
  2.18 -> 86.39. The flat day is the null: nothing can be stored for, and the
  fixer's harness itself reads a +0.00 K tank rise there.

## Blocking: class-open -- the thermostat reference

`_compute_baseline_power` -> `_thermostat_demand_single` (optimizer.py:395) sizes
the reference's power from the slab's need alone, as if the single-zone step
delivered heat straight to the slab. Before this diff that was true. At this
head the single-zone valved step routes the heat into the tank, draws it
through the valve and refuses it at `buffer_max_temp`. The reference does not
know, so it over-drives. These are reviewer probes, both ends, on the finder's
0.6-loss, no-DHW cell at its flat mean price (`ev/baseline-probe-*`,
`ev/savings-probe-*`):

- RESULT head, 750 L manual valve: reference tank 21.4 -> **70.0 C** (ends at
  57.7), **27.79 kWh refused** at the cap and still paid for, reference 27.19
  kWh electric against the plan's 10.72, `predicted_savings` **32.33**,
  `savings_percentage` **73.6 %**.
- RESULT head, no buffer (null): reference 8.15 kWh, savings 0.74 (5.6 %).
- RESULT base, 750 L: identical to the no-buffer arm (8.15 kWh, 0.74, 5.6 %).
- RESULT two-zone, which already modelled the tank at the base: 750 L reference
  14.92 kWh against 9.00 without a buffer, savings 8.08 against 2.17. The
  readings are identical at base and head. So the reference's blindness to the
  tank predates this diff in two-zone. This diff extends it to the single-zone
  default, where it is 3.3x the house's energy instead of 1.66x.

The body's class rule ("one fact -- is this buffer tank a store? -- decided by two
predicates") returns this seam. `_thermostat_demand_single` is a third reader
of the single-zone step that answers "no", and it is neither in the diff nor
dispositioned in the body. `predicted_savings` and `savings_percentage` are
published figures, and on the owner's install type they now read about 74 %
savings on a flat-price day. `_compute_baseline_power`'s docstring states the
invariant this breaks: "Anything it wastes is reported to the user as a
saving."

The control that separates the defect from a real saving is the flat-price
arm: the plan stores nothing there, so any savings growth over the no-buffer
arm is the reference's waste. Re-measure with `ev/baseline_probe.py` (it records
the reference's own tank and refused heat) at both ends.

## Mutation proof (reviewer's own mutants, `ev/mutants.py`, driver tests/features.py)

A disclosure first: each mutant ran in a copy of the head tree without `.git`.
In every copy one check fails for that reason alone: `and the path that
proceeds still stamps a resolvable recorded_at (#363)` reads `'unknown'`. So
"KILLED" below means another check failed, and "survived" means that was the
only failure. I did not run a separate null at this load (the load average is
about 190).

- RESULT R2 (stability row's `c_buf` forced huge, so the valve row ignores the
  tank): KILLED. Three checks fail, including M7's `the stability count
  subdivides for the tank's own row` (26.796 vs 27.649 C). The folded line is
  pinned.
- RESULT R9 (`dT_cap` ignores `headroom_k`): KILLED by `charging stops at
  buffer_max_temp` and the zoned cap census.
- RESULT R1 (the folded row reads `p.buffer_tank_thermal_mass`, without the
  fallback), R3 (`_buffer_capacity` drops the fallback), R4 (fallback doubled):
  survived. Consistent with reachability: every selector volume is at least
  10 L, so `c_buf >= 0.0116` and the fallback never binds. The fold moved the
  old inline `if c_buf < 1e-6:` guard (a GUARD_OFF site) into a ternary that the
  mutation tool does not mutate. The movement is earned by the dedupe, not by
  hiding a live gap.
- RESULT R6 (`headroom_k` CLAMP_DROP, the site at `thermal_model.py:1756` that
  the body leaves to `mutation-autofix`): **survived tests/features.py here.**
  The body says the same mutant on the pre-split line was "killed by
  tests/features.py". At this head features.py does not kill it. Whether
  another driver does is the pin drive's call, and `tests / mutation-pins (1)`
  was still in progress at publish time.
- Triage R5 (`_buffer_capacity` CMP_BOUND): survived, as triaged. A constructed
  volume `1e-6/0.00116` L does reach `c_buf == 1e-6` exactly
  (`v*W == 1e-6` is True), so a test could kill it. No selector reaches it. The
  row's reason says exactly that, and holds.
- Triages R7 / R8 (`max(dt_hours, 1e-6)` floors): survived features.py. My
  `ev/dt_floor_probe.py`, through the public `simulate_step`, finds both
  killable: R7 at `dt_hours=0` (tank and refused go NaN with the tank at the
  cap) and at `dt_hours=1e-7` within 1e-9 K of the cap; R8 at `dt_hours=0`
  with tank == slab (NaN). Reachability rescues the verdict: diagnosis maps a
  zero dt to 0.25, sysid refuses `dts <= 1e-3`, and the coordinator's interval
  replay (`_propagated_slab`, guard `0.0 < dt_h`) passes an inter-cycle elapsed
  time. The rows' reasons name only the plan-step callers and assert "never
  below 1e-6 h", which the tree does not guarantee for the coordinator path. The
  conclusion holds; the reason text is incomplete.

## Figures re-derived at this head

- RESULT `tests/structure.py`: `class_excess_loc 17994 <= 17994`, STRUCTURE
  RATCHET PASSED. Step 14: reverting the fold reads 17996 (+2, FAIL), so the
  re-record is earned by a merged copy. Planting the same three lines
  compacted into one with nothing improved also reads 17994: the span metric
  pays for compaction. Under this sound change that is an instrument note, not
  a block.
- RESULT `ci_predict.py --base origin/main`: **1** unpinned site (the
  `headroom_k` clamp), at this head and at `55bbe8b62`. The body's quoted
  `CI PREDICT: 4 unpinned site(s) the diff adds` at `a5f40d84c`/`55bbe8b62` does
  not re-derive. It predates the triage commit.
- RESULT fixer's `r10_buffer_store.py plans 0` at `55bbe8b62` and at this head
  (twice, deterministic): spread 750 L `6a546df76556` / 22.41 / 1.000 / +40.00
  / 21.947, as the body says. Flat 750 L reads **`0c6ea1b722ec`** / 23.55 /
  0.321 / +0.00 / 38.059 against the body's `5d1137c8e29e`: same figures, a
  different plan hash. Base `07295d4ea`: identical True on both days, as the
  body says.
- RESULT `closure.py select --diff e8cb7e683` and `--diff 07295d4ea`: `MODE:
  SCOPED -- 27 script(s) run, 6 scoped out`, as the body says.
- RESULT CI at this head: `tests / mutation` failure, job 122583074009:
  `ADDED UNPINNED thermal_model.py:1756 CLAMP_DROP: headroom_k = ...`,
  `MUTATION TABLE REFUSED -- ... 1 of them added by this diff`. That is the
  expected bot-pin site, and the body's `## Red checks` names it.
  `mutation-pins (1)` and `prelude` were in progress. Everything else concluded
  success or skipped.
- RESULT review packet: Refusals none, `CARRY-AUDIT: 6 routed`, `FIGURES` no
  refusal.

## Findings

- class-open, blocking: the thermostat reference in `_compute_baseline_power` /
  `_thermostat_demand_single` is blind to the single-zone tank this diff makes
  live. The published savings inflate from 5.6 % to 73.6 % on a flat-price day
  (figures above). Fix it in this pull request: the reference must run the
  same tank-aware law as the step, or settle its refused and stored heat. The
  control is the flat-price arm, which must read savings near the no-buffer
  arm's. The two-zone reference has the same blindness at the base (1.66x):
  disposition it in the body or fix both. Carry: R10-BUFFER-STORE
- carry-missing, blocking once the above is fixed: the body's `## Forward-carry`
  routes the #2499 residual ("R10-STORE-RACES inherits the residual: close it as a
  demand-model fix with the same flat-price null, or refute it ... with
  r10_demand_overbook.py") to `R10-STORE-RACES (handoff/audit-r10-roster at
  4fa0f8418)`. At roster tip `1cb9e0a44`, R10-STORE-RACES holds only two
  r10-buffer-store carries (the CPU cost and the two homes for the fallback),
  and none names the residual, `relaxed DP` or #2499. The accuracy text landed in
  `R10-SAV-COMFORT`, whose stage is `done` and so is not a destination
  (`finding-propagation.md`). `4fa0f8418` is a `roster_sync` stage commit, not
  the carry. Carry: R10-BUFFER-STORE
- R6, the bot-pin site, survives tests/features.py at this head, against the
  body's statement that features.py kills it. If the pin drive finds no killer,
  the site needs a test, not a triage. Carry: R10-BUFFER-STORE
- Body figures that do not re-derive: the `CI PREDICT: 4 unpinned` count (it
  reads 1) and the flat 750 L plan hash `5d1137c8e29e` (it reads `0c6ea1b722ec`
  at `55bbe8b62` and at this head). Correct both at the next head. Carry:
  R10-BUFFER-STORE
- The R7/R8 triage reasons name only the plan-step callers and assert dt is
  "never below 1e-6 h". The coordinator interval replay (`0.0 < dt_h`) and sysid
  are the callers to name. The equivalence holds on every production cadence,
  and `ev/dt_floor_probe.py` shows both are killable through `simulate_step` at
  dt <= 1e-7. Carry: R10-BUFFER-STORE
- `class_excess_loc` pays for compacting lines with nothing improved (the
  one-line plant reads the same 17994 as the fold). Carry: dismissed: a
  physical-span metric is re-spellable by construction; fix-review step 14
  already judges the shape per diff, and this diff's shape is a merged copy

Evidence: `ev/` (files name the head `fa6eb482bcaf1900ad3f86b994e31e8731f69c62`
or the base they were taken at). The probes and mutants are the reviewer's own
instruments, disclosed as such. The finder's harness is
`dev/audit/harnesses/r10_setpoint_boost.py`, run unmodified.
