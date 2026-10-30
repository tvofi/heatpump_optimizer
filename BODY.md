`merge_train.py` had two admission checks that disagreed. `train_add` (`add`) refused a pull request in the live train's `queue.pending.json` or the spool; the drain between batches (`Train.queue_take`) refused any pull request in an in-memory `seen` set that `batch` filled with every entry the train ever held, skipped ones included, and `Train.skip` never took a skipped entry out of `queue.pending.json`. So a skipped entry re-added at a repaired head printed `ADDED` from `add` and was then dropped by the drain as `ALREADY`, and an entry skipped in the running batch was refused by `add` from the pending layer. The field instance (triage P291): in train pid 34197, batch `20261029-193537-b4` formed right after `SKIP REPORT: 5 skipped of 10` with `ALREADY #2917`, `ALREADY #2872` and `ALREADY #2961`, and #2970, skipped because GitHub's base-branch policy refused every merge attempt, was refused twice by `add` at its reviewed head 2a25229f.

This PR replaces both checks with one predicate, `already_held(pr, verdict, seen, spooled)`, which `train_add` and `Train.queue_take` both call. It is triage P129 as amended by P189, plus P291's addition:

- The live train keeps its record in `<state>/queue.seen.json`: for each pull request, the verdict it entered at and its state (`pending`, `merged`, `ran` or `skipped`, plus the skip class). The train writes it under `QUEUE_LOCK`, and `add` reads it under the same lock. `queue.pending.json` is now derived from it: the entries still to run. Its one other reader, `review_packet.train_boarded`, keeps its format.
- Held (`ALREADY` on both sides): a spooled entry, a pending one, one this train merged or ran, and one it skipped at this same verdict.
- Admitted: a skipped entry at a new verdict head. A skipped entry at the same verdict is also admitted when the skip class is the environment's (`READMIT_SAME_VERDICT`). That means `HOLDER` (P189: the train's own worktree holder, including a pre-flight `PARK` at `recarry`, which `PreFlight` returns only for `worktree_holder`) or the new `BRANCH-POLICY` class (P291). The merge loop now gives that class to its `not merged after N attempts` stop when the last refusal is GitHub's `base branch policy prohibits the merge`.
- `Train.skip` and pre-flight parks mark the entry `skipped` in the record, so a skip is no longer pending (P189). `skipped.json` rows carry the `verdict`.
- `_batch` filters its overlap recarries and its serial tail by **its own** skips only (`self.skipped[mine:]`). Before, an entry skipped in an earlier batch and re-admitted would also have been silently left out when routed serial. Without this, the predicate fix would have moved the drop from the drain to the batch.
- An entry the train skipped and then, re-added, merged is **cured** (`Train.skip_report`, `CURED #<pr>`): its rows leave `self.skipped`, so `skipped.json`, `SKIP REPORT: N skipped` and `batch`'s rc no longer over-report a skip the train itself repaired. The cure runs inside `skip_report`, which `_batch` calls after its last `self.skipped[mine:]` read, so no batch's offset moves under it. A `post-merge` skip is the entry's last state, never `merged`, so it is never cured.
- A train started before this change wrote only `queue.pending.json`. `queue_seen_read` reads that list as pending, so an `add` from this code against a running old-code train behaves as before rather than refusing nothing.

`tools/audit/seat/instruments/merge_train.py.md` states the rule and the cure. `dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py` holds one mutant per arm. `tests/closures.json` gains the one `inert_reads` entry `tests/harness_headers.py` needs for that harness, written by `python3 tools/pr/ci_predict.py --apply-inert`.

No live train or state dir was touched. Every arm runs in the self-test's throwaway state dirs.

Part of #2725.

## Head

`5cd2f86ebb8757c8d87f97b6eb9dafc9e9f8ec90` is the code head measured here: one commit on top of the reviewed head `6e89bf7f902f701170b3393e8eaa6d27f23d73e6`, answering fix review round 1 (origin/verdict/2978). It changes `tools/audit/seat/merge_train.py` (the cure in `Train.skip_report`, its docstring paragraph, five new self-test arms), the mutant harness (M14-M19) and the instrument page. origin/main is `043b111d01c90ecb1220980df1d363c0b50bb37f`, the PR's base; `git rev-list --count 6e89bf7f902f701170b3393e8eaa6d27f23d73e6..origin/main` printed `0` when this head was cut.

## Mutation proof

`python3 dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py` copies `tools/audit/seat/merge_train.py` beside itself with exactly one span replaced and runs that copy's `--self-test`. M0, the unmutated file, must pass, and every other mutant must fail at least one check. Result at this head: `MUTANTS: 20 run, 0 not as required`.

