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

## P407: CLOSEOUT-CLEANUP carry 2 discharge (queue line s12-closeout-cleanup-carry2)

Verdict: ACCEPT. Carry 2 of R10-CLOSEOUT-CLEANUP is implemented: its code at `9f7487299` (2026-11-01), merged into main by PR 3085 at `6125b263d94e7ea8c43d31eb483869f8d8c83019`. What remains of it is the group's own `--apply` run, which is the brief's step 2 and carry 1's last act. That run is not this carry's code. The mark lands only by re-appending the carry with this citation, because the gate judges the whole marked text, and carry 2 names `Triage P-A` with no citation.

Source: the orchestrator's queue line of 2026-11-07T17:09:55Z (the mark `implemented 6125b263d` was refused as proposal-sourced and uncited), and the slip study's finding that the carry was built at `9f7487299`.

Instances:
- **The carry.** It is carry [2] (0-based) of R10-CLOSEOUT-CLEANUP at roster `3069eaa49`, `Folded from R10-FLY-PRUNE-REFS ...`. It holds R10-FLY-PRUNE-REFS's brief and its carries 0 to 4.
- **The two shas.**
  - `git merge-base --is-ancestor 9f7487299 6125b263d` succeeds, and both are on origin/main.
  - `9f7487299` (`prune_refs: batched git-push arm, keep guards, --topic`) touches only `tools/audit/seat/prune_refs.py`, with 443 insertions.
  - `6125b263d` is the merge of PR 3085, which the group's `resume.commit` names.
- **Each item, read in `git show 6125b263d:tools/audit/seat/prune_refs.py`:**
  - **Carry (i), the batched push arm:**
    - `apply_plan_push` pushes tags first as `<sha>:refs/tags/<tag>` in `PUSH_CHUNK` chunks, then reads them back, then deletes in the same chunks, and aborts on the first refusal. Each delete chunk is `--atomic`.
    - Self-test: `0 gh calls in the push arm (the gh stub fails on any call)`.
    - Null control: `the gh-api arm makes 2N writes (and N reads) for N unmoved refs`.
  - **Carry (ii), the keeps:**
    - `classify` returns `KEEP_SESSION` for `claude/*`, and `KEEP_DESIGN` for a `design/` or `design-verdict/` ref of a group that `--roster-file` records not done.
    - It returns `KEEP_YOUNG` for a tip younger than `YOUNG_TIP_S = 6 * 3600`, a `dispatch/*` tip younger than `YOUNG_DISPATCH_S = 24 * 3600`, or an unreadable age.
    - Self-test: `a claude/* ref with a main-reachable tip is kept`, `a design-verdict/ ref of a not-done group is kept`, and `null: a dispatch/* tip of 25 h is deleted`.
  - **P-A cleanup, the residue that nothing deleted.** `dispatch/*` and `brief/*` refs now fall to `DELETE_MERGED` or the residue rules, which delete by default (`--keep-residue` keeps), behind the 24 h guard that carry (ii) presumed.
  - **Carries 3 and 4, the audit-output refs.** These are operational: dispose or prune them. On origin there are still 1 `handoff/audit-r10-find-B*`, 910 `dispatch/*` and 1 `brief/*` refs (`git ls-remote origin 'refs/heads/<family>*' | wc -l`). They are exactly what the brief's step-2 `--apply` run archives and deletes with this instrument, so no further code is owed.
- **The self-test.** `python3 tools/audit/seat/prune_refs.py --self-test` over `git archive 6125b263d tools tests` prints `SELF-TEST PASS (74 checks)`.
- **Why the mark was refused.**
  - `roster_edit.py` `op_mark_carry` appends ` [implemented: <sha>]`, and `added_texts` then sees a carry entry the base did not hold.
  - `triage_refusal` finds `PROPOSAL_RE` (`\b(?:triage|proposal)\s+P(?:\d+|-[A-Q])\b`, any case) in the carry's own words `Triage P-A cleanup`, and no `triage:` citation.
  - The mark's value cannot carry a citation, because `SHA_RE` is `\A[0-9a-f]{7,40}\Z`. No op edits a carry in place.
- **The rule on the instance.** Drop the carry by `--match`, re-append the same text with this ruling's citation, and mark the re-appended entry `implemented` by `--match`. This was simulated through `added_texts` and `triage_refusal` against this file:
  - the bare mark is refused;
  - the re-append is accepted;
  - the mark of the cited entry is accepted;
  - the null control, the same citation with the verdict flipped to REJECT, is refused.

Cost: three roster ops and no code. The drop moves carries [3] to [8] down by one, so any pending index-addressed op on the group must use `--match`. No capped file is touched.

Binding:
- Roster ops for R10-CLOSEOUT-CLEANUP, in order. Every op addresses the carry by `--match`, never by index:
  1. `drop-carry --match 'Folded from R10-FLY-PRUNE-REFS'`.
  2. `append-carry` with the dropped text verbatim, followed by `triage: dev/programme/triage/s6-batch133.md#P407 at <roster sha>`.
  3. `mark-carry --match 'triage: dev/programme/triage/s6-batch133.md#P407' implemented 6125b263d94e7ea8c43d31eb483869f8d8c83019`.
- The orchestrator's refused mark is replaced by these three ops.

