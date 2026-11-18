# Proposal triage, session s7, batch 49 (P237-P247)

Eleven entries, V151-V161, filed by the orchestrator s10 on 2026-10-28. V151-V160 were approved
by the owner on decision cards (V155 is in the owner's own words). V161 was filed by a fixer. They are quoted from `proposals.md` as it
stands. The owner's correction of the same day governs the bar: "triage should still do
cost/benefit and is allowed to reject poor proposals". Owner approval makes a proposal worth
triaging; it does not exempt it from `proposal-triage.md`.

Facts were read at origin/main `6d86acc909f7fc465e5736771daf8fa45c1373a4` and at the live roster,
`origin/handoff/audit-r10-roster` `8c57b43dded6bc3ebab94b9a217d72b344ad7564`. The plan is the one
the proposals cite: `plan.json`, generated 2026-10-28T09:37Z from that roster ref, 128.97 h, closing
2026-11-02T18:35Z. Each replan figure below is `python3 tools/plan/replan.py --roster-ref <ref>`
or `--roster-file <counterfactual>` with `--start 2026-10-28T09:37:00Z`. A counterfactual roster
changes only the field named.

Three measurements decide most of these rulings:
- **The plan's chain is not CP-bound.** In the plan itself, R10-FLOW-TOOLKIT-MODEL finishes at
  10-31T01:36Z and R10-ARCH-DOCS starts at 11-01T16:54Z, so the CP has **39.3 h of slack**. ARCH-DOCS
  waits on R10-REPLAY-REAL-DAY (finish 11-01T16:54Z), a non-CP group the six slots delay.
- **Seats do not move closure; slots move it.** `--slots 6` gives 128.97 h at `--seats` 7, 14 and 20
  alike. `--slots 7` gives 110.57 h, `--slots 10` 82.2 h and `--slots 14` 76.1 h (seats 14-20).
- **The slot model is not borne out by history.** Over 7 days, 27 roster snapshots 6 h apart
  (`git rev-list -1 --before="<t> hours ago" origin/handoff/audit-r10-roster`) give groups live
  (in-progress, fixing, review, in-review) against groups done or absorbed 12 h later. The
  correlation is r = 0.045, with a slope of 0.054 groups per 12 h per live group. Windows at WIP
  ≤ 6 closed a mean of 8.2 groups per 12 h (n = 5); windows at WIP ≥ 9 closed 7.67 (n = 15). WIP
  ranged from 6 to 20, so the cap of 6 was routinely exceeded and throughput did not follow.
  Caveat: roster stages lag pull requests; stage derivation from pull requests landed only
  recently (`roster_sync.py`).

## P237: start the R10-ORCH-PLANPAGE and R10-FLOW-TOOLKIT-MODEL designers now, against R10-ORCH-BEATD's current note

Verdict: REJECT. The mechanism does not exist, and the benefit the plan prices is zero.
- **No designer exists for these groups.** `dev/governance/roles/designer.md` lines 7-8 apply
  the designer to "every roster group of size L or XL"; "Any other group goes straight to its
  fixer". Both groups are size M on the live roster, so "start the designers" starts nothing. Read
  as "dispatch their fixers before BEATD merges", the proposal is the counterfactual measured
  below.
- **The premise is false in the plan's own numbers.** The proposal says the 128.97 h "is set by
  the CP chain alone". The plan leaves 39.3 h between TOOLKIT-MODEL's finish and ARCH-DOCS's start,
  so taking hours off the chain cannot move closure until the slack is spent.

Source: `proposals.md` V151 (owner-approved, orchestrator s10, 2026-10-28).

Instances (counterfactual replans; `after` edges edited in a copy of the roster at `8c57b43dd`):
- Base: 128.97 h at `--slots 6`. With R10-ORCH-PLANPAGE's `after` emptied (pipelined): **129.48 h**,
  0.51 h later, because the early start takes a slot from slot-bound work. With TOOLKIT-MODEL's
  BEATD-side edge also cut: 129.48 h.
- At `--slots 14`: 76.1 h, and pipelined 66.4 h (-9.7 h). That saving exists only at a cap
  P240 rejects, and only in a model the history above contradicts.
- The "~22 h of serial design time" counts no design: `replan.py` has no design phase (grep
  `design` in `tools/plan/replan.py`: no match). The 22.8 h is PLANPAGE's and TOOLKIT-MODEL's
  build time, 11.4 h each (`tools/plan/durations.json` `sizes_hours.M`).

Cost: an opus M fixer dispatched against an unreviewed design. BEATD's round-3 note
(`design/R10-ORCH-BEATD` `f0f046929`, 09:41Z) has no verdict yet; the newest verdict is round 2's
`revise` at `810697a5a`. The proposal itself names the risk of a re-cut. The fixer would also
share `tools/audit/seat/state_docs.py` with BEATD's arm (b), which adds the `state_docs.py beat`
refusal (note §6 (b)3).

Binding: a measured benefit of +0.51 h, a loss, at the live cap, against a re-cut risk. That is
not a clear gain, so the contract's REJECT applies. What the chain needs now is its head:
R10-FLOW-ROSTER-FREEZE's #2903 (tick 09:44Z: RED `tests / nightly-status` unanswered, push-stuck
2100 s, 47 commits behind, and the code-owned approval from @tvofi still owed). After it comes the
round-3 BEATD design review.

