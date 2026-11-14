Hotfix R10-HOTFIX-CARRY-TIP-SIGPIPE. Since #3514 (decision 0017), `carry()` in `tools/pr/app_approve.sh` checked whether a head is a branch tip of origin with
`printf '%s\n' "$heads" | grep -q "^$h[[:space:]]refs/heads/" || ours=0` under `set -uo pipefail`. origin lists 7937 branch heads. `grep -q` exits at its first match, the `printf` writer then gets SIGPIPE, and under pipefail the pipeline returns 141. So `ours=0`: a head that **is** a branch tip of origin was read as a fork's head, and every range with a row or bot commit answered `FRESH-REVIEW` / `CARRY: no`. This blocked every verdict carry on main's tools.

How the cause was confirmed:
- `python3 tools/audit/seat/review_carry.py 2b8893814da8e6cf0a5fd8b33c05d849f2717d45 341677c1974c819ee417226897047192b703014c` at origin/main prints `FRESH-REVIEW ... on a head that is no branch tip of origin`. At the same time, `git ls-remote --heads origin` lists `341677c1... refs/heads/fix/r10-hotfix-main-selftest-scope`.
- The pipeline in isolation, under `set -uo pipefail`, with the match first: 8001 heads give `PIPESTATUS=141 0`, and one head gives `PIPESTATUS=0 0`.

The fix uses here-strings (`grep -q ... <<<"$heads"`). A here-string has no writer process that a closing reader can kill, the trailing newline is the same as `printf '%s\n'`, and it works on bash 3.2.

The coordinator also added the `gh_transient` census flake to this hotfix. The row `and gh_transient prints nothing on either stream` failed in CI job 132518925875. `gh_transient` ends in the same shape: `printf '%s\n' "$1" | grep -qE '^Get ...|^error connecting to '`. The CI runner ignores SIGPIPE: the same job log prints `printf: write error: Broken pipe` from `tick_loop.sh:224` and `pr_args.sh:454/464`. So when grep exits at a first-line match while printf is still writing, printf writes that message to stderr, and the census captures it with `2>&1`. When SIGPIPE is not ignored, the same race returns 141 and a transient read is refused. I could not reproduce the race on the census's own two-line inputs locally: 2000 iterations on macOS bash 3.2 in both signal regimes gave 0 hits. With a long input the mechanism is deterministic. The fix makes the race impossible, because the function has no pipe left.

Sweep (tools/pr and tools/audit/seat). Enumerated with
`git grep -nE '\|[[:space:]]*grep[[:space:]]+-[a-zA-Z]*q' -- tools/pr tools/audit/seat`: 236 lines, all at origin/main 6858b4abc1.
Fixed, because each can take an input larger than a pipe buffer (16 KB on macOS before it grows) with the match early:
- `tools/pr/app_approve.sh` `carry()` heads (the defect), `gh_transient` gh stderr (the flake), and the bot-commit name list `$bt`.
- `tools/audit/seat/bus.sh` re-cut check: a PR body can be up to 64 KB, with `## Re-cut` near the top.
- `tools/audit/seat/pr_args.sh` `pr_pushers`: whole script texts (app_push.sh and others are far above 64 KB). This is the source of the CI `Broken pipe` lines; under `pr_trap`'s pipefail it would report a false OPEN.
- `tools/audit/seat/handoff_push.sh` note: the diff names over a main merge. It uses a grep without `-q`, which reads to the end, because a here-string of an empty diff would match the empty line.
Dismissed, with the reason:
- `app_approve.sh:154`: one status line from `tail -1`.
- `bus.sh:827`: one review_packet message.
- `bus.sh` self-test rows 1267 and later (151 lines): stub output of a few lines from one single-argument printf. Locally, 2000 runs of that shape lost no race. It is still the same class with a narrow window, so it is left to the class barrier under Forward-carry rather than rewritten in a hotfix.
- `tick_loop.sh` (37): the self-test turns pipefail off on purpose (line 216), and row 224 is that guard's own test. The production rows read short `$out`.
- `pr_args.sh:457/460` tails (`grep -E ... | grep -qv`): the upstream grep emits a few matching lines, which fits any buffer.
- `pr_args.sh:471` (`printf '%s\n' $found | grep -qxF`) is **fixed** as well, although its list is only about 20 paths. With one argument per path, printf writes once per line, and a local `pr_args.sh --self-test` printed `line 473: printf: write error: Broken pipe` from this line. So a large input is not the only way to trigger the race: a writer that makes several `write()`s can lose it on small input too.
- `pr_args.sh:1397`: the `## Head` section.
- `cloud_relay.sh` (9): single 40/32-hex values, or self-test fixtures (`owes`, `dbtree`).
- `ci-watch.sh`: no pipefail of its own, and it neither sources `pr_args.sh` nor calls `pr_trap`.
- `update_pr.sh:69` (`git worktree list | grep -F "[$BR]" | grep -vqF "$WT "`): it runs under `pr_trap`'s pipefail, but both upstream stages read to the end, and the early-exit `grep -vqF` sees only the few lines naming `[$BR]`. That output fits any pipe buffer in one write.
- `heartbeat.sh`, `seat_venv.sh`: self-test `$out` of a few lines.
- `app_push.sh:930/945`: one `ps` character.
- `prepr.sh:3198/3200`: the match is the last trailer line, so no early exit.
- `push.sh:170/206`: the `## Head` section of a body.

