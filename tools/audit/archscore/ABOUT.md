# The architecture score

It prints, for a diff, delta-S, the gate rises and the per-metric deltas, so a reviewer can ask for a
stated reason. **It is a review trigger, never a target a seat is rewarded for moving**, and a gain that
appears only without the counters did not happen.

Since R9-EG-A4 (#1774, tvofi's decision R3-6) it is a required check: `arch-score`
(`.github/workflows/arch-score.yml`, rule in `gate.py`) passes a pull request whose change reads
delta-S >= 0 with no gate metric rising, or whose body explains each rise under `## Architecture score`,
one line per metric, as a budget raise is argued. The required check runs the base's copy of this directory and of `tests/structure.py`, so an edit to the instrument takes effect only after it merges.

    python3 tools/audit/archscore/score.py --diff origin/main            the tree against a ref
    python3 tools/audit/archscore/score.py --diff BASE_REF HEAD_REF      two refs
    python3 tools/audit/archscore/vector.py ROOT > v.json                one tree's vector
    python3 tools/audit/archscore/score.py --delta BASE.json HEAD.json   two vectors

`ROOT` holds `custom_components/heatpump_optimizer`. A vector costs about ten seconds.

## What it measures

`vector.py` is the definition: `SCORE_METRICS` and `GATE_ONLY`, one line each. A change is
**admissible** when no score metric and no gate-only tripwire rises (every metric is a static count, so
the tolerance is 0). Its score is `sum w * log2((ref + 1) / (cur + 1))`; verdict IMPROVES, NULL or
WORSENS (a rise, or a negative score). Weights are `weights.json`, frozen at the hash
`tests/arch_score.py` carries, and a weight change is a policy change.

Where `tests/structure.py` has a metric the score reads that definition (`vector.py` says which and
how the copy is re-pointed); the metrics it has no row for are in `metrics/`. The two role engines are
not one: structure's `CoordinatorRoles` answers "is this value the coordinator", the engine in
`metrics/common.py` follows paths out of it (the hub and shared-object write censuses need the path).

## The counters

The red team raised the score with 13 of 16 moves that left the architecture no better. Each counter
closes one, and `ARCHSCORE_ABLATE=C1,C3,...` switches a counter off to show the game it closes then
reads IMPROVES. The attempt is `planted/redteam/<NN>_*.py` and its case id is `rt_<NN>_*`.

| counter | closes | attempt |
|---|---|---|
| C1 an `Any` or `object` key is untyped | an all-`Any` TypedDict | 01 |
| C1b so is any other spelling of one: a union with one, `Optional`, `Annotated`, a string, a package alias | the all-untyped contract re-spelled (ARCH-s3, round 10) | 17 |
| C2 `reflective_writes`, C2b `computed_attr_access` (tripwires) | `object.__setattr__`, `type(x).__setitem__`, a hub handle behind a computed name | 02, 03, 10, 13 |
| C3 a clone window is any two statements of a block, in order | junk interleaved in every clone window | 04, 04b to 04zb |
| C4 the coordinator is measured as its whole package class hierarchy | a rename plus an empty subclass, a mixin | 05, 05b, 05c, 05d |
| C5 a passthrough property reads as its private | public `raw_<x>` accessors | 06 |
| C6 `family_orphan_overrides` | families declared into one-member families | 07 |
| C6b an override's target is the first word of the entity's English name | two neighbours declared one invented family (ARCH-s3, round 10) | 18 |
| C7 `unread_private_globals` | a keep-alive registry | 08 |
| C11 literal keys read from a `**kw` are parameters | keyword parameters turned into `**kw` | 11 |
| C12 a `cast(T, x)` is its `x`: the payload census follows it and it types nothing, the footprint does not read it as delegation | the payload builder's return behind a cast (#1852 round-1 review) | 15 |
| C13 the scheduled cycle is a hub root (`hub_solve_writes.ROOTS`) | a hub write moved out of the solve into a pre-solve step (#1887 round-1 review) | 14 |
| C14 a parameter annotated with a package class holds an instance of it (`untyped_payload_keys.Flow.seed`), in any spelling `annotation_members` takes apart | a published dict moved behind an annotated helper, its keys read as gone (ARCH-s3, round 10: ten away keys); the type spelled `Union[None, X]` or `Annotated[X, ..]` (#2293 round-1 review) | 16, 16b, 16c |
| C15 a call is what its callee returns; a hub handed over as a zero-argument reader (`lambda: ctx._thermal_params`, a method reference) or rebound onto a collaborator's attribute is the hub there (`common.Engine`) | a collaborator's hub held as a reader, its writes read as gone (D7-s1-83: ARCH2-s1's P1 prototype hid three spellings) | 19 |
| C16 a coordinator method handed to code outside the package (an event, MQTT or timer callback) is a hub root (`hub_solve_writes.event_roots`) | a solve's hub write moved into an event callback (ARCH2-s2 P4's instrument half) | 20 |
| C17 a function-scope import is an edge of the layering graph (`metrics/layering.py`) | a solver import made lazy, the module read as freed of scipy (ARCH2-s4, round 10); re-spelled into the `else` of `if TYPE_CHECKING:` (24), under `if not TYPE_CHECKING:` (25), as an absolute self-import on the `from` form (27), on the plain dotted `import` with an alias (28) and with the full dotted read (29), through an absolute from-import's module binding (30), from the namespace ABOVE the package -- `import custom_components` aliased (32) and bare (35), `from custom_components import heatpump_optimizer` (33) and aliased (34) -- and as a constant-name `import_module` (26), by its `name` keyword (31), or through a module-level string constant (37), each of them runtime code. Ancestor and descendant are one predicate: the relation of a dotted name to the package's own path, at a dot boundary | 21, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 37, 40 |
| C18 a private name read through a module binding (`m._x`, `getattr(m, "_x")`, a resolved `import_module(..)._x`) crosses like its import | `from .m import _x` re-spelled `from . import m` and `m._x(..)`; the same respelled with the package's full path (27), off the binding a plain dotted `import` makes (28, 29), off the module binding an absolute from-import makes (30), from the namespace ABOVE the package (32 to 35), through an attribute or `getattr` chain rooted at one (36), and through a constant-name `import_module` (26), its `name`-keyword form (31) or a module-level string constant (37). A read that resolves to a module is also that module's EDGE, whether the name read off it is public or private -- which is what an import of an ancestor needs, since that statement loads no module of ours; the edge is added once, at the OUTERMOST point of the chain whose receiver resolves to a module, so a chain that walks past it still takes it (38, 39, 41) | 22, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 41 |
| C19 `unused_boundary_imports` (gate-only): a boundary import whose names the module never reads | each violating module climbs a layer with an unread `import homeassistant` | 23 |
| C20 a literal spec is normalised: numbers by value, keywords and dict items in order (`metrics/literal_clones.py`) | the copies of a selector re-spelled with float bounds | 42 |
| C21 a local bound once to a spec reads as it | a selector's bound hoisted into a local | 43 |
| C22 a card function's own names are numbered by first use (`metrics/card.py`) | the card's copied functions given renamed locals | 44 |
| C23 `shape_copies` (gate-only): a function's own names are numbered, numbers and strings abstracted (`metrics/shapes.py`) | a private helper copied into its importer with its names changed, the crossing read as gone | 45 |

Attempt 09 deletes a working feature. No structural counter exists: only the behaviour suite sees it,
and a score is only meaningful for a change whose suite stays green and whose check count does not
fall. It reads inadmissible today because the gutted functions leave one member dead, an incidental
rise, not because anything measures the deletion. Tripwires are a stopgap until the role engine reads
a reflective spelling as the write it is, which retires C2 and C2b.

## The calibration

`calibrate.py` classifies the labelled cases and the red-team attempts; `tests/arch_score.py` fails when
any verdict differs from `calibration/expected.json`, misses included.

- **corpus**: 45 commits of main's history, GOOD / BAD / NEUTRAL from a source that is not a metric (the
  quote is in `calibration/corpus.tsv`). Both sides are stored vectors; `calibrate.py --measure-corpus`
  re-derives them from git.
- **planted**: the scripted edits of the pinned tree (`planted/cases.py`: `PINNED`), measured live.
- **redteam**: the attempts, measured live, plus a rename null.

The pin is a commit on main. The scripts anchor on its text and assert each anchor occurs once, so a
tree that is not the pin fails loudly.

### What R9-EG-A4 moved

Widening the hub census to the scheduled cycle (C13) re-measured `hub_solve_writes` on all 87 stored
corpus vectors (`calibrate.py --measure-corpus --only-metric hub_solve_writes,footprint`; the footprint
re-measure, C12's, moved none). One corpus verdict moved: `c2a0448d` (GOOD, #1751) reads WORSENS, not
IMPROVES, because its forecast-seeded outdoor reading is one more live-state write in the cycle
(70 -> 71). The cycle-wide census charges a new reading the way it charges a solve value; a pull request
adding one explains the rise. `a1_N5_annotated_return` (NULL) is new and reads WORSENS: the wave's
#1867 disagreement, an annotated alias and a bare `return <name>` that the footprint counts as logic.

### What R10-ARCHSCORE-COVERAGE moved (ARCH-s3's three holes)

C1b, C6b and C14 change three definitions, so each carries a planted BAD and GOOD pair (`a3_payload_any_spelling_*`,
`a3_family_lead_homing_*`, `a3_payload_annotated_param_*`; the family pair has a redundant-override NULL) and
a red-team attempt (16, 17, 18). C1b and C14 read an annotation through one unwrapper, `annotation_members`, after
#2293's review found C14 taking apart fewer spellings than C1b; `a3_payload_annotated_param_spelling_*`, 16b and 16c
pin the two it missed. Only those new cases entered `expected.json`: no recorded verdict moved, no weight
perturbation moves one, and the corpus vectors re-measured for `untyped_payload_keys` and `family_orphan_overrides`
are byte-identical (`calibrate.py --measure-corpus --only-metric untyped_payload_keys,family_orphan_overrides`).
`ARCHSCORE_ABLATE=C14`, `C1b` or `C6b` reopens its own attempt (it reads IMPROVES) and leaves the other two closed.
The cases need the pin to hold no instance, so `controls.py`'s `on` names the case an arm is applied on top of.

### What R10-STRUCTURE-BLIND moved (D7-s1-01, D7-s3-01)

`tests/structure.py`'s dead-member census resolves a load's receiver (`ReceiverTypes`), so a member
whose every load is on a receiver the source types to another class is dead rather than kept by a
shared name. `dead_members` is the leaf this change moves, on 85 of the 87 stored trees
(`calibrate.py --measure-corpus --jobs 4`; the section above records the leaf R10-ARCHSCORE-COVERAGE
part 2 moves, and the two are the corpus's whole delta). No corpus verdict moved.

One planted verdict did, and it retires a row of the table below. `a3_dead_by_reachability_fix` (GOOD)
read NULL because the census kept its deleted member alive behind a same-named member of another class
on an untyped receiver -- the row recorded that as "its documented residual". With the receiver typed it
reads IMPROVES, which is the fix the case is, and the pre-study's own reading.

### What R10-ARCHSCORE-COVERAGE part 2 moved (the hub census: C15, C16)

C16 makes every stored corpus vector's `hub_solve_writes` count the event callbacks' writes: +3 on 74 corpus trees,
+2 on 11 and +0 on 2 (`calibrate.py --measure-corpus --only-metric hub_solve_writes,shared_inplace_writes,footprint`;
`shared_inplace_writes` and `coord_footprint` re-measured byte-identical). Today's tree reads 38 -> 41, the three
event writes `tests/arch_score_head.py` now lists as producers. C15 moves no corpus or today's value: main spells
every hub handle as a path. It closes the spellings the next refactor would use (attempt 19), and ARCH2-s1's
`census_probe.py --tree proto` reads all three of its blind spellings as seen. Each counter carries a planted BAD and
GOOD pair (`a3_hub_reader_*`, `a3_hub_event_write_*`) and an attempt; `ARCHSCORE_ABLATE=C15` or `C16` reopens its own.

### What R10-ARCHSCORE-COVERAGE part 3 moved (layering: `layer_violations`, `private_cross_module`)

Two score metrics at the floor weight (they guard no register class; `weights.json` is unchanged and its floor
applies) and a tripwire. `layer_violations` counts modules reaching, through other package modules, a layer
above their own: pure < the scipy solver < the Home Assistant glue, a module's layer being the highest boundary
it imports itself. `private_cross_module` counts distinct private names one module names of another.
ARCH2-s4's P1 (one owner of the UTC clock), which every earlier metric read as 0.0000, now reads as both
falling (`score_delta.py`).

The first definition, modules bound to a boundary by import or reach, was calibrated first and dropped: it
read four GOOD corpus decompositions (`ca937daa`, `69781076`, `ec263d82`, `33cedffa`) as WORSENS, because a module
extracted from the glue that imports Home Assistant is one more bound module. Under the layer rule a glue
module extracted from the glue is glue, and no recorded corpus verdict moves (`calibrate.py --stored-only`
after `--measure-corpus --only-metric layering`). `56cb0027` (GOOD, already WORSENS on `duplication_copies`)
also rises on `layer_violations`: its unit read made `price_model`, a pure module, reach Home Assistant through
`inputs`.

Round-1 review (`#2320`) found the rule's residual was wider than the sentence claimed, and the four seams it
named are closed here, each with its attempt: the `else` of `if TYPE_CHECKING:` (24), which runs; `if not
TYPE_CHECKING:` (25), true away from a type checker; a constant-name `importlib.import_module` (26), relative and
anchored on `__package__` too; and the absolute self-import `from <pkg>.m import _x` (27). All four read IMPROVES
against the round-1 instrument and NULL against this one, so the property is the census's, not the plant's. The
guard itself is now read as the whole of a positive `if TYPE_CHECKING:` `body`, no more: `_type_checking_guard`
in `metrics/common.py` takes the bare sentinel, and a `TYPE_CHECKING` the module rebinds is not typing's, so the
branch runs and its imports count. `a3_layer_violations_null` carries an annotation-only `if TYPE_CHECKING:`
import of the optimizer on `drift.py` so the exclusion is measured in both directions: with the exclusion read it
is NULL, with it ignored the pure module gains the solver and the case reads WORSENS.

Round-2 review (`#2320`) found that four seams are one class, not four: the rule's own document follows an
absolute self-import, a module binding and a constant-name dynamic import, and the round-2 repair handled one
spelling of each -- `from <pkg>.m import _x`, a relative module binding, a positional `import_module`. The three
further spellings are closed here, an attempt each, each reading IMPROVES against the round-2 head and NULL
against this one: `import <pkg>.m as _o` and the full dotted read off `import <pkg>.m`, whose statement the
graph reached for no edge and whose binding no `modalias` held (28, 29); the module binding an absolute
from-import `from <pkg> import optimizer as _o` makes, which `Pkg.imports` files as an external name (30); and
`import_module(name=".optimizer", package=__package__)`, the same call with its first parameter passed by its
own name (31). `graph` now builds every module binding from the statements it runs -- relative, absolute
from-import, plain dotted -- and resolves a private read through the dotted path that binding roots, so the
spelling is not enumerated anywhere. The census in the same pull request counted both absolute self-import forms
under one counter and planted only the `from` one, so a corpus tree carrying the dotted spelling would have read
as covered; the counters are now per form and the planted precondition tree carries each.

Round-3 review (`#2320`) found the predicate's domain rather than a missing arm: `_self_module` accepted
`SELF` and `SELF.*` and returned `None` for a strict PREFIX of the package, so an import of
`custom_components` -- the namespace the package is nested in -- took no edge, rooted no binding, and kept
the solver reach, reading `IMPROVES dS +0.5849` with `layer_violations 3 -> 2` as its larger term. Round 3
had added the descendant direction (`import <pkg>.m`) only; the ancestor is the same statement family. One
predicate answers both now: `_relative`, `_namespaced` and `_pkg_module` compare a dotted name with `SELF`
at a dot boundary, and a private read that resolves to a module takes that module's EDGE as well as its
crossing -- which is what an ancestor import needs, since the statement alone loads no module of ours. The
receiver of a read resolves through attribute chains and through `getattr` chains, so
`getattr(getattr(_cc, "heatpump_optimizer"), "optimizer")._x` (36) is the same arm as
`_cc.heatpump_optimizer.optimizer._x` (32), and a name held by a module-level string constant is
statically readable, so `_MOD = ".optimizer"` with `import_module(_MOD, __package__)._x` (37) is the
constant-name call it spells. Six attempts, 32 to 37, read IMPROVES against the round-3 head and NULL or
WORSENS here. The boundary is stated rather than implied: a reach is followed when the dotted name is the
package, a path below it, or a strict dot-boundary PREFIX of it.

Round-4 review (`#2320`) found the edge the ancestor statement needs was taken only by the PRIVATE-read arm:
`_private(n.attr)` guarded the arm that gives an ancestor import its edge, so re-spelling a PUBLIC
higher-layer import through the ancestor (`price_model.py`'s `normalize_price_per_kwh`,
`disinfection.py`'s `parse_bool` and `UNBOUNDED`) kept the reach and dropped `layer_violations`
(attempts 38, 39). The edge is now a read's own, public or private; only the CROSSING stays private-only,
which is the one thing C18 prices. The reviewer's own probe measured why the guard cannot simply be
dropped -- every intermediate node of a dotted chain then takes an edge, so `rt_32` to `rt_35` read
WORSENS -- and the rule is that the edge lands once, on the node the chain ENDS on (`_ends_chain`).
`_module_const` read `ast.Assign` only, so the same module-level string constant written with its type
(`_MOD: str = ".optimizer"`) was refused by the resolver rather than by the model; it reads either spelling
now (attempt 40).

Round-5 review (`#2320`) found the chain-end test read from the wrong end when a chain walks ON past the
module: `_cc.<pkg>.optimizer._utc_step_starts.__call__(..)` names `optimizer` four segments down, and the
outermost receiver resolves to a function, so the edge was taken only where the outermost node resolved.
`_reached` now searches the chain OUTSIDE IN and returns the module the first receiver resolves to, with
the name read off it, so a chain that continues past the module is the same arm (attempt 41).

What it does not see, and no rule here closes:

- a private crossing spelled outside the ones C18 counts: `getattr(_o, "_utc" + "_step_starts")`, `vars(_o)["_utc_step_starts"]`,
  and `_m = _o; _m._utc_step_starts`. Each reads the same private of the same module and drops the crossing.
- a name COMPUTED at runtime: `importlib.import_module(f".{module}", __package__)` (the package's own is
  `__init__.py`'s loader), `exec`, and an import bound by a rebind rather than an import statement. A name
  held by a MODULE-LEVEL string constant is NOT in this list: it is statically readable, in either spelling,
  `_MOD = ".optimizer"` or `_MOD: str = ".optimizer"` (attempts 37, 40). The census counts the computed
  form as `dynamic:computed` rather than leaving it out.
- a module-level string constant bound by UNPACKING, `_MOD, _X = ".optimizer", 1`: `Pkg.tops` records a
  binding only when the target is an `ast.Name` (`common.py:275`), and the same construct read as
  `_MOD = ".optimizer"` or `_MOD: str = ".optimizer"` IS closed (attempts 37, 40). Dispositioned rather than
  closed because the fix is in `metrics/common.py`, a module every architecture metric shares: widening its
  index to tuple targets moves the whole instrument, which a folding counter should not do (#2320 round 5).
- a FUNCTION-LOCAL string constant, `_M = ".optimizer"` inside the function that calls `import_module(_M, ...)`.
  OPEN, and recorded rather than closed: `Pkg.tops` is built from the module body, so the resolver reads
  module-level bindings only, and following a local would need the enclosing scope's assignments. A seat
  writes that constant at module level, where it is closed; the residual is the local spelling (#2320 round 4,
  the reviewer's own completeness note, not one of its two blocks).
- `__import__(".optimizer", fromlist=[...], level=1)` -- the same constant name in the builtin's own spelling. It is
  refused as an attempt rather than left open: the round-2 review executed it against a stand-in package and it
  raises `KeyError: "'__name__' not in globals"` in CPython 3.14.7, so it is not code a seat can ship, and the
  resolver reads no anchor it states. `importlib.import_module`, positional or by keyword, is the spelling that runs.
- C19's tripwire keys on "never read", and one bare read satisfies it: an unread `import scipy` plus `assert scipy`
  climbs a layer and leaves `unused_boundary_imports` unmoved.
- `a3_private_cross_module_fix` is a pure rename of a private to a public name. Declaring a private public is a
  real change to an API and the metric is right to credit it, but it is this metric's cheapest move, and a D7
  brief quoting the counter should say so rather than read it as a decoupling.

### What R10-ARCHSCORE-COVERAGE part 4 moved (the card, and literal specs)

Three score metrics at the floor weight. `literal_clone_copies` (`metrics/literal_clones.py`) counts the copies of
a declaration spelled as a call or literal more than once -- a selector, a schema, a record -- which sits inside one
statement and so outside `duplication_copies`' windows: ARCH2-s5's F1 (the setup wizard reading its options-registry
widgets) reads 184 -> 132 on it at the merge base `6e5753a4a` (ARCH2-s5's `arch_delta.py`, base `9061fbd3d`). The card (`www/*.js`, read by a tokenizer in `metrics/card.py`, never a parser)
gets `card_dead_definitions` (D7-s3-02's `textWidth` was its one; R10-UX-SETUP gave it callers, so today reads 0) and `card_clone_copies`, a 20-token window
census; the window was calibrated on ARCH2-s5's four card patches, where 16 tokens read the finite-number owner (a
dedupe) as one copy more. The shape census of N spellings of one rule is part 5's.

### What R10-ARCHSCORE-COVERAGE part 5 moved (the shape census, item 6)

`shape_copies` (`metrics/shapes.py`) counts the members of every class of two or more functions with one SHAPE:
the body with the function's own names numbered and numbers and strings abstracted (counter C23), which is the
clone window's normalisation applied to the whole function. It reads what the window cannot: a rule that is a
whole function below two statements or 30 nodes. On ARCH-s2's own seam rule for the payload-number guard
(`shape_payload_guard.py`'s `family()`, at its baseline `554e2ecfa`) it joins 26 of the 35 implementations into
3 classes; the other 9 are spelled differently, which is what a census on spellings cannot see.

Item 6 asked for it to be calibrated first and weighted only if not gameable. Calibrated, it is **gate-only, weight 0**:

- Weighted at the floor, the one corpus commit it lowers is BAD (`ca711b56`, 69 -> 68), which would read IMPROVES.
- One statement re-spelled leaves a class while the rule is still written twice: `a3_shape_copies_respelled_control`
  (BAD) reads NULL. A weight would pay that move.
- As a tripwire it moves no recorded verdict: of the 45 corpus commits it rises on five BAD, two NEUTRAL and one
  GOOD (`0323c5b8`, 81 -> 83), each already inadmissible; it is flat on the rest. It refuses attempt 45, a private
  helper copied into its importer under new names, which lowers `private_cross_module` and reads IMPROVES without C23.
- Its GOOD plant (`a3_shape_copies_fix`, the copy removed) reads NULL: weight 0 pays no dedupe, by construction.

### Where it differs from the pre-study's calibration (PRE-STUDY section 6)

Three verdicts moved. Sharing `tests/structure.py`'s definitions changed two; the third is the
correction the pre-study already recorded (section 7).

| case | label | was | now | why |
|---|---|---|---|---|
| `97dc04f2` | NEUTRAL | IMPROVES | WORSENS | compare-and-restore leaves the pattern in place; `reflective_writes` rises (the recorded correction) |
| `ca937daa` | GOOD | IMPROVES | NULL | the clone census counts copies, not pairs: the pair count fell 116 to 109 while the copies stayed 43 |
| `a3_private_reach_fix` | GOOD | IMPROVES | NULL | it swaps a private read for the public `mode` passthrough property, which C5 reads as the same reach |

`a3_dead_by_reachability_fix` was a fourth until D7-s3-01 gave the dead-member census a typed receiver;
it reads the pre-study's IMPROVES again, so it is no longer a difference and the pre-study's own table
is right about it.

Nothing else moved: the corpus holdout, every other planted case, and weight sensitivity (no weight
perturbation moves a verdict) read as the pre-study recorded them. Every red-team attempt labelled GAME reads
NULL or inadmissible. The three that read IMPROVES as KNOWN-OPEN until R9-EG-A2 (`rt_04h`, `rt_04i`,
`rt_04j`) are GAMEs since C3 joins clones across any gap, and read NULL.

## Changing it

A verdict that moves is a diff to `expected.json`: `calibrate.py --record` prints each one. Say why in
the commit. A new evasion found is a new case in `planted/redteam/` with its counter.

### Interleaved junk: closed by the window, not by a list

Junk interleaved in every clone splits the shared census's windows of two adjacent statements, and the
score would read that as a dedupe. C3 replaces the census in the score's copy only
(`counters.gapped_clones`): a window is any two statements of one block, in order, however far apart.
A copy keeps its original's statements in order, so whatever is interleaved -- any spelling, any count,
with an effect or without -- leaves the original's pairs intact and the clone joined.

- Its adjacent pairs are exactly the shared census, and `tests/arch_score_head.py` checks the two agree,
  so the score's count is a superset of the ratchet's: 59 shared copies read 87 at `origin/main`.
- Every interleaving attempt reads NULL: 04 and 04b to 04zb, i.e. every spelling an enumeration was
  shown (the round-3 KNOWN-OPEN three, the two review rounds' seven, the seat's probes), and an
  effectful `print` that no rule dropping dead statements could ever drop.
- It replaced the statement-dropping C3 of the first rounds, which each review beat with a spelling
  outside its grammar.

One planted verdict moved with it: `a1_G2_dedupe` (GOOD) reads NULL, not IMPROVES. G2 moves the two
fabric learners' shared replay block into a helper, but the learners still share 12 ordered statement
pairs (the guard, the `dt_h` line, the replay call, the finiteness check), so under any gap they stay one
clone class and the copy count does not fall; the adjacent census lost its only window and read the
partial dedupe as a whole one. No corpus verdict moved (81 corpus vectors re-measured), and no weight
sensitivity. The matcher costs 228 s against 208 s for the corpus re-measure (`--measure-corpus --jobs 4`,
one run each, this machine).

What it does not see: a copy whose statements are reordered or split across blocks. `rt_04zz1` pins the
second: it wraps each statement of a copy in its own always-true `if <n>:`, and reads IMPROVES (+12.63,
admissible), labelled KNOWN-OPEN so a fix that closes it flips the case and asks for the re-record. A
window that crosses block boundaries would close it, at the cost of joining unrelated code that happens
to share two statements anywhere in a function. Until then a reviewer reads such a diff as what it is,
restructuring with no change in logic.

The converse of a known limit below: a count credits a partial repair, but under the gap census a
partial dedupe that leaves a pair sharing any two statements in order reads NULL (`a1_G2_dedupe`).

Known limits, so a reader does not credit the score with more than it does:

- It prices the coordinator and the structures around it; a decomposition elsewhere (the optimizer) reads NULL.
- A count credits a partial repair (one site fewer reads as a gain); it cannot tell a shape from its instances.
- It does not follow module-level globals into the shared-object census.
- Deleting a feature is invisible to it (above).
- Any evasion the red team did not try is open.
