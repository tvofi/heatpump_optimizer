Hotfix for the tick loop's self-test, which could read and move the checkout it ran from, and through which a caller's environment reached the rows. `tools/audit/seat/tick_loop.sh --self-test` now re-runs itself under `env -i` as its first executable statement, carrying no caller variable at all. One poison row, derived from what the script reads, replaces the rows that each tested one name. The loop's production lines are unchanged.

## Re-cut

This is round 4, so the old body is replaced rather than repaired (`fixer.md`, "Past three rounds"). Three reviews each found one more caller variable reaching a row: the drop list, then the allowlist, then `SPY_REAL_GIT` (carried on the allowlist) and `HPO_STATE_DIR` (reaching rows through the PATH computed before the old re-exec). The list was the defect. Cut:
- the allowlist (`SELFTEST_ENV`), its carry of `PATH`, `TMPDIR`, the nesting flag and `offline_spy.py`'s two variables, and the entry check that refused names off it;
- the "every loop variable set in the caller" nest row and the allowlist refusal row (per-name rows);
- `HPO_TICK_SELFTEST_NESTED` as the nesting signal. It is now the argument `--nested`, because no variable crosses the re-exec.

Kept from earlier rounds: the 2 MB pipefail pin and its `set +o pipefail`, the nested checkout rows (branch, detached, `GIT_DIR`, and the behind-0 null control), the scratch `HPO_TICK_CODE_DIR`, the early `throwaway_git_env`, the plain-gh row and the slow-relay row.

The shape:
1. **Re-exec first.** Before `set -uo pipefail` or any computation, `--self-test` runs `exec /usr/bin/env -i PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:${BASH%/*}" "$BASH" "$0" --self-test-rows ...`. `env` is called by absolute path, so an exported function cannot replace it. `BASH` is the running bash's own path, which bash sets at startup whatever the caller exports (`BASH=/x bash -c 'echo $BASH'` printed `/usr/bin/bash`). The internal entry `--self-test-rows` then creates fresh `HOME` and `TMPDIR` under its own `mktemp -d` (no `TMPDIR` is set at that point), before the seat-bin PATH line reads `HOME`. It removes them on exit.
2. **The poison row.** Each name is derived from the script and its helpers, never listed. The rule is a `$`-reference in the shell files the rows source or run (`tick_loop.sh`, `heartbeat.sh`, `tests/throwaway_git.sh`), or an `environ`/`environ.get`/`getenv` key in the Python ones (`ref_privacy.py`, `offline_spy.py`); the command is in `## Figures`. The row exports every derived name in the caller, set to `https://127.0.0.1:9/<nonce>-<NAME>.git`. `PATH`'s sentinel keeps `/usr/bin:/bin` after it, so a leaked PATH still runs and is caught by the nonce rather than by a crash. The row then runs `--self-test --nested` under `offline_spy.py`. It requires rc 0, `network=0 remote_git=0`, a tally with 0 failed, an environment dump present at the rows' root (`  env: PATH=`), stub-row dumps present (`  row env: PATH=`), and the nonce absent from the whole nested output. A nested run prints its own environment and argv, and at its end every environment and argv seen by the relay, tick and heartbeat stubs. The row fails if the derived list is empty.
3. **The spy row** now runs the rows' entry directly under `offline_spy.py`, so the spy's PATH wrapper sees their git calls. Its `SPY_REAL_GIT` is the one `offline_spy.py` finds on the clean run's literal PATH, because none is carried. Disclosed limit: `offline_spy.py` cannot see past `env -i`, since the literal PATH drops its wrapper directory. The poison row's `network=0 remote_git=0` therefore holds with `git=0` counted. The row carries the no-network property by sentinel absence and an unchanged root environment; this spy row carries the git count.

Disclosed self-correction: the first cut of the poison row was vacuous. Its `ck` label held `$(... | grep -c .)`, and that substitution reset `$?` before `ck` read it, so the row printed `ok` while it printed `leaked:` lines. The `carry` mutant survived (`38 checks, 0 failed`) and exposed it. The count is now taken before the predicate (commit 510c466430), and the mutant is killed below.

