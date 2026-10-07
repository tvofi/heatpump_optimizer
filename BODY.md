The `record-autofix` beat's record pull request (branch `record/autofix`, for example #2002) only adds rows under `dev/programme/delivery/`. The job rebuilt that branch on every main merge, so each human or seat review went stale before approval. The pull request never merged, and `delivery-status` stayed OVERDUE on main. This change makes a row-only record pull request merge with no review seat, behind a guard that refuses anything else. It is the owner's "option 1" (tvofi, 2026-10-07).

**The guard.** `tools/audit/seat/record_row.py --automerge-check --pr N [--head SHA] [--hold]` runs `automerge_refusals`, which is a pure function the self-test drives from fixtures. Every condition below must hold:

- The author is `hpo-author[bot]`, type `Bot`, id `331381602`. The id is pinned the way `app_approve.sh` pins the approver's.
- The pull request goes from `record/autofix` to `main` within one repository.
- Every file in the three-dot diff (`/pulls/N/files`) is a **new** `dev/programme/delivery/<N>.md`, with no rename, exactly one added line and no removed or context line.
- That line anchors `<N>` through `delivery_status.anchored`, which is the row parser this guard reuses.
- The line is **byte-equal to what `row_line` writes from the API's own facts for `<N>`**. Those facts are `merged: true`, its `merge_commit_sha` and its title, plus an optional roster suffix. For the pull request's own number, the line must instead equal the `open_row_line` self-row.
- The guard never parses the row back. It regenerates the row and compares, so there is no second row grammar.
- `mergeable` is not false.
- With `--hold`, no **required** context (read from `/rules/branches/main`) has failed at the head. A red that is not required, such as `delivery-status` or `nightly-status`, holds nothing up.

**The mechanism (CI, no session).** The `record-autofix` job in `.github/workflows/tests.yml` changes in three places:

1. **Hold.** If an open record pull request passes `--automerge-check --hold` at its live head, the beat leaves it alone (status `held`) instead of rebuilding it. Rebuilding on every merge was the treadmill. The merge of the held pull request fires the next beat, and that beat rows whatever landed in between. If the guard refuses, or a required check fails, the beat rebuilds as before.
2. **Approve and queue** (a new step, after open/update). The guard runs at the live head.
   - On a pass, the **hpo-approver App** posts one `APPROVE` review with `commit_id` set to that head. It skips this if it already approved that head.
   - The **hpo-author App** then enables auto-merge (GraphQL, `mergeMethod: MERGE`, `expectedHeadOid` set to the head).
   - If the head moved during the step, auto-merge is disabled again.
   - On a refusal, auto-merge is disabled and the pull request keeps the manual review.
   - Every outcome of this step is green and is printed as `AUTOMERGE: <status>`. The existing report step still reddens when a beat was owed and did not land.
3. **Minting.** The mint step now has one `mint` routine. It mints the author token as before, and the approver token only when `HPO_APPROVER_PEM` and `HPO_APPROVER_APPID` exist in the main-only `record-writer` environment. The approver token carries `pull_requests: write` only and is revoked on exit from the step that uses it.

**Why this mechanism.** I measured the alternatives on 2026-10-07:

- **No new secrets: approve as `github-actions[bot]`.** `can_approve_pull_request_reviews` is already `true`, so this would work. It adds a third approving identity that decision 0011 does not name, and it needs a fifth job-level `permissions:` override against the four-jobs floor pin. Rejected.
- **Merge as `hpo-ledger` (5094721).** It is an `always` bypass actor on `main-protect-checks`, so it could merge directly. That would skip the required checks, and it would spend a bypass granted for ledger pushes. Rejected.
- **An instrument the orchestrator's reconcile calls with `~/.zcode/identity-approver.*`.** This works today, but it needs a live session. That is exactly what the brief asked to avoid.
- **The chosen identity pair.** The approver stays the App that decision 0011 names. The merge is the author App's, because auto-merge merges as the identity that enabled it, so the merge push fires main's workflows. A `GITHUB_TOKEN` merge would not fire them. That push is what clears `record`.