Changed since cb803e9e (review round 1, verdict probe/revt-r10-hotfix-carry-tip-sigpipe-a366776e, blocked class-open):
- `tools/audit/seat/open_pr.sh:125` (`op_clear_leftover`) is fixed. Round 1 dismissed it as "no pipefail", and that was wrong: `open_pr.sh` calls `pr_trap`, which sets `set -Eeo pipefail`. `git worktree list --porcelain | grep -qxF "worktree $WT"` read a registered left-over checkout as absent once the list outgrew the pipe. It now uses a here-string. A deterministic probe, with a git wrapper appending 3000 worktree entries after git's own list and `set -Eeo pipefail`, gives `pipe:MISSED 141 0` 5 of 5 and `here:found` 5 of 5.
- `open_pr.sh:48` (`OP_REG=$(git worktree list --porcelain | awk '... exit')`) is fixed as well. The new row found it: awk's `exit` is an early-exit reader on the same list, and under `pr_trap` the 141 stopped the run through errexit before line 125 was ever reached. It now uses a here-string. If `git worktree list` itself fails, that is now read as "no registration" (the lone-run path) rather than stopping the run.
- `pr_args.sh:448` (`kind=$(printf "$PR_PUSHERS" | awk '... exit')`, inside `pr_pushers`, which runs under `pr_trap`) is fixed as well, with a here-string.
- The other early-exit readers in the `pr_trap` scripts (`| head`, `| awk ... exit`, `| sed q`, `| grep -m`, over `open_pr.sh`, `update_pr.sh`, `delivery_row.sh` and `pr_args.sh`) are disposed: `open_pr.sh:170` (`grep -oE 'pull request #N' p1.log | head -1`) reads a grep that emits a line or two in one write, and `pr_args.sh:1532` is a `head -n` on a file, not a pipe.
- New row in `pr_args.sh --self-test` (open_pr's self-test): `open_pr: the same re-run with 3000 more worktrees listed after the left-over one still clears it and opens`. It uses the existing closed-after-p2 re-run harness, with that git wrapper on PATH.
- The enumeration is widened to every shell script under tools/, so that a script with no pipefail of its own but running under a sourced `pr_trap` is caught: `git grep -nE '\|[[:space:]]*grep([[:space:]]+-[a-zA-Z-]+)*[[:space:]]+-[a-zA-Z]*q' -- 'tools/**/*.sh'`. It prints 232 lines at 7d186ed4 and 236 at 6858b4abc1 with macOS git; the counts include comment lines that name the pattern. Every script that calls `pr_trap` (`open_pr.sh`, `update_pr.sh`) or is sourced into one (`pr_args.sh`, `delivery_row.sh`) was re-read: open_pr.sh:125 was the one open `grep -q` site. The early-exit-reader sites the new row then exposed are listed above. The only new file it reaches is `tools/coverage/coverage_tree.sh:300` (`printf "$_grade" | grep -qE`). It is dismissed: the script is executed, not sourced, it sets no pipefail, and a new bash does not inherit a caller's pipefail, so grep's status decides.
- Answer to the verdict's surviving-mutant note (the `$bt`, bus re-cut, handoff_push and census rewrites have no row that fails on the old line): the verdict routes it to R11-INTAKE-R10-RESIDUE, and the class lint pins it there. This hotfix pins the two lines that broke (carry, gh_transient) and the open_pr site.
- Answer to the verdict's count note: the round-1 figure 236 was measured on macOS at 6858b4abc1, and the reviewer's Linux count differs. The widened command's count at this head is given above. A later reader re-measures at their own base.
- Answer to the dismissal note on `update_pr.sh:69`: the reason is rewritten above.

Leaves #3394 open.

## Head

7d186ed4a5fe4f7097332e05562f0870b3e3f1aa

## Mutation proof

Each mutant is a copy of `app_approve.sh` with one old line restored, run with `--self-test`:
- carry line restored (`printf '%s\n' "$heads" | grep -q ...`): `FAIL CARRY on a head of ours listed first among 20001 branch heads of origin (got '1', want '0')`, `app_approve self-test: 353 checks, 1 failed`.
- gh_transient line restored: `FAIL gh_transient: an early transient line in a long stderr is still transient (got '1', want '0')` and `FAIL (and with SIGPIPE ignored, as in CI, it prints nothing and still classifies transient) (got '...: line 160: printf: write error: Broken pipe ...`, `353 checks, 2 failed`. The second FAIL reproduces the CI flake's message class.

Round 2 (open_pr.sh). The new row is `open_pr: the same re-run with 3000 more worktrees listed after the left-over one still clears it and opens`, in `pr_args.sh --self-test` on macOS:
- Both lines old (red first): `FAIL`, `260 checks, 12 failed`.
- Head 7d186ed4: `ok`, `260 checks, 11 failed`. The 11 are the same FAIL lines as origin/main's own run on this host (BSD sed, pr_bounded, host_refusal), with a `diff` of the FAIL lines against the base run that is empty.
- Mutant, line 125 restored alone: `FAIL` (the left-over checkout is read as absent), `12 failed`.
- Mutant, line 48 restored alone: `FAIL` (awk's exit gives 141 under errexit), `12 failed`.
- The neighbouring row `open_pr: a re-run after an open closed at its row push clears ...` (21 worktrees' worth of list) stays `ok` in all four runs. It is this row's null control.

Failing test first: the new carry rows on the unfixed tree gave `FAIL CARRY on a head of ours listed first among 20001 branch heads of origin (got '1', want '0')`, `app_approve self-test: 351 checks, 1 failed`.

## Null control

- Unmodified origin/main 6858b4abc1: `app_approve self-test: 348 checks, 0 failed`. This tree has no row with more than a handful of heads, so the defect passed silently.
- The new null-control rows pass both before and after the fix: `ok   NO CARRY: the same 20000 heads without it (null control)` and `ok   refused as a head that is not ours`. A head that is not a tip still refuses.
- Touched instruments on macOS: `handoff_push self-test: 6 checks, 0 failed`. `pr_args.sh` and `bus.sh` show the same FAIL lines at origin/main as on this head. These are host failures: BSD `sed -i` in the census fixture, and APFS case-insensitivity in bus's case-collision row. I re-ran the census rows by hand with BSD `sed -i ''`: no trap gives `OPEN ... no pr_exit_trap`, a foreground push gives `OPEN ... runs in the foreground`, and no push hold gives `OPEN ... holds no push lock`. Its null control (no branch lock) returns rc 0, and the clean tree returns rc 0. CI on Linux is the authority for those rows.
- After the fix: `app_approve self-test: 353 checks, 0 failed`. `tools/audit/seat/bare_array.py --check` exits 0.

## Figures

none

## Red checks

The defect turned main's carry red with no check catching it. The cheaper detector is the self-test row this PR adds: a stubbed `ls-remote` lists the head first among 20000 heads, so any early-exit reader fails deterministically, in seconds, in the existing `app_approve` self-test step, at no new standing cost. The census flake's detector is the paired long-stderr rows, which are deterministic where the two-line census rows were not. Cause: #3514 added a pipe into `grep -q` over an unbounded producer under pipefail. This class is already named in comments in `prepr.sh:216/1881/3664`, `app_push.sh:1088`, `cloud_relay.sh:308`, `seat_venv.sh:254` and `tick_loop.sh:213`. The fixture had only a few heads, so the row could not see it.

The checks below are red on commits in `6858b4abc1..origin/fix/r10-hotfix-carry-tip-sigpipe` that are not this hotfix's. They arrived when the PR branch merged main at 5c4a7a0fc6: main's own commits since the hotfix's base, and other PRs' branch commits that main carries. None is on cb803e9e or 7d186ed4, which carry no failed run. Each was measured with the check-runs API per commit:
- `governance / instrument-self-tests`: red on 070118088a and ff8b073827, which are other branches' commits merged into main. This branch did not cause it, so it owes no detector.
- `tests / ci-ratchet`: red on 5cd7b87413 (main's merge of #3588). Not this branch's, so it owes no detector.
- `tests / fast (3.14)`: red on 070118088a. Not this branch's, so it owes no detector.
- `tests / mutation`: red on 837ead0bd7 and 5b197bd685. Not this branch's, so it owes no detector.
- `tests / nightly-status`: red on the record commits and main-side merges (63ca72623e, 16ee88317b, 65a5a17301, 341677c197, e81c5ac940, 1506411191, 837ead0bd7, 5b197bd685, 070118088a). It reports the nightly run's state, not this diff, so it owes no detector here.

## Forward-carry

- Recurring class, a barrier owed: `printf | grep -q` (or any pipe into an early-exit reader) breaks on a precondition, "a producer larger than the pipe buffer feeding an early-exit reader under pipefail, or where SIGPIPE is ignored". It is named in comments at `prepr.sh:216/1881/3664`, `app_push.sh:1088`, `cloud_relay.sh:308`, `seat_venv.sh:254` and `tick_loop.sh:213`, and now in this defect. Control: `git grep -nE '\|[[:space:]]*grep[[:space:]]+-[a-zA-Z]*q' -- tools/pr tools/audit/seat` prints 236 lines at 6858b4abc1. The evidence is `PIPESTATUS=141 0` with the match first among 8001 lines against `0 0` with one line, and `printf: write error: Broken pipe` in CI job 132518925875, where SIGPIPE is ignored. This PR fixes 11 of those lines. The rest are listed as dismissed in the sweep above, and the 151 `bus.sh` self-test rows, the `tick_loop.sh` / `heartbeat.sh` / `seat_venv.sh` self-test rows and `pr_args.sh:457/460` still hold the shape with a narrow window. The barrier is a lint over the pattern, which an owner freeze keeps from being a new instrument group before closure. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
