Fix review: merge 04e17d32974e10e4d8805b8299d7d3d43660ba10

bus-nonce: 271ad22c3f7943fcb6b3c7035c9f469a

## Round

Second round, at head 04e17d32974e10e4d8805b8299d7d3d43660ba10 (merge base d3d66c40408e76351ffc528686353cadf815a05c). The previous round returned `merge` with `pending-ci` at 3797b416d98a7d4697623454979b61f14b997a93 (probe/rev-3896-ff83c94b). No verdict names that head on verdict/3896, so the packet's scope is `full`, and the whole three-dot diff is reviewed again here. `review_carry.py 3797b416 04e17d32` prints `FRESH-REVIEW`. The delta is 58c73880 plus its merge 04e17d32: comment and docstring sentences split in tests/case_select.py and tests/entities.py, and `tests/case_select.py` added to the doc_claims.py and entities.py closures in tests/closures.json. There is no code change in tests/case_select.py: both of its hunks are inside docstrings. The roles diff `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Evidence

- RESULT delta: `git diff 3797b416 04e17d32` touches tests/case_select.py (two docstrings), tests/entities.py (one comment) and tests/closures.json (two path insertions), and nothing else. The closures additions are the one path each, which the body says closures-autofix named for each script.
- RESULT body figures re-derived at this head (ev/figures.txt, ev/gates.txt):
  - `case_select.py --self-test`: `CASE-SELECT SELF-TEST: PASSED (27 checks)`.
  - `stats tests/features.py` and `stats tests/entities.py` print the body's lines exactly: 248 and 65 spans, 874588 bytes, 599 paths, and every median, max and seconds figure.
  - `wc -c tests/case_closures.json`: 874588.
  - Table `blob`: features.py 04cc69a4… equals `git hash-object`. entities.py records 5cd6e979…, and the file now hashes to 52438e56…. The body's `## Head` section states exactly this staleness: the comment-only edit at 58c73880 left the entry stale until re-recorded, and nothing selects over the table in P1.
  - `comment_ratchet.py --base origin/main`: `long_units_base=2299 long_units_head=2299` and `comment_ratchet: OK`, as the body's `## Red checks` says.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`. `closure.py selftest`: `ALL 118 closure shrink pins PASSED`. `ledger_merge.py --self-test`: `all passed`. `bash -n` passes on tests/run.sh and tests/derive_closures.sh.
  - `bash tests/derive_closures.sh --cases`: the body's exit-2 refusal is the Darwin arm. This host is Linux, so the script went on to record. I stopped it before it wrote anything, and the worktree was clean afterwards. The refusal's order before planning and leasing (derive_closures.sh:112-117, :142) is unchanged since the last round.
- RESULT mutation proof (ev/mutants.txt): every mutant was applied in place in a separate worktree at this head and restored, and the tree was clean afterwards. Line numbers are one higher than in the last round because of the docstring split.
  - M1, drop (c) (case_select.py:568, :578, :582 to `pass`): 2 FAIL, `recorder (c): beta reads a constant of M ...` and `... count needs [bump]`.
  - M2, `moved_mods.add(u)` to `pass` (:623): 1 FAIL, `... count needs [bump]`.
  - M3, statement-level in-place binding off (:297): 1 FAIL, `static: an in-place L.append binds L ...`.
  - M4, a draw does not add `@random` to sets (:187): 1 FAIL, `static: every RNG draw binds @random ...`.
  - M5, `if pathname in _TABLE_ARMS` to `if False` (ledger_merge.py:409): 1 FAIL, `the ledgermerge driver routes tests/case_closures.json to merge_tables`.
  - M1b (:582), M1c (:568) and M3b (:248) still survive, with `PASSED (27 checks)`. The last round's finding about them stands and is carried again below.
- RESULT runner equivalence, re-derived at this head on Linux: `case_select.py run tests/features.py` and plain `python3 tests/features.py` ran side by side in separate worktrees, under /opt/hpo/venv-ci python3 with `PYTHONPATH=tests/hastub` and the fast job's OMP, OPENBLAS and MKL thread pins. Both print 6307 `ok`/`FAIL` check lines, identical in order and text once worktree paths are masked. Both end `ALL 6170 FEATURE CHECKS PASSED` and exit 0. The span run adds `CASES: FULL tests/features.py -- no plan, 248 spans`, and the only other differing lines are log lines that print wall-clock timestamps (ev/equivalence.txt, ev/span_run.log, ev/plain_run.log). The body's 6284 figure against main run 45596992195 is still not re-derived, because this seat cannot read that job's full log. This head-to-head run supersedes it as the equivalence evidence.
- RESULT scope: tests/run.sh still never invokes case_select.py, and features.py and entities.py still run whole, so P1 selects nothing, as the body states.
- RESULT versions: `VERSION`, the manifest and RELEASE_NOTES.md are untouched in the three-dot diff. No golden fixture or claim file is in it.
- RESULT merge: `git merge-tree --write-tree origin/main 04e17d32` exits 0 (tree 88d30c69…). origin/main is d9100de7, ahead of the merge base. The ledger driver resolved tests/closures.json as sets (doc_claims.py 302 entries, entities.py 603 entries).
- RESULT finder's harness: none is named. This is a CI-time design part, R11-CI-CASE-SELECT P1, under design 25fa1f76 approved at b7e7f57f. Its harness is the design's runner equivalence and self-test, both re-run above.
- RESULT CI: `merge_train.py classify 04e17d32… --pr 3896` was polled about every 75 s from 22:59 UTC. It printed WAIT (`pending: gate red: none`) until 23:08:51, then exited 0 at 23:10:08 with `GREEN 04e17d32974e10e4d8805b8299d7d3d43660ba10 pending: none red: none` (ev/classify.txt). No owed red exists, so no `## Red checks` answer is owed. At 3797b416 the body's two reds were `tests / fast (3.14)` (comment ratchet) and `tests / closures` (UNDER-SCOPED). This head repairs both. The comment ratchet re-derives OK above, and `tests / closures` reads success in the packet digest.

## Findings

- Three recorder or static-analysis mechanisms the body claims have no check that fails when they are removed. Each mutant below was applied at this head, and `case_select.py --self-test` stayed `PASSED (27 checks)`:
  - M1b: drop the one-hop import closure, `files |= set(self._module_imports(u).values())` (case_select.py:582).
  - M1c: drop the span's own names resolved in the live namespace, the `reached.add(u)` in `_static_files` (case_select.py:568).
  - M3b: drop the in-place effects of called module-level functions (case_select.py:248 condition to `False`).

  An under-recorded `files` set makes P2 under-select silently. So before P2 selects on tests/case_closures.json, each arm needs a check that fails with the arm removed, or must be removed as redundant with the control shown. Control: the three mutants in ev/mutants.txt; re-run them at P2's merge base. Carry: #3885
- The tests/entities.py entry of tests/case_closures.json is stale at this head: blob 5cd6e979 against 52438e56. The body discloses it. By the merge arm's rule the script runs whole until it is re-recorded, so P2 must re-record entities.py, or assert that a stale blob falls back to whole, before its first selection. Control: `git hash-object tests/entities.py` against the table's `blob`. Carry: #3885

## Friction

- In this environment the Monitor tool ends its command when its watch expires after 5 minutes. A CI poll and the comms heartbeat started under Monitor stopped there, and I moved them to background Bash. Carry: dismissed: seat tooling, not this PR
