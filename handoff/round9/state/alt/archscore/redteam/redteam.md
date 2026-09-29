# Red team: arch_score v1

Target: `b/arch_score.py` v1 (gate = no SCORE_METRIC rises; dS = sum w_i log2((base+1)/(cur+1))),
`b/weights.json` frozen, vector from `b/measure_vec.py` + `b/metrics_v1.py`.
Baseline tree 7952d8f9. Every attempt is a deterministic script in `attempts/NN_*.py`, applied by
`run_attempt.sh` to a fresh `git reset --hard 7952d8f9` of a scratch worktree. The runner compiles
and imports every package module (`import_check.py`, hastub on `sys.path`), measures, and scores
against `out/base.json`. The per-attempt outputs are `out/NN_*.{diff,diffstat,json,delta.json,counters.json}`.

**Null control.** `00_null_rename` renames a private helper (`_setback_fields`, 3 lines) and scores
admissible, dS 0, NULL. The rig does not invent movement.

**Scale.** The largest dS any GOOD corpus merge earns under v1 is +0.795 (ca937daa). Most earn
under +0.01. Every successful game below scores at least +0.47, and most score 10 to 200 times
a real improvement.

## 1. Results

"Judgement" is my independent architectural verdict on the edit, made without reference to the
score. A game SUCCEEDS when the change is admissible, dS > 0 and the judgement is "not better" or
"worse".

| # | attempt | lines (diffstat) | metric moved | admissible | dS | v1 verdict | judgement | game |
|---|---|---|---|---|---|---|---|---|
| 00 | null: rename a private helper | +3/-3 | none | yes | 0 | NULL | same | (control) |
| 01 | all-`Any`, `total=False` TypedDict on `_async_update_data`'s return | +174/-1 | untyped_payload_keys 164→0 | yes | **+50.86** | IMPROVES | not better | **SUCCEEDED** |
| 02 | hub writes re-spelled `object.__setattr__(hub, "f", v)` | +49/-56 | hub_solve_writes 40→0, footprint -15 | yes | **+29.17** | IMPROVES | worse | **SUCCEEDED** |
| 03 | shared in-place writes via `type(X).__setitem__(X,..)`, `_invoke(X,"clear")`, `object.__setattr__` | +29/-26 | shared_inplace_writes 22→0 | yes | **+24.66** | IMPROVES | worse | **SUCCEEDED** |
| 04 | `id(N)` no-op between the two statements of every clone window | +76 | dup_pairs_v1 121→7 | yes | **+35.09** | IMPROVES | worse | **SUCCEEDED** |
| 05 | move every method but `__init__` into a `_CoordinatorBody` mixin | +390/-160 | many; dead_by_reachability 6→301 | **no** | (+94.9) | WORSENS | not better | FAILED (gate) |
| 05b | same, private methods only | (reorder) | dead_by_reachability 6→297 | **no** | (+55.8) | WORSENS | not better | FAILED (gate) |
| 05c | whole body into `_CoordinatorBody(DataUpdateCoordinator)`, empty named subclass | +329/-94 (moves) | 5 metrics, see 05d | yes | **+101.07** | IMPROVES | not better | **SUCCEEDED** |
| 05d | **minimal 05c: rename the class, append an empty subclass** | **+5/-1** | untyped 164→0, hub 40→0, shared 22→4, footprint 2512→307, writers_multi 130→1 | yes | **+101.07** | IMPROVES | not better | **SUCCEEDED** |
| 06 | public passthrough `raw_<x>` property for every foreign-read private | +171/-75 | private_reach 92→13 | yes | **+2.73** | IMPROVES | not better | **SUCCEEDED** |
| 07 | re-declare the split families' stragglers as singleton families in `ENTITY_FAMILY_OVERRIDES` | +3 | family_splits 3→0 | yes | **+10.93** | IMPROVES | worse | **SUCCEEDED** |
| 08 | module-level keep-alive in diagnostics.py (import + `lambda o: (o.measured, ...)`) | +7 | dead_by_reachability 6→0, public_unused 6→0 | yes | **+5.61** | IMPROVES | worse | **SUCCEEDED** |
| 09 | delete working functionality: gut the away setback / economy relax envelope | +2/-19 | hub_solve_writes 40→31 | yes | **+1.95** | IMPROVES | worse (feature gone) | **SUCCEEDED** (known limit) |
| 10 | `self.X = v` → `setattr(self, "X", v)` in `__init__`/`_init_*` (constructions kept) | +106/-106 | writers_multi 130→59, footprint -85 | yes | **+1.18** | IMPROVES | worse | **SUCCEEDED** |
| 11 | keyword-only params of >10-param functions → `**kw: Any` + `kw.get` prologue | +104/-104 | a1_params_over_10 28→20 | yes | **+0.47** | IMPROVES | worse | **SUCCEEDED** |
| 12 | 02+03+10+06+01+07+08+11+04 in one change | +719/-368 | 11 of 12 metrics | yes | **+160.67** | IMPROVES | worse | **SUCCEEDED** |
| 13 | hub handle via accessor `self._live("_opt_config")` at write sites and call arguments | +87/-82 | hub 40→9, footprint 2512→2524 | **no** | (+11.07) | WORSENS | worse | FAILED (gate, incidentally) |

