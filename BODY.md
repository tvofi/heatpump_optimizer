Hotfix for the tick loop's self-test, which could read and move the checkout it ran from, and through which a caller's environment reached the rows. `tools/audit/seat/tick_loop.sh --self-test` re-runs itself under `env -i` as its first executable statement, carrying no caller variable, and the barrier now fails closed: a `--self-test` the re-exec did not replace refuses, and the rows run only from the `--self-test-rows` entry that re-exec names. The loop's production lines are unchanged.

## Re-cut

Round 5, so the body is replaced, not repaired (`fixer.md`, "Past three rounds"). Rounds 1 to 3 each found one more caller variable reaching a row: the drop list, then the allowlist, then `SPY_REAL_GIT` and the seat-bin `PATH`. Round 4 replaced the lists with `env -i` and a poison row derived from the names the script reads, which closed every variable. Its review found the barrier itself open: a caller's function named `exec`, exported or defined by a `BASH_ENV` file, shadowed the re-exec, and the argument loop's `--self-test` arm, kept for the `envi` mutant, then ran every row in the caller's environment (18 rows failed, the reviewer's scratch `HPO_HEARTBEAT_REMOTE` took a forced `heartbeat/orchestrator`).

Why the list-shaped repairs kept leaving a seam: each closed the channel the last review demonstrated, and the property they guarded, "no caller input reaches a row", was enforced by a path that ran rows whenever the guard was bypassed. Any channel that stopped the guard from acting (a variable, then a function) reopened the whole class. Fail-closed ends it: the only path from `--self-test` to a row is the `env -i` re-exec, so a channel that stops the re-exec yields a refusal, whatever the channel is, and no row ever runs in the caller's environment.

The shape:
1. **Re-exec first** (unchanged): `case ${1:-} in --self-test) exec /usr/bin/env -i PATH="<literal>:${BASH%/*}" "$BASH" "$0" --self-test-rows ...`.
2. **Refusal next.** The following line, `case ${1:-} in --self-test) refused=; refused=${refused:?--self-test refused: ...}`, is reached only when the re-exec did not replace the process. It is an expansion error: it looks up no command name a function could shadow, and a non-interactive bash exits on it, rc 1, no row run. Placed directly after the re-exec rather than in the argument loop's arm (the verdict's direction, not prescribed): between line 68 and the loop the script looks up `set`, `cd`, `dirname`, `pwd`, `export` and `[`, each a name a caller's function could shadow. At the refusal, the only command name looked up so far is `exec`.
3. **The argument loop's `--self-test)` arm is deleted.** It was the fail-open. `--self-test` no longer reaches the loop; if it did, the `*)` arm refuses it as an unknown option (rc 2).
4. **Three rows** (inside the non-nested block): the nested self-test run with `HPO_HEARTBEAT_REMOTE` naming a fresh scratch bare repository and `TICK_RC=1`, under (a) an exported `exec` function that skips the `/usr/bin/env` call and logs that it did, (b) the same function defined in a `BASH_ENV` file, (c) neither (the null). (a) and (b) require rc not 0, the refusal message, no tally line, the shadow log non-empty (the attack was taken) and the repository holding no ref. (c) requires `0 failed`, no shadow log and no ref.

Kept from round 4: the `env -i` re-exec, the derived poison row, the spy row, the nested checkout rows, the pipefail pin. Corrected: round 4's sentence "`env` is called by absolute path, so an exported function cannot replace it" covered `env` and not `exec`; the instrument page `tools/audit/seat/instruments/tick_loop.sh.md` said "no caller variable, nor a value computed from one, reaches a row" unconditionally. It now states the fail-closed barrier, the rows that pin it, and the one limit below.

Disclosed limit, not closable by any line of a script: a `BASH_ENV` file is caller code executed inside this process before line 1. Where it defines functions (the measured attack), the shape makes it harmless; code that does more (runs `--self-test-rows` itself, a DEBUG trap under `extdebug` that skips commands) is the caller running the rows, as is any caller naming `--self-test-rows` directly.

Alternatives, and why each lost. `builtin exec` or `command exec` on the re-exec line: `builtin` and `command` are themselves shadowable, so it moves the seam one name. Refusing when any function is defined (`declare -F`): `declare` is shadowable and the check reads the artifact it guards. Refusing in the argument loop's arm, as the verdict sketched: fail-closed too, but six shadowable names are looked up before it; the arm placement adds those to the channels for no gain.

## Review scope

The delta is `git diff 510c46643055f5f2f9f61b815258a960518eabe0 12ead5feae3ccdb6b1628bec707a0a32b77be2b4`; its non-main part is `tools/audit/seat/tick_loop.sh`, `tools/audit/seat/instruments/tick_loop.sh.md` and `dev/audit/harnesses/r10_tick_selftest_checkout.sh`. No `custom_components/` line moves. The rest of that two-dot range is main's own commits, merged into the PR head 761e518126a81fb6f77e2afa028120fbe793291c.

