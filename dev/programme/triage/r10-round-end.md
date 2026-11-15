# Proposal triage, round 10, round end: one batch over the instrument groups, the proposals and the local prototypes

Contract: `dev/governance/roles/proposal-triage.md` at `origin/main` `a39627da59` (the
once-per-round shape, #3451). One opus seat, read 2026-11-15 from 09:40Z to about 11:30Z.
Inputs, all read whole or grepped in full:

- the roster at `origin/handoff/audit-r10-roster` `80c1fb32c7` (the 47 groups whose stage is
  not `done` or `refused`, read with a script over `groups[]`);
- the round-10 orchestrator's sweep log `$HPO_STATE_DIR/s14/sweep.md` (2621 lines; no other
  session log named `sweep.md` exists under `$HPO_STATE_DIR/s*/`), its proposal list
  `$HPO_STATE_DIR/s14/proposals-r11.md` (PC-1113-01 to -23) and the earlier triage seat of
  2026-11-13 (`$HPO_STATE_DIR/s14/seat/triage-1113/RULING.md`, T1-T23, out of tree);
- `dev/programme/HANDOVER.md` (the prototype inventory, the friction counts, the proposal
  table), the round-11 handover's triage instruction (tvofi, 2026-11-15, verbatim: "it should
  triage all its instrument groups together with your proposals and local prototypes before
  starting instrument work, some might be unnecessary");
- the pickup seat's proposal `$HPO_STATE_DIR/r11/pickup/PROPOSAL.md` (read as a lead, never as
  a ruling; where this batch differs it says so);
- the process-convergence audit (`d5d7ff8187`, section 6) and the loop study
  (`$HPO_STATE_DIR/s14/seat/loop-study-1114/REPORT.md`, cards L1-L9).

This seat made no `gh` call, no roster edit, no push and no GitHub write.

**What is ruled where.** tvofi already ruled the process-audit cards P1-P14, R1-R3 and the
loop-study cards L1-L9; they are not re-ruled. What this batch rules is the **form**: which
group builds each card, which planned groups and prototypes are merged, replaced or dropped,
and each friction family's root cause. Every ruling below takes effect only when tvofi rules
its decision card. **tvofi ruled every card on 2026-11-15, about 09:50-09:57Z** (asked with
AskUserQuestion by the round-11 orchestrator); each ruled entry carries an `Owner:` line with his
verbatim choice. Every card took the recommended option except C9, which he answered in his own
words, and that changed P789 and P790. Two of his rulings in the same set are about production
work this batch does not rule, recorded here so they are findable: Q1 tvofi 2026-11-15 "Fold
into D4 design (Recommended)" (R10-COP-LEARNER-DRAW-FLOOR carries 6 and 8 go to the D4 design on
R11-INTAKE-R10-RESIDUE), and Q2 tvofi 2026-11-15 "Yes, measure then build (Recommended)" (#3602
carry 5: a default start price for a clamped install, measured first).

**Ruled once per instrument** (card L5). Proposals are grouped under the group that owns the
instrument they name. `merge_train.py` (58 accepted proposals in round 10, the loop study's
count) and `orchestrator_tick.py` are past L5's third-change threshold: no further patch is
ruled on either; their residue goes to the redesign that owns them (P754, P752).

**Bars applied.** A new proposal needs over 20% on a `ratchet-budgets.md` measure; a planned
machinery group keeps its place at 10% or more; unmeasured is DEFER; a root-cause
countermeasure, an owner directive and severity high skip the machinery bars (the contract's
own list). No proposal widens CI capacity. **The freeze:** from the v10.0.0 stamp a machinery
change merges only on a ground (`dev/audit/README.md`, "Production share"): it unblocks a named
`custom_components/` pull request, or fixes the required gate's red on main or a self-test red
its own pull request introduced. The R11-PRE groups are built under tvofi's 2026-11-13 ruling
("They should be fixed in the beginning of round 11 before the finders run"), which this batch
reads as the instrument window for them; a kept round-10 group outside that set names its
ground or waits for tvofi to open the window for it. He opened it for the two kept round-10
groups (O1, "Admit, built late": P755 and P761 join the pre-finder set, built after the R11-PRE
groups).

**Verdict words.** ACCEPT is qualified as BUILD (keep the group), MERGE into a group, or
REPLACE by a prototype (the group's work becomes tracking and self-testing it). REJECT is
qualified DROP (recorded `refused` with the reason). A merged group's own stage becomes
`absorbed`, the stage ten round-10 groups already carry, with the destination in its note.

Machinery figure at `a39627da59`, for every Cost line below:
`python3 tools/audit/machinery_ratchet.py --measure --head origin/main` printed
`nonproduction_merges 477`, `production 103`, `window 580`.

# Part A: the instrument groups

## P742: R11-PRE-MACHINERY-LIMITER, built first, with the loop-study policy text it owns

Verdict: ACCEPT, BUILD. First of the kept set (tvofi, 2026-11-14: "limiter first, write that in").
Owner: O2 tvofi 2026-11-15 "Mandate, if sound (Recommended)" (who approves the L2/L4/L5/L7/L8 text on this pull request)
Source: card P2 and P11 (audit section 6 row a2); the group's three carries; loop-study cards
L2, L4, L5, L7 and L8; intake carries 15, 22, 23, 41.
Instances: the ratchet binds nothing: 477 non-production merges against 103 production in a
580-merge window (command above), so 82% of the window is machinery; the audit measured the
ratchet at 90% of its window and triage ACCEPT at 61% with bar skips. On main none of the
following text exists: `git grep -n -i "one in, one out\|one-in-one-out" origin/main --
dev/governance` prints nothing; `proposal-triage.md` still lists `medium, high, major,
critical` as a bar skip (line 23 at `a39627da59`), which P2 narrowed to a red required check on
main or a blocked production pull request.
Cost: one policy pull request (M) for tvofi's review; caps touched: `proposal-triage.md` (its
cap was raised 36->40 lines by #3451), `ratchet-budgets.md`, `root-cause.md`,
`defect-root-cause.md`; the fixer prints each `--budgets` row. One merge, one machinery merge
counted.
Binding: every other kept group is built under the rule this group writes; building them first
would have to be re-judged.
Destination, merged in (each carry text verbatim on this group):
- L2 (delete, then self-repair, then narrow, a new refusal last) into `root-cause.md` section 5
  and `proposal-triage.md`; L4 (price induced work: 2.9 follow-up items per RCA, 0.22 hotfixes
  per machinery merge until L1 has data) into `defect-root-cause.md`'s cost test; L5 (rule
  once per instrument; the third accepted change to one instrument in a round owes a redesign
  decision) and L8 (machinery friction counted by family, analysed once per family at round
  end; product, release and outage defects keep their own seat at once) into
  `proposal-triage.md` and `defect-root-cause.md`; L7 (k at 0.8 or machinery hotfixes above 15%
  of code merges for two weeks: RCA seats record only, proposals are logged) into the playbook.
- intake 15 (MACHINERY-CAPS-RECORD-DOWN, P663): re-record `machinery_budgets.json` down at the
  group's base; 477 against its cap is the figure to re-measure.
- intake 22 (`pr_cap.py` reserves the ten production slots and prints open pull requests by
  class): the production-share rule's enforcement.
- intake 23 and 41 (policy-budget keys on a path the tree no longer has; the README naming a
  census directory without a cap or exclusion): budget-file hygiene in the same files.

## P743: R11-PRE-TOOLCHAIN-PIN, with loop card L3 and the stale-checkout items

