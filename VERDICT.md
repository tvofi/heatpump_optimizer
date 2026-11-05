Fix review: merge 189fdb8893334dba36f5841ee62ddbb160e43659

bus-nonce: 36209c31e2b1067b3c3be8b458d5d233

Round 1 (sonnet). Measured head 189fdb8893334dba36f5841ee62ddbb160e43659; live PR head re-read before posting: see ev/live-head.txt.

## Head
189fdb8893334dba36f5841ee62ddbb160e43659

## Evidence
- RESULT: bus.sh --self-test at head: 132 checks, 0 failed (ev/bus-selftest-head.log); the four new rows pass. cloud_relay.sh --self-test at head: 332 checks, 0 failed (ev/relay-selftest.log).
- RESULT failing-test-first: head's self-test run against a bus.sh with the hold lines deleted (the pre-fix train_add; origin/main's bus.sh carries no hold check): "FAIL a PR listed in the hold file is not added to the train" and "FAIL a malformed hold file adds nothing (never hold-none)", 132 checks, 2 failed (ev/mut-nohold.log).
- RESULT mutation: inverting the check (rc = 1 -> rc = 0): 4 failed, incl. the pre-existing event-add row and both null controls (ev/mut-invert.log). Deleting it: 2 failed (above). Neither is vacuous.
- RESULT null control: a PR not listed is added (stub records argv), an empty hold file adds as before, the pre-existing "posted merge verdict is added at its head" row is unchanged; the skip is called from post_verdict after the poster succeeded, so the post still happens and the held PR gets one "BUS train-add <pr> held (cloud-handoff-hold, rc=0)" line.
- RESULT grammar (ev/grammar.log, own run of cloud_relay.sh held): file "3300" -> 33:not held, 3300:held; file "33" -> 3300 not held; plain "3229" with or without trailing newline, and after a comment and blank line -> held; "#3229" is a comment -> NOT held (the relay's grammar is plain numbers; the file is the orchestrator's); "3229 " (trailing space) -> rc 2 malformed -> train_add adds nothing (never hold-none).
- One function shared: train_add calls `cloud_relay.sh held`, the relay's own subcommand (cloud_relay.sh:377); no copy of held/hold_list in bus.sh. cloud_relay.sh is untouched.
- Scope: diff vs origin/main (three-dot) is dev/programme/delivery/3229.md and tools/audit/seat/bus.sh only; no claim file, VERSION, manifest or RELEASE_NOTES touched; no new file/seat/lane. tests/structure.py: STRUCTURE RATCHET PASSED, no raise. git merge-tree --write-tree origin/main head: clean (tree 13886438), rc 0. Commit messages carry no footer/trailer. R10-PROCESS-SLIM also edits bus.sh and lands after; this hunk is local to train_add and the train self-test block.
- CI: `merge_train.py classify` at this head: "GREEN 189fdb8893334dba36f5841ee62ddbb160e43659 pending: none red: none", rc 0.

## Red checks
Read from the check-runs of the PR (81 runs). Three concluded non-green, all in the earlier push-time run 42106514670 of an earlier head; the head's later runs (gate 127549900431, pr-contract 127549519787, budget-raise-gate, arch-score) are success and classify is GREEN:
- governance / delivery-status (127522986842): failure; the log tail I could read held only checkout cleanup, so I could not name its cause. Superseded by the later green runs; not this diff's code (it adds only a delivery row).
- tests / nightly-status (127522986559): failure; not this PR's (reads nightly state, the diff does not reach it); log tail shows no cause.
- governance / instrument-self-tests (127522986730): cancelled at 21:17:24 (about 30 min in, superseded by a later push's cancel-superseded), not a red; I ran both self-tests it covers (bus, cloud_relay) myself at the head: green.
Cause of the first two is not established by me from the log tails available; I judge them not attributable to this PR.

## Findings
- Follow-up: merge_train.py `sweep` (merge_train.py ~3445-3495) reads no hold file (only the ledger train-stop), and bus.sh's own comment names sweep as the backstop for a head a skipped add missed; a held PR whose merge verdict is posted can therefore still be added by the next sweep, so the hold is closed only for the event add. Carry: R10-FLY-RELAY-HOLD
- Follow-up: the hold file's "#N" spelling is a comment, so a hold written "#3229" holds nothing (relay grammar, unchanged here); the orchestrator writes the file. Carry: dismissed: the grammar is the relay's documented plain-number format and this PR reuses it unchanged
