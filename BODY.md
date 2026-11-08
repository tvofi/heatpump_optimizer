Closes the open part of R10-RAISE-GATE-SHIM carries 5 and 7: `score_check` accepted a `## Raise justification` that quoted a wrong figure beside the measured one. The section's LAST `Architecture score: dS` line (the head's claim) must now be the figure score.py measures; earlier lines stay the payments' own reports, shape-checked only (the contract asks for them). This is a small change to what a raise body must carry, so it is policy-adjacent: it needs the owner's review before merge.

Carries checked at merge base 73365699a:
- Carry 0(a): covered by 1d4ed28e4 (seat-gh refuses a #201 write unless gh_comment.py makes it), proved by seat-gh cases in `tools/audit/seat/shims` selftests from #3223.
- Carry 0(b) and carry 1: covered by 1200ce0a7 and 1b93076e0. `score_check` compares the body's dS and verdict with `measured_score` (the base's scorer, three-dot); the gate, `--check-body` with `--base/--head`, and `merge_train.py` `raise_hold` (`g.justified(..., measured_score)`) all read it. Proved by `budget_raise_gate.py --self-test` ("score: a planted false IMPROVES under a mandate is refused") and merge_train's `planted_ds` case. The #3045 body exists only as the inline `PLANT` string, not a file.
- Carry 0(c) and carry 2: waits. #3223 measured the job at min 19 s, median 28 s, max 48 s of 300 s; no raise diff has run it, so the first raise PR's body should read its job duration. No change made.
- Carries 3, 4, 6 (`exec -a` argv0 spoof): residual by design, recorded in `instruments/shims_seat-gh.md`; no fix in a ps-based check.
- Carries 5 and 7: fixed here.

Alternatives: require every score line to equal the measured one (rejected: the contract asks for score.py lines per payment, so honest bodies would be refused); mark payment lines with a new prefix (rejected: grammar change across fixtures and the policy_lint arm). Residual: a wrong figure placed BEFORE the true last line passes, indistinguishable from a payment's own line.

## Head

b27acc1452b9825fb9037b8cc3526867ee5dc198

## Mutation proof

Predicate `if got and got[-1] == want:` reverted to `if want in got:` in `tools/policy/budget_raise_gate.py`; `python3 -I tools/policy/budget_raise_gate.py --self-test` then prints `FAIL score: a wrong figure after the true one is refused (carry 5): got 0, want 1` and `274 checks, 1 failed`. Restored: `274 checks, 0 failed`.

## Null control

At the merge base the same wrong-after-true body passes (`want in got`), the mutant run above. A body whose last line is the true figure after a payment line still passes (case "the true figure last, after a payment's own line, passes").

## Figures

- `python3 -I tools/policy/budget_raise_gate.py --self-test` -> `274 checks, 0 failed`.
- `python3 -I tools/audit/seat/merge_train.py --self-test` -> `506 checks, 0 failed`.
- Mutant wall time and survivor count: not run beyond the hand mutation above; `tools/` sites are not in `mutation-autofix`'s lane.

## Unpinned sites

The one added predicate is pinned by the hand mutation above (killed by the self-test case "a wrong figure after the true one is refused").

## Red checks

`prepr.sh` step closures refused: `tests/entities.py` exits 1 on 3 checks (the coverage-cache keying, the release ZIP build step, the Pages workflow probe), all environmental to this container. Null control: `PYTHONPATH=tests/hastub python3 tests/entities.py` on the unchanged base 73365699a prints the same `3 of 2665 ENTITY CHECKS FAILED` and the same three names (exit 1). Every prepr step before it was ok, including self-test 514 passed. No cheaper detector is claimed; the checks are inherited and named here.

## Forward-carry

none. The carries 0(c)/2 wait for the first raise PR's job duration; carried in the roster by the existing group entry.

## Friction

none
