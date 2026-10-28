prepr.sh: summary-only stdout by default, the full log in a unique temp file (R10-FLY-PREPR-SUMMARY, owner order tvofi 2026-10-28, prompt-cache gap 5).

A seat keeps each tool output in its context for every later turn. The brief measured prepr.sh's output alone at 27.6M cached-read tokens over 682 calls in one day. Once step 1 (merge-base) holds, `summary_start` sends stdout and stderr to `mktemp "${TMPDIR:-/tmp}/prepr-log.XXXXXXXX"` and keeps the real stdout on fd 3. Stdout then carries:
- one verdict line per step (`say`: ok / REFUSE / skip / WARN);
- for each refusal, its own log lines since the previous verdict (`refusal_lines`: the last 40, prefixed `    | `);
- the last line, `PRE-PR: <head> <digest> rc=<rc>; full log: <path> ...` (`summary_end`).

`PREPR_VERBOSE=1`, or a `--verbose` argument (stripped before step 0 reads `$1` as the body), prints today's full stdout instead. The `--self-test`, `--body-check`, `--fill-red`, `--pr-body` and `--version-edit` modes exit before the main flow and are unchanged.

Callers, enumerated by `git grep -nE 'prepr\.sh' -- '*.sh' '*.py' '*.mjs' '*.js' '*.yml'` with comment lines dropped. Two run the default mode, `tools/pr/push.sh` and `tools/pr/app_push.sh`, and both read the rc alone: push.sh's `PREPR=$?`, app_push.sh's `wait "$prepr_pid" || prepr_rc=$?`. `body_push.sh` runs `--fill-red` and `--body-check`, which are unchanged. update_pr.sh, open_pr.sh and handoff_push.sh reach prepr only through app_push.sh. merge_train.py parses app_push's own `app_push: RECARRY: prepr ...` line, not prepr's stdout. ci_predict.py and review_packet.py never run prepr. No tracked file parses `PRE-PR:`. Every self-test listed under Figures passed at the head.

For the reviewer, one design choice: with a body, the lines that stay in the log only are preflight's advisory `check` lines (the quantifier and figure prompts) and its closing `clean` line. They refuse nothing, and the `preflight` verdict line stays on stdout. On this body's run, stdout was 40 lines and the log 58. Surfacing the advisory prompts too would be a one-line change to `refusal_lines`'s trigger, if review wants it.

## Head

`4a7ccd9305ff9494f6b78117882490b889ff1e40` (base `b6f6ceca4f0323b24171c45a2a2372ba2e2cbaaa`, which was `origin/main` at 2026-10-28T22:05:20Z).

## Mutation proof

The failing test came first: self-test arm (12) drives the main flow's own `say`/`refusal_lines`/`step`/`summary_start`/`summary_end`, read from `$flow`. It runs them over a passing step with per-test chatter and a refusing step.
- Arm (12) grafted onto the base script: 5 of 8 rows fail. These are `summary stdout carries no passing step's per-test chatter`, `and the refusal's failing lines`, `the last line is the result with rc, naming a unique log under TMPDIR`, `and that log holds the full output`, and `the main flow starts the summary after step 1 and ends on its result line`.
- Mutant (cut from `632cc98c9`, which differs from the head by one comment line): `exec 3>&1 >"$PREPR_LOG" 2>&1` replaced by `exec 3>&1`, so the full log prints on stdout. The full `--self-test` of the mutant gave 414 passed, 13 failed. Besides the 9 environment rows (Red checks), it failed `summary stdout carries no passing step's per-test chatter`, `and the refusal's failing lines` and `and that log holds the full output`. It also failed `a change to prepr.sh owes the self-test`, which comes from running a copy outside the tree and not from the mutant.
- Restored head: arm (12) 8 of 8 pass; full `--self-test` 418 passed, 9 failed (the same 9 environment rows).

## Null control

- A refusal is still visible on stdout. Under the mutant, the row `and carries the REFUSE line with its reason (null control: the refusal stays visible)` passes, as it does at the head. Hiding the chatter never hid a REFUSE line.
- `PREPR_VERBOSE=1` restores the full stdout: row `PREPR_VERBOSE=1 prints the full output on stdout` passes at the head.
- The unmodified tree on the same no-body run, `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` from a detached worktree at the base, printed 33 lines with no log file. The head's run printed the same verdict set plus the result line naming the log, and nothing on stderr.

## Figures

- Self-test of the head: `bash tools/pr/prepr.sh --self-test` gave 418 passed, 9 failed. At the base, from a detached worktree, it gave 410 passed, 9 failed, with the same 9 rows. The 8 new passes are arm (12).
- Mutant self-test: `bash <copy with the exec redirect removed> --self-test` gave 414 passed, 13 failed.
- Arm (12) alone (a driver that evals the arm from the named copy): head 8/0, base+arm 3/5, mutant 5/3.
- Caller self-tests at the head, each rc 0: `tools/pr/app_push.sh --self-test`, `tools/pr/push.sh --self-test`, `tools/audit/seat/pr_args.sh --self-test` (144 checks, 0 failed), `tools/audit/seat/update_pr.sh --self-test`, `tools/audit/seat/open_pr.sh --self-test`, `tools/audit/seat/handoff_push.sh --self-test`, `python3 tools/pr/ci_predict.py --self-test`, `python3 tools/audit/seat/merge_train.py --self-test`, `python3 tools/audit/seat/review_packet.py --self-test`, `tools/audit/seat/train.sh --self-test`.
- `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` at the head: rc 1, refused only on `self-test` (the 9 environment rows). Its stdout is the verdict lines and the `PRE-PR: ... rc=1; full log: ...` last line.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` printed `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. Run-always lines run with `PYTHONPATH=tests/hastub`: `tests/env_drift.py --claims-only` rc 0, `tests/closure.py selftest` rc 0, `tests/layout.py` rc 0, `tests/harness_headers.py` rc 1 (`No module named 'voluptuous'`, the same at the base).
- `python3 tests/structure.py`: rc 0.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.

## Red checks

`self-test` (prepr step 3h, locally): 9 rows of 6b and the recorder-signal arms fail with `no interpreter that parses the tree was found (tried the seat venv at .../venv-ci/bin/python3 and the ambient python3)`. The base fails the same 9 rows in this container. `tools/audit/seat/seat_venv.sh` cannot build the venv here (`No download found for request: cpython-3.14.7-linux-x86_64-gnu`). These rows are environmental, not this PR's; CI's `governance` job runs the self-test with its own interpreter. The same goes for `tests/harness_headers.py`'s missing `voluptuous`.

## Unpinned sites

none: step 6d (`ci predict`) predicted no closures, fast, wave-script or instrument red and listed no unpinned site.

## Forward-carry

none

## Friction

none
