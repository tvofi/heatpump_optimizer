Fix review: blocked 26f2a6df6a8bdce67371370c7a4bd0aa58172cfc root-cause-detectable: tests / fast (3.14) is red on harness_headers.py's depth-seam check over this PR's own new harness, and the body's Red checks says none; a 0.7 s inline_scan run showed it before the handoff

bus-nonce: 76da609555d4d7436a83f8eed6165848

## Round

Round 2 (a delta on round 1's block at eeb947e513fb). I measured head 26f2a6df6a8bdce67371370c7a4bd0aa58172cfc from a detached worktree at that SHA. The head merges code head 9787f68e15 and origin/main 2b6bef745. Both merge commits are pure automatic merges: re-running `merge-tree` on each one's parents gives its exact tree (8cff0985, e4a22c34). `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract in force is the one I read. At 01:40Z the head was re-read with `git ls-remote origin refs/heads/fix/r10-prepr-cap` and was still 26f2a6df.

## Block

- The required check `tests / fast (3.14)` concluded `failure` on this head (job 124707602184, 01:26:24Z): `1 of 112 HARNESS HEADER CHECKS FAILED`, `>>> FAILED: python3 tests/harness_headers.py`. The failing row is `every inlined walk matches the canonical helper and no depth root remains`, with `FAIL depth seams: dev/audit/harnesses/r10_prepr_cap_lease_mutants.py:40: ROOT = Path(__file__).resolve().parents[3]` (`ev/ci-fast-3.14.log`, `ev/ci-fast-red-line.txt`). That file was added by this PR (c317fcd02, round 2). It locates the root by a fixed parent depth instead of the canonical `repo_root` walk (`tools/audit/repo_root.py`), and `tests/harness_headers.py` `depth_root_seams()` refuses that shape.
- The body's `## Red checks` says `none`. pr-contract run 124716318356 started 01:36:19Z, after the red concluded, and refuses: `ERROR [pr-body] ... check 'tests / fast (3.14)' is red and '## Red checks' does not name it` (`merge_train.py classify` -> `RED ... red: gate`, rc 1, `ev/ci-classify.txt`).
- A cheaper detector existed before the handoff. `PYTHONPATH=tests/hastub python3 -c "import sys; sys.path.insert(0,'tests'); import harness_headers; raise SystemExit(harness_headers.inline_scan())"` at this head prints the same `FAIL depth seams: ...:40` line, rc 1, in 0.74 s wall (`ev/inline_scan-head.txt`). Running `python3 tests/harness_headers.py` alone, about 207 s on CI, also shows it. The body's prepr run (rc 0) and `ci_predict.py` did not show it, because harness_headers.py is machine-measuring and left to CI.
- Repair owed:
  - Make the new harness find its root with the canonical walk, or by the route the other `dev/audit/harnesses/*` files use, so the depth-seam check passes.
  - Re-run `tests/harness_headers.py`.
  - Name `tests / fast (3.14)` in `## Red checks` with the cheaper detector and its standing cost (defect-root-cause.md's second trigger).
- Everything else that round 2 owed is settled at this head (below). A repair that touches only the harness's root line and the body leaves that evidence standing, except `r10_prepr_cap_lease_mutants.py`'s own RESULT lines, which must be re-taken.

## Findings

- No prepr step and no `ci_predict` arm runs `harness_headers.inline_scan()` (0.74 s) when a diff adds a `.py` under `dev/audit/`. So a depth-root seam in a new harness first shows as a red `tests / fast` after the push. This is the detector the Block names. Whether to build it is the root-cause answer this PR's `## Red checks` owes. Carry: dismissed: owed by this same pull request's repair round as its `## Red checks` answer (the cheaper detector and its standing cost), which the Block above forces

## Evidence

- (1) The re-mark fix, with the finder's harness (round 1's `runsh_edge.sh`, sha1 d5ca4926aa3d2d130a90fca6aca9a42afec33a38, run on `git archive` copies of `tests/` with stress.py and harness_headers.py recorded at 3 s):
  - At round 1's head eeb947e5: `gate_lock: flock-wrap refused, seat holds no lease: lease held by w, not seat`, `>>> FAILED ... tests/harness_headers.py`, manifest `main-002 1`. The defect reproduces (`ev/runsh_edge-r1.txt`).
  - At this head: `seat's lease lapsed; taking it again` and then a bounded give-up. The manifest has `main-001 0 ... #skip tests/stress.py` and `main-002 0 ... #skip tests/harness_headers.py`, both named unrun (`ev/runsh_edge-head.txt`).
  - Control: round 1's tree with only `_mark_held(lock_dir, label)` added after the `release` in the RenewRefused arm prints the same two `#skip` rows (`ev/runsh_edge-r1-control.txt`).
  - The RenewRefused arm now does `release; _mark_held; take(bounded)`, the same as the lapse arm.
  - Unbounded path: with `wait_bound=None`, `take` returns only on success, which re-marks anyway. The only difference is that the witness now survives an interrupt mid-queue, which is finding 3's class (dismissed in round 1, re-stated in the body). The round-1-to-head delta in `tests/gate_lock.py` is exactly that one line plus the new `_wait_cases` row.
- (2) The new `_wait_cases` row and the drop-re-mark mutant:
  - `PYTHONPATH=tests/hastub python3 tests/gate_lock.py --accept` at the head: `ALL 41 gate lock acceptance checks PASSED`, rc 0 (`ev/gate_lock-accept.txt`).
  - My own mutant (a worktree at the head with the `_mark_held` line deleted): `FAIL a bounded give-up on re-queue keeps the witness; the next wrap queues again [first=76 witness_kept=False second=1 ran=False]`, `1 of 41 ... FAILED`, rc 1. Killed (`ev/mutant-remark-own-accept.txt`).
- (3) The run.sh mapping pin:
  - With round 1's nomap mutant (the whole `if [ -e "$one.waited" ]` block deleted), the full committed `tests/entities.py` prints `FAIL run.sh records a wait past its bound as #skip ...` (serial and lanes rows `76 ... tests/stress.py`) and `FAIL run.sh's lane console prints SKIP ... [lane console words=['FAILED']]`, `2 of 2495 ENTITY CHECKS FAILED`, rc 1. Killed (`ev/entities-mutant-nomap.txt`).
  - Unmutated head: `ALL 2495 ENTITY CHECKS PASSED`, rc 0, with both new rows `ok` (`ev/entities-head.txt`).
  - The finder's `runsh_harness.sh` (sha1 593da3b86d10cf1fb75d2fa8857e17b117d6aa95) on the nomap tree records `main-001 76 ... tests/stress.py` as `>>> FAILED` (`ev/runsh_harness-jobs1-nomap.txt`, `-jobs2-nomap.txt`).
- (4) Lane word, `runsh_harness.sh` with `JOBS=2`:
  - Round 1 prints `ok     ... tests/stress.py (6s)`.
  - This head prints `SKIP   ... tests/stress.py (5s)`.
  - The manifest is `#skip tests/stress.py` at both ends (`ev/runsh_harness-jobs2-*.txt`).
  - In `run_always`, the word is computed after `leased` returns and after `WAIT_UNRUN` is set.
- The fixer's `r10_prepr_cap_lease_mutants.py` at the head prints `M0 failed=0 clean`, `M-remark killed`, `M-nomap killed`, `M-word killed`, `mutants=3 survived=0` (`ev/lease-mutants-fixer-harness.txt`). That is the fixer's instrument. It is not the evidence above, which I took with my own mutants and the finder's harnesses.
- (5) Round 1's finding 3 (held witness never cleared) is dismissed in the body with round 1's own reason. The corpus figure round 1 could not re-derive is withdrawn from the body. The body cites no roster SHA and makes no roster carry (`## Forward-carry: none`). There is no live roster carry to check.
- (6) Round 1's carries still hold at this head:
  - P206 (`wait_bound`, `WAIT_BOUND_RC`, `--script`/`--wait-marker`) and P211 (the lapse arm and the held witness) are present.
  - The P309 fold is present: `dev/audit/rca/R10-RCA-JIDOKA-YIELD.md`, the `OWED_CARRY` arm in `tools/audit/carry_audit.py` (`--self-test`: 211 checks, 0 failed, `ev/carry_selftest.txt`), and the `field_coverage.mjs` registration (`FIELD COVERAGE ok`, `ev/field_coverage.txt`). The prepr.sh step 7e WHY now sits at lines 986-993 (it moved from 974-978 with the V148 lines above it) and names fix-review step 10 and process state (c).
  - `r10_carry_parser_mutants.py` prints `RESULT sites=167 unmapped=0 mutants=241 survived=0` (`ev/carry-mutants.txt`).
  - The body states M2 (P310) and shape B (P311) as out of scope.
- Gate and structure:
  - `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, rc 0 (`ev/structure.txt`; this tree has no `summary` subcommand, so I ran it plain).
  - `tests/closure.py select --diff 2b6bef745` prints `MODE: FULL -- every test script runs, nothing is scoped out.` (`ev/mode.txt`).
  - `rules_sync.mjs --check` prints `RULES-SYNC ok`, and `policy_lint.mjs --budgets` exits 0.
  - Both claim files, VERSION, RELEASE_NOTES.md and the manifest are byte-identical to origin/main and unchanged in the three-dot diff (`ev/untouched.txt`).
  - The delivery row `dev/programme/delivery/3051.md` is in the three-dot diff (`ev/three-dot-files.txt`).
- `git merge-tree --write-tree origin/main 26f2a6df`, with origin/main at 8fec54ee2, gives tree 76227165, rc 0, with `LEDGER-MERGE: resolved tests/closures.json` and no conflict (`ev/merge-tree.txt`).
- Figures I could not re-derive: the body's "SECOND prepr PASSED rc=0 at 9787f68e15". I did not re-run prepr; fix-review step 11 says to cite CI's heavy runs. I did confirm that 9787f68e15 differs from c317fcd02 only by one `tests/closures.json` line. That prepr pass did not cover `tests/harness_headers.py`, which CI found red.
- CI on this head, read from the whole check-run set (68 runs):
  - Red: `tests / fast (3.14)` (harness_headers, above); `pr-contract / pr-contract`, three runs, which refuse the body's `## Red checks`; and `gate` (the aggregate).
  - Green: closures, coverage, arch-instrument, instrument-self-tests, policy-docs, wave-script, delivery-status, mutation, typing, browser, env-matrix, arch-score and budget-raise-gate.
- Policy in the diff: `dev/governance/rules/gate-scoping.md` (it drops six issue citations) and `dev/governance/roles/nudge.md` (it drops "Do not start a fifth."). Both need the owner's approving review, as the body's `## Approval` says. That is noted here and is not the block.
