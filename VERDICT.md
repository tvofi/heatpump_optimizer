Fix review: blocked 853c9f47ccb8704697c96afcce0d3916919acab0 mutation-survivor: rollup_walk page-merge reads only the last page (fail-open), and the ROLLUP_Q endCursor and after-argument texts survive the self-test

bus-nonce: b5d616ce3c5ddbeb2ec965d8736f7e48

## Block

Round 2. This is a delta review over dbe75142ac7cc3e505aebfc9758102132a102804. The delta is self-test code in `tools/audit/seat/merge_train.py` only. It touches no `custom_components/` code, so the scope is not widened. Both survivors from round 1 are now killed: M2 has 1 check red and M4 has 1 check red. Survivors are listed for this head as the dispatch asks. Every survivor my mutants found at 853c9f47ccb8704697c96afcce0d3916919acab0:

- M5 fails open. In `rollup_walk` I changed `have["nodes"] = list(have["nodes"]) + list(ctx["nodes"])` to `have["nodes"] = list(ctx["nodes"])`. The self-test stays green at 660 checks, 0 failed (ev/mut-M5-drop-page1-nodes.txt). Under this mutant a two-page head reads **green** when page 1 holds a red required `gate` run and page 2 holds a green rerun. It also reads green when page 1 holds another required context (ev/probe-m5-mutant.txt). At the head both cases read red (ev/probe-m5-head.txt). Every pager fixture is too weak to tell the two apart. The page-1 nodes in `f_red`/`f_grn`/`f_mid` are non-required filler or a green gate, so dropping them changes no verdict. Fix: add a row whose deciding context sits on page 1 and whose page 2 would read green alone. Either a red required gate on page 1, or a non-gate required context on page 1.
- M9 undoes the fix in production. In `ROLLUP_Q` I changed `pageInfo{hasNextPage endCursor}` to `pageInfo{hasNextPage}`. The self-test stays green (ev/mut-M9-query-no-endcursor.txt). Real GitHub would then answer with no cursor, so the walk stops on page 1 with hasNextPage true. Every head with more than 100 contexts reads `unread` again. This fails closed, but it is the defect this hotfix closes. M4 was blocked in round 1 on the same grounds.
- M8 undoes the fix in production. In `ROLLUP_Q` I changed `contexts(first:100,after:$after)` to `contexts(first:100)`. The self-test stays green (ev/mut-M8-query-no-after-arg.txt). Real GitHub would then refuse the query for its declared but unused `$after`, or serve page 1 again. Every rollup read is unread, so this also fails closed. The fakes never read the query text. Fix for M8 and M9: one self-test row that pins the query, e.g. the faked `gh api graphql` checks that `query=` carries `endCursor` and `after:$after`.

## Findings

- M6 and M10 are equivalent mutants, not survivors. M6 changes `except` to return `merged`, and M10 makes the page cap return `payload`. Each changed return still carries hasNextPage true, or no rollup, so `platform_gate` returns `unread` either way (ev/mut-M6-*.txt, ev/mut-M10-*.txt). Carry: dismissed: equivalent mutants, no verdict changes under either
- The body's `## Mutation proof` says the M2 mutant (`if False and commit.get("oid") != head:`) turns 2 checks red, "plus the A5 page-cap row". At this head I measure 1 failed: only the new oid row (ev/mut-M2-no-oid-check-in-walk.txt). Carry: dismissed: a body figure the fixer re-states in the next body; the mutant is killed either way

## Evidence

- No pull request exists yet, so there is no review packet, no CI and no check runs to read. `## Red checks` owes nothing. `merge_train.py owed-reds` prints the required set, but this head has no PR runs to grade against it.
- RESULT self-test at head: `merge_train self-test: 660 checks, 0 failed` (ev/selftest-head.txt). This matches the body's null control, 660 checks and 0 failed.
- RESULT mutants at head (ev/mut-*.txt; the tree was restored after each, and `git status` is clean):
  - M1 `if True:` early return: 3 failed.
  - M2 oid guard off: 1 failed.
  - M3 drop the pageInfo update: 2 failed.
  - M4 cursor not sent: 1 failed.
  - M7 OSError reads green: 1 failed.
  - M11, the body's hand mutant `if merged is None and ...`: 1 failed. That is a check failure, not the NameError crash the body reports.
  - Survivors: M5, M8 and M9 (see Block). Equivalent: M6 and M10.
- RESULT M5 probe (ev/probe_m5.py). At head, page-1 red gate with page-2 green rerun reads red, and page-1 other required context reads red. Under M5 both read green. Control: a red on page 2 reads red under both.
- The new A5 serial rows are real. M4 fails "A5 serial: the train passes each page's endCursor". Round 1's M2 fixture gap (`f_old` at another oid on every page) is closed by `f_mid`, which has page 1 at H0 and page 2 at another oid.
- RESULT `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0 (ev/structure.txt).
- RESULT `git merge-tree --write-tree origin/main 853c9f47ccb8704697c96afcce0d3916919acab0`: rc 0, so it merges cleanly with origin/main at 43e95474559ca8e2188830f8775c1ddf52df964a (ev/merge-tree.txt).
- Changed vs merge base: only `tools/audit/seat/merge_train.py` (ev/changed-files.txt). VERSION, the manifest, the notes heading, the claim files and the golden fixtures are untouched.
- `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current. The body's `## Head` names 853c9f47ccb8704697c96afcce0d3916919acab0, the head reviewed.
