# Proposal triage, session s14, batch 150 (P561)

This batch rules `s7/triage-queue-s7.txt` line 244, which arrived after batch 149. The bar and the
denominators are batch 141's.

Sources: origin/main `63bcdcaad8` (`tools/audit/seat/merge_train.py` line numbers); the live
train's `queue.seen.json` and `train.log` under the train state directory; PR 3386.

## P561: S14-TRAIN-ADD-NO-CARRY-AFTER-SKIP

Verdict: ACCEPT. It repairs an observed wrong behaviour: no `add` can bring back a pull request that
a live train skipped and that was then repaired by a main merge alone. The proposal's fix site is
wrong, though, and this ruling moves it.

Source: queue line 244 (2026-11-11T01:36:04Z, the merge seat, PR 3386).

Instances:
- **The skip.** `train.log` line 19436: `SKIP #3386 ci: #3386 red at its head: gate`, in batch
  `20261111-002834-b2`. `queue.seen.json` holds `{'state': 'skipped', 'verdict': '7628bb71a839...'}`
  for 3386 and no head.
- **The repair.** PR 3386's head is now `b874260809`. Its parents are `7628bb71a8` (the verdict) and
  `d08ed31049` (main), so the repair is a pure main merge. Command:
  `git log --format='%h %p' 7628bb71a839..b87426080936`.
- **Both adds refuse, reproduced on the live state.** `merge_train.already_held` was run over the
  live `queue.seen.json`:
  - At the old verdict it returns `skipped by this train at this same verdict 7628bb71a839; a new
    verdict head re-admits it`. A CARRY repair makes no new verdict, and `bus.sh` forbids a second
    reviewer over a CARRY range.
  - At the new head it returns None. Then `add_verdict` (lines 3948-3966) refuses: the newest
    posted merge verdict (`verdict/3386` at `1bdc23c90e`) names `7628bb71`, not `b8742608`.
  - The null control: with no seen record, the old verdict is admitted (None).
- **The premise, corrected.** The source proposes that `admit_add` accept a head the posted verdict
  carries to. It already does: an add naming the old verdict passes `add_verdict`, and then
  `admit_add` runs `app_approve.sh --carry v h` (line 3927). The blocker is `already_held`
  (lines 1278-1305), which keys a skip on the verdict alone. The skipped head was never recorded, so
  a moved head is invisible to it.
- **Not already in flight.** PR 3424 (`fix/r10-train-residue`, `175556657a`) changes 2 files with 31
  insertions, and no added or removed line touches `already_held`, `add_verdict` or `seen_mark`.
  Command: `git diff origin/main...origin/fix/r10-train-residue -- tools/audit/seat/merge_train.py |
  grep '^[+-].*already_held'`, which printed nothing.
- **The cost.** The pull request waits for the live train to end, which is one batch or more.
  This is one instance.

Cost: a skip records the head it was skipped at.
- `seen_mark(..., "skipped", ...)` at lines 3024 and 3678 stores the stopped head beside the
  verdict.
- `already_held` admits a skip at the same verdict when the pull request's head is no longer the
  skipped head. `admit_add`'s `carry` rule (`app_approve.sh --carry`) then decides, exactly as for
  any add whose verdict is not its head. A carry that fails is refused there, so a repair that
  changes content cannot ride the old verdict.
- A record with no head, written by a train started before the change, keeps today's rule.
- Self-test:
  - the 3386 shape: skipped at v, head moved by a main merge, an add at v is ADDED;
  - the same with a content-changing commit is ADD REFUSED `carry: ...`;
  - the null control: a skip at v with the head unchanged stays ALREADY;
  - a mutant dropping the head comparison fails the first case.
- `merge_train.py` has no row in `tests/structure_budgets.json`.

Binding: one carry to R10-TRAIN-RESIDUE, which holds `merge_train.py`. Its fixer was dispatched at
00:15Z and has handed off (PR 3424), so the carry takes the PART 2 ITEM prefix. Carry file:
`b150-P561.txt`.
