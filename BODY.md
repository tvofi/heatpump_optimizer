Part 2 of R10-ROSTER-WRITE-SWEEP (part 1 merged as #3253). Builds the carries part 1 did not deliver in `roster_edit.py`, `roster_queue.py` and `postmerge.py`; the rest are verified at the merge base and listed below. Part of #201.

## Head

`c220b278826e7d9f5592fbc9b3ae372e33de7ff0` (merge base `51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a`, which was origin/main's tip at 2026-11-08T20:48Z). It is the repair of the round-1 block at `1a1da73c912e471b40b7b06ea94a76b71d62c100`: `11d19c47e` merges origin/main `51cd5ec8a4` into that head (no conflict), and `c220b2788` adds self-test rows only; no production line changed in this round.

## Mutation proof

Each mutant was applied to the production line, the owning self-test run, and the line restored (`cmp` against the saved copy printed `RESTORED` each time).

Round 1 (fix review at `1a1da73c`) blocked on two vacuous mutations. Answers:

- M8: `write_roster` reverting to `lint_gate(checkout, lint_cwd, path)` (no base text) now fails 2 of 256 roster_edit checks: `P435 op: set-resume beside a pre-existing lint error lands rc 0, warning it` and `P435 op: the same op adding a new bad citation refuses rc 3, naming it first (null)`. The row is the one the verdict asked for: a `set-resume` through `main()` over a planted roster whose base brief already fails the lint. Carry: R10-ROSTER-WRITE-SWEEP
- M13: `refusal_tail` ignoring the gate banner now fails 2 of 57 roster_queue checks: `refusal_tail: a lint-gate refusal reports the ERROR line, not only TOTAL` and `run: a lint-gate refusal's report line names the refused citation`. The fixture is now `write_roster`'s real shape (banner, ERROR, `CARRY:` line, blank, TOTAL, `the commit is local ...`), and a precondition row asserts its old three-line tail names no ERROR. Carry: R10-ROSTER-WRITE-SWEEP
- M14: restoring the old `_run_op` tail expression now fails 1 of 57: `run: a lint-gate refusal's report line names the refused citation` (a `run_queue` pass over a stub editor that prints that refusal and exits 3). Carry: R10-ROSTER-WRITE-SWEEP

Round-1 follow-ups:

- M16: postmerge's call site restored to the old last-line expression now fails 1 of 19: `a stage refused by the lint gate owes its ERROR line, not only the last line (P435)`. Carry: R10-ROSTER-WRITE-SWEEP
- M12: deleting the `mark_line(..., "refused")` of a parse-refused batch line now fails 1 of 58: `run --batch --mark: a malformed line is marked `#refused``. Carry: R10-ROSTER-WRITE-SWEEP
- M3 (`update-ref` after our own push): not pinned; recorded under `## Unpinned sites` as equivalent in outcome. Carry: R10-ROSTER-WRITE-SWEEP
- The fallback re-reporting a malformed line when a later batch-level failure falls back without `--mark`: not changed. Under `--mark` the line is already marked `#refused` (the M12 row), so the fallback skips it. Without `--mark` it is reported twice. Fixing that needs `run_queue` to take a line set, which is more than this repair should carry. Carry: dismissed: a duplicate report line only, with no wrong write; under `--mark` it does not occur
- The mutant_run.py figure from round 0 (11 SURVIVED, 0 KILLED) is dropped from `## Figures` and not re-run; the hand mutants above and in round 1 supersede it. Carry: dismissed: superseded by the hand mutants, as the verdict says

Round 0 mutants (all killed, as the verdict reproduced):

- Carry 19: dropping `action="extend"` from `--add` fails `set-files --add a --add b parses to ['a', 'b']` and `set-files --add a b --add c parses to ['a', 'b', 'c']`.
- Carry 17: returning `False` before the fetch in `_on_origin` fails `P409: a stale tracking ref (a rival's push) passes after the one fetch`.
- Carry 20: `new = list(errs)` (an empty base set) fails `lint gate: an unrelated write passes beside a pre-existing error, warning it` and `lint gate: the same write adding a bad citation is refused, naming it`.
- Carry 18: catching `ZeroDivisionError` in place of `(SystemExit, re_.Refuse)` in `_run_batch` fails `run --batch: a malformed line is named and refused, the rest still batch (no fallback)`.

## Null control

- M8 row: the same op adding `__bad_two__` refuses rc 3, leaves the remote branch where the first op put it, and names G-two on the first line under the banner. Under M8 both rows fail, so the pair separates the base-aware gate from the old gate.
- M13/M14 rows: `refusal_tail` of non-gate output is still its last three lines (`refusal_tail: other output is its last three lines (null)`), and the precondition row shows the old tail of the new fixture holds no ERROR, which is why the round-1 fixture could not tell old from new.
- M16 row: `refusal_detail` of plain output is its last line (existing null row).
- M12 row: without `--mark` the queue stays byte-identical (existing `run: without --mark the queue is byte-identical (null)`).
- Carry 19: one `--add a` parses to `['a']`. Carry 17: a real unpushed commit still reports "not on origin". Carry 20: a clean roster writes with `TOTAL: 0`; no base text refuses every error.

## Figures

- Self-tests at `c220b2788`: `python3 tools/audit/seat/roster_edit.py --self-test` (256 checks, 0 failed), `python3 -I tools/audit/seat/roster_queue.py --self-test` (58 checks, 0 failed), `python3 -I tools/audit/seat/postmerge.py --self-test` (19 checks, 0 failed). The rule for each count is the self-test's own `checks` line.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, and `scope.run` names `tests/entities.py`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` (the one script `scope.run` names) at `c220b2788`: ALL 2668 ENTITY CHECKS PASSED, rc 0.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh <body>` at `c220b2788`: `rc=0`; origin/main was still `51cd5ec8a4` when it ran, so no second merge or run was owed.
- Diff size: `git diff --stat origin/main...HEAD` is four files (three tools plus the delivery row).
- Carry audit at the merge base, unchanged from round 0 and not re-derived this round (the verdict did not dispute it); its owed roster-data ops are already carries of R10-CARRY-RESIDUE-2. Carry: R10-CARRY-RESIDUE-2
  - Carries 0, 2, 3, 5, 6, 10, 11, 12, 14, 15 and 21: covered by 28482eceeb6b9809e44b12d80fc994282cc21645, each by the self-test row round 0 named.
  - Carry 1: M4/M5/M6 do not exist in `r10_roster_ops_mutants.py`; the three fail-closed plants are unrecoverable from #2513's text, so no tightening is invented here.
  - Carry 4 and carry 16: code covered by 28482ece; the roster-data ops are owed to the roster seat (already carries of R10-CARRY-RESIDUE-2).
  - Carry 7: covered by `write_roster`'s in-process `privacy_refusal`.
  - Carry 9: roster-data residue, owed as `edit-brief` ops for the roster seat (R10-CARRY-RESIDUE-2). The round-0 count was not verified by the reviewer and is not restated.
  - Carry 13: (1), (3), (4) covered; (2) names `roster_drain.py`, which does not exist in the tree.
- Carries built in this PR: 17 (`_on_origin`, `update-ref` after the push), 18 (`_run_batch` names the failure and isolates a malformed line), 19 (`--add` is `action="extend"`), 20 (`lint_gate(..., base_text)`, `refusal_tail` in `roster_queue.py`, `refusal_detail` in `postmerge.py`).

## Unpinned sites

- `write_roster`'s `update-ref refs/remotes/origin/<branch>` after a successful push (M3): equivalent in outcome. Without it the next op's `_on_origin` misses, fetches the branch once, and finds the head; the `P409: two ops in one run both land after our own push` row lands both ops either way. It saves one fetch per op and changes no result.
- `_on_origin`'s first `if held()` short-circuit: equivalent (the fetch then asks again).
- The fetch's `capture_output`, the base-lint `rmtree` flags and the `refusal_detail` / `refusal_tail` truncation lengths: display bounds or cleanup flags, with no semantic pin.
- Every other added predicate is pinned by a row named under `## Mutation proof`. `tools/` sites are outside the `custom_components/` mutation lane.

## Red checks

none

## Forward-carry

none

## Friction

none
