Part 2 of R10-SUITE-ENV-RESIDUE, body item ec93383a (and its duplicate): `tests/throwaway_git.py` and its shell twin `tests/throwaway_git.sh` set `GIT_CONFIG_GLOBAL` to `/dev/null`. Wherever `/dev/null` holds bytes, git then dies with `bad config line 1 in file /dev/null` (`git init` exit 128).

Repair of the handoff blocked at 7d55d16d97 (`residue-leak`, verdict on probe/revt-r10-suite-env-residue-p2-300c4cd9). That head had two problems: the shell twin left one `mktemp` file behind for each process that sourced it, and it truncated any file named by an inherited `_HPO_EMPTY_GITCONFIG`. Both sides now set `GIT_CONFIG_GLOBAL` to a path whose parent is the helper's own regular file: `tests/throwaway_git.py/no-global-config` (`NO_GLOBAL_CONFIG`) and `tests/throwaway_git.sh/no-global-config`. The shell side resolves its path to an absolute one when the file is sourced. Opening that path fails with ENOTDIR, and git reads ENOTDIR as "no global config file" (`access_error_is_ok`). No process can create a file at that path. No temp file, trap or atexit hook exists any more, and nothing is read from or written to a path taken from the environment.

Alternatives considered:
- (a) The dispatch's design: one mkstemp config per run in a directory the run owns, with ownership verified and the file removed on exit. Not taken. The twin runs in each subshell (`throwaway_git_init` calls it after a `cd`), so it would need an EXIT trap in every subshell that sources it. That trap would compete with the callers' own traps, and a SIGKILL still leaves the file (the review measured one file for python).
- (b) A tracked empty file classified INERT, the reviewer's second cut. Not taken. It adds a third file and a `closure.py` entry, and any writer in the checkout could fill the file.
- The ENOTDIR path has none of these costs.

The reviewer's M4 and M5 sites (`: >"$g"` and the `atexit` unlink) no longer exist. The new checks still kill both mutants when applied to 7d55d16d97 (see Mutation proof).

Carry dispositions (roster state read, unchanged from 7d55d16d97): Carry 0 dismissed on the roster (superseded by its own rule); Carry 1 implemented; Carry 2 implemented; Carry 3 implemented; Carry 4 dismissed on the roster (premise gone). Carry 5 and Carry 6 are built in this pull request.

## Head

c3fa2b58fda798284ee4ae335989bb3cb5ab9616, measured on a worktree of handoff/r10-suite-env-residue-p2@7d55d16d97 (merge base 8c10361eb1fea539dc5acb8f7442eac2810faa47). origin/main was at 43e95474559ca8e2188830f8775c1ddf52df964a when measured, and `git merge-tree --write-tree origin/main HEAD` exits 0, so this head was not merged with main.

