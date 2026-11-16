Fix review: merge b8ccb27bee23f96d475de0e9034f65de3d633a97

bus-nonce: 628ed1b9ee47d917fc98643ed6da40a6

## Findings

- Note: figure: the body's `## Figures` budgets bullet prints `cap 66218 +band 500 = 66718` and `cap = 65926 + 292 growth`, but `policy_budgets.json` at this head records `corpus_tokens: 66226`. `--budgets` prints `cap 66226` at this head (ev/policy-lint-head.txt). The recorded cap is main's measured 65934 plus 292, not main's recorded cap 65926 plus 292. So the raise is 300, and 8 of those tokens are main's own excess, which sat inside main's band. The data is valid and policy_lint is at 0 errors; only the body's arithmetic is stale. Carry: dismissed: paperwork on a text-and-data head, which the fixer can correct in the body without changing the diff
- Note: figure: after main's #3566 (nudge retired) merged, the body's units figure `3952` re-derives as `3929` units, still over `80` files (ev/figures-head.txt). The `Merge order: after #3626` paragraph still says #3626 is open and that the rulings awk exits 2. #3626 has merged, and at this head the awk prints `88` and `wc -c` prints `26389`. Carry: dismissed: stale body figures, paperwork, no code or test effect

## Evidence

- Round: later round over 44766207b7, scope `delta`. Role contracts are unchanged between the merge base and main.
- Previous finding resolved: `## Red checks` now names the full context `budget-raise-gate / budget-raise-gate`. The pr-contract job reported no red at this head (classify line below).
- Delta: two merges of origin/main (c78f6127aa, b8ccb27bee). The only change to this PR's own files is `policy_budgets.json`: `corpus_tokens` goes 69625 -> 66226, and the `nudge.md` row is dropped because main retired the file. The diffs to D11.md and delivery/3642.md are byte-identical to the reviewed head's, three-dot. Three-dot against main still shows the same three files. There is no custom_components/ delta, so there is nothing to widen.
- Mutation proof re-run at this head: with `policy_budgets.json` replaced by origin/main's copy, `policy_lint.mjs` printed 2 errors (D11 126 lines > 109; D11 1939 tokens > 1647). Against main's cap the corpus sits inside the band, so that arm no longer fires. With the head's copy it printed `TOTAL: 0 error(s) across 51 policy file(s)` (ev/mutant-budgets.txt, ev/policy-lint-head.txt).
- Raise arithmetic: `--budgets` at origin/main gives corpus ~65934 against cap 65926 (ev/main-corpus.txt). At the head it gives ~66226, a growth of 292, matching the body. D11 is 126/1939, matching the recorded caps.
- Figures re-derived at this head: RULINGS.md has 88 entries and 26389 bytes; it has 189 RULINGS units; the units command exits 0 over 80 files; STRUCTURE RATCHET PASSED; RULES-SYNC ok; brief_lint rc 0 (ev/figures-head.txt).
- `git merge-tree --write-tree origin/main b8ccb27bee` is clean, rc 0 (ev/merge-tree.txt).
- VERSION, the manifest and the notes heading are untouched, and no claim file or fixture moved.
- CI: `merge_train.py classify b8ccb27bee23f96d475de0e9034f65de3d633a97 --pr 3642` exited 4: `APPROVAL-OWED b8ccb27bee23f96d475de0e9034f65de3d633a97 3 budget raise(s), first .claude/workflows/policy_budgets.json: corpus_tokens: 65926 -> 66226 (a cap went up): a raise is the owner's (0013): no decisive review by tvofi (id 70032254) on this pull request`. The only red is the budget raise's approval, which follows this verdict, so the head is judged GREEN (ev/classify.txt).
