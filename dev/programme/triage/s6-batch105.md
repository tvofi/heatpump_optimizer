# Proposal triage, session s10, batch 105 (P362)

The rolling batch after batch 104. Facts were read at origin/main `407eb0cb3`, at the round's
roster branch `origin/handoff/audit-r10-roster` (`9c1bb4673`), and in the session's seat ledger.

## P362: `pr_tools_fresh` resolves its directory after `update_pr.sh` has changed directory

Verdict: ACCEPT, as one carry on R10-OPENER-REUSE. The fix goes in `pr_args.sh` itself, not in
`update_pr.sh`.

Source: the orchestrator s10's queue line of 2026-11-01T18:19:37Z, and its ledger line of the same
time: "update_pr refuses STALE CHECKOUT when invoked by a relative path ... Workaround: call by
absolute path."

Instances:
- **The defect, read from code at `407eb0cb3`.**
  - `tools/audit/seat/update_pr.sh` line 23 sources `pr_args.sh` as `. "$(dirname -- "$0")/pr_args.sh"`.
    Invoked as `bash tools/audit/seat/update_pr.sh`, that makes `BASH_SOURCE[0]` inside
    `pr_args.sh` the relative path `tools/audit/seat/pr_args.sh`.
  - Line 42 then runs `cd "$M"`, where `M` is the repository's main checkout (line 32,
    `--git-common-dir`).
  - Line 51 calls `pr_tools_fresh`. `tools/audit/seat/pr_args.sh` line 171 resolves
    `d=$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)` at call time, so `d` is the main
    checkout's `tools/audit/seat`. Its HEAD is what gets counted against origin/main, not the
    invoking worktree's.
  - So a seat calling from an up-to-date worktree by a relative path is refused whenever the main
    checkout lags. The orchestrator s10 hit exactly that on #3047 (ledger, 18:19:37Z).
- **The other callers.** `open_pr.sh` calls `pr_tools_fresh` at line 93, before its only
  `cd $WT` (line 99), so it reads the right checkout today. `pr_pushers` (line 371) resolves its
  default root the same call-time way, so it shares the hazard for any caller that changes
  directory first.
- **Not the earlier STALE refusals.** P283 (2026-10-29, seat ledger) found 41 recorded STALE CHECKOUT
  refusals, each naming a checkout that really was stale. This is a different mechanism: a
  refusal that names the wrong checkout.
- **Measured instances: 1.** A known workaround exists: invoke by absolute path.

Cost:
- **Size.** About 3 lines in `tools/audit/seat/pr_args.sh`: one source-time variable, read by
  `pr_tools_fresh` and `pr_pushers`. Plus one self-test arm, its null and one mutant inside the
  existing `fresh()` arms. No new file and no new check.
- **Capped files.** `grep -n pr_args tests/*_budgets.json` prints nothing, so no capped file is
  touched.
- **Hot files.** `pr_args.sh` and `update_pr.sh` are both `HOT_FILES` in `review_packet.py`.
  `gh pr list --state open` names #3055 and #3089 as open on one of them, so the carry tells the
  fixer to land after them or rebase over them.
- **No new group.** R10-OPENER-REUSE is not started, has no `after`, and owns `update_pr.sh`, the
  caller that trips the defect.

Binding:
- **Why it clears the bar.** A false refusal sends a seat to "update the checkout" when its own
  checkout is current, and every seat that calls by relative path can hit it. The fix is a few
  lines in one place, it is the architecturally sound form (the sourcing file owns its own
  directory), and it is pinned by a mutant.
- **Rejected route.** Patching `update_pr.sh` to pass an absolute path leaves `pr_pushers` and
  every future caller exposed.
- **Why R10-OPENER-REUSE over R10-RELAY-HANDOFF-ARM.** R10-RELAY-HANDOFF-ARM runs after
  R10-FLY-RELAY-REVIEW-FF, which is still carries-open. R10-OPENER-REUSE can be dispatched now.

Carry (R10-OPENER-REUSE, `s7/carries/b105-P362.txt`):

> From triage P362 (orchestrator s10, 2026-11-01T18:19:37Z: a false STALE CHECKOUT refusal on
> #3047). tools/audit/seat/pr_args.sh `pr_tools_fresh` resolves its tools directory as
> `cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd` when it is called, not when it is sourced.
> tools/audit/seat/update_pr.sh sources pr_args.sh through `$(dirname -- "$0")`, then runs
> `cd "$M"` (the main checkout) before it calls `pr_tools_fresh`. So a relative invocation
> (`bash tools/audit/seat/update_pr.sh ...` from a fresh worktree) checks the main checkout's
> freshness and refuses STALE CHECKOUT, whatever the invoking worktree holds. Change: pr_args.sh
> records its own absolute directory once, at source time (one variable beside PR_FRESH_PATHS),
> and every function that reads `BASH_SOURCE[0]` for its directory (`pr_tools_fresh`,
> `pr_pushers`' default root) uses it. The fix sits in pr_args.sh, not in each caller, so
> open_pr.sh, handoff_push.sh and cloud_relay.sh inherit it. Controls, in pr_args.sh's self-test
> (the `fresh()` arms): a fresh clone sourcing pr_args.sh by a relative path, then cd'ing into a
> stale sibling checkout, passes; null control: the same clone made stale still refuses STALE
> CHECKOUT; one mutant that restores the call-time resolution leaves the first arm red. Land it
> after #3055 and #3089 (both open on pr_args.sh or update_pr.sh), or rebase over them.
> triage: dev/programme/triage/s6-batch105.md#P362

Roster op (queued `#held` until this file is on origin/main):
1. `append-carry R10-OPENER-REUSE @.../s7/carries/b105-P362.txt`

Rule run on the instance: under the carry, the #3047 call (`bash tools/audit/seat/update_pr.sh`
from a current worktree, main checkout behind) resolves `d` to the invoking worktree's
`tools/audit/seat` at source time, before line 42's `cd`. So it counts 0 commits and passes. Its
null still refuses, because a really stale invoking checkout counts more than 0.
