Triage batch 127 rules on the six queue lines after batch 126, P393 to P398.

- **P393: ACCEPT narrowed**, to R10-TRAIN-MERGE-LOOP-2. The train admits a superseded merge verdict, which is an instrument defect. The measured rule refuses a merge verdict when a blocked verdict at the same head carries a later-dispatched nonce. Over 59 instances, 26 are resolvable: 1 is refused (PR 3232) and 25 are admitted (21 later dispatches, 4 same-nonce revisions). The cheaper "any earlier blocked" form would refuse all 25.
- **P394: DEFER.** The replan figure measures the forecast, not a bar metric.
- **P395: ACCEPT (route only).** The DHW tank-seed carry is a finding's fix, so it keeps its route. It goes to a new size-S fly-in, or to R10-COMBI-TANK.
- **P396: REJECT.** An uncited proposal carry appears in 2 of 400 merged bodies, 0.5 %, under the bar for a new mechanism.
- **P397: DEFER.** The augmented-assignment operator gap is unmeasured.
- **P398: ACCEPT.** This is the owner directive on the subagent discovery line, ruled on form. It goes to R10-POLICY-ROLE-PACK.

The diff is three files against the merge base:
- `dev/audit/harnesses/r10_triage_p393.py`, the harness that prints every figure (INERT under `dev/audit/`);
- `tests/closures.json`, one line recording that `tests/harness_headers.py` reads it (written by `tools/pr/ci_predict.py --apply-inert`);
- `dev/programme/triage/s6-batch127.md`, the ruling.

No product behaviour changes.

## Head

`5f64290de7cad8f54128512420e8126a4eaf344a`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`. `ruling_verdict` reads P393, P395 and P398 as `ACCEPT`, P394 and P397 as `DEFER`, P396 as `REJECT`, and P399 as `None`. A carry citing P393 passes `triage_refusal`. With P393's verdict flipped to DEFER, the same carry is refused as "not an ACCEPT ruling (DEFER)". Citing P394 or P396 is refused the same way. The harness is evidence and has no consumer in the gate.

## Null control

P399 reads `None`, and a carry citing it is refused as "no such entry". A batch file that is absent is refused as "not on the roster branch or origin/main". Uncited text naming `triage P393` is refused as proposal-sourced text that cites no ruling.

## Figures

- `git diff --stat 41aa9050fc87...5f64290de7cad8f54128512420e8126a4eaf344a`: 3 files.
- Every ruling figure is printed by the harness arm the ruling names, at `3a45ec251`.
- No capped file is touched.

## Red checks

`none`. The merge base is main `41aa9050f`. This head's checks run after its push.

## Forward-carry

none

## Friction

none
