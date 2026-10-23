R10-CI-LAYOUT-P2b, the cut-over. Part of #2495. Replaces #2662 (blocked at e542446e; its head carried a trailer commit, cc51e6626, that this branch re-cuts as 619ff2d55, so the head could not move forward).

This PR moves every pull-request check behind one required check, `gate` (GitHub Actions app 15368), produced by the umbrella `.github/workflows/ci.yml`, which calls each former workflow as a `workflow_call` callee. Every reader of the old layout follows the move: seats, harnesses, pins and policy text. Plan of record: `plans/ci-layout/EXECUTION.md` at 1011d6b2f; design `archive/probe/design-ci-rev4` 1371a0a6, approved at review 5 `afc00bfe`. P2a (#2622) landed the engine in `tools/ci/`. P2b-pre2 (#2665) landed U5b's arch-instrument split on main first, as the ci-ratchet payment.

## Approval

Code-owned (`/.github/workflows/`, `tools/ci/`) and policy: the files below change what a seat must do. Approved under mandate 6329234399 (scope `all`):
- `dev/governance/rules/ci-autofix.md` and `defect-root-cause.md`, with their generated `.claude/rules/` and `.cursor/rules/` copies;
- `dev/governance/roles/orchestrator.md` §11 and `nudge.md`;
- `.claude/skills/steward/SKILL.md`, `.claude/workflows/web-fragments.md` and `.github/PULL_REQUEST_TEMPLATE.md`.

tvofi ruled the ruleset-off cut-over in chat, about 10:20Z on 2026-10-23, under the same mandate, and ruled (a) on #2662 round 2: the window opens only once main's newest completed push run shows ci-ratchet green.

## How to read it

The commits run one unit at a time: U0c (umbrella and sweep); the callees U1 hassfest, U2 validate, U7 arch-score, U3 codeql, U4 governance, U5/U5b tests, U6 pr-contract, U8 budget-raise-gate, U11 kernel-points, U10 merge-main; the readers U9a, U9d, U9b; the policy U9p. Each unit's handoff is in unchanged or re-cut over a conflict (`## Unit refs`).

The glue after the units is the integration (plan step 10), each defect red first:
- `sweep_driver` gives its child the repository and a token.
- prepr's pin reader knows the callee's `PINNED` fallbacks (the dispatch base: see F-B4 below).
- The agreement lane registers three shared grammars.
- The red history excludes `gate` and `pr-contract / pr-contract`, with a defer-shape fixture from #2649.
- The required-contexts record carries the old 17 whole as `pre_cutover`; `cutoverDrift` accepts either whole shape.
- `codeowners_gap` reads callees as reachable from a pull request.
- `ruleset_cutover`'s gate-at-head reads every check suite.
- Three files `entities` reads leave the INERT prefixes (`INERT_EXCEPT`), and `harness_headers`' closure lists the two u5 files that move (1c28e979d).
- `ghapi` retries a GET's transient 5xx (a P2a defect; M-5b's gate FAILed on one HTTP 502).
- `ruleset_cutover` drives the narrowed ruleset-off window (below).
- **F-B4 (Arm B step 4):** a `ci.yml` dispatch naming a PR restores governance and `briefs` from the base, not the head (e55be5744 red, 011a15ea3 fix, 3aca3f7b6 input pin).

## What #2662's review blocked, and where each is answered

