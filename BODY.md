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
- `ci-watch.sh`, `open_pr.sh`, `update_pr.sh`: no pipefail, so grep's status wins.
- `heartbeat.sh`, `seat_venv.sh`: self-test `$out` of a few lines.
- `app_push.sh:930/945`: one `ps` character.
- `prepr.sh:3198/3200`: the match is the last trailer line, so no early exit.
- `push.sh:170/206`: the `## Head` section of a body.

Leaves #3394 open.

## Head

cb803e9eedff0a2ea947110e1321cdd6afe0b1d6

## Mutation proof

Each mutant is a copy of `app_approve.sh` with one old line restored, run with `--self-test`:
- carry line restored (`printf '%s\n' "$heads" | grep -q ...`): `FAIL CARRY on a head of ours listed first among 20001 branch heads of origin (got '1', want '0')`, `app_approve self-test: 353 checks, 1 failed`.
- gh_transient line restored: `FAIL gh_transient: an early transient line in a long stderr is still transient (got '1', want '0')` and `FAIL (and with SIGPIPE ignored, as in CI, it prints nothing and still classifies transient) (got '...: line 160: printf: write error: Broken pipe ...`, `353 checks, 2 failed`. The second FAIL reproduces the CI flake's message class.

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

## Forward-carry

- Recurring class, a barrier owed: `printf | grep -q` (or any pipe into an early-exit reader) breaks on a precondition, "a producer larger than the pipe buffer feeding an early-exit reader under pipefail, or where SIGPIPE is ignored". It is named in comments at `prepr.sh:216/1881/3664`, `app_push.sh:1088`, `cloud_relay.sh:308`, `seat_venv.sh:254` and `tick_loop.sh:213`, and now in this defect. Control: `git grep -nE '\|[[:space:]]*grep[[:space:]]+-[a-zA-Z]*q' -- tools/pr tools/audit/seat` prints 236 lines at 6858b4abc1. The evidence is `PIPESTATUS=141 0` with the match first among 8001 lines against `0 0` with one line, and `printf: write error: Broken pipe` in CI job 132518925875, where SIGPIPE is ignored. This PR fixes 11 of those lines. The rest are listed as dismissed in the sweep above, and the 151 `bus.sh` self-test rows, the `tick_loop.sh` / `heartbeat.sh` / `seat_venv.sh` self-test rows and `pr_args.sh:457/460` still hold the shape with a narrow window. The barrier is a lint over the pattern, which an owner freeze keeps from being a new instrument group before closure. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
