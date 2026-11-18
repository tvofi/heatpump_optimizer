# R11-RCA-PLAN-OBJECTIVE-MISSING: seats execute policy from whatever tree they were started in, and no seat checks that tree against main

This was written by the root-cause seat (`dev/governance/roles/root-cause.md`,
`dev/governance/rules/defect-root-cause.md`) on 2026-11-18. It ran apart from
any fix. The figures were taken at `plan/r11` =
`819aa2e354b4e5baaf824b8568fd72bea8168a75` and `origin/main` =
`8751943e17ef4d3ec699e7859ae829b4528d8ce7`.

**Re-opened.** The first version stopped at the proximate cause: P3 read its
contracts from the round branch. This version answers why the architect started
from an out-of-date base at all, and treats that as a class: every seat kind and
how it picks the tree it reads policy from.

The prototypes, measurement scripts and run transcripts are out of tree, under
`$HPO_STATE_DIR/r11/proto/`:
- `base-fresh/` holds the class check and its measurements;
- `plan-objective-gate/` holds the P3 gate.

## 1. The defect, reproduced

Run from `origin/main`:

    python3 tools/audit/seat/plan_audit.py objective-check \
      --ref 819aa2e354b4e5baaf824b8568fd72bea8168a75 \
      --plan dev/audit/rounds/round11/PLAN/PLAN.json \
      --register dev/audit/rounds/round11/JUDGE.json
      FAIL NO objective block: PLAN.json commits to one (0018, architect-planner.md)
    OBJECTIVE FAIL                                                   (exit 1)

At that SHA, `PLAN.json` has no `objective` key and the plan directory has no
`PROJECTION.json`. Neither `REVIEW.md` nor `PLAN.md` contains "objective".

## 2. The facts, checked

| stated | measured |
|---|---|
| the plan was cut at fork `92d38ecb64` | That is the round's measurement fork, named in `PLAN.json`'s `fork`. The branch's **tree** comes from elsewhere: `plan/r11` continues `handoff/audit-r11-register`, which the intake commit `28b864af6d` cut from main at `33b1e089bc` (2026-11-17 13:19Z). It never merged main again. |
| `6142e16f7a` and `f51c5bde89` arrived after the fork | Both are commits on #3703's branch. #3703 merged to main at **2026-11-17 20:33Z** (`e3c75934c2`). The same merge replaced `architect-planner.md`, `plan-review.md` step 5, `audit-plan.js`, `plan_audit.py` and its guide. |
| the third review never mentions the objective | Confirmed. Its point 12 executes the old step 5 word for word: "time, PASS: `projection.py` … re-run". |
| the fix wave dispatched on revision 2 under mandate decisions | Confirmed. `819aa2e354` (11:05Z) is a hand commit made after a `revise` verdict. The fixers were dispatched from 12:16Z, and 11 of the 27 groups had started by 15:09Z. |