Verdict at e542446e (`Fix review: blocked ... cutover-unsound`):
1. **main's push ci-ratchet red, so step 5 could not pass.** 123b828ed (red 8b18a6ac5): `--disable` and `--dry-run --window` refuse unless main's newest completed push run (tests.yml or ci.yml, the newer) shows ci-ratchet success (`main-ratchet-green`). Owner ruling (a): the payment lands first. The payment is #2665; main's push ci-ratchet read success at 27b59c9f7 (run 39967582556, `critical_path_minutes` under its budget; instrument: `tests/ci_ratchet.py`, budget `tests/ci_budgets.json`). The rollback trigger stays "main's push `gate` not green within 75 min"; with the precondition, it no longer fires by construction.
2. **`reds-at-head` passed skipped or absent units.** 52b0cf96d (red c1e5dfe7d): every name in `gate.REQUIRED['pr']` (or `'pr-cc'` when H reaches `custom_components`, unknown reading as reaching) less `BASE_PINNED` must be present at H with `success`; skipped and neutral pass only where nothing is owed. The reviewer's `ev/reds_plant.py` five plants PASS at 4a83592e3 and FAIL at 52b0cf96d; its cancelled control FAILs at both.
3. **Forward-carries not in the tree.** On `origin/handoff/audit-r10-roster` at 54fb6f03e, R10-CI-LAYOUT-P2's carry list holds them at indices 10-14 (`jq '.groups[]|select(.group=="R10-CI-LAYOUT-P2")|.carry[10:]'`).
4. **A commit with Claude trailers.** This branch carries 619ff2d55 in place of cc51e6626; `git log origin/main..HEAD --format=%B | grep -ciE 'co-authored|claude-session'` reads 0.
5. **`tests / closures` red (UNDER-SCOPED harness_headers.py) and `pr-contract` unanswered.** 1c28e979d adds the two u5 files to `harness_headers`' closure from Linux recordings (artifact 12501157066): `closure.py check --in-dir` rc 1 before, rc 0 after. `pr-contract` is named in `## Red checks`.

Findings of the same review, all in 52b0cf96d: the rollback copy is bound to its six-key digest (`F.sha256`; `--enable`/`--rollback` refuse a copy that no longer hashes to it); a literal 15368 pin; `--enable --merged M --head H` refuses an M whose parents lack H; `--disable` removes only the `required_status_checks` rule, so enforcement and code-owner review stay on through the window. The fifth (gate self-test misses cancelled/pending mutants) was dismissed by the reviewer: the design replay pins it.

## The cut-over (step 12): a narrowed ruleset-off window

Three governance jobs restore their grader programs from the BASE commit (decision 0013): `governance / policy-docs`, `env-matrix`, `wave-script`. On this PR main's copies judge P2b's tree and fail by construction (main's `policy_lint` reads the new record against the live 17; main's `agreement_py` names a workflow this PR deletes). `gate` requires them, so no `gate`-at-head precondition can pass before the merge. P2b's own graders over P2b's tree are green (`## Null control`).

The order, run by main at a drained wave boundary; the ruleset PUTs (`--disable`, `--enable`, `--rollback`) are tvofi's or main's under the eight-step checklist, never a seat's:
1. Freeze the train.
2. `python3 -I tools/ci/ruleset_cutover.py --disable --rollback-file /abs/F --staged S --head H --pr N`: saves the 17 and its digest (`F.sha256`), then PUTs the copy less the `required_status_checks` rule, enforcement and the `pull_request` rule kept. Preconditions: staged-hash, caller-is-owner, main-push-idle, queue-drained, reds-at-head, main-ratchet-green. Refuses without `--staged`.
3. Merge this PR at H while the required checks are off.
4. `--enable --rollback-file /abs/F --merged M --head H`: requires the live ruleset equal to the copy less the rule, the copy at its digest, M on main with H among its parents; PUTs `[gate@15368]` with the copy's own enforcement; reads both halves back.
5. main's push `gate`, then `--verify --head <main sha>`.
6. Unfreeze.

Rollback triggers: main's push `gate` not green within 75 min, or the trigger-path check (DESIGN-P2 §7 step 3a) fails. Then `--rollback /abs/F` (restores the 17 and their enforcement from any state, refusing a copy off its digest) and revert this PR.

## Head

The PR head is the code head `ca1bc2b0e` plus this PR's row commit. The code head merges origin/main e6dd46277 (after #2665's merge) in c398efe2b; `tests.yml` takes P2b's side in all three hunks (fast and arch-instrument read the scope from the prelude's `gate_scope` input, so pre2's copied scope steps are not carried), and pre2's `tests/entities.py` 'equal copies' check, red on this tree, is re-cut to pin both jobs' `GATE_SCOPE` to the same input (mutants: arch `GATE_SCOPE: full`, both `RUN_PART: fast`, each FAILs it). Earlier merges: origin/main 27b59c9f7 (18a65781f) and c5e1be196 (13098f8ae; `prepr.sh`'s new 6d checks take P2b's `tests / closures` job prefix). then origin/main d7cb63508 in ca1bc2b0e: `pr-contract.yml` keeps P2b's callee `PR_HEAD` and takes main's `PR_BASE` as `steps.pr.outputs.base` (a dispatch has no pull_request payload); `budget_raise_gate.py` keeps main's `--check-body` and leaves `--rerun-stale` retired.

