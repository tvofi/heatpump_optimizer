R10-STANDING-CONTRACTS-P2, part 1 of 1: builds carries 21, 22, 23 and 27 and forward-carries 24; carries 15 and 16 are answered below.

- Carry 0: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 1: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 2: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 3: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 4: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 5: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 6: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at d69619360
- Carry 7: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 8: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 9: marked [dismissed] on the roster, not answered here. Carry: dismissed: recorded refusal under the orchestrator ruling, the merge and dispatch seats stay standing seats for round 10
- Carry 10: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 11: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 12: marked [dismissed] on the roster, not answered here. Carry: dismissed: recorded refusal under the orchestrator ruling, the merge and dispatch seats stay standing seats for round 10
- Carry 13: marked [dismissed] on the roster, not answered here. Carry: dismissed: recorded refusal under the orchestrator ruling, the merge and dispatch seats stay standing seats for round 10
- Carry 14: marked [dismissed] on the roster, not answered here. Carry: dismissed: recorded refusal under the orchestrator ruling, the merge and dispatch seats stay standing seats for round 10
- Carry 15: belongs to another part of this group and is not answered here. Carry: R10-STANDING-CONTRACTS-P2 | dismissed: not this part, its own part of the group answers it
Carry 16: dismissed: implemented at ae1971474 (hooks_setup.py, hooks/liveness.py, hooks/seat_interpreter.py, hooks/git_identity.py and instruments/hooks_setup.py.md are on main).
- Carry 17: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 0a98a0173
- Carry 18: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 0a98a0173
- Carry 19: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
- Carry 20: marked [implemented] on the roster, not answered here. Carry: dismissed: implemented at 1b174e9b3
Carry 21: built. liveness.py gains the beatd auto-restart (daemonize.py, from beatd/launch.json, seat venv bin first on PATH; RESTARTED or auto-restart FAILED), the read-proof gate (policy-corpus.txt with a sha256 proof last line, compact-owed marker, a UserPromptSubmit arm, --prove) and MISSING checkout presence from the state overlay; beatd.py records its launch and refuses an interpreter below 3.12 naming it; hooks_setup.py --self-test has a planted case, a null control and a mutant per arm.
Carry 22: built. The restart arm relaunches beatd only; the relay is judged by the age of cloud-relay.log (DEAD relay), never a standalone process; the read-proof arm names no session path. Self-test: stale relay log is DEAD, fresh log with no relay process is live, a mutant on each.
Carry 23: built. pulse.py reads the train through merge_train's spool_read, queue_seen_read, read_pid/pid_alive and already_held (--train-state, default $HPO_STATE_DIR/merge_train); a verdict is held by train only for the two answers that mean a batch will run it, and a dead pid holds nothing. Self-test: spooled and pending held with a live pid, STOPPED with a dead one, a skipped PR stays STOPPED, mutants on the spool read and the answer filter.
- Carry 24: belongs to another part of this group and is not answered here. Carry: R10-STANDING-CONTRACTS-P2 | dismissed: not this part, its own part of the group answers it
- Carry 25: marked [dismissed] on the roster, not answered here. Carry: dismissed: meta-note with no work of its own
- Carry 26: marked [dismissed] on the roster, not answered here. Carry: dismissed: meta-note with no work of its own
Carry 27: built. HANDOVER.md's standing-seats bullet names merge and dispatch plus triage and records the tick and roster seats as retired into beat rows.

## Head

907c15d3755fa459b6bd91333fdc2a2828d47995

## Mutation proof

hooks_setup.py --self-test runs six new mutants (restart drops PATH, restart on unrecorded launch, relay never judged, missing checkout never reported, read-proof accepts any sha256, prompt arm silent), each killed. pulse.py: replacing the answer filter with "is not None" fails 2 checks; dropping the spool read fails 1.

## Null control

A fresh relay log, a present checkout, a PR skipped at its current verdict under a live train, a late non-beatd job, and a cleared proof marker each print or judge nothing new; the un-mutated copy passes.

## Figures

none

## Red checks

none

## Forward-carry

none

## Friction

none
