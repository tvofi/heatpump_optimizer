# Round 9, class P2: root cause and plan fold

Seat: round-9 RCA, class P2 (N=27), slug `p2`. Baseline `1936d5ca` (v6.7.1); main at `db878b29`.
Prototype on `handoff/r9-rca-p2` (cut from origin/main):
`tools/audit/round9/rca/p2/owners_lint.py`, sha1 `3aad65da7e9a2656e1d5ff32bb14bc82f777f772`.
Every figure below names the command that produced it. The load figure is this container's
(4 cores, load1 about 12), so the timings are upper-side.

## Root cause

### Cause

When a fact is used at several places, each place decides it with its own local copy of the rule
(a proxy key, a threshold, a stamp chain, a literal service domain). Nothing names one owner of
the fact that other code has to call. So a fix, or a new feature, updates one copy and leaves the
others as they were. The 27 findings are 27 facts of this shape, not 27 copies of one fact. S1
confirms this: only D14-s2-01 has a package-wide enumerator, and the other 26 were each widened
from their own seam rule.

Reproduced at `1936d5ca`:

- D14-s2-01. Run with `PYTHONPATH=tests/hastub /home/claude/venv314/bin/python p2_facts.py`
  (S1's `enumerator.py`, copied unmodified):
  - `derive_preset_disagree=20` of 40;
  - `prefill_refused_or_missed=20` of 40;
  - `wood_picture_vs_model_disagree=2` of 21;
  - each is 0 under the perturbation that routes the seam through its predicate;
  - null control `null_control_disagree=0` of 20.
- D1-s5-01. In memory at baseline, `inputs.age_of` returns 300.0 min for a state reported 1 min ago
  and last updated 5 h ago; InputReader's rule prefers `last_reported`. For a stamp 2 h ahead it
  returns -120.0 min, where InputReader treats that stamp as stale (#775).
- Static: `python3 tools/audit/round9/rca/p2/owners_lint.py --ref 1936d5ca` fails 5 of its 6
  entries at the instance sites. Section B below gives the seams.

**Which side moved** (checked with `git log -S`, not taken from the error text). Three
histories, one per way the second copy appears:

1. **A fix updated one copy and noted the sibling.** `a1bdb11c` (#792, fixing #775, 2026-09-11)
   made InputReader treat a future stamp as stale. It added a second copy of the stamp chain
   (`_age_gate`) and left `age_of` alone. Its commit body says "Coordinator humidity still uses
   age_of against utcnow". The lint, run at `a1bdb11c^` and at `a1bdb11c`, finds the stamp shape
   at 5 and then 8 sites.
2. **A fix enumerated its siblings and dispositioned them wrongly.** `3602b6ca` (#1479, fixing
   R7-D12-01, 2026-09-23) moved the flow-target guard onto `ThermalParameters.from_config`. Its
   PR body carries a step-8 class enumeration that returns 3 sites:
   - it closes 1;
   - it calls `config_flow._derive_preset` "distinct … never a save gate";
   - it calls `modbus_prefill._plant`'s suggestion side "a display choice, not a correctness
     gate".

   Round 9 measured those two sites as the D14-s2-01 defect (20 of 40 cells each, above). The
   lint's `two_zone_enabled` entry reads 3 seams at `3602b6ca^` and 2 at `3602b6ca`.
3. **A feature added a sibling after the canonical rule had landed.** #1576 (R8-P6, merged
   2026-09-24T18:03Z) added `coordinator._on_off_service`, which routes an entity write by the
   entity's own domain. It also added a P6 census in `tests/features.py`. The pump-duty arbiter
   (`3b320405`, merged into its branch with main at 21:09 the same day) writes the mode slot with a
   literal `"select"`, which is D12-s2-02. The census did not catch it. The census skips any slot
   that accepts `sensor` (`if key in _P6_READ_ONLY or "sensor" in domains: continue`), and the
   mode slot accepts `("select", "sensor", "input_select")` (`topology._MODE`). #1576 states the
   assumption this depends on: "No written slot accepts `sensor` today." The arbiter made that
   false a few hours later. The lint's `entity_write_domain` entry reads 1 stray seam at
   `2a451021^` (`coordinator._apply_action`, the #1526 defect) and 0 at `2a451021`. At
   `1936d5ca` it reads 1 (`pump_arbiter._write`).

### Class search: what else the same cause reaches, beyond S1

The prototype's six registry entries, run over the whole package at `1936d5ca`:

- **A fourth copy of the on-threshold.** `coordinator.py:9736`
  (`_observe_compressor_start`) holds `max(0.1, 0.5 * …min_electrical_power)`. S1 says of
  D12-s2-01 "no further site in the package uses this threshold shape". Its grep
  (`min_electrical_power.*\* 0\.5`) misses the reversed operand order. The formula is identical
  today, so this is a sibling that D12-s2-01's fix must route through the same owner, not a
  separate divergence. It is `coordinator.py`, which F1 owns.
- **The stamp chain three times in `inputs.py`.** It sits in `_age_minutes`, `_age_gate` (added by
  the #775 fix) and `age_of`, and the lint counts 8 hits. Only `age_of` diverges today. The other
  two are the next divergence waiting to happen, so D1-s5-01's fix should create one owner
  (`state_stamp` in the demo) rather than patch `age_of`.
- **`fromisoformat` at 24 call sites in 16 files.** S1's widening of D1-s3-01 lists 8 sites in 5
  files. I did not verify the other 16 as defects. The shape belongs to the P1 and
  future-instant barriers (F1.6, F1.9). I left it out of the P2 registry so that one shape is not
  guarded by two checks.
- **Literal service domains (entity_write_domain).** Beyond the instance there is one more:
  `coordinator._command_frequency` writes with a literal `"number"`. It is guarded, because its
  slot accepts `number` only (`config_flow.py:1537`, `_entity_of('number')`). It is dispositioned
  in the registry.
- **The ledger.** `tools/audit/bugclasses.json` records P2 in every one of rounds 1–7 (28
  instances), `detector: null`, `barrier: null`, `status: open`. Its `detector_idea` since the
  round-8 seeding has been "AST: callers of each named gate predicate against the structurally
  sibling functions that should share it", and it was never built. Round 8 added R8-P2
  (#1527/#1542, fixed by #1572 with a hot-water census in `tests/entities.py`). Round 9 has 27.

### Process state: (c), with one instance in (d)

The process is `tools/audit/briefs/fixer.md` step 8, added by `6bc932db` (2026-09-22, #1414):

> name a rule that enumerates the class's seams (a command, not a description), run it, and put
> every seam it returns in `## Figures` against its disposition — closed in this diff, already
> guarded, or a distinct finding named by id.

- **It existed and was followed.** #1479's body names a command, lists 3 sites and dispositions
  each one. #1576's body names its census, lists 8 slots and dispositions 16 (slot, domain) pairs.
- **It did not produce the intended result**, which is a closed class. It failed in two ways:
  1. **The rule runs once.** The enumeration runs at the fix's head and is then thrown away, or,
     in #1576's case, kept with a blind spot the check itself never tests. A sibling added later,
     by a feature branch as in the arbiter's case or by the next fix, meets no check.
  2. **The disposition is free text that nothing checks.** Both of #1479's "distinct" rows were
     the defect.

This is (c), not (b). The instruction was obeyed, so a firmer "enumerate your siblings" would
change nothing. D12-s2-02 on its own is (d): #1576's census was sound under its stated
precondition ("no written slot accepts `sensor`"), and that precondition changed underneath it
without the check noticing. D1-s5-01's origin (#775, 2026-09-11) predates step 8, so it was (a)
at the time. Step 8 is that gap's countermeasure, and (c) is why it has not been enough.

### Cost test

`cost(countermeasure, recurring) < cost(defect) x P(recurrence)`. Wall-clock, per round (one
audit round and its fix wave).

**Left side (standing cost).** A standalone run of `python3 tools/audit/round9/rca/p2/owners_lint.py`
took 2.14, 2.40 and 2.54 s over three runs at load1 about 12 on 4 cores. It imports nothing from
the package. Folded into `tests/entities.py`, whose recorded closure already holds every package
`.py` file (`tests/closures.json`; 66 on main), it runs on each gate run that already runs entities.py. At
41 PRs per round (the round-9 plan) and an assumed 3 runs per PR (not measured), that is
41 × 3 × 2.5 s ≈ **5 min per round**. The other standing cost is per event rather than per run:
one disposition line for each new legitimate read. At baseline the six entries return 56 hits: 13
inside owners, 22 covered by 14 disposition rows, and 21 stray (the instances).

**Right side.**

- **P(recurrence) is measured.** P2 appears in each of rounds 1–7 (ledger) plus round 8 (R8-P2)
  and round 9: 9 of 9 rounds. The instance counts are 28 over rounds 1–7, at least 2 in round 8
  and 27 in round 9, about 6.3 per round.
- **Defect cost, lower bound, measured only for the fix PR's open time.** #1479 was open from
  10:10Z to 11:36Z (86 min) and #1576 from 17:00Z to 18:03Z (63 min). Neither figure counts the
  finder, the three verifiers, the judge or the sweep, which all come before them.
- **Discounted for recall.** The registry does not see every P2 fact. Of the 27 round-9 findings,
  the entries built here cover 4 (D14-s2-01, D1-s5-01, D12-s2-01, D12-s2-02), which is 15%.
- **Result.** 6.3 × 63 min × 0.15 ≈ **60 min per round**.

60 > 5, so it passes by 12× on the most conservative reading: the lowest measured fix cost, the
recall I demonstrated rather than the one I estimate, and no audit cost counted. It stays inside
the bound. It adds 0 production lines, obeys the ratchet, and needs no budget raise, because
`tests/structure_budgets.json` measures production code only.

### Barrier (class-eliminating, as far as a check can be)

No static check can know every fact, so the barrier has two parts. Each maps to the (c) finding.

**1. Make the step-8 rule durable: a P2 owners registry that CI runs** (the prototype). Each entry
has four parts:

- **fact**: what is being decided;
- **shape**: an AST matcher. Three kinds cover the built entries:
  - a decision-context read of a proxy `CONF_` key, with the keys extracted from the canonical
    predicate's body (this is D14-s2-01's rule, generalised);
  - a node whose unparsed text matches a pattern, after a cheap structural pre-filter;
  - a literal-domain `async_call`;
- **owner**: the function or functions allowed to hold the shape;
- **dispositions**: each non-owner hit that is not a decision of the fact, with its reason.

Any other hit fails. Three refusals stop the lint going green by skipping it:

- `OWNER-MISSING`: an owner that is not defined;
- `DEAD-RULE`: a shape that matches nothing, or a proxy entry whose extracted key set is empty;
- `STALE-DISPOSITION`: a disposition whose site no longer hits.

This turns #1479's free-text "distinct" into a table row visible in the diff, and it catches the
arbiter-shaped sibling on the day it is added, whoever adds it.

`python3 tools/audit/round9/rca/p2/owners_lint.py --demo 1936d5ca` gave:

- **(A) Fails on the defect.** `demo_baseline_entries_failing=5 of 6`. The seams it names:
  - `two_zone_enabled`: `config_flow.py:1125 _derive_preset` and `modbus_prefill.py:212 _plant`;
  - `wood_furnace_on`: `topology.py:378–385 _wood_tank_shown` (6 reads);
  - `state_age`: `inputs.py` (all 8 stamp reads, because no owner exists yet);
  - `on_threshold_kw`: 4 sites (owner missing);
  - `entity_write_domain`: `pump_arbiter.py:457 _write`.

  `dhw_enabled` reads ok: its 11 non-owner reads are all dispositioned, taken from D14-s2-01's
  REPORT.md table.
- **(B) Passes once each fact's instances route through the owner.** Each fix is applied as an
  in-memory text edit whose old text is asserted present. Result:
  `demo_own_fix_entries_failing=0 of 5`.
- **(C) Healthy tree.** With all fixes applied, `demo_healthy_entries_failing=0`.
- **(D) Null probes on the healthy tree** (`demo_null_probes_firing=6 of 6`). Each fires on the
  entry intended:
  - a new proxy-key sibling → `two_zone_enabled`;
  - a new literal-domain write → `entity_write_domain`;
  - a new `.last_updated` reader → `state_age`;
  - owner renamed → `on_threshold_kw` OWNER-MISSING;
  - the dispositioned `"number"` write re-routed → `entity_write_domain` STALE-DISPOSITION;
  - the shape removed everywhere → `on_threshold_kw` DEAD-RULE.
- **Reverts of real fixes (history as the control).**
  - `two_zone_enabled` reads 3 seams at `3602b6ca^` and 2 at `3602b6ca`. The #1479 fix is seen,
    and so are the siblings it left.
  - `entity_write_domain` reads 1 stray seam and a missing owner at `2a451021^`, and ok at
    `2a451021` (#1576).
  - `state_age` goes from 5 to 8 hits across `a1bdb11c` (#775 added a copy).
- **Standing cost.** 2.1–2.5 s standalone, as above. The demo itself takes about 38 s because it
  runs 12 scans at a git ref; it is not a gate run.

**2. A policy change to fixer.md step 8.** Draft only; it goes to tvofi, who must approve it
(`fixer.md` is under `tools/audit/briefs/`, which is code-owned). It addresses state (c):

> For a P2 finding, the rule step 8 names is a registry entry in `tests/entities.py`'s P2 owners
> block (fact, shape, owner, dispositions), landed in the same PR, not a one-shot command. Where
> the fact has no syntactic shape (physics consistency, failure signalling, cycle fencing), the
> PR extends or adds a census that drives every sibling it enumerates with the same input and
> compares their outputs, and **the census asserts its own preconditions** (a census that skips
> a class of slots refuses the day a skipped slot gains a writer).

The last clause is the (d) countermeasure for D12-s2-02. As a finding it belongs to the P6 census,
which lands in F1.10 too (below).

**What the registry cannot see**, by my classification of the findings' mechanisms. This is a
judgement, not a measurement:

- **Token-shaped but not built here (9).** A later entry could cover each: D1-s3-01 (P1 and
  future-instant own the shape), D1-s5-52, D2-s2-01 (84 raw `heat_loss_coefficient`-family reads,
  too noisy as a token), D2-s3-01, D7-s1-71, D7-s2-02, D8-s2-02, D8-s2-03, D10-s1-01.
- **Not token-shaped (14).** These need the census half of part 2:
  - cycle fencing and failure signalling: D1-s2-51, D1-s2-91, D1-s4-02, D10-s1-02;
  - lifecycle: D1-s3-02;
  - parse: D1-s5-03;
  - physics: D2-s1-02, D2-s2-03, D2-s4-02;
  - UI: D4-s2-06;
  - entity publishing: D8-s1-02, D8-s1-03, D8-s3-61 (R8-P2's entities.py census covers the
    shape of D8-s3-61);
  - wizard: D12-s3-01.

  That is why part 2 is not optional. The lint alone would leave the class open for more than
  half of this round's mechanisms.

## Plan fold

- **Landing PR: F1.10, as planned.** It is tvofi-gated already, and it lands after every P2
  instance PR, so the check reads zero on main only then. The lint goes in as a class-named block
  ("P2 owners") in `tests/entities.py`. That creates no new tracked file, needs no `closure.py`
  or `closures.json` change, and needs no `run.sh` edit. The prototype file stays INERT under
  `tools/audit/`.
- **Files.**
  - `tests/entities.py`: not code-owned. It is a hub shared by class-named sorted blocks
    (FIX-PLAN section 2), so F1.10 adds it under Edits or Borrows.
  - `tools/audit/bugclasses.json`: P2 `detector` and `barrier` set to the entities.py block's
    command, `status: barriered`. Not code-owned.
  - `tools/audit/briefs/fixer.md` step 8: **policy, code-owned**. The draft above goes to tvofi.
    F1.10 already needs tvofi, so it can ride there or go to F11.3 (the policy PR). tvofi decides.
- **Lines.**
  - **Production: 0 for the barrier.** The owners it names are created by the instance PRs:
    - `on_threshold_kw` in the D12-s2-01 fix (F2.4);
    - the stamp owner in the D1-s5-01 fix (F4.1);
    - domain-from-entity in the D12-s2-02 fix (F3.2);
    - predicate routing in F1.2.
  - **Test: about 230** in `tests/entities.py`, measured as the prototype without its demo
    (294 lines including docstrings). Each future P2 fix adds about 5–10 lines per registry
    entry.
- **Changes to the PR set or `after` edges.** No new PR, and F1.10's existing `after` edges
  already follow every P2 instance PR. Two carries, by finding-propagation.md, go into the
  briefs (this is the record, not the propagation):
  1. **F2.4 and F1.10.** D12-s2-01 has a fourth site, `coordinator.py:9736`, that F2.4 cannot
     edit, because F1 owns it. F1.10 routes it through `on_threshold_kw`, or an earlier F1 PR
     does, before the entry is registered. Otherwise the P2 block fails at F1.10.
  2. **F3.2 and F1.10.** D12-s2-02 escaped the #1576 P6 census through its stated `sensor`
     blind spot (state d). The P6 barrier that F1.10 also lands should make the census refuse a
     skipped (sensor-accepting) slot that any consumer writes, rather than skip it.
  3. **Coordination, not a carry.** The `fromisoformat` shape (24 sites at baseline) is left to
     the P1 and future-instant barriers (F1.6, F1.9). If neither refuses `fromisoformat` outside
     their helper, F1.10 adds it as a P2 entry, with the owner being the helper F3.1 introduces.