## Cut-over staging

Staged file: ruleset 23698884 as read before #2662 opened (enforcement `active`, the 17 contexts), `live-staged.json`, six-key hash `b6d380ac9d90f05d`. Rollback file path for the window: chosen by main, absolute, new (the tool refuses an existing one).

`python3 -I tools/ci/ruleset_cutover.py --dry-run --window --staged live-staged.json --head 2efb2cc2f151086c6fa6d30bd3d4dfcd5b1df7d3 --pr 2662`, read at 2026-10-23T20:01Z, before this PR's update, so the head has no check runs yet:
    PRECONDITION staged-hash: PASS -- live b6d380ac9d90f05d staged b6d380ac9d90f05d
    PRECONDITION reds-at-head: FAIL -- 0 check runs at 2efb2cc2f151086c6fa6d30bd3d4dfcd5b1df7d3 (none, or a full page that cannot prove the list complete)
    PRECONDITION caller-is-owner: PASS -- gh api user reads 'tvofi'
    PRECONDITION main-push-idle: FAIL -- in progress: ['Tests 40013322628', 'Tests 40012744603']
    PRECONDITION queue-drained: FAIL -- open besides #2662: [2672, 2671, 2668, 2657, 2656, 2654, 2653]
    PRECONDITION main-ratchet-green: PASS -- tests.yml push run 40009571064 (2026-10-23T19:12:33Z): ci-ratchet success

Re-run at the PR head once CI completes; full output: `window-dryrun-2efb2cc2f.txt` (evidence).

## Mutation proof

- **F-B4:** e55be5744 is red (`tests/entities.py`: "a dispatch naming a PR restores every gate-required grader from the base, never the head" FAILs on governance.yml policy-docs x2, env-matrix, wave-script x2 and tests.yml briefs). Deleting each production edit at 011a15ea3 re-reddens it: ci.yml's `with: base:` (governance's five), governance.yml's `inputs.base` clause (policy-docs), tests.yml's (briefs); deleting governance.yml's input declaration FAILs "governance.yml declares every `with:` key its ci.yml caller passes" (undeclared `['base']`). Runner: the block executed alone, verbatim, from `tests/entities.py` (`fb4_block.py` in the evidence).
- **codeowners_gap pin form:** ff1a0afaa is red (`--self-test` NULL "PINNED from the dispatched PR's base, else the push's: grader not pinned", 1 wrong); 2efb2cc2f adds the form to `PINNED_OK` (0 wrong, `--check` uncovered 13 -> 0); deleting it is ff1a0afaa.
- **prepr self-test (8f2790ef5):** perturbations `no-pinned-line`, `env-indirect` and `queue-base` replaced a `PINNED` line (`base.sha || github.sha`) governance.yml no longer has; each `assert t != s` failed inside the heredoc with nothing reading its status, so the checks graded the unperturbed file (all three assert-fail against origin/main fd7e289d0). They now target the live line, each changes the file, and one that does not is a failed check; `prepr.sh --self-test` 351 passed, 0 failed at 13098f8ae.
- **ruleset window (52b0cf96d, 123b828ed):** self-test 94 checks, 0 failed. Ten mutants each fail 1-5 checks (GREEN without skipped 5, absent ignored 4, owed accepts GREEN 2, digest unchecked 2, copy count unchecked 1, no integration id 2, merge parent always true 1, reaches ignored 1, disable whole-off 1, base-pinned owed 5); ratchet mutants (always green, oldest run wins, tests.yml only) each fail 2.
- **Earlier glue:** each commit message names its red and its mutant.

## Null control

