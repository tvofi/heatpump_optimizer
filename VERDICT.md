Fix review: blocked 510c46643055f5f2f9f61b815258a960518eabe0 class-open: a caller's exported function named exec (or one a caller's BASH_ENV defines) shadows the env -i re-exec on line 61, and the fail-open --self-test branch then runs every row in the caller's whole environment; with HPO_HEARTBEAT_REMOTE set the self-test force-pushed heartbeat/orchestrator into it and 18 rows failed

bus-nonce: 2a27aa9a931e707729af5e66b9dae97d

## Block

Round 4, the re-cut's handoff review. The scope is the delta `git diff fbde167568 510c466430`, which touches `tools/audit/seat/tick_loop.sh`, its instrument page and the harness, plus round 3's findings. No `custom_components/` line moves, so the scope does not widen. The body has no `## Review scope` line, and there is no review packet.

Round 3's two channels are closed (see Evidence). The re-cut closes variable names by construction, which the list rounds could not do. One seam of the class is still open, at the barrier itself.

- **The re-exec can be shadowed, and the branch behind it fails open.**
  - `tick_loop.sh:61` reads `case ${1:-} in --self-test) exec /usr/bin/env -i ...`. `exec` is a bash builtin, and bash outside POSIX mode resolves a function before a builtin. A caller's environment can define that function: `BASH_FUNC_exec%%`, which `export -f exec` writes, is imported at startup. A `BASH_ENV` file can define it too, because bash sources that file before line 1.
  - If `exec` is shadowed, line 61 calls the function and goes on. `$1` is still `--self-test`, so the argument loop reaches `tick_loop.sh:462`: `--self-test) shift; tick_loop_self_test "$@"; exit ;;  # reached only with the re-exec above taken out`. Every row then runs with the caller's full environment, `HOME`, `TMPDIR` and seat-bin `PATH`.
  - The body says "`env` is called by absolute path, so an exported function cannot replace it". That covers `env` and not `exec`. The instrument page's "no caller variable, nor a value computed from one, reaches a row" (`tools/audit/seat/instruments/tick_loop.sh.md:23-26`) is false at this head.
- **Measured at the head.** Both runs used a scratch copy of the five files, so no checkout was involved, and the same caller environment: `HPO_HEARTBEAT_REMOTE` set to a fresh scratch bare repository, and `TICK_RC=1`. The driver is `ev/attack_exec_func.sh`. This seat built it, not the finder.
  - Control, with no function: `tick_loop self-test: 38 checks, 0 failed`, rc 0. The victim repository has no refs (`ev/attack_control_victim.txt`, `ev/attack_control_out_tail.txt`). The barrier holds against both variables.
  - Attack, the same environment plus an exported `exec` that skips only the `/usr/bin/env` call and otherwise runs `builtin exec`: `tick_loop self-test: 38 checks, 18 failed`, rc 1 (`ev/attack_func_out.txt`). The victim then held `refs/heads/heartbeat/orchestrator TICK-PASS 2026-11-12T23:30:36Z relay=absent tick=1 code=none behind=unknown` (`ev/attack_func_victim.txt`). That is round 2's harm, back: the self-test force-pushed to a remote the caller named. `ev/attack_func_shadow.log` shows the outer re-exec and all four nested re-execs shadowed.
  - The same function, defined but not exported, in a `BASH_ENV` file: `38 checks, 18 failed`, rc 1. The re-exec was shadowed (`ev/attack_bashenv.sh`, `ev/attack_bashenv_out.txt`, `ev/attack_bashenv_shadow.log`). This brief's own instruction to run `tests/entities.py` under `env -u BASH_ENV` shows that seat shells carry a `BASH_ENV`.
- **Why this is the class and not one more instance.** The poison row cannot see this seam. It derives `$`-referenced and `environ` names, but a function name is neither. Its nested run gets a clean environment from the outer rows, so no row puts a function in front of line 61. All 4 mutants are killed and the null control is green, yet the barrier the four rounds converged on is bypassed by one name. The `--self-test)` branch at `:462` is the reason a bypass becomes the full caller environment instead of a refusal. It is kept only for the `envi` mutant's sake.
- **Repair direction (not prescribed):** make the barrier fail closed. The `--self-test)` arm at `:462` refuses, with rc not 0 and no row run, instead of running the rows. The rows then run only from `--self-test-rows`, which is reached only through `env -i`. Add a row that runs the self-test nested with an exported `exec` function and a detectable `HPO_HEARTBEAT_REMOTE`, and requires a refusal and an untouched remote. Correct the body's "an exported function cannot replace it" sentence and the instrument page. Under that shape, the `envi` mutant (re-exec deleted) also yields a refusal, so the poison row still kills it.

## Evidence

- Head reviewed: 510c46643055f5f2f9f61b815258a960518eabe0 (`ev/HEAD.txt`), from a detached worktree. It was re-read before return: `handoff/r10-hotfix-tick-selftest-checkout` and `handoff-wip/...` both point at it. The body's `## Head` names the same SHA.
- No pull request exists and no review packet was issued. No CI has run at this head, so no check run was read. `merge_train.py owed-reds` printed its set (`ev/owed_reds.txt`), none of which has run. The body's `## Red checks: none` has nothing to answer.
- Role files: `git diff 8c10361eb1...origin/main -- dev/governance/roles/` is empty.
- Merge: `git merge-tree --write-tree origin/main 510c466430` exited 0 against origin/main f44e761c19, with `LEDGER-MERGE: resolved tests/closures.json` and tree 037583b045 (`ev/merge_tree.txt`). The head is behind main and merges cleanly.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` are untouched in the three-dot diff from 8c10361eb1 (`ev/version_untouched.txt` is empty).
- Mutation proof, re-run with the in-tree harness at the head, one arm per run. It reproduces the body row for row:
  - `whole: 38 checks, 0 failed rc=0`
  - `carry: 1 failed`
  - `pathfirst: 1 failed`
  - `envi: 1 failed`, the poison row each time
  - `pipefail: 7 failed`
  - Logs: `ev/arm_*.txt`.
- Round 3's channels are closed at this head. The `carry` and `pathfirst` arms put each channel back, and each is killed. The control run above set `HPO_HEARTBEAT_REMOTE` and `TICK_RC` in the caller and stayed green with the remote untouched.
- The harness is the fixer's, landed in this branch. This review's attack driver is this seat's own (`ev/attack_exec_func.sh`, `ev/attack_bashenv.sh`).
- Derived names: the body's rule, run from `tools/audit/seat/`, printed 88 names (`ev/derived_names.txt`). All 7 names the body lists are in it.
- `closure.py select --diff 8c10361eb1` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`ev/select.txt`).
- `doc_claims.py` printed `ALL 343 checks PASSED` and `structure.py` printed `STRUCTURE RATCHET PASSED` (`ev/cheap_checks.txt`).
- `env -u BASH_ENV python3 tests/entities.py`: printed `ALL 2709 ENTITY CHECKS PASSED`, rc 0, matching the body (`ev/entities.txt`).
- Not re-derived: the body's `real 1m31.974s` (host timing). Its "evil_git_calls=0" replay of round 3's attack was not re-run separately. The `carry`/`pathfirst` arms and the control above cover those channels.