## Head

12ead5feae3ccdb6b1628bec707a0a32b77be2b4, descending from 761e518126a81fb6f77e2afa028120fbe793291c. Merge base b6577827b4823cfacb0a309911f3572a6fccd7d2. origin/main was at 3b9749dac55a85c200005352c661198c982e5799 at 2026-11-13T10:57:45Z; `git merge-tree --write-tree origin/main HEAD` exited 0 (`LEDGER-MERGE: resolved tests/closures.json`, no conflict).

## Mutation proof

Each arm runs the whole self-test from a scratch copy that is not a checkout: `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh d1bbd165d9053951c2f0e15936cbd5f25d20afd0 <arm>`, one arm per run. d1bbd165 is the fix commit; the three later commits touch only the instrument page and the harness, not the script.

    whole: tick_loop self-test: 41 checks, 0 failed rc=0
    carry: tick_loop self-test: 41 checks, 1 failed rc=1
        FAIL the poison row: the 90 names the script and its helpers read, ...
    pathfirst: tick_loop self-test: 41 checks, 1 failed rc=1
        FAIL the poison row: the 90 names the script and its helpers read, ...
    envi: .../m-envi/tools/audit/seat/tick_loop.sh: line 67: refused: --self-test refused: the env -i re-exec did not replace this process (a caller function named exec?); no row ran rc=1
    pipefail: tick_loop self-test: 41 checks, 8 failed rc=1
        FAIL a row's verdict is its reader's: a grep -q that leaves at its match, ...
    failopen: tick_loop self-test: 41 checks, 2 failed rc=1
        FAIL fail closed (func): a caller function named exec that skips the env -i re-exec ends in a refusal, ...
        FAIL fail closed (bashenv): a caller function named exec that skips the env -i re-exec ends in a refusal, ...

- `envi` deletes the re-exec line: killed by the refusal itself, before any row (the outer run refuses; nested, it fails the poison and nest rows).
- `failopen` (new, `# mut:selftest-failclosed`) replaces the refusal with `set -- --self-test-rows "${@:2}"`: a skipped re-exec runs every row in the caller's environment, round 4's shape. Both attack rows fail.
- `carry`, `pathfirst`: round 3's two channels, each put back, killed by the poison row.
- `pipefail` deletes `set +o pipefail`; its other seven FAILs are rows that run that row again nested (one more than round 4: the new null row is a nested run).

## Null control

`whole` above: `41 checks, 0 failed rc=0`. The new null row: the same caller (`HPO_HEARTBEAT_REMOTE` a scratch bare repository, `TICK_RC=1`) with no function named `exec` passes, the repository holding no ref.

The reviewer's two drivers, re-run at d1bbd165 on a scratch copy of the five files (`ev/attack_exec_func.sh` at 4b74a2492e95ce3d08c3dda4033cf0d3295264c4, and `ev/attack_bashenv.sh` as the `BASH_ENV` file, its log path pointed at the scratch directory):

    control: tick_loop self-test: 41 checks, 0 failed  rc=0   victim refs: none
    func:    line 67: refused: --self-test refused: ...; no row ran  rc=1   victim refs: none
    bashenv: line 67: refused: --self-test refused: ...; no row ran  rc=1   victim refs: 0

Each attack's shadow log holds the skipped `/usr/bin/env -i ... --self-test-rows` call, so the shadow was taken and refused, not missed.

## Figures