Verdict: ACCEPT, BUILD, design first (L).
Source: card P1 (audit a1); loop card L3 (no group holds it: `git grep -c "L3"` over the
roster's unfinished groups finds it only in the loop-study evidence carry); L6(c); P757;
PC-1113-10's addendum; PC-1113-15; intake 32 and 148.
Instances: no `toolchain/stable` ref and no product-status split on main (`git grep -n
"toolchain/stable" origin/main` prints nothing). Stale tools checkouts: STALE CHECKOUT was 14 of
22 opener failures over 29 h (P627's measurement) and 8 of 25 opener attempts (P581); the
2026-11-13 train ran from a checkout 3314 commits behind main (sweep line 1907). L3's shape:
the introduced-red guard refused reviewer dispatch while `instrument-self-tests` was still
running on #3481, #3557, #3558, #3566, #3568 and #3574 (sweep lines 1758, 1970), each 10-40 min
per head; the push-time ci-ratchet failed closed on a cancelled prelude on four main pushes in
a row (intake 148).
Cost: L, Fable designer and reviewer (owner ruling for L work); touches workflows (code-owned),
`beat_jobs.py`, `stamp.py`, `orchestrator.md`. Standing cost: one ref and one promotion step.
Binding: L6(c)'s revert is a pointer move only under a pinned toolchain; every instrument that
reads "is my checkout current" changes meaning under it.
Destination, merged in: L3 (one helper: an unreadable machinery input reports `unread`, three
in a row escalate; product checks keep failing closed); PC-1113-15 and intake 148 as L3's first
two uses; P757 (R10-FLY-OPENER-STALE-ENV: the design states what STALE CHECKOUT means under the
pin; its HEAD-keyed retry and `open_driver.py retry` verb are carried as acceptance cases);
R10-SEAT-IDENTITY-P5 carry 5 (BEAT-CHECKOUT-ROTATION-BY-HAND); PC-1113-10's addendum (nothing
refuses a train or relay launched from a checkout far behind main); intake 32
(MAIN-CANCEL-BOUNDED: seven consecutive main runs cancelled, first concluded run 4 h 55 min
after #3315), because main's readable status is this card's.

## P744: R11-PRE-ROUND-METRICS, narrowed by what is on main, widened by L1 and P7

Verdict: ACCEPT, BUILD (M).
Source: cards P3 and P8 (audit a3, a7); its four carries (decision 0018 sections 2, 4, 5); card
P7 (`$HPO_STATE_DIR/s14/seat/process-cards/carry-p7.txt`: caused_by and found_by, "build it
once, with this group's convergence records"); loop card L1 (its own text: "Fits
R11-PRE-ROUND-METRICS"); R10-TICK-RESIDUE-P3 carry 8; intake 174 and 176.
Instances: the scorecard's beat row is already on main (`tools/audit/seat/beat_jobs.py:138`,
the `scorecard` row, daily), so that half of P3 is built; the input producer, lead-time
percentiles, time-to-restore and the token line are not (`grep -n -i
"percentile\|time.to.restore" tools/audit/seat/scorecard.py` prints nothing;
`round_metrics` is in no tracked file). P8's live-value alert is not built (`bottleneck_check.py`
re-prints its first line verbatim, line 35). `found_by` and `cm_kind` are in no tracked file.
Cost: M; one daily beat job (about one REST batch); about 300 lines for L1's enumerator (the
card's estimate); no capped file.
Binding: decision 0018's terms `lead_time`, `product_green`, escapes per owning dimension and
the loop's k are NO-READ without it, and the finders cannot be scored.
Destination: this group, with L1's four fields and enumerator (prototype
`$HPO_STATE_DIR/s14/seat/loop-study-1114/data/`), P7's fields on hotfix and outside groups, and
TICK-RESIDUE-P3 carry 8 (a beat row alarming on a `ci.yml` run at attempt 20 or more:
root-cause countermeasure B of R10-RCA-SWEEP-SETTLE-LOOP, 1089 bot re-attempts on 2026-11-08).

## P745: R11-PRE-TOKEN-LEDGER

Verdict: ACCEPT, BUILD (M), after P755's host-wide call log.
Source: card P4 (audit a4); its three carries.
Instances: no token record exists; the audit measured coordination at about 89% of local
tokens and the s14 orchestrator at 4.34 B tokens over 36 compactions (proposals-r11.md,
PC-1113-06); decision 0018 prints `tokens_per_change` NO-READ while one seat class is
unledgered.
Cost: about 150 lines and a daily job (audit's estimate); `cloud_dispatch.py` is shared with
P752, admitted by seam (the dispatch header only).
Binding: none beyond 0018's NO-READ.
Destination: this group, unchanged; its brief's measure-first step (is cloud usage readable per
session) stays first.

## P746: R11-PRE-RULINGS-FILE

Verdict: ACCEPT, BUILD (M, policy).
Source: cards P6 and R3 (audit a5, a8); P5's remainder.
Instances: no rulings file in the tree (`git ls-files dev/programme | grep -i ruling` prints
only triage records); the audit counted 3 re-asked rulings and 112 hidden index entries; the
memory index is 192 lines today (`wc -l` on it), under the 200-line load cut but over P5's
150-line target, so P5 (out of tree) is partly done.
Cost: M, one policy pull request; the compaction hook's proof grows by one file and shrinks by
reading instrument pages by change (R3); `--budgets` rows for `orchestrator.md` and
`CLAUDE.md`.
Binding: every later group's dispatch rests on rulings a compaction can lose.
Destination: this group; P5's remaining work (index under 150 lines, superseded entries out)
is the orchestrator's own act, out of tree, named in the group's body.

## P747: R11-PRE-OBJECTIVE-FUNCTION is done; close it

