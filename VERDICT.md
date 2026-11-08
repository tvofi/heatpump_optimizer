Fix review: merge 85ba6cda83898bb3fcc1dee71432c1622f14a72e

bus-nonce: 72d8cb30cbc2adc4dffeccfa5a481eac

## Round

Round 2 of this review, scoped by the dispatch's ROUND-2 NOTE: does the new test kill the RETURN_DEL mutant at config_flow.py:2193 that survived at 7e27de7a? Did anything else move between 7e27de7a and 85ba6cda83898bb3fcc1dee71432c1622f14a72e? Is every concluded red of this head named? Measured at 85ba6cda83898bb3fcc1dee71432c1622f14a72e, from detached worktrees at the head and at 7e27de7af1bca3789cd879ec5611808c28d17063. Role files unchanged against main.

## Evidence

- RESULT mutant config_flow.py:2193 RETURN_DEL at head: `    return {}` replaced by `    pass`. `PYTHONPATH=tests/hastub python3 tests/config_flow_steps.py` exits rc=1 with `2 of 551 checks FAILED`. The two failures are `FAIL no offset entity configured: the check returns exactly {}  [returned=None]` and `FAIL an offset whose range includes 0: the check returns exactly {}  [returned=None]`. The null-control row (range 20-70 returns the refusal) stays ok. After restoring: rc=0, `ALL 551 checks PASSED`, git status clean. KILLED (ev/head-mutant.log, ev/head-clean.log).
- RESULT same mutant at 7e27de7a: unmutated rc=0 `ALL 548 checks PASSED`; mutated rc=0 `ALL 548 checks PASSED`. SURVIVED, which confirms the red the repair answers (ev/old-mutant.log, ev/old-clean.log).
- Survivor count. At 7e27de7a there is 1 added site left alive (config_flow.py:2193 RETURN_DEL), as the brief and the body say. I confirmed it survives the driver that kills it at head, but I did not read the 7e27de7a CI table myself. At head, CI `tests / mutation` (job 128744481063) prints `2751 unpinned site(s) of 6959 candidate sites, 2755 at the ratchet base 4a9d2d54...; the ledger agrees with the deterministic inventory`, then `0 survivor(s) of 10 evaluated = 0.0%` and `MUTATION TABLE PASSED`. Its baselines and null control (config_flow.py:244 NULL_COMMENT) were green, so the result is not the INCONCLUSIVE kind. That run's 10-site draw did not re-verify the new 2193 ledger row. My own run above is that row's verification. The row's recorded `failed=2` matches it.
- Diff 7e27de7a..85ba6cda83898bb3fcc1dee71432c1622f14a72e: 2 files, +29 lines. They are `tests/config_flow_steps.py` (+23, the direct `_heat_curve_errors` rows) and the ledger row `tests/mutation_ledger/killed_by/config_flow.py/_heat_curve_errors.RETURN_DEL.5e4fa825.json`. There is no production line. The head is a merge of 7e27de7a and 20ceaf9dd whose tree equals 20ceaf9dd's (ca4a8901). Commit 09efe35e2 (the test) comes before 20ceaf9dd (the pin). The three-dot `7e27de7a...85ba6cda83898bb3fcc1dee71432c1622f14a72e` gives the same 2 files (ev/diff-7e27de7a-head.txt).
- Test quality: the test asserts `type(ret) is dict and ret == {}` on the check itself, not on the page. That is the right observable, because the page reads None as "no errors". The refusal row is the null control and passes under the mutant, so the test can tell "no error" from "no answer".
- VERSION, manifest version and RELEASE_NOTES.md are untouched against the merge base 6188936a8. No trailers in 7e27de7a..head.
- Merge with origin/main 8a4974d15: `git merge-tree --write-tree` rc=0, with `MERGE-CLAIM: resolved tests/golden/claimed_drift.txt` and `LEDGER-MERGE: resolved tests/closures.json` (ev/merge-tree.txt).
- CI: `merge_train.py classify 85ba6cda83898bb3fcc1dee71432c1622f14a72e --pr 3299` exits 0: `GREEN 85ba6cda83898bb3fcc1dee71432c1622f14a72e pending: none red: none` (ev/classify.txt). All 69 check runs at this head were read once: none concluded failure (success or skipped). So this head has no red to answer. The body's `## Red checks` names 7e27de7a's reds: `tests / mutation` (own, answered with the cheaper detector: prepr 6d with a config_flow_steps MUTANT_CMD), `gate` (follows from it) and the codeql infra 504s.
- Body figures: `ALL 551 checks PASSED` and `2 of 551 checks FAILED` re-derived above. `2751 unpinned ... 2755 at the ratchet base` re-derived from CI's log at this head (base named 4a9d2d54 there, against the body's 6188936a8; the count is the same). The body's local prepr wall times and the 31/18 diff-mutant survivor counts were not re-derived. The CI mutation table passing at this head covers the added lines.

## Findings

None that this round leaves open. The out-of-round items (the stress memory-probe harness, the handoff-wip leftover) are already dispositioned in the PR body and were not reopened here.
