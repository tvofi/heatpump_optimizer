Fix review: blocked 2469c52668c90af0c143b6905c9ee6e25e140add class-open: draw/engaged cell-only cost unguarded, a loader dropping the samples on a non-bool latch survives every check

bus-nonce: 9368deadf31262f71ae698980b80ac80

Round 1 (first review, no --reviewed-head).

## Block

- The body's class rule measures one direction of "a declaration's cost is what the real loader measures": a `whole=` that no bad value uses is refused. It does not measure the other direction: a cell-only declaration (no `whole`) whose bad value costs other leaves. The PR's one production line sits on that direction. `draw/engaged` becomes `_FLAG`, and its new comment claims "costs only itself; the samples stay". No check holds that claim.
- Mutant M5b (`ev/m5b.diff`), in `DrawRange.from_dict` right after the latch read: `if "engaged" in data and not isinstance(data["engaged"], bool): return out`. This drops the samples whenever the stored latch is present and not a bool, while the store still declares `draw/engaged` as `_FLAG`. Results at the head with M5b applied: `tests/finite_boundary.py` gives `ALL 116 FINITE BOUNDARY CHECKS PASSED` rc 0, with `RESULT domain_refused=0` and `domain_whole_unused=0`. `tests/features.py` gives `ALL 5857 FEATURE CHECKS PASSED` rc 0. The broader M5 also fires on an absent key. It passes `tests/edge.py` (rc 0) and `tests/stress.py` (rc 0). Only features.py kills it, through two idle-window checks, and those checks reach it through the absent-key path, not through a bad value.
- What resolves it: extend Arm 6's cost probe to every declared non-key field, or to a disposition the body states, and refuse a cell-only declaration when some bad value changes another leaf. Then M5b must fail. The over-broad half and its control stay as they are.

## Notes

- Note: figure: the body says `draw/config/#` is used with "every refused bad value costs 19 other leaves". The in-tree rule at the head measures 17, and the control prints `config=17` (`ev/probe_whole_costs.txt`).
- Note: figure: the body gives `duty_switch` fields as "6 or 7". The in-tree rule at the head measures 5 or 6. The body attributes the per-field list to a `/tmp` scratch probe at the merge base, so the in-tree numbers are the ones re-derived here.

## Evidence

- HEAD.txt names the head. The head matches the PR body's head line and the live PR head. Its three-dot diff touches `store.py` (1 line), `tests/finite_boundary.py` and `dev/programme/delivery/3714.md`.
- Merge: `git merge-tree --write-tree origin/main 2469c526` exits 0 and the head is 0 commits behind origin/main. No role-contract drift (`git diff mb...origin/main -- dev/governance/roles/` is empty).
- CI: `merge_train.py classify 2469c52668c90af0c143b6905c9ee6e25e140add --pr 3714` printed `GREEN 2469c52668c90af0c143b6905c9ee6e25e140add pending: none red: none`, rc 0. `tests / nightly-status` is a failure, but it is not in `owed-reds`, so it needs no answer.
- At the head, `PYTHONPATH=tests/hastub python3 tests/finite_boundary.py` gives `ALL 116 FINITE BOUNDARY CHECKS PASSED` rc 0, with `RESULT domain_whole_fields=33` and `domain_whole_unused=0`. At merge base 99a4010e it gives `ALL 114 FINITE BOUNDARY CHECKS PASSED` rc 0. Both match the body.
- Mutation proof re-run, all fail at the head:
  - Base `store.py` (`ev/base.diff`): rc 1. Fails `every whole= declaration is used [whole=34 unused=['accuracy:accuracy/draw/engaged']]`, so the body's figures 34 and 1 are re-derived.
  - M1 (`ev/m1.diff`): rc 1, control fails with `overdraws=1 config=18`.
  - M2 (`ev/m2.diff`): rc 1, two checks fail.
  - M3 (`ev/m3.diff`): rc 1, control fails with `overdraws=1 config=1`.
  - The body's 4-of-4 kill is confirmed.
- The null control is green at the head (`overdraws=0`, `config=17`). The in-tree per-field costs are in `ev/probe_whole_costs.txt`, from an instrument the reviewer built: a print-only patch of the head's own check.
- `features.py` at the head (null control for M5): `ALL 5857 FEATURE CHECKS PASSED` rc 0.
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched (empty diff from the merge base). No claim file is touched, and no golden moves.
- Finder's harness: the packet names none. The instrument here is the fixer's in-tree Arm 6 check, so the harness is the fixer's, not the finder's.
- Carry 3 is routed to R11-OUTSIDE-HONEST-DHW-RUNS (carry_audit: 3 routed, 0 unrouted). It was not re-measured here, because nothing for it is built in this PR. Figures for it that were not re-derived: the tail-arm counts 4/0, 9/0 and 9/9.
- I did not re-run the heavy gate or the mutation table. CI's `gate` and `tests / mutation` are success at this head.
