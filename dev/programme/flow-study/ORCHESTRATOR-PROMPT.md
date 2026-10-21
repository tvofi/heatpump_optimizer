# Final handover prompt for the round-10 orchestrator (revision 3, after your second round of evidence, 2026-10-21)

Send everything between the two lines as it is.

---

You are the round-10 orchestrator. Your contract is unchanged: `dev/governance/roles/orchestrator.md`, with `dev/governance/roles/nudge.md` as your turn. This replaces revisions 1 and 2. It takes in everything you reported:
- the seat's re-chain;
- `update_pr.sh` always merging `main`;
- #2559 as a moving head;
- `BAD-DEST`;
- the missing body-PATCH tool;
- the `--overlap` gate misreading pending checks;
- the unusable guardrail;
- the unpriced freeze;
- the per-seat dispatch cost.

**Authority.** Rulings R1–R9 are #201 comment [6318002897](https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-6318002897), under mandate 6175172275, in force to 2026-10-28T18:14Z. Where this message and nudge.md disagree, follow this message only on what R1–R9 name.

**The pack** is on branch `claude/dazzling-gauss-7l3u2b`, `dev/programme/flow-study/` (a reading copy, not a PR).

```
git fetch origin claude/dazzling-gauss-7l3u2b
git -C ~/hpo-orch/flow-study checkout --detach origin/claude/dazzling-gauss-7l3u2b 2>/dev/null || git worktree add --detach ~/hpo-orch/flow-study origin/claude/dazzling-gauss-7l3u2b
PACK=~/hpo-orch/flow-study/dev/programme/flow-study
```

Read `$PACK/FUTURE-STATE.md` §9 and §11, then `$PACK/SHADOW-PLAN.md` §2 and §3.2. Brief each flow seat with its own `$PACK/STUDY.md` section.

## Phase 0: drain, stop starting (now until about 12 h)

