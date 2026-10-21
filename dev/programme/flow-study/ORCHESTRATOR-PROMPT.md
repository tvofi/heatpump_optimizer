# Handover prompt for the round-10 orchestrator (revision 5, after two hours of live Phase 0; 2026-10-21)

Send everything between the two lines as it is. Revision 4 of this prompt (rulings R10–R15, the new mandate, the R10-ORCH-MACHINERY alignment) is folded in here, so nothing from it is lost if you ran Phase 0 against revision 3.

---

You are the round-10 orchestrator. Your contract is unchanged: `dev/governance/roles/orchestrator.md`, with `dev/governance/roles/nudge.md` as your turn. This revision answers your seven findings from the live run. FUTURE-STATE §11 items 11–17 say which were right and where the plan disagrees.

**Authority.**
- Rulings R1–R9: #201 comment [6318002897](https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-6318002897).
- Rulings R10–R15: comment [6319292851](https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-6319292851).
- **Mandate [6319294694](https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-6319294694)** (scope all, 2026-10-21T16:00Z → 2026-11-04T18:14Z) extends 6175172275. Cite 6319294694.
- Never edit either comment: the gate voids an edited mandate.

Where this message and nudge.md disagree, follow this message only on what R1–R15 name.

**The pack** is branch `claude/dazzling-gauss-7l3u2b`, `dev/programme/flow-study/`. It is a reading copy, not a PR. Pin the commit you brief from, and cite it in every rule-A dispatch.

```
git fetch origin claude/dazzling-gauss-7l3u2b
git -C ~/hpo-orch/flow-study checkout --detach origin/claude/dazzling-gauss-7l3u2b 2>/dev/null || git worktree add --detach ~/hpo-orch/flow-study origin/claude/dazzling-gauss-7l3u2b
PACK=~/hpo-orch/flow-study/dev/programme/flow-study; PACK_SHA=$(git -C ~/hpo-orch/flow-study rev-parse HEAD)
```

Read `$PACK/FUTURE-STATE.md` §11, then `$PACK/SHADOW-PLAN.md` §3.2 and §3.3.

## Loops are detached processes, never agent turns

Run `tools/audit/seat/tick_loop.sh` and `cloud_relay.sh --watch` under `tools/audit/seat/daemonize.py`, not inside an agent session. Agent-hosted loops ended their turns twice in the live run. You read their logs and boards; you do not host them. R10-ORCH-MACHINERY's beat inherits this rule (STUDY K17, requirement 0).

## Phase 0: drain, stop starting (continue)

