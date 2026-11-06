Fix review: blocked c0c60886efc40c653330a3ea9368a2e7050bcff5 wait-cycle: deferring edit gate now waits 720 s on a later edit run whose prelude waits on it

bus-nonce: 4b5d5ad406360c5d586888bfcd2ca2f5

## Round

First round of fix review for R10-HOTFIX-GATE-BUSY-DEFER (PR #3246), measured at head c0c60886efc40c653330a3ea9368a2e7050bcff5 from a detached worktree; merge base dc0a170b671814be196a54b1c71e29449f54d6d7 (= origin/main at review). Roles diff since the merge base: empty.

## Block

Claim: the brief's settle item (1) asks for no cycle of waits; the body's seam disposition says `prelude.wait_sources` is "already guarded ... a deferring edit run it waits on still ends", and the gate.py docstring says the waits stay acyclic. The judge() C3 change (`bound = 0` only when a code run is among the waited runs) breaks that for a gate-vs-prelude pair that main handled at once.

The scene: A = deferring edit run (its prelude ran EDIT_UNDER_CODE; its `pr-contract` listed skipped under the bare name) at its gate; C = the code run it deferred to, already completed; B = a later edit run at the same head still in its prelude. B's prelude: defer_to() is None (C finished), so it calls wait_sources, and waits_on(B, A) is True (earlier run) and judging(A) is False (the same `pr-contract / pr-contract` misread this PR names), so B waits on A for up to WAIT_MAX_S 8700 s. A's gate: busy(A) = [B] (B's gate not started, so the new tie-break does not exempt it); B is an edit run, so the new C3 condition is False and A's bound is GATE_WAIT_MAX_S. A waits on B and B waits on A; the cycle is broken only by A's 720 s bound, and A then publishes the same red deferral main published at 0 s. Carry: dismissed: the blocked defect itself, settled by this PR's re-cut

Evidence (reviewer's own probe, disclosed as mine, not the finder's harness: ev/probe_snippet.py inserted into a scratch copy of gate.py's self-test; output in ev/probe_cycle.txt):
- base dc0a170b: A's verdict `FAIL run(s) [42193153511] at this head are still being judged; their gate decides`, naps=0, held 0 s.
- head c0c60886: the same verdict, naps=12, held 720 s. judging(A) = False and waits_on(B, A) = True at both.
- So at this head B's own verdict, the head's deciding one, comes 720 s later than at the base, a gate runner is held 12 minutes, and A still ends red, to be re-judged by the sweep. Every head with zero judging gates is avoided (B judges after A ends), but a wait cycle is reintroduced. None of r10_gate_defer_race.py's six scenarios (2754, 2754-red, pair, cascade, editcode, single) puts a later run in its prelude beside a deferring gate, so its `DEADLOCK no` lines do not cover this.

Perturbation: the scene differs from the self-test's `busy-defer: the higher deferring edit gate waits on the lower` only in that the waited edit run has not started its gate. Making B's gate `in_progress` (its prelude done) restores the claimed behaviour, because the tie-break then applies one way and B no longer waits in wait_sources.

A remedy the fixer may weigh (not prescribed): keep C3's zero bound unless every waited run is an earlier run whose gate has started (`r["id"] < ctx["run_id"]` and its gate in STARTED). Only such a run is known to end without waiting on this one. Add the probe's scene as a self-test case and a mutant, and a prelude-phase scenario to r10_gate_defer_race.py. Carry: dismissed: owed by this PR's re-cut under the Block; the group is a held roster append with no live destination yet

## Findings

- Follow-up: r10_gate_defer_race.py has no scenario where one run is in prelude.wait_sources while another's gate waits on it. A wait cycle across the prelude/gate seam is therefore invisible to the harness the body cites for `0 DEADLOCK`. Add one with the re-cut. Carry: dismissed: owed by this PR's re-cut under the Block; the group is a held roster append with no live destination yet
- Follow-up: the body's `## Red checks` says none have run, which is stale. At this head the latest `gate` check runs are red: 127870749756 (run 42207498719) and 127870741795 (run 42206948863), both attempt-2 edit runs, at 11:36:24Z and 11:36:22Z, each `FAIL run(s) [<the other>] ... their gate decides`. Those gate jobs ran tools/ci/*.py restored from the base (`git checkout "$PINNED" -- 'tools/ci/*.py'`, PINNED = base SHA; ev/gates_1136_pinned.txt), so this is main's defect, the one this PR fixes, reproducing live. It was not caused by the diff. The re-cut body should name the red and answer it that way. Carry: dismissed: owed by this PR's re-cut under the Block; the group is a held roster append with no live destination yet
- Follow-up: the body's second deferral window "10:07:47Z to 10:07:55Z" does not match its log. Job 127833295321's gate step started at 10:07:45.87Z and printed the FAIL at 10:07:54.86Z. The first window (10:07:46.90Z to 10:07:55.91Z) matches. Correct it in the re-cut body. Carry: dismissed: owed by this PR's re-cut under the Block; the group is a held roster append with no live destination yet

## Evidence

- Cause re-derived from the finder's harness. Job logs 127833303340 (run 42193153511) and 127833295321 (run 42192623509) have sha1 a93636b6d3dbbdb65355733c9e126e3438eb4a45 and da0168eade1217f44e56361f5ffc05e6979eb4e8, as the body says. Line 7047 of each is the FAIL naming the other run. In the attempt-2 jobs listings (ev/jobs*.json), each run lists `pr-contract` completed/skipped and no `pr-contract / pr-contract`. Both runs are titled `CI edit pr=3241`, head 95c7e604.
- gate.py --self-test: base 57 checks, 0 failed; head 63 checks, 0 failed. prelude.py --self-test: 62/0 at both.
- Main's production gate.py with this head's self_test spliced in: 63 checks, 3 failed, the three busy-defer cases. One prints `got ('FAIL run(s) [42193153511] ...`. The body's figure is re-derived.
- r10_ci_gate_core.py mutants at head: `RESULT mutants=20 survivors=0` (ev/mutants.txt). I also planted M17-M20 myself (ev/my_mutants.txt). M17 turns 2 cases red, M18 4 (including `R3-2: a run whose gate is listed but an owed job is not still adds a source`), M19 1 (`busy-defer null (R3-2 EARLY) ...`), M20 1 (`busy-defer: the higher deferring edit gate waits on the lower ...`). That matches the body's table.
- replay and sim: IDENTICAL to 1371a0a6:measure/rev/ at base and head. The head's sim was re-run clean after a run that overlapped my mutant planting (ev/rev.clean.txt).
- r10_gate_defer_race.py at head: rc 0, UNDECIDED-RED 0, MASKED 0, DEADLOCK no and RESIDUAL-RED 0 on all six scenarios (ev/race.rev.txt).
- Settle item (1), the tie-break alone: a started gate implies its run's units are finished, because ci.yml gives `gate` `needs: [prelude, pr-contract]` and `pr-contract` needs every unit, so the exemption is sound. A pair of started gates is ordered by id and cannot cycle. A gate listed `waiting` is still waited on, and M19 is killed by the R3-2 EARLY case. The remaining cycle is the gate/prelude one in the Block.
- Settle item (2), C3: beside a code run (or an unreadable title) the existing C3 case stays green, so the at-once publish holds. Beside only an edit run the gate waits, which is the source of the Block.
- Settle item (3): the self-correction a83b95f9 changes the tie-break to key on STARTED. The final head reads IDENTICAL on sim and replay, as claimed.
- Settle item (4): #3243 (open, head 411270a4) changes dev/programme/delivery/3243.md and tests/gate_lock.py only, disjoint from this diff. Either may merge first.
- `git merge-tree --write-tree origin/main c0c60886` exits 0 with empty stderr.
- tests/structure.py: STRUCTURE RATCHET PASSED. tests/entities.py: ALL 2632 ENTITY CHECKS PASSED.
- closure select at the merge base prints `MODE: FULL`, reason `tools/ci/gate.py changes the gate itself, so every closure is suspect`. CI owes the full suite. Note that the gate job judges with tools/ci/*.py pinned from the base, so this PR's gate.py is exercised only by its self-test and harnesses until it merges.
- Three-dot diff: tools/ci/gate.py, dev/audit/harnesses/r10_ci_gate_core.py and dev/programme/delivery/3246.md. The delivery row is present. custom_components/, VERSION and RELEASE_NOTES.md are untouched (0 paths).
- CI at this head: merge_train classify gave rc 1, `RED c0c60886... pending: none red: gate` (ev/classify2.out). Code run 42206947897 concluded success and its gate 127870368353 succeeded at 11:35:33Z. The later red gates are main's pinned programs (see Findings). The earlier red gate 127858465432 (11:06:59Z) was a C3 deferral to that code run.
- Forward-carry: the body says none, and none is owed.
- Head check: the PR head is c0c60886efc40c653330a3ea9368a2e7050bcff5, the head measured, as the body states.
