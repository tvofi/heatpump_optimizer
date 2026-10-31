Fix review: blocked 87abaed68871d3141b8221965d5a5860a075c43f root-cause-detectable: governance / instrument-self-tests is red on the PR's own gh_calls self-test (no-real-gh arm execs the runner's /usr/bin/gh), unanswered in ## Red checks

bus-nonce: 19ba64062b67482c2648ea4e738bf7e6

Round 1. Measured at head 87abaed68871d3141b8221965d5a5860a075c43f (contains handoff e807e83b36094e3b07b58968960a77d06bc785d7), from a detached worktree at that SHA. Merge base 7539d1675d7fc8b5020f90b395f4bb0c3485d5b3. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the contract I followed is current.

## Block

- **Red checks unanswered (step 11).** The head's workflows have all concluded. `merge_train.py classify` prints `RED 87abaed6… pending: none red: gate` (ev/ci-classify.txt). `pr-contract` run 124618578165 started after the last red concluded and still refuses the body for three checks that `## Red checks` does not name:
  - `governance / instrument-self-tests`
  - `CodeQL`
  - `code-scanning alert 46 (py/overly-permissive-file)`

  For instrument-self-tests a cheaper detector existed before the handoff (below), so the class is `root-cause-detectable`. The CodeQL alert body is unreadable from this seat (HTTP 403, ev/codeql-46.txt), so I did not re-derive which line it flags. The likely sites are the self-test's `chmod(0o755)` calls, which is an inference. The body must name and answer both.
- **The PR's own self-test is red in CI.** `governance / instrument-self-tests` (job 124609326791) concluded `failure` on this head at the step this PR adds:
  - The arm `FAIL no real gh: one line, rc 127, no self-exec` fails, and the run ends `gh_calls self-test: 19 checks, 1 failed` (ev/ci-instrument-self-tests-gh_calls.txt).
  - Cause: the self-test sets `PATH=<own>:<real>:/usr/bin:/bin` (gh_calls.py:171). The arm deletes only the stub. GitHub's runner image ships `/usr/bin/gh`, so the shim finds and execs that one instead of refusing with rc 127.
  - I reproduced it here by planting a temporary `/usr/bin/gh`, which gave `18 checks, 1 failed` (ev/repro-usr-bin-gh.txt), then removed the file.
  - The body's 18/0 figure was taken on a host with no gh in /usr/bin. The `## Red checks` section does not name this check.
  - A cheaper detector existed before the handoff: running the self-test on any host with gh in /usr/bin, or with `PATH` reduced to the stub dirs plus a dir that has `sh`/`ps`/`date`/`tr`/`cut`/`wc`/`mv` symlinked in.
  - Fix: make the test PATH hermetic.
- **class-open: the shim's own parent-command field.** Requirement (1) says the log never holds field values or bodies. The argv parser does drop them. But the third field is `ps -o args= -p $PPID` cut to 80 chars, and that field is not guarded. Any wrapper parent puts the full gh command line into the log, values included. Reproduced at this head (ev/leak-parent-field.txt):
  - `timeout 10 gh api repos/o/r -f body=VIA_TIMEOUT` logs `timeout 10 gh api repos/o/r -f body=VIA_TIMEOUT  api repos/o/r`.
  - `sh -c 'gh api repos/o/r/issues/1/comments -f body=SECRET_VALUE; :'` logs `body=SECRET_VALUE`.
  - `bash -c 'gh issue comment 1 --body TOPSECRET ...; :'` logs `TOPSECRET`.

  The self-test's only parent is the Python test runner, whose command line holds no gh arguments, so no arm reaches this case. The body does not name this field as a site. Fix direction, for the fixer to choose: log only the parent's executable and script name (argv[0], plus argv[1] when argv[0] is an interpreter), never its later args. Or apply the same value-stripping to the parent line, and when the parent is itself a gh-carrying wrapper, log its grandparent. Add a self-test arm where the parent is `sh -c '... -f body=secret'` and `timeout N gh ... -f body=secret`.
- **harness: design-trace-missing latency.** The brief requires the shim's per-call cost to be measured and stated as a number. The body states none. I measured it myself: about 20.9 ms per call over a `exit 0` stub (2.149 ms direct, 23.041 ms through the shim, 200 calls each, this container; ev/latency.txt). The cost comes from the ps/date/wc/tr/cut forks. The body owes the number, and the fixer's own figure on the host.

## Findings

