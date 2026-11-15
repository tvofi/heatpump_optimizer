# The owner's standing rulings

Every ruling of tvofi's still in force, with its date. Quoted text is his words
verbatim, typos kept; "as recorded" marks a ruling whose words were not kept,
and "orchestrator's reading" marks an interpretation, never his. A ruling given
to an orchestrator lands here in its next pull request; one superseded moves to
the closing list, naming its successor. Re-read on change after every
compaction (`dev/governance/roles/orchestrator.md` section 0).

## Authority and the mandate

- **Current mandate:** comment 6893738184 on #3394, scope all, until
  2026-12-15T12:00Z. 2026-11-15: "I hereby extend your mandate until 2026-12-15
  12:00Z, post a new mandate in canonical form on the tracking issue for me."
  Cite it in every approval posted as tvofi; ask him for an extension at the
  time, never assume one (2026-11-14: "I will extend the mandate when needed").
- 2026-10-20: "Mandate is full-scoped so, you have the authority"; 2026-10-27:
  "Remember, my approval is still not required during your valid mandate to act
  as me I have told you this many times now." Never park code-owned, policy or
  budget work as waiting for his review while a mandate is in force.
- 2026-11-06: "You may always approve such changes under a validscope all
  mandate of the changes are objectively sound" (policy pull requests, on an
  independent reviewer's merge verdict; never one the approver wrote).
- 2026-11-08: "it can still be done by you under the mandate. The mandate means
  you may act as me in any way necessary without asking?" The orchestrator posts
  tvofi's approving review itself at the head, declared as an agent's, citing
  the mandate.
- 2026-10-23: "The raise is ok, but you can rule such cases under your mandate".
  A raise still carries `## Raise justification`; a seat's denial is never
  laundered through the mandate.
- 2026-11-12: "They don't need to be read by me, a mandate made by me is valid
  for my machinery." Mandate approvals by our machinery are valid on contributor
  fork pull requests.
- 2026-11-15: "The owners own words can also be you under the mandate." Wording
  the owner owns (dimension briefs) may be written under the mandate, declared
  with its id.
- 2026-10-25: "You can toggle a ruleset under the mandate as you have done
  multiple times before." Narrow it, restore it, read it back, log it.
- 2026-11-13: "Remember you have GitHub admin rights under the mandate."
  2026-11-09: "Yes delete it, you are free to make that call under the mandate"
  (removing a stuck CI run that holds the programme).
- 2026-09-17: "I have given you a standing approval, but importantly, it
  applies to this session ONLY", and "Such exceptional session approvals can
  never be overstated or uncontrollably extended again." Record a grant in his
  words with its scope; a session grant dies with the session.
- 2026-11-13, card X1: "No, mandate stays as is" (actuator-write pull requests
  stay approvable under it).

## Decisions put to him

- 2026-11-15: "For any decisions, if i don't answer within 5 minutes, go with
  what you recommend and log it".
- 2026-11-13: "Describe all the audits findings and han anything to me as
  decision cards before applying"; "Normal decision cards please". 2026-11-15:
  "I want Normal decision cards as before"; when the card widget does not render
  (Remote Control), send the cards through the question tool, never as chat text
  (as recorded).
- 2026-11-07: "Remember to not act on anything before I have decided on the
  verified findings though" (verified is not decided).
- 2026-11-12: "It has already been decided that that should be dropped." Read a
  group's roster stage and note before asking; a settled ruling is not re-asked.
- 2026-10-21 (as recorded): seat questions are decided by the orchestrator
  under the mandate, never surfaced to him in a seat's final text; architectural
  calls take a suitable reviewer's recommendation first.
- 2026-10-29: "there is never a scenario where I would not want to" (fix every
  slip found; never ask).
- 2026-11-12: "Stop replying to no-op notifications to be a bit more token
  effective."
- 2026-11-14: "If they never use it, ship them without it" (cloud seats are
  created with no connectors; never repeat the connector notice).

## Round scope and the objective

- 2026-11-13: "at least for objective bugs, I want the codebase to converge
  towards 0 bugs with infinite number of audit rounds."
