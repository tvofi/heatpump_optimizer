# R10-CI-LAYOUT-P2: execution plan (planning stage only)

Planning seat, read-only. Base: origin/main `738d950aa` (2026-10-22T13:48Z).
Read for this plan:
- the roster group at `origin/handoff/audit-r10-roster`;
- DESIGN-P2.md at `1371a0a6` (copy: `/private/tmp/claude-501/s4/p2plan/DESIGN-P2.md`);
- PLAN.md and DESIGN-REVIEW.md at `origin/plan/ci-layout` (`4a9b0975b`);
- the blocked body at `origin/handoff-body/r10-ci-layout-p2`;
- #2579's diff, read through `refs/pull/2579/head`.

Nothing was pushed, opened or run. **(est.)** marks a figure that was not measured.

Done on main already:
- PR 0 (the stub `ci.yml`). Arch-score payment (a) is in too: the pair sits in
  `lane_golden`, `tests/run.sh:593-594`.
- PR G.
- PR 1 (#2585): `nightly.yml` and `.github/actions/nightly-ha` exist.

So the fan-out's precondition, "the stub must be on `main`", holds today.

---

## 0. Approved decisions (revision 2, 2026-10-22)

The plan was approved with triage P6's changes. The Plan amendment is #201 comment
6343078022. This revision applies them.

1. **The P2a/P2b split is approved.** Any interface change found by the U0 live probes
   lands in **P2b**, never in a P2a-prime. P2a's body says so.
2. **Probe refs are `ci-probe/<unit>`**, plus `ci-probe/<unit>-before`, `ci-probe/all`
   and `ci-probe/base`. They are never `probe/...`, because `cloud_relay.sh`'s probe
   arm lists `refs/heads/probe/*` and reports every non-`rev-*` ref as OWED
   (`cloud_relay.sh:36-37,168-177`).
   - Verified at `738d950aa`: `bus.sh` `snapshot()` (l.270-274) enumerates only
     `handoff|handoff-body|review|verdict`. Its orphans fetch (l.508-511) takes only
     `main`, `handoff/*`, `handoff-body/*` and `fix/*`. `cloud_relay.sh` lists only
     `refs/heads/probe/*` (l.172) and `handoff/*` + `handoff-body/*` (l.206). Both
     ignore `ci-probe/*`.
   - P2a (unit UP) adds `ci_probe.py`'s push site to `ref_privacy.py` `PUSHERS` and a
     `ci-probe/` family to `prune_refs.py`'s deletion set.
   - Control: a planted `ci-probe/x` ref leaves `cloud_relay.sh` `probe_arm` output and
     `bus.sh` orphans output unchanged. The null: a planted `probe/foo` ref is still OWED.
   - DESIGN-P2 §10's ref names are amended by the Plan amendment.
3. **`ci_probe.py` is trimmed.** P2a keeps `push`, `dispatch`, `rerun-job`, `cancel`,
   `label`, `retarget`, `close`, `review` and `dismiss-review`. `sarif-upload`,
   `dismiss-alert` and `workflow-disable` move to **P2b with U6**.
4. **The fan-out is trimmed to about 11 cloud seats.**
   - Merged seats: U4+U11, U8+U10, U9b+U9d+U9p, and U1+U2+U7 (already merged).
   - **U6-lib and U0b run on sonnet**, each with its oracle (`measure/rev/alert_list.py`
     and its mutants; the sweep self-test).
   - Opus stays on U0a, U0c, U9c, U5 and U9a.
   - The shared BEFORE twin is re-taken **only if** `git diff <twin-base> origin/main --`
     over the files the twin touches is non-empty.
5. **The ci-ratchet job is sub-unit U5b**, with its own seat or commit range and its own
   `run.sh` accounting.
   - The null control: `script_runs_per_push == 54`, unchanged.
   - The mutant: dropping the lane-skip leaves `fast` unchanged, which is red.
   - The body describes the payment as headroom: about 5 min, 10 %, against +15 % runner
     variance. It is not described as forced.
6. **Identity of the security-side writes.**
   - The U8 approving review, and its dismissal, come from the **owner account (tvofi)
     under mandate 6329234399, run by the orchestrator**, never by an App.
   - U6's SARIF upload and alert dismissal are orchestrator writes under the mandate.
7. **Decisions from revision 1 that still stand.**
   - M-2 ships `gate-sweep.yml` (§5).
   - M-3's evidence is about 5 reads, with keep as the default (§5).
   - Merge #2579 before P2a's glue (§8).
   - Every live write is local (§2).

---

## 1. Units as amended (A1-A6, B1-B9), with files, size, dependencies, and where they run

Sizes are production lines added or changed (est., from the design's sketches and the
byte size of the measure scripts they port), then test lines. The fixer bound is about
400 production lines (`fixer.md`). U0 and U9 exceed it, so they are cut into sub-units.

| unit | files | prod / test lines (est.) | depends on | runs as | lands in |
|---|---|---|---|---|---|
| **U0a** gate core | `tools/ci/prelude.py` (kind/pr/base/scope/legs derivation, A2 item 2 kinds); `tools/ci/gate.py` predicate + `--refresh` + A1 item 4 `RATE-LIMITED` outcome (fail closed, no re-run before `X-RateLimit-Reset`); B3 `REQUIRED[push]` enumerated by command from `tests.yml`; `tools/policy/fixtures/required-contexts.json` gains `gate_required` (additive, `contexts` unchanged); `tests/closure.py` `GATE_FILES += tools/ci/` | 400 / 250 (`gate_replay2`/`gate_sim` adapted to drive the port, TAIL and EARLY arms, fork plant R3-4) | nothing (offline) | **cloud, opus**, handoff `handoff/r10-ci-layout-p2-u0a` | P2a |
| **U0b** sweep | `gate.py --sweep --run` (N5-1 attempt keying, N5-4 status set, poll ≥ 60 s per tvofi 2026-10-19, one runs listing per poll, 600 s bound, attempt cap 45); `tools/audit/seat/sweep_driver.py` (`--chain`/`--nochain`, idle 900 s, ≥ 60 s poll, 403 back-off, A1 item 5) + `INSTRUMENTS.md` row | 350 / 200 | the P2a interface contract (§3.1); runs in parallel with U0a | cloud, **sonnet** (oracle: the sweep self-test, `driver_arm.py`) | P2a |
| **U9c** ruleset instrument | `tools/ci/ruleset_cutover.py` (`--dry-run`/`--apply`/`--rollback`, `set -e` semantics, absolute rollback path, the review's §4 preconditions 3a-3e, two-half read-back, rollback triggers printed), self-test over saved JSON, wired in `instrument-self-tests` | 250 / 150 | nothing | cloud, **opus** (it drives a security setting) | P2a |
| **UP** probe instrument (new; §2) | `tools/audit/seat/ci_probe.py`, trimmed to `push`/`dispatch`/`rerun-job`/`cancel`/`label`/`retarget`/`close`/`review`/`dismiss-review`; its `PUSHERS` row in `ref_privacy.py`; the `ci-probe/` family in `prune_refs.py`; the relay/bus null control (§0 item 2); `INSTRUMENTS.md` row, self-test with `tests/throwaway_git.py`, mutants under per-file ids (`ci_probe-1`…) inside its own block of `r10_seat_selftests_mutants.py` | 300 / 200 | nothing | cloud, sonnet | P2a |
| **U6-lib** alert lister | `tools/ci/alert_list.py`, ported from `measure/rev/alert_list.py`: N5-2 alert-level dismissed subtraction, N5-3 pinned `sort`/`direction`, 404 fails closed; its self-test and the `alert_list_mutants.sh` cases | 300 / 150 | the P2a interface contract (§3.1) | cloud, **sonnet** (oracle: `measure/rev/alert_list.py` and its mutants) | P2a |
| P2a glue | `governance.yml` `instrument-self-tests`: one step per new self-test; entities pins (`gate.py` `REQUIRED` == fixture `gate_required`; the forgery pins that need no `ci.yml`); `tests/closure.py` classification; `selftest_wiring.py --check` reads N/N/0 | 120 / 80 | U0a, U0b, U9c, UP, U6-lib | **local, integration seat (opus)** | P2a |
| **U0c** umbrella skeleton | real `ci.yml` (run-id `concurrency`, `run-name` ending in `sha=`, prelude/refresh/gate/cancel-superseded, `pull_request` types incl. `edited` + `labeled` (A2 item 1), `pull_request_review`, `push`, `merge_group` (D-3, K9), `workflow_dispatch`); `gate-sweep.yml` (no `concurrency:`); entities `_cc_problems`/`_CC_TWIN_ROUTE`/`edited`/rerun-list/producer pins incl. "gate's `if:` cannot be false for any `on:` type, merge_group included" | 350 / 200 | P2a merged or its verdict head (stack) | cloud, opus | P2b |
| **U1+U2** hassfest, validate | `hassfest.yml`, `validate.yml` → `workflow_call`; maps | 40 / maps | U0c interface | cloud, sonnet (one seat) | P2b |
| **U3** codeql | `codeql.yml` `workflow_call`, legs from prelude, `scope`/`cancel-superseded`/`workflow_dispatch` removed, D-5 extracted-files soundness check | 150 / 80 | U0a (legs) | cloud, sonnet | P2b |
| **U4+U11** governance + kernel-points (one seat; U11's row below) | `governance.yml` → `workflow_call` + `schedule`, `concurrency`/`workflow_dispatch` removed, `push` guards kept | 60 / map | **#2579 and R10-RECORD-API-BUDGET merged first** (§8) | cloud, sonnet | P2b |
| **U5** tests (U5b split out, next row) | `tests.yml` inputs (`gate_scope`, `pr`, `base`, `head`, `recheck`, `no-skip`), `if:`s on `inputs.*`, `browser` step-level stand-down, autofix dispatch `ci.yml -f pr= -f base=`, approve steps retargeted (or deleted per M-3); **ci-ratchet carry**: new job `arch-instrument` running `tests/arch_score.py` + `tests/arch_score_head.py` under the closure-scope decision, `run.sh` lane-skip switch for the pair in `fast`, run.sh accounting kept complete, the pair's script-runs rows still emitted for `ci_ratchet.py` | 350 / 150 | U0c, PR 1 (merged) | cloud, opus | P2b |
| **U5b** ci-ratchet payment | `tests.yml` job `arch-instrument` running `tests/arch_score.py` + `tests/arch_score_head.py` under the closure-scope decision; a `run.sh` switch that skips the pair in `fast`, with its own "every script accounted for" accounting; the pair's script-runs rows still emitted. Null: `script_runs_per_push == 54`. Mutant: dropping the skip leaves `fast` unchanged (red). Described as headroom, not forced | 80 / 60 | U5 (same file; its own commit range) | cloud, sonnet | P2b |
| **U6** pr-contract | `pr-contract.yml` `workflow_call`, red filter `!= "pr-contract / pr-contract"` and `!= "gate"` (N4), code-scanning wait (≥ 60 s poll, the 10 min bound), step 5 via `tools/ci/alert_list.py` (R-10 option B); **plus `ci_probe.py` `sarif-upload`, `dismiss-alert` and `workflow-disable`** (moved here from P2a by decision 3) | 120 / 60 | U0c, U6-lib | cloud, sonnet | P2b |
| **U7** arch-score | `arch-score.yml` `workflow_call`, PR from inputs; D-2 | 40 / map | U0c | cloud, sonnet (shares the U1+U2 seat if it is free) | P2b |
| **U8+U10** budget-raise-gate + bots (one seat; U10's row below) | `budget-raise-gate.yml` `workflow_call`; the review trigger moves to `ci.yml`; `budget-raise-gate-rerun.yml` deleted; `budget_raise_gate.py --rerun-stale` retired into `gate.py --sweep` | 100 net / 60 | U0c, U0b | cloud, sonnet | P2b |
| **U10** bots | `merge-main.yml` (one dispatch, ref guard, `pushed.txt` + PR and base); `pr-contract-rerun.yml` and `tools/pr/contract_rerun.py` retired; M-3 outcome applied | 100 net / 40 | U0c, U5 | cloud, sonnet | P2b |
| **U11** kernel-points | `kernel-points.yml` → `workflow_call` + `workflow_dispatch` with the ref guard; its `cancel-in-progress` not ported; A2 items 1-5 | 60 / 40 | U0c | cloud, sonnet | P2b |
| **U9a** seat readers | `merge_train.py` (`DISPATCH`, `PR_ONLY=()`, `tests / nightly-status`, A5 both directions with the platform cross-check, `RATE-LIMITED` never a pass); `orchestrator_tick.py` (`PR_ONLY`, req = `gate_required` ∪ {gate}); `proof_watch.py`; `ci-watch.sh` fixtures; `autofix_statuses.sh`; `merge_main_bot.py` PIN_CHAIN; `stamp.py` push-`gate` reader (B3); `ci_ratchet.py:177,185` re-key, with (c)'s exclusion kept | 400 / 250 | U0a names | cloud, opus (A5 is adversarial) | P2b |
| **U9b+U9d+U9p** (one seat, after names are final): pins and agreement | `entities.py` (all section 9 rows not taken by U0c); `required-contexts.json` `contexts: ["gate"]`; `agreement_py.py`/`agreement.mjs`; `policy_lint.mjs` (`PR_CONTRACT_CHECK`, `MAIN_STATE_REPORTERS`, REPORTER_INPUTS); `codeowners_gap.py` | 350 / 100 | U0c, U1-U11 names | cloud, sonnet | P2b |
| **U9d** harness and CI readers | `ci_predict.py` + `ci_predict_replay.sh` + `failure_logs.sh` (prefixes; **carry 6**: `ci_predict.py` runs `pr-contract`'s `carry_audit` check, with a plant and a null); `prepr.sh` `REDS_JQ` (N4 filter + the alert listing, R4-1); `governance_cost.py`, `ci_script_seconds.py`, `superseded_runs.py`, `merge_throughput.py`, `dora_keys.py` | 300 / 120 | U0c, U6-lib | cloud, sonnet | P2b |
| **U9p** policy text | `ci-autofix.md`, `orchestrator.md` §11, `defect-root-cause.md:143`, `nudge.md:85,93`, `steward/SKILL.md:106`, `web-fragments.md`, `PULL_REQUEST_TEMPLATE.md:23`, `rules_sync.mjs` + `--check`; record: `HANDOVER.md` and `tests/README.md` | 100 / 0 | all names final; M-3 outcome | cloud, sonnet; **policy caps sit at zero headroom**, so it pays in the same files first | P2b |
| P2b assembly + combined control | `ci-probe/all`, `unitcheck2.py static` per unit against **current** main, the combined control (§10 steps 1-4 + A1 ≤ 700/h projection + A5 two heads + A4 twin-base check + `same_sha_dup_heads` before/after, carry 1) | – | everything | **local, integration seat (opus)** + probe-runner | P2b |

Why the live half runs locally:
- Every live check (M-1, M-3(a), M-4 to M-7, the U4-U8/U11 runtime pairs, U6 cases
  1-7, U8 review submit/dismiss, the combined control) is a GitHub write.
- Decisions 0011 and 0013 put those writes on this machine.
- So a cloud seat only ever produces the **offline** half: static maps,
  `unitcheck2.py static` rc 0, self-tests, and `gate_replay2`/`gate_sim` over the port.
- The probe-runner seat produces the live half. It writes the run ids and readings into
  each unit's evidence directory, and the unit's fixer is resumed (SendMessage) to judge
  them.

---

## 2. Every GitHub write, with its instrument, its runner, and its lifetime

Verified with `git ls-tree origin/main`. These instruments exist:
- `tools/pr/app_push.sh`, `tools/pr/approve_held_runs.sh`, `tools/pr/app_approve.sh`,
  `tools/pr/gh_comment.py`;
- `tools/audit/seat/open_pr.sh`, `handoff_push.sh`, `update_pr.sh`, `body_patch.sh`;
- `tools/audit/seat/bus.sh`, `merge_train.py`, `train.sh`, `prune_refs.py`,
  `pr_cap.py`, `cloud_dispatch.py`.

No instrument covers any of these:
- a probe-ref push (`app_push.sh --branch-only` accepts only `batch/<name>`);
- a workflow dispatch;
- closing a PR, cancelling a run, adding a label, a retarget;
- a review submit or dismissal;
- a SARIF upload or an alert dismissal;
- disabling a workflow.

Tools-live-in-repo forbids hand-rolling them. So **UP** (`tools/audit/seat/ci_probe.py`)
adds one subcommand per write. Each subcommand:
- reads `/rate_limit` first and refuses below 20 % remaining (A1 item 5);
- polls at 60 s or more;
- logs one line per write to the evidence directory.

UP is built first and lands in P2a. Until P2a merges, it runs from its handoff ref,
which is still committed and in the tree's history, never only in `/tmp`.

| # | write | instrument | runs it | lifetime |
|---|---|---|---|---|
| 1 | cloud fixer return refs `handoff/r10-ci-layout-p2-<unit>` + bodies | `cloud_dispatch.py` (orchestrator fires the trigger); the seat's own push of its handoff ref | cloud seat (git, not API) | kept until assembly |
| 2 | probe refs `ci-probe/<unit>`, `-before` (A4 twin), `-all`, `-base` (retarget target) | `ci_probe.py push` (git push; registered in `PUSHERS`). Verified inert: every `push:` trigger on main is branch-filtered to `main`/`master` or tags | probe-runner (local) | deleted after P2b merges by `prune_refs.py` |
| 3 | `workflow_dispatch` of `ci.yml --ref ci-probe/…` (U0 perturbations, U1-U3 and U5 dispatch pairs, U5 `recheck`/`no-skip`, combined step 4); BEFORE dispatches of `hassfest.yml`/`validate.yml`/`codeql.yml` at base | `ci_probe.py dispatch` | probe-runner | n/a |
| 4 | **draft probe PRs**: U0, U4, U5, U6, U7, U8, U11, the shared BEFORE twin (A4; re-taken only when `git diff <twin-base> origin/main` over the files the twin touches is non-empty), the combined control + its twin, step 3a's post-merge probe; about 12, **at most 4 open at once** | `open_pr.sh` (mints via `app_push.sh` as `hpo-author`, adds the delivery row, opens as a draft as `handoff_push.sh:181` does). Topic `r10-ci-layout-p2-probe-<unit>`. The body says "PROBE, throwaway draft, closed unmerged" and "Part of #2495" (no closing keyword). The row is needed so that a probe's `pr-contract`, and so its `gate`, can go green | probe-runner | **throwaway: every one is closed unmerged** (row 12) |
| 5 | probe PR code pushes (perturbations, plants, U6 plant/unplant) | `update_pr.sh` → `app_push.sh` with `PREPR_SKIP_CLOSURES=1` (tvofi 2026-10-21) | probe-runner | n/a |
| 6 | probe PR body-only edits (the edit events: "edit 1 s after push", U6 case 3) | `body_patch.sh` | probe-runner | n/a |
| 7 | approve held runs after every App push (until M-3 decides) | `approve_held_runs.sh` (`hpo-runs`) | probe-runner | n/a |
| 8 | re-run `gate` jobs (sweep, M-5(b), M-6) | `sweep_driver.py` → `gate.py --sweep` (seat token, `actions: write`) | probe-runner | n/a |
| 9 | M-5(a) throwaway lane-group twin of `ci.yml`, job re-run; M-1 cancel-while-pending | `ci_probe.py push` + `dispatch` + `rerun-job` + `cancel` | probe-runner | the twin ref is deleted afterwards |
| 10 | U11 `labeled` events; combined-control retarget | `ci_probe.py label` / `retarget` | probe-runner | n/a |
| 11 | U8 and combined step 3: review submit, then dismiss, on the budget-raising probe | `ci_probe.py review --approve` / `dismiss-review`, run with the **owner account (tvofi) under mandate 6329234399**, never an App (decision 6). Not `app_approve.sh`: it needs a bus `merge` verdict at the SHA | **orchestrator** | the review is dismissed in the same step |
| 12 | close every probe PR and set its row to closed | `ci_probe.py close` (PATCH `state=closed` as `hpo-author`), then `update_pr.sh --row-only` if the record lane does not close the row itself (uncertainty 3) | probe-runner | final |
| 13 | U6 case 4 SARIF upload (an empty python SARIF to `refs/pull/<N>/merge`, category `/language:python`) | `ci_probe.py sarif-upload` (lands in P2b with U6; token with `security-events: write`, this probe only) | **orchestrator** (a security-tool write) | permanent record on a closed PR's merge ref |
| 14 | U6 case 5 alert dismissal | `ci_probe.py dismiss-alert` (lands in P2b with U6) | **orchestrator** | permanent (dismissed) |
| 15 | P2a and P2b themselves: push and open | `handoff_push.sh` / `open_pr.sh` → `app_push.sh` | orchestrator | real PRs |
| 16 | verdicts, reviewer dispatch | `bus.sh dispatch` / `bus.sh` verdict path; `cloud_dispatch.py --role reviewer` | orchestrator | – |
| 17 | approval at the merged head (code-owned + policy) | `app_approve.sh` under mandate 6329234399 (scope `all`) | orchestrator | – |
| 18 | merges | `merge_train.py run` / `train.sh` (workflow PRs take `run`, never batch proof) | orchestrator (merge seat) | – |
| 19 | #201 comments, delivery rows, roster edits | `gh_comment.py` (read back), `delivery_row.sh`, `roster_edit.py`, `state_docs.py --push` | orchestrator | – |
| 20 | **ruleset 23698884 `required_status_checks` PUT** | `tools/ci/ruleset_cutover.py --apply` (lands in P2a); `--rollback` restores | **tvofi only** (a repository security setting) | one action at P2b's merge |
| 21 | rollback of the trigger path (if step 3a fails) | `ci_probe.py workflow-disable gate-sweep.yml` (lands in P2b), then `sweep_driver.py` per open PR | orchestrator | until the follow-up fix |
| 22 | after the cut-over: merge main into every open PR | `merge_train.py` "main merged in"; `merge-main.yml` handles only DIRTY ones | orchestrator | – |

---

## 3. Integration: P2a then P2b

**P2a, "umbrella engine, inert".** U0a + U0b + U9c + UP + U6-lib + glue. About 1720
production lines plus about 1030 test lines (est.); new files are most of it.
- **Mergeable alone, green under the 17:** no workflow trigger and no check name
  changes. The only workflow edit adds `instrument-self-tests` steps to
  `governance.yml`.
- **Sound alone:** each piece is a self-tested, CI-wired instrument.
  - `gate.py`'s `REQUIRED` is pinned equal to the fixture's new `gate_required`.
  - The ruleset instrument's `--dry-run` reads the live ruleset days before it is used.
  - `sweep_driver.py` and `ci_probe.py` are what the fan-out runs.
- **No dead window that matters:** `gate.py` has no caller until P2b, for about a day,
  but its self-test runs in CI.
- **Gates:** FULL (`tests/closure.py` gains `tools/ci/`). Code-owned
  (`/.github/workflows/`), approved under the mandate. Not policy.
- **What it buys:**
  - P2b's review surface drops by about half.
  - The two adversarial pieces get their own opus review: the gate predicate and the
    ruleset instrument tvofi will run.
  - Every unit cuts its probe ref from a base that already has the engine.

### 3.1 The P2a interface contract (binding on every P2a seat)

P2a is **not** one seat. It is about 1,720 production lines (est.), more than four
times the about-400-line fixer bound. The parts are independent once the contract
below is fixed, so they are built as **5 parallel cloud seats** (U0a, U0b, U9c, UP,
U6-lib). The integration seat then assembles them locally, with the glue.

1. **The API client.** All GitHub REST I/O inside `tools/ci/` goes through **one
   module, `tools/ci/ghapi.py`, owned by U0a**:
   - `get(path, params=None) -> Resp` and `post(path, body=None) -> Resp`, where
     `Resp = (status:int, headers:dict, json)`;
   - a `RateLimited(Exception)` raised on 403/429 whose body reads `rate limit exceeded`
     (A1 item 4), carrying `reset_epoch`;
   - `paginate(path, params)`;
   - the token from `GITHUB_TOKEN` / `GH_TOKEN`;
   - stdlib only (`urllib`).
2. **Injection.** Every other `tools/ci/` module (U0b's `tools/ci/sweep.py`, U6-lib's
   `tools/ci/alert_list.py`) is pure decision code over JSON. It takes an **injected**
   `get`/`post` with exactly that signature and raises or propagates `RateLimited`
   unchanged. Self-tests inject fakes. Nothing but `ghapi.py` imports `urllib`. The
   integration seat binds the injected functions to `ghapi` in P2a's glue.
3. **Entry points.**
   - `python3 -I tools/ci/gate.py --pr N --base B --kind K` (the predicate);
   - `--refresh`;
   - `--sweep --run <id>`. U0a's argparse dispatches to `sweep.main(argv, get, post)`;
     U0b writes `sweep.py` and must not edit `gate.py`.
   - `prelude.py` prints `key=value` lines for `$GITHUB_OUTPUT`, with the keys `kind`,
     `pr`, `base`, `scope`, `legs`.
   - Outcome words on stdout, first token: `PASS`, `FAIL <reason>`, `RATE-LIMITED`.
     A rate limit is never `PASS` and never re-run before `reset_epoch`.
4. **`REQUIRED`.** `gate.py` exposes `REQUIRED: dict[str, tuple[str, ...]]` keyed by
   event class. It is read by the entities pin against the fixture's new
   `gate_required` list, which is additive; `contexts` stays the 17 in P2a.
5. **Seat-side tools are not `tools/ci/`.** `sweep_driver.py` (U0b) and `ci_probe.py`
   (UP) live in `tools/audit/seat/` and use `gh api` (seat token), with:
   - a poll floor of 60 s;
   - a `/rate_limit` read before each write, refusing below 20 % remaining;
   - one log line per write.

   `ruleset_cutover.py` (U9c) uses `gh api` as the owner and is never run in CI except
   its offline self-test.
6. **Wiring.** Each seat delivers a `--self-test` that prints
   `<name> self-test: N checks, 0 failed`. The integration seat wires each one as a step
   in `governance.yml` `instrument-self-tests` (after #2579 merges) and re-runs
   `selftest_wiring.py --check` (N/N/0, rc 0). **Seats do not edit `governance.yml` or
   `tests/entities.py`**: the glue does.
   - Each seat classifies only its **own** new files in `tests/closure.py`, one line
     each, because `tests/entities.py` refuses an unclassified file.
   - U0a alone adds `tools/ci/` to `GATE_FILES`.
   - The integration seat resolves the adjacent-line conflicts in `closure.py`.
   - Every other file is touched by one seat only.
7. **Mutants.** Any seat-selftest mutants go in
   `dev/audit/harnesses/r10_seat_selftests_mutants.py`. They take per-file ids
   (`ci_probe-1`, `sweep_driver-1`), inside the instrument's own block, never appended
   at the end. Git repositories are built only through `tests/throwaway_git.py`.

**P2b, "cut-over".** U0c, U1-U8, U10, U11, U9a, U9b, U9d, U9p and the combined control,
assembled on `ci-probe/all`. About 2500 production lines (est.), about 40 reader
sites.
- **Cannot be split further and stay sound.** Its head produces `gate` and not the 17,
  so any part that converts a callee or renames a check can merge only after the PUT.
- **What would let a part land early:** callees made dual-trigger, or readers made
  dual-layout. Either one adds transitional code, re-cuts every unit's static map, and
  needs a later cleanup PR.
- **Fallback:** if P2b passes three review rounds (three-round rule), split out the
  layout-agnostic readers then. Those are A5's newest-`gate` reading and `stamp.py`'s
  reader written to fall back to the `Tests` push run.
- **Gates:** FULL. Code-owned and policy, approved under the mandate.
- **The ruleset PUT staging goes in P2b's body**, with:
  - `ruleset_cutover.py --dry-run` output at head H;
  - the rollback file path;
  - the preconditions;
  - the rollback triggers.

**Merge order:**
1. #2579.
2. P2a.
3. Then, at a wave boundary with the queue drained: freeze, P2b.

The probe refs stack on P2a's **verdict head** and do not wait for its merge (the A3
rule for U5 on PR 1). A unit re-cuts only if P2a's content changes after the verdict.

**Units into one reviewable P2b:**
- The integration seat cherry-picks each unit's handoff commits onto `ci-probe/all`.
- It re-runs `unitcheck2.py static` for every unit against **current** main. A dropped
  row is refused, not lost.
- Then it runs the combined control.
- At every merge of main it runs `selftest_wiring.py --check` and expects `N, N, 0`
  with rc 0 (carry 2).
- Its commits are ordered so a reviewer can read P2b one unit at a time: U0c, then the
  callees, then the readers, then policy.

---

## 4. Order of work and the critical path

T0 = dispatch of this plan. Cloud: at most 4 concurrent (design). Seat cap: 8 in total.

| step | content | after | wall (est.) | ends ≈ |
|---|---|---|---|---|
| 1 | cloud batch A: U0a, U0b, U9c, UP | T0 | 3 h | T+3 h |
| 1' | #2579 merges; R10-RECORD-API-BUDGET dispatched or held (§8) | T0 | – | – |
| 2 | cloud batch B: U6-lib, U0c (from U0a's interface), U9a, U9d (offline against the design names) | 1 (U0a) | 3 h | T+6 h |
| 3 | P2a assembled by the integration seat, prepr, open, FULL, review (opus), merge via `run` | 1, U6-lib | 4-5 h | T+8 h |
| 4 | U0 live on a draft probe from U0c over P2a's verdict head: M-1, M-3(a) (free), M-4, M-5(a)(b), M-6 both arms, M-7, the fork plant, the perturbations | 2 (U0c), 3 verdict | 4 h | T+10 h |
| 5 | cloud batch C: U1+U2+U7, U3, U4, U5 | U0c | 3 h | T+9 h |
| 6 | live: U1-U3 dispatch pairs; U4, U7 PR pairs; shared BEFORE twin | 4, 5 | 2 h | T+11 h |
| 7 | cloud batch D: U6, U8, U10, U11 | U0c, U5 (for U10) | 3 h | T+11 h |
| 8 | live: U5 (PR pair + 2 dispatch pairs), U6 cases 1-7, U8 (review submit/dismiss), U11, U10 (dry-run merge-main) | 6, 7 | 3 h | T+14 h |
| 9 | cloud: U9b, U9p (names final) | 8 | 2 h | T+16 h |
| 10 | assembly + combined control on `ci-probe/all` (events serial, about 46 min per code run) | 8, 9 | 5 h | T+21 h |
| 11 | P2b open, FULL + autofix, review (opus), about 2 rounds | 10 | 5 h | T+26 h |
| 12 | cut-over: drain, freeze, tvofi `ruleset_cutover.py --apply`, `merge_train.py run [P2b @ H]`, then the push `gate` (about 58 min) in parallel with step 3a (about 75 min); unfreeze | 11, at a wave boundary | 1.5 h | **T+27.5 h** |

**Critical path:** U0a → U0c → U0 live (M-5/M-6) → U5 live → combined control → P2b
review → cut-over. That is about 27 h. P2a's review runs beside it and is not on the
path, provided the probes stack on its verdict head.

---

## 5. M-2 and M-3: evidence and its cheapest source

**M-2 (whether `gate-sweep.yml` ships or is deleted).**
- **The question:** when several `gate` check runs sit at one head, does the merge box
  take only the newest, or every suite's latest?
- **A probe cannot answer it:** before the cut-over a probe's `gate` is not a required
  context, so `mergeStateStatus` does not decide (DESIGN-P2 R-8).
- **The tree already answers it, on a required context of the same shape.** One
  workflow writes the same check name from several runs at one head:
  `budget-raise-gate` from `pull_request` and from `pull_request_review`.
  `tools/policy/budget_raise_gate.py:619` records that GitHub's ruleset refuses a merge
  while any suite at the head carries a non-success run (#2009). Its self-test at :1176
  pins "an older red run beside a newer green one is still re-run".
- **That is the every-suite reading.** Under it the merge box does **not** read only
  the newest `gate`, so `gate-sweep.yml` is needed.
- **Decision: ship `gate-sweep.yml`, and run step 3a inside the freeze.** Cost: 0 API
  calls and 0 CI runs. The U8 probe still runs the sweep's functional check through
  `sweep_driver.py --nochain`. The probe-side M-2 readings (one GraphQL
  `statusCheckRollup`/`mergeStateStatus` read and one `check-runs?check_name=gate`
  read) are recorded only as observations.
- Deleting the sweep later needs a measurement on a required `gate` after the cut-over.
  That is a follow-up, never a reason to wait.

**M-3 (whether the held-run approve steps stay).**
- **(a)** Do App pushes and `GITHUB_TOKEN` pushes still leave runs `action_required`?
  The cheapest evidence, in order:
  1. Grep the local `approve_held_runs.sh` outputs on this machine for the last 7 days:
     the count of runs approved per App push (0 API).
  2. Read the "Approve the runs" step logs of the last 3 autofix job runs, where the
     `GITHUB_TOKEN` arm shows up (3 log reads, local `gh`; the cloud seat got 403s on
     the log host).
  3. Right after P2a's first App push, and **before** `approve_held_runs.sh` runs, list
     `actions/runs?head_sha=<H>&status=action_required` (1 call).

  Item 3 is the live plant. An App push known to hold would show the held run.
- **Rule:** any held run in the window → keep the approve steps (the design's default,
  retargeted to `ci.yml`). Zero across at least 10 App pushes and at least 3 autofix
  pushes → delete them per design. That deletion is a P2b policy edit: `nudge.md:85`,
  `INSTRUMENTS.md:36`, and retiring `approve_held_runs.sh`.
- **(b)** Does a held run shadow a green dispatched `gate`? This is only needed if (a)
  finds held runs. Before the cut-over it is not decisive (R-8), so keep the steps.
  Re-measure inside the freeze on P2b's own head, and remove them in a follow-up only
  if that measurement says so.
- **Total cost:** about 4-5 API reads, 0 extra CI runs.
- Carry 1 (`same_sha_dup_heads`) is tied to this outcome. Measure it before and after
  in the combined control, with `dev/audit/harnesses/superseded_runs.py`; the null
  control is a head with a single run.

---

## 6. The ci-ratchet carry: fold into U5, and require it through `gate`

The blocked seat's recommendation stands, with one refinement. Since PR 0, the pair
already sits in `lane_golden` (`tests/run.sh:584-594`). Its own job is the second
payment.

**Why not a standalone PR:**
- A new job is not required until the ruleset names it.
- Before P2b, adding a required context means a second tvofi PUT.
- After P2b, `gate`'s `REQUIRED` covers it for free. That is B3's rule: required on PR
  and push events.
- The window reads 49.86 median against 54.825 at this base (the blocked seat's
  measurement, with a null). So nothing forces a payment before P2b.

**What U5 must also do:**
1. Run the new `tests / arch-instrument` job under the same closure-scope decision as
   `fast`. Name it apart from D-2's `arch-score / arch-score`.
2. Make `run.sh` skip the pair inside `fast` through an explicit switch. Its "every
   script accounted for" check must then count the pair in the new job, not drop it.
3. Keep `ci_ratchet.py`'s `script_runs_per_push` counting the pair's rows. Otherwise
   the ratchet silently loosens.
4. Prove it in two stages:
   - P2b's own FULL run shows `fast` ending at least 5 min sooner than the base's.
   - After the merge, the review's §3 window rule: 5 of 8 push runs, and never re-run
     a push run.

The re-keyed `ci_ratchet.py` (U9a) then measures the `tests / *` span of `ci.yml` push
runs.

**One reason to reconsider:** a new job costs about 2-3 min of runner set-up per code
run (est.). That is runner minutes, not wall-clock, so it does not change the decision.

---

## 7. Cost (est.)

**Seats:**
- **Cloud fixers, 13 after decision 4** (5 opus, 8 sonnet):
  - **opus at medium, 5:** U0a, U0c, U9c, U5 (with U5b as its own commit range), U9a.
  - **sonnet, 8:** U0b, U6-lib, UP, U1+U2+U3+U7 (230 lines), U4+U11, U6, U8+U10,
    U9b+U9d+U9p.
  - Why not 11: P2a alone is 5 parallel seats under the interface contract (§3.1).
    Merging two of them would breach the about-400-line bound or serialise the
    critical path.
- **Local, 2:** the integration seat (opus, long-lived: P2a and P2b assembly, combined
  control) and the probe-runner (sonnet, long-lived, every write in §2).
- **Reviewers, 2:** opus, cloud, from detached worktrees (`fix-review.md`), one for
  P2a and one for P2b. Add 1 more per extra round.
- **haiku:** CI watching and check-run reads only.
- **Peak concurrency:** 4 cloud + 2 local + 1 reviewer = 7, under the cap of 8.

**Wall-clock:** about 27.5 h from dispatch to cut-over, on the critical path in §4.
Without the P2a split it is about 1.5 h shorter, but there is one XL review instead of
two halves.

**CI runs:**
- Probe events: about 70 in total.
  - U0 about 12; U1-U3 6; U4/U7 6; the twin 2 (re-taken once); U5 6; U6 10; U8 4;
    U10/U11 4; the combined control about 15; step 3a about 3.
  - Each PR event on a probe runs `ci.yml` plus the old workflows that probe has not
    converted: up to 12 runs per push.
  - So about 500-700 workflow runs.
- FULL cycles: P2a about 3, P2b about 4.

**API calls:**
- **Seat side** (user and App quotas):
  - polling at ≥ 60 s for about 14 h of live work, about 900 calls;
  - writes, about 250;
  - P2a/P2b instrument traffic, about 200;
  - total about 1350, spread at about 100-150/h, against 5000/h.
- **Repository `GITHUB_TOKEN`:** A1's ≤ 700/h projection is checked in the combined
  control.
  - The fan-out's own pressure is capped at 4 open probes.
  - Probe pushes pause while a merge train runs, and below 20 % remaining.
- **This planning seat:** 1 `gh pr view` (#2579) and 1 `git fetch` of
  `refs/pull/2579/head`; the rest was git.

---

## 8. Interaction with #2579 and the other CI-file groups

**#2579 (R10-FLOW-YIELD-PROBE).**
- **State:** open, draft, BLOCKED, REVIEW_REQUIRED, head `45754ede2`.
- **What it touches:** it adds 7 lines to `governance.yml`'s `instrument-self-tests`,
  directly after the `selftest_wiring.py --check` step. That is the same hunk P2a's
  glue appends to.
- **Rule:** merge #2579 **before** P2a is assembled. If it is not mergeable when P2a's
  glue is ready, P2a merges first and #2579 recarries; it is a trivially adjacent
  hunk.
- **Either way, before U4 cuts `ci-probe/governance`.** Otherwise U4's static
  map is taken from a `governance.yml` without the step, and assembly silently drops
  it (the move-PR silent revert).
- **Why the step survives U4:** U4 changes only triggers, `concurrency` and
  `workflow_dispatch`. So #2579's step rides through unchanged once it is on main.

**R10-RECORD-API-BUDGET** (queued; `governance.yml`, `policy_lint.mjs`).
- It owns the record job's API budget (M0-M3). P2 does not duplicate it.
- It must land before U4 and U9b cut their refs, or wait until after the cut-over and
  retarget to `governance / …` names.
- Recommendation: dispatch it now and merge it before step 5. That moves the freeze
  start; it does not extend it.

**R10-FLOW-MQ-PROBE** (not started; `tests.yml`, `pr-contract.yml`).
- Hold it until after the cut-over.
- Forward-carry K9 into its brief: the one required check is `gate`, which reports on
  `merge_group` (D-3; pinned in U0c).

**Freeze.** From the first probe-ref cut, CI-file edits by other groups stop until P2b
merges. The files:
- `tests.yml`, `governance.yml`, `codeql.yml`, `hassfest.yml`, `validate.yml`;
- `pr-contract.yml`, `arch-score.yml`, `budget-raise-gate.yml`, `kernel-points.yml`;
- `merge-main.yml`, `tests/run.sh`.

The exceptions above land before their unit cuts.

---

## RESULT

PR 2 is executable as **two pull requests**:
- **P2a**: the inert engine plus instruments. Green under the 17. FULL, code-owned.
- **P2b**: the cut-over. It carries the ruleset PUT staging; tvofi runs the instrument
  P2a lands.

Every live GitHub write runs locally, through:
- the existing minting and approval tools (`open_pr.sh`/`app_push.sh`, `update_pr.sh`,
  `body_patch.sh`, `approve_held_runs.sh`, `bus.sh`, `app_approve.sh`, `merge_train.py`);
- one new instrument, `tools/audit/seat/ci_probe.py`, built first and landed in P2a.

Cloud seats build units offline only, about 16 of them, at most 4 at once.
- M-2 is decided now from in-tree evidence (#2009): ship `gate-sweep.yml`.
- M-3 costs about 5 reads; default keep.
- The ci-ratchet pair moves to its own `tests / arch-instrument` job in U5, required
  through `gate`.
- Critical path about 27.5 h.

## CHECKS-RUN

- `git fetch`. Read the roster group, its brief and its 7 carries; `architect_note` is
  null.
- Read DESIGN-P2 §0, 2.1, 5, 7-10 and R-8 in full. PLAN.md and DESIGN-REVIEW.md in full.
- Read the blocked BODY.md.
- `git ls-tree` of `.github/workflows`, `tools/pr`, `tools/audit/seat` on origin/main.
- Placement of the arch pair: `run.sh:584-594`, in `lane_golden`.
- Push-trigger filters of every workflow: all `main`/`master`/tags, so probe-ref
  pushes are inert.
- `budget_raise_gate.py:612-625,1168-1180` (#2009).
- `app_push.sh`, `open_pr.sh`, `handoff_push.sh`, `approve_held_runs.sh` and
  `app_approve.sh` headers.
- CODEOWNERS.
- #2579's three-dot diff and its PR state (1 gh call).
- Roster stages of the related groups.

## UNCERTAINTIES

1. **The line sizes are estimates** from design sketches and the byte sizes of the
   measure scripts, not from a build. U5 and U9a are the likeliest to overrun.
2. **The #2009 evidence comes from `budget-raise-gate`'s runs.** It is the same shape
   as `gate`: one workflow, several runs, one check name, one head. But it was read
   from the tree's record, not re-measured.
3. **Whether a closed probe PR's delivery row closes itself through the record lane.**
   If it does not, it needs `update_pr.sh --row-only` per probe (§2 row 12).
4. **Whether the hpo-author App can open a draft directly.** `handoff_push.sh` opens
   it, then runs `gh pr ready --undo`. Either path works.
5. **Whether `tools/ci/` should be code-owned**, like the `budget_raise_gate.py` and
   `contract_rerun.py` it replaces. That is a CODEOWNERS (policy) edit.
6. **The step durations** come from the round-5 plan's anchors (2026-10-19). Main's
   push wall has since dropped (median 49.86 min).

## ESCALATE (revision 2)

Items 1-3 of revision 1 are resolved by the coordinator's decisions (§0). Open:
1. **The head for the payloads.** The coordinator asked for `--head` = the
   `handoff/audit-r10-roster` tip (`2501a0a16`).
   - `cloud_dispatch.py`'s own rule is that a fixer's head is main and never the
     roster ref ("a fixer must not fork from", `HEAD_REF = roster_lib.MAIN_REF`).
   - The fixer prompt also says "Fetch {head} for the base you were given".
   - So the payloads are rendered at origin/main `738d950aa`. A re-render at the roster
     tip changes one flag.
2. **Tell tvofi in advance** (orchestrator, on #201) about their one action:
   `ruleset_cutover.py --apply` at P2b's merge.
3. **#2579 must merge before the P2a glue** (it is still draft and BLOCKED).

## P2a dispatch (revision 2)

Five cloud fixer payloads, rendered and **not fired**:
`/private/tmp/claude-501/s4/p2plan/payloads/fixer-r10-ci-layout-p2a-{u0a,u9c,u0b,u6lib,up}.json`.
The briefs are in `briefs/full-<unit>.md`: the common block, the unit's brief, and
this plan's P2a section.

Firing order, at most 4 at once:
1. U0a (opus; on the critical path), U9c (opus), U0b (sonnet), U6-lib (sonnet). These
   are parallel under the §3.1 contract.
2. UP (sonnet), fired when the first slot frees. It is needed by P2a assembly and the
   live phase, not by any other unit.

After all five return on `handoff/r10-ci-layout-p2a-<unit>` plus their bodies, the
local integration seat (opus) does the following:
1. assembles them on one branch;
2. binds the shims to `ghapi`;
3. writes the glue (`instrument-self-tests` steps after #2579, the entities pins,
   the closure merge);
4. runs `selftest_wiring.py --check`;
5. hands off for `open_pr.sh`.
