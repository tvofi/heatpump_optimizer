# The owner's standing rulings

Purpose (the orchestrator's wording, confirmed by tvofi on 2026-11-15: "This is
exactly how I see it"): this file is a holding area below policy, not a second
rulebook. (1) An entry policy already states is dropped. (2) An entry that should
bind every session permanently graduates into policy, or into a decision record
when it is structural and its reasoning must be kept, and then leaves this file.
(3) What remains is operational or temporary: the current mandate,
round-specific direction, and preferences too fine-grained for policy. (4) The
file should stay small and shrink over time; a growing file is a signal that
rulings are not being promoted.

Every ruling of tvofi's still in force, with its date. Quoted text is his words
verbatim, typos kept; "as recorded" marks a ruling whose words were not kept,
and "orchestrator's reading" marks an interpretation, never his. A ruling given
to an orchestrator lands here in its next pull request; one superseded moves to
the closing list, naming its successor. An entry belongs here only while no
policy file states it (tvofi, 2026-11-15: "Also screen the rulings for overlap
with policy, if both policy and rulings mandates something, policy is the right
place"; "The point with this is that policy files and policy related files
should follow good data integrity practice, no duplication, that creats risks of
divergence"). Re-read on change after every compaction
(`dev/governance/roles/orchestrator.md` section 0).

## Authority and the mandate

- **Current mandate:** comment 6893738184 on #3394, scope all, until
  2026-12-15T12:00Z. 2026-11-15: "I hereby extend your mandate until 2026-12-15
  12:00Z, post a new mandate in canonical form on the tracking issue for me."
  Cite it in every approval posted as tvofi; ask him for an extension at the
  time, never assume one (2026-11-14: "I will extend the mandate when needed").
- 2026-11-08: "it can still be done by you under the mandate. The mandate means
  you may act as me in any way necessary without asking?" The orchestrator posts
  that review itself and never sends it back to him (what such a review must
  carry is decision 0013's).
- 2026-10-23: "The raise is ok, but you can rule such cases under your mandate".
  A seat's denial is never laundered through the mandate (the raise itself is
  `CLAUDE.md` rule 2 and decision 0013's).
- 2026-11-15: "The owners own words can also be you under the mandate." Wording
  the owner owns (dimension briefs) may be written under the mandate, declared
  with its id.
- 2026-10-25: "You can toggle a ruleset under the mandate as you have done
  multiple times before." Narrow it, restore it, read it back, log it.
- 2026-11-13: "Remember you have GitHub admin rights under the mandate."
  2026-11-09: "Yes delete it, you are free to make that call under the mandate"
  (removing a stuck CI run that holds the programme).
- 2026-09-17: "I have given you a standing approval, but importantly, it applies
  to this session ONLY", and "Such exceptional session approvals can never be
  overstated or uncontrollably extended again." Record a grant in his words with
  its scope; a session grant dies with the session.
- 2026-11-13, card X1: "No, mandate stays as is" (actuator-write pull requests
  stay approvable under it).

## Decisions put to him

- 2026-11-15: "For any decisions, if i don't answer within 5 minutes, go with
  what you recommend and log it".
- 2026-11-15: "Dont default to bring me cards when I have not been active the
  last hour. When I am active, try the 5 minute wait first. Not cards that pause
  your turn".
- 2026-11-13: "Describe all the audits findings and han anything to me as
  decision cards before applying", for audit findings he asks to see (narrowed
  by the 2026-11-15 card rule above).
- 2026-11-07: "Remember to not act on anything before I have decided on the
  verified findings though" (verified is not decided).
- 2026-11-12: "It has already been decided that that should be dropped." Read a
  group's roster stage and note before asking; a settled ruling is not re-asked.
- 2026-10-21 (as recorded): seat questions are decided by the orchestrator under
  the mandate, never surfaced to him in a seat's final text.
- 2026-11-15: "Send judgement-heavy rulings to a seat for a recommendation first
  (an Opus reviewer, or Fable when it is truly architectural), then decide. The
  contract already asks for this on architectural calls." (the orchestrator's
  proposal, accepted in these words; `orchestrator.md` section 5's architect
  note covers concurrent fixes only, so the whole rule stays here).
- 2026-11-15: "Raise effort for a single turn when a ruling warrants it, not for
  the session.".
- 2026-10-29: "there is never a scenario where I would not want to" (fix every
  slip found; never ask).
- 2026-11-12: "Stop replying to no-op notifications to be a bit more token
  effective."
- 2026-11-14: "If they never use it, ship them without it" (cloud seats are
  created with no connectors; never repeat the connector notice).

## Round scope and the objective

- 2026-11-13: "Also verify that the other dimensions also covers the full
  codebase in their contracts, I want future rounds to always check everything
  in their dimension, not only small samples" (for D5 and D6, `D6.md` states it). Where `D3.md` and `D11.md`
  still sample, the change is owned by R11-PRE-BRIEFS-TEXT part 2.
- 2026-11-15: "As soon as everything that is critical to land before the finder
  phase, the finding phase can start in parallel with the remaining groups";
  "Only the finder critical are required for finder start"; "i meant cutover as
  when the finders are finished, so that such groups can move in parallel with
  the finders." What is still open when the finders finish goes to the architect
  and planner phase. "Token Ledger not critical to land before finders."
- 2026-11-15: "Remember that any still open round 10 groups need to be moved to
  round 11 before or at cutover, round 10 no longer is active".
- 2026-11-13: "Make sure the future rounds can use the audit playbook even with
  the addition of the objective function and the improved audit dimension. It
  should also make the round orchestrator pick up the carries and pre-finder
  carries from the previous round."
- 2026-11-13: "outside and owner filed findings and requests should always fold
  into the ongoing round if not explicitly deferred by the owner or outsider".

## The instrument freeze, proposals and root cause

- Card P11 (verbatim in the card list below) sets the freeze's exceptions.
  2026-11-13: "This should be the shape for instrument fixes, prototype
  local fixes in-round, file proposal permanent fixes for consolidation and
  cost/benefit that is carried to the start of next round". (The local in-round
  fix and the round-end triage are `orchestrator.md` section 5's and
  `proposal-triage.md`'s.)
- 2026-11-01: "On any deadlock, you fix it by hand while waiting on the
  permanent fix." 2026-11-13: "For the relay, this repos shape is fix it
  locally, file permanent fix as a proposal".
- 2026-11-14: "limiter first, write that in" (R11-PRE-MACHINERY-LIMITER before
  the other pre-finder instrument groups).
- 2026-11-14, loop-study cards: "L1 loop ledger: Yes · L2 countermeasure order:
  Yes · L3 unread not red: Yes · L4 price induced work: Yes · L5 triage by
  instrument: Yes · L6 probation revert first: All three parts · L7 kill
  criterion: Yes, at 0.8 spawn ratio or 15% hotfix share · L8 machinery rca
  timing: Once per family at round end · L9 generate after merge: Yes · Build
  timing: At round 11 start, per the freeze".
- 2026-09-16: "deploy the rca, it should be done immediately and not deferred as
  owed" (product and release defects and outages; tooling friction is counted by
  family and analysed at round end, L8). The trigger and the separate seat are
  `CLAUDE.md`'s and `defect-root-cause.md`'s.
