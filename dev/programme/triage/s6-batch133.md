# Proposal triage, session s12, batch 133 (P406 onward)

The rolling batch after batch 132. It rules queue lines 81 to 95 of the orchestrator's triage queue, `s12-author-email-guard` to `s12-set-files-repeat-add`. Two lines are folded into the ruling of the line they extend:
- `s12-review-packet-nightly-status` (line 88) into P406;
- the measured addendum to `s12-roster-drain-stale-tracking-ref` (line 83) into P409.

Facts were read at origin/main `364353e67`, at the roster branch `3069eaa49`, through the REST API, and in the orchestration logs. The logs are host-local, so another seat can re-run those commands only on the host that holds them.

The bar is the owner's ruling of 2026-11-07. An instrument change ranks by the wall-clock it saves over the rest of the round, which closes about 2026-11-13. A change that saves 12 h or more is in the production tier. A CI-machinery bug that blocks every merge is in the hotfix tier. An audit class is not a proposal: `defect-root-cause.md` owes it a class-eliminating barrier, and this seat rules only on the barrier's form and destination.

## P406: red-checks retake class, with review-packet-nightly-status folded in (queue lines s12-red-checks-retake-class, s12-review-packet-nightly-status)

Verdict: ACCEPT changed. The class is real, and P405 does not cover it.
- **P405 does not cover it.** P405 carried only the head-note rule. It rejected red-checks-autolist because a handoff-time read cannot see a red that concludes later. This class is a refusal on a red that the diff did not cause, and that refusal comes after the handoff.
- **Three causes.** The seven instances split into three causes, and each is ruled by its own cause:
  - **(A) The nightly-status exemption is voided by a path that cannot redden that check. This is the barrier, accepted.** Four instances, plus line 88's #3275.
  - **(B) A cancelled `governance / instrument-self-tests`.** Its cause has an owner and a fix in flight, so no new barrier is owed.
  - **(C) A `codescan_wait` fail-closed that turned `gate` red.** It has an owner, R10-HOTFIX-GATE-BUSY-DEFER, so the instance is sent there. It is not a barrier here.
- **Both of the queue line's barriers are rejected:** the known-cause registry and the relay that re-takes `## Red checks` at each new head.

The destination for (A) is a carry on R10-BODY-CONTRACT (carries-open, PR 3227), which owns `tools/policy/policy_lint.mjs`. It is not taken on the >10 % exemption. As an audit-class barrier it is owed, not optional.

Source: the orchestrator's queue lines of 2026-11-07, at 17:45:31Z with the 18:14Z update, and the roster-audit2 M7 line.