## P408: author-email guard (queue line s12-author-email-guard)

Verdict: ACCEPT changed, as an owner-tier hotfix. The owner set the tier and ruled that history is not rewritten. This seat rules on the form.
- **The push guard: ACCEPT, with a changed allowlist.** It is a grammar, not a list of names:
  - the seat identity `70032254+tvofi@users.noreply.github.com`;
  - any `<digits>+<login>@users.noreply.github.com`, because the number pins the account;
  - any `<name>[bot]@users.noreply.github.com` or `<digits>+<name>[bot]@users.noreply.github.com`, the Apps and github-actions;
  - `noreply@github.com` as a committer only, the web-merge committer;
  - an adopted outside contributor's own email, named per adoption.
- **The adoption step that preserves the contributor's author: ACCEPT, narrowed.** The adopted commits keep their original author email, which the allowlist admits by name. A contributor whose commits reached main under a placeholder is credited by a `Co-authored-by:` trailer, as the owner ruled for #3226 on R10-COMBI-TANK carry 6.

The destination is a new hotfix group, R10-HOTFIX-AUTHOR-EMAIL. Its owner, R10-SEAT-IDENTITY-GUARDS, is done (PR 3222, merged 2026-11-05T17:45:59Z), and it refused only Claude-authored commits.

Source: the orchestrator's queue line of 2026-11-07, with the owner's tier and no-rewrite rulings it records.

Instances:
- **Placeholder and unnumbered addresses on main.** By `git log origin/main --format='%ae' | sort | uniq -c | sort -rn` (author emails, whole history):
  - `t@t` 386, `fixer@invalid` 25, `noreply@anthropic.com` 1007;
  - `seat@users.noreply.github.com` 522, `hpo-fixer@users.noreply.github.com` 194, `hpo-author@users.noreply.github.com` 25.
  - The queue line's figures are a narrower window. These are cited from the command, not carried.
- **Still arriving after PR 3222 merged.** By `git log origin/main --since=2026-11-05T12:00 --format='%ae%n%ce' | sort | uniq -c`:
  - `seat@users.noreply.github.com` 378, `hpo-fixer@users.noreply.github.com` 144 and `noreply@users.noreply.github.com` 7.
  - An unnumbered `<login>@users.noreply.github.com` is credited by GitHub to whichever account holds that login, so 529 commits in two days credit accounts that are not this project's.
- **What ref_privacy refuses today.** `tools/audit/seat/ref_privacy.py` refuses private-use domains (`host-email`, `PRIVATE_EMAIL_SUFFIXES`, line 158) and Claude attribution (lines 243 to 258), but no placeholder or unnumbered address.
- **The rule on the instances:**
  - `seat@`, `hpo-fixer@`, `noreply@users.noreply.github.com`, `t@t`, `x@x`, `fixer@invalid` and `noreply@anthropic.com` are refused. None matches the grammar.
  - `70032254+tvofi@`, `331381602+hpo-author[bot]@`, `hpo-author[bot]@`, `41898282+github-actions[bot]@` and `noreply@github.com` as committer pass.
  - The null control: `476059+Bankaifan@users.noreply.github.com` in a trailer is not an author or committer, and passes untouched.

Cost:
- **The code:**
  - One `email_identity` check in `ref_privacy.py` over the author and committer of each commit the push adds, which the file already reads for `host-email`. About 30 lines.
  - Self-test arms for each refused and each passing form above, plus a mutant that drops the digits requirement and must pass `seat@users.noreply.github.com`.
- **The writers.** The fixer finds which writers set `seat@` and `hpo-fixer@users.noreply.github.com`, and makes each set the seat identity. The candidates are the cloud environment's git config (`cloud-setup.sh`) and any `git -c user.email` in `tools/`. Otherwise the guard refuses live seats' pushes.
- **Ownership and tier.** `ref_privacy.py` and `cloud-setup.sh` are seat instruments, and neither is a `--budgets` row. The tier is the owner's, hotfix: it misattributes contributors. It is not a wall-clock trade and needs no >10 % exemption.

Binding:
- **New group R10-HOTFIX-AUTHOR-EMAIL:** lane HOTFIX, kind instrument, class instrument, size S.
  - Files: `tools/audit/seat/ref_privacy.py` and `tools/audit/seat/cloud-setup.sh`.
  - Fixer sonnet, reviewer opus, effort medium, no `after`.
- **The brief text:** `From triage batch 133 (triage: dev/programme/triage/s6-batch133.md#P408 at <roster sha>), hotfix tier (owner, 2026-11-07: it misattributes contributors; history is not rewritten). Commits reach main under placeholder or unnumbered author and committer emails that GitHub credits to unrelated accounts: since 2026-11-05T12:00 seat@users.noreply.github.com 378, hpo-fixer@users.noreply.github.com 144, noreply@users.noreply.github.com 7 (git log origin/main --since=2026-11-05T12:00 --format=%ae%n%ce); historically t@t, x@x, fixer@invalid, noreply@anthropic.com. Add to tools/audit/seat/ref_privacy.py's push guard a refusal of any added commit whose author or committer email is outside this grammar: the seat identity 70032254+tvofi@users.noreply.github.com; <digits>+<login>@users.noreply.github.com; <name>[bot]@users.noreply.github.com with or without a <digits>+ prefix; noreply@github.com as committer only; and an adopted outside contributor own email passed explicitly per adoption. Find and fix the writers of seat@ and hpo-fixer@users.noreply.github.com (cloud-setup.sh git identity, any git -c user.email under tools/) so live seats pass. Self-test arms: each refused form above refuses; each allowed form passes; a mutant dropping the digits requirement fails the seat@ arm; null control: a Co-authored-by trailer naming 476059+Bankaifan@users.noreply.github.com is not judged. No history rewrite; credit for past placeholder commits stays the owner Co-authored-by route (R10-COMBI-TANK carry 6).`

