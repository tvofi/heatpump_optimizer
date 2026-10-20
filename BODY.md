The record beat's generator (`tools/audit/seat/record_row.py`) wrote a `## Red checks` section that answered `record` alone. A record pull request rewrites delivery rows that already existed, which voids the main-state reporters' exemption in `policy_lint.mjs` (#2028), so `pr-contract` refused the body whenever `nightly-status` or `delivery-status` was red in the range. #2484 at `623392567da26a16a887a9162aec3bfde2b9d981` is the measured case; a hand-edited body is undone by the next beat, so the generator is fixed and run. The second commit re-points the self-test's citation of `policy_lint.mjs` from the retired `.claude/workflows/` path to `tools/policy/policy_lint.mjs`: `tests/layout.py --guard` refused the first form as a new reference to a landed path, and the resolver now carries both on the line (the guard's own exemption).

## Head

`634c56e1bfcdf03956e22b42699626d4c8536f39`

## Mutation proof

Reverting the generated `## Red checks` text to the single-`record` answer #2484 carried reddens two checks in `python3 -I tools/audit/seat/record_row.py --self-test`:

```
2 self-test check(s) failed: main-state reporters named, body check passes the generated body over the reporter reds (rc 1: PR-BODY: 2 error(s) in .../bodycheck/body.md)
```

Restored, the same command prints `record_row self-test: all checks passed`.

## Null control

The violating body is the generator at `origin/main` (`a2b25bbc5`): `node tools/policy/policy_lint.mjs --pr-body` over its output, with `--red record --red nightly-status --red delivery-status`, the record pull request's path set and `--existing-file` naming the two rows it rewrites, returns rc 1 with `check nightly-status is red and ## Red checks does not name it` and the same for `delivery-status` -- the refusal #2484's run reported. The fixed generator's body returns rc 0 from the same command. Stripping the two names from the fixed body's `## Red checks` returns rc 1 again; the self-test runs that stripped body as its own null-control arm, so the green is not vacuous.

## Figures

- `python3 -I tools/audit/seat/record_row.py --self-test` -- the generator's self-test, green at this head.
- `node tools/policy/policy_lint.mjs --pr-body` -- the body check `pr-contract` runs, driven at both ends above.
- `python3 tests/structure.py` -- the structural ratchet, passed at this head.
- `python3 -I tests/layout.py --guard --base $(git merge-base origin/main HEAD)` -- the layout guard, 0 refusals at this head; it refused the first commit's retired-path citation.
- `python3 tests/entities.py` -- the script the scoped gate selects for this diff (`MODE: SCOPED -- 1 script(s) run`, keyed on the mode line).

## Red checks

none: no check stands red on this branch. The scoped gate runs `tests/entities.py`, and `tests/structure.py` and the generator's `--self-test` pass at the head above.

## Forward-carry

none

## Friction

none
