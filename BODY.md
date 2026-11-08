Closes the open part of R10-RAISE-GATE-SHIM carries 5 and 7: `score_check` accepted a `## Raise justification` that quoted a wrong figure beside the measured one. The section's LAST `Architecture score: dS` line (the head's claim) must now be the figure score.py measures; earlier lines stay the payments' own reports, shape-checked only (the contract asks for them). This is a small change to what a raise body must carry, so it is policy-adjacent: it needs the owner's review before merge.

Carries checked at merge base 73365699a (numbered 1-8 in order; the brief counts them 0-7):
- Carry 1 (brief 0: a, b, c): (a) covered by 1d4ed28e4, seat-gh refuses a #201 write unless gh_comment.py makes it, proved by #3223's seat-gh cases; (b) covered by 1200ce0a7 and 1b93076e0, `score_check` is read by the gate, `--check-body` with `--base/--head` and `merge_train.py` `raise_hold`; (c) waits, see Carry 3.
- Carry 2 (brief 1): covered by 1200ce0a7 and 1b93076e0: `score_check` refuses a body whose dS differs from `measured_score`; proved by `budget_raise_gate.py --self-test` ("score: a planted false IMPROVES under a mandate is refused") and merge_train's `planted_ds` case. The #3045 body exists only as the inline `PLANT` string, not a file.
- Carry 3 (brief 2): waits. #3223 measured the job at min 19 s, median 28 s, max 48 s of 300 s; no raise diff has run it, so the first raise PR's body should read its job duration. No change.
- Carry 4 (brief 3), Carry 5 (brief 4) and Carry 7 (brief 6): `exec -a` argv0 spoof, residual by design, recorded in `instruments/shims_seat-gh.md`; no fix in a ps-based check.
- Carry 6 (brief 5) and Carry 8 (brief 7): fixed here.

Alternatives: require every score line to equal the measured one (rejected: the contract asks for score.py lines per payment, so honest bodies would be refused); mark payment lines with a new prefix (rejected: grammar change across fixtures and the policy_lint arm). Residual: a wrong figure placed BEFORE the true last line passes, indistinguishable from a payment's own line.

## Head

92871ab22330adaf81912036add164f4e51fceec

## Mutation proof

Predicate `if got and got[-1] == want:` reverted to `if want in got:` in `tools/policy/budget_raise_gate.py`; `python3 -I tools/policy/budget_raise_gate.py --self-test` then prints `FAIL score: a wrong figure after the true one is refused (carry 5): got 0, want 1` and `274 checks, 1 failed`. Restored: `274 checks, 0 failed`.

## Null control

At the merge base the same wrong-after-true body passes (`want in got`), the mutant run above. A body whose last line is the true figure after a payment line still passes (case "the true figure last, after a payment's own line, passes").

## Figures

- `python3 -I tools/policy/budget_raise_gate.py --self-test` -> `274 checks, 0 failed`.
- `python3 -I tools/audit/seat/merge_train.py --self-test` -> `506 checks, 0 failed`.
- Mutant wall time and survivor count: not run beyond the hand mutation above; `tools/` sites are not in `mutation-autofix`'s lane.
- `python3 -I tools/audit/seat/r10_mandate_guard_mutants.py --self-test` -> `8 checks, 0 failed` (B4 re-anchored on the new predicate: a verdict-blind mutant, killed by the "same dS with another verdict word" case).

## Unpinned sites

The one added predicate is pinned by the hand mutation above (killed by the self-test case "a wrong figure after the true one is refused").

## Red checks

`prepr.sh` step closures refused: `tests/entities.py` exits 1 on 3 checks (the coverage-cache keying, the release ZIP build step, the Pages workflow probe), all environmental to this container. Null control: `PYTHONPATH=tests/hastub python3 tests/entities.py` on the unchanged base 73365699a prints the same `3 of 2665 ENTITY CHECKS FAILED` and the same three names (exit 1). Every prepr step before it was ok, including self-test 514 passed. No cheaper detector is claimed; the checks are inherited and named here.

## Forward-carry

Carries 0(c) and 2 (the raise-diff job duration of the budget-raise-gate job, unmeasured until a raise PR runs it): the first raise PR's body reads its job duration. Lands in dev/programme/rosters/wave-r10-groups.json. Carry: R10-RAISE-GATE-SHIM

## Friction

none
