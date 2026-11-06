R10-PROCESS-SLIM: cards C4, C5, C8 and C6 (a) of the slip study, as written, plus the merge train's two defects (the post-merge docs step and the carry-ancestry park). content approved by tvofi in chat 2026-11-05. C6 (a) is folded in by the main seat's ruling; its half (b), the wake stream, is out of tree and not here.

Deletion over machinery throughout: `git diff --shortstat $(git merge-base origin/main HEAD)...HEAD` gives 38 files changed, 520 insertions(+), 1882 deletions(-) at the head below. Claim files, `VERSION`, the manifest version and the notes heading are untouched.

### Repair round 2 (verdict `blocked 481c7750 ci-red`, every finding built)

- **Finding 1, the block (`governance / instrument-self-tests` red):** the diff removed `handoff_push.sh`'s row push, and with it the `delivery_row self-test: N checks, 0 failed` line its `--self-test` printed, but `.github/workflows/governance.yml`'s step "Show the handoff push and its row writer refusing their own fixtures" still grepped that line. The grep is deleted and the step renamed "Show the handoff push refusing its own fixtures". `delivery_row.sh`'s own self-test stays pinned by its own step ("Show the delivery-row writer refusing its own fixtures") and by the open_pr/update_pr steps, so no pin is lost.
- **Finding 1, sweep (the property, not the instance):** rule: every step, in every `.github/workflows/*.yml`, whose `run:` text greps a `^<name> self-test:` line, replayed as the runner runs it (`bash --noprofile --norc -eo pipefail`, `RUNNER_TEMP` set), at the base and at the head, compared step by step. 70 steps matched at both ends; 20 are red at both ends in this container (a missing binary or an unset runner variable: environment, identical at the base) and exactly one differs, the handoff step above (base ok, head RED). At the fix it is ok. `grep -n delivery_row .github/workflows/*.yml` returns the delivery-row step (its own self-test: kept), the open_pr and update_pr steps (`open_pr.sh` and `update_pr.sh` still source `delivery_row.sh` and print its line: kept, green in the sweep) and the line this repair deletes. The other self-test summary lines the diff changed are counts only (`postmerge` 16 to 15 checks, `bus` 132 to 138), which every grep matches as `[1-9][0-9]*`.
- **Finding 3 (C8 `CHEAP_CHECKS`' vacuous entry):** re-derived: `.github/workflows/ci.yml`'s `pr-contract` job `needs:` every unit, so its check run does not exist while a head is WAIT and the entry never gated a dispatch. Dropped; the array is `tests / mutation`, `tests / typing`, `governance / policy-docs`. The class is pinned rather than the instance: `bus.sh`'s `cheap_caller_ok` reads `ci.yml` and the self-test requires every entry's caller job to need only `prelude`, with `pr-contract` and an absent job as its null control.
- **Verdict follow-ups:** the opening shortstat figure is re-taken above with its command; `dev/README.md`'s Record step no longer describes the deleted record-autofix job (it names `postmerge.py`'s #201 line and `delivery-status-tracking.md`). The errexit-scan residual stays dismissed as the verdict dispositioned it.
- **Root-cause countermeasure (defect-root-cause.md, second trigger):** `tools/pr/ci_predict.py` gains a STEP REPLAY arm, run by `prepr.sh` step 6d with SELF-TEST READS (`--record-self-tests`). It replays each `instrument-self-tests` step whose run text names a changed file, at the head, and predicts `PREDICT governance / instrument-self-tests STEP REPLAY <step>` only where the base's step of that name is green, so a step this container cannot run is a `NOTE`, never the branch's red. It reads governance.yml as text, because the runner's python has no `yaml` module (the in-tree seat harness found that on the first draft). The seat mutant harness (`dev/audit/harnesses/r10_seat_selftests_mutants.py`) retires `S08` with the row push it mutated, re-anchors `prepr-12` (its anchor no longer matched the `ARMS` line), and adds `bus-10`, `ci_predict-3` and `ci_predict-4`.

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

90bba85adaad2ce7b71372a5977f1a5df2509ec1: the reviewed head 481c7750755be454af93ce8bd8b12f336ed23bac plus this repair's commits, with origin/main merged twice: 5421413b54ba1044b8e91e1afd88b41acfc7a753 (at 0108578bdbe4b393e5ec00c8cd698a1765526d0f; delta `dev/programme/delivery/3239.md`, `3243.md`, the r10 roster, `tests/gate_lock.py`) and b36679ceaa65a08a67a84f0d934c93aa15f7c7f3 (read 2026-11-06T13:20Z; delta `dev/audit/harnesses/r10_triage_p391.py`, `dev/programme/delivery/3238.md`, `dev/programme/triage/s6-batch126.md` and its `tests/closures.json` entry). Neither delta touches a file this diff changes. `tools/pr/prepr.sh` ran clean at this head. Figures naming a file are taken at this head or at the last commit that changed that file (59c39580c390594b3324afa361e1ec72dfb76bac for `ci_predict.py`; 692d5b41eacda6893385a96fa4889cc7a280e9fa for the rest), stated per line where it is not this head.

## Mutation proof

Each production line deleted or neutralised, the named check run, restored. Through the in-tree harness `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py <ids>`, which runs governance.yml's own step for the file:

- `bus-10` (C8: `pr-contract / pr-contract` put back into `CHEAP_CHECKS`): KILLED, bus self-test 138 checks, 1 failed ("every cheap check's ci.yml caller needs only prelude").
- `ci_predict-3` (STEP REPLAY selects no step): KILLED, ci_predict self-test 2 failed. `ci_predict-4` (the base control excuses every red): KILLED, 1 failed.
- `bus-1` (dispatch RED arm) KILLED, 8 failed; `bus-2` (C8 cheap-check die) KILLED, 5 failed; `bus-7` (C4 already-verdicted head) KILLED, 1 failed.
- `S35`, `S36` (`handoff_push.sh`'s push lines replaced by `true`): KILLED, 3 and 2 failed. `postmerge-1`, `postmerge-2`: KILLED, 5 and 1 failed.
- `prepr-9` and `prepr-12` (graded by `prepr.sh`'s step), at 59c39580: KILLED. At 692d5b41 both were NOT RUN, `prepr.sh`'s step red unmutated: the first draft of STEP REPLAY's self-test ran a raw `git init`, which `tests/throwaway_git.py --check` and prepr's raw-git null control refuse; it now builds its repository with `throwaway_git_init`. `ci_predict-3` and `ci_predict-4` re-run at 59c39580: KILLED, 2 and 1 failed.

By hand (an out-of-tree driver editing the committed file and restoring its bytes): STEP REPLAY's other predicates: selection emptied, base control always excusing, never excusing, head replay ignored, and the arm unwired from `predict()`: each KILLED (2, 1, 1, 2 and 1 failed). The governance step itself: the deleted grep is the reviewed head's text, and replayed there the step exits 1 (`delivery_row-grep rc=1`), at the fix 0.

By hand at 0108578b (none of these files changed after it), each restored:
- `app_approve.sh carry()` rc distinction forced (`if true; then echo ... is not an ancestor`): `bash tools/pr/app_approve.sh --self-test` 324 checks, 2 failed ("saying it cannot read the ancestry", "and not calling it a non-ancestor"). The fetch removed: 3 failed ("CARRY: V and the head absent from the checkout are fetched, then judged", "printing CARRY: yes", "naming the ancestry").
- `release_worktrees`' collected check off: `python3 tools/audit/seat/merge_train.py --self-test` 446 checks, 1 failed ("a recarry worktree worktree_gc.sh already collected (unlisted, absent) is not removed again").
- `body_push.sh` head-stale comparison forced to pass: `bash tools/audit/seat/body_push.sh --self-test` 35 checks, 2 failed ("REFUSE head-stale: a stale ## Head is refused, naming both shas", "... and nothing is pushed to handoff-body/t").

## Null control

- Finding 1: the same step at the base (dc0a170b6) exits 0 with both greps rc 0; the sweep's other 69 steps read the same at base and head.
- STEP REPLAY: run against the reviewed head 481c7750 (the new `ci_predict.py` copied in) it prints `PREDICT governance / instrument-self-tests STEP REPLAY Show the handoff push and its row writer refusing their own fixtures: rc 1 at the head, 0 at the base`; at this head it predicts no red. Its self-test carries a head still printing the line, a step naming no changed file, and a step red at both ends (a note) as null arms.
- C8 caller pin: `pr-contract / pr-contract` and an absent job are refused by `cheap_caller_ok`; the three entries pass.

## Figures

- `git diff --shortstat $(git merge-base origin/main HEAD)...HEAD`: 38 files changed, 520 insertions(+), 1882 deletions(-).
- Step sweep (rule in the repair section; driver out of tree, its arm in tree as STEP REPLAY): 70 steps at the base and at 481c7750, 20 red at both ends in this container, 1 differing (the handoff step); at the fix that step exits 0.
- `python3 -I tools/pr/ci_predict.py --self-test`: 0 failed at 59c39580. `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main --only step-replay`: no red, 149 s wall at 692d5b41 (the arm's cost is the self-tests of the steps the diff names; it runs only under `--record-self-tests`).
- `bash tools/audit/seat/bus.sh --self-test`: 138 checks, 0 failed (136 at the reviewed head; the two new arms are the C8 caller pin and its null).
- `bash tools/audit/seat/handoff_push.sh --self-test`: 6 checks, 0 failed.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: ALL 2609 ENTITY CHECKS PASSED (after the `# never-empty:` marker on the new `CHEAP_CHECKS` loop, which `bare_array` refused first).
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. `node tools/policy/policy_lint.mjs`: 0 errors across 49 policy files; `node tools/policy/rules_sync.mjs --check` ok; `python3 -I tools/audit/seat/selftest_wiring.py --check`: 0 unwired, 0 index gaps; `python3 -I tools/audit/seat/ref_privacy.py --check`: 0 refused.
- `python3 tools/audit/archscore/score.py --diff dc0a170b671814be196a54b1c71e29449f54d6d7 HEAD`: `Architecture score: dS +0.0000 NULL`, at the reviewed head and at 692d5b41.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir <dir>`: `MODE: FULL` (nightly.yml changes the gate itself); CI runs the suite.
- `HPO_ALLOW_STALE_TOOLS=1 bash tools/pr/prepr.sh <body>`: run at this head; the run before it, at 59c39580, refused only `## Head` naming the earlier sha. `python3 -I tests/throwaway_git.py --check`: 0 raw git init or clone sites. `python3 tools/audit/carry_audit.py check --body <body> --branch fix/r10-process-slim`: 6 finding items, 6 routed.
- Card figures (RFT, verdict counts, token and job-minute estimates) are the slip study's, cited not re-taken.

## Red checks

Concluded reds at the reviewed head 481c7750755be454af93ce8bd8b12f336ed23bac (check-runs read across all pages by the reviewer, `verdict/3245`), each by its API name:

- `governance / instrument-self-tests`: class: own defect (CI wiring). Answer: fixed above. Cheaper detector: replaying the step's own run text before the handoff (seconds per step), which no local path ran; the fixer's figure printed the surviving `handoff_push self-test` line and not the vanished one. Countermeasure built: the STEP REPLAY arm in `prepr.sh` step 6d (`ci_predict.py`), shown above to predict this exact red at 481c7750; standing cost: the replayed steps' self-tests, 149 s at this head, only under `--record-self-tests`.
- `pr-contract / pr-contract`: class: downstream (body). `## Red checks` named neither `governance / instrument-self-tests` nor `budget-raise-gate / budget-raise-gate` by check-run name, and said no other check had concluded. Answer: this section names every one; the detector is `prepr.sh`'s body check, run on this body before the handoff.
- `budget-raise-gate / budget-raise-gate` (two runs): class: expected, owner. It reads the removed `files_tokens` cap of the deleted `proposal-triage.md` (489 -> None) as a raise; answered under `## Raise justification`; clears on tvofi's approving review at the head or the orchestrator's ruling under the mandate. Cheaper detector: `prepr.sh` predicted it; none cheaper exists.
- `gate` (two runs): class: downstream. The edit run's deferral red and the code run's red, which listed `budget-raise-gate / budget-raise-gate` and `pr-contract / pr-contract`; it clears when they do.

At this head no check has run (a handoff ref runs no workflow). Expected on it: `budget-raise-gate / budget-raise-gate` (the same raise) and `gate` until that clears; STEP REPLAY and the body check predict no other.

## Unpinned sites

n/a: the diff writes no line under `custom_components/`; every new `tools/` predicate is killed by an in-tree self-test arm listed under Mutation proof.

## Raise justification

The one raise the gate reads is `policy_budgets.json` `files_tokens` `dev/governance/roles/proposal-triage.md`: 489 -> None (its `files` cap, 36, falls under the `CAPFILE` rule, which reads a cap removed with its file as no raise; `files_tokens` has no schema rule and falls to frozen). No byte of policy grows: the file the cap measured is deleted by card C6 (a).
Payments tried: four, each below with its outcome; none removes the raise.
- Trim `proposal-triage.md` under its cap: not available, the file is deleted by C6 (a); nothing is left to trim.
- Keep the two caps for the deleted file: refused by `node tools/policy/policy_lint.mjs`: "dev/governance/roles/proposal-triage.md: has a cap ... but is matched by no POLICY_GLOBS pattern ... a cap that measures nothing reads exactly like one that holds" (1 error), measured by restoring the base's `policy_budgets.json` at this head.
- Keep the file as an on-demand contract: rejected, C6 retires the seat, and an unread contract is spent prose.
- Give `files_tokens.*` the `CAPFILE` rule in `tools/policy/budget_raise_gate.py`'s schema, as `files.*` has: not taken here. The gate runs from the pinned base copy, so it would not clear this PR, and widening what a raise gate accepts is a change of its own for the owner, not a payment.
Every other policy file this diff touches is paid inside its own cap: `policy_lint.mjs` 0 errors across 49 files.
Architecture score: dS +0.0000 NULL

## Forward-carry

- Follow-up (verdict): `CHEAP_CHECKS`' `pr-contract / pr-contract` entry could never gate a dispatch; built in this PR in `tools/audit/seat/bus.sh` (entry dropped, every caller pinned to `needs: prelude`).

  Carry: R10-PROCESS-SLIM
- Follow-up (verdict): the opening shortstat figure did not re-derive; re-taken with its command in this PR body's opening paragraph, which `tools/audit/seat/body_push.sh` pushes to `handoff-body/r10-process-slim`.

  Carry: R10-PROCESS-SLIM
- Follow-up (verdict): `dev/README.md`'s Record step described the deleted record-autofix job; corrected in `dev/README.md` in this PR.

  Carry: R10-PROCESS-SLIM
- Residual (verdict): `tests/entities.py`'s errexit-scan check loses its live-workflow plant arm with the record-autofix job; the synthetic arms in `tests/entities.py` still pin the scan.

  Carry: dismissed: the job the plant read is deleted, and a new live plant needs another errexit-shaped workflow step, which is not this group's scope.

## Carries

- Carry 1 (the roster's carry on R10-PROCESS-SLIM: a repair body's `## Head` named the previous handoff): `tools/audit/seat/body_push.sh` refuses `head-stale` when `## Head` does not name `handoff/<topic>`'s code sha, keeps the refused body at `handoff-wip/<topic>-body`, and pushes nothing.

## Friction

- r10-process-slim-1: cost: with the record stream retired, `merge_train.py --bot-prs` (`sweep_bots`, which merges record pull requests through `record_row.py`) likely has nothing left to merge; not measured here. Carry: dismissed: unmeasured, and deleting a live train path is beyond the cards' scope.
- r10-process-slim-3: cost: the self-test replay of instrument-self-tests is red for 20 of 70 steps in a cloud seat's container at the base, so a full replay is unreadable without a base control; STEP REPLAY carries one. Carry: dismissed: the arm's base control is the answer, and making every step runnable in a seat container is not this group's scope.
