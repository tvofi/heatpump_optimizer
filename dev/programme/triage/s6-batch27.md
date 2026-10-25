# Proposal triage, session s6, batch 27 (P140-P149)

Proposals from the s6 `proposals.md`. Numbering continues after `s6-batch26.md` (P127-P139). This batch holds 8-10 entries and merges only through the train queue (tvofi, 2026-10-25).

A roster op citing an ACCEPT below resolves only once this file is on the roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P140: `cloud_dispatch.py --group` renders the brief and drops the group's carries (S6-V61)
Verdict: ACCEPT -> R10-FLOW-DESIGN-STAGES (not-started; owns `tools/audit/seat/cloud_dispatch.py` and its dispatch templates). It rides with the cloud-payload stub that this group's carry (tvofi card 1, recommendation (c)) puts first, as its own sub-PR. Both change what `dispatch_group` writes into PROMPT.md, so one PR edits one function. R10-ORCH-DISPATCH-REG, which the filing names, owns only `bus.sh`. Its carry on `dispatch_group` concerns minting the PR and nonce, a separate seam.
Source: s6 `proposals.md` `## V61` (dispatch seat w34, confirmed by main).
Instances: read at origin/main dfcd8d9be. `dispatch_group` (`cloud_dispatch.py:257` onward) renders the prompt with `brief=group.get("brief") or ""` (line 283) and never reads `group["carry"]`. `_prompt` inlines only that brief (lines 167-168). The filing's line 362 is inside the self-test (`brief.write_text(grp["brief"])`); the production site is 283. The filing's per-group counts at roster 23b0a4cb are its own, except one I re-read: R10-FLOW-JIDOKA holds 21 carries. They are JIDOKA 21, ADVISOR-RESIDUE 9, CARD-VOICE 6, UPDATE-PR-SIGNALS 5 and DIAG-REDACT 3, every one dispatched without its carries. Until the fix lands, the dispatch seat renders the carries by hand.
Cost: S. In `dispatch_group`, render the brief, then `After: <groups>`, then every carry numbered. Add one self-test arm. Prompt size grows by the carry text, which reaches the trigger once the payload stub this group lands first replaces the inlined body with a pinned dispatch commit.
Binding: a fixer that never sees its carries cannot act on them (`finding-propagation.md`). The miss returns at review as a carry-missing or carry-not-implemented block. The fix is one function the destination group already rewrites. Closure saving: 0 h on the critical path (the filing's own figure). Off the path, each affected group avoids one blocked round, at the 1.70 h median carry-missing round trip measured by plan-opt (n=25).
Carry text (for `roster_edit.py append-carry R10-FLOW-DESIGN-STAGES`, citing `triage: dev/programme/triage/s6-batch27.md#P140`): "Render a group's carries in its dispatch. `dispatch_group` (`cloud_dispatch.py` line 283) passes only `group.get('brief')` to the prompt, so every group fixer dispatched with `--group` starts without its carries (2026-10-25: R10-FLOW-JIDOKA 21 carries, R10-ADVISOR-RESIDUE 9, R10-CARD-VOICE 6, R10-UPDATE-PR-SIGNALS 5, R10-DIAG-REDACT 3, re-rendered by hand). Render the brief, then `After: <after groups>`, then each carry numbered `Carry <i>:` with its text verbatim, into PROMPT.md. Land it in the same sub-PR as the payload stub that pins the dispatch commit, since both change what `dispatch_group` writes. Controls: a fixture group with two carries shows both, numbered, in PROMPT.md (null: a group with none renders the brief and `After:` alone); a host path inside a carry refuses as one in the brief does (line 384's check); one mutant that drops the carry loop fails the two-carry arm."

## P141: move `_plan_slots` out of `coordinator.py` (S6-V62)
Verdict: ACCEPT -> R10-ADVISOR-RESIDUE (not-started, M; files `price_tiles.py`, `coordinator.py`, `tests/features.py`; no after-edges, and the only open group after it is the round-closing R10-ARCH-DOCS). Its seam is how the plan's cost is presented. `_plan_slots` builds the published slot summaries (energy, average price and cost per heating slot), beside the price tiles the group already reworks. R10-ARCH-SHAPES, where the growth came from, is REJECTED as destination. A carry there keeps that group open after #2819 merges. Today `roster_lib.is_open` counts carries-open as open, and P133's narrower test has not landed, so R10-HEAT-METER would be held. HEAT-METER is ARCH-SHAPES' one code dependent and the critical path's next link.
Source: s6 `proposals.md` V62 (the orchestrator, 2026-10-25, from R10-ARCH-SHAPES #2819 round 2).
Instances: read at origin/main dfcd8d9be.
- `_plan_slots` is a `@staticmethod` on the coordinator (`coordinator.py:4304-4305`), so it reads no coordinator state. It turns a per-step power schedule into `PlanSlot` dicts.
- `PlanSlot` is the `TypedDict` in `payload.py:626`.
- Its callers are `coordinator.py:4477`, `4485`, `11234` and `11242`.
- The footprint figures (archscore `coord_footprint` 2446 at the merge base, 2436 at #2819's round 1, 2437 at its round 2, the +1 from a second heating mask) are the orchestrator's from #2819's review. I did not re-run archscore.
- `coord_footprint` is an archscore metric (`tools/audit/archscore/metrics/footprint.py`), not a `tests/structure_budgets.json` key.
Cost: S inside the group: move the pure function beside `PlanSlot` in `payload.py`, or into a small plan-view module if archscore reads that as sounder, and call it from the four sites. Measure archscore before and after.
Binding: a pure presentation function on the coordinator is footprint the architecture score counts against it, and the move is mechanical. The destination group already edits the same file without holding the critical path. Closure saving: 0 h. It pays architecture score; it does not move the schedule.
Carry text (for `roster_edit.py append-carry R10-ADVISOR-RESIDUE`, citing `triage: dev/programme/triage/s6-batch27.md#P141`): "Move `_plan_slots` out of `coordinator.py`. It is a `@staticmethod` (`coordinator.py:4304-4305`) that collapses a per-step power schedule into `PlanSlot` dicts (`payload.py:626`) and reads no coordinator state. Its callers are lines 4477, 4485, 11234 and 11242. Put it beside `PlanSlot` in `payload.py`, or in a small plan-view module if `tools/audit/archscore/` reads that as sounder, and keep the call sites' behaviour byte-identical. Source: R10-ARCH-SHAPES #2819 round 2 added a second heating mask and moved archscore `coord_footprint` 2436 -> 2437 against round 1 (2446 at the merge base); moving the function out is the payment, routed here because a follow-on on ARCH-SHAPES would hold R10-HEAT-METER (critical path) behind it. Controls: archscore `coord_footprint` before and after, with its null control (a whitespace-only move of the same function inside `coordinator.py` does not move the metric); the published `slots` lists of the fixture captures (`coordinator.py:4541`, the space plan, and `4558`, the hot-water plan) are byte-identical before and after; one mutant that drops `shared_kwh` from the moved function fails the capture comparison."

## P142: the train is the only path that lands delivery rows on main (S6-V63)
Verdict: ACCEPT narrowed -> R10-FLOW-RECORD-PITCH (S, roster not-started, but its fixer is running: `dispatch/fixer-r10-flow-record-pitch` 214ce7f56, `claim/s6/r10-flow-record-pitch`). The carry replaces the mechanism of the group's brief (the one-pitch automerge bound) and of carry 6 (the record-autofix batching threshold). It fulfils carry 7 (record PRs never merge under a running train) and keeps carry 8 (record PRs need no review verdict) and carry 2 (every merge keeps its row; only the merge time is batched). Carry 0 (close if the merge queue is adopted) is unchanged. The orchestrator must hand the running fixer this carry before its handoff. Narrowed in one respect, from what the tree shows:
- The train cannot write a commit to main itself. It merges only through `gh pr merge --merge --match-head-commit` (`merge_train.py:1071`, `:1765`).
- So "one commit inside the same batch" becomes the record pull request, merged by the train's existing `--bot-prs` sweep (`merge_train.py:1040-1071`) as an entry of a train and never between trains.
- record-autofix (`nightly.yml:541`) stops opening and auto-merging record pull requests. It only plans and pushes the record branch.

Source: s6 `proposals.md` `## V63` (orchestrator, 2026-10-25, tvofi-approved).
Instances: read at origin/main dfcd8d9be over the 48 h before it.
- 32 record merges (`Merge pull request #N from tvofi/record/...`) changed 137 row files under `dev/programme/delivery/`. 105 were modifications, the `**open**` to `**merged `sha`**` upgrade that `record_row.py` `_rewrite_granted` grants (`record_row.py:296-313`). 32 were additions: 31 were the record pull requests' own rows and 1 was a dependabot merge.
- No record merge in that window changed a file outside `dev/programme/delivery/`. The nightly's `ci: record nightly kills` commit (`nightly.yml:375`) has also ridden `record/autofix` (88744e573, in #2686), but its files were already on main by that merge.
- The train already refuses an entry with no delivery row in its three-dot diff (`ROW_MISSING`, `merge_train.py:568`, raised at `:1718` and `:2100`). So a train-merged pull request is never rowless.
- `tests/delivery_status.py` classifies a row on its presence, not its status word (`delivery-status-tracking.md`, "Status stays true"). OVERDUE counts only rowless merges, `STALE_AFTER_COMMITS = 12` (`delivery_status.py:111`).

So the record class is almost entirely self-generated: status-word upgrades, plus the rows of the record pull requests themselves.
Cost: S to M inside the group.
- In record-autofix, remove the open/automerge step and keep the plan and the push of `record/autofix`.
- In `merge_train.py`, at batch close, ensure the record pull request is open (opened as hpo-author, as record-autofix does today) and merge it as an entry of the next batch, or of this one if its checks are already green.
- Edit `dev/governance/rules/delivery-status-tracking.md`. "an immediate record PR" and "The record-autofix beat's own merges..." become "the train lands the record pull request". This is policy, approved under mandate 6329234399.
- Update `tests/entities.py`'s pin on the record-autofix review guard.
- Files added to the group: `tools/audit/seat/merge_train.py`, `.github/workflows/nightly.yml`, `dev/governance/rules/delivery-status-tracking.md`, `tests/entities.py`. `merge_train.py` is shared with R10-TRAIN-OVERLAP-GRADE, R10-FLOW-POSTMERGE and R10-FLY-GH-READ-RETRY. The seam here is the `--bot-prs` sweep and batch close only.

Binding: record merges were 31 of 104 merges in 48 h (plan-opt flow_metrics). Each one moves main under every open head (mean in-flight 10.4) and under a running batch (the `MAIN-MOVED` recovery, `merge_train.py:574-581`). The orchestrator reports that batch 5 ran about 1 h 45 min with 0 merges on that cause (#2811). Removing between-train record merges removes the record and delivery-status red class without a new rule.
Closure saving: about 3 h. Basis:
- about 7 critical-path groups remain (plan v47: ORCH-LEDGER .. CLOSEOUT);
- the measured after-merge round trip has a median of 1.45 h (n=51);
- record merges are about 30% of the main moves that cause those trips;
- 7 x 0.3 x 1.45 h = 3.0 h.

Carry text (for `roster_edit.py append-carry R10-FLOW-RECORD-PITCH`, citing `triage: dev/programme/triage/s6-batch27.md#P142`): "Train-only record landing (tvofi-approved V63; replaces the brief's pitch bound and carry 6's threshold; fulfils carry 7, keeps carries 2 and 8). (1) `.github/workflows/nightly.yml` record-autofix (line 541 on) keeps planning rows (`record_row.py --plan`) and pushing `record/autofix`, but never opens, approves or merges a record pull request. (2) `tools/audit/seat/merge_train.py`: at batch close, if `record/autofix` is ahead of main and no record pull request is open, open it as hpo-author with record_row's generated body. The existing `--bot-prs` sweep (lines 1040-1071) merges it as an entry of the next batch, or of the current one when its required checks are already green, never between trains. (3) Rows: only for merges the API reports, which `record_row.py`'s plan already guarantees; a nightly-kills commit on the same branch lands the same way. (4) Policy: `dev/governance/rules/delivery-status-tracking.md` replaces 'an immediate record PR' and the record-autofix automerge sentence with the train path; `tests/entities.py`'s pin on that guard follows. Controls: a batch where one entry is skipped writes no row for it (a mutant that rows a skipped PR fails); a null batch with nothing owed opens no record PR; the record PR never merges while no train runs (a fixture with the train stopped leaves it open); measure main pushes per merged PR and recarries per batch over 24 h before and after."

## P143: open the pull request on the handoff, with no seat in between (S6-V64)
Verdict: ACCEPT narrowed -> R10-FLY-OPENPR-ATOMIC (S, not-started, after R10-UPDATE-PR-SIGNALS). An open nobody watches has to be atomic first, and a failed open closing itself is this group's brief. The relay arm that calls it is a few lines beside that.

Narrowed: three parts of the filing already exist.
- The per-topic lock: `pr_branch_lock`, `pr_args.sh:66`, held by `open_pr.sh:34` and `update_pr.sh:35`. A second run exits 75 BUSY.
- The existing-PR update: `cloud_relay.sh` runs `update_pr.sh` when a handoff is ahead of its PR (header, lines 89-105).
- Reviewer dispatch at handoff is triage P134 (`s6-batch26.md#P134`) -> R10-ORCH-DISPATCH-REG.

What is missing is only the open. The relay records a `handoff/*` ref with no PR as `handoff-no-pr`, owed (`cloud_relay.sh:101-105`), and leaves it for a seat.
Source: s6 `proposals.md` `## V64` (orchestrator, 2026-10-25, tvofi-accepted idea 1).
Instances: the filing's five handoffs that waited up to 36 min on 2026-10-25, and the near double open (open4.sh beside the opener seat). plan-opt measured handoff-to-open at a median of 0.99 h and a mean of 2.54 h (card V53).
Cost: S. When `handoff-body/<topic>` exists at the handoff tip, the relay's handoff arm turns a `handoff-no-pr` topic into an `open_pr.sh` run under the same branch lock. The Closes list defaults to the roster group's `fixes` (this group's carry 7, P71). After the open, it runs the approve-held-runs and bus-dispatch steps it already runs after an update. Adds `tools/audit/seat/cloud_relay.sh` to the group's files. R10-FLOW-BODY-ONLY edits the update arm of the same file; the seam is the no-PR arm against the update arm.
Binding: the open is mechanical, and every step after it already runs unattended for an update. CI on the PR starts only at the open (PR run wall median 920 s).
Closure saving: about 2 h. Basis: per critical-path group, the open wait falls from a 0.99 h median to one relay pass. P134 already overlaps review with that wait, so only the CI start and the record of the open remain, about 0.3 h each across about 7 critical-path groups.

Carry text (for `roster_edit.py append-carry R10-FLY-OPENPR-ATOMIC`, citing `triage: dev/programme/triage/s6-batch27.md#P143`): "Auto-open on handoff (tvofi-accepted V64), built on this group's atomic open. In `tools/audit/seat/cloud_relay.sh`'s handoff arm, a `handoff-no-pr` topic (lines 101-105) whose `handoff-body/<topic>` ref exists runs `open_pr.sh` under the existing per-branch lock (`pr_branch_lock`, `pr_args.sh:66`; BUSY 75 is retried next pass), with the Closes list defaulted from the roster group's `fixes` (carry 7). On success it runs the same approve-held-runs and bus-dispatch steps the arm runs after an update. On a refusal it records `handoff-open-failed <topic> <sha>` and retries only when the handoff moves, as the update arm does. Seam: R10-FLOW-BODY-ONLY owns the update arm of the same file. Controls: a new topic with a body ref opens exactly one PR; a topic with an open PR takes `update_pr.sh`, never a second open; two concurrent passes open one PR (the second exits 75); a topic with no body ref stays `handoff-no-pr`; measure handoff-to-open latency before and after."

## P144: wake the orchestrator on each fire-owed line; a trigger-rights daemon is a round-11 design item (S6-V65)
Verdict: ACCEPT narrowed -> R10-FLOW-DESIGN-STAGES (M, not-started; owns `cloud_dispatch.py` and the reviewer pool arm, its carries 10 and 11). The daemon part is ruled a round-11 design item -> R10-ROUND-PLAYBOOK (its round-11 backlog).
- Narrowed because nothing in the tree calls the runner's trigger API. `cloud_dispatch.py` only renders the `job_config.ccr` payload that a trigger update takes (`cloud_dispatch.py:24-27`). Firing is the RemoteTrigger tool, reachable only from the orchestrator's own session (subagents lack it).
- A daemon with trigger rights would have to hold the owner's claude.ai credential outside a session. That is a credential decision, not a script.
- What can be built now without that: a waiter that blocks until a new `fire-owed` line lands in the dispatch report and then exits. The orchestrator runs it in the background, so its turn starts within seconds of the line instead of at the next sweep.

Source: s6 `proposals.md` `## V65` (orchestrator, 2026-10-25, tvofi-accepted idea 2).
Instances: about 15 cloud dispatches on 2026-10-25 waited for an orchestrator turn (filing). The dispatch report holds 447 lines, the latest `fire-owed-pool #2826`.
Cost: XS. A `fire_wait` subcommand on the pool module: it reads the report's last line number at start, prints the first new `fire-owed*` line and exits, with a timeout. It excludes its own process from any process match (memory trap: a `pgrep` waiter that matched itself).
Binding: the fire itself stays in the session that holds the right. Only the wait is removed.
Closure saving: about 1.5 h. Basis: about 7 critical-path groups x about 2.3 dispatches each (fixer plus 1.26 re-reviews at mean rounds 2.26) x about 6 min of wait removed = 1.6 h. Measure pool-to-fire latency before and after.

Carry text (for `roster_edit.py append-carry R10-FLOW-DESIGN-STAGES`, citing `triage: dev/programme/triage/s6-batch27.md#P144`): "Fire-owed waiter (tvofi-accepted V65, narrowed). Beside the pool module (carry 10), add a `fire-wait <report>` mode: record the report's line count at start, block until a new line beginning `fire-owed` is appended, print it and exit 0, or exit 3 at `--timeout`. The orchestrator runs it in the background and fires the line in its own session, which holds the RemoteTrigger right; no credential leaves the session. It must not match its own process. Controls: a line appended after start is printed once, while a line present before start is not; a non-fire line does not wake it; timeout exits 3; a mutant that reads from line 0 fails the first arm. Measure pool-to-fire latency before and after."
Carry text (for `roster_edit.py append-carry R10-ROUND-PLAYBOOK`, citing `triage: dev/programme/triage/s6-batch27.md#P144`): "Round-11 design item (tvofi-accepted V65): a local daemon with trigger rights that fires each `fire-owed` line once, idempotent by nonce, and logs it to the cloud-sessions table. Open questions for the design seat: which credential it holds, and how it is scoped and rotated (today the trigger right lives only in the orchestrator's session); the refusal for an unknown trigger id; duplicate-line idempotence. Not built in round 10; round 10 runs the fire-owed waiter on R10-FLOW-DESIGN-STAGES."

## P145: generate the round-2 and round-3 review briefs from the delta (S6-V72)
Verdict: ACCEPT -> R10-ORCH-REVIEW-PACKET (M, not-started, after R10-ORCH-DISPATCH-REG). The packet this group renders at the frozen head is the generated brief. A delta brief is the same packet, with three more parts:
- the reviewed head;
- the diff from it to the new head;
- the prior verdict's items, each to be checked.

Source: s6 `proposals.md` `## V72` (orchestrator, 2026-10-25, tvofi-accepted idea 10).
Instances: hand-written round-2/3 briefs for #2822, #2820, #2823 and #2819 (filing). Measured rounds per fix PR: mean 2.26 (plan-opt, n=110), so about 1.26 re-review briefs per PR.
Cost: S inside the group, on top of the packet:
- the prior verdict is the last `verdict/<N>` on the bus;
- its items are the block's numbered findings;
- the delta is `git diff <reviewed head>..<new head>`, plus the body diff when only the body moved.
Binding: the orchestrator writes each re-review brief by hand from the same three inputs, so a generator removes a wait and a class of omission (an unrechecked item).
Closure saving: about 1 h. Basis: about 1.26 re-reviews x about 0.2 h of brief writing x the about 4 critical-path groups that merge after this group lands = 1.0 h. The cost on the path is small because the packet module already exists by then.

Carry text (for `roster_edit.py append-carry R10-ORCH-REVIEW-PACKET`, citing `triage: dev/programme/triage/s6-batch27.md#P145`): "Delta packet for round 2 and later (tvofi-accepted V72). When `bus.sh dispatch` renders a reviewer packet for a PR that already has a verdict, the packet adds (a) the reviewed head from the last `verdict/<N>`; (b) `git diff <reviewed>..<new>` with its file list, or 'body-only' when the head is unchanged and only the body moved, then the body diff; (c) each numbered item of the prior block verdict, with a line for the reviewer to mark resolved or not; (d) any orchestrator ruling the new body cites by comment id. Controls: a body-only delta yields a body-only packet with no file list; a code delta lists exactly the changed files; a prior verdict with three items yields three check lines (a mutant that drops one fails); a first-round dispatch renders no delta section."

## P146: release ready groups by plan order, each sweep, without a hand step (S6-V71)
Verdict: ACCEPT -> R10-FLOW-DESIGN-STAGES (M, not-started; owns `cloud_dispatch.py --group`, `cloud_dispatch.py:606`, and the pool). The rendering it releases with is P140's.
- R10-ORCH-DISPATCH-REG's carry 5 makes the dispatch half of the standing dispatch seat a beat job. That job calls this release step, and does not own it. This keeps the step off the critical-path group.
- If this group's scope passes M with P140, P144, P146 and P149, its fixer cuts the release step as its own sub-PR, as P140 did.

Source: s6 `proposals.md` `## V71` (orchestrator, 2026-10-25, tvofi-accepted idea 9). Owner rule: dispatch in plan order, about a 12 h window (tvofi, 2026-10-25).
Instances:
- the filing: groups released by hand each sweep, once 21 at a time.
- `tools/plan/replan.py` already writes each group's planned `start` (`replan.py:517`).
Cost: S.
- A `release` mode reads the latest replan JSON and the roster's ready set (all after-groups done by `roster_lib.is_open`).
- It selects groups whose `start` is within the next 12 h, critical-path groups first, and any ready critical-path group regardless of window (owner rule).
- For each, it calls `cloud_dispatch.py --group` (or emits a local-seat line for a tagged group, P149), skipping one that already has a `dispatch/fixer-<topic>` ref.
Binding: the release rule is fully stated by the owner and the inputs are already measured, so a person adds nothing.
Closure saving: about 1 h. Basis: a ready group waits up to one sweep, about 0.25 h to 0.5 h, for a hand release. Over about 4 critical-path hand-offs that is about 1 h, and more off the path.

Carry text (for `roster_edit.py append-carry R10-FLOW-DESIGN-STAGES`, citing `triage: dev/programme/triage/s6-batch27.md#P146`): "Plan-order release (tvofi-accepted V71; owner rule: dispatch in plan order, about 12 h window). A `release` mode: read the latest `tools/plan/replan.py` output (`start` per group, line 517) and the roster's ready set (every after-group not open by `roster_lib.is_open`). Release each ready group whose `start` is within 12 h of now, critical-path first, and every ready critical-path group regardless of window, through `cloud_dispatch.py --group`, rendering carries (P140). Skip a group that already has a `dispatch/fixer-<topic>` ref, and route a capability-tagged group to a local-seat line (P149). R10-ORCH-DISPATCH-REG's beat job calls it; it does not own it. Controls: a ready group starting in 13 h is not released; a ready critical-path group starting in 30 h is; a group with a dispatch ref is not re-released (a mutant that drops that check double-dispatches the fixture); a not-ready group in the window is not released."

## P147: standing rulings go into the contracts they bind (S6-V70)
Verdict: ACCEPT narrowed -> new group R10-STANDING-RULINGS (XS, policy, no after-edges; files `dev/governance/roles/fixer.md`, `dev/governance/roles/fix-review.md`).
- Narrowed in one respect: no separate rulings file. A rulings file beside the role contracts is a second source a reader must reconcile against them. CLAUDE.md names that as a defect when it explains why `SEAT-BLOCK.md` is renamed out of `COMMON.md`'s basename.
- Each recurring ruling that binds a fixer or a reviewer goes into that contract as one numbered line, with the mandate and the date.
- The filing's third example, early release following P133's touched-files test, is code (`roster_lib.is_open`, `roster_lib.py:205-206`; R10-ORCH-ROSTER-SCHEMA carry 16), not a sentence a seat reads, so it is excluded.
- R10-ROUND-PLAYBOOK, which writes the round-11 playbook, cites these lines and does not copy them.

Source: s6 `proposals.md` `## V70` (orchestrator, 2026-10-25, tvofi-accepted idea 8).
Instances: the filing (several round trips on 2026-10-25 asked questions with known answers). The rulings it names:
- out-of-seam hunks accepted when the class closure needs them and the body names them;
- a budget or archscore delta judged against the merge base.

Cost: XS. Two to four lines in each of the two contracts, paid by cutting text elsewhere in the same file under the policy caps (`ratchet-budgets.md`). A policy edit, approved under mandate 6329234399.
Binding: a seat that reads its contract needs no round trip for a ruling the contract states. Writing the ruling into the contract is cheaper than a second file every seat must also read.
Closure saving: about 1 h. Estimated, not measured: a few avoided seat round trips, at the 1.45 h to 2.35 h medians, on the remaining critical path.

New group (for `roster_edit.py append-group`, citing `triage: dev/programme/triage/s6-batch27.md#P147`): R10-STANDING-RULINGS, lane RP, kind policy, class policy, severity medium, size XS, files `dev/governance/roles/fixer.md` and `dev/governance/roles/fix-review.md`, after none, fixer and reviewer opus at medium effort. Brief: "GROUP R10-STANDING-RULINGS (new, size XS, triage: dev/programme/triage/s6-batch27.md#P147; tvofi-accepted V70, narrowed to the contracts). Write each standing ruling the orchestrator has given more than once, that binds a fixer or a fix reviewer, into `dev/governance/roles/fixer.md` or `fix-review.md` as one numbered line carrying the mandate id and the date: (1) an out-of-seam hunk is accepted when the class closure requires it and the body names it and why; (2) a structural-budget or archscore delta is judged against the merge base, never against main's tip. Add any further ruling the orchestrator lists at dispatch, each with its source comment id. Pay each line by cutting text in the same file under the policy caps. Do not create a separate rulings file. Controls: policy_lint and the policy caps pass at the head; each new line cites a comment id that resolves; a seat brief citing the ruling resolves under brief_lint." Seam: R10-ORCH-REVIEW-PACKET also edits `fix-review.md` (its step text). This group touches only the rulings lines.

## P148: detached scripts for the mechanical loops; the merge seat's part is R10-FLOW-POSTMERGE (S6-V68)
Verdict: ACCEPT -> R10-FLOW-POSTMERGE (S, not-started; its only after-group, R10-ROSTER-OPS, is done, so it is dispatchable now). Every other loop the filing names is already carried, and this ruling adds nothing to them:
- the relay is a script (`cloud_relay.sh` pass);
- the tick runs detached: triage P136 (a) -> R10-ORCH-DISPATCH-REG, with the seat retired by R10-ORCH-BEATD carry 10;
- roster application becomes a beat job (R10-ORCH-BEATD carry 22);
- the dispatch half is R10-ORCH-DISPATCH-REG carry 5;
- the train runs detached (`train.sh` under `daemonize.py`, `standing-merge.md`).

What the merge seat still does by hand after each merge is FLOW-POSTMERGE's brief: the #201 line, the roster stage and `state_docs.py --push`, with the merged-issue check after. What it lacks is the contract edit that retires those steps from the seat once both merge paths run them.
Source: s6 `proposals.md` `## V68` (orchestrator, 2026-10-25, tvofi-accepted idea 6).
Instances: the filing (a merge-seat watcher crashed on a JSON parse, and seats need a 2 h refresh). plan-opt: standing seats were 66% of local token reads over 32 h.
Cost: XS on top of the group: one paragraph cut from `dev/governance/roles/standing-merge.md`, as carry 3 already does for `nudge.md` step 12. Adds that file to the group's files.
Binding: the merge seat then only launches the train and reports parked entries. Decisions such as a SKIP reason wake it; mechanics do not.
Closure saving: about 0.5 h. Basis: avoided seat restarts and missed post-merge steps. It is off the critical path but frees the merge path.

Carry text (for `roster_edit.py append-carry R10-FLOW-POSTMERGE`, citing `triage: dev/programme/triage/s6-batch27.md#P148`): "Once both merge paths run the after-merge steps (this group's brief), shrink `dev/governance/roles/standing-merge.md` to what is left by hand: launching the train on the orchestrator's queue lines, and reporting `parked #<n> <reason>` or an OWED post-merge step. Remove the after-merge steps the paths now run (state_docs push, `set-stage owed`, the #201 line), as carry 3 does for `nudge.md` step 12 (tvofi-accepted V68: mechanical loops are scripts, and agents wake only for decisions). Controls: policy_lint and the caps pass; every step the edit removes is named in the dry-run fixture as run by `merge_pr.sh` and by `merge_train.py`."

## P149: capability tags on roster groups (S6-V69)
Verdict: ACCEPT -> R10-ORCH-ROSTER-SCHEMA (M, not-started) for the field and its op, and -> R10-FLOW-DESIGN-STAGES for the cloud refusal. The schema is ROSTER-SCHEMA's seam (`roster_edit.py` validates group fields at `append-group`, lines 233-248). The render is FLOW-DESIGN-STAGES' (`cloud_dispatch.py --group`, line 606).
Source: s6 `proposals.md` `## V69` (orchestrator, 2026-10-25, tvofi-accepted idea 7).
Instances: R10-FLOW-MQ-PROBE was rendered for a cloud seat with no admin token and returned blocked (filing). No group carries a capability field today: the roster's group keys are group, lane, kind, issues, fixes, findings, class, severity, size, wave, files, hot_files, the model fields, effort, fixture, owner_gate, rca, after, carry, architect_note, resume and brief.
Cost: XS + XS.
- An optional `needs` list from a fixed vocabulary (`admin-api`, `local-tooling`, `owner-credential`), validated by `append-group`, with a `set-needs` op.
- `cloud_dispatch.py --group` refuses a group whose `needs` is not empty, naming the tag.
Binding: one instance cost a full cloud fixer run and a re-dispatch. The tag makes the routing a reading, not a recollection.
Closure saving: about 0.5 h (one avoided wasted dispatch on the remaining plan, estimated).

Carry text (for `roster_edit.py append-carry R10-ORCH-ROSTER-SCHEMA`, citing `triage: dev/programme/triage/s6-batch27.md#P149`): "Capability tags (tvofi-accepted V69). Optional group field `needs`: a list from a fixed vocabulary (`admin-api`, `local-tooling`, `owner-credential`), validated by `append-group` (`roster_edit.py` lines 233-248) and settable by a new `set-needs <group> <t1,...|->` op; `roster_sync.py`'s self-test knows the field. Tag R10-FLOW-MQ-PROBE `admin-api` once the op lands. Controls: an unknown tag refuses; `set-needs G -` clears; a mutant that skips vocabulary validation fails the unknown-tag arm."
Carry text (for `roster_edit.py append-carry R10-FLOW-DESIGN-STAGES`, citing `triage: dev/programme/triage/s6-batch27.md#P149`): "Capability refusal at render (tvofi-accepted V69, with R10-ORCH-ROSTER-SCHEMA's `needs` field). `cloud_dispatch.py --group G` refuses when G's `needs` is non-empty, printing `REFUSE: G needs <tags>; dispatch a local seat`, and the plan-order release (P146) emits a local-seat line for such a group instead. Controls: a tagged fixture group refuses a cloud render (exit non-zero, no dispatch ref written); an untagged group renders unchanged (null); a mutant that ignores `needs` fails the first arm."
