R10-HOTFIX-DELTA-REVIEW, repair of #3379 after its blocked verdict (scope-rule-widened). Owner ruling (tvofi 2026-11-09): "I though it was always only the delta that was reviewed in later review rounds? If not, make it so", with the exception "only if the delta touches production code in a way such that the functionality of the other already reviewed code has a risk of being affected in a non obvious way that CI would not detect". A later round covers `git diff <reviewed-head> <head>`, each prior finding resolved and the live required checks. Only a delta touching production code (`custom_components/`) that puts already-reviewed code's functionality at non-obvious risk, in a way CI would not detect, widens it, to exactly that code; the verdict names the path and the risk. Instrument, test, policy and body deltas never widen it. The wording is the same in fix-review.md step 12, the packet's scope line (review_packet.py) and the reviewer prompt (cloud_dispatch.py). The unrelated compression of steps 6, 8, 9 and 13 is reverted (step 9 keeps "not the finder's").

## Head

e03c12274504ad7ede68b6f09b235029b990e404

## Mutation proof

`python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py` ends `MUTANTS: 9 run, 0 not as required`: M0 (unmutated head) PASS, M1 to M8 KILLED. M7 drops the exception's production-code qualifier from the scope line and M8 puts the wider trigger wording back; each turns the new wording self-test red in review_packet.py (`FAIL the packet's scope line: the exception names production code, non-obvious risk and CI's blindness, and the wider trigger wording is absent`) and for step 12.

## Null control

The unmutated head passes the wording check: step 12 and the scope line carry `custom_components/`, `non-obvious` and `CI would not`, and carry neither `reaches code that review relied on` nor `in full`. M0 is PASS. A first round still renders the full diff (review_packet self-test).

## Figures

- `python3 -I tools/audit/seat/review_packet.py --self-test`: `81 checks, 0 failed`.
- `python3 dev/audit/harnesses/r10_hotfix_delta_review_mutants.py`: `MUTANTS: 9 run, 0 not as required`.
- `node tools/policy/policy_lint.mjs --budgets`: the fix-review.md row reads 143 lines and 2549 tokens, equal to its caps.
- `python3 tools/audit/archscore/score.py --diff origin/main`: `Architecture score: dS +0.0000 NULL`.

## Raise justification

Raise: dev/governance/config/policy_budgets.json caps for tools/audit/briefs/fix-review.md, lines 140 to 143 and files_tokens 2451 to 2549, the values `policy_lint.mjs --budgets` measures at this head; `_band` is not widened. The orchestrator approved it under mandate 6715477401, scope all.
Payments tried: compressing other prose in fix-review.md to fit the old caps. Refused: the blocked verdict named exactly that compression of steps 6, 8, 9 and 13 as scope creep, so paying with it would re-open the block.
Architecture score: dS +0.0000 NULL

## Approval

This change to `dev/governance/roles/fix-review.md` step 12 carries out the owner's ruling (tvofi, 2026-11-09): "I though it was always only the delta that was reviewed in later review rounds? If not, make it so". The ruling is not the approval. Merging still needs the owner's approving review at this PR's head (code-owner rule, decision 0009 step 6); the same review covers the two cap raises under `## Raise justification`.

## Red checks

`budget-raise-gate` is red by design: two cap raises (lines 140 to 143, files_tokens 2451 to 2549 for tools/audit/briefs/fix-review.md) stay red until tvofi approves at the head, which the code-owner rule requires. The cheaper detector is \`node tools/policy/policy_lint.mjs --budgets\`, which already prints the measured figures and the cap; it cannot approve a raise, so the standing cost is one owner review per raise. No cheaper detector for the approval exists: the finding is that the step 12 rule cannot be stated in fewer lines without the compression the blocked verdict refused.

## Forward-carry

none

## Friction

none
