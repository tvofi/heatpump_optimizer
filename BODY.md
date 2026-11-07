R10-RELAY-SWEEP repair round 2 (body re-take, round 5; code unchanged): the relay's residue in `tools/audit/seat/cloud_relay.sh` on one owning seam (carries 0-9; part of #201). Round 2 repairs the round-2 block at b9cc5e32e26b8ebdec66cc8bba9ee110a96c04a0: the bus.sh `unpack` read-side case check now reads names from the commit (`git ls-tree`), as cloud_relay.sh `relay()` does, and runs before the head grep; the `## Red checks` section is rewritten; bash 3.2 is stated as not demonstrated.

## Carries

Carry 0: levels written before the serial update loops, exit 75 and body-sha keying, the body-only path kept a function; bash 3.2 empty-array guards in the self-test. Carry 1: the body-only path stays a function the beat job can call unchanged; the handoff-body ledger disposition is not written, as ledger.py has no beat job at this base. Carry 2: both levels are written before the update loop; the tick prints GAP when no-PR OWED lines have no .level file (repair round 1: pinned by the `relay GAP` rows, mutant `if False:` red). Carry 3: handoff-body-unapplied is a registered KIND, printed once per pass; a body older than the head prints nothing. Carry 4: the two-REFUSE stub kills M2, the stderr replay row kills M5, and the guides state the grammar, the Code trailer and handoff-body-stale. Carry 5: the relay holder calls setpgid; tick_loop's self-test sends TERM to the group. Carry 6: relay() skips a probe whose tree review/<pr> already carries, with the RCA at dev/audit/rca/R10-RELAY-REPLAY.md; the state dir and ledger path are printed per pass. Carry 7: HELD-BODY holds a handoff whose body does not name its tip, and the hold file reports MERGED or CLOSED lines as handoff-hold-stale. Carry 8: see Carry 9 below and the read-side row. Carry 8 item 2 (repair rounds 1-2: the bus.sh unpack read-side case-collision rows, now fed by ls-tree names, mutants red). Carry 9 (the packet counts from 1, so it is the brief's last carry, headed 'Case-insensitive evidence collision'): relay() and bus.sh refuse case-colliding ev/ names, and fix-review.md states the unique-name rule.

## Head

Code head 3134798017b1d26994c410206349b06d187559a0 (the PR head; this round changes no code and pushes nothing to fix/ or handoff/). Its tree is identical to code handoff de5a645a413fb537f77dcf94e71328d5ff0dafde (`git diff de5a645a4 3134798017` is empty): 3134798017 is the merge of that handoff into fix/r10-relay-sweep. Parents: 45c0f78a0 and de5a645a4; merge base with origin/main 28d46c4918285d36c409c1fb2f72eb77e04e569e. Of the commits behind de5a645a4, 5431dd59d and de5a645a4 were authored hpo-fixer by another session; I did not mutation-test 5431dd59d and only measured the head with it. origin/main has moved since (aaaec2128e); the head is not merged forward this round by order.

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

