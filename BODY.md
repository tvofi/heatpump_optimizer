Part of #201. R10-RELAY-SWEEP: the relay's residue on one seam, tools/audit/seat/cloud_relay.sh (fold of R10-RELAY-HANDOFF-ARM, R10-FLY-RELAY-DELIVERED-GUARD and the open carry of R10-FLY-RELAY-REVIEW-FF).

Carries: 0 (body-only path stays inside handoff_arm, unchanged for the beat's job), 2 (levels before the serial loops, tick GAP line), 3 (unapplied body-only line), 4 (M2/M5 rows and guide text), 5 (holder in its own process group), 6 (delivered guard, state-dir line, RCA note), 7 (HELD-BODY, stale hold lines), 8 (case-collision refusal in relay(), bus.sh push-verdict and unpack, fix-review.md sentence).

Decisions taken without the owner: carry 1's ledger disposition for the handoff-body ref is not written (the handoff-no-pr fold already rides a body ref on its code ref); carry 6's 'committed after the probe' condition had no historical case and is dropped, not synthesised.

## Head

e9d6ec457171f2b297e6043295f8d9185fd89cd5

## Mutation proof

Predicate mutants, each run against the owning self-test: `tolower(q)` to `q` in cloud_relay.sh turns 4 rows red (the ev/HEAD.txt vs ev/head.txt refusal, naming both files, nothing pushed, the ev/A vs ev/a/x refusal); `tolower` to identity in bus.sh case_collision turns its refusal row red; removing `os.setpgid(0, 0)` from RELAY_HOLDER in tick_loop.sh turns the new group-TERM row red (27 checks, 1 failed).

## Null control

The tree at origin/main: cloud_relay.sh --self-test 332 checks, 0 failed; the same replay of a delivered tree pushes it again (no guard). Null rows in the self-test: distinct ev/ names relay; a new tree is pushed; a body committed before the head prints nothing; a body naming the new tip updates; a relay finishing inside HPO_TICK_RELAY_WAIT is reaped as before.

## Figures

- cloud_relay.sh self-test, 367 checks, 0 failed: `PYTHONPATH=tests/hastub bash tools/audit/seat/cloud_relay.sh --self-test`
- bus.sh self-test, 134 checks, 0 failed: `bash tools/audit/seat/bus.sh --self-test`
- tick_loop.sh self-test, 27 checks, 0 failed: `bash tools/audit/seat/tick_loop.sh --self-test`
- structure ratchet: `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED
- `tools/pr/prepr.sh` ran clean at the head above with origin/main merged in (rc=0); main had moved since the first run, so it was rerun after the merge.
- Scoped gate: `python3 tests/closure.py select` was not run beyond prepr's own gate-mode line (MODE: SCOPED).

Not run here: the replay control (93 of 93 against 2) needs the 14:09Z origin and an empty ledger, which this container lacks; the self-test rows (i)-(iii) stand for it. Not derived: tests/entities.py needs homeassistant, which is absent here; prepr's closures step ran clean.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Pending. This diff adds one sentence to dev/governance/roles/fix-review.md (evidence names under ev/ must differ beyond case), which is policy. No owner approval has been given; the owner's approving review at the head is required before this merges.
