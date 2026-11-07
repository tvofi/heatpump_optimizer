R10-PROCESS-SLIM: cards C4, C5, C8 and C6 (a) of the slip study, as written, plus the merge train's two defects (the post-merge docs step and the carry-ancestry park). content approved by tvofi in chat 2026-11-05. C6 (a) is folded in by the main seat's ruling; its half (b), the wake stream, is out of tree and not here.

Deletion over machinery throughout: `git diff --shortstat $(git merge-base origin/main HEAD)...HEAD` gives 43 files changed, 572 insertions(+), 1919 deletions(-) at the head below. Claim files, `VERSION`, the manifest version and the notes heading are untouched.

### Repair round 2 (verdict `blocked 481c7750 ci-red`, every finding built)

The measurements in this section were taken at earlier heads (343a0521 and before) and are history, not re-taken at 646dbcdd; the current head's figures are under `## Figures` and `## Mutation proof`, and a claim there marked not verified is not verified at this head.

- **Finding 1, the block (`governance / instrument-self-tests` red):** the diff removed `handoff_push.sh`'s row push, and with it the `delivery_row self-test: N checks, 0 failed` line its `--self-test` printed, but `.github/workflows/governance.yml`'s step "Show the handoff push and its row writer refusing their own fixtures" still grepped that line. The grep is deleted and the step renamed "Show the handoff push refusing its own fixtures". `delivery_row.sh`'s own self-test stays pinned by its own step ("Show the delivery-row writer refusing its own fixtures") and by the open_pr/update_pr steps, so no pin is lost.
- **Finding 1, sweep (the property, not the instance):** rule: every step of governance.yml's `instrument-self-tests` job that runs a command (100), replayed as the runner runs it (`bash --noprofile --norc -eo pipefail`, `RUNNER_TEMP` set, 180 s per step), at the base dc0a170b6, at the reviewed head 481c7750 and at this repair, compared step by step. It found the instance and three more reds the reviewed head made in the same job, which CI's log hid: `Refuse a push that names the host, and an unregistered pusher` failed (step 28 of job 127824863756: `ref_privacy.py --self-test`'s fixture "body_push refuses a handoff head authored by a runner default" read the new head-stale refusal before the identity guard), and the two steps after it (`Render the sweep template, and the policy re-read predicate`: the template cited the deleted `proposal-triage.md`; `Show the orchestrator tick deciding its own fixtures`: its D-1 pin required nightly.yml's deleted `record-autofix` push job) were skipped there only because the step before them failed. Each is fixed: `body_push.sh` runs the identity guard before the head-stale check, `tools/audit/seat/sweep_template.md` routes a proposal to the orchestrator, and the D-1 pin requires that nightly.yml run no job on a push. At this repair no step is red that is green at the base; three time out at 180 s at both ends in this container (the pre-PR self-check, the PR argument builder, the supervised beat), which CI runs to completion. An earlier, narrower pass (every workflow step grepping a `^<name> self-test:` line, 70 steps) found only the instance, which is why the rule above is the job's every step. `grep -n delivery_row .github/workflows/*.yml` returns the delivery-row step (kept) and the open_pr/update_pr steps (kept: both scripts still source `delivery_row.sh` and print its line).
- **Finding 3 (C8 `CHEAP_CHECKS`' vacuous entry):** re-derived: `.github/workflows/ci.yml`'s `pr-contract` job `needs:` every unit, so its check run does not exist while a head is WAIT and the entry never gated a dispatch. Dropped; the array is `tests / mutation`, `tests / typing`, `governance / policy-docs`. The class is pinned rather than the instance: `bus.sh`'s `cheap_caller_ok` reads `ci.yml` and the self-test requires every entry's caller job to need only `prelude`, with `pr-contract` and an absent job as its null control.
- **Verdict follow-ups:** the opening shortstat figure is re-taken above with its command; `dev/README.md`'s Record step no longer describes the deleted record-autofix job (it names `postmerge.py`'s #201 line and `delivery-status-tracking.md`). The errexit-scan residual stays dismissed as the verdict dispositioned it.
- **Root-cause countermeasure (defect-root-cause.md, second trigger):** `tools/pr/ci_predict.py` gains a STEP REPLAY arm, run by `prepr.sh` step 6d with SELF-TEST READS (`--record-self-tests`). It replays each `instrument-self-tests` step whose run text names a changed file, at the head, and predicts `PREDICT governance / instrument-self-tests STEP REPLAY <step>` only where the base's step of that name is green, so a step this container cannot run is a `NOTE`, never the branch's red. It reads governance.yml as text, because the runner's python has no `yaml` module (the in-tree seat harness found that on the first draft). A step is selected when its run text names a changed file, or names a tool whose own text names a changed script by file name: `ref_privacy.py`'s step names no `body_push.sh`, yet its self-test drives it. Against the reviewed head 481c7750 the arm predicts all three reds that replay at 180 s (the handoff step, the ref-privacy step, the orchestrator tick); the sweep-template step's red needs the template, which no changed script names, and stays the sweep's. The seat mutant harness (`dev/audit/harnesses/r10_seat_selftests_mutants.py`) retires `S08` with the row push it mutated, re-anchors `prepr-12`, `S12` and `S27`, and adds `bus-10` and `ci_predict-3` to `ci_predict-5`.
- **Roster carry 2 (`instrument-self-tests` cancelled at 30:03 of 30, #3239's review):** re-measured from the check-runs API: job 127760826703 ran every step green and was cancelled at the limit; job 127824863756 (this PR's, four steps skipped) ran 24:46. The three steps carrying `pr_args.sh`'s 3:20 self-test (its own, and `open_pr.sh`'s and `update_pr.sh`'s wrappers, which re-ran it) cost 10 minutes; the wrappers now run only `delivery_row.sh`'s self-test, and `pr_args.sh`'s runs once, in its own step. That run is about 23.5 minutes; one runner ran the same steps 1.35 times slower than another (the pre-PR step's 4:08 against 5:36), so `timeout-minutes` is 40 with the measurement in its comment. Shortening over a bare raise: the duplicate runs pinned nothing their own step did not.

### What changes, per card

- **C4 (verdict carry):** `bus.sh dispatch` without `--reviewed-head` derives it from `verdict/<pr>`'s latest `Fix review: merge <sha>` (`last_merge_verdict`), so the existing `review_carry.py` refusal applies by default, and a second reviewer at the very head a merge verdict names is refused. The carry predicate is unchanged (`app_approve.sh --carry`: main merges git resolved itself, claim files unioned, the branch's own diff equal to the reviewed one). `fix-review.md` step 12 states it.
- **C5 (paperwork is a note):** `fix-review.md` blocks only on code, tests and harness; `carry-missing` and `root-cause-*` become `Note:` lines the orchestrator resolves at merge. The web wave's reviewer prompt (`.claude/workflows/web-fix-wave.js`) says the same; its routing of an old `blocked ... root-cause-*` verdict to the root-cause seat is unchanged. A note on `custom_components/` is still a block. The per-PR delivery row is retired: `bus.sh dispatch` no longer demands it, `handoff_push.sh` no longer writes it, `governance / delivery-status`, `delivery-status-publish` and Nightly's `record-autofix` (the record PR stream) are deleted, and `governance / record`'s refusal step is report-only. `delivery-status-tracking.md`, `defect-root-cause.md`, `finding-propagation.md`, `fixer.md`, `orchestrator.md` section 9, `standing-dispatch.md` and CLAUDE.md follow.
- **C8 (review after the cheap checks):** `bus.sh dispatch` on a WAIT head refuses while any of `CHEAP_CHECKS` (`tests / mutation`, `tests / typing`, `governance / policy-docs`) is still in flight; `bus.sh post` refuses a `merge` verdict at a head `merge_train.py classify` calls RED, and an unreadable classification.
- **C6 (a):** `dev/governance/roles/proposal-triage.md` is deleted; the orchestrator or owner rules a proposal directly. Changed: CLAUDE.md role table (row removed), `orchestrator.md` section 5, `standing-roster.md`, `D11.md` item 5, `policy_budgets.json` (its two cap keys, which `policy_lint.mjs` refuses once the file is gone), `tests/closures.json` (its phantom entry, by `tests/closure.py prune`). `.claude/rules` and `.cursor/rules` regenerated by `tools/policy/rules_sync.mjs`.
- **Train docs step: REMOVED.** `postmerge.py`'s `docs` step ran `state_docs.py --push` after each merge while the `plan-beat` (`beat_jobs.py`) pushes the same state ref; a ref moved between the step's read and its push was rejected, and the cut stderr printed `OWED docs: rc 2: hi...`. One writer owns the ref already, so the duplicate writer is deleted. `release_worktrees` now reads `git worktree list --porcelain` once and logs `released <wt> (already collected)` for an unregistered, absent path that `tools/audit/worktree_gc.sh` already collected.
- **Train carry ancestry: FIXED** in `app_approve.sh carry()`: it fetches an absent verdict or head by sha from origin, refuses `is not an ancestor of` only on `git merge-base --is-ancestor` rc 1, and prints `cannot read the ancestry ... not judged` otherwise.

### Owner constraint, per change (why the risk is acceptable; what still guards production)

- **C4:** only an unchanged own diff carries, and a red CI never carries. `tests / mutation`, goldens, the features suite and CodeQL run on every head as before; Opus review of a production diff still runs whenever the own diff changes.
- **C5:** no code, test or harness class moved; a note on `custom_components/` blocks. The reviewer's real classes (mutation-vacuous, class-open, metric-gamed, architecture-unsound, head-moved) are unchanged; `carry_audit.py` in `pr-contract` still refuses a body line with no `Carry:` marker.
- **C8:** only checks under 10 minutes are waited on; `tests / fast` and the gate are not. Limit stated: a cheap check GitHub has not yet created reads as not in flight, so a dispatch in CI's first seconds proceeds; the post gate then refuses a merge verdict at a head that went red. The post gate reads `merge_train.py classify`, so it refuses at a gate RED; a non-required red reaches it through `pr-contract` and the gate.
- **C6 (a):** no production check reads the triage seat.
- **Train fixes and the STEP REPLAY arm:** no production check changes; the arm only adds a prediction before the handoff.

## Approval

content approved by tvofi in chat 2026-11-05 (cards C2-C9 accepted; C4, C5, C8 and C6 (a) are this group's). The policy files this diff changes: CLAUDE.md, `dev/governance/rules/defect-root-cause.md`, `delivery-status-tracking.md`, `finding-propagation.md`, `dev/governance/roles/fix-review.md`, `fixer.md`, `orchestrator.md`, `standing-dispatch.md`, `standing-roster.md`, `dev/governance/dimensions/D11.md`, `dev/governance/config/policy_budgets.json`, `dev/governance/roles/proposal-triage.md` (deleted), with `.claude/rules` and `.cursor/rules` regenerated. Repair 2 changes no policy file. tvofi posts the approving review at the head.

## Head

646dbcdd106cf45e39ba571fc2f2628080837c92

The code head `handoff/r10-process-slim`. It is the earlier head 343a05219ecf1ab6974755863e9405b26713dd87 plus merges of origin/main and of #3242, #3248 and #3253 (their files are outside this diff's 43). Merge base with origin/main: 28482eceeb6b9809e44b12d80fc994282cc21645. origin/main now reads 80016a71f567d936450d8708abcbb79d9e8071d7, ahead of the merge base. This body re-takes every figure below at the head above with its own command (2026-11-07); a claim not re-derived is marked not verified.

## Mutation proof

Re-run at 646dbcdd106cf45e39ba571fc2f2628080837c92 through `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py S12 S27 bus-10 ci_predict-3 ci_predict-4 ci_predict-5 bus-1 bus-2 bus-7 S35 S36 postmerge-1 postmerge-2 prepr-9 prepr-12`: `RESULT survivors=0`, all 15 KILLED:

- `S12` (open_pr.sh), `S27` (update_pr.sh): KILLED.
- `bus-10` (`pr-contract / pr-contract` back in `CHEAP_CHECKS`): KILLED, bus self-test 141 checks, 1 failed. `bus-1`: 8 failed; `bus-2`: 5 failed; `bus-7`: 1 failed.
- `ci_predict-3`: KILLED, 2 failed; `ci_predict-4`: 1 failed; `ci_predict-5`: 1 failed.
- `S35`: 3 failed; `S36`: 2 failed (handoff_push self-test, 6 checks).
- `postmerge-1`: 5 failed; `postmerge-2`: 1 failed (postmerge self-test, 15 checks).
- `prepr-9` and `prepr-12`: KILLED rc=2 (a mutated `prepr.sh`/`ci_predict.py` no longer parses, so the kill is a syntax error; the same two read KILLED by `prepr.sh`'s step at earlier heads).

Not verified at this head (carried from earlier heads, not re-run): the by-hand mutants of STEP REPLAY's other predicates, of `app_approve.sh carry()` (rc distinction, fetch), of `release_worktrees`' collected check, and of `body_push.sh`'s head-stale comparison. Their self-tests are green here (see Figures), which shows the arms hold, not that each mutant dies.

## Null control

- Re-derived at 646dbcdd106cf45e39ba571fc2f2628080837c92: `bus.sh --self-test` carries the C8 caller pin and its null (`pr-contract / pr-contract` and an absent job refused by `cheap_caller_ok`); the `bus-10` kill above is that arm biting.
- Not verified at this head: the base-versus-reviewed-head comparisons of the governance step (dc0a170b6 exit 0 against 481c7750 exit 1), the STEP REPLAY prediction against 481c7750, and the hidden-red self-test counts at 481c7750. They are earlier-head measurements and are left in the repair section as history.

## Figures

At 646dbcdd106cf45e39ba571fc2f2628080837c92:

- `git diff --shortstat $(git merge-base origin/main HEAD)...HEAD`: 43 files changed, 572 insertions(+), 1919 deletions(-).
- `bash tools/audit/seat/bus.sh --self-test`: 141 checks, 0 failed.
- `bash tools/audit/seat/handoff_push.sh --self-test`: 6 checks, 0 failed.
- `bash tools/pr/app_approve.sh --self-test`: 324 checks, 0 failed.
- `python3 tools/audit/seat/merge_train.py --self-test`: 468 checks, 0 failed.
- `bash tools/audit/seat/body_push.sh --self-test`: 35 checks, 0 failed.
- `python3 -I tools/pr/ci_predict.py --self-test`: 0 failed.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `node tools/policy/policy_lint.mjs`: 0 errors across 49 policy files; `node tools/policy/rules_sync.mjs --check`: ok.
- `python3 -I tools/audit/seat/selftest_wiring.py --check`: 117 self-testing, 117 wired, 0 unwired, 0 index gaps.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: 0 refused.
- `python3 -I tests/throwaway_git.py --check`: 0 raw git init or clone sites.
- `python3 tools/audit/archscore/score.py --diff dc0a170b671814be196a54b1c71e29449f54d6d7 HEAD`: `Architecture score: dS +0.0000 NULL`.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: `MODE: FULL` (nightly.yml changes the gate itself).
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: 2613 of 2614 pass, 1 fails: "a stand-in on PATH wins in a bash -c under a BASH_ENV that re-prepends a toolchain (#2835)", which reads the cloud seat's exported BASH_ENV/toolchain. Whether it also fails at the base in this container was not measured (not verified); CI runs the suite.

Not verified at this head: the step sweep (70 steps), the STEP REPLAY run (`ci_predict.py --only step-replay`), `tools/pr/prepr.sh` as a whole (this re-take runs its body check, not the full script), and the `instrument-self-tests` job timing. Card figures (RFT, verdict counts, token and job-minute estimates) are the slip study's, cited not re-taken.

## Red checks

Concluded reds at the reviewed head 481c7750755be454af93ce8bd8b12f336ed23bac (check-runs read across all pages by the reviewer, `verdict/3245`), each by its API name:

- `governance / instrument-self-tests`: class: own defect, four steps (the delivery_row grep; the ref-privacy self-test; and the sweep template and orchestrator tick, skipped in CI behind it). Answer: fixed in repair 2. Cheaper detector: replaying the step's own run text before the handoff; countermeasure built: the STEP REPLAY arm in `prepr.sh` step 6d (`ci_predict.py`), killed by `ci_predict-3`, `-4` and `-5` above.
- `pr-contract / pr-contract`: class: downstream (body). `## Red checks` named neither `governance / instrument-self-tests` nor `budget-raise-gate / budget-raise-gate` by check-run name. Answer: this section names every one; the detector is `prepr.sh`'s body check.
- `budget-raise-gate / budget-raise-gate` (two runs): class: expected, owner. It reads the removed `files_tokens` cap of the deleted `proposal-triage.md` (489 -> None) as a raise; answered under `## Raise justification`; clears on tvofi's approving review at the head or the orchestrator's ruling under the mandate.
- `gate` (two runs): class: downstream. Listed `budget-raise-gate / budget-raise-gate` and `pr-contract / pr-contract`; clears when they do.

At 646dbcdd106cf45e39ba571fc2f2628080837c92 no check has run (a handoff ref runs no workflow). Expected on it: `budget-raise-gate / budget-raise-gate` (the same raise) and `gate` until that clears.

## Unpinned sites

n/a: the diff writes no line under `custom_components/`; every new `tools/` predicate is killed by an in-tree self-test arm listed under Mutation proof.

## Raise justification

The one raise the gate reads is `policy_budgets.json` `files_tokens` `dev/governance/roles/proposal-triage.md`: 489 -> None (its `files` cap, 36, falls under the `CAPFILE` rule, which reads a cap removed with its file as no raise; `files_tokens` has no schema rule and falls to frozen). No byte of policy grows: the file the cap measured is deleted by card C6 (a).
Payments tried: four, each below with its outcome; none removes the raise.
- Trim `proposal-triage.md` under its cap: not available, the file is deleted by C6 (a); nothing is left to trim.
- Keep the two caps for the deleted file: refused by `node tools/policy/policy_lint.mjs`: "dev/governance/roles/proposal-triage.md: has a cap ... but is matched by no POLICY_GLOBS pattern ... a cap that measures nothing reads exactly like one that holds" (1 error), measured by restoring the base's `policy_budgets.json` at this head.
- Keep the file as an on-demand contract: rejected, C6 retires the seat, and an unread contract is spent prose.
- Give `files_tokens.*` the `CAPFILE` rule in `tools/policy/budget_raise_gate.py`'s schema, as `files.*` has: not taken here. The gate runs from the pinned base copy, so it would not clear this PR, and widening what a raise gate accepts is a change of its own for the owner, not a payment.
Every other policy file this diff touches is paid inside its own cap: `policy_lint.mjs` 0 errors across 49 files at the head above.
Architecture score: dS +0.0000 NULL

## Forward-carry

- Residual (verdict): `tests/entities.py`'s errexit-scan check loses its live-workflow plant arm with the record-autofix job; the synthetic arms in `tests/entities.py` still pin the scan.

  Carry: dismissed: the job the plant read is deleted, and a new live plant needs another errexit-shaped workflow step, which is not this group's scope.

## Carries

- Carry 2 (`instrument-self-tests` cancelled at its 30-minute timeout): answered in the repair section above; `open_pr.sh` and `update_pr.sh` stop re-running `pr_args.sh`'s self-test, and the timeout is 40 with the measurement in its comment.
- Carry 1 (the roster's carry on R10-PROCESS-SLIM: a repair body's `## Head` named the previous handoff): `tools/audit/seat/body_push.sh` refuses `head-stale` when `## Head` does not name `handoff/<topic>`'s code sha, keeps the refused body at `handoff-wip/<topic>-body`, and pushes nothing.

## Friction

- r10-process-slim-1: cost: with the record stream retired, `merge_train.py --bot-prs` (`sweep_bots`, which merges record pull requests through `record_row.py`) likely has nothing left to merge; not measured here. Carry: dismissed: unmeasured, and deleting a live train path is beyond the cards' scope.
- r10-process-slim-3: cost: the self-test replay of instrument-self-tests is red for 20 of 70 steps in a cloud seat's container at the base, so a full replay is unreadable without a base control; STEP REPLAY carries one. Carry: dismissed: the arm's base control is the answer, and making every step runnable in a seat container is not this group's scope.
