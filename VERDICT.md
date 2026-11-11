Fix review: blocked c9aed94c0e5ae5fe7cd99e538aaecdfdf07f85c7 flaky-harness: the added ZPID loop's killed pre-exec subshells run the self-test EXIT trap rm -rf "$W" and fail the pin harness in most runs

bus-nonce: 33f7211048acdf977f64d0b7a0d23e5f

## Block

Delta re-review of 9e2c18ff8..c9aed94c0, which the dispatch brief calls round 3 (the prior verdict also called itself round 3; counted by verdicts, this is the fourth, at which `fixer.md` owes a re-cut). `review_carry.py` prints FRESH-REVIEW.

The repair is sound as code: every mutant the round-3 verdict named is now killed (see Evidence). But the fixture this repair added makes the PR's own pin harness, `bash tools/audit/worktree_gc.sh --self-test`, fail nondeterministically:

- `tools/audit/worktree_gc.sh:217` (added in 9d0e93669) loops `sleep 600 & ZPID=$!; case $ZPID in *0*) break;; esac; kill "$ZPID"` until a pid contains a 0.
- A `kill` that lands in the fork-before-exec window hits a bash subshell. That subshell still carries the self-test's EXIT trap from line 119 (`trap '[ -n "${ZPID:-}" ] && kill "$ZPID" 2>/dev/null; rm -rf "$W"' EXIT`), runs it, and deletes the whole fixture directory `$W`, stubs included, while the self-test is still running.
- Result on this container (GNU bash 5.2.21): the full self-test at the head printed `167 checks, 104 failed`, `100 failed` (in a git worktree), `105 failed` (in a git-archive copy), `105 failed`, then once `0 failed` (ev/selftest-flake-runs.txt, ev/selftest-head*.txt). The base d08ed3104 printed `132 checks, 0 failed` (ev/selftest-base-worktree.txt).
- Minimal repro of lines 119 and 217 alone (ev/zpid-repro.sh, ev/zpid-repro.txt), 6 runs: whenever the loop iterated more than once, the trap ran in 3 to 11 subshells and the fixture was gone (`fixture-present=NO`). Null control: the run whose first pid contained a 0 (`iterations=1`) ran 0 subshell traps and kept the fixture.
- Changing only the trap's `rm -rf "$W"` to `:` (ev/deflaked.sh, a reviewer-built wrapper and not the finder's) gave `167 checks, 0 failed` in every run (ev/selftest-orig-loop-last.txt is the original's one lucky pass; the trap-only variants passed 3 of 3).

So the body's `167 checks, 0 failed` figure is a lucky draw, not the head's behaviour. Any `KILLED` the unmodified harness reports, the fixer's 24 included, can come from the race instead of the mutant. In my first, unmodified run, `trap-zpid-unguarded` read KILLED and then SURVIVED once de-flaked.

CI does not catch this: `worktree_gc.sh` is in no measured closure, so the scoped gate never runs the self-test.

Owed: keep the helper's subshell from inheriting the trap, for example `( trap - EXIT; exec sleep 600 ) &`, or guard the trap with `[ "$BASHPID" = "$$" ] || exit`. Then show the unmodified self-test passing on repeated runs, at least 5 consecutive, and the repro's NO case gone. A fixture that removes the race has to be shown passing repeatedly, not once.

## Findings

- Residual: `[ -n "$out" ] || return 2` in `cwd_inside` (an empty `lsof -a -d cwd` listing counts as unreadable) survives its deletion mutant (`lsofcwd-empty`, SURVIVED under the de-flaked harness). The line comes from main at d08ed3104, not this PR, and the body dispositions it under `## Unpinned sites`. Carry: dismissed: pre-existing line on main, not added or changed by this PR, and not in this PR's mutation scope

## Evidence

- Head reviewed: c9aed94c0e5ae5fe7cd99e538aaecdfdf07f85c7 (ev/HEAD.txt). It matches the PR head in the GitHub API, `refs/pull/3423/head` (ev/head-at-post.txt) and the body's `## Head`.
- FIRST STEP, prior verdict's named mutants, run with `mutant_run.py --spec ev/spec.json` and the de-flaked wrapper `--cmd 'bash ev/deflaked.sh'` (ev/mutants-deflaked.txt): `SURVIVED NULL`, then KILLED argvterm-quote, argvterm-colon, argvterm-dq, argvterm-sq, argvterm-col, argvterm-com, argvterm-slash, argvterm-empty, argvterm-any (the argvsib null control moves), openfile-eq, openfile-sib (the opensib null control moves), pidzero-tr, lockglob-star, lockglob-dot, lsofall, psunread.
- The removed empty-pid guard is redundant, shown by mutant: `pidguard-restored` (re-adds `[ -n "$pid" ] &&`) SURVIVED and `pidempty-unquoted` SURVIVED. A direct probe (ev/pidempty-probe.txt) gives `kill -0 ""` rc 1 and `kill -0` with no argument rc 2. On a no-digit `train.pid` and an empty `x.lock`, both the guarded and unguarded forms read `free`. I accept the deletion.
- `trap-zpid-unguarded` (revert of d43bce9c9's trap) SURVIVED de-flaked. It is cleanup only: it kills the helper `sleep` at exit and pins no behaviour.
- The unmodified-harness spec run (ev/mutants.txt) gave the same verdicts except `trap-zpid-unguarded` KILLED, which is the race. That run's NULL happened to pass.
- Prior findings: round 3's argvterm quote/colon/comma survivors are resolved. The lsofcwd-empty residual is carried as dismissed, as before.
- `git merge-tree --write-tree origin/main c9aed94c0` rc 0: merges cleanly.
- Role drift: `git diff <merge-base>...origin/main -- dev/governance/roles/` changes only the owed-reds wording in fix-review.md and fixer.md, which this review applies.
- CI: `merge_train.py classify c9aed94c0... --pr 3423` read WAIT (pending: gate) at 05:36 UTC and `GREEN c9aed94c0e5ae5fe7cd99e538aaecdfdf07f85c7 pending: none red: none` (rc 0) at 05:37:12 UTC (ev/classify.txt). The review packet's `red-unanswered: gate` refers to gate run 130340237322, which exited early with "FAIL run(s) [42964861546] at this head are still being judged; their gate decides". classify reads the later gate run, which is green, so no red is owed and the body's `## Red checks: none` stands. `merge_train.py owed-reds` is in ev/owed-reds.txt.
- The three-dot diff touches `tools/audit/worktree_gc.sh` and `dev/programme/delivery/3423.md` only. VERSION, the manifest, the notes heading, claim files and budgets are untouched.
- The fixer's 24-mutant count could not be re-derived as stated, because the body gives no spec file. My own 20-mutant spec covers every site the round-3 verdict and this brief name.