## P409: roster drain stale tracking ref, with the push addendum (queue lines s12-roster-drain-stale-tracking-ref and its measured addendum)

Verdict: ACCEPT. Both arms are one defect: `roster_edit.py`'s on-origin guard trusts a remote-tracking ref that nothing keeps current. It goes to R10-ROSTER-WRITE-SWEEP (carries-open, PR 3253), which owns `roster_edit.py` and `roster_queue.py`. It is not taken on the >10 % exemption. The tier is hotfix as the queue line asks, because it stalls every roster-dependent dispatch.

Source: the orchestrator's queue lines of 2026-11-07, measured at about 13:40Z and 13:46Z.

Instances:
- **The guard.** At origin/main, `tools/audit/seat/roster_edit.py` line 911 refuses `HEAD <sha> is on no origin ref` when `git for-each-ref --contains <old> refs/remotes/origin/` is empty. That reads the LOCAL tracking refs.
- **The push.** The push at line 1100 sends `<head>:refs/heads/<branch>` from the worktree. The queue addendum measured that the next op's guard did not see it: it pushed c96a6f2d, then refused the next two ops at c96a6f2d.
- **A rival writer.** When carry_fold or a second drain pushes the roster branch, the same guard refuses until a `git fetch`. At about 13:40Z 48 queued ops stalled this way, the COP hotfix group append among them, while HEAD 575dbfc9 was on origin all along (queue line).
- **The rule on the instances.** Before refusing, the guard runs one `git fetch origin <branch>` and re-reads `--contains`. After its own successful push it runs `update-ref refs/remotes/origin/<branch> <head>`.
  - Both measured cases then pass: 575dbfc9 is on the fresh tip, and c96a6f2d is the tracking ref after the update.
  - The null control: a HEAD on no fetched ref, a real unpushed edit, is still refused.

Cost:
- About 10 lines in `roster_edit.py`, at the guard and after the push.
- Self-test arms in its throwaway-git block: a rival push leaves the local tracking ref stale, and the guard passes after its own fetch; two ops in one run both land; the null control, an unpushed commit, still refuses; a mutant dropping the fetch refuses the rival case.
- One fetch per refusal path, and none on the common path.
- `roster_edit.py` is not a `--budgets` row.
- **Benefit.** 48 ops held until a hand fetch, twice on 11-07, and every two-op run at half throughput. Every roster-dependent dispatch waits on that queue.

Binding:
- **Carry for R10-ROSTER-WRITE-SWEEP.** The carry text: `From triage batch 133 (triage: dev/programme/triage/s6-batch133.md#P409 at <roster sha>), hotfix tier (it stalls every roster-dependent dispatch): roster_edit.py refuses HEAD <sha> is on no origin ref from git for-each-ref --contains over the LOCAL refs/remotes/origin/ refs, which go stale (a) when a rival writer (carry_fold, a second drain) pushes the roster branch (2026-11-07 about 13:40Z: 48 queued ops stalled until a hand git fetch while HEAD 575dbfc9 was on origin) and (b) after its own <sha>:refs/heads/<branch> push (13:46Z: pushed c96a6f2d, then refused the next two ops at c96a6f2d). Before refusing, fetch the branch once and re-check; after a successful push, update-ref refs/remotes/origin/<branch> to the pushed head. Self-test arms (throwaway git): a rival push with a stale local tracking ref passes after the fetch; two ops in one run both land; null control: a real unpushed commit still refuses; a mutant dropping the fetch refuses the rival case.`

## P410: roster drain mispair (queue line s12-roster-drain-mispair)

Verdict: REJECT, as a roster change. The tracked beat row the line names as its fix already marks each op from its own report. The mispair is in the session-local `s9/sweep-runner/roster_drain.py`, which is outside the tree, so a roster carry cannot fix it. The countermeasure is operational: the session drains through the tracked `roster-drain` beat row (decision 0013: never a session-local loop) and retires the local script. That is the orchestrator's step, and this ruling sends it there.

Source: the orchestrator's queue line of 2026-11-07, which extends s12-roster-drain-stale-tracking-ref.

Instances:
- **The session-local script.** `s9/sweep-runner/roster_drain.py` line 41 reads `for op, res in zip(pend, new):` (host-local). When an op writes no report line, or another writer's line lands, every later op takes the wrong result. That is the queue line's `append-group R10-GENERIC-HEAT-CURVE` marked done with `unwire-issue R10-FRICTION-RECORDS`'s note.
- **The tracked beat row.** `tools/audit/seat/beat_jobs.py` `roster_drain` (line 301) writes one op to `roster-one.queue` and unlinks `roster-report.txt` before each call. It runs `roster_queue.py run 1 1` on that single op and reads the report it just wrote. One op per report cannot mispair.
- **The rule on the instance.** Run through the beat row, the GENERIC-HEAT-CURVE op is marked from its own report, and the FRICTION-RECORDS note cannot reach it.

