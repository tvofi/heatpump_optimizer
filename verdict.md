Fix review: blocked e7baa92c83476e30c825843921904c8b83f301ef ruling-unsound: the accepted carry detaches the worktree after the PR-opening push, which makes open_pr.sh's row push in that same worktree refuse

bus-nonce: 676d5732851a037579944da2baf325f9

Round: 1. Reviewed head `e7baa92c83476e30c825843921904c8b83f301ef` (PR #2738, `triage/s6-batch6`), merge base `e97f5749b441b282e43bd99dbcbb762e9d10a369`, contract `dev/governance/roles/fix-review.md` and `proposal-triage.md` read from origin/main.

## Block

- **The ACCEPT's carry is unsound as worded.** P64's carry: "app_push.sh detaches the worktree it was given after the PR is open, when that worktree is clean and HEAD equals the pushed sha". `tools/audit/seat/open_pr.sh`, owned by the same group R10-FLY-OPENPR-ATOMIC, calls `app_push.sh $R $WT $BR` (line 58, `p1`) and that call opens the PR (`app_push.sh` POSTs `/pulls` at line 535). Right after that push the worktree is clean and HEAD equals the pushed sha, so the carry detaches it. open_pr.sh then runs `commit_row .` in that same `$WT` (line 62), which commits onto a detached HEAD, and calls `app_push.sh` again on the same `$WT $BR` (line 71, `p2`). `app_push.sh` lines 481-484 refuse whenever HEAD is not `refs/heads/$br`: "worktree HEAD ... is not the committed tip". Built as written, the carry makes every open_pr.sh open lose its delivery-row push, which is the #2390/#2391 failure that `update_pr.sh`'s header documents. `ev/carry_trace.txt` has the lines and `ev/detach_demo.txt` reproduces the HEAD≠tip state. The ruling's null control (dirty, or HEAD ahead) does not catch this case, because at p1 the worktree is clean and level. Fix: state when the detach happens. It should come after the opener's last push (for open_pr.sh, after p2, or done by open_pr.sh itself), or only for a worktree that no later step reuses.
- **Instances are carried, not cited.** `proposal-triage.md` says: "`Instances:` (each counted instance with the command or log reference beside its figure: cite it, don't carry it)". P64 gives "Instances: 2 ... Orchestrator's account; not re-counted from logs." It names #2734 and #2735 but no log or command reference for either refusal. The refusal text the ruling quotes is `update_pr.sh`'s own (line 50: "branch $BR checked out elsewhere"), so the mechanism is real, but no reference is given for the count.

## Findings

- The ruling does not mention that `update_pr.sh` lines 45-48 already free holders: they detach any clean worktree whose HEAD origin already contains, if it sits under `$HPO_STATE_DIR/pr/`. open_pr.sh's own `$WT` (`$D/wt`, line 29) is under that prefix, so open_pr.sh opens already avoid this class. The two instances come from worktrees outside the prefix (the triage seat's). So the class is narrower than "every opener seat", as the Binding says. Also, the rejected `--free-holders` is an extension of a mechanism the tree already has, not a new risk, so the Binding's case for rejecting it should be argued against that existing sweep (scoped by prefix, clean, origin-contained). The re-cut should name this, and the fixer should say which openers the app_push.sh change still covers. Carry: R10-FLY-OPENPR-ATOMIC

## Evidence

- Merge: `git merge-tree --write-tree origin/main <head>` exits 0, tree `1de008063629ea3fadb20010c0e0ddd4cdce58b5`, no conflict (`ev/merge_tree.txt`).
- CI at this head: 6 check runs (prelude, cancel-superseded, refresh, two of each), all `queued` at review time and none concluded, so there is no red check to answer yet. The body's `## Red checks: none` cannot be confirmed or refuted at this head.
- Figure: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' ...` prints `1 ACCEPT`, which matches the body (`ev/figures.txt`).
- Null control re-run: `roster_edit.ruling_verdict` gives `ACCEPT` for P64 and `None` for P99, which matches the body (`ev/ruling_verdict.txt`).
- Mutation proof: n/a. The diff adds only a ruling record and a delivery row, no production or check line, so no mutant is drawn.
- `VERSION`, the manifest and the `RELEASE_NOTES.md` heading are untouched (the three-dot diff over them is empty). The body's head SHA matches the reviewed head.
- Policy scope: the brief marked this as a policy change. The diff touches only `dev/programme/triage/` and `dev/programme/delivery/`, which are records, not part of the policy set CLAUDE.md names, so there is no policy sentence to check against the owner's wording.
- Numbering: P63 is in `s6-batch5.md` on `triage/s6-batch5` (`5a03e901b`), which is not merged at this base. P64 continues from it correctly.