That makes 13 successful games (12 distinct plus the combination), with 3 stopped by the gate.
Where the gate held, it held by accident. Two of the three stops came from a different metric
misfiring: dead_by_reachability does not follow `self.m` into a package base class, and footprint
does not count a call-argument accessor as plumbing. That price can be paid, and 05d pays it by
not moving any code at all.

Games 03 and 04 also each tripped the gate on footprint in their first version (+2 and +5).
Each was fixed by choosing a spelling that the v1 plumbing rule does not charge: a module helper
instead of `type(X).m(X)`, and `id(N)` instead of a bare constant.

## 2. Details

**01 untyped_payload_keys, all-Any TypedDict (+50.86, 174 lines).**
The edit adds `class CoordinatorPayload(TypedDict, total=False)` declaring all 164 produced keys as
`Any`, and sets it as `_async_update_data`'s return annotation. The metric counts a key as typed
when a package TypedDict on the producer declares it, and ignores the value type.

The judgement is "not better":
- The coordinator stays `DataUpdateCoordinator` (unparameterised), so `coordinator.data` is still
  `Any` to every consumer.
- `total=False` means a producer that stops writing a key still type-checks.
- The P6 mechanism is a consumer reading a key no producer writes, and this edit leaves it
  exactly as undetected as before.

A side finding is a metric bug: `typed_dicts()` registers the functional form
`X = TypedDict("X", {...})`, but `contract()` resolves an annotation only to a class. The first
version of this attempt (functional form) therefore scored 0, and a genuine functional-form
contract would be missed too.

**02 hub_solve_writes, `object.__setattr__` (+29.17).**
All 38 site lines are re-spelled, for example `ctx._opt_config.peak_count = n` becomes
`object.__setattr__(ctx._opt_config, "peak_count", n)`. The mutation, the object and the timing
are identical. The write now also bypasses any `__setattr__` guard and disappears from grep and
from type checking. `write_sites()` only sees `setattr`/`delattr` with a Name func, and an
Attribute call only when its attr is in MUTATORS.

Bonus: footprint fell by 15, because v1's plumbing rule counts
`object.__setattr__(x, "f", simple)` as a delegation, so a write is read as non-logic.

**03 shared_inplace_writes, dunder/unbound/helper spellings (+24.66).**
The edit uses three spellings:
- `X[k] = v` becomes `type(X).__setitem__(X, k, v)`.
- `X.clear()` / `.add()` / `.append()` becomes `_invoke(X, "clear")`, a 2-line module helper
  running `getattr(obj, name)(*args)`.
- Attribute stores become `object.__setattr__`.

Same objects, same await exposure. `X.__setitem__(k, v)` is caught, because `__setitem__` is in
MUTATORS. `type(X).__setitem__` is not, because the receiver `type(X)` evaluates to no role.

**04 dup_pairs_v1, no-op interleave (+35.09, 76 added lines, no logic touched).**
In every clone except the first of each window group, the script inserts `id(<N>)` (a distinct
int per function) between the window's two statements. 121 pairs fall to 7.
- A bare-constant version scored the same on dup_pairs_v1 but tripped the gate: footprint rose
  by 5 because a constant expression counts as a logic statement.
- `id(N)` is a "delegation", so it is free.

**05 / 05b / 05c / 05d, the coordinator is a class node, not a runtime class (+101.07 for a 5-line diff).**
Every coordinator-keyed metric locates the coordinator by the literal class
`HeatPumpOptimizerCoordinator`:
- roots are the literal quals `coordinator:HeatPumpOptimizerCoordinator.async_run_optimization`,
  `.async_simulate` and `._async_update_data`;
