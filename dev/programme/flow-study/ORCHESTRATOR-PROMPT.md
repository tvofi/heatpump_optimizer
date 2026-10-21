# Final handover prompt for the round-10 orchestrator

Send everything between the two lines as it is. It is self-contained: the study pack is on a remote branch the orchestrator fetches itself, and the rulings are already posted on #201.

---

You are the round-10 orchestrator. Your contract is unchanged: `dev/governance/roles/orchestrator.md`, and `dev/governance/roles/nudge.md` as your turn. This message adds a flow plan the owner has adopted. It changes **what you dispatch, when, and how merges are paced**. It changes no gate, no identity rule and no approval rule.

**Authority.** The owner's rulings R1–R9 are #201 comment [6318002897](https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-6318002897) (2026-10-21), under mandate 6175172275, in force to 2026-10-28T18:14Z. Cite that comment wherever nudge.md asks for the session mandate.
- Where this message and nudge.md disagree, follow this message only on the points R1–R9 name. Everything else binds as written.
- When R10-FLOW-PULL merges, nudge.md carries these rules itself and this message retires.

**The pack.** The study lives on branch `claude/dazzling-gauss-7l3u2b`, under `dev/programme/flow-study/`. It is not on `main` and is not a pull request: read it, do not merge it.

```
git fetch origin claude/dazzling-gauss-7l3u2b
git worktree add --detach ~/hpo-orch/flow-study origin/claude/dazzling-gauss-7l3u2b
PACK=~/hpo-orch/flow-study/dev/programme/flow-study
```

Read `$PACK/FUTURE-STATE.md` §1, §4 and §8, then `$PACK/SHADOW-PLAN.md` §1–§3. `$PACK/STUDY.md` is for the seats you dispatch: brief each flow-group fixer with its own section.

## The demand

The demand is a whole round in about 100 h. Round 10's fix wave is long because of two things:
- **the critical chain**: 11 levels, mostly the coordinator.py serial chain;
- **waiting**: absorbs, re-reviews, record churn, and review before CI.

It is not long because of the group count. So:
- do not split groups;
- finish before you start;
- put the critical chain first;
- remove waiting.

## Phase 0: drain, stop starting (now until about 12 h from now)

1. **Measure first.** Re-derive at your own refs, from `origin/main`, `origin/handoff/audit-r10-roster`, the `verdict/*` and `review/*` bus refs, and the open PR list: the open PRs, their newest verdict, and whether that verdict is at the head.
   - At 14:05Z the study saw: merge at head #2560 #2547 #2531; merge on an ancestor #2513 #2544 #2548; blocked #2563 #2561 #2529 #2549 #2567 #2527 #2559; unreviewed #2570 #2569 #2566 #2558 #2557 #2554 #2545 #2528 #2524 #2521.
   - Your measurement wins. Never carry these numbers into a record.
2. **Start nothing new** except an expedite (red main, quota, outage, security, owner-flagged), a size-S fly-in (below), and the R10-FLOW-RECHAIN decision seat once #2513 has merged. `pr_cap.py dispatch-gate` refuses anyway while 20 groups are in progress. Do not override it except for those.
3. **The pitch (R1, R3).** At the first turn after each full hour, load one train of every verdicted PR:
   - first run `tools/pr/app_approve.sh --carry <verdict-sha> <head>` on any moved head (`CARRY: yes` approves with the carry; only `no` gets a reviewer);
   - pass `--bot-prs` so the open record PR lands inside the pitch;
   - pass both `--ignore-red nightly-status` and `--ignore-red delivery-status`.

   Between pitches, merge directly only an expedite, a budget-file or policy PR that nudge.md keeps off the train, or a lone verdicted PR when nothing else waits.
4. **Blocked heads** go back to their own fixer in the same turn. Four are carry-missing: the fix is a `Carry:` marker routing each finding.
5. **Reviewers go to the unreviewed heads, oldest first,** about 2–3 at a time; review is the constraint today. A reviewer starts at handoff but posts its verdict only after the required checks at that head have concluded. fix-review step 11 stands on a green pr-contract run that started after the head's last workflow concluded (R9). The reviewer still runs the step-1 mutation proof.
6. **Frozen heads (R4).** Absorb `origin/main` into an open head only when it is DIRTY or `git merge-tree --write-tree origin/main <head>` reports a conflict.
7. **Fly-ins (R5).** Size S only. Register each one before dispatch with `tools/audit/seat/roster_edit.py append-group`, name `R10-FLY-<topic>`, the existing kind, `after: []`. Lane F holds 2. Anything larger goes to the next round's register.

## Phase 1: one roster burst (as soon as #2513 has merged)

