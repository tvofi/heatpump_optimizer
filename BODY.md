R11-PRE-PRODUCT-READS part 1 of 2 (design `design/R11-PRE-PRODUCT-READS` at 8daf118368, `Design review: approve` at a08d8f47c9): `tools/audit/product_reads.py`, which reads decision 0018's `operation` and `generality` off a seat's cell ledger and counts a row only on a witness the read produced itself; decision 0018 names this group as the builder of `regret`, `operation` and `generality`'s examined count, and R11-PRE-ROUND-METRICS for `escapes` and `unowned` (design 3.6). Part 2 (`regret`: the same-information oracle and the install-day record) is the approved plan's second pull request. No production file and no file under `tests/` other than `tests/layout.json` is edited. Universes are imported from `tools/audit/enumerate.py` (R11-PRE-BRIEFS-CENSUS, merged as #3625), never enumerated a second time.

How each read witnesses, per the design:
- `operation` (3.2): each cited script runs unedited under a launcher (wrappers on `harness.Results.check`, `FakeServices.async_call` installed as a plain function per n1, `FakeEntry`, `pump_arbiter.apply`, the coordinator's constructor, and `log_held` in each importing module's namespace through a post-import hook), twice as it is, then once per cited (site, cell state) with the payload from that site perturbed **only in `apply` passes whose recorded state is the cell's** (v2-1). The state is read off the plan the coordinator holds at `apply` entry by plain indexing; a token with no table entry prints `state not recorded`. Writes outside every pass are printed per site, never witnessed (v2-2).
- v2-3 answered: `arbiter_inputs()` is not read-only for this read: it calls `pump_arbiter.live_power_kw`, which reads through `InputReader` (`inputs.py` binds `log_held`), so an extra call could record a hold the code under test never made. The wrapper reads `coord._optimization_result` and `coord.effective_config` (else `_config`) directly.
- `generality` (3.3): a level row counts only when the read's own run, with that level's observable switched to the next level of its axis in the recorded configuration, turns the check FAIL or changes its detail; a pair only when both its levels are witnessed in one configuration of one script (`--pairs-out` writes them in `enumerate.py d12-cells --pairs --ledger`'s format). Bundle and install-report rows are printed and never counted.
- One departure, raised here: `restart` is read as "not the first coordinator **built** on its entry object" for the real class, and, for a test's own fake coordinator that is never built through it (e.g. `tests/guard_pins.py`'s `Coord`), "not the first seen at `apply`" on that entry object. The design names construction only; with construction only, every fake-coordinator pass would print `state not recorded` and F5's checks could never be witnessed. Keyed on the entry object, not `entry_id`, because `FakeEntry()` defaults every entry to one id.
- At this base `d16-writes --cells` prints duty x {running, restart, upgrade, unavailable} (the census formula, NEW-DIMENSIONS not merged): `upgrade` prints `state not recorded`; the plan-state rows (idle, dhw-only, both, partial, full, min-cold-tank, baseline) are in the table and pinned by direct arms, read the day the formula changes (n10).

## Head

ede3434ae196bc16171a6ac25fa1b8a8354452c1. Merge base and origin/main 1f7c59ebc4 at 2026-11-16T08:29:49Z. The live reads in `## Figures` ran at fd206bef2c; `git diff --stat fd206bef2c ede3434ae1` touches only `tools/audit/product_reads.py`'s self-test (one arm).

## Mutation proof

Rule: one mutant per line the design names as a target (section 6) plus each hold-patch and order guard, applied to a scratch copy of `tools/audit/`, then `python3 -I tools/audit/product_reads.py --self-test` run there; an anchor not found exactly once counts as a failed (vacuous) mutant. 16 mutants, 16 killed, 0 vacuous, at fd206bef2c; the arm each turns red:
- state equality, `all(` -> `any(` over the cell's tokens: `planted (iii): a first-coordinator check cited for restart: state differs`, `planted: another duty mode differs`
- the `state differs` branch removed: the same two arms
- perturbation not limited to passes of the cell's state (v2-1): `planted v2-1: a check on the restart write, a running write before it, cited for running`, `RESULT counts distinct cells`
- moved comparison reduced to `a["ok"]`: `planted (i): a constant-condition check does not move`
- generality's switch-run comparison removed: `planted (i): a constant check after a configuration carrying the level: reached, not witnessed`
- same-ordinal pair test keyed on ordinal 0: `null: two levels witnessed in one configuration make their pairs; planted (iii)`, `the pair rows are a ledger enumerate.py d12-cells --pairs accepts`
- nondeterminism guard, operation: `planted: a check whose detail embeds a counter is never moved`; generality: `planted (iv): a check whose detail embeds a counter`
- exit-2 guards, empty ledger: `operation: an empty ledger exits 2`, `generality: an empty ledger exits 2`; a row naming no item: `operation: a ledger row naming no item exits 2`
- `restart` as `>= 0`: `planted (iii)`; unknown token returning `True`: `planted (iv): a token with no table entry`
- plan state `both` read as `partial`: `plan state: both`
- hold patch table emptied: `null: a hold in a second importing module (off_restore) is reached`; the arbiter's own `log_held` binding unpatched: `null: a hold under the per-module log_held patch is reached`
- the before-the-check order on a configuration: `planted: a configuration built after the check carries nothing for it`

`prepr.sh` step 6d with `MUTANT_CMD="python3 -I tools/audit/product_reads.py --self-test"`: survivors at fd206bef2c are the four under `## Unpinned sites` plus `token_holds`' plan-state branch, killed at ede3434ae1 by `token: a plan-state token reads the recorded plan state`.

## Unpinned sites

- `tools/audit/product_reads.py` `sys.path.insert(1, ...)` (CONST_SWAP of the index): equivalent; the import of `enumerate` resolves at either position, and the launcher rebuilds `sys.path` before any script runs.
- `RUN_TIMEOUT_S` 900 -> 901: a bound on a hung child, not a value any verdict reads.
- `_perturb`'s offset 7.0 -> 14.0: any non-zero offset is a different payload; the rule is "numbers offset", not a magnitude.
- `plan_state`'s `0 < s` -> `0 <= s` in the `partial` branch: equivalent; `s == 0` returns `idle` or `dhw-only` two branches earlier.

## Null control

- `python3 -I tools/audit/product_reads.py --self-test` prints `SELF-TEST passed (54 arms)` at ede3434ae1; its null arms are the design's: a payload-comparing check cited for its own cell is `moved` with `target=plan`; the fixture with no site perturbed turns no check; a hold under the per-module patch is `reached`, and a recorder wrapping `log_latch.log_held` once the package is imported records 0 holds from the same fixture (r1); a key-presence check with its level switched is `witnessed`, two in one configuration make their pairs; an axis with no table entry prints `no witness`.
- Live, `tests/guard_pins.py` unperturbed under the launcher: 88 checks, none FAIL (the same count as `PYTHONPATH=tests/hastub python3 tests/guard_pins.py`'s `ALL 88 GUARD PIN CHECKS PASSED`), so the wrappers change no outcome.
- `replay_doc.py` `ATTRIBUTE_KEYS` (n8's premise): an AST read of the frozenset finds no key containing `forecast`; the same read finds `today` and `tomorrow`, so it reads the set.

## Figures

<!-- figure-block: scope-line mb=1f7c59ebc47bb506dcbcf5793d7a220efb338c60 head=ede3434ae196bc16171a6ac25fa1b8a8354452c1 -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- `operation` live, seed ledger `dev/audit/rounds/round11/product-reads/operation.tsv` (F5's checks at `pump_arbiter.py:1610 _write`, cell `duty=control | running`, the state each drives): `python3 -I tools/audit/product_reads.py operation --ledger dev/audit/rounds/round11/product-reads/operation.tsv` -> exit 0, `RESULT read=operation universe=456 examined=2 moved=4 reached=1`. Four checks `moved` with `target=no plan value` (night-mode number writes, no plan number); `R9-SW-2 mode writes its option` is `not witnessed: the check does not move`: it moved with the site perturbed in every pass, and its write is one of the 3 at that site outside every `apply` pass (`outside every pass ... pump_arbiter.py:1610 3`), so no plan state witnesses it (v2-2). The hold row `pump_arbiter.py:630 _space_target` is `reached`. No `unlisted writer` line (n7).
- `generality` live, seed ledger `dev/audit/rounds/round11/product-reads/generality.tsv` (seven level rows on `tests/config_flow_steps.py`): `python3 -I tools/audit/product_reads.py generality --ledger dev/audit/rounds/round11/product-reads/generality.tsv` -> exit 0, `RESULT read=generality universe=18897 examined=3 levels=3 pairs=0 reached-only=4`. Witnessed: `two_zone_mode=off` (configuration 17), `two_zone_mode=on` (18), `CONF_WOOD_TANK_TOP_ENTITY=present` (27). Reached only, the check unmoved by the switch: `CONF_DHW_SETPOINT_ENTITY=present`, `CONF_INDOOR_TEMP_ENTITY=present` (cited on the two_zone_mode=off check, its pair therefore not counted), `space_setpoint_unit=flow`, `structure=timber_slab`. `checks with no recorded configuration=7` (n3).
- Universes, the rule: `python3 -I tools/audit/enumerate.py d16-writes --cells | wc -l` (456) and `python3 -I tools/audit/enumerate.py d12-cells --pairs | wc -l` (18897), each printed again on the read's `RESULT` line.
- Cost (n2), one launcher run: `tests/guard_pins.py` about 11 s, `tests/config_flow_steps.py` about 27 s, `tests/dst_checks.py` about 64 s; the generality seed read took 87 s wall on this container with the default `--jobs`. `tests/features.py` was not timed.
- `python3 tests/structure.py` -> `STRUCTURE RATCHET PASSED`. Architecture score: dS +0.0000 (`python3 -I tools/audit/archscore/score.py --diff 1f7c59ebc47bb506dcbcf5793d7a220efb338c60`; no package file changes).
- Sibling sites (design section 5): `git grep -n "R11-INTAKE-R10-RESIDUE" -- dev/governance/decisions/0018-objective-function.md dev/audit/config/objective.json dev/audit/README.md dev/audit/yardstick/round10/OBJECTIVE.json` at the head. 0018: the D0 and D12 rows, the `generality` and `operation` bullets, the `regret`, `operation`, `generality`, `unowned`, `escapes` rows and the three gaming rows are edited (3.6), and the Consequences line adds this group beside the holding group; still naming it, not edited: the D1, D2, D8, D11, D15 rows, `coverage` and the `objective.json` axis builders (other groups' builds; decision: orchestrator), and three hits in none of the design's classes, reported not edited: line 319 (a finding fixed correctly), the `unexamined` and `injected` gaming rows. `dev/audit/README.md`'s two hits (the holding group's carry list, step 3's denominator) repeat no row of these reads: not edited. `dev/audit/yardstick/round10/OBJECTIVE.json`: round 10's record, 7 hits, not edited (r3).

## Red checks

none

## Forward-carry

- Part 2 of the approved plan: the regret oracle script under `tools/audit/` and its guide (design 3.4, the grid and the install-day record, with section 6's regret controls). Carry: R11-PRE-PRODUCT-READS
- n8, measured above (`ATTRIBUTE_KEYS` holds no forecast): D15 step 9 asks a seat for `C_same` per install-day, which no bundle can give; part 2 prints it NO-READ with that reason, and the brief's wording is part 2's to align, its owning group being carries-open. Carry: R11-PRE-PRODUCT-READS
- n6, the interface of design 3.5 (one command printing each escape in the window with id, released version, found-by, owning dimension or `none`, objective bug or owner report, then a count line; absent input prints unread), and its gap: `unowned` also counts owner reports that are no objective bug. Its seam is R11-PRE-ROUND-METRICS' by Carry 0, which is carries-open, so `carry_audit.py` keeps it with the producer for the relay to fold; this group builds no escapes record. Carry: R11-PRE-PRODUCT-READS
- n11: `dev/audit/rounds/round10/objective/escapes_hand.tsv` is a hand-read escapes ledger with owner and ruling columns; the round-metrics instrument should read rows of that shape; routed as n6. Carry: R11-PRE-PRODUCT-READS
- n7: the seed run printed no `unlisted writer`, so there is no run-measured finding for the sibling design's F3. Carry: dismissed: no unlisted writer on the seed run, nothing measured to carry

## Friction

none
