R10-STRUCTURE-ALIAS: `seam_cut_total` priced cross-seam attribute-reference **occurrences**, so a local alias of a repeated read paid for itself (O19, `prices = self._prices` in `_raise_cop_issue`, -2). A getter returning state reads paid as well (`_cop_state()`, -2; one edge in place of k reads pays 2(k-1)). Neither moves anything. The roster lists no issue under `fixes`.

Repair round 3. The round-2 fix review (`review/2711`, verdict on `b43ea541`) blocked the PR `class-open`. The return-value rule priced state escaping only through a callee's **return value**, and only from a call spelt `<root>.m(...)`, a property read or a helper handed the root. A getter that handed its reads out through an argument (`out[k] =`, `out.x =`, `out.append/extend`, a callback), or one reached as `type(self).m(self)`, `g = self.m; g()` or `getattr(self, "m")()`, still lowered the cut with nothing moved. Against the clean tree at `b43ea541` that was -4 and -6.

This round closes the class by enumerating both of its axes, and plants every arm:
- **Channels.** These are the ways a callee hands state to its caller.
- **Reaches.** These are the ways a caller reaches a callee, or the state, without the spelling the cut reads.

## What `seam_metrics` in `tests/structure.py` prices at this head

- **Distinct pairs** (unchanged). Each (seam, attribute) pair and each (seam, callee) pair crossing a seam is counted once, however often it is read.
- **`StateFlow`: what a value may hold** (round 2, unchanged in principle). State reads are followed through locals, displays, operators, subscripts, lambdas and unit calls. Only the forms that cannot hold an object are listed (`_FRESH`: a comparison, a `not`, a formatted string, a constant). Any spelling nobody enumerated carries by default.
- **Channels: a call is priced by everything its callee hands on**, not only its return value. Each channel is charged at the caller:
  - the return value or a `yield`;
  - an **exception** the callee raises, or lets pass from a callee it calls (`StateFlow.raised`, propagated through every unit that calls it);
  - what it **leaves in an argument** (`StateFlow.left`). That covers:
    - a store into a parameter (`out[k] = v`, `out.a = v`, `setattr(out, "a", v)`);
    - a method called on one (`out.append(v)`);
    - a parameter called (a callback);
    - a local sharing an object with a parameter (`o = out`, `out.setdefault(k, [])`);
    - a parameter forwarded to another unit that leaves state in it;
  - a name declared `global`/`nonlocal`.

  The coordinator itself, left in an argument, is the coordinator at the caller. The edge is dropped only for a transparent callee: one that reads only what it hands on, stores nothing and calls only transparent callees.
- **Reaches: every constant spelling is the access** (`_OneSpelling`, run on a copy of each unit):
  - `type(x).a` and `x.__class__.a` are `x.a`.
  - `type(x).m(a, ...)`, `x.__class__.m(a, ...)` and `<Class>.m(a, ...)` are the unbound call, so `a` binds `m`'s first parameter.
  - `getattr`/`hasattr`/`setattr`/`delattr` with a literal name are a read, a test, a store and a delete. So is a local only ever bound to literal names (`for name in ("_a", "_b"): getattr(self, name)`). `vars(x)["a"]`, `x.__dict__["a"]` and `x.__dict__.get("a")` are `x.a`.
  - **A read by a name only known at run time** (`getattr(self, n + "x")`) is priced as a read of every attribute any unit stores. It can only cost more than the reads it stands for.
  - **A bound method handed on uncalled** (`g = self.m`, `partial(self.m)`, a callback handed to Home Assistant, `self.m.__call__`) is a call at the reference: the edge plus what `m` hands on. A later `g(...)` maps its arguments onto `m`'s parameters.
  - **The coordinator in a parameter not spelt `self`.** A method's coordinator is its first parameter, whatever its name. A parameter any call site hands the coordinator is the coordinator in the callee (`def m(self, me)` called `self.m(self)`; a static method called `self.s(self)`; through an alias; through `partial`).
  - **A dunder Python calls unnamed** (`self[k]`, `for x in self`, `self()`, a missing attribute through `__getattr__`) is called by every whole-value use of the coordinator.
  - **A class-body descriptor** is read as what it names: `x = _view("_a")`, `x = property(lambda s: s._a)` and `x = property(_get)`.
