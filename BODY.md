R10-RELAY-SWEEP repair round 2: the relay's residue in `tools/audit/seat/cloud_relay.sh` on one owning seam (carries 0-9; part of #201). Round 2 repairs the round-2 block at b9cc5e32e26b8ebdec66cc8bba9ee110a96c04a0: the bus.sh `unpack` read-side case check now reads names from the commit (`git ls-tree`), as cloud_relay.sh `relay()` does, and runs before the head grep; the `## Red checks` section is rewritten; bash 3.2 is stated as not demonstrated.

## Carries

Carry 0: levels written before the serial update loops, exit 75 and body-sha keying, the body-only path kept a function; bash 3.2 empty-array guards in the self-test. Carry 1: the body-only path stays a function the beat job can call unchanged; the handoff-body ledger disposition is not written, as ledger.py has no beat job at this base. Carry 2: both levels are written before the update loop; the tick prints GAP when no-PR OWED lines have no .level file (repair round 1: pinned by the `relay GAP` rows, mutant `if False:` red). Carry 3: handoff-body-unapplied is a registered KIND, printed once per pass; a body older than the head prints nothing. Carry 4: the two-REFUSE stub kills M2, the stderr replay row kills M5, and the guides state the grammar, the Code trailer and handoff-body-stale. Carry 5: the relay holder calls setpgid; tick_loop's self-test sends TERM to the group. Carry 6: relay() skips a probe whose tree review/<pr> already carries, with the RCA at dev/audit/rca/R10-RELAY-REPLAY.md; the state dir and ledger path are printed per pass. Carry 7: HELD-BODY holds a handoff whose body does not name its tip, and the hold file reports MERGED or CLOSED lines as handoff-hold-stale. Carry 8: see Carry 9 below and the read-side row. Carry 8 item 2 (repair rounds 1-2: the bus.sh unpack read-side case-collision rows, now fed by ls-tree names, mutants red). Carry 9 (the packet counts from 1, so it is the brief's last carry, headed 'Case-insensitive evidence collision'): relay() and bus.sh refuse case-colliding ev/ names, and fix-review.md states the unique-name rule.

## Head

Code head 985d8685b25c794d4b59eeed5ba3344e032b21bc: the repair commit on 75fb31af7de84ab83098bd7c0428a0c5ad701e91 (merge of origin/main 28d46c4918285d36c409c1fb2f72eb77e04e569e into 428882f9dc8b40e441b7f04001dc289899de774d, built on, merge never rebase). The PR head I built on is b9cc5e32e26b8ebdec66cc8bba9ee110a96c04a0. origin/main was 28d46c4918 when measured, 2026-11-07T13:07:14Z, unmoved since the merge; no second `prepr.sh` run was needed for a moved main.

## Mutation proof

Block 1 (bus.sh `unpack`, read side), round 2. Production change: `unpack` reads `git ls-tree -r --name-only "$c" -- evidence | case_collision_names` and runs it before the head grep; `case_collision` (push side) now pipes `find` into the same `case_collision_names`. Failing test first: the new rows `unpack names both colliding names when the folded file would not name the head (ls-tree read)` (evidence HEAD.txt and head.txt, content not naming the head, standing in for an APFS-folded extract) and `case_collision_names refuses a folded-source ls-tree name list, naming both`; the existing read-side row is kept. `bash tools/audit/seat/bus.sh --self-test`: 159 checks, 0 failed.
- Mutant X2 (delete the unpack check; the `if cc=$(git ls-tree ...)` branch replaced by `if false; then :`): 159 checks, 2 failed: `FAIL unpack refuses a proposal whose evidence names differ only by case, naming both (read side)` and `FAIL unpack names both colliding names when the folded file would not name the head (ls-tree read)`.
- Mutant Z (revert to the directory read, after the head grep: `case_collision "$d/evidence"` placed where the old line was): 159 checks, 2 failed, the same two names.
- Null control: `unpack lets distinct evidence names past the case check (null control, read side)` and `case_collision_names lets a distinct ls-tree name list past (null control)` stay ok under both mutants and unmutated.
Files restored after each mutant; the committed tree is the unmutated one (`git diff --stat` empty after restore).

Block 2 (tick GAP line, carried from round 1). Mutant `if n > 0:` to `if False:` in `relay_owed` goes red on `FAIL relay GAP: a relay log holding a handoff-no-pr OWED line and no .level file prints GAP, flagged, with the count` (the round-2 reviewer re-ran it: 283 checks, 1 failed, unmutated 283/0). Block 3 (fix-review.md): restored wording, `policy_lint.mjs` rc 0.

