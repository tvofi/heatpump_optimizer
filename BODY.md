R11-READS-RESIDUE: the two carries on the product reads (owner exception to the P11 freeze, tvofi 2026-11-18). Both were re-measured at the merge base, and both reproduce there.

- Carry 0 (items c9cc8bee, population levels of `tank_volume` and `house_size`). `check_scopes.py --population` printed both axes as `NO-READ`, so `plant_recall.py plant` refused a config plant in any of their six cells as `no population level`. This PR adds a population kind `flow_range` to `check_scopes.population`. An axis of this kind declares its levels (min, default, max), and its `rows` name each options-flow key. The reader walks `file` and reads every value it pairs with the key. Bounds are each `_number(lo, hi, ...)` widget beside the key, as a dict's value or as an argument of a call that carries the key (a starred range constant is expanded); they must agree. Defaults are every other value paired with the key: a dict's value for it, the argument after it in a call (the `_F` row's default argument), and a `default=` keyword of such a call. Each must read as a number, either a literal or a constant in the file or its `const.py`, unless the row's `no_default` lists it as a marker that presents none. The heat-loss row lists `_SUGGESTED`, which offers the stored value or none. Every declared level is checked against every value read for it. The axis is UNREADABLE, and the command exits 1, in each of these cases: a value that differs from its level, a default that is no number, a key with no widget or no default, widgets that disagree, a level other than the three, or a row field the reader does not read. `objective.json` moves both axes from `kind: null` to `flow_range`, with their rows, and keeps the declared levels and basis unchanged. `plant_recall.py` is unchanged, as the carry says. It accepts the six cells once `--population` prints them.
- Carry 1 (items c3a1b4ef, operation seed ledger). `dev/audit/rounds/round11/product-reads/operation.tsv` held 6 rows in the retired `duty=control | running` cell format, which `product_reads.py operation --ledger` refused. The re-cut needs a judgement, so it uses the read's own record. For each cited check, the recorder (`product_reads.run_script` on `tests/guard_pins.py`) lists the per-state tokens that hold at the cited site before the check. For all five checks at `pump_arbiter.py:1610` and at hold site `:630`, the only states recorded are `idle` (9 writes, 9 holds; duty control, a plan step, ordinal 0) and `baseline` (5 writes, 1 hold; plan held, no step). Each of the 6 rows is cut into those two cells, which gives 12 rows. The item text also moved to the census's current `_write domain=?` spelling.

Fix review round 1 (`review/3816`, blocked at 5a4b43320394fb57480d835773d02913eb1de4cd, class-open) found that the reader took the default from the one const.py constant the record named, so a `_F` row default argument or a questionnaire-defaults value moved off it (P3, P4) still printed the old level at rc 0. The delta from 5a4b4332 closes that class: the record no longer names a default constant, and the reader reads every value the flow file pairs with each key (Figures: the census of every occurrence, and every value-carrying one planted).

Policy: the diff touches `dev/governance/decisions/0018-objective-function.md`, one sentence. That sentence said a continuous axis "has no tracked levels: it is NO-READ in that file", which stops being true at this head. It now states what the reader does: the declared levels are read in the flow module against every value it pairs with the row's key, minimum and maximum against each `_number` widget's bounds and default against each other value, less the markers the record lists; a differing or non-numeric value, or a key with no widget or no default, refuses the axis. Round 1's note that the earlier wording ("a row that moves makes the command refuse, never print a stale level") claimed more than the code read is answered by this rewording. `objective.json`, `check_scopes.py` and the decision are code-owned, so this needs the owner's approving review (or one under the mandate) before merge.

## Head

Code head 68ee4edddfabcf63e6d205cb675d98e7a35638d4, one commit on the reviewed head 5a4b43320394fb57480d835773d02913eb1de4cd (delta for the reviewer: `git diff 5a4b43320394fb57480d835773d02913eb1de4cd 68ee4edddfabcf63e6d205cb675d98e7a35638d4`, three files: `tools/audit/check_scopes.py`, `dev/audit/config/objective.json`, `dev/governance/decisions/0018-objective-function.md`). Merge base and origin/main cb8edb65a5a9c0940dbe263acee49e02ba5f0b25, measured 2026-11-19T12:33Z. `base_fresh.py tree` passed at the start (stale 0, own 0). `git merge-tree --write-tree origin/main HEAD` rc 0.

prepr: scoped (PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1) at 68ee4edddfabcf63e6d205cb675d98e7a35638d4; CI is the authority for the code-keyed steps.

## Mutation proof

Run against `check_scopes.population_self_test()` (`python3 -I tools/audit/check_scopes.py --self-test --repo .` runs it). Failing test first: the round-2 arms were added before the reader changed, and the old reader held 16 of 27, with 11 red (the 8 new default arms, and the 3 positive arms whose fixture no longer names a default constant). With the reader changed, 27/27 held. A 28th arm was then added to kill mutant D7 below. Each mutant below replaces one line of the new default read in `flow_range_levels`, in an in-tree copy that is removed afterwards. The unmutated copy holds 28/28. All 11 are killed:
- D1 a dict's non-widget value not read as a default. Red: "a flow-range defaults-dict value that moved off the level is UNREADABLE by line", plus 4 more.
- D2 the argument after the key in a call not read. Red: "a flow-range `_F` row whose default argument moved off the level is UNREADABLE by line", plus 3 more.
- D3 the `default=` keyword not read. Red: "a flow-range default= keyword that moved off the level is UNREADABLE by line".
- D4 `no_default` ignored. Red: "a flow-range axis prints its declared levels once each matches its row", plus 2 more.
- D5 every `_`-prefixed name skipped as a marker. Red: "a flow-range default the record does not list as presenting none is UNREADABLE".
- D6 a key with no default accepted. Red: "a flow-range key presented with no default is UNREADABLE", "a flow-range key whose only defaults are recorded markers is UNREADABLE".
- D7 only the first default compared. Red: "a flow-range default that moved is UNREADABLE though an earlier one still matches (every default is read)".
- D8 an unreadable default skipped. Red: "a flow-range default the record does not list as presenting none is UNREADABLE".
- D9 an unread row field accepted. Red: "a flow-range row carrying a field the reader does not read is UNREADABLE".
- D10 every later positional argument read as a default. Red: 6 arms, among them "a flow-range axis prints its declared levels once each matches its row" (the fixture's `_F` row carries a positional argument after its widget that is no default).
- D11 default compared to the lower bound. Red: 10 arms.
The mutants of round 1 (min and max swapped, no const.py fallback, dict and call branches, starred expansion, `field`) ran on lines this delta leaves unchanged. Round 1's review re-ran them and killed them all.

## Null control

- Live tree, in throwaway commits each reset afterwards, `--population` at each end. At the reviewed head 5a4b4332, 6 plants print a stale level at rc 0: P3 (the tank `_F` default argument at 300.0), P4 (the questionnaire `CONF_HEATED_AREA` default at 180.0), the DHW presence-pair default at 250.0, the wizard heat-loss default at 0.2, the wizard tank default at 220.0, and the heat-loss `_F` row's `_SUGGESTED` changed to the literal 0.3. At 68ee4edd, all 6 print `UNREADABLE <axis>: level default declares <level> for <key>, ...config_flow.py line <n> presents <value>`, rc 1. Two plants that move no level stay accepted at rc 0 at both heads: the tank default argument replaced by the literal 200.0, and the heated-area widget step changed from 5 to 10.
- The carry-0 harness, at both ends: `layout=no_valve` is accepted, and `layout=moon` and `tank_volume=typical` are refused, at the base, the reviewed head and this head.
- Carry 1: at the base, the read refuses the committed ledger (exit 2, no RESULT line). At the head it reads it. On the same rows, its verdicts separate moved checks from unmoved ones (Figures).

## Figures

- The class census (step 8). Every `ast.Name` occurrence, in `config_flow.py`, of each row key `objective.json` names, classified by its parent node. This is an independent walk, not the reader. At 68ee4edd it finds 9 occurrences. 7 of them pair the key with a value, and the reader reads all 7: `CONF_DHW_TANK_VOLUME` at the `_F` row (widget and default argument) and at the presence-pair and wizard defaults dicts; `CONF_HEATED_AREA` at the questionnaire defaults dict and the widgets dict; `CONF_HOUSE_HEAT_LOSS_COEFFICIENT` at the `_F` row (widget, and the `_SUGGESTED` marker the row records) and at the wizard defaults dict. The other 2 pair the key with no value: the `_ABSENT_IS_NOT_DEFAULT` set and the `DERIVED_THERMAL_KEYS` tuple. Each of the 7 is planted: 15 plants in all, covering min, default and max of every row, a const.py constant for each default, and the range constant. At 68ee4edd all 15 refuse at rc 1, naming level, key and either `the flow row reads` or the line. At 5a4b4332, 9 refuse and 6 print at rc 0 (Null control). The census command is a python ast walk over `objective.json`'s flow_range rows, which this PR does not commit; it is in the fixer's report.
- `python3 -I tools/audit/check_scopes.py --repo . --ref <ref> --population`. At the base: `NO-READ AXES: 2`. At 5a4b4332 and at 68ee4edd: `tank_volume 3 default,max,min`, `house_size 3 default,max,min`, `NO-READ AXES: 0`, rc 0.
- The carry-0 finder harness, run at each end from that end's own checkout: the `--population` output is passed to `plant_recall.population` (`tools/audit/seat/plant_recall.py`). At base cb8edb65a5, it accepts 0 of the six `tank_volume=` and `house_size=` `min|default|max` cells. At 5a4b433203 it accepts 6/6, and at 68ee4edd 6/6. The controls are as above.
- Carry 1, `python3 -I tools/audit/product_reads.py operation --ledger dev/audit/rounds/round11/product-reads/operation.tsv --jobs 3`, at 68ee4edd: `RESULT read=operation universe=532 examined=4 moved=4 reached=2`, rc 0. This delta does not touch the ledger or the read. At the base it exits 2 with a REFUSE at line 2.
- `python3 -I tools/audit/check_scopes.py --self-test --repo .`: `population arms: 28/28 held`, `SELF-TEST passed (every perturbed scope refused)`, rc 0. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.

<!-- figure-block: scope-line mb=cb8edb65a5a9c0940dbe263acee49e02ba5f0b25 head=68ee4edddfabcf63e6d205cb675d98e7a35638d4 -->
~~~text
MODE: SCOPED -- 0 script(s) run, 33 scoped out.
~~~
<!-- /figure-block -->

## Red checks

Inherited from main, not caused by this change. The diff touches `tools/audit/check_scopes.py`, `dev/audit/config/objective.json`, the 0018 decision, the operation ledger and this PR's delivery row, and none of the files below.

- `tests/features.py` lift-peak check: main's `ci.yml` run at cb8edb65a5 concluded failure on it, a solver float that drifts across BLAS kernels. Hotfix #3815 (R11-CARRY-ROOM-LIFT, which checks within 1e-3 K) is open and repairs it on main. No changed file is in any measured closure (the scope line above).
- code-scanning alert 57 (py/overly-permissive-file): an open alert on `refs/heads/main` on `tools/audit/seat/postmerge.py`, raised before this head and outside this diff; it is main's to answer.
- code-scanning alert 58 (py/overly-permissive-file): an open alert on `refs/heads/main` on `tools/audit/seat/roster_lib.py`, raised before this head and outside this diff; it is main's to answer.
- code-scanning alert 59 (js/insecure-temporary-file): an open alert on `refs/heads/main` on `dev/audit/rounds/round11/D13/s1/window_fetch.mjs`, raised before this head and outside this diff; it is main's to answer.
- code-scanning alert 60 (js/file-system-race): an open alert on `refs/heads/main` on `dev/audit/rounds/round11/D13/s1/window_fetch.mjs`, raised before this head and outside this diff; it is main's to answer.
- code-scanning alert 61 (py/insecure-temporary-file): an open alert on `refs/heads/main` on `dev/audit/rounds/round11/D1/s3/log_flood.py`, raised before this head and outside this diff; it is main's to answer.
- code-scanning alert 62 (py/insecure-temporary-file): an open alert on `refs/heads/main` on `dev/audit/rounds/round11/D1/s3/persist_family.py`, raised before this head and outside this diff; it is main's to answer.
- code-scanning alert 63 (py/insecure-temporary-file): an open alert on `refs/heads/main` on `dev/audit/rounds/round11/D1/s3/silent_broad.py`, raised before this head and outside this diff; it is main's to answer.
- code-scanning alert 64 (py/incomplete-url-substring-sanitization): an open alert on `refs/heads/main` on `dev/audit/rounds/round11/D6/s1/ledger.py`, raised before this head and outside this diff; it is main's to answer.
- code-scanning alert 65 (py/incomplete-url-substring-sanitization): an open alert on `refs/heads/main` on `dev/audit/rounds/round11/D11/s2/provenance.py`, raised before this head and outside this diff; it is main's to answer.
- code-scanning alert 66 (py/overly-permissive-file): an open alert on `refs/heads/main` on `dev/audit/rounds/round11/D11/s1/seat_selftest_sweep.py`, raised before this head and outside this diff; it is main's to answer.
- code-scanning alert 67 (py/overly-permissive-file): an open alert on `refs/heads/main` on `dev/audit/rounds/round11/D11/s1/seat_selftest_sweep.py`, raised before this head and outside this diff; it is main's to answer.

## Forward-carry

none

## Friction

none
