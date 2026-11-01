# Review packet #3074
head: dafcc5759950c7ec3faab4bf993723a758a94710
base: 92588d581fde4ce287af3db5e8bb61461dc28015

Start here (fix-review.md). Re-read the live check state before a verdict: the digest is as read at render.

## Gate digest: pending
CodeQL id=124810850405 success
arch-score / arch-score id=124810815728 success
arm id=124810732652 skipped
budget-raise-gate / budget-raise-gate id=124810815619 success
cancel-superseded id=124810737511 success
codeql / Analyze (actions) id=124810815638 success
codeql / Analyze (javascript-typescript) id=124810815564 success
codeql / Analyze (python) id=124810815649 success
governance / delivery-status id=124810815850 success
governance / delivery-status-publish id=124810817238 skipped
governance / env-matrix id=124810815669 in_progress
governance / instrument-self-tests id=124810815658 in_progress
governance / policy-docs id=124810815704 success
governance / record id=124810817039 skipped
governance / wave-script id=124810815798 success
hassfest / hassfest id=124810815628 success
kernel-points id=124810816700 skipped
prelude id=124810737344 in_progress
refresh id=124810737441 success
tests / arch-instrument id=124810929808 success
tests / briefs id=124810815666 success
tests / browser id=124810929759 in_progress
tests / closure-scope id=124810815677 success
tests / closures id=124810929788 in_progress
tests / coverage id=124810929891 in_progress
tests / fast (3.14) id=124810929806 in_progress
tests / mutation id=124810815630 success
tests / mutation-autofix id=124810967589 skipped
tests / mutation-pins id=124810967320 skipped
tests / nightly-ha id=124810930664 skipped
tests / nightly-status id=124810815789 success
tests / replay id=124810930641 skipped
tests / typing id=124810929811 success
validate / validate-hacs id=124810815537 success

## Refusals
none

## Advisories
none

## carry_audit at the head
CARRY-AUDIT: 0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)

## figure_lint at the head
unverified git show 8fec54ee2:dev/programme/HANDOVER.md
             `git show` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  unverified git ls-files --error-unmatch
             `git ls-files` resolves; its flags are not checked -- git prints a man page rather than a flag list, and a list carried in this file would rot into false refusals
  ok         tools/policy/policy_lint_envmatrix.mjs
             `tools/policy/policy_lint_envmatrix.mjs` is in the tree at this head
  ok         tools/policy/check-wave-script.mjs
             `tools/policy/check-wave-script.mjs` is in the tree at this head
  ok         .claude/hooks/session-start.sh
             `.claude/hooks/session-start.sh` is in the tree at this head
  ok         tests/entities.py
             `tests/entities.py` is in the tree at this head
  ok         tests/closure.py
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
             `tests/closure.py` is in the tree at this head
  ok         python3 tests/structure.py
             `tests/structure.py` is in the tree at this head
  ok         python3 -I tests/layout.py --guard --base $(git merge-base origin/main HEAD)
             `tests/layout.py` is in the tree at this head
  ok         node tools/policy/policy_lint.mjs
             `tools/policy/policy_lint.mjs` is in the tree at this head
  ok         tools/pr/prepr.sh <body>
             `tools/pr/prepr.sh` is in the tree at this head
  ok         tools/audit/seat/roster_lib.py
             `tools/audit/seat/roster_lib.py` is in the tree at this head

FIGURES: 11 resolved, 2 not verified, 0 refused

## Finder's harness: none named
### at the base
not run
### at the head
not run

## Mutation-ledger diff
none

## Three-dot diff
diff --git a/dev/programme/HANDOVER.md b/dev/programme/HANDOVER.md
index b2fcf4797..d0863f494 100644
--- a/dev/programme/HANDOVER.md
+++ b/dev/programme/HANDOVER.md
@@ -1,568 +1,565 @@
 # Handover — the open-issues programme
 
-updated-for: 0cc148b2f80fe224ffe2c504b29fd4f0908183df
+updated-for: a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0
 
-The rule that governs this file is `dev/governance/rules/writing-for-agents.md`
-(generated into `.claude/rules/`, which the harness loads on this path).
+This file is ruled by `dev/governance/rules/writing-for-agents.md` (generated
+into `.claude/rules/`, which the harness loads on this path). It holds what a
+session starting now must know and cannot derive from the tree in one command.
 Delivery status is the frozen table in `dev/programme/plan-2026-09-open-issues.md`
