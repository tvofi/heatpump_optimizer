Fix review: blocked 957c9cd08b520fd07a68a648921d44afbcbe270f guard: non-canonical row paths pass; auto-merge not re-pinned to the judged head; post-queue push rides the bot approval

bus-nonce: fc8e03852d77d83d5bccd1059e0f01c3
Round: 1 (first review of #2029).
Measured head: 957c9cd08b520fd07a68a648921d44afbcbe270f (detached worktree /Users/timmalmstrom/hpo-seats/orch-r9c/review-2029). Merge base e7479ad1. Body's `## Head` names the same SHA (step 7 ok).
Evidence dir: /Users/timmalmstrom/hpo-seats/orch-r9c/review-2029-evidence

## Blocking

### B1. The guard passes files at non-canonical paths (a non-row change gets past it)

`ROW_PATH = re.compile(r"^dev/programme/delivery/(\d+)\.md$")` has no `re.ASCII` and uses `$`, and `automerge_refusals` never checks `path == row_path(n)`. Python's `\d` matches any Unicode decimal digit and `int()` accepts them, and `$` matches before a trailing newline. My harness (`path_attack.py`, reviewer-built, not the finder's) feeds one new file holding the exact generated row for #1995, varying only the filename:

```
RESULT 'control canonical path': PASS (not refused)
RESULT 'arabic-indic digits': PASS (not refused)       dev/programme/delivery/١٩٩٥.md
RESULT 'fullwidth digits': PASS (not refused)          dev/programme/delivery/１９９５.md
RESULT 'leading zero': PASS (not refused)              dev/programme/delivery/01995.md
RESULT 'trailing newline in name': PASS (not refused)  "dev/programme/delivery/1995.md\n"
RESULT 'other dir': REFUSED                            (null control: the harness discriminates)
RESULT duplicate row for one PR at two paths: PASS
```

The content stays constrained to the generated line, so the payload is small. But these are files the generator never writes, approved and merged with nobody looking: a newline in a filename breaks every line-oriented tool here (`git ls-files` consumers, `entities.py`, closures), and a second row file for one PR is a record the generator never makes. The body's claim, "every file ... is a **new** `dev/programme/delivery/<N>.md`", is false as measured. Fix: compare `path == row_path(int(m.group(1)))`, or use `\A…\Z` with `[1-9][0-9]*` and `re.ASCII`. Add each case above as a self-test fixture.

### B2. Auto-merge is never re-pinned to the head the guard judged

The step enables auto-merge only `if auto_merge is None`. Nothing disables it except this step's own refusal arm. Take a beat where the hold guard refuses (a required check failed, or a conflict) and the record step then rebuilds and force-pushes a new head. That head passes the guard and gets a new approval, but the auto-merge request from the earlier enable still stands with the **old** `expectedHeadOid`. A writer's push does not disable auto-merge. Either reading of `expectedHeadOid` (schema text: "The expected head OID of the pull request.", saved in `expectedHeadOid-schema.json`) leaves a defect:

- **Enforced at merge time:** the rebuilt head never auto-merges, because the request is pinned to a SHA that is gone. That is the treadmill this PR exists to end.
- **Not enforced:** the pin is decoration. That is B3.

Fix: on every pass, disable and then re-enable with `expectedHeadOid: $HEAD`. That is coherent under both readings.

### B3. A push after queueing merges unattended on the bot's approval

The ruleset `main-protect-checks` (23698884), read today, has `dismiss_stale_reviews_on_push: false` and `require_last_push_approval: false`. The body discloses this exposure as one that "every pull request shares today". That is true of the approval, but not of the merge. Every other PR merges through `merge_train.py --match-head-commit`, which is a head-pinned merge by the orchestrator. This one merges through GitHub's auto-merge with no head check this job can rely on (B2). Any writer can push to `record/autofix` after the queue (the hpo-author App key is the seats' push identity too). That push then rides the hpo-approver review and merges once the required checks go green. The only thing that stops it is a beat on the next main merge, if one happens first.

CODEOWNERS limits this to unowned paths, but those include `custom_components/` (production) and `tools/audit/seat/record_row.py`, the guard itself. A push in that window can therefore weaken the guard for every later beat. The step's final head-moved check covers only pushes during the step.

I judge the body's "I pass it, and I do not rely on it" insufficient for an unattended merge path. Fix before merge, any one of these:
- (a) Run `record_row.py --automerge-check` in a required check on `record/autofix` heads, for example in `pr-contract`: read-only, `GITHUB_TOKEN` suffices. A non-row push then reddens a required check and auto-merge never fires.
- (b) Have the owner set `require_last_push_approval: true`.
- (c) Drop auto-merge. Merge from the beat with `PUT /pulls/N/merge` and `sha=$HEAD` (REST enforces `sha`) once the required checks are green. The nightly beat covers a quiet main.