- 2026-11-13: "I want the agentic coding process to converge against optimal
  quality, lead time and token effectiveness, both with the number of audit
  rounds, and also within the rounds by the self-feeding mechanisms."
- 2026-11-13: "have a fable seat define that function and add it in the audit
  process, so that everything can be evaluated against that objective when a new
  round is started, and any changes needed is made before the finders start".
  Its acceptance: 'a "perfect" model that reads it, should be able to improve
  the dimensions, process and machinery so that that round is completed
  "perfectly"'; 'Running that "perfect" audit round should result in "perfect"
  production code'; and 'the integration is "perfecty" generic and can run every
  install in a "perfect" way, resulting in "perfect" savings'. "For 5, this is
  yours to set using your best judgement": the supported install population and
  comfort bounds are the orchestrator's, recorded with their basis.
- 2026-11-15 (carry E11-N-OBJECTIVE-RECORD (b), "Write it now (Recommended)",
  preliminary): a round closes only with its objective record under
  `dev/audit/yardstick/`.
- 2026-11-13: "Also verify that the other dimensions also covers the full
  codebase in their contracts, I want future rounds to always check everything
  in their dimension, not only small samples". 2026-11-13: "I would like the
  scope of d5 and d6 to always cover that full scope".
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
- 2026-10-29: "each full audit round means a new major version, and it should
  match the round number on closeout"; never a major bump mid-round.

## The instrument freeze, proposals and root cause

- 2026-11-13, card P11: "Freeze, except production defects, owner orders and red
  main". 2026-11-13: "This should be the shape for instrument fixes, prototype
  local fixes in-round, file proposal permanent fixes for consolidation and
  cost/benefit that is carried to the start of next round".
- 2026-11-01: "On any deadlock, you fix it by hand while waiting on the
  permanent fix." 2026-11-13: "For the relay, this repos shape is fix it
  locally, file permanent fix as a proposal".
- 2026-11-14: "limiter first, write that in" (R11-PRE-MACHINERY-LIMITER before
  the other pre-finder instrument groups); card P2: "Declining cap, one in one
  out, severity route narrowed" (only a red required check on main or a blocked
  production pull request skips the bar for machinery).
- 2026-11-08: "bump the triage cost/benefit target to 20% improvement and the
  limit for keeping already planned instrument groups to 10% instead of 5";
  "the issue bar only applies to instrument and machinery". Product defects
  never take the bar.
- 2026-11-14: "yes, do the once per round shape (preliminary, wait for the
  investigation as well)"; "No, keep it in the once per round shape"
  (`proposal-triage.md` stays, triaging once per round).
- 2026-11-14, loop-study cards: "L1 loop ledger: Yes · L2 countermeasure order:
  Yes · L3 unread not red: Yes · L4 price induced work: Yes · L5 triage by
  instrument: Yes · L6 probation revert first: All three parts · L7 kill
  criterion: Yes, at 0.8 spawn ratio or 15% hotfix share · L8 machinery rca
  timing: Once per family at round end · L9 generate after merge: Yes · Build
  timing: At round 11 start, per the freeze".
- 2026-09-16: "deploy the rca, it should be done immediately and not deferred as
  owed" (product and release defects and outages; tooling friction is counted by
  family and analysed at round end, L8).
- 2026-09-25 (as recorded): three or more instances of an audit class owe a
  class-eliminating barrier, not a refusal (`defect-root-cause.md`).
- 2026-10-24: "each operation or shape that is not clearly a one shot and could
  be mechanical should be mechanical and wired into the machinery. This means
  reusable instrument before policy, only policy if no robust script could be
  built at a reasonable cost (tokens, time, complexity)".
- 2026-10-03: "Useful tools should not be kept in local tmp folders only, they
  should be in the tools folder on remote main"; 2026-10-31: "reusable scripts
  in a generalized form always belong on main if they are not redundant, wrong
  or have negative consequences on the machinery." (Under the freeze they land
  as proposals.)
- 2026-11-13: "you may have a fixer have more carries based on their kind,
  locally for now and filed as a permanent proposal".
