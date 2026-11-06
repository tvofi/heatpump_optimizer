Part of #201. Hotfix topic r10-gate-busy-defer, repair round 2. Two `gate` jobs at one head each deferred to the other, so neither judged. The cause was re-derived from the finder's logs (#3241 head 95c7e604, attempt 2 of runs 42192623509 and 42193153511). Both were edit runs whose prelude had left `pr-contract` to a code run (C3). So each listed `pr-contract` skipped under the caller's bare name, and never listed the `pr-contract / pr-contract` its title's workset owes. `prelude.judging` therefore read each as still adding a source, `gate.busy` named it, and `gate.deferring` set the wait bound to 0. Both published `FAIL run(s) [<the other>] ... their gate decides` within 9 s of starting. Job 127833303340 ran 10:07:46.90Z to 10:07:55.91Z, and job 127833295321's gate step ran 10:07:45.87Z to 10:07:54.86Z.

The round-1 review blocked c0c60886. Its C3 change (a zero bound only beside a code run) re-opened a wait cycle across the prelude/gate seam. A = a deferring edit run at its gate, C = the code run it deferred to (finished), B = a later edit run at the same head, still in its prelude. B's `prelude.wait_sources` waits on A, because `judging(A)` is False. At c0c60886, A's gate waited on B (an edit run) for GATE_WAIT_MAX_S. Only that bound broke the cycle, and A then published the same red deferral that main publishes at 0 s.

The fix, in `tools/ci/gate.py`:
- `busy()` (from round 1, unchanged): a LATER run whose `gate` has started (`in_progress` or `completed`) is not waited on. Of two started gates, the lower id decides and the higher waits on it. A gate merely listed `waiting` is no proof (R3-2). The predicate is now one function, `started()`.
- `judge()`: a deferring gate waits only when every run it waits on has started its gate. Beside any other run, a code run or an edit run in its prelude or units, it publishes the deferral at once, as main does. Such a run may be in `wait_sources` waiting on this one. Every run `busy()` returns with a started gate is an EARLIER run, because `busy()` leaves out later started gates. An earlier started gate waits on no later started gate, and a deferring one again waits only on earlier started gates. So a deferring gate's waits run down in id and cannot close a cycle.

Alternatives that lost:
- Make `prelude.judging` read a gate `in_progress` as judging. ci.yml's `gate` needs `prelude` and `pr-contract`, which needs every unit. This removes the misread at its owner, and it was this round's first fix (commit 3c66c9b3). It contradicts the approved design's replay: `r10_ci_gate_core.py replay` read DIFFERS from `1371a0a6:measure/rev/gate_replay2.txt`, on the case `rev2: ... a unit job re-running beside the listed gate (re-run failed jobs): deferred`. That case is a gate `in_progress` while a unit re-runs, and the design requires it to be waited on. So the commit was reverted (b0bccab4). That is a disclosed self-correction. The final head reads IDENTICAL.
- Teach `judging()` to read the skipped bare `pr-contract` as finished. Round 1 rejected this: a skipped caller is not distinguishable in the listing from one the platform has not expanded yet.
- The reviewer's remedy, worded as an earlier run whose gate has started. It is the rule taken here. The `r["id"] < ctx["run_id"]` clause is implied by `busy()`'s tie-break, so it is not repeated.

## Head

e3a942d0d67e27c7e8049461056c68fc9ca9b018, branch `fix/r10-gate-busy-defer`, which has origin/main 5421413b54ba1044b8e91e1afd88b41acfc7a753 (2026-11-06) merged into it (merge, not rebase). That merge brought in #3243 only (`tests/gate_lock.py` and its delivery row). `git diff --quiet 95971b45 HEAD -- tools/ci dev/audit/harnesses` exits 0, so `tools/ci` and both harnesses are byte-identical to 95971b45. At this head I re-ran the self-test, the race harness, the mutants, replay, `tests/structure.py`, `tests/entities.py` and `prepr.sh`. The probe and the sim ran at 95971b45, which has the same `tools/ci` tree. The mutant cases tabled for M17-M22 were listed at b56b12f1, which differs from this head's `tools/ci` only in `judge()`'s C3 docstring. main had not moved again at the final `prepr.sh` run.

