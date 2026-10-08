Fix review: merge f118161532c4b3e1225cd739b0d28200e767c073

bus-nonce: 2a548b3bde122f8539cc31865253d17e

This is round 3. The measured head is `f118161532c4b3e1225cd739b0d28200e767c073`. It merges the authored head `4805fe7df` into the round-2 head `feaecbca2`; `origin/main` `af79f2114` is already contained. The delta since round 2 is three files: step 11's text, the token cap, and web-fix-wave.js:305.

## The rule, in the two places

- Step 11 now reads: "posted only once the head's workflows all concluded and a `pr-contract` run started after the last to conclude red, else the push-time run, checked the body (tvofi, 2026-10-08); while it refuses, wait or hand back unverdicted, saying so."
- web-fix-wave.js:305 has the same sentence. The only differences are the citation "(fix-review.md step 11)" in place of the date, and "Post it" in place of "posted". Both say what the coordinator's ruling says.

## Postable in every case

The case analysis rests on the trigger in `pr-contract-rerun.yml`: a re-run fires only when one of the watched workflows concludes red, and "PR contract" is not watched.

- **All green.** No workflow concludes red, so the push-time run counts. The condition holds as soon as everything has concluded.
- **A red, then a re-run.** The re-run starts after the red workflow concluded, so it qualifies. I checked the predicate on real data from the two earlier heads of this PR (`settle3.py`):
  - `e50d432ee`: the last red-workflow job ended at 18:01:12Z and the contract re-ran at 18:01:29Z. rc 0.
  - `feaecbca2`: the last red-workflow job ended at 18:23:24Z and the contract re-ran at 18:23:41Z. rc 0. At this head round 2's anchor was never met, because CodeQL went green at 18:40:11Z; the new anchor is met.
- **Class D.** The red is on an earlier commit and the head is green, so the push-time run counts.
  - With #2062's token, that run refuses an unnamed earlier red, and the reviewer waits or hands back.
  - Without the token, it prints `skip red-history`, and the "head's runs are not the range's" paragraph lets the reviewer block directly.
  - The body states both arms correctly.
- **The contract's own red.** If `pr-contract` is the only red at the head, it is "the last to conclude red". The rule then waits for a later contract run, which a body edit (`edited`) starts. That is the right outcome: the reviewer does not post while the contract refuses.

## RESULT lines

- RESULT policy_lint at head: `TOTAL: 0 error(s) across 40 policy file(s)`, rc 0 (`evidence3/policy_lint.head.txt`).
- RESULT structure.py at head: `STRUCTURE RATCHET PASSED`, rc 0.
- RESULT entities.py at head, run in the CI venv: `ALL 2212 ENTITY CHECKS PASSED`, rc 0.
- RESULT check-wave-script.mjs at head: `168 passed, 0 failed`.
- RESULT budgets at head: `fix-review.md` is at 141/141 lines and 2449/2449 tokens. The cap equals the measurement, so it is minimal for this text, and it is within tvofi's confirmed 142/2461. `orchestrator.md` is at 290 lines and 4096 tokens, unchanged.
- RESULT mutation, with the raise removed: 2 `[budgets]` errors, 141 > 140 lines and 2449 > 2393 tokens (`evidence3/mutant_no_raise.txt`).
- RESULT corpus: ~59624 tokens, within the band of 59591 + 500. The body states 59624.
- RESULT body and `## Head`: the body names `f118161532c4b3e1225cd739b0d28200e767c073`, which is the live head, with parents `feaecbca2` and `4805fe7df` as stated. The round-2 Head garbling is fixed. The RCA figures are cited correctly, as checked in round 1.
- RESULT `## Approval`: it records tvofi's option 2 and the "raise the cap" confirmation before the first push. It records the coordinator's two anchors under the mandate. It notes that tvofi's approving review is still required at the head. This is correct. The approval is the orchestrator's to give under mandate 5951564627; I have not given it here.
- RESULT CI at head, read from the commit's check-runs API (`evidence3/check-runs.2.json`, 42 runs). I posted under the new rule itself.
  - Every run had concluded; the last was `Analyze (python)`, at 19:34:01Z.
  - The last red-workflow run was `budget-raise-gate` (Budget raise gate workflow), concluding at 19:26:08Z.
  - The contract re-ran at 19:26:51Z, after it, and passed. That is the live "red, then re-run" case.
  - The red runs are `budget-raise-gate` x3 (owner approval pending) and `nightly-status` (main's). `## Red checks` names both.
  - `pr-contract` passed on all 3 runs.
  - Every other required check is green.
- RESULT VERSION, manifest and notes heading are untouched.

## Polish, not blocking

1. Read literally, "else the push-time run" names a run that a later body edit supersedes. If the push-time run refused and an `edited` run then passed, the literal reader waits forever. "the newest run" would say what is meant. The intent is clear from context.
2. The line `only once the head's workflows all concluded and a \`pr-contract\` run started after` is 86 characters, wider than the file's wrap. Reflowing would not save a line.
3. The `node --check` failure on web-fix-wave.js (an illegal top-level `return` at line 520 under ESM) is the same at main and at head (`evidence2/node-check.txt`). It was there before this PR, and the file is a workflow body by design.
