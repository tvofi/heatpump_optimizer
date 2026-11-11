Fix review: blocked 9e2c18ff8af69a2f1f4269d655761665c2af6dc2 mutation-survivors: argv terminator members quote and colon/comma survive on the added argv-inside awk line

bus-nonce: 23bb0265faaee10ee3d83b62292fff79
pending-ci: gate

## Block

Round 3 of review (delta re-review of 032e758e4..9e2c18ff8; `review_carry.py` prints FRESH-REVIEW). The four mutants the round-2 verdict named now fail, but the `argvterm` class is only partly pinned. The argv-inside awk line added by this PR (`tools/audit/worktree_gc.sh:722`) accepts six terminators: `""`, `/`, `"`, `'`, `:`, `,`. The repair pins `""` (`seat-argvco`) and `/` (`seat-argvscr`), and the null control pins the upper bound (`seat-argvsib`). Nothing pins the other four:

- `argvterm-quote` (drop `t=="\""` and `t=="\x27"`): 154 checks, 0 failed.
- `argvterm-colon` (drop `t==":"` and `t==","`): 154 checks, 0 failed.

Each one is a keep decision that matters in practice. A `sh -c 'cd "<wt>"; ...'` relay shows up in `ps -eo args=` as the token `"<wt>";`, and a `--x=<wt>:<other>` or `<wt>,<other>` list argument ends in `:` or `,`. Delete any of these four members and the sweep collects a live checkout, which is the P453 failure. The suite still stays green. The body's `## Unpinned sites` lists `argvterm` as pinned, and that is true only of the `""`/`/` members.

Fixtures owed: one argv-fixture seat per uncovered terminator, for example `bash -c cd "<wt>/x"` with no space, a `'<wt>'` token, `--paths=<wt>:/tmp` and `--paths=<wt>,/tmp`. Each must be kept and named `argv-inside`. The alternative is to remove a member from the set with a stated disposition under `## Unpinned sites`. Then re-run the two mutants above, plus one mutant per member.

## Findings

- Residual: `[ -n "$out" ] || return 2` in `cwd_inside` (an empty `lsof -a -d cwd` listing counts as unreadable) survives its deletion mutant (`lsofcwd-empty`, 154/0). The line comes from main at d08ed3104 (the old `cwd_inside`, line 651 there), so this PR does not owe it. Carry: dismissed: pre-existing line on main, not added or changed by this PR, and not in this PR's mutation scope

## Evidence

- Head reviewed: 9e2c18ff8af69a2f1f4269d655761665c2af6dc2 (ev/HEAD.txt). It matches the PR head in the GitHub API and the body's `## Head`.
- RESULT selftest-head: `bash tools/audit/worktree_gc.sh --self-test` at the head gives 154 checks, 0 failed, rc 0 (ev/selftest-head.txt). This matches the body's figure.
- RESULT mutants: each applied alone in a detached worktree at the head, the self-test run, then restored (ev/mutants.py, ev/mutant-*.txt):
  - lockglob (both globs dropped): 4 failed. lockglob-star alone: 2 failed (x.lock). lockglob-dot alone: 2 failed (.x.lock). Pinned.
  - argvterm-slash (drop `/`): 2 failed (argvscr). argvterm-empty (drop `""`): 4 failed (argvuse and argvco). Pinned.
  - argvterm-any (accept any terminator): 1 failed, the argvsib null control. The null control moves under its own perturbation.
  - lsofall (`lsof -Fn` with no `|| return 2`): 2 failed (noopen). Pinned.
  - nopsbin/psunread (`ps -eo args=` with no `|| return 2`): 3 failed (nops and nopsbin). Pinned. The deleted `command -v ps` line is redundant with this arm, since an absent ps exits 127. I accept the disposition.
  - argvterm-quote: 0 failed. argvterm-colon: 0 failed. SURVIVORS, see Block.
  - lsofcwd-empty: 0 failed. Pre-existing, see Findings.
- Null controls: argvsib moves (above). The binnops no-ps PATH check is in the self-test and passes. deadpid is unchanged from the prior round.
- The body now has a `## Unpinned sites` section (brief check 2). It is accurate except for the argvterm partial-pin claim.
- Cost figure: the body states the per-candidate reads (one `lsof -d cwd`, one `ps`, one `lsof -Fn` per candidate worktree) and the reason for rejecting a once-per-sweep read. I could not re-derive its exact numbers, because they come from another container. On this container (4164 `lsof -Fn` lines): `lsof -Fn` 0.060 s, `ps -eo args=` 0.009 s, `lsof -a -d cwd -Fn` 0.027 s real (ev/cost.txt). The order of magnitude agrees (tens of ms per candidate), but which of the two reads is slower comes out the other way round here.
- `git merge-tree --write-tree origin/main 9e2c18ff8` rc 0: merges cleanly.
- Role drift: `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- The three-dot diff touches only `tools/audit/worktree_gc.sh` and `dev/programme/delivery/3423.md`. VERSION, the manifest and the notes heading are untouched. There are no claim files and no budgets.
- The prior round's other findings are resolved: lockglob, the argvterm `/` member, lsofall and nopsbin are pinned, and `## Unpinned sites` is present.
- CI: `merge_train.py classify` was polled every ~60 s from 03:12 to 03:33 UTC and printed `WAIT 9e2c18ff8af69a2f1f4269d655761665c2af6dc2 pending: gate red: none` (rc 3) throughout (ev/classify.txt). No required red at review time. This verdict's block does not depend on CI.
- `merge_train.py owed-reds` (ev/owed-reds.txt) lists the required contexts. No red is owed an answer at the time of review.