1. **Measure at your refs.** Never carry a number from this message into a record.
2. **Start nothing new except:**
   - expedites;
   - size-S fly-ins (registered in Phase 1b; noted on #201 until then);
   - **two flow expedites that repair the line:**
     - **R10-FLOW-BODY-PATCH:** STUDY K14; no `after`.
     - **R10-FLOW-MAIN-GATE:** STUDY K15; after #2570, sharing its classifier.
3. **Reading `main`, until MAIN-GATE lands:** judge only the **latest run of each required context** (ruleset `main-protect-checks`, read live).
   - Pending is wait.
   - `record`, `record-autofix`, `nightly-status`, `delivery-status`, and every non-required context (`ci-ratchet` today), never trigger a revert.
   - A "main is not green" line from the `--overlap` gate is not evidence until you have done that reading.
4. **Pitch: on the hour, or when the previous train ends, whichever is later.**
   - A train boards only heads that are **verdicted and green at load time**, proved together in one batch. It never waits for a slow head; that head boards the next pitch.
   - Carry moved verdicts (`app_approve.sh --carry`) before any re-review.
   - Use `--bot-prs` and both `--ignore-red` names.
   - Log each train's CI time. About 57 min is the current measurement, and that is expected for one proof per pitch.
   - #2531 (R10-CI-RATCHET-RED, verdicted at its head) appears to be the `ci-ratchet` fix: board it.
5. **Body fixes without moving a head, until BODY-PATCH lands:**
   1. Check out a clean worktree at the PR's **exact** head.
   2. Write the corrected body.
   3. Run `tools/pr/app_push.sh` with `--dry-run`, then live.
   4. Confirm the head sha is unchanged and the read-back is identical. If the head moves, stop and report it: the procedure is read from the code, not yet run.

   Do this first on #2560's 111→113 figure. Run `update_pr.sh` only when the handoff code tip moved, or the PR is DIRTY or conflicted. Carrying a verdict does not repair a refused body.
6. **Blocked heads** go back to their fixer in the same turn.
7. **Reviewers** take unreviewed heads oldest first, critical-path groups first. A verdict posts once required checks have concluded. Step 11 stands on the post-workflow pr-contract run (R9); the mutation proof stays the reviewer's.

## Phase 1a: #2559 first, under a bounded freeze

- **The freeze runs from #2559's review dispatch until it merges.** No `roster_edit.py --push` in that window. Before the review starts, pushes are still allowed.
- **#2559 boards the next train as its first car.** Do not merge it alongside a running train: the batch would re-prove, costing about one CI run.
- **The expected cost** is about 3 h of lag on set-stage, fly-in registrations and carries. That is harmless during the drain.
- **Bound:** if the freeze passes 4 h, lift it, push the held edits, and request one fresh review.
- Merging #2559 also clears `BAD-DEST` on #2529, #2547 and #2561.

## Phase 1b: one burst, one new roster PR (once #2559 and #2513 have merged)

Through `roster_edit.py`'s lint gate, in one sitting:

1. **Your seat's ruling,** with `set-after`, plus the note and brief text from its decision file:
   - the 8 drops
   - the 3 required edges
   - the 4 recommended edges
   - HEAT-METER ← R10-THERMAL-POWER-OPTION

   Never apply the drops without the required edges. Land the seat's three files in the tree with this burst.
2. **`append-group $PACK/roster/groups/<NAME>.json`,** in this order:
   R10-FLOW-BODY-PATCH, R10-FLOW-MAIN-GATE, R10-FLOW-RECHAIN, R10-FLOW-ROSTER-FREEZE, R10-FLOW-BODY-ONLY, R10-FLOW-PULL, R10-FLOW-ANDON, R10-FLOW-WIP, R10-FLOW-JIDOKA, R10-FLOW-POSTMERGE, R10-FLOW-BOARD, R10-FLOW-AUTOTRAIN, R10-FLOW-DISPATCH, R10-FLOW-MQ-PROBE, R10-FLOW-RECORD-PITCH.
   - Set each group's actual stage: the two expedites and RECHAIN may already be done or in flight.
   - A brief_lint refusal means the roster moved: fix that line, never the linter.
3. **The 6 carries,** with the texts in `$PACK/tools/flow_groups.py` `CARRIES`.
4. **Everything held during Phase 1a,** plus two notes:
   - whether #2528's remaining work overlaps #2526;
   - whether R10-ORCH-MACHINERY part (3) duplicates #2558.
5. **Open one new roster PR and dispatch one reviewer.** The freeze applies again for that review.
6. **Raise lane A to 4** (`HPO_WIP_CAP=13`; lanes A4 B4 C3 F2).
7. **One #201 comment** through `gh_comment.py`, with a byte-identical read-back.

## Phase 2: flow groups through lane K, two at a time (from about 12 h)

In order, each only once its `after` group has merged:

| flow group | waits for |
|---|---|
| ROSTER-FREEZE | — |
| BODY-ONLY | BODY-PATCH and R10-UPDATE-PR-SIGNALS; sequence it with #2567 and #2560 |
| PULL | — |
| ANDON | #2549 |
| WIP | PULL |
| JIDOKA | #2528 |
| POSTMERGE | #2554 |
| BOARD | #2558 |
| AUTOTRAIN | PULL and #2549 |
| DISPATCH | BODY-ONLY |

Each follows `fixer.md` in full. ANDON, AUTOTRAIN, POSTMERGE, BODY-ONLY, ROSTER-FREEZE, DISPATCH, WIP, MAIN-GATE and BOARD each carry a seam note: they are built as job scripts or functions that R10-ORCH-MACHINERY's beat and ledger will host unchanged (STUDY K17). When you dispatch R10-ORCH-MACHINERY, brief it its new alignment carry together with its approved design.
- **Code-owned** (FLOW-PULL, the POLICY-FIXER-MD carry, `carry_audit.py`, workflows): tvofi's review under the mandate **before 2026-10-28T18:14Z**, or a fresh grant.
- **FLOW-DISPATCH builds only the repo half.** Standing per-role triggers are the owner's harness action: ask the owner, do not build around it.
- Lanes A–F dispatch by pull, longest remaining chain first. The critical path is ADVISOR → SCORES → LIVESTATE → PARAMS-OWNER → HEAT-METER → COP-GATE → UX-HEALTH → ARCH-DOCS.

## Phase 3: decide (around day 2)

FLOW-MQ-PROBE runs after R10-CI-LAYOUT-P1, on a throwaway branch and ruleset only. Report to the owner. If the queue is adopted, close FLOW-RECORD-PITCH unbuilt.

## Guardrails: record the baselines at adoption, then stop and tell the owner on #201 if one trips

| guardrail | trips when |
|---|---|
| Main health | a **required** context's latest run on a `main` push concludes failure on two consecutive pushes after a flow change merged. Pending and non-required contexts never trip it. |
| Reverts | any revert of a flow-change merge |
| Reopened issues | any issue reopened that a post-adoption merge closed |
| Review strength | with at least 20 PRs reviewed in a rolling 48 h, real-catch blocks fall below **0.07/PR**. The baseline is 0.15/PR over 47 PRs in the 48 h before 14:50Z 10-21; it was 0.52 over the round's first six days. The fall predates the plan: watch it, do not attribute it. Classes and enumerator: STUDY "Guardrail baselines". |
| Review evidence | a `merge` verdict that names no mutation-proof result or finder's harness at both ends |

## Unchanged

- Identities (decision 0011).
- No budget raise without the owner.
- No `VERSION` or notes edits outside `stamp.py`.
- No `--allow-red`.
- "Leaves #201 open".
- Decision 0012's moratorium, to 2026-10-31.

## Done looks like

- Every roster group merged or deferred, then the stamp.
- One proof per pitch.
- No head moved by a body fix or a roster edit.
- Lane A four wide.

The model's figure is about 92 h after adoption, against about 207 h for the live roster on today's process. Report what you measure.

---
