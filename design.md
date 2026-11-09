# Design: R10-ADVISOR-STEADY-START — the what-if's steady-start estimator (#2257)

Base: 01782a1e3c327cbfb69784b8e676359e5bcfa079 (origin/main; no predecessor, `after` is empty, so no handoff head). Brief: the group's carry 0 (from R10-ADVISOR-WHATIF, #2963). Size L.

## Re-measured at the base

`PYTHONPATH=tests/hastub:tests:custom_components python3 dev/audit/harnesses/r10_advisor_residue.py whatif`: `plan_moves_by_start 24` of 24 rows, `held_moves_by_start 0`; caps `figures reading a saving (< -1) plan 18/36 settled 1/36`. The same command at 92588d581, on this box (numpy 2.5.4, scipy 1.18.1), prints the same 18/36 and 1/36 as at the base. The 19/36 and 3/36 the brief quotes for 92588d581 therefore come from the box that measured them, not from a change between commits: solver-basin variance, not drift. The wrong-sign settled rows reproduce (varying 00:00 target_minus_1 settled +24.6, target_plus_1 -25.5).

## Owning seam

`async_simulate` (coordinator.py:11238, `tests/seam_map.json` "core") owns the estimator. It calls three modules, each for what it already owns:
- optimizer.py: the held start. `_thermostat_held_state` (optimizer.py:574) already builds "``state`` as a thermostat holding ``target`` all along would have it" for the baseline (:5556). A module-level public wrapper beside it takes an optimizer and its solve inputs, and returns that state at the optimizer's own comfort target at the start instant (`config.get_comfort_temp` at `start_time`). It is not a class method: `class_excess_loc` sits at zero headroom and the optimizer class counts toward it.
- price_tiles.py: the figure. `price_tiles.monthly_deltas` (:89) gains a fourth key, the steady figure: per_month of (predicted + deferred) of the steady what-if solve minus the steady live solve, plus the what-if's wood figure. Its docstring says which reader takes which key.
- a new what-if module (the fixer names it; it must be classified in `tests/closure.py` or a measured closure): one per-coordinator state object that replaces `_last_simulation` and `_simulation_cache` (coordinator attrs 2 → 1) and holds a one-slot memo of the steady live solve. It also owns the rate-limit gate now inlined at coordinator.py:11266, moved verbatim.

Coordinator metrics at the base, from `python3 tests/structure.py`: `coordinator_attrs`, `max_class_loc` and `class_excess_loc` all sit at their caps. The coordinator class may not grow by a line. The gate and cache moving out pays for the two extra solve calls. If it does not pay, that is a design finding to report before pushing, not a budget raise.

## Shape

**`async_simulate`'s contract.** It gains a keyword-only `steady: bool = True`. When it is set:
1. It runs one more solve, the what-if from its held start.
2. It runs a second extra solve, the live configuration from its held start. That solve is memoised on (the live result object or `base` record, solve instant), so further calls against the same scheduled plan reuse it.

The answer gains the steady key. `monthly_cost_delta`, `monthly_held_cost_delta` and `monthly_settled_cost_delta` keep their meaning: `simulate_plan` is a service with a response, and changing a published key's meaning breaks an automation silently. Adding a key does not. The live-start solve stays. The panel's comfort, hot-water, compressor and peak lines, and the fuse advisor's breach, peak and minimum, describe the house as it is tonight, and no finding names them. With `steady=False`, behaviour is byte-identical to the base.

payload.py: no TypedDict carries the simulate answer. `PriceTile.monthly_cost_delta` (payload.py:334) keeps its key, and for a cap tile its value becomes the steady mean. No new TypedDict is added; that would be scope this brief does not name.

**What each caller does:**

