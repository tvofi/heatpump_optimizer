This is the root-cause seat for R10-RCA-CLOUD-ENTITIES-ENV, run beside the work and never inside it (`dev/governance/roles/root-cause.md`). The analysis is `dev/audit/rca/R10-RCA-CLOUD-ENTITIES-ENV.md`, registered in `dev/audit/config/bugclasses.json` `_rca`.

**Defect.** On 2026-11-08 four cloud fixer handoffs stopped at `tools/pr/prepr.sh` step 6b with `failed while being recorded: tests/entities.py (exit 1)`. The diffs were not involved. Three checks failed, identically at main: coverage job reuse, the release ZIP, and the Pages probe.

**Cause.** The cloud environment's `BASH_ENV` sources `cloud-setup.sh`'s profile ahead of every nested bash, `--noprofile --norc` included. Since #3222 that profile has exported `RUNNER_TEMP` unconditionally, to a prefix directory that nothing creates. Each of the three harnesses hands its child bash its own `RUNNER_TEMP` and reads the result back from it. Under the profile the child wrote elsewhere, or failed to write at all.

**Reproduction.** The base profile as `BASH_ENV` gives `probe on workflow: rc=1 enabled=[]` and a ZIP build at rc 128. These match the seat's `BLOCKED.md`. The second shape (`ModuleNotFoundError: homeassistant`, then `paho`) was a diagnostic re-run without `PYTHONPATH=tests/hastub`.

**Process state.** (d), with an existing barrier whose unit was too narrow. The #2452 arm covered `PATH` only, and the #2835 `_stub_path_env` covered only the `PATH` stand-in helpers. The second shape is (c).

**Countermeasure.** `write_profile` now sets every variable except `PATH` with `${NAME:-default}`. A new `--self-test` arm takes every name the profile exports and requires each to keep a caller's value under `BASH_ENV`. This is the class barrier: the class has three or more instances in round 10. Not built: a prepr replay at the merge base, refused because it costs 868 s per failed recording and would have passed all four broken environments. Owner action: remove `BASH_ENV` from the environment's variables, and re-paste the setup script after merge (RCA section 7).

The two instrument docs are corrected: `cloud_dispatch.py.md` no longer lists `BASH_ENV` as a toolchain variable, and its `env -u BASH_ENV` workaround is conditional on the new profile. No policy, budget, claim file, `VERSION`, manifest or `RELEASE_NOTES.md` is touched. The new file is under `dev/audit/`, an INERT prefix.

## Head

`4612662f84b3799106f796a215a359b8e946b349`, one commit on origin/main `4a9d2d5425ea13e728dca20aff15d7f76345dc73`.

## Mutation proof

The base `write_profile` is the mutant. The new arm was extracted verbatim and run against it and against the head's (macOS bash 3.2 has no `mapfile`, so the full `--self-test` runs in governance's cloud-setup step).

- On the base profile: `FAIL under BASH_ENV a nested bash keeps every variable its caller set`, with all seven names overwritten (`GIT_AUTHOR_*`, `GIT_COMMITTER_*`, `HPO_TYPING_PYTHON`, `OPENBLAS_CORETYPE`, `RUNNER_TEMP`).
- At head: `ok`.

## Null control

The arm has two controls:

- `control: a nested bash under BASH_ENV runs the profile` reads the profile's own `RUNNER_TEMP`, so the main arm cannot pass because the profile did not load.
- `the profile exports seven names besides PATH` is the never-empty guard.

Without `BASH_ENV` the Pages probe and ZIP harnesses are clean at base. Under the head profile they are clean too (RCA section 2 table).

## Figures

- 4 h 20 min blocked (`r10-dispatch-at-handoff-p2`, 07:31:36Z to 11:51:56Z): `git log --format='%h %ad %s' --date=iso -3 handoff-wip/r10-dispatch-at-handoff-p2`.
- At least 39 min blocked (`r10-fly-no-self-carry`, since 11:56:07Z, read at 12:35Z): `git log -1 --format=%ad --date=iso handoff-wip/r10-fly-no-self-carry`.
- 868 s for `tests/entities.py`: its `seconds` in `tests/closures.json`.
- The arm takes 0.24 s to 0.39 s, from three runs of `/usr/bin/time -p`.

## Red checks

none

## Forward-carry

none

## Friction

none