## Mutation proof

Failing test first: commit 39b17a4d adds the review's scene to `gate.py --self-test` on top of c0c60886's production code. It reads `65 checks, 2 failed`. Each case fails by holding the runner 12 naps (720 s) before publishing the deferral that is wanted at once.

The table was taken from scratch at the final head by `python3 -I dev/audit/harnesses/r10_ci_gate_core.py mutants`: `RESULT mutants=22 survivors=0`. Each mutant was applied to `tools/ci/gate.py` and its self-test was run. These are the red cases for this PR's mutants:

| mutant | what it reverts | red cases (`gate.py --self-test`) |
|---|---|---|
| M17 busy tie-break deleted | `busy()` back to main's predicate | `busy-defer: of two started gates at one head the lower id defers to none, the higher to the lower`; `busy-defer: the lower deferring edit gate judges at once beside the higher one` |
| M18 busy tie-break id inverted | `>` to `<` | both of the above, `busy-defer: the higher deferring edit gate waits on the lower ...`, and `R3-2: a run whose gate is listed but an owed job is not still adds a source` |
| M19 a listed gate read as started (R3-2 EARLY) | `started()` true for a gate merely listed | `busy-defer null (R3-2 EARLY): ...`; `prelude/gate cycle: a deferring gate beside a later edit run in its prelude, gate listed `waiting` (R3-2) publishes at once` |
| M20 C3 at once beside any run | the started-gate condition deleted | `busy-defer: the higher deferring edit gate waits on the lower (an edit run, not C3's code run), then judges, never a red deferral` |
| M21 C3 waits beside any run | the zero bound never applies | `C3: a deferring edit gate beside a busy code run publishes the deferral at once, holding no runner`; both `prelude/gate cycle: ...` cases |
| M22 C3 at once only beside a code run (c0c60886) | c0c60886's predicate restored | `prelude/gate cycle: a deferring gate beside a later edit run still in its prelude publishes at once`; `prelude/gate cycle: ... gate listed `waiting` (R3-2) publishes at once` |

## Null control

- The existing C3 case, `C3: a deferring edit gate beside a busy code run publishes the deferral at once, holding no runner`, stays green: beside a code run the at-once publish still holds.
- The round-1 busy-defer cases stay green, unchanged: the two-started-gates tie-break, the lower judging at once, the higher waiting on the lower and then judging, and the three `busy-defer null` cases.
- `null: no other run at the head, no wait` stays green.
- The designed oracles at this head: `replay` and `sim` read IDENTICAL to `1371a0a6:measure/rev/`.
- The race harness's six earlier scenarios read the same at the merge base, at c0c60886 and at this head: UNDECIDED-RED 0, MASKED 0, DEADLOCK no, CYCLE 0, RESIDUAL-RED 0.

## Figures

