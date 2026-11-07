CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-round-playbook, at head 28d46c4918285d36c409c1fb2f72eb77e04e569e. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch 28d46c4918285d36c409c1fb2f72eb77e04e569e for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-round-playbook before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-round-playbook, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-round-playbook, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-round-playbook <body.md>`, which pushes refs/heads/handoff-body/r10-round-playbook; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-round-playbook`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-round-playbook and refs/heads/handoff-wip/r10-round-playbook-body. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
Owner request (tvofi, 2026-10-21): an audit programme playbook that lets a fresh orchestrator run round 11 onwards from the tree alone, written from round 10's final shape at its completion. Deliver it as dev/audit/README.md (the file CLAUDE.md already indexes as how a round is run), not as a second document. The phase sequence from opening a round to its closure stamp: mandate and owner rulings; audit dimensions and finders; verify and judge; the architect/planner P3 and owner approval; the roster and waves; dispatch under the lane caps; fixer and review with cloud seats and relay; carries; the hourly merge pitch; post-merge beat and state docs; stamps; projections and extension; the closure criteria (0 open PRs, 0 open roster groups, only the coordination issue open) and the final state comment. For each phase give entry criteria, exit criteria, the instrument to run (its tools/ path), the role contract that binds it, and the artefact it leaves. Name every policy file and instrument by path and never paraphrase a rule (name-the-policy-file); state no figure the tree can answer. Keep the existing harness-contract and instruments sections. Control: a self-checking arm in a tree instrument (brief_lint.mjs or a small checker) resolves every path and instrument the playbook names at the merge base, with a fixture that goes red on a renamed or removed instrument and a null control that stays green. policy_lint --budgets must not grow beyond the README's cap; if the content needs a raise, apply the budget-raise gate (mandate 6319294694, Raise justification with Architecture score: dS). Re-derive against the tree at the merge base, after every listed after-group has merged.

After: none

Carry 0: tvofi 2026-10-24 cards 1, 2 (amended twice) and 6 (owner accepted; CARDS.json (prestudy-mech, r10s6 scratch, not in the tree)): write round 10's final shape into dev/audit/README.md. (1) The standing set after the retirements is the triage seat plus the beat jobs; name each retired seat's job and its digest file. (2) Context rotation (card 2, amended twice by tvofi 2026-10-24): caps by role, about 150 k tokens for mechanical, standing and relay seats, reviewers, and S and M fixers; about 300 k for L and XL fixers, designers, pre-studies, root-cause and plan seats; about 500 k for the orchestrator, which rotates through the handover document (state_docs.py plus the resume). Rotation is a fresh context between stages (rca, fix, handoff), never a mid-task cut. (3) Blocked verdicts by class (card 6): mechanical classes (carry-*, body or figure staleness, red-check answer, row-format, head-moved, conflict) go to a script where one exists, else to a fresh sonnet or haiku seat on a short brief; judgement classes (harness, mutation-*, class-open, defect, claim-refuted) still resume the fixer. Binding constraint (owner, tvofi 2026-10-24, verbatim): 'make sure the retirement of the standing seats dont cause you to run things inline'. A seat's work moves to a daemon or beat job, never into the orchestrator's turns, and the seat stays until its replacement job is live and verified.

Carry 1: Round-11 decision item (tvofi, 2026-10-25, orchestrator session: "this should be a round 11 decision"): whether to move the repository to a GitHub organization so the native merge queue can replace the merge train. R10-FLOW-MQ-PROBE measured that a well-formed merge_queue ruleset POST returns HTTP 422 on this user-owned repository, with controls (dev/audit/rounds/round10/D13/mq-probe.md). Round 11's opening plan must carry it as an explicit owner decision with these steps: confirm the plan and visibility requirements; weigh migration costs (HACS URL redirect, App installations, deploy key, ruleset ids, instruments keyed to the owner); after any transfer, re-run the probe for real queue latency, gate names on merge_group, and CI minutes against the train's batch runs; then adopt or decline. Not to be acted on in round 10.

