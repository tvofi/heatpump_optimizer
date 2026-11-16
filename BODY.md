R11-PRE-ROUND-METRICS, part 2 of the group (topic r11-pre-round-metrics-p2): the convergence record of process cards P7 and L1 and decision 0018 sections 2 and 4, built once, with its enumerator `tools/audit/seat/loop_ledger.py`.

Seven roster fields, written only through `roster_edit.py set-field` and refused outside `roster_lib.convergence_why`'s vocabulary: `found_by` (a finder dimension `D<n>`, `reviewer`, `ci-main`, `owner`, `outside`), `owned_by` (`D<n>` or `none`), `caused_by` (`{cause, rca}`: a pull request `#<n>`, another roster group, `external` or `original`, with `rca` one of the group's own `rca` records under `dev/audit/rca/`, so the cause is the root-cause seat's and never the fixer's), `family` (a class of `dev/audit/config/bugclasses.json`), `cm_kind` (card L1's six words), `parent` and `follows` (other roster groups). `loop_ledger.py` reads them from every `wave-r<N>-groups.json` at the reader ref and prints, per round (each roster) and per ISO week of roster entry (`git blame` of the group's `"group":` line), `escapes` by found_by and by owned_by, `injected`, `refix` (a re-report naming the fix it follows) and `loop` (countermeasures by family and cm_kind, k children per countermeasure, groups per generation and each generation's ratio). Which group owes which field is `owed()`: an escape (scorecard line E's two sets, `scorecard.escape_sets`, which `loop_ledger` imports: one definition) owes found_by, owned_by and caused_by; any other hotfix group found_by and caused_by (card P7); a group with an `rca` record caused_by, family and cm_kind (card L1). A read whose owing groups are not all recorded prints `unread (k of n ...)` with the names, never a partial value (0018's NO-READ rule for a partial ledger). `scorecard.py`'s line E gains the owning-dimension split through `loop_ledger.owned_split`, imported inside `scorecard.owned_split` so the scorecard's mutant copies, which run without their siblings, still load (card P7's "the scorecard splits escapes by owning dimension per round": the scorecard's roster is the round's). The enumerator is code-owned in `.github/CODEOWNERS` (carry 0's rule, carried to this part by its text), self-tested in `instrument-self-tests` (step `loop-ledger`), and documented in `tools/audit/seat/instruments/loop_ledger.py.md`.

Also fixed, in a file this diff touches: `roster_lib._replan_production` joined `tools/plan/replan.py` onto `Path(__file__).parents[2]`, which is the `tools/` directory itself, so the file it loaded never existed, it always failed and returned False, and `group_class` never answered `production` for a group without a `class` (ci_priority's tier 1 reads it). Its self-test check accepted either answer. It now loads the repository's `tools/plan/replan.py`, and the check pins `production` for a lane-less group and `instrument` for one owning only `tools/` files.

Carry 5: built: found-by and owning dimension per escape (`none` a value), the cause named through the root-cause seat's record, and the re-report naming the fix it follows (`follows`, read as `refix`); the per-step denominator and the examining pass over a late merge are cards C1 and C2. Carry 6 is carry 5's text without its source line and is folded into carry 5. Carry 7: built as cards C3 to C5 qualify (the four fields, the closed vocabularies, the per-round and per-week enumerator). Carry 8: built (found_by and caused_by on every hotfix and outside group, the scorecard's E split by owning dimension per round), with the convergence record of carry 5, as one mechanism. Carries 0 to 4 belong to the group's other parts and are not answered here. Carry: R11-PRE-ROUND-METRICS

## Cards

Definitions this part cannot meet as written, returned rather than bent:

- **C1 the per-step denominator has no record to read.** Carry 5 owes "the per-step denominator with an off-cadence dimension reading 0". No tracked record holds a finder step's examined count and universe (`git grep -n -i "denominator\|universe" -- .claude/skills/audit-find dev/governance/roles/COMMON.md dev/audit/README.md` returns only `dev/audit/README.md`'s line naming R11-INTAKE-R10-RESIDUE as the owner of the denominator rule). The read needs the finder's report to carry the step's universe command and examined count first; the ledger then reads it. Owner or orchestrator choice: keep that with R11-INTAKE-R10-RESIDUE's brief rewrite, or define the step record here in a later part.
- **C2 the examining pass over a late merge** is `unexamined`'s read (0018 section 2), which 0018 assigns to R11-PRE-ROUND-METRICS from the roster's group kinds; no record says which finder pass examined which merge, so it is not built here.
- **C3 the fields sit on the roster group, not on the RCA record and the triage ACCEPT.** Card L1 puts `caused_by`, `family` and `cm_kind` on an RCA record and a triage ACCEPT. Both become a roster group (an RCA's countermeasure group lists it in `rca`; an ACCEPT is landed by `append-group`), and the group is where the scorecard, the planner and this ledger already read; a second copy in Markdown would be a parallel record. `caused_by` is tied to the RCA by requiring its `rca` id to be one of the group's own records. If the owner wants the fields on the RCA file itself, the ledger reads them through the group's `rca` link.
- **C4 `family` is a bug class.** Card L1 names "the symptom family" with a closed vocabulary but no list; the only tracked closed list of defect families is `dev/audit/config/bugclasses.json`, so `family` is one of its keys. A family that is no class needs a class first.
- **C5 the prototype was not re-measured.** Card L1 cites the prototype under `$HPO_STATE_DIR/s14/seat/loop-study-1114/data/`; that variable is unset in this container and the scripts are not in the tree, so no prototype figure is reproduced. At the head every round's ledger reads unread (no group carries the fields yet: `## Figures`), which is the honest baseline: the figures exist once the orchestrator sets the fields.
- **C6 the reviewer's `caused_by` check and the fixer rule are policy.** Card L1's mitigation ("the fix reviewer checks `caused_by`") and the audit's row a6 (`fixer.md`) change role contracts; they need the owner's approval and are not drafted here. Until then `set-field`'s refusal of a `caused_by` without the group's own RCA record is the only check.

## Head

acf0b725788505349f8908003ce5b6ea2bac4a9b, measured at origin/main 6aa7ddc71216c4bc357db0097839ce40ff94e263, 2026-11-16T02:39:30Z.

## Mutation proof

Each mutant applied to a detached copy of the head, the self-test run, then restored:

- `roster_lib._replan_production`: `_ROOT / "tools"` to `_ROOT.parent / "tools"` (the old wrong path's shape): `FAIL P268 readers: group_class is the class when present, lane-derived only when absent`; at the merge base the same check passes on the broken path, which is the defect.
- `convergence_why`: dropping `rca not in (group.get("rca") or []) or` (the root-cause-seat arm): the check `convergence: caused_by needs one of the group's own rca records` fails (the refusal is gone: `TypeError` on the `None` it now returns).
- `loop_ledger.reads`: the refix partial-ledger arm (`if gap:` to `if False:`): four `FAIL` lines, `... and refix, which needs the whole ledger, is unread too` (three) and `a non-escape hotfix owes found_by`.
- `loop_ledger.reads`: the loop arm's gap emptied (`gap = []`): the self-test exits non-zero (`KeyError: 'family'` on the dropped-field case).
- `loop_ledger.report`: the per-name dedupe replaced by every roster's groups: `FAIL a group carried into a later roster is counted once in its week`.
- `loop_ledger.owed`: the hotfix arm disabled: `FAIL a non-escape hotfix owes found_by` and `FAIL owed: a plain group owes nothing; a machinery hotfix owes no owned_by`.
- `scorecard.line_escapes`: the split dropped: `FAIL E split: unread, naming the count, ...` and `FAIL E split: by owning dimension once every escape records one`.

Diff mutants (`fixer.md` step 2): `MUTANT_CMD="python3 -I tools/audit/seat/loop_ledger.py --self-test" PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` (the draw falls in `loop_ledger.py`) prints one `SURVIVED`: `loop_ledger.py:59 CONST_SWAP` (`sys.path.insert(1, ...)`), equivalent: the script's own directory is the only place `roster_lib` and `scorecard` are found, at either position. The run before it also printed `SHOWN = 6`, the ellipsis bound `len(gap) >= SHOWN` and the generation ladder's `max(gens, default=-2)`: the first two are killed by the case `an unrecorded list names its first five groups, and an ellipsis only past five`, and the third has no site left (the ladder is built only over a non-empty count).

## Null control

`python3 -I tools/audit/seat/loop_ledger.py --dir <empty directory>` prints `loop_ledger unread (no wave-r<N>-groups.json roster)` and no value (self-test case). A fully recorded fixture roster prints every read with values, and dropping one field from one group turns that read, and the whole-ledger `refix`, unread naming the group, the other reads unchanged (self-test cases, one per dropped field). A round with no escape splits none in scorecard line E (`by owning dimension {}`). Every closed word is admitted and its neighbour refused (`roster_lib` and `roster_edit` self-tests).

## Figures

<!-- figure-block: scope-line mb=921214bf4246338c1a83fbc5269eaa0bfe91b7d5 head=acf0b725788505349f8908003ce5b6ea2bac4a9b -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->
- Self-tests at the head: `python3 -I tools/audit/seat/loop_ledger.py --self-test` ends `loop_ledger self-test: 0 failed`; `python3 tools/audit/seat/roster_lib.py --self-test` ends `roster_lib self-test: 95 checks, 0 failed`; `python3 tools/audit/seat/roster_edit.py --self-test` ends `roster_edit self-test: 314 checks, 0 failed`; `python3 -I tools/audit/seat/scorecard_selftest.py` ends `scorecard self-test: ok (without mutants)`.
- `python3 -I tools/audit/seat/loop_ledger.py --repo .` at the head, reading `origin/handoff/audit-r10-roster` (roster_lib's default reader ref), prints every round's `escapes`, `injected`, `refix` and `loop` as `unread`, each naming its owing groups, none recorded: no roster group carries a convergence field yet. Control: `git grep -c '"found_by"\|"owned_by"\|"cm_kind"' -- dev/programme/rosters/` prints nothing, so an all-unread ledger is the right answer and any value would be a guess.
- `group_class({"group": "X"})` (a lane-less group) answers `production` at the head and `instrument` at the merge base (`python3 -c` over `roster_lib` at each); at the merge base `_replan_production`'s path has `tools` twice and no such file exists.
- `python3 tools/audit/archscore/score.py --diff origin/main HEAD` prints `Architecture score: dS +0.0000 NULL`. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- `python3 -I tools/ci/selftest_scope.py record` re-recorded the read sets of `loop-ledger` and of the 38 steps whose committed files held `roster_lib.py`, `roster_edit.py` or `scorecard.py` (rule: `jq` over `tools/ci/selftest_closures.json`'s `steps` for those three paths), unioned into the committed table with `union_record` (roster_lib now reads `tools/plan/replan.py`, the bug classes, the dimension briefs and the RCA directory). In that 39-step run `roster-editor` and `prepr` failed: `prepr` on its throwaway-git null control, which this diff's first self-test (a raw `git init`) did turn red and which is fixed (`python3 -I tests/throwaway_git.py --check` prints `0 raw git init or clone site(s) refused`); `roster-editor`, re-recorded alone with `loop-ledger`, passes (`0 failed []`), and `python3 -I tools/audit/seat/roster_edit.py --self-test` passes untraced.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL` (`tools/ci/selftest_closures.json` is a gate file), left to CI; `python3 -I tools/ci/selftest_scope.py select --base origin/main` prints `MODE: FULL` (`governance.yml` changed).
- `python3 tools/pr/ci_predict.py --base origin/main --apply-inert` wrote `tests/entities.py`'s inert read of `loop_ledger.py`, then predicted no red.

## Red checks

none

## Forward-carry

none

## Friction

none