- 2026-11-01: never propose or triage CI-capacity widening: runners, paid plan,
  second account (as recorded). 2026-11-13: "No" to raising the Actions
  concurrency limit; never ask again. 2026-11-12: "You know you can run seats
  locally if needed right?" (a macOS-only check runs on a local seat).

## Process changes ruled 2026-11-13 and 2026-11-14

- Cards, verbatim: "P1: Yes · P2: Declining cap, one in one out, severity route
  narrowed · P3: Yes · P4: Yes, local and cloud · P5: Keep and do the rest · P6:
  Yes · P7: Yes, fold in · P8: Yes · P9: Yes, design first in round 11 · P10:
  Yes · P11: Freeze, except production defects, owner orders and red main · P12:
  Yes, during round 11 · P13: Yes · P14: Yes · R1: Yes, keep one exception seat ·
  R2: Yes, render on change · R3: "Full for CLAUDE.md, orchestrator contract and
  rulings; changes only for instrument pages" · X1: No, mandate stays as is · X2:
  Yes, trial". On P9, P10, P12, P14, R1, R2: "They should be fixed in the
  beginning of round 11 before the finders run".
- 2026-11-15, relayed by the orchestrator: "Rules in full". After a compaction
  `CLAUDE.md`, the orchestrator's contract and every `.claude/rules/` file are
  read in full.
- 2026-11-15, relayed by the orchestrator: "This file should be excluded by the
  corpus but still needs to be re-read on changes, just like instruments.md".
  This file and the instrument pages are read only where changed since the last
  proof; it is listed in `corpus_excluded.json`, outside the policy caps.
- 2026-11-14: "remerge_main.sh definitely needs to be scoped down aggressively"
  (main merges into a head only on a real conflict); "Day 1 plus shadow" (the
  shadow runs beside round 11 as a measurement; the switch to an integration
  branch is his decision after it); "Yes." to "small shadow first; driver only if
  the replay passes"; "If cloud seats for speculative gating is feasible, they
  should run haiku".
- 2026-11-14: "Keep them open" (never close a re-routed pull request to cut the
  branch count).
- 2026-11-11, study review: "I agree with all the recommendations" (as recorded:
  `tests / ci-ratchet` advisory on a push to main; D11 and D13 name the
  convergence scorecard). 2026-11-12: "2. Round 11" (the product-only required
  check set).

## Priority, caps and the critical path

- 2026-10-22: "ready critical-path groups are exempt from the open-PR soft
  cap->I as an owner demand this, in compination with high priority for the
  critical path PRs"; 2026-10-28: "critical path does always go above any cap and
  first in any queue".
- 2026-11-09: "Your absolute, critical top priority is to never let the critical
  path or outside PRs slip, ever."; "This should under no circumstances never,
  ever be allowed to slip since it is outside request"; "These types of
  worksrounds is definitely warranted for landing critical path an outside
  request PRs as well."
- 2026-11-07: "all accepted outside issues or contributions should be
  prioritized higher than audit or owner submitted ones unless i call the owner
  one a hotfix".
- 2026-11-13: "All production groups now goes above the cap" (orchestrator's
  context: the soft cap of 20 open pull requests before starting new groups,
  2026-11-11).
- 2026-11-11: "Do it, it is already decided and should be built in, no critical
  path, outside or hotfix PR should wait in CI queue"; "Dont do A" (no merging on
  a combined proof with the required-check rule narrowed).
- 2026-11-08: "every item must always have someone on it" for every open pull
  request, ready handoff and unblocked group (as recorded).
- 2026-10-28: "no pr should wait without reason, in particular not CP prs";
  2026-10-18: "act on work waiting on you, you should never ignore it";
  2026-11-06: "Anything ”owed” means by definition you should act in the same
  round"; 2026-11-14: "Act on everything that is owed in the same turn always".
- 2026-10-24: "you should not hold ready handoffs while draining PRs, handoffs
  are more important to drain, so work is not lost".
