# The architecture score

It prints, for a diff, delta-S, the gate rises and the per-metric deltas, so a reviewer can ask for a
stated reason. **It is a review trigger, never a target a seat is rewarded for moving**, and a gain that
appears only without the counters did not happen.

Since R9-EG-A4 (#1774, tvofi's decision R3-6) it is a required check: `arch-score`
(`.github/workflows/arch-score.yml`, rule in `gate.py`) passes a pull request whose change reads
delta-S >= 0 with no gate metric rising, or whose body explains each rise under `## Architecture score`,
one line per metric, as a budget raise is argued. The workflow runs the pull request's own copy;
CODEOWNERS names this directory, so an edit to the instrument takes the owner's review.

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
| C3 a clone window is any two statements of a block, in order | junk interleaved in every clone window | 04, 04b to 04zb |
| C4 the coordinator is measured as its whole package class hierarchy | a rename plus an empty subclass, a mixin | 05, 05b, 05c, 05d |
| C5 a passthrough property reads as its private | public `raw_<x>` accessors | 06 |
| C6 `family_orphan_overrides` | families declared into one-member families | 07 |
| C7 `unread_private_globals` | a keep-alive registry | 08 |
| C11 literal keys read from a `**kw` are parameters | keyword parameters turned into `**kw` | 11 |
| C12 a `cast(T, x)` is its `x`: the payload census follows it and it types nothing, the footprint does not read it as delegation | the payload builder's return behind a cast (#1852 round-1 review) | 15 |
| C13 the scheduled cycle is a hub root (`hub_solve_writes.ROOTS`) | a hub write moved out of the solve into a pre-solve step (#1887 round-1 review) | 14 |

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