## P238: if BEATD's round-3 design is not approvable, split R10-ORCH-BEATD and land arm (a) first so R10-ORCH-PLANPAGE starts on it

Verdict: REJECT. Both halves already exist, and the dependency it would shorten is not real.
- **The split is already the design.** The note's §6 heading reads "each arm one PR". §7 orders
  "(a) → (b) → (c)", so arm (a), the engine and the shim, already lands first as its own PR.
- **The contingency is already policy.** `dev/governance/roles/design-review.md` lines 50-52:
  if the third note still draws `revise`, "the designer re-cuts to the minimal shape the fixer
  can start from". Round 3 is the third note.
- **PLANPAGE needs nothing from arm (a).** Arm (a)'s files are `beatd.py`, `shims/git` and
  `INSTRUMENTS.md`. PLANPAGE's are `plan_page.py` and `state_docs.py`. The only overlap is
  `state_docs.py`, with arm (b)'s refusal, and that is a merge-order collision on distinct
  functions, not an interface PLANPAGE builds on. The 2026-10-23 re-cut note (design/R10-ORCH-MACHINERY
  `2fc665c61`, §4) gives C's one data input as "C reads A's fold": R10-ORCH-LEDGER, whose code is
  on main (`carries-open`, PR 2671).

Source: `proposals.md` V152 (owner-approved, orchestrator s10).

Instances: as for P237. The "~8-10 h off the CP" lands in 39.3 h of slack, and the pipelined
counterfactual at the live cap is +0.51 h.

Cost: one more review cycle, which the proposal names, for a split the design already makes.

Binding: duplicate mechanism and zero measured benefit.

## P239: replan.py starts in-flight groups at their planned slot, which hides the CP lead

Verdict: ACCEPT narrowed. It is carried to **R10-FLOW-TOOLKIT-MODEL**, which owns
`tools/plan/replan.py` and the one plan model (`resume.stage` `not-started`, 14 carries). No new
group is created.

The premise holds on the live roster:
- R10-FLOW-ROSTER-FREEZE is `carries-open`, which is not in `replan.py` `LIVE_STAGES` (line
  108). Its PR #2903 is open, yet the plan starts it at 10-28T17:36Z.
- R10-ORCH-BEATD is `not-started` while its round-3 design is on `design/R10-ORCH-BEATD`, and it
  is planned at 10-29T06:42Z.