| caller | passes | reads after | reason |
|---|---|---|---|
| card, via `handle_simulate_plan` (services.py:767) | `steady=True`, limited | the steady key, for the money line | the brief's ruling |
| fuse advisor (coordinator.py:9050), `limited=False`, base | `steady=True` | the steady key as `cost_delta_sek_month` | a cap must not save; settled saves on 1/36 cap rows at the base, steady on 0/36 |
| price tile, cap (coordinator.py:10776) | `steady=True` | `monthly_figure` picks the steady key for a cap | as above; shares the fuse advisor's live memo for the same record |
| price tile, degree | `steady=False` | `monthly_held_cost_delta`, unchanged | it already starts held (the thermostat). Moving it re-opens #2572/#2834's fixed Advisor items and adds 2 background solves a tile a day |
| `debugger._solver_smoke` (debugger.py:323) | `steady=False` | `cost_delta`, unchanged | it times one solve; its `wall_ms` stays comparable |

**Flow.**
```
card → service → async_simulate(steady)
  ├ gate (what-if module) ─ rate-limited? → cached answer
  ├ live result (scheduled) ┐
  ├ what-if from live state ┘→ cost/plan/comfort keys (unchanged)
  ├ live from held start  (memo) ┐
  └ what-if from held start      ┘→ price_tiles.monthly_deltas → steady key
```

