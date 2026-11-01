Design review: approve 95bdde384713962ab98d95d9a9d53f8224fdb22f

Group R10-MACHINERY-RATCHETS (L), round 2. I read the design from a detached worktree at 95bdde384713962ab98d95d9a9d53f8224fdb22f, which was the design/r10-machinery-ratchets tip at review start and was still the tip before this push. I judged it against 56630e7e6d229d960cf1b4db304d488ee20873e6. As the round-1 verdict asked, this round re-checks only the exemption paragraph, the arm list, the Gaming row and the figures.

## Re-checks

1. **Exemption paragraph (design.md:24-26, :35).** An entry counts only when the merge it exempts is the merge that added it:
   - On a push, the entry must be absent at P and present at M.
   - For the candidate, it must be absent at the merge base and present at the head.
   - In PR mode, the same rule applies to each of the base's W−1 merges.

   PR mode is defined at :13. A merged M is graded by its own P and M in both modes. Point 1 of the round-1 verdict is fixed. The condition belongs to the instrument, not to `SCHEMA`, so it still holds under the superset ruling (:35-36).

2. **Arm list (:79) and games played against the rule.** The arm list contains "an entry appended later for an already-merged PR leaves M1 and M2 unchanged". I tried five games. None survives, because the subject-number match and the absent-at-P / present-at-M test must hold together:
   - **Late append:** the entry is absent at the target's M, so it is refused.
   - **One record PR appending entries for several merged PRs at once:** each target fails at its own M. On the record PR's own M, none of the entries carries its subject number. So it is refused, and M1 stays flat (it is not lowered by 6).
   - **Entry pre-added for a future PR number:** the entry is already present at that PR's P, so it is refused. At worst this is self-harm: the PR passes in PR mode and then fails on the push. It loosens no cap.
   - **Entry on a different path, or the budgets file renamed:** the instrument reads only the budgets file. A file renamed by M makes every entry "absent at P". Even so, only the entry carrying M's own subject number matches. So the game buys nothing beyond M's own entry, and that entry still owes the >10% evidence.
   - **Rename an entry's key from #X to #Y:**
     - #Y is exempt only as its own entry, with its own evidence.
     - #X stays graded by its own M.
     - Removing #X's entry is a raise under superset, so the owner must approve it.

3. **Gaming row (:47).** "append an exemption for an already-merged PR | flat | flat" is present and is correct.

4. **Figures at 56630e7e, re-run by the note's commands.** All of them reproduce:
   - M1 / window / M2: 521 / 580 / 13624.
   - Kind split: 213 machinery, 59 production, 308 record.
   - Bands, as the largest rise above the running minimum, oldest to newest, over 150 positions of sliding 580-merge windows in a 730-merge history: M1 5 and M2 2436. The ranges are M1 516..526 and M2 11188..18162.
   - ACCEPT verdicts: 218 in 87 files.

5. **Diff from 0e83751b1.** Only design.md changed (+17/−12). The changes are the four requested above plus:
   - the base line (:3);
   - the three routed decisions recorded as decided (:35-38);
   - hot_files and `after` (:101-102), which follow the orchestrator's ordering ruling. The ref f214494449b9291146424f97ae3477e1089e4ea5 is confirmed as the current design/r10-fly-standing-contracts tip.

   Nothing else moved. The note is 130 lines and 2290 words, which is still about two pages.

## Notes for the fixer

- The rule at :13 says a merged M is graded "never by the head's files". The evidence condition at :24 resolves the path "at the head". Removing an evidence file later would therefore un-exempt an earlier merge, so that merge counts differently at a different head. This can only tighten the cap, never loosen it. Resolve the evidence path at the exempted M (for the candidate, at the head), and read before/after from the same tree. Carry: R10-MACHINERY-RATCHETS (item R5)
- The mutation proof targets (:88-95) do not list the added-by-its-own-merge test (absent at P, present at M) or the subject-number match. Add both. The new late-append arm at :79 is the arm that kills those mutants. Carry: R10-MACHINERY-RATCHETS (item R6)
- Add a self-test arm for the batch case: one merge appends entries for two earlier merged PRs, and M1 and M2 stay unchanged. The single late-append arm at :79 does not cover this. Carry: R10-MACHINERY-RATCHETS (item R7)
- Items R1-R4 from the round-1 verdict still stand (the `machinery_budgets.json` suffix, the gate restored from the base on the landing PR, `-z` destination paths for cross-boundary renames, and self-testing the rule rather than the enumerator). Carry: R10-MACHINERY-RATCHETS (item R1-R4)

Seat token count: the harness reports none.
