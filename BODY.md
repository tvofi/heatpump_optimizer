R10-FLY-CLOUD-SETUP-TOOLCHAIN: `tools/audit/seat/cloud-setup.sh` names the environment variables that put the toolchain on a cloud seat's PATH, gives a seat `--check` to measure them, and writes a profile that leaves a stub PATH alone. Part of #2505 (the R10-ORCH-MACHINERY re-cut, design note on `design/R10-ORCH-MACHINERY` at 2fc665c61, section 3 row G; the parent issue stays open for the rest of that group).

The defect (the roster's five carries: #2572, #2554, the R10-BRIEFS-FOLD body, #2629, #2627): the payload says "the toolchain (venv python, node, gh) is on PATH from the environment", and in a seat whose environment did not carry it, `python3` was the system interpreter. The root cause, measured in this container:

- A seat's Bash call is `/bin/bash -c "source <snapshot> && ..."`, started by the agent process. It inherits the agent's environment. The snapshot is built with `bash -c -l`, but on Linux it writes `export PATH=` from the agent's own PATH (`process.env.PATH`), not from the login shell's. So `/etc/profile.d/hpo-toolchain.sh` never reaches the seat's PATH through the snapshot.
- That shell is a first-level bash whose stdin is a socket (`/proc/self/fd/0 -> socket:[…]`). Bash then takes its remote-shell path: it reads `/etc/bash.bashrc` and `~/.bashrc` *in place of* `BASH_ENV`. The stock `~/.bashrc` starts with `[ -z "$PS1" ] && return`. The script appended its `. /etc/profile.d/hpo-toolchain.sh` hook after that return, so the hook never ran for any non-interactive shell.
- So nothing a setup script writes can put the toolchain on the seat's PATH. Only the environment's variables can (the agent's process env). In this seat they do: the agent process carries `PATH=/opt/hpo/venv-ci/bin:…` and `BASH_ENV=/etc/profile.d/hpo-toolchain.sh`, and its parent (`environment-manager`) carries neither. Those were set outside the tree. The script never named them.
- #2452's trap has the same cause: every *nested* bash reads `BASH_ENV`, and the unguarded profile prepends `venv-ci/bin` again, ahead of a test's `PATH=<stub>:$PATH`.

What changes (one module, plus its wiring):
- `cloud-setup.sh`: the header note now states the mechanism above and the variables to set. The setup run's last line prints them. `--variables` prints them, one `NAME=value` per line, with `venv-ci/bin` exactly once and first. `--check` answers `OK` when `python3` is venv-ci's and `HPO_TYPING_PYTHON` is executable; otherwise it answers `REFUSE` naming the variables (exit 0 or 1). `--self-test` covers 8 arms. The profile prepends `venv-ci/bin` only when it is absent (`case ":$PATH:"`). The dead `~/.bashrc` append is removed.
- `.github/workflows/governance.yml`: one step runs `cloud-setup.sh --self-test` beside `seat_venv.sh`'s, with the same `N checks, 0 failed` grep.
- `tools/audit/seat/INSTRUMENTS.md`: the `cloud-setup.sh` entry gets the modes and the corrected route. The cloud-runner trap line becomes "until the pasted setup script writes the idempotent profile".
- `dev/audit/harnesses/r10_cloud_setup_toolchain.py`: the finder's control as a re-runnable harness (fixer.md step 18). `tests/closures.json` records it among `harness_headers.py`'s inert reads (`ci_predict.py --apply-inert`).

Owner action, outside the tree: re-paste the script as the environment's setup script, and keep (or set) the variables `--variables` prints. `BASH_ENV` is not needed: it acts only in nested shells, and with the new profile it is harmless there.

Alternatives, and why each lost:
- Source the profile from the cloud payload (the brief's second option): every seat would spend a step on it. It also fails for any shell the seat does not start itself, and `cloud_dispatch.py` is outside this group's `files`. The variables fix it once, for every shell.
- Move the `~/.bashrc` hook above the `PS1` return: the seat's shell would read it. But the snapshot's `export PATH=` runs after it and overwrites it. A nested shell would then re-read it, which is #2452 again.
- An exported marker variable as the profile's guard (my first cut): a test harness spawned from a shell that never read the profile carries no marker, so its `PATH=<stub>:$PATH` child still had the venv prepended. Checking for presence keys on the PATH itself.
- Export `BASH_ENV` from the profile: no shell that matters reads the profile first.

## Head

eec03e0ee65ed73b8c9dc2ee113c455eda1a0e9b. Merge base 145bfe197b9e, which was `origin/main`'s tip when measured, 2026-10-24T10:20Z to 10:40Z. Three commits: the fix, the closures entry, the INSTRUMENTS wording.

## Mutation proof

Instrument: each mutant is a single-occurrence string replacement of a predicate in a scratch copy of `tools/audit/seat/cloud-setup.sh` at the head. Each copy is run 3 times with `bash <copy> --self-test`, and the FAIL lines are collected. `cmp` confirmed that no mutant is byte-identical to the head.

| mutant | the predicate removed | checks that go red (3 of 3 runs) |
|---|---|---|
| M0 none | – | none: `cloud_setup self-test: 8 checks, 0 failed`, 10 of 10 runs |
| M1 | the profile's `case ":$PATH:"` presence test (the merge base's profile line) | the profile sourced twice puts venv-ci/bin on PATH once; under BASH_ENV a nested bash keeps a stub its caller put ahead of the venv (#2452) |
| M2 | `check`'s whole condition, set to `true` | check refuses without them, naming each variable; check refuses venv-ci's python3 without HPO_TYPING_PYTHON |
| M3 | `check`'s `-x "$HPO_TYPING_PYTHON"` half | check refuses venv-ci's python3 without HPO_TYPING_PYTHON |
| M4 | `variables`' `venv-ci/bin` prefix | a non-login bash under the printed variables gets venv-ci's python3; check is OK under the printed variables; check refuses without them, naming each variable |
| M5 | `variables`' `HPO_TYPING_PYTHON` line | check is OK under the printed variables; check refuses without them, naming each variable |
| M6 | `variables`' dedupe filter | the printed PATH holds venv-ci/bin once, first, from a PATH holding it twice |

M3 survived the first 7-arm cut. The arm "check refuses venv-ci's python3 without HPO_TYPING_PYTHON" was added to kill it.

Failing test first: M1 *is* the merge base's profile text (`export PATH="$2/venv-ci/bin:\$PATH"`, unconditional). Under it the #2452 arm and the idempotence arm fail. The base has no `--variables` or `--check`, so it has no arm that could pass.

## Unpinned sites

- The install path's `write_profile "$PROFILE" "$PREFIX"` call and its last `echo`: they run only in a real setup run (root, network, `uv`, pip). Disposition: a written triage. The self-test calls `write_profile` itself. The harness writes the profile with the script's own `write_profile` text. Deleting the call would leave no profile for login shells, and nothing in a seat's own shell depends on that profile (the point of this fix).

## Null control

- The self-test's first arm is the defect itself and passes at both ends: a non-login bash with no variables set gets the system `python3`.
- Harness arm `remedy-nul` is the null control for arm `remedy`. It is the same profile and `BASH_ENV` on a `/dev/null` stdin, and it gets `/opt/hpo/venv-ci/bin/python3 numpy-ok` at both ends. So `remedy`'s `numpy-missing` is caused by the socket-stdin startup path, not by a broken profile.
- `--check` in this seat answers `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3` (rc 0), and the self-test's no-variables arm answers `REFUSE` (rc 1). Both outcomes are reachable.
- Socket-stdin control, measured in this container: `env -i HOME=/nonexistent PATH=/usr/bin:/bin BASH_ENV=<file exporting SAW_ENV=yes> bash -c 'echo $SAW_ENV $PATH'` gives `SAW_ENV=no PATH=/nonexistent/.nix-profile/bin:/nix/var/nix/profiles/default/bin:/usr/bin:/bin` on a socketpair stdin (`/etc/bash.bashrc`'s nix lines ran, `BASH_ENV` did not). On `/dev/null` it gives `SAW_ENV=yes PATH=/usr/bin:/bin`.

## Figures

- The finder's control at both ends (fixer.md step 3), harness `dev/audit/harnesses/r10_cloud_setup_toolchain.py` (sha1 b377aeaeaca0e7065cfc5c071275b57e3cf4fa94): `python3 -I dev/audit/harnesses/r10_cloud_setup_toolchain.py --script <cloud-setup.sh>`. The base copy is `git show 145bfe197:tools/audit/seat/cloud-setup.sh` (sha1 de09983785a7b6a15d5a164cc76e5b2eba2d705d). The head is sha1 40fdfa19eb13dfa4b7964ef014c118ddb2e3d3fd.
  - base: `bare` `/usr/local/bin/python3 numpy-missing`; `remedy` `/usr/local/bin/python3 numpy-missing`; `remedy-nul` `/opt/hpo/venv-ci/bin/python3 numpy-ok`; `variables` `n/a`; `nested` `/opt/hpo/venv-ci/bin/python3`; `verdict: … no`.
  - head: `bare` and `remedy` unchanged (a script cannot change the agent's own environment, so they read flat; this is the step-3 case); `remedy-nul` unchanged; `variables` `/opt/hpo/venv-ci/bin/python3 numpy-ok`; `nested` `<tmp>/stub/python3`; `verdict: … yes`.
- The self-test, 20 runs on this seat's socket stdin and 10 each on `/dev/null` and a pipe: `for i in $(seq N); do bash tools/audit/seat/cloud-setup.sh --self-test | tail -1; done | sort | uniq -c`, all `0 failed`. Disclosed self-correction: the first cut's self-test did not redirect its children's stdin. Under the inherited socket, `env -i` (no `SHLVL`) made each child a first-level remote-shell bash that skipped `BASH_ENV`, and some runs read 3 failures. Every child now runs on `/dev/null`. That intermittency is how the socket-stdin mechanism was found.
- The snapshot's PATH source: `grep -a` on `/opt/claude-code/bin/claude` for the snapshot builder (`Jvr`). On non-Windows it writes `export PATH=` from `process.env.PATH`, under a `bash -c -l` that first sources `~/.bashrc < /dev/null`.
- The agent's environment against its parent's: `tr '\0' '\n' </proc/<pid>/environ | grep -E '^(BASH_ENV|PATH)='` for the agent (PATH with `/opt/hpo/venv-ci/bin` first, `BASH_ENV` set) and for `environment-manager` (PATH without the venv, no `BASH_ENV`).
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out.` (`tests/entities.py`, `tests/harness_headers.py`). Those two and the `run_always` lines (`tests/env_drift.py --claims-only <merge base>`, `tests/closure.py selftest`, `tests/layout.py`, `tests/harness_headers.py`) were run with `PYTHONPATH=tests/hastub` under `env -u BASH_ENV`, each rc 0: `ALL 2425 ENTITY CHECKS PASSED`, `ALL 112 HARNESS HEADER CHECKS PASSED`, `claims hygiene: 145bfe197b9e7c09eb90bedadec44c6bc19d679d ok`, `ALL 117 closure shrink pins PASSED`, `layout self-test: ok`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 145bfe197 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: one predicted `tests / closures` red (the harness's INERT READS entry) before `--apply-inert`, then `CI PREDICT: no closures or fast red predicted against 145bfe197b9e`.
- The class's seams (fixer.md step 8). Rule: `git grep -n -E 'hpo-toolchain|on PATH from the environment|BASH_ENV' -- tools .claude dev/governance dev/programme/HANDOVER.md .github ':!tools/audit/seat/cloud-setup.sh'`. Every returned seam:
  - `tools/audit/seat/INSTRUMENTS.md` (`cloud-setup.sh` entry, and the cloud-runner `BASH_ENV` trap): closed in this diff.
  - `tools/audit/seat/INSTRUMENTS.md` (`cloud_dispatch.py` entry, "comes from the environment's variables"): already true, unchanged.
  - `tools/audit/seat/cloud_dispatch.py` (the prompt's "is on PATH from the environment"): true where the environment carries the variables. Making it measured is a Forward-carry below.
  - `dev/programme/HANDOVER.md` item 52 ("run with `env -u BASH_ENV`"): still true until the setup script is re-pasted, and harmless after. Unchanged.
  - `.github/workflows/governance.yml`, `.github/workflows/tests.yml`, `dev/governance/decisions/0013-…`: `BASH_ENV` as a CI injection vector, a distinct concern. Not this class.
  - The rule excludes `dev/audit/rca/R10-N-structure-blind.md`, a record that recounts; it stays as written (fixer.md step 10).

## Red checks

none

## Forward-carry

- `tools/audit/seat/cloud_dispatch.py`'s setup line should tell a seat to run `bash tools/audit/seat/cloud-setup.sh --check` first and stop on `REFUSE`, so that "on PATH from the environment" is measured, not asserted. The file is outside this group's `files`. Carry: R10-ORCH-MACHINERY

## Friction

- cloud_dispatch: stale: the payload's "the toolchain … is on PATH from the environment" holds only where the environment's variables carry it; a setup script cannot (the snapshot exports the agent's PATH, and a first-level socket-stdin bash skips `BASH_ENV`), and nothing told the owner which variables to set. Carry: R10-ORCH-MACHINERY
- fixer.md#3: cost: a shell self-test run from a seat's Bash call inherits a socket stdin, and a child started under `env -i` is then a first-level remote-shell bash that ignores `BASH_ENV`, so a test of `BASH_ENV` read intermittently red until every child ran on `/dev/null`. Carry: R10-ORCH-MACHINERY