- 2026-11-13: "you may have a fixer have more carries based on their kind,
  locally for now and filed as a permanent proposal" (operational until the
  round-end proposal triage rules PC-1113-08).
- 2026-11-01: never propose or triage CI-capacity widening: runners, paid plan,
  second account (as recorded). 2026-11-13: "No" to raising the Actions
  concurrency limit; never ask again. 2026-11-12: "You know you can run seats
  locally if needed right?" (a macOS-only check runs on a local seat).

## Process changes ruled 2026-11-13 and 2026-11-14

- Cards, verbatim: "P1: Yes · P2: Declining cap, one in one out, severity route
  narrowed · P3: Yes · P4: Yes, local and cloud · P5: Keep and do the rest · P6:
  Yes · P7: Yes, fold in · P8: Yes · P9: Yes, design first in round 11 · P10:
  Yes · P11: Freeze, except production defects, owner orders and red main · P12:
  Yes, during round 11 · P13: Yes · P14: Yes · R1: Yes, keep one exception seat
  · R2: Yes, render on change · R3: "Full for CLAUDE.md, orchestrator contract
  and rulings; changes only for instrument pages" · X1: No, mandate stays as is
  · X2: Yes, trial". On P9, P10, P12, P14, R1, R2: "They should be fixed in the
  beginning of round 11 before the finders run".