On a refusal, also dismiss the approver App's earlier reviews. Today the refusal arm only unqueues, so a stale bot approval still satisfies the ruleset for a hand merge of refused content. That makes "keeps the manual review" a convention, not a gate.

## The body's two stated gaps, judged
- `dismiss_stale_reviews_on_push: false`: needs a fix before merge, as B3 above, because this PR adds the first unattended merge that relies on it.
- `expectedHeadOid` semantics: needs a fix before merge, as B2 above. The code as written is wrong under either semantics.

## Verified (non-blocking)

- **Self-test:** `python3 tools/audit/seat/record_row.py --self-test` prints `record_row self-test: all checks passed`, rc 0 (`selftest.out`).
- **Mutations, re-run singly with a byte-identical restore** (`mutations.out`). M1 merged, M4 status, M5b rename, M8 branch and M10 self-row each fail their named check, as the body says. The author tuple fails two checks. The mergeable arm fails `conflicting`.
  - **Survivor:** disabling `automerge_check`'s head-pin (`if head and pr["head"]["sha"] != head`) passes the self-test. The pin that keeps the judged head equal to the approved head has no test. Add a fixture-level test (inject `_api`).
- **Replay #1989–#2002** (`replay.out`), with my own token through `/usr/bin/python3`. The framework python fails TLS locally, which is an environment issue and not the PR's.
  - #1989, #1991, #1992, #1998, #2000, #2001 and #2002 give `AUTOMERGE OK`, rc 0.
  - #1993, #1994, #1995, #1997 and #1999 refuse, rc 1, on branch.
  - `--hold` on #2002 is OK. Reproduced.
  - Note: the non-record refusals are a weak control, because every one refuses on the branch arm alone.
- **`GITHUB_TOKEN` is not used to merge or approve.** The approve uses `$APPROVER` (`pull_requests: write` only) and the enable/disable use the author App token. The job is gated to `github.ref == 'refs/heads/main'` on push/schedule/dispatch, and the `record-writer` environment's deployment policy is `main` only. The guard runs from a `ref: main` checkout, so a PR cannot alter it before it runs.
- **Token scope and revocation:** the approver token is revoked by the automerge step's EXIT trap. Minor: it is minted in the mint step whenever its secrets exist, so on any beat where the automerge step does not run (`nothing-owed`, `skip-*`) it is never revoked and lives up to its 1h expiry. Minting it inside the step that uses it would make the body's "revoked in the step that uses it" hold on every path. Pre-existing: the author token is never revoked.
- **Auto-merge on refusal:** the refusal arm calls `unqueue` (`disablePullRequestAutoMerge`, errors swallowed), and the head-moved arm also unqueues. See B3 for the approval left in place.
- **Unpinned facts:** the guard does not check that a cited PR merged into `main` (`base.ref`), so a row for a PR merged into a side branch regenerates and passes. Minor, but it is not what the generator would write.
  - A symlink whose target is the row text is indistinguishable in `/pulls/N/files`. Low impact.
- **Policy sentence** (`delivery-status-tracking.md`): it is accurate in substance, but "merges unreviewed" is loose, since an App review is posted. "with no review seat" would match the body.
  - Items 4 and 5 were reworded to pay for it with no change to what a seat must do.
  - `policy_lint --budgets`: `.claude/rules/delivery-status-tracking.md` is at 25/26 lines and 603/606 tokens, under its cap with no raise. `rules_sync --check` is ok.
- **Stray old-path row:** none. The three-dot diff `e7479ad1...957c9cd0` touches 7 files, none under `docs/delivery/` or `dev/programme/delivery/`.
- **VERSION, manifest and notes heading:** untouched. CI's `pr-contract` step "no version edit" confirms it.

## CI at 957c9cd0 (check-runs API, `checkruns-final.tsv`)
23 success, 11 skipped, 3 failure, 1 cancelled, and 1 still `in_progress` when posted (`closures`, which is not waited on: no blocker here turns on it).
- `pr-contract` **failure**, required: `[pr-body] check nightly-status is red and ## Red checks does not name it` (job 112941228104, run at 18:11Z). The body was edited at 18:26Z and now names `nightly-status`, but no `pr-contract` re-run exists at this head. The orchestrator must re-run it before any merge.
- `delivery-status` and `nightly-status` are **failure**. They grade main, and the body answers both under `## Red checks`.
- `budget-raise-gate` was **cancelled**. Re-run the cancelled twin, as for any cancelled budget gate.
- All other required checks are success: `fast (3.14)`, `coverage`, CodeQL and the rest. Full list in `checkruns-final.tsv`.
Live head at posting: re-read through the API, and it equals the measured head.