Verdict: LOG (no build): set `done`, mark carries 0-5 implemented at `4eea986a62`.
Source: the roster (stage `carries-open`, six pending carries); #3575.
Instances: #3575 merged as `4eea986a62` (`git log --first-parent --oneline origin/main | grep
"#3575 "`). Carries 0-4 are the owner's requirements the group's own body answered: decision
0018 holds sections 1 (the terminal objective), 4 (from a perfect round to perfect code) and 5
(honesty) (`grep -n "^## " dev/governance/decisions/0018-objective-function.md`). Carry 5
(the playbook pointer to the evaluator contract) is landed: `dev/audit/README.md:30` names
`evaluator.md`. Its forward carries already sit on P744, P745 and R11-INTAKE-R10-RESIDUE
(intake 173-178).
Cost: two roster ops.
Binding: while it stays `carries-open` the pickup prints it every round start.

## P748: R11-PRE-SHARED-FILES, widened by L9 to the four generated artifacts

Verdict: ACCEPT, BUILD, design first (L). Its first part needs no new design (below).
Source: card P9 (audit b1); loop card L9 (owner: yes); P762, P763; PC-1113-10, -18, -19;
intake 12, 13, 162, 184, 194; the selftest-scope-drift and figure-block families
(`dev/audit/rca/R10-RCA-FAMILY-SELFTEST-SCOPE-DRIFT.md`,
`dev/audit/rca/R10-RCA-FAMILY-FIGURE-BLOCK-STALE.md`).
Instances: shared files touched by 94% of production merges and 3.61 main absorbs per pull
request (audit b1). The self-test table: 27 of 255 first-parent merges since #3315 touched
`tools/ci/selftest_closures.json` (`git log --first-parent --format=%h ba6fd7e8b0..origin/main
-- tools/ci/selftest_closures.json | wc -l`; `git rev-list --first-parent --count
ba6fd7e8b0..origin/main`), nine of them hotfix re-records. Figure blocks: 10 pull-request reds
in two days (family record). Claim files: three hand merges after the 2026-11-14 stamp
(PC-1113-18).
Cost: L, Fable; the design owes how `tests/structure.py` and the closure rules stay enforced
when the files are generated (the brief's own condition). One merge per part.
Binding: L9's own text: it "would make R10-SELFTEST-SCOPE-UNION-GUARD and its deferred round-11
sibling unnecessary"; every round-10 drift hotfix was a hand edit of a generated table.
Destination: this group. **Part 1, before the design of the rest:** the self-test table, cut
from countermeasure A of the self-test drift analysis, which already states its demonstration:
`record` unions (P762's union half), then a bot re-records refused steps from main's own run
(P763). The other three artifacts (figure blocks, brief line pins, the stamp line of the claim
files) are the design's.

## P749: R11-PRE-HANDOFF-BOOKKEEPING, owner of carry, body and red-check mechanics

Verdict: ACCEPT, BUILD (M, policy).
Source: card P10 (audit b2); PC-1113-01, -04, -17, -20; R10-PROCESS-SLIM carry 0;
R10-RELAY-NOBODY-STALL arm 3 and carries 0, 1, 3; R10-TICK-RESIDUE-P3 carries 9, 12, 13, 17,
19, 25, 33, 34; R10-OUTSIDE-CONTRIBUTOR-CYCLE carry 5; intake 11, 17, 30 (items 1, 2, 6), 38,
73, 193; the friction family carry-fold (2).
Instances: bookkeeping blocks 42% of verdicts (audit b2). Cloud fixers stopped on
CARRY-LANDED three times on 2026-11-13 (PC-1113-01, sweep line 1818); the relay's carry-fold
level held 65 owed topics against 6 folded on 2026-11-11 (RELAY-NOBODY-STALL arm 3); carry_fold
lost the roster push 3 of 3 against a 21-op drain (TICK-P3 carry 33); roster_sync appended 39
of 312 body items twice (TICK-P3 carry 17); 15 gating heads each needed one body patch for an
inherited red (PC-1113-20); one privacy-refused body was kept on origin (PC-1113-17).
Cost: M, one policy pull request (`fixer.md`, `fix-review.md` change); `--budgets` rows for
both; the PC-1113-17 arm is a few lines in `body_push.sh` (`keep_refused` skips a
`ref_privacy` refusal).
Binding: PC-1113-17 is a privacy defect: a refused body must write nothing to origin.
Destination: this group with all of the above. TICK-P3 carries 12 and 13 are roster-data repairs
the orchestrator does at the pickup, not code: carry 13 is already implemented
(`roster_queue.replay_unsafe`, `tools/audit/seat/roster_queue.py:186`), so mark it; carry 12's
four carries are restored only if their destination group is still live. Intake 11 and 73 are
copies of this group's carry 0/1 (`ci_predict.py` reads a local roster ref): marked duplicate.

## P750: R11-PRE-RELAY-REBUILD, absorbing the relay residue and the update-path holder

Verdict: ACCEPT, BUILD (M).
Source: card P12 (audit b4); PC-1113-03; R10-RELAY-NOBODY-STALL arm 1 and carries 2, 5 (P756);
R10-UPDATE-PR-SEAT-WORKTREE (P760); R10-TICK-RESIDUE-P3 carries 11, 18, 21; intake 4, 37, 87;
sweep candidates at lines 1522, 1562, 1626, 1751; the relay-serial-update family
(`dev/audit/rca/R10-RCA-FAMILY-RELAY-SERIAL-UPDATE.md`); the prototype `relayc.sh` (P792) and
the detached watch-mode relay.
Instances: seven stalls of the serial pass inside one `update_pr.sh`, up to 1 h 34 min (family
record); a fire that pushed code and never a body was 124 of 628 fires (19.7%) over
2026-11-04..11, median 174-196 min to re-fire (NOBODY-STALL arm 1); retired seat worktrees held
`update_pr.sh` at BUSY, 40 min and 32 min waits (P760).
Cost: M; `cloud_relay.sh`, `tick_loop.sh`, plus `update_pr.sh`'s holder loop (P760's seam).
The NOBODY-STALL brief's three stale line pins (`cloud_relay.sh:765`, `:808`, `ledger.py:609`,
the pickup's brief_lint read) are re-pinned in this group's brief, not on the absorbed one.
Binding: a verdict waits behind an unrelated pull request's full pre-PR check; the owner ruled
the fix (P12).
Destination: this group. Retires the second detached relay. The landing chains stay
session-local until P789's benchmark reads (card C9).

## P751: R11-PRE-ACK-COMPLETION, absorbing the owed-line residue of the tick

Verdict: ACCEPT, BUILD (M).
Source: card P14 (audit section 8, b6); PC-1113-02, -22; R10-TICK-RESIDUE-P3 carries 1, 4, 6,
7, 14, 16, 22, 23, 24, 27, 28, 30, 32; intake 170, 181; the prototype `wake_filtered.sh` (P791).
Instances: 2368 OWED-ACK lines, 134 keys re-acked five times or more, one 142 times (audit);
13 groups idle up to 61 h with no board line (sweep line 1825, PC-1113-02); a gantt accept
without expiry hid a 44 h closure slip (TICK-P3 carry 32, severity high); verdict_audit dropped
71 of 300 `FIRED` ledger lines and printed false UNHELD (carry 24); the round-11 orchestrator
re-armed `wake_filtered.sh` at its start (sweep line 2622) because repeated levels woke it
about once a minute (sweep line 1531).
Cost: M as briefed; the absorbed items make it large for one part: the fixer splits by file
(`orchestrator_tick.py`, `owed_unactioned.py`, `verdict_audit.py`, `gantt_drift.py`), at most
five carries a part (light text carries excepted, PC-1113-08).
Binding: an ack that never closes is a level, not a decision; the orchestrator's wake is driven
by such levels.
Destination: this group. Carries 14 and 23 are one item (23 supersedes 14). Intake 170/181
(refuse the round start while a pickup line has no disposition) joins as the same "an owed item
names its closing event" shape; see P795 for the policy half.

## P752: R11-PRE-STANDING-SCRIPTS, re-sized L, the dispatch prototypes as its specification

Verdict: ACCEPT, BUILD, re-sized L, design first; in part REPLACE by the dispatch-seat
prototypes (P792).
Owner: C8 tvofi 2026-11-15 "L, design first (Recommended)"
Source: card R1 (audit 2.2, the removals list); `dev/audit/README.md`'s opening carry "Retire
the merge and dispatch seats into beat jobs" (R10-STANDING-CONTRACTS-P2 carries 9, 12-14, "size
L, design first"); PC-1113-06 (as design input, P772), -07, -08, -09 (P773); R10-RELAY-NOBODY-STALL
arm 2 and carries 0, 4 (prompt text); R10-TICK-RESIDUE-P3 carries 0, 2, 3, 5, 15, 20, 26, 31
(below); intake 28/76/152 (`roster_lib.is_hotfix`), 35 (MERGE-PR-NO-REPOST), 42.
Instances: standing seats took 66% of local seat tokens (1.42 B in s14); the dispatch seat was
recycled five times on 2026-11-13 and three more times on 2026-11-14/15 (`dispatch-s15-2` to
`-5`); every dispatch round 10 closed on ran through `disp.sh`/`disploop.sh`/`verify.sh`
(their STATE-HANDOFF files).
Cost: L (the README already says L); the roster says M. Re-size before dispatch. Touches the
standing contracts (owner review).
Binding: the brief is M while two rulings on the same work say L and design first; dispatching
it as M would hand a fixer a design.
Destination: this group. The design owns the L5 redesign decision for `orchestrator_tick.py`:
TICK-P3 carries 0, 2, 3, 20 and 31 are its input, not build items (carry 3 is re-measured first;
carry 31 is a HANDOVER sentence for the next record pull request). TICK-P3 carry 15 (the
critical-path and outside watch row, owner directive) is built first in this group, and carries
5 and 26 (record line read back before raising Owed) with the merge operation.

## P753: R11-PRE-PLAN-RENDER, with build_tabs.py as its prototype

Verdict: ACCEPT, BUILD (S); in part REPLACE by `build_tabs.py` (its carry 2 already says so).
Source: card R2; its three carries; PC-1113-05; sweep candidates at lines 1131 and 2356;
R10-TICK-RESIDUE-P3 carry 10; the plan beat's refusal after the stamp (sweep line 2584); the
local timeout raise in `$HPO_STATE_DIR/s14/beat_extras.sh` (sweep line 1196).
Instances: 498 PLAN.html commits in 13 days (audit); stage-word liveness cost about 12 h of
planned closure and drifted 1 h per hour (sweep line 1131); the closure figure counted seven
post-closure groups (sweep line 1854); the render took over 150 s at load 30 and timed out
(line 1196).
Cost: S; `plan_page.py`, `beat_jobs.py`, `state_docs.py`.
Binding: the plan page is the owner's view (owner rulings 2026-11-13 ~19:59Z and ~20:00Z).
Destination: this group, plus: the plan beat passes `--live-refs` and `--in-flight` (line 1131);
the PLAN-CAP3 refusal after a stamp is by design and is answered by the round-11 roster file
existing, not by code. TICK-P3 carry 20 (`beatd` class_wait_s) goes to P752's design, not here.

## P754: R11-PRE-PARALLEL-PIPELINE, day 1 as approved, and the merge-train residue as its input

Verdict: ACCEPT, BUILD day 1 (NO-ABSORB S, PROOF-INPUT M, TRAIN-ROUTING S) and the shadow, as
the approved design and tvofi's 2026-11-14 rulings say.
Source: the group (design approved round 2, `22fdbabafb30`, design-verdict `2d229ce672bb`);
R10-TRAIN-REVIEW-PRESETTLE (P759); intake 2, 3, 33, 34, 36, 39, 115, 117, 124, 153, 154, 186;
PC-1113-11, -16 (P775); sweep candidates at lines 1494, 1560, 1593, 2213.
Instances: the design's own cost test; TRAIN-REVIEW-PRESETTLE's measurement (11 of 22 merges
waited on the approval's review run, 23-28% of the train's time over 11:13-14:05Z on
2026-11-11).
Cost: XL as designed; day 1 is three groups. The group has `files: []`: `set-files` is owed
before any fixer or carry (the pickup's finding, confirmed: `files` is empty on the roster).
Binding: L5, `merge_train.py` is past the redesign threshold, and this is its redesign.
Destination: this group. The merge-train residue listed above is design input for
TRAIN-ROUTING, read by the design reviewer at the delta; nothing of it is a patch of its own.
The baseline harness in `$HPO_STATE_DIR/s14/seat/pipeline-design/` lands on
`design/R11-PRE-PARALLEL-PIPELINE` before the build (HANDOVER: "or the cost test has no
enumerator").

## P755: R10-GH-READ-RESIDUE-P3, narrowed to the call budget, kept

Verdict: ACCEPT, BUILD narrowed (S to M); roster stage `not-started`.
Deferred by: tvofi's 2026-11-12 07:34Z ruling (self-fed work that moves closure goes to round
11), applied 2026-11-12 09:35Z. That ruling placed it in round 11; it is not overturned.
Owner: O1 tvofi 2026-11-15 "Admit, built late (Recommended)"; C14 tvofi 2026-11-15 "Ratify as ruled (Recommended)"
Source: the group (P596, P625, P669, P683); PC-1113-13 (P777); intake 16 (T5).
Instances: brief item 2 (shim logs the script's basename) is on main
(`tools/audit/seat/shims/seat-gh:15`); carry 2 (the shim refusing the train's postmerge record
comment) met an admit landed 2026-11-11 (`git log -L340,352:tools/audit/seat/shims/seat-gh`:
`0aead91cf4`, `e899dde4ab`), yet refused four merges on 2026-11-12, and no refusal appears in the
s14 log after that day (`grep -n "OWED record"` prints two lines, neither a refusal): re-measure,
then build or mark. Kept: item 1 and carry 0 (conditional ETag reads; tick 210-350 calls/h,
ruleset 235 calls/h) and carry 1 (one host-wide call log; 61% of 3021 logged calls were in a log
`--top` never read). Measured share: 445-585 calls/h of the 5000/h core bucket, 9-12%; with
intake 16 (`ancestry_reds` read 3482 calls in under an hour on one pull request, sweep line
1450) it exceeds 20% in the hours it bites.
Cost: S plus `prepr.sh`'s `ancestry_reds` (one cached read per sha); no capped file.
Binding: the bucket read 0 of 5000 twice on 2026-11-14 (PC-1113-13); opens and dispatches
refused until reset, among them an opener of the required-red fix #3578 (sweep line 1987). That
is its freeze ground.
Destination: this group, before P745 (the pickup's ordering, accepted: the token ledger reads
the same accounting).

## P756: R10-RELAY-NOBODY-STALL, merged, split three ways

Verdict: ACCEPT, MERGE; roster stage `absorbed`.
Deferred by: tvofi's 2026-11-12 ruling as P755. Recommendation: absorbed, not refused.
Owner: C2 tvofi 2026-11-15 "Merge and split (Recommended)"; C14 tvofi 2026-11-15 "Ratify as ruled (Recommended)"
Source: the group (P611, P616-P618) and its six carries.
Instances: arm 1, 19.7% of fires (P750); arm 3, 65 owed against 6 folded (P749).
Cost: none of its own.
Binding: its seams are three kept groups' files; a separate group would re-pin three stale
line numbers and add a merge.
Destination: arm 1 and carries 2, 5 to P750 (relay); arm 3 and carries 1, 3 to P749 (carry
fold); arm 2 and carries 0, 4 to P752 (rendered prompt text). The pickup put carry 1 and 3 in
P750; this batch puts them with the fold (`carry_fold_arm` and the fold reader are the fold's
seam, P749 owns `carry_fold.py`).

## P757: R10-FLY-OPENER-STALE-ENV, merged into the toolchain pin

Verdict: ACCEPT, MERGE into R11-PRE-TOOLCHAIN-PIN; roster stage `absorbed`.
Deferred by: tvofi's 2026-11-12 ruling as P755.
Owner: C3 tvofi 2026-11-15 "Fold in (Recommended)"; C14 tvofi 2026-11-15 "Ratify as ruled (Recommended)"
Source: the group (P627, P678).
Instances: STALE CHECKOUT 14 of 22 opener failures, one topic stuck; three hand resets of
`fails.json` in 40 h.
Cost: none of its own; the HEAD-keyed retry and the `retry` verb are acceptance cases of P743.
Binding: under a pinned toolchain the refusal's premise (the tools checkout is behind main)
changes; patching it first builds against a premise P743 removes. The pickup recommended
building it (S); this batch merges because of that premise.
Destination: P743. Fallback written into P743's brief: if its design keeps STALE CHECKOUT
as is, the S item is built unchanged in P743's first part.

## P758: R10-TICK-RESIDUE-P3, dropped as a group; its carries re-homed

Verdict: REJECT, DROP; roster stage `refused`, reason: "carries re-homed by triage
r10-round-end#P758; no build of its own (L5: orchestrator_tick.py past the redesign threshold)".
Deferred by: tvofi's 2026-11-12 ruling as P755. The drop removes no work: every carry is moved.
Owner: C1 tvofi 2026-11-15 "Refuse, re-home (Recommended)"; C14 tvofi 2026-11-15 "Ratify as ruled (Recommended)"
Source: the group (35 carries, 34 unmarked; carry 29 marked).
Instances: L size, 34 patch items on two instruments (`orchestrator_tick.py`, `tick_loop.sh`)
past L5's threshold; carry 29 (scorecard beat row) is on main (`beat_jobs.py:138`).
Cost: the moves, 34 `mark-carry moved` ops.
Binding: L5 ("a fourth patch is not an option").
Destination, by carry index: to P751: 1, 4, 6, 7, 14, 16, 22, 23, 24, 27, 28, 30, 32; to P750:
11, 18, 21; to P753: 10; to P749: 9, 12, 13, 17, 19, 25, 33, 34; to P744: 8; to P752: 0, 2, 3,
5, 15, 20, 26, 31; 29 stays marked (built). The pickup kept a remainder here; this batch keeps
none.

## P759: R10-TRAIN-REVIEW-PRESETTLE, merged into the train's redesign

Verdict: ACCEPT, MERGE into R11-PRE-PARALLEL-PIPELINE (TRAIN-ROUTING); roster stage `absorbed`.
Deferred by: tvofi's 2026-11-12 ruling as P755.
Owner: C4 tvofi 2026-11-15 "Fold in (Recommended)"; C14 tvofi 2026-11-15 "Ratify as ruled (Recommended)"
Source: the group (P628).
Instances: 23-28% of train time spent waiting on the approval's review run (measured
2026-11-11); null control: none of 50 review runs turned a green head red.
Cost: none of its own.
Binding: it changes `merge_train.py`'s approve step, the instrument L5 sends to redesign; the
measured gain clears the 10% keep bar, so it is merged, not dropped.
Destination: P754's TRAIN-ROUTING part, its acceptance cases verbatim; refused there only if
the design reviewer finds the routing makes it moot.

## P760: R10-UPDATE-PR-SEAT-WORKTREE, merged into the relay rebuild

Verdict: ACCEPT, MERGE into R11-PRE-RELAY-REBUILD; roster stage `absorbed`.
Deferred by: tvofi's 2026-11-12 ruling as P755.
Owner: C5 tvofi 2026-11-15 "Fold in (Recommended)"; C14 tvofi 2026-11-15 "Ratify as ruled (Recommended)"
Source: the group (P675, P689).
Instances: five holds, 40 min and 32 min waits; no OWED line printed (the relay reads rc 75 as
retry-unrecorded).
Cost: none of its own; the widened holder loop and its three guards are P750 acceptance cases.
Binding: "a slow or refused update does not hold the pass" is P750's requirement; a BUSY
holder is one such hold.
Destination: P750.

## P761: R10-PREPR-DARWIN-SELFTEST-LANE: the lane replaced by the beat row; kept as pre-PR shell lints

Verdict: ACCEPT, REPLACE (the lane) by the `darwin-selftest` beat row; BUILD narrowed (S) for
the rest; roster stage `not-started` with a re-cut brief.
Deferred by: tvofi's 2026-11-12 ruling as P755. The paid macOS lane is refused under tvofi's
2026-11-12 ruling that macOS-only checks run on local seats and paid runners are never asked
about.
Owner: C7 tvofi 2026-11-15 "Replace, keep lints (Recommended)"; O1 tvofi 2026-11-15 "Admit, built late (Recommended)"; C14 tvofi 2026-11-15 "Ratify as ruled (Recommended)"
Source: the group (P684, P686) and its three carries; intake 5, 10, 31, 149, 163; the
pipefail-sigpipe family (`dev/audit/rca/R10-RCA-FAMILY-PIPEFAIL-SIGPIPE.md`).
Instances: the beat row is on main (`beat_jobs.py:111`, `darwin-selftest`, merged by #3565): it
runs `prepr.sh --self-test` and every wired instrument self-test on a Darwin host at each main
tip; "it detects after the merge; it does not prevent" (its own text). The raw-wc compare and
the pipefail early exit are both detectable before the push by a sub-second scan of added lines.
Cost: S; `prepr.sh` gains one diff-scoped step (added lines in `tools/**/*.sh` only); standing
cost under one second per run.
Binding: the barrier owed at the third Darwin instance (carry 0) and at the third pipefail site
(the family record) is a pre-merge detector; the beat row is the post-merge one.
Destination: this group, re-cut to: (a) land `cce3f946`'s BODY.md as
`dev/audit/rca/R10-RCA-PREPR-DARWIN-SELFTEST.md` and its bugclasses entry (carry 1a); (b) the
stub host-independence rule (carry 0); (c) one diff-scoped shell-hazard lint: a raw `wc -l`
string compare and an early-exit reader on a pipe under `pipefail`; (d) intake 5/10:
`harness_headers.inline_scan()` in prepr (a static, sub-second check that reached CI as a
`tests / fast` red). Carry 2 is a duplicate of carry 0.

## P762: R10-SELFTEST-SCOPE-UNION-GUARD (#3551): merged into the shared-files part 1, union half only

Verdict: ACCEPT, MERGE into R11-PRE-SHARED-FILES part 1; the shrink guard dropped; roster stage
`absorbed` once the part lands.
Owner: C6 tvofi 2026-11-15 "Re-cut as part 1 (Recommended)"
Source: the group (audit-class barrier C, triage 2026-11-13), #3551 (open, head `00a470f7b7`),
its nine carries; loop card L9.
Instances: `record` still replaces (`tools/ci/selftest_scope.py:750-751` at `a39627da59`); the
replace dropped 660, 8 and 10 entries in #3409, #3419, #3506.
Cost: #3551 is built. Re-cut cost: drop the guard hunk and its two mutants, one delta review.
Binding: under L9 no pull request edits the table, so a guard over pull-request edits of it has
no input; the union is still needed by the generator.
Destination: P748 part 1, by re-cutting #3551 to the union record. Alternative on the card:
land #3551 as built (one merge sooner, one refusal more).

## P763: R11-SELFTEST-SCOPE-MAIN-UNION-RERECORD, merged as the shared-files part 1

Verdict: ACCEPT, MERGE into R11-PRE-SHARED-FILES part 1; roster stage `absorbed`.
Deferred by: the 2026-11-13 triage ruling "barrier A accepted for round 11" (in the group's
note); placed in round 11, not refused.
Owner: C6 tvofi 2026-11-15 "Re-cut as part 1 (Recommended)"; C14 tvofi 2026-11-15 "Ratify as ruled (Recommended)"
Source: the group; countermeasure A of the self-test drift analysis.
Instances: main's drift step went red in six episodes in the s14 log (family record) and was
repaired by nine hotfix merges in round 10.
Cost: S; edits `governance.yml` (code-owned, tvofi's review).
Binding: it is L9's first artifact; as a separate group it would be built twice.
Destination: P748 part 1.

## P764: R10-NUDGE-RETIRE (#3566): finish it

Verdict: ACCEPT, BUILD (finish).
Source: owner instruction 2026-11-12 ("ok, correct any references to that script or remove it
entirely"); #3566 (head `3487296ce9`); its carry 0; intake 80.
Instances: `nudge.md` is 115 lines, 3808 tokens of the 69077-token corpus (5.5%; `node
tools/policy/policy_lint.mjs --budgets`). #3566 is held only on the bus self-test's P354 flake
(failed twice in CI, 0 failed locally at head, base and head plus main, 8 of 8 concurrent runs).
Cost: one quiet-runner CI run and a delta review; it deletes a policy file, so the machinery
ratchet counts one merge and the corpus falls.
Binding: owner directive (skips the bars). Under one-in-one-out it is an "out".
Destination: finish; intake 80 (drop the orphan `files_tokens` cap) is its carry.

## P765: R10-PROCESS-SLIM's two open carries

Verdict: ACCEPT, MERGE each; then set the group `done`.
Source: the group (#3451 merged `a39627da59`); `roster_lib.pending_carries` prints carries 0 and
6 pending.
Instances: carry 0, a repair handoff's body keeps `## Head` naming the previous handoff (#3230,
#3212, #3231); carry 6 is a copy of carry 5 (outside guides and decision 0017).
Cost: two roster moves.
Binding: none.
Destination: carry 0 to P749; carry 6 to R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3 (P767).

