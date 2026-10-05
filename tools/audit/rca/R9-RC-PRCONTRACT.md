# R9-RC-PRCONTRACT: a live head's required `pr-contract` is left red or cancelled

Root-cause seat for roster group **R9-RC-PRCONTRACT**, beside the class, not
inside a fix (`tools/audit/briefs/root-cause.md`, `.claude/rules/defect-root-cause.md`).
No production or workflow file is changed here.

**Trigger.** Recurrence, not a cheaper detector that the gate skipped. `pr-contract`
reddening on a stale `## Head` is the check doing its job. What costs merge time
is that the recovery S10 documents (`edited`) and the concurrency item 3 pin
(`tests/entities.py` "only a pull request's superseded run is cancelled") leave
a required context at the live SHA that is `failure` or `cancelled`. HANDOVER
trap 39 said a third instance of the head-red shape owed this seat; RCA-865
had refused a detector and kept S10.

**Class.** Process friction on `pr-contract`, not a D14 ledger class. Precedents:
RCA-865 (`pr-contract cannot be green at every head`, refused, S10 kept);
RCA-1514 (body edit recreating required contexts; split the workflow out).

Enumerators for every figure below sit in §Figures. Scratch copies of the API
payloads: `/Users/timmalmstrom/hpo-seats/r9-rc-prcontract/`.

## 1. Cause (reproduced)

Three processes sit on top of each other.

1. **S10** (`.claude/skills/steward/SKILL.md`): commit, write the body, push,
   confirm. It assumes one body per push. It documents one expected failed
   `pr-contract` per push, and that an `edited` event re-measures. `tools/audit/push.sh`
   `body-then-push` is that order for a fixer push on an open PR.
2. **`pull_request: [edited]`** on `.github/workflows/pr-contract.yml`: the
   recovery when the body changes without a new commit (or after a foreign
   head move).
3. **Round-9 process review item 3** (`a98d5a05`, 2026-10-01T17:14:01Z):
   `concurrency` on `pr-contract.yml` (same expression as `tests.yml`). Two
   `pull_request` runs of one PR from anyone except `github-actions[bot]` share
   a group and cancel. The pin in `tests/entities.py` asserts that for
   `hpo-author[bot]` too. The comments say "superseded"; the expression keys on
   PR number, not SHA.

GitHub required checks then read every `pr-contract` check-run at the head SHA,
including a cancelled twin.

The brief's candidate cause "GITHUB_TOKEN / `github-actions[bot]` pushes cancel
superseded in-flight runs" is **false for this workflow**. The concurrency
expression sets `cancel-in-progress` false and a unique group when
`sender.login == github-actions[bot]`. The cancelled runs below are
`hpo-author[bot]`.

### Instance (1): #1959 carry / head-move — `edited` recovered

PR #1959, branch `fix/r9-diag-1f-pr`, merged 2026-10-05T16:39:39Z.

Two owner `synchronize` runs failed `Check the body against the contract` with
``## Head` does not name <live sha>``:

| run | head | created | actor | conclusion |
|---|---|---|---|---|
| 37315318058 | `093776f823` | 13:14:50Z | tvofi | failure |
| 37322736729 | `68410b6708` | 14:11:42Z | tvofi | failure |

GraphQL `userContentEdits` on #1959: hpo-author re-bodied at 13:21:03Z and
14:14:40Z. Matching `edited` runs, both `hpo-author[bot]`, both success on
attempt 1: 37316119261 at 13:21:08Z (`093776f823`); 37323213533 at 14:15:16Z
(`68410b6708`, the 14:15Z green the brief named).

Stalls: 6 min 18 s and 3 min 34 s. No manual re-run. This is S10's recovery
working for an orchestrator head move.

### Instance (2)+(3): #1969 — cancelled twin, stale body, `edited` cancelled

PR #1969, branch `record/autofix` (reused after #1968), merged 2026-10-05T14:31:00Z.
One commit: `343021aa0f` at 13:18:07Z. PR created 12:35:46Z — **42 min 21 s
before that commit**. GraphQL: body at create 12:35:46Z, next edit 14:23:21Z
(hpo-author).

