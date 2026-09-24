<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: two fix branches that both re-recorded `tests/mutation_budgets.json`, `tests/structure_budgets.json` or `tests/closures.json` conflicted there on every merge of main, even when they recorded different keys. A seat resolved each one by hand, and the hand resolutions were often wrong: in 3 of the 9 historical `structure_budgets.json` conflicts the committed numbers do not match what `tests/structure.py` measures at that merge commit.

After: a `ledgermerge` merge driver merges those three files key by key. Replayed over every branch-side merge since 2026-09-10, ledger conflicts fall from 48 to 3. The session-start hook installs it, the same way it installs `claimnotes`.

The driver keeps disjoint keys from both sides. Where both sides changed the same key, it merges counts as base plus both deltas, closure lists as sets, timings as the larger value, `recorded_at` as the descendant SHA, and a `last_measured` block as the later measurement. It refuses anything else, including a disposition record both sides rewrote. A refusal falls back to git's text merge, so the driver never does worse than no driver: on every historical merge the text merge resolved cleanly, it writes the same bytes. Every number it writes is still re-checked by the gate that owns the file, so a wrong merge shows up as a failed check, not silently.

How: new `tools/merge/ledger_merge.py` (driver, `--install`, `--self-test`, `--replay`), `.gitattributes` routes the three ledgers to it, `tests/entities.py` runs its self-test, and `.claude/hooks/session-start.sh` installs it. `tests/closures.json` re-records the `tests/entities.py` closure, which now reads the new file. No policy file changes. `.claude/hooks/` is code-owned by tvofi, so this needs tvofi's approving review. It is not a policy change and not a budget raise. Pairs with #1577: until the mutation ledger is keyed by content, a merge that shifts code still leaves line-keyed dispositions to re-key (the driver removes the conflict, not that work). GitHub still shows `DIRTY` until main is merged locally, because drivers never run there (#570).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01JdRqz9ze2bzL9HX952LVsA

## Head

`92e6694b1193a08dc6598866a3ae80f922a3585e`

## Mutation proof

Each mutant was applied to `tools/merge/ledger_merge.py` and `--self-test` was re-run. Every one is red, which reddens `tests/entities.py`'s check `tools/merge/ledger_merge.py --self-test passes`:

- sum of deltas replaced by `ours`: red `structure: a count both sides moved takes base plus both deltas`
- record refusal removed: red `refuses: one disposition both sides rewrote differently`, `driver: a refusal exits 1 and leaves conflict markers in %A`
- set merge ignores removals: red `closures: an addition on one side and a removal on the other both land`, `driver: resolves into %A and exits 0`
- `recorded_at` always ours: red `structure: a recorded_at pair with no ancestry is refused`, `structure: recorded_at takes the descendant SHA`
- later measurement replaced by earlier: red `mutation: a measurement both sides re-took keeps the later one whole`
- text-merge fallback removed: red `driver: a format refusal falls back to a clean text merge`
- format check removed: the self-test raises (`rc=1`), which `tests/entities.py` reports as a red check
- timings max replaced by min: red `closures: a timing both sides re-took no longer conflicts`
- new keys appended instead of placed: red `an unsorted map places a new key where the text merge would`

## Null control

Without the driver, the same replay gives 28 / 9 / 11 conflicts (mutation / structure / closures), the first column of `--replay`. On the merges the text merge resolves cleanly, the driver's output is byte-identical to the text merge's in all 259 × 3 cases. For `structure_budgets.json`, the driver's numbers were checked against `tests/structure.py` run at each of the 9 merge commits: 220 of 221 metric values match. The one miss is `coordinator_methods` at db8f670e: both sides went from 227 to 226 by removing different methods, and the driver reads two equal values as one change (226, where the tree has 225). `tests/structure.py` refuses that value, so the seat re-records it.

## Figures

- 48 → 3 ledger conflicts over 259 merges: `python3 tools/merge/ledger_merge.py --replay 2026-09-10`
- the self-test's checks: `python3 tools/merge/ledger_merge.py --self-test`

## Red checks

none

## Forward-carry

none

## Friction

none
