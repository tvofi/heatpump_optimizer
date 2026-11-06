R10-RELAY-SWEEP: the relay's residue in `tools/audit/seat/cloud_relay.sh`, folded from R10-RELAY-HANDOFF-ARM, R10-FLY-RELAY-DELIVERED-GUARD and the last carry of R10-FLY-RELAY-REVIEW-FF. Part of #201.

Carries, by number:

- Carry 0: exit 75 and body-sha keying for a failed update, the level written before the serial loop, the unapplied body-only line, the two relay mutants (Carry 4), the bash 3.2 empty-array guard in `bus.sh` orphans, and the holder's process group (Carry 5); the body-only path stays a function the beat's job can call.
- Carry 1: the body-only path is unchanged as a callable function; the unapplied kind is a DERIVED `ledger.py` kind, so `ledger.py` holds its disposition.
- Carry 2: both levels are written before the serial update loop, and `orchestrator_tick.py` prints a GAP line when no-PR OWED lines exist without a `.level` file.
- Carry 3: a body-only handoff left unapplied owes one `handoff-body-unapplied` level line, registered in `ledger.py` KINDS; a body tip older than the head prints nothing (null control).
- Carry 4: M2 (last REFUSE line) and M5 (update output replay) are pinned by self-test rows, and the instrument guides `cloud_relay.sh.md` and `body_push.sh.md` carry the new grammar.
- Carry 5: `tick_loop.sh` starts the relay holder with `os.setpgid(0, 0)`; a self-test sends TERM to the loop's group and asserts the relay still writes its rc.
- Carry 6: `relay()` skips a probe whose tree `review/<pr>` already carries and prints the state dir and ledger path once per pass; RCA note `dev/audit/rca/R10-RELAY-REPLAY.md`. No `bugclasses.json` exists in the tree, so it is not cited there.
- Carry 7: HELD-BODY holds an update whose body does not name the tip's first 8 characters; hold-file lines for PRs not open are owed as `handoff-hold-stale`.
- Carry 8: evidence names colliding case-insensitively are refused early in `relay()` (rc 2, naming both files) and in `bus.sh` push-verdict and unpack; `fix-review.md` tells reviewers evidence names must be case-unique.

## Head

46ea96ca5f527cb0bcfdcdcf06e146124766b334 (HEAD merged with origin/main at 5421413b5).

## Mutation proof

Mutants of `tools/audit/seat/cloud_relay.sh`, each run with `bash tools/audit/seat/cloud_relay.sh --self-test` (baseline: 367 checks, 0 failed):
- M2 `tail -n 1` to `head -n 1`: 2 red, "a failed update's handoff-update line ends in the last of its REFUSE lines" and "and not retried on the next pass, which keeps its reason".
- M5 delete the `cat "$bd/update.out" >&2` replay: 1 red, "and the update's whole output reaches the relay's stderr".
- HELD-BODY: the body check replaced by `false`: 2 red, "a handoff ahead of its PR whose body names the old tip prints HELD-BODY once per pass" and "and runs no update and owes one handoff-held line with why BODY".
- Case compare `tolower(q)` to `q`: 4 red, including "ev/HEAD.txt and ev/head.txt are refused rc 2" and "a file ev/A and a directory ev/a/x are refused rc 2".

## Null control

The null rows ride in the same self-tests: a body naming the new tip updates; a body tip older than the head prints no line; distinct evidence names relay; a hold line for an open PR is not stale; a delivered tree is skipped and a new tree is pushed. Control for the 6 failures of `prepr.sh --self-test` seen on a seat shell: the same self-test passes (rc 0, 0 FAIL) on origin/main and on this tree with the four GIT_AUTHOR/GIT_COMMITTER variables unset, so they came from the session environment.

## Figures

- `bash tools/audit/seat/cloud_relay.sh --self-test`: 367 checks, 0 failed (instrument: its own summary line).
- `bash tools/audit/seat/bus.sh --self-test`: 134 checks, 0 failed.
- `bash tools/audit/seat/tick_loop.sh --self-test`: 27 checks, 0 failed.
- `bash tools/pr/prepr.sh --self-test`: rc 0, with the identity variables unset.
- `python3 tests/entities.py` with the identity variables unset: exit 0.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Pending: this diff touches `dev/governance/roles/fix-review.md` (the case-unique evidence-name rule for reviewers and a wording trim that keeps it at its token cap), which is policy. It needs the owner's approving review at the head before it merges; none has been given.
