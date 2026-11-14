# Proposal triage, session s14, batch 186 (P608)

The bar and the denominators are batch 141's.

Sources:
- origin/main `cbd23f1c8b`. Every line number below is at that commit.
- The roster at `origin/handoff/audit-r10-roster`, read at 11:10Z.
- The live train log (`merge_train` state directory, `train.log`).
- GitHub, read at 11:10Z:
  - `gh pr view <n> --json statusCheckRollup,mergeStateStatus` for #3445, #3405 and #3398;
  - ruleset 23698884 (`main-protect-checks`).

## P608: TRAIN-POLICY-REASON-STALE-CONTEXT

Verdict: ACCEPT, narrowed to the misread that both queue lines share. The narrowed arm makes
`policy_refusal` read each required context's newest rollup entry, not the last one listed. It goes
as a carry on R10-TRAIN-RESIDUE-P2, which is not-started, has no `*train-residue-p2*` ref, and owns
`merge_train.py`.

REJECTED:
- **(b), undraft on every route.** The draft flag is not the cause:
  - #3398 was undrafted (`UNDRAFT #3398 141f8af1b1a5` in `train.log`), and it was still refused
    with the same text.
  - #3445 is still BLOCKED after `gh pr ready`.
- **Reading `isDraft` in the reason.** A draft reports `mergeStateStatus` DRAFT, not the BLOCKED
  that all three instances logged.
- **(a) as worded, a CodeQL re-run as the blocker.** `codeql / Analyze (python)` is not a required
  context: the ruleset's required list is `["gate"]`, strict false. The newest-entry rule below
  still covers a re-run of any required context in progress over an older success.

Source: queue lines 286 and 287, 2026-11-11T10:54:06Z and 10:54:22Z, orchestrator s14.

Instances:
- **The reason text in all three instances.** Command:
  `grep -E '#(3445|3405|3398)' train.log | grep 'policy refusal'`.
  - Result: all three read `mergeStateStatus BLOCKED, reviewDecision APPROVED: every required
    context is green, so the missing requirement is a review at <head>`.
  - If draft were the cause, the state would read DRAFT, or #3398 would carry no UNDRAFT line.
- **The cause, at #3445's head `7fb8680c85`.** Command:
  `gh pr view 3445 --json statusCheckRollup`, the `gate` entries in list order.

  | index | conclusion | completed |
  |---|---|---|
  | 88 | FAILURE | 09:29:08Z |
  | 89 | FAILURE | 09:24:57Z |
  | 90 | FAILURE | 09:22:49Z |
  | 91 | FAILURE | 09:29:14Z (the newest) |
  | 92 | SUCCESS | 09:23:45Z |

  - The newest `gate` is red, so GitHub blocks the merge.
  - `policy_refusal` (`:2792-2834`) builds `last[name] = conclusion` in list order. It keeps entry
    92, the older SUCCESS. It then reads every required context as green and blames a review.
  - If the claim were false, the last-listed `gate` entry would also be the newest, or would be
    red.
- **The train attempted #3445 unproved.** `#3445 D: a batch of one merges at its verdicted head,
  unproved`. Under `--overlap`, main itself was red on `gate` right before. So nothing upstream of
  the attempt read the PR's own red `gate`, and the policy read was the only diagnosis.
- **#3405 and #3398.** Both are merged, and their rollups now show only SUCCESS `gate` entries. The
  refusal-time state cannot be re-read, so they are counted as the same text, not as the same
  proven cause.
- **What each instance cost.** A wrong park reason led to a re-add, a batch, and an orchestrator
  diagnosis (lines 286 and 287 themselves). The correct reason, "gate red at 7fb8680c", sends the
  orchestrator straight to a re-run.

Cost:
- About 10-15 lines in one method of `tools/audit/seat/merge_train.py`, and one self-test fixture.
- No new file, check or API call: the same `gh pr view` read.
- `merge_train.py` is not in `tests/structure_budgets.json`.

Binding: this repairs a misdiagnosis in existing machinery, not new machinery. The benefit clearly
outweighs the cost: three instances in one session, each a lost batch slot plus a manual
diagnosis, against a one-method change.

### Card (carry on R10-TRAIN-RESIDUE-P2)

**`tools/audit/seat/merge_train.py` `policy_refusal` (`:2792-2834`).**

- **The newest-entry rule.** Reduce `statusCheckRollup` to one entry per context name, chosen by
  newest `completedAt`, else `startedAt`. Any entry still QUEUED, IN_PROGRESS or PENDING makes the
  context pending, so the method returns `wait`. Never use list order.
- **Context names.** Keep the existing name/context key, and key the duplicates the same way.
- **The reason text.**
  - A newest-red required context is reported as `required context(s) red at <h>: gate`.
  - A context that is only an older success under a newer failure must never read as "green".

**Self-test fixture.** It is the five #3445 `gate` entries above, frozen.
- **In list order:** the method returns red `gate`, with wait false and approval false.
- **Reversed:** the result is the same.
- **[SUCCESS 09:00, IN_PROGRESS started 10:29]:** the method waits.
- **Null control:** five SUCCESS entries in any order still reach the review branch, as today.
- **Mutation proof:** restoring the last-listed-wins dict fails the list-order case.