`pr-contract` at `343021aa0f`:

| run | created | att | triggering_actor | conclusion | notes |
|---|---|---|---|---|---|
| 37315758146 | 13:18:18Z | 1 | hpo-author[bot] | cancelled | completed 13:18:20Z; never re-run |
| 37315758446 | 13:18:18Z | 1 | hpo-author[bot] | failure | ``## Head` does not name 343021a``; red list empty |
| same | 13:18:43Z | 2 | github-actions[bot] | failure | `pr-contract-rerun.yml` / `contract_rerun.py` |
| same | 13:34:44Z | 3 | github-actions[bot] | failure | same, body still stale |
| same | 14:24:27Z | 4 | tvofi | success | manual re-run after 14:23:21Z re-body |
| 37324419853 | 14:24:15Z | 1 | hpo-author[bot] | cancelled | the `edited` event; cancelled 14:24:37Z by att 4's group |
| same | 14:29:29Z | 2 | github-actions[bot] | success | contract rerun of the cancelled edited run |

`GET /commits/343021aa0f/check-runs` after merge still lists three `pr-contract`
check-runs: cancelled 111781963180, success 111811535607, success 111813793964.

The GitHub merge-refusal string the brief quoted (`Required status check
pr-contract is cancelled`) is not stored on the PR after merge; the residue
that string describes is the cancelled check-run that remains at the SHA.

**Null control: #1968**, same branch name, same record-beat lane, merged
12:35:12Z. Commit `b67965b425` at 10:28:41Z, PR created 10:28:44Z (commit
then open). `lastEditedAt` null. One `pr-contract` run, 37296836218, success
on attempt 1. No cancelled twin, no stall.

So #1968 is not an instance of the class. The resume's "three instances are
PRs #1968/#1969 merges and #1959 carries" over-counts #1968. The three
measured phenomena are two #1959 recoveries (class of stale `## Head` after
a foreign push, recovered) and #1969 (stale `## Head` because the body
predated the commit, plus a cancelled required check, plus the `edited` run
cancelled by a sibling in the same concurrency group).

## 2. Process state: **(c)** — followed, and it did not produce the intended result

Quoted processes, all present and obeyed:

- **S10** on #1959: the App re-bodied after the head move; `edited` re-measured.
  On #1969 the record beat opened the PR 42 min before the commit, which is
  the `push-then-create` / S10 order inverted, but that is one lane's use of
  a reused branch, not the class: #1968 in the same lane followed commit-then-open
  and was clean. A firmer S10 instruction would not have saved #1959 (S10 was
  followed) and would not have saved #1969's cancelled `edited` (the body edit
  did fire).
- **Item 3 / the pin.** Two `hpo-author[bot]` `pull_request` events at one SHA
  share a group and cancel. Measured: #1969's two runs created in the same
  second; one cancelled in 2 s. The pin's comment says "superseded"; its
  assertion is "two PR runs by hpo-author share a group". Same-head twins
  (open+synchronize, synchronize+edited, edited+manual rerun) are in the unit.
- **`pr-contract-rerun.yml`.** Followed: it re-ran 37315758446 at 13:18:43Z and
  13:34:44Z. The body still did not name `343021a`, so both attempts failed.
  The rerunner is for a red *other* workflow that the contract listed too
  early (D13-s1-03). It cannot repair a stale `## Head`.

Not (a): S10, `edited`, item 3, and `contract_rerun.py` all exist.
Not (b): the #1959 seats re-bodied; the pin is what CI enforces; the rerunner
fired.
Not (d) as the primary letter: GitHub treating a cancelled required check as
non-success is the environment item 3 assumed away by claiming only superseded
heads are cancelled. The process was followed and its unit was wider than
"superseded". That is (c).

## 3. Class reach