**Invariants.**
- The steady figure cannot move with the measured start; the held start replaces it.
- The rate-limit slot is spent once per call, before the first solve (#1448, #1753); the 3 s `SIMULATE_MIN_INTERVAL_SECONDS` is untouched.
- `limited=False` callers never touch the slot or the card cache.

## Spike (scratch; reproduces the shape, never merges)

The spike solves `r10_advisor_residue.py`'s whatif rows with both plans from `_thermostat_held_state` at their own `get_comfort_temp`, using that harness's own fixtures and figure formula. It prints `rows 24 moves_by_start 0 degree_sign_disagrees 0/36 cap_saves 0/36`:
- Steady degree figures (null, then varying): 00:00 −31.1/+25.2 and −32.2/+28.8; 07:00 −41.3/+40.3 and −47.4/+42.5; 15:00 −39.2/+36.3 and −26.8/+37.9.
- Held figures on the same rows: ±51.5–80.0.
- Cap rows in the null read −0.7 to −0.3. That is solver noise above the harness's −1 threshold, so the sign check keeps the −1 tolerance; tightening it to 0 fails on noise.
- Wall per what-if pair: two steady solves mean 1.02 s, max 1.63 s; two live-start solves mean 1.12 s, max 1.89 s (24 h horizon at 15 min).

**Cost bound.** Base: 1 solve per what-if. After, a user what-if takes 3 solves on the first call against a scheduled plan and 2 after a memo hit. A degree tile takes 1. A cap tile or the fuse advisor takes 2 or 3 per scheduled record, sharing the memo. The fixer measures both, solve count and wall time per what-if, before and after on `tests/features.py`'s `_whatif_solves` counter (features.py:30450) and states the Pi bound as these counts times the measured per-solve wall.

## Alternatives, and why each lost

1. **The panel reads `monthly_held_cost_delta`.** 0 extra solves, but it prices a thermostat, not the plan: a cap reads 0 on every row (the thermostat ignores caps), and degrees read 1.6–2.8× the plan's steady figure.
2. **Settle the live-start figure (`monthly_settled_cost_delta`).** It moves by start (spread up to 89.9) and has the wrong sign on degree rows.
3. **Hold only the what-if, against the scheduled live plan.** One extra solve, but the difference mixes a held start with a measured one, so it moves with the start.
4. **Memo on a new coordinator attribute.** `coordinator_attrs` is at its cap; the state object instead lowers it by one.
5. **Disclosure only.** Refused by the owner's ruling (tvofi, 2026-11-01).

## Sibling sites

`git grep -n "monthly_cost_delta\|monthly_settled_cost_delta\|monthly_held_cost_delta\|async_simulate(" -- custom_components docs`:
- coordinator.py:9050/9082 and :10776, debugger.py:323 and services.py:767: covered in the table above.
- price_tiles.py:105-107, :142 and :188: covered (the steady key, then `monthly_figure`'s cap branch).
- heatpump-optimizer-card.js:9948 and :9961-9962: the Advisor tile, which reads the PriceTile mean, unchanged.
- heatpump-optimizer-card.js:13300 (`summary`): switches to the steady key.
- The harness and test doubles (`solve_inputs_parity.py`, `r9_dbg2_selftest_price.py`, `tests/debug_collect.py`, `tests/dst_checks.py`) keep the default and are re-run, not edited, unless a stub's signature refuses the new keyword.

## Evidence plan, by file

- **Failing tests first** (`tests/features.py`, beside :30481):
  - (a) `async_simulate` driven from the three `r10_advisor_degree.STARTS` with `target_plus_1`: the key the card reads spreads 0. It is red at the base: 24/24 rows move.
  - (b) Sign: warmer > 0 and cooler < 0 on the key the cap paths read, and no cap value below −1. It is red at the base on varying 00:00 (`monthly_settled_cost_delta` +24.6/−25.5).
  - (c) `tests/card.mjs`: `summary()` renders money only from the steady key, with the steady-state caveat line. With no draft result, the idle status renders no money and no caveat.
- **Finder's harness**: `r10_advisor_residue.py`'s whatif arm gains a steady column that calls the production `price_tiles.monthly_deltas` on solves started by the new optimizer wrapper. It must not re-implement either, because a test that re-implements a production formula pins nothing (`tests/README.md`). Run it at the base and at the head.
- **Null control**: held spread 0.00 on every row; the null series' steady figure is identical at all three starts, before and after; the idle panel shows no money.
- **Cost**: `_whatif_solves` counts 3 then 2 on a repeated call; a degree tile counts 1; the rate-limit test (:30481) still spends one slot for 5 calls.
- **Goldens**: `git grep -ln "monthly_cost_delta\|monthly_settled" tests/golden` decides whether a fixture moves. If one does, it is claimed in the claim file with its direction, never re-recorded.
- **Mutation targets**:
  - the what-if held start (fed the live state, so (a) goes red);
  - the live held start;
  - the deferred term in the steady key;
  - the memo key (ignoring the record, so a stale figure test goes red);
  - `steady` on the degree tile (passed True, so the tile test goes red);
  - the card's key.
- **Docs**: `docs/dashboard-card.md` :619-624's one-off sentence becomes "that panel prices the change in steady state, both plans started as if each schedule had been held, so its figure leaves out the one-off coast or heat-up". The what-if section (:451) says the money line is a steady-state monthly estimate. The paragraph also says why the panel's figure is about half the tile's: the tile prices a degree held by a plain thermostat, the panel the plan, which absorbs part of it by timing.

## Hot files and serial position

coordinator.py, optimizer.py, price_tiles.py, heatpump-optimizer-card.js, docs/dashboard-card.md, tests/features.py, tests/card.mjs, plus the new module. No `after` edges; the fixer rebases on whichever coordinator or card group merges first and re-runs `fixer.md` steps 2–8. Closes #2257; `fixes` must list 2257.

## Notes for the fixer

- Wood: `_thermostat_held_state` sets a two-tank install's wood tank to `_NO_WOOD_TANK_C`, so the steady figure prices no stored wood at the start. Pin this with a wood fixture, or state it in the docs. Carry: R10-ADVISOR-STEADY-START (item wood-start)
- Away: the held target is the scratch config's `get_comfort_temp` under `_whatif_banded`. A test with away on must show the what-if's held start uses the banded target. Carry: R10-ADVISOR-STEADY-START (item away-target)
- Tile against panel: after this change the tile and the panel disagree by design (about −54 against −31 per degree in the null). That is decided here, not left open. Carry: dismissed: decided in this note, tiles stay held (item tile-panel-gap)
- Received: carry 0 of this group (R10-ADVISOR-WHATIF's carry, #2963). This note implements all of it.
