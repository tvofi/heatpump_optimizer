R10-RCA-GATE-BUSY-DEFER-2, the root-cause seat for R10-HOTFIX-GATE-BUSY-DEFER. It ran beside that fixer (topic r10-gate-busy-defer-2) and did not edit `tools/ci/`. Part of #201. The analysis is `dev/audit/rca/r10-gate-busy-defer-2.md`, indexed in `dev/audit/config/bugclasses.json` as `_rca.R10-RCA-GATE-BUSY-DEFER-2`.

- **Cause.** ci.yml restores `tools/ci/*.py` from the payload's `pull_request.base.sha`, and a job re-run replays that payload. `refresh` and the sweep re-judge through the job-rerun API. So every re-run of a run created before #3246 merged (`355d9965`) ran the pre-fix `gate.py`. All six mutual-deferral gates in the brief's evidence ran such a copy: #3261's pair (attempt 8, pinned `28482ece`), #3265's (attempt 4, `f2a01514`) and #3255's (attempts 5 and 4, `80016a71`). Replayed through main's `gate.py`, the listings GitHub served decide every pair.
- **#3263 is not the race.** Run 42338396358's 2-second red ran the fixed program (pinned `294a880d`). It is C3's designed at-once deferral to its unstarted code run, and every program copy gives the same verdict on its listing.
- **Process state (c).** The harnesses import one `tools/ci` copy per scene, and the mutation proof mutates that copy. The review read the live reds' `programs restored from b36679ce` lines and dismissed them "until this fix lands". Landing does not reach a run pinned when it was created.
- **Cost test: passes** for the proposed countermeasure, under 0.01 s of compare per re-run. Against it: 21 deferral reds on 7 PRs from stale-pinned gates in the 65 minutes after the merge, and 3 gate hotfixes in 7 days.
- **Countermeasure.** Built: `dev/audit/harnesses/r10_rca_gate_busy_defer_2.py`, which replays recorded live run and job listings through a chosen program copy and has a live `census` arm. Proposed, and not built here because it edits `tools/ci/`: a re-run of a gate whose pinned programs differ from the base tip becomes a ci.yml dispatch (`pr=N base=<base>`).

## Head

