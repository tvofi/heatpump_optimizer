Root-cause analysis for the bug-class register's merge conflicts, with its countermeasure. Every root-cause PR appends its `_rca` entry after the same last entry of `dev/audit/config/bugclasses.json`, so when two are open at once, the second to merge goes `DIRTY` and a seat has to merge main by hand. This PR routes the register to the existing `ledgermerge` driver (`tools/merge/ledger_merge.py`) through `.gitattributes`. It adds `dev/audit/rca/R9-RCA-bugclasses.md`, its evidence under `dev/audit/rca/bugclasses/`, and one `_rca` entry. It changes no production or policy file.

**Count.** I replayed every merge since the register existed (2026-09-23) in which both parents changed it, across all 268 `origin/*` refs. There are 27. Four conflicted on the register, all on 2026-10-07: `82af801a` (#2012), `e62b8b63` (#2018), `af62b2b8` and `dfe2bb79` (#2014). The brief said there were several earlier instances; I found none in any reachable merge.

**Process state: (d).** The driver routing existed and worked for the files every branch writes. Its precondition changed on 2026-10-02 (`606ad289`), when the rule began requiring every RCA to add an in-tree `_rca` entry. Nothing noticed that the register had become one of those files.

**Cost test.** Each instance waited 25 to 26 minutes, from main's merge to the hand resolution, and then needed a new review verdict at the new head. Since the rule landed, 3 of the 5 entry-adding PRs conflicted. The driver costs 0.08 s, and runs only when both sides changed the file. GitHub still shows `DIRTY`, because it never runs a merge driver. What changes is that the merge train's `remerge_main.sh` now clears it automatically, with no fixer seat and no resolution to review. Git reads `.gitattributes` from the branch, so this applies only to branches cut after this PR lands.

**Driver behaviour for the register.** `_rca` merges entry by entry. An entry that both sides rewrote differently still refuses. A class record (`P1`, `N-*` and the rest) that both sides changed also refuses. If two branches each add one instance, both raise `total` to the same number, and a key-by-key merge would accept that wrong count. Raw non-ASCII text is written back raw.

## Head

14ca7bebc4f74df8e1dc56c31d92d7f75f739d7e. Measured against `origin/main` 8d7903e6 on 2026-10-07.

## Mutation proof

Each of these four mutations of `tools/merge/ledger_merge.py` turns `python3 tools/merge/ledger_merge.py --self-test` red:

| mutation | check that fails |
|---|---|
| class-record refusal disabled (`if False and not all(`) | "bugclasses refuses: a class both sides added an instance to" |
| `ensure_ascii=True` | "bugclasses: raw non-ASCII text is written back raw" |
| register routed as `"sum"` | "bugclasses refuses: a class both sides added an instance to" |
| `RAW = set()` | "bugclasses: raw non-ASCII text is written back raw" |

Deleting the `.gitattributes` line fails ".gitattributes routes every ledger to the driver". With the tree unmutated, the self-test passes. `tests/entities.py` runs it.

## Null control

`dev/audit/rca/bugclasses/replay.sh` re-runs all 27 merges with a real `git merge`, in a standalone clone with the register routed to the driver:

- **Without the driver** (`without.log`): 4 conflicted. The other 23 merged and equal the recorded merge.
- **With the driver** (`with.log`): 0 conflicted. All 27 equal the recorded merge as JSON, including the resolution the seat committed in each of the four conflicts. Two of those four differ in bytes only because the two new entries are in the other order.

The 23 merges that were already clean stayed byte-equal. The driver did not pass by skipping: it resolved 16 merges itself, and in 6 others it fell back to a clean text merge. In those 6, a side was the register's pre-v2 format.

## Figures

- 27 merges, 4 conflicts without the driver, 0 with: `S=<scratch> bash dev/audit/rca/bugclasses/replay.sh without|with $(cat dev/audit/rca/bugclasses/merges.txt)`
- 217 file-conflicts across all refs since 2026-09-20, 4 of them on the register: `dev/audit/rca/bugclasses/conflicts_since_0920.tsv`
- 0.08 s per driver run on the real `dfe2bb79` inputs (3 runs); the whole self-test runs in 0.25 s
- `python3 tools/audit/fold_ledger.py check`: 0 violation(s), 100 rca entries
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED
- `PYTHONPATH=tests/hastub python tests/entities.py`: ALL 2202 ENTITY CHECKS PASSED
- `GATE_SCOPE=auto bash tests/run.sh`: `MODE: SCOPED -- 3 script(s) run, 30 scoped out`; 7 TEST SCRIPT(S) PASSED (entities, plan_view, card_drift and the run_always scripts)

## Red checks

none at authoring

## Forward-carry

From section 5a of the RCA: `tests/entities.py` had 11 conflicts and `tests/features.py` 16 in the same window. Whether those are the same tail-append shape is not established. No stage owns them. They are the next candidate if the cost recurs.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
