R10-HOTFIX-GATE-BUSY-DEFER (reopened), topic r10-gate-busy-defer-2: an edit gate that defers to a sibling run at its head no longer publishes the deferral at once, and no two runs at a head wait on each other.

**Cause.** `prelude.judging()` read the units a run owes from its title's workset. A deferring edit run (C3, `prelude.defer_to`) never expands `pr-contract`: GitHub lists the caller under its bare name `pr-contract`, completed `skipped`, and never lists `pr-contract / pr-contract`. So judging() read every deferring run as busy, to every gate and prelude at its head, forever. #3246 dodged the resulting prelude/gate cycle with an at-once bound in `gate.judge` (the `deferring(...)` clause). That bound is #3263's red: edit run 42338396358 published `FAIL run(s) [42338396871] at this head are still being judged; their gate decides` 2 s into its judge step, beside code run 42338396871 still in progress.

**Fix.** `prelude.judging()` reads a unit whose caller job is listed completed under the unit's bare name as one the run never ran, so it adds no source. A deferring run is then judging once its gate is listed, and nothing waits on it. With the cycle gone, the at-once bound and `deferring()` are deleted, and a deferring edit gate waits on its sibling bounded by `GATE_WAIT_MAX_S`, like every other gate. The order is total:
- a code run's prelude waits on nothing;
- any other prelude waits only on an earlier run, or a code run, that is not judging;
- a gate waits only on runs that are not judging, past `busy()`'s id tie-break.

No judging run waits on a non-judging one, so no cycle closes. The tie-break stays, for a started gate whose listing lags a caller already resolved.

**#3261's pair is a different cause.** 42307493684 and 42307798573 were sweep re-runs at attempt 10. A re-run restores `tools/ci` from the original event's `pull_request.base.sha`, so both ran 28482ece's programs, which predate #3246 (each gate log: `programs restored from 28482eceeb6b9809e44b12d80fc994282cc21645`). The recorded replay reproduces both verdicts on 28482ece and reads PASS at origin/main and here. See Forward-carry for the re-run finding.

**Alternatives not taken.**
- (a) *An edit gate that exits non-failing (PASS) when it defers.* Unsafe. While code run 42338396871 ran, `commits/02e92e7c/check-runs?check_name=gate` listed only the edit run's `gate` check-run: a gate waiting on its `needs` has no check-run yet. A PASS would have read the head green with tests still running.
- (b) *"Only the lowest id decides."* Ids order nothing here: a same-second edit and code run are numbered out of order (sweep.py docstring).
- (c) *Keep the at-once red, add a second exemption.* That stacks a parallel rule on a misread; the misread is the cause.
- (d) *Raise the bound past a code run's span.* Needs `ci.yml`'s `timeout-minutes`, outside this group's files, and holds a runner throughout.

**Residual, stated plainly.** A code run longer than the bound still ends in the documented past-bound deferral red. #3263's code run was still in progress 20 min in, so the replay at this head waits 720 s and then publishes that red. gate-sweep.yml re-judges it once the code run's gate is green. The at-once red is gone for every sibling that finishes inside the bound. Whether to lengthen the bound (`ci.yml`'s gate `timeout-minutes`) is the orchestrator's call. Carry: R10-HOTFIX-GATE-BUSY-DEFER

**Departure from the owned files.** `tools/ci/prelude.py` (`judging`, 4 lines and its docstring) is outside the roster's list (gate.py and the two harnesses). It is the one owner of "can this run still add a source": `gate.busy` and `prelude.wait_sources` both read it. A gate-side copy would be a parallel mechanism and would leave the prelude edge of the cycle open. The new fixture `tools/ci/fixtures/gate_busy_defer_runs.json` is the jobs API's record of both heads, fetched via `gh api` at 2026-11-07T04:4xZ, not re-typed.

## Head

cc100c27555e6936dd179293cd8897dae0a3b9ae, measured on a branch cut from origin/main 294a880dae608502b62055775e34a5db93217b98 (origin/main unmoved since the prepr run, read 2026-11-07T04:52Z: no merge and no second run owed).

## Mutation proof

`python3 dev/audit/harnesses/r10_ci_gate_core.py mutants` at the head: `RESULT mutants=21 survivors=0`. The two new mutants:

- **M25** deletes the fix's line in `judging` (`if jobs.get(u, ("",))[0] == "completed": continue` → `pass`). KILLED (self-test rc 1). Red:
  - `busy-defer-2: listed as GitHub lists it (`pr-contract` skipped), neither started gate waits on the other`
  - `busy-defer-2: the higher deferring edit gate beside the lower one listed as GitHub lists it judges at once`
  - `prelude/gate order: beside an earlier started deferring gate and a later edit run in its prelude, it waits on the later run only, then judges`
  - `the cycle's other edge: a deferring run at its gate is judging (its bare `pr-contract` caller skipped), so no prelude or gate waits on it`
  - `#3263: the code run's gate never waits on that deferring edit run (the edge that closed the cycle)`
