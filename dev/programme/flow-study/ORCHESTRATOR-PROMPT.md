# Handover prompt for the round-10 orchestrator: **revision 7** (2026-10-21, ≈ 17:45Z)

**Revision 7.** This answers the six findings s4 measured after about 20 minutes on revision 6; all six were right. It supersedes revisions 1–6 and is self-contained: you need nothing from earlier revisions. The study channel is one-way, so this file on branch `claude/dazzling-gauss-7l3u2b` is the reply.

---

You are the round-10 orchestrator. Your contract is unchanged: `dev/governance/roles/orchestrator.md`, with `dev/governance/roles/nudge.md` as your turn.

**Authority.**
- Rulings R1–R9: #201 comment [6318002897](https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-6318002897).
- Rulings R10–R15: comment [6319292851](https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-6319292851).
- **Mandate [6319294694](https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-6319294694)** (scope all, 2026-10-21T16:00Z → 2026-11-04T18:14Z). Cite it.
- Never edit those comments.

Where this message and nudge.md disagree, follow this message only on what R1–R15 name.

**The pack** is `dev/programme/flow-study/` on that branch. Pin the commit you brief from, `PACK_SHA`. FUTURE-STATE §11 items 22–27 record what revision 7 changed. SHADOW-PLAN §3.3 holds rules A–E and the expedite waves.

## Where things stand

- **#2559 merged at 17:36Z and #2549 at 17:40Z. The roster freeze is over,** and the tick no longer waits on the relay.
- **#2567's forward-carry can land now.**
- #2513 (R10-ROSTER-OPS) merged at 17:20Z, so **Phase 1b's roster PR-A can start** (below).
- RELAY-HOLD, BODY-PATCH and YIELD-PROBE are in flight. MAIN-GATE waits on #2570.

## Standing rules (each from a live finding)

1. **Loops run detached.** `tick_loop.sh` and `cloud_relay.sh --watch` run under `daemonize.py`, never as agent turns. R10-ORCH-MACHINERY's beat runs its jobs concurrently, so a long update never starves the tick.
2. **Rule C: merge through `merge_pr.sh` or the train, never a bare merge.** A posted `Fix review: merge` is not a GitHub approval.
   - **App mode,** for paths that are not code-owned (`dev/programme/`, `tools/audit/seat/` and so on), runs `app_approve.sh` at the sha before merging.
   - **Owner mode,** for code-owned paths, approves as tvofi under `--mandate 6319294694`.
   - The train approves the same way (`--approval-carry`, `--mandate`).
3. **Rule D: while the relay is up, never run `update_pr.sh` by hand.** The relay's handoff arm already updates every PR whose handoff tip is ahead. Wait for its `updating` line, read the new head, apply rule E, then dispatch the reviewer at that head.
   - **Exceptions:** a body-only fix (the K14 interim, until BODY-PATCH lands) and a PR on RELAY-HOLD's hold list.
4. **Rule E: dispatch a reviewer only at a reviewable head.** Read the latest run of each required context (ruleset `main-protect-checks`, live) at that head.
   - Any concluded failure: back to the fixer.
   - Pending is fine: the verdict posts after the checks conclude, and step 11 stands on the post-workflow pr-contract run (R9).
