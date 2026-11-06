Part of #201. Hotfix topic r10-gate-busy-defer, repair round 3. Two `gate` jobs at one head each deferred to the other, so neither judged. Both were edit runs whose prelude had left `pr-contract` to a code run (C3). Each listed `pr-contract` skipped under the caller's bare name and never listed the `pr-contract / pr-contract` its title's workset owes. So `prelude.judging` read each as still adding a source, `gate.busy` named it, and `gate.deferring` set the wait bound to 0. Both published `FAIL run(s) [<the other>] ... their gate decides` within 9 s of starting (finder's logs: #3241 head 95c7e604, attempt 2 of runs 42192623509 and 42193153511).

The fix, in `tools/ci/gate.py`:
- `busy()`: a LATER run whose `gate` has started (`in_progress` or `completed`, the one predicate `started()`) is not waited on. Of two started gates, the lower id decides and the higher waits on it. A gate merely listed `waiting` is no proof (R3-2).
- `judge()`: a deferring gate waits only when ALL the runs it waits on have started their gate. Beside any other run (a code run, or an edit run in its prelude or units) it publishes the deferral at once, as main does, because such a run may sit in `prelude.wait_sources` waiting on this one. `busy()` leaves out later started gates, so every started run a deferring gate waits on is an earlier one, and the waits run down in id and cannot close a cycle.

This round adds no production line. It pins the `all` in that rule. The round-2 review's mutant M24 (`and not all(` to `and not any(` in `judge()`) re-opened the prelude/gate cycle and survived the self-test. This round adds the review's mixed scene as a self-test case and M24 to the mutant table.

