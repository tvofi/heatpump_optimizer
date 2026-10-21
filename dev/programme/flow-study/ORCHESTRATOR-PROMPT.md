# Handover prompt for the round-10 orchestrator: **revision 11** (2026-10-21)

**Revision 11** answers s4's four points on revision 10:
- standing rule 16 states that expedites go over the WIP cap;
- standing rule 17 and every instrument brief now carry the self-test hygiene;
- the RATCHET-RED facts are corrected;
- a stacking option is added for P1 on PR G.

**Revision 10** has two parts:
- the owner's ask that R10-CI-LAYOUT-P2 land as soon after PR 1 as possible, in a gap between critical-chain groups;
- a cost-of-delay (CD3) re-ordering of every open non-production group (sections "CI layout" and "Finish first", standing rule 15, FUTURE-STATE §12).

**Revision 9** set the CI-layout minutes. This prompt supersedes revisions 1–9 and is self-contained. The study channel is one-way, so this file on branch `claude/dazzling-gauss-7l3u2b` is the reply.

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

*As of revision 8. Re-read the live state before acting on any line here. At revision 10 (about 16:27Z by the PR list), these were open as drafts: roster PR-A #2576, DISPATCH #2577, BODY-PATCH #2578, and RATCHET-RED #2531 (ready) with #2575.*

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

11. **The K14 body-only interim is slow but correct.** It costs about 3 minutes, because `app_push.sh` runs prepr. Accept that until BODY-PATCH lands; BODY-PATCH runs only the body contract (target under 30 s).
12. **An offline `carry_audit.py check --body` reads the roster from the worktree,** so it passes a carry that is not on the roster branch, and only fix-review step 10 would catch it. Until JIDOKA and BODY-PATCH pass the roster ref themselves, run it as:
    ```
    git fetch origin handoff/audit-r10-roster
    python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <file>
    ```
    `--roster-ref` is a global option, so it goes before `check`.
13. **Stale check-runs recur** (#2559, #2567). One re-run of the stale run clears each: do that before any merge attempt, never a merge retry loop. Log each instance with its run id on #201; **a third instance goes to a root-cause seat** (`defect-root-cause.md`). MAIN-GATE (b) automates the re-run in `merge_pr.sh` and the train.
14. **A relayed "verdict posted" is not evidence. Read it back from the PR's comments:** the first line must match `Fix review: merge|blocked <the head sha>` and carry the dispatch nonce. Only then confirm, approve, board or return it (`comment-readback.md`). R10-ORCH-MACHINERY's ledger closes `verdict-unposted` only on that read-back (its carry, item 4b).
15. **The next critical-chain link never waits for a lane slot.** When a chain link's predecessor merges, dispatch it even if its lane is at cap: it counts one over the cap until the lane drains below it. This is CCPM's capacity buffer. The model found a chain link losing an hour to a full lane A (FUTURE-STATE §12).
16. **Expedites go over the WIP cap; that is the intent.** The board read 17 against a cap of 6, with 24 open PRs. The groups below dispatch over the cap:
    - the five flow expedites (RELAY-HOLD, BODY-PATCH, MAIN-GATE, YIELD-PROBE, DISPATCH);
    - FLOW-ANDON;
    - R10-CI-LAYOUT-P1 and P2's units (the owner's ask);
    - the next critical-chain link (rule 15).

    A rework round on a group already dispatched (PR G round 2) is not a new dispatch. Everything else waits for the drain.

    If `pr_cap.py` has no per-group override, set `HPO_WIP_CAP` to the board's count plus one **for that one dispatch command only**. Never persist it, and log each one in a line on #201. At most two expedite reviews run at once, as before. When roster PR-A merges, the persistent cap becomes 13 (A4 B4 C3 F2), with lane K's 2 on top.
17. **Self-test hygiene.** Every pack brief for an instrument group now carries both points; they come from today's live findings.
    - **(a)** A new seat-selftest mutant in `dev/audit/harnesses/r10_seat_selftests_mutants.py` takes a per-file id (`cloud_relay-1`), never a new `S` number (the P6 convention).
    - **(b)** A self-test builds git repositories only through `tests/throwaway_git.py`, never a hand-built `git init`, and runs `python3 tests/throwaway_git.py --check` before the handoff.

    Point (a) cost a code round each to RELAY-HOLD, YIELD-PROBE and PR G in one day. That is the third instance, so by CLAUDE.md it goes to a root-cause seat (`root-cause.md`), not an issue. The countermeasure available now is brief text, because decision 0012's moratorium bars a new check until 2026-10-31. The seat records whether a check is worth building after that.