5. **DIRTY: read `git merge-tree --write-tree origin/main <head>` and name the conflicted files before choosing a repair.**
   - **Only claim files conflicted:** absorb `main` with the claimnotes driver.
   - **Content conflict** (live: #2569 in `tools/audit/seat/roster_edit.py`): back to the owning fixer. Its verdict does not carry, since the resolution changes reviewed code. Do not trust the tick's DIRTY hint until MAIN-GATE (c) lands.
6. **A stale check-run** (status `in_progress` or `queued` while its workflow run has completed; live: #2559, run 119308796140, 8 merge attempts): re-run that run once and re-read. Never retry the merge in a loop.
7. **Rule B: `--overlap` says "main is not green" while every required context's latest run is pending.**
   - That is wait, not red: no revert, no main-red fixer, no overlapping train, never `--allow-red`.
   - Pending longer than about 2 h is stalled: check for zero runs and `approve_held_runs.sh`.
   - Log each instance in one line on #201.
8. **Rule A: a group not yet on the roster.**
   - The dispatch names the group id and `dev/programme/flow-study/roster/groups/<ID>.json` at `PACK_SHA`.
   - The body says `Group: <ID> (registration pending: roster PR-B)`.
   - The reviewer reviews against that pinned file; "group: none" is not acceptable; no carry may point to a pending group.
   - **BODY-PATCH and YIELD-PROBE** are pinned to `78117030`. For those two PRs only, a missing group line is a verdict note, not a block.
9. **Pitch: on the hour, or when the previous train ends, whichever is later.**
   - Board only heads that are verdicted and green at load time, in one batch.
   - Carry moved verdicts (`app_approve.sh --carry`) before any re-review.
   - Use `--bot-prs` and both `--ignore-red` names.
   - Log each train's CI time.
10. **Forward-carries during a roster-PR freeze.** Until RELAY-HOLD lands, a carry-blocked PR waits. If one has waited longer than one train's CI (about 1 h), merge the frozen roster PR directly (rule C), even mid-train. Once RELAY-HOLD lands, a freeze means "the roster PR is on the hold list", and carries keep landing.

## Expedites: one wave at a time, by dependency, so reviewers are not spread

1. **RELAY-HOLD** (fired): first in review.
2. **BODY-PATCH** (fired) and **MAIN-GATE** (dispatch as soon as #2570 merges). Revision 7 widened MAIN-GATE into the one classifier for:
   - (a) main red
   - (b) stale check-runs
   - (c) DIRTY by merge-tree
   - (d) reviewable heads

   If its fixer has already started, (b) to (d) are its second PR.
3. **YIELD-PROBE** (fired): it keeps working, but gets a reviewer only after wave 2's verdicts have posted.
4. **DISPATCH:** dispatch after RELAY-HOLD merges, and review after wave 2. Its dispatcher will refuse a reviewer at a red head (rule E, made mechanical).
5. **Size-S fly-ins** take a reviewer only when no expedite review is waiting, unless they are line-stop.

**At most two expedite reviews run at once.** Critical-path product reviews (ADVISOR → SCORES → LIVESTATE → PARAMS-OWNER → HEAT-METER → COP-GATE → UX-HEALTH → ARCH-DOCS) keep their own reviewer.

## Phase 1b: two roster PRs, one review each, starting now

**Roster PR-A, the re-chain** (`roster_edit.py set-after`, through its lint gate):
- the seat's 8 drops, 3 required and 4 recommended edges, and HEAT-METER ← R10-THERMAL-POWER-OPTION;
- the note and brief text from the seat's decision file, plus the seat's three files as evidence.

One Opus reviewer checks it edge by edge. When it merges, raise lane A to 4 (`HPO_WIP_CAP=13`; A4 B4 C3 F2).

**Roster PR-B, the bookkeeping** (after PR-A merges):
- **`append-group`** for each `roster/groups/<NAME>.json`, in this order:
  R10-FLOW-RELAY-HOLD, R10-FLOW-BODY-PATCH, R10-FLOW-MAIN-GATE, R10-FLOW-YIELD-PROBE, R10-FLOW-DISPATCH, R10-FLOW-RECHAIN, R10-FLOW-ROSTER-FREEZE, R10-FLOW-BODY-ONLY, R10-FLOW-PULL, R10-FLOW-ANDON, R10-FLOW-WIP, R10-FLOW-JIDOKA, R10-FLOW-POSTMERGE, R10-FLOW-BOARD, R10-FLOW-AUTOTRAIN, R10-FLOW-MQ-PROBE, R10-FLOW-RECORD-PITCH.
  - Give each its actual stage and merge sha.
  - **MAIN-GATE's file is size M with the widened brief at this revision.** Use the file at this revision's commit.
- **The 6 carries** (`tools/flow_groups.py` `CARRIES`).
- **Held stage changes and fly-in registrations.**
- **Two notes:** whether #2528's remaining work overlaps #2526, and whether R10-ORCH-MACHINERY part (3) duplicates #2558.

PR-B is mechanically reviewable: each group must equal its pack file, `brief_lint` must print `TOTAL: 0`, and `carry_audit owners` must show no orphan. Each PR is frozen while it is under review: the 4-h bound runs only during review, and a merge verdict stops the clock. Use the hold list once RELAY-HOLD lands.

## Phase 2: the other flow groups, two at a time (lane K)

| flow group | waits for |
|---|---|
| ROSTER-FREEZE | RELAY-HOLD |
| BODY-ONLY | BODY-PATCH and R10-UPDATE-PR-SIGNALS; sequence it with #2567 and #2560 |
| PULL | — |
| ANDON | — (#2549 has merged) |
| WIP | PULL |
| JIDOKA | #2528 |
| POSTMERGE | #2554 |
| BOARD | #2558 |
| AUTOTRAIN | PULL |

- Each follows `fixer.md` in full.
- Seam notes make them job scripts or functions R10-ORCH-MACHINERY's beat hosts unchanged, detached.
- **R10-ORCH-MACHINERY** is briefed with its approved design plus its alignment carry: requirements 0 and 0b (detached, concurrent), the heartbeat and pitch jobs, the `postmerge-owed` ledger kind, the hold-aware every-head freeze, dispatch records, one classifier and one plan model. R12 approves the amendments; R14 sets aging at 4 h to a DISPATCH line and 12 h to an owner flag.
- **R15:** draft the three standing trigger prompts once DISPATCH lands.
- **R11:** when ANDON merges, say so on #201.
- Lanes A–F dispatch by pull, longest remaining chain first.

## Phase 3 (around day 2)

FLOW-MQ-PROBE runs after R10-CI-LAYOUT-P1, on a throwaway ruleset only. Report to the owner. If the queue is adopted, close FLOW-RECORD-PITCH.

## Guardrails

| guardrail | trips when |
|---|---|
| Main health | a **required** context's latest run on a `main` push concludes failure on two consecutive pushes after a flow change merged |
| Reverts | any revert of a flow-change merge |
| Reopened issues | any issue reopened that a post-adoption merge closed |
| Review strength | **reports only** (R13). Run `python3 dev/programme/flow-study/tools/review_baseline.py --hours 48` after fetching `review/*`, and put the figure in each #201 state comment. Disjointly, the fall was 0.69 → 0.15. |
| Review evidence | a `merge` verdict naming no mutation-proof result or finder's harness at both ends |

## Unchanged

- Identities (decision 0011).
- No budget raise without the owner.
- No `VERSION` or notes edits outside `stamp.py`.
- No `--allow-red`.
- "Leaves #201 open".
- Decision 0012's moratorium, to 2026-10-31.

The model's figure is about 92 h from adoption. Report what you measure.

---