- **M26** restores the at-once FAIL (`bound = 0` for a deferring workset's deferral). KILLED (self-test rc 1). Red:
  - `C3 (r10-gate-busy-defer-2): a deferring edit gate beside a busy code run waits on it, then judges its sources, no red`
  - `busy-defer: the higher deferring edit gate waits on the lower whose listing lags, then judges, never a red deferral`
  - `prelude/gate order: a deferring gate beside a later edit run still in its prelude waits on it (that run's prelude no longer waits on this one), then judges`
  - `prelude/gate order: a deferring gate beside a later edit run in its prelude, gate listed `waiting` (R3-2) waits on it (that run's prelude no longer waits on this one), then judges`
  - `prelude/gate order: beside an earlier started deferring gate and a later edit run in its prelude, it waits on the later run only, then judges`
  - `#3263 (42338396358 beside code run 42338396871): the deferring edit gate never publishes the deferral before its bound`

M20, M21, M22 and M24 pinned the deleted `deferring(...)` clause; they are removed with it, because their patterns no longer exist.

**Failing test first.** The head's self-test was run over origin/main's production code (`prelude.py`, and `gate.py` above `self_test`). Result: `gate self-test: 74 checks, 9 failed`, the #3263 replay among them (`got (False, True)`: the deferral published with no wait). Over 28482ece's production code: `74 checks, 14 failed`, both #3261 replays among them (each got the pair's deferral, as CI logged).

## Null control

Each of these is in the self-test:
- A lone code run with no sibling still gates normally: `null: no other run at the head, no wait`, `("PASS", [])`.
- A finished sibling still decides: `C3: the deferred gate re-judged once the code run ended (green|its pr-contract red) is that run's verdict` reads PASS, and `FAIL pr-contract / pr-contract: failure (run 99)`.
- A real red is never masked: `a deferring gate published after the decider's red is that red, never a PASS`.
- The bound still holds: `past the bound, the deferral FAILs (for gate-sweep.yml), and the wait stays inside the bound`.
- The fix's own null: `... null: a caller still running (not completed) still owes its unit` reads `judging` False.
- At the harness level, `single` reads `UNDECIDED-RED 0 ... gate-wait 0 s`.

## Figures

- `python3 -I tools/ci/gate.py --self-test`: `gate self-test: 74 checks, 0 failed`. `python3 -I tools/ci/prelude.py --self-test`: `62 checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_gate_defer_race.py --ci "$X/tools/ci" fixture`, with `$X` a `git archive <sha> tools/ci tools/pr` export:
  - at 28482ece: all three recorded gates read as CI logged them, the deferral after 0 s;
  - at 294a880d (origin/main): 42338396358 the deferral after 0 s, the #3261 pair `PASS`;
  - at the head (no `--ci`): 42338396358 the deferral after 720 s (the bound; its code run never finishes in the record), the #3261 pair `PASS` after 0 s.
  - Null for the replay itself: at 28482ece it reproduces CI's three logged verdicts verbatim.
- The same harness, `prelude` scenario: `UNDECIDED-RED 1` at 28482ece and at 294a880d; `UNDECIDED-RED 0 ... DEADLOCK no CYCLE 0` at the head. Every scenario at the head reads `UNDECIDED-RED 0`, `MASKED 0`, `DEADLOCK no` and `RESIDUAL-RED 0`.
- The class's seams (fixer step 8). The rule: every non-self-test reader of a title's workset, `grep -n "workset(" tools/ci/prelude.py tools/ci/gate.py tools/ci/sweep.py tools/ci/sweep_selftest.py`, with hits inside `def self_test` excluded. It returns 4 seams:
  - `prelude.py` `workset` (the definition);
  - `prelude.judging` (closed in this diff);
  - `prelude.outputs` (the producer: it writes the run's own workset, which `defer_to` narrows; it reads no other run);
  - `gate.gate`'s source loop (already guarded: `a unit that run deferred (C3) judged nothing: no source`, the all-skipped `continue`, with self-test `C3: a unit a run deferred is no source even under its full job name (skipped)`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: FULL` (a `tools/ci/` gate file: nothing scoped to reproduce locally).
- `bash tools/pr/prepr.sh`: `PRE-PR: cc100c27555e ... rc=0` (every step ok or a named skip; `ci predict`: no closures, fast, governance or instrument red predicted)

## Red checks

none predicted. A red at the PR is CI's, past the handoff.

## Forward-carry

- **A gate re-run executes the programs of its event's original base, not of main.** `ci.yml`'s gate step restores `tools/ci/*.py` from `github.event.pull_request.base.sha`, and a re-run (gate-sweep.yml's included) replays that event. So a PR whose last event predates a gate fix keeps running the old gate on every sweep re-run. #3261's pair at attempt 10 ran 28482ece, before #3246. That changes how the orchestrator reads a red re-run gate after a gate fix merges: re-judge such a PR only after a fresh event (a push, an edit, a review), or read the `programs restored from` line first. `.github/workflows/ci.yml` is outside this group. This fixer writes no roster or brief, so it routes the finding to this group for the orchestrator to place (its gate-fix merge step in `dev/governance/roles/orchestrator.md` is the proposed home). Carry: R10-HOTFIX-GATE-BUSY-DEFER

## Friction

none