Three narrowings:
1. **Live by evidence, not by stage word.** A group is live when it has an open pull request or a
   design ref with no build. `replan.py` reads that from a file the tick writes (the tick already
   reads `number,headRefOid,headRefName,isDraft`). `replan.py` itself makes no API call. An open-PR
   group starts at the replan instant with `live_remaining_fraction`. A design-only group starts
   then too, but with **no credit**: design is not build progress.
2. **Name the scheduled binding chain beside `critical_path()`.** Walk back from the closing group
   through each group's last-finishing predecessor in the schedule, and print each link's slack.
   On this plan that chain is ARCH-DOCS ← REPLAY-REAL-DAY, and the unconstrained CP has 39.3 h of
   slack. Three owner-approved proposals today (V151, V152, V154) read the unconstrained chain as
   the bound. This is a finding against the group's brief, which says "The critical chain comes
   from roster_lib.critical_path". It is propagated by this carry (`finding-propagation.md`).
3. **Not the "credit the elapsed work" half for designs.** Elapsed design time does not shorten
   the build.

Source: `proposals.md` V153 (owner-approved, orchestrator s10).

Instances:
- The counterfactual with FREEZE `in-review` and BEATD `in-progress` gives 128.97 h at
  `--slots 6`, identical to the base. The ETA error is in the chain's dates: FREEZE is 8 h late and
  BEATD 21 h late. Closure does not change.
- The cost of the wrong reading is today's three proposals and their decision cards.

Cost: inside an M group already rewriting `replan.py`: the in-flight input (about 20 lines), a
back-walk over `merged_t` (about 15 lines), and fixtures. Controls: a fixture with an open PR on a
`carries-open` group starts it at t = 0 with credit; a design-only group starts at t = 0 at full
duration; a null (no in-flight file) reproduces today's plan byte for byte; a mutant crediting
the design-only group fails; and a fixture with a slot-delayed predecessor names it as the
binding link with the CP's slack. There is no API call, no standing CPU and no new group or slot.

Binding: closure-neutral, so a separate group would not pay for its slot and its review. As a
carry in the owning seam, the cost is small and it corrects the reading behind three wrong
proposals. Clear.

## P240: raise the open-PR soft cap from 10 to 14 for cloud-only groups

Verdict: REJECT.

Source: `proposals.md` V154 (owner-approved, orchestrator s10).

Instances:
- **There is no cap of 10 in the tree.** The cap is `pr_cap.py dispatch-gate` at `HPO_WIP_CAP`
  (default 6), counting `in-progress` groups (`tools/audit/seat/pr_cap.py` line 14;
  `dev/governance/roles/orchestrator.md` §5). `replan.py` models it as `"slots": 6` (line 111).
  "10" is the owner's soft guide for open PRs ("swing between 1-10"), not a mechanism.
- **"Cloud-only" is not a roster field.** The roster schema has `fixerModel`, `model`, `lane`
  and `size`, and no cloud flag, so the gate could not tell the groups apart.
- **The model's gain does not survive history.** `--slots 14` prices -52.87 h (128.97 to
  76.1 h). The 7-day roster history gives r = 0.045 between live groups and completions 12 h
  later: WIP ≥ 9 closed 7.67 groups per 12 h, against 8.2 at WIP ≤ 6. WIP already ran to 20 under
  critical-path over-cap dispatch, and throughput stayed flat. The owner's own 2026-10-18 cap
  measurement found the same: 64 PR×PR file-overlap pairs among 16 open PRs, and 5 of 8 reviewed
  heads moved after their verdict. Review and merge are the drain.
- Now: `WIP: 4/6 (open PRs 7)` at the 09:44Z tick. The cap is not even reached.

Cost: more concurrent CI (the plan's `ci_minutes` 5962.5 at six slots, with more overlap
recarries), more review load on the drain that measurably binds, and a cap rule that the gate
cannot evaluate without a new roster field.

Binding: the measured benefit is nil. Throughput is flat in WIP over 27 windows, and the cost is
the rework the 2026-10-18 cap was adopted to stop.

## P241: record PRs merge with no review

