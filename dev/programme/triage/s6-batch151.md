# Proposal triage, session s14, batch 151 (P562)

This batch rules `s7/triage-queue-s7.txt` line 245, which arrived after batch 150. The bar and the
denominators are batch 141's.

Sources: origin/main `63bcdcaad8` (`tools/audit/seat/merge_train.py` line numbers); the live
train's `train.log` under the train state directory; batch 32's P191.

## P562: S14-TRAIN-BOT-PR-VOIDS-PROOF

Verdict: ACCEPT narrowed. It repairs an observed wrong behaviour: P191's record sweep fires on a
merge refusal before the refusal is classified, so it voids a green proof in a batch that was not
stuck. The proposal's remedy is rejected: merging bot PRs only after the batch's merges would undo
P191.

Source: queue line 245 (2026-11-11T01:38:03Z, the orchestrator, train batch `20261111-002834-b2`).

Instances:
- **The proof it voided.** In `train.log`, `proof batch/20261111-002834-b2-1 at b7b5b3f3: pushed`.
  It waited through poll 12 (`t+2660s`, 44 min) and came back `red=[]`.
  - Next come `UNDRAFT #3405`, `#3405 merge attempt 1/8 refused (rc=1): ... the base branch policy
    prohibits the merge`, and `BOT #3422 MERGED 63bcdcaad8` (line 19473).
  - Then `[MAIN-MOVED] before #3405's merge: re-proving #3405, #3374, #3381, #3382, #3387, #3388 on
    63bcdcaa`, and a second proof `b2-m1-1` at `fae46a88`.
- **The premise, corrected.** The source says the bot PR merged "before the batch's own merges".
  The log and the code say otherwise: it is P191's refusal arm. At `merge_train.py` lines
  2730-2735, the first refused attempt of an entry runs `sweep_bots()`, and a merge there raises
  MainMoved. That runs before the refusal's own reading, `BRANCH_POLICY_SAID` and
  `policy_refusal` (line 2737).
- **How often it fires.** Every `BOT #N MERGED` in `train.log` was checked against its neighbouring
  lines. The refusal arm merged a record PR directly after an entry's `merge attempt 1/8 refused` 4
  times: refusals at lines 9257 (#3065), 14615 (#3269), 15301 (#3288) and 19472 (#3405). Each was
  followed by a recarry or a re-prove. A fifth, #3151 at line 8314, swept and found #3155 `pending`,
  so it merged nothing.
- **An attempt-1 refusal is not "stuck".** Of the 59 attempt-1 base-policy refusals in `train.log`:
  - 21 later merged in the same loop with no record merge;
  - 33 ended in a SKIP;
  - 5 reached a later `BOT ... MERGED`, the 4 sweeps above and #3151's unrelated later merge.
  - The command was a python pass over `train.log` that follows each refusal to its entry's next
    MERGED, SKIP or BOT MERGED line.
  - P191's own binding promised that "Sweeping only on a refusal keeps the re-prove cost to a batch
    that is already stuck". A first refusal right after `UNDRAFT` is not that.
  - A false premise would have looked like no attempt-1 refusal ever clearing without a record
    merge.
- **Why the proposal's remedy is rejected.** P191 (`s6-batch32.md`) answered s44, where a record
  PR that turned green mid-batch went unseen through 8 of 8 refusals until the train was killed.
  Sweeping only after the batch's merges brings that deadlock back.

Cost: the refusal arm sweeps only once the refusal is classified as stuck.
- In the merge-attempt loop, the `sweep_bots()` call moves below the `BRANCH_POLICY_SAID` /
  `policy_refusal` reading. It runs only when that reading is neither a wait nor an approval the
  loop can still carry, and never on attempt 1 (at attempt 2 or later). One move and one condition
  in an existing loop; no new file and no new read.
- Self-test:
  - the 3405 shape (attempt 1 refused, a green record PR open) runs attempt 2 with no BOT merge;
  - the s44 shape (repeated policy refusals, a green record PR) still sweeps and merges it, then
    recovers through MAIN-MOVED;
  - the null control: with no record PR open, attempts run as today;
  - a mutant that restores the sweep at attempt 1 fails the first case.
- `merge_train.py` has no row in `tests/structure_budgets.json`.
- Benefit: one full proof, 44 min of polls in the measured instance, each time the arm would have
  fired on a refusal that clears by itself.

Binding: one carry to R10-TRAIN-RESIDUE, which holds `merge_train.py` and is P191's seam today. Its
fixer has handed off (PR 3424), so the carry takes the PART 2 ITEM prefix. Carry file:
`b151-P562.txt`.
