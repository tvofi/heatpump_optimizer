Fix review: merge 7bda397d1226e798a14e17c5367697de95e77e9d

bus-nonce: e99676781fff16418196bf81075013b1

Round: 1. The PR has no earlier `Fix review:` comment (0 issue comments, 0 reviews at read time).
Measured head: 7bda397d1226e798a14e17c5367697de95e77e9d. It was still the PR head when this verdict was written, and origin/main is still c8cc75ea9.
Contract: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract read is current.
Policy: this PR changes `ci-autofix.md`, so tvofi must approve it at the head before it merges. This verdict does not stand in for that approval.

## RESULT lines (ev/ holds each output)

- RESULT merge-tree: `git merge-tree --write-tree origin/main 7bda397d` gives rc=0 and tree 87f07e9666. No conflict and no claim-driver line.
- RESULT CI (check-runs API, filter=all, at the head): 46 runs, 31 success and 15 skipped. None failed, and none is pending or action_required (`ev/check_runs.txt`).
  - pr-contract started 17:14Z, before the last run concluded at 17:35Z. That is fine here because nothing at the head is red.
  - pr-contract's range line: `record red-history 6 commit(s) ... every failure conclusion across them: nightly-status`. nightly-status grades main, so it is not this PR's. The "Red checks: none" answer stands.
- RESULT range (I checked this myself, beyond the contract's line): at the earlier head 21e457fea, the first attempts of arch-score, validate-hacs, env-matrix and pr-contract were red. arch-score's log reads `gh: API rate limit exceeded for installation`, and env-matrix's reads `the GitHub API is unreachable`. All of them are success on their latest attempts at that same commit (`ev/range_21e457fea_latest.txt`, `ev/range_reds_logs.txt`). These are infrastructure failures, not this diff's, and the contract's range check counts latest conclusions.
- RESULT behaviour: `merge_train.py` and `queue_pre_flight.py` have the same AST at the merge base and at the head once every string constant is masked (`ev/ast_compare.txt`: True, True). The `ci-watch.sh` diff changes comment lines only (0 non-comment lines). The PR changes no behaviour, as it claims.
- RESULT live train behaviour (`--overlap`, batch): unchanged by construction, given the AST result.
  - The batch admit still adds `BOT_ROUTE` from `bot_tip` (line 1275).
  - The `--overlap` up-front recarry still excludes bot-routed entries (line 1516; they recarry at their own turn).
  - `bot_refusal` still raises `BOT_HEAD`.
  - The new prose describes this path correctly. The train does not read whether held runs were approved, and the body says so.
- RESULT self-tests at the head:
  - merge_train: 180 checks, 0 failed
  - ci-watch: 8 checks, 0 failed
  - queue_pre_flight: 32 checks, 0 failed
- RESULT other checks at the head:
  - rules_sync --check: ok
  - policy_lint: 0 errors
  - structure.py: PASSED
  - env_drift --claims-only <merge-base>: ok
  - entities (env -u BASH_ENV): ALL 2347 PASSED, rc=0
- RESULT budget: `ci-autofix.md` uses about 1468 of its 1469 `files_tokens`, the figure the body says it compared exactly. No `*_budgets.json` is touched.
- RESULT null control (my own run, on a detached origin/main): adding only the INERT sentence and regenerating makes policy_lint refuse: `about 1518 tokens ... exceeds its cap of 1469 (files_tokens)`, 1 error (`ev/null_control.txt`). The cuts are what pay for the change, as claimed.
- RESULT mutations (`ev/mutations.txt`):
  - M1: reverting `.cursor/rules/ci-autofix.mdc` to the base gives `RULES-SYNC: 1 file(s) out of date`.
  - M2: dropping "App push" from `bot_refusal` gives 1 failed self-test.
  - M3: dropping "GITHUB_TOKEN" from `bot_refusal` gives 2 failed self-tests, including the null control.
  - The tests that pin the message are not vacuous.
- RESULT verbatim: the landed sentence matches `dev/audit/rca/R10-RCA-INERT-PREDICT.md` lines 224-226 word for word. It sits where the RCA places it.
- RESULT VERSION, the manifest and RELEASE_NOTES are untouched (empty three-dot diff), and no golden or claim file is touched.

## API figures, re-derived under the body's rule

- Run 38781421410:
  - attempt 1: Tests, `action_required`, actor github-actions[bot], event pull_request, head 720d3636, subject `ci: pin killed mutants`.
  - latest: attempt 2, triggering actor hpo-runs[bot].
  - Confirmed (`ev/api_cited.txt`).
- Null-control heads:
  - 3c9fe53f and 63084989 (bot-authored): 0 `pull_request` runs each.
  - 18a04ed6 and 72cfb1d0: 8 runs each.
  - Confirmed.
- 28 of 28: I listed workflow_dispatch runs from 2026-10-15 to 2026-10-18 whose head_commit author email starts `41898282`, created from 10:23Z, and kept unique heads (`ev/bot_heads_pr_runs.tsv`). The heads up to and including 6f6aa4e48d, the head the body names as its read time, number exactly 28, and all 28 have `pull_request` runs. Confirmed.

## Class attack (configurations beyond the window)

The body's enumeration rule is a tree-wide grep, and I re-ran it (`ev/class_grep.txt`).

- Outside `.github/workflows/tests.yml` it finds no unedited stale claim. `merge-main.yml:106` already says the runs are held. The `budget_raise_gate.py` and `contract_rerun.py` hits are run-time messages about a different subject.

The 2026-10-18 heads after the fixer's read time add 9 more bot heads.

- Eight have 8 `pull_request` runs each.
- One, 33dfae1e67 on #2399 at 14:06Z, has 0 runs, which looks like a counterexample to the new "held, not absent" claim.
  - It is explained: `git merge-tree` of that head against main at that moment (f1b21daab) conflicts on `dev/audit/rounds/round4/D6/claims.py`.
  - A DIRTY head queues no run, which the rule already states.
  - The new claim holds for every non-DIRTY bot head I found: 36 of 36.

## Non-blocking notes for the orchestrator (the body should be corrected; none gates the merge)

1. Friction line `ci-autofix-held-runs` says "five" stale `tests.yml` comments, but the grep finds **seven**:
   - 2895, above the dispatch
   - 3010, 3283 and 3572, the push steps
   - 3032, 3302 and 3591, the approve steps

   The body's description of where they are ("above mutation-autofix's dispatch, and at each job's push and approve steps") covers all seven, so the seam is dispositioned. Only the count is wrong.
2. The body's entities figure, `ALL 2346`, is not what this head measures, which is 2347. origin/main c8cc75ea9 also measures 2347 (`ev/entities_main.txt`), so the extra check came in with the main merge. The body's figure was taken at an earlier head.
3. The new held-runs sentence is hard to parse: "...fail-soft while their secrets are absent, when an App push or body edit cures it." The body's own wording ("An App push or a body edit is the cure when it fails") is clearer. This is prose quality only.
4. The friction `merge-train-bot-tip` stands: the train still refuses every bot tip, although approvals were seen at every non-DIRTY bot head. That is a behaviour change for a later PR, correctly kept out of this one.

Forward-carry: the body says none. No finding here changes a later stage's brief. The remaining stale `tests.yml` comments are a gate-file edit, and the body correctly leaves that to the orchestrator.

Harness: the finding has no committed harness. The figures are REST queries stated in the body, and I re-ran them as stated. I built two instruments myself and disclose them: the AST-equality check and the bot-head enumeration script. Both live in `ev/`.