- **An opaque call's co-argument, or a module it is called on, is not the coordinator.** Round 2 bound every argument of an opaque call to every other. So `f(now, self)` made `now` the coordinator, and `dt_util.as_utc(self)` made `dt_util` the coordinator. Their attributes were then counted as coordinator reads. A local receiver still holds what it is handed, the coordinator included (`box.append(self)`). An opaque call's result never becomes the coordinator, nor a unit reference (a reference is priced where it is named).

Design choices the checks encode (`fixer.md` step 11):
- **Conservative over-pricing is the accepted direction.** Two arms read dearer than the direct reads:
  - a dunder (`dunder_*` plants: +13 at the head), because every whole-value use of the coordinator may call it;
  - a computed name (`computed_getattr`, `read_computed_getattr`).

  Neither arm can be spelt cheaper. The ratchet is gamed downward, so the self-check families assert `>=` the direct reads, and an exact equality where one is owed: literal names read exactly their attributes.
- **A reference charges at the reference**, whoever later calls it. That is the dominant real-tree change (+67): callbacks registered across seams are edges an extraction has to name.
- **Not closed: state copied into a slot that outlives the call.** For example, `self._cop_pair = (a, b)` in learning, read from views. The metric's unit of state is the named attribute, and a copy into a new attribute is a new attribute the writing seam owns. Pricing every source through every slot that ever held it would charge each reader of a composed slot for everything it was built from, and that changes what the metric measures. The harness plants it (`snapshot_attr`). At this head it reads 423, above the clean 420, so the plant does not lower the cut either.

## Head

`86d4dba1c4091beebe087b208b8c873a315ed199` (code head, branch `handoff/r10-structure-alias`). It is the PR head `b43ea541` with origin/main `e463e95e2` merged in (`f6e83cd28`), then two commits:
- `a5c58c0c0`, the rule, the self-check families and the harness plants;
- `86d4dba1c`, the re-record.

Every figure was taken at this head against the merge base `e463e95e255dac31ed229e520e197b5710a07d94`. The exceptions name `b43ea541` or the merge base. Main moved to `4a00a3f05` during the measurement (`git diff e463e95e2 4a00a3f05 --stat`: four files, delivery rows, a triage note and `tools/audit/seat/roster_sync.py`). Nothing the cut reads moved. Measured 2026-10-24, about 19:00Z-21:30Z.

## Mutation proof

Instrument: `$SCRATCH/mutrun.sh` with `$SCRATCH/muts.py` (not committed). Each mutant replaces exactly one predicate in `tests/structure.py` at the head, runs `PYTHONPATH=tests/hastub python3 tests/structure.py`, records the FAIL lines, and restores the file with `git checkout`. Results:

- M0, no mutant (the runner's null control): rc=0, `STRUCTURE RATCHET PASSED`.
- M1, the left channel reads nothing (`StateFlow.left` returns empty): rc=1. Red: `FAIL  a callee handing both reads on through an argument the callee stores into, mutates or calls costs at least the two reads (O19)`; `FAIL  a callee handing both reads on through the coordinator itself, left in an argument or a local costs at least the two reads (O19)`.
- M2, a parameter called is not handed its arguments (`callback = False`): rc=1. Red: `FAIL  a callee handing both reads on through an argument the callee stores into, mutates or calls costs at least the two reads (O19)`.
- M3, what a call leaves in an argument is not carried on through it (no `_handed`): rc=1. Red: `FAIL  a callee handing both reads on through an argument the callee stores into, mutates or calls costs at least the two reads (O19)`.
- M4, what a callee leaves is not charged at the caller: rc=1. Red: `FAIL  a callee handing both reads on through an argument the callee stores into, mutates or calls costs at least the two reads (O19)`.
- M5, a raise hands nothing on (`StateFlow.raised` returns empty): rc=1. Red: `FAIL  a callee handing both reads on through an exception the callee raises, or lets pass costs at least the two reads (O19)`.
- M6, an exception does not propagate through the units that call its raiser: rc=1. Red: `FAIL  a callee handing both reads on through an exception the callee raises, or lets pass costs at least the two reads (O19)`.
- M7: retired with its arm (the `try`/`except` handler binding, below).
- M8, `_OneSpelling` not run: rc=1. Red: `FAIL  a callee handing both reads on through an argument the callee stores into, mutates or calls costs at least the two reads (O19)`; `FAIL  a callee handing both reads on through the callee reached through its class, a literal or computed name, or a dict costs at least the two reads (O19)`; `FAIL  a name only ever bound to literals reads exactly those attributes, no more`.
- M9, `type(x).m(a, ...)` not rewritten to the unbound call: rc=1. Red: `FAIL  a callee handing both reads on through the callee reached through its class, a literal or computed name, or a dict costs at least the two reads (O19)`.
- M10, a literal `getattr` not rewritten: rc=1. Red: `FAIL  a callee handing both reads on through the callee reached through its class, a literal or computed name, or a dict costs at least the two reads (O19)`; `FAIL  a name only ever bound to literals reads exactly those attributes, no more`.
- M11, `vars(x)["a"]` / `x.__dict__["a"]` not rewritten: rc=1. Red: `FAIL  a callee handing both reads on through the callee reached through its class, a literal or computed name, or a dict costs at least the two reads (O19)`.
- M12, a bound method handed on uncalled is not a call: rc=1. Red: `FAIL  a callee handing both reads on through the callee handed on uncalled: an alias, a partial, a callback costs at least the two reads (O19)`; `FAIL  a callee handing both reads on through the coordinator in a parameter not spelt self costs at least the two reads (O19)`; `FAIL  a callee handing nothing on through a parameter or a reference is still the edge`.
- M13, a method's coordinator is always `self`, never its first parameter: rc=1. Red: `FAIL  a callee handing both reads on through the callee reached through its class, a literal or computed name, or a dict costs at least the two reads (O19)`; `FAIL  a callee handing both reads on through the coordinator in a parameter not spelt self costs at least the two reads (O19)`.
- M14, no parameter becomes the coordinator by a call site handing it: rc=1. Red: `FAIL  a callee handing both reads on through the callee reached through its class, a literal or computed name, or a dict costs at least the two reads (O19)`; `FAIL  a callee handing both reads on through the coordinator in a parameter not spelt self costs at least the two reads (O19)`.
- M15, no implicit dunder: rc=1. Red: `FAIL  a callee handing both reads on through a dunder Python calls unnamed costs at least the two reads (O19)`.
- M16, no class-body descriptor: rc=1. Red: `FAIL  a callee handing both reads on through a class-body descriptor costs at least the two reads (O19)`.
- M17, a local receiver holds what it is handed only as an opaque result: rc=1. Red: `FAIL  a callee handing both reads on through the coordinator itself, left in an argument or a local costs at least the two reads (O19)`.
- M18, co-arguments and module receivers hold the coordinator again (round 2's spread): rc=1. Red: `FAIL  the state root is the binding, not the name it is bound to`.
- M19, a `global` assignment is not a channel: rc=1. Red: `FAIL  a callee handing both reads on through an argument the callee stores into, mutates or calls costs at least the two reads (O19)`.
- M20, `partial(...)` not mapped onto the bound unit: rc=1. Red: `FAIL  a callee handing both reads on through the coordinator in a parameter not spelt self costs at least the two reads (O19)`.
- M21, a local sharing an object with a parameter is not linked to it: rc=1. Red: `FAIL  a callee handing both reads on through an argument the callee stores into, mutates or calls costs at least the two reads (O19)`.
- M22, a local bound only to literal names is not resolved: rc=1. Red: `FAIL  a name only ever bound to literals reads exactly those attributes, no more`.
- M23, a computed-name read charges nothing: rc=1. Red: `FAIL  a callee handing both reads on through the callee reached through its class, a literal or computed name, or a dict costs at least the two reads (O19)`; `FAIL  a name only ever bound to literals reads exactly those attributes, no more`.

Two arms were removed rather than pinned, because their mutants survived and showed they were dead:
- a `try`/`except` handler bound to what its body raised. Propagation already charges a caught exception, so this arm was redundant.
- the old `Cls.m(x, ...)` to `x.m(...)` rewrite. It was replaced by the unbound form that M9 pins, after its mutant survived and a planted `type(self).m(other, self)` showed that the rewrite itself hid the reads.

The receiver arm (M17) survived its first run. The pin that kills it, a `box.append(self)` local, was added to the "coordinator itself" family. The list above is the re-run at the head.

**Failing test first.** `$SCRATCH/ftf.py` runs the head's round-3 families against another tree's `seam_metrics` and counts the cases that read cheaper than the two direct reads:
- At the head: `RESULT head_families_red=0 of 8`, 0 of 37 cases cheaper.
- At `b43ea541`: `RESULT other_families_red=8 of 8`, 35 of 37 cases cheaper.
- At the merge base `e463e95e2`: 8 of 8 families, 37 of 37 cases cheaper.

## Null control

- **The unperturbed tree, twice.** `dev/audit/harnesses/r10_structure_alias.py` reads `clean_seam_cut_total=420` before its plants and `clean_again_seam_cut_total=420` after them. `python3 tests/structure.py` reads `seam_cut_total 420 <= 420` (`STRUCTURE RATCHET PASSED`).
- **One planted callback edge moves the cut by its expected amount.** `edge_called` and `edge_referenced` plant a new learning unit that stores and hands nothing on, `_cop_touch`. `_scores_view` (views) then calls it, or hands it uncalled to `self.hass.async_create_task`. Both read 422 at the head: one new views -> learning pair, counted once in each seam's cut, so +2, whether called or referenced. At the merge base they read 712 and 711. The reference there costs only its `hass` read, which is the defect the referenced plant pins.
- **A callee that hands nothing on is still the one edge.** This is the self-check `a callee handing nothing on through a parameter or a reference is still the edge`: a fresh-bool callee read through a parameter, through an alias and directly, all equal and all unequal to the direct reads.

## Figures

- **The finder's harness at both ends.** `PYTHONPATH=tests/hastub python3 dev/audit/harnesses/r10_structure_alias.py`, sha1 `cc3a57fc0ac7503db04f4ed18a8eb99b4df66b62`. At the merge base it was copied into a detached worktree at `e463e95e2`. Rule: a plant reads `<name>_seam_cut_total`, and a plant is closed when it reads at least the clean figure.
  - Head: clean 420. The alias plant, the eight round-1/2 getter spellings and every `ROUND3` plant read 420, except four that read more: the three `dunder_*` plants at 433, `computed_getattr` 544 and `read_computed_getattr` 523. That is 50 plants, none below 420. `snapshot_attr` (dispositioned) reads 423. Census: `units_returning_state=126`, `transparent_callees=77`, `units_returning_coordinator=1`, `cross_seam_calls_of_state_returners=68`, `units_leaving_state=18`, `units_raising_state=1`, `unresolved_unit_names=51`, `computed_names=1`.
  - Merge base: clean 710. Every plant reads between 706 and 709, so each pays at the base. The only exceptions are the null-control edges, 712 and 711. The census is absent (`# census: this tree's structure.py prices no callee by its return value`).
- **The reviewer's instrument** (`review/2711:evidence/variants.py`, 16 spellings: out-param dict/append/attr/extend, callback, `type(self)`, `getattr`, bound alias, the body shapes). At the head, clean 420 and every one of the 16 variants 420 (`RESULT <name>=420` for each of `ref_plain`, `call_type_self`, `call_getattr`, `call_bound_alias`, `body_const_getattr`, `body_nested_def`, `body_lambda_call`, `body_dict_unpack`, `body_iadd`, `body_try`, `body_if_else`, `outparam_dict`, `outparam_append`, `outparam_attr`, `outparam_extend`, `callback`). At the merge base, clean 710 and every variant 706 to 708.
- **`seam_cut_total` re-recorded 367 -> 420** by `python3 tests/structure.py --record --allow-regression=...` against the pre-round table, with `recorded_at` the merge base `e463e95e2`. The reason and the decomposition are in commit `86d4dba1c`'s message (CLAUDE.md rule 2). Main's table reads 710, so the budget file moves down against main. `git diff origin/main...HEAD -- tests/structure_budgets.json` shows only `seam_cut_total` and `recorded_at`.

  The decomposition against this branch's interim 367 was measured in this order, each step by ablating one rule of `seam_metrics` on the same tree (`$SCRATCH/abl/run.py`):

  | step | change |
  |---|---|
  | the new channels and spellings, with round 2's opaque-call spreading kept | +22 (367 -> 389) |
  | an opaque call's co-argument or module receiver is no longer the coordinator | -37 (-> 352) |
  | an uncalled bound-method reference is charged | +67 (-> 419) |
  | a local only ever bound to literal names is resolved | +1 (-> 420; the three `_unsub_*` reads in `_release_registrations`) |
- **Seam table** (`python3 tests/structure.py`, "coordinator seam table" block), cut per seam, round-2 head -> this head:

  | seam | b43ea541 | head |
  |---|---|---|
  | dhw | 30 | 31 |
  | learning | 119 | 125 |
  | fetch | 65 | 67 |
  | grid | 88 | 103 |
  | views | 65 | 94 |
- **Class seams (`fixer.md` step 8).** The rule is the harness census at the head, which lists what a syntactic reading finds and what `seam_metrics` prices.
  - `# unresolved` lists every occurrence of a unit's name that the scan did not read as a call or a reference: 51 occurrences. Each is one of these:
    - an attribute of an object that is not the coordinator: `mode` 17 (`self._pump_signals.mode`, `signals.mode`), `prices` 19 (`horizon.prices`, `result.prices`, `simulated.prices`), `dhw_temperature` 9 (`state.dhw_temperature`, `ctx._current_state.dhw_temperature`), `target_temperature` 2 (`ctx._config.target_temperature`, `EntryConfig.from_mapping(...).target_temperature`);
    - `super().__init__` and `super().async_shutdown()`;
    - `topology.describe_setup`;
    - a string literal that is not a member name: the `"mode"`/`"prices"`/`"dhw_temperature"` dict keys, and the `"_price_model"` piece of an f-string.

    None reaches a coordinator unit, so each is dispositioned "not a reach".
  - `# computed-name`: 1 occurrence, `async_update_thermal_params`'s `setattr(self, attribute, ...)`. It is a store, listed and not owned. It is also in both trees, and a store cannot lower a read. A computed read is priced as every stored attribute (`read_computed_getattr`).
  - `# leaves-state`: 18 units. `# raises-state`: 1 unit (`async_set_target_temperature`, `_config`). Each is priced by the one channel rule at every caller. No unit has a second path.
  - The 68 cross-seam calls into state returners: closed by the same rule as in round 2.
- **Gate.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 8 script(s) run, 25 scoped out`. Run at the head with `PYTHONPATH=tests/hastub`:
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED` (`seam_cut_total 420 <= 420`).
  - `tests/arch_score.py`: `ALL 255 ARCHITECTURE SCORE CHECKS PASSED`.
  - `tests/arch_score_head.py`: `ALL 18 ARCHITECTURE SCORE HEAD CHECKS PASSED`.
  - `tests/doc_claims.py`: `ALL 203 checks PASSED`.
  - `tests/harness_headers.py`: `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `tests/features.py`: `ALL 4356 FEATURE CHECKS PASSED`.
  - `tests/entities.py`: `4 of 2425 ENTITY CHECKS FAILED`. All four are in the heartbeat lane's py-spy positive control. They are `hb:positive_control` and its retry self-tests (`hb:positive_control survives one hung py-spy sample ...`, `the control rests between tries ...` with `two tries took 0.80s against a 1.0s rest`, and `the control survives two hung samples ...`). Each was read on this seat at a load average of 12 to 16. Rounds 1 and 2 recorded `hb:positive_control` reds of the same lane on this branch. This diff touches no file that lane runs (`tests/nightly_ha.py`, `tests/entities.py`, the coordinator). It was not re-run at the merge base, and CI runs `entities.py` on its own runner.
  - The `run_always` set: `tests/layout.py` rc=0; `tests/closure.py selftest` `ALL 117 closure shrink pins PASSED`; `tests/env_drift.py --claims-only e463e95e255dac31ed229e520e197b5710a07d94` `claims hygiene: e463e95e255dac31ed229e520e197b5710a07d94 ok`.
  - `tests/stress.py` is left to CI's required mutation check (`fixer.md` step 5).
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` reads `CI PREDICT: no closures or fast red predicted against e463e95e255d`.
- `python3 -I tools/audit/seat/tmp_paths.py --check` reads `0 refused`.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD` reads `Architecture score: dS +0.0000 NULL`. No production line changed, and `tools/audit/archscore/vector.py` stubs `seam_metrics`.

## Red checks

- `gate` at `b43ea541`: red on its first run, an early-gate race. It ran before the other workflows of that head had concluded. The fix review read no concluded red at 16:30Z, and `budget-raise-gate` concluded success at 16:05Z and 16:47Z. Both `gate` check-runs at that head now conclude success (check-runs 120929474649 at 16:50Z and 120930173982 at 16:54Z, read from the check-runs API).

  Root-cause answer: the cheaper detector already exists and is wired. `.github/workflows/gate-sweep.yml` (`tools/ci/sweep.py`) re-runs the red `gate` of an older run at a head once a later run's gate is green, and that is what turned it green. A local check cannot see CI run ordering, so no cheaper pre-push detector exists. Its standing cost is one sweep job per completed CI run. Nothing in this diff touches the gate.

## Forward-carry

n/a: the roster's only group carrying `seam_cut_total` or O19 is this one. Every later stage derives the metric at its own merge base. A branch in flight that re-records `seam_cut_total` will conflict on `tests/structure_budgets.json` and re-record at its merge with main. That is a merge mechanic, not a finding.

## Friction

none
