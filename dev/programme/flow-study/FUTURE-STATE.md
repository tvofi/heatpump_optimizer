# Round 10 Lean study: a full programme round in about 100 hours

Prepared 2026-10-21 (final overhaul). It **supersedes** the first report (`r10-lean-future-state.md`).

**What changed since the first report**
- Demand is now a whole round in about 100 h, not one group per hour.
- Group splitting and stacking are dropped.
- Fly-ins are designed in.
- Redundancy against the existing roster is assessed.
- Mechanical work that agents still do by hand is wired into groups.

**Read-only throughout.** Nothing was written to the repository, its branches, issues or PRs. Figures are measured at:
- `origin/main` 22615537a
- the live roster `origin/handoff/audit-r10-roster` 617ce1316
- the review/verdict bus refs
- two GitHub list calls, made in the first study

The rest of the pack:

| file | contents |
|---|---|
| `STUDY.md` | one pre-study section per group, for the fixers |
| `SHADOW-PLAN.md` | the projected schedule and the day-by-day fold-in |
| `ORCHESTRATOR-PROMPT.md` | the handover prompt |
| `roster/shadow-r10-groups.json` | the shadow roster: live + flow groups + folded carries, `brief_lint` `TOTAL: 0` |
| `roster/groups/*.json` | the new groups, ready for `roster_edit.py append-group` |
| `tools/` | the builder and the projection model |

---

## 1. Demand and takt

| | value |
|---|---|
| Customer demand | one full programme round in about **100 h**, from the previous round's stamp to this round's stamp |
| Round takt | 100 h per round |
| Round 10 so far | opened at v7.0.0 (2026-10-14 15:27 +02:00); **168 h elapsed**; 51 of 108 roster groups done; 57 open |
| Round 10, projected on today's process | about **207 h more**, so about 375 h in total: 3.75× the demand |

The round's phases (the value stream), with their round-10 measurements:

| phase | round 10 actual | budget at a 100-h takt |
|---|---|---|
| P1–P2 Find, verify, judge, register (v7.0.0 → register PR #2244 merged 10-15 14:25) | **23 h** | 20 h |
| P3 Plan: roster with briefs (roster commit 14:37; roster PR #2277 merged 18:38; then 9 correction PRs `audit-r10-roster-c2…c9` and ≈ 20 roster-edit merges over the round) | 4 h, plus a long tail of corrections | 4 h, complete at first pass |
| P4 Fix wave | **145 h so far, ≈ 207 h to go** | 60 h |
| P5 Drain, stamp, record | (not reached) | 6 h |
| Project buffer (critical-chain method) | none | 10 h |

**P4 is about 90% of the round.** Inside P4 the length is set by:
- **the critical chain**: the longest run of `after` edges, at the lead time of each link;
- **lead time per link**: about 8–20 h measured, set by waiting, rework and integration churn;
- **capacity on the chain's lane**: one `coordinator.py` lane, capped at 2;
- **scope growth**: the roster grew from 52 to 108 groups during the round;
- **availability**: merges landed in 71% of hours; there were silent stops of 6 h and 16 h.

Group count matters only through capacity. That is why **splitting groups does not help**: it adds a review, a CI run, a record and a pitch slot per part, and shortens no chain. This answers your doubt.

---

## 2. Current state (measured; enumerators in STUDY §0)

- **Critical chain:** 11 levels of not-done `after` edges. 16 not-done groups sit on one serial chain through `coordinator.py` (architect-note positions 6–25 of 25).
  - Yet **each of those groups already owns a named, disjoint seam** of that file ("Touch only the owning seam named here").
  - The chain orders merges on a file. In most links, no group consumes another's change.
  - orchestrator.md §5, which every architect note cites as its authority, contains no chain rule at all.
- **Lead time** (first commit → merge, medians): S 8–15 h, M 12 h, L 20 h. A fix branch absorbs `main` a median of 4 times (40% of its commits), and each absorb re-runs `fixer.md` steps 2–8 and CI.
- **Review first-pass yield** is 48% (2.18 verdicts per PR). 30 verdicts re-reviewed unchanged code after a head moved. About 38% of blocks are bookkeeping a script checks: carry markers, red-check answers, body.
- **Integration:** 51% of all merges to `main` were record PRs and about 9% roster edits. Every move stales every open head.
- **WIP:** 20 roster groups in progress against `HPO_WIP_CAP` 6 (pr_cap.py `dispatch-gate`, since #2525), plus fly-ins the cap cannot see.
- **Fly-ins:** 34 merges in 145 h (0.23/h, peak 10 a day), median 200 lines, nearly all process or tooling. Besides those, **56 groups were added to the roster mid-round**.
- **Mechanical work done by agents:**
  - the 18-step nudge scan every turn
  - building the train queue by hand
  - per-merge bookkeeping
  - record-PR approvals
  - deciding whether a moved head carries its verdict
  - reviewers re-deriving red-check answers that the pr-contract re-run already checked at that head (HANDOVER's own decision: "Never re-gate an unchanged head")

---

## 3. Root causes, worked back from the 100-h demand

1. **The chain is built by file, not by seam.** That makes the critical chain about 2× longer than the work requires, and caps the chain's lane at 2.
2. **Lead time per link is 70–80% waiting and rework:** absorbs, re-reviews, record churn, serial train CI, review before CI concludes.
3. **Scope is not frozen at the register.** The round doubled, so it cannot converge on a date.
4. **The line stops silently.** No heartbeat is visible off the host.
5. **Mechanical decisions sit in the LLM loop.** They wait for a turn, and they vary with the model running the turn.

---

## 4. Future state

### 4.1 The round as a value stream

```
v(N-1) stamp ─► P1 find (pinned baseline) ─► P2 verify+judge+register ─► P3 plan ─► P4 fix wave ─► P5 drain+stamp
    0 h              ≤10 h                        ≤20 h                   ≤24 h       ≤84 h          ≤90 h  [+10 h buffer]
                                                       │ scope freezes here
P4: ready queue (ranked by critical chain) ─pull─► FIX ─► prepr+jidoka ─► PR ─► CI ∥ REVIEW ─► verdict
        ▲ lanes A4 B4 C3 F2 (CONWIP 13)                                               │
        └──────── one in when one merges ◄── :00 AUTO-TRAIN (batch proof, --bot-prs) ◄─┘
                                               └─► POST-MERGE bookkeeping (scripted)
heartbeat ref every tick ─► off-host watcher ─► owner alert > 20 min (andon)
flow board: round fever chart = critical chain done vs buffer consumed
```

### 4.2 Rules

- **Plan for the chain, not the count (P3).**
  - Chains order groups whose **owning seams overlap**, not groups that share a file.
  - Each group is sized S or M **at planning**. This is sizing a new plan, not re-cutting live groups.
  - The critical chain at target lead times must fit P4's 60 h with its buffer.
  - The roster passes `brief_lint` before P4 starts, so P3 has no correction tail.
- **Scope freezes at the register.** A mid-round finding goes to the next round's register unless it is expedite, or a fly-in of size S.
- **Pull with lane caps.**

  | lane | what it holds | cap |
  |---|---|---|
  | A | critical chain and coordinator | 4 |
  | B | other product groups | 4 |
  | C | process groups | 3 |
  | F | fly-ins | 2 |

  - Within a lane, dispatch the longest remaining chain first.
  - The expedite class (red main, quota, outage, security, owner-flagged) bypasses the caps, one at a time.
- **Merge on an hourly pitch, mechanically.** Each hour a train loads every head whose newest verdict is `merge` at that head, or whose verdict carries (`app_approve.sh --carry`). It runs as one batch proof with `--bot-prs`, so record PRs land inside the pitch.
- **Heads stay frozen.** Absorb `main` only when the head is DIRTY or `merge-tree` reports a conflict. The batch proves the combined result.
- **Review adds only what CI cannot produce:** the mutation proof, the finder's harness at both ends, the null control, the class attack, the architecture judgement. The red-check-answer check (fix-review step 11) stands on a green pr-contract run that started after the head's last workflow concluded.
- **Error-proof before handoff.** prepr runs the same `carry_audit.py check` that pr-contract runs after the push.
- **Andon:** a heartbeat ref is pushed every tick; an off-host watcher alerts you after 20 min of silence.

### 4.3 Why lane A is 4, not 2

The coordinator cap of 2 protected a file-ordered chain. Once the chain orders seams, parallel PRs on disjoint seams of `coordinator.py` merge cleanly, and the batch proof catches the exception. The train stops at the first refusal and returns that PR to its fixer.

In the projection, lane A at 2 → 4 on a re-chained roster cuts the remaining round from 95 h to 77 h.

### 4.4 Fly-ins, designed in

| class | definition | handling |
|---|---|---|
| Expedite | red main, Actions quota exhaustion, outage, security, owner-flagged | bypasses caps, one at a time; direct merge |
| Fly-in | size S; owner request or a defect the line found in itself | registered at dispatch as `R10-FLY-<topic>` with `roster_edit.py append-group` (counted, capped, recorded); lane F, WIP 2, target lead 4 h; merges in the pitch |
| Anything larger | — | not a fly-in: it goes to the next round's register (scope freeze), or, if the owner rules it into this round, to the ready queue in its lane |

**Sizing:** lane F gives about 0.5/h of capacity against 0.23/h measured (peak 0.42/h). A burst waits in arrival order; an expedite never waits.

**Accounting:** the flow board reports planned-group progress and fly-ins separately, so fly-ins never mask chain progress.

---

## 5. Redundancy: what the flow groups make unneeded

| existing group | effect of the flow groups | recommendation |
|---|---|---|
| R10-RCA-HEADMOVED (study, not started) | its countermeasure is already designed: FLOW-PULL step 9, the K5 carry, FLOW-MQ-PROBE; its measurement is already in this study | **Rescope to record-only** (carry added). Still owed under `defect-root-cause.md`: 9 instances is past the threshold. |
| R10-RCA-ORCH-CONTINUITY (rca, in progress) | FLOW-ANDON is a ready countermeasure | **Rescope**: run the cost test against FLOW-ANDON (carry added); the record is still owed |
| R10-FLOW-RECORD-PITCH (new) | made unneeded by the merge queue if you adopt it | **Conditional**: close unbuilt after FLOW-MQ-PROBE if the queue is adopted |
| Train CI wait, batch proof, `train-hold` (#2519) | superseded by a native merge queue, if adopted | retire after adoption, not before |
| Any group that splits live L/XL groups | — | **Not added** (see §1) |

Spotted in passing, not caused by the flow groups (verify before acting):
- **R10-PREPR-CAP (in progress)** may already be delivered by the fly-in #2526, R10-GATE-PRIORITY ("a slot is held for the life of its run"). Check before dispatching more work on it.
- **R10-ORCH-MACHINERY part (3)**, the plan page as a tree instrument, overlaps R10-PLAN-ARTIFACT (#2558, open). Both port the plan page.
- **R10-TICK-OWED-LEVEL** is a stopgap the ORCH-MACHINERY obligations ledger replaces. Keep it: it is in progress and fixes a live 4.5 MB board.
- **Architect notes say "position N of 25" while their brief copies say "of 24"**, and they cite orchestrator.md §5 for a chain rule §5 does not contain. FLOW-PULL adds the rule there.

**No existing group becomes fully redundant.** Two RCA seats shrink to records, and one new group is conditional.

---

## 6. Projection (model in `tools/simulate.py`; assumptions in SHADOW-PLAN §5)

Hours from adoption to the last roster merge, with fly-ins arriving every 4 h. **Today** is the live roster's 57 open groups. The other rows add the 10 flow groups (67 in all): the improvements pay for their own build inside the window.

| scenario | levers | hours |
|---|---|---|
| Today | lead times as measured; `HPO_WIP_CAP` 6; chain by file | **≈ 207** |
| Re-chain plus lanes only | FLOW-RECHAIN (a roster PR) and caps A4 B4 C3 F2 (a ruling); lead times unchanged | **≈ 133** |
| Lead time only | target lead times (pull, frozen heads, error-proofing, pitch, andon); chain by file | ≈ 106 |
| **Full future state** | both; drain-first phasing (SHADOW-PLAN §3) | **≈ 78** |
| Full, but lane A kept at 2 | re-chain without the cap ruling | ≈ 95 |
| Full, slower ramp | as above, with lead times reaching target over 96 h, not 48 h | ≈ 97 |
| Stacking added | (dropped) | no change |

Round 10 cannot come in at 100 h: 168 h are already spent. **It can end in about 3–4 days instead of about 9.**

Round 11 is where the 100-h takt is met: P1–P3 in ≤ 24 h, as round 10 nearly achieved, then P4 of a seam-chained, scope-frozen roster at about 77 h for a round-10-sized scope. The rounds would have a fixed cadence and a buffer.

---

## 7. The groups (shadow roster; pre-studies in STUDY.md)

| group | what | why (round time) | after | owner gate |
|---|---|---|---|---|
| **R10-FLOW-RECHAIN** | drop `after` edges between disjoint-seam coordinator.py groups (edge-by-edge proposal in STUDY K7) | chain depth 11 → 5; the biggest single lever | R10-ROSTER-OPS (`set-after`) | ruling R6 |
| **R10-FLOW-PULL** | nudge.md: pull, lanes, classes of service, pitch, frozen heads, verdict after CI, carry predicate before any re-review. orchestrator.md §5: the seam chain rule and the scope freeze | lead time and scope | — | policy (tvofi, mandate) |
| **R10-FLOW-WIP** | pr_cap.py: lane caps; counts fly-ins and orphaned handoffs; `next` prints the ranked dispatch list | WIP, critical chain first | FLOW-PULL | mandate |
| **R10-FLOW-AUTOTRAIN** | the pitch as a loop: build the queue from verdict refs and the carry predicate, run `merge_train.py batch --bot-prs` every hour | removes a manual queue build and the waiting between turns | FLOW-PULL, R10-TICK-RELAY-DECOUPLE | mandate |
| **R10-FLOW-POSTMERGE** | `merge_pr.sh` and the train run the step-12 bookkeeping themselves (gc, #201 comment with read-back, set-stage via roster-sync, state docs) | mechanical; was an LLM step every merge | R10-ROSTER-OPS | mandate |
| **R10-FLOW-JIDOKA** | prepr runs `carry_audit.py check` | 19% of blocks, caught before review | R10-PREPR-CAP | ruling R7 (0012) |
| **R10-FLOW-ANDON** | heartbeat ref on every tick, plus an off-host watcher | availability 71% → ≥ 90% | R10-TICK-RELAY-DECOUPLE | mandate |
| **R10-FLOW-BOARD** | a flow board in `merge_throughput.py` (no gh calls) with the round fever chart | measures every change | R10-PLAN-ARTIFACT | mandate (workflow wiring) |
| **R10-FLOW-MQ-PROBE** | GitHub merge-queue probe on a throwaway ruleset | could retire absorbs and re-reviews for good | R10-CI-LAYOUT-P1 | owner decides |
| **R10-FLOW-RECORD-PITCH** | pitch bound on record automerge, **conditional** | records ≈ 51% of main moves | CI-LAYOUT-P1, FLOW-PULL, FLOW-MQ-PROBE | mandate (workflow) |

**Folded carries** (no new group):
- **R10-POLICY-FIXER-MD:** K5 (absorb only on conflict or DIRTY). fix-review step 11 stands on the post-workflow pr-contract run.
- **R10-ORCH-MACHINERY:** its beat advances the heartbeat ref.
- **R10-CI-LAYOUT-P1:** the record step's train-hold arm is kept.
- **R10-CI-LAYOUT-P2:** if the queue is adopted, the umbrella reports on `merge_group`.
- **R10-RCA-HEADMOVED, R10-RCA-ORCH-CONTINUITY:** rescoped as in §5.

---

## 8. Owner rulings needed (one #201 comment, read back)

| ruling | question | recommended |
|---|---|---|
| R1 | Demand: one round in ≤ 100 h; hourly merge pitch | yes |
| R2 | Lane caps A4 B4 C3 F2 (CONWIP 13), replacing `HPO_WIP_CAP` 6 and the coordinator cap of 2 | yes, after FLOW-RECHAIN merges; until then A stays at 2 |
| R3 | Record PRs merge inside the pitch (`--bot-prs`) | yes |
| R4 | Absorb `main` only when DIRTY or on a merge-tree conflict | yes, either condition |
| R5 | Classes of service and fly-in definition (§4.4); scope freezes at the register | yes |
| R6 | Chains by owning-seam overlap (FLOW-RECHAIN, orchestrator.md §5) | yes |
| R7 | Decision 0012: running an existing checker earlier in prepr is not a new lint class | yes |
| R8 | Authority for the merge-queue probe ruleset (throwaway branch only) | yes |
| R9 | fix-review step 11 stands on a green pr-contract run that started after the head's last workflow concluded; the step-1 mutation proof stays the reviewer's (HANDOVER: CI cannot produce it) | yes: HANDOVER's "never re-gate an unchanged head" |

Mandate 6175172275 covers the code-owned and policy PRs until **2026-10-28T18:14Z**. FLOW-PULL and the POLICY-FIXER-MD carry must merge before then, or need a fresh grant.

---

## 9. Quality guardrails (must not move)

- the red rate of push runs on `main`
- post-merge reverts
- issues reopened
- mutation kills on added lines
- blocked verdicts per PR in the **real-catch** classes (`harness`/`class-open`, `vacuous`)

A fall in the real-catch rate after FLOW-PULL or the K5 carry means review got weaker, not the work better: stop and re-examine. Every group carries the finder's harness at both ends and a null control (STUDY §0).

---

## 10. Risks

- **A wrong edge drop in RECHAIN.** It is caught by the batch proof (the train stops at that entry) or by the fix review. It costs one rework, never a silent merge.
- **Seat concurrency:** lanes summing to 13 assume about 8 Opus fixers, 3 Sonnet fixers and 2–3 reviewers running at once. With fewer seats, the effective cap is the seat count. The flow board shows it.
- **The projection is a model.** Lead-time targets (S 3 h, M 5 h, L 8 h, XL 12 h dispatch → verdicted) are design targets; the 48-h ramp is an assumption, and the 96-h ramp (97 h) is the pessimistic case.
- **The mandate expiry** (10-28) and **moratorium end** (10-31) bound which changes can land without fresh grants.
