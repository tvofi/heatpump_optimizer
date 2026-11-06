Fix review: blocked 8af5fa58b79233127ce01d81bd94b6c1d48271cf mutation-vacuous: judge() C3 all-to-any mutant restores the 720 s prelude/gate wait and no self-test case is red

bus-nonce: f805b9e82d28b4358f381573a9f7f1dd

## Round

This is round 2 of fix review for R10-HOTFIX-GATE-BUSY-DEFER (PR #3246), critical path. I measured at head 8af5fa58b79233127ce01d81bd94b6c1d48271cf from a detached worktree. Merge base 5421413b54ba1044b8e91e1afd88b41acfc7a753 equals origin/main at review. The roles diff since the merge base is empty. Under the three-round rule, a further block goes to round 3, the last before a re-cut is owed.

## Block

Claim: the re-cut's C3 rule is that a deferring gate waits only when EVERY run it waits on has started its gate (`not all(started(r) ... if r["id"] in waiting)`). The body's mutant table says the self-test pins it (M20, M21, M22). It does not pin the `all`. My own mutant M24 changes `and not all(` to `and not any(` in judge(). The deferring gate then waits whenever ANY waited run has started. That re-opens round 1's prelude/gate cycle whenever a later run in its prelude sits beside an earlier started gate. `gate.py --self-test` stays `65 checks, 0 failed` under it. Carry: dismissed: the blocked defect itself, owed by this PR's re-cut

Evidence (reviewer's own probe, disclosed as mine and not the finder's harness): ev/probe_mixed.py, a variant of round 1's ev/probe_snippet.py, inserted the same way into a scratch copy of gate.py's self-test. The scene: A = the deferring edit gate (lo); E = an earlier deferring edit run with its gate in_progress; B = a later edit run still in its prelude; C = the code run, completed. Output is in ev/probe_mixed.txt:
- head: `FAIL run(s) [42192000000, 42193153511] ...`, naps=0, held_s=0.
- head with M24: the same verdict, naps=12, held_s=720. B's wait_sources waits on A (judging(A) is False), A waits on B, and only GATE_WAIT_MAX_S breaks it. This is the exact round-1 defect.
- My planted mutants (ev/my_mutants.txt): M20-mine (the started condition deleted) is red on 1 case. M22-mine (c0c60886's code-run predicate) is red on 2 cases, both `prelude/gate cycle:`. M23-mine (started() accepts `waiting`) is red on 2 cases. M24-mine (`all` to `any`) is red on 0 cases, and survives.

Perturbation: the mixed scene differs from the in-tree `prelude/gate cycle: a deferring gate beside a later edit run still in its prelude publishes at once` case only by the added earlier started gate E. Without E, M24 is killed, because `any` over {B} equals `all` over {B}.

Owed (not prescribed): add the mixed scene as a self-test case, and the all-to-any mutant to r10_ci_gate_core.py's MUTANTS, shown red by that named case. A push also gives the head a fresh code run whose gate judges after the edit runs (see the CI finding). Carry: dismissed: owed by this PR's re-cut under the Block

## Findings

- Follow-up: the required `gate` is RED at this head. `merge_train.py classify 8af5fa58... --pr 3246` gives rc 1: `RED 8af5fa58... pending: none red: gate` (ev/classify_final.txt). The code run 42217217301's gate 127907245280 succeeded at 13:03:34Z after its `pr-contract / pr-contract` 127906937350 succeeded. Attempt 2 of the two edit runs then published red at 13:04:30Z: gate 127907648432 (run 42217406703, `FAIL run(s) [42217218226] ...`) and gate 127907644986 (run 42217218226, `FAIL run(s) [42217406703] ...`). Both had `programs restored from 5421413b...` (ev/gates_1304.txt), so this is main's mutual deferral, the defect this PR fixes, reproducing live. The diff did not cause it. The attempt-1 reds 127891515500 and 127890801445 are C3 deferrals to that code run. The body's `## Red checks` answers the c0c60886 reds but none of these four at 8af5fa58. Step 11 cannot be judged yet, because no `pr-contract` run started after the last red (13:04:33Z). The re-cut body owes their names and answers. Carry: dismissed: owed by this PR's re-cut under the Block
- Out of scope: the code run 42217217301 concluded `cancelled`. Its `governance / instrument-self-tests` (127890366334) hit the 30-minute job limit at 12:53:39Z, while in ci_predict's self-test (ev/instr_selftests_tail.txt). Main's own push run at the merge base, 42214947262, timed out the same job (12:05:33Z to 12:35:45Z, cancelled). At 7e8939d3 the job took 29m17s (ev/main_instr.txt). So it is main's own budget, not this diff, which adds only seconds of gate.py self-test. Main's red is visible to the orchestrator directly. Carry: dismissed: main's own red at 5421413b (run 42214947262), not this PR's to settle

## Evidence

- Round-1 probe (the brief's finder harness for this block): ev/probe_snippet.py from probe/rev-3246-4b5d5ad4, run at three SHAs (ev/probe_r2.txt; the head re-run after the mutant harness had finished, ev/probe_r2_rerun.txt). Base 5421413b: naps=0, held_s=0. c0c60886: naps=12, held_s=720. Head: naps=0, held_s=0. The verdict is `FAIL run(s) [42193153511] ...` at all three, and judging(A) is False at all three. The scene now holds at 0 s.
- The finding's own perturbation (ev/probe_perturb.py, B's gate in_progress): head and c0c60886 give `PASS` with naps=0. Base gives `FAIL run(s) [42193153511]`, main's defect. The claimed behaviour is restored.
- gate.py --self-test: base `57 checks, 0 failed`, head `65 checks, 0 failed`. prelude.py --self-test: `62 checks, 0 failed` at both (ev/selftest.*.txt).
- r10_ci_gate_core.py mutants at head: `RESULT mutants=22 survivors=0` (ev/mutants.rev.txt). M17-M22 are KILLED by the self-test (rc 1) with replay rc 0, which matches the body's table. M24 is mine and not in it.
- replay: `gate_replay2.py ... IDENTICAL to 1371a0a6:measure/rev/gate_replay2.txt`. sim: `gate_sim.py ... IDENTICAL to 1371a0a6:measure/rev/gate_sim.txt` (ev/replay.rev.txt, ev/sim.rev.txt). Settle item (3), the self-correction a83b95f9 and the 3c66c9b3/b0bccab4 revert: the final head reads IDENTICAL, as claimed.
- r10_gate_defer_race.py, run on a `git archive` export per SHA (ev/race.{base,c0c,rev}.txt, rc 0 at all three). The new `prelude` scenario reads `UNDECIDED-RED 1 MASKED 0 DEADLOCK no CYCLE 0 gate-wait 300 s` at base and head (RESIDUAL-RED 0), and `UNDECIDED-RED 2 MASKED 0 DEADLOCK yes CYCLE 1 gate-wait 1500 s` at c0c60886. Its DEADLOCK line covers the prelude-phase cycle. The six earlier scenarios are unchanged across all three and match the body's figures.
- Settle item (1): busy() waits only on non-judging runs and leaves out later started gates. So a deferring gate's started waited runs are earlier non-judging runs: deferring ones, which recurse downward in id, or ones whose listing lags, which a re-read clears, as the docstring says. Under `all` no cycle forms. A gate listed `waiting` is not read as started: M19 and my M23 are both killed.
- Settle item (2), null controls: `C3: a deferring edit gate beside a busy code run publishes the deferral at once` stays green (M21 kills it), and the busy-defer cases are unchanged and green.
- Settle item (4): #3243 is already merged (origin/main 5421413b is its merge), and the body states the order. Disjoint files.
- `git merge-tree --write-tree origin/main 8af5fa58...` exits 0 with tree 410748b5, no conflict.
- tests/structure.py: `STRUCTURE RATCHET PASSED`. tests/entities.py: `ALL 2637 ENTITY CHECKS PASSED`. closure select: `MODE: FULL`, reason `tools/ci/gate.py changes the gate itself` (ev/ratchets.txt). CI owes the full suite. The gate job judges with tools/ci/*.py pinned from the base, so this PR's gate.py runs only in its self-test and harnesses until merged.
- Three-dot diff: tools/ci/gate.py, both r10 harnesses, and dev/programme/delivery/3246.md (the delivery row is present). custom_components/, VERSION and RELEASE_NOTES.md: 0 paths.
- Body corrections owed from round 1 are made: the second window now reads 10:07:45.87Z to 10:07:54.86Z, and the reds 127870749756 and 127870741795 are named and answered as main's pinned defect.
- Head check: the PR head is 8af5fa58b79233127ce01d81bd94b6c1d48271cf, the head measured, as the body's `## Head` states. Forward-carry: the body says none.