Reproduction, run as root under `unshare -m` with a file holding `junk line` bind-mounted over `/dev/null` and run from both worktrees (the reviewer's ev/repro_bindmount.sh, re-pointed):
- At the base 8c10361eb1: py exit 128 `fatal: bad config line 1 in file /dev/null`, and sh exit 128.
- At this head: py exit 0 and sh exit 0, with 0 regular files left in the fresh TMPDIR.

## Mutation proof

The four new checks are run with `python3 tests/throwaway_git.py --self-test`. At 7d55d16d97 plus the new tests, 3 checks fail and the self-test reports 49 checks, 3 failed:
- "each side's GIT_CONFIG_GLOBAL is a path under its own regular file ...": at that head it is a temp path, and the sh side reads the inherited core.keep.
- "a file named by an inherited _HPO_EMPTY_GITCONFIG or GIT_CONFIG_GLOBAL is never written": the file is truncated to ''.
- "a python and a shell process that built the env leave nothing in TMPDIR": `['hpo-empty-gitconfig-gUbFvE']` is left behind.

The reviewer's mutants, applied to 7d55d16d97 plus the new tests:
- M4, the shell truncation `: >"$g"` replaced by `:`, is killed (2 failed). The sh side now reads the inherited `core.keep = 1`, and the shell residue remains.
- M5, the python `atexit` unlink dropped, is killed (3 failed). The residue check lists two `hpo-empty-gitconfig-*` files, one of them python's.

Mutants of this head, each restored afterwards:
- N1, py `GIT_CONFIG_GLOBAL=os.devnull`: killed (1 failed).
- N2, sh `GIT_CONFIG_GLOBAL=/dev/null`: killed (1 failed).
- N3, sh source path left unresolved (`"${BASH_SOURCE[0]}/no-global-config"`): killed (1 failed). It first survived, so the probe now sources the twin by a relative path and then runs `cd`, as `.claude/hooks/pre-bash.sh` does.
- N4, py `GIT_CONFIG_GLOBAL` not set: killed (2 failed). Twin parity fails and the host's `core.leak` is read.
- N5, sh reuses an inherited `GIT_CONFIG_GLOBAL`: killed (1 failed).
- N6, py path under the `tests/` directory rather than under the file: killed (2 failed). The create probe succeeds and the parent check fails. This mutant's probe left `tests/no-global-config` in the worktree. The file was removed, and the probe now unlinks anything it creates.

`prepr.sh`'s `MUTANT_CMD` draws only from added `.py` lines outside `tests/`, so it draws no mutants from this diff.

## Null control

All three are in the self-test and asserted alongside the arms:
- A non-empty file (`not a config line`) set as `GIT_CONFIG_GLOBAL` makes `git init` exit non-zero, while the env's path inits.
- Without the env, git reads the host's `~/.gitconfig` (`core.leak = home`), XDG config (`core.xleak = xdg`) and the inherited `GIT_CONFIG_GLOBAL` file (`core.keep = 1`). Under each side's env, all three read empty.
- `open(NO_GLOBAL_CONFIG, "w")` raises `NotADirectoryError`. Under N6 the same open succeeds and the check goes red.

Residue across processes was measured with a fresh TMPDIR per head. Each head ran `python3 tests/throwaway_git.py --self-test`, `--check`, `bash .claude/hooks/stop-selfcheck.sh --self-test` and `python3 tools/audit/seat/tmp_paths.py --check`, then `find $T -maxdepth 1 -type f | wc -l` was taken. 7d55d16d97 left 3 files and c3fa2b58fd left 0.

- Review follow-up: neither self-test drives git under a `/dev/null` that holds bytes. The check above stands in for it: a junk file as the global config fails, and the env's path inits. A bind-mount arm needs root and `unshare -m`. It ran here as the Head reproduction, and the self-test does not run it because most seats are not root. Carry: dismissed: the property is pinned seat-independently by the junk-file null control and the ENOTDIR path; the bind mount only re-proves that git reads `/dev/null` as a file

## Figures

All figures were taken at c3fa2b58fd.
- `python3 tests/throwaway_git.py --self-test`: 49 checks, 0 failed.
- `python3 tests/throwaway_git.py --check`: 0 refused, 0 stale allow entries.
- `bash .claude/hooks/stop-selfcheck.sh --self-test`: 29 passed, 0 failed.
- `python3 tools/audit/seat/tmp_paths.py --check`: 0 refused.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tests/closure.py select --diff 8c10361eb1fe`: `MODE: SCOPED -- 4 script(s) run, 29 scoped out` (arch_score, doc_claims, entities, layout). The scripts run with `PYTHONPATH=tests/hastub`:
  - layout: exit 0.
  - doc_claims: exit 0, all checks passed.
  - entities (`env -u BASH_ENV`): exit 0, ALL 2709 ENTITY CHECKS PASSED.
  - arch_score: exit 0, ALL 280 ARCHITECTURE SCORE CHECKS PASSED.
- `env -u BASH_ENV bash tools/pr/prepr.sh` (no skips, closures included): `PRE-PR: c3fa2b58fda798284ee4ae335989bb3cb5ab9616 ... rc=0`. Every step reported ok or skip, and the claim files are byte-identical to origin/main.

## Red checks

none

## Forward-carry

none

## Friction

none