- 2026-10-24: "as long as they are separated by seams and clear briefs it is ok"
  (concurrent pull requests on one hot file); 2026-11-08: "Raise the coordinator
  cap to 3".
- 2026-11-05: "The point with the roster and plan is to avoid such file
  conflicts" (compare open pull requests' files before queueing).
- 2026-10-25 (as recorded): new work goes to an existing open group; a new group
  only when nothing is in common.
- 2026-11-07: "The dependsncy is backwards, user docs verify need to be after
  every user facing change. Verify no other seams are backwards".
- 2026-11-08: "is it really necessary for a group to feed carries into itself?"
  and, on the card, "Do it, narrow exceptions": a finding in a group's own seam is
  built in its pull request.
- 2026-11-01: "Each time the plan html is updated, compare the real state against
  the gantt, mechanically if possible, and have slips surfaced to you to act on,
  defer or accept."
- 2026-10-30: "dark mode should absolutely not be scoped out. you have your
  mandate". User-visible quality is never scoped out for cost or ownership.

## Merges, CI and reds

- 2026-11-01: "batch mode should be the default mode but the merge seats keep
  dropping that info"; 2026-11-07: "I meant the batch mode with combined proof
  that the train supports".
- 2026-10-22: "It is recommended to run the train with --overlap as long as ci of
  the prs are run"; 2026-10-24: "have the merge seat run with batch where
  possible, and always overlap".
- 2026-11-04: "keep records such as triage and roster edits on separate branches,
  and merge them with main only around the stamp and in batches"; "records should
  not drown out production PRs. Merge the record PRs together with stamps".
  2026-10-28: "we should keep them, but that kind of reviews are for sonnet seats"
  (record pull request reviews).
- 2026-11-04: "DONT CLOSE THEM. JUST CANCEL THEIR CI RUNS".
- 2026-11-07: "One thing I want to do immediately is not having anything block
  because of unnamed reds that is non required."; 2026-11-09: "No pr merge should
  be blocked on a non-required red". The required set is
  `merge_train.py owed-reds`'s.
- 2026-11-05: "It he cause of red is not the pr, comment that and use
  —allow-red".
- 2026-11-04: "You don't have to pause merges due to CI ratchets red, since it was
  not caused by any PR".
- 2026-10-28 (as recorded): cancel superseded runs every sweep, CP and hotfix
  heads included ("keep cancelling them, yes"); never a live head or main.
  2026-11-13: "2. Yes" (cancelling superseded main runs while Actions is
  healthy); 2026-11-11 (as recorded): never while Actions is degraded.
- 2026-10-21: "A pr still needs valid evidence" (fix an over-firing check's
  classification, never the requirement).
- 2026-11-07: "Having the fixers merge main and re-run prepr after each main head
  move seems extremely wasteful, as the train can handle that."
- 2026-11-04 (as recorded): a heavy pre-PR script runs once per code; a fixer's
  run is not repeated at the opening. 2026-11-09: "hotfixes should have
  aggressively scoped or no prepr". 2026-10-21: "Tell seats they are allowed to
  run prepr without closures".
- 2026-11-11: "4. Go with what you recommend" (a finished merge verdict may post
  before CI is green; the train still gates CI).
- 2026-10-24 (as recorded): a small-scope main-red hotfix may merge on a green
  gate with its review after the merge.

## Reviews

- 2026-10-08: "That fixes should be done in an architecturally sound way should
  always be true, binding and persistent"; "budgets can increase as a last resort
  if it is the option that lands a truly better architecture".
- 2026-11-09: "I though it was always only the delta that was reviewed in later
  review rounds? If not, make it so"; "The only exception should be if the delta
  touches production code in a way such that the functionality of the other
  already reviewed code has a risk of being affected in a non obvious way that CI
  would not detect."; "only fire reviewers before ci is finished for prs on the cr
  watch" (critical path and outside); otherwise once CI is green.
- 2026-10-20: "remember reviewers are owed as soon as prs are open on a handed off
  fix."
- 2026-10-04: "in general, blocked review verdicts go back to the original
  fixer."
