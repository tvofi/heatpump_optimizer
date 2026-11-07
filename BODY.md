R10-RCA-GATE-BUSY-DEFER-2, the root-cause seat for R10-HOTFIX-GATE-BUSY-DEFER. It ran beside that fixer (topic r10-gate-busy-defer-2) and did not edit `tools/ci/`. Part of #201. The analysis is `dev/audit/rca/r10-gate-busy-defer-2.md`, indexed in `dev/audit/config/bugclasses.json` as `_rca.R10-RCA-GATE-BUSY-DEFER-2`.

- **Cause.** ci.yml restores `tools/ci/*.py` from the payload's `pull_request.base.sha`, and a job re-run replays that payload. `refresh` and the sweep re-judge through the job-rerun API. So every re-run of a run created before #3246 merged (`355d9965`) ran the pre-fix `gate.py`. All six mutual-deferral gates in the brief's evidence ran such a copy: #3261's pair (attempt 8, pinned `28482ece`), #3265's (attempt 4, `f2a01514`) and #3255's (attempts 5 and 4, `80016a71`). Replayed through main's `gate.py`, the listings GitHub served decide every pair.
- **#3263 is not the race.** Run 42338396358's 2-second red ran the fixed program (pinned `294a880d`). It is C3's designed at-once deferral to its unstarted code run, and every program copy gives the same verdict on its listing.
- **Process state (c).** The harnesses import one `tools/ci` copy per scene, and the mutation proof mutates that copy. The review read the live reds' `programs restored from b36679ce` lines and dismissed them "until this fix lands". Landing does not reach a run pinned when it was created.
- **Cost test: passes** for the proposed countermeasure, under 0.01 s of compare per re-run. Against it: 21 deferral reds on 7 PRs from stale-pinned gates in the 65 minutes after the merge, and 3 gate hotfixes in 7 days.
- **Countermeasure.** Built: `dev/audit/harnesses/r10_rca_gate_busy_defer_2.py`, which replays recorded live run and job listings through a chosen program copy and has a live `census` arm. Proposed, and not built here because it edits `tools/ci/`: a re-run of a gate whose pinned programs differ from the base tip becomes a ci.yml dispatch (`pr=N base=<base>`).

## Head

`7dba286df3b9324badaa5b1b0e2f99c43751f59f`, branch `fix/r10-rca-gate-busy-defer-2`, cut from origin/main `294a880dae608502b62055775e34a5db93217b98`. origin/main was still `294a880d` at the final `tools/pr/prepr.sh` run, so no merge and no second run were owed. The three-dot diff adds the harness and its fixture, the RCA document, the `_rca` entry and the harness's `tests/closures.json` INERT READS entry (`ci_predict.py --apply-inert`).

## Mutation proof

This PR adds no production line. The detector it adds is the `replay` arm, and it is proven against real program copies and two mutants of this tree's `gate.py`:

