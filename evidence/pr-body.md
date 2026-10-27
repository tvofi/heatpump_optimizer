`tools/plan/replan.py`'s `pick()` ordered candidates by remaining longest path alone, so the owner's dispatch priority (tvofi 2026-10-26) reached no schedule. This wires it in: **tier 0** is the critical path, recomputed by `critical_path()` from the roster graph at every replan and never stored; **tier 1** is a production group (`roster_lane()` in `Learners`, `Core model` or `Product UX`); **tier 2** is everything else, ranked by a per-group `savings` field on the roster, with an absent field sorting last; height breaks ties inside a tier. The t==0 live admission sorts by the same `priority()` function, so the static schedule and the instant admission cannot disagree. `plan_page.py` prints each group's tier, and `plan.json` carries it.

The same change makes the planner refuse a roster size `durations.json` does not measure. At the base, the live roster crashes the planner — `KeyError: 'XS'` from `size_hours[G[n].get("size")]` at `tools/plan/replan.py:325`, naming neither the group nor the roster. There are 8 roster groups sized `XS` and `sizes_hours` carries `L, M, S, XL`; four XS groups are marked done, but none carries a start or finish and none lies in the 25-group sample the table was measured on, so no XS duration is derivable from recorded data. Rather than invent one, the size is refused at the roster boundary with a message naming the group, the size and the roster path.

## Head

`012b795d930ba31e164c1b9a6a6021221007e84d` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2874.md`. The authored code head is `b13dc43bd994d685a5dd5ff40b08f53af877c6ba`.

`b13dc43bd`

## Mutation proof

Each row is one exact one-occurrence deletion inside a named function, applied by the in-file harness in `selftest()` (`REPLAN_MUTATION_CHILD` guards the nesting), which then requires the copy's `--self-test` to exit non-zero. The arm column is the check that goes red, quoted from that run.

| deleted | arm that goes red |
|---|---|
| `if n in crit:` → `if False:` | `FAIL the critical path is dispatched before the shorter work: {'CP': '2026-01-05T02:00:00Z', 'CP2': '2026-01-05T16:00:00Z', 'PROD': '2026-01-05T00:00:00Z', 'TALL': '2026-01-05T08:00:00Z'}` |
| `return TIER_PRODUCTION if lane[n] in PRODUCTION else TIER_OTHER` → `return TIER_OTHER` | `FAIL a short production group outranks a taller non-production one: {'CP': '2026-01-05T00:00:00Z', 'CP2': '2026-01-05T06:00:00Z', 'PROD': '2026-01-05T18:00:00Z', 'TALL': '2026-01-05T10:00:00Z'}` and `FAIL the t==0 live admission uses the same priority key: {'PROD': False, 'TALL': True}` |
| `sav = -savings[n] if n in savings else float("inf")` → `sav = 0.0` | `FAIL tier 2 ranks by savings, and absent savings sorts last: {'HI': '2026-01-05T18:00:00Z', 'LO': '2026-01-05T08:00:00Z', 'NONE': '2026-01-05T14:00:00Z'}` |
| `return (t, sav, -height[n], -dur_min[n], n)` → `return (t, sav, n)` | `FAIL height breaks ties within a tier, ahead of the name: {'AAA': '2026-01-05T08:00:00Z', 'ZZZ': '2026-01-05T10:00:00Z'}` |
| `key=priority` (the t==0 admission only) → `key=lambda n: (-height[n], n)` | `FAIL the t==0 live admission uses the same priority key: {'PROD': False, 'TALL': True}` |
| `if isinstance(s, bool) or not isinstance(s, (int, float)):` → `if False:` | `FAIL a non-numeric savings is refused: could not convert string to float: 'lots'` |
| `if size not in size_hours:` → `if False:` | `FAIL an unmeasured size is refused, naming roster, group and size: 'XS'` |

Both refusal arms began by catching `PlanError` alone, so deleting either guard escaped as an uncaught `ValueError` or `KeyError` — a crash, which is not a check. Both now catch any exception and still require the refusal's own message, which is why each row above goes red on its own assertion rather than on a traceback.

`tools/audit/seat/plan_page.py`'s Tier column has its own mutant in `dev/audit/harnesses/r10_plan_page_mutants.py` (`tier-column`, the cell → `"—"`), and it dies against the page's own check: `FAIL every open group's tier is shown, and a merged group's is not`.

### The required fixture, before and after

The priority fixture is a critical chain `CP → CP2`, a **short** production group `PROD` and a **taller** non-production group `TALL`, with one slot. Restoring the base `pick()` key (`(-height[n], -dur_min[n], n)`) and the base admission key while keeping the new fixtures fails three arms:

```
FAIL a short production group outranks a taller non-production one: {'CP': '2026-01-05T00:00:00Z', 'CP2': '2026-01-05T14:00:00Z', 'PROD': '2026-01-05T18:00:00Z', 'TALL': '2026-01-05T06:00:00Z'}
FAIL the t==0 live admission uses the same priority key: {'PROD': False, 'TALL': True}
FAIL tier 2 ranks by savings, and absent savings sorts last: {'HI': '2026-01-05T18:00:00Z', 'LO': '2026-01-05T08:00:00Z', 'NONE': '2026-01-05T14:00:00Z'}
self-test: 3 failed
```

At this head the same file prints `self-test: 0 failed`.

## Null control

The unmutated copy's self-test exits 0, asserted by the harness itself (`the unmutated copy's self-test exits 0 (null control)` → `rc=0`), so a mutation is what turns the suite red, not the copying.

