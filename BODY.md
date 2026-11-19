R11-READS-RESIDUE: the two carries on the product reads (owner exception to the P11 freeze, tvofi 2026-11-18). Both were re-measured at the merge base, and both reproduce there.

- Carry 0 (items c9cc8bee, population levels of `tank_volume` and `house_size`). `check_scopes.py --population` printed both axes as `NO-READ`, so `plant_recall.py plant` refused a config plant in any of their six cells as `no population level`. This PR adds a population kind `flow_range` to `check_scopes.population`. An axis of this kind declares its levels (min, default, max), and its `rows` name each options-flow key and default constant. The reader finds every `_number(lo, hi, ...)` call that presents the key in `file`, as a widget-dict value or as an argument of the same `_F` call (a starred range constant is expanded). It reads the default constant from the file or its `const.py`, and checks every declared level against what the row reads. The axis is UNREADABLE, and the command exits 1, in each of these cases: a level that differs from its row, a key that no `_number` row presents, rows that disagree, or a level other than the three. So a moved flow row never leaves a stale level printed. `objective.json` moves both axes from `kind: null` to `flow_range`, with their rows, and keeps the declared levels and basis unchanged. `plant_recall.py` is unchanged, as the carry says. It accepts the six cells once `--population` prints them.
- Carry 1 (items c3a1b4ef, operation seed ledger). `dev/audit/rounds/round11/product-reads/operation.tsv` held 6 rows in the retired `duty=control | running` cell format, which `product_reads.py operation --ledger` refused. The re-cut needs a judgement, so it uses the read's own record. For each cited check, the recorder (`product_reads.run_script` on `tests/guard_pins.py`) lists the per-state tokens that hold at the cited site before the check. For all five checks at `pump_arbiter.py:1610` and at hold site `:630`, the only states recorded are `idle` (9 writes, 9 holds; duty control, a plan step, ordinal 0) and `baseline` (5 writes, 1 hold; plan held, no step). Each of the 6 rows is cut into those two cells, which gives 12 rows. The item text also moved to the census's current `_write domain=?` spelling.

Policy: the diff touches `dev/governance/decisions/0018-objective-function.md`, one sentence. That sentence said a continuous axis "has no tracked levels: it is NO-READ in that file", which stops being true at this head. It now says that the levels the file declares are read against their flow rows and that a moved row refuses. `objective.json`, `check_scopes.py` and the decision are code-owned, so this needs the owner's approving review (or one under the mandate) before merge.

## Head

Code head e395a9f66ff9aadb2276ad95e275ecc3a6d1d443, cut from origin/main cb8edb65a5a9c0940dbe263acee49e02ba5f0b25 (merge base), measured 2026-11-19T11:04Z. `base_fresh.py tree` passed at the start (stale 0, own 0).

prepr: passed rc=0 at e395a9f66ff9aadb2276ad95e275ecc3a6d1d443 (PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1). CI is the authority for the code-keyed steps.

## Mutation proof

Run against `check_scopes.population_self_test()` (`python3 -I tools/audit/check_scopes.py --self-test --repo .` runs it). Each mutant replaces one predicate line of `flow_range_levels`, or its dispatch line in `levels`, and the file is restored afterwards (`git status` clean). The unmutated arms all held. Before the reader existed, the three positive arms failed: "a flow-range axis prints its declared levels once each matches its row", "... not its row's bound is UNREADABLE by level and key" and "... not the row's default constant is UNREADABLE".
- `or float(want) != read[name]:` -> `:`. Red: "a flow-range level that is not its row's bound is UNREADABLE by level and key", "a flow-range level that is not the row's default constant is UNREADABLE".
- `if len(found) != 1:` -> `if False:`. Red: "a flow-range key no _number row presents is UNREADABLE by key", "a flow-range key whose _number rows disagree is UNREADABLE".
- `if not lv or set(lv) - {"min", "default", "max"}:` -> `if False:`. Red: "a flow-range level other than min, default and max is UNREADABLE by name".
- `if k == "flow_range":` -> `if False:`. Red: all six flow-range arms.

## Null control

- Live tree, carry 0: in a throwaway commit (reset afterwards), the tank row's `_number(50, 1500, 10, 'L')` was changed to `_number(60, ...)`. `check_scopes.py --population` then printed `UNREADABLE tank_volume: level min declares 50 for CONF_DHW_TANK_VOLUME, the flow row reads 60` and exited 1. The unmoved head prints the levels and exits 0.
- For both ends of the plant harness: `layout=no_valve` is accepted and `layout=moon` is refused, at base and at head.
- Carry 1: at the base, the read refuses the committed ledger (exit 2, no RESULT line). At the head it reads it. On the same rows, its verdicts separate moved from unmoved checks (Figures).

## Figures

- `python3 -I tools/audit/check_scopes.py --repo . --population`. At the base: `tank_volume NO-READ`, `house_size NO-READ`, `NO-READ AXES: 2`. At the head: `tank_volume 3 default,max,min`, `house_size 3 default,max,min`, `NO-READ AXES: 0`, rc 0.
- The carry-0 harness: the output of `python3 -I tools/audit/check_scopes.py --repo . --ref <ref> --population` is passed to `plant_recall.population` (`tools/audit/seat/plant_recall.py`). At base cb8edb65a5, all six of `tank_volume=` and `house_size=` `min|default|max` print `no population level`. At head e395a9f66f, all six are accepted. The control rows are as above.
- `python3 -I tools/audit/product_reads.py operation --ledger dev/audit/rounds/round11/product-reads/operation.tsv --jobs 3`. At the base: `REFUSE: ...operation.tsv:2: '... _write | duty=control | running' is no item of this universe as printed`, exit 2. At the head: rc 0. `idle`: GCHV writes, hold and write_ints are `moved`; daytime and R9-SW-2 are `the check does not move`. `baseline`: daytime is `moved`, and the other four are `the check does not move`. Both hold rows are `reached`. The RESULT line reads 4 moved, 2 reached.
- `python3 -I tools/audit/seat/plant_recall.py --self-test`: ok (with mutants). `python3 -I tools/audit/enumerate.py --self-test`: SELF-TEST passed (166 arms). `python3 -I tools/audit/check_scopes.py --self-test --repo .`: `population arms: 19/19 held`, `SELF-TEST passed (every perturbed scope refused)`, rc 0. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.

<!-- figure-block: scope-line mb=cb8edb65a5a9c0940dbe263acee49e02ba5f0b25 head=e395a9f66ff9aadb2276ad95e275ecc3a6d1d443 -->
~~~text
MODE: SCOPED -- 0 script(s) run, 33 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

none
