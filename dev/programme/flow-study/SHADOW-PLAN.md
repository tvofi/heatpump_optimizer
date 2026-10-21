# Round 10 shadow plan: the flow groups folded into the live roster

**Base:** live roster `origin/handoff/audit-r10-roster` at 617ce1316 when planned; the committed shadow is rebuilt at 2c76c3128 (one stage change on R10-MERGE-PR-MANDATE) (108 groups: 51 done, 20 in progress, 34 not started, 3 queued).

**Shadow:** `roster/shadow-r10-groups.json`, 124 groups. It adds:
- 16 flow groups
- 6 carries folded into existing groups

`node tools/policy/brief_lint.mjs roster/shadow-r10-groups.json` run from a main checkout prints `TOTAL: 0 error(s)`. Rebuild it at any newer roster ref with `python3 tools/build_shadow.py origin/handoff/audit-r10-roster`.

Hour 0 (T0) is the moment the orchestrator adopts the plan. "Day" means 24 h from T0, not a calendar day.

## 1. What changes in the existing roster

| group | change | why |
|---|---|---|
| R10-POLICY-FIXER-MD | carry: absorb `main` only on conflict or DIRTY (K5); fix-review step 11 stands on the post-workflow pr-contract run | 40% of fix commits are absorbs; step 11 duplicates pr-contract |
| R10-RCA-HEADMOVED | carry: **rescope to record-only**; the countermeasure is FLOW-PULL step 9, K5 and FLOW-MQ-PROBE | measurement and countermeasure already exist |
| R10-RCA-ORCH-CONTINUITY | carry: run the cost test against FLOW-ANDON | the countermeasure is ready |
| R10-ORCH-MACHINERY | carry: its beat advances the heartbeat ref | one liveness signal, not two |
| R10-CI-LAYOUT-P1 | carry: keep the train-hold arm where D-1 moves record-autofix | RECORD-PITCH builds on it |
| R10-CI-LAYOUT-P2 | carry: the umbrella reports on `merge_group` if the queue is adopted | the trap of a required check that never reports |
| 15 coordinator.py edges | the decision seat's ruling: 8 dropped, 3 required and 4 recommended edges added, plus HEAT-METER ← THERMAL-POWER-OPTION (STUDY K7) | critical depth 11 → 8 |
| none | no group is split, deleted or merged | splitting shortens no chain; see FUTURE-STATE §1 |

