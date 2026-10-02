_Requested by **tvofi**_

Part of #1774.

Lands the report-only architecture score under `tools/audit/archscore/`. `score.py --diff` prints delta-S, the gate rises and the per-metric deltas for a diff; `tests/arch_score.py` re-runs the calibration and fails when a verdict moves or a red-team game re-opens; `tests/arch_score_head.py` fails when the score stops measuring today's tree. It is a report and a review trigger, never a target a seat is rewarded for moving: no budget raise, no gate on any other pull request, no weight change.

**Scope shrunk at current main.** #1838 (the PR that delivered #1738) put the clone, reach, writer, cycle and dead-member censuses in `tests/structure.py`, so the score reads those definitions (`vector.py` loads that file as a fresh module re-pointed at the tree measured) and does not carry the prototype's copies: `private_reach`, `import_cycles`, `dead_by_reachability`, `xmodule_duplication`, the `a1` probes and `metrics_v1`'s clone and cycle code are not landed. What lands is what `structure.py` has no row for (`ls tools/audit/archscore/metrics`): the hub and shared-object write censuses, the payload contract, entity families, the unused public surface, the coordinator footprint and the parameter count, on their own path-following role engine, which `structure.py`'s `CoordinatorRoles` (a yes/no on one value) cannot replace.

**Decisions.**
- The counters are applied to the loaded copy and never to `tests/structure.py`: C5 (a passthrough property reads as its private) adds reach sites and C3 (an effect-free statement does not split a clone) merges windows, so either in `structure.py` would move the ratchet's own rows. `python3 tests/structure.py` is unchanged by this diff.
- The planted cases anchor on the text of `7952d8f9` and assert each anchor occurs once, so the check measures a `git archive` of that commit, never the working tree. The calibration is therefore not selected by an integration change; `arch_score_head.py` is the one script that reads today's tree.
- Corpus history is stored as vectors (`calibration/corpus_vectors.json`, re-derivable with `calibrate.py --measure-corpus`); the planted cases and the red-team attempts are measured live on every run, which is what notices a metric change.
- `tools/audit/` is INERT, and this directory is read by the gate, so `tests/closure.py` gains `_is_archscore`: the directory's shape except its prose, not one line per file. It is a gate-file edit, so this diff is `MODE: FULL`.

## Head

f6b39ccd931a190372a4d4a46590a115aee9cc01

## Approval

