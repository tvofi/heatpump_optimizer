# Final handover prompt for the round-10 orchestrator (revision 2, after your evidence of 2026-10-21)

Send everything between the two lines as it is.

---

You are the round-10 orchestrator. Your contract is unchanged: `dev/governance/roles/orchestrator.md`, with `dev/governance/roles/nudge.md` as your turn. This message replaces the first flow-plan prompt. It takes in your four findings:
- the seat's re-chain ruling;
- `update_pr.sh` merging `main` on every run;
- #2559 as a moving head;
- `BAD-DEST` on handoff-only carries.

It changes **what you dispatch, when, and how merges are paced**. It changes no gate, no identity rule and no approval rule.

**Authority.** The owner's rulings R1–R9 are #201 comment [6318002897](https://github.com/tvofi/heatpump_optimizer/issues/201#issuecomment-6318002897), under mandate 6175172275, in force to 2026-10-28T18:14Z. Cite it wherever nudge.md asks for the session mandate.
- Where this message and nudge.md disagree, follow this message only on what R1–R9 name.
- When R10-FLOW-PULL merges, nudge.md carries the rules itself and this message retires.

**The pack** is on branch `claude/dazzling-gauss-7l3u2b`, under `dev/programme/flow-study/`. It is a reading copy, not a pull request.

```
git fetch origin claude/dazzling-gauss-7l3u2b
git worktree add --detach ~/hpo-orch/flow-study origin/claude/dazzling-gauss-7l3u2b   # or: git -C ~/hpo-orch/flow-study checkout --detach origin/claude/dazzling-gauss-7l3u2b
PACK=~/hpo-orch/flow-study/dev/programme/flow-study
```

Read `$PACK/FUTURE-STATE.md` §11 (what changed after your evidence) and §8, then `$PACK/SHADOW-PLAN.md` §3.2. `$PACK/STUDY.md` is for the seats: brief each flow-group fixer with its own section.

**Your seat's re-chain ruling is the authority.** STUDY K7 now reproduces it, and the model's critical depth is 8. Keep its files (`rechain-decision.md`, `-drops.json`, `-adds.json`) and land them in the tree with the Phase-1b burst, never only on a host.

## Phase 0: drain, stop starting (now until about 12 h)

1. **Measure at your refs first.** Never carry a number from this message into a record.
2. **Start nothing new** except an expedite (red main, quota, outage, security, owner-flagged) or a size-S fly-in. A fly-in is registered as `R10-FLY-<topic>` with `append-group` in Phase 1b, and noted on #201 until then.
3. **Pitch: on the hour, or when the previous train ends, whichever is later** (R1, R3).
   - Load every verdicted PR, with `--bot-prs` and both `--ignore-red nightly-status` and `--ignore-red delivery-status`.
   - Before any re-review, run `tools/pr/app_approve.sh --carry <verdict-sha> <head>`. Only `CARRY: no` gets a reviewer.
   - Log each train's CI time: the pitch is set from that measurement, and a 2-h pitch costs only about 2 h.
