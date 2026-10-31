Re-routes P46, P97, P299 and P302 (R10-ORCH-BEATD closed without building them). `pulse.py` judged a standing seat's alive file by its mtime alone, so a process that is not the seat kept a role live: a 41 h orphan loop kept `merge.alive` fresh and the board printed `ok merge seat beat` across a session handover (round 10, four instances). New: `pulse.py --seat-alive SEAT=FILE[:MIN]` and `--launch-ledger FILE`; `sweep_template.md` step (1b) runs one `--seat-alive` per entry of a new optional `seat_alives` placeholder.

Carry 1 (P46): --seat-alive plus step (1b). Carry 2 (P97): per-id entries FILE.d/<id>, DUPLICATE. Carry 3 (P299): FOREIGN and --launch-ledger. Carry 4 (P302): seat_alives placeholder, one flag per overlay seat.

Closes: none (carries P46, P97, P299, P302 from dev/programme/triage/s6-batch2.md, s6-batch21.md, s6-batch68.md, s6-batch69.md).

## Head

f002cabbefdca95527e80790a73847b32d6a397e, cut from origin/main 7539d1675 (the dispatched base 811112b78 is its ancestor; the four touched files are identical between the two).

## Mutation proof

One mutant per arm, each run as `python3 -I tools/audit/seat/pulse.py --self-test` (baseline: 56 checks, 0 failed):
- per-role fallback restored (the `not fresh` arm returns ok): fails "a fresh per-role file with no id entry is FOREIGN" and "a per-role file fresh beside only a stale id entry is FOREIGN" (54 checks, 2 failed).
- newest-launch comparison dropped (`if fresh[0] != newest` -> `if False`): fails "a fresh id under an older launch is FOREIGN naming the newest", "a stop line retires a launch" and "every launch stopped has no newest" (3 failed).
- DUPLICATE count dropped (`len(fresh) > 1` -> `if False`): fails "two fresh ids of one role print DUPLICATE" (1 failed).
- P302: `entries[:4]` in `flag_text` (hard-codes four): `python3 -I tools/audit/seat/sweep_render.py --self-test` fails "an overlay with five seats renders five --seat-alive arguments" (1 failed; baseline 29 checks, 0 failed).

## Null control

At the merge base `pulse.py` has no `--seat-alive` arm, so a fresh per-role file with no id entry prints no alive line at all (the "prints ok today" state). Controls in the self-test: a stale per-role file is STOPPED; a fresh id under the newest unstopped launch is ok though an older launch has no stop line; one fresh plus one stale id is not DUPLICATE; a missing alive file is UNREADABLE, not skipped; an overlay with no `seat_alives` renders step (1b) with no `--seat-alive`, no double space, and does not fail.

## Figures

Design choices, stated: a fresh per-role file beside only stale ids is FOREIGN (unattributed beat), a stale per-role file is plain STOPPED; a role whose launches are all stopped has no newest, so any fresh id is FOREIGN (newest launch none). The id entry name is the launch nonce, in `FILE.d/<id>`. FOREIGN and DUPLICATE ride the STOPPED word (exit 1).
- `python3 -I tools/audit/seat/pulse.py --self-test` : 56 checks, 0 failed at f002cabbefdca95527e80790a73847b32d6a397e
- `python3 -I tools/audit/seat/sweep_render.py --self-test` : 29 checks, 0 failed at f002cabbefdca95527e80790a73847b32d6a397e
- `python3 tests/structure.py` : STRUCTURE RATCHET PASSED
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` : MODE: SCOPED, 0 scripts run (the self-tests above are run by governance.yml)

## Red checks

none

## Forward-carry

none

## Friction

none