Cost:
- **The binding cost.** A carry to edit `beat_jobs.py` would re-implement what it already does. A carry to fix a host-local script lands nothing in the tree, and leaves the second drain loop that P409's rival-writer instance also came from.
- **What would change this ruling:** a mispair measured from the beat row itself.

Binding: no roster op. The orchestrator moves its drain onto the `roster-drain` beat row and retires `s9/sweep-runner/roster_drain.py`. Then it re-queues `append-group R10-GENERIC-HEAT-CURVE`, and every other op the local script marked done from another op's line: read back the roster for each.

## P411: relay auto carry-fold (queue line s12-relay-auto-carry-fold)

Verdict: ACCEPT changed. The line is the third instance set of a class that R10-CARRY-RESIDUE-2 carry 3 already owns: "body_push refuses CARRY-LANDED missing for forward carries a fixer cannot land", 4 instances on 11-06. It is not a new group. It goes to R10-CARRY-RESIDUE-2 (not-started) as a carry that fixes the barrier's form to the queue line's relay arm:
- `cloud_relay.sh`'s handoff arm folds the carries through `carry_fold.py`, the designated writer, and re-runs `body_push.sh` on the kept body. This applies only when the fixer's `BLOCKED.md` refusal is CARRY-LANDED alone.
- Any other refusal owes a line on the tick board.
- The carry-3 alternative, "body_push emits land-ops and exits with a distinct code", is kept as the signal that the relay keys on, not as a second writer.

It is not taken on the >10 % exemption.

Source: the orchestrator's queue line of 2026-11-07.

Instances:
- **11-07, two hotfix-tier groups:**
  - R10-HOTFIX-SELFTEST-TIMEOUT (PR 3275; 1 carry) was blocked at 13:23Z and folded at 13:45Z.
  - R10-HOTFIX-GATE-BUSY-DEFER (3 carries) was blocked at 13:36Z and found at 14:10Z.
  - Each waited 20 to 35 min until the orchestrator looked (queue line).
- **11-06, the class's own four instances:** #3241 r3, the #3234 recut, #3242 tml-body and the #3241 body (R10-CARRY-RESIDUE-2 carry 3, roster `3069eaa49`).
- **The relay today.** At origin/main `git grep -n BLOCKED.md tools/audit/seat/cloud_relay.sh` prints nothing, so no arm reads a fixer's BLOCKED.md.
- **The fold tool.** `tools/audit/seat/carry_fold.py` already appends each missing `Carry: <GROUP>` item with `roster_edit.py append-carry --push`, and asserts after the fold that every item is present (its docstring). It is the orchestrator's tool today, and nothing calls it on a block.
- **The rule on the instances.** With the arm, each of the six is folded on the relay's next pass and its body re-pushed. That removes the 20 to 35 min wait, and the null control holds: a BLOCKED.md that also names any other refusal is not auto-folded, and prints its line.

Cost:
- **The code:**
  - About 30 lines in `cloud_relay.sh`'s handoff arm. It reads `handoff-wip/<topic>-body` and BLOCKED.md, checks that the only refusal is CARRY-LANDED, runs `carry_fold.py --body ... --topic ...` and then `body_push.sh` from the relay's checkout.
  - A self-test fixture for each arm, and a mutant that drops the CARRY-LANDED-only test, which must auto-fold a mixed refusal.
- **Ownership.** `cloud_relay.sh` is in `review_packet.py`'s HOT_FILES, so the fixer overlaps by seam with any open relay PR (R10-HANDOFF-PATH, R10-TICK-LEVELS). It is not a `--budgets` row.
- **Benefit and tier.**
  - 6 instances in 2 days at 20 to 35 min each, which is 2 to 3.5 h.
  - Most repair rounds carry, so expect 10 to 20 more in the 6 days left: **3.5 to 11 h, central 6 h. Tier: instrument.**
  - On hotfix groups each hold is on the merge path.

Binding:
- **Carry for R10-CARRY-RESIDUE-2.** The carry text: `From triage batch 133 (triage: dev/programme/triage/s6-batch133.md#P411 at <roster sha>), savings estimate 3.5 to 11 h (central 6 h; instrument tier), the barrier form for this group carry 3 (CARRY-LANDED strands a cloud fixer): two more instances on 2026-11-07, R10-HOTFIX-SELFTEST-TIMEOUT (PR 3275, blocked 13:23Z, folded 13:45Z) and R10-HOTFIX-GATE-BUSY-DEFER (3 carries, blocked 13:36Z, found 14:10Z). Build it in tools/audit/seat/cloud_relay.sh handoff arm: when a fixer BLOCKED.md refusal is CARRY-LANDED alone and its body is kept on handoff-wip/<topic>-body, run tools/audit/seat/carry_fold.py (the designated writer) on that body and then body_push.sh; any other refusal prints a tick line and folds nothing. body_push.sh may exit with a distinct code for CARRY-LANDED-only so the relay keys on it. Fixtures: a CARRY-LANDED-only block is folded and re-pushed; null control: a block naming CARRY-LANDED plus any other refusal is not folded and prints its line; a mutant dropping the CARRY-LANDED-only test folds the mixed block and fails.`