**F-B4, live, one head two runs** (#2657 at 75011ea7e): the pull_request run's policy-docs (job 120438602400) restored from the base 7108101d7, "17 file(s) differ", `TOTAL: 37 error(s)`, failure; the dispatched run's (job 120446627407, run 39963221009, `-f pr=2657 -f base=main`) restored from 75011ea7e itself, "0 file(s) differ", success. That dispatch was the newest run at the head, so its `gate` decided. In the fixed tree the check's null arms: on pull_request every such restore reads `github.event.pull_request.base.sha`, on push `github.sha`; the plant (no base passed) reads the head.

**Own graders on P2b's tree:** the three base-pinned jobs' commands with this tree's graders over this tree exit rc 0 (policy_lint TOTAL 0 with the PRE-CUT-OVER line; env-matrix 16 outcomes held; check-wave-script, agreement, fold_ledger clean). Re-read at 2efb2cc2f: every command rc 0 (rules_sync, codeowners_gap `uncovered_files=0`, policy_lint, fragments_sync, hooks, field_coverage `FIELD COVERAGE ok`, env-matrix, check-wave-script, agreement and its self-test, fold_ledger). At c398efe2b codeowners_gap REFUSED 13 grader files (origin/main: 0): 011a15ea3's `PINNED` form was outside `PINNED_OK`; red first at ff1a0afaa, see `## Mutation proof`.

**Combined control (Arm B: B1 #2656, B2 #2657, twin #2654), read 2026-10-23.** Summary table and per-step reading: `probe-runner-B.txt` (evidence). Every `gate` ordering event held: no run lost or cancelled across push/edit/review/retarget sequences; older runs at a head defer ("still being judged; their gate decides") and the newest decides. Every name a final `gate` FAILed on was one of the three base-pinned jobs, `tests / closures` (the stale closure 1c28e979d fixes) or a probe body's own `pr-contract`. 3b (budget raise with review submit and dismiss) and 3d (briefs break) were refused at the door by prepr; 3b's live raise proof is a residual (`## Forward-carry`). Step 4's same-SHA pair produced F-B4. M-3(a): both merge-main bot heads' pull_request runs were held `action_required` until `hpo-runs` approved them, so the approve steps stay (plan §5 rule).

## Figures

- F-B4 class enumerator: `grep -nE '\|\| github\.sha|: \$\{\{ github\.sha \}\}' .github/workflows/{ci,governance,tests,pr-contract,budget-raise-gate,arch-score,codeql,hassfest,validate,kernel-points}.yml`, read at 011a15ea3 after the fix: one seam, `tests.yml` `coverage-ratchet` (`base.sha || github.sha`). Disposition: not in `gate.REQUIRED['pr']` or `['pr-cc']`, so its head-graded result on a dispatch decides nothing; on push `github.sha` is main. The six gate-required seams are closed in this diff.
- ruleset_cutover self-test: `python3 -I tools/ci/ruleset_cutover.py --self-test` -> 94 checks, 0 failed (2efb2cc2f).
- selftest_wiring: `python3 -I tools/audit/seat/selftest_wiring.py --check` -> 91 self-testing, 91 wired, 0 unwired (2efb2cc2f).
- tests/entities.py at 3aca3f7b6 (Darwin, `seat-python3`, `PYTHONPATH=tests/hastub`): 5 of 2423 FAIL, all environmental: four `hb:positive_control` py-spy timing checks, and "the coverage job reuses only an entry main's push run saved", whose `covtrust` step calls `python`, absent on this host (its three trust arms pass with a `python` shim). Not re-run at 2efb2cc2f (CI's `fast` runs it).
- `tools/pr/prepr.sh --self-test` at 8f2790ef5: 349 passed, 0 failed. `tests/structure.py`: STRUCTURE RATCHET PASSED. `brief_lint.mjs`, `rules_sync.mjs --check`: ok. `ci_predict.py`: no closures or fast red predicted against fd7e289d0.

## Red checks

- `governance / policy-docs`, `governance / env-matrix`, `governance / wave-script`: red by construction (base-pinned graders judge this tree; see the cut-over). No cheaper detector exists before the merge, since the merge is what replaces the base.
- `gate`: red because it requires the three above; the window reads `reds-at-head`, not `gate`.
- `pr-contract / pr-contract`: red only if this body's `## Red checks` misses a red; named here so main's pinned policy_lint finds it named.
- Ancestry reds, each fixed in this branch: `tests / closures` + `closures-autofix` (UNDER-SCOPED `harness_headers.py`; 1c28e979d), `governance / instrument-self-tests`, `tests / fast (3.14)` and `tests / briefs` on a0f525900 (ff7244ac0, 1cce735c3). Cheaper detector for the closures class (3 instances in P2b): after any INERT edit, freshly record each script reading a moved file with the branch's own `closure.py` and run `check` over those recordings before the push; the barrier is its own PR (R10-FLY-INERT-LOAD-TIME). Root cause: `handoff-body/r10-rca-inert-closure-recording`.

## Unit refs

Each P2 ref against the code head with `git cherry` (patch-id); a re-cut counterpart is matched by subject and identical file set:

| ref | tip | disposition |
|---|---|---|
| `handoff/r10-ci-layout-p2-u0c` | d22b5f303 | in by patch-id (3/3) |
| `handoff/r10-ci-layout-p2-u1u2u7` | eaaf57e6d | in by patch-id (8/8) |
| `handoff/r10-ci-layout-p2-u3` | 0f7f26089 | in by patch-id (1/1) |
| `handoff/r10-ci-layout-p2-u4` | 767a06f7f | in by patch-id (5/5); its cc51e6626 patch is in as 619ff2d55, trailer-free |
| `handoff/r10-ci-layout-p2-u9bp` | ffe738c7c | in by patch-id (20/20) |
| `handoff/r10-ci-layout-p2-u11` | 27146eeb8 | in by patch-id (4/4) |
| `handoff/r10-ci-layout-p2-u5` | fbc994804 | 9/10; b0bd2d25e re-cut as 44185427c |
| `handoff/r10-ci-layout-p2-u6` | e75ea158c | 6/7; 0c04d5da4 re-cut as 11353903d |
| `handoff/r10-ci-layout-p2-u8` | e56c58263 | 4/5; 4f3d54e14 re-cut as 5416c0224 |
| `handoff/r10-ci-layout-p2-u9a` | c9d647e64 | 3/4; c9d647e64 re-cut as 44185427c |
| `handoff/r10-ci-layout-p2-u9d` | 1877542fd | 0/1; 1877542fd re-cut as 5cee85cec |
| `handoff/r10-ci-layout-p2-u10` | c2143e8e8 | 9/11; c2143e8e8 re-cut as c2bc867d5, b0bd2d25e as 44185427c |
| `handoff/r10-ci-layout-p2-u0c-probe` | 65f112ec5 | 3/4; 65f112ec5, the probe cut of `ci.yml`, dropped on purpose |
| `handoff/r10-ci-layout-p2-pre` | 54c60b5ac | #2658, closed. 2/6 by patch-id; its `ghapi` retry is in as 412c2ef5b and 9e677aa29; b31fe0812, 1ea885f50, b9e408c7a, b1de8abec are superseded by the window |
| `handoff/r10-ci-layout-p2-policylint` | 4ef641145 | nothing outstanding |
| probe-B1, probe-B2, probe-Btwin | -- | probe-only, dropped on purpose |

After the merge these refs can be archived: every `handoff/r10-ci-layout-p2-*` ref above, `handoff/r10-ci-layout-p2b`, `ci-probe/all`, `ci-probe/all-before`, `ci-probe/base`, `ci-probe/b2`, `ci-probe/u0c{,-absent,-red,-skip}`.

## Forward-carry

- Delete required-contexts.json's `_pre_cutover` and `pre_cutover` keys after the PUT; owner: the step-22 beat. Carry: R10-CI-LAYOUT-P2
- Delete `tools/ci/gate.py`'s self-check reading the old 17 as renamed, after the PUT. Carry: R10-CI-LAYOUT-P2
- Delete `merge_train.py`'s A5 layouts pair after the PUT. Carry: R10-CI-LAYOUT-P2
- `same_sha_dup_heads` after the cut-over (roster carry 1); before: B1 and B2 heads never coincided, and step 4's deliberate pair deferred correctly. Carry: R10-CI-LAYOUT-P2
- U8's live raise proof (Arm B 3b) was refused at the door twice and not retried: the first post-cut-over budget raise reads `budget-raise-gate` under `gate` once, and its review submit/dismiss re-grade. Carry: R10-CI-LAYOUT-P2

## Friction

none