- Surviving mutant: removing `--input` from the value-flag list leaves the self-test at 18/0. The arm "-X value, --input value and query string are dropped" puts `--input tokfile` after the path, where the parser has already stopped (`break`), so the arm cannot see the skip. `gh api --input FILE repos/o/r` is the case it misses: with the mutant, FILE is logged as the target. Add an arm that puts `--input` before the path. Carry: R10-FLY-GH-CALL-LOG
- Surviving mutant: replacing `clean()`'s `tr -c 'A-Za-z0-9_./:-' '?'` with `cat` leaves the self-test at 18/0. No arm feeds a token outside the allowed set, so the `?` claim in the body and the instrument doc is untested. Carry: R10-FLY-GH-CALL-LOG
- Mutant `usable()` without `! is_shim` (self-recursion): the self-test does not fail. It hangs, because the shim execs itself forever, and I stopped it at 60 s with `timeout`. In CI that is a hung job, not a FAIL line. Put a timeout on the self-test's `subprocess.run`. Carry: R10-FLY-GH-CALL-LOG
- No logging when the state directory is missing: the shim never runs `mkdir -p "$state"`, so on a host where `$HOME/.local/state/hpo` does not exist yet it logs nothing, silently. The null control depends on that, so a fix would make the null control use a read-only path instead. Carry: R10-FLY-GH-CALL-LOG

## Evidence

- RESULT self-test (env -u BASH_ENV, head): `gh_calls self-test: 18 checks, 0 failed`. As root, the read-only-directory arm prints `skip`, so the root container never ran that arm (ev/selftest-head.txt). The body's 18/0 is re-derived.
- RESULT mutants, each run by me (ev/mutants.txt):
  - drop-exec: 4 FAIL (byte, stderr/status, null control, mutant-present). Matches the body's mutation proof.
  - drop `-f|-F`: 1 FAIL.
  - fatal log write: 1 FAIL (null control).
  - no rotate: 1 FAIL.
  - no query cut: 1 FAIL.
  - no `-X` skip: 1 FAIL.
  - no parent cmd: 1 FAIL.
  - no is_shim: hang (rc 124 under timeout).
  - no `--input` skip: 0 FAIL (survives).
  - no clean: 0 FAIL (survives).
- RESULT argv leak probes: 14 shapes, among them `--input` before the path, `-H Authorization:…`, `--repo o/r` before the subcommand, `--field=k=v`, `-XPOST`, `pr create --title/--body`, `issue comment --body` and `search prs <query>`. No value reached the subcommand or target fields (ev/argv-leak-probes.txt). The leak is the parent field only.
- RESULT stdin/stdout/stderr/status pass-through: verified by the self-test arms, and they fail under the drop-exec mutant. Signals pass through via `exec`; checked by reading the code, not tested.
- Requirement (2): the body says it measured by reading the launchers, not live processes. It names `roster_queue.py` as not logged (its shims dir holds the file only as `seat-gh`). It names `beatd.py`, `daemonize.py --path-prepend` and `train.sh` as logged only if the install dir is on the inherited PATH. This container runs no daemon, so I could not re-derive a live count either. `--coverage` is the stated instrument for the host.
- Requirement (3): `--top`/`--since` arms pass, and a malformed `--since` is refused with rc 2.
- Classification: `gh_calls.py` is in tests/closures.json. The other new files are under INERT `tools/audit/`. INSTRUMENTS.md lists both.
- Blind spots (cloud seats sharing the token, record_row.py's direct urllib read) are stated in the docstring, the instrument doc and the body. No cache or poll change is in the diff.
- `git merge-tree --write-tree origin/main 87abaed6…`: rc 0, tree d1ca1d18116b9670df82949581535a3e4e7e3f08, no conflict (ev/merge-claims.txt).
- Claim files are byte-identical to origin/main. VERSION, the manifest and RELEASE_NOTES.md are untouched (three-dot diff empty).
- Delivery row dev/programme/delivery/3049.md is in the three-dot diff.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Scoped gate: `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (entities.py, harness_headers.py), the same set as the body.
- The PR body's head line names e807e83b…, and 87abaed6… is that plus only its own delivery row, as stated.
- Finder's harness: none is committed for P284. The self-test is the fixer's own instrument, disclosed as such. The leak probes and the latency loop are mine, built for this review (ev/).
- CI at this head: `classify` RED (`gate`). Red jobs: `governance / instrument-self-tests` 124609326791, `CodeQL` 124609893863, `pr-contract` 124617884716 and 124618578165, `gate` 124618012759 and 124618755912. Everything else is green or skipped. I did not re-run CI's heavy lanes.