**New: what P3 actually ran.** The Workflow launch at 2026-11-18 07:36:47Z
(recorded in the orchestrator session's transcript) used:
- `scriptPath` `$HPO_STATE_DIR/r11/proto/plan-overlay/audit-plan.js`;
- `repo` `$HPO_STATE_DIR/r11/intake-reg-wt`, a worktree of the register branch;
- `branch` `handoff/audit-r11-register`.

The overlay is an **untracked copy**. It is main's `audit-plan.js` as of
2026-10-27 (`6f44346080`, 12 lines apart), with `model: 'fable'` added to six
agent calls. Its mtime is 07:36Z, eleven hours after #3703 replaced the tracked
file, and it contains the word "objective" zero times.

## 3. The cause

The proximate cause is that P3 executed superseded contracts. Three stale
sources fed it. The orchestrator chose each of them, and none of them was
compared with main:

1. **The workflow script** was an untracked overlay. It was copied from a
   version main had already replaced, to change the model routing. The
   overlay practice (patch a local copy at once, file the proposal) has no
   rule that keeps the copy current.
2. **The policy tree the stage's seats read.** `audit-plan.js` tells each
   seat to "work in a fresh worktree off `${branch}` … Read
   `architect-planner.md`, `plan-review.md` … there". The register branch's
   base was 13:19Z on 11-17.
3. **The orchestrator's own checkout.** CLAUDE.md and `.claude/rules` load
   from it automatically, both for the orchestrator and for every local seat
   it starts. It sat on `8f39313a44` (11-17 08:41Z) from the session's start
   at 11:05Z on 11-17 until 14:19Z on 11-18. That is where the orchestrator
   read `plan-review.md` and `orchestrator.md` when it decided the open points
   and dispatched the wave.

**The root cause, for the class:** no seat of any kind checks the tree it
executes policy, instruments and workflows from against `origin/main`.

- **Who picks the base.** Whoever starts a seat picks its base: the harness,
  the brief, a launch argument, or a hand-made copy.
- **Where it is checked.** The repository has freshness barriers, but each
  covers one instrument's own code paths:
  - `tick_loop.sh` P14;
  - `beatd.py` BEAT-STALE-CHECKOUT (P581);
  - `pr_args.sh` `pr_tools_fresh`;
  - `fix-review.md` step 0, over `dev/governance/roles/` only.
- **Where nothing checks.** No check reaches:
  - the orchestrator's checkout;
  - a Workflow script or overlay;
  - a round-branch stage;
  - the CLAUDE.md a local seat inherits.

## 4. The mechanism, per seat kind

For each seat kind, the questions are: who picks the base, where that choice
is written, which tree the seat's policy, rules, instruments and workflows
come from, and what checks it against `origin/main`.

**The orchestrator session.**
- **Base.** The harness creates `.claude/worktrees/<name>` on branch
  `claude/<name>` from the checkout's HEAD at session creation. After that it
  moves only by a hand `git pull --ff-only`.
- **Where written.** The branch tip, and the transcript's `gitBranch`.
- **Policy tree.** CLAUDE.md and `.claude/rules` auto-load from this tree, and
  Workflow scripts launched by `name` resolve from its `.claude/workflows`.
- **Check.** None. `orchestrator.md` names no base for it. In round 10 a
  separate `orch-wt` was kept on main by a loop (fetch and detach every
  600 s, started 10-28); that loop has been dead since 11-04 without an alarm.

**Local Agent seats.**
- **Base.** The session cwd is the parent's, so CLAUDE.md and the rules load
  from the parent's checkout. The work tree is whatever the brief tells the
  seat to `git worktree add`.
- **Where written.** The brief.
- **Policy tree.** The parent checkout, plus whatever path the brief names
  for contracts. This seat's brief said "read both from origin/main"; that
  was the only guard.
- **Check.** None.

**Cloud seats (`cloud_dispatch.py`).**
- **Base.** A fresh clone of the default branch at fire time, then `git fetch
  --unshallow`. A fixer is told to work "in a worktree of your own cut from
  origin/main"; a reviewer fetches the PR head.
- **Where written.** `PROMPT.md`, pinned at a SHA.
- **Policy tree.** Main at fire time, or the PR head for a reviewer.
- **Check.** None at start, which is fresh by construction. At handoff only
  `merge-tree` conflicts are checked.

**Workflow-tool runs (`audit-find`, `audit-verify`, `audit-plan`, `web-*`).**
- **Base.** The script is `scriptPath` or `name`, resolved from the session
  cwd. The seats inside cut worktrees off `args.branch` or `args.baseline`.
- **Where written.** The launch arguments, in the transcript only.
- **Policy tree.** The script copy, and the branch named in `args`.
- **Check.** None. All 14 round-11 launches ran untracked overlays.

**Designers.**
- **Base.** `designer.md` step 1 names the code base: the predecessor's
  handoff head, else `origin/main`.
- **Where written.** The design note.
- **Policy tree.** The worktree. No rule names it.
- **Check.** None.

**Reviewers (fix, design, plan).**
- **Base.** A detached worktree at the head under review.
- **Where written.** The verdict's SHA.
- **Policy tree.** The **head's** tree.
- **Check.** `fix-review.md` step 0 diffs `dev/governance/roles/` only, as a
  stated instruction with nothing enforcing it. Design review and plan review
  have none.

**Fixers.**
- **Base.** `fixer.md`: a worktree "branched from `origin/main`". Main is
  merged in only on a conflict, because the handoff freezes the branch.
- **Where written.** The branch.
- **Policy tree.** The branch's base.
- **Check.** At start, none. At open, `pr_tools_fresh` covers
  `tools/audit/seat` and `tools/pr` of the opener's checkout.

**The train and the opener.**
- **Base.** The tools checkout the scripts run from.
- **Where written.** The checkout.
- **Policy tree.** That checkout.
- **Check.** `pr_tools_fresh`, over tools paths only.

**Beat jobs and the tick loop.**
- **Base.** Their own worktrees (`beat-wt-*`, `tickloop-wt`).
- **Where written.** The checkout.
- **Policy tree.** That checkout.
- **Check.** Yes: P581 and P14 measure behind-ness on tools paths and restart
  on main. Measured now, `beat-wt` equals main, and `tickloop-wt` is 18
  policy and instrument files behind, inside its bound.

**The `wt_sync.sh` snapshot loop.**
- **Base.** Round 10's `orch-wt`, at `d7582ed404` (2026-11-04).
- **Where written.** The daemon's argv.
- **Policy tree.** That tree, which is **314** policy and instrument files
  behind main.
- **Check.** None.

## 5. Incidence, measured

The policy paths counted are:
- `CLAUDE.md`, `AGENTS.md`;
- `dev/governance/`;
- `.claude/workflows`, `.claude/rules`, `.claude/skills`;
- `tools/audit`, `tools/policy`, `tools/pr`, `tools/plan`.

**Pull-request seats** (`measure_seat_bases.py`): every PR merged to main,
from its oldest own commit. "Stale at start" means the merge base lacked a
policy file that main held `lag` hours before that commit.

| window | PRs | stale at start, lag 0 / 1 h / 6 h | head missing a policy change main had at handoff |
|---|---|---|---|
| round 10 (10-15 to 11-16 19:05Z) | 1181 (39 rebased after their first commit, not counted) | 103 / 19 / 1 | 240 (mean 5.4 files) |
| round 11 (from 11-16 19:05Z) | 50 | 9 / 3 / 0 | 19 (mean 12.5 files) |

What the table shows:
- **PR seats start fresh.** One of 1,231 missed a policy change main had held
  for 6 h: #3533, a `-p3` carry branch cut at `d95a3490ef`, 76 files behind.
  The cut-from-main rule (fixer, cloud) works where it is stated.
- **Reviewers read stale heads.** The handoff column is what a reviewer reads
  at a detached head: 240 of 1,181 heads in round 10 (20 %) and 19 of 50 in
  round 11 (38 %) lacked a policy change that main already carried.

**The orchestrator's own checkout** (`checkout_lag.py`; lower bounds, because
the branch tip is the newest base the session can have had):

