R10-RELAY-SWEEP repair round 1: the relay's residue in `tools/audit/seat/cloud_relay.sh` on one owning seam (carries 0-8; part of #201). Repair of the round-1 block at 69aa9cd37c7cb86d5868f643fd19e1a19e93ca5c: the bus.sh read-side case-collision line and the tick's GAP line each get a failing-first self-test row with a null control, and the deleted "to be confirmed" obligation in `dev/governance/roles/fix-review.md` is restored.

## Carries

Carry 0: levels written before the serial update loops, exit 75 and body-sha keying, the body-only path kept a function; bash 3.2 empty-array guards in the self-test. Carry 1: the body-only path stays a function the beat job can call unchanged; the handoff-body ledger disposition is not written, as ledger.py has no beat job at this base. Carry 2: both levels are written before the update loop; the tick prints GAP when no-PR OWED lines have no .level file (repair round 1: pinned by the `relay GAP` rows, mutant `if False:` red). Carry 3: handoff-body-unapplied is a registered KIND, printed once per pass; a body older than the head prints nothing. Carry 4: the two-REFUSE stub kills M2, the stderr replay row kills M5, and the guides state the grammar, the Code trailer and handoff-body-stale. Carry 5: the relay holder calls setpgid; tick_loop's self-test sends TERM to the group. Carry 6: relay() skips a probe whose tree review/<pr> already carries, with the RCA at dev/audit/rca/R10-RELAY-REPLAY.md; the state dir and ledger path are printed per pass. Carry 7: HELD-BODY holds a handoff whose body does not name its tip, and the hold file reports MERGED or CLOSED lines as handoff-hold-stale. Carry 8: see Carry 9 below and the read-side row. Carry 8 item 2 (repair round 1: the bus.sh unpack read-side case-collision row, mutant red). Carry 9 (the packet counts from 1, so it is the brief's last carry, headed 'Case-insensitive evidence collision'): relay() and bus.sh refuse case-colliding ev/ names, and fix-review.md states the unique-name rule.

## Head

428882f9dc8b40e441b7f04001dc289899de774d: merge of origin/main 601b9695a into the PR head daaf9c55e385afa05c77004cd41fd03761a28c1d (merge, never rebase). The authored code head 4f7f846d7699cf467f3e992d6c55b9659744f51a is unchanged in content. origin/main was 601b9695a when measured; measured 2026-11-07T10:08:12Z.


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

No check run exists yet at the merge head 428882f9 (not pushed to a PR head before this handoff), so no concluded red is knowable there. Carried from the previous head daaf9c55 (the PR's check runs): the two `gate` deferral failures described in the kept body ("still being judged; their gate decides"), class deferral: the deciding run reads green and no cheaper detector is owed; I did not re-read check runs for this resolution.


## Forward-carry

none

## Friction

none

## Approval

This diff edits `dev/governance/roles/fix-review.md`, which is policy: it adds one sentence ("Evidence names differ beyond case."). No existing obligation is removed (the earlier deletion of "to be confirmed" is reverted). The owner's approving review at the head is pending.

## Resolution delta

Merge-resolution only; no other change. origin/main (601b9695a) conflicted with the PR head in `tools/audit/seat/ledger.py`, one hunk, the `KINDS` table. The PR side added `handoff-body-unapplied` and `handoff-hold-stale`; main added `record-owed`. Union chosen: the line keeps all three, and every pre-existing kind on both sides. Parent read-back: `git diff HEAD^1 HEAD -- tools/audit/seat/ledger.py` removes only the old KINDS line (superseded by the union line) and the `review_owed` signature/doc lines main itself changed; `git diff HEAD^2 HEAD -- tools/audit/seat/ledger.py` removes only main's old KINDS line. Every other hunk of either side is present unmerged-by-hand (auto-merged). Checks at this head: ledger self-test 101 checks 0 failed; cloud_relay 367/0, bus 156/0, orchestrator_tick 283/0, tick_loop 27/0; selftest_wiring 118 wired 0 unwired; structure ratchet PASSED; entities 2642 PASSED; doc_claims 296 PASSED; scoped gate `MODE: SCOPED -- 2 script(s) run, 31 scoped out`. Mutation-proof, null-control and figures sections above describe the authored head and are carried, not re-taken (self-test counts above moved with main's additions).
