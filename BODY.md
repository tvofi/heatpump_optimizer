Triage batch 130 rules on one queue line, P401, `s12-update-pr-tools-root`.

**P401: ACCEPT narrowed**, to R10-HANDOFF-PATH.

- **The defect is real:** `pr_tools_fresh` in `pr_args.sh` resolves its directory from `BASH_SOURCE` when it is called. `update_pr.sh` (line 53) and `open_pr.sh` (line 42) have already run `cd "$M"` into the main checkout by then. A relative invocation from a fresh tools worktree therefore measures the main checkout, which is 175 commits behind under the tools directories, and refuses.
- **Reproduced at origin/main `294a880da`:** with a relative `$0` followed by the `cd`, the check refuses. With no `cd`, or with an absolute `$0`, it passes. The dispatch seat's tools worktree is 0 behind, yet its update runs print `NOTICE: STALE CHECKOUT 5a04096d1711`. All 47 of its run scripts set `HPO_ALLOW_STALE_TOOLS=1`, and 77 notices since 11-04 name the main checkout. The guard is effectively off.
- **Narrowed:** the queue line says the check measures the common-dir parent. It already measures the sourced file's own checkout, but it resolves that path too late. The fix resolves the directory once, at source time, which is about 3 lines plus one self-test arm. A probe patch passed the instance and still refused a really stale checkout (the null control).
- **Not the defect:** the 118 refusals that name `orch-wt` or `orch-wt2` were correct firings, and so is the relay, which runs from its levelled tools tree.

The diff is one file against the merge base: `dev/programme/triage/s6-batch130.md`, the ruling. No product behaviour changes.

## Head

`65c333b2f25e03cb0953ec77784cf55933beb9ba`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`. `ruling_verdict` reads P401 `ACCEPT`, and a carry citing it passes `triage_refusal`. With the verdict flipped to REJECT, the same carry is refused as "not an ACCEPT ruling (REJECT)".

## Null control

P402 reads `None`, and a carry citing it is refused as "no such entry". With the file absent, the carry is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 294a880da...65c333b2f25e03cb0953ec77784cf55933beb9ba`: 1 file.
- Every ruling figure is printed by the command the ruling names beside it.
- No capped file is touched.

## Red checks

`none`. The merge base is main `294a880da`. This head's checks run after its push.

## Forward-carry

none

## Friction

none
