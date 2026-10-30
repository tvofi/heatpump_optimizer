`merge_train.py` had two admission checks that disagreed. `train_add` (`add`) refused a pull request in the live train's `queue.pending.json` or the spool; the drain between batches (`Train.queue_take`) refused any pull request in an in-memory `seen` set that `batch` filled with every entry the train ever held, skipped ones included, and `Train.skip` never took a skipped entry out of `queue.pending.json`. So a skipped entry re-added at a repaired head printed `ADDED` from `add` and was then dropped by the drain as `ALREADY`, and an entry skipped in the running batch was refused by `add` from the pending layer. The field instance (triage P291): in train pid 34197, batch `20261029-193537-b4` formed right after `SKIP REPORT: 5 skipped of 10` with `ALREADY #2917`, `ALREADY #2872` and `ALREADY #2961`, and #2970, skipped because GitHub's base-branch policy refused every merge attempt, was refused twice by `add` at its reviewed head 2a25229f.

This PR replaces both checks with one predicate, `already_held(pr, verdict, seen, spooled)`, which `train_add` and `Train.queue_take` both call. It is triage P129 as amended by P189, plus P291's addition:

- The live train keeps its record in `<state>/queue.seen.json`: for each pull request, the verdict it entered at and its state (`pending`, `merged`, `ran` or `skipped`, plus the skip class). The train writes it under `QUEUE_LOCK`, and `add` reads it under the same lock. `queue.pending.json` is now derived from it: the entries still to run. Its one other reader, `review_packet.train_boarded`, keeps its format.
- Held (`ALREADY` on both sides): a spooled entry, a pending one, one this train merged or ran, and one it skipped at this same verdict.
- Admitted: a skipped entry at a new verdict head. A skipped entry at the same verdict is also admitted when the skip class is the environment's (`READMIT_SAME_VERDICT`). That means `HOLDER` (P189: the train's own worktree holder, including a pre-flight `PARK` at `recarry`, which `PreFlight` returns only for `worktree_holder`) or the new `BRANCH-POLICY` class (P291). The merge loop now gives that class to its `not merged after N attempts` stop when the last refusal is GitHub's `base branch policy prohibits the merge`.
- `Train.skip` and pre-flight parks mark the entry `skipped` in the record, so a skip is no longer pending (P189). `skipped.json` rows carry the `verdict`.
- `_batch` now filters its overlap recarries and its serial tail by **its own** skips only (`self.skipped[mine:]`). Before, an entry skipped in an earlier batch and re-admitted at a new head would also have been silently left out of the serial tail when routed serial (for example a GITHUB_TOKEN tip). Without this, the predicate fix would have moved the drop from the drain to the batch.
- A train started before this change wrote only `queue.pending.json`. `queue_seen_read` reads that list as pending, so an `add` from this code against the running train (pid 34197) behaves as before rather than refusing nothing.

`tools/audit/seat/instruments/merge_train.py.md` states the rule. `dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py` holds one mutant per arm. `tests/closures.json` gains the one `inert_reads` entry `tests/harness_headers.py` needs for that new harness, written by `python3 tools/pr/ci_predict.py --apply-inert`.

No live train or state dir was touched. Every arm runs in the self-test's throwaway state dirs.

Part of #2725.

## Head

`fbe478bbaae37e945ab4f8b24a6bfdc77d4961a2`

The self-test count and the mutant run were taken at `72cfd9049889c0af1e445466cb862b18f4755e5a`. The head adds only the `tests/closures.json` entry on top of it. `git diff --quiet 72cfd9049889c0af1e445466cb862b18f4755e5a fbe478bbaae37e945ab4f8b24a6bfdc77d4961a2 -- tools/audit/seat/merge_train.py dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py` exits 0, so both files are byte-identical at the head. `tests/entities.py`, `tests/structure.py` and `tools/pr/prepr.sh` were run at the head itself.

## Mutation proof

`python3 dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py` copies `tools/audit/seat/merge_train.py` beside itself with exactly one span replaced and runs that copy's `--self-test`. M0, the unmutated file, must pass, and every other mutant must fail at least one check. Result at this head: `MUTANTS: 14 run, 0 not as required`.