- M1, the drain reverts to the any-seen rule: red on `P291 batch-4 replay`, `P189 HOLDER arm` and `live queue: ...`.
- M2, `Train.skip` leaves the entry pending: red on `P291 batch-4 replay`.
- M3, `BRANCH-POLICY` dropped from `READMIT_SAME_VERDICT`: red on `P291 batch-4 replay`.
- M4, `HOLDER` dropped from `READMIT_SAME_VERDICT`: red on `P189 HOLDER arm`.
- M5, the same-verdict exception reaches `add` only: red on `P291 batch-4 replay` and `P189 HOLDER arm`.
- M6, the merge stop carries no class: red on `P291 batch-4 replay` and `P291 the merge skip carries its environment class`.
- M7, a skipped entry at a new verdict is held: red on `P291 batch-4 replay`.
- M8, `_batch`'s serial tail filters by every skip of the train: red on `P291 batch-4 replay`.
- M9, a merge is not recorded `merged`: red on `live queue: ...`.
- M10, a pending entry is admitted: red on `null control: an entry still in the live batch ...` and others.
- M11, `add` reads no record: red on `P189 null control` and others.
- M12, a spooled entry is admitted: red on `add is idempotent` and others.
- M13, a pre-flight `recarry` PARK carries no class: red on `P189 HOLDER arm, pre-flight`.
- M14 (review X7), `queue_take` writes no record for a drained entry: red on `a drained entry (#2, added while batch 1 ran) re-added while its batch runs and after it merges is ALREADY ...`.
- M15 (review X1), `queue_seen_read`'s old-code fallback returns nothing: red on `an add against an old-code train (QUEUE_PENDING only, live pid) ...`.
- M16 (review X2), the `_batch` OVERLAP up-front recarry list filters by every skip: red on `--overlap: an entry an EARLIER batch skipped, re-added, is recarried up front ...`.
- M17 (review X5), `queue_seen_write`'s pending view lists every entry: red on `a rehearsal's serial entry not run is recorded ran: QUEUE_PENDING lists pending only ...`.
- M18 (review X3), a completed batch's unmerged, unskipped entry is not marked `ran`: red on the same `ran` arm.
- M19, the cure's filter deleted: red on `skipped-then-merged is cured: ...`.

The reviewer's X4 (the skip row's verdict) was already killed and stays pinned by `P291 the merge skip carries its environment class`, which now reads batch 2's `skipped.json` before the cure. X6 (the owner-pid guard in `seen_mark`) the review read as equivalent in a single-process self-test; not pinned, not a finding.

The new arms were written before their mutants were run, and each new mutant above was run against them (M14-M19 killed, M0 passing) before the whole list was re-run.

## Null control

- M14's arm: the first `add` of #2 while batch 1 runs is `ADDED` (rc 0) — the arm admits a fresh entry, so its two `ALREADY` lines are not a refuse-everything artefact.
- M15's arm: #10, absent from the old train's `queue.pending.json`, is `ADDED` beside #9's `ALREADY`.
- M16's arm: batch 1's own OVERLAP line and `SKIP #2` are read before `BATCH t-b2`, so the arm sees the entry skipped by an earlier batch, not one never skipped.
- M17/M18's arm: #3, still to run, is reported boarded by the real `review_packet.train_boarded` (loaded from its file), so an empty boarded set cannot pass it.
- M19's arm: batch 1's `SKIP REPORT: 1 skipped of 2` still counts #2; only after its merge does the train's last report read `0 skipped of 3`, rc 0.
- Things that must stay refused (from round 0, unchanged): an entry still in the live batch, a ci-skipped entry at its same verdict, and a merged one are `ALREADY` on both sides; M10 and M11 show those arms are not vacuous.

## Figures