**Ruleset and CODEOWNERS (read 2026-10-07).**

- `main-protect-checks` (23698884) requires 1 approving review with `require_code_owner_review`, `dismiss_stale_reviews_on_push: false` and `strict_required_status_checks_policy: false`.
- `.github/CODEOWNERS` owns nothing under `dev/programme/delivery/`, so no CODEOWNERS change is needed. The approver App's review satisfies the rule.
- `allow_auto_merge` is `true` on the repository.

**Owner action before it takes effect.** Add `HPO_APPROVER_PEM` and `HPO_APPROVER_APPID` (the values of `~/.zcode/identity-approver.pem` and `.appid`) to the `record-writer` environment. Its deployment-branch policy is `main` only. Until then the approve step reports `skip-no-approver` and the hold still removes the treadmill, so one manual approval at a held head now sticks.

**Residual, disclosed.**

- `dismiss_stale_reviews_on_push` is false. A push to `record/autofix` between beats by a writer other than the job would therefore ride an existing approval. Every pull request shares that exposure today, because tvofi left the setting unchanged (D11-s1-01).
- `expectedHeadOid`'s schema description does not say whether GitHub re-checks the head at merge time. I pass it, and I do not rely on it.

## Head

`690c47ecea5c1bc4f8f5d42aa2ea1248936f3743`

## Mutation proof

Each mutation was applied singly to `tools/audit/seat/record_row.py` and run with `python3 tools/audit/seat/record_row.py --self-test`, which `tests/entities.py` runs as `tools/audit/seat/record_row.py --self-test passes`. Afterwards the file was restored byte-identical (`diff -q` against the kept copy). The failing check names:

- M1 drops `merged is not True`. Fails: `automerge refuses: unmerged PR`.
- M2 compares the author id to itself. Fails: `automerge refuses: lookalike bot id`.
- M3 drops `len(lines) != 1`. Fails: `automerge refuses: two lines`.
- M4 drops `status != "added"`. Fails: `automerge refuses: a row added to an existing empty file`.
- M5 changes the path arm's `or` to `and`. Fails: `automerge refuses: a one-line file outside the row directory` and `automerge refuses: a renamed row`.
- M5b drops the rename arm. Fails: `automerge refuses: a renamed row`.
- M6 makes the regenerate-and-compare always pass. Fails: `automerge refuses: wrong merge commit`.
- M7 drops the empty-diff arm. Fails: `automerge refuses: empty diff`.
- M8 drops the branch arm. Fails: `automerge refuses: foreign head branch`.
- M9 inverts the required-context membership. Fails: `failed_required ignores a red that is not required` and `failed_required names a red that is required`.
- M10 makes the self-row comparison always pass. Fails: `automerge refuses: an altered self row`.

The first fixture set let M4 and M5 survive, because each bad fixture refused through some other arm. The second commit adds one fixture per arm that is clean in every other field.

The workflow pin is `tests/entities.py` `_raf_job_ok`/`_raf_review_gated`. Its null-control check (`and the pin reads the job's own lines, not its name`) now also strips the guard ahead of the review and swaps the approver token for the author's. Each must turn the pin red, and the check is green at the head.

## Null control

