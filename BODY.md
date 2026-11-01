Triage batch 105 rules one queue proposal from the orchestrator s10 (2026-11-01T18:19:37Z): `update_pr.sh` refuses STALE CHECKOUT, naming the wrong checkout, when it is invoked by a relative path. It is the rolling batch after batch 104.

- **P362: ACCEPT, as one carry on R10-OPENER-REUSE.**
  - **The defect, read from code.** `update_pr.sh` sources `pr_args.sh` through `$(dirname -- "$0")` (line 23), runs `cd "$M"` into the main checkout (line 42), and only then calls `pr_tools_fresh` (line 51). `pr_tools_fresh` resolves `dirname "${BASH_SOURCE[0]}"` at call time (`pr_args.sh` line 171), so a relative invocation measures the main checkout, not the invoking worktree.
  - **The instance.** The orchestrator s10 hit it on #3047.
  - **The fix.** `pr_args.sh` records its own absolute directory at source time, for `pr_tools_fresh` and `pr_pushers`. Every caller inherits it. The controls are one self-test arm, its null and one mutant.
  - **Why R10-OPENER-REUSE.** It is not started, has no `after`, and owns `update_pr.sh`.
  - **Hot files.** #3055 and #3089 are open on `pr_args.sh` or `update_pr.sh`, so the carry tells the fixer to land after them or rebase over them.

The roster op is queued `#held` and released when this file is on main: one `append-carry R10-OPENER-REUSE`. No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`60958b81b1cbc872141a6e50368af709cebd536b`; the file is the whole diff against `407eb0cb3`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `triage_refusal` passes the carry.
- With P362's verdict flipped to `REJECT`, it is refused: `dev/programme/triage/s6-batch105.md#P362 is not an ACCEPT ruling (REJECT)`.
- On roster branch `9c1bb4673`, `op_append_carry` applies: R10-OPENER-REUSE goes from 6 carries to 7.

## Null control

- With the file absent, the carry is refused: `the triage ruling dev/programme/triage/s6-batch105.md is not on the roster branch or origin/main`.

## Figures

- `node tools/policy/brief_lint.mjs` on the roster after the op: `TOTAL: 0 error(s)`.
- No capped file is touched (`grep -n pr_args tests/*_budgets.json` prints nothing).
- `gh pr list --state open` names #3055 and #3089 as touching `pr_args.sh` or `update_pr.sh`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