1. **Measure at your refs.** Never carry a number from this message into a record.
2. **Start nothing new except:**
   - expedites;
   - size-S fly-ins;
   - **four flow expedites:**
     - **R10-FLOW-BODY-PATCH** (STUDY K14)
     - **R10-FLOW-MAIN-GATE** (STUDY K15; after #2570, sharing its classifier)
     - **R10-FLOW-YIELD-PROBE** (R13)
     - **R10-FLOW-DISPATCH** (STUDY K16; an expedite since this revision, with no dependency)
3. **Their groups are not on the roster yet. Apply SHADOW-PLAN §3.3 rule A:**
   - the dispatch names the group id and the brief source `$PACK/roster/groups/<NAME>.json` at `$PACK_SHA`;
   - the PR body says `Group: <ID> (registration pending: roster PR-B)` and cites it;
   - reviewers review against that pinned file;
   - "group: none" is not acceptable;
   - no carry may point to a pending group.

   Fly-ins follow the same rule, with the brief text in the dispatch and one #201 line.
4. **Reading main: rule B.** When `--overlap` says "main is not green", read the latest run of each required context (ruleset `main-protect-checks`, live):
   - if they are all pending, that is **wait**: no revert, no main-red fixer, no overlapping train, never `--allow-red`;
   - re-check next tick;
   - pending longer than about 2 h (twice the train CI) is stalled, not red: check for zero runs and run `approve_held_runs.sh`;
   - log each instance in one line on #201.
5. **Pitch: on the hour, or when the previous train ends, whichever is later.**
   - Board only heads that are verdicted and green at load time, in one batch.
   - Carry moved verdicts before any re-review.
   - Use `--bot-prs` and both `--ignore-red` names.
   - Log each train's CI time.
6. **Body fixes without moving a head,** until BODY-PATCH lands: use the K14 interim. Run `app_push.sh` from a clean worktree at the PR's exact head, `--dry-run` first, and confirm the head is unchanged afterwards.
   - **It has never run live.** The #2560 case revision 3 cited was stale (its body already says 113).
   - **The first real test is #2561** (carry-missing at 1019d18d), if that block survives #2559's merge. Otherwise it is the next block whose repair is body-only at an unchanged head.
   - Run `update_pr.sh` only when the code tip moved, or the PR is DIRTY or conflicted.
7. **Blocked heads** go back to their fixer in the same turn. **Reviewers** take critical-path groups first. Step 11 stands on the post-workflow pr-contract run (R9).

## Phase 1a: #2559 under the freeze (the clock is redefined)

- **The freeze** runs from review dispatch until #2559 merges: no `roster_edit.py --push` in that window.
- **The 4-h bound runs only while #2559 is under review,** from dispatch until a verdict posts.
  - **Blocked verdict:** lift the freeze, push the held edits, and request one fresh review (its own clock).
  - **No verdict in 4 h:** lift the freeze and push the held edits. That stale review then needs re-dispatching.
  - **`merge` verdict:** the clock stops. The freeze holds until merge.
- **Now:** #2559 holds a `merge` verdict at 802b3850 (16:58Z). The clock is stopped, and #2559 boards **as the first car of the next train**. If no train is running, merge it directly at once.
- Its merge clears `BAD-DEST` on #2529, #2547 and #2561.

## Phase 1b: two roster PRs, one review each (your default split, adopted)

**Roster PR-A, the re-chain** (once #2559 and #2513 have merged):
- the seat's 8 drops, 3 required and 4 recommended edges, and HEAT-METER ← R10-THERMAL-POWER-OPTION (`set-after`);
- the note and brief text from the seat's decision file, plus the seat's three files as evidence.

One Opus reviewer checks it edge by edge. When it merges, raise lane A to 4 (`HPO_WIP_CAP=13`; lanes A4 B4 C3 F2).

**Roster PR-B, the bookkeeping** (after PR-A merges; one roster branch, so sequential):
- **`append-group`** for each `$PACK/roster/groups/<NAME>.json`, in this order:
  R10-FLOW-BODY-PATCH, R10-FLOW-MAIN-GATE, R10-FLOW-YIELD-PROBE, R10-FLOW-DISPATCH, R10-FLOW-RECHAIN, R10-FLOW-ROSTER-FREEZE, R10-FLOW-BODY-ONLY, R10-FLOW-PULL, R10-FLOW-ANDON, R10-FLOW-WIP, R10-FLOW-JIDOKA, R10-FLOW-POSTMERGE, R10-FLOW-BOARD, R10-FLOW-AUTOTRAIN, R10-FLOW-MQ-PROBE, R10-FLOW-RECORD-PITCH.
  - Give each group its actual stage and merge sha (the rule-A expedites may be done already).
- **The 6 carries** (`$PACK/tools/flow_groups.py` `CARRIES`).
- **The held stage changes.**
- **Fly-in registrations.**
- **Two notes:** whether #2528's remaining work overlaps #2526, and whether R10-ORCH-MACHINERY part (3) duplicates #2558.

PR-B is mechanically reviewable. Each group must equal its pack file at `$PACK_SHA` (stage and resume fields excepted), each carry must equal its `CARRIES` text, `brief_lint` must print `TOTAL: 0`, and `carry_audit.py owners` must show no orphan. If PR-A's review loops, PR-B may go first. The freeze and its clock apply to each PR in turn.

Then post one #201 comment through `gh_comment.py`, with a byte-identical read-back.

## Phase 2: flow groups through lane K, two at a time

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

- Each follows `fixer.md` in full.
- ANDON, AUTOTRAIN, POSTMERGE, BODY-ONLY, ROSTER-FREEZE, DISPATCH, WIP, MAIN-GATE and BOARD carry seam notes: they become job scripts or functions that R10-ORCH-MACHINERY's beat and ledger host unchanged. ANDON's and AUTOTRAIN's scripts run detached.
- **When you dispatch R10-ORCH-MACHINERY,** brief it with its approved design plus its alignment carry: requirement 0 (detached), the two jobs, the `postmerge-owed` ledger kind, the every-head freeze, dispatch records, one classifier, one plan model.
  - R12: the amendments are approved in that brief.
  - R14: the stranded-handoff aging is 4 h to a DISPATCH line and 12 h to an owner flag.
- **Code-owned work** is approved under mandate 6319294694.
- **R15:** draft the three standing trigger prompts once DISPATCH lands; the owner creates them.
- **R11:** when ANDON merges, say so on #201; the study session then sets up the off-host watcher.
- Lanes A–F dispatch by pull. The critical path is ADVISOR → SCORES → LIVESTATE → PARAMS-OWNER → HEAT-METER → COP-GATE → UX-HEALTH → ARCH-DOCS.

## Phase 3: decide (around day 2)

FLOW-MQ-PROBE runs after R10-CI-LAYOUT-P1, on a throwaway branch and ruleset. Report to the owner. If the queue is adopted, close FLOW-RECORD-PITCH.

## Guardrails: record the baselines at adoption

| guardrail | trips when |
|---|---|
| Main health | a **required** context's latest run on a `main` push concludes failure on two consecutive pushes after a flow change merged. Pending and non-required contexts never trip it. |
| Reverts | any revert of a flow-change merge |
| Reopened issues | any issue reopened that a post-adoption merge closed |
| Review strength | **reports only** (R13) until YIELD-PROBE reports. Re-measure with `python3 $PACK/tools/review_baseline.py --hours 48` after fetching the `review/*` refs, and put the figure in each #201 state comment. The method is in STUDY, "Guardrail baselines": the old 0.52 and 0.15 windows overlap; disjointly it is 0.69 → 0.15. |
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