Alternatives that lost:
- Make `prelude.judging` read a gate `in_progress` as judging (round 2's first fix, 3c66c9b3, reverted by b0bccab4, a disclosed self-correction). The approved design's replay reads DIFFERS on it: a gate `in_progress` while a unit re-runs must be waited on.
- Teach `judging()` to read the skipped bare `pr-contract` as finished. A skipped caller cannot be told apart in the listing from one the platform has not expanded yet.
- C3 at once only beside a code run (c0c60886, round 1). It re-opened the cycle with a later edit run in its prelude (M22 now pins this).

## Head

ea6d8de7ee27344285fdab6a628c4db0337d1307, branch `fix/r10-gate-busy-defer`. It resumes from the PR head 8af5fa58b79233127ce01d81bd94b6c1d48271cf and merges origin/main b36679cea (#3238; merge, not rebase; no conflict). Its three-dot diff against main touches `tools/ci/gate.py`, `dev/audit/harnesses/r10_ci_gate_core.py`, `dev/audit/harnesses/r10_gate_defer_race.py` and `dev/programme/delivery/3246.md`. Against 8af5fa58 this round changes `tools/ci/gate.py` (one self-test case, no production line) and `r10_ci_gate_core.py` (M24, and the mutants arm prints each red case). Every figure below was taken at 4710b715, whose tree is byte-identical to this head (`git diff --quiet 4710b715 HEAD` exits 0): the same two commits, re-made under the brief's `hpo-fixer` identity because the exported toolchain had set the author to `seat`. origin/main was b36679cea at the merge and at the final `tools/pr/prepr.sh` run at this head, so main had not moved and no second run was owed.

## Mutation proof

Failing test first. The new case `prelude/gate cycle: a deferring gate beside an earlier started gate and a later edit run in its prelude publishes at once` is green at this head. With M24 applied by hand to `tools/ci/gate.py`, `python3 -I tools/ci/gate.py --self-test` prints `66 checks, 1 failed`. The one failure is this case, which gets the right deferral only after 12 naps of `POLL_S` (720 s held; wanted: at once, no nap). The in-tree file was restored afterwards.

The table, taken from scratch at this head by `python3 -I dev/audit/harnesses/r10_ci_gate_core.py mutants`, prints `RESULT mutants=23 survivors=0`. The arm applies each mutant to `tools/ci/gate.py` (or `prelude.py`), then runs the self-test and the designed replay. It now prints each red self-test case by name. The rows for this PR's mutants:

| mutant | what it reverts | red cases (`gate.py --self-test`), as the arm prints them |
|---|---|---|
| M17 busy tie-break deleted | `busy()` back to main's predicate | `busy-defer: of two started gates at one head the lower id defers to none, the higher to the lower`; `busy-defer: the lower deferring edit gate judges at once beside the higher one` |
| M18 busy tie-break id inverted | `>` to `<` in the tie-break | `R3-2: a run whose gate is listed but an owed job is not still adds a source`; `busy-defer: of two started gates at one head the lower id defers to none, the higher to the lower`; `busy-defer: the lower deferring edit gate judges at once beside the higher one`; `busy-defer: the higher deferring edit gate waits on the lower (an edit run, not C3's code run), then judges, never a red deferral`; `prelude/gate cycle: a deferring gate beside an earlier started gate and a later edit run in its prelude publishes at once` |
| M19 a listed gate read as started (R3-2 EARLY) | `started()` true for a gate merely listed | busy-defer null (R3-2 EARLY): a later run whose gate is listed `waiting` beside running units is still deferred to; prelude/gate cycle: a deferring gate beside a later edit run in its prelude, gate listed `waiting` (R3-2) publishes at once |
| M20 C3 at once beside any run | the started-gate condition deleted | `busy-defer: the higher deferring edit gate waits on the lower (an edit run, not C3's code run), then judges, never a red deferral` |
| M21 C3 waits beside any run | the zero bound never applies | `C3: a deferring edit gate beside a busy code run publishes the deferral at once, holding no runner`; `prelude/gate cycle: a deferring gate beside a later edit run still in its prelude publishes at once`; prelude/gate cycle: a deferring gate beside a later edit run in its prelude, gate listed `waiting` (R3-2) publishes at once; `prelude/gate cycle: a deferring gate beside an earlier started gate and a later edit run in its prelude publishes at once` |
| M22 C3 at once only beside a code run (c0c60886) | c0c60886's code-run predicate restored | `prelude/gate cycle: a deferring gate beside a later edit run still in its prelude publishes at once`; prelude/gate cycle: a deferring gate beside a later edit run in its prelude, gate listed `waiting` (R3-2) publishes at once; `prelude/gate cycle: a deferring gate beside an earlier started gate and a later edit run in its prelude publishes at once` |
| M24 C3 waits beside any started run (all to any) | `all` to `any` in `judge()`'s C3 wait | `prelude/gate cycle: a deferring gate beside an earlier started gate and a later edit run in its prelude publishes at once` |

## Null control

- Without the new case, M24 survives. At 8af5fa58 (this case absent, the same `judge()`), the review measured `65 checks, 0 failed` under M24 (`origin/verdict/3246:evidence/my_mutants.txt`). The new case is the only one that goes red under M24 here.
- The two existing `prelude/gate cycle:` cases stay green under M24. With B alone, `any` over {B} equals `all` over {B}. That is why only the mixed scene, which adds the earlier started gate E, separates the two.
- The existing C3 case `C3: a deferring edit gate beside a busy code run publishes the deferral at once, holding no runner` and the busy-defer cases stay green at this head.
- The designed oracles at this head: `replay` and `sim` read IDENTICAL (`gate_replay2.py over tools/ci/gate.py: rc 0; output IDENTICAL to 1371a0a6:measure/rev/gate_replay2.txt`, and the same for `gate_sim.py` against `gate_sim.txt`).

## Figures

- Finder's harness for this block: the reviewer's probe `git show origin/probe/rev-3246-f805b9e8:ev/probe_mixed.py` (sha1 04d0c9e21161107d1c3371f4282abebf8f3bc286), a self-test snippet. By the reviewer's record (`ev/probe_mixed.txt`) it reads `naps=0 held_s=0` at 8af5fa58 and `naps=12 held_s=720` under M24. This round changes no production line, so the probe reads flat across 8af5fa58 and this head. Its re-runnable in-tree form is the new self-test case, whose expected value is the probe's head verdict, `FAIL run(s) [42192000000, 42193153511] ...` with no nap. The companion that reads the defect is the mutant table: the case is red under M24 and green at the head.
- Self-test: `python3 -I tools/ci/gate.py --self-test` prints `gate self-test: 66 checks, 0 failed`. `python3 -I tools/ci/prelude.py --self-test` prints `prelude self-test: 62 checks, 0 failed` (prelude.py is unchanged in the three-dot diff).
- Mutants: `python3 -I dev/audit/harnesses/r10_ci_gate_core.py mutants`, `RESULT mutants=23 survivors=0`. The 23 rows are M1-M22 and M24. M23 is the review's own label for `started()` accepting `waiting`, which M19 already is.
- Designed replays: `python3 -I dev/audit/harnesses/r10_ci_gate_core.py replay` and `... sim`. Each prints IDENTICAL or DIFFERS against its `1371a0a6:measure/rev/` reference.
- Race harness: `python3 -I dev/audit/harnesses/r10_gate_defer_race.py --ci <export>/tools/ci`, the export made by `git archive HEAD tools/ci tools/pr`, rc 0. The `prelude` scenario reads `prelude: verdicts 3 UNDECIDED-RED 1 MASKED 0 DEADLOCK no CYCLE 0 gate-wait 300 s (judge takes a clock: True); prelude: sweep present re-runs 1 RESIDUAL-RED 0`; its one UNDECIDED-RED is C3's designed at-once deferral, which the sweep converges to PASS. The six earlier scenarios read UNDECIDED-RED 0, MASKED 0, DEADLOCK no, CYCLE 0, RESIDUAL-RED 0.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL` (`tools/ci/gate.py changes the gate itself`). The full suite is CI's to run.
- Ratchets: `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2637 ENTITY CHECKS PASSED`.
- Seam enumeration (fixer step 8). Rule: `git grep -n "sleep(" -- 'tools/ci/*.py'`, one line per wait loop in the CI programs. The disposition of each returned seam is unchanged from round 2, because this round adds no wait:
  - `gate.py` `judge()`: closed in this diff, and its `all` is now pinned by M24's killing case.
  - `prelude.py` `wait_sources`: already guarded. Its one edge into a gate is closed from the gate side.
  - `codescan_wait.py` (two loops): already guarded. Units wait on no run.
  - `sweep.py` `run`: already guarded. Nothing in ci.yml waits on it.
  - `ghapi.py` (two lines): a retry back-off, with no wait on any run.

## Red checks

- `governance / instrument-self-tests` job 127890366334 (code run 42217217301 at 8af5fa58) hit the 30-minute job limit while in ci_predict's self-test, and its run concluded `cancelled`. **MAIN-WIDE**: main's own push run at the merge base, 42214947262, timed out the same job (12:05:33Z to 12:35:45Z, cancelled). This diff adds seconds of gate.py self-test. It is carried in R10-PROCESS-SLIM, not settled here.
- `gate` 127907648432 (run 42217406703) and 127907644986 (run 42217218226), attempt 2 of the two edit runs at 8af5fa58, published red at 13:04:30Z. Each printed `FAIL run(s) [<the other>] ...`, and both ran `programs restored from 5421413b...`. So the job judged with main's pinned `tools/ci/*.py`: main's mutual deferral, the defect this PR fixes, reproducing live. The diff did not cause them. The cheaper detector is this PR's own self-test busy-defer cases and race harness, whose standing cost is the gate self-test that already runs.
- `gate` 127891515500 and 127890801445, attempt 1 at 8af5fa58: C3 deferrals to the code run 42217217301. That is the designed at-once publish, which the sweep re-judges. Not caused by the diff.
- Any red at this head is the CI run's to show past the handoff. A `gate` red reading `programs restored from <base>` with a mutual `FAIL run(s)` deferral is the same pinned-main defect.

## Forward-carry

none

## Friction

- PROMPT.md: contradiction: the payload says to pin git identity `seat` with the seat noreply address, and the snapshotted brief says `hpo-fixer` and never `seat`; the brief's `hpo-fixer` identity was used. Carry: dismissed: one-shot payload text, the brief's later line is explicit
- tools/audit/seat/cloud-setup.sh: contradiction: the exported toolchain sets GIT_AUTHOR_NAME and GIT_COMMITTER_NAME to `seat`, which overrides `git config user.name`, so a fixer told never to commit as `seat` does so unless it overrides the environment per commit. Carry: dismissed: identity of a seat commit, settled per brief; this round's commits were re-made as `hpo-fixer` with an identical tree