- M1, the drain reverts to the any-seen rule: red on `P291 batch-4 replay`, `P189 HOLDER arm` and `live queue: ...`.
- M2, `Train.skip` leaves the entry pending: red on `P291 batch-4 replay`.
- M3, `BRANCH-POLICY` dropped from `READMIT_SAME_VERDICT`: red on `P291 batch-4 replay`.
- M4, `HOLDER` dropped from `READMIT_SAME_VERDICT`: red on `P189 HOLDER arm`.
- M5, the same-verdict exception reaches `add` only (the drain sees the record without its class): red on `P291 batch-4 replay` and `P189 HOLDER arm`.
- M6, the merge stop carries no class: red on `P291 batch-4 replay` and `P291 the merge skip carries its environment class`.
- M7, a skipped entry at a new verdict is held: red on `P291 batch-4 replay`.
- M8, `_batch` filters by every skip of the train: red on `P291 batch-4 replay` (re-added #3, a GITHUB_TOKEN tip routed serial, is never run).
- M9, a merge is not recorded `merged`: red on `live queue: ...` (its ALREADY line names `merged by this train`).
- M10, a pending entry is admitted: red on `null control: an entry still in the live batch ...`, `P291 batch-4 replay`, `add is idempotent` and `add refused`.
- M11, `add` reads no record: red on `P189 null control`, `null control: an entry still in the live batch ...`, `P291 batch-4 replay` and `P189 HOLDER arm`.
- M12, a spooled entry is admitted: red on `add is idempotent`, `add refused` and the `carry` null control.
- M13, a pre-flight `recarry` PARK carries no class: red on `P189 HOLDER arm, pre-flight`.

The failing test came first. The final self-test, run against `origin/main`'s production code (`2ab53fe90`), fails both P291 arms. It also crashes on the HOLDER arm (`NameError: queue_seen_write`), because that arm drives the new record directly. Its replay lines reproduce the field shape exactly. At the base, `add` printed `ADDED #2` and `ADDED #3` while the drain printed `ALREADY #2: in this train already; not queued twice` and `ALREADY #3: ...`. `add` also refused `ALREADY #5: queued in the live train (pid ...); nothing added`, where #5 was the branch-policy skip.

## Null control

- Things that must stay refused, measured at the base and at the head, both green at both ends. An entry still in the live batch re-added as batch 2 starts (#5, #6) is `ALREADY` from the pending layer, rc 0, with nothing spooled (`null control: an entry still in the live batch ...`). A ci-skipped entry re-added at its same verdict (#6) and an entry this train merged (#4) are `ALREADY` on both sides (`P189 null control ...`). These arms passing at the base is what makes them null controls. Had the fix loosened the rule globally, M10 and M11 show they would go red.
- The P189 HOLDER arm's own null: a `carry`-skipped entry at the same verdict is `ALREADY` from both `add` and the drain. A `carry` pre-flight PARK records no class.
- The unchanged train: `live queue NULL CONTROL` (a one-batch queue with nothing added runs with the same lines and calls as before, and no queue line) stays green at this head.

## Figures

- `merge_train self-test: 350 checks, 0 failed` -- `python3 tools/audit/seat/merge_train.py --self-test`
- `MUTANTS: 14 run, 0 not as required` -- `python3 dev/audit/harnesses/r10_train_overlap_grade_p2_mutants.py`
- `STRUCTURE RATCHET PASSED` -- `python3 tests/structure.py`
- `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, the script `tests/entities.py`, run here: `ALL 2477 ENTITY CHECKS PASSED` (`PYTHONPATH=tests/hastub python3 tests/entities.py`) -- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`
- The seams of this class (every reader or writer of the train's admission state), from `git grep -n "QUEUE_PENDING\|QUEUE_SEEN\|already_held(\|queue_seen_read(" -- tools/ .github/ tests/`, each with its disposition:
  - `train_add` and `Train.queue_take`: closed here, as both callers of `already_held`.
  - `queue_seen_write`, `seen_mark`, `queue_open`, `queue_close` and the drain's close: the record's writers, closed here.
  - `review_packet.train_boarded` reads `queue.pending.json`. Already consistent: the format is unchanged, and a skipped entry now correctly reads as not boarded.
  - The sweep (`SWEEP_SEEN`, a per-head memory) admits only through `train_add`, so it inherits the rule. By its own design it does not re-add a head it already added, so a same-verdict environmental re-admission comes from `add` or bus.sh's `add --auto`. That is a distinct, existing behaviour, not changed here.

## Red checks

none

## Carries

Each of the group's roster carries, by index, against this part (part 2). Part 1 is #2882.

- Carry 1 (#2595's semantic-merge barrier, the overlap grade): landed in part 1 (#2882, `Train.grade_merge`). Not touched here.
- Carry 2 (#2577: 8 retries on a base-policy refusal, park on a missing approval): not in this part and still open. This part only classes the stop `BRANCH-POLICY` and lets a same-verdict re-add back in. The park-before-attempt check is not built.
- Carry 3 (triage P4: diagnose the policy refusal, then widen `_carry_owner_approval`): not in this part, still open.
- Carry 4 (triage P34: the head waits read `pr_head=True`): not in this part, still open (`git grep -n "pr_head=True" -- tools/audit/seat/merge_train.py` returns nothing).
- Carry 5 (card 4, the merge-queue conditional): superseded by carries 6 and 10. The train path is taken.
- Carry 6 (the orchestrator's ruling that this barrier is not held behind R10-FLOW-MQ-PROBE): in effect. Nothing to build.
- Carry 7 (#2595 body item 6fb50ac5 and review item 98904e32): the barrier is part 1's (carry 1). The `## Head` paragraph it names belongs to #2595's body, not this tree.
- Carry 8 (triage P112: `add --front` / `add --remove`): not in this part, still open.
- Carry 9 (triage P129, one admission rule): **closed here**. `already_held` is the one predicate `train_add` and `Train.queue_take` call. The verdict head is recorded in the record (`queue.seen.json`, with a merged mark) and in `skipped.json`'s rows. The arms are `P291 batch-4 replay`, `P189 null control` and `live queue: ...`, with mutants M1, M7 and M9.
- Carry 10 (the merge queue not adopted in round 10): taken. This is the train path.
- Carry 11 (triage P164: `stats` and `--cap auto`): not in this part, still open.
- Carry 12 (triage P184: stale holders): arm (a), the abort in `remerge_main.sh`, is on main from R10-FLY-ABORT-OWN-MERGE (332661e99, `# mut:remergeabort`). Arm (b), `freeable` accepting an ancestor of origin, is not in this part and still open: `freeable` still requires HEAD to equal origin's tip.
- Carry 13 (triage P189, amending carry 9): **closed here**. `Train.skip` takes the entry out of the pending layer (`seen_mark` rewrites `queue.pending.json`). The skip class is recorded beside the verdict. A `HOLDER` skip at the same verdict is re-admitted, and any other class at the same verdict is ALREADY on both sides. The arms are `P189 HOLDER arm`, `P189 HOLDER arm, pre-flight`, `P189 null control` and `null control: an entry still in the live batch ...`, with mutants M2, M4, M10 and M13.
- Carry 14 (triage P191: sweep the record PR inside the merge-attempt loop): not in this part, still open.
- Carry 15 (#2846 review item 7bff69ba: the HOLDER exception inside the one shared predicate): **closed here**. `READMIT_SAME_VERDICT` is read only inside `already_held`. Mutant M5 applies the exception on the `add` side only and turns `P189 HOLDER arm` and `P291 batch-4 replay` red.
- Carry 16 (triage P231: name `gh pr merge`'s refusal in the BOT line): not in this part, still open.
- Carry 17 (triage P267: pause the lowest-priority PR's CI): not in this part, still open.
- Carry 18 (triage P268: the priority mapping from the roster): not in this part, still open.
- P291 (triage s6-batch63, at `handoff/triage-s7-batch63`, not yet on the roster): **closed here**. A `merge` skip whose last refusal is GitHub's branch policy is classed `BRANCH-POLICY` and re-admitted at the same verdict. The arms are `P291 batch-4 replay` and `P291 the merge skip carries its environment class`, with mutants M3 and M6.

## Forward-carry

none

## Friction

none
