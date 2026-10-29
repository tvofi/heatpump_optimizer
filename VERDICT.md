Fix review: merge 38ffa02aeb39e8a49d667ec80bad0d434e8be58a

bus-nonce: b7a01a7c223d570280913db9855831ef

## Round

Round 3 of the fix review for #2964 (R10-FLY-NIGHTLY-HB), at head 38ffa02aeb39e8a49d667ec80bad0d434e8be58a. This is the round-3 fixer commit b23e91e0 plus the orchestrator's automatic merge. Rounds 1 and 2 were blocked on `dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py`. That block is cleared: the harness's null control now runs clean and every mutant is killed.

## Findings

- The comment above the heartbeat-only launch, `tests/nightly_ha.py:3550` ("py-spy reads this process from a child of it: ptrace needs the cap"), still names only py-spy. On 3.14 the stdlib unwinder is now the sampler and needs the same cap. The body discloses this and leaves it to the reviewer. The cap is still granted and needed, and the sampler's own comment block (`tests/nightly_ha.py:285-291`) names both samplers. Carry: dismissed: comment wording only, the behaviour it describes (SYS_PTRACE granted) is correct for both samplers
- R10-NIGHTLY-HB-RESPAWN's premise has changed and must be re-measured before anything is built. The roster carry (commit d63e5544d, `dev/programme/rosters/wave-r10-groups.json`) states the precondition and the control: a respawn is owed only if a nightly on a main carrying this fix fails `hb:positive_control` with every try's sampler timed out or rc!=0, counted against the pre-merge history as the null. Carry: R10-NIGHTLY-HB-RESPAWN
- `tests / nightly-status` stays red after this merge. It reads dispatch 40835853528, whose only failing job is `slow` (job 123320354392, "Closed-loop simulation"), and this diff does not reach that lane. The body names and answers it under `## Red checks`. Carry: dismissed: main's slow-lane red, owed on main by defect-root-cause.md, not this diff's

## Evidence

- Head measured: 38ffa02aeb39e8a49d667ec80bad0d434e8be58a. It is still `refs/pull/2964/head` at verdict time. The body's `## Head` names this SHA (step 7).
- Policy: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty at e5ddba1fa. main has since moved to 2fde526340bdb1da17fa7a5cd8bff283cff2757c, and that move changes nothing under roles/ or rules/.
- Merge (step 13): `git merge-tree --write-tree origin/main 38ffa02` exits 0 against e5ddba1fa (tree a0138ad65) and against the moved main 2fde52634 (`ev/merge_tree_new_main.txt`). There is no conflict and no claim driver involved.
- Mutation proof (step 1), production line: I deleted `if importlib.util.find_spec("_remote_debugging") is not None: return [sys.executable, "-c", _STDLIB_SAMPLE]` from `sample_command()` and ran `tests/entities.py` under CPython 3.14.6. Result: `1 of 2473 ENTITY CHECKS FAILED`, and the failing check is `the stall sampler is the interpreter's own unwinder where it ships one, staged or not; ...` (`ev/entities_mutant_no_predicate.txt`). Unmutated head: `ALL 2473 ENTITY CHECKS PASSED` (`ev/entities_head.txt`).
- Mutant harness, the round-1/2 blocker. `PYTHONPATH=tests/hastub python dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py` at the head:
  - Under CPython 3.14.6: `M0-null all checks pass`, `SUMMARY killed=15 survived=0 null=ok`, EXIT 0.
  - Under CPython 3.12: the same summary.
  - Each of M1-M11, X1, X2, X3 and X5 prints `KILLED by:` with a named check. M11-pyspy-first is killed by the sampler-selection check (`ev/mutants_head_python3.14.txt`, `ev/mutants_head_python3.12.txt`).
  - Under the container's CPython 3.11 the harness cannot parse `tests/entities.py` (PEP 701 f-string at line 4265). The tree's floor is 3.13, so this is the environment, not the harness (`ev/mutants_head.txt`).
- Finder's harness at both ends (steps 2 and 3): `dev/audit/harnesses/r10_fly_nightly_hb.py` from the head, `--inproc`, CPython 3.14.6 with py-spy 0.4.2 (`ev/fly/*.txt`). Results:
  - base e5ddba1fa, plain hung: ok=0 fail=3, gaps 5281-5342 ms, sampler=py-spy.
  - base, plain real: ok=5 fail=0, gaps about 600.5 ms.
  - head, plain hung: ok=5 fail=0, sampler=python.
  - head, plain real: ok=5 fail=0.
  - N1: ok=0 fail=2, readings (False, False, False).
  - N2: ok=0 fail=2, readings (True, False, False).
  - N3: ok=0 fail=2, readings (True, True, False).
  - N4 hung: ok=0 fail=2, sampler=py-spy, gaps 5290-5322 ms.
  - Every row matches the body's direction and readings. I ran fewer runs than the body on base real (5 vs 10) and on head plain (5 vs 10).
- Smoke test: the lane's `_STDLIB_SAMPLE` snippet run against a live 3.14.6 process prints `Thread <id>` plus frames, rc=0.
- Class rule (step 6): the body's `git grep` at the head returns 8 lines in `dev/audit/rca/nightly-ha-pyspy-timeout.md`, 1 in `dev/programme/carries/carry-201.json`, and 1 in `dev/audit/harnesses/r10_fly_nightly_hb.py`. That is exactly the body's disposition list (`ev/class_rule_head.txt`). Its null at ac7353951 returns 8 lines outside `dev/audit/rca/`, 6 of them in the mutant harness, which matches the body (`ev/class_rule_ac7353951.txt`).
- Cheap checks at the head:
  - `env_drift.py --claims-only e5ddba1fa`: `claims hygiene: e5ddba1fa ok`.
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `closure.py select --diff e5ddba1fa`: `MODE: SCOPED -- 5 script(s) run, 28 scoped out.`
  - No golden fixture or claim file is touched (step 4).
  - `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched (step 5).
  - No budget file moves. `tests/closures.json` gains the group harness as one entry, earned by the new file (step 14).
- CI on the head, read from the check-runs API after every run concluded (`ev/checks.txt`):
  - Green: `gate` (123777274951 and the earlier runs), `pr-contract` (123777275679, started after `nightly-status` concluded), `tests / nightly-ha (stable)`, `tests / nightly-ha (2025.2.0)`, `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `tests / mutation`, `governance / instrument-self-tests`, `arch-score`, and every codeql run.
  - The only red is `tests / nightly-status` (123751563872). Its log says it is not a required check and does not block a merge, and the body answers it (step 11).
- Forward-carry (step 10): the roster carry is in `dev/programme/rosters/wave-r10-groups.json` at this head and states its control as a precondition.
- Not re-derived (step 8):
  - The real-container Docker figures: base probe 60 runs, ok 59; fix side 30 runs, ok 30, py-spy hung on 2. This container has no Docker. The body marks them as an earlier seat's.
  - The body's harness-mutant figure (import injection removed: `M0-null FAILS ... NameError`).
  - The CI figures at ac7353951. The head's own `nightly-ha (stable)` green above supersedes them.
- Instruments: the finder harnesses are both committed in this PR, and I built none of my own. The venv was created with uv at `/root/v314` from `tests/requirements-ci.txt` plus `py-spy==0.4.2`.
