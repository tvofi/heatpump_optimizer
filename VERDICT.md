Fix review: merge fbda69ef770330e43de3f2202c4bfc18eaa97671

bus-nonce: 93521581a91005e4bad77f888de5fc65
pending-ci: gate

## Review

Round 3, a delta review over 853c9f47ccb8704697c96afcce0d3916919acab0 (`review_carry.py` prints FRESH-REVIEW, so the round-2 block does not carry). The PR's own delta is commit 7090e74587bb, self-test code in `tools/audit/seat/merge_train.py` only: a `rollup_queries` record in the faked `gh api graphql`, a page-merge row and a query-text row. The rest of `git diff 853c9f47 fbda69ef` is main's merge (#3448, #3461), not this PR's patch; the three-dot diff against the merge base is `tools/audit/seat/merge_train.py` and `dev/programme/delivery/3516.md` only. No `custom_components/` line is in the PR's patch, so the scope is not widened.

Each round-2 survivor is now killed at this head: M5 (page-1 nodes dropped) 1 failed, M8 (`after:$after` removed from `ROLLUP_Q`) 1 failed, M9 (`endCursor` removed from `ROLLUP_Q`) 1 failed. The body's mutation-proof figures (1 red each for the oid guard, cursor argument, M5, M8, M9) and its null control (662 checks, 0 failed) re-derive exactly.

## Findings

- M12, `if not more or not cursor:` made `if not more:`, survives (662 checks, 0 failed). It is equivalent in verdict: a page answering hasNextPage true and no endCursor then re-reads page 1 with no cursor up to the page cap and returns a merge still carrying hasNextPage true, which `platform_gate` reads unread, as the unmutated walk does after one read. Only the read count differs (fail-closed both ways). Carry: dismissed: equivalent in verdict, fail-closed; only extra reads on a malformed answer GitHub does not serve once the query asks endCursor (M9 is killed)
- M15, the train's `if code: raise OSError` made `if False and code:`, survives (0 failed). A failed `gh` read then reaches `json.loads` on its error text, raising ValueError, which reads `unread` with the reason "the rollup answer is not JSON" rather than gh's text; the gate verdict is the same. Carry: dismissed: equivalent in verdict, only the logged reason differs
- M6 and M10 remain equivalent, as round 2 found (0 failed each; the changed return still carries hasNextPage true or no rollup, read unread). Carry: dismissed: equivalent mutants, no verdict changes under either

## Evidence

- RESULT self-test at head: `merge_train self-test: 662 checks, 0 failed` (ev/selftest-head.txt).
- RESULT mutants at head, tree restored after each and `git status` clean (ev/mutants-summary.txt, ev/mut-*.txt): M1 early return 4 failed; M2 oid guard off 1; M3 pageInfo update dropped 3; M4 cursor not sent 1; M5 page-1 nodes dropped 1; M5b page-2 nodes dropped 4; M6 0 (equivalent); M7 OSError reads green 1; M8 no `after:$after` 1; M9 no `endCursor` 1; M10 0 (equivalent); M12 0 (equivalent, above); M13 `if not cursor:` only, self-test crashes (IndexError), killed; M14 one-page cap 4; M15 0 (equivalent, above); M16 endCursor read as None 4. M8 and M9 were applied to the `ROLLUP_Q` production line alone, as the body states; the test's own literal is unchanged.
- The new query-text row reads the `query=` argument the train actually sends through `self.run`, so it pins production text, not a copy.
- RESULT `env -u BASH_ENV` `PYTHONPATH=tests/hastub python3 tests/entities.py` at head: `ALL 2709 ENTITY CHECKS PASSED`, rc 0 (ev/entities.txt).
- RESULT `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0 (ev/structure.txt).
- RESULT `git merge-tree --write-tree origin/main fbda69ef770330e43de3f2202c4bfc18eaa97671`: rc 0, merges cleanly (ev/merge-tree.txt).
- VERSION, the manifest, the notes heading, the claim files and golden fixtures are untouched (ev/changed-files.txt). `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty: the contract is current.
- The body's `## Head` names fbda69ef770330e43de3f2202c4bfc18eaa97671, the head reviewed. Forward-carry, Figures, Friction: none; carry_audit at the head reports 0 finding items.
- `## Red checks`: no required check has concluded red at this head (owed-reds set in ev/owed-reds.txt); nothing owed.
- CI at this head: `merge_train.py classify fbda69ef770330e43de3f2202c4bfc18eaa97671 --pr 3516` printed `WAIT fbda69ef770330e43de3f2202c4bfc18eaa97671 pending: gate red: none` on every poll from 00:13 to 00:42 UTC (rc 3); no required check had concluded red. The relay posts this verdict once CI is green at this head.
