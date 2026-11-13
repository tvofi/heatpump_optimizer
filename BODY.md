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

Round 6 (reconcile, merge with main): origin/main 5288db5dad merged into the PR head c17c11af72; the one conflict, `tools/audit/seat/tick_loop.sh`, is resolved as a union of main's 38aee2235a (`pr_bounded` around `--self-test`) and this branch's fail-closed `env -i` barrier, the bound taken inside the cleaned environment on the `--self-test-rows` entry (no allow-list widening); the union is proved clause by clause under `## Figures`, and a new row and harness arm pin the bound.

## Review scope

`git diff c17c11af72a8af22fc19e5cd7360bf8adf0acabe bab56d8017035e8b3436b29efee43f1499978a60`. Its non-main part is `tools/audit/seat/tick_loop.sh` (the conflict resolution, one row, the nested clone's file list) and `dev/audit/harnesses/r10_tick_selftest_checkout.sh` (a `bound` arm, `pr_args.sh` in the scratch copy); the rest is main's own commits through 5288db5dad. No `custom_components/` line moves.

## Head

bab56d8017035e8b3436b29efee43f1499978a60, descending from the merge 06a18faeb5 (c17c11af72 + origin/main 5288db5dad). Merge base 5288db5dadbffbaf83cb4ed258a669d46c3224fe. origin/main was at 23963d39be3a3202d91258c9ebe22bafca6cfd83 at 2026-11-13T12:44:50Z; `git merge-tree --write-tree origin/main HEAD` printed one tree (6e6d43de82) and exited 0, so no second merge.

## Mutation proof

Round 6, at bab56d8017035e8b3436b29efee43f1499978a60: `bash dev/audit/harnesses/r10_tick_selftest_checkout.sh HEAD whole envi failopen bound` (each arm a scratch copy that is not a checkout, now six files with `pr_args.sh`):

    whole: tick_loop self-test: 42 checks, 0 failed rc=0
    envi: .../m-envi/tools/audit/seat/tick_loop.sh: line 67: refused: --self-test refused: the env -i re-exec did not replace this process (a caller function named exec?); no row ran rc=1
    failopen: tick_loop self-test: 42 checks, 2 failed rc=1
        FAIL fail closed (func): a caller function named exec that skips the env -i re-exec ends in a refusal, ...
        FAIL fail closed (bashenv): a caller function named exec that skips the env -i re-exec ends in a refusal, ...
    bound: tick_loop self-test: 42 checks, 1 failed rc=1
        FAIL the rows run under pr_args.sh's self-test bound: PR_BOUND set, a session of their own

- `bound` (new, `# mut:selftest-bound`) deletes main's bound from the rows' entry: killed by the new row. Main's 38aee2235a added no row for tick_loop's bound (its only test-side change is `merge_train.py`'s), so before this round nothing in tick_loop's self-test pinned it; `pr_args.sh --self-test` pins `pr_bounded` itself.
- `envi` and `failopen` (the round-5 refusal mutant) are still killed.
- Disclosed self-correction: at the merge 06a18faeb5 the bound was fail-open. The harness's `whole` arm, whose copy then lacked `pr_args.sh`, failed the new row (`42 checks, 1 failed`): `.` failed and the rows ran unbounded. b2eb556cfd makes the entry refuse when the bound does not take and adds `pr_args.sh` to the harness copy. That refusal then failed the four nested-checkout rows, whose clone also lacked `pr_args.sh` (the reviewer-driver control at b2eb556cfd: `42 checks, 4 failed`). bab56d8017 adds the file to that clone.

Earlier rounds' proof, at d1bbd165d9 (unchanged):

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

Round 6, at bab56d8017035e8b3436b29efee43f1499978a60. `time bash tools/audit/seat/tick_loop.sh --self-test`: `tick_loop self-test: 42 checks, 0 failed`, rc 0, `real 1m41.178s`. Pre-merge counts, each side run whole: this branch at c17c11af72 `41 checks, 0 failed`; main at 5288db5dad `30 checks, 0 failed`. The +1 is the bound row; main's change adds no tick_loop row.

The bound fails closed, null for the refusal: a copy of the five files without `pr_args.sh`, run from `/`, printed `tick_loop self-test: refused: pr_args.sh's bound did not take (pr_args.sh missing or pr_bounded failed); no row ran`, rc 1.

The reviewer's two drivers (`ev/attack_exec_func.sh` at 4b74a2492e, and `ev/attack_bashenv.sh` as the `BASH_ENV` file with its log path pointed at the scratch directory), each against a scratch bare repository as `HPO_HEARTBEAT_REMOTE` and `TICK_RC=1`, with the source a symlink to the checkout at bab56d8017035e8b3436b29efee43f1499978a60:

    control: tick_loop self-test: 42 checks, 0 failed  rc=0   victim refs: none
    func:    --self-test refused: the env -i re-exec did not replace this process (a caller function named exec?)  rc=1   victim refs: none
    bashenv: --self-test refused: the env -i re-exec did not replace this process (a caller function named exec?)  rc=1   victim-refs=0

Two shadow-log lines, one per attack, each holding the skipped `/usr/bin/env -i ... --self-test-rows` call: the shadow was taken and refused. The func driver's log lands in `shadow-.log`, because its function reads `$arm`, which the driver does not export.

Earlier round:

`whole` above: `41 checks, 0 failed rc=0`. The new null row: the same caller (`HPO_HEARTBEAT_REMOTE` a scratch bare repository, `TICK_RC=1`) with no function named `exec` passes, the repository holding no ref.

The reviewer's two drivers, re-run at d1bbd165 on a scratch copy of the five files (`ev/attack_exec_func.sh` at 4b74a2492e95ce3d08c3dda4033cf0d3295264c4, and `ev/attack_bashenv.sh` as the `BASH_ENV` file, its log path pointed at the scratch directory):

    control: tick_loop self-test: 41 checks, 0 failed  rc=0   victim refs: none
    func:    line 67: refused: --self-test refused: ...; no row ran  rc=1   victim refs: none
    bashenv: line 67: refused: --self-test refused: ...; no row ran  rc=1   victim refs: 0

Each attack's shadow log holds the skipped `/usr/bin/env -i ... --self-test-rows` call, so the shadow was taken and refused, not missed.

## Figures

- **The union, read back from the merged file at bab56d8017035e8b3436b29efee43f1499978a60** (orchestrator.md section 6). Main's 38aee2235a, one changed line in `tick_loop.sh`, three clauses: (1) the `[ -n "${PR_BOUND:-}" ] ||` guard is at line 72; (2) `. "$(dirname -- "$0")/pr_args.sh"` is at line 72; (3) `pr_bounded tick_loop ... "$0"` is at line 72, now with `"$BASH" "$0" "$@"` where main has `bash "$0" --self-test`, because it re-enters the `--self-test-rows` entry it guards. Main's fourth clause, `tick_loop_self_test; exit` in the argument loop's `--self-test)` arm, is not kept as an arm: the branch deleted that arm (it was round 4's fail-open), and the rows run from line 503's `--self-test-rows)` arm, the branch's own. This branch's clauses: the `env -i` re-exec at line 66 (`# mut:selftest-envi`), the refusal at line 67 (`# mut:selftest-failclosed`), the `--self-test-rows` arm at line 503, the deleted `--self-test)` loop arm (`grep -n -- '--self-test)' tools/audit/seat/tick_loop.sh` prints only lines 66 and 67). Added this round: the bound's refusal at line 72 (`# mut:selftest-bound`), the bound row at line 230, and `pr_args.sh` in the nested clone at line 415. No other file was resolved by hand: `tests/closures.json` auto-merged.
- **Why inside the cleaned environment, and not through the allow-list.** The bound runs after the `env -i` re-exec, on the `--self-test-rows` entry before `SELFTEST_TMP` is made, so `pr_args.sh` is sourced, and `python3` is looked up, under the literal `PATH`, with no caller function or `BASH_ENV`. The allow-list stays `PATH` alone: `pr_bounded` sets `PR_BOUND` itself, inside the process. The other order, bound before the re-exec, would source `pr_args.sh` and look up `python3` in the caller's environment, ahead of the refusal. That would put back command lookups the round-5 shape keeps out from ahead of the refusal. A caller's `PR_SELFTEST_SECONDS` is not carried, so the rows take the default 1200 s bound. A nested run (the nest, poison and shadow rows) is bounded again under its own supervisor, whose watchdog ends it when the outer bound ends that supervisor.
- `bash -n tools/audit/seat/tick_loop.sh` and `bash -n dev/audit/harnesses/r10_tick_selftest_checkout.sh`: rc 0. At bab56d8017035e8b3436b29efee43f1499978a60: `python3 tools/pr/ci_predict.py` printed `CI PREDICT: no closures, fast, governance or instrument red predicted against 5288db5dadbf`; `python3 tools/audit/seat/bare_array.py --check` rc 0; `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED` (at 06a18faeb5; the later commits touch only these two shell files).
- Scope: `python3 tests/closure.py select --diff 5288db5dadbffbaf83cb4ed258a669d46c3224fe` printed `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/doc_claims.py`, `tests/entities.py`). At bab56d8017035e8b3436b29efee43f1499978a60: `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/doc_claims.py` printed `ALL 348 checks PASSED`, and `PYTHONPATH=tests/hastub env -u BASH_ENV python3 tests/entities.py` printed `ALL 2711 ENTITY CHECKS PASSED`, rc 0.