-plus one `dev/programme/delivery/<N>.md` per pull request (#1081), linked from
-here and never restated. Chronology this file no longer carries is read at its
-last pre-round-10 form, `git show a77faf30d:dev/programme/HANDOVER.md`.
-
-## Round 10 — durable state
-
-**Round 9 closed at v7.0.0** (#201 stays the tracking issue). Its handoff
-branches are archived as tags (`git tag -l 'archive/handoff/audit-r9-*'`), so a
-round-9 plan, roster or resume is read from its tag, never resumed.
-
-**Round 10 opened 2026-10-14** under tvofi's rulings: every dimension under
-`dev/governance/dimensions/`, three disjoint finder seats per dimension, one
-verifier per dimension whose refute marks a finding **disputed**, one common
-judge. Its stamps are read from main's first-parent line
-(`git log --first-parent --format='%h %s' v7.0.0..origin/main | grep ' v7\.'`),
-never listed here.
-
-- **The plan of record is the roster**, `dev/programme/rosters/wave-r10-groups.json`
-  on `origin/handoff/audit-r10-roster`, edited only through
-  `tools/audit/seat/roster_edit.py`. The resume, plan table and next-session
+plus one `dev/programme/delivery/<N>.md` per pull request, linked from here and
+never restated. **Volatile state is on #201 and nowhere here**: running seats,
+open pull requests and heads, the train queue, today's next action, the open-PR
+cap currently in force, and the mandate's id and dates. Chronology this file no
+longer carries is read at its last pre-round-10 form,
+`git show a77faf30d:dev/programme/HANDOVER.md`, and at the form before this
+rewrite, `git show b161681af:dev/programme/HANDOVER.md`.
+
+## Round 10 — what a resuming session needs
+
+**Round 9 closed at v7.0.0.** Its handoff branches are archived as tags
+(`git tag -l 'archive/handoff/audit-r9-*'`); a round-9 plan or roster is read
+from its tag, never resumed. Round 10 opened 2026-10-14 under tvofi's rulings:
+every dimension under `dev/governance/dimensions/`, three disjoint finder seats
+per dimension, one verifier per dimension whose refute marks a finding
+**disputed**, one common judge. Its stamps are read from main's first-parent
+line (`git log --first-parent --format='%h %s' v7.0.0..origin/main | grep ' v7\.'`).
+
+- **The plan of record is the roster**,
+  `dev/programme/rosters/wave-r10-groups.json` on
+  `origin/handoff/audit-r10-roster`, edited only through
+  `tools/audit/seat/roster_edit.py`, and by the roster seat. The tracked copy
+  of the roster on `main` lags that branch; `dev/programme/rosters/critical-path.json`
+  is a dated snapshot, not the path. The resume, plan table and next-session
   prompt under `handoff/round10/state/` on `origin/handoff/audit-r10-plan` are
-  generated from it by `tools/audit/seat/state_docs.py`; they are volatile and
-  not this file.
-- **Volatile state** — running seats, open heads, the train queue, the next
-  action, the critical-path set — is on #201 and nowhere here.
+  generated from the roster by `tools/audit/seat/state_docs.py`.
+- **Done for round 10** (tvofi, 2026-10-25, verbatim): "run the full programme
+  to completion (no owed handoffs, no deferred findings, no deferred leads, no
+  open roster groups, no issues open except 201, nothing deferred to round
+  11)". The plan page's ETAs are the contract the owner tracks; an owed line or
+  a slip is acted on the turn it appears.
+- **The critical path to closure** is whatever
+  `roster_lib.critical_path(roster)` returns over the open groups of the roster
+  at `origin/handoff/audit-r10-roster` (`tools/audit/seat/roster_lib.py`; load
+  the JSON and call it). Read at 2026-10-31 it was `R10-FLY-MUTANT-RESTORE`,
+  `R10-AUDIT-COVERAGE-ENDGAME`, `R10-CLOSEOUT-CLEANUP`, `R10-ROUND-PLAYBOOK`;
+  re-derive it, it moves with every `set-stage`. Closure follows it: the
+  coverage endgame runs after every group that adds code, the closeout cleanup
+  (refs archived as tags, main plus at most two development branches) and the
+  playbook (`dev/audit/README.md` for round 11 on) are the last groups, and
+  `R10-CATALOG-PR` (the hacs/default catalog pull request) waits until the
+  closeout stamp. A critical-path group whose `after` groups are done starts
+  at any cap (`orchestrator.md` section 5).
+- **Versions.** The closeout stamp of round N is N.0.0, so round 10 closes at
+  v10.0.0 through `tools/release/stamp.py --round-close 10`; between closeouts
+  a stamp is `--bump minor` or `--bump patch` and `--bump major` refuses
+  (decision 0016, tvofi, 2026-10-29). Versions jump 7.x to 10.0.0 by rule.
 - **The record beat writes delivery rows; this file's `updated-for:` line stays
-  manual by design.** `tools/audit/seat/record_row.py` generates each row from
-  REST facts into a `record/autofix` pull request that merges with no review
-  seat where `--automerge-check` passes. Expect two things and do not repair
-  them: the one-beat lag (a merge's row lands on the next cycle), and no beat row
-  for a closed-unmerged pull request, whose `closed, superseded` row is a manual
-  record pull request. A seat's edit to a generated row takes that pull request
-  off the automerge path.
+  manual.** `tools/audit/seat/record_row.py` generates each row from REST facts
+  into a `record/autofix` pull request that merges with no review seat where
+  `--automerge-check` passes. Expect, and do not repair, the one-beat lag, and
+  no beat row for a closed-unmerged pull request (a manual record pull request
+  writes its `closed, superseded` row). A seat's edit to a generated row takes
+  that pull request off the automerge path.
+
+## The seats and who may do what
+
+- **Identity** (decisions 0011, 0013; `CLAUDE.md`). Pull requests are authored
+  by `hpo-author` through `tools/pr/app_push.sh`; verdicts post as
+  `hpo-approver`; only the orchestrator writes to GitHub. A seat pushes refs
+  only: a fixer `handoff/<topic>` and `handoff-body/<topic>`
+  (`tools/audit/seat/body_push.sh`), a reviewer its verdict on the probe ref its
+  brief names. **Commits take the author from the environment**: set
+  `GIT_AUTHOR_*` and `GIT_COMMITTER_*` to `hpo-fixer` and the noreply address
+  in every shell that commits, because the session environment pre-sets them to
+  the owner and beats `git config` and `-c`. Check `git log -1
+  --format='%an <%ae>'` after each commit.
+- **Standing seats**, each on its own contract in `dev/governance/roles/`:
+  `standing-tick.md` (lists owed items, never acts), `standing-merge.md`
+  (operates the train, never chooses what merges), `standing-dispatch.md`
+  (dispatch, relay, verdict confirm), `standing-roster.md` (`roster_edit.py`
+  ops behind the lint gate), plus `proposal-triage.md` (opus; a proposal gets a
+  ruling before it is routed). The orchestrator sends queue lines and acts on
+  reports; `tools/audit/seat/pulse.py` and the sweep's liveness step restart an
+  absent one. **The orchestrator never runs `train.sh add`, a roster op or a
+  dispatch inline** (tvofi, 2026-10-21 and 2026-10-27): it confirms a verdict on
+  the bus and hands the merge seat the PR head, the verdict's reviewed head and
+  any carry judgement.
+- **Seat placement** (tvofi, 2026-10-24, 2026-10-28, 2026-10-30). Cloud seats
+  are uncapped and fire through `tools/audit/seat/cloud_dispatch.py` and a
+  remote trigger; a cloud run is one-way, nothing comes back on SendMessage.
+  M-and-larger, critical-path and repeatedly blocked groups run as local seats
+  so the orchestrator can steer them, at most eight local seats counting the
+  standing ones. **When the local 1-minute load is far above the core count
+  (the ruling's own figure was about 50 on 8 cores), L, XL and critical-path
+  fixers go to the cloud too.** A cloud seat silent past about 2.5 hours with
+  no ref pushed is re-run locally after an `ls-remote` guard against a late
+  push. Fixers run at medium effort; a mechanical turn takes sonnet or haiku.
+- **The open-PR cap** is the owner's, restated on #201 each time it moves, and
+  it is a count of open pull requests that gates only starting a new roster
+  group. `pr_cap.py dispatch-gate` counts in-progress roster groups against
+  `HPO_WIP_CAP` instead, which is not the owner's rule: never quote its `WIP
+  n/6` as the cap.
+- **Record pull requests** (this file, delivery rows, roster batches) are
+  reviewed by sonnet. A record seat's checks are `tools/pr/prepr.sh` with no
+  closures skip, its CI-predict step, and `python3 tests/structure.py`.
+
+## The instruments in daily use
+
+`tools/audit/seat/INSTRUMENTS.md` is the operator's guide and the only
+inventory; look an instrument up there before writing a loop, relay or helper
+(`orchestrator.md` section 13). The ones a session reaches for first are the
+tick driver (`tick_loop.sh`, `orchestrator_tick.py`), the verdict path
+(`bus.sh`, `cloud_dispatch.py`, `cloud_relay.sh`, `review_packet.py`,
+`review_carry.py`), the handoff path (`open_pr.sh`, `update_pr.sh`,
+`body_push.sh`, `body_patch.sh`), the merge path (`train.sh`, `merge_train.py`,
+`tools/pr/app_approve.sh`), the roster (`roster_edit.py`, `roster_sync.py`,
+`state_docs.py`), the sweep (`sweep_render.py`, `sweep_template.md`), and
+`tools/audit/worktree_gc.sh` after each merge. Comments on #201 and on pull
+requests are posted with `tools/pr/gh_comment.py` and read back
+(`comment-readback.md`).
+
+- **The seat interpreter.** Put `$HOME/.local/state/hpo/venv-ci/bin` and the
+  repository's `tools/audit/seat/shims` first on `PATH`, and set `PYTHON` to
+  that venv's `python3`; bare `python3` is 3.11 and `prepr.sh` dies on a PEP 701
+  f-string. `tools/audit/seat/seat_venv.sh` builds it. A seat venv's `BASH_ENV`
+  can make an instrument self-test pass vacuously: reproduce a red with
+  `env -u BASH_ENV`. A cloud container may not put the toolchain on `PATH`
+  either: prepend `/opt/hpo/venv-ci/bin`, run with `env -u BASH_ENV
+  PYTHONPATH=tests/hastub`, and through the agent proxy loop
+  `?per_page=100&page=N` on the `repos/<owner>/<repo>` path, because `gh api
+  --paginate` follows GitHub's numeric-id `Link` URL and gets 403 after page one.
+- **Anything over about 60 seconds runs detached** through
+  `tools/audit/seat/daemonize.py --log <file>`; read the log when it exits and
+  do not block a foreground turn on it (tvofi, 2026-10-30).
+- **Never `git stash`**: every worktree shares one stash list and a pop can take
+  another seat's work. Commit to a scratch branch or copy the files.
+- **No `pkill -f` or kill by pattern**; stop only a PID you started. A wait loop
+  that `pgrep`s its own pattern matches itself.
+- **A GitHub poll is no faster than every 300 s**; prefer `git ls-remote` and
+  `git fetch` to REST. Heads of moving refs are read with `ls-remote`, never
+  from `FETCH_HEAD` in a shared worktree.
+
+## The mandate
+
+The authority to approve as the owner is a record, read from the API at the
+moment of use and trusted nowhere in the tree: the newest comment by `tvofi`
+on #201 whose first line is `MANDATE: agents may approve as tvofi, scope
+<code-owned|budget-raise|all>, from <ISO> until <ISO>`. Its id, scope and
+dates are on #201 and in the sweep prompt; decision 0013 and its 2026-10-02
+and 2026-10-14 amendments are the rule. After `until`, decision 0007's
+per-pull-request owner review is the rule again.
+
+- **Under scope `all`, the orchestrator approves code-owned, policy and
+  budget-raise merges itself** (tvofi, 2026-10-20 and 2026-10-27, "my approval
+  is still not required during your valid mandate to act as me"). Do not park a
+  group as waiting on the owner's review. Cite the mandate in the review and
+  merge body in the grammar `MANDATE_CITE` reads (`mandate #<id>` or a bare
+  `issuecomment-<id>`, never backticked), exactly one id per review.
+- **A raise is still searched for.** A budget raise under the mandate owes
+  `## Raise justification`: each payment tried and the `Architecture score: dS`
+  line `tools/audit/archscore/score.py --diff` printed. The mandate waives the
+  owner's signature and not the search (`CLAUDE.md` rule 2). A raise the only
+  sound payment calls for is the orchestrator's to rule (tvofi, 2026-10-23); a
+  seat's classifier denial of it is not laundered through the mandate, the seat
+  is re-briefed or the work runs where the action is allowed.
+- **The kill switch is deliberately loose.** `budget_raise_gate.py` voids a
+  mandate on any later comment by the owner's account on #201 that contains the
+  stem of the verb "to revoke", in any case, on any line, beside that
+  mandate's id. **An identifier counts**: a roster group whose name contains
+  that stem voided it a second time (2026-10-31) and refused a pull request's
+  `budget-raise-gate`. The first time (2026-10-21) a decision's text did. In any
+  comment posted as `tvofi`, never write the stem next to a mandate id and
+  grep the text for it first; say "withdrawn", or cite the mandate in a
+  separate comment. The repair for a voided mandate is the owner posting a
+  fresh one, or, as on 2026-10-31, editing the offending comment and
+  re-running the failed jobs after a local gate PASS. The barrier is the
+  mandate-guard roster group's carry (`gh_comment.py` refusing the pairing).
+- **What the mandate does not cover**: anything past its `until`, and a change
+  to what a seat must do that has no review verdict behind it. While
+  `tvofi`'s own latest decisive review is CHANGES_REQUESTED the gate refuses.
+- **While the owner is away** (tvofi, 2026-10-28): decide by the recommendation,
+  record the decision and its reason, never stall on an owner flag.
+
+## Merge, train and stamp
+
+1. **Evidence.** `gate` passed at the head, and a `Fix review: merge <sha>`
+   verdict from a reviewer who measured this head, or a carry
+   (`tools/pr/app_approve.sh --carry <verdict> <head>`; `review_carry.py` says
+   whether a moved head needs its own review). `orchestrator.md` section 11 is
+   the list. Read check-runs from `/repos/<owner>/<repo>/commits/<sha>/check-runs`
+   and not `gh pr checks`, which shows the latest run per check and hides a
+   red behind a later green; a context with no run at a head is "not yet",
+   never green, and a `CANCELLED` required context is not a verdict (rerun it).
+2. **Queue.** The orchestrator picks membership and order, critical path first,
+   and hands the merge seat each PR, its reviewed head and the mandate. The
+   queue entry's `verdict` is the **reviewed PR head** from the verdict's first
+   line, an ancestor of the live head, never the commit `bus.sh confirm` prints
+   (that one is never an ancestor, and a wrong value reads as
+   `STALE-VERDICT-CARRY`). `verdict_comment` is the comment id read back from
+   the API.
+3. **Train.** The merge seat runs `tools/audit/seat/train.sh` on its
+   `RECOMMENDED` defaults, `batch`, one live train, detached; `train.sh add`
+   loads a late verdict into the batch already running. **No merge outside the
+   train** (tvofi, 2026-10-26): not a budget head, a policy head or a hotfix;
+   those are reasons to batch. A refusal is reported and the head fixed, never
+   landed another way. `--overlap` means the train does not wait on `main`'s
+   gate between merges and each car's own CI must have run on its current
+   head; batching is the `batch` subcommand, not that flag. Never a second
+   train on the same state dir, and never `--allow-red`.
+4. **The merge message** is a closing surface (`orchestrator.md` section 4):
+   no negated closing keyword, never a custom `--subject`, `preflight.sh` as a
+   filter with the intended issues as arguments, then read which issues the
+   merge actually closed.
+5. **After each merge**: `state_docs.py --push`, the merge's #201 comment, the
+   delivery row (the beat writes it; a frozen PR's own row costs a record pull
+   request), the roster `set-stage` through the roster seat, and
+   `tools/audit/worktree_gc.sh`. This file is updated in the same record pull
+   request as the merge it records, and `updated-for:` names a merge that
+   `origin/main` contains (`tests/entities.py` refuses a branch-local SHA, which
+   a squash orphans).
+6. **If a merge reddens `main`**: a behaviour change in the merged diff is
+   reverted first and diagnosed after; a failure the diff cannot reach is
+   established as such and is its own issue.
+7. **Stamp.** The orchestrator stamps, `stamp.py --push --push-key
+   ~/.zcode/stamp-deploy.key --known-hosts <file>`, never by hand and never in
+   a branch. It refuses a `main` whose `ci.yml` push run's `gate` is not green
+   (`--allow-red` takes the cause in the release notes and on #201), a window
+   with a merged PR lacking its row (`--allow-rowless` likewise), and notes
+   omitting a merged PR. The deploy key's SSH on port 22 can time out from the
+   stamping host: route `github.com` to `ssh.github.com:443` and verify the host
+   key against GitHub's published fingerprints.
 
 ## Decisions taken — do not relitigate
 
-- **Mandate 6175172275 (#201, tvofi): `MANDATE: agents may approve as tvofi,
-  scope all, from 2026-10-14T18:14Z until 2026-10-28T18:14Z`.** It covers
-  code-owner, policy and budget-raise approvals, so the round-10 orchestrator
-  approves code-owned and policy merges under it, citing the id in the review
-  body. Read it and any revocation from the API at the moment of use, as 0013's
-  2026-10-02 amendment does; a raise under it also owes that decision's
-  2026-10-14 amendment (`CLAUDE.md` rule 2). After `until`, decision 0007's
-  per-pull-request owner review is the rule again.
-- **The open-PR soft cap of 6 gates only starting a new roster group; opening or
-  updating a pull request for an owed handoff is never refused** (tvofi,
-  2026-10-21, refining the 2026-10-18 ruling in `tools/audit/seat/pr_cap.py`).
-  The instrument predates the refinement: `open_pr.sh` calls `pr_cap.py gate` on
-  every open, so until it learns the distinction an owed handoff opens with
-  `--over-cap "owed handoff <topic> (tvofi 2026-10-21)"`. Owed below.
-- **Cloud seats are dispatched through `tools/audit/seat/cloud_dispatch.py` and a
-  remote-trigger dispatcher routine, never as interactive session cards**
-  (tvofi, 2026-10-21). The payload shape, the return refs and the two driving
-  traps are `tools/audit/seat/INSTRUMENTS.md`'s.
+- **`main` is guarded by three rulesets**, read from
+  `/repos/<owner>/<repo>/rulesets/<id>` and never from here: `main-protect`
+  (22628467), `main-protect-checks` (23698884; the required checks, one
+  approving review, the code owner's review per 0009 step 6) and
+  `release-tags-protect` (23937752). Rollback is one DELETE per ruleset.
+  **Before adding a required context** confirm it reports on a pull-request
+  head and not only on a push to `main`: one that never reports blocks every
+  merge, a matrix change is a required-set change, `skipped` and `neutral`
+  satisfy the rule, and a scheduled context made required blocks the merge that
+  would repair it. `GET /repos/.../rules/branches/<branch>` is not
+  bypass-aware: test a bypass on a probe branch with its own ruleset, both arms.
+- **CI is one umbrella with one required check.** `.github/workflows/ci.yml`
+  calls one file per unit, each check reading `<stem> / <job>`; `gate` is the
+  only required context (`tools/policy/fixtures/required-contexts.json`),
+  moved by `tools/ci/ruleset_cutover.py`. Autofix jobs dispatch `ci.yml -f pr
+  -f base` once; the stamp precondition is the latest `ci.yml` push run's
+  `gate` on `origin/main`. The approve steps and `approve_held_runs.sh` stay
+  until M-3 decides (design `archive/probe/design-ci-rev4`, review
+  `archive/probe/design-ci-review5`).
 - **Model routing is Claude seats, per roster group** (`fixerModel`,
   `reviewerModel`, the `model` object). The owner's 2026-09-09 ruling: Opus for
   orchestration, architectural fixes and review, survey, judge and production
   fixes; Sonnet for tests, tooling, docs, records and read-only reporting;
   **Fable only for a very large multi-layer refactor where Opus is judged too
   risky.** A model trailer on a merge or a stamp is the session's model, not a
-  routing event.
-- **`main` is guarded by three rulesets**, read from
-  `/repos/<owner>/<repo>/rulesets/<id>`, never from here: `main-protect`
-  (22628467) holds deletion and non-fast-forward and, read 2026-10-21, no bypass
-  actor; `main-protect-checks` (23698884) holds the required checks, one
-  approving review and the code owner's review (0009 step 6), with `always`
-  bypasses for the stamp deploy key and the `hpo-ledger` App 5094721;
-  `release-tags-protect` (23937752) guards tags, deploy key bypassing. Rollback
-  is one DELETE per ruleset (#1300). **Before adding a required context** confirm
-  it reports on a pull-request head, not only on a push to `main`: one that
-  never reports blocks every merge, a matrix change is a required-set change,
-  `skipped` and `neutral` satisfy the rule (measured both arms), and a scheduled
-  context made required blocks the merge that would repair it.
-- **CI is one umbrella with one required check** (R10-CI-LAYOUT P2b; design
-  `archive/probe/design-ci-rev4`, review `archive/probe/design-ci-review5`).
-  `.github/workflows/ci.yml` calls one file per unit, each check reading
-  `<stem> / <job>`; `gate` is the only required context
-  (`tools/policy/fixtures/required-contexts.json`, `gate_required` lists the
-  units it stands for), moved by `tools/ci/ruleset_cutover.py` at the merge.
-  Autofix jobs dispatch `ci.yml -f pr -f base` once; the stamp precondition is
-  the latest `ci.yml` push run's `gate` on `origin/main`. `RUN_PART=fast|arch`
-  splits `run.sh` between `tests / fast` and `tests / arch-instrument`. The
-  approve steps and `approve_held_runs.sh` stay until M-3 decides. Policy text
-  moved with it (`ci-autofix.md`, `orchestrator.md` section 11, `nudge.md`).
-- **A stamp pushes over the deploy key only**: `tools/release/stamp.py --push
-  --push-key <key> --known-hosts <file>`. The old admin token returns 401.
-  A stamp over a red `main` takes `--allow-red` with the cause recorded in the
-  release notes and on #201, and over a merge whose row is not yet written
-  `--allow-rowless` likewise (v7.0.2, tvofi, 2026-10-20).
+  routing event. Effort and the mechanical-turn models are under the seats
+  section above.
 - **Merges land as merge commits** (0010); the merge body defaults to the pull
-  request's title, so a closing keyword in a title reaches `main`.
-- **`_helper(self, ...)` is refused** as a decomposition: it erases moved
-  references at zero cost, a measurement artefact; a supplied-literal check pins
-  nothing.
+  request's title, so a closing keyword in a title reaches `main`. A closing
+  keyword in a branch's commit message links an issue just as a pull-request
+  body does (#503 acquired a false link to #457 that way).
 - **Never re-gate an unchanged head.** A terminal CI result at that head is the
-  gate evidence. Local runs exist for what CI cannot produce: the mutation proof,
-  the failing test at the merge base, the finder's harness at both ends.
-- **#387 was fixed with the `env_drift` shape**, not by growing `alt_basins` nor
-  by lowering the coverage floor: tree and merge base in one run, computed to
+  gate evidence. Local runs exist for what CI cannot produce: the mutation
+  proof, the failing test at the merge base, the finder's harness at both ends.
+- **`_helper(self, ...)` is refused** as a decomposition: it erases moved
+  references at zero cost, a measurement artefact.
+- **#387 was fixed with the `env_drift` shape**, not by growing `alt_basins`
+  nor lowering the coverage floor: tree and merge base in one run, computed to
   computed. The coverage floor is a literal, not an environment override.
-- **Every sentence earns its place** (owner, 2026-09-07); the rule is
-  `writing-for-agents.md`.
-- **The #1058 tie-break: a body long from disclosed self-corrections is re-cut by
-  relocating them here.** `fixer.md`'s re-cut and *cutting evidence is never
-  compliance* pointed opposite ways; a disclosed self-correction is a correction
-  to the record, so it moves into that section below and nothing is cut.
-- **A pull-request body carries `## Figures`** (#676). The detector that works
-  resolves a file name to an artefact; the looser one — any number near a file
-  name — was refused in review for reading a date and a line count as caps.
-- **The pull-request body is one live object.** Every head's contract job reads
-  the current body, so a red at a superseded head is the instrument, not the
-  commit.
-- **A new option key derives into `config_flow._ABSENT_FALLBACKS`** or every
-  options-page visit writes it (#1107); `tests/config_flow_steps.py` derives the
-  set rather than listing it.
-- **A coverage ratio over an open set of mutation carriers is not a figure**; the
-  denominator is unbounded, so state the class. **A figure about the document it
-  lives in is derived beside it, at the head.**
+- **The #1058 tie-break: a body long from disclosed self-corrections is
+  re-cut by relocating them here.** `fixer.md`'s re-cut and *cutting evidence
+  is never compliance* pointed opposite ways; a disclosed self-correction is a
+  correction to the record, so it moves into this file and nothing is cut.
+- **A pull-request body carries `## Figures`** (#676). The detector resolves a
+  file name to an artefact; the looser one, any number near a file name, was
+  refused for reading a date and a line count as caps. The body is one live
+  object: every head's contract job reads the current body, so a red at a
+  superseded head is the instrument, not the commit.
+- **A coverage ratio over an open set of mutation carriers is not a figure**;
+  the denominator is unbounded, so state the class. A figure about the
+  document it lives in is derived beside it, at the head.
 - **A generalised vacuous-acceptance-arm detector is refused on cost** (#201
-  comment 5720829142, #1125's reviewer ruling): the shape is three classes — a
-  harness decoupled from the mutated code (W1067-G7b-1), an under-specified
-  environment precondition (#1115), a false prose claim no mutation proof
-  addresses (#1120) — and a detector needing different logic per class was
-  judged a research project against a defect costing about one review round.
-  The refusal owes its qualifier: the catch rate rests on an attentive seat, not
-  a mechanism. #1126 is the instance found after it: a check carried a retyped
-  copy of `VERDICT_RE` that diverged from `web-fix-wave.js`'s, and its null
-  control passed on either regex; the fix executes the source's own literal. Do
-  not re-propose without new information.
+  comment 5720829142): three classes (a harness decoupled from the mutated
+  code, an under-specified environment precondition, a false prose claim no
+  mutation proof addresses) needing different logic per class, against a defect
+  costing about one review round. The refusal owes its qualifier: the catch
+  rate rests on an attentive seat. The instance found after it, #1126: a check
+  carried a retyped copy of `VERDICT_RE` that diverged from
+  `web-fix-wave.js`'s and its null control passed on either regex; the fix
+  executes the source's own literal. Do not re-propose without new information.
 - **Wave 1067's three deferrals stand** (plan
   `dev/archive/plans/plan-1067-rotenso-inputs.md`): the new option keys stay
   options-page slots out of `topology._SLOTS`; no zone-2 supply slot, since the
   two-zone model carries one flow temperature and no per-zone emitter law; the
   flow-lift bias stays one-sided so the scalar and batch COP paths agree.
-  **W1067-POST1** (offer the pre-fill when a heat-pump device is added) gets its
-  own issue when started, none before.
+  **W1067-POST1** (offer the pre-fill when a heat-pump device is added) gets
+  its own issue when started, none before.
 - **dp 107 is read two ways and stays unresolved without a reading from the
-  owner's install** (owner decision 7, W1067-G7b-2): make-all/tuya-local
-  (`4551357`, `devices/fisher_water_heatpump.yaml`) reads it as the tank's
-  current temperature, tvofi/tuya_heat_pump (`fda9bed`, `models/000004k4z6.py`)
-  as the wired controller, tank on dp 26; both readings are pinned in
-  `tests/features.py`. A DP-keyed localtuya table is refused for the same reason
-  — a DP number is not identity — unless a firmware signature proves the device.
+  owner's install**: make-all/tuya-local (`4551357`,
+  `devices/fisher_water_heatpump.yaml`) reads it as the tank's current
+  temperature, tvofi/tuya_heat_pump (`fda9bed`, `models/000004k4z6.py`) as the
+  wired controller, tank on dp 26; both readings are pinned in
+  `tests/features.py`. A DP-keyed localtuya table is refused for the same
+  reason, a DP number is not identity, unless a firmware signature proves the
+  device.
 
 ## Corrections to the record
 
 - **This file is not policy and no budget reads its text.** It sits outside
-  `POLICY_GLOBS` (owner, 2026-09-16, #201 comment 5702401684; `.github/CODEOWNERS`
-  says so in its header), so a record pull request touching only it owes no
-  `## Approval` and no code-owner review. `policy_budgets.json` names it in
-  `roles.record.opens`, which charges the rules that path loads, not the file:
-  `policy_lint.mjs --budgets` prints the same aggregates with this file grown.
-  The residual is a reviewer's: prose moved here leaves the corpus.
-- **The `hpo-ledger` bypass on `main-protect` is gone.** The owed item that asked
-  tvofi to ratify or remove App 5094721's `always` bypass on 22628467 (#201
-  comment 5902383542; 0011's 2026-10-02 setup recommends removal) is retired: a
-  read of that ruleset on 2026-10-21 returns no bypass actor. 0011 still records
-  the decision as the owner's to take.
-- **The "34-key `data` payload" is wrong**, as is any count of it; the freeze is
-  enforced by `tests/features.py`'s symmetry check and the `coord_*` goldens
-  (#193).
-- **#510 was blindness, not decoupling**: `tests/structure.py` did not resolve
-  `getattr(self, "_ctx", self).X`; under a counter that does, Wave 4's S1 cut
-  series is identical at both ends (#512).
+  `POLICY_GLOBS` (owner, 2026-09-16, #201 comment 5702401684), so a record pull
+  request touching only it owes no `## Approval` and no code-owner review.
+  `policy_budgets.json` names it in `roles.record.opens`, which charges the
+  rules that path loads, not the file. The residual is a reviewer's: prose
+  moved here leaves the corpus.
+- **The "34-key `data` payload" is wrong**, as is any count of it; the freeze
+  is enforced by `tests/features.py`'s symmetry check and the `coord_*` goldens.
+- **The `hpo-ledger` bypass on `main-protect` is gone**: a read of that ruleset
+  on 2026-10-21 returns no bypass actor; 0011 still records the decision as the
+  owner's.
+- **Leave both claim files exactly as you found them** (#662). "Always
+  byte-identical" was refused (#600 rightly carries claim lines), then "empty
+  on a branch that claims nothing": a squash applies that deletion to `main`
+  and carries another lane's claims off, measured four times.
 - **A file reported missing was there**: the seat listed a checkout on a stale
   branch. Check existence with `git show origin/main:<path>`.
-- **Leave both claim files exactly as you found them** (#662). "Always
-  byte-identical" was refused (#600 rightly carries 33 claim lines), then "empty
-  on a branch that claims nothing" — a squash applies that deletion to `main` and
-  carries another lane's claims off, measured four times (#608, #635, #658,
-  #746). Since #747 the guard, the bot and the stale-claim judgement ask per file
-  kind.
-- **The pull-request checks listing shows the latest run per check** (#669), so
-  an earlier red behind a later green is invisible, and the mirror error reads a
-  superseded failure as red. Read `/repos/<owner>/<repo>/commits/<sha>/check-runs`
-  (`web-fragments.md`).
 - **The subject enumerator missed merges and invented them, and the errors hid
-  each other** (`24 = 25 - 2 + 1` over `a9d117c..8f754c9`). Compare sets, never
-  totals; the API enumerator is the default since #1050.
-- **The red-check refusal fires from `f605da4` (#1040) on**; `CLAUDE.md`'s "only
-  the red-check trigger is enforced" is a measurement from that SHA.
-- **`GET /repos/.../rules/branches/<branch>` is not bypass-aware**: emptying the
-  bypass list returns an identical answer. The honest test is a probe branch
-  with its own ruleset, both arms.
-- **An empty diff over `tests/` and `custom_components/` does not mean no gate is
-  owed** (#1122): the merge had moved files inside recorded closures. Derive scope
-  from `closure.py select`, never from top-level directories.
-- **Wave 1067's merged bodies carry three figures their reviewers could not
+  each other.** Compare sets, never totals; the API enumerator is the default.
+- **An empty diff over `tests/` and `custom_components/` does not mean no gate
+  is owed** (#1122): derive scope from `closure.py select`, never from
+  top-level directories.
+- **Wave 1067's merged bodies carry figures their reviewers could not
   re-derive**; the bodies stay, this is the correction. #1150's "22 other
-  configs" is 21 (`comm -23`), and its empty-signature predicate returns `True`
-  on `all(())` — unreachable today, a trap for a future table. #1152's "253.3 µs
-  per drive" measured 72.4 µs on the reviewer's driver, unverified either way;
-  the verdict holds at both. #1153's "256 production lines (218/32/6)" is 281
-  (`237 + 37 + 7`) under the body's own rule, and its "0 `mypy --strict` errors"
-  is unavailable, not true or false; CI's `typing` check is the answer.
+  configs" is 21, and its empty-signature predicate returns `True` on
+  `all(())`, unreachable today and a trap for a future table. #1152's "253.3 µs
+  per drive" measured 72.4 µs on the reviewer's driver; the verdict holds at
+  both. #1153's "256 production lines" is 281 under the body's own rule, and
+  its "0 `mypy --strict` errors" is unavailable, not true or false; CI's
+  `typing` check is the answer.
 
 ## Traps that cost a session
 
-**A trap that has acquired a mechanical detector becomes a one-line pointer to
-it.** Promotion, not cutting. The detector must fire when the trap would bite,
-in that trap's mode — reporting where a reader is asked to look, refusing where
-a wrong answer would pass unattended — and each graduation owes a mutation proof
-in its own pull request.
-
-1. **A killed agent never writes its own `state at stop:` comment.** On resume
-   the orchestrator walks the session's branches and open pull requests and
-   posts the notes the dead agents owed.
-2. **A stand-down note and a committed roster can disagree; origin is the
-   tiebreak** — the pull request's own comments. One re-review nearly
-   re-derived a verdict already posted.
-3. **A gate cannot be its own witness.** When the subject is the selection
-   machinery, the selection that runs is chosen by what is under test; #356
-   shipped a regression its own CI could not see, because editing a gate file
-   routed it to the one path that could not reproduce the fault.
-4. **A check whose failure is *visible* and one whose failure is *blocking*
-   look identical in a passing run.** Two sessions each built the first
-   believing they had the second.
-5. **Six of this project's own instruments reported rather than measured** —
-   #341, #347, #354, #350, #357, #510 — each found by someone chasing something
-   else. The pattern is the finding, not the individual bugs.
-6. **A figure from another artefact is not measured until you run the thing
-   that produced it.**
-7. **A branch can be stale against main invisibly in its own diff**: a move
-   reverting a fix that landed inside the moved lines, or a stale claim or
-   budget table. Only a three-dot comparison against current main catches it.
-8. **One CI runner is not the fleet** (#387). Graduated:
-   `policy_lint_envmatrix.mjs`, five declared shapes and thirteen named rows.
-9. **The machinery a handover depends on is code nobody ran** — `.claude/` is
-   `INERT`. Graduated: `check-wave-script.mjs` and `policy_lint --hooks`.
-10. **A closing keyword in a commit message links an issue just as a pull-request
-    body does.** #503 acquired a false link to #457 that way and had to be
-    corrected before it could merge.
-11. **A shallow checkout fails a driver on the clone, not the tree.** Graduated:
-    `entities.py` refuses a history-reading driver at depth 1 (#901).
-
-12. **A shallow clone turns "commits ahead" into fiction**; four such figures
-    once reached a handover. Graduated: `.claude/hooks/session-start.sh`.
-13. **A fix gets verified against the instance that was demonstrated, not the
-    property that was stated.** The demonstration displaces the specification,
-    the verification is built from the demonstrated instance's *form*, and any
-    sibling carrying the property in a different form survives — including one
-    the same commit creates. Established by root-cause analysis over #531, #569
-    and #591: **3.1% of reviewed pull requests, 11.2% of all review rounds.**
-    A check cannot close it — `tools/audit/preflight.sh`, written against this
-    very class, catches **0 of 3**: a grep asks *is there a figure here* while
-    the defect is *was the right thing measured*. The divider is **structural,
-    not dispositional**: across every review-round body in the corpus at the
-    time — 161 rounds over 97 reviewed pull requests, and it grows, so
-    re-derive — the class reached no seat's *production* fix. A production fix
-    is accepted by standing property-quantified instruments (CI, the ratchet,
-    closures, the mutation proof); a record or policy artifact has none.
-14. **"The pull request is open" is not a handoff.** The freeze starts at
-    handoff, and a seat that has opened one may still be pushing while it waits
-    on CI. Six pull requests had a head moved under a live review in one
-    session, #531 four times by itself.
-15. **A record pull request cannot converge while the merge queue runs.** #531
-    stayed open 20 hours over 45 commits, 25 content edits and 11 blocked
-    rounds, with 31 pull requests merging underneath it, each merge
-    invalidating part of its content. One record per merge has a bounded truth
-    condition and cannot be overtaken; live state belongs on #201, where no
-    merge can stale it.
-16. **`date -jf '%Y-%m-%dT%H:%M:%SZ'` parses a UTC stamp as local time.** Every
-    age computed that way is wrong by the offset; it once made a queue aged
-    8 minutes to 20 hours read as a flat "2h". Use Python's
-    `datetime.fromisoformat` with an explicit UTC now.
-17. **Backticks inside a double-quoted shell string are command substitution.**
-    Three review comments were posted with their SHAs silently missing. Write
-    the body to a file with a quoted heredoc and hand it to `gh_comment.py
-    --body-file`.
-18. **A citation and its referent can live on two branches, and the relation
-    between them is invisible to every branch-scoped check.** Two green branches
-    merged to a red `main` with no conflict and no shared file: one landed a
-    brief citing `configuration_url`, the other deleted the tracked tree's only
-    occurrence of that string, and git reported nothing because they touch
-    different files. Nothing was overwritten and both changes survived intact;
-    the failure is purely relational. `CLAUDE.md` rule 1's asymmetry caught it:
-    a push to
-    `main` forces `GATE_SCOPE=full`, and that argument, written about closures,
-    paid out for something nobody had in mind. **The preventable half is that
-    the citation was anchored to one English sentence. Prose is not a pin** —
-    restoring the sentence would have greened the gate and reproduced the
-    defect, so the repair was to re-anchor.
-19. **A clean merge is evidence of no textual overlap and nothing else.** Twice
-    in one session two sides appended at the same insertion point and shared a
-    trailing bracket, so `--ours` would have dropped a whole block silently.
-    Verify a merge by parsing the result and naming the checks that run.
-20. **A one-sided cap and a growing document collide across branches** — #608
-    capped this file, #607 added 43 lines 56 minutes later and `main` went red.
-    Graduated: `policy-docs`'s `[budgets]`. Trap 17 on a budget.
-21. **A comment bumps a pull request's `updated_at`, so it is not a body-edit
-    clock.** Read as one, it dated a body edit to a reviewer's comment. The
-    clock is the `Governance` run list: the job fires on `[edited]`, so a
-    missing run means no edit happened.
-22. **Assert a mutation's occurrence count before applying it.** A control
-    reported a cap mutant NOT CAUGHT: the replacement hit the string's first
-    occurrence, inside a comment, so the run was unmutated. "I could not find
-    it" differs from "it is pinned". Same shape: an unanchored `case` glob
-    accepts `v1.2.3; rm -rf /`.
-23. **A subagent does not survive a session restart; its report does.** Read
-    `tasks/<agentId>.output` before re-dispatching — `ListAgents` goes empty
-    with no notification, and an hour nearly went on finished work.
-24. **Re-pointing a branch chain by POSITION after a rebase drops a commit.**
-    Map by commit subject and verify the tip's pin count: by index once shifted
-    eight branches by one, and only that count noticed.
-25. **A citation repointed to a commit that resolves but lacks the file is
-    worse than a dead one.** Graduated for the corpus and the rosters:
-    `citations` refuses a tag-cited path the tag does not carry. Elsewhere,
-    `git cat-file -e <sha>:<path>`, not per directory.
-26. **A body's count of its own diff must come from the diff.** #621's body
-    said five disposition rows; the diff added nine, because the author counted
-    what they remembered writing. Derive a body's counts by mutating the
-    artefact and reading the detector: here, removing all nine rows and reading
-    `--record`'s refusal.
-27. **A figure in prose whose referent is a function of `origin/main` is stale
-    by construction, not by neglect.** It was the single largest source of
-    blocked rounds under the 2026-09-09 grant, and `claims` outnumbered every
-    other block class together. **No count is given here, and that is the trap
-    demonstrating itself**: the first draft carried one, it went stale on every
-    round of the review that landed it because its referent was that review's
-    own history, and the replacement count of how many times it had gone stale
-    went stale too. Derive it — scrape `Fix review: blocked <sha> <class>:`
-    across the grant's pull requests and count the classes.
-    Partly graduated: `COUNT_RULES` in `.claude/workflows/counts.mjs` refuses
-    prose disagreeing with a figure derived from the artefact that answers it,
-    and `brief_lint.mjs` runs that set less `modules` over roster briefs (#672).
-    Quote neither count — #676 added a rule while this said eight, the trap
-    firing on itself. **The other half does not graduate**, per #581 — a rule
-    refusing a *bare figure* was built and driven, and reported 20 on the live
-    briefs of which five were the defect: three wrong reports per right one, on
-    a corpus whose authors mostly did anchor. Write `58.6 % at 4b6e0765`.
-28. **A blank line ends a markdown table, and every row below it renders as
-    literal text while the source still looks like a table.** Not reduced to a
-    pointer, although its detector exists: the check catches the defect, and
-    what survives here is the method for settling a render question at all. 26 of the plan's
-    36 disposition rows were not in a table, for an unknown number of sessions,
-    in the most-read document here. Graduated: `policy_lint --record`'s
-    `table` check over both disposition documents. Ground truth for a render
-    question is GitHub's own `/markdown` endpoint, not the CommonMark spec —
-    how #686 established that a row's *leading* pipe is optional in GFM, so
-    deleting one is correctly not reported. The blank line is the defect.
-29. **A replacement that matches a prefix leaves both halves in one line, and
-    an anchor that matches the first occurrence lands your insertion in the
-    wrong section.** Both happened in one pull request. The row became five
-    cells wide in a three-column table with its old half still contradicting
-    the new one, and a governance-queue entry was appended under an earlier
-    heading of nearly the same name. Neither is visible to a check: `--record`
-    matches a number anywhere in its region and has no idea about placement.
-    Assert the *whole* construct you meant to replace, and anchor on a string
-    you have counted.
-30. **A verdict that does not parse loses its routing class, not just its text.**
-    `web-fix-wave.js`'s `VERDICT_RE` anchors on `^Fix review:`, reads only the
-    first line, and takes `<class>` from the closed `VERDICT_CLASSES` list — so
-    backticks around that line and an invented class both make the dispatcher
-    report no verdict on a pull request that has one, and the result is recorded
-    as an undifferentiated non-merge. The class is what dispatches a repair
-    round rather than a root-cause seat, so losing it costs the routing. Both
-    halves have fired: four of the fifteen grant merges were wrapped, and
-    `revise` — which is not a class — was written into every review brief and
-    cost six verdicts before it was caught. Post the first line bare, and read
-    the class list out of the file rather than from memory.
-31. **In zsh, assigning to a variable named `path` destroys `PATH`.** A
-    `while read -r path branch` loop over `git worktree list` left the shell
-    unable to find `basename`, `git` or `df`. Same reserved-variable family as
-    `GID`. Rename the loop variable.
-32. **A record's own fields are checked by almost nothing** (#687). An
-    unrecognised `resume.stage` is refused by `check-wave-script.mjs`, but a dead
-    path in `resume.note` is invisible to `brief_lint.mjs` while the same path in
-    `brief` is an error. A roster `resume` a record seat truths has one guarded
-    field and a reader for the rest.
-33. **A worktree shares the repository's config and its refs with every other
-    worktree.** A seat ran `git remote remove origin` inside one while building
-    a fixture; the main checkout's `origin` was repointed at a local path and
-    every remote-tracking ref went with it. A throwaway git experiment goes in a
-    standalone clone under the seat's own `mktemp -d`, never in a worktree here.
-34. **A detached worktree can be collected while a seat is still using it.**
-    `tools/audit/worktree_gc.sh --apply` removes a detached, clean worktree over
-    an hour old that is not an open pull request's head. A fix-review seat is
-    protected by that last criterion; a root-cause or audit seat detached at
-    `main` is not. **Claim it with `git worktree lock`**: `classify()` keeps
-    `locked` ahead of every criterion, as it does `main`, `current` and
-    `missing` — none named in its header, none pinned by a `--self-test` case.
-    **Not an untracked marker at the root**: criterion 2 keeps it, and
-    `closure.py select` then turns `MODE: SCOPED` into `MODE: FULL` naming it.
-35. **A coverage check can run a guard's line and pin nothing.** Four shapes
-    found by mutation across W5-G7, none visible to an instrument that sees the
-    line run either way. An EARLIER guard rejected the input (eight checks). The
-    exception ESCAPES and ends the script instead of failing the check named for
-    it (eleven; worst on an event-bus `@callback` whose helper swallows it). The
-    f-string DETAIL is eager, so a `sorted` over a mixed set aborts in place of
-    the failure. And the value the mutation leaves UNTOUCHED equals the asserted
-    one, so a push or a coercion is invisible when the constructed value already
-    agrees. **Only-arm inputs, a catcher on every call, details by `repr`, state
-    edited before the call.** And never assert EQUALITY against a production
-    structure: a second declaration cannot learn the original moved (#851).
-    Fifth shape: a mutant that cannot PARSE reports a pass, which here reads as
-    a finding about production. Assert it parses.
-36. **The leftover sweep reads part of a row; a stale row hides its state in
-    the rest.** #690's rule — the row's own verdict, quoted prose excluded —
-    applied literally reads the first `**…**` span. #678's row opened on its
-    root-cause verdict, carried `**IN REVIEW as #715**` later in that cell, and
-    ended `governance, in review` unbolded; it stood five days of record beats
-    after #715 merged. **The rule that holds both ends: in a table
-    row every cell, in a bullet the leading verdict, both dropping quoted and
-    backticked text first** — 12 table rows here before the repair, 0 after.
-    Without it the bullet arm fires on already-repaired prose, and #582's row
-    on its own leftover; **count those with your own vocabulary.**
-37. **A read-back that checks an id and a URL passes a body the API rewrote.**
-    PR #1058's provenance comment published a script whose field separator was
-    a JSON unicode escape for the unit separator; the API converted the escape
-    to the control character, so the published script was not the script that
-    ran — `identical=False`, 6505 bytes against 6508. The correcting paragraph
-    failed the same way, because describing the escape writes it; words, on the
-    third attempt, passed. Byte-identity against the sent file
-    (`comment-readback.md`) is the only read-back that fails all three.
-
-38. **A sectioned config-flow field resolves its label ONLY at
-    `step.<id>.sections.<s>.data.<field>` and `data_description`, with no
-    fallback to step level.** Every label check this repository had read the
-    step-level `data` map, which the HA frontend does not consult for a field
-    inside a `section()`; the fields rendered as raw keys — per language, in
-    both flows — from v6.3.19 (#653) and v6.4.1 (#849) until #1111 restored
-    them in v6.6.2. **The class is a check and the production code agreeing
-    about the wrong location**, so the check confirms the defect. Graduated:
-    the schema-derived, no-fallback assertion in `tests/entities.py`, which
-    walks the built schema rather than a hand-written key list. #1114 then
-    fixed the same blind read in seven audit harnesses under
-    `tools/audit/round3/` and `tools/audit/round4/`, none of which the gate had
-    ever contradicted.
-39. **`prepr.sh` gates `## Head` against the LOCAL head and `pr-contract` gates
-    the pull request's REMOTE tip, so a pull request that writes its own record
-    file must push twice and one `pr-contract` run necessarily fails on the
-    commit being replaced** (#1116). It is a red-then-green at a superseded
-    head, not a defect — `push.sh`'s `pr_arm` selects `body-then-push` once a
-    pull request is open, which is what orders the two. Read it with the
-    commit's `check-runs` API (correction above), and answer it in the body by
-    naming the superseded head rather than re-running anything.
-    **Instances: #1116, then #1121. This is a named recurrence at two, recorded
-    here so the next seat knows where it stands** — at a third,
-    `defect-root-cause.md`'s recurrence trigger fires and the answer is a
-    root-cause seat, not a third pull-request paragraph explaining the same red.
-    No countermeasure is proposed at two, and that is the decision rather than
-    an omission: a check that suppressed this red would have to stop reporting a
-    body genuinely stale at the head, which is what `pr-contract` is for, and
-    the gap itself exists only between two API calls that `push.sh`'s own header
-    says it cannot make atomic.
-40. **`policy_lint.mjs --budgets` exits 0 whatever it prints — it reports, and
-    never refuses.** Its handler is `if (has('--budgets')) return
-    cmdBudgets(files), process.exit(0)`, unconditional; the bare
-    `node tools/policy/policy_lint.mjs` is the path that refuses
-    (`process.exit(errors > 0 || rc ? 1 : 0)`). A mutation proof driven against
-    `--budgets` proves nothing (#1123): its own proof was driven against the
-    refusing bare form instead — appending two lines turned it rc=1, naming
-    both the touched file's cap and the corpus cap; restoring returned rc=0.
-41. **The test for whether a repair's invariant is true by construction, or
-    true only because the arm now asserts nothing, is to force the precondition
-    it relies on back to false and check the arm reddens.** #1115's `--record`
-    acceptance arm had asserted an invariant that held only where
-    `origin/main` is reachable from `HEAD`; under a shallow clone it
-    enumerated 611 merges and reddened. The repair made the window
-    `mainRef()..mainRef()`, empty by construction — and the decisive check was
-    not that the window is empty: reverting to `HEAD` inside the shallow clone
-    had to reproduce the original red, and deleting the `requireToken` call
-    had to redden the refusing arms (`FIXTURE VACUOUS`). Both did. Apply this
-    test to any repair that makes a window, a set or a diff empty by
-    construction, not only to this one.
-42. **A main-only ratchet red hides behind per-PR grading, and two such reds deadlock each other.** Per-PR grading reads each merge commit's own checks; a red that only exists on `main` — a `main` selftest, a `main`-grading ratchet — reddens every open pull request's required verdict while the pull request's own checks stay green, and no pull request can fix it alone. Round 9 paid this twice in one day: the closure lane-balance pin was unsatisfiable for every lane plan once #2142's re-record (`282054566`) put `boost_drift_replay.py` at 3379.1 s, more than half the 6059.1 s table total, against a `2*max(loads) < sum(loads)` pin with no escape arm (#2173 added the optimality second arm: a plan whose wall equals the heaviest indivisible script is provably optimal), and the `archscore.coord_footprint` row had grown to 2592 derived against a committed 2587 (#2118 grew it without re-recording). The two fixes then deadlocked — each pull request's merge commit lacked the other's fix, so neither required-context verdict could go green while both stayed open — resolved only by cherry-picking #2175's re-record verbatim onto #2173 as `4d6d329e5` and closing #2175 as superseded. The third re-record of the same class, `script_runs_*` 63 → 68, is #2179. And the mirror error: a required context with **no run at all** at a head is not green — it is "not yet" to any completion wait (#2170, #2171, `dev/audit/rca/R9-RCA-TRAIN-WEDGE.md`), and check-runs at merge tips may not exist during saturation, so "no runs" never reads as a conclusion.
-
-43. **A daemonized instrument with a silent log is not a dead instrument.** The wrapper's `dup2` makes stdout a file, Python block-buffers a file, and every heartbeat sat in the 8 KB buffer a SIGKILL dropped — an 8-minute healthy train (a FULL run in progress at main's tip) was read as dead and killed. #2180 (`d9e54b642`) kills the class with three one-liners: the entry reconfigures stdout line-buffered itself, batch and train announce tag/pid/base/queue as the log's first line before any blocking call, and the poll sleeps to the next beat (`HEARTBEAT_SECONDS`, not `POLL_SECONDS`) — before that, even unbuffered, the first beat was 305 s. Rehearse under the incident's exact wrapper shape before believing any launch fix.
-
-44. **Rate-limit 403s arrive disguised as red lanes and as missing runs.** At saturation the repository's `GITHUB_TOKEN` bucket — every workflow job's own token, not an App's (`dev/audit/rca/install-ratelimit.md`); Governance's `record` log prints its size and remainder on every push to main as `RATE_LIMIT before:`/`after:` — turns into arch-score/env-matrix/validate-hacs reds that are rate limits, not verdicts (#2168's body names its arch-score red as this class), and dropped workflow events leave required contexts with no run at the head. The fix is a **recarry** — a new merge commit at the live head re-fires the events, the verdict carrying via #2162's `--approval-carry` — not a rerun of the failed lane. The automated recovery is session-only and does not fire while turns are active; a manual recarry is the recovery.
-
-45. **A sibling merge silently reverts its sibling.** #2120's branch was cut before #2119 merged; on fold, main's side of a shared region carried the sibling's newer fix and the branch's side was empty — resolving to the branch would have reverted #2119 with no conflict and no red check — and the branch's structure-budget payment had lost its hunk to the sibling's newer comment on the same spot, so the honest re-record restores main's own value rather than raising anything. The countermeasure, executed at every fold that day (#2120 at `ab2307794`, #2066 at `2f3934468`): a silent-revert sweep over every shared file (0 of main's lines lost, named budget cells excepted) and a union-with-name-set proof for add/add conflicts in `tests/features.py` (0 of main's `R.check` names lost).
-
-46. **The recarry treadmill prices every queue move.** A queued pull request's verdict is carried to the live head by recarry; each move of `main` re-prices every queued entry. Merge fast after lanes conclude or main moves first. The working shape is the 2026-10-13T14:07Z cascade on #201: up-front recarries, admissions in queue order, machinery-touching heads held to a final pass that runs the fixed code.
-
-47. **`merge_pr.sh` stops on `UNSTABLE` when only an optional context is red**,
-    though every required context is green (#2465). `nightly-status` reports the
-    last scheduled run, not the pull request; read the required set from the
-    ruleset and merge at the exact head.
-48. **A `CANCELLED` required context is not a verdict.** A recarry supersedes the
-    run in flight; rerun it and read the conclusion (#2469, `Analyze (python)`).
-49. **No detached loop survives a host reboot.** At the 2026-10-21 takeover the
-    train, the tick loop, the state-docs beat and `wt_sync.sh` were all dead and
-    the train had stopped mid-queue; a resuming orchestrator restarts each from
-    the tree and re-reads the queue, never assumes a loop it did not start.
-50. **The deploy key's SSH on port 22 can time out from the stamping host.**
-    Route `github.com` to `ssh.github.com:443` in the SSH config and verify the
-    host key against GitHub's published fingerprints (v7.0.2's stamp).
-51. **`body_push.sh`'s predictor does not run the layout guard.**
-    `tools/pr/ci_predict.py` passed a head that `prepr.sh` then refused inside
-    `open_pr.sh` on `new-reference` (R10-HANDOVER-REFRESH's first handoff, a
-    retired path cited in prose). Before `body_push.sh`, run
-    `python3 -I tests/layout.py --guard --base $(git merge-base origin/main HEAD)`;
-    rc=0 and `0 refusal(s)` is the pass.
-52. **A cloud seat's container may not put the toolchain on `PATH`, and the
-    system `python3` cannot parse the suite.** Measure `python3 -V`: on 3.11
-    `tests/entities.py` fails on its own f-string before any check runs. Prepend
-    `/opt/hpo/venv-ci/bin` and run with `env -u BASH_ENV
-    PYTHONPATH=tests/hastub`. Through the agent proxy, `gh api --paginate`
-    follows GitHub's numeric-id `Link` URL and gets 403 after page one: loop
-    `?per_page=100&page=N` on the `repos/<owner>/<repo>` path instead.
+A trap that has acquired a mechanical detector is a one-line pointer to it:
+promotion, not cutting. The detector must fire when the trap would bite, in that trap's mode, and each
+graduation owes a mutation proof in its own pull request.
+
+- **A killed agent never writes its own `state at stop:` comment**, and a
+  subagent does not survive a session restart though its report does
+  (`tasks/<agentId>.output`; `ListAgents` goes empty without notice). On
+  resume walk the session's branches and open pull requests, post the owed
+  notes, and read the report before re-dispatching. **No detached loop survives
+  a host reboot** (train, tick loop, state-docs beat, `wt_sync.sh` were all dead
+  at one takeover): restart each from the tree and re-read the queue.
+- **A daemonized instrument with a silent log is not a dead one.** The
+  wrapper's `dup2` makes stdout a block-buffered file; an 8-minute healthy FULL
+  train was read as dead and killed. The entry now line-buffers and announces
+  itself first; rehearse a launch fix under the incident's exact wrapper.
+- **A stand-down note and a committed roster can disagree; origin is the
+  tiebreak**, the pull request's own comments. A roster's `resume.stage` and
+  `resume.branch` are a seat's claim: read the ref (`standing-dispatch.md`).
+- **A gate cannot be its own witness.** When the subject is the selection
+  machinery, the selection that runs is chosen by what is under test (#356).
+  A check whose failure is visible and one whose failure is blocking look
+  identical in a passing run.
+- **A figure from another artefact is not measured until you run the thing
+  that produced it**, and a figure in prose whose referent is a function of
+  `origin/main` is stale by construction: it was the largest source of blocked
+  rounds under the 2026-09-09 grant. Derive it (scrape `Fix review: blocked
+  <sha> <class>:`); `COUNT_RULES` in `tools/policy/counts.mjs` refuses
+  prose disagreeing with the artefact, `brief_lint.mjs` runs it over briefs.
+  A bare figure is not refused by a rule (a rule was built and reported three
+  wrong per right one): write `58.6 % at 4b6e0765`. The same rule: a body's
+  count of its own diff comes from the diff, by mutating the artefact and
+  reading the detector.
+- **A fix is verified against the instance demonstrated, not the property
+  stated.** The verification is built from the instance's form and a sibling
+  carrying the property in another form survives, including one the same
+  commit creates. `tools/pr/preflight.sh` catches none of the instances
+  measured (root-cause analysis over #531, #569, #591). A production fix is
+  accepted by standing property-quantified instruments; a record or policy
+  artifact has none, so a reviewer of one measures the property.
+- **A repair that makes a window, set or diff empty by construction passes for
+  the wrong reason.** Force the precondition back to false and check the arm
+  reddens (#1115: the window `mainRef()..mainRef()`; reverting to `HEAD` inside
+  a shallow clone had to reproduce the original red).
+- **A branch can be stale against main invisibly in its own diff**: a move
+  reverting a fix that landed inside the moved lines, or a stale claim or
+  budget table; and a citation and its referent can live on two branches with
+  nothing shared (`configuration_url`: a brief cited it, another branch deleted
+  its only occurrence, `main` went red). Only a three-dot comparison against
+  current `main` catches the first; `CLAUDE.md` rule 1's forced `full` push run
+  caught the second. **Prose is not a pin**: restoring the sentence would have
+  greened the gate and reproduced the defect, so re-anchor.
+- **A clean merge is evidence of no textual overlap and nothing else.** Two
+  sides appending at one insertion point shared a trailing bracket, and
+  `--ours` would have dropped a block silently; a sibling merge silently
+  reverts its sibling (#2120 was cut before #2119 merged, and its side of a
+  shared region was empty). Verify by parsing the result, sweeping every shared
+  file for main's lost lines (0 lost, named budget cells excepted) and, for
+  add/add conflicts in `tests/features.py`, proving the union keeps every `R.check` name of
+  main.
+- **A main-only ratchet red hides behind per-PR grading, and two such reds
+  deadlock each other.** A red that exists only on `main` reddens every open
+  pull request's required verdict while its own checks stay green, and no pull
+  request fixes it alone: round 9's closure lane-balance pin and
+  `archscore.coord_footprint` row each needed the other's re-record in their
+  merge commit. The resolution was cherry-picking one re-record verbatim onto
+  the other and closing the first as superseded (`dev/audit/rca/R9-RCA-TRAIN-WEDGE.md`).
+- **Rate-limit 403s arrive disguised as red lanes and missing runs.** At
+  saturation the repository's `GITHUB_TOKEN` bucket (`dev/audit/rca/install-ratelimit.md`;
+  Governance's `record` log prints `RATE_LIMIT before:`/`after:`) turns
+  arch-score, env-matrix and validate-hacs into reds that are not verdicts and
+  drops workflow events, leaving required contexts without a run. The fix is a
+  **recarry**, a new merge commit at the live head that re-fires the events
+  with the verdict carried (`--approval-carry`), not a rerun of the failed
+  lane. The automated recovery is session-only and does not fire while turns
+  are active. **The recarry treadmill prices every queue move**: each move of
+  `main` re-prices every queued entry; merge fast after lanes conclude, up-front
+  recarries, machinery-touching heads held to a final pass that runs the fixed
+  code.
+- **`merge_pr.sh` stops on `UNSTABLE` when only an optional context is red**
+  (#2465); `nightly-status` reports the last scheduled run, not the pull
+  request. Read the required set from the ruleset and merge at the exact head.
+- **"The pull request is open" is not a handoff.** The freeze starts at
+  handoff and only the orchestrator moves the head; a head moved under a live
+  review costs it (`orchestrator.md` section 7). A record pull request cannot
+  converge while the merge queue runs (#531 stayed open 20 hours over 31
+  merges), so one record per merge, and live state on #201.
+- **`prepr.sh` gates `## Head` against the LOCAL head and `pr-contract` gates
+  the REMOTE tip**, so a pull request that writes its own record file pushes
+  twice and one `pr-contract` run necessarily fails on the commit being
+  replaced (#1116, #1121). A red-then-green at a superseded head, answered in
+  the body by naming that head. **A named recurrence at two; at a third
+  `defect-root-cause.md`'s recurrence trigger fires and the answer is a
+  root-cause seat.** No countermeasure at two is the decision: a check
+  suppressing it would stop reporting a body genuinely stale at the head.
+- **`body_push.sh`'s predictor does not run the layout guard.**
+  `tools/pr/ci_predict.py` passed a head that `prepr.sh` then refused on
+  `new-reference` (a retired path cited in prose). Before `body_push.sh` run
+  `python3 -I tests/layout.py --guard --base $(git merge-base origin/main HEAD)`;
+  rc=0 and `0 refusal(s)` is the pass.
+- **`policy_lint.mjs --budgets` exits 0 whatever it prints**; the bare
+  `node tools/policy/policy_lint.mjs` refuses. A mutation proof driven against
+  `--budgets` proves nothing (#1123).
+- **A verdict that does not parse loses its routing class.** `web-fix-wave.js`'s
+  `VERDICT_RE` anchors on `^Fix review:`, reads the first line only and takes
+  `<class>` from the closed `VERDICT_CLASSES`: backticks around the line or an
+  invented class (`revise` is not one) make the dispatcher record an
+  undifferentiated non-merge. Post the first line bare; read the class list from
+  the file.
+- **A coverage check can run a guard's line and pin nothing.** Shapes found by
+  mutation: an earlier guard rejected the input, the exception escapes and ends
+  the script, an eager f-string detail aborts, the value the mutation leaves
+  untouched equals the asserted one, and a mutant that cannot parse reports a
+  pass. Assert the mutation's occurrence count before applying it (a control
+  reported NOT CAUGHT because the replacement hit a comment), use only-arm
+  inputs, and never assert equality against a production structure.
+  **A mutator restores only on a clean exit**: a harness killed by a timeout
+  leaves production mutated, so check `git status --porcelain` when you stop
+  one (`R10-FLY-MUTANT-RESTORE` owes the shared helper).
+- **A sectioned config-flow field resolves its label only at
+  `step.<id>.sections.<s>.data.<field>` and `data_description`**, with no
+  fallback to step level; every check had read the step-level map and confirmed
+  the defect (#1111 restored the labels). The class is a check and the
+  production code agreeing about the wrong location.
+- **A worktree shares the repository's config and refs with every other
+  worktree.** `git remote remove origin` inside one repointed the main
+  checkout. A throwaway git experiment goes in a standalone clone under
+  `mktemp -d`. `worktree_gc.sh --apply` collects a detached, clean worktree
+  over an hour old that is not an open pull request's head: claim a root-cause
+  or audit seat's with `git worktree lock`, not an untracked marker at the root
+  (`closure.py select` turns `MODE: SCOPED` into `MODE: FULL` naming it). The
+  main checkout stays clean; `handoff_push` runs `prepr`.
+- **A leftover sweep reads part of a row.** In a table row every cell, in a
+  bullet the leading verdict, both dropping quoted and backticked text first
+  (#690, #678). A blank line ends a markdown table; ground truth for a render
+  question is GitHub's `/markdown` endpoint.
+- **zsh**: assigning to a variable named `path` destroys `PATH`; `${PIPESTATUS}`
+  is empty (use `pipestatus`); `date -jf '%Y-%m-%dT%H:%M:%SZ'` parses UTC as
+  local, so compute ages with `datetime.fromisoformat` and an explicit UTC now;
+  backticks inside a double-quoted string are command substitution (write a
+  comment body to a file with a quoted heredoc and pass `--body-file`).
+- **A replacement that matches a prefix leaves both halves in one line, and an
+  anchor that matches the first occurrence lands an insertion in the wrong
+  section.** Assert the whole construct to be replaced and anchor on a string
+  you have counted.
+- **A comment bumps a pull request's `updated_at`**; the body-edit clock is the
+  `Governance` run list, which fires on `[edited]`.
+- **A record's own fields are checked by almost nothing** (#687): a dead path
+  in a roster `resume.note` is invisible to `brief_lint.mjs` while the same path
+  in `brief` is an error.
+- **Re-pointing a branch chain by position after a rebase drops a commit.** Map
+  by commit subject and verify the tip's pin count: by index once shifted eight
+  branches by one, and only that count noticed.
+- **Six of this project's own instruments reported rather than measured**
+  (#341, #347, #354, #350, #357, #510), each found by someone chasing something
+  else: the pattern is the finding, not the individual bugs.
+
+Graduated, one line each:
+
+- **One CI runner is not the fleet** (#387): `tools/policy/policy_lint_envmatrix.mjs`.
+- **The machinery a handover depends on is code nobody ran** (`.claude/` is
+  `INERT`): `tools/policy/check-wave-script.mjs` and `policy_lint --hooks`.
+- **A shallow checkout fails a driver on the clone, not the tree** (#901):
+  `tests/entities.py` refuses a history-reading driver at depth 1.
+- **A shallow clone turns "commits ahead" into fiction**:
+  `.claude/hooks/session-start.sh`.
+- **A one-sided cap and a growing document collide across branches** (#608,
+  #607): `policy-docs`'s `[budgets]`.
+- **A citation repointed to a commit that resolves but lacks the file is worse
+  than a dead one**: `policy_lint`'s `citations` for the corpus and rosters;
+  elsewhere `git cat-file -e <sha>:<path>`, not per directory.
+- **A blank line ends a markdown table**: `policy_lint --record`'s `table` check
+  over both disposition documents.
+- **A sectioned config-flow field's label**: the schema-derived, no-fallback
+  assertion in `tests/entities.py`, which walks the built schema.
+- **A new option key derives into `config_flow._ABSENT_FALLBACKS`**, or every
+  options-page visit writes it (#1107): `tests/config_flow_steps.py`'s
+  "_ABSENT_FALLBACKS is exactly the proven set".
 
 ## Owed
 
-**Post-hoc reviews from 2026-09-07.** #591, #592, #596, #602, #603, #605
-and #569 merged without an independent verdict at their final head (review
-capacity lost to a rate limit), and #606 with no review at all as a red-`main`
-repair; each squash body names where a reviewer starts. **#603** is policy whose
-approved form changed twice after approval; **#596** introduced
-`tests/typing_budgets.json`, the baseline every typing tranche ratchets against,
-which no reviewer has checked.
-
-**A finding for `dev/governance/roles/fixer.md`**, not landed because it is
-policy: a probe that builds its own input can build the complement of
-production's input (#591's seat).
-
-**From 2026-09-09, none decidable by a seat.**
-
-- Two one-clause policy edits carried out of #580: `fix-review.md` has no step
-  for an ABSENT check (a pull request whose workflows never queued shows no red),
-  and the mutation proof runs twice, fixer and reviewer, landing only in prose
-  where no later seat can re-run it. Both need a cap raise or a graduation.
-- `finding-propagation.md` holds a producing pull request until its carry is in
-  the tree, so two branches owing a carry to the same contract cannot both
-  comply under concurrency. Raised on #201; the owner breaks the tie.
-
-**The open-PR soft-cap instrument against the 2026-10-21 ruling.** `pr_cap.py
-gate` refuses any open at or over the cap; the ruling exempts an owed handoff.
-Until it distinguishes the two, the `--over-cap` reason above is the route.
-
-**An instrument over the plan's open-issue dispositions, or a decision not to
-build one.** `recordRegion` reads the plan's `## Delivery status`, the delivery
-rows and this file; `## Open friction issues — dispositions` is read by no
-check, while `delivery-status-tracking.md` obliges a disposition for every open
-issue. A detector must not disposition an issue by mere mention — the shape #658
-narrowed the region to escape.
-
-**A stale-pin sweep** (cited from `.github/workflows/codeql.yml`). #960
-SHA-pinned every mutable `uses:`; no lane reads a workflow ref for staleness, so
-an upstream fix arrives only when a seat re-pins deliberately.
-
-**`tools/policy/policy_lint_envmatrix.mjs`'s `okRef` row still drives
-`--record --since HEAD`** on the assumption that `HEAD..origin/main` is empty in
-its clone — the defect #1115 fixed for `--record`'s acceptance arm. For whoever
-next touches the env matrix.
-
-**`tests/typing_ruler.py`'s docstring still says the pinned toolchain is one
-"which no gate lane has"** (grep that phrase); #1122 established it false —
-`HPO_TYPING_PYTHON` re-execs the pinned mypy half through `run.sh`.
+- **Policy edits not landed because they are policy**: `fix-review.md` has no
+  step for an ABSENT check (a pull request whose workflows never queued shows
+  no red); the mutation proof runs twice, fixer and reviewer, landing only in
+  prose where no later seat can re-run it; `fixer.md` owes the finding that a
+  probe that builds its own input can build the complement of production's
+  (#591's seat); `standing-merge.md` still names `merge_pr.sh` for budget and
+  policy heads, which the owner's 2026-10-26 "no merge outside the train"
+  ruling supersedes. `finding-propagation.md` holds a producing pull request
+  until its carry is in the tree, so two branches owing a carry to the same
+  contract cannot both comply under concurrency (raised on #201). Each is the
+  orchestrator's under a mandate of scope `all`, with a verdict behind it.
+- **Post-hoc reviews from 2026-09-07**: #591, #592, #596, #602, #603, #605 and
+  #569 merged without an independent verdict at their final head (review
+  capacity lost to a rate limit), and #606 with none as a red-`main` repair.
+  **#603** is policy whose approved form changed twice after approval; **#596**
+  introduced `tests/typing_budgets.json`, the baseline every typing tranche
+  ratchets against, which no reviewer has checked.
+- **An instrument over the plan's open-issue dispositions, or a decision not to
+  build one.** `recordRegion` reads the plan's `## Delivery status`, the
+  delivery rows and this file; `## Open friction issues — dispositions` is read
+  by no check, while `delivery-status-tracking.md` obliges a disposition for
+  every open issue. A detector must not disposition an issue by mere mention,
+  the shape #658 narrowed the region to escape.
+- **A stale-pin sweep** (cited from `.github/workflows/codeql.yml`). #960
+  SHA-pinned every mutable `uses:`; no lane reads a workflow ref for staleness.
+- **`tools/policy/policy_lint_envmatrix.mjs`'s `okRef` row still drives
+  `--record --since HEAD`**, assuming `HEAD..origin/main` is empty in its
+  clone, the defect #1115 fixed for `--record`'s acceptance arm.
+- **`tests/typing_ruler.py`'s docstring still says the pinned toolchain is one
+  "which no gate lane has"** (grep that phrase); #1122 established it false:
+  `HPO_TYPING_PYTHON` re-execs the pinned mypy half through `run.sh`.
 
 ## The machine this runs on — measure it, do not read it
 
 A seat's box is not the owner's. Measure your own (`nproc`, `command -v gh`,
 `python3 -V`); `tests.yml` matrixes both declared interpreters, CI is the
-authority for the browser lane, and `git branch --show-current` beats trusting
-a path.
-
-**A 403 is not always the repository's answer.** "Resource not accessible by
-integration" is a token scope; "not permitted through this proxy" is the
+authority for the browser lane, and `git branch --show-current` beats trusting a
+path. **A 403 is not always the repository's answer**: "Resource not accessible
+by integration" is a token scope; "not permitted through this proxy" is the
 environment. Recording the second as the first sends a reader to change what was
 never the obstacle.
diff --git a/dev/programme/delivery/3074.md b/dev/programme/delivery/3074.md
new file mode 100644
index 000000000..53a3016a0
--- /dev/null
+++ b/dev/programme/delivery/3074.md
@@ -0,0 +1 @@
+- [#3074](https://github.com/tvofi/heatpump_optimizer/pull/3074) — **open**, record: dev/programme/HANDOVER.md rewritten at round-10 closing state (R10-HANDOVER-S9)