- **A valid row-only pull request passes.** The fixture `automerge: valid row-only PR passes` has a merged-row line regenerated from facts plus the self-row. `automerge: a roster-suffixed row passes` covers the group-suffixed shape.
- **Real record pull requests pass.** I replayed the guard on every record pull request in #1989 to #2002: #1989, #1991, #1992, #1998, #2000, #2001 and #2002. Each printed `AUTOMERGE OK` with rc=0. The older ones wrote `docs/delivery/`, which is read through the layout move map (`--replay-moved`). #2002 also passes `--hold` at its live head.
- **Non-record pull requests refuse.** The other numbers in that range that are pull requests (#1993, #1994, #1995, #1997, #1999) each refuse with rc=1, on branch and path. #1990 and #1996 are not pull requests, and the API returned 404 for them.
- **Every perturbation refuses alone:**
  - another file
  - an edited row
  - a deleted row
  - two lines
  - an unmerged pull request
  - a wrong merge commit
  - a non-bot author
  - a lookalike bot id
  - a foreign head branch
  - a self-row for another number
  - an altered self-row
  - an empty diff
  - a conflict
  - a one-line file outside the row directory
  - a renamed row
  - a status-modified row

## Figures

- Guard self-test, all arms: `python3 tools/audit/seat/record_row.py --self-test`. It printed `all checks passed`.
- Replay on the record pull requests: `GH_TOKEN=$(gh auth token) python3 tools/audit/seat/record_row.py --automerge-check --replay-moved --pr 2001`, and the same for each number listed under Null control.
- Hold at the open record pull request's live head: `GH_TOKEN=$(gh auth token) python3 tools/audit/seat/record_row.py --automerge-check --hold --pr 2002`.
- Workflow wiring pins: `PYTHONPATH=tests/hastub python3 tests/entities.py`. It printed `ALL ... ENTITY CHECKS PASSED` at the head, run with the seat venv.
- Policy caps after the rule edit: `node tools/policy/policy_lint.mjs --budgets`. The `delivery-status-tracking.md` row is under its cap. The edit was paid by cutting spent prose in the same file (items 4 and 5), with no raise.
- Generated rule copies: `node tools/policy/rules_sync.mjs --check`.
- Ratchet: `python3 tests/structure.py`. It printed `STRUCTURE RATCHET PASSED`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL`, because `tests.yml` changes the gate itself. The heavy suite is CI's (SEAT-BLOCK). Locally I ran only the scripts this change reaches: `tests/entities.py`, the self-test and `tests/structure.py`.

## Red checks

`delivery-status` is red on main (OVERDUE). This pull request answers it.

**Cause.** The record beat rebuilt `record/autofix` from main on every main merge, with a force-with-lease sibling commit. Every main merge therefore moved the record pull request's head. That restarted its required checks and staled the head-pinned review (`app_approve.sh` approves one exact head). On a busy main the record pull request never reached a head that was both green and reviewed. Rows aged past `STALE_AFTER_COMMITS`, and `delivery-status` went OVERDUE.

**Process state.** The #1952 design kept the review manual on purpose and pinned "no review-posting step" in `tests/entities.py`. Nothing measured whether a manually reviewed pull request could ever merge under a beat that rebuilds it per merge. The pin enforced the design that caused the red.

**Why a predicate is cheaper than review here.** The diff is fully determined by API facts. Each row is regenerated from `/pulls/<N>` and compared byte for byte. A reviewer seat can add nothing the comparison does not check, and it costs a dispatch plus a stale-head round per main merge. The guard costs one API read per row per beat.

`nightly-status` is red at the ancestry because main's nightly failed: `boost_drift_replay` timed out in the nightly mutation drive. The fix is #2026, which is open. This branch does not touch that job or its inputs:

- `git diff -U0 $(git merge-base origin/main HEAD)...HEAD -- .github/workflows/tests.yml` has 14 hunks, and every one sits inside `record-autofix`: its header comment and its steps. None touches `nightly-status`, `slow`, `nightly-ha` or any mutation job.
- The branch changes no file under `tests/` except the `record-autofix` pins in `tests/entities.py`.
- The cheaper detector is `nightly-status` itself, which already names the run. Its standing cost is one red per failed night until #2026 merges.

The `delivery-status` answer above is its cause; this pull request is the countermeasure.

No other check went red on this branch locally. The suite is CI's.

## Forward-carry

none

## Friction

none

## Approval

Policy change: `dev/governance/rules/delivery-status-tracking.md`, with its generated `.claude/rules/` and `.cursor/rules/` copies. A `record-autofix` record pull request now merges with no review seat where `record_row.py --automerge-check` passes, and one the guard refuses is reviewed. The workflow is code-owned too (`.github/workflows/`). This is owner-approved as tvofi's "option 1" (2026-10-07), under the programme mandate #201 comment 5951564627. The labelled approval posts after the merge verdict, per the policy-approval procedure.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
