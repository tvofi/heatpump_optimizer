Part 2 of R10-SUITE-ENV-RESIDUE, body item ec93383a (and its duplicate): `tests/throwaway_git.py` and its shell twin `tests/throwaway_git.sh` set `GIT_CONFIG_GLOBAL` to `/dev/null`, which makes git die with `bad config line 1 in file /dev/null` (`git init` exit 128) wherever `/dev/null` holds bytes. Both now point at an emptied per-process `mktemp` file (the python side removes it at exit). The first cut used a fixed per-uid temp path and `tmp_paths.py --check` refused it (`tmpdir-fixed`), so it was replaced.

## Head

7d55d16d97926797c5cdaf33eea2b6a981ee75b2, measured on a worktree cut from 8c10361eb1fea539dc5acb8f7442eac2810faa47. Reproduction: not reproduced in this cloud container. `/dev/null` here is the normal empty char device (`ls -l /dev/null`: `crw-rw-rw- 1 root root 1, 3`), and `GIT_CONFIG_GLOBAL=/dev/null git init` exits 0, as did `tests/entities.py`'s throwaway-git section and `stop-selfcheck.sh --self-test` (29 passed) at the base. The failure mechanism is reproduced instead with a non-empty file as the global config (see Null control).

## Mutation proof

Mutant: `empty_global_config()` stops truncating (`open(path, "a").close()`) on a first-cut variant; `python3 tests/throwaway_git.py --self-test` went red on: "a non-empty file at the old global-config path fails git init (null control); the env's path still inits, and again after the file was dirtied", "git reads auto-maintenance off, and gc.auto 0, through the env", "null control: an inherited -c maintenance.auto=true outranks both layers...", "the env survives the same hostile parameters, once rebuilt from them". Restored; 45 checks, 0 failed. The truncation line is retained in the final mktemp form.

## Null control

A non-empty file (`not a config line`) as `GIT_CONFIG_GLOBAL` makes `git init` exit 128 (the self-test's `old` arm, asserted nonzero); the env's path inits with exit 0 and still inits after the file was dirtied (re-emptied on each call). The twin comparison now also asserts both sides name an empty regular file, since the two paths differ per process.

## Figures

- `python3 tests/throwaway_git.py --self-test`: 45 checks, 0 failed.
- `python3 tests/throwaway_git.py --check`: 0 refused.
- `bash .claude/hooks/stop-selfcheck.sh --self-test`: 29 passed, 0 failed.
- `python3 tools/audit/seat/tmp_paths.py --check`: 0 refused at HEAD.
- `env -u BASH_ENV PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh`: exit 0. PREPR_SKIP_CLOSURES=1 was used because the closure recording of tests/entities.py ran under strace for over 17 minutes without finishing (the brief's cloud trap); `tests/entities.py` run directly passed its throwaway-git section with no CalledProcessError (it exceeded a 220 s cut for time, not for failure).

## Red checks

none

## Forward-carry

none

## Friction

- gate-scoping: cost: `prepr.sh`'s closure recording of `tests/entities.py` under strace did not finish in 17+ min in the cloud image. Carry: dismissed: a slow strace recording of one script in this image is one occurrence, not a recurring class (defect-root-cause.md); recorded here only
