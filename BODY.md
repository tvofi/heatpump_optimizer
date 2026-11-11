P453: `worktree_gc.sh` collected live train/relay checkouts because it kept a worktree only when a process's cwd was inside it (five instances on 11-08). Every removal arm (all go through `cwd_free`) now also keeps a worktree named in a live process's argv (`git -C`, `--checkout=`, script path; `ps -eo args=`), with an open file (`lsof -Fn`), or holding a live `train.pid`/`*.lock`/`.*.lock` pid; an unreadable or absent `lsof`/`ps` keeps it as `cwd-unread`. `--keep-dir` is documented as the evidence destination, not a keep list; no protect flag was added. Alternative rejected: `lsof +D` per worktree, which walks the tree.

Carry 1 (the brief's Carry 0, GC-LIVE-TRAIN-CHECKOUT) is built in this PR.

Round 3 repair of the blocked verdict at 9e2c18ff (`argvterm` quote and colon/comma members survived): every member of the argv terminator set now has its own kept fixture and its own killed mutant, three further added-line survivors found by the mutation pass are pinned or deleted, and the earlier rounds' pins stay.

## Head

d43bce9c9bbf571fc0d9b716fe8a411f9e03c5c2 (base origin/main dbd1ab5b07, 2026-11-11 `date -u`)

## Mutation proof

Instrument: `python3 tools/audit/seat/mutant_run.py --spec <spec.json> --cmd 'bash tools/audit/worktree_gc.sh --self-test'` at the head above, 24 mutants over the PR's added production lines (the `--diff` mode of that driver mutates Python only and printed nothing for this shell diff, so the spec is the added-line enumeration: `cwd_inside`'s argv, open-file and pidfile arms). Result: `SURVIVED NULL` (the unedited tree passes), then `KILLED` for all 24, zero `SURVIVED`.

The argv terminator set, each member by its own mutant (that member dropped), the failing self-test checks quoted from a run with it applied (the restored tree: 167 checks, 0 failed):

- `""` (`--checkout=<wt>`; `git -C <wt> log`): `term-empty`, 4 failed: "argv names the worktree (git -C) ... kept", "naming argv-inside", "argv carries --checkout=<worktree> (empty terminator): kept", "naming argv-inside for --checkout=".
- `/` (`bash <wt>/script.sh`): `term-slash`, 2 failed: "argv names a script inside the worktree (terminator /) ... kept", "naming argv-inside for the script path".
- `"` (`sh -c 'cd "<wt>"; ...'` shows the token `"<wt>";`): `term-dq`, 2 failed: "argv carries a double-quoted <wt> token from sh -c cd (double-quote terminator), cwd elsewhere: kept (got '1', want '0')", "naming argv-inside for argvdq".
- `'` (a single-quoted `'<wt>'` token): `term-sq`, 2 failed: "... single-quoted <wt> token (single-quote terminator) ... kept", "naming argv-inside for argvsq".
- `:` (`--paths=<wt>:/tmp`): `term-colon`, 2 failed: "argv carries --paths=<wt>:/tmp (colon terminator) ... kept", "naming argv-inside for argvcol".
- `,` (`--paths=<wt>,/tmp`): `term-comma`, 2 failed: "argv carries --paths=<wt>,/tmp (comma terminator) ... kept", "naming argv-inside for argvcom".
- `term-any` (every terminator accepted): the sibling-prefix null control `seat-argvsib` fails, so the set is bounded above as well as below.

The other added lines, each mutant killed: `awk-k-ge` (`k>0` to `k>=0`), `awk-field1` (`$i` to `$1`), `awk-tail-1` (terminator offset), `ps-ret2` and `lsofall-ret2` (`|| return 2` replaced by `|| true`), `way-argv`/`way-open`/`way-pid` (wrong `HELD_WAY`), `kill0` (`kill -0` check replaced by `true`), `glob-all`/`glob-star`/`glob-dot`/`trainpid` (the pidfile globs and `train.pid`), `head-c`, and the three below.

Survivors found by the first pass of this spec and answered in this diff:

