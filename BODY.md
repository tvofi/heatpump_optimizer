The `record-autofix` beat's record pull request (branch `record/autofix`, for example #2002) only adds rows under `dev/programme/delivery/`. The job rebuilt that branch on every main merge, so each human or seat review went stale before approval. The record pull request never merged, and `delivery-status` stayed OVERDUE on main.

With this change, a row-only record pull request merges with no review seat. A guard refuses anything else. This is the owner's "option 1" (tvofi, 2026-10-07). Round 2 applies the orchestrator's decisions on the round-1 review.

**The guard.** `tools/audit/seat/record_row.py --automerge-check --pr N [--head SHA] [--hold] [--require-green]` runs `automerge_refusals`. That is a pure function, and the self-test drives it from fixtures. The guard passes only if all of these hold:

- **Author.** The author is `hpo-author[bot]`, type `Bot`, id `331381602`. The id is pinned the way `app_approve.sh` pins the approver's.
- **Branch.** The pull request goes from `record/autofix` to `main` within one repository.
- **Path.** Every file in the three-dot diff (`/pulls/N/files`) sits at exactly `row_path(N)` for its own number. That means ASCII digits, no leading zero, no trailing newline, and so one row file per pull request. A file whose path matches the pattern but is not canonical is refused.
- **Content.** Each file is new, is not a rename, and adds exactly one line with nothing removed and no context.
- **Anchor.** That line anchors `<N>` through `delivery_status.anchored`, the existing row parser.
- **Facts.** The line is byte-equal to what `row_line` writes from the API's own facts for `<N>`. Those facts are: merged, merged into `main`, its merge commit, and its title (an optional roster suffix is allowed). The pull request's own row must equal the generated `open_row_line` self-row. The line is regenerated and compared, never parsed back.
- **Mergeable.** `mergeable` is not false.
- **`--hold`.** No required context has failed at the head. The newest run per name counts, so a re-run supersedes the red it replaced. Required contexts are read from `/rules/branches/main`.
- **`--require-green`.** While any required context has not yet passed at the head, the guard exits 3 (`AUTOMERGE PENDING`).
- **`--head`.** If the live head is not the one asked for, the guard refuses before it reads any file.

**The mechanism (CI, no session, no ruleset change).** The `record-autofix` job in `.github/workflows/tests.yml` changes in four ways:

1. **Hold.** If an open record pull request passes `--automerge-check --hold`, the beat leaves it alone instead of rebuilding it. Rebuilding on every merge was the treadmill.
2. **Approve and merge.** This step runs after the open/update step, at the live `HEAD`.
   - On a guard refusal, it dismisses every approval by `hpo-approver[bot]`. A refused head therefore cannot be hand-merged on the bot's word, and the review becomes manual.
   - On a pass, the **hpo-approver App** posts one APPROVE pinned to `HEAD`.
   - Then `--require-green` decides. While it is pending, the step ends as `approved-pending`, and the next beat retries (a main push, or the nightly on a quiet main).
   - Once every required context has passed at `HEAD`, the **hpo-author App** merges with `PUT /pulls/N/merge` and `sha: HEAD`. If the head moved after the guard judged it, the REST API refuses the merge, so it fails closed.
   - There is no auto-merge. That removes the post-queue push window and the `expectedHeadOid` question from round 1.
   - The author App's merge push fires main's workflows. A `GITHUB_TOKEN` merge would not.
3. **Revoke.** A final `if: always()` step revokes both installation tokens on every path through the beat.
4. **Mint.** One `mint` routine mints the author token. It mints the approver token only when `HPO_APPROVER_PEM` and `HPO_APPROVER_APPID` exist in the main-only `record-writer` environment, and that token holds `pull_requests: write` only.

**Why this mechanism.** I measured the alternatives on 2026-10-07:

- **Approving as `github-actions[bot]`.** `can_approve_pull_request_reviews` is already `true`. This would add an approving identity that decision 0011 does not name, and it would need a fifth `permissions:` override. Rejected.
- **Merging as `hpo-ledger` (5094721).** It is a bypass actor, so it would skip the required checks. Rejected.
- **A session instrument.** It would need a live orchestrator. Rejected.
- **Auto-merge.** The round-1 review dropped it: it merges later, on a head nobody judged.

`.github/CODEOWNERS` owns nothing under `dev/programme/delivery/`. The approver App's review therefore satisfies `main-protect-checks`' one-approval rule, and no CODEOWNERS change is needed.

**Owner action before approval works.** Add `HPO_APPROVER_PEM` and `HPO_APPROVER_APPID` (the contents of `~/.zcode/identity-approver.pem` and `.appid`) to the `record-writer` environment. Until then the step approves nothing. The hold still ends the treadmill, so one manual approval at a held head sticks, and the beat then merges that head once its checks are green.

**Residual.** A writer that pushes to `record/autofix` between beats changes the head. The next beat's guard then judges the new head, and that beat's merge is pinned to the head it judged. An earlier approval left on a stale head cannot carry an unjudged head through this job. A hand merge of such a head is the same exposure every pull request has under `dismiss_stale_reviews_on_push: false`.

## Head

`e052636aa02e404701677c59fc8f6f2b849b4aaa`

## Mutation proof

Each mutation was applied singly to `tools/audit/seat/record_row.py` and run with `python3 tools/audit/seat/record_row.py --self-test`. `tests/entities.py` runs that self-test as `tools/audit/seat/record_row.py --self-test passes`. After each mutation the file was restored byte-identical. The failing check names:

- **R1** removes the canonical-path comparison. It fails `automerge refuses: path attack: arabic-indic digits`, `...: fullwidth digits`, `...: leading zero`, `...: trailing newline in name` and `...: one PR rowed at two paths`.
- **R2** removes the merged-into-main arm. It fails `automerge refuses: a row for a pull request merged into another branch`.
- **R3** removes `automerge_check`'s head pin, the round-1 survivor. It fails `automerge_check refuses a head that moved, before reading files`.
- **R4** makes the newest-run rule order-dependent. It fails `failed_required reads a re-run over the red it supersedes`. It survived at first, and a newer-listed-first fixture now kills it.
- **R5** counts a still-running run as green. It fails `not_green names a required context missing or still running`.

The round-1 set (M1–M10) still holds. Each of its arms kept its own fixture.

The workflow pin lives in `tests/entities.py`:

- `_raf_review_gated` requires the review to come only after the guard, and only with the approver token.
- `_raf_merge_pinned` requires the merge PUT to come after `guard --require-green`, to carry the `sha` payload, and the job to contain no `AutoMerge`.

The null-control check (`and the pin reads the job's own lines, not its name`) also strips the green gate and the `sha` pin. Each must turn red, and that check is green at the head.

## Null control

- **Valid fixtures pass.** `automerge: valid row-only PR passes` and `automerge: a roster-suffixed row passes` pass. `automerge_check` passes the same pull request at its live head (`and passes the same pull request at its live head (null control)`). `not_green is empty when every required context passed` holds.
- **Real record pull requests pass.** Replayed on every record pull request in #1989–#2002 (#1989, #1991, #1992, #1998, #2000, #2001, #2002), each prints `AUTOMERGE OK` with rc=0. The pre-move ones are replayed through the layout move map (`--replay-moved`). #2002 also passes `--require-green` at its head with rc=0.
- **Without the move map, the old path is refused.** #2001 without `--replay-moved` refuses `docs/delivery/2000.md` as non-canonical.
- **Non-record pull requests are refused.** #2029 is refused on branch and on every path. #1993, #1994, #1995, #1997 and #1999 were refused in round 1.
- **The round-1 reviewer's `path_attack.py` (its harness) refuses all five path cases and the duplicate.** Its "control canonical path" case now refuses too, but only because its fixture facts carry no `base` and the guard now requires a merge into `main`. Real `/pulls/N` facts carry `base`, and the replay above passes.

