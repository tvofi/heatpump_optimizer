Fix review: merge 61ce00f0404fd7a3c7ae999741ad306deb3f4bd3

bus-nonce: 87e79cee788d144843bbf9aad2499b3a

## Scope

Round 5 of PR #3234, limited by the brief to the round-4 block (verdict at 4512d770, probe/rev-3234-d519881f): `tests/replay_cost_draws.tsv` was in no audit universe, and `## Red checks` did not name `governance / instrument-self-tests` (job 127916728606). Round 5 is past the three-round rule. The body has a `## Re-cut` and the repair is one line, so I agree the re-cut justifies this round. The round-4 verdict's settled findings (the ref46/ref53 border) stand, because the repair does not touch them (see Evidence).

## Evidence

- Head measured: 61ce00f0404fd7a3c7ae999741ad306deb3f4bd3 (packet pin; it is the PR's head per `pull_request_read get`). It is a merge of 824c2b64 into 87cb76a3. 87cb76a3 merges 8de8ada9 into 4512d770. 824c2b64 and 8de8ada9 are the same patch (patch-id 60e372b81d67b957e03e340f36f94b0994bab70c). 83579e22 merges main a2240924 into 4512d770, and `git show --remerge-diff 83579e22` shows no resolution delta beyond `LEDGER-MERGE: resolved tests/closures.json`.
- The repair diff has no production or budget change. `git diff 83579e22 61ce00f0` is one added line, `"tests/replay_cost_draws.tsv",` in `dev/audit/config/scopes.json`. The blobs of tests/replay.py, tests/replay_cost_draws.tsv, tools/audit/seat/replay_draws.py and dev/programme/delivery/3234.md are identical at 4512d770 and at the head. The PR's own closures.json delta is identical before and after. The three-dot diff touches no `*_budgets.json`, no claim file, no VERSION, no manifest and no RELEASE_NOTES (`no-budget-claim-version-touch`).
- Roles: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- check_scopes at each commit (ev/check_scopes-*.txt):
  - main a2240924: rc 0, `unclassified=0`; self-test passed.
  - Round-4 head 4512d770: rc 1, `FAIL coverage tracked=9100 in_universe=1416 excluded=7683 unclassified=1`, naming `tests/replay_cost_draws.tsv`; self-test rc 1, `SELF-TEST FAILED`.
  - Merged tree before the edit, 83579e22 (the body's null): rc 1, `FAIL coverage tracked=9106 in_universe=1417 excluded=7688 unclassified=1`. Self-test rc 1, and only `the default verdict passes the live scopes` and `the default invocation exits 0 on the live scopes` are False. This reproduces the body.
  - Head 61ce00f0: rc 0, `ok coverage tracked=9106 in_universe=1418 excluded=7688 unclassified=0`; self-test rc 0, `SELF-TEST passed (every perturbed scope refused)`. This reproduces the body.
- Mutation, my own: deleting the line at the head gives `check_scopes --repo .` rc 1 with `FAIL coverage tracked=9106 in_universe=1417 excluded=7688 unclassified=1` (ev/mutant-check_scopes-61ce00f0.txt). The test is not vacuous.
- Classification: the file sits at `/D3/universe[6]`, beside `tests/replay/**`. D3 is test-suite gaps. The file is the recorded CI draw table that `tests/replay.py` reads (`COST_DRAWS = ROOT / "tests" / "replay_cost_draws.tsv"`, tests/replay.py:530) to derive live budgets. D3 is the right audit universe, and an exclusion would hide a live input, so I judge the classification sound.
- The round-4 red, read from its own log. `governance / instrument-self-tests`, job 127916728606, failed at step 35, "Show the self-tests outside tools/audit/seat/ refusing their own fixtures". Log line 1007 is `SELF-TEST FAILED (...'the default verdict passes the live scopes': False ... 'the default invocation exits 0 on the live scopes': False ...)`, then `##[error]Process completed with exit code 1` (ev/job-127916728606.log, ev/job-127916728606-steps.txt).
- `## Red checks` against the live check runs of 4512d770, two pages, 107 runs (ev/checkruns-4512d770.tsv). The concluded reds are exactly the four the body names: instrument-self-tests 127916728606, pr-contract 127916741200, and `gate` 127919039308 (run 42216249923) and 127919030269 (run 42214982575). Each has the cause the body gives.
- Cheaper-detector claim:
  - `tools/pr/prepr.sh` contains no `check_scopes` (grep rc 1).
  - `check_scopes` runs only in `.github/workflows/governance.yml`.
  - `check_scopes --repo .` takes 1.21 s wall here (ev/check_scopes-timing.txt), against the body's 1.2 s.
  - The body names the detector, its standing cost, and the follow-up as a Forward-carry, so the trigger is answered.
- Other body figures re-derived at the head: `tests/replay_cost_draws.tsv` has 565 rows and 116 distinct jobs (csv reader, ev/draws-count.txt). That matches the body.
- Merge: `git merge-tree --write-tree origin/main 61ce00f0` rc 0, no conflict (ev/merge-tree.txt). The three-dot diff names 6 files (ev/threedot-names.txt).
- Entities (`PYTHONPATH=tests/hastub python3 tests/entities.py`): rc 0 at the head, `ALL 2640 ENTITY CHECKS PASSED`; rc 0 at main a2240924, `ALL 2637 ENTITY CHECKS PASSED` (null control).
- Structure: `tests/structure.py` at the head prints `STRUCTURE RATCHET PASSED`, rc 0.
- Carries: the packet's carry_audit routes both body items (the prepr follow-up and the ref47/51.12 residual) to R10-REPLAY-COST-2, which exists on origin/handoff/audit-r10-roster. Neither item's text is in that group yet: a scout search for check_scopes/prepr/51.12/ref47 in the group's strings found none. Landing them after the merge is owed, and both are restated under Findings.
- CI at the head, read live over all pages (68 check runs, ev/checkruns-61ce00f0-final.tsv):
  - The deciding CI run 42239004072 concluded `success`. Its `gate` 127988309283 is `success` (15:46:09Z).
  - Every `tests / *` unit is success or skipped, and so is `governance / instrument-self-tests` (now green: the red of round 4 is repaired in CI).
  - `pr-contract / pr-contract` 127987907573 started 15:44:52Z, after the last red concluded (15:07:55Z), and is `success`. By fix-review.md step 11 that green run is the evidence that the body answers the head's reds.
- `merge_train.py classify` still exits 1: `RED 61ce00f0... pending: none red: gate` (ev/classify-1.txt, classify-2.txt, classify-final.txt, classify-sweep-log.txt). The cause, read from the job logs:
  - The two edit-workset runs 42239005979 and 42239202136 each carry a `gate` that deferred to the deciding run (`FAIL run(s) [42239004072] at this head are still being judged; their gate decides`).
  - When the deciding run concluded, the gate sweep re-ran both deferring gates in the same second (15:46:32Z). Each then deferred to the other: job 127988798034 logs `FAIL run(s) [42239202136] ... their gate decides`, and job 127988804259 logs `FAIL run(s) [42239005979] ... their gate decides`.
  - This is the gate.py busy() mutual-deferral defect already on the roster as R10-HOTFIX-GATE-BUSY-DEFER (not started). It is not reachable from this diff, which touches no `tools/ci/` or workflow file.
  - I judge the head GREEN in substance. GitHub's ruleset refuses the merge while either deferring suite's `gate` is red, so the orchestrator (`hpo-runs`) must re-run ONE of the two gate jobs (not both at once) and see it `success` before merging. Re-running both together reproduces the deadlock.
- Mutation lane: the diff writes no production code line, so it draws no mutant, and `tests / mutation` is green. I did not rely on it.
- Seat instruments: no harness of my own was built. All the commands above are in-tree tools, run from detached worktrees of a2240924, 4512d770, 83579e22 and 61ce00f0.
- Head re-read at verdict time: the PR head is 61ce00f0404fd7a3c7ae999741ad306deb3f4bd3, and it did not move during the review.

## Findings

- Follow-up (the body's own): `tools/pr/prepr.sh` does not run `tools/audit/check_scopes.py --repo .` (1.21 s measured), so a tracked file in no audit universe reaches CI before it is caught. The text is not yet in the group's strings and must be landed. Carry: R10-REPLAY-COST-2
- Residual (the body's own): grading is one pooled ruler per job, so a ref47 runner whose job ruler reaches >= 51.12 is graded on ref53's budget 2.076. The text is not yet in the group's strings and must be landed. Carry: R10-REPLAY-COST-2
- Follow-up: at this head the two edit-workset `gate` jobs, re-run together by the gate sweep at 15:46:32Z (jobs 127988798034 and 127988804259), each deferred to the other's run, so the required `gate` stays red with no gate judging. This is a fresh reproduction for the fixer's failing test: runs 42239005979 and 42239202136 at 61ce00f0. A re-run of one gate alone is owed before this PR can merge. Carry: R10-HOTFIX-GATE-BUSY-DEFER

## Friction

- The frugal-routing PreToolUse hook refused plain inline Bash calls after five search operations in one prompt, so one roster lookup went to a scout subagent instead. Its result was checked by a second in-tree read.
