Fix review: merge 7243c07fe53232e96750ec89ff1687753fa50b53
bus-nonce: 16964d236bcbf2aa39bc275c9eaac9c8

# Fix review -- PR #2892, triage batch 43 (P217-P218)

Reviewed head: 7243c07fe53232e96750ec89ff1687753fa50b53, in a detached worktree at that head,
against origin/main. `dev/governance/roles/` has no diff between the merge base and origin/main.

## Results

- Headings: `## P217: ... (V130)` and `## P218: ... (V131)` are in the contract's form and
  are new, since main ends at P211. Each id matches its `Source:` line. `proposals.md` holds
  `## V130` (orchestrator s7, 20:55Z) and `## V131` (21:00Z, owner-directed) with the same
  titles.
- Verdicts, through `roster_edit.ruling_verdict` at the head: P217 REJECT, P218 ACCEPT.
- P218's cost claims hold. `grep -ci draft tools/audit/seat/merge_train.py` prints 0 at
  `e8cb7e683` and 0 at the head, so the train reads no draft flag today. No workflow triggers
  on `ready_for_review`: `ci.yml`'s `pull_request` types are opened, synchronize, reopened,
  edited and labeled. So `gh pr ready` re-runs no check, and "writes no commit and moves no
  head" holds for CI as well (`ev/claims.txt`).
- Destination: R10-TRAIN-UPGRADE is `done` at roster `de410e4c9`, owns `merge_train.py` and
  `train.sh`, holds 1 carry, and has the brief "upgrade tools/audit/seat/merge_train.py so
  that ...". This is as stated.
- Instances: the API's `ready_for_review` events are #2878 at 2026-10-27T20:30:28Z, as cited,
  and #2854 at 20:42:14Z, after a draft from 2026-10-26T06:43:22Z.
- Red checks: at the earlier head `fc6218ad6`, run 40582127206 has `governance / env-matrix`
  (21:07:33Z) and `governance / policy-docs` (21:07:18Z) red. The aggregates `pr-contract` and
  `gate` followed. `## Red checks` names both and answers them: a live ruleset read inside the
  stamp's disable window, with no cheaper detector. The `pr-contract` run at this head
  (job 122567680253) prints `record red-history 6 commit(s) ... governance / env-matrix,
  governance / policy-docs` and passes.
- Live check-runs at the head: 55 runs, 38 success, 17 skipped, 0 failure, 0 pending.
  `git merge-tree --write-tree origin/main <head>` exits 0 (tree `1d6648077`). `VERSION`, the
  manifest and the notes heading are untouched.

## Findings

- F1 (non-blocking): P218's destination R10-TRAIN-UPGRADE is `done`, so the carry is live
  only after the orchestrator reopens it. Two live groups also list `merge_train.py`:
  R10-FLOW-POSTMERGE (`not-started`) and R10-FLY-GH-READ-RETRY (`carries-open`). The ruling
  does not weigh them, or the cost of a third concurrent owner of that file. Neither live
  group's brief is about the merge-step draft check, so the choice is defensible, but the
  ruling should state it. Carry: dismissed: destination choice is defensible; the reopen is the orchestrator's routing step
- F2 (non-blocking): "undrafted 23 s later" needs the train's admission time, which is in an
  out-of-tree log. I verified only the `ready_for_review` stamp. Carry: dismissed: the in-tree and API half verified; the ruling does not turn on the 23 s
