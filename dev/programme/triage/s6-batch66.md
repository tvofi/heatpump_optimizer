# Proposal triage, session s7, batch 66 (P297)

The rolling batch (V182) after batch 65 (#2981, merge verdict at `bd36aebf`, not yet merged).
Facts were read at origin/main `1148ee635`, at #2977's head `967abc3e`, and in the live train
log.

## P297: a recarried head's claim file is refused as not the union

Verdict: ACCEPT as already ruled. This is P290 (`s6-batch62.md`). Its fix is option (a), a
resolution the claimnotes driver produces, computed rather than compared byte for byte against
the union. That fix is built: it is R10-FLY-CARRY-CLAIM-DRIVER's pull request #2977, approved and
in the live train. The three new instances carry under it, as measured below. No new group or
carry. (b) is REJECTED. (c) is not owed: the cause is measured.

Source: the orchestrator's message of 2026-10-30, P297. The class has 4 instances: #2917, #2975,
#2955 and #2976. When the train recarries a verdicted head onto main, `app_approve.sh --carry`
refuses because `tests/golden/claimed_drift.txt` "resolves to something other than the union".
Each refusal costs a resolution-delta reviewer seat and about 1 h of train idle.

Instances, from `merge_train/train.log` and re-run here:
- **The field refusals.** The train log has 9 `SKIP #<n> carry:` lines naming
  `claimed_drift.txt`, plus one `ADD REFUSED #2917` (line 1984) whose text is cut short.
  - 6 of the `SKIP` lines are #2917's, the case P290 measured.
  - The new ones are:
    - #2975, `f6ff3e56 -> 2c162670`, at log line 2582;
    - #2955, `eab999bc -> 502b0df3`, at line 2799;
    - #2976, `1381df1f -> ebbdcaa6`, at line 2885.
- **The fix carries all three.** `bash tools/pr/app_approve.sh --carry <verdict> <merge>
  origin/main` was run from a checkout of origin/main `1148ee635` and from one of #2977's head
  `967abc3e`, against the same origin/main.
  - #2975, #2955 and #2976 each give rc 1 on main (`... resolves tests/golden/claimed_drift.txt
    to something other than ...`).
  - Each gives rc 0 at `967abc3e` (`CARRY: yes ... every merge the automatic one ...`).
  So the mechanism P290 named (the driver takes the side that changed the claim list, and the
  check demands the union) is the cause of all four instances. It is not inherited claims or the
  stamp's emptied list.
- **The fix's state.** R10-FLY-CARRY-CLAIM-DRIVER is `in-progress` on the roster branch, with PR
  #2977. #2977 reads `reviewDecision: APPROVED`, `mergeStateStatus: BLOCKED`, head `967abc3e`.
  That head is the clean merge of its verdicted head `9f0e4478` (`Fix review: merge 9f0e4478`)
  with origin/main `1148ee635`. The live train is on it now (`beat: waiting CI at 967abc3e`).

Cost and benefit:
- **(a) is built.** It costs nothing more than #2977's merge. Benefit, measured: every refusal of
  this class seen in the train log carries under it.
- **(b) REJECTED.** Re-running claims-autofix before the carry check would rewrite the claim file
  on a verdicted head. That moves the head the verdict names, so it would then need a carry of
  its own.
- **(c) not owed.** The cause is measured at all four instances, which is what an RCA seat would
  establish first.

Binding:
- **The barrier this audit class owes is #2977.** The class reached 3 or more instances, which
  owes a barrier rather than a refusal, and #2977 is in the live train. No new seat or group.
- **The lever is #2977's merge.** Its train run comes first. A second claim-file refusal of #2977
  itself would be this class refusing its own fix. If it happens, the orchestrator decides at
  once, rather than through a resolution-delta seat.
- **After #2977 merges.** #2975, #2955 and #2976, if still parked, re-carry under the new rule on
  the train's next add, with no fresh reviewer seat. A refusal then would be a new mechanism and
  would come back here.