- 2026-11-15, relayed by the orchestrator: "This file should be excluded by the
  corpus but still needs to be re-read on changes, just like instruments.md". It
  is listed in `corpus_excluded.json`, outside the policy caps; the reading rule
  is `orchestrator.md` section 0's.
- 2026-11-14: "Day 1 plus shadow" (the shadow runs beside round 11 as a
  measurement; the switch to an integration branch is his decision after it);
  "Yes." to "small shadow first; driver only if the replay passes"; "If cloud
  seats for speculative gating is feasible, they should run haiku";
  "remerge_main.sh definitely needs to be scoped down aggressively" (merging
  main only on a conflict is `fixer.md` step 6's).
- 2026-11-14: "Keep them open" (never close a re-routed pull request to cut the
  branch count).
- 2026-11-11, study review: "I agree with all the recommendations" (as recorded:
  `tests / ci-ratchet` advisory on a push to main; D11 and D13 name the
  convergence scorecard). 2026-11-12: "2. Round 11" (the product-only required
  check set).

## Priority, caps and the critical path

- 2026-11-09: "Your absolute, critical top priority is to never let the critical
  path or outside PRs slip, ever."; "This should under no circumstances never,
  ever be allowed to slip since it is outside request"; "These types of
  worksrounds is definitely warranted for landing critical path an outside
  request PRs as well."
- 2026-11-07: "all accepted outside issues or contributions should be
  prioritized higher than audit or owner submitted ones unless i call the owner
  one a hotfix".
- 2026-10-28 (as recorded): a hotfix is a production bug the owner or a user
  reports, a feature he calls a hotfix, a critical bug found while fixing, a red
  required check on main, or a machinery bug deadlocking all merges. 2026-10-29:
  "critical-path PRs jump the record step too" (card, 2026-11-15: "Keep both
  parts").
- 2026-11-13: "All production groups now goes above the cap" (orchestrator's
  context: the soft cap of 20 open pull requests before starting new groups,
  2026-11-11).
- 2026-11-11: "Do it, it is already decided and should be built in, no critical
  path, outside or hotfix PR should wait in CI queue"; "Dont do A" (no merging
  on a combined proof with the required-check rule narrowed).
- 2026-11-08: "every item must always have someone on it" for every open pull
  request, ready handoff and unblocked group (as recorded).
- 2026-10-28: "no pr should wait without reason, in particular not CP prs";
  2026-10-18: "act on work waiting on you, you should never ignore it";
  2026-11-06: "Anything ”owed” means by definition you should act in the same
  round"; 2026-11-14: "Act on everything that is owed in the same turn always".
- 2026-11-08: "Raise the coordinator cap to 3" (ordering by owning seam, not
  shared file, is `orchestrator.md` section 5's).
- 2026-11-05: "The point with the roster and plan is to avoid such file
  conflicts" (compare open pull requests' files before queueing).
- 2026-10-25 (as recorded): new work goes to an existing open group; a new group
  only when nothing is in common.
- 2026-11-07: "The dependsncy is backwards, user docs verify need to be after
  every user facing change. Verify no other seams are backwards".
- 2026-11-01: "Each time the plan html is updated, compare the real state
  against the gantt, mechanically if possible, and have slips surfaced to you to
  act on, defer or accept."
- 2026-10-30: "dark mode should absolutely not be scoped out. you have your
  mandate". User-visible quality is never scoped out for cost or ownership.

## Merges, CI and reds

- When a merge train is run, it runs in batch mode with combined proof and with
  overlap, and it pauses while a stamp runs: 2026-11-01: "batch mode should be
  the default mode but the merge seats keep dropping that info"; 2026-11-07: "I
  meant the batch mode with combined proof that the train supports"; 2026-10-22:
  "It is recommended to run the train with --overlap as long as ci of the prs
  are run"; 2026-10-24: "have the merge seat run with batch where possible, and
  always overlap"; 2026-11-08: "The train should pause while a stamp is running
  the next time." These bind nothing while merges are single (card, 2026-11-15:
  "Keep, scoped to train runs (Recommended)").
- 2026-11-04: "keep records such as triage and roster edits on separate
  branches, and merge them with main only around the stamp and in batches";
  "records should not drown out production PRs. Merge the record PRs together
  with stamps". 2026-11-15, card "Hold delivery rows for the stamp too": the
  automatic delivery-rows pull request (record/autofix) also waits and merges
  with the stamp batch, never on its own guard between stamps. 2026-10-28: "we
  should keep them, but that kind of reviews are for sonnet seats" (record pull
  request reviews).