| session | hours | stale for | policy and instrument merges missed (CLAUDE.md, governance, rules) |
|---|---|---|---|
| round 10, session 14 (11-11 to 11-14) | 81.6 | 81.1 h (99 %) | 61 (10) |
| round 10, programme closure (11-14 to 11-15) | 26.1 | 21.8 h (84 %) | 11 (4) |
| round 11 orchestrator (11-17 11:05Z to 11-18 14:19Z) | 27.2 | 25.0 h (92 %) | 8 (3) |

Of the 300 local seats the round-11 orchestrator session started, **235**
started while its checkout lacked a policy merge main already had. Each of
them inherited that CLAUDE.md and those rules.

**Workflow launches** (from the transcripts):
- **Round 11.** All 14 launches ran untracked overlays (`overlay_source.py`).
  - The `audit-plan` overlay was superseded at launch: main had moved the
    tracked file once (#3703) past the overlay's source.
  - The `audit-find` overlay was cut from `a57433c661` (11-17 05:24Z). Main
    did not move that file before its five launches.
- **Round 10.** Four `web-stamp` launches, from session checkouts. The script
  was unchanged on main in their windows, so none had a consequence.

**Consequential instances of the class.** There are at least four, each with
its own repair:
- S14-TICK-STALE-SILENT: about 4 h of relay dark over three episodes;
- BEAT-STALE-CHECKOUT (P581);
- the opener's STALE CHECKOUT (P-P);
- this P3 plan.

Three of them fall in round 10. That is an audit class by
`defect-root-cause.md`'s count, so it owes a class-eliminating barrier.

## 6. The process state, for the class: (c)

**Is there a rule naming the base a seat reads policy from?**
- **Stated for some code bases.** The fixer and the cloud fixer start from
  `origin/main`. The designer reads code at the predecessor's head or main.
- **Stated for some policy.** Reviewers check `dev/governance/roles/` only.
- **Not stated** for the orchestrator's checkout, Workflow scripts and
  overlays, round-branch stages, a local seat's inherited CLAUDE.md, the plan
  and design reviewers, or the standing snapshot loop.
- **Followed?** Every seat measured did what its text said:
  - PR seats start fresh (6 h lag: 1 of 1,231);
  - the reviews and P3 ran their copies faithfully;
  - the loops honour their own checks.
- **Checked?** Only inside four units: the tick loop, the beat, the opener and
  updater, and the reviewer's roles diff, which is not enforced. Each was
  built after an instance in its own unit.

**Why (c).** The process existed as per-instrument freshness barriers, it was
followed, and it did not produce the intended result: its unit is "the code
this instrument runs", not "the tree this seat executes policy from". By
`root-cause.md`, an instance of a class that already carries a barrier is not
(a); the countermeasure changes the unit, not the arm count.

**Why not the others.**
- Not (b): no seat broke a stated rule.
- Not (d) for the class: no precondition changed. The units were always
  narrow, and every new seat kind (Workflow overlays, round-branch stages) was
  outside them from the day it was added.
- The P3 instance alone reads as (d), as the first version found, but that
  stops one level short.

## 7. The cost test, over the class

**cost(defect)**, measured per instance where possible.
- **This instance:**
  - 77.0 h of started fix-wave work on three groups that carry no verified
    bug and that the floor projection drops;
  - 105.3 h of rank-1 first-wave work not started, including the head of the
    critical chain;
  - 35.5 h of critical path the unpriced floor would recover;
  - 2.6 h to re-run P3;
  - 13 verified bugs deferred without a card.
  - The hours are `replan.py` group durations on the plan's roster; the ranks
    are bug-derived lower bounds.
- **Prior instances:** about 4 h of relay dark (S14-TICK-STALE-SILENT). The
  others are unpriced in their records.
- **Exposure:** 235 local seats in one session ran under a checkout without 3
  policy merges.

**P(recurrence).** At least 3 consequential instances in round 10 and at least
1 in round 11 were measured, which is at least 1 a round. The orchestrator's
checkout was stale for 84 % to 99 % of every session measured.

**cost(countermeasure, recurring).** Measured on this machine (`demo.txt`):
- **Tree mode:** 1.7 s with the fetch, and 0.3 s to 0.5 s without it.
- **Overlay mode:** 0.1 s.
- **A refusal on a very stale tree:** up to 22.6 s (314 files).
- **Per round:** 300 local seats in one 31 h session, plus 117 cloud
  dispatch payloads. At about 1,000 checks a round (start plus handoff) that
  is about 28 min of machine time, run in parallel and off the critical path.
  The orchestrator's own check on each wake adds 1.7 s.
- **Induced work.**
  - Start refusals on PR seats were measured at 19 of 1,181 (round 10) and
    3 of 50 (round 11) at a 1 h lag, under 2 %. One merge each, at about
    10 min, is under 1 h a round.
  - Overlay regenerations, one per family per main change to the script, take
    about 5 min each; 4 families were in use this round.
  - The orchestrator's checkout repairs itself and induces no work.
  - The total is under 1 h a round.

**Verdict.** About 1.5 h a round against more than 115 h for one instance, at
1 or more a round. It passes by about two orders of magnitude.

## 8. The countermeasure, for the class

The rungs, in order. Each later rung says why the earlier ones are not enough.

1. **Delete the second policy tree.** A seat's policy, instruments and
   workflows come from `origin/main`, never from its work tree.
   - Round-branch stages read contracts with `git show origin/main:<path>`
     and only the round's data from `${branch}`.
   - Model routing becomes a Workflow launch argument, so the overlay family
     that only changes `model` has no reason to exist.
   - This cannot reach a hand-made copy, a seat started in a stale checkout,
     or the CLAUDE.md the harness loads from the session's cwd.
2. **Self-repair the checkouts that carry no work.** The orchestrator's
   checkout and every standing loop's tree detach to `origin/main` when they
   hold no commits of their own. This is P581's and P14's mechanism, made
   general; round-10's `orch-wt` loop did it for one tree until it died.
   - It cannot reach a work tree with commits, an untracked overlay, or a
     seat whose start nobody watches.
3. **A refusal at the seat level**: `base_fresh.py`. It runs at every seat's
   start, before every handoff, at every Workflow launch, and on each
   orchestrator wake.
   - **Tree mode.** For each policy path whose blob at HEAD differs from
     main's:
     - **STALE** if main moved it after the merge base, which is a refusal;
     - **OWN** if only the branch moved it, which is the seat's own diff and
       is allowed.
     - Uncommitted edits to a policy path are refused as overlays.
   - **Overlay mode.** An untracked script must equal main's current file with
     its declared patch applied. A patch that no longer applies, or a file cut
     from another version, is refused.
   - Each refusal prints its repair.
   - For PR seats it checks the **policy tree** at handoff (the tree prepr and
     the instruments ran from). It does not force a merge of a frozen head, by
     `fixer.md`'s handoff rule; reviewers read policy from `origin/main` under
     rung 1.

**Demonstrations** (`base_fresh/demo.sh`, transcript `demo.txt`):

| run | result |
|---|---|
| stale: the round-11 orchestrator checkout's base `8f39313a44` | FAIL, 54 stale. The lines name #3703 for `architect-planner.md`, `plan-review.md` and `audit-plan.js`. |
| stale: `plan/r11` `819aa2e3` | FAIL, 49 stale, 1 own (its roster draft) |
| stale: round-10 `orch-wt`, which `wt_sync.sh` still runs from | FAIL, 314 stale |
| stale overlay: `proto/plan-overlay/audit-plan.js`, launched 07:36Z | FAIL: its patch no longer applies to main's file |
| fresh: `origin/main` | PASS, 1.7 s including the fetch |
| fresh overlay: the same model routing re-derived against main (8 calls; carries `objective-check`) | PASS |
| control: an own policy edit committed on a fresh base | PASS, 1 own |
| control: an uncommitted policy edit on a fresh base | FAIL, 1 stale |
| control: the stale overlay checked against main's patch | FAIL |
| this RCA branch | PASS |

**Shadow run.** The incidence table is the shadow over the PR heads. At start
with a 1 h lag it would have refused 19 of round 10's 1,181 seats and 3 of
round 11's 50; at a 6 h lag, 1 and 0.

**The P3 instance gate.** `plan-objective-gate/plan_objective_gate.py` stays as
a second layer at the plan head, at the reviewer's approve and at fix-wave
dispatch. It checks the P3 contract files plus main's `objective-check`.
- It refuses all five P3 heads.
- It passes a synthetic plan carrying the block (`33fdfbf7`).
- Each of its two checks refuses alone: drift in `1bebb5fe`, objective in
  `49643dba`.
- A tool without `objective-check` is refused, not passed.

**Who decides.**
- These change tracked tooling and the orchestrator, reviewer, designer and
  P3 contracts. Policy changes only with the owner's approval, and the
  instrument freeze sends tooling to round-end triage.
- The countermeasure addresses state (c): it changes the unit from the
  instrument to the seat.
- **Overlay until then:** the orchestrator runs `base_fresh.py tree` on its
  own checkout on each wake and `base_fresh.py overlay` before any `scriptPath`
  launch, and states "read policy from origin/main" in every local seat's
  brief.
- `wt_sync.sh` should be restarted from a fresh tree.

## 9. Owed to round 11 itself (the fix, not this seat's)

1. Merge main into `plan/r11`, write the objective block, run
   `objective-check --write`, then the reviewer's delta.
2. Rule on the three started rank-2 candidates and the 13 deferred bugs before
   the next dispatch.
3. Move the orchestrator's checkout to `origin/main`; it was moved at 14:19Z.
   Regenerate the `audit-plan` overlay from main before any further P3 launch.

## 10. Did round 10 feed itself on fixes it had not adopted? Measured: no

**The question.** Did round 10 keep producing instrument changes because the
orchestrator ran its tools from trees that lacked fixes already merged, so the
same defects came back and asked for more fixes?

**How it was measured** (`base-fresh/adoption_lag.py`; rows in
`adoption.tsv`, summary in `adoption.sum`):
- **The fixes.** Every round-10 PR merged by a first-parent merge whose own
  diff touches `tools/audit/seat`, `tools/pr`, `tools/ci` or
  `.claude/workflows`. There are **362** of them.
- **Orchestrator adoption.** Each orchestrator instrument call in the four
  surviving transcripts (11-04, 11-07 to 11-10, 11-11 to 11-14, 11-14 to
  11-15) is resolved to the commit of the tree it ran in. That commit comes
  from the tree's name (`tools-wt-<sha>`, `beat-wt-<sha>`, `tick-wt-<sha>`) or
  from the session checkout's branch tip.
  - 1,321 calls resolve this way.
  - 2,782 run in trees that record no commit, and are left out.
  - A fix's lag runs from its merge to the first call made in a tree that
    contains it. It is cut at the session's end, because the next session
    starts on a newer base.
  - Only the 129 fixes merged inside an observed session are scored; the
    other 233 have no observed consumer.
- **Tick-loop adoption.** From the `code=<sha7>` field of its `TICK-PASS`
  lines.
- **A recurrence.** A later PR of the same family: the same branch name with
  part and retry suffixes removed, timed from its oldest own commit, which is
  when the seat began. Each candidate's PR body was then read for its stated
  trigger.

**Adoption lag.**
- **The orchestrator.** 110 of the 129 fixes reached the trees the
  orchestrator executed from 1 h or more after their merge: median 12.6 h,
  maximum 47.6 h. 19 arrived in under 1 h. Summed over fixes, there are
  12,866 (call, fix) pairs in which a call ran in a tree lacking a fix that
  was already merged.
- **The tick loop.** Over 188 fixes after 11-04: median 1.7 h, 90th
  percentile 17.4 h, 76 under 1 h. The loop restarts only past 25 commits on
  its own paths, so a lag on a fix it never runs is no exposure.

**Follow-ups started inside the lag window.** There are 12, each a later part
of the same group:

| fix merged | follow-up begun inside its lag window |
|---|---|
| #3252 relay-sweep | #3340 |
| #3293 handoff-path-p2 | #3317 |
| #3464 standing-contracts-p2 | #3492, #3494 |
| #3452 outside-disinfection-setpoint | #3497 |
| #3470 train-residue-p2 | #3498 |
| #3448 review-dispatch-residue-p1 | #3533, #3539, #3541, #3544 |
| #3507 closeout-prep | #3553 |
| #3499 gate-defer-barrier | #3573 |

Every one of the 12 bodies names its trigger as planned work, not as a recurring
defect: "part 2 (carries 5, 7, 8, 9, 10; carries 0-4 are part 1, merged as #3499)",
"part 3 of 6", "Part 4 of 5", and "the round-down ruling" for #3497. None
reports that a defect the merged fix had already repaired came back.

**The self-feeding loop.**
- **Count.** 0 of 362 round-10 instrument PRs (0 of the 129 observable) had a
  defect already fixed on main, but not yet adopted, as their trigger.
- **Hours.** 0 measured. The 12 candidates' 190.6 h of seat time (oldest own
  commit to merge) is planned part work, which would have been done whatever
  the lag.