## P766: R10-SEAT-IDENTITY-P5's six open carries

Verdict: LOG for carries 0-3 (built: mark implemented at `099d4fa3f2`); ACCEPT, MERGE for
carries 8 and 10.
Source: the group (#3491 merged `099d4fa3f2`); pending carries 0, 1, 2, 3, 8, 10.
Instances: carries 0-2 (generation token P63, session lock P236, one writer per seat) are
`tools/audit/seat/seat_gen.py` on main (`bump`, `check`, `lock`, lines 51-125); carry 3 (the
`loop-cwd` row) is on main (`beat_jobs.py:92`, and `"loop-cwd"` in the job list line 164).
Carries 8 and 10 are one item: `dev/audit/harnesses/r10_open_driver_mutants.py` aborted at
`61afd4f2db`; run here at `a39627da59` it did not print the abort within 120 s (stopped then),
so the abort may no longer reproduce.
Cost: four marks, one move.
Binding: none. The pickup routed the `loop-cwd` row to P752; it is built.
Destination: carry 8 to P743 (the next group editing `open_driver.py`), re-measured there;
carry 10 marked duplicate.

## P767: R10-OUTSIDE-CONTRIBUTOR-CYCLE's open carries, and the proposed P3 group

Verdict: ACCEPT. The new group R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3 is outside work, not
machinery under the freeze: it builds now and this triage does not hold it. Carries 8, 9, 10
are its part 1, severity high, ahead of carries 0-3.
Owner: C12 tvofi 2026-11-15 "Open now as outside (Recommended)"
Source: the group (source outside, owner ruling 2026-11-12 ~07:40Z: "The contributor cycle
mechanism should be built in full, asap"); pending carries 0, 1, 2, 3, 5, 7, 8, 9, 10; the
pickup's queue section D.
Instances: carry 8, `merge_pr.sh` app mode merges a cross-repository head without asking
`outside.py`'s contract (`gates` returns before `head_is_ours` unless the mode is owner); carry
9, `Train.fork_head` runs the checkout's `tools/pr/outside.py` before comparing it with main's
blob; carry 10, `Train.land` asks the contract only when the base is main. Each was established
by a reviewer's read; none by a perturbation, so each part starts with its failing test.
Cost: one S part (8-10, `merge_pr.sh` and `merge_train.py`), then carries 0-3 as briefed.
Binding: a fail-open path on the gate that admits fork heads, while fork pull requests are
reviewed in place under the mandate. Outside items fold into the round (owner, 2026-11-13).
Destination: R11-OUTSIDE-CONTRIBUTOR-CYCLE-P3 (`source: outside`), carries 0, 1, 2, 3, 8, 9,
10, part 1 = 8-10. `merge_train.py` is shared with P754: admitted by seam (the outside contract
calls only). Carry 5 is a copy of P749's carry 0 (marked duplicate); carry 7 (the carry
predicate's file branch, a recorded residual) is LOG. Section D of the pickup queue can run as
written once tvofi's card is answered.

## P768: R11-INTAKE-R10-RESIDUE's instrument carries, split by seam

Verdict: ACCEPT, the split below (coordinator item 3); the production carries are the
orchestrator's and are not ruled here.
Source: the group's 196 carries (indices 0-based at `80c1fb32c7`), each read; the pickup's
`intake_carries.txt` keyword marking was not used as a classification.
Instances and destinations (`dup` = a copy of another index or of a group carry; marked
duplicate):
- P742 (limiter, policy): 15, 22, 23, 41.
- P743 (toolchain pin, L3): 32, 148.
- P744 (round metrics): 174, 176.
- P748 (shared files): 12, 13, 162, 184, 194 (dup of 162).
- P749 (handoff bookkeeping): 11 (dup), 17, 30 items 1, 2 and 6, 38, 73 (dup), 193.
- P750 (relay): 4, 37, 87.
- P751 (ack completion): 170, 181 (dup).
- P752 (standing scripts): 28, 35, 42, 76 (dup), 152 (dup).
- P754 (parallel pipeline, train redesign input): 2, 3, 33, 34, 36, 39, 115, 117 (dup), 124,
  153, 154 (dup), 186 (dup of 36).
- P755 (call budget): 16.
- P761 (pre-PR shell lints): 5, 10, 31, 149, 163 (dup).
- P764 (nudge retire): 80.
- P767 (outside P3): 1, 185 (dup).
- P786 (policy-docs timeout): none; P782 (flake arms): 167.
- DEFER, each with what would change it: 0 (P267's cancel sender: a measured cancel at a live
  head in round 11); 6-9 (R10-RCA-OPEN-PREPR-SLOW C1-C4: re-measure `update_pr.sh` wall after
  P750 lands; if a relay pass can still wait on one update, build); 27/75/151
  (`priority_cancel`: the after-figure from `ci_priority.py queue-wait`); 30 items 3, 4, 5
  (predictor arms: a second instance each); 69 (BOT_HEAD stop count: measure first); 71 (the
  `other (untaught)` keying: the round-11 D13 seat rules it or records the refusal); 78/166
  (`assertLegacyControl` false pass: survey `LEGACY_CONTROL_FILES`, one instance so far);
  171/182 (an unresolved group id in the playbook: a second instance).
- LOG, standing constraints the next seat editing the file reads, no build: 14, 43-70 except
  55 and 69, 79, 172 (each carry-201/-1922 entry is a "constraint on the next seat" or a
  recorded residual); 55 with 79 (pin `tmp_paths.py` into a required job: a new gate, so it
  waits for one-in-one-out under P742); 64 (owner's call on the ORCH-CONTINUITY barrier,
  pending since round 10, not re-asked here); 116 (D14 re-measures mutation-vacuous).
- Roster acts, no code: 26/74/150 (backfill `source`/`hotfix`/`savings_source`), 40 (carry 31's
  paragraphs), 86 and 88 (records of the card rulings; P13 is on main, see the summary), 169/180
  (a pointer edit after R10-DIMENSIONS-FULL-COVERAGE part 2).
- Not instrument (the orchestrator's): 18-21, 24, 25, 29, 77, 81-85, 89-114, 118-147, 155-161,
  164, 165, 168, 173, 175, 177, 178, 183, 187-192, 195.
Cost: about 150 roster ops (moves and marks); no code.
Binding: one S group cannot hold 196 items, and the pickup prints it until it is empty.

# Part B: the proposals

## P769: PC-1113-01, -02, -03 are already owned

Verdict: LOG.
Source: proposals-r11.md; HANDOVER's proposal table ("owned by").
Instances: PC-1113-01 is in R11-PRE-HANDOFF-BOOKKEEPING's brief, PC-1113-02 in
R11-PRE-ACK-COMPLETION's, PC-1113-03 in R11-PRE-RELAY-REBUILD's (each brief quotes the id).
Cost: none.
Binding: none; ruled with P749, P751, P750.

## P770: PC-1113-04 and -20: red-check items at handoff

Verdict: ACCEPT, MERGE into R11-PRE-HANDOFF-BOOKKEEPING.
Source: PC-1113-04 (a handoff accepted with predicted reds reached CI after merge verdicts,
#3561, #3562); PC-1113-20 (an inherited main red answered in every open body); the sweep
candidate at line 1074 (a handoff-form merge verdict before the first CI).
Instances: 2 (PC-04); 15 gating heads, one body patch each (PC-20); 1 (line 1074, #3512).
Cost: inside P749's policy pull request.
Binding: card P10 is "red-check items decided mechanically at the handoff".
Destination: P749.

## P771: PC-1113-05: what the plan counts

Verdict: ACCEPT, MERGE into R11-PRE-PLAN-RENDER.
Source: PC-1113-05; sweep lines 1131, 1854, 2356.
Instances: post-closure groups counted in closure (7 groups, line 1854); stage words make running
groups read not started (about 12 h of closure, line 1131).
Cost: inside P753.
Destination: P753.

## P772: PC-1113-06: the per-group pipeline as deterministic workflow scripts

Verdict: DEFER, owning group R11-PRE-STANDING-SCRIPTS (design input).
Owner: C15 tvofi 2026-11-15 "Defer as design input (Recommended)"
Source: PC-1113-06 (no prototype; evidence 4.34 B orchestrator tokens, 36 compactions in 66 h).
Instances: the evidence measures the cost of the present shape, not the benefit of the proposed
one.
Cost: unknown.
Binding: none until measured. What would change it: P752's design pricing the fan-outs it does
not script, against P745's ledger.

## P773: cloud_dispatch.py rendering: PC-1113-07, -08, -09 and two sweep candidates

Verdict: ACCEPT, MERGE into R11-PRE-STANDING-SCRIPTS.
Source: PC-1113-07 (`--group --part` refuses with and without `--topic`), -08 (carries weighed
by kind; tvofi, 2026-11-13: "you may have a fixer have more carries based on their kind, locally
for now and filed as a permanent proposal"), -09 (designer roles refused on a size-M group that
asked for a design); sweep lines 1636 (the part line carried forward on a re-fire) and 1725 (the
flag path appends the group's carries).
Instances: 07 on R10-DOCS-STRINGS-RESIDUE and on the #3598 resume (`dispatch-s15-5`
STATE-HANDOFF: "a resume needs the flag path"); 08 one group, two parts instead of three; 09 on
R10-START-COUNTER-EDGES, an outside production group; 1636 two instances.
Cost: inside P752; the five-carry rule lives in `cloud_dispatch.py:544`, `:924`.
Binding: 08 is an owner directive; 09 blocked an outside group's design. Prototypes:
`$HPO_STATE_DIR/s14/seat/pubfix.sh`, `partline_fix.sh`.
Destination: P752.

## P774: PC-1113-10 and -19: a body describing an old head

Verdict: ACCEPT. The base fix as a hotfix group now (ground below); the class to
R11-PRE-SHARED-FILES (L9's figure blocks).
Source: PC-1113-10, -19; sweep lines 1407, 1626; the figure-block family record.
Instances: ten pull-request reds over 2026-11-13 22:15Z to 2026-11-15 07:32Z (the record's
table).
Cost: the hotfix is two lines (`update_pr.sh:105` and `open_pr.sh:118` render with the pull
request's recorded `base.sha`, which `pr-contract` verifies against); S.
Binding: `pr-contract` is a need of the required `gate`; #3593 (a `custom_components/` pull
request) went gate-red on it at `5723ce19`. That is the freeze ground.
Destination: new group R11-HOTFIX-FIGURE-BLOCK-BASE (S, hotfix, sonnet fixer, opus reviewer,
files `tools/audit/seat/update_pr.sh`, `tools/audit/seat/open_pr.sh`); the head-move half
(recarry, merge-main bot, pin bot) to P748.

## P775: merge_train.py: PC-1113-11, -16 and four sweep candidates

Verdict: ACCEPT, MERGE into R11-PRE-PARALLEL-PIPELINE as TRAIN-ROUTING design input (L5).
Source: PC-1113-11 (the train fails eight merges on a draft), -16 (a second train in the default
state directory); sweep lines 1494 (`filter=latest`), 1560 (a red gate read final while a
second run is in flight), 1593 (GREEN read while a re-run is queued), 2213 (land waits on a
pending required context; prototype `$HPO_STATE_DIR/s14/train_guard.sh`).
Instances: one each, except 1560/1593 (two readers of the same in-flight state).
Cost: inside P754.
Binding: L5; `land.sh`'s `gh pr ready` arm (P790) is PC-11's prototype.
Destination: P754.

## P776: PC-1113-12: strace PTRACE_LISTEN after a clean exit

Verdict: DEFER.
Source: PC-1113-12 (main `50373173d4`, one job).
Instances: one; its own text: "Not established: frequency on earlier runs".
Cost: unknown.
Binding: tvofi allowed merging over it (2026-11-13 ~23:52Z). What would change it: a recurrence
count over the last 50 main runs reaching three.

## P777: PC-1113-13: the shared REST bucket

Verdict: ACCEPT, MERGE into R10-GH-READ-RESIDUE-P3 (P755).
Source: PC-1113-13.
Instances: the bucket at 0 of 5000 twice on 2026-11-14; 1745 local calls in the hour, ruleset
read 240 times.
Cost: inside P755.
Destination: P755. A separate token for cloud seats is refused here (a second account is CI
widening by another name).

## P778: PC-1113-14: the home-path guard on a quoted diff

Verdict: LOG.
Source: PC-1113-14 (#3563).
Instances: one; the dispatch was published from a copy with the prefix replaced.
Cost: none.
Binding: blocks no production merge.

## P779: PC-1113-15: the introduced-red guard waits for a running job

Verdict: ACCEPT, MERGE into R11-PRE-TOOLCHAIN-PIN as L3's first use.
Source: PC-1113-15; sweep lines 1758, 1970.
Instances: six heads, 10-40 min each (P743).
Destination: P743.

## P780: PC-1113-17: body_push keeps a privacy-refused body on origin

Verdict: ACCEPT, MERGE into R11-PRE-HANDOFF-BOOKKEEPING, first in it.
Source: PC-1113-17 (sweep line 2009).
Instances: one; the ref was gone at read-back, the commit may persist unreferenced.
Cost: a few lines in `body_push.sh`.
Binding: privacy; severity high skips the bars.
Destination: P749.

## P781: PC-1113-18: a stamp strands every pre-stamp handoff on the claim file

Verdict: ACCEPT, MERGE into R11-PRE-SHARED-FILES (L9's claim-file stamp line).
Source: PC-1113-18; sweep line 2049.
Instances: three hand merges after the 2026-11-14 stamp; two gating items idle about 2 h.
Destination: P748.

## P782: PC-1113-21: timing-dependent self-test arms

Verdict: ACCEPT (root-cause countermeasure, `dev/audit/rca/R10-RCA-FAMILY-FLAKY-SELFTEST.md`).
Source: PC-1113-21 and its addendum; intake 167.
Instances: four (the family record).
Cost: S: make the bus P354 concurrent-confirm arm and the beatd case (9) deterministic, and pin
the clock in the `entities.py` redaction check.
Binding: an INTRODUCED read on #3564 (`custom_components/` strings) blocked a production pull
request; that is the freeze ground.
Destination: new group R11-HOTFIX-SELFTEST-FLAKE-ARMS (S, sonnet fixer, opus reviewer, files
`tools/audit/seat/bus.sh`, `tools/audit/seat/beatd.py`, `tests/entities.py`).

## P783: PC-1113-22: no tracked "GREEN with a merge verdict that carries" line

Verdict: ACCEPT, MERGE into R11-PRE-ACK-COMPLETION with R10-TICK-RESIDUE-P3 carry 27.
Source: PC-1113-22 (sweep line 2112).
Instances: #3564 ready one hour unseen; #3574, #3569, #3561 read by hand.
Destination: P751.

## P784: PC-1113-23: built

Verdict: LOG.
Source: PC-1113-23.
Instances: built as #3584 (`1791869fdb`); its residue (`gate.py` refresh re-running a covered
green gate) is intake 115/117, in P754.

## P785: the unnumbered sweep candidates after the 2026-11-13 triage seat

Verdict: per line below. The candidates up to sweep line 1475 were ruled by the triage seat of
2026-11-13 (T1-T23, out of tree; its ACCEPT-R11 rulings are intake 16 and 17); `grep -c -i
"proposal candidate\|PROPOSAL-NOTE\|PROPOSAL:"` over the log prints 122 lines in all.
Source and destination, each one instance unless stated:
- 1495 (postmerge's stage write races the drain) and 1513 (a BLOCKED note raises its own
  digest line): P749.
- 1520 (the roster drain lints once per op, 1.5-4 min each): P749, measured: one batch about 90
  min.
- 1522, 1562, 1626, 1751: P750.
- 1553 (the nightly kill-drain pins a site an open pull request removes): DEFER, a second
  instance.
- 1597 (update_pr checks the merge-tree against main before the heavy steps; one update
  refused after 5729 s): P750, as part of "a slow update does not hold the pass".
- 1609 (cloud briefs state a 120 s per-command bound): P752.
- 1689 (cancelling a superseded main run cancels its self-tests and fails closed downstream):
  P743 (L3).
- 1732 (the bot commits the uploaded selftest-closures artifact): P748 part 1 (it is
  countermeasure A).
- 1758 (dispatch on a running self-tests job): P743 (L3).

## P786: policy-docs times out when field coverage runs

Verdict: ACCEPT (root-cause countermeasure, `dev/audit/rca/R10-RCA-FAMILY-POLICY-DOCS-TIMEOUT.md`).
Source: the friction family policy-docs-field-coverage-slow (sweep lines 2605, 2606).
Instances: three (the record).
Cost: one line in `.github/workflows/governance.yml` (`policy-docs` `timeout-minutes` 5 to 10),
code-owned; zero standing seconds on a run that finishes.
Binding: the required `gate` went red on #3451 and on main (`b046b22d`); fixing the required
gate's red on main is a freeze ground.
Destination: new group R11-HOTFIX-POLICY-DOCS-TIMEOUT (S, hotfix, sonnet fixer, opus reviewer).

## P787: the pipefail early-exit class

Verdict: ACCEPT (root-cause countermeasure, `dev/audit/rca/R10-RCA-FAMILY-PIPEFAIL-SIGPIPE.md`),
MERGE into P761's lint.
Source: the family pipefail-sigpipe; intake 149, 163.
Destination: P761 item (c).

## P788: reusable instruments left in scratch

Verdict: LOG (no new countermeasure; `dev/audit/rca/R10-RCA-FAMILY-SCRATCH-INSTRUMENTS.md`).
Source: decision 0013 and the 2026-11-13 freeze shape; the prototype inventory.
Destination: R11-PRE-MACHINERY-LIMITER carry 2 already owes "where the proposals file and the
prototypes live"; Part C below rules on every prototype round 10 left.

# Part C: the local prototypes and workarounds

## P789: the landing chains (chain_one.sh, chain_one_v2.sh, chain_after_green.sh, chain_3481_3582.sh)

Verdict: DEFER (tvofi's card C9): neither dropped nor tracked. They stay session-local, and a
benchmark against the merge train is owed; its result is triaged at round 11's end.
Owner: C9 tvofi 2026-11-15 "Keep them locally and benchmark them against the train"
Source: `$HPO_STATE_DIR/s14/bypass/` (52, 14, 41 lines and one per-PR copy).
Instances: they relay a held verdict once CI is green, post the prepared mandate approval and
land; #3593 and #3451 merged through them on 2026-11-15 (sweep lines 2603, 2612).
Cost: the benchmark: one read of git and the verdict bus per window, no new seat; each chain
keeps its session-scratch paths, so it runs only from a session that sets them.
Binding: whether the chains land faster than the train is unmeasured; dropping them (this
batch's first ruling) assumed the train's wait was acceptable.
The benchmark, owned by R11-PRE-PARALLEL-PIPELINE (the group that owns the train's redesign
and its replay baseline of handoff-to-merge wall clock):
- measures, per pull request, the merge wait: minutes from the later of (a merge verdict
  posted at, or carried to, the live head) and (`merge_train.py classify` reading GREEN) to the
  committer time of its merge commit on main, with the landing path (chain or train) as the
  factor, plus each path's refusals and wrong merges (a wrong merge must read 0);
- reads main's moves and lead time per size from `python3 tools/audit/merge_throughput.py flow`,
  which publishes those from git alone; that instrument has no per-PR merge-wait column, so the
  benchmark adds it there (or reads it from the design's baseline harness in
  `$HPO_STATE_DIR/s14/seat/pipeline-design/`, which P754 lands on its design ref), never as a
  third parser of the bus;
- null control: the train's own entries in the same window, same classes;
- decision rule, stated now so the benchmark cannot pick it later: if the chains' median merge
  wait is more than 20% below the train's over at least ten pull requests each, with no wrong
  merge, their posting-at-GREEN behaviour becomes a proposal into P750 and P754 at round 11's
  end; otherwise they are retired.
Destination: R11-PRE-PARALLEL-PIPELINE runs the benchmark during its shadow; the chains stay in
`$HPO_STATE_DIR/s14/bypass/`.

## P790: land.sh and land_3568.sh, the ruleset-release merge

Verdict: DEFER (tvofi's card C9, which covered the chains and `land.sh` together): kept
session-local, benchmarked with P789.
Owner: C9 tvofi 2026-11-15 "Keep them locally and benchmark them against the train"
Source: `$HPO_STATE_DIR/s14/bypass/land.sh` (62 lines): it verifies, merges normally, else
releases ruleset 23698884 for one merge and restores it.
Instances: used under tvofi's 2026-11-14 bypass authority for the 15/11 closure.
Cost: as P789.
Binding: the benchmark compares landing paths, so only `land.sh`'s normal-merge path enters it;
its ruleset-release arm stays bound to the authority it was written under (the 15/11 closure)
and is not run for the benchmark. Its two useful arms are named for the redesign: `gh pr ready`
is PC-1113-11's prototype (P775) and the merge-tree `structure.py`/`policy_lint` check is the
train's pre-flight.
Destination: P789's benchmark, owned by R11-PRE-PARALLEL-PIPELINE.

## P791: wake_filtered.sh

Verdict: ACCEPT, MERGE into R11-PRE-ACK-COMPLETION; keep the script running until it lands.
Owner: C10 tvofi 2026-11-15 "Fold in, keep running (Recommended)"
Source: `$HPO_STATE_DIR/s14/wake_filtered.sh` (session-local, "Proposal candidate for triage;
not a tracked instrument").
Instances: repeated levels woke the orchestrator about once a minute (sweep line 1531); the
round-11 orchestrator armed it at start (line 2622).
Binding: its noise list is a list of levels that P14 makes close or escalate; the tracked cure
is upstream (no repeat line), not a second filter.
Destination: P751; its NOISE pattern is the acceptance list.

## P792: the dispatch seats' scripts (dispatch-s15-2 to -5)

Verdict: ACCEPT, REPLACE: R11-PRE-STANDING-SCRIPTS tracks and self-tests them as the dispatch
half; `relayc.sh` goes to R11-PRE-RELAY-REBUILD.
Source: `$HPO_STATE_DIR/s14/seat/dispatch-s15-*/STATE-HANDOFF.md`: `disp.sh`, `disp0.sh`,
`disploop.sh`, `disploop0.sh`, `verify.sh`, `relayc.sh`, `watch3.sh`/`watch4.sh`, `pub*.sh`,
`c*.sh`, `v.sh`, `vfix2.sh`, `mkfix*.sh`, `cl3451.sh`, `chkfix.sh`.
Instances: every reviewer and fixer dispatch from 2026-11-14 to the closure ran through them;
their traps are written down (a relay-minted nonce reused, never a second bus dispatch; a
first round has no `--reviewed-head`; payload line 1 verified before every fire).
Binding: R1 asks for exactly these mechanics as tracked beat scripts; the prototypes are the
specification, and their hard-coded paths and session env make them unfit to track as they are.
Destination: P752 (design input and acceptance cases); `relayc.sh` to P750.

## P793: the closure runbook and the closeout prune pass

Verdict: DEFER, owning group: the round-11 closeout group (R10-CLOSEOUT-CLEANUP's successor);
one item ACCEPT now.
Owner: C11 tvofi 2026-11-15 "Defer, safe default now (Recommended)"
Source: `$HPO_STATE_DIR/s14/seat/closure-runbook/` (`make_queue.py`, `sim_queue.py`,
`fill_shas.py`, `retarget.py`, `extra_retarget_lines.py`, `main_only_roster_delta.py`,
`groups_now.py`, `catalog_pr.sh`, `stamp_prep.sh`, `stamp_push.sh`, the `rec*` scripts,
`RUNBOOK.md`); `seat/closeout-prune-1114/`; intake 179 (`prune_refs.py` batch read); sweep line
990; HANDOVER's owed `closeout.py` retarget arm and `--orch-root` default.
Instances: they ran once, at one closure; benefit per round is unmeasured.
Cost: unknown for the scripts; the `--orch-root` default is a few lines.
Binding: closeout runs once a round, after the finders. The ACCEPT: a closeout default
`--orch-root` that cannot delete `HPO_STATE_DIR` (a destructive default, severity high), built
before the next closeout run. The scripts are kept on an archive ref (decision 0013) until
then; what would change the DEFER: the round-11 closure's time measured against round 10's.

## P794: the rest of the inventory

Verdict: per line.
Source: HANDOVER's "Local prototype inventory" and the sweep log.
- `seat/replan-*/build_tabs.py`: REPLACE target of P753 (its carry 2).
- `plan-proto/` and `refs/proto/plan-gating` (a gating-only costing on a fixture roster): DROP;
  P753's round filter is the tracked form.
- `seat/pipeline-design/` harness: owed on `design/R11-PRE-PARALLEL-PIPELINE` (P754).
- `seat/loop-study-1114/data/`: L1's prototype, P744.
- `seat/soak-read/`: LOG; D15's bundle reader, a round harness, not machinery.
- `s14/train_guard.sh`: P775 (design input), then dropped.
- `seat/pubfix.sh`, `pubrev.sh`, `pubrevt.sh`, `partline_fix.sh`: P773/P752.
- `s14/beat_extras.sh` (plan render timeout 150 to 420 s): P753.
- the detached watch-mode relay: retired by P750 (its brief).

# Part D: policy

## P795: finder-start condition (a) cannot read none as the tools stand

Verdict: ACCEPT, the smallest sound change: playbook wording plus `--roster-ref`; policy
(`dev/audit/README.md`), tvofi's card.
Owner: C13 tvofi 2026-11-15 "Reword + --roster-ref (Recommended)"
Source: coordinator item 2; the pickup's measurement.
Instances: the Round start one-liner prints every group not in `FINISHED_STAGES + ('refused',)`,
33 lines at `80c1fb32c7`; groups that must stay open at finder start (R10-CATALOG-PR until
hacs/default#14201 merges, every scheduled production group) print forever. `carry_audit.py
roster` without `--roster-ref` read 83 stranded on main's copy, 61 at the roster branch.
Cost: two sentences and two command edits in the README; no code.
Binding: condition (a) is a finder-start gate; as written it never passes.
Destination: a README edit (by P742's policy pull request or the next playbook edit): (a)
reads "every line the two pickup commands print, run against
`origin/handoff/audit-r<N>-roster`, has a disposition: a stage the round schedules
(`not-started`, `design`, `in-progress`, `carries-open` with a named next step), `done` or
`refused`; `deferred` is not a disposition at a round start"; `carry_audit.py` gains
`--roster-ref origin/handoff/audit-r<N>-roster` and the one-liner reads `git show
<ref>:dev/programme/rosters/wave-r<N>-groups.json`. A disposition column in the tool is P751's
round-start refusal (intake 170), not this edit.

# Part E: friction families

Families with three or more instances, or any instance that turned a required check red, each
have a root-cause record: selftest-scope-drift (four in the counting window; six episodes in the
log), policy-docs-field-coverage-slow (three; gate red), figure-block-base-mismatch and its
head-move sibling (ten; gate red), pipefail-sigpipe (three sites), flaky-selftest (four),
relay-serial-update (seven), and reusable instruments in scratch (more than three). Records:
`dev/audit/rca/R10-RCA-FAMILY-*.md`.

Under the threshold, one line each:
- macos-selftest-portability, 1 (sweep line 2558; the bus `seat_gen` null-control arm compares
  padded `wc -l` on Darwin): under three; the class is barriered by the `darwin-selftest` beat
  row and P761 (c).
- predictor-time-bound-darwin, 1 (line 2573; 763 checks, 0 failed, 3 min 10 s at load 4 against
  `SELF_TEST_TIMEOUT` 180 s): under three; a host bound, not a red.
- relay release line not honoured (HELD-VERDICT kept for #3451 despite `cloud-handoff-release`):
  count not reproduced; no HELD line for #3451 in `cloud-relay.log` or its level file, and the
  log's #3451 entries after the release (lines 2557-2612) show the update applied and seven
  POSTED verdicts; stated as unreproduced.
- prune artefacts, 1 episode (lines 2593-2594: four stale blocked-stop and two seat-no-return
  lines after pass A): under three; P750 (the no-return arm reading archived refs).
- plan beat refusing after the stamp, 1 (line 2584): by design (a round closes once); answered by
  the round-11 roster file.
- hung-instrument 2, roster-drain-refusal-unlogged 1 (P749 via TICK-P3 carry 19), relay-handoff 1,
  relay-ev-case 1, carry-fold 2 (P749), approval-retriggers-gate 2 (P754): under three
  (HANDOVER's counts, each its last stated count).
