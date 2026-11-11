P453: `worktree_gc.sh` collected live train/relay checkouts because it kept a worktree only when a process's cwd was inside it (five instances on 11-08). Every removal arm (all go through `cwd_free`) now also keeps a worktree named in a live process's argv (`git -C`, `--checkout`, script path; `ps -eo args=`), with an open file (`lsof`), or holding a live `train.pid`/`*.lock` pid; an unreadable `ps` keeps it as `cwd-unread`. `--keep-dir` is documented in the header and usage line as the evidence destination, not a keep list; no real protect flag was added (none is needed once live users are detected). Alternative rejected: `lsof +D` per worktree, which walks the tree and is slow on a Pi; one `lsof -Fn` listing is matched instead.

Carry 1 (the brief's Carry 0, GC-LIVE-TRAIN-CHECKOUT) is built in this PR: failing test first (a worktree used only through \`git -C\`, cwd elsewhere, survives every arm), null control (same worktree, no live user, is collected), \`--keep-dir\` usage line corrected.

## Head

5276f31b5ac10b11e395522ae252192ff968c213 (base origin/main 32aea942e19d36433713292ae02508e46753e932, 2026-11-11T00:35Z)

## Mutation proof

Predicate mutants in `cwd_inside`: the `argv-inside`, `open-file` and `pidfile-live` returns replaced by `true`. `tools/audit/worktree_gc.sh --self-test` then fails 6 checks: "argv names the worktree (git -C), cwd elsewhere: kept", "naming argv-inside", "an open file inside, cwd elsewhere: kept", "naming open-file", "a live train.pid inside: kept", "naming pidfile-live". Restored: 140 checks, 0 failed.

## Null control

Same on-remote detached worktree (`seat-deadpid`) with a dead-pid `train.pid` and no live argv or open file: collected (self-test check "null control: the same worktree with a dead-pid train.pid and no live user is collected"). `seat-argvuse` has cwd elsewhere and only a `git -C <wt>` argv; it is kept, and removed at the mutant above. Unreadable `ps` case (`nops`) keeps the worktree.

## Figures

- `bash tools/audit/worktree_gc.sh --self-test` : last line "140 checks, 0 failed" at the head above.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` : mode line `MODE: SCOPED`, `scope.run` empty (worktree_gc.sh is in no measured closure); `run_always` lines, `tests/structure.py` passed.
- Seam enumeration (step 8): `grep -n 'cwd_free' tools/audit/worktree_gc.sh` lists every removal arm's keep check; all call `cwd_free`, so all gain the new arms (closed in this diff). No `+D` form is used.

## Red checks

none

## Forward-carry

none

## Friction

none