## Null control

Block 1: a review/<pr> commit whose `evidence/` holds `HEAD.txt` and `other.txt` is not refused as a collision (it reaches `BUS undispatched`), row `unpack lets distinct evidence names past the case check (null control, read side)`. Block 2: a relay log with no `.level` file and no handoff-no-pr line prints no GAP, and the same log with its `.level` file published prints no GAP (two rows in the `relay GAP` check). Block 3: the restored sentence is the merge base's wording; `node tools/policy/policy_lint.mjs` exits 0 with it restored.

## Figures

- `bash tools/audit/seat/bus.sh --self-test` last line: 159 checks, 0 failed (base 152, PR head b9cc5e32 156).
- `python3 -I tools/audit/seat/orchestrator_tick.py --self-test`: 283 checks, 0 failed.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: 367 checks, 0 failed (unchanged file; base 332).
- `bash tools/audit/seat/tick_loop.sh --self-test`: 27 checks, 0 failed (unchanged file).
- `python3 -I tools/audit/seat/ledger.py --self-test`: 101 checks, 0 failed.
- `python3 tools/audit/seat/selftest_wiring.py --self-test`: 26 checks, 0 failed.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`; scope.run names tests/doc_claims.py (ALL 296 checks PASSED) and tests/entities.py (ALL 2643 ENTITY CHECKS PASSED).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget file touched.
- `node tools/policy/policy_lint.mjs`: rc 0 at the PR head (verdict/3252 evidence); this round does not touch policy files.
- `python3 tools/audit/seat/bare_array.py --check`: rc 0, no output (static evidence for bash 3.2).

Finding (a), bash 3.2: not demonstrated, bash 5.2 only. This container has bash 5.2.21; I attempted to fetch and build GNU bash-3.2.57, and the environment's permission classifier denied the download-and-compile of external source, so I did not work around it. `cloud_relay.sh --self-test` and `bus.sh --self-test` were NOT run under bash 3.2. Static evidence: `bare_array.py --check` rc 0 above. Roster destination for the run: see Forward-carry.

## Red checks

Check runs read by me from the PR 3252 head b9cc5e32e26b8ebdec66cc8bba9ee110a96c04a0 (the head this code head extends; total_count 42, one page of 100, read 2026-11-07). Two runs concluded not-success:
- `tests / nightly-status` 128377933403, failure: not this PR's. The job (tests.yml `nightly-status`) runs tests/nightly_status.py, which reads the conclusions of the last scheduled nightly.yml run through the Actions API; the three-dot diff (dev/audit/rca/R10-RELAY-REPLAY.md, fix-review.md, delivery/3252.md, tools/audit/seat/{bus.sh,cloud_relay.sh,ledger.py,orchestrator_tick.py,tick_loop.sh}, instruments/cloud_relay.sh.md) touches no workflow and no file that script reads, so it reflects the nightly's state, not this diff.
- `governance / instrument-self-tests` 128377933374, cancelled after the 30-minute timeout (10:26:18Z-10:56:32Z): class R10-HOTFIX-SELFTEST-TIMEOUT, cure #3275. No cheaper detector exists for a job timeout of the self-test suite; the answer is the attempt that concludes green after #3275 (not yet run on this head).
All other 40 runs at that head were success or skipped, including `gate` 128385605028 and `pr-contract / pr-contract` 128385450387. The code head 985d8685 has no check runs until the PR head moves to it; any red concluding there is answered by the orchestrator's run, not carried from here.

## Forward-carry

bash 3.2 run of `cloud_relay.sh --self-test` and `bus.sh --self-test` under macOS /bin/bash 3.2 (not demonstrable in this container): destination, the audit-r10 roster (origin/handoff/audit-r10-roster) as an owed macOS-seat check. Carry: R10-RELAY-SWEEP

## Friction

none

## Approval

This diff edits `dev/governance/roles/fix-review.md`, which is policy: it adds one sentence ("Evidence names differ beyond case."). No existing obligation is removed (the earlier deletion of "to be confirmed" is reverted). The owner's approving review at the head is pending.

## Resolution delta

The head merges origin/main 28d46c4918 into 428882f9 with no conflict; the earlier ledger.py KINDS resolution is unchanged. The repair commit adds only the bus.sh change and its self-test rows.
