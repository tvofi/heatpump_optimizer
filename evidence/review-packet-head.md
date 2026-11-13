# Review packet #3520
head: 434213ade270b7debbd299681e2586416c6ec64f
base: 3038b9deaf915a4b3defedd52307f5c57e574a50

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
.github/dependabot.yml id=131910915393 success
CodeQL id=131914086680 neutral
arch-score / arch-score id=131913965457 queued
arm id=131910924519 skipped
budget-raise-gate / budget-raise-gate id=131913965430 queued
cancel-superseded id=131914594224 queued
codeql id=131912641730 skipped
codeql / Analyze (actions) id=131913965492 in_progress
codeql / Analyze (javascript-typescript) id=131913965395 success
codeql / Analyze (python) id=131913965315 success
gate id=131914489309 in_progress
governance id=131912641862 skipped
governance / delivery-status id=131913965506 queued
governance / delivery-status-publish id=131913967803 skipped
governance / env-matrix id=131913965525 queued
governance / instrument-self-tests id=131913965247 in_progress
governance / policy-docs id=131913965265 queued
governance / record id=131913967265 skipped
governance / wave-script id=131913965420 queued
hassfest id=131912642255 skipped
hassfest / hassfest id=131913965002 queued
kernel-points id=131913967010 skipped
pr-contract id=131914491479 skipped
prelude id=131914593922 queued
refresh id=131914594375 queued
tests id=131912641535 skipped
tests / briefs id=131913965128 queued
tests / closure-scope id=131913965042 queued
tests / mutation id=131913965120 success
tests / mutation-autofix id=131915010834 skipped
tests / mutation-pins id=131915009062 skipped
tests / nightly-status id=131913965186 queued
validate id=131912642575 skipped
validate / validate-hacs id=131913965257 queued

## Refusals
introduced-red: unreadable: head governance / instrument-self-tests job 131913965247: in_progress has not concluded: an introduced red cannot be ruled out (fail closed)

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified channels fn-all: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels bashenv-all: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels fn-exec: ...line 67: refused: --self-test refused: ...; no row ran rc=1 fn-calls=1 victim-refs=0
             no segment of this names a program this check knows
  unverified channels posix: /usr/bin/bash: `exec': is a special builtin rc=2 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels shellopts-posix: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels noexec:  rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels opts: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels env: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels path: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels ifs: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
             no segment of this names a program this check knows
  unverified channels null control fn: fn-calls=4
             no segment of this names a program this check knows
  unverified channels null control bashenv: fn-calls=4
             no segment of this names a program this check knows
  unverified channels null control env: fn-calls=1
             no segment of this names a program this check knows
  unverified channels null control path: fn-calls=1
             no segment of this names a program this check knows
  unverified channels corpus: 85 function names
             no segment of this names a program this check knows
  unverified bash "$0" --self-test
             the path `$0` is a template or an expansion, not a literal
  unverified python3
             python3 with no script argument
  ok         bash -n tools/audit/seat/tick_loop.sh
             `tools/audit/seat/tick_loop.sh` is in the tree at this head
  ok         bash -n dev/audit/harnesses/r10_tick_selftest_checkout.sh
             `dev/audit/harnesses/r10_tick_selftest_checkout.sh` is in the tree at this head
  ok         python3 tools/pr/ci_predict.py
             `tools/pr/ci_predict.py` is in the tree at this head
  ok         python3 tools/audit/seat/bare_array.py --check
             `tools/audit/seat/bare_array.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff 5288db5dadbffbaf83cb4ed258a669d46c3224fe
             `tests/closure.py` is in the tree at this head
  ok         tests/doc_claims.py
             `tests/doc_claims.py` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         bash dev/audit/harnesses/r10_tick_selftest_checkout.sh HEAD channels
             `dev/audit/harnesses/r10_tick_selftest_checkout.sh` is in the tree at this head
  unverified bash sources it, 1. -
             `sources` does not look like a path in this tree
  unverified is a special builtin there; bash refuses to import the function (rc 2) or never reads
             `refuses` does not look like a path in this tree

FIGURES: 9 resolved, 19 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Review scope: delta (later round over the reviewed head c17c11af72a8af22fc19e5cd7360bf8adf0acabe)
Confirm each finding of the previous verdict is resolved, re-read the live required checks, and review the delta below. Widen only to exactly the already-reviewed code a delta touching production code (custom_components/) puts at risk of being affected in a non-obvious way CI would not detect, naming the path and the risk in the verdict; an instrument, test, policy or body delta never justifies a wider review (fix-review.md step 12).

## Previous verdict at c17c11af72a8af22fc19e5cd7360bf8adf0acabe
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