- `seed_env` gives `self` the COORD role only when `fn.cls == coord_key`;
- footprint counts `logic_stmts(class node)`.

05d renames the class to `_CoordinatorBody(DataUpdateCoordinator)` and appends
`class HeatPumpOptimizerCoordinator(_CoordinatorBody): """..."""`. The result:
- The producer and both solve roots vanish, so untyped 164→0 and hub 40→0.
- `self` loses its role, so shared 22→4 and writers_multi 130→1.
- Footprint falls to the f(coord) free functions only, 2512→307.
- private_reach does not move, because it measures foreign modules.

The mixin variants (05, 05b) were stopped only because dead_by_reachability does not resolve
`self.m` into a package base class, so 297 to 301 live methods read as dead. That is a false
positive in the metric, not a guard.

Judgement: an identical runtime class with one extra, empty MRO level. Not better.

**06 private_reach, passthrough properties (+2.73).**
The edit adds 24 `@property raw_<x>: return self._<x>` accessors to the coordinator and re-spells
79 foreign reads as `coord.raw_<x>`. Same objects handed out (mutable dicts included), same
coupling, and the coordinator surface grows by 24. The trivial accessor is plumbing, so footprint
does not move. Writes were left alone, because a setter body is a counted logic statement.

Reads through the `_ctx` hop were excluded: the first version broke `boost.apply` at runtime on
`CoordinatorContext`, which features.py caught.

**07 family_splits, declaring the split away (+10.93, 3 lines).**
`away_return` and `compressor_frequency_advisor` are homed in singleton families, via overrides
naming each key itself. No name, translation or sort order changes, so the user's entity list is
split exactly as before. The declaration now simply says those entities are not family. The
repository's own check (tests/entities.py) reads the same declaration, so it would pass too.

**08 dead_by_reachability + public_unused, keep-alive registry (+5.61, 7 lines).**
diagnostics.py gains `from .const import ENTITY_FAMILY_OVERRIDES` and
`_KEEP_ALIVE = (ENTITY_FAMILY_OVERRIDES, lambda o: (o.healthy, o.last_success, o.measured, o.reset, o.start, o.weather))`.
Module-level code is a root, and an untyped `o.m` reaches every member named `m`. Nothing calls
the lambda. The dead code stays dead and the unused name stays unused.

**09 delete working functionality (+1.95).**
`apply_setback` now returns the originals without lowering anything, and `lower_floor` and
`restore_setback` return None. Every away entity, option and service remains and still reports
"away"; the house is simply never set back, and the economy / open-window floor relax is gone.
features.py fails 5 behavioural checks (economy widening, open-window relax, away set-back,
default fallback), so the behaviour gate catches it and the structure score rewards it.

**10 a1_coord_writers_multi, setattr in the construction phase (+1.18).**
104 plain `self.X = v` in `__init__`/`_init_*` become `setattr(self, "X", v)`. Constructions
(`self.X = K(..)`) were kept, because re-spelling those broke `_derive_aliases` and raised
shared_inplace_writes 22→23 (the first version was not admissible).

Judgement: the attribute declarations vanish from mypy's view and from every reader.
- writers_multi 130→59.
- Footprint -85, because `setattr(self, "X", simple)` is plumbing under v1.
- entities.py's S8 structural pin notices one attribute ("COP-health watch state is initialised
  in the learning seam").

**11 a1_params_over_10, `**kw` bags (+0.47).**
Eight functions whose surplus parameters are keyword-only get `**kw: Any` plus a prologue
`name = kw.get("name"[, default])`. Callers are unchanged. The signature, its types and the
unexpected-keyword check are lost. The prologue lines are plumbing, so footprint does not move.

**13 hub handle accessor (FAILED, gate held incidentally).**
`self._live("<hub>")` replaces the hub at write bases and call arguments. It is a two-line
accessor returning `getattr(getattr(self, "_ctx", self), name)`, both lines plumbing. The role
engine cannot evaluate a method's return value, so hub 40→9, with no reflective write at all.

The gate stopped it only because footprint rose by 12: a call argument `self._live(..)` makes a
formerly plumbing delegation count as logic. That price is payable, for example 10's
setattr-in-init lowers footprint by 85.

## 3. Counters: proposals and prototypes

The prototypes are in `counters/`:
- `counters.py ROOT` produces the counter rows.
- `flatten_coord.py SRC DST` is the C4 normaliser.
- `score_proto.py` rescores every attempt with the counters swapped in.
- `calib_proto.py` runs the same swap on the 45-case corpus holdout.
- `corpus_counters.sh` measures the counters on every corpus tree.

