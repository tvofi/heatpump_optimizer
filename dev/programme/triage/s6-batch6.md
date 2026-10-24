# Proposal triage, session s6, batch 6 (P64)

One ruling, S6-V10 of the s6 orchestrator's out-of-tree `proposals.md`, filed
2026-10-24T14:15Z. Numbering continues after `s6-batch5.md` (P63). GitHub calls: 0.

## P64: opener seat's worktree holds the branch update_pr.sh needs (S6-V10)
Verdict: ACCEPT narrowed -> R10-FLY-OPENPR-ATOMIC (owns app_push.sh); carry: app_push.sh detaches the worktree it was given after the PR is open, when that worktree is clean and HEAD equals the pushed sha
Source: s6 proposals.md S6-V10. The proposed `update_pr.sh --free-holders` is rejected.
Instances: 2 (`update_pr.sh` refused #2734 and #2735 with "branch checked out elsewhere" because the triage seat's worktrees held the branches). Orchestrator's account; not re-counted from logs.
Cost: XS -- about 6 lines in app_push.sh plus one self-test arm beside the existing push arms.
Binding: the opener is the only party that knows its worktree is its own, so releasing there removes the class for every opener seat; `update_pr.sh --free-holders` would detach a worktree another seat may be using. Null control: a worktree with an uncommitted file, or with HEAD ahead of the pushed sha, stays on its branch.