Enumerator A (capped at 1000 runs): `pr-contract.yml` runs with
`created>=2026-09-20` returned 1000 rows (2026-09-27 through 2026-10-05).
Conclusions: success 611, cancelled 231, failure 158. Unique head SHAs: 536.
SHAs with a cancelled run **and** at least one other `pr-contract` run at the
same SHA: **217**.

Enumerator B (the brief's day): `created>=2026-10-04` yielded 124 runs, 51 of
them on 2026-10-05 (success 19, cancelled 19, failure 13) across 28 SHAs.
Same-head cancelled+other on that day: **17 of 28 SHAs**. Zero SHAs that day
were cancelled-only (true supersede-and-drop would look like that; it did
not appear in this slice).

Every future carry merge (#1959 shape) and every App double-event at one SHA
(open+push, push+edit, edit+rerun) is in the 217. Most twins pair cancelled
with a later success and never stall a merge. The costly subset is: stale
`## Head` until a body edit, or the latest required check-run concluding
`cancelled`.

`contract_rerun.py` does not watch `PR contract` itself (loop guard) and does
not trigger on `edited`. It cannot be the recovery for this class; on #1969
it spent two attempts on a body it could not fix.

## 4. Cost test

Unit: wall-clock over a release cycle, as `defect-root-cause.md` requires.

**cost(defect) × P(recurrence), measured this window.**

- #1969, first `pr-contract` at the live head 13:18:18Z to merge 14:31:00Z:
  **73 min** of merge blocked on a one-line record PR. Of that, 65 min until
  the 14:23:21Z re-body, then 6 min of cancel/rerun after `edited`.
- #1959 recovered stalls: **6 min 18 s** and **3 min 34 s**. No merge refusal.
- P(same-head cancelled twin): 17/28 SHAs on 2026-10-05; 217/536 in the 1000-run
  cap. P(costly stall) is lower: two PRs on that day (#1959 recovered in
  minutes, #1969 lost 73 min). Record beats and carry merges continue every
  merge; one 73 min event per busy day is the measured lower bound, not a
  guess.

**cost(countermeasure, recurring).**

Candidate A — drop `cancel-in-progress` on `pr-contract.yml` only, leave
`tests.yml`. The job's measured wall is 15–21 s (37323213533 14:15:20Z–14:15:41Z;
37315758446 att 4 14:24:40Z–14:24:55Z). 231 cancelled runs in the 1000-run cap
would have completed: about **4 600 s** of extra runner time across those
eight days, unattended. Orchestrator minutes are the scarce unit; runner
seconds are not.

Candidate B — an `edited`-triggered rerunner on the pattern of
`budget-raise-gate-rerun.yml` for the newest red `pr-contract` at the same
head. #1959 already got a new run from `edited` (no rerunner needed). #1969's
`edited` run 37324419853 *was* created and was cancelled by the same
concurrency group as the manual re-run. A second workflow posting another
`pull_request`-grouped job would be cancelled the same way. Recurring cost:
another workflow_run job per body edit, and it does not address the cancelled
required context.

Candidate C — extend the `github-actions[bot]` exemption to `hpo-author[bot]`
on `pr-contract.yml` (unique `run_id` groups). Same effect as A for App
events; would also stop cancelling a truly superseded *previous SHA*'s
in-flight 20 s job, which is the extra runner cost already priced under A.
It would **not** stop a human (`tvofi`) re-run cancelling an in-flight
`edited` run: #1969 att 4's triggering_actor was `tvofi`. A is strictly
wider and is the one that covers that pair.

**Verdict.** A passes: ~20 s extra per superseded push, against 73 min
measured on one record PR and 217 same-head twins in the capped window. B
fails the test (does not close the measured #1969 arm; adds a job). C is A
with a hole for human re-runs.

This is not an audit class in `bugclasses.json`, so the three-in-a-round
barrier obligation does not mint a D14 id. The cost test still picks a
countermeasure.

## 5. Countermeasure (proposed, not landed)

**Addressing state (c): shrink item 3's unit on this required short job.**

On `.github/workflows/pr-contract.yml` only: `cancel-in-progress: false` (or
a unique `run_id` group for every event). Keep `tests.yml` as it is — that
is the forty-minute runner item 3 actually saves.

The `tests/entities.py` pin that currently requires `hpo-author[bot]`
`pull_request` runs of *every* `on: pull_request` workflow to share a group
and cancel must then treat `pr-contract.yml` as the exception the comments
already claimed ("superseded", not "same head"). That pin and the workflow
are owner paths (`.github/workflows/` in CODEOWNERS). **Owner approval
before landing.** State (c), not a policy rewrite of S10.

**Refused:** candidate B (edited rerunner). The `edited` event already
creates the run; concurrency cancelled it; a rerunner inherits the group.

**Refused:** a firmer S10. That is the (b)-shaped instruction
`comment-readback.md` measured at 0 of 3. #1959 followed S10's recovery.
#1968 shows the record lane already has a clean order (commit then open).

**Not a check.** No fail-then-pass detector demonstration is owed for
turning cancel off. The demonstration a later fixer owes is: two
`hpo-author` `pull_request` events at one SHA both conclude `success` or
`failure`, never `cancelled`; a `tests.yml` superseded push still cancels.

Residual: a *later* `failure` at the same SHA still supersedes an earlier
`success` in GitHub's required-check listing. That is RCA-865's remaining
shape (push then edit with S10 inverted). S10 and `body-then-push` remain
the authoring order. This countermeasure does not claim to make every head
green; it claims to stop writing a cancelled required context at a live SHA
and to stop cancelling the `edited` recovery.

## Figures

Commands that printed the figures. Re-run against `tvofi/heatpump_optimizer`.

```
# 1959 / 1968 / 1969 metadata
gh api repos/tvofi/heatpump_optimizer/pulls/1959 --jq '{created_at,merged_at,head:.head.sha}'
gh api repos/tvofi/heatpump_optimizer/pulls/1968 --jq '{created_at,merged_at,head:.head.sha}'
gh api repos/tvofi/heatpump_optimizer/pulls/1969 --jq '{created_at,merged_at,head:.head.sha}'

# commits (1968/1969 each one; dates vs created_at)
gh api repos/tvofi/heatpump_optimizer/pulls/1969/commits --jq '.[]|{sha,date:.commit.committer.date}'

# pr-contract runs since 2026-10-04 (124; 51 on 2026-10-05)
gh api --paginate --jq '.workflow_runs[]|{id,conclusion,head_sha,head_branch,created_at,run_attempt,actor:.actor.login,triggering_actor:.triggering_actor.login}' \
  'repos/tvofi/heatpump_optimizer/actions/workflows/pr-contract.yml/runs?per_page=100&created=>=2026-10-04T00:00:00Z'

# same listing created>=2026-09-20 is capped at 1000 (this seat: 1000 rows,
# 2026-09-27..2026-10-05, cancelled 231, same-head cancelled+other SHAs 217)

# #1969 attempts
gh api repos/tvofi/heatpump_optimizer/actions/runs/37315758446/attempts/{1,2,3,4} --jq '{run_attempt,conclusion,run_started_at,trig:.triggering_actor.login}'
gh api repos/tvofi/heatpump_optimizer/actions/runs/37324419853/attempts/{1,2} --jq '{run_attempt,conclusion,run_started_at,trig:.triggering_actor.login}'

# check-runs remaining at the merged #1969 head
gh api --paginate --jq '.check_runs[]|select(.name=="pr-contract")|{id,conclusion,completed_at}' \
  repos/tvofi/heatpump_optimizer/commits/343021aa0fa77234d17653a3075f2224aaf1a17f/check-runs

# body edits
gh api graphql -f query='{ repository(owner:"tvofi", name:"heatpump_optimizer") { pullRequest(number:1969) { lastEditedAt userContentEdits(first:20) { nodes { editedAt editor { login } } } } } }'
```

Attempt 1 log of 37315758446, and the two #1959 failure logs, each contain the
``## Head` does not name …`` line quoted above (`gh run view <id> --log-failed`).
