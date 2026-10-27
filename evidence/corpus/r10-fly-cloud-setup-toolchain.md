R10-FLY-CLOUD-SETUP-TOOLCHAIN: `tools/audit/seat/cloud-setup.sh` names the environment variables that put the toolchain on a cloud seat's PATH. It gives a seat `--check` to measure them, and writes a profile that leaves a stub PATH alone. Part of #2505 (the R10-ORCH-MACHINERY re-cut, design note on `design/R10-ORCH-MACHINERY` at 2fc665c61, section 3 row G; the parent issue stays open for the rest of that group).

The defect (the roster's five carries: #2572, #2554, the R10-BRIEFS-FOLD body, #2629, #2627): the payload says "the toolchain (venv python, node, gh) is on PATH from the environment". In a seat whose environment did not carry it, `python3` was the system interpreter. The root cause, measured in this container:

- A seat's Bash call is `/bin/bash -c "source <snapshot> && ..."`, started by the agent process. It inherits the agent's environment. The snapshot is built with `bash -c -l`, but on Linux it writes `export PATH=` from the agent's own PATH (`process.env.PATH`), not from the login shell's. So `/etc/profile.d/hpo-toolchain.sh` never reaches the seat's PATH through the snapshot.
- That shell is a first-level bash whose stdin is a socket. Bash then takes its remote-shell path: it reads `/etc/bash.bashrc` and `~/.bashrc` *in place of* `BASH_ENV`. The stock `~/.bashrc` starts with `[ -z "$PS1" ] && return`. The script appended its `. /etc/profile.d/hpo-toolchain.sh` hook after that return, so the hook never ran for any non-interactive shell.
- So nothing a setup script writes can put the toolchain on the seat's PATH. Only the environment's variables can (the agent's process env). In this seat they do: the agent process carries `PATH=/opt/hpo/venv-ci/bin:…`, `HPO_TYPING_PYTHON`, `OPENBLAS_CORETYPE` and `BASH_ENV`, set outside the tree. The script never named them.
- #2452's trap has the same cause: every *nested* bash reads `BASH_ENV`, and the unguarded profile prepends `venv-ci/bin` again, ahead of a test's `PATH=<stub>:$PATH`.

What changes (one module, plus its wiring):
- `cloud-setup.sh`: the header note states the mechanism above and the variables to set. The setup run's last line prints them. `--variables` prints them, one `NAME=value` per line, with `venv-ci/bin` exactly once and first. `--check` answers `OK` (exit 0) only when `python3` is venv-ci's, `HPO_TYPING_PYTHON` is executable and `OPENBLAS_CORETYPE` is the pinned core type. Otherwise it answers `REFUSE` naming the three values it read and the variables to set (exit 1). The core type is named once, as `CORETYPE`, and read by the profile, `--variables` and `--check`. `--self-test` covers 13 arms. The profile prepends `venv-ci/bin` only when it is absent (`case ":$PATH:"`). The dead `~/.bashrc` append is removed.
- `.github/workflows/governance.yml`: one step runs `cloud-setup.sh --self-test` beside `seat_venv.sh`'s, with the same `N checks, 0 failed` grep.
- `tools/audit/seat/INSTRUMENTS.md`: the `cloud-setup.sh` entry gets the modes, the corrected route and `--check`'s three conditions and exit codes. The cloud-runner trap line becomes "until the pasted setup script writes the idempotent profile".
- `dev/audit/harnesses/r10_cloud_setup_toolchain.py`: the finder's control as a re-runnable harness (fixer.md step 18), now with `check-ok` and `check-sys` arms. `dev/audit/harnesses/r10_cloud_setup_mutants.py`: the mutation table below, re-runnable. `tests/closures.json` records both among `harness_headers.py`'s inert reads (`ci_predict.py --apply-inert`).

Why `--check` now reads `OPENBLAS_CORETYPE` (review round 1's third finding): the variable pins the BLAS kernel the golden fixtures' floats were recorded under (`CLAUDE.md` rule 3). A seat without it can pass `python3` and still record or compare different floats. `--check` is the one measurement a seat runs, so it tests all three variables the script tells the owner to set.

Owner action, outside the tree: re-paste the script as the environment's setup script, and keep (or set) the variables `--variables` prints. `BASH_ENV` is not needed: it acts only in nested shells, and with the new profile it is harmless there.

Alternatives, and why each lost:
- Source the profile from the cloud payload (the brief's second option): every seat would spend a step on it. It also fails for any shell the seat does not start itself, and `cloud_dispatch.py` is outside this group's `files`. The variables fix it once, for every shell.
- Move the `~/.bashrc` hook above the `PS1` return: the seat's shell would read it. But the snapshot's `export PATH=` runs after it and overwrites it. A nested shell would then re-read it, which is #2452 again.
- An exported marker variable as the profile's guard: a test harness spawned from a shell that never read the profile carries no marker, so its `PATH=<stub>:$PATH` child still had the venv prepended. Checking for presence keys on the PATH itself.
- Export `BASH_ENV` from the profile: no shell that matters reads the profile first.
- Leave `OPENBLAS_CORETYPE` out of `--check` and triage it: rejected, because a seat missing it would read `OK` while the golden comparison it then runs differs.

## Head

2b641269e5b3bcdb724e07e36044c6b99315012e. Merge base 806aa2ce89aeb6c00cf756195f31026ab798f3ca, `origin/main`'s tip when measured (2026-10-24, from 16:37Z). Review round 2's head 5e4fbb0d3b14 plus one merge of `origin/main`. The code is unchanged: `git diff 5e4fbb0d3b14 HEAD -- <the seven files this PR changes>` is empty, and the three scripts' sha1s below match round 2's.

Review round 2 (blocked, carry-missing) and what answered it: the Forward-carry named R10-ORCH-MACHINERY, which is absorbed, and no roster brief held it. The carry is now on the roster as an `append-carry` to R10-FLOW-DESIGN-STAGES, the live group whose `files` list `tools/audit/seat/cloud_dispatch.py`, at 65c67fc26 on `handoff/audit-r10-roster`. The Forward-carry and the `cloud_dispatch` Friction line below name that group. The `fixer.md#2` Friction line goes to R10-POLICY-FIXER-MD, which owns `fixer.md`, at 8ecacecb1.

Review round 1 (blocked, mutation-vacuous) and what answered it:
- M9 (`check`'s python3-is-venv-ci half removed) survived 8 of 8 arms. New arm "check refuses the system python3 beside an executable HPO_TYPING_PYTHON" kills it. The harness's new `check-sys` arm reads it as `verdict: … no`.
- M12 (`--check`'s exit code) survived because no arm ran `cloud-setup.sh --check`. Two arms now run it, pinning exit 0 and exit 1.
- M7 and M10 (the profile's two exports) survived. New arm "check is OK in a shell that sourced the profile" kills both.
- `OPENBLAS_CORETYPE` was in no pattern and not in `check`. `check` now requires it (above), arm "check refuses without OPENBLAS_CORETYPE" pins that, and the refusal-text arm's pattern includes it.

## Mutation proof

Instrument: `python3 -I dev/audit/harnesses/r10_cloud_setup_mutants.py` (sha1 b4b5ba0df9ff5350f0f091715a416d8888702ccc) at the head. Each mutant is one single-occurrence string replacement in a temporary copy of `tools/audit/seat/cloud-setup.sh` (sha1 c634e17854e8e84e650f480eb53bad5dbc73a3e2). Each copy is run 3 times with `bash <copy> --self-test` on a `/dev/null` stdin. A mutant is KILLED only when all 3 runs fail. The tool refuses (`NO-APPLY`) a string that does not occur exactly once. It printed `RESULT survivors=0`, rc 0.

| mutant | the predicate removed | arms that go red (3 of 3 runs) |
|---|---|---|
| M0 none | – | none: `M0 none: PASS 3/3 runs 0 failed` |
| M1 | the profile's `case ":$PATH:"` presence test (the merge base's line) | the profile sourced twice puts venv-ci/bin on PATH once; under BASH_ENV a nested bash keeps a stub its caller put ahead of the venv (#2452) |
| M2 | `check`'s whole condition, set to `true` | check refuses the system python3 beside an executable HPO_TYPING_PYTHON; check refuses venv-ci's python3 without HPO_TYPING_PYTHON; check refuses without OPENBLAS_CORETYPE; check refuses without them, naming each variable; cloud-setup.sh --check exits 1 without them |
| M3 | `check`'s `-x "$HPO_TYPING_PYTHON"` half | check refuses venv-ci's python3 without HPO_TYPING_PYTHON |
| M4 | `variables`' `venv-ci/bin` prefix | a non-login bash under the printed variables gets venv-ci's python3; check is OK under the printed variables; check refuses without them, naming each variable; cloud-setup.sh --check exits 0 under the printed variables |
| M5 | `variables`' `HPO_TYPING_PYTHON` line | check is OK under the printed variables; check refuses without them, naming each variable |
| M6 | `variables`' dedupe filter | the printed PATH holds venv-ci/bin once, first, from a PATH holding it twice |
| M7 | the profile's `OPENBLAS_CORETYPE` export, set to `:` | check is OK in a shell that sourced the profile |
| M8 | `variables`' `OPENBLAS_CORETYPE` line | check is OK under the printed variables; check refuses without them, naming each variable |
| M9 | `check`'s `[ "$py" = "$1/venv-ci/bin/python3" ]` half | check refuses the system python3 beside an executable HPO_TYPING_PYTHON |
| M10 | the profile's `HPO_TYPING_PYTHON` export, set to `:` | check is OK in a shell that sourced the profile |
| M11 | `check`'s `return 1`, set to `return 0` | check refuses the system python3 beside an executable HPO_TYPING_PYTHON; check refuses venv-ci's python3 without HPO_TYPING_PYTHON; check refuses without OPENBLAS_CORETYPE; check refuses without them, naming each variable; cloud-setup.sh --check exits 1 without them |
| M12 | `--check`'s refusal exit: `check "$PREFIX" \|\| true; exit 0` | cloud-setup.sh --check exits 1 without them |
| M12b | `--check`'s OK exit: `exit 1` | cloud-setup.sh --check exits 0 under the printed variables |
| M13 | `check`'s `OPENBLAS_CORETYPE` half | check refuses without OPENBLAS_CORETYPE |

The review's literal M12 (`exit $?` replaced by `exit 0`) is an equivalent mutant at this head: under the script's `set -e`, a refusing `check` exits the script with 1 before `exit 0` runs. Measured: the copy differs from the head (`cmp -s … && echo SAME || echo DIFFERS` printed `DIFFERS`), its self-test reads `13 checks, 0 failed`, and `env -i PATH=/usr/bin:/bin bash <copy> --check </dev/null` exits 1. M12 above is the behaviour the review named, a refusal a seat would carry on past, and it is killed.

Failing test first: under M9, round 1's 8-arm self-test reads `cloud_setup self-test: 8 checks, 0 failed` (`bash <round-1 script with M9> --self-test </dev/null`). The head's self-test under M9 reads `FAIL check refuses the system python3 beside an executable HPO_TYPING_PYTHON` and `13 checks, 1 failed`. M1 *is* the merge base's profile text, and under it the #2452 arm and the idempotence arm fail.

## Unpinned sites

- The install path's `write_profile "$PROFILE" "$PREFIX"` call and its last `echo`. They run only in a real setup run (root, network, `uv`, pip). Disposition: a written triage. The self-test calls `write_profile` itself, and the profile's text is pinned by M1, M7 and M10 above. The harness writes the profile with the script's own `write_profile` text. Deleting the call would leave no profile for login shells, and nothing in a seat's own shell depends on that profile (the point of this fix).

## Null control

- The self-test's first arm is the defect itself and passes at both ends: a non-login bash with no variables set gets the system `python3`.
- M0 is the null control for the mutation table: the unmutated copy reads `0 failed` on 3 of 3 runs, so each KILLED is the mutant's.
- Harness arm `check-ok` is the null control for `check-sys`: the same `--check` with `PATH` from `--variables` answers `OK … rc=0` at the head and under M9. So `check-sys`'s `REFUSE … rc=1` at the head is the system `python3`'s doing.
- Harness arm `remedy-nul` is the null control for arm `remedy`: the same profile and `BASH_ENV` on a `/dev/null` stdin. It gets `/opt/hpo/venv-ci/bin/python3 numpy-ok` at both ends. So `remedy`'s `numpy-missing` is caused by the socket-stdin startup path, not by a broken profile.
- `--check` in this seat: `bash tools/audit/seat/cloud-setup.sh --check` prints `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`, rc 0. `env -u BASH_ENV -u OPENBLAS_CORETYPE bash tools/audit/seat/cloud-setup.sh --check` prints `REFUSE python3 is /opt/hpo/venv-ci/bin/python3, HPO_TYPING_PYTHON is /opt/hpo/venv-ha/bin/python, OPENBLAS_CORETYPE is unset; …`, rc 1. Both outcomes are reachable. `BASH_ENV` has to be unset too, because this seat's `BASH_ENV` profile re-exports `OPENBLAS_CORETYPE` in the nested `bash`.

## Figures

What this round re-took (2026-10-24, from 16:37Z, macOS seat, head 2b641269e, merge base 806aa2ce8): the three sha1s, the scoped gate, `run_always`, structure, archscore, the predictor and the class's seams. The container-only figures (the harness, the self-test runs, the mutation table, `--check` in the seat, the snapshot source) were measured in round 2's Linux cloud container at 37415bf21f4d and are not re-taken. They need `/opt/hpo` and bash 4's `mapfile`, which this seat lacks: here `bash tools/audit/seat/cloud-setup.sh --self-test </dev/null` stops at `mapfile: command not found` after its first arm. They still describe this head, because `shasum` on the three scripts prints the same sha1s as round 2's (c634e178…, b4b5ba0d…, e5d50e1f…) and the merge touched none of this PR's seven files. CI's governance step re-runs the self-test on Linux.

- The finder's control at both ends (fixer.md step 3), harness `dev/audit/harnesses/r10_cloud_setup_toolchain.py` (sha1 e5d50e1f5bdaea4c3054242bb60fd60180f1077f): `python3 -I dev/audit/harnesses/r10_cloud_setup_toolchain.py --script <cloud-setup.sh>`. This is the fixer's rebuild of the finder's control, disclosed under fixer.md step 18. The base copy is `git show 145bfe197:tools/audit/seat/cloud-setup.sh` (sha1 de09983785a7b6a15d5a164cc76e5b2eba2d705d, the same blob at round 2's merge base e97f5749b). The head is sha1 c634e17854e8e84e650f480eb53bad5dbc73a3e2.
  - base: `bare` `/usr/local/bin/python3 numpy-missing`; `remedy` `/usr/local/bin/python3 numpy-missing`; `remedy-nul` `/opt/hpo/venv-ci/bin/python3 numpy-ok`; `variables`, `check-ok` and `check-sys` `n/a`; `nested` `/opt/hpo/venv-ci/bin/python3`; `verdict: … no`.
  - head: `bare` and `remedy` unchanged (a script cannot change the agent's own environment, so they read flat; this is the step-3 case); `remedy-nul` unchanged; `variables` `/opt/hpo/venv-ci/bin/python3 numpy-ok`; `check-ok` `OK … rc=0`; `check-sys` `REFUSE python3 is /usr/local/bin/python3, … rc=1`; `nested` `<tmp>/stub/python3`; `verdict: … yes`.
  - head with M9 (sha1 9025f4008eaea46efb241c2380a639bbc8ccfdf6): as the head except `check-sys` `cloud-setup check: OK python3 is /usr/local/bin/python3 rc=0`, `verdict: … no`. Round 1's harness read M9 as `yes`.
- The self-test, 10 runs on this seat's inherited stdin and 10 on `/dev/null`: `for i in $(seq 10); do bash tools/audit/seat/cloud-setup.sh --self-test | tail -1; done | sort | uniq -c` printed `10 cloud_setup self-test: 13 checks, 0 failed` both ways. The null control is the mutation table: the same command on a mutant reads `1 failed` or more.
- The snapshot's PATH source: `grep -a` on `/opt/claude-code/bin/claude` for the snapshot builder. On non-Windows it writes `export PATH=` from `process.env.PATH`, under a `bash -c -l` that first sources `~/.bashrc < /dev/null`. Measured in round 1, unchanged by this round.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py`, `tests/harness_headers.py`). Those two and the `run_always` lines were run with `PYTHONPATH=tests/hastub`: `ALL 112 HARNESS HEADER CHECKS PASSED`, `claims hygiene: 806aa2ce89aeb6c00cf756195f31026ab798f3ca ok`, `ALL 117 closure shrink pins PASSED`, `layout self-test: ok`. `tests/entities.py` printed `4 of 2425 ENTITY CHECKS FAILED`, rc 1, the same at a clean `origin/main` (806aa2ce8) worktree. These are main's, not this PR's (see `## Red checks`).
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`
- `python3 tools/audit/archscore/score.py --diff 806aa2ce89ae HEAD`: `Architecture score: dS +0.0000 NULL`
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures or fast red predicted against 806aa2ce89ae (a data-file read is not seen)`.
- The class's seams (fixer.md step 8). Rule: `git grep -n -E 'hpo-toolchain|on PATH from the environment|BASH_ENV' -- tools .claude dev/governance dev/programme/HANDOVER.md .github ':!tools/audit/seat/cloud-setup.sh'`. Every returned seam:
  - `tools/audit/seat/INSTRUMENTS.md` (`cloud-setup.sh` entry, and the cloud-runner `BASH_ENV` trap): closed in this diff.
  - `tools/audit/seat/INSTRUMENTS.md` (`cloud_dispatch.py` entry, "comes from the environment's variables"): already true, unchanged.
  - `tools/audit/seat/cloud_dispatch.py` (the prompt's "is on PATH from the environment"): true where the environment carries the variables. Making it measured is a Forward-carry below.
  - `dev/programme/HANDOVER.md` item 52 ("run with `env -u BASH_ENV`"): still true until the setup script is re-pasted, and harmless after. Unchanged.
  - `.github/workflows/governance.yml`, `.github/workflows/tests.yml`, `dev/governance/decisions/0013-…`: `BASH_ENV` as a CI injection vector, a distinct concern. Not this class.
  - The rule excludes `dev/audit/rca/R10-N-structure-blind.md`, a record that recounts; it stays as written (fixer.md step 10).

## Red checks

None turned red by this branch. Inherited, local only: `tests/entities.py` fails 4 checks at this head and at a clean `origin/main` 806aa2ce8. The comparison is of sets, not counts. Each log's top-level `  FAIL <description>` lines, without the self-tests' `id:check  [...]` negative arms, were sorted and diffed, and `diff` printed nothing, so the sets are identical. All four are the heartbeat `hb:positive_control` retry and rest checks: "survives one hung py-spy sample", "a try whose sample misses the spin … is retried", "the control rests between tries", and "survives two hung samples, answering on try 3". They are py-spy and timing checks under this host's load, and this diff touches none of their inputs.

## Forward-carry

- `tools/audit/seat/cloud_dispatch.py`'s setup line should tell a seat to run `bash tools/audit/seat/cloud-setup.sh --check` first and stop on `REFUSE`, so that "on PATH from the environment" is measured, not asserted. `--check` now also covers `OPENBLAS_CORETYPE`, so the same line covers the golden-float pin. The file is outside this group's `files`. Carry: R10-FLOW-DESIGN-STAGES (roster 65c67fc26)

## Friction

- cloud_dispatch: stale: the payload's "the toolchain … is on PATH from the environment" holds only where the environment's variables carry it. A setup script cannot put it there (the snapshot exports the agent's PATH, and a first-level socket-stdin bash skips `BASH_ENV`), and nothing told the owner which variables to set. Carry: R10-FLOW-DESIGN-STAGES (roster 65c67fc26)
- fixer.md#2: cost: a mutant that swaps a dispatch's `exit $?` for `exit 0` is equivalent under `set -e`, so it reads like a survivor of a missing arm. The arm that pins the refusal exit has to be killed by the mutant that actually lets a refusal through (`|| true; exit 0`). Carry: R10-POLICY-FIXER-MD (roster 8ecacecb1)
