Fix review: blocked 44766207b74e16930c42c268c67380ed5c0ad951 ci-red: pr-contract / pr-contract red at the head because ## Red checks names budget-raise-gate, not the context budget-raise-gate / budget-raise-gate; gate fails on it

bus-nonce: cdb9ceef61edd0bcad73a28e4d540759

## Block

`merge_train.py classify 44766207b74e16930c42c268c67380ed5c0ad951 --pr 3642` printed `RED 44766207b74e16930c42c268c67380ed5c0ad951 pending: none red: gate` (rc 1, ev/classify.txt), not APPROVAL-OWED. `gate` (job 133004382380) lists two failures: `budget-raise-gate / budget-raise-gate`, which is the expected wait for the raise's approval, and `pr-contract / pr-contract` (job 133003629587), which printed `ERROR [pr-body] /tmp/pr-body.md: check \`budget-raise-gate / budget-raise-gate\` is red and \`## Red checks\` does not name it` (ev/pr-contract-tail.txt). The body's `## Red checks` bullet names `budget-raise-gate` only. Card C8 says a red head takes no merge verdict. The repair is a body edit only: name the full context in `## Red checks` and re-run `pr-contract`. The text and data diff passed every check below, so a re-review only needs to confirm classify reads GREEN or APPROVAL-OWED (`review_carry.py` on an unchanged diff).

## Findings

- Note: root-cause-detectable: pr-contract / pr-contract: `node tools/policy/policy_lint.mjs --pr-body <body>`, run locally in seconds with no added standing cost, would have caught the context-name mismatch before the handoff. The fixer answers this red under `## Red checks` when repairing the body. Carry: dismissed: the fixer's own repair of this head's body, owed before merge under the block above

## Evidence

- Round: first (no --reviewed-head). Role contracts unchanged between merge base and main.
- Mutation proof (step 1) re-run: with `policy_budgets.json` replaced by origin/main's copy, `policy_lint.mjs` printed `TOTAL: 3 error(s)`: whole corpus 70032 > 69833, D11 126 lines > 109, D11 1939 tokens > 1647. With the head's copy it printed `TOTAL: 0 error(s) across 52 policy file(s)` (ev/mutant-budgets.txt).
- Raise arithmetic (step 14): D11.md at the merge base measures 109 lines and 1647 tokens, with corpus ~69740. At the head it measures 126 lines, 1939 tokens and corpus ~70032. The corpus delta is 292, and 69333 + 292 = 69625, the recorded cap, so the raise covers only this diff's own growth (ev/base-budgets.txt). Payments: step 1 of D11 already carries the `policy_lint_mutants.mjs` / `--self-test` control column, so cutting the Detector-health bullet removes a real duplicate and loses nothing. I found no further payment that would not delete a finder's input. Archscore dS +0.0000 NULL is consistent with a text-only diff.
- Every body figure re-derived at the head: units command rc 0, 3952 units over 80 files; generated-copy overlap 376; multi-file sentences >60 chars 11; rulings awk exits 2 at the head; MODE: SCOPED -- 1 script(s) run, 32 scoped out; rules_sync ok; brief_lint rc 0; STRUCTURE RATCHET PASSED. The `11` used my own awk definition (unit text length > 60, at least two distinct files outside .claude/rules/), and it matched.
- #3626 has now merged (main 921214bf42), so the body's merge-order precondition holds. On main, RULINGS.md has 88 entries and 26389 bytes, matching the body. `git merge-tree --write-tree origin/main 44766207b74e16930c42c268c67380ed5c0ad951` is clean. In the merged tree, `policy_lint.mjs` prints 0 errors, corpus is ~70040 against a 70125 limit, and the units command yields 189 RULINGS.md units (ev/merged-tree.txt).
- Null control: `printf '# x\n## Superseded\n- a\n' | awk ...` printed 0.
- VERSION, the manifest and the notes heading are untouched; the diff is three files: policy_budgets.json, D11.md, delivery/3642.md. No claim file or fixture moved, so env_drift is not owed. This is a one-seam policy-text change: there is no finder's harness, and policy_lint's budgets class is the pinning check.
- Packet refusal `introduced-red` (instrument-self-tests in progress at render) is superseded by the live checks: the only failures are budget-raise-gate, pr-contract and gate.
