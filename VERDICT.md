Fix review: blocked 0e12b4f8a007f9ead26584ad6f261aade0255d64 metric-gamed: policy_budgets.json: fix-review.md's line cap 140->141 is no longer earned after the recarry (it measures 140, which main's cap holds), and the token cap 2449 sits 3 above the measured 2446

bus-nonce: 79c82a7d6024d0042b0e4748b13eb66b

This is round 4, a delta review of the recarry. The measured head is `0e12b4f8a007f9ead26584ad6f261aade0255d64`. Its parents are `f11816153` (the round-3 merge head) and `bd59a4af1` (main, which merged #2064).

Against main, the three-dot diff has the same 5 files as before. The policy text in step 11, the `web-fix-wave.js` prompt and `orchestrator.md` section 11 is unchanged from round 3. Only the caps came from the conflict resolution.

## The block (step 14)

When #2064 merged, it trimmed `fix-review.md`. At main `bd59a4af1` the file measures 137 lines and 2384 tokens, against caps of 140 and 2393. With this PR's step-11 text, the merged file measures **140 lines and 2446 tokens** (`evidence4/budgets.head.full.txt`).

Take the step-11 text away and the line cap's movement still stands, so the movement was not earned:
- With main's caps of 140 and 2393 restored, `policy_lint` reports **1** error, the token cap only (`evidence4/mutant_main_caps.txt`). The line raise from 140 to 141 is not needed.
- With caps of 140 and 2446, `policy_lint` reports `TOTAL: 0 error(s)` (`evidence4/minimal_caps_140_2446.txt`).

The minimal raise is now **tokens only, 2393 to 2446**. The line cap stays at main's 140.

The resolution kept the round-3 caps of 141 and 2449. That loosens a cap by 1 line and 3 tokens beyond what the change uses. Rule 2 of `CLAUDE.md` and `ratchet-budgets.md` allow a raise only by what the change needs.

This came from the merge, not from intent. The fix is two numbers in `dev/governance/config/policy_budgets.json`. It stays within tvofi's confirmed 142 and 2461, so no new owner ask is needed.

**The body is wrong in the same place.**
- `## Approval` still says "141 and 2449. That is exactly what the new text measures". Its own `## Mutation proof` says the text measures 140 and 2446.
- `## Mutation proof` says "#2064 touches neither `fix-review.md` nor the step-11 text". It does touch `fix-review.md`: +4 and -5 lines from the merge base `af79f2114` (`git diff af79f2114 bd59a4af1 -- dev/governance/roles/fix-review.md`). That edit included the step-11 paragraph's closing sentence, which now reads "(`root-cause.md`'s)", and it added step 15.
- So the raise-removed bullets are not carried over unchanged. My re-measure at this head replaces them: with main's caps there is 1 error, tokens only.

This is round 4. Under `fixer.md`, that means a re-cut of the caps and of the `## Approval` and `## Mutation proof` figures, not a patch.

## Steps 11 and 15 read together

- Step 11, the settle-then-post timing for `root-cause-unanswered`, survived the merge byte-for-byte. Main's own edit to its closing sentence ("You check that the trigger was answered, not the answer (`root-cause.md`'s)") sits under it and does not conflict.
- Step 15, "Judge `fixer.md` step 17 on added lines ... `blocked <sha> architecture-unsound: <how>`", is a separate verdict class with no timing condition.
- Neither step refers to the other, and nothing in step 11 constrains when an `architecture-unsound` block may be posted. They are coherent.
- `architecture-unsound` is in `web-fix-wave.js`, and the wave prompt's step-11 sentence is unchanged from round 3.

## RESULT lines

- RESULT `policy_lint --budgets` at head: rc 0. `fix-review.md` is at 140 of 141 lines and 2446 of 2449 tokens. `fixer.md` is at 315 of 315 and 5216 of 5216, main's caps. `orchestrator.md` is at 290 of 291 and 4090 of 4096. Corpus ~59973, within its band of 60091.
- RESULT `policy_lint` at head: `TOTAL: 0 error(s) across 40 policy file(s)`, rc 0.
- RESULT `structure.py`: `STRUCTURE RATCHET PASSED`, rc 0.
- RESULT `entities.py` (CI venv): `ALL 2227 ENTITY CHECKS PASSED`, rc 0.
- RESULT `check-wave-script.mjs`: `170 passed, 0 failed`.
- RESULT main `bd59a4af1`: `fix-review.md` is at 137 of 140 and 2384 of 2393 (`evidence4/budgets.main.txt`).
- RESULT `## Head`: correct. It names `0e12b4f8a` and its real parents, and correctly states the conflict resolution for `fixer.md`.
- RESULT CI was read from the check-runs API (`evidence4/check-runs.6.json`). I posted under step 11's own rule: every run had concluded, and the contract re-ran at 23:46:29Z, after the last red workflow concluded at 23:46:14Z. The reds are `budget-raise-gate` x2 (owner approval pending) and `nightly-status` (main's), and `## Red checks` names both. `pr-contract` is green on every run.