## Expedites: one wave at a time, by dependency, so reviewers are not spread

1. **RELAY-HOLD** (fired): first in review.
2. **BODY-PATCH** (fired) and **MAIN-GATE** (dispatch as soon as #2570 merges). Revision 7 widened MAIN-GATE into the one classifier for:
   - (a) main red
   - (b) stale check-runs
   - (c) DIRTY by merge-tree
   - (d) reviewable heads

   If its fixer has already started, (b) to (d) are its second PR.
3. **YIELD-PROBE** (fired): it keeps working, but gets a reviewer only after wave 2's verdicts have posted.
4. **DISPATCH and ANDON:** dispatch DISPATCH after RELAY-HOLD merges and ANDON now; review both after wave 2. DISPATCH's dispatcher will refuse a reviewer at a red head (rule E, made mechanical).
5. **Size-S fly-ins** take a reviewer only when no expedite review is waiting, unless they are line-stop.

**At most two expedite reviews run at once.** Critical-path product reviews (ADVISOR → SCORES → LIVESTATE → PARAMS-OWNER → HEAT-METER → COP-GATE → UX-HEALTH → ARCH-DOCS) keep their own reviewer.

## CI layout: P1 now, P2 straight after it (revision 10, the owner's ask)

The three groups are lane IN, so they take no A–F WIP slot. They get the next reviewer before any lane pull that is **not** on the critical chain. One Opus reviewer takes P1 and then P2, in CODEOWNER mode under the mandate. The critical chain keeps its own reviewer.

**Measured today** (job timestamps):
- PR run 39625218966 (scoped): 48.6 min. coverage 25.8 min, then closures 20.3 min. closures waits for coverage; fast took 11.0 min in parallel.
- Main push run 39619839750 (FULL): 47.8 min. fast took 40.6 min.
- The last 4 Tests push runs on main are red: `ci-ratchet` (metrics gather) and `record-autofix` ("Enumerate the window's merges").

| group | CI minutes per train | when |
|---|---|---|
| **R10-CI-RATCHET-RED**: #2531 merged at 17:00Z and #2575 is closed | 0: it runs only on main pushes | **Done.** `ci-ratchet` reads an empty or partial window body as a failed fetch, never as an empty window, on main at f2fb1b0e9 (`tests.yml`, the "Gather this run's and the recent window's metrics" step). #2575's other half (list the window lane by lane; a failed listing fails the step) is not on main. Reopen it only if Gather still fails. The first push runs carrying #2531 were still in progress at 17:08Z (39640285028, 39640647700, 39640981803), so main is not yet confirmed green. |
| **R10-CI-LAYOUT-P1** | about 7 min (FULL train) to about 19–21 min (scoped run) | **Dispatch now, beside PR G #2529.** The roster edge P1 → CI-LAYOUT orders merges only. PR G gets the next reviewer once its head reaches the round-2 handoff (`bfcdece3`) and is reviewable, because it gates P1's merge. Where P1's files overlap PR G's (`governance.yml`, the self-test wiring), base P1 on PR G's head rather than main, and merge main in after PR G lands. That avoids a fourth content-conflict round. |
| **R10-CI-LAYOUT-P2** | about +1 min per run. Its value is one required `gate` in place of 17 contexts, and no rerun followers. | **As soon after PR 1 as possible** (below). |

**P2 schedule.** Units follow DESIGN-P2 L1374–1377:
1. U0 now (the platform facts M-1 and M-4).
2. U1–U4 and U6–U8 beside PR 1: cloud fan-out, at most 4 at once.
3. U5 once PR 1 merges, then U10, then U9 on `probe/ci-layout-all`.
4. The combined null control.

That leaves about 6 h between PR 1's merge and P2's verdict. The model puts P1 at about h30 and P2 at about h36–47 from adoption (revision 9's order had them at h45–83 and h57–94).

**P2's cut-over goes in a gap between critical-chain groups.** It is the merge plus the owner's ruleset PUT (17 contexts → `gate`).
- **Merge only at a pitch where no critical-chain PR** (ADVISOR → SCORES → LIVESTATE → PARAMS-OWNER → HEAT-METER → COP-GATE → UX-HEALTH → ARCH-DOCS) is verdicted and green waiting to board, or is in its final CI run (within about 1.5 h of boarding). The best moment is right after a train that carried a chain link.
- **Tell the owner when P2 gets its merge verdict,** so the ruleset PUT follows the merge within minutes. Rollback is two actions, ruleset first.
- **Then one cut-over sweep.** It is the one exception to rule D. Absorb main into the in-flight critical-chain PR first, then the rest in pull order. Keep at most 4 full CI runs queued at once. The relay's handoff arm does not do this for you.

**P2's brief carries three things.**
- (a) The re-keyed `ci-ratchet`, which reads `ci.yml` push runs, keeps #2531's never-read-empty fetch. It is on main; carry it, do not re-derive it.
- (b) After cut-over, an edit or review made during an in-flight code run waits for that run (R-2; median 1406 s before W1, less after). So BODY-PATCH's 30-s target holds only when no code run is in flight. MAIN-GATE (d) reads `gate`.
- (c) The stamp needs one green `ci.yml` push run on main after cut-over.

**If no group owns `record-autofix`'s "Enumerate the window's merges" failure,** register fly-in `R10-FLY-RECORD-ENUM`: it blocks a green push run, and P1 only moves the job.

## Finish first: the open non-production groups in CD3 order (revision 10)

CD3 is the round time a group removes, per hour it lands earlier, divided by its size. In the model, the order changes the round by 0 h when every in-progress group lands on its size's lead. It changes it by 1 h at twice that lead, and 3 h at three times (today: #2524, #2528 and #2529 have been drafts for about 17 h). The enablers' effects themselves are worth about 6 h (92 → 86 h), but only if they land before the chain's middle links dispatch (LIVESTATE about h29, PARAMS-OWNER about h45). Stop starting, start finishing.

**Review first, in this order** (none takes a reviewer from a critical-chain link):
1. **R10-CI-RATCHET-RED** (#2531): the stamp's push run.
2. **R10-PREPR-CAP** (#2528): 10–25 min of local closures per handoff; load about 168 on 8 cores. It unblocks FLOW-JIDOKA, and must merge before POLICY-GATE-SCOPING (same file).
3. **R10-TICK-OWED-LEVEL** (#2547, ready): the tick re-reads 35,214 OWED lines (4.5 MB) every pass.
4. **R10-REPLAY-CAP** (#2548, ready): a red nightly turns `nightly-status` red on every PR run. It is a re-record (0.111 → 0.143), so it owes its `## Raise justification`.
5. **R10-ROSTER-PUSH-RACE** (#2569): a lost roster edit is silent, and PR-B makes about 25 roster edits. **Merge it before PR-B.** It is also the live DIRTY content conflict (rule 5).
6. **R10-UPDATE-PR-SIGNALS** (#2524): pusher survivors 26–62 min old. It gates FLOW-BODY-ONLY.
7. **R10-HANDOVER-REFRESH**: every new seat orients from a page 2072 commits stale.
8. **R10-FLOW-ANDON** joins expedite wave 4 with DISPATCH. The silent stops it guards against cost 6.2 h, 8 h and 16 h across 4 days (R10-RCA-ORCH-CONTINUITY).
9. **PR G #2529 → P1 → P2**, as above.
10. **R10-RCA-FRICTION → R10-BRIEFS-FOLD → R10-POLICY-FIXER-MD**, serially, because they share fixer.md and fix-review.md at zero headroom. They mean fewer bookkeeping blocks, and BRIEFS-FOLD also blocks ARCH-DOCS (the chain's last link). These are policy edits: the owner's call at merge, under decision 0012's moratorium.
11. **R10-ORCH-MACHINERY**: build the ledger, beat and page now, after PR G. Its workflow-wiring PR merges after P2, because it collides with the umbrella's files.
12. **R10-PLAN-ARTIFACT** (#2558): it unblocks FLOW-BOARD.

**Merge now and move the closing keyword.** R10-I5-DOCS (#2521) is ready, but its brief holds it to merge last of four, to close #2222. A finished PR held open is WIP: put `closes #2222` on whichever of the four merges last.

**Normal pull:** R10-POLICY-GATE-SCOPING (after PREPR-CAP), R10-POLICY-LINT-FAMILY (false friction lines make the cron file spurious issues).

**Later: finishing these earlier saves nothing, or costs CI or reviewers.**
- R10-REPLAY-LANE and R10-REPLAY-SCOPED: they add replay runs to relevant PRs. Deadline: before ARCH-DOCS dispatches (about h79).
- R10-MUTATION-ANCHOR: it touches `tests/entities.py`, which forces FULL CI, for quality only.
- R10-MERGE-SUBJECT-HARDEN.
- R10-RCA-HEADMOVED: record only.
- The RCA records for R10-RCA-HANDOFF-SLIP and R10-RCA-ORCH-CONTINUITY: merge when ready; their countermeasures are ANDON, DISPATCH and the ledger.
- R10-MUTANT-SKIP, except that its step 1 (the replay matrix) runs now as a probe. If `mutation-pins` (median 2940 s on pin-chain PRs in the design's sample) sits on critical-chain PR runs, promote it.

## Phase 1b: two roster PRs, one review each, starting now

**Roster PR-A, the re-chain** (`roster_edit.py set-after`, through its lint gate):
- the seat's 8 drops, 3 required and 4 recommended edges, and HEAT-METER ← R10-THERMAL-POWER-OPTION;
- the note and brief text from the seat's decision file, plus the seat's three files as evidence.

One Opus reviewer checks it edge by edge. When it merges, raise lane A to 4 (`HPO_WIP_CAP=13`; A4 B4 C3 F2).

**Roster PR-B, the bookkeeping** (after PR-A merges):
- **`append-group`** for each `roster/groups/<NAME>.json`, in this order:
  R10-FLOW-RELAY-HOLD, R10-FLOW-BODY-PATCH, R10-FLOW-MAIN-GATE, R10-FLOW-YIELD-PROBE, R10-FLOW-DISPATCH, R10-FLOW-RECHAIN, R10-FLOW-ROSTER-FREEZE, R10-FLOW-BODY-ONLY, R10-FLOW-PULL, R10-FLOW-ANDON, R10-FLOW-WIP, R10-FLOW-JIDOKA, R10-FLOW-POSTMERGE, R10-FLOW-BOARD, R10-FLOW-AUTOTRAIN, R10-FLOW-MQ-PROBE, R10-FLOW-RECORD-PITCH, R10-FLOW-TOOLKIT-MEASURE, R10-FLOW-TOOLKIT-MODEL.
  - Give each its actual stage and merge sha.
  - **MQ-PROBE and RECORD-PITCH now wait on R10-CI-LAYOUT-P2** (revision 10). Use their files at this revision's commit.
  - **MAIN-GATE's file is size M with the widened brief at this revision.** Use the file at this revision's commit.
- **The 10 carries** (`tools/flow_groups.py` `CARRIES`). Revision 11 adds the self-test hygiene carry on R10-CI-LAYOUT-P2 and R10-ORCH-MACHINERY. Revision 10 added the owner's shape-docs carry on R10-ARCH-DOCS and its table carry on R10-ORCH-MACHINERY.
- **Revision 10's edges:** R10-ARCH-DOCS ← R10-ORCH-MACHINERY, R10-CI-LAYOUT-P2 and R10-FLOW-TOOLKIT-MODEL (`set-after`; 0 depth).
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
| TOOLKIT-MEASURE | — (the study's tools on main; its critical-path instrument serves P1's body) |
| TOOLKIT-MODEL | ORCH-MACHINERY and TOOLKIT-MEASURE; due before round 11's P3 |

- Each follows `fixer.md` in full.
- Seam notes make them job scripts or functions R10-ORCH-MACHINERY's beat hosts unchanged, detached.
- **R10-ORCH-MACHINERY** is briefed with its approved design plus its alignment carry: requirements 0 and 0b (detached, concurrent), the heartbeat and pitch jobs, the `postmerge-owed` ledger kind, the hold-aware every-head freeze, dispatch records, one classifier and one plan model. R12 approves the amendments; R14 sets aging at 4 h to a DISPATCH line and 12 h to an owner flag.
- **R15:** draft the three standing trigger prompts once DISPATCH lands.
- **R11:** when ANDON merges, say so on #201.
- **The last stage, R10-ARCH-DOCS,** now documents and draws the orchestration machinery beside the CI shape (owner, revision 10).
- Lanes A–F dispatch by pull, longest remaining chain first.

## Phase 3 (after P2; about h45–50)

- FLOW-MQ-PROBE (and FLOW-RECORD-PITCH) now wait for **P2**, not P1: probe once, on the layout that would be adopted, whose single `gate` is what reports on `merge_group`.
- Use a throwaway ruleset only, and report to the owner, who decides adoption.
- If the queue is adopted, close FLOW-RECORD-PITCH.

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

The model's figure is about 86 h from adoption if the enablers land on their leads, and 91–97 h if in-progress groups keep taking two to three times their lead (FUTURE-STATE §12). Report what you measure.

---
