The 1-based "Carry N" numbers here are the packet's (roster array index N-1). The waste-study ruling (cards 3 and 7) is Carry 18 in that numbering ("Carry 17" in the orchestrator's 0-based wording): `bus.sh dispatch` reads a required-context RED as a repair owed to the fixer, not a refusal a retry loop re-tries. A WAIT head still dispatches and only RED holds. Part 2 also carries the two earlier `review_packet.py` commits already on this branch (head-note asks `policy_lint --pr-body --head`; the packet refuses a figure_lint red and a moved head).

Ruling cited: orchestrator ruling (mandate 6715477401, 2026-11-08): "a PENDING (queued or in-progress) required context does NOT hold a dispatch; WAIT dispatches, only RED holds." That supersedes the brief's pending ruling. Carry 7 (the 0-based "6"; hold on a pending required context) is therefore closed as superseded by this ruling and not built. Card 7's WAIT-dispatches arm is already the code (`0|3) ;;`) and is pinned by the existing "classify WAIT dispatches" self-test arm; I changed nothing there.

Also built on this branch (1-based numbers; the commit subjects use the 0-based ones): Carry 1 (dispatch at the handoff: `bus.sh dispatch-handoff` and `rekey`, `cloud_dispatch.py` topic-keyed reviewer, `open_pr.sh` re-key, the relay's held handoff verdict arm, policy text), Carry 5 (`roster_lib.brief_lines`), Carry 9 (`cloud_dispatch.py` roster model), Carry 12 (`body_patch.sh` Dependabot `--commits-file`), Carry 13 (`cloud_relay.sh` pending-ci verdict). Carry 7 vs 18: resolved as above.

## Approval

Owed, not yet given: this diff changes dev/governance/roles/fix-review.md and dev/governance/roles/standing-dispatch.md (fix-review.md step 7 tells a reviewer to measure the handoff tip as the head when no PR exists yet and drops the script-routing aside; standing-dispatch.md tells the dispatch seat to run `bus.sh dispatch-handoff` then `cloud_dispatch.py --role reviewer --topic` at the handoff, where only a red holds). It merges on the orchestrator's approval under mandate 6715477401 or on tvofi's review. No approval is claimed here.

## Head

e27484ffc9fb1f282974a35f02a470f657795e57 (40 hex, `git rev-parse HEAD`): 092a333d577dbc28e390e8e0979d67b63d9cd9c7 plus a clean merge of origin/main (no conflict, no code edit by this body repair). origin/main has since moved to 3fdaa9da9ab667042338fcf034147bde16b91fe4; it is not merged here, per the brief to change no code.

## Mutation proof

Mutant: `exit 5` changed to `exit 1` in the RED arm of `bus.sh dispatch`. `bash tools/audit/seat/bus.sh --self-test` then fails "a head whose required context concluded failure (classify RED) is not dispatched, owes its fixer a repair (rc 5, REPAIR-OWED, no REFUSE), and nothing is recorded". Restored, the arm passes. Failing-first was done in one step: the arm asserts rc 5, the `REPAIR-OWED` prefix and no `REFUSE`, which the old `die` (rc 1, `bus: REFUSE:`) could not satisfy.

## Null control

The same self-test keeps the null arms: classify GREEN mints and records, WAIT (rc 3) dispatches, APPROVAL-OWED dispatches, unreadable (rc 2) still refuses with `REFUSE`. A head whose only red is non-required classifies GREEN (classify reads the required set through merge_train.py), so it dispatches; non-required reds never bounce. Environment control: `tests/entities.py` at origin/main in this container fails the same three checks as BLOCKED.md named (coverage job reuse, release ZIP root, Pages tag probe), so they are environment and not this diff's.

## Figures

- `bash tools/audit/seat/bus.sh --self-test` at e27484ff: 168 checks, 0 failed. The single failure of the 092a333d run ("an ordinary append with no intervening fetch is the same commit object as before") no longer fails after the main merge.
- `PREPR_SKIP_CLOSURES=1 MUTANT_CMD="bash tools/audit/seat/bus.sh --self-test" bash tools/pr/prepr.sh` at e27484ff: rc=0 (`PRE-PR: e27484ffc9fb... rc=0`; main had moved to 3fdaa9da after this head, not merged, so this is a run against the merge base 6457496a). The diff-mutant step printed "no survivor: BASELINE FAILS: the command fails on the unedited tree; no mutant was run": the self-test passes standing alone (168 checks, 0 failed) but its baseline run inside prepr failed, so survivor count 0 means none run, and I did not diagnose why the baseline differs. Mutant wall time not applicable.
- The earlier `tests/entities.py` environment failures (coverage job reuse, release ZIP root, Pages tag probe) were measured at the old main and are not re-claimed here.

## Unpinned sites

The changed `bus.sh` RED-arm lines are pinned by the manual mutation above (the `exit 5` predicate). The Carry 1, 5, 9, 12 and 13 sites are exercised by the self-test arms of `bus.sh`, `cloud_dispatch.py`, `cloud_relay.sh` and `roster_lib.py` that each commit added; the diff-mutant outcome is in Figures.

## Carry dispositions

- Carry 1: built here (dispatch at the handoff, parts 1 and 2, policy text).
- Carry 2: delivered at main by an earlier PR, no re-fix (survey of afc1586a4).
- Carry 3: delivered at main, no re-fix.
- Carry 4: delivered at main, no re-fix.
- Carry 5: built here (`roster_lib.brief_lines` live consumers and class enumeration).
- Carry 6: delivered at main, no re-fix.
- Carry 7: superseded by the orchestrator ruling cited above.
- Carry 8: delivered at main, no re-fix.
- Carry 9: built here (`cloud_dispatch.py` reads the roster model; carry-only and record-PR reviews run sonnet).
- Carry 10: delivered at main, no re-fix.
- Carry 11: delivered at main, no re-fix.
- Carry 12: built here (`body_patch.sh` passes a Dependabot PR's commit list as `--commits-file`).
- Carry 13: built here (`cloud_relay.sh` posts a pending-ci verdict only once classify reads its head green).
- Carry 14: delivered at main, no re-fix.
- Carry 15: delivered at main, no re-fix.
- Carry 16: delivered at main, no re-fix.
- Carry 17: built on this branch (review_packet.py head-note asks policy_lint --pr-body --head, P405).
- Carry 18: built here, cards 3 and 7 (REPAIR-OWED on RED; WAIT dispatches).

## Red checks

none

## Forward-carry

none

## Friction

none
