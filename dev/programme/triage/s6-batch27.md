# Proposal triage, session s6, batch 27 (P140-P149)

Round-1 re-cut (verdict 6402367085, 2026-10-25): an unmeasured benefit is DEFER, never ACCEPT (`proposal-triage.md`). P142 and P145-P149 are re-ruled DEFER, each naming the measurement that would change the answer. P144 keeps its waiter as a trial against a measured tail, and its daemon arm is DEFER. P141 is re-routed behind its destination's handoff.

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
Verdict: ACCEPT -> R10-ADVISOR-RESIDUE, as a second sub-PR after the group's handoff (round-1 re-cut, verdict 6402367085 item 4). The group's fixer handed off `handoff/r10-advisor-residue` 367afeb85 at 18:22:34Z, and `handoff-body/r10-advisor-residue` followed, before this ruling, so the move does not ride that frozen head. It is owed as the group's follow-on sub-PR, and the group stays open until it lands. That costs nothing on the critical path: the only open group after R10-ADVISOR-RESIDUE is the round-closing R10-ARCH-DOCS. Its seam is how the plan's cost is presented. `_plan_slots` builds the published slot summaries (energy, average price and cost per heating slot), beside the price tiles the group reworks. R10-ARCH-SHAPES, where the growth came from, is REJECTED as destination: a carry there would keep it open after #2819 merges, and `roster_lib.is_open` counts carries-open as open, which would hold R10-HEAT-METER, the critical path's next link.
Source: s6 `proposals.md` V62 (the orchestrator, 2026-10-25, from R10-ARCH-SHAPES #2819 round 2).
Instances: read at origin/main dfcd8d9be.
- `_plan_slots` is a `@staticmethod` on the coordinator (`coordinator.py:4304-4305`), so it reads no coordinator state. It turns a per-step power schedule into `PlanSlot` dicts.
- `PlanSlot` is the `TypedDict` in `payload.py:626`.
- Its callers are `coordinator.py:4477`, `4485`, `11234` and `11242`.
- The footprint figures (archscore `coord_footprint` 2446 at the merge base, 2436 at #2819's round 1, 2437 at its round 2, the +1 from a second heating mask) are the orchestrator's from #2819's review. I did not re-run archscore.
- `coord_footprint` is an archscore metric (`tools/audit/archscore/metrics/footprint.py`), not a `tests/structure_budgets.json` key.
Cost: S inside the group: move the pure function beside `PlanSlot` in `payload.py`, or into a small plan-view module if archscore reads that as sounder, and call it from the four sites. Measure archscore before and after.
Binding: a pure presentation function on the coordinator is footprint the architecture score counts against it, and the move is mechanical. The destination group already edits the same file without holding the critical path. Closure saving: 0 h. It pays architecture score; it does not move the schedule.
Carry text (for `roster_edit.py append-carry R10-ADVISOR-RESIDUE`, citing `triage: dev/programme/triage/s6-batch27.md#P141`): "Follow-on sub-PR, after the handoff 367afeb85 merges (not part of that head): move `_plan_slots` out of `coordinator.py`. It is a `@staticmethod` (`coordinator.py:4304-4305`) that collapses a per-step power schedule into `PlanSlot` dicts (`payload.py:626`) and reads no coordinator state. Its callers are lines 4477, 4485, 11234 and 11242. Put it beside `PlanSlot` in `payload.py`, or in a small plan-view module if `tools/audit/archscore/` reads that as sounder, and keep the call sites' behaviour byte-identical. Source: R10-ARCH-SHAPES #2819 round 2 added a second heating mask and moved archscore `coord_footprint` 2436 -> 2437 against round 1 (2446 at the merge base); moving the function out is the payment, routed here because a follow-on on ARCH-SHAPES would hold R10-HEAT-METER (critical path) behind it. Controls: archscore `coord_footprint` before and after, with its null control (a whitespace-only move of the same function inside `coordinator.py` does not move the metric); the published `slots` lists of the fixture captures (`coordinator.py:4541`, the space plan, and `4558`, the hot-water plan) are byte-identical before and after; one mutant that drops `shared_kwh` from the moved function fails the capture comparison."

## P142: the train is the only path that lands delivery rows on main (S6-V63)
Verdict: DEFER -> R10-FLOW-RECORD-PITCH's handoff c24adf589 owns the record cadence. What would change the answer is the record merges per 24 h left after that handoff merges, together with the price of a train-less day under `stamp.py`'s rule 5. (Round-1 re-cut, verdict 6402367085 item 1; it replaces the earlier ACCEPT, which nothing has routed.)
- The fixer handed off `handoff/r10-flow-record-pitch` c24adf589 at 19:10:43Z and `handoff-body/r10-flow-record-pitch` 852abf936 at 19:27:13Z. The handoff builds the brief's pitch bound and carry 6's batching (floor 8 rows), which is the mechanism the earlier ruling would have replaced.
- Its body weighs the train-only design and rejects it on a cost this ruling had not answered. A day with no train, and the stamp, would leave rows unmerged, and `stamp.py`'s rule 5 (the `# Rule 5: the window` arm, `stamp.py:1254`) refuses those.
- The measured basis, record merges as a share of main moves, is the pre-batching regime. Once the handoff merges, batching at a floor of 8 rows cuts that share. The train-only increment over the handoff is therefore unmeasured.
- So R10-FLOW-RECORD-PITCH's review of c24adf589 is not bound by any triage carry from this batch.

Source: s6 `proposals.md` `## V63` (orchestrator, 2026-10-25, tvofi-approved).
Instances: in the 48 h before dfcd8d9be, 31 of 107 first-parent merges were record merges. Command: `T=$(git log -1 --format=%ct dfcd8d9be); git log --first-parent --format='%ct %s' dfcd8d9be | awk -v s=$((T-172800)) '$1>=s' | grep -c ' Merge pull request #[0-9]* from tvofi/record/'` gives 31, and the same pipe ending in `grep -c ' Merge pull request #'` gives 107. Those 31 merges changed 137 row files: 105 status upgrades and 32 additions, 31 of them the record PRs' own rows. No record merge changed a file outside `dev/programme/delivery/`.
Cost: S to M if built (the `merge_train.py` batch close and `--bot-prs` sweep, record-autofix in `nightly.yml`, and a `delivery-status-tracking.md` edit), plus a path for the stamp on a train-less day.
Binding: the destination already handed off a different, cheaper mechanism, and the increment over it is unmeasured. Re-measure record merges per 24 h, and the recarries they caused, over the first 24 h after the record-pitch PR merges. If record merges between trains still cost a measurable share of recarries, re-file V63 with that figure and the rule-5 path.

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

## P144: wake the orchestrator on each fire-owed line, as a trial; the trigger-rights daemon is DEFER (S6-V65)
Verdict: ACCEPT as a trial -> R10-FLOW-DESIGN-STAGES (M, not-started; owns `cloud_dispatch.py` and the reviewer pool arm, its carries 10 and 11). The waiter is XS and is judged by a named measurement with a removal criterion. The trigger-rights daemon is DEFER. Nothing in the tree calls the runner's trigger API: `cloud_dispatch.py` only renders the `job_config.ccr` payload a trigger update takes (`cloud_dispatch.py:24-27`). A daemon would have to hold the owner's claude.ai credential outside a session, and its benefit is unmeasured. It is re-filed if the trial shows the tail is the orchestrator's turn and the waiter does not close it.
Source: s6 `proposals.md` `## V65` (orchestrator, 2026-10-25, tvofi-accepted idea 2).
Instances (round-1 re-cut, verdict 6402367085): pool-to-fire latency, measured from two in-tree-adjacent records.
- The method: each `dispatch/reviewer-<pr>-<sha8>` ref's commit time (`git for-each-ref --format='%(refname) %(committerdate:unix)'` over the fetched `refs/heads/dispatch/reviewer-*`, 187 refs) is matched to the first reviewer line in the orchestrator's `cloud-sessions.tsv` that names that PR at or after it.
- 25 of 180 dispatch refs matched. The other lines name a pool, not a PR, so this is a sample, not the population.
- Of the 25, 20 fired within 5 min (median 1.1 min). 5 waited 22.5, 61.9, 90.7, 148.4 and 166.1 min, the last two on critical-path #2819.
- The logs do not say whether those waits were the orchestrator's turn or something else.

Cost: XS. A `fire-wait` mode on the pool module: it records the report's line count, blocks until a new `fire-owed` line appears, prints it and exits, with a timeout. It must not match its own process.
Binding: a 5-of-25 tail of 22 to 166 min is worth an XS trial, and only a trial attributes it. The trial is judged on the same measurement for the 24 h after the waiter runs. If the share of dispatches waiting over 5 min does not fall, the waiter is removed and V65 is closed. Closure saving: not claimed until the trial measures it.

Carry text (for `roster_edit.py append-carry R10-FLOW-DESIGN-STAGES`, citing `triage: dev/programme/triage/s6-batch27.md#P144`): "Trial: fire-owed waiter (V65, triage P144). Beside the pool module (carry 10), add a `fire-wait <report>` mode: record the report's line count at start, block until a new line beginning `fire-owed` is appended, print it and exit 0, or exit 3 at `--timeout`. The orchestrator runs it in the background and fires the line in its own session, so no credential leaves the session. It must not match its own process. Judge it on pool-to-fire latency (dispatch/reviewer ref commit time to the matching cloud-sessions.tsv fire line) for the 24 h after it runs, against the 2026-10-25 sample: 20 of 25 within 5 min, 5 waiting 22-166 min. If the share over 5 min does not fall, remove it. Controls: a line appended after start is printed once, while a line present before start is not; a non-fire line does not wake it; timeout exits 3; a mutant that reads from line 0 fails the first arm."

## P145: generate the round-2 and round-3 review briefs from the delta (S6-V72)
Verdict: DEFER -> R10-ORCH-REVIEW-PACKET owns the packet a delta brief would extend. What would change the answer is the measured wait from a blocked verdict to the next reviewer dispatch for the same PR, which hand-writing the brief is said to lengthen. (Round-1 re-cut: the earlier ACCEPT asserted 0.2 h per brief without a measurement.)
Source: s6 `proposals.md` `## V72` (orchestrator, 2026-10-25, tvofi-accepted idea 10).
Instances: four hand-written round-2 or round-3 briefs (#2822, #2820, #2823, #2819), from the filing. No time per brief is recorded.
Cost: S inside the group once the packet exists.
Binding: the measurement is cheap and should come first: for each PR with two or more `dispatch/reviewer-<pr>-*` refs, take the blocked verdict comment's `created_at` to the next dispatch ref's commit time. Re-file with that median and its count.

## P146: release ready groups by plan order, each sweep, without a hand step (S6-V71)
Verdict: DEFER -> the release stays the orchestrator's sweep step under the owner rule (dispatch in plan order, about a 12 h window). What would change the answer is the measured lag from "ready" to dispatch. (Round-1 re-cut: the earlier ACCEPT asserted a 0.25-0.5 h wait per release.)
Source: s6 `proposals.md` `## V71` (orchestrator, 2026-10-25, tvofi-accepted idea 9).
Instances: one, from the filing: a hand release of 21 groups at once. `tools/plan/replan.py:517` writes each group's planned `start`, so the input exists.
Cost: S (a release mode reading the replan output and the roster's ready set, calling `cloud_dispatch.py --group`).
Binding: the lag is measurable from git: per group, take the merge time of its last after-group to its `dispatch/fixer-<topic>` ref's commit time. Re-file with the median lag of critical-path groups and its count.

## P147: standing rulings go into the contracts they bind (S6-V70)
Verdict: DEFER. What would change the answer is the count of seat round trips that asked a ruling already given, each by comment id, with their measured round-trip time. (Round-1 re-cut, verdict 6402367085 item 2: the earlier ACCEPT stated its own benefit as "estimated, not measured".)
Source: s6 `proposals.md` `## V70` (orchestrator, 2026-10-25, tvofi-accepted idea 8).
Instances: none counted. The filing says "several round trips on 2026-10-25" without ids.
Cost: XS if built: one numbered line per ruling in `fixer.md` or `fix-review.md`, with the mandate id and the date, paid by cuts under the policy caps. A separate rulings file is not the form: a second source beside the contracts is the defect CLAUDE.md names for `SEAT-BLOCK.md`.
Binding: no count, no benefit. Re-file with the ids.

## P148: detached scripts for the mechanical loops (S6-V68)
Verdict: DEFER -> owned by the groups that already carry each loop. Tick: triage P136 (a) and R10-ORCH-BEATD carry 10. Roster application: R10-ORCH-BEATD carry 22. The dispatch half: R10-ORCH-DISPATCH-REG carry 5. The merge seat's after-merge steps: R10-FLOW-POSTMERGE's brief. The relay is already a script (`cloud_relay.sh`). (Round-1 re-cut, verdict 6402367085 item 6: the earlier ACCEPT added a `standing-merge.md` cut on an unmeasured 0.5 h.)
Source: s6 `proposals.md` `## V68` (orchestrator, 2026-10-25, tvofi-accepted idea 6).
Instances: the filing names one merge-seat watcher crash on a JSON parse. The 66% standing-seat token share (plan-opt) does not isolate the merge seat.
Cost: none new. The contract cut follows R10-FLOW-POSTMERGE's own steps, if its reviewer finds the contract stale.
Binding: every loop already has an owner. A further `standing-merge.md` edit is re-filed only with the merge seat's restarts and missed post-merge steps counted from the tick log.

## P149: capability tags on roster groups (S6-V69)
Verdict: DEFER. What would change the answer is a live group that needs a capability a cloud seat lacks, named with its cost. (Round-1 re-cut, verdict 6402367085 item 3.)
Source: s6 `proposals.md` `## V69` (orchestrator, 2026-10-25, tvofi-accepted idea 7).
Instances: one, R10-FLOW-MQ-PROBE (cloud seat without an admin token), and that group is now `done` (#2826 closed: merge queue infeasible). The reviewer's grep of the roster at 32ffe43c0 finds no live group whose brief or carries name an admin token.
Cost: XS + XS if built (a `needs` field with a `set-needs` op in `roster_edit.py`, and a refusal in `cloud_dispatch.py --group`).
Binding: the only instance is closed. Re-file when a live group needs it.
