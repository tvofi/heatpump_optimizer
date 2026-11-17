Fix review: blocked 4bfd3c06fa7316f88ffa19621d3df1ac0b1b69c3 class-open: dev/audit/rounds/round11/product-reads/operation.tsv still names the retired `duty=control | running` cells and product_reads.py operation refuses it at this head; neither in the diff nor dispositioned in the body

bus-nonce: a0d6676cef67e11ef0fb4130b6ae6623

## Block

The body's cause is that #3665 built product_reads on the old `d16-writes --cells` format, which #3672 retired. The PR moves product_reads.py's fixture and `token_holds` to the new format. It leaves the other #3665 artifact on the old format: the committed round-11 seed ledger `dev/audit/rounds/round11/product-reads/operation.tsv` (77de985de7). All 6 of its rows are `... | duty=control | running`. At this head, `python3 -I tools/audit/product_reads.py operation --repo . --ledger dev/audit/rounds/round11/product-reads/operation.tsv` exits 2 with `REFUSE: ...operation.tsv:2: '... _write | duty=control | running' is no item of this universe as printed` (ev/seed-ledger-at-head.txt). The instrument this hotfix repairs therefore still cannot read its own committed input.

This was already broken at the base (ev/seed-ledger-at-base.txt), so the PR does not introduce it. By fix-review.md step 6, though, a site of the stated class that is neither in the diff nor dispositioned in the body is `class-open`. Either of these clears the block:
- re-cut the 6 rows to the new cell text, choosing a plan-state token per row, which is a judgement because `running` has no 1:1 successor; or
- disposition the file in the body with a route.

The sibling `generality.tsv` reads fine at the head: `RESULT read=generality universe=18897 examined=3 levels=3 pairs=0 reached-only=4`, exit 0 (ev/generality-at-head.txt).

## Findings

- Surviving mutants on the new `if tok in ("observe", "off"): return first` branch in `token_holds`: replacing `return first` with `return False` (M3) or with `return True` (M6) both leave `--self-test` at `SELF-TEST passed (85 arms)`, exit 0 (ev/mutants.tsv). No arm witnesses an `observe` or `off` cell holding, and none refuses one on a restart pass or an unavailable write. Arms `v(6)` and `v(15)` only exercise the duty-mismatch guard, which returns before this branch. To kill both: add one positive arm (an `off` cell under `duty=off`, first pass) and one negative arm (the same cell with `ordinal>0`). Carry: R11-HOTFIX-SELFTEST-SCOPES

## Evidence

- Head reviewed: 4bfd3c06fa7316f88ffa19621d3df1ac0b1b69c3 (ev/HEAD.txt). It still equals refs/pull/3698/head. Merge base: 38bf516bdd73f926ee9639ffda7b9ca5163fd50e. Code head 20e8f10a91 differs from the head only by dev/programme/delivery/3698.md.
- Role contracts: `git diff MB...origin/main -- dev/governance/roles/` touches only architect-planner.md, so fix-review.md is current.
- Merge: `git merge-tree --write-tree origin/main <head>` gives a clean tree, 6e32d8dc364a8f74651abaef032343a771cef8fb.
- Null control, both ends: at base `product_reads.py --self-test` exits 1 with the `enumerate.Refuse: const.py PUMP_DUTY_MODES ['control', 'off'] ...` the body quotes (ev/selftest-base.log). At head it prints `SELF-TEST passed (85 arms)` and exits 0 (ev/selftest-head.log).
- Mutation proof (body a, b) reproduced:
  - (a) the fixture reverted to `('off', 'control')` brings back the Refuse (ev/mutant-a.txt).
  - M1, which deletes the DUTY_OF guard and is equivalent to (b), is KILLED.
  - My own mutants: M2 (plan-state tokens without `first`), M4 (`first` ignoring unavailable) and M5 (`first` ignoring ordinal) are KILLED. M3 and M6 SURVIVE (see Findings).
- Scope: `selftest_scope.py static` prints `122 gated step(s), 0 problem(s)` at both ends. `select --change M:tools/audit/enumerate.py` and `--change M:tools/audit/product_reads.py` both select `self-tests-outside-seat` at base and head (ev/selftest-scope.txt). The closures re-record is measured data from the CI artifact. I did not re-record it: strace record is main-only and heavy.
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched (ev/figures.txt).
- Finder's harness: none named. The defect's harness is the CI step itself (`instrument-self-tests` / self-tests-outside-seat), re-run above at both ends.
- CI at this head: classify printed `WAIT 4bfd3c06fa7316f88ffa19621d3df1ac0b1b69c3 pending: gate red: none` on every poll (ev/classify-polls.txt, ev/classify-final.txt). No red is known at this head. The review_packet's `introduced-red: unreadable` refusal was the queued instrument-self-tests job (ev/review-packet.md).
- Note: figure: the body says `selftest_scope.py --self-test` prints `118 checks, 0 failed`. At the head it prints `selftest_scope self-test: 128 checks, 0 failed` (ev/figures.txt).
- Note: figure: the body says `check_scopes.py --self-test` prints `SELF-TEST passed (161 arms)` (from main's log). At the head it prints `SELF-TEST passed (every perturbed scope refused)` with no count, so 161 is not re-derived.

## Friction

none