- 2026-11-04: "DONT CLOSE THEM. JUST CANCEL THEIR CI RUNS".
- 2026-11-04: "You don't have to pause merges due to CI ratchets red, since it
  was not caused by any PR".
- 2026-10-28 (as recorded): cancel superseded runs every sweep, CP and hotfix
  heads included ("keep cancelling them, yes"); never a live head or main.
  2026-11-13: "2. Yes" (cancelling superseded main runs while Actions is
  healthy); 2026-11-11 (as recorded): never while Actions is degraded.
- 2026-10-21: "A pr still needs valid evidence" (fix an over-firing check's
  classification, never the requirement).
- 2026-11-04 (as recorded): a heavy pre-PR script runs once per code; a fixer's
  run is not repeated at the opening (scoped prepr is `fixer.md` step 5's).
- 2026-11-11: "4. Go with what you recommend" (a finished merge verdict may post
  before CI is green; the train still gates CI).

## Reviews

- 2026-10-04: "in general, blocked review verdicts go back to the original
  fixer."
- 2026-11-11: "the reviewer has to be fable under the reviewer >= fixer model
  rule" (a reviewer's model is at least the strongest author's; orchestrator's
  reading since 2026-11-15: a Fable reviewer only where the reviewed work is
  itself of that class).
- 2026-11-07: "Remember that a significant new feature should have a design and
  design reviews, especially outside ones. Post on the outside PR that the
  feature is being planned with the design choices made, then post again with a
  link to the plan html as soon as the public page has landed" (whatever its
  size; design first for L and XL is `orchestrator.md` section 5's).

## Outside contributions

- 2026-11-06: "the plan html for an ongoing round should be made publically
  available from a suitable place in the developer documentation on the repo.
  [...] When the plan html is done, and any outside submission is on the roster,
  the plan HTML should be linked in an answer to the outside submission." (Each
  outside submission's disposition is `orchestrator.md` section 5's.)
- Fallback, for an outside pull request decision 0017 does not admit (order by
  card, 2026-11-15: "I3 first, I2 as fallback (Recommended)"): 2026-11-06:
  "R10-PR-CONTRACT-OUTSIDE should be cancelled, drop that path"; "With our
  additions in mind, change the strategy to mergeing our version, but thank the
  outside cotributor in the PR description".
- 2026-11-06, for every outside pull request either way: "For outside PRs, the
  reviewer needs to take extra care on code security".

## Seats and models

- 2026-09-17: "the orchestrator should route to sonnet and haiku models where
  reasonable"; 2026-09-24: "only start your opus 5.5 fixers with medium effort".
- 2026-11-15: "From now on, reserve fable for the most complex, architectural
  work, both for fixers, finders and reviewers". 2026-11-11: "S and M groups may
  go to Opus when no oracle exists or if the groups requires judgement";
  2026-11-12: "Budget is fine for important work".
- 2026-10-25: "the triage seat should be opus, since it requires judgement";
  2026-11-15: "product-feature triage can run on opus".
- 2026-10-21: "try to keep heavy runs on cloud runners to keep the box load
  under control"; 2026-10-25: "dont forget cloud seats are uncapped" (where a
  fixer runs is `orchestrator.md` section 5's).
- 2026-11-08: "Don't forget that you have a cap of 7 local seat that you can use
  for fixers and reviewers as well, best used for work that might need
  sendmessage communication"; "Repeated failures of cloud seats on the same
  prompt could warrant running it on a local seat instead that has sendmessage."
