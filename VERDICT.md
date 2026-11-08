Fix review: merge 569318eded525daf0d9f5eb89e1d169475284b2c

bus-nonce: 3fe79a4defdbfa65d005d4184c13a74e

## Verdict

This is round 4, the fourth review of #3290, done under orchestrator ruling s13. The round-3 class-open finding (`classify_at` read the gate-sweep settle gap as RED) is closed at this head. The repair is sound, and the diff since a38bd141 grew no scope beyond what the brief named.

The repair has two parts:
- `gate_rerunning`: an unfinished ci.yml run whose suite's latest gate has completed counts as busy.
- `sweep_settling`: a wall-clock settle of `SWEEP_SETTLE_SECONDS` = 240 s after the newest green GATE suite completed.

Both run only on a red GATE. Past the bound, or with no stamp, or with a stamp ahead of the clock, the red still ends RED. Neither part can merge anything: merges still need gate success and `cross_check`.

On the re-cut question: had this round blocked, I would have said so for a fifth round. It does not block, so no re-cut is owed.

## Findings

- Residual: mutant MJ survives (`SWEEP_SETTLE_SECONDS = SWEEP_SETTLE_POLLS * HEARTBEAT_SECONDS` -> `10 ** 9`). Both past-the-bound nulls take the bound from the constant itself: merge_train's `settle gap null` uses `bound + 1` and proof_watch's `(g4) null` uses `SWEEP_SETTLE_SECONDS + 1`. So the bound's existence is pinned, but its size is not. If the constant were inflated, the one-read settle would in effect be unbounded on the wall clock. The constant is named, is derived from two pinned constants, and the body states it as 240 s, so this is an unpinned design input, not a wrong line. Carry: dismissed: constant-definition mutant; the bound's presence is pinned relative to the named constant (MF5 kills an unbounded comparison), and its 240 s value is a stated design input, not a defect of this diff
- Residual: mutant MN survives (`gate_rerunning`'s `if c.get("status") == "completed"` filter on `done` dropped). It is equivalent. With that filter gone, the only runs newly counted are those whose suite's latest gate is in progress. For such a run, `classify` already reads GATE as pending rather than red, and `gate_busy` (gate.py `busy`) names the run anyway: ev/mn-equivalence.txt prints `gate_busy [101]`, `rerunning []` and `classify ('wait', ['gate'], [])`. This has the same shape as the body's dismissal of MF7, which my ML re-confirmed as surviving. Carry: dismissed: equivalent mutant, an in-progress gate is pending in classify and busy in gate.py already

## Evidence

- Head reviewed: 569318eded525daf0d9f5eb89e1d169475284b2c (ev/HEAD.txt). It is a merge of authored head 94da0b7f onto a38bd141.
  - The merge base is 364353e670f666be6c97a5942ffa0bea9132b5ce. origin/main is at 17e1157925908bd69addb58ed824c1ac22bfa82f.
  - The roles diff from the merge base to main touches only fix-review.md, one line, which I read at main.
  - The body's `## Head` names this head.
- Scope since round 3: `git diff a38bd141 HEAD` touches 6 files.
  - merge_train.py: `gate_rerunning`, `sweep_settling`, `SWEEP_SETTLE_SECONDS`, `classify_at` and their self-tests.
  - proof_watch.py: the `wall` pass-through and the (g4) cases.
  - train.sh: `add --front`.
  - The three instruments docs.
  - The `--front` pass-through was named by the round-3 brief and is the only addition outside the finding.
  - The RCA branch tip (0f71c6d7) no longer touches train.sh (`git diff 364353e6 origin/handoff/r10-rca-gate-busy-defer-4 -- tools/audit/seat/train.sh` is empty), so `--front` lives only here.
  - `git merge-tree` against the RCA branch has rc 0 both ways (ev/merge-tree.txt).
- `git merge-tree --write-tree origin/main HEAD`: rc 0, tree d079fcb6, no conflict (ev/merge-tree.txt).
- CI on this head: `merge_train.py classify 569318ed... --pr 3290` read WAIT (rc 3) from 00:34:52Z. The 00:56:38Z read printed `GREEN 569318eded525daf0d9f5eb89e1d169475284b2c pending: none red: none`, rc 0 (ev/classify-log.txt).
- Red checks: all 55 check runs at this head are on one page. Every conclusion is success or skipped, and none is a concluded red (ev/check-runs-head.txt).
  - `pr-contract / pr-contract` 128582183933 is green, 00:53:31Z to 00:54:19Z.
  - The body's `## Red checks` still describes a38bd141's two deferral reds. That is accurate for that head, and this head adds no red to answer, so no root-cause trigger fires.
- Self-tests at this head (ev/selftests-head.txt):
  - `merge_train self-test: 506 checks, 0 failed`
  - `proof_watch self-test: 47 checks, 0 failed`
  - `ci-watch self-test: 18 checks, 0 failed`
  - `train.sh self-test: ok`
  - All four match the body.
- The finder's harness (RCA branch, dev/audit/harnesses/r10_rca_gate_busy_defer_4.py with its .json), replayed against `--tree` exports (`git archive`) of this head, a38bd141 and origin/main.
  - As committed, it crashes at this head with `AttributeError: 'Train' object has no attribute 'wall'` (ev/rca-harness-asis.txt). It builds `Train` by `object.__new__`, which skips `__init__`. This is a harness artefact, not a production defect: every production construction goes through `__init__`, which sets `wall`.
  - I added one line, `t.wall = <HARNESS_WALL>` (ev/rca-harness-adapter.diff). It is my adaptation, not the finder's. With the synthetic code gate completed at 21:20:00Z (ev/rca-harness-wall.txt):
    - At gate+60 s and gate+240 s, this head gives `#3293-settle-gap(synthetic) got=WAIT`, `RESULT replay defects=0 settle_gap=0 null_bad=0 scenes=7`.
    - At gate+241 s and gate+3600 s, this head gives `settle-gap got=RED`, `settle_gap=1 null_bad=0`. That is WAIT within the bound and RED after it.
    - a38bd141 gives `settle-gap got=RED` at every offset.
    - The three evidence heads read WAIT at this head (`defects=0`). `null-code-run-red` reads RED, and `null_bad=0` throughout.
    - Unadapted, origin/main gives `defects=3 settle_gap=1 null_bad=0`.
- My own replay of a38bd141's recorded runs (ev/replay_gap_wall.py, adapted from the round-3 reviewer's replay_gap.py with the Train's wall set to the cut time T), through `classify_cmd` (ev/replay-gap-wall.txt):
  - This head reads `3 WAIT` at 19:30, 20:02:45, 20:03:00, 20:03:40, 20:04:00, 20:05:00 and 20:05:50Z, and `0 GREEN` at 20:07:00Z (the swept row).
  - a38bd141 reads `1 RED` from 20:02:45Z to 20:05:00Z, WAIT at 20:05:50Z and GREEN at 20:07:00Z.
  - So the 20:03Z and 20:04Z rows the round-3 verdict named now read WAIT.
- Targeted mutants on the new lines (ev/mutants.txt; one exact single-occurrence replacement each, both self-tests run, file restored; `tree clean` at the end):
  - MF (`sweep_settling` -> False): merge_train 3 failed (20:03:00Z, exact bound, age 0); proof_watch both (g4) cases failed.
  - MG (re-run read dropped): merge_train 1 failed (re-run past the bound).
  - MH (`<=` -> `<`): 1 failed (exact bound).
  - MI (stamp-ahead guard dropped): 1 failed (the stamp-ahead null).
  - MK (green filter dropped): 3 failed (the content-FAIL null and both #3293 nulls).
  - MO (`classify_at` early return removed): 1 failed (green with no listing read).
  - MP (proof_watch wall not passed): (g4) 2 failed.
  - MQ (unstamped -> True): 4 merge_train and 3 proof_watch checks failed.
  - MJ, ML and MN survive. ML is the body's MF7, dismissed as equivalent there. MJ and MN are under Findings.
  - Nulls (comment-only edits in `sweep_settling` and in proof_watch's Train construction): every check passes in both self-tests.
- Diff hygiene: the three-dot diff has 9 files (ev/diffstat.txt) and includes dev/programme/delivery/3290.md.
  - The only new tracked file is that delivery row.
  - No VERSION, manifest, RELEASE_NOTES.md or `*_budgets.json` file is touched.
  - `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED` (ev/structure.txt).
  - No second copy of the deferral grammar is added: the readers still go through `gate_busy` -> gate.py `busy`.
- Class enumeration: `git grep -n "classify(\|classify_at(" -- tools/audit/seat` returns 78 lines at this head (ev/grep-classify.txt). The CLI `classify` and `proof_watch.required_state` both route through `classify_at`, as in round 3.
- Figures I could not re-derive: the s12 study's 56/32 SKIP counts (out of tree, and the body says so); the #3293 90-snapshot live log (the fixer's one-off logger, kept in seat scratch); and the prepr durations and diff-mutant survivor list. I did not re-run prepr or the gate (CI's heavy runs are cited instead, per fix-review step 11).