- `open-eq` (`d==p ||` dropped from the open-file awk): new seat `openeq`, an open file that is the worktree directory itself, kept naming `open-file`; killed.
- `open-prefix` (`index(d, p "/")==1` to `index(d, p)==1`): new null control `opensib`, an open file under `<worktree>2/f`, collected; killed.
- `tr-digits` (`tr -dc '0-9'` to `'1-9'`): new seat `pidzero`, `train.pid` holding a live pid that contains a zero digit (a helper `sleep` chosen so its pid has a 0), kept naming `pidfile-live`; killed.
- `pid-empty-guard` (`[ -n "$pid" ] &&` dropped): equivalent, because `kill -0 ""` fails. The guard was dead code, so it is deleted rather than triaged; the remaining `kill -0 "$pid"` is pinned by `kill0` and the pidfile seats.

Kept members and the caller shape each serves: `""` `--checkout=<wt>`/`-C <wt>`; `/` `<wt>/script.sh`; `"` `sh -c 'cd "<wt>"; ...'`; `'` `'<wt>'`; `:` `--paths=<wt>:/tmp`; `,` `--paths=<wt>,/tmp`. No member was removed: each serves a caller shape the ps listing shows, and each is now pinned.

Self-correction while building the fixtures: the first `argvdq` assertion message carried raw double quotes, which closed the shell string, so that assertion passed vacuously under the dropped-`"` mutant and only the naming check failed; the message is reworded and both checks now fail under the mutant (quoted above).

Earlier rounds' mutants (`lockglob`, `lsofall`, `psunread`/`nopsbin`) are in the spec above and killed.

## Null control

- `seat-argvsib`: argv names `<worktree>2` (a sibling prefix): collected; moves under `term-any`.
- `seat-opensib`: an open file under `<worktree>2/f`: collected; moves under `open-prefix`.
- `seat-deadpid`: dead-pid `train.pid`, no live user: collected.
- `binnops` PATH really has no `ps` (`command -v ps` rc 1, a self-test check).
- The unedited tree: `SURVIVED NULL` from `mutant_run.py` (the command passes before any edit).

## Unpinned sites

- `argvterm` (all six members), `open-file` equality and prefix, the zero-digit pid, `lockglob`, `lsofall`: pinned by in-tree self-test fixtures, mutants above (a `tools/` site has no `mutation-autofix` lane; `--self-test` is the in-tree harness).
- `command -v lsof ... || return 2`, and `[ -n "$out" ] || return 2` in `cwd_inside` (an empty cwd listing counts as unreadable): pre-existing main lines, not added or changed by this PR. Carry: dismissed: pre-existing lines on main (the review's residual, out of this PR's scope).
- `[ -n "$pid" ] &&`: deleted as equivalent (above).

## Figures

- `bash tools/audit/worktree_gc.sh --self-test`: last line "167 checks, 0 failed" at the head above.
- `python3 tools/audit/seat/mutant_run.py --spec <spec.json> --cmd 'bash tools/audit/worktree_gc.sh --self-test'`: 24 `KILLED`, `SURVIVED NULL`, 0 `SURVIVED`.
- `python3 tools/audit/seat/mutant_run.py --diff $(git merge-base origin/main HEAD)...HEAD --cmd 'bash tools/audit/worktree_gc.sh --self-test' --report-only`: prints no mutant, because the diff arm reads Python lines and this diff has none (the null control of the spec count above).
- Cost per candidate: unchanged from round 2 (one `lsof -d cwd`, one `ps`, one `lsof -Fn` per candidate worktree, measured on the review's container at tens of ms each; which of the two is slower varies by container). A once-per-sweep read was rejected: a process starting between candidates would be missed.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: mode line recorded by the prepr run; worktree_gc.sh is in no measured closure.
- Seam enumeration (step 8): `grep -n 'cwd_free' tools/audit/worktree_gc.sh` lists every removal arm's keep check; all call `cwd_free`, so all gain the new arms (closed in this diff).

## Red checks

none

## Forward-carry

none

## Friction

none