- 2026-11-11: "the reviewer has to be fable under the reviewer >= fixer model
  rule" (a reviewer's model is at least the strongest author's).
- 2026-11-07: "Remember that a significant new feature should have a design and
  design reviews, especially outside ones. Post on the outside PR that the
  feature is being planned with the design choices made, then post again with a
  link to the plan html as soon as the public page has landed".

## Outside contributions

- 2026-11-06: "the plan html for an ongoing round should be made publically
  available from a suitable place in the developer documentation on the repo.
  During future audit rounds, issues, PRs or other posts from outside users should
  be regularly checked, triaged/designed and planned. Fold this shape into the repo
  machinery. When the plan html is done, and any outside submission is on the
  roster, the plan HTML should be linked in an answer to the outside submission."
- 2026-11-06: "R10-PR-CONTRACT-OUTSIDE should be cancelled, drop that path";
  "With our additions in mind, change the strategy to mergeing our version, but
  thank the outside cotributor in the PR description"; "For outside PRs, the
  reviewer needs to take extra care on code security".
- 2026-11-12: "Implement a mechanism that allow baikanfans PRs to be accepted as
  is as long as they follow all our conventions and rules and have a valid merge
  verdict (the reviewer may also be run by bankaifan). Merges with main and
  codeowner approvals remain in our machinery even for such PRs." The same
  ruling's round-11 deferral clause is superseded (closing list).

## Seats and models

- 2026-09-17: "the orchestrator should route to sonnet and haiku models where
  reasonable"; 2026-09-24: "only start your opus 5.5 fixers with medium effort".
- 2026-11-11: "Replace L and XL architectural groups that are now routed to opus
  to fable 5.2, use cheaper seats for easier work"; "S and M groups may go to Opus
  when no oracle exists or if the groups requires judgement"; 2026-11-12: "Be a
  bit more economical with the fable seats, L and XL seats only"; "Budget is fine
  for important work".
- 2026-10-25: "the triage seat should be opus, since it requires judgement";
  2026-11-11: "Have the triage seat as fable when triaging new product features".
- 2026-11-01: "I think we should run the majority of the fixers in the cloud so
  the heavy runs are not constrained."; 2026-10-21: "try to keep heavy runs on
  cloud runners to keep the box load under control"; 2026-10-25: "dont forget
  cloud seats are uncapped".
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
  see fit"; 2026-11-01: "You would not need my go ahead for something like that."
- 2026-10-28: "you start your standing seats with multi hour windows so the dont
  shutdown"; 2026-10-31: "To be token effective, you should recycle the standing
  seat at a suitable frequency" (card 9, 2026-11-01, as recorded: about 150k
  tokens sonnet, 200k opus, 300k for L and XL fixers; repairs on the group's
  model).
- 2026-11-09: "Drop it, the seats should use cheaper sub seats when the frugal
  guard says so"; 2026-10-21: "The frugal guard should be on but it should allow
  you to read the policy that binds you". No seat edits `.claude/settings.json`.
- 2026-11-04 (as recorded): every local seat type can message the orchestrator.

## Record, handover and identity

- 2026-09-16: "Always keep a clean handover document up to date so another session
  can pick up if this fails."
- 2026-11-14: "The resume prompt is generated mechanically".
- 2026-10-28: "sweep should also include the record beat"; "mechanically replan
  and generate the plan html". 2026-11-08: "I would like the public plan page to
  refresh on every update to it without needing a stamp"; "Have a cheap seat read
  it next time".
- 2026-11-13: "5. Leave." (duplicate record lines on #3394 stay).
- 2026-09-24 (as recorded): the owner is named only "tvofi"; only policy and
  budget-raise pull requests need his approval, everything else merges on the
  approver App's review.
- 2026-10-22: "please have your seats not post claude code footers, especially
  not with direct links to sessions".
- 2026-11-12: "ok, correct any references to that script or remove it entirely"
  (`nudge.md`, which binds Cursor orchestrators only).
- 2026-10-28: "no, you keep working while waiting on background jobs";
  2026-11-07: "NEVER run long scripts inline. Daemonize or background, or use a
  seat".
- 2026-11-01: "Fix this and dont let it slip again" (the wake loop is re-armed
  after every exit and compaction).
- 2026-10-25: "the policy that binds you should be retained in durable memory and
  updated when main updates as well."; 2026-11-09: "You should always, always read
  the whole corpus, including all instrument usage descriptions and correct any
  gaps." (what is read is now ruled by R3 and "Rules in full"; the gap check
  stands).
