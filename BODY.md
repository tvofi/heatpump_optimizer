Adds the gh call-log (P284, triage s6-batch60.md#P284): a `gh` shim that records who calls GitHub, so the next exhaustion of the shared token's core bucket names its caller. No cache or poll change (out of scope; R10-ORCH-BEATD, P248).

- `tools/audit/seat/shims/seat-gh`, installed as `gh` by `seat_venv.sh --install-shims`: one line `<utc> <ppid> <parent cmd, 80 chars> <subcommand> <api path or verb>` to `$HPO_STATE_DIR/gh-calls.log`, flag values (`-f`/`-F`/`--input` and every other value flag) never read into the line, query string cut, any token outside `[A-Za-z0-9_./:-]` logged `?`. Then `exec` of the first real gh past itself. An unwritable log is skipped. Capped: past `HPO_GH_LOG_MAX` (1 MiB) it moves to `.1`.
- `tools/audit/seat/gh_calls.py`: `--top [--since <utc>]` ranks callers and endpoints; `--coverage [PID...]` names processes whose PATH finds a real gh before the shim; `--self-test` wired in governance.yml.
- Instrument docs and INDEX entries. `gh_calls.py` is classified by `tools/pr/ci_predict.py --apply-inert` (tests/closures.json, tests/entities.py's inert reads); the other new files are under INERT `tools/audit/`.

Daemon coverage (step 2), measured by reading the launchers: `roster_queue.py` prepends the checkout's `tools/audit/seat/shims`, which holds the shim only under the name `seat-gh`, so it does NOT log there (the shim is deliberately not named `gh` in that directory). `beatd.py` builds job PATH as `beatd_shims` + its own inherited PATH: logged only if the seat bin dir is on beatd's PATH. `daemonize.py --path-prepend` and `train.sh` (prepends venv-ci/bin only) likewise log only if the install dir is on PATH. No daemon runs in this container, so a live count is not measured here; run `gh_calls.py --coverage` on the host to name each that does not. Cloud seats share the token from another host and record_row.py's direct urllib read (line 882) are not counted.

## Head

9ad1cdcec61380ed5b13150118e2350b18e80832

## Mutation proof

Run `python3 -I tools/audit/seat/gh_calls.py --self-test` against a mutant shim. Dropping the exec pass-through (`exec "$real" "$@"` replaced by a call with output discarded): FAIL on "stub bytes pass through", "stderr and exit code pass through", "null control: unwritable log leaves output and status unchanged". Removing `-f|-F` from the value-flag list: FAIL on "-f/-F values placed before the path are dropped". Removing the hermetic guard's test (`hermetic_ok` made to return True): FAIL on both "mutation: a PATH that includes the fake gh fails the hermetic guard" and "mutation: the old-style PATH fails the hermetic guard". Round 2 mutants, each run by hand against the real shim under `env -u BASH_ENV` and each also an in-test arm ("mutant killed: ..."): removing `--input|` FAILs "--input FILE placed before the path is skipped"; `clean()`'s `tr` replaced by `cat` FAILs "a token outside the allowed set is logged with ?"; deleting `mkdir -p "$state"` FAILs "a missing state directory is created and the call logged"; disabling the redaction (both sed patterns) FAILs the planted-value, marker and census arms. Restored: 35 checks, 0 failed.

## Null control

Unmutated shim: an unwritable state directory leaves stdout, stderr and rc 7 identical to the stub's (arm "null control: an unwritable log leaves output and status unchanged"); the state directory is not created.

## Figures

- `python3 -I tools/audit/seat/gh_calls.py --self-test`: 35 checks, 0 failed (rule: every `ok`/`FAIL` line it prints), run under `env -u BASH_ENV`; also with with a fake executable gh planted first on the ambient PATH. Shim cost, measured on this host over 200 calls each against an `exit 0` stub: 20.42 ms direct, 76.37 ms through the shim, so about 56 ms per call (the ps/date/wc/tr/cut forks); the round-1 figure, taken before the parent redaction added a sed fork, is not re-measured.
- `bash tools/audit/seat/seat_venv.sh --self-test`: 21 checks, 0 failed.
- `python3 tests/closure.py select --diff origin/main`: scope.run = tests/entities.py, tests/harness_headers.py; both pass (entities 2493 checks on a rerun; one earlier run failed one check while a second copy ran concurrently, not reproduced).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `selftest_wiring.py --check`: 0 unwired.

## Round-1 findings, all answered

- Parent-command leak: the shim now replaces the parent's command line from its first value-bearing flag to the end of the line with `<redacted>`, flag name kept, before the 80-char cut. Long flags always (`--body --body-file --notes --notes-file --title --subject --desc --description --field --raw-field --header --input --jq --template --env-file --squash-merge-commit-message`); the short ones (`-f -F -H -b -n -t -T -q -d`) only when a `gh` word is on the line. Census: the free-text and secret-bearing flags of `gh api`, `issue comment|create|edit`, `pr create|comment|review|merge|edit`, `release create|upload`, `gist create`, `label create`, `workflow run`, `secret set`, `variable set`, `repo edit`, `search prs`, `run view|rerun`, read from `gh <cmd> --help`; a self-test arm sends each of 25 census flags through a `sh -c 'gh api ... FLAG VAL'` parent and requires VAL absent. Planted-body fixtures (`-f body=`, `--body`, `--field=k=`, glued `-fbody=`, `env gh pr create --body`) must read redacted, with the marker and `gh api repos/o/r` still present (non-vacuous); a non-gh parent keeps its `-m json.tool`.
- Surviving `--input` mutant: new arm with `--input FILE` before the path.
- Surviving `clean()` mutant: new arm with a path holding `$ ; \` logged as `?`.
- Hang under the self-recursion mutant: the self-test's `subprocess.run` has a 60 s timeout.
- Missing state directory: decision, the shim creates it (`mkdir -p`); the arm pins it, and the null control now uses a path under a regular file so it stays valid.
- Hermetic PATH, latency number and `## Red checks` answers are above and below.

## Red checks

- UNDER-SCOPED / closures INERT READS (predicted by prepr step 6d, repaired by `ci_predict.py --apply-inert` before handoff).
- `governance / instrument-self-tests`. Cause: the self-test arm "no real gh: one line, rc 127, no self-exec" ran with `PATH=<own>:<real>:/usr/bin:/bin` and deleted only its stub; GitHub's runner ships `/usr/bin/gh`, which the shim found and exec'd instead of refusing with rc 127 (`gh_calls self-test: 19 checks, 1 failed` in CI). On the author's Mac no gh sits at that path, so the arm passed locally. Fix: every arm's PATH is now hermetic (`<own>:<real>:<tools>`, where `<tools>` is a scratch dir of symlinks to only ps, tr, cut, wc, mv, date, cat, sh; never /usr/bin or /bin), and the no-real-gh arm asserts first (`hermetic_ok`) that the only gh on its PATH is the shim under test or none. Planted-defect control: a fake executable gh placed ahead of /usr/bin on the old PATH shape makes the old arm red (rc not 127, `DECOY` on stdout) and the hermetic PATH stays green; two mutation arms show the guard refuses a PATH holding the fake gh. Process state: a host-dependent test environment. Why prepr's CI-predict did not catch it: it reads the diff statically and does not run the self-test on a runner image; the failure depended on the host PATH (a gh in /usr/bin), which only the runner has. Countermeasure: the hermetic guard in the test itself, plus the fake-gh control, which reproduces the CI red on any host and so makes the detector cheaper than CI. No wider check is built: this is the first instance of the class in this instrument.
- `CodeQL` / code-scanning alert 46 (`py/overly-permissive-file`): the alert body is unreadable from this seat (HTTP 403 reported by the reviewer). The likely sites are the self-test's `chmod(0o755)` on a stub and shim in a private `tempfile.TemporaryDirectory()`; these files must be executable to run and live in a 0o700 scratch dir. This is an inference, not re-derived; left unchanged.

## Forward-carry

none

## Friction

none