- 2026-11-11: "When you re-fire any seats, have them pick up from the work the
  previous seat left"; "when you schedule seats, you can schedule them in just a
  couple of minutes".
- 2026-10-21: "I get these notifications to approve the cloud seats, there is a
  documented dispatch that uses scheduled tasks, use that".
- 2026-11-04 (as recorded): cloud seats get generous windows, and their liveness
  and output are checked every sweep.
- 2026-10-22: "You are free to restart seats or start entirely new seats as you
  see fit"; 2026-11-01: "You would not need my go ahead for something like
  that."
- 2026-11-09: "Drop it, the seats should use cheaper sub seats when the frugal
  guard says so"; 2026-10-21: "The frugal guard should be on but it should allow
  you to read the policy that binds you". No seat edits `.claude/settings.json`.
- 2026-11-04 (as recorded): every local seat type can message the orchestrator.

## Record, handover and identity

- 2026-11-14: "The resume prompt is generated mechanically".
- 2026-10-28: "sweep should also include the record beat"; "mechanically replan
  and generate the plan html". 2026-11-08: "I would like the public plan page to
  refresh on every update to it without needing a stamp"; "Have a cheap seat
  read it next time".
- 2026-11-13: "5. Leave." (duplicate record lines on #3394 stay).
- 2026-09-24 (as recorded): the owner is named only "tvofi" (card, 2026-11-15:
  "Keep the naming rule only"; who approves what is `CLAUDE.md`'s Identity).
- 2026-10-22: "please have your seats not post claude code footers, especially
  not with direct links to sessions".
- 2026-11-12: "ok, correct any references to that script or remove it entirely"
  (`nudge.md`, which binds Cursor orchestrators only).
- 2026-10-28: "no, you keep working while waiting on background jobs";
  2026-11-07: "NEVER run long scripts inline. Daemonize or background, or use a
  seat".
- 2026-11-01: "Fix this and dont let it slip again" (the wake loop is re-armed
  after every exit and compaction).
- After a compaction, check running seat briefs and pending steps against the
  instrument pages that changed (card, 2026-11-15: "Retire K11, K12 on parity
  (Recommended)").
- 2026-11-09: "Yes, keep the local one, but propose an update to the live one to
  cover the gaps". The local liveness hook is retired once the tracked hook is
  installed and shown to cover it (same card).

## Releases

- 2026-11-01: "to not stall the programme when waiting for ci on main when you
  stamp, admin stamp to keep the merges flowing with overlap"; 2026-11-12: "You
  may stamp without waiting for main"; 2026-11-08: "Stamp manually without
  waiting for main." (When `--allow-red` may be used is `orchestrator.md`
  section 11's.)
- 2026-11-09: "You should have at least one new feature in custom_components or
  3-5 bug fix PRs touching that path between the stamps, if I don't tell you
  otherwise".
- 2026-11-13: "Every release requiring extra steps should either be shipped with
  an automated migration script or very clearly describe the human action needed
  at the beginning of the release notes."; "the incorrect config flow text and
  the release notes omission are defects in themselves".

## Superseded, spent or expired

- 2026-11-15, tvofi on the orchestrator's list: "Retire your candidates". Each
  line below is dated 2026-11-15.
- Default to the recommendation (2026-10-21, 2026-10-31): folded into the
  5-minute rule.
- Text verification split between rounds 10 and 11, "before round 11" changes,
  and "you are round 10" (2026-11-13): spent with round 10's closure; full-scope
  dimensions stand above, the two new dimensions are roster groups.
- Every proposal triaged before implementation (2026-10-22): superseded by
  once-per-round triage.
- The production-share exemption (2026-11-01): superseded by the 20%/10% bar;
  the exemption itself is policy in `ratchet-budgets.md`.
- Queue order of 2026-10-28: superseded by outside first (2026-11-07); its
  hotfix definition stays above.
- The 20-PR soft cap entry (2026-11-11): retired; the cap is named where the
  production-above-cap ruling cites it.
- No merge outside the train (2026-10-26) and the orchestrator never runs
  `train.sh` (2026-10-29): retired; round 11 merges single pull requests through
  `merge_pr.sh` without a standing merge seat.
- GitHub poll cadence (2026-10-07, 2026-10-19, 2026-11-08): retired.
- R10-DRAW-MAP-EVIDENCE rulings (2026-11-14) and the R10-COMBI-TANK waiver
  (2026-11-06): retired here; they live on those groups' roster entries.
- Reviewers owed as soon as a pull request opens (2026-10-20): superseded by the
  delta-review timing of 2026-11-09 (early only for critical path and outside,
  otherwise once CI is green); card "Retire H3 (Recommended)".
- Standing seats with multi-hour windows and their recycling (2026-10-28,
  2026-10-31, 2026-11-01): retired, round 11 has no standing seats; tick and
  roster work are beat jobs (card "Retire J10").
- A main-red hotfix merging before its review (2026-10-24): retired, a merge
  verdict precedes every merge (card "Retire G14 (Recommended)").
- Only policy and budget-raise pull requests need his approval (2026-09-24):
  dropped, `CLAUDE.md`'s Identity section states who approves what (card "Keep
  the naming rule only").
- Fable for L and XL architectural groups (2026-11-11: "Replace L and XL
  architectural groups that are now routed to opus to fable 5.2, use cheaper
  seats for easier work") and "L and XL seats only" (2026-11-12): superseded by
  "reserve fable for the most complex, architectural work" (2026-11-15).
- "Have the triage seat as fable when triaging new product features"
  (2026-11-11): superseded by "product-feature triage can run on opus"
  (2026-11-15).
- Decision cards as the default ("Normal decision cards please", 2026-11-13; "I
  want Normal decision cards as before" and cards through the question tool on
  Remote Control, 2026-11-15): superseded by "Dont default to bring me cards
  when I have not been active the last hour" (2026-11-15).
- "architectural calls take a suitable reviewer's recommendation first"
  (2026-10-21): merged into "Send judgement-heavy rulings to a seat for a
  recommendation first" (2026-11-15).
- Reviewer timing, "only fire reviewers before ci is finished for prs on the cr
  watch" (2026-11-09): superseded by `orchestrator.md` section 5's dispatch at
  the fixer's push, with `bus.sh dispatch` refusing a red head (2026-11-15).
- Mandate 6715477401: superseded by 6893738184 (2026-11-15).
- R3's reading of this file in full (2026-11-13) and the card answer "Count it,
  raise the cap (Recommended)" (2026-11-15): superseded by "excluded by the
  corpus but still needs to be re-read on changes" (2026-11-15).
- Durable policy memory, the full corpus re-read after every compaction
  (2026-10-24, 2026-10-25, 2026-11-09) and the session-start corpus hook
  (2026-10-21): superseded by R3 (2026-11-13), "Rules in full" and the 2026-11-15
  reading rules (card "Retire K11, K12 on parity (Recommended)").
- Non-critical outside and self-fed work goes to round 11 if it moves closure
  (2026-11-12): superseded by the 2026-11-13 fold rule.
- Severity exemption stays (2026-11-11, item 1): narrowed by card P2.
- Every-sweep slip proposals and continuous triage (2026-10, 2026-11):
  superseded by the freeze shape and once-per-round triage (2026-11-13,
  2026-11-14).
- Triage bar 10% / keep 5% (before 2026-11-08): superseded by 20% / 10%.
- Spent with round 10's closure (v10.0.0, 2026-11-15): "Nothing is to be moved
  to round 11" (2026-11-01); the closure definition and gating list (2026-11-07,
  2026-11-13); "catalog PR goes after v10.0.0 stamp" (2026-11-04); the 15/11
  date, its workarounds and bypass authority (2026-11-13, 2026-11-14); "Only
  land gating PRs as long as CI capacity is full" and the two top non-gating
  groups (2026-11-14); the soak before v10.0.0 (2026-11-11, 2026-11-12,
  2026-11-14); part D's round-10 condition (2026-11-13); the round-11 session
  start (2026-11-14); the overnight run and its Fable fallback (2026-11-14); the
  2026-11-08 top set and zero-slip directive (2026-10-24); the 2026-11-12
  catalog, learner and Pages answers; the 2026-11-11 above-cap starts (items 2,
  3, 8); the 2026-11-13 handoff archive (item 4).
