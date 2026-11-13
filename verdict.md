Fix review: blocked c17c11af72a8af22fc19e5cd7360bf8adf0acabe merge-conflict: git merge-tree --write-tree origin/main 5288db5dad c17c11af72a8af22fc19e5cd7360bf8adf0acabe conflicts in tools/audit/seat/tick_loop.sh, where main's 38aee2235a wraps the --self-test argument arm in pr_bounded and this head deletes that arm; the round-4 class itself is closed at this head

bus-nonce: 7ed37fb3ee97986606a70a94e4e2eb06

## Block

- **Merge conflict with main.** `git merge-tree --write-tree origin/main c17c11af72a8af22fc19e5cd7360bf8adf0acabe` exits 1 against origin/main 5288db5dadbffbaf83cb4ed258a669d46c3224fe with `CONFLICT (content): Merge conflict in tools/audit/seat/tick_loop.sh` (`ev/merge_tree.txt`). The pull request reads `mergeable_state: dirty` too.
  - Since the merge base b6577827b4, main has changed one line of this file in 38aee2235a ("seat scripts: quiet train output by default with --verbose, and pr_bounded in 12 seat self-tests", merged by d3e955485a). It changed the argument loop's `--self-test) tick_loop_self_test; exit ;;` into `--self-test) [ -n "${PR_BOUND:-}" ] || { . "$(dirname -- "$0")/pr_args.sh"; pr_bounded tick_loop bash "$0" --self-test; }; tick_loop_self_test; exit ;;` (`ev/main_ticks.txt`).
  - This head deletes that arm, because the arm is the round-4 fail-open.
- **This conflict is not mechanical.** Taking main's line puts back a `--self-test` arm that runs the rows in the caller's environment. That is round 4's harm. The `failopen` mutant shape shows it, and rows (a) and (b) would then depend only on the refusal line.
  - Also, `PR_BOUND` is a caller variable, so `env -i` drops it. A `pr_bounded` placed before the re-exec would re-enter `--self-test` unbounded on every run.
  - The resolution has to keep `--self-test` free of any row-running arm. It needs to put main's bound somewhere it survives the `env -i` re-exec, for example on the `--self-test-rows` entry or as the re-exec's argv. Then it re-runs `whole`, `envi`, `failopen` and the `channels` arm at the merged head.
  - The resolution is not prescribed here.
- Everything else in scope is judged below. A re-review after the merge can confirm the resolution and the re-run arms as a delta.

## Evidence

- **Head and scope.** The head reviewed is c17c11af72a8af22fc19e5cd7360bf8adf0acabe (`ev/HEAD.txt`), from a detached worktree.
  - The rendered packet reads `## Review scope: full`, because no `verdict/<pr>` ref names 510c46643055. The round-4 verdict lives on a probe ref at 4b74a2492e. This seat's brief asks for a delta review against it.
  - Three-dot from the merge base touches only `tools/audit/seat/tick_loop.sh`, its instrument page, the harness, `tests/closures.json` and `dev/programme/delivery/3520.md`.
  - No `custom_components/` line moves, so the scope does not widen. `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` are untouched (`ev/version_untouched.txt` is empty).
- **Review packet** (`ev/review-packet.md`): `REFUSE introduced-red: unreadable`, because `instrument-self-tests` was queued. classify decides, see CI below.
- **The class is closed at this head.** Round 4's own drivers were re-run on a scratch copy of the head's five files, with `HPO_HEARTBEAT_REMOTE` set to a fresh bare repository and `TICK_RC=1`.
  - Control: `tick_loop self-test: 41 checks, 0 failed`, rc 0, victim holds no ref.
  - Exported `exec`: `line 67: refused: --self-test refused: the env -i re-exec did not replace this process ...; no row ran`, rc 1, no ref.
  - `BASH_ENV` `exec`: the same refusal, rc 1, `victim refs: 0`. The shadow log holds the skipped `/usr/bin/env -i ... --self-test-rows` call, so the shadow was taken and then refused.
  - Files: `ev/attack_exec_func.sh`, `ev/attack_bashenv.sh`, `ev/r4_driver_func.txt`, `ev/r4_driver_bashenv.txt`.
  - Round 4 at 510c466430, same drivers: `38 checks, 18 failed`, and the victim took `heartbeat/orchestrator`.
