Fix review: merge 699e404ce570639e6572277391665f7ed4946562

bus-nonce: dc2ec26f4e5fba6dfc251c130d9787b7

Round 2 of review, so a repair and not a re-cut. I measured head `699e404ce570639e6572277391665f7ed4946562`, and it was still the branch head at 20:17Z. origin/main was `2636ce9e9378addc393b749160be0bd928af4f90`, which is the PR's base, so the merge base equals main. The role files on main are unchanged since that base.

## Findings

- `dev/audit/rca/R10-RCA-GATE-LEASE-FLAKE.md` section 6 says case `torn_marker` "polls `_unleased` against 4000 `mark_unleased` rewrites (1000: ...)". The code does 1000 rewrites, and the body says 1000. The sentence contradicts itself and should read 1000. Carry: rca-gate-lease-flake
- The same RCA, section 7, says "`tests/entities.py` cannot run in this seat (no `paho`)". The body's Figures say entities.py did run in the fixer's seat (`2 of 2429` at the head, `2 of 2425` at main). One of the two accounts is stale. Carry: rca-gate-lease-flake
- `_write_whole` has no `finally` cleanup. An exception between `tmp.write_text` and `os.replace` (for example ENOSPC) leaves a `.write-*` dot-file behind, the same way a crash does. Carry: dismissed: RCA section 7 discloses the leftover staging file; no reader globs a dot-prefixed name (`unleased-*`, `ticket` prefix, `slot-<i>` by index), and `_clear_lock` removes it.

## Evidence

- Round 1's block (class-open: `mark_unleased`/`_unleased`) is closed. The harness is a rebuild of round 1's out-of-tree probe, which is the reviewer's instrument and not the finder's: `ev/unleased_probe.py`. It re-marks one label 4000 times while a thread polls `_unleased`. RESULT, base `2636ce9e9`: lost=13478, 11532, 9408 in three runs. RESULT, head: lost=0, 0, 0. Null control (no rewrites, the same reader polling): lost=0 three times at both ends (`ev/finder-probe.txt`). The counts depend on thread timing, so only the base-vs-head split reproduces.
- Mutation proof, re-run here, each mutant one edit to the head and restored after its run (`ev/mutants.txt`):
  - `mark_unleased` back to `path.write_text`: `torn_marker` FAIL (2666 missing), 1 of 33 FAILED.
  - `_write_whole` back to `path.write_text`: `torn_write` and `torn_marker` FAIL, 2 of 33 FAILED.
  - `Owner.create`'s `finally: tmp.unlink` removed (round 1's surviving M4): `pool_contents` FAIL with `.create-…-slot-000` left, 1 of 33 FAILED. M4 is now killed.
  - `Owner.write` bypassing `_write_whole`: `torn_write` FAIL, 1 of 33.
  - `Owner.create`'s `os.link` swapped for `os.replace`: `torn_create` `winners=['rival', 'a']` and `one_winner` `overlaps=1`, 2 of 33.
  - The body's figures match in shape (1, 2, 1 of 33). Its missed-poll counts are timing-dependent and agree with these in order of magnitude only.
- Null control on the unmutated tree: `ALL 33 gate lock acceptance checks PASSED` three times at the head, and `ALL 29 ... PASSED` three times at the base (`ev/accept-head.txt`, `ev/accept-base.txt`). The 4 added cases match the body.
- Class: I ran the body's rule (`grep -nE "write_text\(|os\.open\(|\.touch\(|\.write\(" tests/gate_lock.py`, production lines only) at the head (`ev/class-rule.txt`). It returns lines 184/189 (`Owner.create`, staged), 261 (`_write_whole`), 267/285 (`flock` touch/open, no content), 293 (`holding`, read only with `.exists()` at line 314), 376 (ticket temp, then `os.link`/`os.replace`) and 546/595/735 (`Owner.write`, now whole). The body or the RCA table dispositions every one; no seam is open. The outside-file `git grep` returns only `tests/README.md` prose and a `prepr.sh` self-test string.
- Brief question, the prepr `closures` red on `hb:positive_control`: the body's answer holds. CI owns `tests/entities.py`, and at this head `tests / fast (3.14)` and `tests / closures` both concluded success (check-runs API). The seat-local red does not reproduce in CI, which is consistent with the body's py-spy environment explanation. I did not re-run entities.py at main in this seat; I cite CI instead (role step 11, heavy runs).
- Merge: `git merge-tree --write-tree origin/main 699e404c…` exits 0 (`ev/merge-tree.txt`). No claim file is touched, so the driver did not run.
- VERSION, the manifest version, the RELEASE_NOTES heading and `tests/golden` are untouched (`ev/version-untouched.txt`, empty diff). CI's version-edit step prints "no version edit".
- Head line: the body names `699e404ce570639e6572277391665f7ed4946562`, the head I measured.
- Forward-carry: the body says none, and nothing found here changes a later stage.
- CI at this head (check-runs API, 20:17Z): `pr-contract / pr-contract` is a failure only at `codescan_wait.py` ("no run at this head owns a finished codeql unit for base 'main' after 600 s"), because `codeql / Analyze (python)` was still in progress. Its figures, preflight and carry-audit steps are clean (`CARRY-AUDIT: 0 finding item(s)`, `FIGURES: 5 resolved, 1 not verified, 0 refused`). `gate` is a failure only with "run(s) [40127570155] at this head are still being judged". `tests / coverage` and `codeql / Analyze (python)` were still in progress. The head's workflows had not all concluded, so role step 11 does not let me take a root-cause verdict on these two reds; neither names a defect in this diff. This verdict does not stand in for the gate: the merge train still needs `pr-contract` and `gate` re-run green once those workflows conclude.
- Architecture (step 15): one shared writer, `_write_whole`, replaces two truncating writes; `Owner.create` keeps its link-fails-if-exists semantics. No budget, closure or INERT entry moves (the diff is 3 files: `tests/gate_lock.py`, the RCA, the delivery row).
