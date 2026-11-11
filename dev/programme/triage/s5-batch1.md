# Proposal triage, session s5, batch 1 (P5-P33)

Session s4 kept its proposals and its draft rulings out of the tree: a
proposals ledger (`proposals.md`) and 25 draft rulings (`triage.md`, counted by
`rg -c '^## ' triage.md`) in the s4 orchestrator's scratch directory, plus one
assessor proposal routed to a done group (`roster/c2569.txt`). The first four
drafts are `s4-batch1.md` P1-P4. Every other proposal is re-ruled here from
`dev/governance/roles/proposal-triage.md`; an s4 verdict is a claim, re-derived,
not copied. Enumerated with `rg -n '^## ' triage.md` and
`rg -n -i 'proposal:|^P[0-9]+ \(|^## P|candidate:|recommend' proposals.md`,
then each hit read in place.

Base: origin/main `27b59c9f7`; roster origin/handoff/audit-r10-roster
`e4c92864f`, read with
`git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json | jq -r '.groups[] | select(.group=="<G>") | .carry[]'`.
"carry N" below is that list's 0-based index at `e4c92864f`. GitHub calls: 3
(`gh pr list --state open`, `gh pr view 2653`; nothing written).

Not ruled here, with the reason:
- The ledger's P1-P24 (2026-10-21) carry assessor `DECISION` lines made before
  decision 0015 (`b16084794`, 2026-10-22T21:58Z) and are routed already; ledger
  P5 is the c2569 item, ruled afresh as P30.
- Plan amendments and decisions (R10-TRAIN-OVERLAP-GRADE, R10-NIGHTLY-PYSPY-RETRY,
  the owner-disposition board line, the ruleset change, the R10-ORCH-MACHINERY
  re-cut, the R10-SCORES carries, P2b-pre): not proposals.
