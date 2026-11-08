Fix review: merge d96b14c349acc69869183552071adbaf7ece498e

bus-nonce: 265b7e7d61ccc8ac925280a83365baea

Round: second round (delta review) of PR #3344 (R10-ROSTER-WRITE-SWEEP part 2). The previous verdict blocked head 1a1da73c912e471b40b7b06ea94a76b71d62c100. This round reviews head d96b14c349acc69869183552071adbaf7ece498e, merge base 51cd5ec8a42abde3c223f22e9f4a0d5f35f8844a (origin/main's tip; 0 behind). I worked from a detached worktree at the head.

## Block

none

## Findings

none. Each of the previous verdict's Block and Findings items is closed at this head, or recorded in the body; see Evidence.

## Evidence

- Delta scope. The head's tree equals c220b2788's tree (`git diff c220b2788 d96b14c34` is empty). The parent merge 11d19c47e brings in origin/main 51cd5ec8a4, and main touched none of the PR's four files between 996ded2a6d and 51cd5ec8a4. So the PR's own change since round 1 is c220b2788 alone. It adds rows inside `_self_test` / `self_test` in roster_edit.py, roster_queue.py and postmerge.py, and changes no production line. The three-dot diff `git diff 51cd5ec8a4...d96b14c34` is four files: three tools plus dev/programme/delivery/3344.md (ev/threedot.txt). VERSION, the manifest, RELEASE_NOTES.md and every *_budgets.json are untouched.
- RESULT self-tests at the head (ev/selftests.txt): roster_edit 256 checks, 0 failed; roster_queue 58 checks, 0 failed; postmerge 19 checks, 0 failed. These match the body's figures. The null control is the unmutated run of the same three self-tests, all green, against the mutant runs below.
- RESULT mutants: round 1's own script, unchanged, run at this head (ev/mut_r1.py, ev/mut_r2.txt). `git status --porcelain` was clean afterwards.
  - Block 1 (M8, `write_roster` drops `base_text`): CLOSED. KILLED. It fails `P435 op: set-resume beside a pre-existing lint error lands rc 0, warning it`, a row that goes through `main()` set-resume. Under M8 the op returns rc 3 with `LINT GATE REFUSED`. The null row, `P435 op: the same op adding a new bad citation refuses rc 3, naming it first (null)`, refuses with the base-aware gate, so the pair separates old from new.
  - Block 2 (M13, `refusal_tail` ignores the gate; M14, the old `_run_op` tail): CLOSED. Both KILLED. M13 fails `refusal_tail: a lint-gate refusal reports the ERROR line, not only TOTAL` (got ` | TOTAL: 1 error(s)...`). M14 fails `run: a lint-gate refusal's report line names the refused citation`. The new precondition row asserts that the fixture's old three-line tail holds no ERROR. That was round 1's objection.
  - Finding M3 (no `update-ref` after the push): SURVIVED, as before. It is now recorded under the body's `## Unpinned sites` as equivalent in outcome: `_on_origin` fetches on a miss and the P409 two-op row lands both ops either way. I agree with that reasoning: M2, which removes that fetch, is KILLED, so the fallback the equivalence rests on is itself pinned. CLOSED, as round 1 offered.
  - Finding M16 (postmerge call site restored to the old last line): CLOSED. KILLED by `a stage refused by the lint gate owes its ERROR line, not only the last line (P435)`.
  - Finding M12 (no `mark_line(...,"refused")` for a parse-refused batch line): CLOSED. KILLED by `run --batch --mark: a malformed line is marked `#refused``. The no-`--mark` double report is dismissed in the body; it causes no wrong write. I accept that.
  - Finding on the mutant_run.py figure: CLOSED. The body drops it from `## Figures`.
  - The other round-1 mutants still kill: M1, M2, M4, M5, M6, M7, M9, M10, M11, M15.
- CI. `merge_train.py classify d96b14c349acc69869183552071adbaf7ece498e --pr 3344` printed `GREEN d96b14c349acc69869183552071adbaf7ece498e pending: none red: none` with rc 0 (ev/ci_classify.txt).
  - All check-run pages, read once with filter=all (ev/check_runs_all.txt, 58 runs): no run concluded failure.
  - Two runs concluded `cancelled`, `gate` 128862797001 and `prelude` 128862184047, and each was superseded by a green run (`gate` 128873106886 success). The review packet's `required-red` / `red-unanswered` refusal was rendered while the cancelled `gate` was the only gate run, and it does not hold at the concluded state.
  - So the body's `## Red checks: none` holds, and `pr-contract / pr-contract` is success.
- Merge. `git merge-tree --write-tree origin/main d96b14c34` exits 0 (tree b861c613) at origin/main daf8b349f, re-fetched just before this verdict. No conflict.
- Head. `git ls-remote` shows fix/r10-roster-write-sweep-p2 at d96b14c349acc69869183552071adbaf7ece498e. The body's `## Head` names it and its authored head c220b2788.
- Delivery row. dev/programme/delivery/3344.md is in the diff and reads `open`, which is current for an unmerged PR.
- tests/entities.py, run plainly (BASH_ENV removed, no workaround): NOT clean. rc 1, `ModuleNotFoundError: No module named 'homeassistant'` from tests/harness.py (ev/entities_full.txt). This is the container's environment, not the diff. With `PYTHONPATH=tests/hastub` it prints `ALL 2668 ENTITY CHECKS PASSED`, rc 0 (ev/entities_hastub.txt), which matches the body's figure. CI `tests / closures` and `tests / closure-scope` are green at this head.
- Structure. `tests/structure.py` printed STRUCTURE RATCHET PASSED (ev/structure.txt).
- Not re-derived. The body's carry-audit listing for carries 0 to 16 is unchanged from round 0, and its roster-data residue is already carried to R10-CARRY-RESIDUE-2. I did not re-verify it this round, because it is outside the blocked points.
- Finder's harness. None is committed; the group's controls are the self-test rows. My instrument is round 1's mutant script, reused unchanged.
- Forward-carry. The body says none, and this round raises nothing new.
