Part of #201. R10-RELAY-SWEEP: the relay's residue on one seam, tools/audit/seat/cloud_relay.sh (fold of R10-RELAY-HANDOFF-ARM, R10-FLY-RELAY-DELIVERED-GUARD and the open carry of R10-FLY-RELAY-REVIEW-FF).

Carry 0: the body-only path stays inside handoff_arm, unchanged for the beat's job; exit 75 and body-sha keying kept.
Carry 1: no code change; the ledger disposition for the handoff-body ref is not written (the handoff-no-pr fold already rides a body ref on its code ref).
Carry 2: both levels are published before the serial loops (handoff_level before the update loop, probe levels before the relay loop); the tick prints a GAP line when the log has no-PR OWED lines but no .level file.
Carry 3: a body-only handoff left unapplied while its body tip is newer than the head's commit prints BODY-ONLY and owes a handoff-body-unapplied level line (registered in ledger.py KINDS).
Carry 4: the M2 and M5 rows exist in the self-test (second REFUSE line wins; the replayed update output); the guide text is updated.
Carry 5: RELAY_HOLDER starts in its own process group (setpgid), with a group-TERM row in tick_loop.sh's self-test.
Carry 6: delivered guard in relay(), the per-pass state-dir line, and the RCA note dev/audit/rca/R10-RELAY-REPLAY.md.
Carry 7: HELD-BODY before an update whose body does not name the tip's first 8 characters; hold-file lines for PRs no longer open are owed as handoff-hold-stale.
Carry 8: case-collision refusal in relay(), bus.sh push-verdict and unpack, and one sentence in fix-review.md.
Carry 9: the packet lint counts the nine carries 1-9; the brief numbers them 0-8, so this is Carry 8 above (the case-collision carry): nothing further is owed.

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
