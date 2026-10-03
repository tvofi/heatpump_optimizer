# The architecture score

Report-only. It prints, for a diff, delta-S, the gate rises and the per-metric deltas, so a reviewer
can ask for a stated reason. **It is a review trigger, never a target a seat is rewarded for moving**,
and a gain that appears only without the counters did not happen. Whether delta-S becomes a required
check is round 10's decision (issue 1774, R9-EG-A4), after one wave of report-only data.

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
| C2 `reflective_writes`, C2b `computed_attr_access` (tripwires) | `object.__setattr__`, `type(x).__setitem__`, a hub handle behind a computed name | 02, 03, 10, 13 |
| C3 a statement dead by data flow does not split a clone | junk interleaved in every clone window | 04, 04b to 04n |
| C4 the coordinator is measured as its whole package class hierarchy | a rename plus an empty subclass, a mixin | 05, 05b, 05c, 05d |
| C5 a passthrough property reads as its private | public `raw_<x>` accessors | 06 |
| C6 `family_orphan_overrides` | families declared into one-member families | 07 |
| C7 `unread_private_globals` | a keep-alive registry | 08 |
| C11 literal keys read from a `**kw` are parameters | keyword parameters turned into `**kw` | 11 |

Attempt 09 deletes a working feature. No structural counter exists: only the behaviour suite sees it,
and a score is only meaningful for a change whose suite stays green and whose check count does not
fall. It reads inadmissible today because the gutted functions leave one member dead, an incidental
rise, not because anything measures the deletion. Tripwires are a stopgap until the role engine reads
a reflective spelling as the write it is, which retires C2 and C2b.

## The calibration

`calibrate.py` classifies 103 labelled cases and the red-team attempts; `tests/arch_score.py` fails when
any verdict differs from `calibration/expected.json`, misses included.

- **corpus**: 45 commits of main's history, GOOD / BAD / NEUTRAL from a source that is not a metric (the
  quote is in `calibration/corpus.tsv`). Both sides are stored vectors; `calibrate.py --measure-corpus`
  re-derives them from git.
- **planted**: 58 scripted edits of the pinned tree (`planted/cases.py`: `PINNED`), measured live.
- **redteam**: the attempts, measured live, plus a rename null.

The pin is a commit on main. The scripts anchor on its text and assert each anchor occurs once, so a
tree that is not the pin fails loudly.

### Where it differs from the pre-study's calibration (PRE-STUDY section 6)

Four verdicts moved. Sharing `tests/structure.py`'s definitions changed two, the counters one, and one
is the correction the pre-study already recorded (section 7).

| case | label | was | now | why |
|---|---|---|---|---|
| `97dc04f2` | NEUTRAL | IMPROVES | WORSENS | compare-and-restore leaves the pattern in place; `reflective_writes` rises (the recorded correction) |
| `ca937daa` | GOOD | IMPROVES | NULL | the clone census counts copies, not pairs: the pair count fell 116 to 109 while the copies stayed 43 |
| `a3_dead_by_reachability_fix` | GOOD | IMPROVES | NULL | the dead-member census keeps a member alive when another class defines its name and an untyped receiver reads it (its documented residual) |
| `a3_private_reach_fix` | GOOD | IMPROVES | NULL | it swaps a private read for the public `mode` passthrough property, which C5 reads as the same reach |

Nothing else moved: the corpus holdout, every other planted case, and weight sensitivity (no weight
perturbation moves a verdict) read as the pre-study recorded them. Every red-team attempt labelled GAME reads
NULL or inadmissible. The three that read IMPROVES as KNOWN-OPEN until R9-EG-A2 (`rt_04h`, `rt_04i`,
`rt_04j`) are GAMEs since C3 drops a statement dead by data flow, and read NULL.

## Changing it

A verdict that moves is a diff to `expected.json`: `calibrate.py --record` prints each one. Say why in
the commit. A new evasion found is a new case in `planted/redteam/` with its counter.

### Interleaved junk: what C3 closes, and what it leaves

Junk interleaved in every clone splits its windows, and without C3 the score reads that as a dedupe
(IMPROVES, admissible). C3 drops, before a window is cut, every statement dead by data flow
(`counters.inert_statements`): one whose expressions are effect-free by grammar (constants, names,
operators, displays, and calls only of a PURE builtin, a lambda, or a non-dunder method of a value built
from literals) and which binds only names nothing in the function reads; an `assert`, `if`, `while` or
`for` whose test folds to a constant is judged on the branch that runs, and a `try` on its every part. It is
a class by grammar, not a list of spellings: the round-3 KNOWN-OPEN three (`assert True`, `_ = None`,
`(_ := 0)`) and four no list carried (`rt_04k` a dead store, `rt_04l` a called lambda, `rt_04m` an empty
`try`, `rt_04n` a method of a fresh literal) all read NULL.

Still open, by design: a statement with an effect the grammar cannot rule out -- a call of anything else,
a write through an attribute or a subscript. That is logic in the diff, not junk, and a reviewer reads a
duplication-driven IMPROVES against the diff, as a report and not as evidence. A gap tolerance inside the
clone window would close it too, but it redefines the window `tests/structure.py` shares, so it is not
taken here.

Known limits, so a reader does not credit the score with more than it does:

- It prices the coordinator and the structures around it; a decomposition elsewhere (the optimizer) reads NULL.
- A count credits a partial repair (one site fewer reads as a gain); it cannot tell a shape from its instances.
- It does not follow module-level globals into the shared-object census.
- Deleting a feature is invisible to it (above).
- Any evasion the red team did not try is open.