Every `roster_edit.py --push` moves roster PR #2559's head, and #2559 was just blocked head-moved. So do all of this **back to back, in one sitting**, through the tool's lint gate (never a JSON splice). Then dispatch **one** reviewer for #2559.

1. **The R10-FLOW-RECHAIN seat** (Opus) decides each coordinator.py `after` edge from the two owning seams. `$PACK/STUDY.md` K7 proposes dropping 10 edges and keeping 7. Apply only the drops it confirms, with `set-after`, and amend the two architect notes per drop.
2. **The ten groups,** in this order, so every `after` exists:
   ```
   roster_edit.py append-group $PACK/roster/groups/<NAME>.json
   ```
   R10-FLOW-RECHAIN, R10-FLOW-PULL, R10-FLOW-ANDON, R10-FLOW-WIP, R10-FLOW-POSTMERGE, R10-FLOW-JIDOKA, R10-FLOW-BOARD, R10-FLOW-AUTOTRAIN, R10-FLOW-MQ-PROBE, R10-FLOW-RECORD-PITCH.
   - Set RECHAIN's stage to match the seat's actual state.
   - If `--push` refuses on brief_lint, the roster has moved since 617ce1316: fix that line, never weaken the linter.
3. **Six `append-carry`,** with the texts in the `CARRIES` list of `$PACK/tools/flow_groups.py`, on:
   - R10-RCA-HEADMOVED (rescoped to record-only)
   - R10-RCA-ORCH-CONTINUITY (cost test against FLOW-ANDON)
   - R10-CI-LAYOUT-P2
   - R10-CI-LAYOUT-P1
   - R10-POLICY-FIXER-MD
   - R10-ORCH-MACHINERY
4. **Two `set-resume --field note` checks,** recorded on the groups. Do not file issues (CLAUDE.md: fix, verify, then file):
   - whether R10-PREPR-CAP's remaining work (#2528) overlaps the merged #2526;
   - whether R10-ORCH-MACHINERY part (3) duplicates R10-PLAN-ARTIFACT (#2558).
5. **Raise lane A to 4 in the same hour** (R2): `HPO_WIP_CAP=13` with lanes A4 B4 C3 F2. Until then lane A stays at 2.
6. **One #201 comment** through `tools/pr/gh_comment.py`, with a byte-identical read-back: the roster sha after the burst, and "flow plan phase 1 done".

## Phase 2: improvements through lane K, two at a time (from about 12 h)

Dispatch the flow groups in the order above, at most **two at once** (lane K, on top of A–F), each only once its `after` group has merged:

| flow group | waits for |
|---|---|
| ANDON | #2549 |
| JIDOKA | #2528 |
| POSTMERGE | #2554 |
| BOARD | #2558 |
| WIP and AUTOTRAIN | PULL |

Brief each with `$PACK/STUDY.md`'s section and the roster brief. They follow `fixer.md` in full: failing test first, mutation proof, STUDY §0's enumerators as the finder's harness at both ends, a null control, the scoped gate and the structure ratchet. FLOW-PULL and the R10-POLICY-FIXER-MD carry change policy: tvofi's review under the mandate, **before 2026-10-28T18:14Z**, or a fresh grant.

Lanes A–F dispatch normally by pull as the drain frees them: the longest remaining chain first, then the smallest size. Lane C takes no new process group until it holds fewer than 3.

## Phase 3: decide (around day 2)

- FLOW-MQ-PROBE runs after R10-CI-LAYOUT-P1, on a throwaway branch and ruleset only (R8). It never touches `main-protect-checks`. Put its report to the owner.
- If the owner adopts the merge queue, close FLOW-RECORD-PITCH as not needed. Otherwise build it.

## Unchanged

- Identities (decision 0011).
- No budget raise without the owner.
- No `VERSION` or notes edits outside `stamp.py`.
- No `--allow-red`.
- "Leaves #201 open".
- Decision 0012's moratorium on new policy files and rules, to 2026-10-31.

## Stop and tell the owner on #201

Stop if, after a flow change merges, you see any of these:
- a red push run on `main`;
- a revert;
- a reopened issue;
- a fall in real-catch blocked verdicts per PR (`harness`, `class-open`, `vacuous`).

The plan removes waiting, not review.

## Done looks like

- Every roster group merged or deferred by the owner, then the stamp.
- Merges arriving on the hour.
- The coordinator lane four wide on disjoint seams.
- Measured lead times falling toward S 3 h, M 5 h, L 8 h.

The study's model puts the last merge about 78 h after adoption, against about 207 h on today's process. That is a model: report what you measure.

---
