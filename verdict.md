Fix review: merge 3ffdfa633186ab6e9eadfde8bdcc2206cec3421f

bus-nonce: 660b69fb0213d5edd65e30c79327d7f5

## Summary

Review round 2 of PR #2937 (R10-FLY-CACHE-PROMPTS; repair round 1 after the mutation-vacuous block). Measured at head 3ffdfa633186ab6e9eadfde8bdcc2206cec3421f, which is still the PR head. The blocked mutant, ci-watch.sh loop `sleep "$POLL_S"` -> `sleep 300`, is now killed by the new self-test arm "the loop sleeps POLL_S between cycles" (slept 300, 1 failed); the line-deleted variant (slept never) and `POLL_S=300` are killed too, and the unmutated script passes (slept 240), the null control. No other named check regressed.

## Findings

- `reviewer-head-off` survives r10_flow_dispatch_mutants.py at the head (RESULT mutants=33 survived=1), pre-existing at the base per the body; dispatch_group's reviewer --head refusal stays unpinned after this merge. Carry: R10-FRICTION-MUTATION-SURVIVOR
- The cloud environment's python3 is /usr/bin/python3 3.11 and /opt/hpo/venv-ci/bin is not on PATH, so tests/entities.py fails with an f-string SyntaxError unless run under the venv (reproduced here; the body's Friction item). Carry: R10-FLY-SUITE-ENV-FLAKES

## Evidence

- Mutation proof (step 1): sleep 300 mutant killed; POLL_S=300 killed; no-sleep killed; restored file passes 15/15. Dispatch harness M0 null-ok at head and base; the body's pointer/publish/wait-line/claude-md mutants all read killed at the head.
- Figures re-taken at the head: cloud_dispatch 87/0, stop-selfcheck 29/0, policy_lint --hooks ok (3 hooks), ci-watch 15/0, proof_watch 43/0, structure ratchet passed, closure MODE: SCOPED -- 1 script(s) run. entities.py reads 2470 checks here against the body's 2467: the body took it at c9dfba06, before the main merge, so the number differs from the body's and the difference is not this diff's; it passes.
- Class enumeration (step 6): the body's grep rule and dispositions read; daemons and stubs left are dispositioned in the body.
- Merge (step 13): git merge-tree --write-tree origin/main head exits 0; origin/main 6493ea362 is the merge base.
- Step 5: VERSION, manifest, RELEASE_NOTES.md and goldens untouched.
- CI (step 11), live at return: all concluded gate checks green except governance / delivery-status. It is OVERDUE on other merged PRs' rows (#2921, #2910, #2873, #2909), not on this PR's row; its log says it is not a required context and a red there blocks no merge; by fix-review.md step 11 it is not this pull request's, so the packet's red-unanswered refusal on it does not block here. codeql / Analyze (python) and two prelude jobs were still in_progress at return; their conclusions are not re-read in this verdict.
- Code-owned paths (.claude/settings.json, .claude/hooks/): merge still needs @tvofi's approving review; this verdict does not supply it.
