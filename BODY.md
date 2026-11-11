Triage batch 141 rules every triage-queue line after the last line a batch cites (line 164), plus two items from session 13's notes. It holds 46 rulings, P500 to P545: 9 ACCEPT, 36 REJECT and 1 DEFER.

- **The ACCEPTs.** Each goes as one carry into an existing group:
  - P501 (plan-page leftovers) to R10-PLAN-PAGE-RESIDUE;
  - P506 (liveness-hook parity and the restart PATH) to R10-STANDING-CONTRACTS-P2;
  - P510 (DESIGN-REVIEW OWED, third instance) and P515 (the critical-path and outside watch) to R10-TICK-RESIDUE;
  - P526 (hotfix-scoped prepr) to R10-PREPR-RESIDUE;
  - P528 (the mechanical-only exemption from the three-round split) to R10-REVIEW-DISPATCH-RESIDUE;
  - P530 (the train recarries on main's cured red) to R10-TRAIN-RESIDUE;
  - P541 (the tick's main-red brief reads the job log when the check-run output is empty) to R10-TICK-RESIDUE;
  - P545 (four lessons for the playbook) to R10-ROUND-PLAYBOOK-FINAL.

  Each passes the bar on one of three routes: an owner directive, a class barrier at the third instance, or a repair of wrong behaviour that was observed.
- **The REJECTs.** Each is already built, a duplicate of a live carry, or measured below the >20 % bar. The Dependabot `ignore:` (P543) would have turned 0 of 3 pip pull requests green. The PyPI hash checker (P544) saves 0 rounds over CI's own `--require-hashes` install.
- **The DEFER.** TRAIN-SERIAL-GRADER (P533), whose benefit is unmeasured. The ruling names the measurement that would decide it.

The diff is one file against the merge base: `dev/programme/triage/s6-batch141.md`, the ruling. No product behaviour changes.

The fixers for the TICK, PREPR, TRAIN and PLAN-PAGE residue groups were dispatched at 00:24Z to 00:28Z from briefs rendered before these carries. So each carry to those groups is a part-2 item, unless that group's fixer has not handed off when the carry lands. Each carry says so in its first line.

## Head

`53637b2c37b12f7b14067238cc84749c13868fe9`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`.
- `ruling_verdict` reads ACCEPT for each of the 9 ACCEPT entries.
- A text citing each of the 9 passes `triage_refusal` (9 of 9).
- With P501's verdict flipped to REJECT, the citation is refused: "dev/programme/triage/s6-batch141.md#P501 is not an ACCEPT ruling (REJECT)".

## Null control

- P546 reads `None` and is refused as "not an ACCEPT ruling (no such entry)".
- With the file absent, a citation is refused: "the triage ruling dev/programme/triage/s6-batch141.md is not on the roster branch or origin/main".

## Figures

- `git diff --stat d08ed31049...53637b2c37b12f7b14067238cc84749c13868fe9`: 1 file.
- Every ruling figure is printed by the command or read the ruling names beside it.

## Red checks

`none`. The merge base is main `d08ed31049`; its checks are not a red in this head's ancestry. This head's checks run after its push.

## Forward-carry

none

## Friction

none
