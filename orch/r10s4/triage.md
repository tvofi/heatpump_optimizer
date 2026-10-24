# Proposal triage, round 10 session s4

Seat: triage (sonnet). Base measured: origin/main 543c8087c, roster wave-r10-groups.json at that ref.
Batch 1: 2026-10-22 ~12:10Z. Time used ~35 min. gh calls: 4 (2580 view, 2580 reviews, ruleset, 2580 state).

Constraint note that applies to all four: decision 0012 (the moratorium) is REVOKED. Decision 0014
(dev/governance/decisions/0014-design-seats-and-the-end-of-0012s-moratorium.md, on origin/main) says "0012 is
revoked ... its moratorium included". So "no new lint class / rule until 2026-10-31" does not bind any of these.
Several roster briefs still quote it (R10-FLOW-JIDOKA, R10-RCA-ORCH-CONTINUITY): stale text, no effect.
None of the four needs a new policy file; all four are instruments under tools/ (no owner round-trip).

---------------------------------------------------------------------------------------------------

## P1 bus.sh orphans: skip a handoff ref that adds only main merges

VERDICT: DEFER -> R10-FLY-ORPHANS-REWRITTEN (not-started, files bus.sh + cloud_relay.sh, after TICK-OWED-LEVEL,
FLOW-RELAY-HOLD, UPDATE-PR-SIGNALS). Fold, do not open a separate PR.

Measured facts (git only):
- The false positive is real: handoff/r10-fly-gh-read-retry a457acaf4 is a merge commit with parents 9b9770b34 and
  b787c7d45. `git log --no-merges a6e90cbcc..a457acaf4 ^origin/main` is empty; `git rev-list --no-merges --count
  a457acaf4 --not origin/main a6e90cbcc` = 0; `--count` without --no-merges = 1 (the merge itself, which is the
  "uncovered=1" the ORPHAN line prints).
- Correction to the proposal's wording: the PR head a6e90cbcc is NOT an ancestor of the tip. Both of the tip's
  parents are already ancestors of the head (update_pr.sh merged main into the PR separately). So bus.sh gives it
  `repair=review` (neither contains the other), not `update`. The predicate that fits is not "commits beyond the
  PR head are only merges"; it is "the tip has no non-merge commit outside origin/main plus every origin/fix/* head".
- Frequency: of 134 handoff refs with a handoff-body ref, 1 matches right now (this one). Lower bound for the round:
  1 confirmed instance; the other ORPHAN lines in the s4 logs (r10-roster-sync, r10-replay-cap, r10-night-folds,
  r10-merge-pr-mandate ...) all have real non-merge commits, so they are not this class.
- Existing arms miss it: the ancestry arm needs tip ancestral to main or a fix head; content_superseded() diffs
  merge-base(main,tip)..tip and sees the PR's own work as an unmerged modification.

Cost: ~6 lines in orphans() (one `git rev-list --no-merges --count "$tip" --not "$main" $fix_heads`, counted as
`anc`), one self-test arm plus a mutant, inside a function the destination group already rewrites. Marginal
review cost near zero as a fold; as a standalone PR it is a full gate + fix-review cycle (~1.5 h) for one ref.
Benefit: a persistent false ORPHAN on every sweep (4.5 h so far, ~1 line per sweep read, ~10 s of orchestrator
attention each, plus the risk that the real orphan count normalises to "ignore the list"). Small per instance,
no API cost.

Binding constraint: none of 0012/CLAUDE.md. Owner rule is finding-propagation.md (carry it into the stage's brief).
Interim, zero build: pass `--exclude-topic r10-fly-gh-read-retry` to the sweep/tick call of `bus.sh orphans`
(the flag exists), or let #2589 merge: once the PR merges the fix head is in main and the ref is an ancestor.

Carry text for R10-FLY-ORPHANS-REWRITTEN (append with roster_edit.py):
  "Fold (s4 triage P1): bus.sh orphans reports a handoff tip as ORPHAN when the tip is a merge commit of main whose
  non-merge content is already in main or a live fix/* head. Measured 2026-10-22: handoff/r10-fly-gh-read-retry
  a457acaf4 (parents 9b9770b34, b787c7d45; fix head a6e90cbcc contains both parents and is not an ancestor of the
  tip) was listed for 4.5 h as repair=review, uncovered=1. Add a discharge arm beside the ancestry arm:
  `git rev-list --no-merges --count <tip> --not <main> <fix heads>` = 0 counts as covered (ancestor-class, counted in
  the summary line). Control: that ref's shape in a fixture is not reported; null control: a tip with one non-merge
  commit absent from main and every fix head is still reported; a tip whose merge commit carries a conflict
  resolution touching a file the fix head lacks stays reported (use `git diff` of the merge against its first
  parent). Mutant: dropping the --no-merges makes the fixture report."

---------------------------------------------------------------------------------------------------

## P2 update_pr.sh / app_push.sh body-only mode without the branch checked out

VERDICT: DEFER -> R10-FLOW-BODY-PATCH (not-started, files INSTRUMENTS.md + app_push.sh, after [], flagged expedite).
R10-FLOW-BODY-ONLY (update_pr.sh part (b), after UPDATE-PR-SIGNALS + BODY-PATCH) already owns the update_pr.sh side.
Not a new proposal: the group exists and is unblocked. The finding is that it is not dispatched.

Measured:
- Roster owns it three ways: BODY-PATCH ("Repair a pull request's body without moving its head ... no tool PATCHes a
  body alone"), BODY-ONLY (a body-only mode when the code sha is `-` and the head contains the handoff tip; no
  worktree commit), and a P22 carry on BODY-ONLY that makes update_pr.sh exit 75 (not 1) for "checked out elsewhere"
  so the relay retries instead of recording failure.
- Instances in the brief text: #2513, #2544, #2548, #2529, #2549 each had a clean head moved by a body fix (5), plus
  #2567 (interim proven, head 4ef1a827 unchanged), #2561, and #2589 at 11:40Z today (update_pr refused: train 21
  holds the branch worktree; re-body went to the merge seat on the train worktree). At least 8 in ~2 days, i.e.
  ~4/day; each head move costs a CI cycle and a re-review or a --carry (~40-60 min of wall time, one reviewer turn),
  each refusal like #2589's costs a seat dispatch (~10 min). Benefit ~3 h/day of pipeline wall time at the current
  rate. Cost is already priced into the roster (S/M, sonnet fixer, opus reviewer).
- The sentence in update_pr.sh that refuses is line 42: `git worktree list | grep -F "[$BR]" | grep -vqF "$WT "`
  -> "branch ... checked out elsewhere", exit 1.

Gap to carry (this is the useful part of P2): BODY-PATCH revision 18 says "use the branch's private update_pr.sh
worktree (a second worktree for the same branch is refused)". That design fails exactly the #2589 case, because the
merge train holds the branch checked out in its own worktree. A body-only repair needs no branch at all: it must not
check the branch out. Run the body contract and the PATCH from a detached worktree at the expected head SHA (or no
worktree: the body contract is offline over the body file plus the PR's tree at that sha), and the
check "live head == expected sha" is the only guard needed.

Binding constraint: identity (0011/0013): the PATCH must be minted as hpo-author through the same mint app_push.sh
uses (BODY-PATCH already says "factored out rather than copied"). No new policy.

Carry text for R10-FLOW-BODY-PATCH (append with roster_edit.py):
  "Triage P2 (s4): the instrument must work while another worktree holds the branch. #2589 at 11:40Z: update_pr.sh
  refused ('branch fix/r10-fly-gh-read-retry checked out elsewhere') because merge train 21 held the branch's
  worktree, and the re-body went to the merge seat on the train's worktree. Revision 18's 'use the branch's private
  update_pr.sh worktree' does not cover this. Run from a detached checkout of the expected head sha (or no checkout:
  contract over the body file at that sha), never `-B <branch>`, and never detach or remove a worktree the instrument
  did not create. Control: a fixture where another worktree has the PR branch checked out must still PATCH the body
  with the head unchanged; null control: a head that moved refuses before any write. Mutant: switching to
  `worktree add -B <branch>` makes the held-branch fixture refuse."
Priority note for the orchestrator: BODY-PATCH has no `after` edge and is the highest-value unstarted instrument
group in this batch; dispatching it ahead of lower-yield groups pays back within a day at the measured rate.

---------------------------------------------------------------------------------------------------

## P3 prepr replays the base-pinned policy lane locally

VERDICT: ACCEPT -> R10-FLOW-JIDOKA (not-started, tools/pr/prepr.sh, S, sonnet fixer / opus reviewer,
after R10-PREPR-CAP). Answer to the round-3 fixer of #2609: prepr does NOT already do this.

What prepr does today (prepr.sh steps 3e-3g, header at l.101-125, `pinned_graders`/`pinned_paths`/`pinned_touched`):
it runs the graders CI pins to the base on THIS head's copy (the push-to-main direction, #1633). It has the
detector for the other direction, `PIN_TOUCHED` (l.2699), but only uses it to decide whether to run brief_lint on the
head. Nothing runs the BASE's copy of the pinned checkers over the PR's tree, which is what the pull_request event
does in policy-docs, env-matrix and wave-script (governance.yml: 3 "Restore the check source from the base commit"
steps, PINNED = base.sha). Hence #2609 round 2: passed locally at its head, red in CI.

Measured:
- Instances this round: #2609 round 2 (policy-docs, env-matrix, wave-script, ~1 h on the stamp path); #2529
  (survey/SURVEY.md: policy-docs `pinned tools/policy/agreement_restore.py is unregistered` and
  `FIELD COVERAGE REFUSED`, same mechanism: base registry versus a new pinned file). 2 in ~8 days found, 1 more
  historically (#1633 R1a). Each costs one CI cycle plus one review round (~1 h wall, one reviewer turn).
- Exposure: 72 of 297 first-parent merges since 2026-10-14 (24%, ~9/day) touch a pinned-ish path
  (tools/policy/*.mjs|py, tools/pr/*, .claude/workflows/*.mjs, tests/{structure,entities,layout}.py, tools/audit/*.sh),
  and R10 not-started groups still edit them: R10-POLICY-LINT-FAMILY, R10-CI-LAYOUT-P2, R10-FLOW-BOARD,
  R10-RECORD-API-BUDGET, R10-FLY-BUDGET-LEAF. Realistic expectation: 3-5 further instances before round close.
- Run cost of the replay: `node tools/policy/policy_lint.mjs` measured at 15 s wall on this loaded box. The agreement
  and wave-script lanes are of the same order. The replay would run only when `PIN_TOUCHED` = 0 (the diff changes a
  pinned path), so ~1-2 min on ~9 PRs/day, zero on the rest. No API calls.
- Benefit: 3-5 avoided red cycles x ~1 h plus one reviewer turn each; the replay is what the pinned-job comment in
  prepr.sh says it should be ("the two verdicts differ exactly when the diff touches a pinned path").

Cost: S to M. Reuse the existing reader: `pinned_paths .github/workflows/*.yml` is the exact restore list; build in a
temporary worktree: `git worktree add --detach <tmp> HEAD`, overlay `git checkout origin/main -- <paths>` (CI's own
list shape), then run the lanes CI runs there (`node tools/policy/policy_lint.mjs`, the agreement lane, the
check-wave-script lane, the env-matrix lane). The inherent limit: a PR that must be base-incompatible by construction
(a two-step landing) will fail the replay; that is not a defect, it is the case the replay exists to name earlier and
the body's `## Red checks` can answer. prepr.sh is 2.7k lines and many groups touch it; keep the new step a function
beside 3f. Review rounds expected: 2 (opus reviewer, mutants for the overlay list and the PIN_TOUCHED gate).

Binding constraints: none new. 0012 revoked (0014). Decision 0013's base restore is unchanged (the replay mirrors it,
does not weaken it). The tests/structure ratchet measures python, not prepr.sh, so no budget pressure. Heavy
runs belong to CI (tvofi 2026-10-07), and this one is light enough to stay local.

Carry text for R10-FLOW-JIDOKA (append with roster_edit.py):
  "Triage P3 (s4): add the base-pinned replay to prepr. CI's policy-docs, env-matrix and wave-script restore the
  checkers from the base (governance.yml 'Restore the check source from the base commit', decision 0013) and grade
  the pull request's tree with them; prepr 3e-3g runs the head's copy of the same graders and never the base's, so a
  PR that edits a checker or adds a pinned file passes locally and reddens in CI (#2609 round 2, ~1 h; #2529
  policy-docs 'pinned tools/policy/agreement_restore.py is unregistered'). When PIN_TOUCHED=0, build a detached
  worktree at HEAD, overlay `pinned_paths .github/workflows/*.yml` from origin/main, and run policy_lint.mjs and the
  agreement and wave-script lanes there; print one `base-pinned replay` step line with the first refusal. Control:
  a fixture PR that adds a pinned file the base registry lacks must refuse locally; null control: a diff touching no
  pinned path skips the step with its reason; mutants: removing the overlay makes the fixture pass (the defect),
  and flipping the gate runs the step on an unpinned diff. Do not extend to jobs that run the head's copy (briefs
  already runs the head's)."
Sequencing: JIDOKA is after R10-PREPR-CAP (in-progress, same file). If the orchestrator wants this earlier, the
step is independent of the lease work and can be cut from a separate leaf, but the same-file conflict argues for
waiting.

---------------------------------------------------------------------------------------------------

## P4 Train auto-re-points the owner review after a clean recarry

VERDICT: ACCEPT, NARROWED (diagnose first, carry second) -> R10-TRAIN-OVERLAP-GRADE (queued, merge_train.py +
INSTRUMENTS.md, no `after`). Not accepted as stated: most of it exists, and the stated cause is unproven.

What already exists (merge_train.py on main):
- `--approval-carry` (run and batch; train.sh passes it through): after a recarry whose h0..h delta names no
  branch-own file, it re-posts the owner's latest APPROVED review at h with the prior body plus a carried-by line,
  re-reading the mandate at the merge moment (`_carry_owner_approval`, l.994-1032) and failing closed. It is
  attributable: the review is posted by the logged-in account (the orchestrator's tvofi login under the mandate),
  with the mandate id re-read, which is the same shape as the hand re-points.
- It is gated on `raise_hold(...)` returning raises, i.e. it covers budget-raise entries only. Other code-owned
  entries get a fresh mandate approval from approve() (l.1036-1062). Neither path matches what the hand re-points of
  #2580 did.
- The live train (pid 79285, queue27) is launched WITHOUT --approval-carry: `--ignore-red nightly-status
  --ignore-red delivery-status --overlap --mandate 6329234399 --bot-prs`. So even the existing flag is unused.
  For raise entries add it: free.

Why the proposal as stated is not enough:
- #2580 touches r10_seat_selftests_mutants.py, delivery/2580.md, INSTRUMENTS.md, cloud_relay.sh. None is a
  CODEOWNERS path (grepped .github/CODEOWNERS on main), so it is not code-owned and not a raise; the train logged
  `#2580 approved (app)` (the hpo-approver App) and then `merge attempt 1/8 ... refused: the base branch policy
  prohibits the merge` x8, then MAIN-MOVED. The truncation at 200 chars hides which requirement was unmet.
- The ruleset 23698884 pull_request rule: required_approving_review_count 1, require_code_owner_review true,
  dismiss_stale_reviews_on_push false, require_last_push_approval false, and
  `require_extra_approval_for_unattributed_changes: true`. The last knob is the likely reason a recarry (a merge
  commit pushed by the App) needs a fresh non-App approval at the new head, which the orchestrator then supplied by
  hand (tvofi reviews 5612257192, 5612987427, 5613250362, 5613520742 on #2580). I did not prove it. GitHub
  re-anchors approval commit_id across clean base merges (the merge_train docstring says so), which is consistent
  with the App approvals appearing at the newer head.
- Frequency (train logs, hpo-seats/r10s3/train2547/state*/train.log, 22 trains): 'policy prohibits' refusals in 4
  trains: state12 (1), state19 (9), state20 (1), state27 (16); MAIN-MOVED in 5 trains. So ~18% of trains hit it, 27
  retries in total, concentrated in two trains. On #2580 alone the hand re-points were 6 in ~4 h (08:09Z to 11:35Z),
  ~3 min each plus one gh write each, and each holds the car until the orchestrator acts (the merge only becomes
  possible after the re-point). Estimated 20-60 min/day of orchestrator time and car latency at this rate. Cost to
  build: one function generalised plus a diagnostic, ~80-120 lines with self-test arms in a 3.5k-line file that the
  destination group already edits; +1 review round.