- `merge_train self-test: 355 checks, 0 failed` -- `python3 tools/audit/seat/merge_train.py --self-test`
- `MUTANTS: 20 run, 0 not as required` -- `python3 dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py`
- `STRUCTURE RATCHET PASSED` -- `python3 tests/structure.py`
- `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, the script `tests/entities.py`, run here: `ALL 2479 ENTITY CHECKS PASSED` (`PYTHONPATH=tests/hastub python3 tests/entities.py`) -- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`
- The seams of this class (every reader or writer of the train's admission state), from `git grep -n "QUEUE_PENDING\|QUEUE_SEEN\|already_held(\|queue_seen_read(" -- tools/ .github/ tests/`, each with its disposition:
  - `train_add` and `Train.queue_take`: closed here, as both callers of `already_held`; the drained-entry record write is pinned (M14).
  - `queue_seen_write`, `seen_mark`, `queue_open`, `queue_close` and the drain's close: the record's writers, closed here; the pending-only view is pinned (M17), the `ran` mark (M18).
  - `queue_seen_read`'s old-code fallback: pinned (M15).
  - `review_packet.train_boarded` reads `queue.pending.json`, unchanged: the `ran` arm drives the real function and reads a ran entry not boarded and a pending one boarded. It is correct as is; no change.
  - The sweep (`SWEEP_SEEN`) admits only through `train_add`, so it inherits the rule.

## Red checks

- `tests / nightly-status` concluded failure on the reviewed head: it is main's red. The diff touches only `merge_train.py`, its instrument page, the mutant harness, `tests/closures.json` and the delivery row, none of which nightly-status reads. No cheaper detector is owed by this PR.

## Review round 1

Each finding of origin/verdict/2978, against this head:

- X7, a drained entry's record unpinned: fixed, arm and M14. Carry: R10-TRAIN-OVERLAP-GRADE
- X1, the old-code `queue.pending.json` fallback unpinned: fixed, arm and M15. Carry: R10-TRAIN-OVERLAP-GRADE
- X2, the `_batch` overlap-recarry filter unpinned: fixed, arm and M16. Carry: R10-TRAIN-OVERLAP-GRADE
- X5, the pending-only view unpinned and `train_boarded` unchecked: fixed, arm and M17; `train_boarded` read correct, unchanged. Carry: R10-TRAIN-OVERLAP-GRADE
- X3, the `ran` mark unpinned: fixed, arm and M18. Carry: R10-TRAIN-OVERLAP-GRADE
- `## Red checks` said none while `tests / nightly-status` was red: answered above as main's. Carry: R10-TRAIN-OVERLAP-GRADE
- A skipped-then-merged entry over-counted in `self.skipped`, `skipped.json`, `SKIP REPORT` and rc: fixed (the cure), arm and M19. Carry: R10-TRAIN-OVERLAP-GRADE
- `BRANCH-POLICY` same-verdict re-admission has no bound (a missing code-owner approval costs `merge_tries` refusals per re-add): not built here; open carry 2 (park on a missing approval before attempting) is the bound and stays open on the roster for this group. Carry: R10-TRAIN-OVERLAP-GRADE
- `review_packet.train_boarded` reads `queue.pending.json` without `QUEUE_LOCK` against a non-atomic `write_text`. Carry: dismissed: pre-existing unlocked reader; a torn read only drops boarded entries from an advisory packet line for one render, and atomic replace is a cheap optional hardening, not a defect of this PR

## Carries

Each of the group's roster carries, by index, against this part (part 2). Part 1 is #2882.

- Carry 1 (#2595's semantic-merge barrier, the overlap grade): landed in part 1 (#2882, `Train.grade_merge`). Not touched here.
- Carry 2 (#2577: 8 retries on a base-policy refusal, park on a missing approval): not in this part and still open. This part classes the stop `BRANCH-POLICY` and lets a same-verdict re-add back in; carry 2's park-before-attempt is the bound on repeated re-adds (review round 1), not built.
- Carry 3 (triage P4: diagnose the policy refusal, then widen `_carry_owner_approval`): not in this part, still open.
- Carry 4 (triage P34: the head waits read `pr_head=True`): not in this part, still open (`git grep -n "pr_head=True" -- tools/audit/seat/merge_train.py` returns nothing).
- Carry 5 (card 4, the merge-queue conditional): superseded by carries 6 and 10. The train path is taken.
- Carry 6 (the orchestrator's ruling that this barrier is not held behind R10-FLOW-MQ-PROBE): in effect. Nothing to build.
- Carry 7 (#2595 body item 6fb50ac5 and review item 98904e32): the barrier is part 1's (carry 1). The `## Head` paragraph it names belongs to #2595's body, not this tree.
- Carry 8 (triage P112: `add --front` / `add --remove`): not in this part, still open.
- Carry 9 (triage P129, one admission rule): **closed here**. `already_held` is the one predicate `train_add` and `Train.queue_take` call; arms `P291 batch-4 replay`, `P189 null control`, `live queue: ...` and the drained-entry arm, mutants M1, M7, M9 and M14.
- Carry 10 (the merge queue not adopted in round 10): taken. This is the train path.
- Carry 11 (triage P164: `stats` and `--cap auto`): not in this part, still open.
- Carry 12 (triage P184: stale holders): arm (a) is on main from R10-FLY-ABORT-OWN-MERGE (332661e99, `# mut:remergeabort`). Arm (b), `freeable` accepting an ancestor of origin, is not in this part and still open.
- Carry 13 (triage P189, amending carry 9): **closed here**. A skip leaves the pending layer; a `HOLDER` skip at the same verdict is re-admitted, any other class at the same verdict is ALREADY on both sides; arms `P189 HOLDER arm`, `P189 HOLDER arm, pre-flight`, `P189 null control`, mutants M2, M4, M10 and M13.
- Carry 14 (triage P191: sweep the record PR inside the merge-attempt loop): not in this part, still open.
- Carry 15 (#2846 review item 7bff69ba: the HOLDER exception inside the one shared predicate): **closed here**. `READMIT_SAME_VERDICT` is read only inside `already_held`; mutant M5.
- Carry 16 (triage P231: name `gh pr merge`'s refusal in the BOT line): not in this part, still open.
- Carry 17 (triage P267: pause the lowest-priority PR's CI): not in this part, still open.
- Carry 18 (triage P268: the priority mapping from the roster): not in this part, still open.
- Carry 19 (triage P289: critical-path entries skip `Train.sweep_bots`'s record step): not in this part, still open.
- Carry 20 (triage P291, the field instance for carries 9 and 13; dev/programme/triage/s6-batch63.md#P291): **closed here**, including the skipped-then-merged cure. Arms `P291 batch-4 replay`, `P291 the merge skip carries its environment class` and `skipped-then-merged is cured`, mutants M3, M6 and M19.

## Forward-carry

none

## Friction

none