- **Why the class is closed, not the one name.** `tick_loop_self_test` has exactly one caller, `tick_loop.sh:492` (`--self-test-rows)`). The argument loop has no `--self-test` arm, so an unknown `--self-test` hits `*)` and exits 2. A `--self-test` run now reaches a row only through the `env -i` re-exec, whatever stops the re-exec.
- **This seat's own channels beyond the fixer's set** (`ev/extra_channels.txt`). Each run used the same victim set-up through `BASH_ENV`.
  - `readonly refused=x` plus exec shadow: rc 2, 0 rows, 0 refs.
  - `declare -i refused` plus exec shadow: rc 2, 0 rows, 0 refs.
  - In both, the refusal line itself is defeated, but the second layer (the deleted arm, then `*)`) refuses. Only `cd`, `dirname` and `pwd` run in between (lines 68-104). This sits inside the body's disclosed `BASH_ENV`-code limit.
  - `alias exec=:` under `expand_aliases`: rc 1, the refusal.
  - Exported `exit` plus exec shadow: rc 1, the refusal. An expansion error runs no `exit` lookup.
  - `set -E` with an ERR trap: rc 1, the refusal.
  - `execfail`: rc 0, 41 rows, 0 refs. The exec succeeded.
  - An alias of the reserved word `case` (`set -- --self-test-rows; case`): rc 2 at `unknown argument --self-test-rows`, 0 rows, 0 refs. This one does enter `tick_loop_self_test` in the caller's process. It is hostile caller code rewriting the script's own words, which the body's disclosed limit names ("runs `--self-test-rows` itself"). It is not a seam a line of this script can close.
- **Mutation proof**, re-run with the in-tree harness at the head, one arm per run (`ev/harness_arms.txt`). Every row the body reports reproduces:
  - `whole: 41 checks, 0 failed rc=0`
  - `envi`: the refusal, rc=1
  - `carry: 1 failed` (poison row, 90 names)
  - `pathfirst: 1 failed`
  - `failopen: 2 failed` (fail closed func and bashenv)
  - `pipefail: 8 failed`
- **The `channels` arm** reproduces the body's ten lines and its four null controls (fn 4, bashenv 4, env 1, path 1), with a corpus of 85 names (`ev/harness_arms.txt`).
- **Shape arms**: branch, detached and gitdir each read `behind=1: 31 checks, 0 failed HEAD-UNMOVED`. shim and level each read `behind=0 ... 0 failed HEAD-UNMOVED`.
- **entities.py**: `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py` printed `ALL 2709 ENTITY CHECKS PASSED`, rc 0 (`ev/entities.txt`). An earlier run without `PYTHONPATH` failed on the import of `homeassistant`, as the body's command anticipates.
- **CI.** `merge_train.py classify` printed `WAIT c17c11af72a8af22fc19e5cd7360bf8adf0acabe pending: gate red: none` (rc 3) twice, about 10 minutes apart (`ev/classify1.txt`, `ev/classify2.txt`). This seat's dispatch says not to wait on CI. `merge_train.py owed-reds` is in `ev/owed_reds.txt`. No red was read, and the body's `## Red checks: none` has nothing to answer.
- **Not re-derived:**
  - the body's `real 1m42.892s`, which is a host timing
  - its `pr_args`, `offline_spy`, `bare_array`, `selftest_wiring`, `tmp_paths`, `brief_lint`, `structure.py` and `doc_claims.py` lines
  - `closure.py select`
- **Body figures that were checked** match this head: 41 checks, 3 rows added, 90 derived names, the mutation table, the channels table and the entities count.
