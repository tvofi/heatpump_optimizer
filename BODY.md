R10-RELAY-SWEEP repair round 4: the relay's residue in `tools/audit/seat/cloud_relay.sh` on one owning seam (carries 0-9; part of #201). Round 4 repairs the orchestrator's macOS run of 985d8685 (bash 3.2.57, APFS, case-insensitive: 367 checks, 4 FAILED): `relay()` now checks `ev/` case collisions from the commit's own name list BEFORE `git archive | tar -x` writes anything, and the self-test builds its colliding trees in the object database only, so no working-tree file with either name is ever created.

## Carries

Carry 0: levels written before the serial update loops, exit 75 and body-sha keying, the body-only path kept a function; bash 3.2 empty-array guards in the self-test. Carry 1: the body-only path stays a function the beat job can call unchanged; the handoff-body ledger disposition is not written, as ledger.py has no beat job at this base. Carry 2: both levels are written before the update loop; the tick prints GAP when no-PR OWED lines have no .level file (repair round 1: pinned by the `relay GAP` rows, mutant `if False:` red). Carry 3: handoff-body-unapplied is a registered KIND, printed once per pass; a body older than the head prints nothing. Carry 4: the two-REFUSE stub kills M2, the stderr replay row kills M5, and the guides state the grammar, the Code trailer and handoff-body-stale. Carry 5: the relay holder calls setpgid; tick_loop's self-test sends TERM to the group. Carry 6: relay() skips a probe whose tree review/<pr> already carries, with the RCA at dev/audit/rca/R10-RELAY-REPLAY.md; the state dir and ledger path are printed per pass. Carry 7: HELD-BODY holds a handoff whose body does not name its tip, and the hold file reports MERGED or CLOSED lines as handoff-hold-stale. Carry 8: see Carry 9 below and the read-side row. Carry 8 item 2 (repair rounds 1-2: the bus.sh unpack read-side case-collision rows, now fed by ls-tree names, mutants red; round 4: relay() checks before extracting). Carry 9 (the packet counts from 1, so it is the brief's last carry, headed 'Case-insensitive evidence collision'): relay() and bus.sh refuse case-colliding ev/ names, and fix-review.md states the unique-name rule.

## Head

Code head de5a645a413fb537f77dcf94e71328d5ff0dafde: a merge (`-s ours`, tree unchanged) of the stale step ref handoff-wip/r10-relay-sweep into the repair commit 5431dd59df63a418878ccaa5cf16094f85017a8a, which sits on 985d8685b25c794d4b59eeed5ba3344e032b21bc (built on, merge never rebase). The PR head I built on reads b9cc5e32e26b8ebdec66cc8bba9ee110a96c04a0. origin/main was 28d46c4918285d36c409c1fb2f72eb77e04e569e at 2026-11-07 (`git rev-list --count HEAD..origin/main` printed 0 after `git fetch origin main`), unmoved since the merge into 985d8685, so no second `prepr.sh` run for a moved main is owed.

## Mutation proof

Cause: on a case-insensitive filesystem the unpack (`git archive "$sha" | tar -x -C "$d"`) wrote colliding paths before the collision check refused, so it died rc 1 (mkdir/write error) where a refusal rc 2 was owed. Production change: the awk fold moved into `ev_case_collision <commit>` (reads only `git ls-tree -r --name-only <commit> -- ev`, folding every full path and every parent prefix, so ev/A and ev/a/x collide), called right after `git fetch` and before `mktemp`/`git archive`. bus.sh `unpack()` already reads names from `git ls-tree` before anything else (round 2; row `unpack names both colliding names when the folded file would not name the head (ls-tree read)`), so it shares no write-before-check shape and is unchanged.

Fixture: `mkdb` builds the colliding tree with `git hash-object -w`, `git mktree`, `git commit-tree` and `update-ref` in a throwaway repo; no working-tree file is created (row `the fixture never materialises a name (work tree empty)` asserts the work tree holds only .git). It runs the same on case-sensitive ext4 and on APFS.