## Figures

- Guard self-test, all arms: `python3 tools/audit/seat/record_row.py --self-test`.
- Replay: `GH_TOKEN=$(gh auth token) python3 tools/audit/seat/record_row.py --automerge-check --replay-moved --pr 2001`, and the same for each number under Null control.
- Green gate on a record head: `GH_TOKEN=$(gh auth token) python3 tools/audit/seat/record_row.py --automerge-check --require-green --pr 2002`.
- Round-1 reviewer harness: `python3 /Users/timmalmstrom/hpo-seats/orch-r9c/review-2029-evidence/path_attack.py`, run from the worktree root.
- Workflow pins: `PYTHONPATH=tests/hastub python3 tests/entities.py`. It printed `ALL ... ENTITY CHECKS PASSED` at the head, run with the seat venv.
- Policy caps: `node tools/policy/policy_lint.mjs --budgets`. The `delivery-status-tracking.md` row is under its cap, with no raise.
- Full policy lint: `node tools/policy/policy_lint.mjs` printed `TOTAL: 0 error(s)`.
- Generated rule copies: `node tools/policy/rules_sync.mjs --check`.
- Ratchet: `python3 tests/structure.py`.
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL`, because `tests.yml` changes the gate. The heavy suite is CI's (SEAT-BLOCK).

## Red checks

**`delivery-status`** is red on main (OVERDUE), and this pull request answers it.

- **Cause.** The record beat rebuilt `record/autofix` from main on every main merge. Each rebuild moved the record pull request's head, restarted its required checks and staled its head-pinned review. On a busy main the record pull request never reached a head that was both green and reviewed. Rows aged past `STALE_AFTER_COMMITS`.
- **Process state.** The #1952 design kept the review manual, and `tests/entities.py` pinned "no review-posting step". Nothing measured whether a manually reviewed pull request could ever merge under a beat that rebuilds it on every merge. The pin enforced the design that caused the red.
- **Why a predicate is cheaper than review here.** The diff is fully determined by API facts, because each row is regenerated from `/pulls/<N>` and compared byte for byte. A reviewer seat adds nothing the comparison does not check, and it costs a dispatch plus a stale-head round on every main merge. The guard costs one API read per row per beat.

**`nightly-status`** is red at the ancestry because main's nightly failed: `boost_drift_replay` timed out in the nightly mutation drive. The fix is #2026, which is still open. This branch does not touch that job or its inputs:

- The three-dot diff of `.github/workflows/tests.yml` (`git diff -U0 $(git merge-base origin/main HEAD)...HEAD -- .github/workflows/tests.yml`) only has hunks inside `record-autofix`: its header comment and its steps. None touches `nightly-status`, `slow`, `nightly-ha` or any mutation job.
- Under `tests/`, only the `record-autofix` pins in `tests/entities.py` change.
- The cheaper detector is `nightly-status` itself, which names the run. Its standing cost is one red per failed night until #2026 merges.

**`pr-contract`** went red at `957c9cd0` on a body that did not yet name `nightly-status`. This body names it, and the new head re-runs the check.

**`budget-raise-gate`** was cancelled at `957c9cd0`. The new head re-runs it.

## Forward-carry

none

## Friction

none

## Approval

Policy change: `dev/governance/rules/delivery-status-tracking.md` and its generated `.claude/rules/` and `.cursor/rules/` copies. The change: "the `record-autofix` beat's own merges with no review seat where `record_row.py --automerge-check` passes at its head; else it is reviewed." The workflow is code-owned (`.github/workflows/`). Owner-approved as tvofi's "option 1" (2026-10-07), under the programme mandate #201 comment 5951564627. The round-2 design decisions are the orchestrator's, under the same mandate. The labelled approval posts after the merge verdict, per the policy-approval procedure.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
