Adds the gh call-log (P284, triage s6-batch60.md#P284): a `gh` shim that records who calls GitHub, so the next exhaustion of the shared token's core bucket names its caller. No cache or poll change (out of scope; R10-ORCH-BEATD, P248).

- `tools/audit/seat/shims/seat-gh`, installed as `gh` by `seat_venv.sh --install-shims`: one line `<utc> <ppid> <parent cmd, 80 chars> <subcommand> <api path or verb>` to `$HPO_STATE_DIR/gh-calls.log`, flag values (`-f`/`-F`/`--input` and every other value flag) never read into the line, query string cut, any token outside `[A-Za-z0-9_./:-]` logged `?`. Then `exec` of the first real gh past itself. An unwritable log is skipped. Capped: past `HPO_GH_LOG_MAX` (1 MiB) it moves to `.1`.
- `tools/audit/seat/gh_calls.py`: `--top [--since <utc>]` ranks callers and endpoints; `--coverage [PID...]` names processes whose PATH finds a real gh before the shim; `--self-test` wired in governance.yml.
- Instrument docs and INDEX entries. `gh_calls.py` is classified by `tools/pr/ci_predict.py --apply-inert` (tests/closures.json, tests/entities.py's inert reads); the other new files are under INERT `tools/audit/`.

Daemon coverage (step 2), measured by reading the launchers: `roster_queue.py` prepends the checkout's `tools/audit/seat/shims`, which holds the shim only under the name `seat-gh`, so it does NOT log there (the shim is deliberately not named `gh` in that directory). `beatd.py` builds job PATH as `beatd_shims` + its own inherited PATH: logged only if the seat bin dir is on beatd's PATH. `daemonize.py --path-prepend` and `train.sh` (prepends venv-ci/bin only) likewise log only if the install dir is on PATH. No daemon runs in this container, so a live count is not measured here; run `gh_calls.py --coverage` on the host to name each that does not. Cloud seats share the token from another host and record_row.py's direct urllib read (line 882) are not counted.

## Head

e807e83b36094e3b07b58968960a77d06bc785d7

## Mutation proof

Run `python3 -I tools/audit/seat/gh_calls.py --self-test` against a mutant shim. Dropping the exec pass-through (`exec "$real" "$@"` replaced by a call with output discarded): FAIL on "stub bytes pass through", "stderr and exit code pass through", "null control: unwritable log leaves output and status unchanged". Removing `-f|-F` from the value-flag list: FAIL on "-f/-F values placed before the path are dropped". Restored: 18 checks, 0 failed.

## Null control

Unmutated shim: an unwritable state directory leaves stdout, stderr and rc 7 identical to the stub's (arm "null control: an unwritable log leaves output and status unchanged"); the state directory is not created.

## Figures

- `python3 -I tools/audit/seat/gh_calls.py --self-test`: 18 checks, 0 failed (rule: every `ok`/`FAIL` line it prints).
- `bash tools/audit/seat/seat_venv.sh --self-test`: 21 checks, 0 failed.
- `python3 tests/closure.py select --diff origin/main`: scope.run = tests/entities.py, tests/harness_headers.py; both pass (entities 2493 checks on a rerun; one earlier run failed one check while a second copy ran concurrently, not reproduced).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `selftest_wiring.py --check`: 0 unwired.

## Red checks

UNDER-SCOPED / closures INERT READS (predicted by prepr step 6d, repaired by `ci_predict.py --apply-inert` before handoff).

## Forward-carry

none

## Friction

none