4. **R4 is not yet true in `update_pr.sh`** (it merges main on every run). Until R10-FLOW-BODY-ONLY lands:
   - run `update_pr.sh` only when the handoff code tip moved, or the PR is DIRTY or conflicted;
   - for a body-only fix, run the body contract and PATCH the body through the App without `update_pr.sh`. Where you cannot, carry the verdict (#1667) rather than re-review.
5. **Blocked heads** go back to their own fixer in the same turn.
6. **Reviewers** take unreviewed heads oldest first, critical-path groups ahead of everything. A verdict posts once the head's required checks have concluded. Step 11 stands on the post-workflow pr-contract run (R9); the mutation proof stays the reviewer's.

## Phase 1a: merge #2559 first, under a roster freeze

- **No `roster_edit.py --push` of any kind until #2559 has merged.** That includes stages and carries. Note any roster fact on #201 meanwhile.
- Re-review #2559 once, at its frozen head, then merge it. That also clears the `BAD-DEST` blocks on #2529, #2547 and #2561 at their next pr-contract run.

## Phase 1b: one burst, one new roster PR (once #2559 and #2513 have merged)

In one sitting, through `roster_edit.py`'s lint gate (never a JSON splice):

1. **Your seat's ruling,** with `set-after`, plus the architect-note and brief text its decision file lists:
   - the 8 drops
   - the 3 required edges
   - the 4 recommended edges
   - the study's HEAT-METER ← R10-THERMAL-POWER-OPTION edge (0 depth; they share flow_meter.py, config_flow.py and const.py)

   Never apply the drops without the required edges.
2. **The 12 flow groups,** in this order so every `after` exists:
   ```
   append-group $PACK/roster/groups/<NAME>.json
   ```
   R10-FLOW-RECHAIN, R10-FLOW-ROSTER-FREEZE, R10-FLOW-BODY-ONLY, R10-FLOW-PULL, R10-FLOW-ANDON, R10-FLOW-WIP, R10-FLOW-JIDOKA, R10-FLOW-POSTMERGE, R10-FLOW-BOARD, R10-FLOW-AUTOTRAIN, R10-FLOW-MQ-PROBE, R10-FLOW-RECORD-PITCH.
   - Mark RECHAIN done once item 1 has landed.
   - A brief_lint refusal means the roster moved: fix that line, never the linter.
3. **The 6 carries** (`append-carry`; the texts are in `$PACK/tools/flow_groups.py`'s `CARRIES`) on:
   - R10-RCA-HEADMOVED
   - R10-RCA-ORCH-CONTINUITY
   - R10-CI-LAYOUT-P2
   - R10-CI-LAYOUT-P1
   - R10-POLICY-FIXER-MD
   - R10-ORCH-MACHINERY
4. **The stage changes you held during Phase 1a,** any fly-in registrations, and two `set-resume --field note` checks:
   - whether #2528's remaining work overlaps #2526;
   - whether R10-ORCH-MACHINERY part (3) duplicates #2558.
5. **Open one new roster PR and dispatch one reviewer.** No roster push while that review runs.
6. **Raise lane A to 4 that hour** (R2: `HPO_WIP_CAP=13`, lanes A4 B4 C3 F2).
7. **One #201 comment** through `gh_comment.py`, with a byte-identical read-back: "flow plan phase 1 done", plus the roster sha.

## Phase 2: flow groups through lane K, two at a time (from about 12 h)

Dispatch in §2's order, each only once its `after` group has merged:

| flow group | waits for |
|---|---|
| **ROSTER-FREEZE** | — (first: removes the head-moving loops you found) |
| **BODY-ONLY** | R10-UPDATE-PR-SIGNALS; sequence it with #2567 and #2560, which edit `update_pr.sh` |
| PULL | — |
| ANDON | #2549 |
| WIP | PULL |
| JIDOKA | #2528 |
| POSTMERGE | #2554 |
| BOARD | #2558 |
| AUTOTRAIN | PULL and #2549 |

Each follows `fixer.md` in full, with STUDY §0's enumerators as the finder's harness at both ends.

FLOW-PULL, the R10-POLICY-FIXER-MD carry, FLOW-ROSTER-FREEZE's `carry_audit.py` change and the workflow changes are code-owned. They need tvofi's review under the mandate **before 2026-10-28T18:14Z**, or a fresh grant.

Lanes A–F dispatch by pull as the drain frees them: the longest remaining chain first. The critical path is ADVISOR → SCORES → LIVESTATE → PARAMS-OWNER → HEAT-METER → COP-GATE → UX-HEALTH → ARCH-DOCS.

## Phase 3: decide (around day 2)

FLOW-MQ-PROBE runs after R10-CI-LAYOUT-P1, on a throwaway branch and ruleset only (R8). Report to the owner. If the merge queue is adopted, close FLOW-RECORD-PITCH; otherwise build it.

## Unchanged

- Identities (decision 0011).
- No budget raise without the owner.
- No `VERSION` or notes edits outside `stamp.py`.
- No `--allow-red`.
- "Leaves #201 open".
- Decision 0012's moratorium, to 2026-10-31.

## Stop and tell the owner on #201

Stop if, after a flow change merges, you see any of these:
- a red push run on `main`;
- a revert;
- a reopened issue;
- a fall in real-catch blocked verdicts per PR (`harness`, `class-open`, `vacuous`).

## Done looks like

- Every roster group merged or deferred, then the stamp.
- Trains on the pitch.
- No head moved by a body fix or a roster edit.
- Lane A four wide.

The model puts the last merge about **92 h** after adoption on your seat's chain, against about 207 h for the live roster on today's process. It is a model: report what you measure.

---
