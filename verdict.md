Fix review: blocked 6289321a8451138719535f170ab395590ff556f0 ci-red: governance / instrument-self-tests fails at this head on ref_privacy.py --self-test (109 checks, 1 failed), because body_push.sh's new head-stale refusal fires before the author guard in ref_privacy's fixture

bus-nonce: 3a9e249fd4fcca149cf54865b567992d

## Round

Round 2 of the fix review of #3245 (R10-PROCESS-SLIM), measured at head 6289321a8451138719535f170ab395590ff556f0. Round 1 was blocked at 481c7750 (ci-red, handoff_push delivery_row grep). That cause is repaired. A new cause is red in the same job.

## Block

- `governance / instrument-self-tests` (check-run 127997950671, attempt started 16:03:36Z, concluded **failure** at 16:33:24Z) failed at step 28, "Refuse a push that names the host, and an unregistered pusher". This is a step failure, not a cancel at the 30-min timeout, so the owner's standing timeout line does not cover it. The failing step's line: `ref_privacy self-test: 109 checks, 1 failed`. The failing arm: `FAIL body_push refuses a handoff head authored by a runner default, and writes no body ref: rc=1 ... "body_push: REFUSE head-stale: ## Head does not name the handoff's code sha <sha>; it names none"`.
- Cause: the diff's Carry 1 adds a `head-stale` refusal to `tools/audit/seat/body_push.sh`. That refusal runs before the runner-default-author guard that `tools/audit/seat/ref_privacy.py`'s fixture pins. The fixture's body names no `## Head`, so body_push now refuses for head-stale and the arm's expected author refusal is never reached. The arm pins a privacy guard, so the guard it measures is now masked.
- Reproduced in this seat (ev/ref_privacy/summary.txt): `python3 -I tools/audit/seat/ref_privacy.py --self-test` prints `109 checks, 1 failed` at 6289321a8, and `109 checks, 0 failed` at the base b36679cea and at origin/main 817c2b169 (null control).
- The PR's own body_push self-test (35 checks, 0 failed, re-run here) does not cover ref_privacy's caller of body_push. Neither `## Figures` nor `## Red checks` names `ref_privacy`, so the cheap detector existed and was not run. It is one command of seconds, and the instrument-self-tests job runs it.
- Repair, without loosening anything: give ref_privacy's runner-default fixture a body whose `## Head` names the fixture handoff's code sha, so that only the author guard can refuse it. Or order body_push's author guard before head-stale. Either way, keep the arm's assertion on the author refusal, and re-run `ref_privacy.py --self-test` and the whole instrument-self-tests step list before the handoff.

## Owner constraint

The diff writes **0 files under `custom_components/`** (`git diff --name-only <merge-base> 6289321a8 -- custom_components` is empty). For each change, the production path it touches and the check that still guards it:

- **C4** (bus.sh derived `--reviewed-head`, fix-review.md step 12): no production path. Mutation, goldens, features and CodeQL still run on every head. `tests / mutation`, `codeql / Analyze (python)` and `tests / fast (3.14)` concluded success at this head. A carried verdict needs the PR's own diff unchanged, and a red never carries.
- **C5** (paperwork becomes a note, the delivery row and record stream retired, `governance / delivery-status` deleted): no production path. A note on `custom_components/` still blocks (fix-review.md at the head). `governance / delivery-status` is not a required context: the required list in `tools/ci/fixtures/ruleset/ruleset_23698884.json` does not name it, and `tools/ci/` is unchanged by the diff.
- **C8** (bus.sh refuses dispatch while a cheap check is in flight, and refuses posting `merge` at RED): no production path. A production review waits at most for `tests / mutation`, itself a merge-blocking production check. bus-2 is killed (below).
- **C6 (a)** (proposal-triage.md deleted, its two caps removed): no production path.
- **Train fixes** (postmerge docs step removed, app_approve carry() ancestry rc, merge_train release_worktrees): no production path.
- **Workflows**: tests.yml loses only the PR-copy delivery_status step. nightly.yml loses `record-autofix`. governance.yml loses `delivery-status` and `delivery-status-publish`, and `record`'s refusal step becomes report-only. None of these is the mutation lane, goldens, features or CodeQL. `ci.yml` and `tools/ci/*` are untouched, so the gate's workset rules for production-only, machinery-only and mixed diffs are main's. That is not re-derived here beyond the file list. This head is a mixed governance diff, and the final `gate` ran `KIND: code` with workset `arch-score budget-raise-gate codeql governance hassfest pr-contract tests validate` and no SKIPPED required job.
- **Planted production defect**, with a null control:
  - plant 1, `fee_bound` × 2 at grid_fee.py:81: the scoped gate selects 22 scripts and scopes out 11, identical at the head and at origin/main (ev/plant/select.diff is empty). `tests/config_flow_steps.py` passes at **both** ends (rc 0), because its fee_bound pin compares the function with itself. That gap is pre-existing, not this PR's; see Findings.
  - plant 2, `fee_bound` returns -1: `tests/config_flow_steps.py` refuses it, **rc 1, 2 of 539 checks FAILED, at the head and at origin/main alike** (ev/plant2/summary.txt).
- The body states, per change, why the risk is acceptable and names the remaining guard (`### Owner constraint, per change`). No cut goes beyond the cards C4, C5, C8 and C6 (a) as written. I found no large unforeseen risk with a measurement behind it.

## Policy text changed (for the coordinator to surface to tvofi)

The full diff is ev/policy.diff, and the list below is ev/policy_sentences.md. In summary:
- CLAUDE.md:
  - the delivery-status row now reads "the record is the pull-request list and one #201 line per merge ... no per-PR row";
  - finding-propagation's "before the producing pull request merges" becomes "landed at the latest at the producing pull request's merge";
  - the `proposal-triage.md` row is removed;
  - fix-review's row loses "a head that moved under the review is a blocked verdict" and gains "blocks on code, tests and harness, paperwork is a note; a verdict carries while the PR's own diff is unchanged";
  - "the fix reviewer returns `blocked` on one the body left unanswered" becomes "an unanswered one is a reviewer's note resolved at merge (card C5)".
- fix-review.md:
  - adds "Block only on code, tests and harness (card C5) ... one on `custom_components/` blocks. `bus.sh post` refuses `merge` at a red (C8)";
  - `carry-missing` and `root-cause-*` become `Note:` lines;
  - removes the "posted only once the head's workflows all concluded ... (tvofi, 2026-10-08)" sentence;
  - the delivery-status exemption is removed;
  - step 12's carry is extended to "any later head whose own diff is unchanged (card C4)", and head-moved now applies only when the own diff moved.
- fixer.md: "Your PR does not merge until any finding that changes how a later stage must work is in that stage's own brief" becomes "Put any finding ... in that stage's own brief".
- orchestrator.md:
  - section 5: a proposal is "ruled directly, by the owner or by you ... no standing triage seat (card C6)";
  - section 9: the record is the postmerge #201 line and roster `resume`, with no per-PR row;
  - "bar its delivery row" is removed.
- standing-dispatch.md: the delivery-row check is removed, and "(cards C4, C8 refuse there)" is added.
- standing-roster.md: the proposal-triage citation becomes "An op naming a triage or proposal number cites its ruling".
- D11.md item 5: "goes to `proposal-triage.md`" becomes "goes to the orchestrator".
- defect-root-cause.md:
  - the enforcement block becomes a C5 note and a C8 no-merge-at-red;
  - `governance / delivery-status` is dropped from the main-graded pair;
  - "or a row it did not add" and "or drain the overdue rows" are removed.