- Red on the defect: `replay --ci` on a `git archive` export of each pinned base the live gates ran (`28482ece`, `f2a01514`, `80016a71`) gives rc 1, with `3261-pair: DEADLOCK`, `3265-pair: DEADLOCK` and `3255-pair: DEADLOCK`. The deferral ids are the ones the live logs print.
- Green on the fix: rc 0, with all three pairs `DECIDED`, at `294a880d` and at this head's `tools/ci`.
- M17 (busy()'s later-started-gate tie-break deleted), on an export of this head: rc 1, with `3261-pair: HALF-DEFERRED`, `3265-pair: DEADLOCK` and `3255-pair: DEADLOCK`.
- M24 (`all` to `any` in judge()'s C3 wait) survives the arm, rc 0. No recorded scene is the mixed prelude/gate scene that M24 opens. `gate.py --self-test`'s named case still pins it, and the RCA says so.

## Null control

- The three C3 scenes (#3263, #3261 at `61187afe`, #3241) read `C3-AT-ONCE` with naps 0 under every program copy, so the arm does not count the designed red as the race.
- The arm refuses, and does not go green, on a fixture whose pair gates did not overlap in time or whose gate never started.
- `census`: the fixed-pin row holds 3 gates, all C3 deferrals, so it is not empty and it holds no mutual deferral. Gates with no `programs restored from` line are counted `unpinned` (5), not stale.
- The compare the countermeasure would run, `git diff --quiet 28482ece 294a880d -- <restored paths>`, gives rc 1. The same sha on both sides gives rc 0.

## Figures

- Pins of the 9 recorded gates: `python3 dev/audit/harnesses/r10_rca_gate_busy_defer_2.py pins` prints `RESULT pins gates=9 stale=6`. The 6 are the three pairs, and each lacks `355d9965`.
- Replay: `python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay --ci <export>/tools/ci`, where the export is `git archive <sha> tools/ci tools/pr`. rc 1 at `28482ece`, `f2a01514` and `80016a71`. rc 0 at `294a880d`, and at this head with no `--ci`.
- Fixture: `dev/audit/harnesses/r10_rca_gate_busy_defer_2.json`, sha1 f926d6a67b5582c172f49cb436a09e7ff7b63b70, written by the harness's `record` arm at 2026-11-07T04:47:56Z.
- Census: `python3 dev/audit/harnesses/r10_rca_gate_busy_defer_2.py census --since 2026-11-07T03:45:14Z --until 2026-11-07T04:50:21Z`. It counts every `gate` job that started in the window, by whether its pinned sha carries the fix:
  - stale: `gates=46 {'defer': 21, 'other-red': 1, 'pass': 24}`, 7 PRs, `reruns=36`, `defer_job_s=685`
  - fixed: `gates=3 {'defer': 3}`, `reruns=0`
  - unpinned: `gates=5`
- Recurrence: `git log --first-parent --since=2026-10-31 origin/main -- tools/ci/gate.py tools/ci/prelude.py` returns 3 merges (#3205, #3230, #3246). Over every program ci.yml restores, the same rule returns 27 commits since 2026-10-23.
- Ledger: `python3 tools/audit/fold_ledger.py check` prints `0 violation(s)`, 134 rca entries.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run`, and that script is `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py`: prints `ALL 2640 ENTITY CHECKS PASSED`. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Seam enumeration (fixer step 8). Rule: the `git checkout "$PINNED" --` lines in `.github/workflows/ci.yml`, each naming the programs a run restores from its payload base. Each returned seam (prelude/gate: `tools/ci/*.py`, `tools/pr/codeql_scope.py`, `tests/closure.py`; cancel-superseded: `tools/pr/cancel_superseded.py`; refresh: `tools/ci/*.py`) is in the class, and it is dispositioned in RCA section 3 as open, covered by the proposed countermeasure 5.2.

## Red checks

none. No check has run on this branch, because the orchestrator opens the PR. The branch adds no production line.

## Forward-carry

- To the R10-HOTFIX-GATE-BUSY-DEFER fixer (topic r10-gate-busy-defer-2): #3263's red is C3's designed at-once deferral under the fixed program. The six pair reds never ran main's busy(). Re-prove any gate change with `replay --ci <export>` (dev/audit/rca/r10-gate-busy-defer-2.md, Carries). This seat may push no roster or brief ref, so the orchestrator relays it to that group's brief. Carry: #201
- To the orchestrator: the stale-pin re-run countermeasure in `refresh()` and `sweep.py` (RCA 5.2) is a `tools/ci` change for the gate's owner. Until it lands, after any pinned-program merge, dispatch ci.yml (`pr=N base=main`) for each PR whose latest gate is a stale-pinned red. A re-run does not clear it (RCA 5.3). Carry: #201

## Friction

- PROMPT.md: contradiction: the payload pins git identity `seat` and the brief says `hpo-fixer` and never `seat`; `hpo-fixer` was used, set in the environment because the exported toolchain sets GIT_AUTHOR_NAME/GIT_COMMITTER_NAME to `seat`. Carry: dismissed: identity settled per brief, as on #3246
- frugal-routing-hook: cost: an inline-search budget of 5 per prompt blocked `tests/entities.py` and `structure.py` runs as "search ops", forcing delegations for single reads. Carry: dismissed: seat-harness configuration, outside this repository
