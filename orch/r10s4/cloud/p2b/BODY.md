R10-CI-LAYOUT-P2b, the cut-over. Part of #2495.

This PR moves every pull-request check behind one required check, `gate` (GitHub Actions app 15368). `gate` is produced by the umbrella workflow `.github/workflows/ci.yml`, which calls each former workflow as a `workflow_call` callee. Every reader of the old layout follows the move: the seats, the harnesses, the pins and the policy text. It completes the plan of record (`plans/ci-layout/EXECUTION.md` at 1011d6b2f; design `archive/probe/design-ci-rev4` 1371a0a6, approved at review 5 `afc00bfe`). P2a (#2622) landed the engine in `tools/ci/`.

## Approval

Code-owned (`/.github/workflows/`, `tools/ci/`) and policy: the files below change what a seat must do. They are approved under mandate 6329234399 (scope `all`):
- `dev/governance/rules/ci-autofix.md` and `defect-root-cause.md`, with their generated `.claude/rules/` and `.cursor/rules/` copies;
- `dev/governance/roles/orchestrator.md` §11 and `nudge.md`;
- `.claude/skills/steward/SKILL.md`, `.claude/workflows/web-fragments.md` and `.github/PULL_REQUEST_TEMPLATE.md`.

tvofi ruled the ruleset-off cut-over below in chat, about 10:20Z on 2026-10-23, and granted it under the same mandate.

## How to read it

The commits run one unit at a time. U0c is the umbrella and its sweep. Then come the callees: U1 hassfest, U2 validate, U7 arch-score, U3 codeql, U4 governance, U5 and U5b tests, U6 pr-contract, U8 budget-raise-gate, U11 kernel-points and U10 merge-main. Then the readers (U9a seat readers, U9d harness and CI readers, U9b pins) and the policy (U9p). Each unit's handoff is cherry-picked unchanged, so a unit's own body and static map still describe it.

The glue commits after the units are the integration (step 10). Each one is a defect the assembly or its probes found, fixed red-first:
- `sweep_driver` gives its child the repository and a token.
- prepr's pin reader knows the callee's `PINNED` fallback.
- The agreement lane registers three shared grammars.
- The red history excludes `gate` and `pr-contract / pr-contract`, with a defer-shape fixture from #2649.
- The required-contexts record carries the old 17 whole as `pre_cutover`, and `cutoverDrift` accepts either whole shape. Because the comparison takes the WHOLE shape, an acceptance row has a `pre_cutover` whose rulesets differ, which closes the contexts-only mutant from #2658's review.
- `codeowners_gap` reads callees as reachable from a pull request.
- `ruleset_cutover`'s gate-at-head reads every check suite.
- Three files that `entities` reads leave the INERT prefixes (`INERT_EXCEPT`). P2b's own classification caused this: U5 added `run_part.py` and `unitcheck.py`, and U3 added the `codeql_scope.py` pin. CI's closures-autofix on probe #2656 (job 120356230438) refused its merge with `skip-merge-failed: files on the INERT list are actually read by tests`. With the entries, the same Linux recordings (artifact 12493224545) merge and `check` clean, and `closures.json` takes that merge (4a83592e3).
- `ghapi` retries a GET's transient 5xx. This is a P2a defect: M-5b's gate FAILed on one HTTP 502, and the sweep never re-runs the newest run's red. It was folded in from #2658.
- `ruleset_cutover` drives the ruleset-off window.

The #2658 precursor was closed and folded in here. Its two `pr-contract` reds, jobs 120336368847 and 120336562671, came from a `carry_audit` UNROUTED item in its `## Forward-carry`. Root-cause-detectable: `python3 -I tools/audit/carry_audit.py check --body <body>` reproduces the red locally in seconds before a push, but `app_push.sh` runs it only under `--row-only` and prepr does not run it. This body was checked with it before opening.

## The cut-over (step 12): a ruleset-off window

Three governance jobs restore their grader programs from the BASE commit before running them over the PR's tree (decision 0013): `governance / policy-docs`, `env-matrix` and `wave-script`. On this PR, main's copies therefore judge P2b's tree and fail by construction:
- main's `policy_lint` reads the new record against the live 17 (37 `[required-contexts]` errors);
- main's `agreement_py` reads a `_GOV_FILES` list that names a workflow this PR deletes.

`gate` requires them, so `gate` is red at every head of this PR, and no `gate`-at-head precondition can pass. P2b's own graders, run over P2b's tree, are green (Null control). Once this PR merges, main carries those graders.

The order, run by main at a drained wave boundary:
1. Freeze the train.
2. `python3 -I tools/ci/ruleset_cutover.py --disable --rollback-file /abs/F --staged S --head H --pr N`
   - It saves the 17, then PUTs them with `enforcement: disabled`.
   - Preconditions: staged-hash, caller-is-owner, main-push-idle, queue-drained, and `reds-at-head`. `reds-at-head` means every check at H is complete and the only reds are the three base-pinned jobs and `gate`.
   - It refuses without `--staged`.
3. Merge this PR at H while enforcement is off.
4. `--enable --rollback-file /abs/F --merged <merge sha>`
   - It requires the disabled copy live and the merge commit on main.
   - It PUTs `[gate@15368]` with the copy's own enforcement, then reads both halves back.
5. main's push `gate`, then `--verify --head <main sha>`: every check suite's newest `gate` at main's head is green.
6. Unfreeze.

Rollback triggers: main's push `gate` is not green within 75 min, or the trigger-path check (DESIGN-P2 §7 step 3a) fails. Then run `--rollback /abs/F`, which restores the 17 and their enforcement from any state, and revert this PR. The revert restores the standalone workflows, so it can produce the 17.

The staged reads at this head are under `## Cut-over staging`: `--dry-run --window` against the live ruleset saved as the staged file, and a dry read of the rollback against it.

## Head

`e542446e725f703f2cfd51a35fbc987ed0d54584` is the code head 4a83592e3 plus one commit containing only this PR's own row, `dev/programme/delivery/2662.md`.

The code head 4a83592e3 is ci-probe/all. It merges origin/main `a6620c30a` in f3a37894d, an automatic merge with no conflict resolution, and then takes CI's Linux closures recordings (4a83592e3).

## Cut-over staging

The staged file is the live ruleset 23698884 as read before this PR opened (enforcement `active`, the 17 contexts), saved as `ruleset/live-staged.json`. Its six-key hash is `b6d380ac9d90f05d`.

`python3 -I tools/ci/ruleset_cutover.py --dry-run --window --staged <staged> --head e542446e7 --pr 2662`, read at 11:58Z:
- DISABLE payload: the live six keys with only `enforcement` changed, from `active` to `disabled`.
- ENABLE payload: the rollback copy with the 17 contexts replaced by `[gate@15368]` and its own enforcement.
- Preconditions:
```
PRECONDITION staged-hash: PASS -- live b6d380ac9d90f05d staged b6d380ac9d90f05d
PRECONDITION reds-at-head: FAIL -- pending: ['prelude', 'prelude', 'refresh', 'refresh']; reds: none (base-pinned and gate only)
PRECONDITION caller-is-owner: PASS -- gh api user reads 'tvofi'
PRECONDITION main-push-idle: PASS -- in progress: none
PRECONDITION queue-drained: FAIL -- open besides #2662: [2661, 2659, 2657, 2656, 2654, 2653, 2632, 2620]
WINDOW DRY-RUN REFUSED: nothing was written
```
Both FAILs are expected this early in the PR's life, and main re-reads them at the window:
- reds-at-head was pending only because CI had just started at this head. It saw no red outside the base-pinned three and `gate`.
- queue-drained requires main's drained wave boundary.

Rollback: `--disable` saves the copy to `--rollback-file`, an absolute path main chooses at the window. `--rollback` has no dry-run mode and only writes, so the dry read checks the copy it would restore: the staged file passes the tool's own `assert_old` (`ROLLBACK COPY READ: assert_old PASS; 17 contexts; enforcement active`).

## Mutation proof

Each glue fix is red first. The red commit, mutant or plant comes before its fix:
- **ruleset window:** the self-test exited 2 before the modes existed; it now reads 72 checks, 0 failed. Three mutants each fail 1 check:
  - `reds-at-head` accepting any red;
  - merged-on-main always true;
  - `--disable` without `--staged`.
- **cutoverDrift whole shape:** the contexts-only mutant gives `FIXTURE VACUOUS ... 6 finding(s)`. The pre-shape pin failed with 4 findings before the arm.
- **ghapi:** red by `NameError` before the fix. Mutants:
  - `RETRY_5XX=()` gives 4 failed;
  - retrying any status >= 400 fails the 404 null.
- **INERT_EXCEPT:** CI's refused merge, above, is the plant.
- **Earlier glue:** each commit message names its red and its mutant (`git log 85d13b859^..HEAD`).

## Null control

**Own graders on P2b's tree.** The three base-pinned jobs' commands, run with this tree's graders over this tree (`p2b-ownsim`), all exit rc 0:
- policy-docs:
  - rules_sync ok;
  - codeowners_gap uncovered 0;
  - policy_lint TOTAL 0, with the PRE-CUT-OVER line;
  - fragments ok;
  - hooks ok;
  - field_coverage read=69 dead=0 refused=0.
- env-matrix: 16 declared outcomes held, 0 did not, across 6 environment shapes.
- wave-script:
  - check-wave-script 209/0;
  - agreement divergent=0 unregistered=0 dead=0;
  - agreement self-test 27/27;
  - fold_ledger 0 violations.

**Battery** at fab4acdb1, after the main merge:
- selftest_wiring 91 self-testing, 91 wired, 0 unwired;
- self-tests: gate 28/0, ruleset_cutover 72/0, ghapi 19/0, sweep 21/0, prelude 27/0, merge_train 240/0, sweep_driver 20/0, ci_probe 53/0, merge_main_bot 42/0;
- prepr --self-test 349/0;
- brief_lint and tmp_paths --check: 0;
- structure passed; closure selftest 112;
- entities: after 4a83592e3 the 4 environmental py-spy controls remain.

**Unit maps.** Every unit's `unitcheck2.py static` against current main reads rc 0 under its map and rc 1 on its plant. The U5 harness passes.

**Live probes:**
- M-6 `--nochain` and `--chain` PASS: every gate suite ends green.
- M-7 PASS: `gate` is not listed before its needs finish.
- M-5b PASS: a re-run of an old gate leaves the newer run green and cancels nothing.
- M-4: names, and the bare skipped-caller check run.
- U1–U3 and U5 runtime pairs: equivalent apart from mapped edits.

**Combined control (Arm B, B1 #2656, B2 #2657, twin #2654).** It runs in parallel with this review and gates the cut-over, not this PR's open. Its gate reading is "green modulo base-pinned": a FAIL that names only the three.

## Figures

- ruleset_cutover self-test: 72 checks, 0 failed. `python3 -I tools/ci/ruleset_cutover.py --self-test`
- policy_lint against the live ruleset: TOTAL 0. `node tools/policy/policy_lint.mjs`
- selftest_wiring: 91, 91, 0. `python3 -I tools/audit/seat/selftest_wiring.py --check`

## Red checks

- `governance / policy-docs`, `governance / env-matrix` and `governance / wave-script`: red by construction. These jobs restore their graders from the base commit (decision 0013), so main's copies judge this tree: main's policy_lint against the new required-contexts record, and main's agreement_py against a `_GOV_FILES` list naming a deleted workflow. The same commands with this tree's graders are green (Null control). No cheaper detector exists before the merge, since the merge is what replaces the base. The cut-over runs in the ruleset-off window above, which tvofi ruled for exactly this.
- On the ancestor a0f525900 (ci-probe/all during step 10, read by the U5 dispatch pairs 39918497616 and 39918505090), each was red, fixed later in this branch, and green on every later probe head (B1 #2656, B2 #2657):
  - `governance / instrument-self-tests`: `tmp_paths --check` refused `tests/entities.py:26932` (`"> /tmp/pr-alerts.txt" in _PC_WAIT`, U6's pin). Fixed by ff7244ac0 (an ALLOW entry).
  - `tests / fast (3.14)`: `tests/layout.py` refused the moved-tree spellings in U9b's reads. Fixed by ff7244ac0 (`locate()`, a `layout:old` marker).
  - `tests / briefs`: `carry-1648.json` cited the retired `pr-contract-rerun.yml` bare. Fixed by 1cce735c3 (cites 57b7b4994).
  - `tests / closures` and `tests / closures-autofix`: INERT READS UNDER-APPROXIMATED, and then the INERT-and-read pair. The autofix job refused its merge (`skip-merge-failed`, job 120356230438 on #2656). Fixed by 9f7f443cc and 4a83592e3.
  - The cheaper detector for all four: `tools/audit/seat/tmp_paths.py --check`, `tests/layout.py`, `brief_lint.mjs` and `closure.py check` over CI's recordings, run on the assembly before a probe push. Each takes seconds except the recording, which only CI's Linux recorder can produce. They were not in the step-10 battery before those pushes; the battery script now runs them (`p2b-battery.sh`, about 15 min a tip).
- `gate`: red because it requires the three above. That is the reason `ruleset_cutover --disable` reads `reds-at-head` and not `gate`.

## Unit refs

Each P2 ref, checked against the code head 4a83592e3 with `git cherry` (patch-id). Where a unit was re-cut over a conflict, its counterpart was matched by subject and file set:

| ref | tip | disposition |
|---|---|---|
| `handoff/r10-ci-layout-p2-u0c` | d22b5f303 | in by patch-id (3/3) |
| `handoff/r10-ci-layout-p2-u1u2u7` | eaaf57e6d | in by patch-id (8/8) |
| `handoff/r10-ci-layout-p2-u3` | 0f7f26089 | in by patch-id (1/1) |
| `handoff/r10-ci-layout-p2-u4` | 767a06f7f | in by patch-id (5/5) |
| `handoff/r10-ci-layout-p2-u9bp` | ffe738c7c | in by patch-id (2/2) |
| `handoff/r10-ci-layout-p2-u11` | 27146eeb8 | in by patch-id (4/4) |
| `handoff/r10-ci-layout-p2-u5` | fbc994804 | in; b0bd2d25e re-cut as 20382dd99 |
| `handoff/r10-ci-layout-p2-u6` | e75ea158c | in; 0c04d5da4 re-cut as 8f339b0fa |
| `handoff/r10-ci-layout-p2-u8` | e56c58263 | in; 4f3d54e14 re-cut as 2d5378a20 |
| `handoff/r10-ci-layout-p2-u9a` | c9d647e64 | in; c9d647e64 re-cut as 20382dd99 |
| `handoff/r10-ci-layout-p2-u9d` | 1877542fd | in; 1877542fd re-cut as ea38b17fe |
| `handoff/r10-ci-layout-p2-u10` | c2143e8e8 | in; c2143e8e8 re-cut as e3b6c8730, b0bd2d25e as 20382dd99 |
| `handoff/r10-ci-layout-p2-u0c-probe` | 65f112ec5 | in except 65f112ec5, the probe cut of `ci.yml`: dropped on purpose, probe-only |
| `handoff/r10-ci-layout-p2-pre` | 54c60b5ac | #2658, closed. Its (c), the `ghapi` 5xx retry, is in as 3585c7feb and 81900c11a. Its (a) and (b), b31fe0812 to b1de8abec, are superseded by the ruleset-off window |
| `handoff/r10-ci-layout-p2-policylint` | 4ef641145 | nothing outstanding: every commit is in this head |
| `handoff/r10-ci-layout-p2-probe-B1` | d4506f37e | probe-only, dropped on purpose: d4506f37e, 536fdb4b9 and c758cb770 are the Arm B 3a trivial edit and its neutralise |
| `handoff/r10-ci-layout-p2-probe-B2` | 14b8d768a | probe-only, dropped on purpose: 14b8d768a, d924db603, 4cf31cc50 and 89a4a44e7 are the 3g trivial edit, the 3d break and its neutralise |
| `handoff/r10-ci-layout-p2-probe-Btwin` | 69a9279a5 | probe-only, dropped on purpose: the twin's gate-file comment on main's layout |

After the merge these refs can be archived: every `handoff/r10-ci-layout-p2-*` ref in the table, `ci-probe/all`, `ci-probe/all-before`, `ci-probe/base` and `ci-probe/u0c{,-absent,-red,-skip}`. Arm B still reads probe-B1, probe-B2 and probe-Btwin until it reports.

## Forward-carry

- Delete required-contexts.json's `_pre_cutover` and `pre_cutover` keys after the PUT; owner: the step-22 beat (a "stale" print is not the carry). Carry: R10-CI-LAYOUT-P2
- Delete `tools/ci/gate.py`'s self-check that reads the old 17 as renamed after the PUT. Carry: R10-CI-LAYOUT-P2
- Delete `merge_train.py`'s A5 layouts pair (old 17 against new) after the PUT. Carry: R10-CI-LAYOUT-P2
- `same_sha_dup_heads` before and after (roster carry 1): measured on the combined control's opening runs, and patched into this body when Arm B reports. Carry: R10-CI-LAYOUT-P2

## Friction

`none`