Failing test first (acceptance a/c): on this Linux (case-sensitive) the four reported rows pass under the pre-fix ordering, so the red is shown by mutants, run with `bash tools/audit/seat/cloud_relay.sh --self-test` (unmutated: 372 checks, 0 failed):
- Mutant 1, delete the check (`local dup; dup=$(ev_case_collision "$sha")` replaced by `local dup=`): 372 checks, 5 failed: `refused before any write: nothing was extracted (tar never ran)`, `and no scratch directory was created (TMPDIR still empty)`, `ev/HEAD.txt and ev/head.txt are refused rc 2`, `naming both files`, `a file ev/A and a directory ev/a/x are refused rc 2`.
- Mutant 2, move the check after the write (same call placed after `subj=$(git log ...)`, i.e. after the extract): 372 checks, 4 failed: `refused before any write: nothing was extracted (tar never ran)`, `and no scratch directory was created (TMPDIR still empty)`, `naming both files`, `a file ev/A and a directory ev/a/x are refused rc 2`. This is the write-before-check shape the macOS run hit; the rows that stay green under it are the ones a case-sensitive disk cannot distinguish, which is why the two direct no-write rows exist.
Both mutants were restored from a saved copy; the committed tree is the unmutated one.

## Null control

Acceptance b: `refused before any write` stubs `tar` with a function that logs each call and asserts no call happened on a refused `ev/HEAD.txt`+`ev/head.txt` probe, and `and no scratch directory was created` points TMPDIR at an empty directory and asserts it is still empty after the refusal. Null control: row `null control: distinct names do run the extract` relays `ev/head.txt`+`ev/other.txt` under the same stub and asserts tar did run (so the stub detects a write when there is one); the older row `distinct names relay (null control)` is kept.

## Figures

Measured at code head de5a645a4 (the tree of 5431dd59), 2026-11-07, this container (bash 5.2.21):
- `bash tools/audit/seat/cloud_relay.sh --self-test`: 372 checks, 0 failed (985d8685: 367; +5 rows: work-tree-empty, tar-never-ran, TMPDIR-empty, tar-ran null control, ev_case_collision names both).
- `bash tools/audit/seat/bus.sh --self-test`: 159 checks, 0 failed (unchanged file).
- `python3 -I tools/audit/seat/orchestrator_tick.py --self-test`: 283 checks, 0 failed (unchanged file).
- `bash tools/audit/seat/tick_loop.sh --self-test`: 27 checks, 0 failed (unchanged file).
- `python3 -I tools/audit/seat/ledger.py --self-test`: 101 checks, 0 failed (unchanged file).
- `python3 tools/audit/seat/selftest_wiring.py --self-test`: 26 checks, 0 failed.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`; scope.run names tests/doc_claims.py (ALL 296 checks PASSED) and tests/entities.py (ALL 2643 ENTITY CHECKS PASSED).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tools/audit/seat/bare_array.py --check`: rc 0, no output.

Acceptance d: NOT demonstrated under bash 3.2 and NOT demonstrated on a case-insensitive filesystem. `curl -sI https://ftp.gnu.org/gnu/bash/bash-3.2.57.tar.gz` returns `HTTP/1.1 403 Forbidden` from the environment proxy, so bash-3.2.57 could not be fetched or built, and I did not attempt a loop mount (no casefold-capable device in this container; not tried). What stands in for it: the fixture never materialises either name, with the evidence of row `the fixture never materialises a name (work tree empty)` and of Mutant 2, which pins that the check precedes the extract. The orchestrator's macOS run of this head is the demonstration that remains owed; the earlier owed bash 3.2 run on verdict/3252 finding 2 is unchanged.

## Red checks

Check runs read by me across all pages (total_count 42, one page of 100, one read at 2026-11-07) for PR 3252's head, which still reads b9cc5e32e26b8ebdec66cc8bba9ee110a96c04a0; the pushed code head de5a645a4 has no check runs of its own. Two runs concluded not-success:
- `tests / nightly-status` 128377933403, failure: not this PR's. It runs tests/nightly_status.py, which reads the conclusions of the last scheduled nightly.yml run through the Actions API; the three-dot diff touches no workflow and no file that script reads, so it reflects the nightly's state, not this diff.
- `governance / instrument-self-tests` 128377933374, cancelled after the 30-minute timeout (10:26:18Z-10:56:32Z): class R10-HOTFIX-SELFTEST-TIMEOUT, cure #3275. Not answerable by a cheaper detector; the answer is the attempt that concludes green after #3275, which this head has not yet had.
The other 40 runs were success or skipped, including `gate` 128385605028 and `pr-contract / pr-contract` 128385450387.

## Forward-carry

none

## Friction

none

## Approval

This diff edits `dev/governance/roles/fix-review.md`, which is policy: it adds one sentence ("Evidence names differ beyond case."). No existing obligation is removed (the earlier deletion of "to be confirmed" is reverted). The owner's approving review at the head is pending.

## Resolution delta

The head merges the stale step ref handoff-wip/r10-relay-sweep with `-s ours` so the step-ref push stays fast-forward; it carries no tree change. origin/main (28d46c4918) is already in 985d8685. The repair commit changes only tools/audit/seat/cloud_relay.sh.
