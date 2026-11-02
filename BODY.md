Part 1 of R10-DEPS-ACTIONS-BUMP (replaces dependabot #3087, never edited). CI grades `governance/policy-docs` with main's copy of `dev/audit/rounds/round6/D11/fix/codeowners_gap.py`, whose `ALLOWED_USES` admits a step before a pinned grader only at exact action revisions; a PR cannot widen the allowlist and bump the actions in one change (the bump alone makes `--check` refuse 18 uncovered files). This PR widens the allowlist to admit both the current and the bumped revision of checkout, setup-python, setup-node and download-artifact. Part 2 (the workflow bumps) follows once this is on main. No workflow, no claim file, no `tests/entities.py` change.

SHAs re-verified against upstream tags with `git ls-remote https://github.com/actions/<name> refs/tags/<tag>`: checkout v7.0.1 = 3d3c42e5, setup-python v7.1.0 = 6d4fd22b, setup-node v7.1.0 = 949feb24 (also main's tip), download-artifact v8.0.2 = 9000827c; all lightweight tags, so no dereference needed.

`tests/entities.py`: its exact graders-head-copy literal must match `tests.yml`. Part 1 does not change `tests.yml`, so the literal stays at the current revisions and still matches (entities.py unchanged, run in the scoped gate). Part 2 changes `tests.yml` and the literal together, as commit ac737333 did in the saved work, so it matches at Part 2 too.

## Head

99835eadcf0d06e371f65c940bf7641fce7f9a3f

## Mutation proof

Run from this head: `python3 -W ignore dev/audit/rounds/round6/D11/fix/codeowners_gap.py --self-test`. Mutant 1: delete the `actions/setup-node@949feb24...` line from ALLOWED_USES: the self-test prints 1 FAIL (`NULL setup-node at its bumped pin: grader not pinned`). Mutant 2: delete the `actions/download-artifact@9000827c...` line: 1 FAIL (`NULL download-artifact at its bumped pin`). Both restored; the self-test then prints `0 wrong`.

## Null control

At this head `--self-test` prints `SELF-TEST: 55 probe(s), 15 null(s), 0 wrong` and `--check` prints `uncovered_files=0`. Nulls: each of the four actions at its current and its bumped revision leaves the grader PINNED. Probes: each bumped SHA one character off (checkout, setup-python, setup-node, download-artifact) leaves it not pinned, so any other revision still refuses.

## Figures

- `python3 -W ignore dev/audit/rounds/round6/D11/fix/codeowners_gap.py --self-test` : 55 probes, 15 nulls, 0 wrong.
- `python3 -W ignore dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` : uncovered_files=0.
- `python3 tests/structure.py` : STRUCTURE RATCHET PASSED.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` : MODE: SCOPED, scope.run = tests/entities.py, tests/harness_headers.py.
- Main has not moved since the base: origin/main = 94d8b47f.

## Red checks

none

## Forward-carry

none

## Friction

none