To verify, not caused by this plan:
- R10-PREPR-CAP may already be delivered by #2526.
- R10-ORCH-MACHINERY part (3) overlaps R10-PLAN-ARTIFACT (#2558).

## 2. Lanes and dispatch order (pull)

| lane | what it holds | cap |
|---|---|---|
| A | critical chain and coordinator | 4 (2 until FLOW-RECHAIN merges) |
| B | other product groups | 4 |
| C | process groups | 3 |
| F | fly-ins (`R10-FLY-*`) | 2 |
| **K** | the 16 flow groups: an improvement allowance on top of A–F during the drain | **2** |
| expedite | line-stop items | bypasses the caps, one at a time |

**Flow-group order** (each only once its `after` groups are done):
- **Expedite, now:**
  1. FLOW-BODY-PATCH
  2. FLOW-MAIN-GATE (after #2570)
  3. FLOW-YIELD-PROBE (ruling R13: explain the real-catch fall before any threshold relies on it)
  4. FLOW-DISPATCH (expedite since revision 4: no technical dependency, and its cost recurs for every seat)
- **Then:**
  5. FLOW-RECHAIN (applies the seat's ruling in roster PR-A)
  6. FLOW-ROSTER-FREEZE
  7. FLOW-BODY-ONLY
  8. FLOW-PULL
  9. FLOW-ANDON
  10. FLOW-WIP
  11. FLOW-JIDOKA
  12. FLOW-POSTMERGE
  13. FLOW-BOARD
  14. FLOW-AUTOTRAIN
  15. FLOW-MQ-PROBE
  16. FLOW-RECORD-PITCH (conditional)

**Within lanes A–F:** the longest remaining chain first, then the smallest size.

## 3. Phasing against today's congestion (verified 2026-10-21 ≈ 14:05Z)

### 3.1 What the system holds right now

23 open non-record pull requests and 1 record PR (#2568). The newest verdict on each, from the `verdict/*` and `review/*` bus refs:

| state | PRs | what it needs |
|---|---|---|
| `merge` verdict at the current head | #2560, #2547, #2531 | the next pitch |
| `merge` verdict on an ancestor of the head | #2513 (R10-ROSTER-OPS), #2544, #2548 (its head was not available locally; check) | `app_approve.sh --carry`, then the pitch; a reviewer only if the carry refuses |
| blocked at the head | #2563, #2561, #2529, #2549 (all **carry-missing**), #2567 (mutation-survivor), #2527 (metric-gamed), #2559 (head-moved) | return to the same fixer this turn |
| no review yet | #2570, #2569, #2566, #2558, #2557, #2554, #2545, #2528, #2524, #2521 | a reviewer each; this is the queue |

**Diagnosis**
- **Review is the constraint today.** There are 10 unreviewed heads, plus 7 blocked heads that will return for review. That is about 17 reviews owed in the next ~12 h, roughly 2–3 reviewers running continuously.
- **4 of the 7 current blocks are carry-missing.** That is the class FLOW-JIDOKA moves before handoff (ruling R7).
- **Adding all 10 flow groups at T0 would raise PR WIP from 23 to 33**, and the new PRs would queue behind those 17 reviews. **The first version of the shadow plan did exactly that ("ride expedite"). It is withdrawn.**
- **The roster PR #2559 was just blocked head-moved.** Every `roster_edit.py --push` (append-group, append-carry, set-after) moves its head again. Roster edits must therefore come in **one burst**, followed by **one** review, not as a trickle.

### 3.2 The phases (revised 2026-10-21 after the orchestrator's evidence)

**Phase 0: drain, stop starting (now until about 12 h from now).**
- Dispatch nothing not yet started, except an expedite or a size-S fly-in. **Two flow groups are expedite, because they repair the line:**
  - **R10-FLOW-BODY-PATCH:** no tool can fix a refused body at an unchanged head today.
  - **R10-FLOW-MAIN-GATE:** the train's gate reads pending checks as "revert main". Until it merges, read main by hand: latest run per required context only (§3.3 rule B).
  - **R10-FLOW-YIELD-PROBE** and **R10-FLOW-DISPATCH** are expedites too (since revision 4).
  - None of the four is on the roster yet: §3.3 rule A says how their seats are briefed and reviewed.
- Load a train each pitch with `--bot-prs`. Carry moved verdicts with `app_approve.sh --carry` instead of re-reviewing.
- Blocked heads go back to their fixer in the same turn. Reviewers take the unreviewed heads, oldest first, posting verdicts once the head's required checks have concluded.
- **R4 is not yet true in the tool.** `update_pr.sh` merges main on every run, so until R10-FLOW-BODY-ONLY lands:
  - run `update_pr.sh` only when the code tip moved, or the PR is DIRTY or conflicted;
  - apply a body-only fix with the K14 interim (`app_push.sh` from a clean worktree at the PR's exact head, `--dry-run` first, head sha checked unchanged after), until BODY-PATCH lands. Carrying a verdict does not repair a refused body.
  - The interim has **never run live**. The #2560 case revision 3 cited was stale; the first real test is #2561, if its carry-missing block survives #2559's merge (STUDY K14).
- **The pitch** is "on the hour, or when the previous train ends, whichever is later".
  - **A train boards only heads that are verdicted and green at load time**, proved together in one batch (`train.sh` always runs `batch`). It never waits for a slow head: that head boards the next pitch.
  - The pitch is dominated by one batch CI run, measured at about 57 min (13:47Z → #2544 merged around 14:44Z, held by `closures`, `graders-head-copy` and `fast (3.14)`). That is expected: one proof per pitch, not one per PR.
  - The model shows a 2-h pitch costs about 2 h of round time.

**Phase 1a: merge #2559 first, under a bounded roster freeze** (the clock is redefined in revision 4).
- **The freeze** runs from #2559's review dispatch until #2559 merges. No `roster_edit.py --push` in that window. It is unchanged, because a merge verdict must stay at the head it names.
- **The 4-h bound runs only while #2559 is under review,** from review dispatch until a verdict posts. That is the phase that looped five times. It never runs while nothing is reviewing.
  - **Blocked verdict:** the freeze lifts at once. Push the held edits, then request one fresh review; the next review restarts the clock.
  - **No verdict within 4 h:** lift the freeze and push the held edits. That stale review then needs re-dispatching.
  - **`merge` verdict at the head:** the bound stops. The freeze holds **without a bound** until #2559 merges, since lifting it would only re-stale the verdict.
- **Merging #2559:**
  - It boards **as the first car of the next train**. With no train running, it merges directly at once (nudge step 7: a lone verdicted PR).
  - Boarding to merge is about one CI run (about 57 min measured).
  - It never merges alongside a running train: a foreign merge forces the batch to re-prove.
- **Why not start the clock at boarding,** as the orchestrator proposed? That would leave the review phase, the one that cost five rounds, unbounded. And boarding to merge needs no bound: it is one train's CI.
- **The proposal's real point stands:** the clock must not burn while #2559 merely waits. Stopping it at the verdict does that.
- **Live state at revision 4:** #2559 holds a `merge` verdict at 802b3850 (16:58Z). The clock is stopped, the freeze holds, and #2559 is first car of the next train.
- Merging #2559 also clears `BAD-DEST` on #2529, #2547 and #2561.

**Phase 1b: two roster PRs, one review each** (split in revision 4, agreeing with the orchestrator's default). #2559 took five rounds at a fraction of the original single burst's size, and the burst mixed one judgement-heavy change with many mechanical ones.

- **Roster PR-A, the re-chain only** (once #2559 and #2513 have merged).
  - Contents: the seat's 8 drops, 3 required and 4 recommended edges, and HEAT-METER ← R10-THERMAL-POWER-OPTION (`set-after`), plus the architect-note and brief text from the decision file and the seat's three files as evidence.
  - Review by one Opus reviewer, against the seat's decision file, edge by edge.
  - It goes first: it is the critical-path lever, and lane A goes to 4 the hour it merges.
- **Roster PR-B, the bookkeeping** (after PR-A merges; both ride the one roster branch, so they are sequential).
  - Contents:
    - the 16 flow groups (`append-group`);
    - the 6 carries;
    - the held stage changes;
    - fly-in registrations (`R10-FLY-*`);
    - the `set-resume` notes.
  - It is **mechanically reviewable.** Each appended group must equal its `roster/groups/<NAME>.json` at the pinned pack commit (stage and resume fields excepted), each carry must equal its `CARRIES` text, `brief_lint` must print `TOTAL: 0`, and `carry_audit.py owners` must show no orphan. The reviewer verifies those checks and reads only what they do not cover.
  - If PR-A's review loops, PR-B may go first instead: it unblocks rule-A registrations.
- **The freeze applies to each** in turn, under the same clock as Phase 1a.

**Phase 2: improvements through lane K, two at a time (from about 12 h).** The order is §2's, each once its `after` group has merged:
- **ROSTER-FREEZE and BODY-ONLY first.** They remove the two head-moving loops the orchestrator found.
- **Then:**

  | flow group | waits for |
  |---|---|
  | PULL | — |
  | ANDON | #2549 |
  | WIP | PULL |
  | JIDOKA | #2528 |
  | POSTMERGE | #2554 |
  | BOARD | #2558 |
  | AUTOTRAIN | PULL and #2549 |

- **Critical-path links** (ADVISOR, SCORES, LIVESTATE, PARAMS-OWNER, HEAT-METER, COP-GATE, UX-HEALTH, ARCH-DOCS) get review before anything else in the queue.

**Phase 3: decide (around day 2).**
- FLOW-MQ-PROBE runs after R10-CI-LAYOUT-P1. You decide on the queue.
- FLOW-RECORD-PITCH is then built or closed.

### 3.3 Rules for cases revision 3 left undefined (revision 4)

**Rule A: an expedite or fly-in fixer whose group is not on the roster yet.**
1. **Brief source.** The dispatch names the group id: an `R10-FLOW-*` id, or `R10-FLY-<topic>` for a fly-in. It also names the brief source the seat and its reviewer read instead of the roster:
   - **flow group:** `dev/programme/flow-study/roster/groups/<NAME>.json` at a **pinned** commit of `claude/dazzling-gauss-7l3u2b`;
   - **fly-in:** the brief text the orchestrator writes in the dispatch, also posted once on #201.
2. **PR body.** It states `Group: <ID> (registration pending: roster PR-B)` and cites that brief source.
3. **Review.** The reviewer reviews against the pinned brief source exactly as against a roster brief. The verdict grammar is unchanged. **"group: none" is not acceptable**; "group pending" with a cited, pinned brief is.
4. **Carries.** A carry **to** a pending group is `BAD-DEST` until PR-B merges. Route it to the group's issue or to an existing roster group instead, or hold it until PR-B.
5. **Merging** before registration is allowed: the delivery row is per PR, not per group. PR-B then registers the group with `stage: done` and its merge sha.

**Rule B: `--overlap` says "main is not green" while the latest runs of all required contexts are pending.**
1. **That is wait, not red.**
   - Do not revert.
   - Do not dispatch a main-red fixer.
   - Never pass `--allow-red`.
   - Do not start an overlapping train: the gate's refusal to load is right, only its wording is wrong.
2. **Read main yourself:** the latest run per context in ruleset `main-protect-checks`, read live. Ignore `record*`, `nightly-status`, `delivery-status` and other non-required contexts.
3. **Re-check at the next tick.**
   - When every required context's latest run is success or skipped, main is green: load.
   - When one has concluded failure, main is red: nudge step 11 applies (revert only when the diff can reach the failure).
4. **Stalled pending.** If the required contexts stay pending longer than twice the measured train CI time (about 2 h at 57 min), treat it as stalled, not red: check for zero runs and run `approve_held_runs.sh`.
5. **Record each instance** in one line on #201 (time, main sha, the gate's line, your reading). That is R10-FLOW-MAIN-GATE's evidence.

**Effect in the model**, with the seat's chain (depth 8), drain-first, in-progress groups treated as not started, and lane K at 2:

| scenario | last merge |
|---|---|
| **this plan** | **≈ 92 h** |
| lane A kept at 2 | ≈ 103 h |
| 2-h pitch | ≈ 94 h |
| lead time ramping over 96 h | ≈ 109 h |
| no re-chain | ≈ 109 h |
| today's process (live roster only) | ≈ 207 h |

## 4. Projected schedule (model output: `tools/simulate.py`, rendered by `tools/gen_plan.py`)

Lane K is the flow allowance; BODY-PATCH and MAIN-GATE dispatch inside the drain as expedites. "after" lists the edges as re-chained by the seat.

day 0: 31 · day 1: 29 · day 2: 8 · day 3: 4

| day | merge h | start h | group | lane | size | kind | stage now | after (as re-chained) |
|---|---|---|---|---|---|---|---|---|
| 0 | 11 | 0 | R10-FLOW-BODY-PATCH | K | S | instrument | not-started | — |
| 0 | 11 | 0 | R10-FLOW-MAIN-GATE | K | S | instrument | not-started | — |
| 0 | 11 | 0 | R10-FREQ-DEFROST | A | S | defect | in-progress | R10-TRUST-RELATIVE |
| 0 | 11 | 0 | R10-HANDOVER-REFRESH | C | S | record | in-progress | — |
| 0 | 11 | 0 | R10-I5-DOCS | C | S | docs | in-progress | R10-I1, R10-STRUCTURE-BLIND, R10-REGISTRY-LEAK |
| 0 | 11 | 0 | R10-PREPR-CAP | C | S | instrument | in-progress | — |
| 0 | 11 | 0 | R10-RCA-FRICTION | C | S | policy | in-progress | — |
| 0 | 11 | 0 | R10-RCA-HANDOFF-SLIP | C | S | rca | in-progress | — |
| 0 | 11 | 0 | R10-REPLAY-CAP | B | S | defect | in-progress | — |
| 0 | 11 | 0 | R10-ROSTER-OPS | C | S | instrument | in-progress | — |
| 0 | 11 | 0 | R10-ROSTER-PUSH-RACE | B | - | defect | in-progress | — |
| 0 | 11 | 0 | R10-TICK-OWED-LEVEL | C | S | instrument | in-progress | — |
| 0 | 11 | 0 | R10-TICK-RELAY-DECOUPLE | C | S | fix | in-progress | — |
| 0 | 11 | 0 | R10-UPDATE-PR-SIGNALS | C | S | instrument | in-progress | — |
| 0 | 12 | 0 | R10-ADVISOR | A | M | owner | in-progress | R10-UX-SETUP, R10-SAV-REASONS |
| 0 | 12 | 0 | R10-CI-RATCHET-RED | B | M | defect | in-progress | — |
| 0 | 12 | 0 | R10-NIGHT-FOLDS | A | M | defect | in-progress | R10-VENT-DETECTOR |
| 0 | 12 | 0 | R10-PLAN-ARTIFACT | C | M | fix | in-progress | — |
| 0 | 12 | 0 | R10-RCA-ORCH-CONTINUITY | C | M | rca | in-progress | — |
| 0 | 12 | 0 | R10-REPLAY-LANE | B | M | owner | in-progress | R10-DIAG-REPLAY |
| 0 | 21 | 11 | R10-FLOW-DISPATCH | K | S | instrument | not-started | — |
| 0 | 21 | 11 | R10-FLOW-YIELD-PROBE | K | S | study | not-started | — |
| 0 | 21 | 12 | R10-CURRENCY | A | S | defect | not-started | — |
| 0 | 21 | 12 | R10-INPUT-STALENESS | A | S | defect | not-started | — |
| 0 | 21 | 12 | R10-LOOP-CPU | A | S | defect | not-started | R10-NIGHT-FOLDS |
| 0 | 21 | 12 | R10-POLICY-GATE-SCOPING | C | S | policy | not-started | R10-TICK-DRIVERS |
| 0 | 21 | 12 | R10-POLICY-LINT-FAMILY | C | S | instrument | not-started | — |
| 0 | 21 | 12 | R10-RCA-HEADMOVED | B | S | study | not-started | R10-RCA-FRICTION |
| 0 | 21 | 12 | R10-REPLAY-SCOPED | B | S | owner | not-started | R10-REPLAY-LANE, R10-TICK-ORCH, R10-TRAIN-HOLD, R10-REF-PRIVACY |
| 0 | 23 | 12 | R10-SAV-COMFORT | B | M | owner | not-started | R10-SAV-BASELINE |
| 0 | 23 | 12 | R10-SOLVER | B | M | defect | not-started | R10-SAV-REASONS, R10-TARIFF |
| 1 | 24 | 0 | R10-CI-LAYOUT | C | XL | instrument | in-progress | — |
| 1 | 29 | 12 | R10-SCORES | A | L | owner | not-started | R10-ADVISOR, R10-RATIO-SITES |
| 1 | 29 | 21 | R10-CONFIG-NOTICES | A | S | arch | not-started | — |
| 1 | 29 | 21 | R10-FLOW-RECHAIN | K | S | instrument | not-started | R10-ROSTER-OPS |
| 1 | 29 | 21 | R10-FLOW-ROSTER-FREEZE | K | S | instrument | not-started | R10-ROSTER-OPS |
| 1 | 29 | 21 | R10-LEARNER-DEFAULT | A | S | defect | not-started | — |
| 1 | 29 | 21 | R10-MERGE-SUBJECT-HARDEN | C | S | instrument | not-started | — |
| 1 | 30 | 21 | R10-BRIEFS-FOLD | C | M | policy | not-started | R10-ARCHSCORE-COVERAGE, R10-D15-GRADER |
| 1 | 30 | 21 | R10-BUFFER-STORE | B | M | production | queued | R10-SETPOINT-BOOST |
| 1 | 30 | 21 | R10-COP-PARTLOAD | B | M | production | queued | R10-SETPOINT-BOOST |
| 1 | 30 | 21 | R10-RATIO-ANCHOR | A | M | defect | not-started | — |
| 1 | 32 | 23 | R10-CARD-VOICE | B | M | feature | not-started | R10-DEEPLINK-HANDLERS |
| 1 | 33 | 24 | R10-CEILING-PROBE | B | M | production | not-started | R10-SETPOINT-BOOST, R10-CI-LAYOUT, R10-NIGHT-FOLDS |
| 1 | 36 | 29 | R10-FLOW-BODY-ONLY | K | S | instrument | not-started | R10-UPDATE-PR-SIGNALS, R10-FLOW-BODY-PATCH |
| 1 | 36 | 29 | R10-FLOW-PULL | K | S | policy | not-started | — |
| 1 | 36 | 30 | R10-POLICY-FIXER-MD | C | S | policy | not-started | R10-RCA-FRICTION, R10-BRIEFS-FOLD |
| 1 | 37 | 29 | R10-LEARNER-ETA | A | M | study | not-started | — |
| 1 | 38 | 24 | R10-ORCH-MACHINERY | C | L | instrument | not-started | R10-ROSTER-OPS, R10-CI-LAYOUT |
| 1 | 38 | 30 | R10-DEMAND-OVERBOOK | A | M | production | queued | R10-SETPOINT-BOOST |
| 1 | 41 | 36 | R10-FLOW-ANDON | K | S | instrument | not-started | R10-TICK-RELAY-DECOUPLE |
| 1 | 41 | 36 | R10-FLOW-WIP | K | S | instrument | not-started | R10-FLOW-PULL |
| 1 | 42 | 29 | R10-SENSOR-PAYLOAD | A | L | arch | not-started | R10-SCORES |
| 1 | 43 | 36 | R10-MUTATION-ANCHOR | C | M | instrument | not-started | — |
| 1 | 44 | 37 | R10-THERMAL-POWER-OPTION | A | M | production | not-started | — |
| 1 | 45 | 38 | R10-MUTANT-SKIP | C | M | instrument | not-started | — |
| 1 | 46 | 29 | R10-CI-LAYOUT-P1 | C | XL | instrument | not-started | R10-CI-LAYOUT |
| 1 | 46 | 29 | R10-LIVESTATE | A | XL | arch | not-started | R10-SCORES, R10-PUMP-MODEL, R10-LOOP-CPU |
| 1 | 46 | 41 | R10-FLOW-JIDOKA | K | S | instrument | not-started | R10-PREPR-CAP |
| 1 | 46 | 41 | R10-FLOW-POSTMERGE | K | S | instrument | not-started | R10-ROSTER-OPS |
| 2 | 50 | 46 | R10-FLOW-BOARD | K | S | instrument | not-started | R10-PLAN-ARTIFACT |
| 2 | 52 | 46 | R10-FLOW-AUTOTRAIN | K | M | instrument | not-started | R10-FLOW-PULL, R10-TICK-RELAY-DECOUPLE |
| 2 | 55 | 46 | R10-ARCH-SHAPES | A | L | arch | not-started | R10-SENSOR-PAYLOAD, R10-FREQ-DEFROST, R10-LIVESTATE, R10-INPUT-STALENESS |
| 2 | 55 | 50 | R10-FLOW-MQ-PROBE | K | M | study | not-started | R10-CI-LAYOUT-P1 |
| 2 | 58 | 55 | R10-FLOW-RECORD-PITCH | K | S | instrument | not-started | R10-CI-LAYOUT-P1, R10-FLOW-PULL, R10-FLOW-MQ-PROBE |
| 2 | 59 | 46 | R10-CI-LAYOUT-P2 | C | XL | instrument | not-started | R10-CI-LAYOUT-P1 |
| 2 | 59 | 46 | R10-PARAMS-OWNER | A | XL | arch | not-started | R10-ARCHSCORE-COVERAGE, R10-SERVICES-GUARD, R10-LIVESTATE, R10-NIGHT-FOLDS, R10-RATIO-ANCHOR |
| 2 | 71 | 59 | R10-HEAT-METER | A | XL | owner | not-started | R10-LEARNER-ETA, R10-INPUT-STALENESS, R10-UX-SETUP, R10-RATIO-ANCHOR, R10-PARAMS-OWNER, R10-ARCH-SHAPES, R10-THERMAL-POWER-OPTION |
| 3 | 76 | 71 | R10-COP-GATE | A | M | study | not-started | R10-HEAT-METER, R10-SENSOR-PAYLOAD |
| 3 | 79 | 71 | R10-CONFIGFLOW-PAGES | A | L | arch | not-started | R10-HEAT-METER |
| 3 | 84 | 76 | R10-UX-HEALTH | A | L | owner | not-started | R10-SCORES, R10-COP-GATE, R10-HEAT-METER |
| 3 | 92 | 84 | R10-ARCH-DOCS | A | L | feature | not-started | R10-VENT-DETECTOR, R10-NIGHT-FOLDS, R10-RATIO-ANCHOR, R10-INPUT-STALENESS, R10-CURRENCY, R10-TRUST-RELATIVE, R10-FREQ-DEFROST, R10-LOOP-CPU, R10-SAV-BASELINE, R10-SAV-REASONS, R10-ADVISOR, R10-SCORES, R10-PUMP-MODEL, R10-LIVESTATE, R10-CONFIG-NOTICES, R10-ARCHSCORE-COVERAGE, R10-PARAMS-OWNER, R10-SENSOR-PAYLOAD, R10-ARCH-SHAPES, R10-LEARNER-ETA, R10-HEAT-METER, R10-COP-GATE, R10-UX-HEALTH, R10-CONFIGFLOW-PAGES, R10-SOLVER, R10-I5-DOCS, R10-TICK-DRIVERS, R10-BRIEFS-FOLD, R10-DIAG-REPLAY, R10-REPLAY-LANE, R10-REPLAY-SCOPED, R10-TRAIN-HOLD, R10-DEEPLINK-HANDLERS |

## 5. Model assumptions (change any of them and re-run)

- **Pitch:** hourly. Everything verdicted whose `after` edges are merged lands together (the batch proof). A refusal is not modelled; the train in reality stops at that entry and the rest wait one pitch.
- **Lead time, dispatch → verdicted:**
  - It ramps over 48 h from the round-10 medians (S 11, M 12, L 20, XL 24 h, first commit → merge) to the targets (S 3, M 5, L 8, XL 12 h).
  - Pessimistic ramp (96 h): last merge at about 97 h.
  - No ramp (lead times as today): about 158 h with the seat's re-chain and the lane caps.
- **In-progress groups** are taken as needing a full lead time from T0 (`INPROG=1.0`): the congestion is real, and half-done was optimistic. With `INPROG=0.5` the end moves by about 1 h.
- **Drain first:** no not-started group dispatches before T0 + 12 h except RECHAIN and fly-ins (`HOLD=12`). The flow groups have their own 2-slot lane K (`KAIZEN=2`).
- **Fly-ins:** one size-S fly-in every 4 h, in lane F. That is about 0.25/h, the measured rate.
- **Scope frozen:** no new roster groups mid-round. With groups still added at round 10's rate (one every 3 h), the last *original* group still lands at about 92 h; lanes B and C absorb them. Without the freeze, though, "the round" never ends.
- **Re-chain:** exactly the decision seat's ruling, in `tools/simulate_rules.py` (8 drops, 3 required, 4 recommended, plus the study's THERMAL-POWER-OPTION edge): depth 8. The recommended and study edges cost 0 h.
- **Seat capacity is not modelled.** 13 lanes of WIP assume about 13 concurrent seats plus reviewers. With fewer, the cap is the seat count.

## 6. Round 11 on the 100-h template

| phase | budget | entry rule | exit rule |
|---|---|---|---|
| P1 find | ≤ 10 h | baseline pinned at the round-10 stamp | every scope's finder report in |
| P2 verify, judge, register | ≤ 10 h | P1 done | register PR merged; **scope frozen** |
| P3 plan | ≤ 4 h | register merged | roster lints clean at first pass (no correction tail); chains by owning seam; groups S/M; critical chain ≤ 60 h at target lead times |
| P4 fix wave | ≤ 60 h | roster merged | every group merged or deferred by the owner |
| P5 drain and stamp | ≤ 6 h | P4 done | stamp pushed |
| project buffer | 10 h | consumed by any phase | fever chart on the flow board: chain % done against buffer % used |

**Fix-wave sizing:**
- Capacity at the future state is about 1.2 planned groups/h, after fly-ins and process work.
- P4 can therefore carry about 70 groups. Round 10's opening scope of 52 fits.
- Its mid-round growth to 108 does not fit, which is why the scope freezes at the register.