- Reviewer's probe (the finder's harness for this block): `git show origin/verdict/3246:evidence/probe_snippet.py` (sha1 df85c155c3cec3bdc5eb1d023fae0e8c2a66c898). It was run by the reviewer's recipe (`git show origin/verdict/3246:evidence/probe_cycle.txt`): inserted after `eclaim3 = ...` into a scratch copy of gate.py's self-test, in a detached worktree per SHA, run with `--self-test`, and the scratch copy deleted afterwards. That copy is a one-off and is not in the tree. Its in-tree, re-runnable form is the two `prelude/gate cycle:` cases of `python3 -I tools/ci/gate.py --self-test`. Merge base 7e8939d3: `naps=0 held_s=0`. c0c60886: `naps=12 held_s=720`. This head: `naps=0 held_s=0`. `judging(A)` reads False at all three, because the gate side breaks the cycle and the prelude side does not. The verdict is `FAIL run(s) [42193153511] ... their gate decides` at all three, and it is re-judged by the sweep.
- Race harness: `python3 -I dev/audit/harnesses/r10_gate_defer_race.py --ci <export>/tools/ci`, with each export made by `git archive <sha> tools/ci tools/pr`. The new `prelude` scenario reads: merge base `UNDECIDED-RED 1 ... DEADLOCK no CYCLE 0 gate-wait 300 s`, RESIDUAL-RED 0; c0c60886 `UNDECIDED-RED 2 ... DEADLOCK yes CYCLE 1 gate-wait 1500 s`; this head `UNDECIDED-RED 1 ... DEADLOCK no CYCLE 0 gate-wait 300 s`, RESIDUAL-RED 0. The one UNDECIDED-RED at the base and at the head is C3's designed at-once deferral, which the sweep converges to PASS.
- Self-test: `python3 -I tools/ci/gate.py --self-test` prints `65 checks, 0 failed` at this head. `python3 -I tools/ci/prelude.py --self-test` prints `62 checks, 0 failed` (prelude.py is unchanged across the three-dot diff).
- Mutants: `python3 -I dev/audit/harnesses/r10_ci_gate_core.py mutants` (its `RESULT` line).
- Designed replays: `python3 -I dev/audit/harnesses/r10_ci_gate_core.py replay` and `... sim`, each printing IDENTICAL or DIFFERS against its reference.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL` (`tools/ci/gate.py changes the gate itself`). The full suite is CI's to run.
- Ratchets: `python3 tests/structure.py` (STRUCTURE RATCHET PASSED) and `PYTHONPATH=tests/hastub python3 tests/entities.py` (its summary line).
- Seam enumeration (fixer step 8). Rule: `git grep -n "sleep(" -- 'tools/ci/*.py'`, one line per wait loop in the CI programs. Each returned seam is dispositioned:
  - `gate.py` `judge()`: closed in this diff.
  - `prelude.py` `wait_sources`: already guarded on every other edge. It waits on earlier runs and on code runs that are not judging. Code runs never call it. Its one edge into a gate, a deferring run that `judging()` reads busy, is closed from the gate side here: that gate no longer waits on a run whose gate has not started.
  - `codescan_wait.py` (two loops): already guarded. It waits on another run's `codeql` unit jobs and analyses, and units wait on no run.
  - `sweep.py` `run`: already guarded. It runs in gate-sweep.yml after a CI run completes, and nothing in ci.yml waits on it.
  - `ghapi.py` (two lines): a retry back-off, with no wait on any run.

## Red checks

- `gate` check runs 127870749756 (run 42207498719) and 127870741795 (run 42206948863) are red at c0c60886, counted across all pages of the check listing. Both are attempt-2 edit runs. Each printed `FAIL run(s) [<the other>] ... their gate decides`, at 11:36:24Z and 11:36:22Z. Both gate jobs judged with `tools/ci/*.py` restored from the base (`git checkout "$PINNED" -- 'tools/ci/*.py'`, PINNED = the base SHA; reviewer evidence `ev/gates_1136_pinned.txt`). So this is main's defect, the one this PR fixes, reproducing live. The diff did not cause it. The cheaper detector is this PR's own: the `busy-defer` self-test cases and the race harness. Their standing cost is the gate self-test that already runs.
- The earlier red gate 127858465432 (11:06:59Z) at c0c60886 was a C3 deferral to the code run 42206947897, which then went green. It was not caused by the diff either.

## Forward-carry

none

## Friction

- PROMPT.md: contradiction: the payload says to pin git identity `seat` with the seat noreply address, and the snapshotted brief says `hpo-fixer` and never `seat`; the brief's `hpo-fixer` identity was used. Carry: dismissed: one-shot payload text, the brief's later line is explicit
