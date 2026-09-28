# Review brief: round-9 readiness R3a (verify checker)

Before doing any work, read `CLAUDE.md` in the repository and all related rules files (`.claude/rules/`, and the role contract for your seat under `tools/audit/briefs/`), and follow them. Pass this rule on in every sub-agent brief you write.

Never refer to the project owner as "Tim" anywhere, especially on the public repository (PR bodies, commits, comments, issues, delivery notes). Call them "tvofi". A PR body's attribution line is `_Requested by **tvofi**_` and carries no claude.ai project link. Pass this rule on in every sub-agent brief you write.

Role: adversarial fix reviewer, `tools/audit/briefs/fix-review.md`. Cloud seat: no GitHub writes. Verdict back as text in fix-review.md's form (`merge <sha>` / `blocked <sha> <reason>`) via the coordinator; the Mac posts it as hpo-approver. Review the PR head the coordinator names if a PR is open (Mac adds only a docs/delivery row; state whether the authored diff is byte-identical to the code head below).

- Branch `handoff/r9-r1a-find-checker`. Code head `a897272a`; last commit `14b9f803` adds the PR body `tools/audit/handoff/r9-r1a-find-checker.md` (stripped before push). Base 81f2c18c.

- Branch `handoff/r9-r3a-verify-checker`, stacked on R1a (`c6ca4132`, PR #1633). Code head `9fd82c91`; body commit `518c333a` (stripped). Pushed as a PR only after #1633 merges; review the PR head then.
- Why split: the required `wave-script` context restores `check-wave-script.mjs` from the BASE before grading, and the base checker runs `audit-verify.js` pinning round 8's shape (one verifier per dim, a stub providing only `pipeline`). Verify that.
- Content: only `.claude/workflows/check-wave-script.mjs`. Round-8 pins run only while `// PANEL:BEGIN` is absent from audit-verify.js; the new block evaluates the panel rules and runs the driver with stubbed agents: three lens verifiers per group; a 16-finding dimension split in two along a finder-seat boundary; killed never reaches the judge, disputed does, marked; dedup → runners → verdicts; one sweep per class, RCA at ≥3; no filing unless args.file; empty verifier re-run once; `from: "judge"` path. Rotation-yield block passes `parallel`; two stale comments fixed.
- Test: can a driver dodge the new block by renaming PANEL markers (should fail closed, as R1a's DISPATCH did)? Checker passes with main's driver, R3's driver (`241a480f`), and R3's + R1's audit-find.js; seven claimed driver mutants each exit 1 — pick your own too. Run codeowners_gap.py --check (R1a was blocked on it), policy_lint, prepr.sh, closure.py select.
- Spec: PLAN.md §5, §6, §8.1; tools/audit/briefs/verifier.md and judge.md (merged #1627). Not code-owned (verify vs CODEOWNERS).