- `bash tools/audit/seat/bus.sh --self-test` last line: 159 checks, 0 failed (base 152; re-run at 3134798017).
- `python3 -I tools/audit/seat/orchestrator_tick.py --self-test`: 283 checks, 0 failed.
- `bash tools/audit/seat/cloud_relay.sh --self-test`: 372 checks, 0 failed (base 332).
- `bash tools/audit/seat/tick_loop.sh --self-test`: 27 checks, 0 failed (unchanged file).
- `python3 -I tools/audit/seat/ledger.py --self-test`: 101 checks, 0 failed.
- `python3 tools/audit/seat/selftest_wiring.py --self-test`: 26 checks, 0 failed.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`; scope.run names tests/doc_claims.py and tests/entities.py. Re-run here: `python3 tests/doc_claims.py` ALL 296 checks PASSED; tests/entities.py was not run here (the cloud venv-ha lacks paho, a toolchain gap), so no entities count is restated; CI `tests / closures` and `tests / fast (3.14)` at this head are success.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, no budget file touched.
- `node tools/policy/policy_lint.mjs`: rc 0, re-run at 3134798017.
- `python3 tools/audit/seat/bare_array.py --check`: rc 0, no output (static evidence for bash 3.2).

Finding (a), bash 3.2: not demonstrated, bash 5.2 only. This container has bash 5.2.21; I attempted to fetch and build GNU bash-3.2.57, and the environment's permission classifier denied the download-and-compile of external source, so I did not work around it. `cloud_relay.sh --self-test` and `bus.sh --self-test` were NOT run under bash 3.2. Static evidence: `bare_array.py --check` rc 0 above. Destination for the run: the owed macOS bash 3.2 run is already the reviewer's carry on group R10-RELAY-SWEEP in the audit-r10 roster (verdict/3252 finding 2); I could not land a new roster op (outside my write scope), so none is added here.

## Red checks

Check runs read by me at head 3134798017 across all pages (total_count 68, one page of 100, `get_check_runs`, 2026-11-07). Six runs concluded failure; the diff causes none of them. Runs 42385417686, 42387066581 and 42385416529 are the workflow runs at this head.
- `gate` 128448828285 (run 42385417686, KIND edit, 15:44-15:56Z), failure: the gate's edit/code deferral race. Its log reads "run(s) [42387066581] at this head are still being judged; their gate decides". A later run owns the judgement; nothing in the diff is involved.
- `gate` 128452383371 (run 42387066581, 16:05-16:06Z), failure: the same race. Its log reads "FAIL tests: no run at this head judged base 'main'" (codeql, governance, hassfest, validate likewise not yet judged) with workset arch-score budget-raise-gate pr-contract, i.e. the edit run's gate ran before the code run's units finished.
- `gate` 128471344242 (run 42385416529, KIND code, 17:14-17:15Z), failure: the gate read a failed pr-contract of a superseded run. Its log reads "FAIL pr-contract / pr-contract: failure (run 42387066581)". In its own run `pr-contract / pr-contract` 128471138373 concluded success at 17:14:35Z, before the gate began (17:14:38Z), so the next gate attempt judges green; I do not claim a later gate result.
- `pr-contract / pr-contract` 128446411039 (run 42385417686) and 128449815767 (run 42387066581), failure: the same cause, the CodeQL deferral race. The log of 128449815767 reads "FAIL closed: no run at this head owns a finished codeql unit for base 'main' after 600 s" (codeql, hassfest, kernel-points, validate, tests, governance units of that run were skipped), while the body check in the same job reported FIGURES 10 resolved, 0 not verified, 0 refused and CARRY-AUDIT 0 findings. 128446411039 shows the same body-check output. The cheaper detector is the existing 600 s codescan wait itself; the answer is the later run 42385416529, in which `CodeQL` 128457033368 and `codeql / Analyze (actions|python|javascript-typescript)` are success and `pr-contract / pr-contract` 128471138373 is success. Neither failure was a body refusal at that time, but those body checks read the body published then, which was the round-2 one naming the b9cc5e32 runs; this re-take supersedes it.
- `tests / nightly-status` 128455324026 (run 42385416529), failure: not this PR's. The job runs tests/nightly_status.py, pinned to main at 28d46c4918, which reads the last concluded nightly.yml dispatch: run 42369836867 (dispatched 2026-11-07T11:50:04Z, head 08fd676, conclusion cancelled), failing lanes mutation-ledger (1), (2), (3), (4), mutation-ledger-push, mutation-nightly and slow, all cancelled; run 42382408131 was still in flight. The three-dot diff (dev/audit/rca/R10-RELAY-REPLAY.md, dev/governance/roles/fix-review.md, dev/programme/delivery/3252.md, tools/audit/seat/{bus.sh,cloud_relay.sh,ledger.py,orchestrator_tick.py,tick_loop.sh}, tools/audit/seat/instruments/cloud_relay.sh.md) touches no workflow and none of those lanes' inputs, so the red reflects the nightly's state, not this diff. The job states it is not a required context on main-protect. No verification dispatch run exists for this PR; I name none and did not dispatch one (outside my write scope).
- Cleared reds, superseded head b9cc5e32e26b8ebdec66cc8bba9ee110a96c04a0 (round 2 body, total_count 42): `governance / instrument-self-tests` 128377933374, cancelled after the 30-minute timeout, class R10-HOTFIX-SELFTEST-TIMEOUT, cure #3275; at 3134798017 `governance / instrument-self-tests` 128455323930 concluded success (16:19:16-16:47:42Z). `tests / nightly-status` 128377933403 at that head is the same nightly red as above. `gate` 128385605028 and `pr-contract / pr-contract` 128385450387 there were success.
All other runs at 3134798017 are success or skipped; `code-scanning` alerts: none listed in the pr-contract output.

## Forward-carry

none

## Friction

none

## Approval

This diff edits `dev/governance/roles/fix-review.md`, which is policy: it adds one sentence ("Evidence names differ beyond case."). No existing obligation is removed (the earlier deletion of "to be confirmed" is reverted). The owner's approving review at the head is pending.

## Resolution delta

No code change this round; the body is re-taken whole at 3134798017. The earlier merge of origin/main 28d46c4918 and the ledger.py KINDS resolution are unchanged.