Alternatives, and why each lost. One was to unset `SPY_REAL_GIT` in the spy row and strip the seat-bin prefix from the carried PATH, the two repair directions the verdict sketched. Each closes one channel and leaves the next name to the next review. That is the list shape `fixer.md` step 17 names (#1874, #2345). Another was to keep an allowlist with an empty carry and a check on the internal entry. The check would refuse the spy row's own environment, which the spy builds, so the spy row would need an exception, which is a list again.

## Head

510c46643055f5f2f9f61b815258a960518eabe0, merge base 8c10361eb1fea539dc5acb8f7442eac2810faa47. origin/main was at a18e2e9d00b17a0349f29938a469d1bc3edd1ae3 at 2026-11-12T22:29:26Z. `git merge-tree --write-tree origin/main HEAD` exited 0 (no conflict).

## Mutation proof

Each mutant runs the whole self-test from a scratch copy that is not a checkout, using `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh HEAD <arm>` at 510c466430, one arm per run:

    carry: tick_loop self-test: 38 checks, 1 failed rc=1
        FAIL the poison row: the 88 names the script and its helpers read, ...
    pathfirst: tick_loop self-test: 38 checks, 1 failed rc=1
        FAIL the poison row: the 88 names the script and its helpers read, ...
    envi: tick_loop self-test: 38 checks, 1 failed rc=1
        FAIL the poison row: the 88 names the script and its helpers read, ...
    pipefail: tick_loop self-test: 38 checks, 7 failed rc=1
        FAIL a row's verdict is its reader's: a grep -q that leaves at its match, ...

- `envi` deletes the re-exec line.
- `carry` inserts `SPY_REAL_GIT="${SPY_REAL_GIT-}"` into the `env -i` carry: one caller variable, round 3's first channel.
- `pathfirst` moves the seat-bin PATH computation (`SEAT_BIN=`, the `# mut:seatbin` line and `export PATH`) above the re-exec and has the re-exec carry `PATH="$PATH"`: round 3's second channel.
- `pipefail` deletes `set +o pipefail`: the kept earlier repair. Its other six FAILs are the nested and spy rows that run that row again.

## Null control

`bash dev/audit/harnesses/r10_tick_selftest_checkout.sh HEAD whole` at 510c466430 printed `whole: tick_loop self-test: 38 checks, 0 failed rc=0`.

The verdict's attack, replayed at the head: a logging pass-through git written to scratch, set as `SPY_REAL_GIT`, as `$HPO_STATE_DIR/bin/git` and first on the caller's PATH. Then `bash tools/audit/seat/tick_loop.sh --self-test` printed `rc=0 tick_loop self-test: 38 checks, 0 failed evil_git_calls=0`. Control: one `git --version` through that PATH logged `1`, so the logger counts when it is reached.

## Figures

- Derived names: 88, printed in the poison row's label at 510c466430. The rule is `{ grep -ohE '\$\{?[A-Za-z_][A-Za-z0-9_]*' tools/audit/seat/tick_loop.sh tools/audit/seat/heartbeat.sh tests/throwaway_git.sh | sed 's/^\$[{]*//'; grep -ohE "(environ(\.get)?[[(]|getenv\()[\"'][A-Za-z_][A-Za-z0-9_]*" tools/audit/seat/ref_privacy.py tools/audit/seat/offline_spy.py | sed -E "s/.*[\"']//"; } | sort -u`, run in the row from the script's own directory. It includes `PATH`, `HOME`, `TMPDIR`, `HPO_STATE_DIR`, `HPO_HEARTBEAT_REMOTE`, `SPY_REAL_GIT`, `SPY_LOG` and every `HPO_TICK_*` the script reads. It also includes shell locals, which are harmless to export. Null control: the row fails on an empty list, and the three mutants above.
- Self-test: `time bash tools/audit/seat/tick_loop.sh --self-test` printed `tick_loop self-test: 38 checks, 0 failed`, `real 1m31.974s`, on this cloud host.
- Scope: `python3 tests/closure.py select --diff 8c10361eb1fea539dc5acb8f7442eac2810faa47` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (`tests/doc_claims.py`, `tests/entities.py`). `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/doc_claims.py` printed `ALL 343 checks PASSED`. `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py` printed `ALL 2709 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.

<!-- figure-block: scope-line mb=8c10361eb1fea539dc5acb8f7442eac2810faa47 head=510c46643055f5f2f9f61b815258a960518eabe0 -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->

## Red checks

none

## Forward-carry

none

## Friction

none