Carry 2: Rerouted from R10-FLOW-MQ-PROBE (dropped: #2826 closed unmerged, tvofi 2026-10-25 ruling; the org move is a round-11 decision carried here). HANDOVER trap: a required context that never reports blocks every merge, in either direction.

Carry 3: Rerouted from R10-FLOW-MQ-PROBE (dropped: #2826 closed unmerged, tvofi 2026-10-25 ruling; the org move is a round-11 decision carried here). Pre-study: the Lean flow pre-study, section K9.

Carry 4: Rerouted from R10-FLOW-MQ-PROBE (dropped: #2826 closed unmerged, tvofi 2026-10-25 ruling; the org move is a round-11 decision carried here). tvofi 2026-10-24 card 4 (owner accepted; CARDS.json (prestudy-mech, r10s6 scratch, not in the tree)): this probe runs right after R10-CI-LAYOUT-P2 closes, before the groups that build head-carry and absorb machinery, and its report ends with an explicit adopt-or-decline recommendation for each held group: R10-FLOW-RECORD-PITCH, R10-FLY-ROW-HEAD-CARRY, R10-FLY-CARRY-DOC-CONTEXT, R10-TRAIN-OVERLAP-GRADE and part (a) of R10-FLOW-BODY-ONLY. The orchestrator takes the owner's decision on that report and closes each group the queue makes moot, so this group's merge is not the release of the held groups; the roster edit that closes or releases them is. The after-edges on those groups hold them until this group is done.

Carry 5: Owner-sourced (tvofi, 2026-10-25, decision cards from the pipeline benchmark seat, measured at origin/main c9cbe6b45). ACCEPTED for round 11: G1-G10. REJECTED: G11 (rc + canary release).

Baseline (round 10, 10-14..10-25):
- 459 first-parent merges, of which 40 (8.7%) touch custom_components/.
- custom_components grew +5%; tools/ grew +69% (52.2k to 88.5k lines).
- Instruments lane is 59% of groups.
- Product first-pass yield 9/40 (22.5%) at 2.9 verdicts each; other PRs 51%.
- 286 blocks: 113 real, 173 bookkeeping.
- Product lead time median 19.6 h.
- Instruments: flow_metrics.py, review_strength.py.

Each card gives its destination in brackets, then the change.

- G1 Meta-work budget [R11 playbook + D13 amended]: cap the machinery share of dispatched groups or seat-hours (about 40%). When the budget is spent, new instrument groups freeze; the exception is a group whose pre-registered metric removes measured toil. Cap fly-in inflow. D13 reports allocation (product share of merges, groups and lines).
- G2 Tiered evidence by blast radius [R11 playbook + D13]:
  - Tier 0 (record/roster/triage): deterministic checks only.
  - Tier 1 (non-gating tools, docs): a rubric review.
  - Tier 2 (custom_components, gate/merge/stamp/approval instruments): the full fixer/fix-review protocol.
  - Tiering is keyed on closures, not directory names. Design seat.
- G3 Parallel-candidate pilot [R11 playbook]: covers the next 6 L/XL product groups, or any product group after its second real-class block. Two independent fixers work from the approved design note. Choose mechanically: mutants killed, then the finder's harness at both ends, then the archscore delta. Only the winner is reviewed. Pre-registered against 22.5% yield / 2.9 verdicts. Small design seat for the selection rule.
- G4 Reviewer calibration [D13 amended + R11 playbook]: each round, a blind judge on a different model re-adjudicates about 30 blocks (stratified by class) plus about 20 merge verdicts at the same heads. Publish the false-block and missed-defect rates and set a precision floor. The labels feed G5.
- G5 Contract regression evals [R11 playbook + D11 amended]: a frozen set of 30-50 labelled historical PR heads (labels from G4). A fix-review.md or COMMON.md change runs k=3 and reports precision, recall and pass^k. A fixer.md change runs on 5-10 seeded tasks. D11: a contract change without an eval result is a finding. Design seat; depends on G4.
- G6 Ratchet the machinery [D7 amended + R11 playbook]: one-sided caps on tools/ at current values (max file LOC, max function LOC/CC, duplication). Extend archscore counters to tools/; D7 audits the machinery. Design seat for the archscore part only.
- G7 Pre-registered process changes [R11 playbook + D13]: triage accepts only with a metric, a baseline instrument, a review date and a revert criterion. At most about 5 unvalidated process changes run at once. D13 reports closed vs open loops.
- G8 Rule-enforcement registry [R11 playbook + D11 amended]: every must/never rule gets an id mapped to its enforcing check, or marked judgement. Enforced rules' prose moves into the check's refusal message. Role briefs keep only the judgement rules. D11 audits coverage. Design seat.
- G9 Token/cost telemetry [R11 playbook + D13]: a ledger from seat transcripts and cloud run logs, by group, stage and model. Report tokens per merged product PR, per real catch, and per standing-seat hour.
- G10 One tool surface [R11 playbook]: a single `hpo <noun> <verb>` entry point with uniform --json, exit codes and idempotency keys. INSTRUMENTS.md is generated from it. Migrate the most-used paths first. Design seat first; phased.

Do not regress (benchmark: already at or above the standard):
- review grounded in execution;
- diff-scoped mutation testing;
- measured closures;
- the merge train;
- the writer/reviewer split with a frozen head;
- state outside the context window;
- one-sided policy caps;
- RCA triggers;
- null controls;
- claimed golden drift;
- small groups.

Carry 6: Owner-sourced (tvofi, 2026-10-25): the throughput/yield/quality proposals tvofi accepted are recorded here for round-11 planning. The set is V63-V103, with tvofi's exclusions as recorded in proposals.md: all of ideas 1-10 except 5; all 6 structural ideas; and the 30-idea set except T3, t5, f6, f8 and q4.

Triage batches 27-31 re-ruled the ones it could not measure in round 10 as DEFER. Each DEFER names its measurement or owning group, in triage PRs #2827-#2831. Round-11 planning takes each deferred item as owner-accepted. It is pre-registered per benchmark card G7 (metric, baseline, review date, revert criterion) before implementation. Design-seat items: T2, F5, Q2, Q3, Q7.

Carry 7: `rounds.py`: unenforced: the group's brief names `rounds.py --stats`, which is not a mode; the invocation exits 0 with zero bytes and would read as a measurement (record section 1). Carry: R10-ROUND-PLAYBOOK

Carry 8: From #2946 (R10-CONFIGFLOW-PAGES arm D, verdict/2946 carry-missing): round 11's class-P2 sweep must run differently in two ways. (1) The eleven F5 clone-class sweep instances of #2238 (enumerate_p2.py clone classes #7, #16, #17, #18, #30, #31, #32, #36, #39, #40, #41: coordinator _accumulate_energy|_maybe_run_fuse_advisor|_settle_interval_diag, _async_learn_house_heat_loss|_async_learn_lower_floor_loss, _file_lead_predictions|_predicted_next_room_temp, _fold_internal_gains|_fold_solar_aperture; optimizer _buffer_charge_ceiling|hold_demand_kw, _grid_report|tariff._peak_excess, _peak_day_kwargs|_peak_window_factors; sensor extra_state_attributes pair; tariff _close_window|from_dict, _window_means_batch|metering_windows, plan_window_days|window_factors) have no owning group once #2238 closes; they stand as class P2 instances in dev/audit/config/bugclasses.json, and the playbook's round-11 intake re-measures them and routes each still present to a group by owning seam. (2) dev/audit/rounds/round10/D14/sweep-P2/probes_p2.py's sixth probe raises NameError: name 'defrost_interval' is not defined since #2527 extended coordinator._observe_frequency's predicate; the playbook's P2 sweep step binds that name (and `self._pump_signals`) in the eval namespace or re-extracts the predicate before reading probes_failed. Precondition and control: re-measure at the stage's own merge base with probes_p2.py (defrost_interval bound or the predicate re-extracted) and enumerate_p2.py; at #2946's tree (origin/main 66974d473) enumerate_p2.py read F5_clone=24, F1_run_threshold=13, seams_total=50. Null: enumerate_p2.py --fixture (a clean synthetic package) must read 0 per family.
(3) Friction from #2946: the fixer brief for R10-CONFIGFLOW-PAGES dispatched the group's whole design (bug first, arms A-C2) while #2912, #2913 and #2915 had already merged them and the roster still read resume.stage not-started; the seat found it from git log. Playbook dispatch step: before a group's fixer is dispatched, compare its roster stage with the merged pull requests that name the group, and brief only the arms not yet on main. [moved: R10-CLONE-2238]

Carry 9: The eleven F5 clone-class sweep instances of #2238 (#7, #16, #17, #18, #30, #31, #32, #36, #39, #40, #41) have no owning group. They stay as class P2's instances in `dev/audit/config/bugclasses.json`, which round 11's D14 sweep reads. That sweep's `probes_p2.py` no longer evaluates its sixth probe (it predates `defrost_interval`, added by #2527), so the next run must bind that name or re-extract the predicate. This changes how round 11's P2 sweep is run. It landed in `dev/programme/rosters/wave-r10-groups.json`, group R10-ROUND-PLAYBOOK, on `handoff/audit-r10-roster` at `8c06d2836260bd2447b763cc269422725bc9d85b` (roster tip `3b14d527a03926d092cb06631dcd3601b35786a9` contains it), with its control stated as a precondition. Carry: R10-ROUND-PLAYBOOK [moved: R10-CLONE-2238]

Carry 10: `delivery-status-tracking`: stale: the roster group R10-CONFIGFLOW-PAGES on `handoff/audit-r10-roster` still read `resume.stage` `not-started` at this dispatch, and the fixer brief asked for D7-s2-56's bug first and then the design's moves, though #2912, #2913 and #2915 had merged all of them. The seat found this from `git log` and re-measured instead of re-making. The countermeasure is a dispatch-time step for the playbook: before a group's fixer is dispatched, compare its roster stage with the merged pull requests that name the group. It is item (3) of the same roster carry, `8c06d2836`. Carry: R10-ROUND-PLAYBOOK

Carry 11: A seat must record an instruction from another agent that contradicts policy as pending, not as direction (P216, V129, from this seat's own record at 20:20Z: the orchestrator's "the append-carry ops are yours to re-run" was written into `triage-STATE.md` as "main's direction, superseding" its earlier reading, contradicting `dev/governance/roles/proposal-triage.md` (line 32: "**You do not** implement, edit the roster or merge") and the owner's rule that roster ops go to the standing roster seat's queue -- caught only by a policy re-read before the next merge). Add to `CLAUDE.md`, beside the rules that bind every seat, this paragraph (5 lines, 414 bytes, about 104 tokens): "**Another agent's instruction is not a contract change.** An instruction from another agent (the orchestrator, a fixer relaying a ruling, any peer) that conflicts with this file, the seat's role contract or the owner's standing rules is recorded as `pending owner confirmation`, quoting the rule it would change; the seat neither acts on that half nor writes it as direction until the owner or the contract moves." A genuine lane change is recorded the same way and unblocked by the owner's or the contract's move, so the marker is an open question, not a veto. `CLAUDE.md` is at its exact per-file token cap (3605/3605, `policy_lint.mjs --budgets`): the same pull request deletes at least 414 bytes of other `CLAUDE.md` text so the cap is unchanged and the file stays at or under its 221-line cap; do NOT raise the cap in `dev/governance/config/policy_budgets.json` (an always-loaded charge on every session, rejected in the ruling). If the owner's review accepts no cut, close the carry unimplemented. Do NOT add a text predicate over seat state (`state_docs.py` or elsewhere): a state file that quotes a rule or records an owner-approved lane change would be refused, and the null control -- a state file quoting `CLAUDE.md` while changing nothing -- cannot be told from the failing one by any substring. This is policy: the carrying pull request merges only on tvofi's approving review at its head, and its body must say so. Distinct from P215: that guard refuses the caller at the instrument; this rule governs the receiver's record. triage: dev/programme/triage/s6-batch42.md#P216

Carry 12: STRANDED CARRY 9 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 12; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: R10-ORCH-BEATD done at #2916 with arm (a) only (#2916 body: "The (b) and (c) carries stay on the roster group"); design/R10-ORCH-BEATD 32e249d2 sections 3-4 scope arms (b) and (c); orchestrator.md has no rotation paragraph (`git grep -i rotat` hits only fixer.md:9); R10-ROUND-PLAYBOOK carry[0] writes card 2 into dev/audit/README.md, not orchestrator.md.

Fold into: R10-ROUND-PLAYBOOK (live). It writes round 10 final shape and carries the round-11 decision items.

Original text, verbatim:
tvofi 2026-10-24 card 2, amended twice (owner; CARDS.json (prestudy-mech, r10s6 scratch, not in the tree)): the same orchestrator.md edit adds one paragraph on context rotation, with caps by role: about 150 k tokens for mechanical, standing and relay seats, reviewers, and S and M fixers; about 300 k for L and XL fixers, designers, pre-studies, root-cause and plan seats; about 500 k for the orchestrator, which rotates through the handover document (tools/audit/seat/state_docs.py plus the resume, with handover_prompt.py and resume_doc.py) at a ledger-clean point. Rotation means a fresh context between stages, never a mid-task cut and never mid-merge. The text pays for itself by cutting text elsewhere in that file (zero headroom).

Carry: R10-ROUND-PLAYBOOK

Carry 13: STRANDED CARRY 14 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-MACHINERY, index 1; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: yes.

Why stranded: owner decision 2026-10-20: #1763 P2/I5 split deferred, "recorded here ... so the deferral is not silently lost a second time"; MACHINERY closed and no live group or brief names 1763 (live grep empty).

Fold into: R10-ROUND-PLAYBOOK (live). It writes round 10 final shape and carries the round-11 decision items.

Original text, verbatim:
Owner decision 2026-10-20 on the slip screen's card 3: #1763's P2/I5 catch-all split, deferred to round 10 with a detector-first pre-study, is not built this round. Round 10 has no group for it and no pre-study artifact; the only trace was the round-9 plan row. Recorded here as a decision rather than left implicit, so the deferral is not silently lost a second time.

Carry: R10-ROUND-PLAYBOOK

Carry 14: STRANDED CARRY 45 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-BEATD, index 24; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: R10-ORCH-BEATD done at #2916 with arm (a) only (#2916 body: "The (b) and (c) carries stay on the roster group"); design/R10-ORCH-BEATD 32e249d2 sections 3-4 scope arms (b) and (c); #2916 body carries no record-merge count against 2026-10-24's 19; the carry says "not a PR of its own", so it needed a host body.

Fold into: R10-ROUND-PLAYBOOK (live). It writes round 10 final shape and carries the round-11 decision items.

Original text, verbatim:
Carry from R10-FLOW-RECORD-PITCH (#2836, merged 28800999b): the roster carry asks for a post-merge measurement. Count one full UTC day of record merges after 28800999b and compare it with 2026-10-24's 19. Record the number and the comparison in this group's PR body. Run it as a script over `git log --merges`, with a flat-day null control. This is not a PR of its own. Ruling: orchestrator, 2026-10-26, under mandate 6329234399. The group closes as done, and this measurement moves here so it is not lost (zero leftover carries).

Carry: R10-ROUND-PLAYBOOK

Carry 15: STRANDED CARRY 52 (carry-strand audit, orchestrator s9, 2026-10-31)

Source: group R10-ORCH-MACHINERY, index 2; triage id: none; roster ref origin/handoff/audit-r10-roster abb47a06cd190e49c9d9da264ea3fab2a71f890d.
Owner-ordered: no.

Why stranded: #1721 token-view detector unproven; live grep "1721|token-view" empty; MACHINERY closed.

Fold into: R10-ROUND-PLAYBOOK (live). It writes round 10 final shape and carries the round-11 decision items.

Original text, verbatim:
Unproven, from the 2026-10-20 slip screen: #1721's token-view ruleset detector could be neither confirmed as delivered nor refuted; an RCA refusal would settle it. Carried unproven rather than turned into work on a guess. If the group touches the ruleset probes, answer it there.

Carry: R10-ROUND-PLAYBOOK

Carry 16: Owner directive (tvofi, 2026-10-31): "the architects 30% arch score improvement can be even higher if cheap enough, and each group that touches production code should aim to also improve the score by sound changes, gaming fully prohibited."
Fold into the round playbook and the contracts it names, as a policy change approved before merging:
(1) dev/governance/roles/architect-planner.md: the dS >= +22.7 target, a 30% fall in the weighted geometric mean, is a FLOOR, not a cap. The planner plans past it wherever the extra moves are cheap, priced by the plan's own cost terms: seat hours, review rounds, hot-file contention. Each move past the floor carries its cost estimate beside its expected dS.
(2) dev/governance/roles/fixer.md step 17 (and plan-review.md for the plan): a group whose diff touches production code also takes sound score-improving changes in the code it already touches, inside its size budget and seam: one owner per concern, removed duplication, fewer parameters, no layer violations. Its body states the archscore dS with its command.
(3) Gaming stays fully prohibited, and the mechanism already exists: fix-review.md step 14 (metric-gamed: remove the mechanism; plant the same move with nothing improved), plus fixer.md 17's list of non-improvements. The playbook names both and adds no new gate.
Reconcile this with the score's own doctrine. tools/audit/archscore/score.py says the score is "a review trigger ... never a target a seat is rewarded for moving". The playbook text must say that a seat aims at the improvement in the code, and the score only reports it. A seat is never credited for dS alone.
Control: the playbook and the three contracts state (1) to (3); brief_lint passes; a plan review of a plan stopping at the floor with a cheap move left over flags it.

Carry 17: Owner ruling (tvofi, 2026-11-01, "go with what you recommend"): the mold guard keeps precedence over the away setback. It protects the building, and on the owner's recorded 2026-10-30 away period (52-53 % indoor humidity, outdoor 1-5 C) it held the floor at 19.2-20.9 C, capped at the 19.5 C target, so away saved nothing. Away must not lower the mold-safe floor. The fix is visibility, not precedence: while away is on and the mold floor is what holds the setpoint, the integration must say so (a reason on the away/plan status and in the advisor's savings view: "away savings limited by the mold guard", with the floor and humidity), so the user is not told away is saving energy when it is not. Round-11 item: a UX/advisor change with a failing test that reproduces the recorded condition (away on, mold floor >= away target) and asserts the reason is shown, and a null control (away on, mold floor below the away target: no such reason).

Carry 18: Round-11 D15 inputs, re-homed from R10-REPLAY-REAL-DAY (its 0-based carries 3, 5 and 8; handoff 73ef64912). Both items read the owner's live diagnostics bundle, which no round-10 seat holds, so they belong to round 11's D15 run. They are not part of this group's own README work. Where the playbook describes the audit-dimensions phase, it states that the round-11 D15 seat's task names these reads:
(1) D15 lead L9. Read `unhealthy_input` from each weekly learner snapshot (`snapshots.py`), name the input that marked each unhealthy snapshot, and say whether it was genuinely silent or whether outdoor's 180 min on-change limit flagged a quiet, healthy sensor. Change that limit only on that evidence. Controls: a week with every input reporting names none (null); a week with one input silent all day names that input.
(2) The R10-SCORES scale drift. Run `dev/audit/harnesses/r10_scores_envelope.py --bundle PATH` on the owner's bundle, to measure the suspected 2.6x scale drift and the band on the owner's house.
No figure is stated here that the bundle must supply. The README stays within its `policy_lint --budgets` cap.
triage: dev/programme/triage/s6-batch97.md#P352 [moved: R10-LIVE-BUNDLE-READS]

Carry 19: Machinery freeze after v10.0.0 (tvofi 2026-11-01, production-share ruling). From the round-10 closeout stamp on, a change to the programme's machinery (tools/audit/**, tools/pr/**, tools/plan/**, tools/policy/**, .github/workflows/**, dev/governance/**, seat scripts) merges only if it (a) unblocks a named production pull request (one touching custom_components/) or (b) fixes a red on main or on such a PR. Everything else waits for a planned instrument window the owner opens. EXEMPTION (shared with the proposal bar): a change whose proposal PROVES more than a 10% improvement in CI time, programme completion time, right-first-time rate or token usage, measured with a baseline and a null control, may merge outside a window. Write it into the round playbook (dev/audit/README.md, CLAUDE.md index line) and state who checks it (merge seat at admission; the R10-MACHINERY-RATCHETS instrument mechanically). Evidence for the rule: 2 of 37 merges in the 24 h to 2026-11-01T19:40Z touched custom_components/; 59 of 581 in 14 days.

Carry 20: Production slots (tvofi 2026-11-01, production-share ruling). Of the open-PR cap (16 in round 10), reserve 10 slots for pull requests that touch custom_components/; machinery and record PRs share the remaining 6. A machinery PR that would take a reserved slot waits; a production PR is never refused for lack of a machinery slot. Write it into the round playbook (dev/audit/README.md) and into the dispatch gate's cap rule (tools/audit/seat pr_cap / dispatch-caps), with the open-PR count by class printed on every tick so the split is visible.

Carry 21: Proposal bar (tvofi 2026-11-01, production-share ruling; in force operationally since 2026-11-01T19:50Z by owner ruling to the triage seat). proposal-triage.md: a process or tooling proposal is ACCEPTED only when its friction blocks a production merge (a PR touching custom_components/); otherwise it is ruled LOG (recorded with evidence, nothing built). EXEMPTION: a proposal that proves more than a 10% improvement in CI time, programme completion time, right-first-time rate or token usage, with a measured baseline and a null control, is ruled on cost/benefit as before. Amend dev/governance/roles/proposal-triage.md (policy: owner approval at merge; mandate 6329234399 scope all applies while in force) and the triage instrument's verdict vocabulary (LOG beside ACCEPT/REJECT/DEFER).

Carry 22: From the s9 leads and prose sweep (2026-11-01): dev/programme/HANDOVER.md still lists the pr_cap owed-handoff exemption as owed, but it is fixed in code on main at 92588d581. Under writing-for-agents.md and the one-living-handover rule, the durable handover must not carry a stale owed item. Fix: rewrite that entry in place to say what the code now does (or drop it), citing the line in pr_cap that exempts owed handoffs. Failing test first: none; this is a record change. Null control: a grep of HANDOVER.md "Owed" items against code at the same sha finds no other stale entry. Re-measure it at the PR's merge base.

Carry 23: From R10-LIVE-BUNDLE-READS (handoff 06234008): a version change across a gap counts as a restart whatever its length; the 43.6 min upgrade gap read as no restart. Its Round-11 D15 inputs carry was done in that group and may be discharged. Re-read unhealthy_input on the next bundle: only the newest of 8 snapshots carries it. Carry: R10-ROUND-PLAYBOOK

Carry 24: Owner ruling (tvofi, 2026-11-07, verbatim "Approve both", recorded on the coordination issue, comment 6707334933): R10-ROUND-PLAYBOOK is split. This group drafts the playbook now, with no after-edges: write dev/audit/README.md from the tree at its merge base, with the phase sequence, entry and exit criteria, instruments and role contracts its brief names, and the path-resolving checker with its fixture and null control. The final reconciliation pass, re-derived after every group this group used to wait on has merged, is R10-ROUND-PLAYBOOK-FINAL (size S); this group's brief sentence "Re-derive against the tree at the merge base, after every listed after-group has merged" binds that group, not this draft. The closure criteria the playbook states are the owner's 2026-11-07 sentence, verbatim: "The programme is not considered closed until both v.10.0.0 and the catalog PR has landed, there are no open prs, handoffs, carries, findings or leads, and only issue 201 is open". The draft does not edit CLAUDE.md (open PR 3245 edits it; CLAUDE.md already indexes dev/audit/README.md); any index edit waits for the final pass.
Carry: R10-ROUND-PLAYBOOK