## P412: file-overlap cap (queue line s12-file-overlap-cap)

Verdict: ACCEPT narrowed. The owner asked for the measurement first, and this ruling is on that measurement.
- **The per-file open-PR cap: REJECT.**
- **(1) Keyed merge drivers: ACCEPT narrowed** to the two files whose shape keys every entry:
  - `dev/programme/rosters/wave-r10-groups.json`, keyed by `group`;
  - `tools/audit/seat/INSTRUMENTS.md`, one bullet per instrument, keyed by its link target.
- **The Python files: DEFER.** These are `dev/audit/harnesses/r10_seat_selftests_mutants.py` and `dev/audit/rounds/round4/D6/claims.py`. A union driver on code can merge two valid files into an invalid one. They need either a data-file split or a measured lag share per file.
- **(2) The warn-only handoff-time overlap check: DEFER.**

The destination for (1) is a new fly-in group, R10-FLY-KEYED-MERGE-DRIVERS, because no open group owns `tools/merge/` or `.gitattributes`. It is not taken on the >10 % exemption.

Source: the orchestrator's queue line of 2026-11-07 and seat a50195df's evidence file (orchestration log `s12/filecap/evidence.txt`, host-local).

Instances (all from that evidence file):
- **Step 1.** 147 merge-forward conflict rounds in 94 PRs under the repo's merge drivers. Lag: median 1.4 h, sum 919 h, p90 14.1 h.
- **Conflicted files, by rounds:** `r10_seat_selftests_mutants.py` 16, `wave-r10-groups.json` 15, `coordinator.py` 8, `INSTRUMENTS.md` 8, `bugclasses.json` 8, `D6/claims.py` 6.
- **Step 3, the replay of 428 merged work PRs:**
  - a cap of 1 per file shifts the last merge by +1124 h (row b');
  - 1 per roster-hot file, also +1124 h (row c-);
  - a global cap of 16 shifts it +3 h (row a16).
- **Step 4.** The roster forecast names a median 0.26 of a PR's actual files, and 276 of 320 PRs touch a file outside it. A cap enforced from the forecast holds 155 PRs for 22575 h and prevents 76 of 121 conflicts (row (c) from forecast).
- **The rule on the instances:**
  - The two keyed files account for 23 of the 147 rounds (15 + 8).
  - Under a keyed driver, a round in which the two sides added or edited different keys resolves clean. A round in which both edited the same key still conflicts, and that same-key conflict is the null control.
  - `bugclasses.json` already has `merge=ledgermerge` (`.gitattributes`) and still conflicted 8 times. So the fixer measures the same-key share on the 23 rounds by replaying them against the driver. It does not assume all 23 resolve.

Cost:
- **(1) The code:**
  - A driver under `tools/merge/` modelled on `tools/merge/ledger_merge.py`, a three-way merge per key that refuses a same-key conflict, plus two `.gitattributes` lines and the install step that `ledger_merge.py --install` already provides.
  - About 120 lines with self-tests: disjoint additions merge; a same-key edit conflicts; a reorder-only change is a no-op; the null control, a malformed side, refuses and leaves the conflict to git.
- **(1) Benefit:**
  - 23 rounds in about 23 days, at a median lag of 1.4 h and p90 14.1 h. For the 6 days left, about 6 rounds: **8 to 20 h of pull-request lag, central 10 h. Tier: instrument.**
  - It also removes the hand resolutions: 75 of the 147 rounds were resolved by tvofi.
- **The per-file cap, the binding cost:** +1124 h of last-merge shift for at most 104 of 121 conflicts prevented, against +3 h at the global cap.
- **(2), what would change it:**
  - A warning prevents no conflict. Its benefit is a seat's choice to wait or re-cut, and that has not been measured.
  - Re-file it with a count of the PRs whose fixer, warned, would have avoided a measured conflict. The 38 of 320 PRs that left the forecast on a file that later conflicted are the population.
- **The Python files, what would change it:** a per-file lag share from the evidence script, or a split of the mutant table into a keyed data file, which is the owning group's architecture call, R10-SEAT-SELFTESTS-CI's successor.

Binding:
- **New group R10-FLY-KEYED-MERGE-DRIVERS:** lane F, kind instrument, class instrument, size S.
  - Files: `tools/merge/keyed_merge.py`, `.gitattributes` and `tools/merge/ledger_merge.py` (install step only).
  - Fixer sonnet, reviewer opus, effort medium, no `after`.
- **The brief text:** `From triage batch 133 (triage: dev/programme/triage/s6-batch133.md#P412 at <roster sha>), savings estimate 8 to 20 h (central 10 h; instrument tier). The file-overlap measurement (seat a50195df, 2026-11-07): 147 merge-forward conflict rounds in 94 PRs, lag median 1.4 h, sum 919 h; dev/programme/rosters/wave-r10-groups.json 15 rounds and tools/audit/seat/INSTRUMENTS.md 8. Add a keyed three-way merge driver under tools/merge/ modelled on ledger_merge.py: wave-r10-groups.json merged per group object (keyed by group), INSTRUMENTS.md per bullet (keyed by its link target), refusing a same-key edit on both sides so git keeps the conflict; wire both in .gitattributes and in the existing --install step. Self-tests: disjoint additions merge; a same-key edit conflicts; a reorder-only side is a no-op; null control: a malformed side refuses. Measure before and after by replaying the evidence 23 rounds on these two files against the driver and report how many resolve. No per-file open-PR cap; no driver for Python files (r10_seat_selftests_mutants.py, D6/claims.py).`

## P413: the fixer.md spelling-corpus sentence (queue line, orchestrator RULING under mandate 6624093439)

Verdict: ACCEPT. This is an owner-mandate directive, so it keeps its route and this seat rules only on the form. The destination the line asks for already exists: R10-FIXER-MD-SPELLING-CORPUS (not-started, lane IN, size S, files `dev/governance/roles/fixer.md`). Its brief quotes the approved sentence verbatim and names the placement, budget and control rules. No other open group lists `dev/governance/roles/fixer.md`, so no existing policy group precedes it. No append-carry is owed: the brief already carries the whole directive.

Source: the orchestrator's ruling line, mandate comment 6624093439 (scope all), 2026-11-07, and the roster-audit4 note in that group's `resume.note`.

Instances:
- **The group.** At roster `3069eaa49`, R10-FIXER-MD-SPELLING-CORPUS has `owner_gate` `policy: merges under mandate 6624093439`, `carry` `[]`, and a brief that holds the sentence `A guard that classifies text by shape is driven over a generated spelling corpus (case, quoting, glued options, delimiters, wrapping) with the corpus size named in the body; a spelling the reviewer finds is added to it.` exactly once.
- **The search.** It is the only group not done, absorbed or struck whose `files` include `dev/governance/roles/fixer.md`, by a scan of `groups[].files` in `wave-r10-groups.json`.
- **The source text.** The drafted sentence is in `dev/audit/rca/R10-RCA-CLASS-OPEN.md` at origin/main, lines 99 to 101.

Cost: no op. The policy cost is the group's: `fixer.md`'s `--budgets` cap, paid by tightening first, as its brief binds.

Binding: none beyond the group as it stands. The orchestrator dispatches it.

## P414: relay body-only alarm (queue line s12-relay-body-only-alarm)

Verdict: REJECT. The alarm it asks for already exists. `orchestrator_tick.py` prints `OWED body-ahead #<pr> <sha> handoff-body/<topic> is newer than the head, repair done and unapplied` (line 927 at origin/main), which is the R10-TICK-LEVELS BODY-AHEAD level. The 50 minutes were lost downstream: `owed_unactioned.py` cannot key that line and goes UNREADABLE, so the sweep's owed check reported nothing. That defect is P416's, and P416 fixes it.

Source: the orchestrator's queue line of 2026-11-07 (f-3265-body).

Instances:
- **The one instance.** f-3265-body's body sat unapplied for 50 min (queue line).
- **The tick line was printed.** The orchestration logs hold `UNACTIONED-UNREADABLE: UNREADABLE: an owed line names no topic or pull request: -> OWED body-ahead #3265 c7c5cef52a49 handoff-body/r10-hotfix-plan-lanes is newer than the head, repair done and unapplied` (`grep -rh UNACTIONED-UNREADABLE` under the session directory). So the tick saw #3265's body-ahead, and the owed check failed to read it.
- **The rule on the instance.** With P416's keying, that line is keyed `#3265` on `c7c5cef52a49`, and is reported unactioned on the next sweep: within one sweep, not 50 min.

Cost:
- **The binding cost.** A second beat row with a 30-min threshold duplicates a level that already fires at once, adds a row to the beat file and a second reader of the same fact, and adds a hot-file edit to `cloud_relay.sh`.
- **What would change it:** a body-ahead held past one sweep after P416 lands.

Binding: none. See P416.

## P415: bottleneck mutation-vacuous (queue line s12-bottleneck-mutation-vacuous)

Verdict: DEFER. The class already has its RCA document and its landed countermeasures, so `defect-root-cause.md`'s audit-class clause is answered, not open.
- **The barrier the line names already exists, in report-only form.** `prepr.sh` step 6d' runs `mutant_run.py --diff` on the diff's added lines (line 4448), but only when `MUTANT_CMD` is set (line 4460), and it refuses nothing.
- **What would change the verdict.** Whether to make 6d' refuse, or to make `MUTANT_CMD` default from the group's self-test, turns on one unmeasured fact: did 6d' run on the 11 blocked heads, and would it have reported the hand mutant that survived? Measure that and re-file.
- **The owner.** This is an RCA re-take of `dev/audit/rca/R10-RCA-MUTATION-VACUOUS.md` section 6, the T population, which already names this class's new cause.

Source: the orchestrator's queue line of 2026-11-07T16:13:23Z and the prototype bottleneck checker's output.

Instances:
- **The checker.** Orchestration log `s12/proto-plan/live-check.txt`, host-local: `BOTTLENECK: block-class mutation-vacuous 39% (11/28 blocks, 24 h) vs 30%` and `BOTTLENECK: yield 0.46 (11/24 first passes, 24 h) vs 0.6`.
- **The record.** `dev/audit/rca/R10-RCA-MUTATION-VACUOUS.md` counts `mutation-vacuous` at 31 PRs and 38 entries since v7.0.4 (`node tools/policy/policy_lint.mjs --stats --since v7.0.4`, measured at `7e8939d38`). It records countermeasure C (`mutation-autofix` reddens on a site left alive, #3059) and the family-map change, and it names population T as a new cause with its countermeasure landed (section 6).
- **The overlap check the line asked for.** `dev/audit/rca/R10-RCA-MUTATION-SURVIVOR.md` section 7 places its own countermeasure in `prepr.sh` step 7d (`unpinned_line`), the survivor half. Neither record promotes 6d' to a refusal.
- **The arm in the tree.** `tools/pr/prepr.sh` 6d' reads `say skip "diff mutants" "MUTANT_CMD unset ..."` when unset. So a fixer who sets nothing gets no diff mutants at handoff.

Cost:
- **What a refusal arm would cost:** a mutant run per handoff, minutes per group self-test, on every PR, against 11 blocks in 24 h.
- **The fact that sets the benefit, still unmeasured:** whether 6d' would have caught those hand mutants. The reviewer's mutant is chosen by hand, and `mutant_run.py`'s operators (GUARD_OFF, RETURN_DEL, CMP_BOUND, CALL_DEL) may not include it.
- An unmeasured benefit is DEFER.

Binding: the measurement goes to the R10-RCA-MUTATION-VACUOUS owner as a re-take of section 6. The 11 blocks of the 24 h window are read from the checker's own source. For each one, record whether `MUTANT_CMD` was set at the handoff, and whether `mutant_run.py --diff` with the group's self-test, run at that head, reports the reviewer's surviving mutant. If it would have caught 6 or more of the 11, re-file with a refusal arm and its standing cost.

## P416: owed_unactioned body-ahead key (queue line s12-owed-unactioned-body-ahead)

Verdict: ACCEPT. This is an instrument defect, not a trade. `owed_unactioned.py`'s `key_of` has no arm for the tick's own `OWED body-ahead` line, and `board()` raises `Unreadable` on any unkeyed line. So the whole run prints `UNREADABLE` and exits 2, and every owed line on that board goes unchecked, not only the body-ahead one. The destination is a carry on R10-TICK-LEVELS (carries-open, PR 3200), which owns `owed_unactioned.py` and `orchestrator_tick.py`. It is not taken on the >10 % exemption.

Source: the orchestrator's queue line of 2026-11-07T16:57:07Z.

Instances:
- **The tick writes the line.** `tools/audit/seat/orchestrator_tick.py` line 927 returns `"owed", f"handoff-body/{body} is newer than the head, repair done and unapplied", "body-ahead"`, which renders as `-> OWED body-ahead #<pr> <sha12> handoff-body/<topic> ...`.
- **The reader cannot key it.** `owed_unactioned.py` `key_of` (line 79) keys `OWED handoff:` and `OWED: OWED ...`, but no `OWED body-ahead`. It falls through to `raise Unreadable(...)` (line 111).
- **One line blinds the run.** `run()` returns 2 after one `UNREADABLE` from `board()` (lines 164 to 168).
- **The logged instance.** The orchestration logs hold `UNACTIONED-UNREADABLE: UNREADABLE: an owed line names no topic or pull request: -> OWED body-ahead #3265 c7c5cef52a49 handoff-body/r10-hotfix-plan-lanes ...`. This is P414's 50-minute instance.
- **The rule on the instance.** With a `OWED body-ahead (#\d+) ([0-9a-f]{12})` arm, the #3265 line keys `#3265` on `c7c5cef52a49`, and the run reads the rest of the board.

Cost:
- About 4 lines, and a self-test arm in the existing block beside the RECORD-OWED arm (line 390): a body-ahead line is keyed and is reported unactioned on the second sweep.
- The null control: a line that names no PR is still UNREADABLE.
- Also one cross-check that every owed kind `orchestrator_tick.py` can emit has a key arm, so the next new kind fails a self-test instead of blinding the run. The kinds are read from the tick's own self-test fixtures.
- `owed_unactioned.py` is not a `--budgets` row. An S carry, sonnet.
- **Benefit.** Every sweep while any body-ahead is on the board, which recurred all day on 11-07, the owed check reports nothing. It cost P414's 50 min once, and a stale owed line of any kind can hide behind it.

Binding:
- **Carry for R10-TICK-LEVELS.** The carry text: `From triage batch 133 (triage: dev/programme/triage/s6-batch133.md#P416 at <roster sha>), instrument defect: owed_unactioned.py key_of has no arm for orchestrator_tick.py own owed line (OWED body-ahead, then the hash-prefixed PR number, the head sha12 and handoff-body/<topic>; tick line 927), so board() raises Unreadable and run() exits 2 on the whole board; logged 2026-11-07 as UNACTIONED-UNREADABLE on PR 3265 at c7c5cef52a49 while that body sat 50 min unapplied. Add the arm (key the hash-prefixed PR number, id the sha12) and a self-test that every owed kind the tick emits in its own fixtures has a key arm. Self-test arms: a body-ahead line keys and is reported unactioned on the second sweep; null control: a line naming no PR stays UNREADABLE; a mutant dropping the arm fails the first.`

## P417: roster batch swallows the refusal (queue line s12-roster-batch-swallows-reason)

Verdict: ACCEPT. This is a silent-swallow defect. `roster_queue.py` `_run_batch` catches `SystemExit` and `Exception` as `e`, discards `e`, and prints only `roster: batch fell back to the single-op path`. Accepted:
- print the exception and the line it names;
- when the failure is attributable to one line (argparse refused that line's parse, or `roster_edit` raised `Refuse` naming it), re-batch once without that line and report it refused.

Any other batch-level failure still falls back as today. The destination is a carry on R10-ROSTER-WRITE-SWEEP (PR 3253), which owns `roster_queue.py`. It is not taken on the >10 % exemption.

Source: the orchestrator's queue line of 2026-11-07T17:16:12Z.

Instances:
- **The swallow.** In `tools/audit/seat/roster_queue.py` `_run_batch` (line 264), both `except SystemExit as e` and `except Exception as e` set `rc, m, results = 1, None, None` and never read `e`. Line 307 is the only output.
- **The instance.** A 116-line hold drain fell to the single-op path, about 2 h, with no way to see or drop the one bad line (queue line).
- **The rule on the instance.** The failing line is printed, with roster_edit's message. If that line's parse or `Refuse` caused the failure, the other 115 lines land in one batch in seconds: `_run_batch`'s docstring gives 0.36 s a line against 1 to 3 min a line single-op. The bad line is reported refused.

Cost:
- About 20 lines, with self-test arms:
  - a batch with one malformed line lands the rest and names the bad line;
  - a batch-level failure not tied to a line (a lost race) still falls back;
  - a mutant that drops the re-batch falls back on the first arm.
- The null control: a clean batch is unchanged.
- **Benefit.** About 2 h on the measured instance. Long hold drains recur at each freeze release, so expect 2 to 4 more this round: **4 to 8 h. Tier: instrument.**

Binding:
- **Carry for R10-ROSTER-WRITE-SWEEP.** The carry text: `From triage batch 133 (triage: dev/programme/triage/s6-batch133.md#P417 at <roster sha>), savings estimate 4 to 8 h (instrument tier): roster_queue.py _run_batch catches SystemExit and Exception as e, discards e and prints only roster: batch fell back to the single-op path, so a 116-line hold drain on 2026-11-07 fell to about 2 h single-op with the refusing line unknown. Print the exception and the line it names; when the failure is one line (its parse_op SystemExit or a roster_edit Refuse naming it), re-batch once without that line and report it refused; any other batch-level failure falls back as today. Self-test arms: one malformed line in a batch lands the rest and names it; a lost race still falls back; null control: a clean batch is unchanged; a mutant dropping the re-batch fails the first.`

## P418: set-files keeps only the last --add (queue line s12-set-files-repeat-add)

Verdict: ACCEPT. This is an instrument defect: a silent partial write, and a guard narrower than its own grammar. The destination is a carry on R10-ROSTER-WRITE-SWEEP (PR 3253), as the line asks, plus an operational re-apply of the lost path.

Source: the orchestrator's queue line of 2026-11-07T18:14:32Z.

Instances:
- **The parser.** `tools/audit/seat/roster_edit.py` line 1151 reads `p.add_argument("--add", nargs="+", help="set-files: paths appended to files")`. With `nargs="+"` and the default `store` action, a repeated flag replaces the earlier list.
- **The repro.** `python3 -c "import argparse; p=argparse.ArgumentParser(); p.add_argument('--add', nargs='+'); print(p.parse_args(['--add','a','--add','b']).add)"` prints `['b']`.
- **The instance.** In the slip batch at roster `c2e398675`, `set-files R10-USER-DOCS-VERIFY --add docs/img/brand/coffee.svg --add docs/img/readme/mermaid_figures.json` landed only `mermaid_figures.json`, and the tool reported pushed.
- **The rule on the instance.** With `action="extend"`, the same line lands both paths. The null control: one `--add a b` lands both, and one `--add a` lands one.

Cost:
- One line, plus self-test arms in the existing set-files block (line 1926 onward):
  - two `--add` flags land both paths;
  - the null control, one `--add` with one path, lands one;
  - a mutant restoring the default action fails the first.
- The same check applies to every other repeatable flag that roster_edit's grammar documents as `...`.

Binding:
- **Carry for R10-ROSTER-WRITE-SWEEP.** The carry text: `From triage batch 133 (triage: dev/programme/triage/s6-batch133.md#P418 at <roster sha>), instrument defect (silent partial write): roster_edit.py --add is nargs=+ with the default store action, so repeated --add flags keep only the last list (argparse repro prints [b] for --add a --add b); at roster c2e398675 set-files R10-USER-DOCS-VERIFY --add docs/img/brand/coffee.svg --add docs/img/readme/mermaid_figures.json landed only mermaid_figures.json and reported pushed. Use action=extend; check every other flag the grammar documents as repeatable. Self-test arms: two --add flags land both paths; null control: one --add with one path lands one; a mutant restoring the default action fails the first.`
- **The operational step is already done.** At roster `3069eaa49`, R10-USER-DOCS-VERIFY's `files` list both `docs/img/readme/mermaid_figures.json` and `docs/img/brand/coffee.svg`. No re-apply is owed.
