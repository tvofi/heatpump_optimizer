# Lean flow pre-study: one section per FLOW group

Sections: §0 shared harness · K1 BOARD · K2 JIDOKA · K3 PULL · K4 WIP · K5 (carry on POLICY-FIXER-MD) · K6 RECORD-PITCH (conditional) · K7 RECHAIN · K8 ANDON · K9 MQ-PROBE · K10 AUTOTRAIN · K11 POSTMERGE · K12 BODY-ONLY · K13 ROSTER-FREEZE · K14 BODY-PATCH · K15 MAIN-GATE · K16 DISPATCH · K17 ORCH-MACHINERY alignment · guardrail baselines · fly-in intake.

This is for the fixer and reviewer seats that build the round-10 flow groups. Every anchor was read at `origin/main` 22615537a (2026-10-21) and the live roster at `origin/handoff/audit-r10-roster` 8afd645da. **Re-derive every figure at your own merge base** (`fixer.md` step 3): a line number here is a pointer, not a citation.

The measurements behind each group (the round-10 baseline) come from the study. Re-take them with the enumerators in §0, at both ends, as your finder's harness.

---

## §0 Shared harness: the round-10 baseline and how to re-take it

| figure (round-10 Phase 3, 2026-10-15 14:37 → 2026-10-21 13:00) | value | enumerator |
|---|---|---|
| Roster groups closed per hour | 0.30 (43 groups in 142 h) | roster `resume.stage` in `roster_lib.DONE_STAGES`, counted against roster PR merges in the window |
| Groups added to the roster per hour | 0.39 (52 → 108) | `git log -p` of the roster file on `handoff/audit-r10-roster` |
| Fly-in merges (branch topic on no roster group) | 34, median 200 inserted lines, median 7 commits, 1 touches `custom_components/` | first-parent merges of `origin/main`; branch from `Merge pull request #N from tvofi/<branch>` |
| Record merges (`record/*`) | 113 of 223 PR merges (51%) | same log |
| Roster-edit merges (`audit-r10-roster*`) | 20 | same log |
| Fix review first-pass yield | 63 of 131 PRs (48%); 2.18 verdicts per PR | `git log --format=%s origin/review/<pr>`: one commit per verdict |
| Merge-to-merge re-reviews (head moved, code unchanged) | 30 | consecutive `merge` subjects on one `review/<pr>` ref |
| Blocked classes | harness/class-open 38, carry-missing 25, red/contract/body ≈ 25, vacuous/mutation 14, other ≈ 31 | class token after the 40-hex in blocked subjects |
| Main absorbs per fix branch | median 4, mean 5.6 (40% of branch commits) | multi-parent commits in `<merge>^1..<merge>^2` |
| Lead time, first commit → merge, by size | S 8–15 h, M 12 h, L 20 h (medians) | per-PR first commit date against merge date |
| Hours with at least one merge | 117 of 165 (71%) | hourly buckets of first-parent merges |

