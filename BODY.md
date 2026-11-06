R10-RELAY-SWEEP repair round 1: the relay's residue in `tools/audit/seat/cloud_relay.sh` on one owning seam (carries 0-8; part of #201). Repair of the round-1 block at 69aa9cd37c7cb86d5868f643fd19e1a19e93ca5c: the bus.sh read-side case-collision line and the tick's GAP line each get a failing-first self-test row with a null control, and the deleted "to be confirmed" obligation in `dev/governance/roles/fix-review.md` is restored.

## Carries

Carry 0: levels written before the serial update loops, exit 75 and body-sha keying, the body-only path kept a function; bash 3.2 empty-array guards in the self-test. Carry 1: the body-only path stays a function the beat job can call unchanged; the handoff-body ledger disposition is not written, as ledger.py has no beat job at this base. Carry 2: both levels are written before the update loop; the tick prints GAP when no-PR OWED lines have no .level file (repair round 1: pinned by the `relay GAP` rows, mutant `if False:` red). Carry 3: handoff-body-unapplied is a registered KIND, printed once per pass; a body older than the head prints nothing. Carry 4: the two-REFUSE stub kills M2, the stderr replay row kills M5, and the guides state the grammar, the Code trailer and handoff-body-stale. Carry 5: the relay holder calls setpgid; tick_loop's self-test sends TERM to the group. Carry 6: relay() skips a probe whose tree review/<pr> already carries, with the RCA at dev/audit/rca/R10-RELAY-REPLAY.md; the state dir and ledger path are printed per pass. Carry 7: HELD-BODY holds a handoff whose body does not name its tip, and the hold file reports MERGED or CLOSED lines as handoff-hold-stale. Carry 8: see Carry 9 below and the read-side row. Carry 8 item 2 (repair round 1: the bus.sh unpack read-side case-collision row, mutant red). Carry 9 (the packet counts from 1, so it is the brief's last carry, headed 'Case-insensitive evidence collision'): relay() and bus.sh refuse case-colliding ev/ names, and fix-review.md states the unique-name rule.

## Head

4f7f846d7699cf467f3e992d6c55b9659744f51a (the PR head accca58859ef89acafe74a3ee74aaf064acfb712 merged with origin/main 4b7e1770ba81fa02a8dda531463eba68e987ff59, which was already in it; merge, never rebase). Main has not moved since the merge, so one `tools/pr/prepr.sh` run covers it. Every figure below was measured at this head.

## Mutation proof

Block 1 (bus.sh `unpack`, read side). Mutant: delete the line `if [ -z "$why" ] && cc=$(case_collision "$d/evidence" ...); then why=...; fi`. `bash tools/audit/seat/bus.sh --self-test` with the line: 136 checks, 0 failed. With the line deleted: 136 checks, 1 failed, `FAIL unpack refuses a proposal whose evidence names differ only by case, naming both (read side)`. At the reviewed head the same mutant read 134 checks, 0 failed.

Block 2 (tick GAP line). Mutant: `if n > 0:` in front of the `GAP:` line of `relay_owed` replaced by `if False:`. `python3 -I tools/audit/seat/orchestrator_tick.py --self-test` with the line: 275 checks, 0 failed. With the mutant: 275 checks, 1 failed, `FAIL relay GAP: a relay log holding a handoff-no-pr OWED line and no .level file prints GAP, flagged, with the count`. At the reviewed head the same mutant read 272 checks, 0 failed.

Both files were restored after each mutant; the committed tree is the unmutated one.

## Null control

Block 1: a review/<pr> commit whose `evidence/` holds `HEAD.txt` and `other.txt` is not refused as a collision (it reaches `BUS undispatched`), row `unpack lets distinct evidence names past the case check (null control, read side)`. Block 2: a relay log with no `.level` file and no handoff-no-pr line prints no GAP, and the same log with its `.level` file published prints no GAP (two rows in the `relay GAP` check). Block 3: the restored sentence is the merge base's wording; `node tools/policy/policy_lint.mjs` exits 0 with it restored.

## Figures

- `bash tools/audit/seat/bus.sh --self-test` last line: 136 checks, 0 failed (counts the checks that run; at the reviewed head 134).
- `python3 -I tools/audit/seat/orchestrator_tick.py --self-test` last line: 275 checks, 0 failed.
- `bash tools/audit/seat/cloud_relay.sh --self-test` last line: 367 checks, 0 failed (unchanged file).
- `bash tools/audit/seat/tick_loop.sh --self-test` last line: 27 checks, 0 failed (unchanged file).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`; scope.run names tests/doc_claims.py (ALL 296 checks PASSED) and tests/entities.py (ALL 2637 ENTITY CHECKS PASSED).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0, no budget file touched.
- `node tools/policy/policy_lint.mjs`: rc 0; `node tools/policy/rules_sync.mjs --check`: ok.
- `python3 tools/audit/seat/bare_array.py --check`: rc 0, no output (the static evidence for bash 3.2 below).

Block 3 (policy edit): the fix-review.md hunk now only adds the sentence "Evidence names differ beyond case." and restores "report its output to be confirmed"; the token cap was paid by shortening the new sentence (it previously also named HEAD.txt and head.txt).

Finding (a), bash 3.2: not demonstrated. No bash 3.2 exists in this environment (`bash --version` reads 5.2.21) and none was built; `cloud_relay.sh --self-test` was NOT run under bash 3.2. The static evidence is `bare_array.py --check` rc 0 above, which the reviewer already read.

## Red checks

Read once from the PR's check runs (all 68, one page of 100) at the PR head accca58859ef89acafe74a3ee74aaf064acfb712; this final head 4f7f846d has no CI yet, so its reds are not knowable at the handoff.
- `gate` job 128049827027 (run 42256513658) concluded failure with `FAIL run(s) [42255824791] at this head are still being judged; their gate decides`: the deferral class, not a verdict on the diff. The run it names is not green-judged by this body; it is run 42255824791's own `gate` below.
- `gate` job 128049855357 (run 42255824791) also concluded failure at the same minute; I read its job log's tail but not its FAIL line, so its class is not established here: presumed the same mutual deferral, to be read by the reviewer. The run 42255824634 `gate` (job 128048873271) is success.
Answer for both: no cheaper detector is owed to the diff; the deferral is the gate's design and the deciding run reads green.
- governance / instrument-self-tests: success at accca58 (run 42255824634); the previous head's cancellation at the 30-minute timeout is main-wide, cure R10-PROCESS-SLIM #3245.

## Forward-carry

none

## Friction

none

## Approval

This diff edits `dev/governance/roles/fix-review.md`, which is policy: it adds one sentence ("Evidence names differ beyond case."). No existing obligation is removed (the earlier deletion of "to be confirmed" is reverted). The owner's approving review at the head is pending.