The unmodified tree on the live roster is the base crash above: `KeyError: 'XS'` at line 325, rc 1. At this head the same command refuses cleanly:

```
refused: R10-FLY-SUITE-ENV-FLAKES: size 'XS' has no measured duration in sizes_hours (L, M, S, XL) -- roster dev/programme/rosters/wave-r10-groups.json
```

rc 2, naming the group, the size and the roster path. A fixture roster of measured sizes only still plans (`FAIL`-free `measured` arm), so the refusal is of the value, not of the planner.

## Figures

- `python3 -I tools/plan/replan.py --self-test` → `self-test: 0 failed`, 56 `ok`, 13 mutants all non-zero.
- `python3 -I tools/audit/seat/plan_page.py --self-test` → `plan_page self-test: 51 checks, 0 failed`.
- `python3 -I tools/audit/seat/plan_table.py --self-test` → `plan_table self-test: 25 checks, 0 failed`.
- `python3 -I dev/audit/harnesses/r10_plan_page_mutants.py` → `RESULT survived=0`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`, every metric at its budget and none above.
- `./tests/run.sh` with `GATE_SCOPE=auto` → `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`, final line `4 TEST SCRIPT(S) PASSED; 31 SCOPED OUT AND NOT RUN (see the NOT RUN block above -- this is not a full gate)`. The four that ran are the `run_always` ones — `env_drift --claims-only`, `closure.py selftest`, `harness_headers.py`, `layout.py` — and none of them opens these files. That is **zero coverage of this change, not a pass**: `tests/closure.py:336` declares `tools/plan/` INERT ("no gate script opens it"), so no suite script opens it either way, and the green mode line says only that the selection is empty. The proof of this change is the self-test and mutation runs above; the automated net that actually executes `replan.py --self-test` is the `governance / instrument-self-tests` CI job.

That gap is also why a planner defect reaches `main` unmeasured: the `XS` `KeyError` the live roster had been hitting was visible to nobody in CI, because no gate script opens `tools/plan/`. It was found by a seat running the planner by hand, and it is proven fixed here the same way.

## Red checks

none

## Forward-carry

- `dev/programme/rosters/wave-r10-groups.json`: 8 groups are sized `XS`, a value `tools/plan/durations.json` does not define, and nothing checks the roster's size vocabulary when it is written. `replan.py` now refuses it at the boundary by name. Carry: dismissed: the roster-vocabulary class is being root-caused in its own seat (coordinator, 2026-10-27), and the planner's side is closed by this change.

## Friction

none

