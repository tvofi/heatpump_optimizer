P453: `worktree_gc.sh` collected live train/relay checkouts because it kept a worktree only when a process's cwd was inside it (five instances on 11-08). Every removal arm (all go through `cwd_free`) now also keeps a worktree named in a live process's argv (`git -C`, `--checkout=`, script path; `ps -eo args=`), with an open file (`lsof -Fn`), or holding a live `train.pid`/`*.lock`/`.*.lock` pid; an unreadable or absent `lsof`/`ps` keeps it as `cwd-unread`. `--keep-dir` is documented as the evidence destination, not a keep list; no protect flag was added. Alternative rejected: `lsof +D` per worktree, which walks the tree.

Carry 1 (the brief's Carry 0, GC-LIVE-TRAIN-CHECKOUT) is built in this PR.

Round 2 repair of the blocked verdict at 032e758e: the four surviving mutants are pinned (below), the redundant `command -v ps` line is deleted, and the per-candidate cost is measured rather than claimed.

## Head

df7b7ac6b33e14fe959ee32eb77d83a59dd02d52 (base origin/main d08ed31049, 2026-11-11)

## Mutation proof

Each mutant applied alone to `tools/audit/worktree_gc.sh`, then `bash tools/audit/worktree_gc.sh --self-test`, then restored (restored: 154 checks, 0 failed):

- `lockglob` (`"$p"/*.lock "$p"/.*.lock` dropped): 4 failed, the `x.lock` and `.x.lock` kept/`pidfile-live` checks.
- `argvterm` (terminator set reduced to `t==""`): 2 failed, "argv names a script inside the worktree (terminator /)" and its naming check.
- `lsofall` (`out=$(lsof -Fn ...) || out=""`): 2 failed, the `noopen` case (a stub failing only the non-`-d cwd` call), kept as `cwd-unread`.
- `psunread` (`ps ... || out=""`): 3 failed, the `nops` stub case and the `nopsbin` case (no `ps` on PATH).
- Earlier verdict mutants `argv`, `open`, `pid`, `killcheck`, `heldway` are unchanged by this repair.

## Null control

- `seat-deadpid`: dead-pid `train.pid`, no live user: collected.
- `seat-argvsib`: argv names `<worktree>2` (terminator `2`, not in the set): collected. This pins the reason the terminator set exists; it moves only under a widening mutant, not under `argvterm`.
- `binnops` PATH really has no `ps` (`command -v ps` rc 1, a self-test check).

## Unpinned sites

- `command -v ps >/dev/null 2>&1 || return 2` (the verdict's `nopsbin`): the mutant `:` survived 154/0 because an absent `ps` already fails `out=$(ps ...) || return 2` (rc 127). The line was redundant, so it is deleted rather than pinned; the `|| return 2` arm it duplicated is now pinned by `nopsbin` (no `ps` on PATH) and `nops`.
- `lockglob`, `argvterm`, `lsofall`: pinned by in-tree self-test fixtures (the in-tree mutant harness for a `tools/` site is `--self-test` itself), mutants above.
- `command -v lsof ... || return 2` predates this PR and is covered by `nolsof`.

## Figures

- `bash tools/audit/worktree_gc.sh --self-test` : last line "154 checks, 0 failed" at the head above.
- Cost per candidate (step 8 figure; instrument `time lsof -Fn` and `time ps -eo args=` on this container, which has 4708 `lsof -Fn` lines): `lsof -Fn` 0.011 s real, `ps -eo args=` 0.068 s real. `cwd_inside` runs one `lsof -d cwd`, one `ps` and one `lsof -Fn` per candidate worktree, not once per sweep. Reading them once per sweep was rejected: a process starting between candidates would be missed, and the sweep is the case where a seat starts late. The sweep cost is that figure times the candidate count; no Pi re-measurement was made (none in this environment).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` : mode line `MODE: SCOPED`, 0 scripts run (worktree_gc.sh is in no measured closure).
- Seam enumeration (step 8): `grep -n 'cwd_free' tools/audit/worktree_gc.sh` lists every removal arm's keep check; all call `cwd_free`, so all gain the new arms (closed in this diff).

## Red checks

none

## Forward-carry

none

## Friction

none
