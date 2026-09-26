# Review brief: round-9 readiness R4b (web-fragments gate-lease text)

Before doing any work, read `CLAUDE.md` in the repository and all related rules files (`.claude/rules/`, and the role contract for your seat under `tools/audit/briefs/`), and follow them. Pass this rule on in every sub-agent brief you write.

Never refer to the project owner as "Tim" anywhere, especially on the public repository (PR bodies, commits, comments, issues, delivery notes). Call them "tvofi". A PR body's attribution line is `_Requested by **tvofi**_` and carries no claude.ai project link. Pass this rule on in every sub-agent brief you write.

Role: adversarial fix reviewer, `tools/audit/briefs/fix-review.md`. Cloud seat: no GitHub writes. Verdict back as text in fix-review.md's form (`merge <sha>` / `blocked <sha> <reason>`) via the coordinator; the Mac posts it as hpo-approver. Review the PR head the coordinator names if a PR is open (Mac adds only a docs/delivery row; state whether the authored diff is byte-identical to the code head below).

- Branch `handoff/r9-r1a-find-checker`. Code head `a897272a`; last commit `14b9f803` adds the PR body `tools/audit/handoff/r9-r1a-find-checker.md` (stripped before push). Base 81f2c18c.

- Branch `handoff/r9-r4b-web-fragments`. Code head `26b51272aca3fc62781bd5dfc2d640ebe853e1f3`; last commit `e3872880` adds the PR body (stripped before push). Base 81f2c18c.
- Ask: `.claude/workflows/web-fragments.md`'s GATE fragment and its four `web-*.js` copies said `run.sh` "holds flock for the gate run and renews the lease before every script"; since v6.7.0 run.sh leases each stress.py run alone. Make them agree with `.claude/rules/gate-scoping.md`, citing it.
- Test, don't trust: the claim is false at base (read tests/run.sh `leased()`, `gate_lock.py needs-lease`); the copies were copied out by a scratch script using the sync check's boundary rule (fragments_sync.mjs has no write mode) — confirm with `node .claude/workflows/fragments_sync.mjs` and its --self-test, and by mutating one copy; nothing kept from the old fragment is now wrong (MODE: FULL explanation, "never remove a lock you did not create", process-count rule); no other live stale text (`git grep -n -E "holds flock|renews the lease|TAKE THE LOCK|NO LOCK"` outside tools/audit/round*). Run entities.py (the scoped selection), policy_lint (+ --budgets, no cap raised), rules_sync --check, check-wave-script, structure.py, prepr.sh, and codeowners_gap.py --check (R1a was blocked on it).
- Code-owned policy (web-fragments.md, web-fix-wave.js @tvofi) → tvofi approval under mandate 3 (to 09:35Z) on your merge verdict + green CI.
