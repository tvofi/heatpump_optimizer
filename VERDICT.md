Fix review: merge aa095ec99497f4cd3c5c13bbc421768da5095ba1

bus-nonce: 620965e99cea9cad0b771e809b0df058

## Verdict

Round 1. Measured head aa095ec99497f4cd3c5c13bbc421768da5095ba1 (still `refs/pull/3336/head` when I finished), merge base bb7dfb9bd6c68548d1a956adc411be91e02965e0, three-dot diff of 3 files. The change tightens `score_check`: the section's last `Architecture score: dS` line has to match score.py's measured figure. Under the old rule (`want in got`) any line could match. No raise path or mandate path gets looser. Earlier lines are still checked for shape only, which the PR body states, and that matches the brief's carries 35c84a90 and 5/7.

## Findings

- Follow-up: a gap that predates this PR, in the gate's own self-test: the verdict-only mutant `if got and got[-1][1] == want[1]:` (compares the verdict word and ignores the dS) survives `budget_raise_gate.py --self-test` (274 checks, 0 failed). The analogue at the merge base (`if want[1] in [v for _, v in got]:`) also survives (273 checks, 0 failed). `merge_train.py --self-test` kills it ("a mandated raise whose body quotes a dS the scorer did not measure stops ..."), and the governance instrument-self-tests job runs that self-test, so CI does catch it. Still, the gate's own suite has no case for the same verdict word with a different dS. One check would close it, e.g. `TRUE_BODY.replace("+0.0000", "+0.0100")` expecting 1. Carry: R10-RAISE-GATE-SHIM
- Follow-up: decision 0013 (`dev/governance/decisions/0013-verdicts-post-as-the-approver-app.md`, "What the gate checks") still says the gate "checks the shape". It does not mention that the dS is checked, which earlier PRs already added, or that this PR now requires the head's figure to be the last score line. A raise body that is honest but lists the head's line first and the payments after it is now refused. The refusal text tells the author what to fix ("as the section's last score line"), but the policy text the author reads does not. Updating it is a policy change for the owner's review, and this PR's body already flags it as policy-adjacent. Carry: R10-RAISE-GATE-SHIM
- Residual, by design (declared in the PR body): a wrong figure placed before the true last line still passes, because the gate cannot tell it from a payment's own report. The true head figure is still enforced. Carry: dismissed: by design, payment lines report trees the gate cannot rebuild

## Evidence

- RESULT merge-tree: `git merge-tree --write-tree origin/main aa095ec9` exits 0 (tree df0b31234e6b), no conflict (ev/merge_tree.txt).
- RESULT CI: `merge_train.py classify` printed `GREEN aa095ec99497f4cd3c5c13bbc421768da5095ba1 pending: none red: none`, exit 0 (ev/classify.txt). Live check-runs: 68 total on one page, none concluded failure. Every run is success or skipped, budget-raise-gate, arch-score, gate, pr-contract and instrument-self-tests among them.
- RESULT self-tests at head: budget_raise_gate 274 checks, 0 failed. merge_train 564 checks, 0 failed. r10_mandate_guard_mutants 8 checks, 0 failed. At the merge base: budget_raise_gate 273 checks, 0 failed (ev/selftests_*.txt).
- Body figure merge_train `506 checks`: re-derived as 506 at the body's stated base 73365699a. At this head (after main merged in) the count is 564, and the difference comes from main's changes, not this diff. The 274 and 8 figures re-derive exactly.
- RESULT mutation proof (body's mutant): reverting to `if want in got:` makes the self-test fail with `FAIL score: a wrong figure after the true one is refused (carry 5)`, 274 checks, 1 failed. Restored: 0 failed. Reproduced.
- RESULT my own mutants on the changed predicate (ev/mutants.txt): `got[0] == want` killed (2 fails). `got[-1][0] == want[0]` (verdict-blind) killed (1). `got and want in got` killed (1). `if got:` killed (4+). `got[-1][1] == want[1]` (dS-blind) survives the gate's self-test and is killed by merge_train's self-test (see Findings).
- RESULT PR mutant harness at head: `r10_mandate_guard_mutants.py --null` gives rc=0 fails=0. B1 rc=1 fails=2, B2 rc=1 fails=12, B3 rc=1 fails=1, B4 (re-anchored) rc=1 fails=1, so `plants=4 killed=4` (ev/r10_mutants_head.txt).
- Null control: the merge base accepts the wrong-after-true body (shown by the mutant above, which is base semantics). The new self-test case "the true figure last, after a payment's own line, passes" still passes at head.
- RESULT architecture: `score.py --diff bb7dfb9bd aa095ec99` gives `Architecture score: dS +0.0000 NULL`. No worsening.
- Structure and budgets: no `*_budgets.json`, `tests/closures.json` or INERT change in the diff. VERSION, manifest and RELEASE_NOTES.md are untouched. The delivery row dev/programme/delivery/3336.md is in the diff. `## Head` names aa095ec9, which is the current head.
- tests/entities.py run plainly at head did not run clean: it exited 1 on `ModuleNotFoundError: No module named 'homeassistant'` at import (ev/entities_head.txt). With `PYTHONPATH=tests/hastub` at head: `ALL 2666 ENTITY CHECKS PASSED`, rc=0 (ev/entities_hastub_wt.txt). The new delivery row is classified (no FULL-forcing refusal).
- Red checks: no CI check on this head concluded red. The body's `## Red checks` covers a local prepr refusal and names it as environmental. Nothing needs a root-cause answer.
- Finder's harness: the brief's group names none. The gate's self-test and the PR's own mutant harness r10_mandate_guard_mutants.py are the instruments. I built no instrument of my own beyond the ad-hoc predicate mutants listed above.
- Forward-carry: the body says none, and the only open residual is the by-design one declared above.