Verdict: ACCEPT narrowed. It is carried to **R10-RECORD-HOLD-APPROVE** (size S, `not-started`;
its one `after` group, R10-ARCH-SHAPES, is `done`, so it is dispatchable now), with a forward-carry
to R10-ORCH-BEATD.

This is policy-adjacent. The carry edits a policy file, so **the implementing pull request merges
only on tvofi's approving review**, which mandate 6329234399 covers.

Four narrowings, each forced by code:
1. **No change to `app_approve.sh` or `merge_train.py`. The premise is false.** The record PR,
   branch `record/autofix` (`record_row.py` line 619 `RECORD_BRANCH`), already merges on the
   guard alone. `merge_train.py` `sweep_bots` (lines 1078-1114) runs `record_row.py
   --automerge-check --require-green` and never `app_approve.sh`. Its self-test pins that as owner
   directive [7] (lines 3288-3296). Since 2026-10-20, 101 of the 102 first-parent merges whose diff
   is confined to `dev/programme/delivery/` came from `record/autofix`.
2. **"No review" means no review seat. The App approval stays.** `main-protect-checks` requires one
   approving review: #2893's `gh pr merge` was refused with zero reviews, as the seat ledger
   records at 22:19Z on 2026-10-27. The approver App's review, posted on the same deterministic
   guard, is a mechanical step and costs no seat. Removing it would be a ruleset change, which is
   the owner's alone.
3. **The seat comes from the tick, and BEATD would make it automatic.** `ledger.py`
   `review_owed` (lines 505-522) flags every open non-draft PR, the record PR included. The one
   measured instance is #2885, which got an opus fix-review
   (`~/hpo-orch/r10s6/s7/brief-review-2885-r1.txt`); 1 of the 9 record PRs merged since
   2026-10-25 had one. BEATD's arm (c) adds `bus.sh dispatch-owed`, which mints one dispatch per
   `REVIEW OWED` (note §6 (c)4). Without a skip, every record PR then gets a reviewer: 101 in 8
   days.
4. **The stall half is this group's own brief:** the hold block moves after the approval.

Carried change: `review_owed` skips a PR whose `headRefName` equals `record_row.RECORD_BRANCH`.
The tick already fetches `headRefName`. Pass the constant in rather than import `record_row`
from `ledger.py`. `dev/governance/roles/standing-dispatch.md` gains one sentence: a `record/autofix`
pull request is never dispatched a reviewer; its oracle is `record_row.py --plan` equality,
`tests/delivery_status.py --require-rows` and `--automerge-check --require-green`, and the
approver App's review is the ruleset's approval. Controls: a record-branch PR at an unverdicted
head prints no `REVIEW OWED`; null: a `fix/` PR in the same state prints it; a mutant dropping the
skip fails. Files added to the group: `tools/audit/seat/ledger.py` and
`dev/governance/roles/standing-dispatch.md`. `ledger.py` is a BEATD hot file ((b), (c)); this S
group lands first.

Forward-carry to R10-ORCH-BEATD: arm (c)4's `dispatch-owed` fixture includes a `record/autofix`
PR that mints no registry line.

Source: `proposals.md` V155. The owner's words: "record PRs should not need a review at all".

