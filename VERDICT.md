Fix review: blocked feaecbca27864f6b4b05c74e690ebe7eecbbff41 other: step 11's anchor (a pr-contract run started after the head's workflows) never arrives when the last workflow concludes green, as at this head and in every class-D case, so root-cause-unanswered becomes unpostable

bus-nonce: a613ed120de0fa6c7b5427a391854811

This is round 2. The measured head is `feaecbca27864f6b4b05c74e690ebe7eecbbff41`. It merges `fa9ee29c2` into the round-1 head `e50d432ee`, and main is not re-merged. The delta since round 1 touches 3 files: fix-review.md, policy_budgets.json and web-fix-wave.js.

## Round-1 contradiction: gone

Step 11 now says the block is "posted only once the head's workflows concluded and a `pr-contract` run started after them re-checked the body". The "Never wait on coverage" sentence is removed. Because the wait is now keyed on workflows, not on required checks, it matches what `pr-contract-rerun.yml` actually does, which is to fire on `workflow_run: completed`. A wait for `coverage` is now implied, and it is the cost the RCA states. The contradiction is resolved.

## The block: class D is not answered, it is made unpostable

`pr-contract-rerun.yml` re-runs the contract only in one case:

- The triggering workflow concluded `failure`, `timed_out` or `cancelled`. This is its `if:`.
- The triggering workflow is one of "Budget raise gate", "CodeQL", "Governance", "Hassfest", "Tests" or "Validate". "PR contract" is not in that list.

Take a head where every workflow concludes green. No re-run fires there, so no `pr-contract` run ever starts after the head's workflows concluded. A body edit (`edited`) would start one, but nothing in the text asks for an edit.

That is exactly the class-D shape. The RCA, at lines 84-86, says "Every autofix commit is this shape": the red is on the commit below, and the autofix head itself is green.

The body's answer is that "a push-time run that started before the head's workflows concluded does not count as the re-check". That settles which run counts. It also guarantees that, on a green head, no run counts.

So the reviewer is left like this:

- It may not post `root-cause-unanswered`, because the condition never arrives.
- "While that run refuses the body, wait or hand back" does not apply, because "that run" does not exist.
- The text names no exit. Waiting forever and returning `merge` over an unanswered earlier-commit red are both readable from it.

Before this PR, step 11's "The head's runs are not the range's" paragraph let the reviewer block such a head directly. #2062's token makes the push-time run refuse such a body, but under the new anchor that refusal is precisely the run that "does not count".

A suggested repair costs about one clause and is for the fixer or coordinator to choose. Either:

- add "where any of them concluded red", and otherwise let the newest run at the head count; or
- say that when no re-run comes, the reviewer hands back asking for a body touch, which starts an `edited` run.

The same text is now in web-fix-wave.js:305, so the repair goes in both places.

## RESULT lines

- RESULT web-fix-wave.js:305 matches step 11. Both carry the same condition, "head's workflows concluded and a pr-contract run started after them re-checked the body; while that run refuses the body, wait or hand back ... saying so". This includes the class-D gap above.
- RESULT `node --check` on web-fix-wave.js fails in the same way at main `af79f2114` and at head `feaecbca2`, so this PR did not cause it (`evidence2/node-check.txt`):
  - Plain `node --check` stops at line 4, `export`, because the file is parsed as CommonJS.
  - `node --input-type=module --check` stops at `[stdin]:520` with `SyntaxError: Illegal return statement`.
  - The file is a workflow-script body, and its trailing top-level `return` is by design.
  - Its own checker, `node tools/policy/check-wave-script.mjs`, reports `168 passed, 0 failed` at head (`evidence2/wave-script.head.txt`).
- RESULT policy_lint at head: `TOTAL: 0 error(s) across 40 policy file(s)`, rc 0.
- RESULT structure.py at head: `STRUCTURE RATCHET PASSED`, rc 0.
- RESULT entities.py at head: `ALL 2212 ENTITY CHECKS PASSED`, rc 0. This was run in the CI venv with `PYTHONPATH=tests/hastub:custom_components:tests`.
- RESULT budgets at head: fix-review.md is at 141/141 lines and 2442/2442 tokens. The raise is minimal for this text. orchestrator.md is at 290 lines and 4096 tokens.
- RESULT mutation, raise removed: 2 `[budgets]` errors, 141 > 140 and 2442 > 2393 (`evidence2/mutant_no_raise.txt`).
- RESULT corpus: ~59617 tokens, which is inside the 500-token band of cap 59591 (60091). The body now states this, and the figure matches.
- RESULT RCA figures: unchanged from round 1, and the body still cites them correctly.
- RESULT `## Approval`: the coordinator's anchoring under the round-9 mandate is recorded. tvofi's "raise the cap" covered 142/2461, and the cap is now lower at 141/2442. The section is correct. Owner approval at the head is still needed and has not been given here.
- RESULT CI was read from the commit's check-runs API, in `evidence2/check-runs.*.json`. Every run at the head completed, with the last at 18:40:11Z. The red workflows were Tests (`nightly-status`) and Budget raise gate. The contract re-ran at 18:23:41Z, after the last red workflow concluded at 18:23:24Z. The reds are `budget-raise-gate` x2 and `nightly-status`, and both are answered in `## Red checks`. `pr-contract` is green on both runs. I posted at that point; this verdict is not a `root-cause-unanswered`, so step 11's timing does not govern it.

## This head demonstrates it

The gap is not limited to class D. At this head the last workflow to conclude was CodeQL, with `Analyze (python)` green at 18:40:11Z. A green conclusion triggers no re-run, so the newest `pr-contract` run, at 18:23:41Z, started **before** "the head's workflows concluded". Read literally, step 11's condition is unmet here and can never be met: I polled 3 times through 18:51Z, and the details are in `evidence2/settle.txt`.

The re-check that matters did happen. It ran after the last **red** workflow, which ended at 18:23:24Z. So the anchor wants to be "a `pr-contract` run started after the last of them to conclude red", or simply "none concluded red".

As written, any head whose slowest workflow is green blocks the very post the rule governs. CodeQL is routinely the slowest: 23 min here, against 6 min for `closures`. That makes this most heads.

## Non-blocking

1. The `## Head` text says the head "then merges origin/main `af79f2114` ... into this PR's previous head". The head's parents are `e50d432ee` and `fa9ee29c2`, and main was merged earlier, in `0cff5a993`. The template wording is garbled, but the SHAs it names are right.
