Fix review: merge 960135738416bf6b23cc6552923c392ca9cedc2c

bus-nonce: d7b9da0aaa204d1fe6601a439354e76d

Round 2 review of #2625 (R10-RCA-BODY-LINT), measured at head 960135738416bf6b23cc6552923c392ca9cedc2c (still the PR head at post time; origin/main = merge base fef4a1351).

## Findings

- dev/audit/rca/R10-RCA-BODY-LINT.md section 6 quotes "338 passed, 0 failed" for the self-test (lines 182 and 193); at this head it is 337 (the PR body says 337). The doc records round 1's count and was not refreshed in round 2. Carry: dismissed: a stale count in a narrative record of round 1; the body's figure is the one that binds and re-derives.

## Evidence

- Round 1 block resolved: the red `instrument-self-tests` (ref_privacy unregistered push site in tools/pr/prepr.sh) is named and answered in the body's Red checks (cheaper detector: ref_privacy.py --check), and r2 registers prepr.sh in PUSHERS as fixture. `ref_privacy.py --check` at this head: only refusal is the RCA doc line 3 home-directory, which is this host's uid-0 /root and not CI's (CI instrument-self-tests was still running when read; no red).
- The RCA's demonstration (replay of five refused bodies, null control a4c998f1) is in the doc section 6 and the body; the self-test arms are the planted-defect proof: a body with a pathless carry and an unparseable Friction line is refused with both ERROR lines and nothing pushed; the passing body with the session link pushes.
- Mutation proof re-run (PREPR_SKIP_CLOSURES=1 prepr.sh --self-test, venv-ci python 3.13): unmutated 337 passed, 0 failed (M0). BP-SKIP (lint call -> if false &&): 335 passed, 2 failed (refusal arm, session-link push arm). BP-HEADEQ (head-equality -> true): 336 passed, 1 failed (not-the-head arm). Both match the body. RE-SESSION and LOG not re-run; policy_lint --self-test FIXTURE ok and policy_lint_mutants.mjs MUTANTS ok.
- Forward-carry: roster branch handoff/audit-r10-roster holds a46a37a87 (pinned-grader base-copy carry, with its control) and 5ba47bffc (figure_lint --pr-body at body push, with its control), both R10-FLOW-JIDOKA, both naming #2625; the prepr.sh-copy carry is also on the branch tip.
- Diff does not touch dev/programme/rosters/wave-r10-groups.json (three-dot diff from the merge base: 0 matches). VERSION, manifest, RELEASE_NOTES, tests/golden untouched.
- Merge: git merge-tree --write-tree origin/main HEAD exits 0 (clean).
- fold_ledger.py check: 0 violations. The class N-body-lint-bounce is registered in bugclasses.json, finding.schema.json and audit-find.js (wave-script check green in CI).
- CI at head from check-runs: success: pr-contract (both), wave-script, policy-docs, env-matrix, delivery-status, budget-raise-gate, arch-score, mutation, closure-scope, typing, browser, validate-hacs. In progress when read: closures, fast (3.14), coverage, instrument-self-tests, Analyze (python). Red: nightly-status only, which is main's known NIGHTLY ABSENT and is not a required check and does not block; this diff touches nothing it reads. Per the contract I did not re-run heavy lanes.
- Not re-derived: the five-body replay table and --body-check timings (round 1 figures; their files are unchanged since).