- **The class's seams, enumerated.** Two rules. (1) Command names looked up before the refusal: `grep -nv '^#' tools/audit/seat/tick_loop.sh | sed -n '1,3p'` prints lines 66 (the re-exec), 67 (the refusal) and 68 (`set -uo pipefail`); lines 66-67 hold `case` (a reserved word, never a function) and `exec`, so `exec` is the only name a function can shadow before the barrier. (2) The channels bash takes from its caller at startup (bash(1), INVOCATION and Shell Variables): imported functions, `BASH_ENV`, `ENV`, `POSIXLY_CORRECT`, `SHELLOPTS`, `BASHOPTS`, `PATH`, `IFS`. Each is driven by the harness's new `channels` arm, `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh HEAD channels` at 12ead5feae, every run beside a scratch `HPO_HEARTBEAT_REMOTE` repository and `TICK_RC=1`; `fn-calls` counts files the channel's functions or programs touched:

      channels fn-all: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
      channels bashenv-all: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
      channels fn-exec: ...line 67: refused: --self-test refused: ...; no row ran rc=1 fn-calls=1 victim-refs=0
      channels posix: /usr/bin/bash: `exec': is a special builtin rc=2 fn-calls=0 victim-refs=0
      channels shellopts-posix: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
      channels noexec:  rc=0 fn-calls=0 victim-refs=0
      channels opts: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
      channels env: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
      channels path: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
      channels ifs: tick_loop self-test: 41 checks, 0 failed rc=0 fn-calls=0 victim-refs=0
      channels null control fn: fn-calls=4
      channels null control bashenv: fn-calls=4
      channels null control env: fn-calls=1
      channels null control path: fn-calls=1
      channels corpus: 85 function names

  Dispositions:
  - exported functions, any name: `fn-all` exports a function for every bash builtin but `exec` (`compgen -b`) plus every command the script runs, 85 names; none is called (the re-exec replaces the process first, `env -i` drops `BASH_FUNC_*`), rows pass. `exec` itself: refused, pinned by row (a). Null control: the same corpus under `bash -c 'cd /; git status; mktemp; exit 0'` touched 4.
  - `BASH_ENV`: function definitions harmless (`bashenv-all`), `exec` refused (row (b)); other code is the disclosed limit above. Null control: 4.
  - `ENV`: not read by a non-interactive bash; `fn-calls=0`. Null control: an interactive `--posix` bash sources it, 1.
  - `POSIXLY_CORRECT`, `SHELLOPTS=posix`: `exec` is a special builtin there; bash refuses to import the function (rc 2) or never reads `BASH_ENV`; no row runs in the caller's environment.
  - `SHELLOPTS=noexec`: bash runs no line of any script, the caller's own gate included; no row, no tally line, rc 0. Out of the class (nothing of this script runs); a gate keying on the tally line reads it as missing.
  - `SHELLOPTS=errexit:nounset:xtrace`, `BASHOPTS=execfail:extglob`: dropped by `env -i`; rows pass. `execfail` matters only to a failed exec, which falls to the same refusal row (a) reaches.
  - `PATH`: the re-exec names `/usr/bin/env` and `$BASH` (set by bash itself) absolutely, and the rows get a literal PATH; a PATH led by a `bash`/`env`/`git`/`python3` that touch a file: `fn-calls=0`. Also pinned by the poison row's `PATH` sentinel. Null control: `git status` through that PATH touched 1.
  - `IFS`: bash does not import it (`env IFS=x bash -c 'printf "%q\n" "$IFS"'` printed `$' \t\n'`); rows pass.
- Derived names: 90 at this head (round 4: 88; the new rows add `$src`, `$refs`, `$refused` among others), printed in the poison row's label. Rule unchanged: `{ grep -ohE '\$\{?[A-Za-z_][A-Za-z0-9_]*' tick_loop.sh heartbeat.sh ../../../tests/throwaway_git.sh | sed 's/^\$[{]*//'; grep -ohE "(environ(\.get)?[[(]|getenv\()[\"'][A-Za-z_][A-Za-z0-9_]*" ref_privacy.py offline_spy.py | sed -E "s/.*[\"']//"; } | sort -u`, run from `tools/audit/seat/`. Null control: the `carry` and `pathfirst` mutants.
- Self-test: `time bash tools/audit/seat/tick_loop.sh --self-test` at d1bbd165 printed `tick_loop self-test: 41 checks, 0 failed`, rc 0, `real 1m42.892s` on this cloud host (38 rows before this round, 3 added).
- `bash -n` passes on `tools/audit/seat/tick_loop.sh` and `dev/audit/harnesses/r10_tick_selftest_checkout.sh`. At 92f82a80d7 (the last commit changes only the harness): `bash tools/audit/seat/pr_args.sh --self-test` printed `pr_args self-test: 205 checks, 0 failed`; `python3 tools/audit/seat/offline_spy.py --self-test` printed `offline_spy self-test: 10 checks, 0 failed`; and at 12ead5feae: `python3 tools/audit/seat/bare_array.py --check` rc 0; `python3 tools/audit/seat/selftest_wiring.py --check` printed `selftest_wiring: 0 index gap(s)`; `python3 tools/audit/seat/tmp_paths.py --check` printed `tmp_paths: 0 refused, 0 stale allow entries at HEAD`; `node tools/policy/brief_lint.mjs` rc 0; `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- Scope: `python3 tests/closure.py select --diff b6577827b4823cfacb0a309911f3572a6fccd7d2` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/doc_claims.py`, `tests/entities.py`). `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/doc_claims.py` printed `ALL 343 checks PASSED`. `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py` printed `ALL 2709 ENTITY CHECKS PASSED`, rc 0.

<!-- figure-block: scope-line mb=b6577827b4823cfacb0a309911f3572a6fccd7d2 head=12ead5feae3ccdb6b1628bec707a0a32b77be2b4 -->
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
