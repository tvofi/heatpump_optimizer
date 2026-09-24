<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: two fix branches that both re-recorded `tests/mutation_budgets.json`, `tests/structure_budgets.json` or `tests/closures.json` conflicted there on every merge of main, even when they recorded different keys. A seat resolved each one by hand, and the hand resolutions were often wrong: in 3 of the 9 historical `structure_budgets.json` conflicts the committed numbers do not match what `tests/structure.py` measures at that merge commit.

After: a `ledgermerge` merge driver merges those three files key by key. Replayed over every branch-side merge since 2026-09-10, ledger conflicts fall from 60 to 0. The session-start hook installs it, the same way it installs `claimnotes`.

The driver keeps disjoint keys from both sides. Where both sides changed the same key, it merges counts as base plus both deltas, a fractional cap (`max_survivor_fraction`) as the lower of the two, closure lists as sets, timings as the larger value, `recorded_at` as the descendant SHA, and a `last_measured` block as the later measurement. In the mutation ledger it first matches each disposition across the three sides by file, operator and pinned `old` text, so a re-key (#1577's content anchors, or a line shift) is not read as a deletion plus an addition, and a branch's own rows and edits survive it. It drops `unpinned_sites` when one side retired it, and where one side only appended to the `reason` prose it keeps both texts. It refuses anything else, including a disposition record both sides rewrote or one side deleted while the other rewrote it. A refusal falls back to git's text merge, so the driver never does worse than no driver: on every historical merge the text merge resolved cleanly, it writes the same JSON value, and the same bytes in all cases but one, where it writes a raw non-ASCII character (`ö`) escaped, as the ledger's writer does. Every number it writes is still re-checked by the gate that owns the file, so a wrong merge shows up as a failed check, not silently.

How: new `tools/merge/ledger_merge.py` (driver, `--install`, `--self-test`, `--replay`), `.gitattributes` routes the three ledgers to it, `tests/entities.py` runs its self-test, and `.claude/hooks/session-start.sh` installs it. `tests/closures.json` re-records the `tests/entities.py` closure, which now reads the new file. No policy file changes. `.claude/hooks/` is code-owned by tvofi, so this needs tvofi's approving review. It is not a policy change and not a budget raise. Pairs with #1577: until the mutation ledger is keyed by content, a merge that shifts code still leaves line-keyed dispositions to re-key (the driver removes the conflict, not that work). GitHub still shows `DIRTY` until main is merged locally, because drivers never run there (#570).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Head

`398df490b39d489912c0ef281bba8d4eed60d417`

## Approval

`.claude/hooks/session-start.sh` is code-owned, so tvofi's approving review is
owed before merge. This is not a policy change and not a budget raise.

## Mutation proof

The reviewer's 11 mutants (`/mnt/project-files/fix-helper/review-1593/mutproof-spec.json`) and 8 more for the round-2 rules were each applied to `tools/merge/ledger_merge.py`, and `--self-test` was re-run; `tests/entities.py` runs it as `tools/merge/ledger_merge.py --self-test passes`. 18 of 19 are killed:

- M1, delete-vs-modify takes the deletion: red `refuses: a disposition one side deleted and the other rewrote (ours deletes)` and `(theirs deletes)`
- M2, the set merge drops theirs' additions: red `closures: a file only theirs added lands beside ours' removal`
- a cap raised on both sides takes the higher, or goes back to the sum: red `mutation: a cap both sides raised takes the lower raise, not the sum`
- re-key pass off: red `re-keyed ledger: the branch's edit lands on main's key` and `re-keyed ledger: a row both sides re-keyed appears once, under main's key`
- a key only the branch moved takes main's: red `re-keyed ledger: a row only the branch re-keyed keeps the branch's key`
- both moved, always theirs: red `re-keyed ledger: when both sides moved a row, the anchored key wins`
- retired count refused again: red `pre-#1577 branch: a count main retired is dropped, not refused`
- append rule off, or the appended text dropped: red `pre-#1577 branch: its addition to `reason` is appended to main's text`
- M3 to M10 stay killed, as in round 1
- M11 survives, as in round 1. It skips the write read-back, a defensive check that no test input can fail.

## Null control

Without the driver, the replay gives 36 / 11 / 13 conflicts (mutation / structure / closures), the first column of `--replay`. On the 765 file merges the plain text merge resolves cleanly, the driver writes the same JSON value in all 765 and the same bytes in 764. The exception re-escapes a raw `ö` (fed09e23, `tests/mutation_budgets.json`), as the ledger's writer does.

On the 36 mutation-ledger conflicts, the driver's dispositions match the hand resolutions row for row in 33, compared by file, operator and row content. In the other 3 the seat also reworded a row's `reason` during the merge. #1572's own merge of #1577 (87045701) is one of the 33: the driver's result plus `tests/mutation_table.py --normalize` equals the hand resolution in every disposition (108, 0 retired keys naming no site). The only difference is that it keeps the branch's appended `reason` text.

For `structure_budgets.json`, the driver's numbers were checked against `tests/structure.py` at each historical merge commit: 220 of 221 metric values match. The miss is `coordinator_methods` at db8f670e: both sides went from 227 to 226 by removing different methods, and the driver reads two equal values as one change (226, where the tree has 225). `tests/structure.py` refuses that value.

The full gate at this head passes: `ALL TEST SCRIPTS PASSED`, `ALL 1867 ENTITY CHECKS PASSED`.

## Figures

- 60 → 0 ledger conflicts over 275 merges: `python3 tools/merge/ledger_merge.py --replay 2026-09-10`
- the self-test's checks: `python3 tools/merge/ledger_merge.py --self-test`

## Red checks

none

## Forward-carry

none

## Friction

none