`4839ac959f690730d966a47e13bc191f3947b216`, branch `fix/r10-rca-gate-busy-defer-2`, a draft PR. It moved from `fbf55e8ffc184ca5732778284770b48a316c78a5` by one commit, `4839ac959 ci: merge main`, a merge of origin/main `ca60d4e4e` (PR #3261, the R10-RCA-PROCESS-WORKER-HANG RCA). `git log fbf55e8f..4839ac95` lists 13 commits: that merge plus the 12 commits of #3261 branch history it brought in (`af75c8822`, `a65397f3c`, `5c246022a`, `5dbff79de`, `3a8fb9857`, `95ae9d26d`, `eb7102637`, `04f41926f`, `f914e1d9c`, `e17fadc17`, `61187afe6`, `ca60d4e4e`). No commit on this branch's own work changed. The three-dot diff (`git diff $(git merge-base origin/main 4839ac95)...4839ac95`, merge-base `ca60d4e4`) is still the same 6 files, 10922 insertions: the harness and its fixture, the RCA document, the `_rca` entry, the harness's `tests/closures.json` INERT READS entry (`ci_predict.py --apply-inert`) and `dev/programme/delivery/3278.md`. The two-dot `fbf55e8f 4839ac95` diff (6 files, 438 insertions) is main's #3261 only. Every figure below was re-taken at this head; no code is changed or pushed in this re-take.

## Mutation proof

This PR adds no production line. The detector it adds is the `replay` arm, and it is proven against real program copies and two mutants of this tree's `gate.py`:

- Red on the defect: `replay --ci` on a `git archive` export of each pinned base the live gates ran (`28482ece`, `f2a01514`, `80016a71`) gives rc 1 and `RESULT replay ... deadlocks=yes`, with `3261-pair: DEADLOCK`, `3265-pair: DEADLOCK` and `3255-pair: DEADLOCK`. The deferral ids are the ones the live logs print.
- Green on the fix: rc 0 and `deadlocks=no`, with all three pairs `DECIDED`, at `294a880d` and at this head's `tools/ci` (re-run at 4839ac95).
- M17 (busy()'s later-started-gate tie-break deleted), on an export of this head: rc 1, with `3261-pair: HALF-DEFERRED`, `3265-pair: DEADLOCK` and `3255-pair: DEADLOCK`. Taken at the prior head `7dba286d`; `tools/ci` is not in the 4839ac95 merge's diff, so the program under the mutant is unchanged.
- M24 (`all` to `any` in judge()'s C3 wait) survives the arm, rc 0. No recorded scene is the mixed prelude/gate scene that M24 opens. `gate.py --self-test`'s named case still pins it, and the RCA says so.

## Null control

- The three C3 scenes (#3263, #3261 at `61187afe`, #3241) read `C3-AT-ONCE` with naps 0 under every program copy, so the arm does not count the designed red as the race.
- The arm refuses, and does not go green, on a fixture whose pair gates did not overlap in time or whose gate never started.
- `census`: the fixed-pin row holds 3 gates, all C3 deferrals, so it is not empty and it holds no mutual deferral. Gates with no `programs restored from` line are counted `unpinned`, not stale.
- The compare the countermeasure would run, `git diff --quiet 28482ece 294a880d -- <restored paths>`, gives rc 1. The same sha on both sides gives rc 0.

## Figures

- Pins of the 9 recorded gates: `python3 dev/audit/harnesses/r10_rca_gate_busy_defer_2.py pins` prints `RESULT pins gates=9 stale=6` at 4839ac95. The 6 are the three pairs, and each lacks `355d9965`.
- Replay: `python3 -I dev/audit/harnesses/r10_rca_gate_busy_defer_2.py replay --ci <export>/tools/ci`, where the export is `git archive <sha> tools/ci tools/pr`. rc 1 at `28482ece`, `f2a01514` and `80016a71`. rc 0 at `294a880d`, and at this head with no `--ci`.
- Fixture: `dev/audit/harnesses/r10_rca_gate_busy_defer_2.json`, sha1 f926d6a67b5582c172f49cb436a09e7ff7b63b70 (`sha1sum` at 4839ac95), written by the harness's `record` arm at 2026-11-07T04:47:56Z.
- Census: `python3 dev/audit/harnesses/r10_rca_gate_busy_defer_2.py census --since 2026-11-07T03:45:14Z --until 2026-11-07T04:50:21Z`. It counts every `gate` job that started in the window, by whether its pinned sha carries the fix:
  - stale: `gates=46 {'defer': 21, 'other-red': 1, 'pass': 24}`, 7 PRs, `reruns=36`, `defer_job_s=685`
  - fixed: `gates=3 {'defer': 3}`, `reruns=0`
  - unpinned: `gates=5`, 4 cancelled and 1 other-red, none a deferral (re-run at 4839ac95: the counts are the recorded ones)
- Recurrence: `git log --first-parent --since=2026-10-31 4839ac95 -- tools/ci/gate.py tools/ci/prelude.py` returns 3 merges (#3205, #3230, #3246). Over every program ci.yml restores (`git log --first-parent --since=2026-10-23 4839ac95 -- 'tools/ci/*.py' tools/pr/codeql_scope.py tests/closure.py tools/pr/cancel_superseded.py`), it returns 27 commits. Main has since merged #3276 on `gate.py`; it is not in this head.
- Ledger: `python3 tools/audit/fold_ledger.py check` prints `0 violation(s)` at 4839ac95, with 135 rca entries (48 classes, 755 instances).
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and that script is `tests/entities.py`.
- Entities and ratchet at 4839ac95: `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2642 ENTITY CHECKS PASSED`. `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- Seam enumeration (fixer step 8). Rule: the `git checkout "$PINNED" --` lines in `.github/workflows/ci.yml`, each naming the programs a run restores from its payload base. Each returned seam (prelude/gate: `tools/ci/*.py`, `tools/pr/codeql_scope.py`, `tests/closure.py`; cancel-superseded: `tools/pr/cancel_superseded.py`; refresh: `tools/ci/*.py`) is in the class, and it is dispositioned in RCA section 3 as open, covered by the proposed countermeasure 5.2.

## Red checks

Read with `filter=all` across all pages for every head of the PR that carries check runs (`4839ac95` 134 runs, `fbf55e8f` 160, `dc226703` 27; `175d059a`, `fccc86af` and `7dba286d` carry none). At the head `4839ac95` no check is red: its latest attempt of every check concluded green. The concluded reds at the head and the ones a later attempt cleared:

- At `4839ac95`, cleared by a later green attempt:
  - `governance / instrument-self-tests` cancelled (run 42353487847, 08:11:47Z to 08:42:02Z, the 30-minute timeout; class R10-HOTFIX-SELFTEST-TIMEOUT, cure R10-PROCESS-SLIM #3245). Re-run green at 09:25:53Z.
  - `gate`, `prelude` and `refresh` cancelled (run 42353340570, attempt 1, 08:01:37Z to 08:02:05Z): whole-attempt cancel by the superseding dispatch run 42353487847, not a verdict. Attempt 3 concluded green: `gate` success 10:14:24Z, `prelude` 09:15:59Z, `refresh` 09:12:55Z, `governance / instrument-self-tests` success 09:19:48Z.
  - The dispatched run 42353487847 (`workflow_dispatch`, attempt 2) concluded success: `gate` success 10:15:04Z.
- At `fbf55e8f`, cleared by a later green attempt (the head moved after them):
  - `gate` failure x4, all `FAIL run(s) [...] at this head are still being judged; their gate decides`, the edit-run mutual deferral of R10-HOTFIX-GATE-BUSY-DEFER, run on the pre-fix program pinned to `be813ecd4924865b75489f12c56600e9432d5727` (log of job 128341650362): jobs 128327752449 (06:39:39Z) and 128341892100 (07:40:50Z) in run 42345749170, and jobs 128329201600 (06:40:25Z) and 128341650362 (07:37:44Z) in run 42346332344. Answer: the cause is this PR's own analysis; the cure is that fix. Runs 42345749170 and 42346332344 concluded success (attempt 3): `gate` success 07:49:48Z and 07:43:30Z.
  - Whole-run cancel of code run 42345748044 (attempt 2) at 06:40:34Z to 06:40:37Z: `gate` (job 128330010434), `tests / claims-autofix`, `tests / closures-autofix`, `tests / ci-ratchet`, `tests / coverage-ratchet`, `tests / graders-head-copy` and `tests / lane-proofs` cancelled, and in-flight `tests / fast (3.14)`, `tests / closures` and `tests / coverage` cancelled with them, by the re-run that replaced the attempt. Answer: a whole-run cancel is a supersede, not a verdict. The re-run attempt then ran: `gate` success 07:34:35Z (job 128341175635), `tests / fast (3.14)` success 07:05:13Z.
  - `governance / instrument-self-tests` cancelled x2 in run 42345748044 (job 128325095603, 06:20:25Z to 06:40:26Z, cut by the whole-run cancel; job 128330399020, 06:46:02Z to 07:16:19Z, the 30-minute timeout): R10-HOTFIX-SELFTEST-TIMEOUT, cure R10-PROCESS-SLIM #3245. Neither attempt concluded green at `fbf55e8f`, and run 42345748044 itself concluded `cancelled`. The PR head then moved to `4839ac95`, whose code runs concluded success (above); the red at `fbf55e8f` was cleared by the new head, not by a green attempt.
- At `dc226703`, all cancelled by the next push: `cancel-superseded`, `prelude`, `refresh` and `gate` of runs 42345729241 and 42345732459 (06:09:21Z to 06:15:09Z). Answer: superseded by the push of `fbf55e8f`.
- Open `code-scanning alert`: none. `CodeQL` concluded success at the head.

## Forward-carry

- To the R10-HOTFIX-GATE-BUSY-DEFER fixer (topic r10-gate-busy-defer-2): #3263's red is C3's designed at-once deferral under the fixed program. The six pair reds never ran main's busy(). Re-prove any gate change with `replay --ci <export>` (dev/audit/rca/r10-gate-busy-defer-2.md, Carries). This seat may push no roster or brief ref, so the orchestrator relays it to that group's brief. Carry: #201
- To the orchestrator: the stale-pin re-run countermeasure in `refresh()` and `sweep.py` (RCA 5.2) is a `tools/ci` change for the gate's owner. Until it lands, after any pinned-program merge, dispatch ci.yml (`pr=N base=main`) for each PR whose latest gate is a stale-pinned red. A re-run does not clear it (RCA 5.3). Carry: #201

## Friction

- PROMPT.md: contradiction: the payload pins git identity `seat` and the brief says `hpo-fixer` and never `seat`; `hpo-fixer` was used, set in the environment because the exported toolchain sets GIT_AUTHOR_NAME/GIT_COMMITTER_NAME to `seat`. Carry: dismissed: identity settled per brief, as on #3246
- frugal-routing-hook: cost: an inline-search budget of 5 per prompt blocked `tests/entities.py` and `structure.py` runs as "search ops", forcing delegations for single reads. Carry: dismissed: seat-harness configuration, outside this repository
