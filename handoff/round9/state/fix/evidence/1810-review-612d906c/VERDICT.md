Fix review: merge 612d906c83d20784d2af88e79bf1d36de6952e57

F10.3 (#1810), round 1. Code head 612d906c measured; PR head 51f4bcb4 = 612d906c + main 787fe137, judged as a merge delta. Reviewer: opus seat, cloud.

## Head and ancestry
- Branch tip 5d43a3a7 is transport only (4 files under handoff/round9/fix/resume/), above the code head. No resume or body file in a413832a..612d906c.
- VERSION, manifest version, RELEASE_NOTES heading, tests/golden/ untouched (three-dot diff empty). tools/audit/briefs/ unchanged on main since the merge base.

## Merge delta (51f4bcb4)
- `git merge-tree --write-tree origin/main 612d906c` exits 0 with tree f0d1bcaf, which equals 51f4bcb4's tree.
- `git diff origin/main 51f4bcb4` equals `git diff a413832a...612d906c` line for line (index lines aside), so the delta is main's alone. bugclasses.json parses.

## Mutation proof (targeted, mine)
Each mutant edits tests/mutation_table.py; tests/entities.py at the head, run in a detached worktree:
- RESULT null (a comment before `_scope_tail`): ALL 2002 ENTITY CHECKS PASSED.
- RESULT mutant A (the move match drops the same-def requirement, the anti-laundering half): KILLED, 1 of 2002 failed ("added_unpinned refuses a site traded in at an unchanged count, and keeps a re-indented or moved site the base's").
- RESULT mutant B (the move match ignores which files the diff removes from): KILLED, the same check.
The fixer's M0 to M11 were not re-run.

## The design call: Python children only, INERT reads dropped
The call is right.
- Dropping INERT reads: the INERT list is the classification, and `affected`'s docs-only skip rests on it. A recorder that quietly moved DISCLAIMER.md, LICENSE and three docs pages into a closure would reclassify them as a side effect. That belongs to tvofi, as the body says.
- Python only: I measured with the finder's enumerator (tools/audit/round9/D14/s5/closure_divergence.py, byte-identical to the I2 sweep's) on tests/entities.py at the head. The results were `seams=2343`, of which `node-child=517` (26 on measured files) and `git=1826` (293 on measured files), with `python-child=0` and 2024 seams on INERT files. The 26 node-child measured files are all test scripts and tools that a node linter content-scans. The git seams are content scans of tools/audit, tests/golden and the like. Folding either into entities.py's closure turns content scans into dependencies. That is the over-scope direction, which `_warm_index` already prices for git, and the residual is named in the body and in the bugclasses.json I2 entry. A push to main forces the full gate, so any residual under-scope is bounded at one merge.
- The I2 carry asked for a nightly second oracle. The body answers that every Linux closures-job recording is now that oracle, and that over-scope gets no barrier. I accept that answer.
- strace on CI: tests.yml's closures job installs strace on every non-docs-only diff, so the instrument does run there.

## Diff read
- The env_drift `judge_drift` and stress `scenario_verdict` lifts preserve behaviour: the same branches, messages and counters.
- `added_unpinned` and `diff_sides`: when the ref cannot be read, the sides come back empty, so the gate refuses more and never less. The move match requires the same kind, the same stripped text and the same innermost scope, and pairs a removed file with an added one.
- `strace_files`: a process counts only while its last exec was Python, and its forks count too. The `execd` set covers a child that execs before its parent's clone returns. If the `-o` trace is unreadable, the record falls back to the hook record.

## Notes (non-blocking)
- N1, latent: GUARD_OFF builds `new` as `line[node.test.end_col_offset:]`, a UTF-8 byte offset applied to a str. The CLAMP branch does handle bytes. A test containing a non-ASCII literal yields an unparseable mutant. probe_syn.py shows `if u == "°C":  # deg` becoming `if False  # deg`. At the head there are 0 such sites: probe_guard.py found 2995 GUARD_OFF/CLAMP_DROP candidates, 0 syntax errors, and 2 non-ASCII lines, both with the non-ASCII text after the test. The failure is fail-safe: an unparseable mutant is SKIP-UNPARSEABLE (mutation_table.py:2305-2309), so such a site stays unpinned and is refused until a seat triages it by hand. It is a one-line fix (`line.encode()[off:].decode()`) for F10.5 or F10.6 to carry.
- N2: on a box with strace installed but ptrace denied, `record` fails, because strace does not start the command, rather than falling back to the hook alone. CI and the Mac are unaffected.
- N3: the stray `f10-3` branch at 64b4bc24 on origin is for the orchestrator to delete.

## Numbers not re-derived
The per-site demo (8 of 10, 10 of 10 with pins stripped), the #1748 146-to-0 figure, the I1 sweep figure (552 to 392), the residual counts and the strace cost were not re-run. They are quoted from the body, not verified.

## CI at 51f4bcb4 (read 12:2xZ)
- Green: mutation (no production line, empty scope), typing, briefs, pr-contract, closure-scope, budget-raise-gate, policy-docs, delivery-status, nightly-status, env-matrix, instrument-self-tests, browser, hassfest, validate-hacs, wave-script.
- Still running: closures, fast (3.14), coverage, CodeQL python. None is red.
- The merge seat merges only on green. A closures UNDER-SCOPED there is ci-autofix's to repair, not a block on this verdict.
- Real-HA at 51f4bcb4 is 61/61, as the Mac relayed.

Evidence: /mnt/project-files/audit-r9/fix/evidence/1810-review-612d906c/
