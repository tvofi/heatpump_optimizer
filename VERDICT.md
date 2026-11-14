Fix review: blocked dbe75142ac7cc3e505aebfc9758102132a102804 mutation-survivor: rollup_walk per-page oid guard and Train fetch cursor argument survive the self-test

bus-nonce: 2bc16771dbbafec2a13211b60c1f9591

## Block

Round 1, handoff review at dbe75142ac7cc3e505aebfc9758102132a102804 (BODY.md at handoff-body ref 547acf1eb998, `## Head` names this sha). Two of four targeted mutants on lines this diff adds survive `python3 tools/audit/seat/merge_train.py --self-test` (657 checks, 0 failed):

- M2, fail-open. Deleting `if commit.get("oid") != head: return payload` from `rollup_walk` leaves the self-test green (ev/mut-M2-no-oid-check-in-walk.txt). Under that mutant a page 2 that answers at another head is merged into page 1 and reads **green** (ev/mut-M2-no-oid-check-in-walk-probe.txt, case `p2 at another head`). That is the case where a push lands between page reads. The new A5 check's text and the body's `## Null control` both claim "a later page at another head ... unread". The fixture does not test that: `f_old` is built with `oid="f"*40` on **every** page, so page 1 is already at another head and the unchanged `platform_gate` oid check refuses it without the walk's guard. The code behaves correctly at the head (ev/probe-head.txt: `unread`), but the check claims coverage it does not give. Fix: page 1 at H0 and page 2 at another oid in the fixture.
- M4, the fix undone in production. Deleting `+ (["-f", f"after={cursor}"] if cursor else [])` from `Train.cross_check`'s `fetch` leaves the self-test green (ev/mut-M4-cursor-not-sent.txt). The train then re-reads page 1 until MAX_PAGES and reads every >100-context head `unread`, which is exactly the defect this hotfix closes. This fails closed, but the Train-level wiring of the walk is not pinned. No Train scenario feeds a multi-page rollup through `self.run` (the scenario table's `rollup=(0, json)` answers every call alike). Fix: one Train scenario whose fake `gh api graphql` answers by its `after` argument, green on page 2.

The named mutant (M1 `if True:`) and M3 (drop the `pageInfo` update) both turn the self-test red on the new A5 check, as the body says.

## Findings

- The train's other check-run readers that do not page, enumerated over merge_train.py, its imports and its callers (ev/readers.md). In the train itself: `Train.policy_refusal` (`gh pr view --json statusCheckRollup`, gh's own single page) runs only after GitHub has refused a merge. A context it misses there misnames the refusal as pending (a retry) but never lands a merge. `Train._selftest_runs` is one `per_page=100` read filtered to one check name. `record_row.py`'s automerge check is one `per_page=100` read, where a missing required check reads as pending, which fails closed. `_check_runs` and the ancestry read page through `gh_read.read_pages`, which returns `(code, None, out)` on a mid-walk failure, never a partial list. None of these fails open, so none is owed by this hotfix. Carry: dismissed: each fails closed or only misdiagnoses a refusal GitHub already made; no merge reads green from a truncated listing

## Evidence

- No pull request exists, so there is no review packet and no CI to read. `merge_train.py owed-reds` has no PR run set to grade, and `## Red checks` is owed nothing.
- RESULT self-test at head: `merge_train self-test: 657 checks, 0 failed` (ev/selftest-head.txt). This matches the body's figure.
- RESULT `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0 (ev/structure.txt). This matches the body.
- RESULT mutants: M1 red (1 failed), M2 survives, M3 red (1 failed), M4 survives (ev/mut-*.txt). The tree was restored after each run (`git status` clean).
- RESULT probes at head (ev/probe.py, ev/probe-head.txt). Required context on page 2: red reads red, pending reads wait, green reads green. A required context absent on both pages reads red. A non-gate required context on page 2 reads red. A last page holding exactly 100 contexts with hasNextPage false reads green. A page-2 read failing with OSError or ValueError reads unread through `cross_check`'s handlers, never green. A page 2 with GraphQL errors reads unread. hasNextPage true with no endCursor reads unread. A never-ending listing reads unread at the MAX_PAGES cap. Gate green on page 1 and red on page 2 reads red.
- RESULT merge: `git merge-tree --write-tree origin/main <head>` rc 0 (ev/merge-tree.txt). It merges cleanly.
- Only `tools/audit/seat/merge_train.py` changed (ev/changed-files.txt). VERSION, the manifest and the notes heading are untouched, and no claim file or golden fixture moved.
- `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the role contract is current.
- The null control "one-page head makes one read, [None]" is reproduced (probe and self-test). The control "later page at another head reads unread" holds in the code but is not pinned (see Block).