- delivery-status-tracking.md: rewritten around #201 and the PR list. "same session or an immediate record PR" becomes "at that merge"; the status-word and record-autofix bullets are removed; a stale body becomes a note; and it adds "An owner's ask in a verdict or a body goes into the roster at the merge".
- finding-propagation.md: "before the PR that produced it merges" becomes "by the producing PR's merge (card C5)".
- policy_budgets.json: the two proposal-triage.md keys (36, 489) are removed.
- proposal-triage.md: deleted.

The body says `content approved by tvofi in chat 2026-11-05`.

## Findings

- `tests/config_flow_steps.py:7591` pins `fee_bound` by comparing the form placeholder with `config_flow.grid_fee.fee_bound(currency)` itself. So a scaling defect in `fee_bound` (×2 at grid_fee.py:81) passes at both the head and origin/main (rc 0, 539 checks). This is a pre-existing test-suite gap, not this PR's diff, and a sign of plant 2's -1 is still caught. Carry: dismissed: pre-existing at origin/main and outside this PR's diff; a D3 test-gap observation from a planted-defect control, not a defect this group owns

## Evidence

- Head measured: 6289321a8451138719535f170ab395590ff556f0 (ev/HEAD.txt). It is the PR head per the API at review time, and the body's `## Head` names it.
- `review_packet.py render`: REFUSE required-red `gate` (an early gate run that deferred: "run(s) [42246392699] at this head are still being judged"). I re-read the live checks after all runs concluded.
- Check-runs, both pages, 66 runs (ev/checkruns.txt). Concluded reds at this head:
  - `governance / instrument-self-tests` failure;
  - `budget-raise-gate / budget-raise-gate` failure (three runs);
  - `gate` failure (three runs; the final one, 128022390637, reads `FAIL budget-raise-gate / budget-raise-gate: failure (run 42246900077)` only).
  - `pr-contract / pr-contract` success (16:46:55Z, started after the last red concluded). `tests / mutation`, `tests / fast (3.14)`, `codeql / Analyze (python)` and `tests / arch-instrument` succeeded.
- `merge_train.py classify ... --pr 3245`: final rc 1, `RED 6289321a8... pending: none red: gate` (ev/classify.txt, ev/classify.log).
- `budget-raise-gate` fails at step 4, "Refuse a budget raise the owner has not approved at this head". The body carries `## Raise justification` with the line "Raise approved under mandate (comment 6624093439, scope all) by the orchestrator ..." and `Architecture score: dS +0.0000 NULL`. The diff of `*_budgets.json` is exactly the two removed proposal-triage.md keys. I did not re-run the archscore.
- Round-1 cause repaired: governance.yml at the head no longer greps the handoff_push output for `delivery_row` (main's line 719 is removed). Each self-test run here with its CI grep (ev/selftests/summary.txt) passed at the head:
  - handoff_push, body_push, postmerge, merge_train, ci_predict, bus, app_approve;
  - open_pr and update_pr, both with the `delivery_row` grep;
  - structure.py, entities.py, rules_sync --check, policy_lint.
- `## Red checks` names `governance / instrument-self-tests`, `budget-raise-gate / budget-raise-gate`, `pr-contract / pr-contract` and `gate` by check-run name, for the older head 481c775. At this head pr-contract passed.
- Mutants, the PR's harness `dev/audit/harnesses/r10_seat_selftests_mutants.py bus-1 bus-2 bus-7 bus-10 ci_predict-3 ci_predict-4`: all KILLED, `RESULT survivors=0` (ev/mutants.txt).
- `git merge-tree --write-tree origin/main 6289321a8`: rc 0, no conflict, no MERGE-CLAIM line (ev/mergetree.err is empty).
- VERSION, the manifest, RELEASE_NOTES.md, tests/golden/claimed_drift.txt and card_claimed_drift.txt are byte-identical to the merge base.
- Finder's harness: none named. This group is a process change with no audit finding harness. The planted production defect above is this seat's own control, disclosed as mine.
- Not re-derived: the card figures (RFT, token and job-minute estimates; the body cites them, not re-taken) and the docs-step probe (out of tree, not re-run by the fixer either).
