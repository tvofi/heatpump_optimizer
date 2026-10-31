R10-TRAIN-OVERLAP-GRADE part 4 (#2725), in `tools/audit/seat/merge_train.py`. It covers carry 8 (P112: `add --front` and `add --remove`), carry 19 (#2992's forward-carry: the batch admission's required set, plus the review survivors R3, R5, R8 and R9), and carry 21's check. Carry 11 (P164) is forward-carried; see `## Forward-carry`.

What the train does differently:

- **Batch admission reads the PR-head set (carry 19; P34's sibling seam).** `Train._batch` reads `head_req = self.required(pr_head=True)` once per batch and passes it to `Train.admit`, whose parameter is now `head_req`. `admit`'s head wait judges that set. main's set (`req`, which leaves out PR_ONLY) still grades main (`main_green`) and the proof (`settle`), and neither of those carries a pull-request-only context. The bug stayed hidden because `PR_ONLY` is `()` at the fork. With a non-empty one, a head whose pr-contract was red would have been admitted.
- **`add --front <pr> [<verdict>]` and `add --remove <pr>` (carry 8, P112).** Both run under QUEUE_LOCK, through `spool_edit` / `spool_edit_locked`. Each prints the spool order read back from the file (`FRONT #13: spool read back: #13 #11 #12`, `REMOVED #12: spool read back: #11 #13`).
  - `--front` on a spooled PR moves its line first. On a new PR it runs `add`'s own admission, then spools the entry first in a live train, or with no live train queues it first in the train it starts.
  - `--remove` drops only that PR's line(s).
  - Every other line stays byte-identical and in order, unreadable lines included. The spool is rewritten aside and renamed (`spool_rewrite`).
  - An absent PR is refused with rc 1 and nothing is written. `--front --remove` together, or a plain `add` with no verdict, is refused with rc 2.
  - There is no priority drain. `Train.queue_take` is untouched (carries 20-22).
- **Four #2992 review survivors pinned (carry 19).** Each gets a self-test arm. Production code is unchanged:
  - R3: a critical-path entry that stops at ci under `--bot-prs` still lets the record PR merge, through `serial`'s `except Stop:` sweep.
  - R5: `CHANGES_REQUESTED` parks after one attempt, and no approval carry is tried.
  - R9: BLOCKED + APPROVED + every required context green is carried under `--approval-carry` and merges on the next attempt. Without the flag it parks naming the review.
  - R8: `Train._critical`'s live read runs against a stub `roster_lib`. It maps a critical group True and a non-critical or unmapped branch False, and reads the roster once for three entries. A read that raises gives False for every entry and is not retried.

Each roster carry (1-based, as `review_packet.py` numbers them on `handoff/audit-r10-roster`):

Carry 1: the overlap grade (#2595's countermeasure). Built in part 1, #2882, merged at 4db1d3e.
Carry 2: park instead of 8 retries on a missing approval at the live head (#2577). Built in part 3, #2992, merged at e035c66.
Carry 3: P4, park with the read reason and widen `_carry_owner_approval` under --approval-carry. Built in #2992. Its last sentence, --approval-carry in the live launch, is met on main: `RECOMMENDED` holds `--approval-carry`, and train.sh and the sweep launch it by default (0b79e8de9).
Carry 4: P34, the head wait reads `required(pr_head=True)`. Built in #2992 for `serial`. Its batch-admission sibling is closed here (carry 19).
Carry 5: the hold behind R10-FLOW-MQ-PROBE. Resolved by carry 10; no code owed.
Carry 6: the orchestrator ruling that releases the group. A resolution; no code owed.
Carry 7: #2595's root cause, item 6fb50ac5. The countermeasure is the overlap grade from #2882 (carry 1). Item 98904e32 concerns #2595's own merged body, so nothing is owed in this tree.
Carry 8: P112, `add --front` and `add --remove`. Built here.
Carry 9: P129, one admission rule. Built in part 2, #2978, merged at 89ccf73.
Carry 10: the merge queue is not adopted. A resolution: the train path was taken.
Carry 11: P164, `stats` and `--cap auto`. Not built; forward-carried (`## Forward-carry`).
Carry 12: P184. (a) remerge_main.sh aborts its failed merge: 332661e99 (R10-FLY-ABORT-OWN-MERGE, P276). (b) `freeable` frees an ancestor holder: #2992.
Carry 13: P189, the skip leaves pending, plus the HOLDER exception. Built in #2978.
Carry 14: P191, a record PR merged on refusal recovers through MAIN-MOVED. Built in #2992.
Carry 15: the HOLDER exception in the one shared predicate. Built in #2978.
Carry 16: P231, gh's refusal text in the BOT line. Built in #2992.
Carry 17: P289, critical-path entries jump the record sweep. Built in #2992.
Carry 18: P291, a BRANCH-POLICY skip is re-admitted at the same verdict. Built in #2978 (`READMIT_SAME_VERDICT`).
Carry 19: #2992's forward-carry (batch admission's required set, plus survivors R3, R5, R8 and R9). Built here.
Carry 20: P312, the priority drain. Not built here, per carry 21.
Carry 21: checked. At the fork 7539d167, and at the merge base c3a47e56 (whose `merge_train.py` is the same file), there is no priority drain: `grep -n priority tools/audit/seat/merge_train.py` prints only a comment, line 2734 at this head. R10-FLY-TRAIN-DEFAULTS has not landed P312, so there is no SHA to cite.
Carry 22: `add --front` and `add --remove` are built as written. `Train.queue_take` is untouched, so P312's sort, when it lands, keeps both verbs: they reorder only the spool file.

Alternatives not taken:
- Reading `required(pr_head=True)` inside `admit`, per entry, as part 3 did in `serial`. It lost because it costs two ruleset API reads per entry instead of two per batch, and `_batch` is `admit`'s only caller (`grep -n '\.admit(' tools/audit/seat/merge_train.py` prints its two call sites, both in `_batch`).
- A separate reorder verb. Carry 8 names flags on `add`, and a second verb would be a second writer of the spool.

Closes nothing: #2725 stays open for carry 11.

## Head

Measured at 34660f5c594b731d3099bedb13b17c888a304b43, pushed to `handoff/r10-train-overlap-grade`. It is three commits on the fork 7539d1675d7fc8b5020f90b395f4bb0c3485d5b3 (5126ec445fd6fb24279cb259e05d49fbc22b7de2), plus a merge of origin/main c3a47e5656ef858674a1fd011c0e2f039c4ed838 (read at 2026-10-31, before the final prepr run). main moved during the first prepr run, so it was merged and every check re-run. The merged delta touches `tools/pr/ci_predict.py` and triage records only. `git diff --quiet 5126ec44 34660f5c -- tools/audit/seat/merge_train.py dev/audit/harnesses/r10_train_overlap_grade_p4_mutants.py tests/closures.json && echo MERGE_TRAIN_HARNESS_CLOSURES_IDENTICAL` prints the word, so the mutant run at 5126ec44, which reads only those two files, describes this head's `merge_train.py`. The merge base is c3a47e5656ef858674a1fd011c0e2f039c4ed838.

## Mutation proof

Instrument: `python3 dev/audit/harnesses/r10_train_overlap_grade_p4_mutants.py`, landed in this PR. It makes one exact single-occurrence replacement per mutant (a span not found once is reported STALE), runs `--self-test` on a sibling copy, and prints the FAIL lines. It was run at 5126ec44 and printed `MUTANTS: 13 run, 0 not as required`. M0, the unmutated head, prints PASS. Each mutant mutates the predicate:

- M1, batch admission reads main's set (`head_req = self.required(pr_head=True)` -> `self.required()`): fails `P34 batch: a PR-only context red at the head refuses admission, naming it; nothing merges`.
- M2, `--front` appends instead (`mine + rest` -> `rest + mine`): fails the `P112 --front` arm, its null arm, the new-entry arm and `P112 --front under the lock`.
- M3, `--remove` keeps the line (`else rest` -> `else raw`): fails `P112 --remove: drops only #12's line ...` and `P112 --remove under the lock`.
- M4, absent-PR refusal dropped (`if not mine:` -> `if False:`): fails `P112 --remove null: an absent PR exits nonzero and the spool is byte-identical`.
- M5, the lock dropped (`with queue_lock(t.state):` -> `if True:` in `spool_edit`): fails `P112 --front under the lock` and `P112 --remove under the lock`.
- M6, a new `--front` entry in a live train not moved first: fails `P112 --front on a new entry: admitted, spooled first ...`.
- M7, `--front` with no live train queued last: fails `P112 --front with no live train: the train it starts runs the entry FIRST ...`.
- M8 (R3), `serial`'s stop-path sweep -> `pass`: fails `P289 serial, a critical-path entry that stops at ci: the record PR still merges, the entry does not`.
- M9 (R5), `rd != "CHANGES_REQUESTED"` -> `True`: fails `carry 2 null (CHANGES_REQUESTED): ...`.
- M10 (R9), `or ms == "BLOCKED"` dropped: fails both `carry 2 (BLOCKED, APPROVED, all green)` arms.
- M11 (R8), `_critical` -> `return False`: fails `R8 _critical: the live read maps fix/a (critical group) True ...`.
- M12 (R8), the first-read sentinel `self.cp_read = ({}, set())` -> `pass`: fails `R8 _critical null: a roster read that raises is nothing critical for every entry, and is not retried per entry`.

Failing test first: the two `P34 batch` arms and the R-arms were written before or against the unmutated production line. M1 restores the fork's line and fails the new arm.

## Null control

- P34 batch: the same world with pr-contract green at both heads admits both and merges them on one proof (`P34 batch null: ...`).
- P112: a plain `add` into the live train appends last (`P112 null: a plain add appends last`). `--remove` of an absent PR leaves the spool byte-identical (`read_bytes()` compared). The lock arm's own null control runs the same edit without the lock (`spool_edit_locked` called directly, which is the M5 shape), and the concurrent add's line is lost (`P112 --front null (no lock, the mutant) ...` and `P112 --remove null ...`). So the locked arm measures the lock, not the timing.
- R8: a raising roster read gives "nothing critical", today's order.
- Every self-test arm that existed at the fork still passes: 381 checks there, all of them in the 400 here.

## Figures

- Self-test: `python3 tools/audit/seat/merge_train.py --self-test` prints `merge_train self-test: 400 checks, 0 failed` at 34660f5c (and at 5126ec44). In a detached worktree at the fork 7539d167 (whose `merge_train.py` is the merge base's: the merged delta does not touch it) it prints `merge_train self-test: 381 checks, 0 failed`. The count is checks executed (some arms loop), not call sites.
- Mutants: `python3 dev/audit/harnesses/r10_train_overlap_grade_p4_mutants.py` prints `MUTANTS: 13 run, 0 not as required` at 5126ec44. M0 PASS and M1-M12 KILLED, each with the FAIL lines above.
- Gate scope: `python3 tests/closure.py select --diff c3a47e5656ef858674a1fd011c0e2f039c4ed838 --workdir "$D"` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out` and names `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2493 ENTITY CHECKS PASSED`.
- `run_always` lines: `python3 tests/env_drift.py --claims-only c3a47e56...` exits 0, `python3 tests/closure.py selftest` exits 0 and `python3 tests/layout.py` exits 0. `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` prints `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tools/pr/ci_predict.py --apply-inert` applied one entry (the new harness as an inert read of `tests/harness_headers.py`, in `tests/closures.json`), then printed `CI PREDICT: no closures, fast, governance or instrument red predicted against 7539d1675d7f`. Re-run after the merge, `python3 tools/pr/ci_predict.py` prints the same line against c3a47e5656ef.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`. No metric was re-recorded and no budget was touched.
- `python3 tools/audit/archscore/score.py --diff c3a47e5656ef858674a1fd011c0e2f039c4ed838` prints `Architecture score: dS +0.0000 NULL`. No gain is claimed.
- Class rule, step 8. Let E be the line of `def _self_test` in merge_train.py (3343 at this head).
  - Required-set reads: `awk -v E=$E 'NR<E && /self\.required\(/' tools/audit/seat/merge_train.py` returns 4 sites. `serial`'s head wait (`pr_head=True`) was closed by #2992. `policy_refusal` (`pr_head=True`) was closed by #2992. `_batch`'s `req = self.required()` grades main and the proof, which carry no PR-only context, so it is correct as main's set. `_batch`'s `head_req = self.required(pr_head=True)` feeds `admit` and is closed in this diff. Null control: the same rule at the fork 7539d167 returns 3 sites, with `admit` fed main's set, which is the open seam.
  - Spool writers: `awk -v E=$E 'NR<E && /QUEUE_SPOOL/ && !/^QUEUE_SPOOL/' tools/audit/seat/merge_train.py` returns 10 lines. Every write goes through `spool_append` (append), `spool_rewrite` (`--front` / `--remove`), `train_add`'s unlink after it moves the spool into a started train's queue, and `queue_take`'s unlink after the drain. All of them run under `queue_lock`. The rest are reads and log text. `git grep -n "queue-add" -- . ':!tools/audit/seat/merge_train.py' ':!dev/programme/triage'` returns only the roster's carry text, so no other tool or doc tells anyone to hand-edit the spool.

## Unpinned sites

n/a: every production line this diff adds is pinned by a mutant in `dev/audit/harnesses/r10_train_overlap_grade_p4_mutants.py` (M1-M7). The `tools/` lane is outside mutation-autofix, so this is the in-tree harness fixer.md step 2 names.

## Red checks

none: no check has run on this head yet. `ci_predict.py` predicts no red.

## Forward-carry

- Carry 11 (P164: `merge_train.py stats` and, only past 0.5 h/day lost, `--cap auto`) is not built here. It needs "wall time lost to drop-and-retry, over a window", and the train's log lines carry no timestamps. `Train.log` is `print` into `train.log` through train.sh, and only the batch tag (`BATCH <yyyymmdd-hhmmss>`) holds a time. So the figure the cap decision keys on cannot be derived from the log, and no train log is in the tree or reachable from this container. The next stage must first give each train log line a UTC stamp, or define lost time from batch tags, before `stats` can measure it. Carry: R10-TRAIN-OVERLAP-GRADE

## Friction

- fixer.md-step-3: unclear: the carries' instances (#2753's hand reorder, #2804's hand removal, #2992's review survivors) are train logs and review notes, not finder harnesses, so there is no finder harness to re-run. The self-test fixtures model each instance. Carry: dismissed: no finder harness exists for instrument carries; the fixtures are the measurement