**Null control.** Follow-ups per fix in the 12.6 h after the merge (the slow
group's median lag):

| group | follow-ups per fix |
|---|---|
| fixes adopted in under 1 h | 3 / 19 = 0.158 |
| fixes adopted after 1 h or more | 9 / 110 = 0.082 |

Slow adoption does not raise follow-ups; if anything the prompt group has more,
because a group's parts are dispatched together. **The loop hypothesis fails.**

Two notes on the method:
- **The after-adoption window was dropped.** A comparison over an equal window
  after adoption reads 0 follow-ups, but that window mostly falls past the
  observed sessions, so it is not used.
- **What the data cannot show.** Round 10's volume of instrument PRs is
  explained by carries and parts planned before their predecessors merged. It
  is not explained by recurrences of defects that had been fixed but not
  adopted. Recurrences that never produced a PR (a seat that worked around a
  stale tool by hand) are invisible to this method. Before 11-04 the
  orchestrator's trees are unrecorded except for round 10's `orch-wt`, which
  a loop kept on main every 600 s from 10-28 to 11-04.

**What it changes.** The cost test in section 7 stands without a loop term.
Adoption lag is real (median 12.6 h for the orchestrator), and section 8's
self-repair rung removes it. It is not shown to have generated round 10's
instrument work.
