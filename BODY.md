R10-RELAY-SWEEP: the relay's residue in `tools/audit/seat/cloud_relay.sh`, folded from R10-RELAY-HANDOFF-ARM, R10-FLY-RELAY-DELIVERED-GUARD and the last carry of R10-FLY-RELAY-REVIEW-FF. Part of #201.

Carries landed: relay levels written before the serial update loop plus the tick's GAP line (2); a level line for a body-only handoff left unapplied, kind registered in `ledger.py` (3); `REFUSE` last-line and update-output replay pinned, guides updated (4); the relay holder in its own process group (5); the delivered guard and the RCA note `dev/audit/rca/R10-RELAY-REPLAY.md` (6); HELD-BODY and stale hold lines (7); case-insensitive evidence collisions refused early in `relay()` and in `bus.sh` push-verdict and unpack, and the reviewer-contract line in `fix-review.md` (8). Carry 1: the body-only path stays a function the beat's job can call; the unapplied kind is a DERIVED `ledger.py` kind, so the ledger holds its disposition. No `bugclasses.json` exists in the tree, so the RCA is not cited there.

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
