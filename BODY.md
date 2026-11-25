Round-11 roster record: puts the round-11 roster branch tip onto main so the carry file `dev/programme/carries/carry-3885.json` and the roster groups it routes to are on `origin/main`. It closes nothing by keyword and leaves #3885 and #3394 open.

## Summary

Roster state, plus one line in `tests/closures.json` listing `carry-3885.json` in `tests/entities.py`'s closure beside `carry-1645.json` (the predictor refuses an unclassified file; added by hand because `derive_closures.sh --single tests/entities.py` exceeded 580 s here, so `closures-autofix` may re-record it). Roster files: `dev/programme/carries/carry-3885.json` (new, byte-identical to the copy at `7eb9b2fd81bbe71be048e730481470de62c0932c`), `dev/programme/rosters/critical-path.json` and `dev/programme/rosters/wave-r11-groups.json`. No production or instrument code is touched.

The roster branch tip landed is `29bd37b5e52d04b5928a4abda9d5fe70d3bc2760` (`handoff/audit-r11-roster`), merged with `--no-ff` into `origin/main` `7f7e05118f`.

Why now: PR #3888 (issue #3885) routes its carries to `carry-3885.json`. `bus.sh dispatch`, `review_packet.py` and the train pre-flight run `carry_audit.py` with `--roster-ref origin/main`, so #3888 cannot get a reviewer until the file is on main (orchestrator.md section 10: a carry a PR names needs it).

## Head

`6d7018d725b0f73d840e318424465bbc691f1f9a` is `handoff/r11-roster-land`: the merge (`f125eb72819f`) of `29bd37b5e52d04b5928a4abda9d5fe70d3bc2760` into `origin/main` `7f7e05118f`.

## Mutation proof

n/a: records only; no production, test or instrument code behaviour changes.

## Null control

`python3 -I tools/audit/carry_audit.py check --body <#3888 body>`: at `origin/main` `7f7e05118f` it prints `BAD-DEST body item 6d58c80a: #3885: #3885 has no owner ...` and `BAD-DEST body item a3ad602b ...`, ending `2 finding item(s): 0 routed, 0 unrouted, 2 bad destination(s)`; at this head it prints `2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)`.

## Figures

none

## Red checks

None known at this head; the orchestrator reads the check-runs. `node tools/policy/brief_lint.mjs` at this tree exits 0. The scoped gate was not run locally; CI is the authority.

## Forward-carry

none

## Friction

carry-audit: unenforced: the instruments read carry files at `origin/main` or the roster ref, so a carry file a PR adds is unreceivable until a roster landing (P-R11-CARRY-LINE-OWN-FILE). Carry: dismissed: proposal P-R11-CARRY-LINE-OWN-FILE in the orchestrator's round-end triage
