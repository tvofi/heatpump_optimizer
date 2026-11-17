R11-HOTFIX-SELFTEST-SCOPES: product_reads self-test on the per-state d16 cells, and the self-test scope re-record

Main (38bf516bdd73f926ee9639ffda7b9ca5163fd50e) is red on `governance / instrument-self-tests` (push run 43987459885, job 133732070457), at two steps.

Red 1, step "Show the self-tests outside tools/audit/seat/ refusing their own fixtures": `python3 -I tools/audit/product_reads.py --self-test` dies with `enumerate.Refuse: const.py PUMP_DUTY_MODES ['control', 'off'] are not the duty modes STATES names ['control', 'observe', 'off']`.

Cause: a semantic merge conflict between two PRs whose CI each passed alone. #3672 (b98c78e0f6) re-cut `enumerate.py d16-writes --cells` from `site | duty=M | running/restart/upgrade/unavailable` to `site domain=X | <state>` over `census.STATES`, and refuses unless const.py's `PUMP_DUTY_MODES` equal the STATES duty modes. #3665 (54cb721164, branched before #3672 merged) landed `product_reads.py`, whose fixture plants `PUMP_DUTY_MODES = ('off', 'control')` and whose ledger rows and `token_holds` use the old `duty=` / `running` tokens.

Repair 1, `tools/audit/product_reads.py` only: the fixture plants `('off', 'observe', 'control')`; `token_holds` reads each token as a STATES row and holds only under that row's duty mode (`DUTY_OF = dict(census.STATES)`); a plan-state token, `observe` and `off` hold on the first coordinator pass with the written entity available (the old `running` meaning); the `duty=` and `running` branches go. Fixture rows move to the new cell text, and the no-`now` row is cited for `baseline`, so the RESULT arm reads examined=8.

Red 2, step "Refuse a self-test read set the committed table misses": 20 UNDER-SCOPED refusals (files added since the #3671 re-record, from #3630, #3602, #3683, #3665, #3654 and others) plus 4 UNMEASURED (throwaway-git-helper, merge-train, carry-check-and-the, train-launcher), skipped only because step 48 failed first. Repair 2, `tools/ci/selftest_closures.json`: the run's own `selftest-closures` artifact (id 14291519472) for its 118 steps, plus the committed entries kept for the 4 unmeasured steps. Committing the artifact verbatim would turn those 4 UNRECORDED.

## Head

Code head `a571679e9004f9eca41ae5255691517a48f6872e`, two commits on origin/main 38bf516bdd73f926ee9639ffda7b9ca5163fd50e. Everything below was measured there.

prepr: passed rc=0 at a571679e9004f9eca41ae5255691517a48f6872e (hotfix mode: `PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`; CI is the authority).

## Mutation proof

Each mutation was applied at the head, then reverted. Each fails at the head and passes once reverted:
- (a) fixture const.py back to `('off', 'control')`: `python3 -I tools/audit/product_reads.py --self-test` exits 1 with the same `enumerate.Refuse: const.py PUMP_DUTY_MODES ['control', 'off'] are not the duty modes STATES names ['control', 'observe', 'off']`.
- (b) the `DUTY_OF` guard disabled (`if False and tok in DUTY_OF ...`): exits 1, `SELF-TEST FAILED`, failing arms `planted: another duty mode differs: got False, want True` and `planted: a hold whose recorded state differs is not reached: got False, want True`.
- (c) the `observe`/`off` branch of `token_holds` (`if tok in ("observe", "off"): return first`), the fix review's surviving M3 and M6. A new arm, `token: off holds under duty=off on the first pass, not on a restart pass`, pins an `off` token under `duty=off` that holds at ordinal 0 and does not hold at ordinal 1. M3 (`return False`) exits 1 with `got (False, False), want (True, False)`. M6 (`return True`) exits 1 with `got (True, True), want (True, False)`. Unmutated, it prints `SELF-TEST passed (86 arms)`, exit 0.

## Null control

- Failing first: at origin/main 38bf516bdd, `python3 -I tools/audit/product_reads.py --self-test` exits 1 with the Refuse quoted above.
- At the head: `SELF-TEST passed (86 arms)`, exit 0.
- `python3 -I tools/ci/selftest_scope.py static` at the head prints `122 gated step(s), 0 problem(s)`, and `--self-test` prints `selftest_scope self-test: 118 checks, 0 failed` on macOS, which skips the strace end-to-end checks, and `128 checks, 0 failed` on Linux with strace (the fix review measured 128).
- The trace check runs only on main (strace, Linux). If the first main run after the merge prints UNDER-SCOPED for self-tests-outside-seat, which now runs to the end, that run's artifact is committed the same way.

## Figures

<!-- figure-block: scope-line mb=38bf516bdd73f926ee9639ffda7b9ca5163fd50e head=a571679e9004f9eca41ae5255691517a48f6872e -->
~~~text
MODE: FULL -- every test script runs, nothing is scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `governance / instrument-self-tests` on main (push run 43987459885, job 133732070457): the defect this PR fixes, at both steps above. The `FAIL D1 ... owned twice` and `FAIL D2 ... unowned` lines in that log are `check_scopes.py --self-test`'s own planted perturbations; that script passes (`SELF-TEST passed (every perturbed scope refused)` at the head).

## Root cause

- Cause: a semantic merge conflict. #3672 changed the `d16-writes --cells` contract and added the duty-mode refusal. #3665 built `product_reads.py` on the old cell format. Neither PR's CI ran against the other's change.
- Process state: (c). A detector existed and each PR's CI passed it in isolation. Only the post-merge combination on main failed.
- Cheaper detector: re-run `instrument-self-tests` at merge, in the train's batch proof, over the combined head, so a pair that conflicts semantically goes red before main does. Standing cost: one instrument-self-tests job per train batch. Red 2's UNDER-SCOPED half is the known push-only-trace class; its countermeasure is already ruled (loop-study card L9, round 11 start) and is not rebuilt here.

## Forward-carry

- Out of scope: the committed round-11 seed ledger `dev/audit/rounds/round11/product-reads/operation.tsv` (from #3665) still holds 6 rows in the retired `duty=control | running` cell format, so `product_reads.py operation --ledger` refuses it at this head. It was already broken at the base. Re-cutting each row needs a judgement, because `running` has no 1:1 successor among the plan-state tokens. That makes it the product-reads owner's work, not this hotfix's. R11-PRE-PRODUCT-READS is at carries-open, which carry_audit refuses as a destination, so the residual goes to the round-11 holding group, which re-homes it. Carry: R11-INTAKE-R10-RESIDUE (operation.tsv seed re-cut to per-state cells)

## Friction

none
