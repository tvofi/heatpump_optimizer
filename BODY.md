Part 2 of R10-FLY-TRAIN-DEFAULTS: the folded after-merge bookkeeping (R10-FLOW-POSTMERGE, R10-FLY-RECORD-BEAT), the CARRIED HEAD refusal (P96), the spool drain order (P312) on both seams that turn the spool into a batch, the CI-review wait (P331) and the standing-merge.md statement (P330). Policy files changed (standing-merge.md, nudge.md): merges on the owner's approving review. Closes none.

Repair round 3 answers verdict/3090 round 2 (blocked at 3e6bf423086464ee6207f98adab18861e81871d4, class-open): `train_add`'s start path built a new train's first batch as `spooled + [entry]`, never through `Train.drain_order`, so `add --priority` over a stopped train's leftover spool ran the HOTFIX last.

The seam, named: the spool becomes a batch at exactly two places, enumerated by `grep -n "spool_read(" tools/audit/seat/merge_train.py` over production lines (the self-test's reads excluded): `Train.queue_take` (already through `drain_order`, pinned in round 2) and `train_add`'s start path (closed in this diff: `queue = t.drain_order([entry] + spooled if front else spooled + [entry])`, marked `# mut:start`). The third production `spool_read` caller, `queue_close`, only names leftovers in a `NOT RUN` line and builds no batch; `spool_order` prints the read-back. Both batch-building seams now call the one helper, so there is no second ordering copy. A fronted entry is placed first in the list it sorts and carries `front`, so the stable sort keeps it first in the top tier, as before.

Carries of the brief, each answered in this diff:
Carry 1 (part 2 and P312): the after-merge bookkeeping is `postmerge.py`/`record_beat.py`, run by `merge_pr.sh` and the train's landing; the spool drains `--priority`/`--front`, then critical-path, then arrival, on the live drain (`queue_take`) and on the start path (`train_add`), both through `Train.drain_order`.
Carry 2 (P330): standing-merge.md's Instruments paragraph states the train-join rule, within its cap, no raise.
Carry 3 (P92): `set-stage owed <GROUP> <sha>` with the group from `record_beat.resolve_group` (equality, then resume.pr, else no-group); printed only when the roster sync fails (a departure, disclosed below). Mutants record_beat-2 and the R9-FR-1/R9-FR-10 style fixture pin it.
Carry 4 (P331): review_settle time-bounded and policy_refusal arm 2, fixtures for the #3031 and #3039 shapes and the null parks.
Carry 5 (the brief's remaining sub-carries): all in the sections above. Carry: R10-FLY-TRAIN-DEFAULTS

## Head

f68107fd0c59bdbc71eae71ccec48bb9d6b175bb

Fast-forward of the PR head 3e6bf423086464ee6207f98adab18861e81871d4 (two commits: the start-path fix with its self-test arm and in-tree mutant, then the instrument doc sentence). origin/main at ea59e9a09de56447326ae71d8a45fec81c3cc275 (moved from a568a2e12 during the work; 2026-11-02T16:03Z); `git merge-tree --write-tree origin/main HEAD` rc 0, its only note `LEDGER-MERGE: resolved tests/closures.json`, so main is not merged in (the brief: merge only on a conflict). prepr.sh ran after the move, against this main. Every figure below was re-taken at this head in this round.

## Mutation proof

- The start-path mutant: `# mut:start` reverted to `queue = [entry] + spooled if front else spooled + [entry]` (in-tree `dev/audit/harnesses/r10_seat_selftests_mutants.py merge_train-42`, and planted by hand). `merge_train self-test: 421 checks, 2 failed`: FAIL "P312 start path: a stopped train's spool [#13 critical, #11] plus `add #14 --priority` starts the train with the HOTFIX first, then the critical #13, then #11" and FAIL "P112 start path: `add #14 --front` over a spool whose #11 is a HOTFIX keeps first place, then the HOTFIX #11 (the same tier), then the critical #13". Restored; `git status` clean.
- `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py merge_train-34 merge_train-35 merge_train-36 merge_train-37 merge_train-38 merge_train-39 merge_train-40 merge_train-41 merge_train-42`: every one KILLED, `RESULT survivors=0`.
- The round-2 reviewer's mutants (verdict/3090 `evidence/mut2.py`, sha1 f6270262c1b64e9b47d8ea1ef0a441c33df108a0, plus the start mutant as S1; run copy sha1 8221fe9ab59f524d4207ad08a16805a9f6cdae97), from a detached worktree at e8125e19f: R1 KILLED (1 failed), R2 KILLED (1), R3 KILLED (2), R4 KILLED (2), B1 KILLED (7), R5 KILLED (5), R6 KILLED (1), F1 KILLED (3), F2 KILLED (2), F3 KILLED (2), S1 KILLED (2); each `merge_train self-test: 421 checks`. No survivors.
- Earlier rounds, unchanged by this diff: `merge_pr.sh` comparison made unconditional fails "a verdict for another head refuses CARRIED HEAD and posts nothing"; `r10_seat_selftests_mutants.py postmerge-1 postmerge-2 record_beat-1 record_beat-2 S10`: RESULT survivors=0 (round 1, not re-run).

## Null control

- A plain (non-priority, non-front) add over a stopped train's spool [#13 critical, #11]: the start queue is [13, 11, 14], equal to `drain_order` of the same entries, at the old head and at this head; the self-test arm "P312 start path null" pins it and it stays ok under the start mutant (the mutant fails only the two arms above), so the fix changes nothing where arrival and drain order already agree.
- Finder's harness, the `none` arm: `start_queue=[3, 1, 4] drain_order_of_same=[3, 1, 4]` at both ends; the `front` arm `[4, 3, 1]` at both ends.
- Unmutated head: `merge_train self-test: 421 checks, 0 failed`.

## Figures

- Finder's harness, exported from verdict/3090 as `$EXPORT/evidence/start_path.py` (sha1 c68cdc3a3e4abfc098e63a301679ccd26c42c464; a reviewer's evidence file, kept out of the tree), run from the repo root at each end as `python3 $EXPORT/evidence/start_path.py`. At 3e6bf423086464ee6207f98adab18861e81871d4: `RESULT priority: rc=0 start_queue=[3, 1, 4] drain_order_of_same=[4, 3, 1]`. At e8125e19feda6f5ef3e306c148fed471a7e7bd3f (the fix; f68107fd0 adds only a doc sentence): `RESULT priority: rc=0 start_queue=[4, 3, 1] drain_order_of_same=[4, 3, 1]`. `front` and `none` unchanged (Null control).
- Class census: `grep -n "spool_read(" tools/audit/seat/merge_train.py`, production lines: `spool_order`, `train_add` (start path: closed here), `Train.queue_take` (guarded, round 2), `Train.queue_close` (names leftovers, builds no batch). No seam left un-dispositioned.
- `python3 -I tools/audit/seat/merge_train.py --self-test`: 421 checks, 0 failed (418 at 3e6bf423 plus the three start-path arms)
- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`; scope.run names `tests/entities.py` and `tests/harness_headers.py`
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2497 ENTITY CHECKS PASSED
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: ALL 112 HARNESS HEADER CHECKS PASSED
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED
- `node tools/policy/policy_lint.mjs --budgets`: rc 0, standing-merge.md and nudge.md within cap, no raise
- `git diff $(git merge-base origin/main HEAD)...HEAD -- tests/golden/claimed_drift.txt tests/golden/card_claimed_drift.txt`: empty (the branch claims nothing; a two-dot difference from origin/main is main's own later claim commits). VERSION, the manifest version and the RELEASE_NOTES.md heading untouched.
- `bash tools/pr/prepr.sh body.md`: `PRE-PR: f68107fd0c59bdbc71eae71ccec48bb9d6b175bb ... rc=0` on this committed head; the run_always lines (`tests/env_drift.py --claims-only`, `tests/closure.py selftest`, `tests/layout.py`) pass

Not as written in the brief (earlier rounds, still true): the `set-stage owed <GROUP> <sha>` line prints only when roster_sync fails, not after every merge. The tick-finder control is a full-sha substring test, not a run of the tick's code. `r10_main_gate_replay.py` reads live GitHub and read the same with and without --pending; it exercises code this diff does not change. Main's suite state is read through `merge_train.py classify --main` (no third rule). No ledger-event writes beyond postmerge-owed open/close.

Alternatives for the start path, and why each lost: a second sort at the start path (a copy of the key) duplicates the concept the brief forbids; ordering only the spooled part and appending the entry leaves the HOTFIX last; calling `drain_order` on `spooled + [entry]` for a fronted add would let a spooled HOTFIX overtake the fronted entry, against P112's "FIRST in the next batch". Taken: one call to the existing helper over the list the start path already built.

## Red checks

none: the PR head 3e6bf423086464ee6207f98adab18861e81871d4 carries 55 check runs on one page of 100, every one concluded success or skipped (none failure, cancelled, timed_out or action_required). This head, f68107fd0c59bdbc71eae71ccec48bb9d6b175bb, has no concluded run before the handoff moves the PR to it.

## Forward-carry

none

## Friction

none

## Approval

Policy files changed: `dev/governance/roles/standing-merge.md` (P330's train-join statement, within its cap) and `dev/governance/roles/nudge.md` (step 12 cut to its exceptions). Owner approval is owed: this pull request merges only on tvofi's approving review at its head, or under a mandate in force scoped `all` (6329234399). This seat claims none.
