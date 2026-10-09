Fix review: merge 7c1d3b1b740b52615e937634dc263848f1ddab0e

bus-nonce: 0df70189561cd97c4469ac6befd27f5b

Round 5 is a delta review from `0e12b4f8a`. The measured head is `7c1d3b1b740b52615e937634dc263848f1ddab0e`, a single commit on `0e12b4f8a`. Its only change is to `dev/governance/config/policy_budgets.json`: `fix-review.md` goes from 141 to 140 lines and from 2449 to 2446 tokens. `origin/main` `bd59a4af1` is contained. The policy text (step 11, `web-fix-wave.js:305`, `orchestrator.md` section 11) is unchanged from round 3. Round 4 checked it at the merged tree and found it coherent with step 15.

## Round-4 block resolved

- The three-dot budget diff against main is now one line, `fix-review.md` tokens 2393 to 2446 (`evidence5/budget-diff.txt`). The line cap equals main's 140.
- `--budgets` at head: `fix-review.md` is 140 of 140 lines and 2446 of 2446 tokens. rc 0.
- Cap 2445 gives 1 error, so the token cap is the minimum (`evidence5/mutant_2445.txt`).
- Main's caps (2393) give 1 error, tokens only, so the raise is needed and the line cap is not (`evidence5/mutant_main_caps.txt`).
- Null control: with main's caps and `fix-review.md` reverted to main, `TOTAL: 0 error(s)` (`evidence5/control_reverted.txt`). The raise is used only by this PR's text. This re-measure is after #2064's merge, which settles the body's bullet marked "carried from before that merge".

## Body

- `## Approval` now says the raise is tokens only, 2393 to 2446, line cap at main's 140, within tvofi's confirmed 142 and 2461. That is correct.
- The false "#2064 touches neither fix-review.md" claim is gone. The bullet carried from before the merge is marked as such, and my control above re-runs it at this head.
- `## Head` names `7c1d3b1b7` and its parent chain correctly.
- The corpus is 59911 to ~59973, within its band, as stated.

## RESULT lines

- RESULT `policy_lint`: `TOTAL: 0 error(s) across 40 policy file(s)`, rc 0.
- RESULT `policy_lint --budgets`: rc 0.
- RESULT `structure.py`: `STRUCTURE RATCHET PASSED`.
- RESULT `entities.py` (CI venv): `ALL 2227 ENTITY CHECKS PASSED`.
- RESULT VERSION, the manifest and the notes heading are untouched.
- RESULT `## Approval`: tvofi's approving review at the head is still owed (`budget-raise-gate`, code-owner rule). It is not given here.
- RESULT CI was read from the check-runs API (`evidence5/check-runs.4.json`, 40 runs). I posted under step 11's own rule.
  - All 40 runs concluded, the last at 00:18:50Z.
  - The last red workflow concluded at 00:04:15Z, and the contract re-ran after it at 00:09:02Z and passed.
  - The red checks are `budget-raise-gate` x2 (owner approval pending) and `nightly-status` (main's). The body's `## Red checks` names both.
  - Every other required check is green.