Instances (the check-runs at each PR's current head, by `gh api repos/tvofi/heatpump_optimizer/commits/<head>/check-runs?per_page=100`; the files by `gh pr view <n> --json files`):
- **The rule today.** `policy_lint.mjs` exempts `MAIN_STATE_REPORTERS` (`tests / nightly-status`, `governance / delivery-status`) from `## Red checks`. The exemption is VOID when the diff touches any path in the one shared set `REPORTER_INPUTS`, and that set includes `.github/workflows/governance.yml`.
- **Where the check lives.** `tests / nightly-status` is a `tests.yml` job (line 1396). Its one step runs the BASE's `tests/nightly_status.py`, which is restored from `github.event.pull_request.base.sha`, checked byte-identical and run under `-I -S`. No path in `governance.yml` can change what it reports at a pull-request head. `governance.yml` is in the set for `delivery-status`'s sake (its job is at line 1727).
- **Cause A, four instances, each with a pr-contract log line** (`gh api --allow-escape-sequences repos/tvofi/heatpump_optimizer/actions/jobs/<id>/logs`):
  - #3264 (job 128470376626), #3267 (job 128463906157) and #3294 (job 128477471244) print `red checks the body must answer: ,tests / nightly-status`.
  - #3275 (R10-HOTFIX-SELFTEST-TIMEOUT, line 88's instance) is also refused on nightly-status, by its file list.
  - The only reporter input that any of the four touches is `.github/workflows/governance.yml`.
- **Cause B.**
  - #3293's head has `governance / instrument-self-tests` `cancelled` at 17:08:06Z.
  - #3295 had the same at an earlier head, by the queue line. Its current head shows only `tests / nightly-status`, and its diff touches no reporter input.
  - `review_packet.py` line 134 counts `cancelled` as red, while `policy_lint.mjs` `failingCheckNames` counts only `failure`. This is P405's class A. Its cause is R10-HOTFIX-SELFTEST-TIMEOUT's (PR 3275, in progress). Whether a cancelled run is a red is already the #3262 carry on R10-HOTFIX-GATE-BUSY-DEFER.
- **Cause C.**
  - #3252's two pr-contract failures (jobs 128446411039, 128449815767) both print `FAIL closed: no run at this head owns a finished codeql unit for base 'main' after 600 s` from `tools/ci/codescan_wait.py`. `gate` went red three times, at 15:56Z, 16:06Z and 17:15Z.
  - That is not a `## Red checks` text failure. It is the gate's deferral path, which R10-HOTFIX-GATE-BUSY-DEFER (PR 3287) and R10-RCA-GATE-BUSY-DEFER-2 (PR 3278) own.
- **#3245 is a real red, the null control.**
  - It touches `.github/workflows/tests.yml` and `.github/workflows/nightly.yml`, and it has a real `governance / instrument-self-tests` `failure` (18:18:10Z) and a `budget-raise-gate` failure.
  - It owes its answers under any rule.
- **Line 88's #3274 is not this class.** The orchestration log (`s10` chain notes, chain3274.sh) records its refusal as red-unanswered `tests / mutation` (49 unpinned sites), a real red of its own diff. #3274 touches no reporter input.
- **The rule on every instance.** Key the void set per reporter. For nightly-status it is `ci.yml`, `tests.yml` and `nightly.yml`. For delivery-status it is `ci.yml`, `governance.yml`, `tests/delivery_status.py`, the plan, the handover and the base's delivery rows, as today. The run is a membership test of each diff's paths:
  - **#3264, #3267, #3294 and #3275: void today on `governance.yml`; exempt under the rule.** No re-take is owed.
  - **#3245: void today and still void under the rule,** on `tests.yml` and `nightly.yml`. That is the null control, and it owes, as today.
  - **#3293, #3295 and #3252: no reporter input under either rule.** Their refusals are causes B and C, and this barrier leaves them unchanged.
- **Frequency.** 16 of 194 first-parent merges on main since 2026-10-31 touched `governance.yml` (`git log origin/main --since=2026-10-31 --first-parent --format=%h -- .github/workflows/governance.yml | wc -l` against the same without the path). Every new instrument self-test row lands there. So while main's nightly is red, each such pull request is refused once for a fact about main.

Cost:
- **The code:**
  - `REPORTER_INPUTS` becomes a map from reporter to path set. `reporterInputsTouched(paths, existing, reporter)` reads the reporter's own set.
  - The delivery-row clause stays on `delivery-status` alone. The `existing` and no-paths semantics are unchanged.
  - About 15 lines.
  - Acceptance arms in the existing table (line 4481): a diff touching only `governance.yml` owes delivery-status and not nightly-status; a diff touching `tests.yml` owes nightly-status; a mutant that merges the sets back fails the first arm.
  - The null controls: `tests/nightly_status.py` alone voids nothing, because it is base-pinned; the existing arms stay as they are.
- **Which copy is read.** The set is read from the base's copy of the file, so a pull request still cannot widen its own exemption. `review_packet.py` delegates to `policy_lint.mjs` (P282), so the packet follows without its own edit.
- **Size and ownership:**
  - `policy_lint.mjs` is 7771 lines with 12 commits since 2026-10-24.
  - It is code-owned and in the policy machinery, so it merges on tvofi's approving review or under a mandate in force.
  - No `--budgets` row reads it. An S carry, sonnet, one review.
- **Benefit:**
  - 4 refusals on 11-07 alone. At P405's measured cost, a 4 to 7 min body-only fixer plus 30 to 60 min of update, contract re-run and re-dispatch on the pull request's path, that is 2 to 4.5 h on one day.
  - Main's nightly has been red for most of 11-07. At 8 % of merges touching `governance.yml`, expect 5 to 15 more over the 6 days left while nightly stays red.
  - **3 to 15 h.**
- **The known-cause registry, the binding cost.**
  - It is a widenable allow-list of reds keyed to an owner, which a pull request would be judged against. An entry outlives its cause the moment the owner's PR merges and the red recurs for a new reason, and that converts a real red into an answered one.
  - That is the "check that passes while the bug is present" `defect-root-cause.md` forbids.
  - Cause A needs no registry, because the exemption is already a fact about which paths can redden a check.
  - Cause B's owner removes the red itself.
- **The relay re-take, the binding cost.** It automates the `## Red checks` answer, which `fix-review.md` step 11 makes the fixer's, and P405 already ruled that. It also spends a body push per new head on every pull request to save the few that have the red.

Binding:
- **Carry for R10-BODY-CONTRACT.** The carry text: `From triage batch 133 (triage: dev/programme/triage/s6-batch133.md#P406 at <roster sha>), audit-class barrier (red-checks retake class, 7 instances on 2026-11-07), savings estimate 3 to 15 h: policy_lint.mjs voids the main-graded exemption for both MAIN_STATE_REPORTERS when the diff touches any path in one shared REPORTER_INPUTS set, so a diff touching only .github/workflows/governance.yml owes tests / nightly-status, a tests.yml job that runs the base-pinned tests/nightly_status.py and that no governance.yml path can redden (PR 3264, PR 3267, PR 3294, PR 3275 refused on 11-07). Key REPORTER_INPUTS per reporter: nightly-status voided by ci.yml, tests.yml, nightly.yml; delivery-status by ci.yml, governance.yml, tests/delivery_status.py, the plan and handover files and the base delivery rows as today; keep the set read from the base copy. Acceptance arms in the existing table: a governance.yml-only diff owes delivery-status and not nightly-status; a tests.yml diff owes nightly-status; null control: tests/nightly_status.py alone and the existing arms unchanged; one mutant merging the sets back fails the first arm. review_packet.py delegates (P282), so it needs no edit; no known-cause registry, no relay re-take of Red checks.`
- **Cause C.** #3252's codescan_wait fail-closed goes to R10-HOTFIX-GATE-BUSY-DEFER as an instance, through the orchestrator. No carry is ruled here: whether a deferral or timeout should redden `gate` is that group's open question.
- **The audit class is answered by this barrier together with R10-HOTFIX-SELFTEST-TIMEOUT.** Once both have merged, a repeat of cause A or B is an instance of a barriered class.
