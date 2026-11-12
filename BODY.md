Removes carry-file content that landed commits answer: `dev/programme/carries/carry-1774.json` (discharged by 4efdd6cea1, as its own brief records) and entry 5 of `dev/programme/carries/carry-201.json` (`tools/audit/prepare_baseline.sh` carries the files `tests/entities.py` opens, 57a47dd9aa and d176dd1435), with their closure-table lines. Data files only.

Draft pass, ahead of the open groups. The rest of the roster's carry files are untouched here and stay where they are: carry-1645 (answered, but its removal edits the pinned grader `tools/policy/brief_lint.mjs`, so it needs a grader-only part), carry-2065, carry-2066, carry-2075, carry-1922 and the other 23 entries of carry-201.

Of the dispatch's carries, Carry 0 is partly met here (seven carry files stood at the cut; carry-1774 and one entry of carry-201 are answered, the rest listed above wait for the final pass, so the dispatch's `git ls-tree` control does not yet hold). Carry 1 (dev/README.md) and Carry 2 (machinery caps) are outside this pull request because the dispatch was deliverable 1 only.

## Head

071f551147a95b22b8591f2a0cb354e1fac6342f, on origin/main 6e100ef6980216a81eaa0438bdc215d62b19271f (unmoved since the cut, so no second prepr run).

## Mutation proof

n/a: data files only, no production line.

## Null control

At the merge base `PYTHONPATH=tests/hastub python3 tests/entities.py` passes; with only the two carry files deleted it fails `inert_reads` and one scoped-path check, which the closure-table lines removed here restore (head: all entity checks pass).

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
