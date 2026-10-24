R10-CI-LAYOUT-P2, step 11a: the precursor that P2b's cut-over needs on main first. Part of #2495.

**Cause.** `governance.yml` restores its grader programs from the BASE commit before it runs them over the pull request's tree (decision 0013). On P2b's probes, B1 #2656 and B2 #2657 (both cut from the assembly), main's copies therefore judged P2b's tree, and three governance jobs failed by construction:
- `policy-docs` and `env-matrix`: main's `policy_lint` read U9b's record, `contexts: ["gate"]` with the old 17 as `pre_cutover`, against the live ruleset's 17. That gives 37 `[required-contexts]` errors.
- `wave-script`: main's `agreement_py.py` read main's `tests/entities.py` `_GOV_FILES`. That list still names `budget-raise-gate-rerun.yml`, which P2b deletes, so the read raised FileNotFoundError.

P2b's `gate` requires all three jobs, so P2b's gate was red at every head, and `ruleset_cutover.py --apply`'s gate-at-head precondition would refuse: the PUT and the merge each waited on the other. P2b's own linter already carried `cutoverDrift`, but a base-pinned job never runs the PR's copy. That is why the assembly's checks were green and the probes were not.

**What lands.** Each change is a red test first, then the fix:
1. `counts.mjs` `cutoverDrift`, and its two readers, `policy_lint` `requiredContextsOverTree` and `field_coverage` `RULESET_PROBE`. Main's record carries no `pre_cutover`, so on main `cutoverDrift` is `requiredContextsDrift` unchanged: no stale-arm note, and no record churn. P2b's record supplies `pre_cutover`.
2. `agreement_py.py` `governance_pin`: a listed governance file that the tree lacks adds no jobs. `tests/entities.py` now pins that every `_GOV_FILES` entry names a file the tree holds, and it reads only those. A stale list therefore still fails on the tree that carries it, and fails by name instead of by crash.
3. `ghapi.py`: a GET retries a 5xx after 2 s and then 6 s, then returns what it got. Every other status, a rate limit included, answers at once, and a POST is never retried. This is a P2a defect found by M-5b on #2649: a gate re-run FAILed on one HTTP 502. `sweep.py` re-runs only older reds, so a 5xx on the newest run's gate would stay red until the next event, and `--apply` reads through the same client.

**Next.** After this merges, P2b merges main, B1 and B2 re-run on that head, and P2b's gate at head must be green before `--apply`.

## Head

`f8c05fbf7e1ddaf4d15652b88cd40b77372df0f6` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2658.md`. The authored code head is `54c60b5ac88892e08241f91377354c2740b82e9c`.

Everything below was measured at the code head; origin/main was already its ancestor, so `open_pr.sh` merged nothing.

## Mutation proof

- **1:** commit b31fe0812 (pins only) fails `node tools/policy/policy_lint.mjs --acceptance` with `FIXTURE VACUOUS: a live set equal to the recorded pre_cutover shape produced 4 finding(s) and no PRE-CUT-OVER line`.
- **2:** commit b9e408c7a fails `agreement_py.py --self-test` on its 2 new rows. Main's `governance_jobs` over a tree without `budget-raise-gate-rerun.yml` raises FileNotFoundError. The mutant `if True:` in `governance_pin` gives 6 failed. The entities plant, the same tree without that file, fails `every _GOV_FILES entry names a governance workflow file the tree holds` with `absent: ['.github/workflows/budget-raise-gate-rerun.yml']`.
- **3:** commit f17e09d63 fails `tools/ci/ghapi.py --self-test`. Mutant `RETRY_5XX = ()` gives 4 failed. Mutant "retry any status >= 400" fails the 404 null.

## Null control

- **Plant:** P2b's record (`tools/policy/fixtures/required-contexts.json` at 1cce735c3) copied into this tree. Main's linter reads `TOTAL: 37 error(s)`, which reproduces the CI red. This branch's linter reads `TOTAL: 0 error(s)` and says `the live set is the recorded PRE-CUT-OVER shape`.
- **On main's own record:** `policy_lint` reads TOTAL 0, `field_coverage` reads `read=69 dead=0 refused=0`, and `entities` reads `4 of 2407` (the four py-spy controls, environmental and the same as main).
- **Self-tests:** a 404 is not retried, and a present governance file still adds its jobs.

## Figures

- policy_lint against P2b's record, main's copy against this branch's: 37 and 0 errors. `node tools/policy/policy_lint.mjs`
- ghapi self-test: 19 checks, 0 failed. `python3 -I tools/ci/ghapi.py --self-test`
- agreement_py self-test: 9 checks, 0 failed. `python3 -I tools/policy/agreement_py.py --self-test`

## Red checks

`none`

## Forward-carry

`none`

## Friction

`none`