Policy files in this diff: `.github/PULL_REQUEST_TEMPLATE.md`. tvofi adopted R3-1 (the optional "Architecture score" line) on 2026-09-29 (#1774). The template was at zero token headroom, so the line is paid for by deleting three sentences that restate another rule: the null-control sentence (`fixer.md` step 3 carries it), the forward-carry sentence (`finding-propagation.md` carries it) and the head-comparison sentence (`pr-contract` does it). Those three deletions are a template change the approving review is asked to see as such. `.github/CODEOWNERS` gains four lines (the frozen weights, their hash file, the pinned verdicts and `tests/arch_score.py`: a weight or a pinned verdict that moves is a policy change). The approving review at this head is GitHub's code-owner requirement, requested by the orchestrator.

## Mutation proof

The check's own mutation is the counters switched off (`ARCHSCORE_ABLATE`, which exists for this and for nothing else). `ARCHSCORE_ABLATE=C1,C2,C3,C4,C5,C6,C7,C11 python3 tests/arch_score.py` (round 1, before the `04b`-`04g` cases) failed 16 checks: `rt_01`, `rt_02`, `rt_03`, `rt_04`, `rt_05`, `rt_05b`, `rt_05c`, `rt_05d`, `rt_07`, `rt_08`, `rt_10`, `rt_11`, `rt_12`, `rt_12b` (each now reads IMPROVES, or `rt_05` WORSENS by a side effect), `a3_private_reach_fix` (IMPROVES, recorded NULL), and "no red-team attempt reads IMPROVES".

Counter by counter, each alone off (`ARCHSCORE_ABLATE=<C> python3 tools/audit/archscore/calibrate.py --only <ids>`, base measured under the same switch), the game reads:

| counter off | game | verdict | delta-S |
|---|---|---|---|
| C1 | `rt_01` all-`Any` TypedDict | IMPROVES, admissible | +50.86 |
| C2 | `rt_02` `object.__setattr__` on the hubs | IMPROVES | +29.17 |
| C2 | `rt_03` dunder spelling of shared writes | IMPROVES | +24.62 |
| C2 | `rt_10` `setattr` in `__init__` | IMPROVES | +0.05 |
| C3 | `rt_04` `id(N)` in every window | IMPROVES | +32.01 |
| C4 | `rt_05b` private methods to a mixin | IMPROVES | +62.49 |
| C4 | `rt_05c` / `rt_05d` the class behind a rename | IMPROVES | +103.62 |
| C5 | `a3_private_reach_fix` (a public passthrough for a private read) | IMPROVES | +0.02 |
| C6 | `rt_07` families declared into one-member families | IMPROVES | +10.93 |
| C7 | `rt_08` keep-alive registry | IMPROVES | +5.27 |
| C11 | `rt_11` keyword parameters into `**kw` | IMPROVES | +0.47 |
| C2, C6, C7 | `rt_12` all evasions in one change | IMPROVES | +70.04 |

No line of `custom_components/` changes, so `python3 tests/mutation_table.py --scope changed` has no site on this diff.

**Round 2.** B2 (C3 evaded by `pass`): `counters.is_noop` now covers `pass`, constant, name, attribute and pure-call expression statements and an `if` on a constant whose branches are all such. The reviewer's game (`pass` in the uncharged functions) is `rt_04c`; `rt_04b` is `pass` everywhere, `rt_04d` `...`, `rt_04e` `None`, `rt_04f` a string (structure's docstring filter already drops it, so it is a control), `rt_04g` `if False: pass`. With `ARCHSCORE_ABLATE=C3`, `rt_04c`, `rt_04d`, `rt_04e` and `rt_04g` each read IMPROVES, admissible, delta-S +14.15 (the reviewer's figure); with the widening they read NULL, and `rt_04b` WORSENS through `coord_footprint` as before. No pinned verdict moved from the round-2 re-run; the six new cases are recorded.

B1 (closure): the smoke path now loads `tests/structure.py` in-process, so the recorded closure of `tests/arch_score.py` lists it. A scratch commit changing only `DUP_WINDOW_STATEMENTS` in `tests/structure.py` (the reviewer's mutation) now selects `tests/arch_score.py` (`MODE: SCOPED`, 8 scripts, `scope.run` names it); before it did not.

Three counters are not alone what stops their game, and the body says so rather than credit them. `rt_13` (a hub handle behind a computed-name accessor) reads WORSENS with C2b off too, through a coordinator footprint rise (`coord_footprint`), so C2b is a second stop that would hold only if the accessor cost no logic statement. `rt_05` (the mixin move of every method) reads WORSENS with C4 off, through `public_unused`. `rt_06` (public `raw_<x>` properties) reads WORSENS with C5 off, through `dead_members`; C5 is what takes its delta-S from positive to not. `rt_09` (delete the away setback) reads WORSENS through `dead_members` +1 and nothing else: no structural counter exists, only the behaviour suite sees a deleted feature.

## Null control

The unmodified calibration: `python3 tests/arch_score.py` passes at this head, 135 checks, and `python3 tests/arch_score_head.py` passes. The rename null `rt_00` reads NULL; the pre-study's nulls `a1_N1`, `a1_N1b`, `a1_N1c`, `a1_N2`, `a1_N3` read NULL; `a1_N4` (a `const.X` namespace import) reads WORSENS, a recorded miss. The report on an unchanged tree is `score.py --diff origin/main`, which prints delta-S 0 NULL. The same instrument against the pre-study's pin prints a non-zero report, so it is not a constant.

**The pre-study's bar, and the one decision for tvofi.** PRE-STUDY section 6 asked that every case classify as it records, amended by the counters' one correction. Four verdicts moved, each listed with its cause in `tools/audit/archscore/ABOUT.md`: `97dc04f2` (that recorded correction), `ca937daa` and `a3_dead_by_reachability_fix` (sharing `structure.py`'s clone and dead-member definitions: copies where the prototype counted pairs, and a name two classes define keeps a member live), and `a3_private_reach_fix` (C5: the public property it swaps in is a passthrough). The alternative was to keep the prototype's own copy of each census and match section 6 exactly, at two definitions of each; the brief asked for one, so `expected.json` records the four. Weight sensitivity is unchanged: no weight halved, doubled or equalised moves a verdict.

## Figures

- A `tests/structure.py`-only mutation selects the calibration (the probe is a scratch worktree commit changing `DUP_WINDOW_STATEMENTS`; the instrument): `python3 tests/closure.py select --diff HEAD~1`
- Score vector of today's tree (the table of metrics at main `af7660c74`, 2026-10-02T13:06Z): `python3 tools/audit/archscore/vector.py .`
- Calibration totals and every verdict (77 of 103 labelled cases classify as labelled; 23 of 23 red-team attempts read NULL or inadmissible; none reads IMPROVES): `python3 tools/audit/archscore/calibrate.py --jobs 4`
- Frozen weights hash `2891a874ad476d7d761743ae7c47bae9779e150190aaf65f9a82e06ddd867978`, equal to the recorded one: `shasum -a 256 tools/audit/archscore/weights.json`
- The template at its caps (38 of 38 lines, 304 of 305 tokens): `node .claude/workflows/policy_lint.mjs --budgets`
- The same instrument against the pre-study's pin prints a non-zero report: `python3 tools/audit/archscore/score.py --diff 7952d8f9`
- The ratchet is unmoved: `python3 tests/structure.py`
- `tests/structure.py` is not in this diff (empty output; the control is `tests/closure.py`, which prints a stat line): `git diff origin/main...HEAD --stat -- tests/structure.py`
- The calibration's closure lists no `custom_components/` file, and the head script's lists them (the control): `python3 -c "import json; c = json.load(open('tests/closures.json'))['closures']; print([sum(f.startswith('custom_components/') for f in c[s]) for s in ('tests/arch_score.py', 'tests/arch_score_head.py')])"`
- No new orphan file: `python3 -c "import sys; sys.path.insert(0, 'tests'); import closure; print(closure.orphan_files())"`
- Gate mode of this diff (`MODE: FULL`, reason: `tests/closure.py` changes the gate itself): `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`
- Cost of the full check, about 9 minutes at 256 percent CPU on a loaded seat machine with four workers (CI's figure is the one to use): `time python3 tests/arch_score.py`
- `policy_lint` on a clean `origin/main` checkout reads the same `[required-contexts]` errors as on this head: `node .claude/workflows/policy_lint.mjs`
- The scopes the gate named and this seat could not run: `tests/entities.py` and every numpy lane; the gate is CI's.

## Red checks

none on this branch. `prepr.sh` refuses three steps locally (`policy_lint`, `mutants`, `field coverage`) because each reads the live `main-protect-checks` ruleset through `gh` and finds `bypass_actors` that `.claude/workflows/fixtures/required-contexts.json` does not record; a clean detached checkout of `origin/main` refuses `policy_lint` the same way, with the same `[required-contexts]` errors, so the drift is main's and not this diff's (the cheaper detector exists: `policy_lint.mjs` itself). The ruleset record is the orchestrator's and tvofi's to re-record.

## Forward-carry

`docs/plan-2026-09-open-issues.md`: the rows for #1774 and #1775 now say the clone census is `duplication_copies` (copies, not the retired pair count), measured through `score.py --diff` at the stage's own merge base, and that four calibration verdicts moved from the pre-study. The roster briefs of R9-EG-A2, R9-EG-A3 and R9-EG-A4 (and the EG-B stages that cite a prototype command) still name the prototype's vector commands and `dup_pairs_v1` targets; they are the orchestrator's to carry before this merges, and are named here so the reviewer checks them: the in-tree command is `python3 tools/audit/archscore/score.py --diff`, the clone target is re-derived, and a gate rise on `reflective_writes`, `computed_attr_access`, `family_orphan_overrides` or `unread_private_globals` is a tripwire to explain, not a metric to improve.

## Friction

- `fixer.md`: stale: step 5 says run what `scope.run` names; any diff that edits `tests/closure.py` or `run.sh` is `MODE: FULL`, and this seat has no numpy, so the whole gate is CI's.
- `ratchet-budgets.md`: cost: the template sat at zero token headroom, so one optional line cost three deleted sentences.
- `brief-citations.md`: cost: a new `README.md` under `tools/audit/` was named by the basename fallback of `tools/audit/README.md`'s own citation and failed `named-docs`; the prose is `ABOUT.md` for that reason.