Constraints (binding for the build):
- Attribution: the carried review must be posted by the orchestrator's login under the mandate and keep the
  existing carried-by line (prior review id, h0, mandate re-read). It must never convert an hpo-approver App review
  into an owner review (0011: an App cannot satisfy an owner review) and must refuse for policy-class files unless
  the mandate scope is `all` (budget_raise_gate's own constants, the GATE-READY predicate).
- Fail closed as the existing carry does: flag off, mandate not live at the merge moment, a branch-own file in the
  delta, no prior tvofi review citing exactly one mandate comment, or a read-back failure -> park, never carry.
- Not a licence to skip the verdict: a prior merge verdict at an ancestor must exist (ancestor check, as
  app_approve --carry does).

Carry text for R10-TRAIN-OVERLAP-GRADE (append with roster_edit.py):
  "Triage P4 (s4): the train's hand re-points. Step 1, diagnose: when `gh pr merge` is refused 'base branch policy
  prohibits', the train logs the whole stderr and the reason read from `gh pr view --json
  mergeStateStatus,reviewDecision,statusCheckRollup` plus the ruleset's pull_request parameters (not the first 200
  characters), and parks the car with that reason instead of retrying 8 times (this is the existing #2577 item).
  Measured: #2580 in train 27 was refused 8 times after `approved (app)`; it is not code-owned (no CODEOWNERS path),
  the ruleset has require_extra_approval_for_unattributed_changes true, and the orchestrator re-pointed it by hand 6
  times in 4 h. Step 2, only if step 1 shows the missing requirement is an owner/extra approval at the recarried
  head: widen `_carry_owner_approval` beyond raise entries to this refusal class, under --approval-carry, same
  conditions (clean recarry, no branch-own file in h0..h, prior tvofi APPROVED citing exactly one mandate, mandate
  re-read live at merge, byte-identical read-back). Controls: a fixture car refused for a missing approval at a
  clean-recarried head is carried and merges; null controls: a conflict-resolution delta, a prior review by the
  hpo-approver App, and a lapsed mandate each park with the reason. Mutants: dropping the delta check and dropping
  the live mandate read each redden an arm. Also: pass --approval-carry in the live launch (the 2026-10-22
  queue27 command line omits it)."
Interim, zero build: the orchestrator can stop hand re-pointing non-code-owned cars until `gh pr view --json
reviewDecision,mergeStateStatus` shows they need it (one gh read), and add --approval-carry to the next
train.sh launch for raise entries.

---------------------------------------------------------------------------------------------------

Summary table

| P | verdict | destination | measured benefit | cost |
|---|---------|-------------|------------------|------|
| P1 | DEFER (fold) | R10-FLY-ORPHANS-REWRITTEN | 1 false ORPHAN of 134 refs, 4.5 h on the board | ~6 lines in the group's own function |
| P2 | DEFER (owned, unblocked, dispatch it) | R10-FLOW-BODY-PATCH (+ BODY-ONLY) | >= 8 instances / 2 days, ~3 h/day of wall time | already in roster |
| P3 | ACCEPT | R10-FLOW-JIDOKA | 2 instances this round x ~1 h + 1 review round; 3-5 more expected | S/M in prepr.sh, 1-2 min only on pinned-path diffs |
| P4 | ACCEPT narrowed | R10-TRAIN-OVERLAP-GRADE | 6 hand re-points on one PR in 4 h; 27 refused retries in 4 of 22 trains | ~100 lines in merge_train.py, +1 review round |

---------------------------------------------------------------------------------------------------

## P5 A read-only study seat for the "Its components" figure (owner suggestion, 2026-10-22)

VERDICT: ACCEPT, with the timing changed: dispatch it NOW as input to R10-ARCH-DOCS-FIRST, not after
R10-ORCH-MACHINERY. Carry 4 on R10-ARCH-DOCS stays as the late re-verify. Not a new group.

Measured (git only; the figure is read from refs/tmp/p2609 = PR #2609 head, dev/README.md l.236-279, since #2609 is not on main
and dev/README.md does not exist on origin/main 47147487b):
- The figure has 24 edges. 13 touch only nodes that exist in the tree today (tick, orch, disp, seats, bus, relayp, relayh,
  roster, docs, hb, watch, owner, train, main). 11 touch a node tagged [target: ...] (beat 5, hold 1, ledger 3, model 1, kit 1).
  tools/audit/seat/{beatd.py, ledger.py} are not on main (ls-tree), so the target edges cannot be checked against code yet.
- Owner's suspicion is confirmed from the figure text alone, zero build: at least 6 edges read "is read by", against the
  owner's "writes or triggers" convention: tick-->orch, ledger-.->tick, roster-->docs, model-.->docs, kit-.->model,
  hold-.->relayh (and hb-->watch is "pushes a ref the watcher reads"). `orch` has no incoming edge and `owner` is a sink, so
  there is no entrypoint. (Count is mine, from the mermaid source; the study should classify each, I have not read the code each cites.)
- Owner-flagged, so the cost of a wrong arrow is already paid once: the figure went through #2609 review and the owner still
  finds it unreadable. I could NOT verify the "#2579 rounds 2 to 6" figure (dev/programme/delivery/2579.md is not on main; no
  local record found). I did not use it. Benefit stated without it: one review round (~1-2 seat-hours plus CI) per wrong
  arrow caught late, at an expected 1 round avoided.

Why the proposed timing is wrong:
- R10-ARCH-DOCS is the LAST stage (after 34 groups, incl. L-size R10-ORCH-MACHINERY, itself not-started with a design step and
  5 after-edges). A study dispatched on "ORCH-MACHINERY merged" arrives at the very end, and the figure stays misleading on main
  until then.
- R10-ARCH-DOCS-FIRST (queued, ASAP per owner; its carry 0 already says "document and draw the machinery's shape") is the group
  that redraws it first, and a design note for it exists (16954f0c, carry 2). The study pays most there: the fixer draws the
  edges once, correctly. The target nodes' edges come from the approved design (handoff/orch-machinery 09174d94e, review round 3
  APPROVE), which does not change when the code is built; the code check on those edges stays with R10-ARCH-DOCS carry 0 and 4.
- Overlap risk: the designer seat for ARCH-DOCS-FIRST may already cover edges. The study seat must read note 16954f0c first and
  only add what it lacks (edge table with file:line), not redo it.

Cost: one sonnet/medium read-only seat, ~1 seat-hour, git only, no API; one hand-off (note to the orchestrator, landed as a
carry body). No code, no policy, no new rule (0012 revoked by 0014). Optional second pass at R10-ARCH-DOCS: delta only,
~20 min, the existing carry 4 (1) already owns it.
Binding constraint: finding-propagation.md: the note must reach the FIRST fixer's brief before it dispatches (a carry, not a
PR comment). Roster writes are the orchestrator's (roster_edit.py). The study makes no repo write.

Study deliverable (as proposed, accepted): edge table (actor, target, verb writes|triggers, file:line); each current edge marked
right | reversed | missing | spurious, and "is-read-by" edges named as convention breaks; mermaid draft, top-down, one entrypoint
(owner or orchestrator dispatching a seat), stores grouped apart from actors, one-line legend; present-tree edges verified against
code, target edges against the design ref with the group that lands each.

Carry text for R10-ARCH-DOCS-FIRST (append with roster_edit.py; use @file and read back):
  "Triage P5 (s4, owner suggestion 2026-10-22): the 'Its components' figure (dev/README.md 'The orchestration machinery', landed
  by #2609) is redrawn from a study note, not from inference. A read-only study seat (sonnet, medium, git only) delivers
  <absolute path> before this group's fixer dispatches: an edge table (actor, target, verb writes|triggers, file:line), the
  current 24 edges each marked right|reversed|missing|spurious, and a top-down mermaid draft with one entrypoint and a one-line
  legend ('an arrow is writes-to or triggers, actor to target, never is-read-by'). Measured: at least 6 current edges read
  'is read by' (tick-->orch, ledger-.->tick, roster-->docs, model-.->docs, kit-.->model, hold-.->relayh), `orch` has no incoming
  edge. The fixer implements the draft; target-tagged edges name the group that lands them. Control: reversing one arrow of the
  draft turns the pin red (R10-ARCH-DOCS carry 4 (3)); the figure parses under dev/audit/harnesses/r10_mermaid_parse.mjs."
Carry text for R10-ARCH-DOCS (append to carry 4): "Verify the study note's target edges against the code at this merge base
  (after R10-ORCH-MACHINERY); delta only, the present-tree edges were verified by the study."

P5 OVERRULE (coordinator, 2026-10-22): timing changed from "now, feeding R10-ARCH-DOCS-FIRST" to "first step of R10-ARCH-DOCS, ahead of
its fixer". Reasons given: R10-ARCH-DOCS-FIRST is #2609, already in the merge train with its fixer finished, so no fixer brief is left
to feed; the owner said "No action for now, but fold in ... at the end of the programme". Logged in proposals.md. Triage seat's note:
the premise is accepted; the ACCEPT verdict stands. Consequences for the carry texts above: (1) the FIRST carry text is void, the
ARCH-DOCS carry carries the study; (2) the study then runs after R10-ORCH-MACHINERY has landed as a matter of the group's order,
so target-node edges can be checked against code, not only the design ref, and the "delta-only re-verify" sentence is moot; (3) the
6-reversed-edges / no-entrypoint figures remain starting evidence only, counted from the mermaid source at the #2609 head, not
re-checked against code; (4) the figure stays unchanged on main until the end of the programme, which the owner has accepted.

---------------------------------------------------------------------------------------------------

## P6 R10-CI-LAYOUT-P2 execution plan: the four added choices (EXECUTION.md, base 738d950aa)

Scope: the group is approved (DESIGN-P2 1371a0a6, plan/ci-layout 4a9b0975b); only (a)-(d) are ruled. Read: EXECUTION.md in full,
DESIGN-P2 §8-§10, cloud_relay.sh probe arm, tests/ci_budgets.json, the group's carries on handoff/audit-r10-roster. Calls: 0 gh.
Not on main today (ls-tree): tools/ci/*, sweep_driver.py, ci_probe.py (all built by P2a). 0012 revoked (0014).

(a) Split into P2a (inert engine) and P2b (cut-over): ACCEPT.
- DESIGN-P2 §8's "one diff" is about PR 2 versus phase 1 (PR 1 = ledger/record/nightly moves, no ruleset edit). It states no soundness
  reason against a pre-merge of new, caller-less files. The plan's own test holds: P2a changes no trigger and no check name, so it is
  green under today's 17 contexts (the only workflow edit adds instrument-self-tests steps).
- Benefit: P2b review surface about 4200 to about 2500 production lines; the two adversarial pieces (gate predicate, the ruleset
  instrument tvofi will run) get their own opus review; ruleset_cutover.py --dry-run can read the live ruleset days early; every probe
  stacks on a base that already has the engine. Fits the three-round rule (a PR past 3 rounds is split anyway; the plan keeps that fallback).
- Cost, from the plan: +1 FULL cycle set (P2a about 3 FULL runs), +1 merge, wall +1.5 h (plan's figure; critical path unchanged because
  P2a's review runs beside it), the freeze starts at the first probe-ref cut either way. Risk: dead code on main for about a day
  (0004, "correct and never run"), bounded by the self-tests wired into instrument-self-tests and the entities pin gate.py REQUIRED ==
  fixture gate_required.
- Binding conditions: (1) interface changes found by the live U0 probes (step 4, after P2a's verdict) land in P2b, not a P2a-prime;
  say so in P2a's body. (2) Record as a Plan amendment on #201 (the plan asks this itself). (3) P2a is code-owned, FULL, closure
  classification of tools/ci/ in the same PR (tests/entities.py "force the FULL suite"). (4) #2579 merges before P2a's glue, as planned.
Cheaper alternative: none that keeps the review benefit; a single XL PR is the thing the plan removes.

(b) New instrument tools/audit/seat/ci_probe.py for the uncovered GitHub writes: ACCEPT, trimmed, plus one blocking fix.
- Tools-live-in-repo (decision 0013, CLAUDE.md "Instruments": new reusable instruments land in tools/audit/seat, never only in
  /tmp) rules out raw gh by the orchestrator. Measured coverage today: cancel/rerun/dispatch fragments exist in 8 tools
  (push.sh 8 hits, a1_dispatch_arms.sh 7, cancel_superseded.py 6, contract_rerun.py, codeql_scope.py, merge_train.py, handoff_push.sh,
  approve_held_runs.sh), none as a reusable CLI; app_push.sh --branch-only refuses anything but batch/<name>. So the gap is real.
- Benefit: about 250 writes plus 900 polls in the plan; the instrument gives the audit log line per write, the /rate_limit refusal below
  20 % and the 60 s poll floor in one place. Raw gh from a sonnet probe-runner has none of these. A bare dozen of raw gh calls costs the
  orchestrator ~5 turns each to review; the instrument is paid once (300/200 lines, sonnet, one review).
- BLOCKING FIX: the plan names probe refs probe/ci-layout-<unit>. cloud_relay.sh's probe arm lists refs/heads/probe/* and treats every
  ref that is not probe/rev-* as OWED until disposed (cloud_relay.sh l.36-37, l.168-176). About 12 probe refs x several days would
  appear as OWED relay obligations on the tick board and in owed.log, and are exactly the "noise read as fact" class. Pick a namespace
  the relay and bus.sh do not enumerate (for example ci-probe/<unit>), add it to PUSHERS in ref_privacy.py and to prune_refs.py's
  deletion set, and amend DESIGN-P2 §10's ref names by Plan amendment. Control: a planted ci-probe/ ref leaves cloud_relay.sh probe_arm
  and bus.sh orphans output unchanged (null: a probe/foo ref is still OWED).
- Trim: keep in P2a only the subcommands used by more than one unit: push, dispatch, rerun-job, cancel, label, retarget, close,
  review, dismiss-review. Build sarif-upload, dismiss-alert (each used once, U6 cases 4-5, orchestrator-run security writes) and
  workflow-disable (rollback only) in P2b with U6, so P2a stays smaller and each security write is reviewed with its single use.
  Identity: review submit/dismiss must use the identity budget-raise-gate accepts under mandate 6329234399; an App review must
  never be what carries it (0011).
Cheaper alternative: reuse by extending cancel_superseded.py / push.sh; rejected, they are unrelated tools with their own contracts.

(c) Fan-out scale (16 cloud seats, 500-700 probe runs, about 7 FULL cycles, about 1350 API calls, 27.5 h): ACCEPT as a ceiling, with
three trims; not as a target.
- Plausibility: 70 probe events x about 95 run-min per head (FLY-ROW-HEAD-CARRY measurement: 11066 run-min over 116 PR head pairs)
  is about 6650 run-min, roughly 0.7 of a normal day's PR CI load (about 100 heads/day x 95), spread over about 27 h. Adds about
  60 % to runner load while it runs. The risk is not minutes, it is the installation rate limit: today's #2589 reds were
  rate-limit reds (validate-hacs, env-matrix) at normal load. The plan's guards are right (4 probes open, pause during a train, refuse
  below 20 % remaining, A1 <= 700/h projected); keep them as acceptance conditions, not intentions.
- Trims (each reduces seats or runs with no loss of a control):
  1. Seats 16 to about 11: U4+U11 (both are trigger-only conversions, 60+60 lines), U8+U10 (100+100 net), U9b+U9d+U9p in one seat
     after names are final (the plan already allows "1"); U1+U2+U7 is already merged. Each stays under the 400-line fixer bound.
  2. Model routing (route-seats-by-judgement.md): U6-lib and U0b are ports of measured scripts with existing oracles
     (measure/rev/alert_list.py and its mutants; the sweep self-test) = sonnet with oracle. That leaves opus for U0a, U0c, U9c
     (security setting), U5, U9a (A5 adversarial): 5 opus instead of 7. Reviewers stay opus.
  3. Probe runs: reuse the shared BEFORE twin across U4/U5/U6/U7/U8 (the plan does) and run the combined control once; do not
     re-take the twin unless main's layout moved a file the twin touches (the plan re-takes it "when main's layout moves", make that
     test explicit: git diff of the unit's files).
- Cost of the trims: zero controls dropped. Savings: about 5 seats, about 2 opus seat-slots, fewer hand-offs; wall time unchanged
  (critical path U0a-U0c-U0 live-U5 live-combined control-P2b review).
- Peak 7 of 8 seats is inside the cap (seat-cap-eight); the 27.5 h estimate is the plan's, unmeasured (est.).

(d) The ci-ratchet pair as new `tests / arch-instrument` job in U5, required through gate: ACCEPT, as its own sub-unit, with the claim corrected.
- Facts (tests/ci_budgets.json, group carry of 2026-10-21): critical_path_minutes budget 54.825; main was red at 57.6-58.9; tests/
  arch_score.py + arch_score_head.py are about 41 of `fast`'s 58 min on a slow runner; payment (a) put the pair in lane_golden and the
  plan reads the window at 49.86 median. So main is green now, with about 5 min (10 %) headroom against an observed +15 % runner
  variance. The plan's own sentence "nothing forces a payment before P2b" is right; the carry's "pay, don't raise" is not satisfied
  by a margin that variance can eat again.
- Benefit: `fast` drops about 41 min of work on the slow-runner case; a repeat ratchet red costs a held merge queue (the stamp path
  waits on a green main) and an orchestrator tick; evidence: one red on 2026-10-21. After P2b the metric is re-keyed to the
  `tests / *` span of ci.yml push runs (U9a) and the old window baseline is void, so the payment is cheapest while the job graph is
  open anyway.
- Cost: about 2-3 runner-min per code run for set-up (est., plan), one required context through gate (free: B3 REQUIRED covers it, no
  second ruleset PUT), run.sh lane-skip switch and "every script accounted for" accounting, ci_ratchet.py script_runs rows kept.
  The risk is coupling: U5 is already the largest cloud unit (350/150, opus). Make it U5b with its own seat or commit range, so a
  bug in the accounting cannot hold U5's tests.yml inputs.
- Acceptance as stated in the plan is right (P2b's own FULL: `fast` at least 5 min shorter than base's; after merge 5 of 8 push runs,
  never a re-run of a push run). Add a null control: the pair's script-runs rows still present (script_runs_per_push unchanged at 54);
  a mutant that drops the lane-skip makes `fast` unchanged (red). Do not describe it as "forced" in the body; describe it as headroom
  bought, with the numbers.
Cheaper alternative: leave the pair in `fast` and raise nothing. Acceptable only if the post-cut-over window shows >= 10 % headroom
over 8 push runs; that is a decision with no data until after the cut-over, so the sub-unit is the conservative path.

Summary: (a) ACCEPT. (b) ACCEPT trimmed, and rename probe/ci-layout-* (relay OWED noise). (c) ACCEPT as ceiling, trim to about 11 seats
and 5 opus. (d) ACCEPT as separate sub-unit U5b; the pair is headroom, not forced.


# Batch 2 (2026-10-22 ~21:00Z)

Seat: triage (sonnet, judgement with an oracle; contract = the draft seat definition at
/Users/timmalmstrom/hpo-seats/r10s4/triage2/seat-definition.md). Base measured: origin/main fd9914851, roster
origin/handoff/audit-r10-roster 26645ca88 (wave-r10-groups.json). gh calls: 0 (git, local logs, `git ls-remote`).
Decision 0012 is revoked (0014); no ruling below leans on it.

Summary: Q1 REJECT. Q2 REJECT. Q3 ACCEPT stands (P3 -> R10-FLOW-JIDOKA), no new carry; re-point two body lines.
Q4 REJECT (as worded). Q5 REJECT, reopen trigger named. Q6 ACCEPT NARROWED -> R10-FLOW-ARCH-PLANNER (policy text only).

---------------------------------------------------------------------------------------------------

## Q1 replan.py: a ready critical-path group is never held by the slot cap

VERDICT: REJECT. The scheduler already does what is asked; the slip was a dispatch decision, which is Q6.

Measured (git, tools/plan/replan.py at origin/main):
- `git show origin/main:tools/plan/replan.py | sed -n 15,23p`: list scheduling "longest-remaining-path first";
  heights() l.262-281 docstring says shortest-job-first "wrecks the critical path"; the ready-set sort at l.388 is
  `key=lambda n: (-height[n], n)`. Among PENDING groups the least-critical group is already the one held.
- Same docstring l.19-23: groups whose fixer is already working (stage `in-progress`) "start at the replan instant ...
  whatever their dependency state". An in-progress group cannot be held or pre-empted by a scheduler. So "hold the
  least-critical group when slots are full" can only act at dispatch time, in the orchestrator, not in replan.py.
- The 24.5 h figure (04:05 Fri vs 03:31 Thu) is real (proposals.md l.236-237) but it is the replan's honest read of
  "six groups in flight, SCORES not started". After the orchestrator dispatched SCORES the plan reads it as
  in-progress and the slip disappears without any replan change.
- R10-PLAN-ARTIFACT (the proposed home) is `in-progress` (fix/r10-plan-artifact, files plan_table.py + replan.py): a
  carry now widens a branch in review.

Cost of building it: a pre-emption or "critical group may exceed slots by 1" model in replan.py, plus a `--check`
rule, plus a second review round on a group already in flight. Benefit: none beyond Q6, which needs no code.
Binding constraint: the benefit is already delivered by the orchestrator's dispatch (Q6) and the scheduler's own
ordering; a model of the exception would let the plan promise a seventh slot the owner's cap (6, replan.py
DEFAULT_CAPS "slots") does not grant.
Reopen if: a replan prints a critical group late with a free slot (a scheduler fault). Null control: none seen.

---------------------------------------------------------------------------------------------------

## Q2 A ratchet payment the orchestrator grants must cut a dependency, not a count

VERDICT: REJECT. fixer.md and fix-review.md already carry the rule; the cost was the review catching it one round
later, which is what rule 14 is for. No orchestrator.md addition (policy file, and a self-grading gate).

Does fix-review rule 14 already cover it: yes.
- `git show origin/main:dev/governance/roles/fix-review.md` rule 14 (l.119-134): "Every number the diff moves is earned
  by the change, not the instrument"; remove the named mechanism; "then plant the diff's own kind of move on the same
  instrument with nothing improved. If it reproduces the movement, block". The #2620 review did exactly this
  (probe/rev-2620-62684c0b: `prices = self._prices` alias moved seam_cut_total to 706, archscore dS +0.0000 NULL).
- fixer.md l.236-250 (step 17): "`tests/structure.py` and `tools/audit/archscore/score.py --diff` not regressed";
  "An improvement claim names its mechanism, which the reviewer removes as the null control"; "Never move a metric by
  a change that does not improve the code: a mechanical split ...". CLAUDE.md rule 2 (budget-raise mandate) adds
  "moving, deleting, sharing or refactoring code that archscore, run before and after, does not read as worse".
- The fixer therefore already owes the before/after and the plant. The proposal asks the orchestrator to demand it
  again at grant time. orchestrator.md section 14 first bullet forbids "an automated gate that clears your own work";
  a grant-time plant is that, run by the party who granted the route.

Instances counted (orchestrator-granted route that review blocked as metric-gamed):
- `for r in $(git for-each-ref --format=%\(refname\) 'refs/remotes/origin/probe/*'); do git show $r:verdict.md | head -3 |
  grep -q metric-gamed && echo $r; done` over 171 probe refs: 2 hits, probe/rev-2620-62684c0b (orchestrator route 1)
  and probe/rev-2527-98e8d4b4 (the fixer's own _freq_view reflow, no orchestrator grant). Orchestrator-granted: 1.
  Pre-round history in rule 14: #1874, #1867, #1868, all fixer-side.
- Cost of the one instance: one fixer round plus one opus review round (proposals.md l.219-229), no wrong merge.

Cost of the proposal: a seat step on every payment decision (the proposing seat runs archscore + plant before the
grant), orchestrator.md text (file sits at its cap; zero headroom, so it must be paid by moving text), policy approval.
Binding constraint: 1 granted-route instance, caught by the existing gate at the existing price; marginal trade.
Practice, no policy: when granting a route, name the dependency it cuts and ask the fixer for archscore dS in the reply;
that is a sentence in a brief, not a rule.
The structure.py "counts occurrences, not distinct attributes" finding is the round-3 fixer's, routed to the owner of
structure.py; it is not a proposal and stays out of this ruling.

---------------------------------------------------------------------------------------------------

## Q3 Base-copy replay of pinned graders: one owner

VERDICT: ACCEPT -> R10-FLOW-JIDOKA, unchanged from P3. No new carry (the P3 carry text already names the agreement and
wave-script lanes and the overlay; appending again would route a duplicate). The instances raise its urgency, not its scope.

Existing carry to drop. Two places hold the duplicate route and neither is a roster carry:
- Roster: `R10-RCA-BODY-LINT` carry list at 26645ca88 is `[]`. Nothing to drop there. If an append-carry for the
  base-copy detector was run after 26645ca88, drop it. Do not route the detector to that group: its code is
  frozen at handoff/r10-rca-body-lint 5b27a11aa (prepr.sh +42, body_push.sh +21, policy_lint.mjs +6: the body lint,
  `--body-check`), its RCA record (dev/audit/rca/R10-RCA-BODY-LINT.md) scopes class N-body-lint-bounce, and a new
  scope after the handoff breaks the freeze (fixer.md).
- The P2a (#2622) body, `handoff-body/r10-ci-layout-p2a` BODY.md l.103, which reads exactly:
  "- **The agreement lane in `tools/pr/prepr.sh` runs the branch's copy**: CI's wave-script runs the base's copy of
  `tools/policy/agreement.mjs`, so a head can pass prepr and fail CI, as `19d36dcda` did. The cheaper detector is
  prepr running the lane against the base copy, as wave-script does. Carry: R10-RCA-BODY-LINT"
  Re-point its final marker to `Carry: R10-FLOW-JIDOKA`. The same marker ends l.93
  ("... Its standing cost is seconds. Carry: R10-RCA-BODY-LINT"): re-point that too. Re-take both lines from the live
  body before editing (the quote is the handoff-body ref's tip at this triage; the live PR body may differ).
- Optional, same group: JIDOKA's first carry is stale (0012 revoked by 0014; batch 1 recorded this):
  "Owner ruling owed first: whether running an existing checker earlier counts as a new lint class under decision 0012 (it is undefined there)."
  Drop it with `roster_edit.py` as a separate op; it blocks nothing today but invites a needless owner round-trip.

Instances (cite, don't carry):
- #2609 round 2, #2529, #1633 R1a: P3 (batch 1) figures, unchanged.
- #2622 P2a: handoff-body/r10-ci-layout-p2a BODY.md l.82 and l.93: base copy gave `UNREGISTERED "[0-9a-f]{40}"` at
  19d36dcda while prepr's branch copy read AGREEMENT ok; cost a fixer round plus a route decision (orchestrator log
  proposals.md l.239-243).
- r10-rca-body-lint: orchestrator log (proposals.md, request text) records the agreement lane refusing
  `DIVERGENT finding-class-id "N-body-lint-bounce"` and wave-script failing 1; the diff adds that class in
  dev/audit/config/bugclasses.json (`git diff --stat origin/main...origin/handoff/r10-rca-body-lint`). Not verified
  from a CI log in this triage (no gh call): taken from the orchestrator's statement.
- R10-CI-LAYOUT (done) carry 21 in the roster: "a program added beside a pinned grader is refused by the base's
  field_coverage registry ... no pre-push instrument runs the base's registry over the head". Same mechanism, third
  base-registry variant, parked on a done group (dead letter).
Total six, two on 2026-10-22. Interim cost: one agreement-lane line in every fixer prompt since 20:38Z plus the run
(seconds) by each seat, and nothing enforces it.

Priority: JIDOKA's only `after` is R10-PREPR-CAP, which is `done` in the roster, so it is dispatchable now (S, not
started). The "scheduled around 25 Oct" is slot order, not a dependency. Dispatch it at the next ordinary slot, not
over the cap: it is not shown on the critical path in anything read here. Sequencing hazard: it edits prepr.sh, which
the open RCA-BODY-LINT PR also edits; cut the JIDOKA fixer after the RCA-BODY-LINT PR merges, not in parallel.
Cost/binding constraint as P3 (opus review, 2 rounds, ~1-2 min of local run on ~9 PRs/day). Benefit at six instances
over about eight days, ~1 h and one reviewer turn each: clears the bar.

---------------------------------------------------------------------------------------------------

## Q4 Mutation null control killed by a flaky timing test

VERDICT: REJECT as worded (retry once, or exclude timing checks from the kill set). The flake itself is DEFER, with its
trigger named below; no group owns it today.

Measured:
- The test is tests/gate_lock.py:1547 "concurrency control: two waiters released in one poll, exactly one holds the
  slot" (`git grep -n 'released in one poll' origin/main -- tests tools`), driven through tests/entities.py. One
  instance (#2612 head 7b42306f, run 39838974680; the orchestrator's own count is 1, proposals.md l.248).
- tests/mutation_table.py treats a killed NULL_COMMENT as a refusal on purpose (docstring l.33 "if that null control
  dies"; the null control is built at l.2102-2129). The refusal is the instrument reporting that a check in the kill set
  is not deterministic. A retry-once would turn that report into a pass, and a kill-set exclusion list names checks by
  hand, which is a second source of truth for which checks are timing-sensitive.
- Cost of the instance: one CI rerun (the recarried head passed).
Binding constraint: weakens the control that proves the table honest, for one rerun's worth of cost. Marginal at best.
Reopen if: a second kill of a null control by the same test (then fix the test's timing: it belongs to tests/gate_lock.py,
the group that last owned it is R10-PREPR-CAP, done), or a third by any test (CLAUDE.md: root-cause.md, owed a
countermeasure or a recorded refusal). Do not edit the runner for it.

---------------------------------------------------------------------------------------------------

## Q5 bus.sh confirm across an autofix-only head move

VERDICT: REJECT. One refused confirm in 164 merged verdicts; the carry path the proposal wants to reuse already
carries the other 163. Reopen at three more.

Measured:
- Merges since 2026-10-14 with a verdict/N ref: `git log origin/main --since=2026-10-14 --merges --first-parent` joined
  to `git log origin/verdict/<N> --format=%s | sed -n 's/.*Fix review: merge \([0-9a-f]\{40\}\).*/\1/p'`: 164 PRs,
  all 164 merged at a head different from the verdict's V (train recarries plus bot pins), 20 of them with only
  autofix-class commits in V..head (e.g. #2612, #2608, #2600, #2595, #2485). So a posted verdict at V already survives
  a head move through `app_approve.sh --carry`; the failure is only when no verdict could be POSTED at V.
- That needs `app_comment.sh` to refuse (it requires a merge verdict at exactly the live head: app_comment.sh l.27-31,
  `die "head moved: ..."` l.68-69). Cases found: #2612 at 7b42306f (proposals.md l.221, `app_comment` refusal). The
  "earlier candidate" (a6e53320, l.194) was resolved by the ancestor-verdict rule before any confirm. Local logs
  (`grep -rh 'head moved: the merge verdict' ~/.local/state/hpo/merge_train` etc.) show no other refused confirm. Count: 1.
- Cost of the instance: one sonnet delta review (~20 min) plus a train relaunch.
- Bot pins are frequent (32 `ci: pin killed mutants` commits on main since 10-14), but a pin only collides when it
  lands between the review commit and `bus.sh confirm`: 1 of 164 verdicts.

Cost of the proposal: bus.sh `confirm` and app_comment.sh sit on the identity/verdict path (decision 0011); a relaxation
of "merge verdict only at exactly the live head" (fix-review.md step 12) is a policy-adjacent change with a posted
verdict naming a head the reviewer never read (the carry rule vouches for the delta; the reviewer did not). Needs opus
review rounds, mutants on both arms, and a text change in fix-review.md. Benefit: ~20 min once.
Binding constraint: 1 instance against a verdict-gate relaxation. If it recurs, the narrower design is to post the
reviewer's verdict at V (true to what was read) and let the existing `--carry V H` carry it, not to mint "merge <H>";
home then R10-FLY-CARRY-DISPOSITION (bus.sh + carry_audit.py, S, after R10-FLY-ORPHANS-REWRITTEN).

---------------------------------------------------------------------------------------------------

## Q6 Critical-path groups exempt from the drain-first soft cap

VERDICT: ACCEPT NARROWED -> R10-FLOW-ARCH-PLANNER, policy text only, no code. One sentence in
dev/governance/roles/orchestrator.md section 5, beside the soft-cap bullet. Not a new group, and not the sweep template.

POLICY FILE: orchestrator.md is policy (CLAUDE.md "where the policy is"); the owner, or the orchestrator under a mandate
in force with scope all, approves before merge. The change belongs in R10-FLOW-ARCH-PLANNER's fold-in, whose
deliverable (2) already rewires orchestrator.md (proposals go to triage) and which already merges after
R10-FLOW-DESIGN-POLICY (done) for that file. It must pay for the sentence by moving text: the file's cap
(dev/governance/config/policy_budgets.json, "dev/governance/roles/orchestrator.md" canon key briefs/orchestrator.md =
4513 tokens, no headroom).

Why accept, and why narrowed:
- The mechanism exists: orchestrator.md section 5 says `pr_cap.py dispatch-gate` "refuses at HPO_WIP_CAP (default 6)
  unless `--over-cap "<reason>"` says why", and pr_cap.py l.176-182 accepts it with a logged reason. The owner built the
  override; what is missing is which reasons are standing. Practice has already used it: R10-SCORES dispatched
  20:12Z (cloud-sessions.tsv l.30 "critical-path head, over drain cap"), then LOOP-CPU 20:38Z and RECORD-API-BUDGET 20:50Z.
- Benefit measured in Q1: 24.5 h on the critical path (Thu 03:31Z -> Fri 04:05Z), projected closure Wed 28 Oct 23:00Z ->
  Fri 30 Oct 03:11Z, from one held group. A session restarting without this sentence re-learns it at that price.
- Narrowing: the exemption is for a group that is a MEMBER of `critical_path` in the current plan (replan.py summary
  `critical_path [group...]`), ready (every `after` done, design verdict approved where the group has one). Not "feeds
  the critical path": the 20:38Z LOOP-CPU dispatch was justified as "feeds the critical path through LIVESTATE", which
  the rule as worded does not cover (membership not verified in this triage); it should have used `--over-cap` with
  its own reason. RECORD-API-BUDGET was a throughput lever (3 required-check reds/day), also a reason, not this rule.

Carry text for R10-FLOW-ARCH-PLANNER (append with roster_edit.py):
  "Triage Q6 (s4): in dev/governance/roles/orchestrator.md section 5, in the soft-cap bullet, state that a roster group
  that is a member of the current plan's `critical_path` and is ready (every `after` group done, its design verdict
  approved where it has one) is dispatched even at the cap, with `pr_cap.py dispatch-gate --over-cap "critical path:
  <group>"`; a group that only feeds the critical path takes the ordinary cap or its own --over-cap reason. One sentence;
  the file sits at its cap, so pay by moving text (CLAUDE.md rule 2). Measured 2026-10-22: R10-SCORES held ready behind
  the drain cap put it at Fri 23 Oct 04:05Z against Thu 03:31Z in plan rev 19 (24.5 h) and moved the projected closure
  from Wed 28 Oct 23:00Z to Fri 30 Oct 03:11Z; dispatched over the cap at 20:12Z. It is tvofi's 2026-10-20 soft-cap
  bullet made explicit, not a change to it; the pull request is policy, approved at merge. No code (pr_cap.py already
  takes --over-cap), no change to replan.py (Q1), no change to sweep_template.md."

Cost: ~40 tokens of policy moved, inside a PR that already edits the file; one extra approval sentence. Binding
constraint: the owner's drain-first ruling (tvofi 2026-10-20/21); the carve-out sits inside the clause he wrote
("unless --over-cap says why"), so it needs his or the mandate's approval at merge, which the PR needs anyway.
Interim: practice stands (it is within the written rule).

---------------------------------------------------------------------------------------------------

Time used: ~35 min. gh calls: 0.

---------------------------------------------------------------------------------------------------

# Batch 3 (2026-10-22 ~23:10Z)

Seat: triage (sonnet). Base measured: origin/main fef4a1351 (fetched), roster at origin/handoff/audit-r10-roster.
gh calls: 0. Constraint: 0012 revoked by 0014; both items are instruments under tools/, no policy file.

## P-A Cloud dispatch payload size: render a stub that points at a pushed ref

VERDICT: ACCEPT NARROWED -> R10-FLOW-DESIGN-STAGES (not-started, M, no `after`, files already include
tools/audit/seat/cloud_dispatch.py). Plus a cleanup carry to R10-FLY-PRUNE-REFS (not-started).

Measured facts:
- The ref half is already on main. R10-FLOW-DISPATCH is done. `dispatch_group()` / `--role R --group G --model M`
  publishes PAYLOAD.json and PROMPT.md as `dispatch/<role>-<topic>` and prints the ref name. INSTRUMENTS.md says "fire
  the standing trigger with the printed ref". 19 `dispatch/*` refs exist on origin.
- The missing piece: nothing renders the short trigger body. The ccr is resent whole on every trigger update (INSTRUMENTS.md,
  "every trigger update resends the full ccr"), so a standing trigger still needs a ccr whose prompt names the ref. Today
  the only output is the full ccr or the bare ref name. No `--stub` or equivalent exists (grep of cloud_dispatch.py).
- Volume: cloud-sessions.tsv has 35 fires on 2026-10-22. Brief plus carries of not-started roster groups: median 2.4 KB,
  max 28.9 KB, so the saving is concentrated in the large briefs (P2b-class), not the median.
- Not re-measured: the orchestrator's "about 35k tokens for 11 KB". 11 KB is about 3k tokens per copy, so 3 echoes is
  about 9k; 35k implies roughly 12 copies. Treat the figure as unverified; the direction holds at either number.
Ref-family cleanup cost (the question asked): a stub adds no new ref, since it reuses `dispatch/*`. But
prune_refs.py has no `dispatch/` or `brief/` rule (grep: only handoff/, verdict/, ci-probe/, archive/), so these refs are
residue that nothing deletes. 19 dispatch refs now, about 35 a day at the 10-22 rate, and 1 `brief/*` ref. R10-FLY-PRUNE-REFS
carry (ii) already guards "dispatch/* younger than 24h", which presumes a delete rule that is not there.
Cost: S inside an M group on the same file; one `--stub` arm, a self-test arm with null control (full ccr unchanged byte for byte),
a mutant. Benefit: orchestrator tokens per fire, 35 fires a day.
Binding constraints: (1) the seat then reads the brief at start, not at `run`; a brief edited between the fire and the seat's
fetch reaches the seat, which is acceptable but must be stated; (2) the stub must not carry host paths (ref_privacy, already
enforced for the ref); (3) cloud_dispatch.py is a hot file: R10-FLOW-DESIGN-STAGES also edits it, so one owner avoids a conflict.

## P-B tick_loop.sh runs stale code: freshness check

VERDICT: ACCEPT -> R10-FLY-RELAY-REVIEW-FF (not-started, S, files include tools/audit/seat/tick_loop.sh and cloud_relay.sh),
plus a forward-carry to R10-ORCH-MACHINERY's design (finding-propagation) because the same hazard moves to beatd.py.

Measured facts (origin/main tools/audit/seat/tick_loop.sh):
- It does no self-check at all. No `git` call, no SHA, no version in the banner or the heartbeat message. Each pass runs
  `$HERE/cloud_relay.sh pass` and `$HERE/orchestrator_tick.py` from whatever checkout it started in; only `tick_loop.sh` itself is
  read once. So a checkout never updates and every fix to those files is invisible to a running loop.
- The stale checkout 16a8240f1 (2026-10-22 08:11 +0200) is 506 commits behind origin/main fef4a1351; 119 touch tools/audit/seat and
  28 touch cloud_relay.sh, tick_loop.sh or orchestrator_tick.py. The hold check landed in cfa89d24f (R10-FLOW-RELAY-HOLD).
  A path filter on tools/audit/seat therefore cuts the restart rate from 506 to 119 candidates.
- Ownership: no group owns it. R10-RCA-ORCH-CONTINUITY and R10-FLOW-ANDON (tick_loop.sh, both done) cover liveness (heartbeat), not
  code freshness, so the heartbeat reads healthy while the code is old. R10-ORCH-MACHINERY (L, not-started) moves the relay to a
  launchd-supervised beat; its brief has no clause on which checkout the beat runs, so the hazard would carry over. FLY-RELAY-REVIEW-FF
  and R10-FLOW-AUTOTRAIN are the not-started groups on tick_loop.sh; REVIEW-FF is S and sits on the relay_start lines.
Design (narrower than the proposal):
- Do not fast-forward by default. The loop is documented as a read-only driver, and orch-wt is a worktree other seats may share
  (a dirty tree or a detached HEAD would make `merge --ff-only` fail or surprise).
- Each pass: `git -C $HERE fetch -q origin main` (a git fetch, no API) and count `HEAD..origin/main -- tools/audit/seat`. Put
  `code=<sha7> behind=<N>` in the TICK-PASS banner and the heartbeat message, so staleness shows off-host.
- If behind>0 and the tree is clean and `merge --ff-only` succeeds: `bash -n` the new tick_loop.sh, then `exec bash "$0" "$@"`. Otherwise
  print `TICK-STALE behind=N` and carry on (never exit: a stopped loop is worse than a stale one).
Null control: a throwaway origin whose main did not move prints behind=0 and does not exec. Mutant: drop the path filter or the
`bash -n` guard. Cost: S; one fetch per 300 s pass, 288 a day, no API.
Binding constraints: tick_loop.sh is measured by the mutant file (new arm takes a per-file id, e.g. tick_loop-N); a new git call
sites need no PUSHERS entry (fetch only). The exec guard matters: a broken main would crash-loop the driver, so the `bash -n`
check and the single re-exec per pass are part of the carry.

---------------------------------------------------------------------------------------------------

Time used ~20 min. gh calls: 0.

# Batch 4 (2026-10-23, triage seat)

gh calls: 0 (git on origin/main and origin/handoff/audit-r10-roster, local files).

## P-C Relay confirm gap: tick_loop's relay pass posts the verdict

VERDICT: Option A ACCEPT (already carried, no new group). Option B REJECT. Option C REJECT.
Recommended: A, as the P15 carry already in R10-FLY-RELAY-REVIEW-FF, with one added sentence.

Measured facts (origin/main):
- cloud_relay.sh already has the mechanism. `pass [--confirm]` runs `bus.sh confirm <pr> <review-sha>` after a
  PASSED push-verdict and logs `POSTED <utc> <pr> <sha>` or `OWED <utc> <pr> <sha|-> <why>` (lines 159-165; added in
  1acdb3cdc, 2026-10-18, with the stated reason "two verdicts once sat relayed and unposted for 20 minutes").
  It has a self-test arm (lines 356-380: confirm runs with the sha push-verdict printed; no confirm after a refused
  relay or a failed push-verdict; a failing confirm logs OWED).
- tick_loop.sh relay_start (line 63) runs `bash "$relay" pass` with no `--confirm`. That is the whole gap. So
  #2635 printed the "next: bus.sh confirm" line (cloud_relay.sh line 166, printed unconditionally) and stopped.
- orchestrator_tick.py relay_owed (lines 694-720) already prints `OWED:` for any OWED line in the relay log
  until a later POSTED for that PR. So with --confirm a failed confirm becomes a level line with no new code.
- Was confirm left out on purpose? No comment says tick_loop omits it. The only intent on file is the opposite:
  the --confirm header. The one real constraint is in bus.sh (lines 84-100, 385-390): confirm needs the
  hpo-approver key on the orchestrator's machine ("no App key in the cloud"). The tick loop and the relay both run
  there (pid 94539 on this host), and push-verdict already needs the dispatch record from the same machine, so
  identity is no obstacle. The softer point: bus.sh describes confirm as run "after the orchestrator has read that
  reviewer's own thread". --confirm replaces that read with the relay's checks (nonce, head, dispatch record, grammar).
  That trade was made on 2026-10-18 and the fold below is the same trade; surface it, do not relitigate it.
- Already carried: R10-FLY-RELAY-REVIEW-FF (wave 4, S, not-started, resume.stage not-started, `after`
  R10-TICK-OWED-LEVEL, R10-FLOW-RELAY-HOLD, R10-FLOW-ANDON, R10-UPDATE-PR-SIGNALS; files cloud_relay.sh, bus.sh,
  tick_loop.sh). Carry 1 (P15 fold, 2026-10-21) and the brief both say "tick_loop.sh relay_start passes --confirm to
  cloud_relay.sh pass". #2635 is the second measured instance of that carry, not a new proposal. Not done, so the
  carry has not landed; the running loop is also a stale checkout (P-B), so a landed fix reaches it only after a restart.

Costs:
- A: one token in relay_start (`pass --confirm`) plus one self-test line in tick_loop.sh (the stub relay logs its
  args; assert `relay pass --confirm`, null control: the `absent` case still ticks). About 4 lines. tick_loop.sh
  is mutant-measured, so the new line takes a per-file mutant id (drop `--confirm`, must be killed).
  Nothing in cloud_relay.sh changes. Latency: the verdict posts in the same pass (seconds), against 4 min of
  tick plus the relay seat's report plus a hand step (#2635: about 4 min after relay).
- B: the board must know "the PR has the hpo-approver `Fix review:` comment for that head". That is a per-PR
  GitHub read every tick (API, which the owner is sparing) or a local ref compare of review/<pr> against
  verdict/<pr> (no API, about 25 lines in orchestrator_tick.py plus tests). It only reports; a hand step remains.
  Rejected as the fix. As a backstop it is redundant: the OWED level above already covers a failed confirm, and
  `BUS unconfirmed` from bus.sh watch already covers a review/<pr> tip that was never confirmed.
- C: a rule from main, no code. A rule for a hand step cost the instance measured here, and "NOT CONFIRMED" came
  from the very seat the rule would burden. Rejected: it is the failure it describes.

Binding constraints for the carry: (1) --confirm only after a PASSED push-verdict (already so); (2) tick_loop's
relay is detached under a flock, so a slow confirm cannot hold the board (already so); (3) the relay seat's pass
must not double-post: the ledger line `<ref> <sha>` already stops a second relay, and confirm on an already
posted sha must be a no-op or a logged OWED, not a duplicate comment: assert that in the self-test.

EXACT CARRY TEXT (append to R10-FLY-RELAY-REVIEW-FF.carry; the P15 fold stays, this adds the second instance):
"Triage P-C (s4, batch 4, 2026-10-23, accepted as already carried): #2635 is the second measured instance of the
P15 fold. Probe landed 00:20:59Z, relayed 00:21:08Z, cloud_relay printed 'next: bus.sh confirm 2635 <review
commit>' and stopped; the verdict posted only when main ran confirm by hand about 00:25Z, after the relay seat
reported NOT CONFIRMED. Cause: tick_loop.sh relay_start (line 63) runs 'cloud_relay.sh pass' without --confirm,
although cloud_relay.sh --confirm exists (1acdb3cdc) and logs POSTED/OWED, which orchestrator_tick.py relay_owed
already prints as a level. Fix: pass --confirm in relay_start; one self-test line in tick_loop.sh (stub relay
logs its args; assert 'pass --confirm'; null control: relay=absent still ticks); a per-file mutant that drops
--confirm must be killed; add a cloud_relay.sh self-test case that confirm on an already posted review sha logs
OWED or no-ops and never posts twice. Do not build a CONFIRM OWED board line (Option B): OWED and BUS unconfirmed
already cover a failed or missing confirm. State in the PR body that --confirm replaces the orchestrator's read of
the reviewer thread with the relay's nonce, head and dispatch-record checks (decided 2026-10-18)."

Residual: the carry has no effect on the running loop until it is restarted from a checkout that has the merge (P-B).

---------------------------------------------------------------------------------------------------

Batch 4 time used ~12 min. gh calls: 0.

---------------------------------------------------------------------------------------------------

# Batch 5: 2026-10-23 ~10:50Z

Seat: triage (sonnet). Base measured: origin/main a6620c30a, roster handoff/audit-r10-roster. Six items (P-I with its
refinement, P-F recurrence, P-J, P-K, P-L, P-M). gh calls: 0 (git only, one `git ls-remote` of review/* and verdict/*).
Moratorium 0012 is revoked (0014); none of these needs a policy file.

## P-I (+ refinement) A cloud seat idles out holding unpushed work: push each verified step, to handoff-wip/<topic>

VERDICT: DEFER -> R10-FLOW-DESIGN-STAGES (not-started, wave 4, M, files cloud_dispatch.py + bus.sh among others).
Fold the text and its self-test row there. Interim, no code: the orchestrator puts the push-before-wait line in
every fixer re-fire brief by hand (already done for #2632).

Measured facts (git only):
- cloud_dispatch.py `_prompt`, fixer branch (lines 150-155), tells the seat to push the code to
  refs/heads/handoff/<topic> once, then body_push.sh, and "Push nothing else"; the tail says "Never write to any
  branch except your return refs". So no step push is licensed today, and a seat that obeys has nothing on GitHub
  until the end. The proposal's gap is real in the dispatched text.
- The refinement is right: cloud_relay.sh (lines 65-66, 175, 235) acts on handoff/<topic> moving and not being an
  ancestor of the PR head (it runs update), and lists only `refs/heads/handoff/*` and `handoff-body/*`. A step push to
  handoff/<topic> would move the PR head to an intermediate state, as #2632 showed. `handoff-wip/` matches neither
  glob, so the relay ignores it; `git grep handoff-wip origin/main` is empty, so nothing else names it.
- bus.sh orphans fetches only handoff/* and handoff-body/* (lines 509-510), so a wip ref is not listed as an orphan
  either: it is invisible to every sweep. That is what makes it safe and also what leaves it uncollected.
- Frequency: one measured loss (3.5 h, #2632 r4). I did not search the other s4 fixers for the same shape; a
  lower bound of 1.

Cost: S. One sentence in `_prompt`'s fixer branch (push after each verified step, fast-forward, to
refs/heads/handoff-wip/<topic>, before any wait on a background run; the final code still goes to handoff/<topic>),
one amended clause in the tail so the rule it states is not contradicted, one self-test row asserting the fixer text
names handoff-wip and the probe/reviewer text does not, and a null control (the reviewer payload is unchanged). The
fixer must also decide who deletes handoff-wip/<topic> (suggest the existing post-merge ref cleanup or
cloud_relay's final-handoff step) and check ref_privacy.py's push scan covers the new prefix; neither is in the
proposal. In the fold the marginal review cost is small because the group already rewrites `_prompt` for the designer
roles, whose text states "may push only to ..." in the same sentence family.
Benefit: removes the whole class "3.5 h of fixer work lost to a container idling", on every cloud fixer. Real but not
frequent; one instance.

Route: carry onto R10-FLOW-DESIGN-STAGES (cloud_dispatch.py `_prompt`). If main wants it before wave 4 starts, open it
as a fly group R10-FLY-CLOUD-WIP-PUSH (S, files cloud_dispatch.py, INSTRUMENTS.md) and drop the fold; both are cheap,
and the fold wins only because the file is shared.

## P-F recurrence #2 (+ `budget_raise_gate.py --check-body` run by body_patch.sh)

VERDICT: ACCEPT (route unchanged, priority raised). Destination stays R10-POLICY-LINT-FAMILY (not-started, wave 2,
S, no `after`): the P-F carry text is already in its roster carry list. Dispatch it ahead of the other not-started
instrument groups. The proposed `--check-body` mode is accepted as the mechanism, not as a second change.

Measured facts (git only):
- policy_lint.mjs and tools/pr at origin/main still contain no "Raise justification" or "Payments tried"
  (`git grep` empty), so the carry is still unlanded. R10-RCA-BODY-LINT (#2625) merged without it.
- The second instance fails a different clause of the same function: budget_raise_gate.py `justification()` (line
  410) takes the section from the heading to the next `#`/`##` line (lines 415-420) and then needs both
  JUSTIFICATION_PAID (line 137) and JUSTIFICATION_SCORE (line 138, a verdict word IMPROVES|NULL|WORSENS) inside it.
  Instance 1 broke the PAID clause, instance 2 the SCORE clause and then the section scope (a verdict word placed
  outside the section). One shared function covers all three; a mirrored regex in .mjs would have covered at most
  the clause someone had already seen. That is the argument for calling the gate's own function.
- body_patch.sh step 3 runs `policy_lint.mjs --pr-body` and `carry_audit.py check --body` and nothing from the gate
  (header lines 17-22). Making policy_lint call the gate fixes body_patch, pr-contract and prepr in one place; a
  second call in body_patch.sh would fix one of three and leave pr-contract blind. So `--check-body` belongs in
  budget_raise_gate.py (a small argv mode that reads a body file, calls `justification()`, prints the `why`, exits 0/1)
  and policy_lint.mjs shells out to it when the body has the heading or the PR touches *_budgets.json. body_patch.sh
  needs no edit.
- Frequency: 2 PRs / 3 refused or parked gate runs (#2633 once, #2647 twice, run40 and run41). The second parked
  run cost a 50 min CI wait. Both were found at train pre-flight, after the reviewer and pr-contract passed.

Root-cause trigger (defect-root-cause.md, read from origin/main): the red-check trigger was met at instance 1 (the
gate that refused it is a late check; a one-line regex over the same body is the cheaper detector and already existed).
Two recurrences do not change the route; they confirm it. They also add a process-state fact the fixer's RCA must
carry: instance 2 happened AFTER the countermeasure was known and carried, because the carry is not yet built, so the
state is (a) the process did not exist, with the interim hand rule ("run the section-scoped regex, require count 1") a
(b)-prone stopgap that failed once already. The roster shows `rca: []` on the group: the RCA is owed beside the fix in
its own seat, and the audit-class barrier (3 instances) is one recurrence away. Recommendation: (1) dispatch the group
now; (2) name the root-cause seat in the dispatch (the fixer is not the author of the RCA); (3) a third refusal before
it lands should be recorded as the barrier trigger, not as another P-F.

Cost: S, 40-70 lines: `--check-body` (about 15 lines in budget_raise_gate.py plus a self-test row for each of the
three shapes: bare `Payments tried:` heading, score line without a verdict word, verdict word outside the section),
the policy_lint.mjs call and its fixture; the policy_lint.mjs size budget may bind. Null control: a body with
`Payments tried: x` and `Architecture score: dS +0.1000 IMPROVES` inside the section passes.
Benefit: ends a 50 min parked-run class on every mandated raise PR (there will be more raises).

Route: R10-POLICY-LINT-FAMILY carry (existing text) + this amendment: "implement the shared check as
`budget_raise_gate.py --check-body <file>` and have policy_lint --pr-body call it; add the three shapes."

## P-J bus.sh watch should prune unconfirmed entries for merged or closed PRs

VERDICT: REJECT as worded. The mechanism it asks for does not exist in the tree, and its cause is being removed.

Measured facts (git only):
- `bus.sh watch` keeps no list of unconfirmed entries. watch_once (bus.sh lines 433-475 region) diffs the remote ref
  snapshot against `$S/refs` and prints one event per ref that moved or went, then rewrites `$S/refs`: each change is
  reported once. Nothing to prune. `BUS unconfirmed` is printed by `review_status`, once per review/<N> event with
  `--post` (line 321).
- `orchestrator_tick.py` and `tick_loop.sh` at origin/main contain no "unconfirmed" at all (`git grep -i` empty). The
  "tick seat reports BUS unconfirmed for open PRs each pass" is that seat's own hand-built scan, not tree code. The
  12 stale lines are in its output and are cured by the filter it already states ("for open PRs"): nothing in the
  tree to change.
- Remote state now: `git ls-remote` shows 60 review/* and 198 verdict/*; the only review ref with no verdict is
  `review/orch-machinery-design`, a design ref and not a PR. So the tree holds no stale unconfirmed PR review.
- The underlying delay (verdicts sitting 1 h unconfirmed) has the cause the P-C carry already removes:
  cloud_relay.sh has `--confirm` (1acdb3cdc), and tick_loop.sh relay_start does not pass it; R10-FLY-RELAY-REVIEW-FF
  carries the fix (triage P-C, batch 4).

Cost of the proposal as worded: it would add state to a stateless watcher (a PR-state read per ref, i.e. API cost
on a loop the owner is sparing) to tidy another seat's output. Benefit: none beyond the filter that exists.
If the real wish is "main is told a confirm is owed, as a level not an event": that is the OWED level in
orchestrator_tick.py (R10-TICK-OWED-LEVEL, done) fed by the P-C `--confirm`, not a bus.sh change.

Route: none. Close the loop with R10-FLY-RELAY-REVIEW-FF (P-C); tell the tick seat to keep the open-PR filter.

## P-K tools/plan/replan.py raises KeyError 'XS'

VERDICT: DEFER -> R10-FLOW-TOOLKIT-MODEL (not-started, wave 4, M, files tools/plan/replan.py, roster_lib.py,
roster_edit.py). Not R10-ORCH-PLANPAGE (files plan_page.py, state_docs.py: it reads the model, it does not own
durations).

Measured facts (git only):
- Defect is real. tools/plan/durations.json `sizes_hours` at origin/main holds exactly S 13.1, M 11.4, L 20.1, XL 30.2
  (no XS), and replan.py line 335 does `size_hours[G[n].get("size") or "M"]` with no fallback: any open group of size
  XS raises KeyError. The roster holds seven XS groups now (R10-FLY-WORKTREE-GC, -DAEMONIZE-ARGV, -CIPREDICT-LAYOUT,
  -CLOUD-SETUP-TOOLCHAIN, -YIELD-GUARD, -ENVMATRIX-NOREMOTE, -SUITE-ENV-FLAKES), so every replan would crash while any
  is open. The proposal's example group is among them. The overlay (XS = S/2) hides it for rev 22 only.
- Side note for the fixer: the measured numbers are not monotone (S 13.1 h > M 11.4 h), so "XS = S/2" is not derived
  from anything; the measured value should come from the durations measurement, with a stated n, and the fallback for
  an unknown size should be loud (a `size not in model` line), not the smallest size silently.
- replan.py line 814 has an embedded default table `{"S": 2.0, "M": 4.0, "L": 6.0, "XL": 8.0}` also without XS.

Cost: S inside an M group. A measured XS value or an explicit fallback, a refusal-or-line for any other unknown size,
two self-test rows (XS group renders; a size outside the table refuses or lines, never KeyError) with a null control (a
roster of S..XL only gives the same output as before). The group already extends the same plan model with --project;
doing it there avoids a second PR on replan.py (a hot file for three groups). Benefit: removes a crash on the planner
that runs the next wave's slot reservation.

Interim, because wave 4 may be late and every replan now needs the overlay: if the owner wants it sooner, a fly group
R10-FLY-REPLAN-XS (XS, files tools/plan/replan.py, tools/plan/durations.json) is cheaper than waiting and does not
conflict with FLOW-TOOLKIT-MODEL if that group is told to rebase on it. My recommendation is the fold plus the interim
overlay already in use, since replan runs by the orchestrator under overlay; I would open the fly group only if a
replan crashes in an unattended path. The tick mentions replan (orchestrator_tick.py, 4 lines, see its REPLAN
detection item: it names the owed action and does not run replan.py, as far as the grep shows), so the exposure is the
orchestrator's hand run.

## P-L ledger merge driver: add/add on tests/mutation_ledger/killed_by/*.json

VERDICT: DEFER -> R10-MUTATION-ANCHOR (not-started, wave 1, M, files tests/mutation_table.py, tests/entities.py;
it already owns the killed_by pins). Fix the cause at the writer, not the driver; keep the driver as the fallback.

Measured facts (git only):
- .gitattributes at origin/main sends only four whole-file ledgers to `ledgermerge` (mutation_budgets.json,
  structure_budgets.json, closures.json, bugclasses.json). `tests/mutation_ledger/killed_by/**` has no attribute, so
  two branches adding the same pin file take git's text merge and conflict (add/add).
- 2108 pin files exist under killed_by/survivor_triage at main. A pin file is flat: anchor, killed_by, old, reason.
  `reason` is built by `pin_entry` (mutation_table.py line 1196) as "Recorded by `mutation_table.py --pin-killed`
  against {ref}: ..."; 1324 pin files carry that sentence. The only field that differs between a bot's pin and a
  fixer's pin of the same mutant on different bases is `{ref}`, exactly the case reported.
- Cheapest sound fix: make two independent pins of the same mutant byte-identical, by not writing the base ref (or
  writing it at a place that is not part of the compared file, git history already records the commit). Identical
  add/add content merges cleanly with git's default merge, on GitHub too. A driver cannot do that: ledger_merge.py
  runs only where `--install` ran and the claim-files lesson stands (GitHub does not run it). It also covers the
  rc/failed counts only when the two runs agree, which holds for equal-anchor kills in the same suite.
- Caveat the fixer must measure: whether anything reads the sha in `reason` (entities.py R9-F10.13 block and the
  mutation_table self-test could). If so, the ledger_merge route is the fallback: a `killed_by/**` attribute plus one
  rule in ledger_merge.py (equal anchor, killed_by, old: take the newer; any other difference refuses).
- Frequency: one measured conflict (#2632, update_pr.sh stopped). It recurs whenever ci-autofix's killed-pin job and a
  fixer pin the same mutant, which fix waves with mutation proof make likely (not counted: one instance measured).

Cost: S, about 3 lines in pin_entry plus one self-test row (two pins of one mutant on different refs are equal) with a
null control (pins of different mutants still differ), plus the repin of nothing (existing files unchanged). The group
is already in the same function's neighbourhood. Fallback driver rule: about 30 lines and a self-test. Benefit:
removes an update_pr.sh stop (a human step) per collision.

Route: carry onto R10-MUTATION-ANCHOR: "make pin_entry's reason independent of the base ref (or prove why not);
add a self-test row; if the sha must stay, add `tests/mutation_ledger/killed_by/** merge=ledgermerge` and the
equal-anchor rule in tools/merge/ledger_merge.py instead." Note ledger_merge.py is not in that group's files; the
fallback adds it.

## P-M Phantom in-progress slots; flag STALE-SLOT

VERDICT: DEFER -> R10-FLOW-WIP (not-started, wave 4, S, after R10-FLOW-PULL, files pr_cap.py, orchestrator_tick.py,
INSTRUMENTS.md). This is the group whose brief is "the work the cap cannot see"; STALE-SLOT is the same count seen from
the other side (work the cap sees that is not there).

Measured facts (git only):
- pr_cap.py counts roster groups whose `resume.stage` is `in-progress` (WIP_STAGE, line 52; module docstring lines
  10-24) and reads open PRs as information only. It asks nothing of the PR list or the branch, and orchestrator_tick.py
  prints `WIP: N/6` from the same count. So a group left in-progress after its PR merged holds a slot until someone
  sets the stage; this is exactly the reported failure.
- Roster at a6620c30a: R10-REPLAY-LANE is in-progress with `branch handoff/r10-replay-lane`, `commit null`, and
  `next_step` still the dispatch text (never advanced); R10-UPDATE-PR-SIGNALS is in-progress, branch null, note
  dated 2026-10-20, and #2524 (fix/r10-pusher-reap, merge fd9914851) is merged on main. The other two named
  (SCORES, TOOLKIT-MEASURE) read `done` now, so main has already repaired those; two phantoms are still live.
  Caveat on UPDATE-PR-SIGNALS: #2524 may be one deliverable of a group whose note adds more, so "no open PR" alone would
  flag a group still owed work; the rule below handles that with the push-recency clause.
- Cause is the stage not being set at merge (done-before-reroute, state-docs-after-merge both name it). A detector is
  the cheaper layer; making state_docs.py auto-set `done` is a policy-shaped change (the owner approves stage rules)
  and I do not propose it.
- Cost evidence given: 18:21Z wave pushed, 3 real fix PRs open, ready queue idle about 2 h, 4 of the 6 slots phantom.

Cost: S in a group that already edits both files. Rule as proposed is right with one refinement: STALE-SLOT when a
group is `in-progress` AND has no open PR whose branch it owns AND its `handoff/<topic>` and `handoff-body/<topic>`
refs have not moved in 6 h (committer date of the ref tip, read after the one fetch the tick already does; no gh).
Null control: a group dispatched 1 h ago with no push yet is not flagged; a group with an open PR is not flagged. A
flagged group still counts toward WIP (the tick only lists it), so the tick never silently refills a slot a live seat
holds; the orchestrator sets the stage. About 40 lines plus fixture and a mutant. Benefit: ends hours of idle ready
queue; high leverage given 4/6 slots lost once.

Interim: the orchestrator sets stage on UPDATE-PR-SIGNALS and REPLAY-LANE now (roster edit by main; I did not touch
the roster).

Route: carry onto R10-FLOW-WIP with the 6 h refinement and the two example groups as the fixture.

---------------------------------------------------------------------------------------------------

Batch 5 time used ~25 min. gh calls: 0.

---------------------------------------------------------------------------------------------------

# Batch 6: 2026-10-23 ~12:25Z

Seat: triage (sonnet). Base measured: origin/main (fetched 12:2xZ), roster handoff/audit-r10-roster. gh calls: 0.

## P-N fixer returns fail at the opener's prepr (agreement lane, unpinned sites, budget-raise-gate Red checks)

VERDICT: DEFER -> R10-FLOW-JIDOKA (not-started, S, files tools/pr/prepr.sh + fixtures). Narrower than proposed:
mechanism (2) is already half built, and the default route (R10-UPDATE-PR-SIGNALS) does not own the path.

Measured facts (git only):
- tools/audit/seat/body_push.sh at origin/main ALREADY runs ci_predict.py (step 6d predictor) and
  `prepr.sh --body-check` (step 7, pr-body lint) before the push, and refuses on either (lines 17-44). It landed as
  2fe11ffbc R10-RCA-BODY-LINT (#2625) and 03c0766bf (predictor), 2026-10-22 ~20:25Z. So "body_push runs ci_predict but
  not the body lint" is stale for any fixer dispatched from a main at or after those; a fixer cut earlier (long cloud
  runs, #2620 r5 is one) predates them. Reported refusals may partly be old-base fixers: unverified, the proposal gives no
  base SHA per refusal.
- What is still NOT covered, by design in the code, and matches two of the three refusals:
  (a) agreement lane: prepr.sh lines 871-875 state it is deliberately outside the skip table (reads the branch's own
      first-parent merge-subject history); `--body-check` (lines 1283-1300) never runs it. Matches ORCH-LEDGER ("3
      unregistered shared grammars").
  (b) unpinned sites: --body-check header says "Step 6d's unpinned sites are not fed: the open still is". Matches
      INPUT-STALENESS ("10 ADDED UNPINNED sites", mutation predicted red).
  (c) #2620 r5 "budget-raise-gate not named in ## Red checks, intended issues not passed": body_line is reached, but the
      red history is "read at the open, never here" (offline), and the open passes issue numbers body_push cannot. Partly
      uncoverable offline; the Red-checks naming could be predicted from the diff (the changed *_budgets.json).
- open_pr.sh calls body_push.sh with `$ISS` (line 53), so the opener's own prepr is where the issues arrive.
- Option (1) of the proposal (fixer runs full prepr before return) is the "M1" the body_push header already rejected:
  "Seconds, where a full prepr here (M1) costs ..." (header line 20). Full prepr on a cloud fixer costs minutes to a
  heavy-gate lease; I recommend not re-opening M1 unless (a)/(b) cannot be made cheap.

Cost: S. In prepr.sh `--body-check`: run the agreement lane (agreement_py.py reads local git only, no network) and feed
step 6d's unpinned-site list (ci_predict output is already produced by body_push one step earlier), so the two classes
refuse at return. For (c): predict the Red-checks naming from the three-dot diff touching *_budgets.json. Failing
fixtures first: a head with an unregistered shared grammar must make `--body-check` (and so body_push) exit non-zero; a
head with an ADDED UNPINNED site and no `## Unpinned sites` disposal must too; null control: a clean head and a head
whose sites are disposed still pass. The policy_lint/prepr size budgets may bind. JIDOKA's brief ("stop at the source")
and files (prepr.sh + policy fixtures) fit; UPDATE-PR-SIGNALS owns update_pr.sh/cloud_relay.sh, which are the update
path, not the return path.
Benefit: each refusal at open costs one fresh cloud fixer round of 30-60 min on the critical path; three in an hour
(per the proposal; I could not verify it from git, the refusals are in seat logs). Worth the S.

Preamble half (option 1, softer): one sentence in cloud_dispatch.py's fixer `_prompt` -- "if `body_push` refuses, repair and
re-run; do not hand back a head it refuses" -- is already implied by the refusal. Not worth a separate carry; if wanted it
rides R10-FLOW-DESIGN-STAGES (owns cloud_dispatch.py).

Interim, no code: the orchestrator tells the opener-side seat to dispatch fixers from a fresh main so they carry 2fe11ffbc.

Route / carry text for R10-FLOW-JIDOKA:
"P-N (triage batch 6): extend `prepr.sh --body-check` (what body_push.sh runs) so a return is refused for the two classes
open_pr's prepr still refuses it for: (a) run the agreement lane (agreement_py.py; local git only) in --body-check; (b)
feed step 6d's unpinned-site list (ci_predict.py output body_push already holds) to the step-7d `## Unpinned sites`
disposal check; (c) predict 'budget-raise-gate not named in ## Red checks' from the diff touching *_budgets.json. Failing
fixtures first, one per class, each with a null control (clean head passes, disposed sites pass). Do NOT run full prepr in
body_push (M1 rejected in body_push.sh header). Measure each refusal's base SHA first: a fixer cut before 2fe11ffbc is not
a gap."

Batch 6 time used ~10 min. gh calls: 0.

---------------------------------------------------------------------------------------------------

# Batch 7: 2026-10-23 ~12:45Z

Seat: triage (sonnet). Base: origin/main fetched 12:3xZ, roster handoff/audit-r10-roster. gh calls: 0.

## P-O relay loop relays a probe but never confirms; a relayed-unconfirmed verdict is never retried

VERDICT: ACCEPT -> R10-FLY-RELAY-REVIEW-FF (not-started, S, files cloud_relay.sh + bus.sh + tick_loop.sh). Third
measured instance of the family that group already carries (P15 #2582, P-C #2635, now #2659 and #2632). Dispatch it
ahead of other not-started groups: it blocks the critical-path merge seat each time (~50 min here).

Measured facts (git only, tools/audit/seat at origin/main):
- The proposal's structural claim holds. cloud_relay.sh `relay()` writes the ledger line `$ref $sha` to
  cloud-relayed IMMEDIATELY after push-verdict succeeds (line 158) and only then runs `bus.sh confirm` (lines 159-165).
  `probe_arm` skips any ref+sha in the ledger (line 192) and `relay` refuses it with "was already relayed" (line 134).
  So if confirm fails or is skipped for ANY reason, nothing retries it: the ledger says done.
- Confirm failure is swallowed: `bus.sh confirm ... >/dev/null 2>&1 && posted || owed "... bus.sh confirm failed; run
  it by hand"`. The refusal text (e.g. "BUS undispatched", "no hpo-approver key", HTTP failure) is discarded; the OWED
  line carries no reason. The OWED goes to the relay log level, which only helps if the orchestrator reads it.
- Retry is safe: bus.sh `confirm` -> `post_verdict` refuses "already posted" via `$S/posted` (line ~320), and
  `review_status` already derives the unconfirmed state from refs plus the dispatch record. So a retry arm cannot double
  post (null control exists in the tree).
- I could NOT establish from git which branch of the code the 12:30Z failure took (no relay log in the tree). Candidates
  in order of fit: (1) confirm ran and failed -> OWED logged, ledgered, never retried (fits "relayed, never posted" and
  "later replay refused"); (2) the loop was running stale cloud_relay.sh (the P-B class, which tick_loop's freshness check
  also lives in this group); (3) confirm skipped because the probe was relayed by an earlier non-confirm call. The fix
  below covers all three; the fixer must first read ~/.local/state/hpo relay log for 12:2x-12:30Z and name the branch.
- Correction to the proposal's predicate: "the PR head is H" needs a gh call. Use only refs and the local dispatch record
  (what review_status already does): owed = review/<pr> tip exists, is dispatched, and not in `$S/posted`. No API.

Cost: S, about 30-50 lines. In cloud_relay.sh: (a) log the confirm stderr's last line in the OWED message; (b) a
`confirm_arm` in `pass` (after probe_arm): for each review/<pr> ref whose review commit is not in `$S/posted` and has a
dispatch record, run `bus.sh confirm` (idempotent), log POSTED, and keep the OWED level line until it posts; bounded
(not on every 120 s pass for a permanent refusal: back off, e.g. retry at most 3 times then OWED stays). Failing fixture
first: relayed probe + failing-then-passing confirm stub -> the second pass posts (via HPO_RELAY_CONFIRM stub, as the
self-test does for confirm). Null controls: a review already posted does nothing; an undispatched review is not
confirmed (confirm itself refuses, and the arm must log it OWED once, not loop). Mutants: drop the arm; drop the
posted-check. Overlaps P-C's existing carry (pass --confirm in tick_loop's relay_start); does not replace it.
Benefit: closes the class "relayed but unposted verdict stalls the merge seat" (4 instances in 2 days: P15 33/35, #2635,
#2659, #2632); each costs 5-144 min of the critical path plus a hand step. Highest-leverage S on the board.

Route: carry onto R10-FLY-RELAY-REVIEW-FF. Carry text:
"P-O (triage batch 7): a relayed probe is ledgered (cloud-relayed) BEFORE confirm runs, so a failed or skipped confirm
is never retried ('already relayed'). Add to `cloud_relay.sh pass` a confirm arm: for each dispatched review/<pr> whose
review commit is not in bus.sh's posted record, run `bus.sh confirm <pr> <sha>` (idempotent: post_verdict refuses
'already posted'), POSTED on success, bounded retries then OWED stays on the level; no gh call. Log the confirm failure's
last stderr line in the OWED message (today discarded to /dev/null). First read the 2026-10-23 12:2x-12:30Z relay log and
name which of: confirm failed, stale cloud_relay.sh, relayed by a non-confirm call. Failing fixture first (relayed probe,
confirm stub fails then passes, second pass posts); null controls: already-posted review does nothing, undispatched
review logs OWED once. Mutants: drop the arm, drop the posted check."

Interim: the merge seat should treat `BUS unconfirmed` for a PR it needs as its own trigger to run `bus.sh confirm`
rather than wait on the loop (as main did for #2632).

Batch 7 time used ~12 min. gh calls: 0.

---------------------------------------------------------------------------------------------------

# Batch 8: 2026-10-23 ~13:10Z

Seat: triage (sonnet). Base: origin/main fetched 13:1xZ, roster handoff/audit-r10-roster. gh calls: 0.

## P-P openers run stale tools from a stale main checkout

VERDICT: DEFER -> R10-FLY-OPENPR-ATOMIC (not-started, S, owns open_pr.sh). Not R10-FLY-NO-FOOTERS-PUSH-PATHS as
proposed: that group is in-progress and its files are handoff_push/body_push/ci_probe/app_push/ref_privacy (the footer
push paths); a stale-tools guard is a different concern and would widen a live group.

Measured facts (git only):
- The trigger instance is already fixed in the tree and is not itself a gap: delivery_row.sh at origin/main has no
  Co-Authored-By (01ee39a07 "stop the delivery-row and stamp commits writing a Co-Authored-By trailer",
  R10-FLY-NO-FOOTERS-EMITTERS, done). The failure was the invoking checkout holding the pre-fix tool; the class is
  "an opener runs whatever tools its checkout has".
- open_pr.sh sources `$(dirname $0)/delivery_row.sh` and pr_args.sh from its own directory (lines 14-17), derives the main
  checkout `$M` from git-common-dir (line 26) and then `cd "$M"`; the only freshness action is `git fetch origin main` +
  merge of origin/main into the PR WORKTREE (line 43), which updates the PR tree but not the tools being run. update_pr.sh
  likewise fetches main (line 44) and merges it into the PR branch, never compares its own tool tree. grep for
  is-ancestor against origin/main in either script finds only the unpushed-work check (update_pr.sh line 47). So nothing
  detects stale tools.
- Same hazard class as the tick_loop stale-checkout carries (P-B and the 07:10Z one, in R10-FLY-RELAY-REVIEW-FF): third
  place the class shows (tick_loop, cloud_relay, now open_pr/update_pr). Frequency here: 1 instance, 10 min.

Narrowing of the predicate (the proposed one over-fires): `git merge-base --is-ancestor origin/main HEAD` in the running
checkout fails for any seat branch checkout that has not merged main yet, and for a checkout legitimately developing
these very tools (a fly group editing update_pr.sh runs its own copy). Use the tool paths only: after the fetch, in
`$M` count `git rev-list --count HEAD..origin/main -- tools/audit/seat tools/pr`; refuse above 0 with
`STALE CHECKOUT <head> behind origin/main <sha> by <n> commits touching tools/audit/seat tools/pr`. That is the same
path-scoped count the tick_loop carry uses, so one helper serves both. Do not auto-pull (agreed: the main checkout is the
owner's, and must stay clean). Escape hatch: HPO_ALLOW_STALE_TOOLS=1 prints a notice and continues, for a fix that must
run its own pre-merge copy.

Cost: S, about 10-15 lines: a `pr_tools_fresh` helper in pr_args.sh (the one file both scripts source, so open_pr and
update_pr cannot drift) called after open_pr's fetch (line 43 region) and update_pr's fetch (line 44). Self-test rows
with a throwaway origin: tools behind with a change under tools/audit/seat -> refuses and names the sha; behind with a
change only under docs/ -> passes (null control, shows the predicate is path-scoped); HEAD at origin/main -> passes;
escape hatch continues. Mutants: drop the path filter (the docs/-only row must fail), drop the refusal. pr_args.sh is
also in R10-UPDATE-PR-SIGNALS' files (in-progress): the fixer must rebase on it and put the helper in its own function to
keep the merge trivial.
Benefit: closes a silent-wrong-tools class where the symptom is far from the cause (a red pr-contract and a stalled
review dispatch). Value is modest at one instance; it is cheap, and hand-fast-forwarding $M after every tools merge is the
alternative that already failed once.

Route: carry onto R10-FLY-OPENPR-ATOMIC. Carry text:
"P-P (triage batch 8): open_pr.sh and update_pr.sh run the tools of whatever checkout invokes them, and nothing compares
that tool tree to origin/main (a stale main checkout wrote a Co-Authored-By delivery row, #2664). Add `pr_tools_fresh` to
pr_args.sh (both scripts source it), called after each script's `git fetch origin main`: refuse with `STALE CHECKOUT
<head> behind origin/main <sha> by <n> commits touching tools/audit/seat tools/pr` when `git rev-list --count
HEAD..origin/main -- tools/audit/seat tools/pr` is above 0 in the checkout holding the tools; no auto-pull; escape
HPO_ALLOW_STALE_TOOLS=1 prints a notice and continues. Self-test rows on a throwaway origin: stale tools refuse; a
docs/-only difference passes (null control); fresh passes. Mutants: drop the path filter, drop the refusal. Rebase on
R10-UPDATE-PR-SIGNALS (also edits pr_args.sh); keep the helper a separate function. Reuse the path-scoped count the
tick_loop freshness carry (R10-FLY-RELAY-REVIEW-FF) defines, one helper if both land."

Interim: main keeps ~/heatpump_optimizer fast-forwarded after any merge touching tools/audit/seat or tools/pr (it did at 13:00Z).

Batch 8 time used ~10 min. gh calls: 0.

---------------------------------------------------------------------------------------------------

# Batch 9: 2026-10-23 ~13:45Z

Seat: triage (sonnet). Base: origin/main fetched 13:4xZ, roster handoff/audit-r10-roster. gh calls: 0.

## P-Q seat bodies pass prepr and body_push, then pr-contract refuses them on carry_audit

VERDICT: ACCEPT, folded into R10-FLOW-JIDOKA (not-started, S, files tools/pr/prepr.sh + policy fixtures) as item (d) of
the P-N carry. Not R10-FLY-OPENPR-ATOMIC / a body_push.sh owner as proposed: the one place both openers already share
is `prepr.sh --body-check`, so the call goes there, once.

Measured facts (git only):
- carry_audit.py `check --body` runs in exactly two places at origin/main: the pr-contract workflow (pr-contract.yml line
  ~400, "Every finding the body records names its destination", the job's last step) and body_patch.sh line 98, the
  post-open repair path. `git grep carry_audit` in tools/pr/prepr.sh, tools/audit/seat/body_push.sh and open_pr.sh is
  empty. So the proposal's observation is exact: the pre-open gate (prepr step 7 via body_push `--body-check`, the same
  step open_pr's prepr runs) never calls it. Two instances in 30 min (#2664, #2666), each cured by body_patch.sh with the
  head unmoved: the cheaper detector (body_patch's own call) already existed one step later in the same toolbox.
- Feasible offline: carry_audit is documented read-only ("`gh api` GETs, `git show`/`ls-tree`; nothing is written", header
  line 63) and reads the roster by `git show <ref>:...` through roster_lib; the checks in `--body-check` already assume
  `git fetch origin` happened. The pr-contract copy notes an O-brief is out of tree and passes UNVERIFIED there; the same
  holds locally, so no new false red. The "issue a live group or carry file owns" arm may call `gh api` for an issue state
  (Dests issue_state); the call in `--body-check` must tolerate a missing token the way the .mjs red-history does
  ("offline: read at the open"), and say UNVERIFIED rather than refuse.
- Caveat for the fixer: the two refused bodies had "Forward-carry: none" followed by prose. Establish from carry_audit.py
  whether a `none` item followed by explanatory prose SHOULD read UNROUTED (the audit is strict by design) or is an
  over-firing parse (memory: predicates that over-fire). If the parse is the defect, fix carry_audit.py's reading (in
  R10-FLY-CARRY-DISPOSITION's file, not-started) with a null control; if it is correct, only the pre-open call is owed.
  I did not read the two bodies (not in git), so I cannot say which.

Root-cause trigger (defect-root-cause.md): this meets the red-check trigger (a red pr-contract on a check a cheaper
detector could have run) at the FIRST instance, not the third; the proposal's "third instance triggers the RCA" is later
than the policy. Cause: --body-check was assembled from policy_lint's step list and carry_audit was left to the contract
and the repair path. Process state: (a) the process did not exist at the pre-open stage. The countermeasure is this
carry; the RCA is owed beside the fix in its seat (roster `rca: []` on JIDOKA). This is also the same class as P-N
(agreement lane / unpinned sites not in --body-check) and P-F (policy_lint's gate-justification regex): three instances in
24 h of "a pr-contract-time check missing from the pre-open --body-check", which is the audit-class barrier (>=3
instances owes a barrier, not another carry per member). Recommendation: JIDOKA's fixer builds ONE parity check, not
four calls: a self-test that enumerates the checks pr-contract.yml runs on the body (policy_lint --pr-body, carry_audit,
budget_raise_gate justification, agreement) and asserts `--body-check` runs each or names why not. That turns the
fourth member into a failing test instead of a fourth red.

Cost: S for the call (about 6 lines in --body-check plus self-test rows); the parity test is the extra S-M and is what
earns the barrier. Rows: a body with a `## Forward-carry` item naming no group -> `--body-check` exits non-zero; the same
body with `Carry: <live group>` or `dismissed: <reason>` -> passes (null control); a body with no carry section -> passes.
Mutant: drop the call. Benefit: one red pr-contract and one main body_patch repair per instance (about 10-15 min of
stalled review dispatch each, 2 in 30 min), and with the parity test the class stops recurring.

Route: carry onto R10-FLOW-JIDOKA, appended to the P-N carry. Carry text:
"P-Q (triage batch 9): `prepr.sh --body-check` (what body_push.sh and open_pr's prepr step 7 run) never calls
`carry_audit.py check --body`, which pr-contract runs and body_patch.sh runs after the open (#2664 and #2666 opened with
a '## Forward-carry: none' plus prose and went red at pr-contract; main repaired both with body_patch.sh). Add the call to
--body-check; refuse on UNROUTED, say UNVERIFIED (never refuse) where the check needs a token or an out-of-tree O-brief.
First establish from carry_audit.py whether 'none' plus prose should read UNROUTED; if the parse over-fires, fix it in
carry_audit.py (R10-FLY-CARRY-DISPOSITION owns that file) with a null control. Failing fixtures first: unrouted item
refuses; routed and dismissed items pass; no carry section passes. Mutant: drop the call. ALSO build the parity test: the
checks pr-contract.yml runs on a body (policy_lint --pr-body, carry_audit, budget_raise_gate justification, the
agreement lane) are each run by --body-check or listed with a reason, so a fifth missing check is a failing test. The
RCA for the class (three members in 24 h: P-N, P-F, P-Q) is owed beside the fix in its own seat."

Interim: unchanged, main's body_patch.sh repair; seats' briefs say "run `carry_audit.py check --body BODY.md` before
body_push" (one line, from the repo root) until the call lands.

Batch 9 time used ~12 min. gh calls: 0.