Null control for every rate: the same enumerator over 2026-10-08 → 10-14 (round 9's drain). Its figures must stay unmoved by your change. Only the window after your merge may move.

---

## K1 · R10-FLOW-BOARD (instrument, S, Sonnet fixer, Opus reviewer)

**Where:** extend `tools/audit/merge_throughput.py`; add no new file.
- **Today:** about 330 lines with argparse `--self-test`, `--from-runs FILE`, `--since`, `--wait`. It reads only a `gh run list` JSON (no network of its own) and prints `RESULT …` lines. Its self-test has 20 `check()` calls and **no `# mut:` markers**.
- **It has no callers and runs in no workflow.** Its self-test runs nowhere today (the decision-0004 shape: an assertion that never runs). Wiring it in is part of this group.
- **Classification:** `tools/audit/` is INERT by prefix (`tests/closure.py`, the INERT list). The file is in neither INERT nor INERT_EXCEPT by name, and no CODEOWNERS line covers it.
- **The beat:** `tools/audit/seat/state_docs.py` publishes `PLAN-TABLE.md`, `RESUME-CURRENT.md` and `NEXT-SESSION-PROMPT.md` to `handoff/audit-r<N>-plan`. The generator list is `generate()`'s `plan` list, and `DOC_NAMES` sets the write set (checked by `check_write_set`). Adding `FLOW-BOARD.md` touches both.
- `state_docs.py` **is** in INERT_EXCEPT, a file the gate reads, so this change selects closure scripts. Expect the scoped gate to pick them.
- **Bus grammar** (`bus.sh`): `verdict: #N Fix review: merge <40hex>` has **no class token**; `… blocked <40hex> <class>: <why>` has one. Parse both.

**Design notes**
- Data: `git log --first-parent origin/main`; `refs/remotes/origin/review/*` (fetch them, since a default clone may lack them); the roster through `roster_lib.show_roster`.
- No `gh` calls: the flow board must cost no API quota (the round already exhausted the Actions quota once, see R10-FOLLOWER-DEBOUNCE).
- Lanes are derived, not stored. **F** = group name `R10-FLY-*`, or a merged or open branch no group owns. **C** = kind in {instrument, policy, rca, record, docs, fix} or name `R10-FLOW-*`. **A** = coordinator.py in `hot_files`, or roster_lib critical-path depth ≥ 3. **B** = everything else.
- An unreadable source prints `UNAVAILABLE`, never 0, the same rule ORCH-MACHINERY's plan page follows.

**Seams**
- R10-PLAN-ARTIFACT (#2558, open) ports the plan page into `plan_table.py`. Sequence after it (shadow `after`) and add a flow strip to that page, not a second page.
- `plan_table.py` has no separate model builder: its functions are `gantt`, `swimlanes`, `detail`, `eta`, `render`. Do not invent a shared model the file does not have.

**Controls**
- A fixture (one group merge, one blocked-then-merged verdict pair, one record merge, one fly-in) yields exact counts.
- The null-control window reads identical before and after.
- Mutants: deleting the record filter, the class parse, or the UNAVAILABLE arm each fail a named check.
- Wire `python3 -I tools/audit/merge_throughput.py --self-test` into `governance.yml`'s `instrument-self-tests` job. That workflow is code-owned, so it needs tvofi's review under mandate 6175172275.

---

## K2 · R10-FLOW-JIDOKA (instrument, S, Sonnet fixer, Opus reviewer)

**Where:** `tools/pr/prepr.sh`, which has no CODEOWNERS line.
- **Step API:** `step <name> <rc> [detail]` (around L2490). rc 0 prints `ok`; anything else prints `REFUSE` and makes the run exit 1.
- **The body** is positional `$1` (around L2861). There is no BODY.md default, and `PREPR_BODY_PATH_ONLY` is honoured.
- **The existing `pr-body` step** (around L2885) runs `body_line …` into `/tmp/prepr-body.$$`. Note that this writes to `/tmp`, not the scratchpad.
- **The checker to call:** `python3 -I tools/audit/carry_audit.py check --body <file>`. It is **offline** (it reads the roster from the tree; no `gh`) and enforces `Carry: <GROUP> | #<issue> | O<n>[-name] | dismissed: <reason>`.
  - A `dismissed:` needs at least two words, and a marker inside a code span is not a marker.
  - `pr-contract.yml` runs exactly this command, as its last step, against the posted body. Running it in prepr moves the same refusal before handoff, with no new rule.
  - `carry_audit.py` is code-owned (CODEOWNERS L91). You call it; you do not edit it.

**The second question: why red-check answers still blocked review**
- prepr already reads live check state: `ancestry_reds` calls `gh api …/check-runs` for each sha in `base..HEAD`, and `reds_line` passes every red name as one `--red` to `body_check`. The call site is around L2952, gated around L2945–2951.
- Yet 25 blocks were root-cause-unanswered, ci-red or contract. Establish which applies:
  - (a) The gate skipped: no credential, or `PREPR_GH` unset in the seat.
  - (b) The reds appeared **after** the handoff push. CI starts on push, so prepr cannot see them, and the fix is R10-FLOW-PULL's verdict-after-CI rule.
- Measure on 5 of the round's blocked PRs before changing anything. If (b), this group changes no `reds_line` code and says so in the body.

**Owner ruling owed first:** decision 0012 bars a new "lint class" until 2026-10-31 and does not define the term. Running an existing checker earlier is arguably not one, but the owner rules, not the seat.

**Controls**
- A fixture body with an unrouted `## Forward-carry` item: `REFUSE` at the new step, `ok` once it carries `Carry: R10-… `.
- The prepr self-test count rises by exactly the new arms. It runs from `governance.yml` via `bash tools/pr/prepr.sh --self-test`, and a prepr change owes the self-test (`selftest_owed`).
- A step-deleted mutant fails it.

**Sequencing:** after R10-PREPR-CAP, which is in progress and also edits `prepr.sh`. Verify first whether R10-PREPR-CAP is already delivered by the fly-in #2526 (R10-GATE-PRIORITY, merged: "a slot is held for the life of its run").

---

## K3 · R10-FLOW-PULL (policy, S, Opus; tvofi review under the mandate)

**Where:** `dev/governance/roles/nudge.md` (owner `@tvofi`); reconcile `dev/governance/roles/orchestrator.md`.

**Budget:** `node tools/policy/policy_lint.mjs --budgets` measures nudge.md at **115/115 lines and 3812/3814 tokens**. The budget key still reads `tools/audit/briefs/nudge.md`, a path that no longer exists, but it measures the roles file. orchestrator.md is at 317/319 and 4502/4513. **Every added sentence is paid by a cut**, and `ratchet-budgets.md` forbids a raise to make room.

**The sentences this replaces** (quoted at L-anchors on main):

| step | today | becomes |
|---|---|---|
| 2 (L37) | "…dispatch a reviewer this turn… Do not wait for required checks." | Reviewer still dispatched at handoff. **Post** the verdict once the required checks at that head have concluded. Do not wait to dispatch. |
| 3 (L45) | "Load a new train only when … at least two open pull requests are verdicted…" | Load on the **hourly pitch** (at most one train per pitch), with `--bot-prs` so the open record PR merges inside the pitch (`merge_train.py` `sweep_bots`, around L620). A single verdicted PR still merges directly. |
| 3 (L47), 6 (L65), 7 (L69) | record PRs are left off the train and merged directly whenever ready | record PRs merge in the pitch: the `--bot-prs` sweep or the pitch's direct merge, never between pitches unless the record backlog is older than two pitches |
| 9 (L77) | "Exit 0 and no train running: merge `origin/main` and push" | absorb main only when the head is DIRTY or `merge-tree` reports a conflict; a clean merge-tree leaves the head (the batch proves the combined result) |
| 16 (L105) | "…gets a fixer this turn when no fixer is working on it" | dispatch by **pull**: only when `pr_cap.py dispatch-gate` passes for that group's lane, ordered by roster_lib critical-path depth, then size (smallest first) |
| §5 of orchestrator.md (new sentence) | none: every architect note cites §5, but §5 holds no chain rule | a serial chain orders groups whose **owning seams** overlap, not groups that share a file |
| new, step 16 | none | **Scope freezes at the register**: a mid-round finding goes to the next round's register unless it is expedite or a fly-in of size S |
| new, inside 16 | none | **Classes of service.** *Expedite* (red main, Actions quota exhaustion, outage, security, owner-flagged) bypasses caps, one at a time, and merges directly. A *fly-in* (owner request or orchestrator-found defect, size S) is registered at dispatch with `roster_edit.py append-group` under a name starting `R10-FLY-` and occupies lane F. Anything larger than S is not a fly-in: it enters the ready queue and is ranked normally. |

**Conflicts to reconcile in the same PR**
- orchestrator.md L57 ("Absorb `main` locally with the claimnotes driver. Conflicting or DIRTY is not ready"): keep it. DIRTY still absorbs, and the new rule only stops absorbing on a clean merge-tree.
- orchestrator.md L132 ("Dispatch a fix's reviewer when the fixer pushes, not when CI settles"): compatible, because dispatch timing is unchanged and only posting moves.

**Already true, do not restate:** `pr_cap.py dispatch-gate` refuses at HPO_WIP_CAP (6) roster groups in progress (the orchestrator.md bullet from #2525).

**Owner rulings this group cannot make**
- R1: a round in 100 h as the demand, with an hourly merge pitch.
- R2: lane caps A4 B4 C3 F2, total 13. This replaces HPO_WIP_CAP 6 and the tick's coordinator.py 2, which only made sense while the chain was by file (FUTURE-STATE §4.3).
- R3: records inside the pitch.
- R4: the absorb trigger (DIRTY or merge-tree conflict).
- R5: the classes of service and fly-in definition.

**Controls**
- `policy_lint.mjs --budgets` passes with no raise.
- `node tools/policy/rules_sync.mjs --check` is unaffected, since roles are not mirrored.
- The study's harness, re-run 24 h after merge, shows re-reviews and absorbs per PR moving and the null window unmoved.

---

## K4 · R10-FLOW-WIP (instrument, S, Opus)

**Where:** `tools/audit/seat/pr_cap.py` (rewritten by #2525, merged 15:01 today). Read the new file, not an older copy.
- `dispatch-gate` counts `wip_groups(roster)`: groups with `resume.stage == "in-progress"`, through `roster_lib`.
- It refuses at `HPO_WIP_CAP` (default 6), and `--over-cap "<reason>"` overrides. An unreadable roster is a refusal (`# mut:wipunread`).
- `info` prints the open-PR count without gating. `COORDINATOR_CAP = 2` is reported by the tick only.
- Mutants exist: `caprecord`, `capbot`, `capreadrc`, `inforead`, `wipunread`, `overcap`, `cap`.

**What it cannot see**
1. An open PR that no roster group owns: a fly-in, invisible to the cap.
2. A handoff no PR carries. `bus.sh orphans` prints `ORPHAN <topic> … repair=opener|update|review` with summary `orphans: N stranded, …`, and rc 1 only when something is stranded.
3. Lanes: today the cap is a single number.

**Change**
- WIP = in-progress groups ∪ open PRs with no owning group ∪ stranded orphans, de-duplicated by topic.
- Lane caps come from the env, for example `HPO_WIP_LANES="A=4,B=4,C=3,F=2"`, with lanes derived as in K1. Share one lane function with K1: put it in `roster_lib.py` (in INERT_EXCEPT), not in two copies (`fixer.md` step 17).
- `dispatch-gate <group>` refuses when that group's lane is full.
- **Expedite** bypasses with `--over-cap "expedite: <reason>"`. The reason is logged, so the bypass is visible on the board.
- `orchestrator_tick.py` prints `WIP n/cap A a/4 B b/4 C c/3 F f/2` where it prints `WIP:` today.

**Controls**
- A fixture roster, open-PR list and orphan list give exact lane counts.
- One mutant per new counting rule.
- An orphan list that cannot be read is a refusal, never zero.
- **Null control:** with `HPO_WIP_LANES` unset, behaviour is byte-identical to today's single cap.

**Seam:** R10-ORCH-MACHINERY's obligations ledger will own `handoff-no-pr`. Read it when it lands; until then, `bus.sh orphans`.

---

## K5 · carry on R10-POLICY-FIXER-MD (policy, S, Opus; tvofi review)

**Where:** `dev/governance/roles/fixer.md` step 6 (around L71–91) and `.claude/skills/steward/SKILL.md` S2 (L37–52).
- Budgets: fixer.md is at **315/315 lines and 5215/5216 tokens**, and the fixer role is about 6085 tokens against cap 5852 + band 500. steward is at 134/135 and 1532/1533. Pay by cutting.
- **Today:**
  - L80–81: "Until then, update it from `origin/main` whenever you need to — `git merge origin/main`."
  - L71–72: "After any rebase or merge, steps 2–8 are re-executed."
  - S2: "IF the pull request is DIRTY… Merge `origin/main` locally and push."
- **Change (also fix-review step 11):** fix-review step 11 stands on a green pr-contract run that started after the head's last workflow concluded; the step-1 mutation proof stays the reviewer's (HANDOVER L69: CI cannot produce it).

**Change:** before handoff, merge `origin/main` only when `git merge-tree --write-tree origin/main HEAD` reports a conflict, or the PR is DIRTY (the claim-file driver case S2 covers). Steps 2–8 re-run only when the absorb touched a file in the diff's closure.
- **Escalated ambiguity, owner ruling R4:** a merge-tree conflict and DIRTY are different conditions. A claim-file move makes a PR DIRTY that merge-tree may resolve cleanly with the claimnotes driver installed. The rule above takes **either**, so neither case is lost.

**Control:** the study's absorbs-per-PR enumerator, before and after; DIRTY PRs still absorb, shown by the S2 example.

---

## K6 · R10-FLOW-RECORD-PITCH (instrument, S, Opus; code-owned workflow) — CONDITIONAL

**Where:** `.github/workflows/tests.yml`, job `record-autofix` (around L3833).
- It runs on push to main, schedule `17 2 * * *`, and dispatch. There is no job-level concurrency.
- Its automerge step reads ref `train-hold` with `HOLD_MAX_AGE_S=3600`: young means `skip-train-hold`, stale or unreadable means proceed. That arm is from #2519.
- `record_row.py --automerge-check`: exit 0 is clear, 3 is checks pending, 1 is refused. `plan_merges` re-plans any merge whose row is missing or still `**open**`.
- **Change:** a pitch bound in the same step. Skip when the newest `record:` merge on main is younger than 3600 s, **unless** the oldest unrowed merge is older than 7200 s. That keeps trap 15's truth condition: one row per merge, bounded staleness.

**Conditions**
- **Build it after R10-CI-LAYOUT-P1**: the CI-LAYOUT design's D-1 moves `record-autofix` off the Tests push run, and the brief does not name which PR does it, so ask the orchestrator.
- **Close it unbuilt if the owner adopts the merge queue (K9).** With a queue, heads never absorb main, so a record merge no longer stales anything.
- The zero-code part (records merge in the train's `--bot-prs` sweep) is K3, and lands first.

**Controls:** a harness for the step's shell, as #2519's `wf_harness.py` did. Cases: a young record merge skips, a stale backlog proceeds, the train-hold arm is unchanged, and the API returning 404 or 500 proceeds with a warning.

---

## K7 · R10-FLOW-RECHAIN (orchestrator roster burst, S, Opus): **decided by the seat; this group applies it**

**Correction to this study.** The first K7 proposal dropped 10 edges based on the owning-seam *names* in the architect notes. The R10-FLOW-RECHAIN decision seat (2026-10-21) checked all 15 coordinator.py edges against the code at main 5d433771a and roster 2c76c3128: it mapped functions with `ast`, mapped every prototype-patch hunk, and recomputed depth with `roster_lib.depth_of`. **Four of the ten drops were wrong:**
- **SCORES ← ADVISOR:** one sensor publishes both, at sensor.py L2679, and the two views are adjacent in `_insight_view`.
- **ARCH-SHAPES ← FREQ-DEFROST:** both edit `_freq_fold_blocked`.
- **HEAT-METER ← RATIO-ANCHOR:** HEAT-METER calls RATIO-ANCHOR's re-anchor, and they are config_flow.py chain positions 1 and 2.
- **HEAT-METER ← LEARNER-ETA:** LEARNER-ETA's status view reads the learner state HEAT-METER adds.

The drops also lost two real orderings, PARAMS-OWNER and ARCH-SHAPES after LIVESTATE. Reading a seam's name was not enough: the seat's code-level evidence governs.

**The ruling** (the seat's files `rechain-decision.md`, `rechain-drops.json` and `rechain-adds.json` are the record; land them in the tree with the burst):

| | edges |
|---|---|
| **drop (8)** | RATIO-ANCHOR ← NIGHT-FOLDS · INPUT-STALENESS ← RATIO-ANCHOR · CURRENCY ← INPUT-STALENESS · LOOP-CPU ← FREQ-DEFROST · CONFIG-NOTICES ← LIVESTATE · PARAMS-OWNER ← CONFIG-NOTICES · ARCH-SHAPES ← PARAMS-OWNER · LEARNER-ETA ← ARCH-SHAPES |
| **keep (7)** | SCORES ← ADVISOR · LIVESTATE ← SCORES · ARCH-SHAPES ← FREQ-DEFROST · HEAT-METER ← LEARNER-ETA · HEAT-METER ← INPUT-STALENESS · HEAT-METER ← RATIO-ANCHOR · COP-GATE ← HEAT-METER |
| **required, in the same burst (3)** | PARAMS-OWNER ← LIVESTATE · ARCH-SHAPES ← LIVESTATE · HEAT-METER ← PARAMS-OWNER, ARCH-SHAPES |
| **recommended, 0 depth each (4)** | LIVESTATE ← LOOP-CPU · LOOP-CPU ← NIGHT-FOLDS · PARAMS-OWNER ← NIGHT-FOLDS, RATIO-ANCHOR · ARCH-SHAPES ← INPUT-STALENESS |
| **this study's addition, 0 depth** | HEAT-METER ← R10-THERMAL-POWER-OPTION: they share flow_meter.py, config_flow.py and const.py, and THERMAL-POWER-OPTION has no edge today. HEAT-METER already waits at depth 5, so THERMAL-POWER-OPTION (depth 1) can start now at no cost. R10-LEARNER-DEFAULT also has no edges; check it the same way. |

**New critical path (8):** ADVISOR → SCORES → LIVESTATE → PARAMS-OWNER → HEAT-METER → COP-GATE → UX-HEALTH → ARCH-DOCS.
- `tools/simulate_rules.py` encodes exactly this.
- The projection moves from about 78 h (the wrong 10 drops) to **about 92 h**. The recommended and study edges cost 0 h.
- Every critical-path link except ADVISOR is L or XL. Their review should jump the queue: in a critical chain, a link's waiting time is round time.

**Why still no splitting.** The path's XL links (LIVESTATE, PARAMS-OWNER, HEAT-METER) could only get shorter by splitting if the next link depended on just one part. Nothing in the seat's evidence shows that. Splitting would add review, CI and record cost per part for an unproven gain. Re-open it only with a code-level dependency map like the seat's.

**Apply** (in the Phase-1 burst, SHADOW-PLAN §3.2):
- `roster_edit.py set-after` for the 8 drops plus all additions.
- The architect-note and brief text the decision file lists per group.

**Controls**
- `brief_lint` `TOTAL: 0`.
- `roster_lib` prints depth 8 and the path above.
- No edge outside coordinator.py changes, except the THERMAL-POWER-OPTION addition.

## K8 · R10-FLOW-ANDON (instrument, S, Sonnet fixer, Opus reviewer)

**Facts:** no loop writes a liveness signal readable off the host.
- `tick_loop.sh` prints `TICK-PASS <utc> relay=… tick=… out=…` and writes `$HPO_STATE_DIR/tick.txt` locally, every 300 s.
- `state_docs.py beat` pushes `handoff/audit-r<N>-plan` **only when main or the roster moved**.
- `wt_sync.sh` pushes `wip-sync/*` only when something is unpushed. Its 15-min cadence is a comment ("e.g."), not code.
- `daemonize.py` writes a local log header.

**Change**
- Each tick pass (after R10-TICK-RELAY-DECOUPLE, which restructures the same loop) force-pushes one ref, `heartbeat/orchestrator`. Its commit message is `TICK-PASS <utc> relay=<…> tick=<rc>`.
- The push uses the seat credential `wt_sync.sh` already uses, with `-f --no-verify`.
- A failed push prints `HEARTBEAT NOT PUSHED: <reason>` and never kills the loop.

**Watcher (owner side, no repo change):** a scheduled cloud task every 15 min runs `git ls-remote` plus a fetch of `heartbeat/orchestrator`, compares the committer date with now, and alerts the owner (push notification) when it is older than 20 min.

**Controls:** the loop's self-test shows a pass moves the ref in a bare-repo fixture and a refused push is printed; a stale fixture makes the watcher command alert and a fresh one does not.

**Seams:** R10-RCA-ORCH-CONTINUITY runs its cost test against this. R10-ORCH-MACHINERY's supervised beat later advances the same ref (carry added).

---

## K9 · R10-FLOW-MQ-PROBE (study, M, Opus; owner decides)

**The workflows are already queue-ready**
- `tests.yml` has `merge_group` throughout. `closure-scope` takes `BASE=${{ … pull_request.base.sha || … merge_group.base_sha }}` (around L2324).
- Around L341 it refuses a queue commit with no second parent ("the queue must merge with merge method MERGE"), which matches decision 0010's merge commits.
- `pr-contract.yml` derives the PR from the queue ref and asserts the API head equals `HEAD^2` (around L135–142).
- `governance.yml`'s `record` job is excluded from `merge_group` (around L991).
- Missing `merge_group`: `kernel-points`, `merge-main`, `pages`, the two `*-rerun` followers, `release`, `ci`.

**Probe**
- Follow the HANDOVER step-5 pattern: a throwaway branch plus a throwaway ruleset with the merge queue on (method merge) and the **same required contexts** as `main-protect-checks`. Read those from the ruleset endpoint; the tree stores no list.
- Run two arms: a passing PR and a deliberately failing one.
- For each required context, record whether it reported on `merge_group` and with what conclusion. Remember the HANDOVER trap: a context that never reports blocks every merge, in either direction.
- Also measure the queue's CI time against the 51-min planned cycle.

**Output:** a report to the owner, never a change to `main-protect-checks`. If the owner adopts the queue, R10-FLOW-RECORD-PITCH closes as not needed, and the train's CI wait and batch proof retire in favour of the queue.

---

## K10 · R10-FLOW-AUTOTRAIN (instrument, M, Opus) — mechanising the pitch

**Facts**
- **No queue builder exists.** The schema is only in `merge_train.py`'s docstring (L12–18): `[{pr, verdict (40-hex), verdict_comment (id), branch?, worktree?, issues?}]`. The orchestrator writes every queue by hand.
- **`train.sh`** (L4–59) always runs `merge_train.py batch` (L242). Flags: `--queue --repo --state-dir` (all required), `--mandate`, `--ignore-red` (repeatable), `--approval-carry`, `--bot-prs`, `--pre-flight`, `--free-holders`, `--skip-bad`, `--main-moved-tries`.
  - It refuses on a live pidfile (L206–214) and needs the seat venv (L221–227).
  - It owns no schedule: "the caller detaches and owns the schedule" (L27–28).
- **`app_approve.sh --carry <V> <H> [main]`** (L482–487) prints `CARRY: yes|no V -> H: why` (exit 0 or 1). Predicate `carry()` (L142–241):
  - V is an ancestor of H.
  - Every first-parent commit in V..H is either a main merge whose tree equals merge-tree's automatic result outside the driver files, or a `ci:`/bot commit touching only driver files or its own paths.
  - The branch diff against the merge base is identical at V and H.
- **`queue_pre_flight.py <queue.json>`** reads only. Per entry it checks: verdict hex, PR open, bot tip, carry, own delivery row, row not stale, worktree holder, policy gate, raise hold, findings gate. It prints `#N PASS|PARK|FAIL`; exit 0 only if every entry passes; an empty queue is exit 1.
- **`merge_fastpath.file_class`** sends `.github/`, claim, grader and unmeasured-budget files serial in the batch admit (`merge_train.py` L97–99).

**Change**
- Add `merge_train.py queue --from-open --out <file>`:
  - For each open PR whose title does not start `record:`, read the newest **confirmed** verdict (the `verdict/<pr>` bus ref tip's `VERDICT.md` first line; the posted comment's id comes from that ref's commit or one `gh api` read).
  - Admit the PR if the verdict is `merge <head>`, or `merge <V>` and `app_approve.sh --carry V head` prints `yes`.
  - Order oldest first; write the documented schema.
- In `tick_loop.sh` (after R10-TICK-RELAY-DECOUPLE restructures it), at the first pass after each full hour, when no train pidfile is live: build the queue. If it is non-empty, run `queue_pre_flight.py`, then `train.sh --queue … --bot-prs --approval-carry --pre-flight --mandate <cite> --ignore-red nightly-status --ignore-red delivery-status`, detached (`daemonize.py`).
  - nudge.md's `--ignore-red` replaces the default list, so name both.

**Controls**
- Fixture set: verdicted head, carried head, carry-refused head, blocked verdict, budget-file PR, `record:` PR. The queue holds exactly the first two; the budget PR goes serial; the record PR is left to `--bot-prs`.
- An empty queue starts nothing. A live pidfile starts nothing.
- One mutant per admission rule.
- The first live pitch runs with the orchestrator watching, and its log is quoted in the PR.

## K11 · R10-FLOW-POSTMERGE (instrument, S, Sonnet fixer, Opus reviewer) — mechanising nudge step 12

**Facts**
- `merge_pr.sh` merges with `gh pr merge --merge --match-head-commit` (L172), prints `merged <sha>` and `issue <n> <state>` (L173–174), then runs `worktree_gc.sh` and `git pull --ff-only` (L175).
- `merge_train.py` reads closingIssuesReferences (L1274–1277) and runs `worktree_gc` (L1278–1279).
- `proof_watch.py` delegates to `merge_pr.sh` (L289–300).
- **None of them** posts the #201 line, sets the roster stage, or runs `state_docs.py`.
- `gh_comment.py post --repo O/R --issue N --body-file F` refuses a body file in a shared root (`/tmp`, `TMPDIR`, `HOME`, scratchpad, `claude-<n>`), so write it under the state dir.
  - It reads back byte-identical (`READBACK … identical=True`), exits 2 on a mismatch or refusal, and supports `--dry-run`.

**Change:** one post-merge function, shared by both merge paths, run after the `merged <sha>` line:
1. `gh_comment.py post` of a fixed template: `merged #N at <sha>; group <G>; closes <issues read from the merge>; Leaves #201 open`.
2. The roster stage. Prefer R10-ROSTER-OPS's roster-sync (`state_docs.py beat --apply`) when it has landed; until then `roster_edit.py set-stage <G> done --at-sha <sha>`.
3. `state_docs.py` with its push flag.

Each failure prints `OWED post-merge <step>: <why>` and the script exits non-zero **after** the merge line. It never retries the merge and never reverts.

**Controls:** a `--dry-run` fixture prints the exact comment and commands; a refused comment yields `OWED`; deleting each step fails a named self-test arm. `governance.yml` already runs the seat self-tests: check that `selftest_wiring.py --check` stays green.

## K12 · R10-FLOW-BODY-ONLY (instrument, S, Opus): R4 made true in the tool

**Facts at main**
- **`update_pr.sh`** (usage `update_pr.sh <branch> <code-sha|-> <body-file> [issues...]`) runs:
  1. a flock lock
  2. derives the topic
  3. fetches the handoff code head (when the code sha is not `-`)
  4. re-adds the worktree at the PR branch
  5. merges the code head
  6. **merges `origin/main` unconditionally** (L70; no flag skips it)
  7. ensures the delivery row (a commit when missing)
  8. checks the author
  9. prefixes the body
  10. runs `app_push.sh`, which runs prepr, mints, pushes, then PATCHes the body and reads it back
- **`app_push.sh`:** flags `--dry-run`, `--recarry`, `--branch-only`; **no body-only mode**. A run whose HEAD equals the branch tip pushes nothing new and still PATCHes the body. That is inferred from the code, not run.
- **`cloud_relay.sh`'s handoff arm** (around L179–235) skips any topic whose `handoff/<topic>` tip the PR head already contains (L196). **A body-only move is therefore never propagated by the relay.** The orchestrator runs `update_pr.sh` by hand, which merges main.
- **`pr-contract.yml`** triggers on `edited` (L23) and reads the body from the API at run time, so a body PATCH re-gates without a push.

**Observed 2026-10-21:** body fixes moved clean heads on #2513, #2544, #2548, #2529 and #2549. The orchestrator carried their verdicts with `app_approve.sh --carry`.

**Change**
- (a) L70 becomes conditional: merge only when the PR is DIRTY or `git merge-tree --write-tree origin/main HEAD` reports a conflict.
- (b) Body-only mode: code sha `-`, and the PR head already contains the handoff tip. It makes no worktree commit, and no row commit when the row exists. It runs the body contract at the unchanged head, then the body PATCH with nothing pushed. It asserts that the head sha is unchanged, and refuses otherwise.
- (c) The relay's handoff arm calls body-only when the `handoff-body/<topic>` tip changed and the code tip is already contained.

**Controls**
- With main ahead and a clean merge-tree, the head sha is identical before and after.
- A DIRTY fixture still absorbs.
- Body-only on a moved head refuses.
- The relay calls body-only exactly once per body move.
- One mutant per rule.

**Sequence:** after R10-UPDATE-PR-SIGNALS (#2524), and with #2567 (row-only update) and #2560 (update_pr lock), which edit the same script.

## K13 · R10-FLOW-ROSTER-FREEZE (instrument, S, Opus)

**Facts**
- Roster edits push to `handoff/audit-r10-roster`, and the relay carries them into the open roster PR. On 2026-10-21, #2559 lost five reviewer rounds to `head-moved` and `body-stale`.
- `carry_audit.py check` resolves destinations against main's roster only. A carry to a group that exists only on the handoff roster fails as `BAD-DEST` until the roster PR merges. That blocked #2529, #2547 and #2561.
- `carry_audit.py` already accepts a repeatable `--roster-ref` global option. `pr-contract.yml` (around L384–386) calls `check --body` without one.

**Change**
- (a) The relay does not move an open roster PR's head while a review of it is in flight: the fix-head freeze, applied to the roster PR.
- (b) `carry_audit.py` also reads the round's handoff roster (`roster_lib.round_ref`) as a destination source, and names which ref resolved each carry.

`carry_audit.py` is code-owned, so it needs tvofi's review under the mandate.

**Controls**
- A handoff-only destination passes and names its ref; a destination on neither ref fails.
- With a review in flight, the roster head is unchanged, and it moves once the verdict posts.
- Mutants for both arms.

**Until this lands:** freeze roster pushes by hand while #2559 is under review (SHADOW-PLAN §3.2 Phase 1a).

## K14 · R10-FLOW-BODY-PATCH (instrument, S, Sonnet fixer, Opus reviewer): expedite

**Gap** (orchestrator, 2026-10-21): until R10-FLOW-BODY-ONLY lands, the plan said "PATCH the body without `update_pr.sh`, or carry the verdict". No PATCH tool exists, and carrying a verdict does not repair a body that `pr-contract` or `carry_audit` refuses. The open case is #2560's 111→113 figure.

**Facts**
- `app_push.sh` (flags `--dry-run`, `--recarry`, `--branch-only`) runs prepr, then checks that HEAD equals the branch tip and the tree is clean, then the ref-privacy guard, then mints the App token, pushes, and PATCHes the body of an open PR with a read-back.
- A run from a clean worktree at the PR's exact head, with a corrected body, pushes nothing new and still PATCHes. That is **read from the code, not run**.
- `pr-contract.yml` re-runs on `edited` and reads the body from the API.

**Interim, today:**
1. Check out a clean worktree at the PR's exact head.
2. Write the corrected body.
3. Run `tools/pr/app_push.sh … --dry-run`, then the same command live.
4. Confirm the head sha is unchanged and the body read back is identical.
5. If the head moves, stop and report it: the inference was wrong.

**Change**
- A seat instrument taking `<pr> <expected-head-sha> <body-file>`:
  1. refuse unless the live head equals the expected sha;
  2. run the body contract offline (prepr's `policy_lint.mjs --pr-body … --head <sha>` arm and `carry_audit.py check --body`);
  3. PATCH as hpo-author, through `app_push.sh`'s mint, factored out rather than copied;
  4. read the body back byte-identical;
  5. re-read the head.
- Wire its self-test into `governance.yml`'s instrument-self-tests job; `selftest_wiring.py` requires that for a new seat file.

**Controls**
- A moved head refuses before any write.
- A refused body is never sent.
- `--dry-run` prints the request.
- Mutants for the head check, the contract arm and the read-back.

## K15 · R10-FLOW-MAIN-GATE (instrument, S, Opus): expedite

**Observed** (orchestrator, main `e7c66485`): 30 checks concluded and 7 in flight. The only failures were `record` and `record-autofix`, red because the record beat was owed. Yet the `--overlap` gate logged "main is not green, revert it first". Acting on it would have been wrong.

**Change**
- Judge main on the **latest run of each context**.
- Queued or in-progress runs mean **wait**, never red.
- Count only the contexts the ruleset `main-protect-checks` requires, read live (nudge step 4). Never count `record`, `record-autofix`, `nightly-status` or `delivery-status`.
- An unreadable ruleset is a refusal, never green.
- **One owner for "is main red":** the open #2570 fixes the same misreading in the tick's MAIN section (it "judged every non-green latest lane red"). Share its classifier; do not write a second. Sequence after #2570.

**Controls:** the e7c66485 shape reads wait or green; a failed required context reads red; mutants for each arm.

## K16 · R10-FLOW-DISPATCH (instrument, S, Sonnet fixer, Opus reviewer), plus an owner action

**Observed:** each cloud seat costs a rendered payload plus two trigger bodies pasted whole. The renderer needs environment, model and repo flags, and refuses host paths.

**Repo half (this group):** `cloud_dispatch.py` takes role, group and model. It derives the rest from the roster and its known seat environment, writes the rendered brief to a ref the seat fetches, and prints one short line, the ref name.

**Owner half, outside the repo:** one standing trigger per seat role, whose prompt fetches the brief ref named in its fire text. A dispatch is then one fire call carrying one line. Whether the trigger tool can take a file is the harness's call, not the designer's.

**Controls:** byte-identical payload against today's path; a host path still refuses; the printed line round-trips to the brief.

## K17 · Alignment with R10-ORCH-MACHINERY's approved design (carry on that group; seam notes on nine flow groups)

**The design**, read at `handoff/orch-machinery` 09174d94e (DESIGN.md) with review round 3 at 0bd5d12f0 (APPROVE), has three parts:
- **`beatd.py`,** a supervised beat. Its tracked job table `beatd.jobs.json` has **seven jobs**: `tick` 300/900 s, `relay-probe`, `handoff` 120/3600 s, `state-docs`, `sync`, `plan-page`, `seats`.
  - It writes a local journal (`PASS … outcome=` lines, plus a 60-s `RUNNING` line) and `beatd status`.
  - It retires the three hand-launched daemons in one switch: `tick_loop.sh` (M01), the `state_docs.py` beat (M06) and the `wt_sync.sh` loop (M29).
  - It specifies **no train job, no owner alerting and no off-host liveness signal**.
- **`ledger.py`.** Its kinds are `handoff-no-pr`, `handoff-update`, `probe-ref`, `stage-mismatch`, `absorb-edge-missing`, `record-owed`, `reviewer-fire`, `verdict-unposted` and `train-stop`.
  - `open_pr.sh` and `update_pr.sh` write dispositions when they apply a handoff.
  - **An OWED shape with no ledger kind is refused.**
- **`plan_page.py`,** sharing one `plan_model()` with `plan_table.py`.

**Collisions, and how this plan resolves them:**

| flow group | collides with | resolution (seam note on the group; binding carry on R10-ORCH-MACHINERY) |
|---|---|---|
| FLOW-ANDON | `tick_loop.sh` is retired by the beat; the design has no off-host signal | heartbeat as a standalone `--once` job script. The beat gains a `heartbeat` job (300/60 s) whose ref message carries `beatd status`, so a timed-out job alerts too, not only a dead host |
| FLOW-AUTOTRAIN | no train job in the design | pitch as a standalone `--once` job script. The beat gains a `pitch` job that only launches a detached train and reads the `train-stop` obligation |
| FLOW-POSTMERGE | free OWED lines are refused by the ledger | new event kind `postmerge-owed`: producer the after-merge step, closer its later success or an orchestrator disposition |
| FLOW-BODY-ONLY | the relay handoff arm becomes the `handoff` job | the body-only path is a callable function. The job writes a disposition for the `handoff-body` ref it applies |
| FLOW-ROSTER-FREEZE | the design has no freeze state; it has `workers.json` seat liveness | the predicate reads a live reviewer from `workers.json`. The `handoff` job **generalises it to every head**, making `fixer.md`'s freeze mechanical |
| FLOW-DISPATCH | M12 `bus.sh dispatch`, the `reviewer-fire` close, `workers.json` | dispatch through `bus.sh dispatch` and add the seat to `workers.json`. This also supplies the dispatch-reason state review N11-R found missing |
| FLOW-WIP | `handoff-no-pr` lives in the ledger fold | count stranded handoffs from the fold once `ledger.py` lands |
| FLOW-MAIN-GATE | the design has no is-main-red rule | one classifier (#2570's) for the train, the tick and the sweep |
| FLOW-BOARD | part (3) and R10-PLAN-ARTIFACT (#2558) both build the plan page | one model. If #2558 merges first, part (3) extracts `plan_model()` from it and keeps the UNAVAILABLE page and the five mutation fixtures; the flow board is a section of that page |

**Also:** inventory row M43 is stale. `pr_cap.py` has gated dispatch, not opening, since #2525.

**Owner decisions this needs:** the two job rows and the ledger kind amend an approved design; so does part (3)'s scope cut.

**Sequencing:** R10-ORCH-MACHINERY stays after R10-ROSTER-OPS and R10-CI-LAYOUT (design B5: each instrument lands with its wiring). The flow groups that land earlier are written as job scripts and functions so that the beat hosts them unchanged.

## Guardrail baselines (for FUTURE-STATE §9), measured 2026-10-21 14:50Z from the `review/*` bus refs

**Real-catch classes:**
- harness
- class-open
- test-vacuous / vacuous-test / vacuous-check
- mutation-vacuous / mutant-survives / mutation-survivor / mutation-untriaged / mutation
- architecture-unsound
- metric-gamed
- defect
- product-tradeoff-regression
- policy-regression
- figures-false

Every other blocked class is bookkeeping.

| window | reviewed PRs | real-catch blocks per PR | bookkeeping blocks per PR |
|---|---|---|---|
| round-10 study window (10-15 12:37Z → 10-21 11:00Z) | 112 | 0.52 | 0.58 |
| last 48 h before adoption | 47 | **0.15** | 0.64 |
| since 13:00Z 10-21 (the orchestrator's sample) | 11 | 0.36 | 0.45 |

The real-catch rate fell from 0.52 to 0.15 **before any flow change merged**. A guardrail on "a fall" therefore needs the pre-change baseline (0.15/PR over 47 PRs), a minimum sample and a defined trigger (FUTURE-STATE §9). Otherwise it fires on noise, or on a fall that predates the plan.

**Enumerator:** for each `review/<pr>` ref, take the commit subjects (`verdict: #N Fix review: merge|blocked <40hex> <class>: …`) by committer time in the window. Count PRs, merges, and blocked subjects by class.

## Fly-in intake (no group: operating rule, carried by K3)

- **Classify at arrival.** Expedite, or fly-in (size S), or not a fly-in (anything larger goes to the ready queue and is ranked normally).
- **Register before dispatch:** `roster_edit.py append-group <file>` with `group: "R10-FLY-<topic>"`, the existing kind (`instrument`, `defect` and so on) and `after: []`. The board counts it, the cap sees it, and the record is complete (`delivery-status-tracking.md` item 4).
- **Lane F, WIP 2**, target lead 4 h. A burst beyond 2 waits in arrival order. An expedite never waits.
- **Merge in the pitch** like any other PR. Its record row rides the same record car.

**Capacity basis:** 34 fly-ins in 145 h is 0.23 per hour, with a peak of 10 in one day. Lane F at 2 × (1 / 4 h) gives 0.5 per hour, about 2× the mean.