- The 19:26Z body-lint countermeasure is a root-cause countermeasure (merged as
  #2625), and the 21:35Z prune-refs defects were routed as a finding to
  R10-FLY-PRUNE-REFS: neither is a proposal.

A roster op citing an ACCEPT below resolves only once this file is on the
roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P5: a read-only study seat for the "Its components" figure
Verdict: ACCEPT -> R10-ARCH-DOCS (carry 5, landed; no op owed)
Source: s4 P5, owner suggestion (tvofi, 2026-10-22).
Instances: 1 owner-flagged figure. At origin/main dev/README.md lines 262-275
still hold the 6 edges drawn read-direction against the writes-or-triggers
convention (tick-->orch, ledger-.->tick, roster-->docs, model-.->docs,
kit-.->model, hold-.->relayh) and `orch` has no incoming edge; read with
`sed -n 236,282p dev/README.md`.
Cost: one sonnet read-only seat, about 1 seat-hour, git only, no API.
Binding: the owner asked for it and set the timing ("at the end of the
programme"); the seat writes nothing, so the cost is the seat alone.

## P6: R10-CI-LAYOUT-P2's four execution choices (split, ci_probe.py, fan-out ceiling, arch-instrument job)
Verdict: ACCEPT -> R10-CI-LAYOUT-P2 (delivered or in flight; no op owed)
Source: s4 P6 (a)-(d), the P2 conductor's EXECUTION.md.
Instances: (a) P2a merged as #2622 (`a1633381a`); (b)
tools/audit/seat/ci_probe.py is on main and tools/audit/seat/prune_refs.py
deletes its `ci-probe/` namespace (`rg -n ci-probe tools/audit/seat/prune_refs.py`),
the relay-noise rename s4 made a condition; (c) executed under its guards; (d)
open as #2665 (P2b-pre2, "the architecture-score pair gets its own job beside
fast").
Cost: as the plan stated; no further triage-owned cost.
Binding: each choice is already executed or in review inside the approved
group; re-ruling it would only re-open a design-approved plan.

## P7: replan.py never holds a ready critical-path group at the slot cap
Verdict: REJECT
Source: s4 Q1; the s4 log at 2026-10-22T20:12Z.
Instances: 1 (R10-SCORES, dispatched over the cap at 20:12Z). The scheduler
already orders the ready set longest-remaining-path first
(`rg -n -- '-height\[n\]' tools/plan/replan.py`: lines 367 and 388).
Cost: a pre-emption model in replan.py plus a check, inside R10-PLAN-ARTIFACT
(now done), so a new group.
Binding: the hold was a dispatch decision, and the owner's ruling now carries
it in dev/governance/roles/orchestrator.md line 100 ("A ready critical-path
group starts regardless of every cap"); a scheduler model of the exception
promises a slot the cap does not grant.

## P8: a ratchet payment the orchestrator grants must cut a dependency, not a count
Verdict: REJECT
Source: s4 Q2; the s4 log at 2026-10-22T19:55Z (R10-CURRENCY route 1).
Instances: 1 orchestrator-granted route blocked as metric-gamed
(probe/rev-2620-62684c0b); counted by s4 over the probe refs whose `verdict.md`
head names `metric-gamed`.
Cost: a grant-time archscore run and plant on every payment decision, plus
orchestrator.md text in a file at its cap.
Binding: fix-review.md rule 14 already plants the diff's own kind of move and
caught this instance at its normal price; a grant-time gate run by the granter
is the self-clearing gate orchestrator.md refuses.

## P9: base-copy replay of pinned graders, one owner
Verdict: DEFER -> owned by R10-FLOW-JIDOKA under `s4-batch1.md#P3` (carry 3)
Source: s4 Q3.
Instances: the same item as P3; its re-point actions are moot because #2622
merged.
Cost: none beyond P3's.
Binding: a duplicate of an ACCEPT already routed; a second carry would route
the item twice.

## P10: a mutation null control killed by a flaky timing test
Verdict: REJECT
Source: s4 Q4; the s4 log at 2026-10-22T20:55Z.
Instances: 1 (#2612, run 39838974680; the s4 ledger's own count). No second
kill recorded since in the s4 ledger (`rg -n -i NULL_COMMENT proposals.md`).
Cost: retry-once or a hand-named kill-set exclusion in tests/mutation_table.py.
Binding: both forms weaken the control that proves the table honest, for one
CI rerun. Reopen at a second kill by the same test (fix tests/gate_lock.py's
timing) or a third by any test (root-cause.md).

## P11: bus.sh confirm across an autofix-only head move
Verdict: REJECT
Source: s4 Q5; the s4 log at 2026-10-22T19:39Z.
Instances: 1 refused confirm (#2612 at `7b42306f`) against 164 merged verdicts
counted by s4 (`git log origin/main --since=2026-10-14 --merges --first-parent`
joined to each verdict ref's subject); no refusal line in the local merge-train
or relay logs.
Cost: a relaxation of the verdict-at-the-live-head rule on the identity path
(app_comment.sh, fix-review.md step 12), opus review rounds, mutants on both
arms.
Binding: a verdict gate relaxed for about 20 minutes once. If it recurs, post
the verdict at the head the reviewer read and let `app_approve.sh --carry` carry
it.

## P12: critical-path groups exempt from the drain-first soft cap
Verdict: ACCEPT -> R10-FLOW-ARCH-PLANNER (done; delivered by #2633)
Source: s4 Q6.
Instances: R10-SCORES held 24.5 h by the cap (plan rev 19 against rev 24, s4
ledger 2026-10-22T20:12Z).
Cost: delivered.
Binding: the owner's ruling (carry 5 of R10-FLOW-ARCH-PLANNER) superseded the
narrowed text, and dev/governance/roles/orchestrator.md line 100 carries it.

## P13: render the cloud dispatch trigger as a stub that points at a pushed ref
Verdict: DEFER -> owned by R10-FLOW-DESIGN-STAGES (carries 3 and 4)
Source: s4 P-A; s4 ledger 2026-10-22T22:53Z (RemoteTrigger payload echo), the
same item.
Instances: the token figure (about 35k per fire) is the orchestrator's
observation; s4 could not reproduce it from git (11 KB is about 3k tokens a
copy). The s4 log at 2026-10-22T17:22Z records the `--group` path plus a
3-line trigger prompt already cutting the echo from about 5 KB x4 to 0.4 KB x4
for every later seat; tools/audit/seat/cloud_dispatch.py's docstring says a
standing trigger that fetches the published ref "needs nothing else".
Cost: S inside an M group already editing the same render path.
Binding: the saving is already taken in practice; what is left is the fires the
`--group` path refuses (a reviewer with a hand brief), never counted. What
would change it: a count of fires since 17:22Z that still inline a brief, with
their sizes. The group's fixer weighs carries 3 and 4 against that count.

## P14: tick_loop.sh runs stale code
Verdict: ACCEPT -> R10-FLY-RELAY-REVIEW-FF (carries 2 and 5, plus one reconciling carry)
Source: s4 P-B; s4 ledger 2026-10-22T23:00Z (tick_loop.sh stale checkout), the
same item.
Instances: 2 -- ledger P4 (2026-10-21, a loop predating the relay decouple) and
#2626, whose head moved 4 times under a 30 h loop at `16a8240f1` whose
cloud_relay.sh lacked the hold check (s4 ledger 23:00Z). The open #2664
(head `1270ba9b9`) does not build it: handoff-body/r10-fly-relay-review-ff
BODY.md line 33 lists "the stale-checkout restart" as not built.
Cost: S-M, about 30-50 lines in tick_loop.sh, one git fetch per pass, no API.
Binding: a stale relay acts (it moved a reviewed head 4 times), so the cost of a
miss is review rounds. Carries 2 and 5 disagree (fast-forward and carry on,
against detached checkout and refuse the pass); the reconciling carry binds:
restart between passes from a detached origin/main, and when it cannot restart,
skip the relay arm and keep the board.

## P15: tick_loop's relay pass posts the verdict (--confirm)
Verdict: ACCEPT -> R10-FLY-RELAY-REVIEW-FF (carries 0 and 3; in flight)
Source: s4 P-C.
Instances: #2635 (s4 batch 4) after the P15 fold's #2582 case. Built on #2664:
`relay_start` runs `cloud_relay.sh pass --confirm`
(`git diff $(git merge-base origin/main origin/fix/r10-fly-relay-review-ff) origin/fix/r10-fly-relay-review-ff -- tools/audit/seat/tick_loop.sh`).
Cost: about 4 lines and a mutant, in review.
Binding: the verdict-to-post gap stalls the merge seat each time; the fix is one
flag on an instrument that already logs POSTED and OWED.

## P16: open_pr.sh leaves its PR worktree on the PR branch
Verdict: ACCEPT -> R10-FLY-OPENPR-ATOMIC (carry 1; no op owed)
Source: s4 P-D.
Instances: 2 -- #2632's opener worktree blocked merge trains run24 and run25
("already checked out"); the no-footers opener's retry refused after a
fetch-race stop (s4 ledger 01:10Z). Still open at main: `pr_exit_trap` in
tools/audit/seat/pr_args.sh runs `pr_reap` and `PR_AFTER_REAP`, and
open_pr.sh sets no `PR_AFTER_REAP` (`rg -n PR_AFTER_REAP tools/audit/seat/open_pr.sh`
is empty).
Cost: S, 10-20 lines in open_pr.sh, one self-test row, one file-scoped mutant.
Binding: each instance stopped a merge train; `--free-holders` cures only a
clean holder at the branch tip, not a stopped run's.

## P17: a cloud seat that ends without a return push goes unseen
Verdict: ACCEPT -> R10-FLY-RELAY-REVIEW-FF (carry 4; no op owed)
Source: s4 P-E.
Instances: 2 -- #2620's round-3 fixer ended 20:01Z with nothing pushed and was
unseen 6 h (s4 ledger 02:15Z); #2632's round-4 fixer idled 3.5 h holding
unpushed work (s4 ledger 09:05Z). Not built on #2664: its BODY.md line 34.
Cost: S-M, 40-80 lines and a fixture, git-only (return-ref age against the
dispatch time).
Binding: 9.5 h of silent fixer loss in two instances against a git-only check
in a group already editing the relay.

## P18: the pr-body contract does not run the raise gate's grammar
Verdict: ACCEPT -> R10-POLICY-LINT-FAMILY (carries 6-8; in flight as #2669)
Source: s4 P-F and its recurrence 2 (s4 ledger 08:4xZ and 09:30Z).
Instances: 2 PRs, 3 refused or parked gate runs (#2633 once; #2647 at run40 and
run41, the second after a 50 min CI wait). #2669 (head `763702294`) adds
`budget_raise_gate.py --check-body` and calls it from policy_lint
`--pr-body`; its body records the recorded sections refused by the gate's own
function.
Cost: in review.
Binding: each miss parks a train at pre-flight; the detector is the gate's own
function run earlier.

## P19: carry_audit counts a blocked verdict's confirmations as findings
Verdict: ACCEPT -> R10-FLY-CARRY-DISPOSITION (carry 3; no op owed)
Source: s4 P-G.
Instances: 1 -- #2645 parked at run37 on 8 unrouted items; s4 measured the
mechanism on origin/verdict/2645 `cbac2180d`: a flagged lead's `lead_flag` is
never reset at a heading (tools/audit/carry_audit.py lines 186-220,
`rg -n lead_flag tools/audit/carry_audit.py`), and a reset at a section change
takes the 8 to 1.
Cost: S, 5-8 lines in the item classifier and 4-6 self-test rows, in a group
already owning the file.
Binding: a false unrouted item parks a train; the fix is narrower than the
heading-name rule proposed, which would hide a real item.

## P20: cloud_relay's auto-update voids a reviewed and approved head
Verdict: ACCEPT -> R10-FLOW-ROSTER-FREEZE (carry 4; no op owed)
Source: s4 P-H.
Instances: 1 -- #2651 moved `2bb638af` -> `91e37c09` by the relay's handoff
arm, voiding its merge verdict and approval 5624790576 while queued (s4 ledger
06:5xZ). The arm at main skips only on ancestry, the hold file and the failed
record (`rg -n 'cloud-handoff-hold|HELD' tools/audit/seat/cloud_relay.sh`); #2664
does not touch it.
Cost: S, 15-25 lines in the handoff arm, one `git ls-remote` of verdict refs
per pass, four fixture rows.
Binding: the hunk is the one ROSTER-FREEZE already rewrites, so the marginal
cost is the fixture rows; each miss costs a re-review, a body re-take and a
re-approval.

## P21: a cloud fixer pushes each verified step to handoff-wip/<topic>
Verdict: ACCEPT -> R10-FLOW-DESIGN-STAGES (carry 5, plus one carry closing its open decision)
Source: s4 P-I and its refinement (s4 ledger 09:05Z and 09:20Z).
Instances: 1 -- 3.5 h of #2632's round-4 work lost to an idle container.
tools/audit/seat/cloud_dispatch.py's fixer prompt (lines 152-155) licenses one
code push at the end and then "Push nothing else"; `git grep handoff-wip origin/main`
is empty.
Cost: one prompt sentence, one tail clause, one self-test row with a null
control, inside a group already rewriting the same prompt.
Binding: carry 5 leaves the ref's deletion open, and an uncollected ref family
is the residue prune_refs.py exists to clear; the added carry makes the seat
delete its own wip ref after its final push, so the ACCEPT adds no standing
residue but one ref per dead seat.

## P22: bus.sh watch prunes unconfirmed entries for closed PRs
Verdict: REJECT
Source: s4 P-J (s4 ledger 09:35Z).
Instances: 12 stale lines, all in the tick seat's hand-built scan:
orchestrator_tick.py and tick_loop.sh contain no "unconfirmed"
(`rg -n -i unconfirmed tools/audit/seat/orchestrator_tick.py tools/audit/seat/tick_loop.sh`
is empty), and `bus.sh watch` keeps no list to prune.
Cost: state and a PR-state read per ref added to a stateless watcher.
Binding: nothing in the tree produces the lines; the delay behind them is P15
and P27, in flight on #2664.

## P23: tools/plan/replan.py raises KeyError 'XS'
Verdict: ACCEPT -> R10-FLOW-TOOLKIT-MODEL (carry 6; no op owed)
Source: s4 P-K (s4 ledger 10:25Z).
Instances: a defect, live: `jq .sizes_hours tools/plan/durations.json` holds
L, M, S, XL only, and replan.py line 325 indexes it with no fallback while six
not-started XS groups sit on the roster.
Cost: S inside an M group already editing replan.py.
Binding: a crash in the planner is a defect fix owed under policy, so this
ruling only confirms its route; until it lands every replan needs the overlay.

## P24: the ledger merge driver resolves add/add on killed_by pins
Verdict: DEFER -> owned by R10-MUTATION-ANCHOR (carry 1)
Source: s4 P-L (s4 ledger 10:35Z).
Instances: 1 -- update_pr.sh stopped on #2632. `pin_entry` in
tests/mutation_table.py writes the base ref into `reason`, the only field that
differs between two pins of one mutant; .gitattributes routes no
`tests/mutation_ledger/` path to the ledger driver.
Cost: about 3 lines in `pin_entry` and a self-test row, or a driver rule of
about 30 lines; unmeasured whether any reader parses the ref.
Binding: one instance and an unmeasured reader set. What would change it: a
second add/add stop, or the group's fixer showing no reader of the ref.

## P25: phantom in-progress slots, flagged STALE-SLOT
Verdict: ACCEPT -> R10-FLOW-WIP (carry 5; no op owed)
Source: s4 P-M (s4 ledger 10:45Z).
Instances: 4 of 6 slots phantom on 2026-10-23 with the ready queue idle about
2 h. Still live at the base: R10-UPDATE-PR-SIGNALS reads `in-progress`,
branch null, while #2524 merged (`git merge-base --is-ancestor fd9914851 origin/main`).
Cost: S, about 40 lines in pr_cap.py and orchestrator_tick.py plus a fixture
and a mutant, in a group already editing both.
Binding: an idle ready queue costs critical-path hours; the flag only lists, so
it cannot refill a slot a live seat holds.

## P26: fixer returns refused at the opener's prepr
Verdict: ACCEPT -> R10-FLOW-JIDOKA (carry 10; no op owed)
Source: s4 P-N (s4 ledger 12:18Z).
Instances: 3 reported, 2 read in the openers' state-dir logs:
`pr/r10-orch-ledger/p1.log` line 16 ("REFUSE agreement lane") and
`pr/r10-input-staleness/p1.log` line 63 ("REFUSE pr-body ... check `mutation`
is red"), each ending "app_push: REFUSE".
Cost: S in `prepr.sh --body-check`: the agreement lane and the unpinned-site
list, each with a failing fixture and a null control; no full prepr in
body_push.sh.
Binding: each refusal costs a cloud fixer round of 30-60 min on the critical
path, against checks that already run locally in seconds.

## P27: the relay retries confirm for a relayed, unposted verdict
Verdict: ACCEPT -> R10-FLY-RELAY-REVIEW-FF (carry 6; in flight)
Source: s4 P-O (s4 ledger 12:30Z).
Instances: 4 over two days (#2582, #2635, #2659, #2632), the last costing about
50 min of the critical path. Built on #2664: a confirm arm in `cloud_relay.sh
pass` with bounded retries (handoff-body/r10-fly-relay-review-ff BODY.md line 3).
Cost: in review.
Binding: highest-frequency stall on the merge path; the retry is idempotent on
bus.sh's posted record.

## P28: openers run stale tools from a stale main checkout
Verdict: ACCEPT -> R10-FLY-OPENPR-ATOMIC (carry 2; no op owed)
Source: s4 P-P (s4 ledger 13:02Z).
Instances: 1 here (#2664 opened without its row: a checkout 1706 commits behind
wrote a refused trailer), the third of the stale-tools class with P14's two.
Cost: S, 10-15 lines, one helper in tools/audit/seat/pr_args.sh sourced by both
openers, self-test rows with a docs-only null control.
Binding: the class has three instances on two surfaces; one path-scoped count
serves this and P14.

## P29: carry_audit check runs before the open
Verdict: ACCEPT -> R10-FLOW-JIDOKA (carry 11; no op owed)
Source: s4 P-Q (s4 ledger 13:35Z).
Instances: 2 -- #2664 and #2666 went red on pr-contract's carry audit at open;
the #2664 shape is on record at handoff-body/r10-fly-relay-review-ff BODY.md
line 89. The red-check trigger of defect-root-cause.md applies at the first
instance; JIDOKA's resume note names its root-cause topic.
Cost: about 6 lines in `--body-check`, plus the parity self-test over the checks
pr-contract.yml runs on a body.
Binding: a check pr-contract runs, missing from the pre-open gate, is the third
member of one class in 24 h with P18 and P26; the parity test ends the class.

## P30: a roster_edit.py self-test arm for two concurrent edits from one checkout
Verdict: REJECT
Source: the standing proposals assessor's P5 from the #2569 review
(`roster/c2569.txt`); ledger P5 (2026-10-21).
Instances: 0 since #2569 landed (R10-ROSTER-PUSH-RACE done at `3a9c6f849`, an
ancestor of origin/main). The race arms of the self-test already drive a rival
edit through the same checkout and assert the outcome: the rival survives, the
loser's edit reaches origin, the sha reported is origin's tip (the block under
"THE PUSH RACE" in tools/audit/seat/roster_edit.py).
Cost: a new group to carry it (the destination is done), a fixer, a review and
CI, about 1.5-2 h, for one assertion on the mechanism.
Binding: the outcome the arm protects is already asserted; the arm adds a test
of how, not of what, with no recurrence to price.

## P31: update_pr.sh leaves its worktree holding the branch
Verdict: DEFER -> owned by R10-UPDATE-PR-SIGNALS (carry 2)
Source: s4 ledger 2026-10-22T17:31Z, narrowed at 18:01Z (the train passes
`--free-holders` by default, or update_pr releases on exit).
Instances: carry 2 counts 3 (#2513, #2544, #2547); the 17:31Z case (#2580) is a
fourth.
Cost: owned there.
Binding: the group already owns the item; train.sh already accepts
`--free-holders` (tools/audit/seat/train.sh line 52), so the default is that
group's call.

## P32: merge seat and trains stagger reruns
Verdict: DEFER
Source: s4 ledger 2026-10-22 08:30 CEST (06:30Z).
Instances: the installation rate-limit reds of 06:27Z; the RCA (#2606) traced
the load to the governance record job walking the window per push, and #2629
(R10-RECORD-API-BUDGET, `97b4fddf2`) addressed that.
Cost: unmeasured.
Binding: the benefit is unmeasured after #2629. What would change it: an
installation rate-limit red after `97b4fddf2` attributable to reruns.

## P33: an approved record/autofix PR left open is flagged as owed
Verdict: ACCEPT -> R10-ORCH-LEDGER (new carry)
Source: s4 ledger 2026-10-22T09:20Z.
Instances: 2 -- #2599 undrained until delivery-status went red on #2580 and
#2601 (09:20Z); #2653 (head `fafcf2d32`) APPROVED, merge state BLOCKED, open
since 2026-10-23T07:46Z and still open at this triage
(`gh pr view 2653 --json createdAt,reviewDecision,mergeStateStatus`), with no
board line naming it.
Cost: one ledger entry kind and three fixture rows in the group building the
obligations ledger; reads the open-PR list the tick already fetches, no added
GitHub call.
Binding: an undrained record PR reddens other PRs' required checks and nothing
surfaces it; the ledger is the one owner of obligations (its brief refuses an
obligation with no ledger kind), so a second scanner is not an option. The
group's current handoff is frozen, so the carry rides its next pull request.