Round 5's figures, at 12ead5feae:

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


## Red checks

- `tests / briefs`, red at c17c11af72 (run 43426401498, 2026-11-13T12:36Z, `TOTAL: 27 error(s) across 46 file(s)`, every one a legacy carry file's `control`). Cause: base skew, not this branch's diff. The job checks out the head and restores only the graders' `tools/policy/*.mjs` and `*.py` from origin/main (588aad8d5a). Main's `brief_lint.mjs` reads main's `tools/policy/legacy_control_files.json` exemption list, which a head behind main lacks, so the head's archived carry files were refused. Reproduced: in a c17c11af72 checkout, `git checkout 588aad8d5a -- 'tools/policy/*.mjs' 'tools/policy/*.py'; node tools/policy/brief_lint.mjs` printed `TOTAL: 27 error(s) across 46 file(s)`, rc 1. Null control: the same with all of `tools/policy/` restored (the exemption list included) printed `TOTAL: 0 error(s) across 46 file(s)`. At this head, which carries main's exemption list through the merge, `node tools/policy/brief_lint.mjs` printed `TOTAL: 0 error(s) across 45 file(s)`, rc 0, and the same at its merge with origin/main 23963d39be. Cheaper detector: `git merge-tree --write-tree origin/main HEAD`, which `prepr.sh` already runs in under a second. It reported this head's conflict before CI ran, and this round's merge answers it. `tools/pr/ci_predict.py` does not see this class: its own line says `a data-file read is not seen`. No new countermeasure: the existing detector fired, and the skew ends at the merge.
- This round read the check runs of PR head c17c11af72 once (`get_check_runs`) and that job's log, nothing per commit. `prepr.sh`'s body check, which reads the owed-reds set, named only this check. The new head has run no CI yet.

## Forward-carry

none

## Friction

none