The prototype score works as follows:
- It swaps untyped_payload_keys→_v2, dup_pairs_v1→dup_pairs_v2, private_reach→_v2 and
  a1_params_over_10→params_over_10_v2, with the same weights.
- It adds four gate-only rows with weight 0 that must not rise: reflective_writes,
  computed_attr_access, family_orphan_overrides and unread_private_globals.
- C4 measures the flattened tree.

| game | counter (smallest fix) | prototyped | result under prototype |
|---|---|---|---|
| 01 | **C1** `untyped_payload_keys_v2`: a key annotated `Any`/`object` (also inside `NotRequired[...]`) is not typed. Stronger, not prototyped: require the contract to bind the consumer (`DataUpdateCoordinator[Payload]`), and fix the functional-form resolution bug. | yes | 164→164, **NULL** (no credit) |
| 02, 03, 10 | **C2** `reflective_writes`, gate-only: explicit `__setattr__/__setitem__/__delitem__/__delattr__`, `setattr/delattr`, `type(x).m(..)`, unbound builtin mutators, `vars(x)[k]=`/`__dict__[k]=`, `getattr(o,n)(..)`, `operator.setitem`, all outside dunder bodies. **The principled fix is in `_common.write_sites`:** read these spellings as the writes they are, so no gate is needed. Also: v1's plumbing rule should not count `setattr`/`object.__setattr__` as delegation. | yes (tripwire) | 02: 16→53, 03: 16→32, 10: 16→120, all **not admissible** |
| 13, and 03's helper | **C2b** `computed_attr_access`, gate-only: getattr/setattr/hasattr/delattr with a non-literal name. Principled fix: interprocedural return roles in `Engine.ev(Call)` (a method returning a hub returns the hub role). | yes (tripwire) | 13: 31→32, **not admissible** without the incidental footprint rise |
| 04 | **C3** `dup_pairs_v2`: effect-free expression statements (constant, name, attribute, `id/len/hash/repr/type/str/...` of simple args) are dropped before windowing. Sturdier, not prototyped: also count single-statement clones of ≥ N nodes, which interleaving cannot break. | yes | 121→121, **NULL** |
| 05c, 05d | **C4** the coordinator is its MRO: inline package-local bases into the coordinator before measuring (or, in `_common`, make `coord_key` the set of package classes in the MRO, resolve roots through `pkg.member`, and sum footprint over the MRO). Also fix dead_by_reachability: `self.m` must resolve up the package MRO (05/05b's 6→301 is a false dead). | yes (normaliser) | flat(05c) and flat(05d) vs flat(base): dS 0, **NULL**. Identity on the baseline (flat(base) vs base: NULL). |
| 06 | **C5** `private_reach_v2`: a foreign read of a coordinator property whose body is only `return self._x` counts as a read of `_x`. More general, not prototyped: price reach to coordinator STATE (any spelling) rather than to underscore names. | yes | 99→99 (baseline itself rises 92→99: existing trivial accessors), **NULL** |
| 07 | **C6** `family_orphan_overrides`, gate-only: an override whose target is the key itself or a family of fewer than 2 members. Belongs in tests/entities.py too (policy, owner's call). | yes | 0→2, **not admissible** |
| 08 | **C7** `unread_private_globals`, gate-only: module-level `_X` that nothing loads. Metric fixes, not prototyped: in dead_by_reachability, a module-level lambda body is not a root unless referenced; in public_surface, an import whose name is never loaded outside an unread binding is not a use. | yes | 0→1, **not admissible** |
| 09 | No structural counter can see a deleted behaviour. **Admit a change to scoring only when the behaviour suite is green and its check count does not fall.** features.py catches this one (5 FAIL). | n/a | still IMPROVES +1.95 on structure alone |
| 11 | **C11** `params_over_10_v2`: literal keys a function reads from its own `**kw` count as parameters. | yes | 28→28, **NULL** |
| 12 | C1 to C7 together | yes | +71.5 but **not admissible** (reflective 16→173, orphans 0→2, unread 0→1) |

**Null holds.** Every counter reads identically on 00 and the baseline (`out/base.counters.json`).

**Corpus holdout** (`out/calib_proto.txt`, the counters measured on all 87 corpus trees):
- 1 of 45 verdicts changes. NEUTRAL 97dc04f2, the away envelope's compare-and-restore
  (`setattr(obj, name, original[name])`), goes from v1's misclassified IMPROVES to WORSENS on
  reflective_writes 14→15. That is the right direction.
- No GOOD case is newly blocked.

**False-positive risks, for anyone adopting the tripwires.**
- The GOOD merge 67e1cf33 (hub facade descriptor) raises reflective_writes 11→13 and
  computed_attr_access. It was already WORSENS under v1, but the tripwires would block that merge
  on their own.
- computed_attr_access is common at baseline (31).
- C2 and C2b are therefore tripwires to replace with the engine-level canonicalisation, not
  permanent score rows.
- C6 and C7 have baseline 0 and no corpus rise.

## 4. Behaviour checks (beyond compile + import)

`tests/features.py` (3573 checks, about 5 minutes) and `tests/entities.py` (1988 checks) were run
with `PYTHONPATH=tests/hastub`. Both are all green on the baseline.

| tree | features.py | entities.py |
|---|---|---|
| 12b = 02+03+10+01+07+08+11+04 | **ALL 3573 PASSED** | 1 FAIL: S8 structural pin (10's setattr hides one `_init_*` assignment) |
| 06 alone | crashes after 2714 ok / 0 FAIL: duck-typed test doubles (`SimpleNamespace`, `FakeCoordinator`) lack `raw_*` | FAILs from the same doubles, plus the pin "coordinator methods read those hubs through _ctx" |
| 05c (source pin `inspect.getsource(_Coord)` patched to read the MRO, in the scratch copy only) | 1234 ok / 0 FAIL, then aborts on a second AST pin (`methods["_async_update_data"]` of the class node) | not run |
| 09 | **5 FAIL**: economy widening, open-window relax, away set-back, default fallback | not run |

So the evasions in 12b preserve behaviour as far as features.py sees.
- 06 and 05c would also need their structural test pins and test doubles edited. A gamer would
  do that; it is test-harness coupling, not production behaviour.
- The suite's structural pins (S8, "hubs through _ctx", getsource of the class) are an existing,
  accidental line of defence against 05c, 06 and 10.

## 5. Findings about the score itself

1. **Name-keyed identity is the largest hole.** The coordinator class name, literal root quals
   and `fn.cls == coord_key` make a 5-line rename worth +101, about 125 times the best real merge.
   C4 closes it.
2. **Spelling-keyed write detection is the second.** hub_solve_writes,
   shared_inplace_writes and writers_multi each fall to zero under a re-spelling. The v1 plumbing
   rule makes it worse: it credits `setattr(self, "X", v)` and `object.__setattr__(x, "f", v)` as
   non-logic, so a gamer earns footprint while evading.
3. **Declaration-keyed metrics** (untyped_payload_keys, family_splits) credit a declaration without
   checking that it constrains anything. Examples are `Any` values and singleton families.
4. **The weights amplify it.** A P2+P3 or P6 metric reaching 0 is worth 8.9 or 6.9 × log2(base+1),
   that is +35 to +51 for one game. The log form makes "to zero" the most lucrative move, and
   evasion is exactly the move that reaches zero.
5. **The gate's accidental catches are not guards.** 03, 04, 05, 05b and 13 were each stopped
   first by an unrelated metric's side effect: footprint's plumbing rule, or dead_by_reachability's
   missing MRO walk. Each was payable, or was sidestepped with a different spelling.
6. **Metric bugs found along the way:**
   - functional-form TypedDict never resolves in `contract()`;
   - dead_by_reachability's `self.m` does not walk package bases.

## 6. Files

- `attempts/NN_*.py`: the attempt scripts. Re-run one with `bash run_attempt.sh attempts/NN_x.py`;
  `WT=` overrides the worktree. `attempts/rt_lib.py` holds the span-rewrite helpers.
- `run_attempt.sh`, `import_check.py`: the harness.
- `out/`:
  - `base.json`: baseline vector;
  - per-attempt `.diff`, `.diffstat`, `.json`, `.delta.json` and `.counters.json`;
  - `flat_*.json`;
  - `score_proto.txt`, `calib_proto.txt`;
  - test logs `features*_wt*.log` and `entities*_wt*.log`. In those logs, wt2 is 12 then 12b,
    wt3 is 05c then 06, and wt4 is 09. `features_base.log` and `entities_base_clean.log` are the
    baseline runs.
- `counters/`: counters.py, flatten_coord.py, score_proto.py, calib_proto.py, corpus_counters.sh.
- `corpus/*.counters.json`: counters on every corpus tree.