Instances: #2885 reviewed (one in nine); #2856 waited about 3 h at REVIEW_REQUIRED under a train
hold (the group's brief, nightly run 40300518367); #2893 was refused for want of the App review.

Cost: about 5 lines in `ledger.py`, three fixture rows, one policy sentence (zero-headroom caps
are paid by cutting text), and an owner review that the mandate covers. Run time: none.

Binding: prevents an opus review per record PR, about 12 a day once dispatch-owed lands, at the
price of a skip and a sentence in a group already owed. Clear. As filed, the tooling change would
edit code that already does what it asks, and "no review at all" would remove an approval the
ruleset requires. Hence the ACCEPT is narrowed.

## P242: bots and the relay hold off a head with a live dispatch or merge verdict; the train merges main at merge time

Verdict: ACCEPT narrowed. It is carried to **R10-RCA-HEADMOVED**, the root-cause seat that owns
this class (size S, `not-started`; its one `after` group, R10-RCA-FRICTION, is `done`, so it is
dispatchable now). Its brief already lists "merge-main bot, autofix pins, fixer pushes,
orchestrator recarry" and 9 PRs. What is carried is the evidence and the measured reason the
filed mechanism is the wrong countermeasure. The countermeasure, or a recorded refusal, is that
seat's to own (`defect-root-cause.md`). No bot hold is built.

Source: `proposals.md` V156 (owner-approved, orchestrator s10).

Instances: the eight filed moves, classified by author and subject (`git log -1 --format='%an | %s'`):
- 3 bot commits:
  - #2887: `fdf33f466` and `cf5beb181`, `github-actions[bot]` `ci: merge main`;
  - #2894: `65dcf9b2c`, `ci: pin killed mutants`.
- 5 seat or orchestrator commits:
  - #2894: `e6c2df546` (a delivery-row commit), `cf025530d` and `14a9f1cd` (both `Merge remote-tracking branch 'origin/main'`);
  - #2883: `7b071dbd7` and `a7f644700` (the same merge subject).

The proposal's mechanism reaches 3 of the 8. For each of those 3 the hold is wrong:
- **merge-main pushes only on a DIRTY head.** `tools/pr/merge_main_bot.py`'s docstring:
  "GitHub reports it unmergeable (`mergeable: false`)". A DIRTY pull request runs no CI and
  cannot merge. Holding the bot freezes the PR un-runnable until the train arrives, and the tick
  then reads it "NOT REVIEWABLE".
- **Its commit already carries the verdict.** The same docstring says `app_approve.sh --carry`
  judges it "as an automatic merge: a verdict carries over it without a re-review".
- **The pin commit carries too.** `ci: pin killed mutants` is a carried bot subject
  (`app_approve.sh` lines 205 and 213).
- **The relay's handoff arm already freezes** on a live review: R10-ROSTER-FREEZE's part (3),
  landed `07cbe6fe1` (BEATD note "Notes for the fixer").

The cost these moves imposed is therefore not the bot's push. It is a fixer's local branch
stranded behind it (#2887) and the five seat-side merges. Both are the RCA's process question.

Cost: carry text only; the RCA seat is already owed. A hold as filed would add a state read in
two workflows (`merge-main.yml`, `tests.yml`'s autofix) for a mechanism that, as shown, buys
nothing.

Binding: the class is real and owned. The filed mechanism hits 3 of 8 instances and is harmful
or moot on each. Recording the instances where the root cause is owed is cheap and clearly
useful.

## P243: update_pr.sh and open_pr.sh generate `## Head`, `## Red checks` and the measured figures

Verdict: REJECT.

Source: `proposals.md` V157 (owner-approved, orchestrator s10).

Instances: the four filed (#2887 `cd731ff0d`, #2899, #2903, #2873). Against each part:
- **`## Head` is already generated.** `tools/audit/seat/update_pr.sh` lines 76-82 prefix
  `` `<head>` merges origin/main `<M>` ... `` under `## Head` at every update, through
  `tools/pr/head_note.py`. A `## Head` goes stale only when something other than the opener moves
  the head afterwards, which is P242's class.
- **The red names are already detected.** The 09:44Z tick prints `RED unanswered in ## Red
  checks: <names>` for #2872, #2873 and #2903. `prepr.sh` step 6d already writes the
  by-construction `mutation` red (lines 624-651). What a re-take seat supplies is the answer to
  each red, which is the judgement `pr-contract` requires. A generated name with no answer still
  refuses.
- **The figures cannot come from the opener.** The openers run `prepr.sh` and the push. The
  figures are the fixer's harness, null-control and mutation measurements, and nothing the opener
  executes produces them.

Cost: a check-runs read per update (one paginated call per head in the range) and a generator in
two hot openers.

Binding: the one part not already in the tree, red names, removes no seat, because the answer is
the seat's work.

## P244: prepr runs the reviewer's mechanical checks before the handoff

Verdict: DEFER. The carry arm is owned by **R10-FLY-CARRY-DISPOSITION** carry 1, sized by P66;
the packet arm by **R10-ORCH-REVIEW-PACKET** (P229). The mutation-census arm is rejected.

Source: `proposals.md` V158 (owner-approved, orchestrator s10).

Instances: the blocked verdicts' first lines on `verdict/<N>` (fetched by git):
- **Carry-missing: three of the four are mechanical, and owned.**
  - #2899 `a374d0b6c`: "not carried to R10-REVIEW-CARRY (P200) or R10-FLOW-TOOLKIT-MODEL (P203)";
  - #2906 `aa2a03c01`: "not carried to R10-FLOW-BOARD";
  - #2896 `aca91d7d1`: "#2733's only groups are R10-ORCH-ROSTER-SCHEMA (done)".

  These are exactly R10-FLY-CARRY-DISPOSITION carry 1's `carry_audit.py landed` (the body item's
  id present in its routed group's carry at `--roster-ref`; CARRY-MISSING lines; rc 1) and
  `land-ops`. P66 (`s6-batch8.md#P66`) measured 24 of 33 carry-family blocks, 3.8 h median, and
  wired it at `bus.sh dispatch` ("add no opener call site"), before review, which is where
  V158 wants it. #2887's block is `class-open`, a judgement.
- **Review-packet signals:** P229 carries handoff-not-applied to R10-ORCH-REVIEW-PACKET. P232
  showed the packet's 0-item `carry_audit` line is body-only by design.
- **Mutation census: rejected.** CI's `tests / mutation` and `mutation-autofix` already run the
  census on every push, and `prepr.sh` step 6d lists unpinned sites. The filed survivors were
  picked by reviewer judgement, not by the census:
  - #2873 `8e5accc3c`: `mutation-vacuous`, `diagnostics._over_age`;
  - #2903 `339f5fb0e`: `class-open`, `load_dests` rc domain.

  A local census adds minutes per prepr against four shared slots (tick: "prepr slots: 12 running
  (cap 4)").
- **Host path:** `prepr.sh` already runs `ref_privacy.py --check` (lines 264-273).

Cost of what is owned: nothing new. The lever is dispatch. R10-FLY-CARRY-DISPOSITION is
`not-started` behind R10-FLY-ORPHANS-REWRITTEN (`not-started`), and both are S fly-ins.

Binding: the mechanism exists as carried, sized work, so a second ruling would duplicate it. The
census arm adds load and would not have caught the filed survivors.

## P245: once BEATD's design is approved, put 3-4 fixers on arms (a)-(d) in parallel

Verdict: REJECT.

Source: `proposals.md` V159 (owner-approved, orchestrator s10). It interacts with P238.

Instances (counterfactual: R10-ORCH-BEATD's size set to M, 11.4 h for the "8-10 h", in a roster
copy at `8c57b43dd`, `--slots 6 --seats 8`): 128.78 h, against 128.97 h, so **-0.19 h**. The CP's
39.3 h slack absorbs the rest.

The slack also holds under measured throughput, not only in the model:
- About 8 groups close per 12 h (the 7-day series above), so the 58 open groups drain in about
  87 h.
- The chain, run serially from now, is FREEZE's remaining share plus BEATD, PLANPAGE and
  TOOLKIT-MODEL: about 9 + 20.1 + 11.4 + 11.4 = 52 h.
- R10-ARCH-DOCS waits on about 80 predecessors, so it waits on the drain, not the chain.

Cost: the arms share hot files.
- (b) and (c) both edit `ledger.py`; (b) and (d2) both edit `orchestrator_tick.py`.
- (c) appends rows to the table (b) creates; (b)'s loop refusals read (a)'s `beatd.lock`.
- The note orders them "(a) → (b) → (c); (d2) after (b)" (§7).

Building them in parallel means 3-4 opus fixers rebasing onto each other's unreviewed
interfaces, which is P242's head-moved class by construction.

Binding: a measured 0.19 h, against parallel rework on shared hot files.

## P246: one seat audits the 58 open groups against main and closes the moot ones

Verdict: REJECT.

Source: `proposals.md` V160 (owner-approved, orchestrator s10).

Instances: two of the four filed were merged by their own fix PRs, not found already done:
- R10-PLAN-PRIO: #2874, `524c1896b`, 260 lines in `tools/plan/replan.py`;
- R10-FLOW-AUDIT-PLAN: #2869, `6f4434608`.

Their stale stages were roster lag, which `roster_sync.py`'s stage derivation from pull requests
now closes (`de410e4c9`, 2026-10-28). R10-FLOW-ROSTER-FREEZE's arm (b) merged as #2779, which is
also fix work. That leaves roster-lint as the one moot instance in the filing.

Each fixer already catches a moot group at its own dispatch: `fixer.md` step 2 is "Failing test
first". A finding with no failing test at the merge base is not fixed, and the roster records it
(the `unreproduced` key).

Cost: one opus seat reading 58 briefs and their carries against main (314 carries on the open groups of
the live roster), for one measured hit.

Binding: about one moot group in four filed instances. The per-group check already happens at
dispatch, so the audit duplicates it at a large up-front read.

## P247: the mutant harnesses restore the file under test only on a clean exit

Verdict: ACCEPT narrowed. A **new group, R10-FLY-MUTANT-RESTORE** (size S, lane IN, instrument;
no `after`). No group owns `dev/audit/harnesses/`.

Source: `proposals.md` V161 (fixer s10, #2903 PROPOSAL line, routed by orchestrator s10).

Instances: three.
1. #2874's reviewer, 2026-10-27: a tool timeout killed `r10_plan_page_mutants.py` and left
   `tools/plan/replan.py` carrying the `E-explicit-ref-wins` mutant. The retry refused with "has
   uncommitted edits".
2. #2903's fixer (the filing).
3. #2873's round-4 reviewer (the filing).

Survey: 17 harnesses match `dev/audit/harnesses/*_mutants.py`. 14 restore in `finally`, which a
kill skips. 6 check the tree's state, and 9 use a copy, temp dir or worktree (`grep -c` per file;
the sets overlap). Eight use no copy at all: `carry_parser`, `flow_dispatch`, `merge_subject`,
`plan_issues_chart`, `plan_page`, `policy_lint_family`, `sav_baseline` and `train_upgrade`.

Narrowed to the guard, not the copy:
- **No `git archive` copy.** `fixer.md` step 2 says "A mutant run from a `git archive` copy fails
  the #363 `recorded_at` check on every mutant, baseline included".
- **One shared helper in `dev/audit/harnesses/`.** Before the first mutant it refuses (rc 2) when
  any file it will mutate differs from `git show HEAD:<path>`. That catches a mutant left by a
  killed run before anything is measured. It installs SIGTERM and SIGINT handlers that restore.
  After the restore it verifies each file's sha256 against HEAD's blob and exits 1 on a mismatch.
- **Adoption:** every harness that writes a tracked file in place takes it, about 3 lines each. That is at least the eight above; the fixer reads the other nine.

Cost: the helper (about 40 lines) with its own self-test, and 8-17 small edits. No CI, standing CPU
or API cost.

Controls:
- a harness killed with SIGTERM mid-mutant leaves the file at HEAD's digest;
- a planted leftover mutant makes the next run refuse rc 2, naming the file;
- null: a clean tree runs as today;
- mutant: dropping the start check lets the planted run measure the mutant.

Binding: three instances in two days. The failure is a silent wrong result, plus a production
file that can be committed mutated. The fix is small and local, and pays clearly.