- 2026-11-09: "Yes, keep the local one, but propose an update to the live one to
  cover the gaps" (the local liveness hook stays until the tracked one has
  parity).

## Releases

- 2026-11-01: "to not stall the programme when waiting for ci on main when you
  stamp, admin stamp to keep the merges flowing with overlap"; 2026-11-12: "You
  may stamp without waiting for main". Never over a concluded red whose cause is
  unknown.
- 2026-11-08: "The train should pause while a stamp is running the next time.
  Stamp manually without waiting for main."
- 2026-11-09: "You should have at least one new feature in custom_components or
  3-5 bug fix PRs touching that path between the stamps, if I don't tell you
  otherwise".
- 2026-11-13: "Every release requiring extra steps should either be shipped with
  an automated migration script or very clearly describe the human action needed
  at the beginning of the release notes."; "the incorrect config flow text and the
  release notes omission are defects in themselves".
- 2026-11-11: "7. Agreed" (stamping with `--allow-red` while main's red is in CI
  tooling, not product code).

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
- Queue order of 2026-10-28: superseded by outside first (2026-11-07).
- The 20-PR soft cap entry (2026-11-11): retired; the cap is named where the
  production-above-cap ruling cites it.
- No merge outside the train (2026-10-26) and the orchestrator never runs
  `train.sh` (2026-10-29): retired; round 11 merges single pull requests through
  `merge_pr.sh` without a standing merge seat.
- GitHub poll cadence (2026-10-07, 2026-10-19, 2026-11-08): retired.
- R10-DRAW-MAP-EVIDENCE rulings (2026-11-14) and the R10-COMBI-TANK waiver
  (2026-11-06): retired here; they live on those groups' roster entries.
- Mandate 6715477401: superseded by 6893738184 (2026-11-15).
- R3's reading of this file in full (2026-11-13) and the card answer "Count it,
  raise the cap (Recommended)" (2026-11-15): superseded by "excluded by the
  corpus but still needs to be re-read on changes" (2026-11-15).
- Full corpus re-read after every compaction (2026-10-24, 2026-10-25, 2026-11-09)
  and the session-start corpus hook (2026-10-21): superseded by R3 (2026-11-13)
  and "Rules in full" (2026-11-15).
- Non-critical outside and self-fed work goes to round 11 if it moves closure
  (2026-11-12): superseded by the 2026-11-13 fold rule.
- Severity exemption stays (2026-11-11, item 1): narrowed by card P2.
- Every-sweep slip proposals and continuous triage (2026-10, 2026-11): superseded
  by the freeze shape and once-per-round triage (2026-11-13, 2026-11-14).
- Triage bar 10% / keep 5% (before 2026-11-08): superseded by 20% / 10%.
- Spent with round 10's closure (v10.0.0, 2026-11-15): "Nothing is to be moved to
  round 11" (2026-11-01); the closure definition and gating list (2026-11-07,
  2026-11-13); "catalog PR goes after v10.0.0 stamp" (2026-11-04); the 15/11 date,
  its workarounds and bypass authority (2026-11-13, 2026-11-14); "Only land gating
  PRs as long as CI capacity is full" and the two top non-gating groups
  (2026-11-14); the soak before v10.0.0 (2026-11-11, 2026-11-12, 2026-11-14); part
  D's round-10 condition (2026-11-13); the round-11 session start (2026-11-14);
  the overnight run and its Fable fallback (2026-11-14); the 2026-11-08 top set and
  zero-slip directive (2026-10-24); the 2026-11-12 catalog, learner and Pages
  answers; the 2026-11-11 above-cap starts (items 2, 3, 8); the 2026-11-13
  handoff archive (item 4).
