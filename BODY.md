Triage batch 129 rules on one queue line, P400, `s12-ci-predict-tree-leak`.

**P400: REJECT**, with no carry.

- **Already in the tree:** `ci_predict.py` already removes `hpo-ci-predict-tree-*` in a `try`/`finally` (origin/main `355d9965a`, lines 601 to 624). So do its graders and plant trees.
- **What is left:** a tree survives only when a signal kills the process. A SIGTERM or SIGHUP handler would cover some of those cases. SIGKILL cannot be covered.
- **Measured:** the one tree on the host now is 603M and live, held by `policy_lint_envmatrix.mjs` under a running `ci_predict.py`. The queue line reports two unheld trees from 11-04, about 0.55 GB, which were already removed and are not re-measured. Free disk is 15 GiB.
- **Binding cost:** a fix seat, a review and a change to a hot file (30 commits since 10-24) would save one hand `rm` every few days. That moves no CI time, completion time, right-first-time or tokens.
- **What reopens it:** a measured leak that pushed free disk below the worktree_gc trigger and cost seat time, or a leak rate above one tree a day. In either case the killing signal must be one a handler can catch.

The diff is one file against the merge base: `dev/programme/triage/s6-batch129.md`, the ruling. No product behaviour changes.

## Head

`8ce9788566da0ffb011e5de072db1502fb39d6ec`

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`. `ruling_verdict` reads P400 `REJECT`, and a carry citing it is refused as "not an ACCEPT ruling (REJECT)". With the verdict flipped to ACCEPT, the same carry passes `triage_refusal`.

## Null control

P401 reads `None`, and a carry citing it is refused as "no such entry". With the file absent, the carry is refused as "not on the roster branch or origin/main".

## Figures

- `git diff --stat 355d9965a...8ce9788566da0ffb011e5de072db1502fb39d6ec`: 1 file.
- Every ruling figure is printed by the command the ruling names beside it.
- No capped file is touched.

## Red checks

`none`. The merge base is main `355d9965a`. This head's checks run after its push.

## Forward-carry

none

## Friction

none
