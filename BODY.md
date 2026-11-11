P453: `worktree_gc.sh` collected live train/relay checkouts because it kept a worktree only when a process's cwd was inside it (five instances on 11-08). Every removal arm (all go through `cwd_free`) now also keeps a worktree named in a live process's argv (`git -C`, `--checkout=`, script path; `ps -eo args=`), with an open file (`lsof -Fn`), or holding a live `train.pid`/`*.lock`/`.*.lock` pid; an unreadable `lsof` or `ps` keeps it as `cwd-unread`. `--keep-dir` is documented as the evidence destination, not a keep list; no protect flag was added. Alternative rejected: `lsof +D` per worktree, which walks the tree.

Carry 1 (the brief's Carry 0, GC-LIVE-TRAIN-CHECKOUT) is built in this PR.

## Re-cut

Fourth verdict (blocked at c9aed94c: `flaky-harness`), so this is a re-cut and not a narrow repair. It is a new commit series on the PR branch: c9aed94c, then a merge of origin/main a7628041, then one commit (76b902b9) that rebuilds the self-test from main's file to the smallest set its pins need. The production hunks (`cwd_inside`, `cwd_free`, the header and the usage line) are byte-identical to c9aed94c, which the reviewer called sound as code.

Kept: every fixture that a named mutant needs, listed under `## Mutation proof`: `argvuse`, `argvscr`, `argvdq`, `argvsq`, `argvcol`, `argvcom`, the `argvsib` null control, `openuse`, `openeq`, the `opensib` null control, `pidzero`, `lockuse`, `dotlock`, the `deadpid` null control, `nops` and `noopen`, plus the `ps` stub and the `lsof` cwd/open split.

Dropped, each because a kept fixture already kills every mutant it was there for:
- `argvco` (`--checkout=<wt>`, terminator `""`): `argvuse` (`git -C <wt> log`) ends on the same empty terminator. `v2-argvterm-empty`, `v3-argvterm-empty` and `v1-argvterm` are KILLED without it.
- `pidfuse` (a live `$$` in `train.pid`): `pidzero` puts a live pid in `train.pid` too. `v1-pid`, `v1-killcheck` and the new `recut-trainpid` (drops `"$p/train.pid"` from the loop) are KILLED without it.
- `nopsbin`, its `binnops` PATH farm, and the `PATH="$W/binnops"` line in `run()`: their mutant was written against a `command -v ps || return 2` line that no longer exists, because an absent `ps` exits 127 into the same `out=$(ps -eo args= ...) || return 2` arm. The replacement mutants `v1-nopsbin-replacement` and `v2-nopsbin` (that arm's `|| return 2` dropped) and `v1-psunread`/`v3-psunread` (`|| true`) are KILLED by `nops` alone.

### The root repair: the zero-pid helper sends no signal

Before: `while :; do sleep 600 & ZPID=$!; case $ZPID in *0*) break ;; esac; kill "$ZPID" 2>/dev/null; done`. A `kill` that lands between fork and exec hits a bash child that still has the self-test's EXIT trap handler, which runs `rm -rf "$W"`.

After: `while :; do sh -c 'case $$ in *0*) exec sleep 600 ;; esac' & ZPID=$!; case $ZPID in *0*) break ;; esac; wait "$ZPID"; done`.

Why this cannot reach `rm -rf "$W"`:
- The trap's `rm` runs in only two places: the parent's own exit, or a forked copy of the shell that dies by a signal while the inherited handler is still installed.
- The loop now sends no signal at all. A child whose pid has no 0 runs `sh`, falls through the `case` and exits normally; the loop then reaps it with `wait`. The child whose pid has a 0 `exec`s `sleep` under the same pid.
- The only `kill` left is the trap's own `kill "$ZPID"`, which runs in the parent at exit, beside that same `rm`.

Alternatives not taken:
- `( trap - EXIT; exec sleep 600 ) &` keeps the kill-in-the-fork-window. A signal that arrives before `trap -` runs still finds the inherited handler, so it narrows the race and does not remove it.
- Guarding the trap with `[ "$BASHPID" = "$$" ] || exit` works, but it keeps a loop that signals half-started children and leaves the self-test's correctness resting on that guard. Removing the signal removes the cause.
- Restricting the kill to processes that have exec'd needs a `/proc` read or a sleep before each kill: more code, and a retry-shaped wait.

## Head

76b902b9f78e2deb15c51845bd6a9e619645ee70 (base origin/main a7628041dc, `date -u` Wed Nov 11 06:56:04 UTC 2026; `git merge-base --is-ancestor origin/main HEAD` true at that time)

## Mutation proof

Instrument: `python3 tools/audit/seat/mutant_run.py --spec spec.json --cmd 'bash tools/audit/worktree_gc.sh --self-test'` at the head above, with the default git-archive copy and the unmodified self-test (no de-flaking wrapper). The spec is 43 mutants:
- `v3-*`: built by running the reviewer's own `ev/mkspec.py` from probe/rev-3423-33f72110, unchanged, on this head's file.
- `v2-*`: the `M` table of `ev/mutants.py` from probe/rev-3423-23bb0265, verbatim.
- `v1-*`: the verdict from probe/rev-3423-468a0851, which named its mutants in prose only, so they are rebuilt from its descriptions. `argv`, `open` and `pid` each delete that whole arm of `cwd_inside`. `psunread` is ps `|| return 2` -> `|| true`. `killcheck` is `kill -0 "$pid"` -> `true`. `heldway` prints a fixed `cwd-inside` in place of `$HELD_WAY`. `lockglob` keeps `train.pid` only. `argvterm` cuts the terminator set to `t==""`. `lsofall` is `|| return 2` -> `|| out=""`. `nopsbin-replacement` is described under `## Re-cut`.
- `recut-*`: this re-cut's own, covered below.

Output, quoted verbatim (`ev/mutants.txt`, rc=0):

```
SURVIVED NULL
KILLED v3-argvterm-quote
KILLED v3-argvterm-colon
KILLED v3-argvterm-dq
KILLED v3-argvterm-sq
KILLED v3-argvterm-col
KILLED v3-argvterm-com
KILLED v3-argvterm-slash
KILLED v3-argvterm-empty
KILLED v3-argvterm-any
KILLED v3-openfile-eq
KILLED v3-openfile-sib
KILLED v3-pidzero-tr
SURVIVED v3-pidguard-restored
SURVIVED v3-pidempty-unquoted
KILLED v3-lockglob-star
KILLED v3-lockglob-dot
KILLED v3-lsofall
KILLED v3-psunread
SURVIVED v3-lsofcwd-empty
SURVIVED v3-trap-zpid-unguarded
KILLED v2-lockglob
KILLED v2-lockglob-star
KILLED v2-lockglob-dot
KILLED v2-argvterm-slash
KILLED v2-argvterm-empty
KILLED v2-argvterm-any
KILLED v2-argvterm-quote
KILLED v2-argvterm-colon
KILLED v2-lsofall
KILLED v2-nopsbin
SURVIVED v2-lsofcwd-empty
KILLED v1-argv
KILLED v1-open
KILLED v1-pid
KILLED v1-psunread
KILLED v1-killcheck
KILLED v1-heldway
KILLED v1-lockglob
KILLED v1-argvterm
KILLED v1-lsofall
KILLED v1-nopsbin-replacement
KILLED recut-trainpid
KILLED recut-openfile-slash
```

38 KILLED and 6 SURVIVED (NULL among them). Every survivor is one the round-4 verdict also read as SURVIVED and accepted:
- `pidguard-restored` and `pidempty-unquoted` are equivalent, because `kill -0 ""` fails.
- `lsofcwd-empty` (both spellings) is a pre-existing line on main.
- `trap-zpid-unguarded` is cleanup only.

All four are dispositioned under `## Unpinned sites`.

The re-cut dropped no production line any mutant was written against. The dropped fixture lines are covered by the replacement mutants under `## Re-cut`. The re-cut adds two mutants for disjuncts whose only pin used to be shared with a dropped fixture:
- `recut-trainpid`: `train.pid` dropped from the pidfile loop; KILLED by `pidzero`.
- `recut-openfile-slash`: `|| index(d, p "/")==1` dropped from the open-file awk; KILLED by `openuse`, which is why `openuse` stays beside `openeq`.

Argv terminator set, each member kept and pinned by its own fixture and its own KILLED mutant:

| member | fixture | mutant |
|---|---|---|
| `""` | `argvuse` | `v3-argvterm-empty` |
| `/` | `argvscr` | `v3-argvterm-slash` |
| `"` | `argvdq` | `v3-argvterm-dq` |
| `'` | `argvsq` | `v3-argvterm-sq` |
| `:` | `argvcol` | `v3-argvterm-col` |
| `,` | `argvcom` | `v3-argvterm-com` |

The upper bound is pinned by `v3-argvterm-any`, killed by the `argvsib` null control.

## Null control

- `SURVIVED NULL`: the unedited tree passes under the same command.
- `argvsib` (`<worktree>2` in argv) is collected, and it moves under `v3-argvterm-any`/`v2-argvterm-any`.
- `opensib` (an open file under `<worktree>2/f`) is collected, and it moves under `v3-openfile-sib`.
- `deadpid` (a dead-pid `train.pid`, no live user) is collected, and it moves under `v1-killcheck`.
- Flake control: at c9aed94c (before the repair) the same 25-run loop gave 13 of 25 green (below), so a loop at the new head would have shown the race had it survived.
- Minimal repro, before and after (line 119's trap plus the loop line, nothing else; the two scripts differ only in the loop line):
  - old loop: `runs=30 multi-iteration=21 fixture-NO=21 trap-runs>0=21`
  - new loop: `runs=30 multi-iteration=21 fixture-NO=0 trap-runs>0=0`, with `zpid-comm=sleep` on every line (the helper exec'd and is live).

## Unpinned sites

- Every member of the argv terminator set, the open-file equality and `/`-prefix arms, the zero-digit pid read, the `train.pid`/`*.lock`/`.*.lock` globs, and the `lsof -Fn` and `ps` `|| return 2` arms are pinned by in-tree self-test fixtures, with the mutants above. A `tools/` site has no `mutation-autofix` lane; `--self-test` is the in-tree harness.
- `[ -n "$out" ] || return 2` (an empty cwd listing counts as unreadable) and `command -v lsof ... || return 2` in `cwd_inside` are pre-existing main lines that this PR neither adds nor changes. Carry: dismissed: pre-existing lines on main, out of this PR's mutation scope (the review's residual)
- `[ -n "${ZPID:-}" ] && kill "$ZPID"` in the self-test EXIT trap is cleanup that stops the helper `sleep` outliving the self-test; it pins no behaviour, so `trap-zpid-unguarded` survives. Carry: dismissed: self-test cleanup with no observable outcome inside the run
- The removed `[ -n "$pid" ] &&` guard is equivalent (`v3-pidguard-restored` and `v3-pidempty-unquoted` SURVIVED, because `kill -0 ""` fails), so it stays deleted rather than triaged.

## Figures

- Flake control, run with `for i in $(seq 1 25); do bash tools/audit/worktree_gc.sh --self-test 2>/dev/null | tail -1; done`, counting lines that end `, 0 failed`. Both runs were in git worktrees on one x86_64 Linux cloud container, GNU bash 5.2.21:
  - at 76b902b9 (this head): every line read `worktree_gc self-test: 160 checks, 0 failed`; count line `25 of 25 green`.
  - at c9aed94c (the reviewer's reproduction): lines alternated between `167 checks, 0 failed` and `167 checks, 104 failed` / `167 checks, 100 failed`; count line `13 of 25 green`.
- Check count, rule: the self-test's own `N` counter, one per `st` call. 167 at c9aed94c, 160 here: `argvco` and `pidfuse` take 2 each, and `nopsbin` takes 3.
- The mutant run above: 43 spec entries, 38 KILLED, 6 SURVIVED including NULL. Rule: `grep -c ^KILLED` and `grep -c ^SURVIVED` over the run's output.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`, and `scope.run` is empty. `worktree_gc.sh` is in no measured closure, so CI never runs this self-test.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, rc 0; no metric moved up.
- `git merge-tree --write-tree origin/main HEAD` rc 0 at a7628041.
- Seam enumeration (step 8): `grep -n 'cwd_free' tools/audit/worktree_gc.sh` lists every removal arm's keep check. They all call `cwd_free` and so gain the new arms; the class is closed in this diff.
- Cost per candidate: one `lsof -a -d cwd`, one `ps -eo args=` and one `lsof -Fn` per candidate worktree, which the round-2 review measured at tens of ms each. A once-per-sweep read was rejected because a process starting between candidates would be missed.

## Red checks

none

## Forward-carry

none

## Friction

none
