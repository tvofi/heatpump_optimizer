Fix review: blocked 032e758e484bec0753cd2f68cfb5393f028fe223 mutation-survivors: four added cwd_inside lines survive their mutants, two of them carrying behaviours the body claims (*.lock pidfile, script-path argv)

bus-nonce: 468a08516fd8f401a3795ec2ae3d6ff6

## Block

Round 1 (first review). Head measured: `032e758e484bec0753cd2f68cfb5393f028fe223`.

Each mutant was applied alone to `tools/audit/worktree_gc.sh` at the head, followed by `bash tools/audit/worktree_gc.sh --self-test`, then `git checkout` to restore. Output is in `ev/mut-<name>.txt`. Four mutants of production lines this PR adds survive (140 checks, 0 failed):

- `lockglob`: `for f in "$p/train.pid" "$p"/*.lock "$p"/.*.lock; do` -> `for f in "$p/train.pid"; do`. The body claims a live `*.lock` pid keeps a worktree, and no check pins that. Owed: a fixture with a live pid in `<wt>/x.lock` (and `.x.lock`), kept and named `pidfile-live`.
- `argvterm`: the argv terminator set `t=="" || t=="/" || t=="\"" || t=="\x27" || t==":" || t==","` -> `t==""`. The body claims the "script path" form (`bash <wt>/tools/x.sh`, terminator `/`) and `--checkout=<wt>` forms. The only fixture is `git -C <wt> log`, a bare token. Owed: an argv fixture `<wt>/script.sh` (terminator `/`) kept, and a sibling-prefix null control (`<wt>2` in argv, terminator `2`) collected. That control pins the reason the set exists.
- `lsofall`: `out=$(lsof -Fn 2>/dev/null) || return 2` -> `|| out=""`. This is the fail-closed arm of the new open-file read. The `nolsof` stub breaks every `lsof` call, so the earlier cwd call returns 2 first and this line is never reached. Owed: a stub that fails only the non-`-d cwd` call. The worktree must be kept as `cwd-unread`.
- `nopsbin`: `command -v ps >/dev/null 2>&1 || return 2` -> `:`. The self-test always has the `ps` stub on PATH, so a host without `ps` is untested. Owed: a case with `ps` absent from PATH, kept as `cwd-unread`, or a stated disposition of the site.

The fail-closed arms above guard against the defect P453 is about (collecting a live checkout), so an unpinned arm is the bug this PR fixes, left open on another path. `fixer.md` step 2 requires a disposition for every unpinned site the diff adds (a `tools/` site needs an in-tree mutant harness). The body has no `## Unpinned sites` section.
- Unverified figure (step 8): the body says "one `lsof -Fn` listing is matched instead" of `lsof +D`. In fact `cwd_inside` runs a full `lsof -Fn` and a `ps -eo args=` once per candidate worktree, not once per sweep. The body gives no figure for either, so the cost on a Pi is not verified. Owed with the re-cut: read both listings once per sweep, or give the measured per-candidate cost.

## Evidence

- RESULT self-test at head: `worktree_gc self-test: 140 checks, 0 failed` (`ev/selftest-head.txt`). This matches the body's figure.
- RESULT named mutants, killed one at a time: `argv` 2 failed, `open` 2 failed, `pid` 2 failed (`ev/mut-argv.txt`, `ev/mut-open.txt`, `ev/mut-pid.txt`). The body's "fails 6 checks" is the three applied together. I reproduced 6 when my first run accumulated all three, so the body's figure is re-derived.
- RESULT other killed mutants: `psunread` 1 failed (the `nops` case), `killcheck` 1 failed (the dead-pid null control), `heldway` 3 failed.
- Null control (`seat-deadpid`): present, and killed by the `killcheck` mutant, so the control moves under its own perturbation.
- Seam enumeration: the body's rule is `grep -n 'cwd_free'`, and every removal arm calls `cwd_free` -> `cwd_inside`. No seam lies outside the diff.
- Closure figure: `python3 tests/closure.py select --diff <merge-base>` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out.`, which matches the body (`ev/closure-select.txt`).
- Merge: `git merge-tree --write-tree origin/main <head>` rc 0, no conflict. The merge base equals origin/main `d08ed31049` (`ev/merge-tree.txt`).
- `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched; the three-dot diff touches only `tools/audit/worktree_gc.sh` and `dev/programme/delivery/3423.md`. The claim files are untouched.
- The role contracts under `dev/governance/roles/` are the same on main and at the merge base (the diff is empty).
- Finder's harness: none is committed. The finding (P453) is checked by the self-test fixtures this PR adds, so the instrument is the fixer's, not the finder's (step 9).
- Red check `gate` id 130258225077 (01:33Z): the log reads `FAIL run(s) [42939424618] at this head are still being judged; their gate decides`. This is a defer, not a verdict. `merge_train.py classify --pr 3423` reads `WAIT ... pending: gate red: none` (`ev/classify.txt`). Final: `GREEN 032e758e484bec0753cd2f68cfb5393f028fe223 pending: none red: none`, rc 0 at 01:52:14Z. CI is not a ground for this block.
- Head at verdict: `git ls-remote origin refs/pull/3423/head` reads `032e758e484bec0753cd2f68cfb5393f028fe223`, the head measured, so it has not moved.
