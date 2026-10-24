# Routing audit 1 (round 10, 2026-10-24)

Roster: origin/handoff/audit-r10-roster @ d3c2a27c7 (dev/programme/rosters/wave-r10-groups.json, 176 groups: 104 done, 1 absorbed, 71 live). Carry files: dev/programme/carries/*.json at the worktree (9 files; the roster branch holds 8, lacking carry-2674.json). Open issues: 53, cached once (`gh issue list --state open --limit 500 --json number,title,labels`), 52 after excluding #201. No writes to GitHub or the roster.

## Summary

| invariant | violations |
|---|---|
| 1 carries routed | 40 distinct (PR, destination) pairs bad (70 items) + 25 unrouted items in 13 PRs; 7 carry files point at closed issues |
| 2 groups linked | 32 of 71 live groups |
| 3 issues covered | 14 of 52 open issues |

Caveat for 1: `carry_audit` flags any destination group that is `done`, and cannot tell a carry that was consumed before the group finished from one never implemented. The 70 are candidates, not confirmed lost carries; each needs a check that the group's merged PR implemented it. Dest groups are done groups, so a clean answer is often 'implemented'. The 25 unrouted are mostly review `## Evidence` prose the item grammar reads as findings.

## Invariant 1: carries routed

Commands:
```
python3 -I tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster sweep --last 150   # 150 merged PRs, bodies + review comments
python3 tools/audit/seat/orchestrator_tick.py --only CARRY --roster-ref origin/handoff/audit-r10-roster   # 20-PR window, plus --issues
```
Sweep result: `CARRY-AUDIT: 423 finding item(s): 328 routed, 25 unrouted, 70 bad destination(s)`. Group `carry` lists (all 176 groups) were read directly: 71 live groups hold carries as destinations; the 71 done/absorbed groups' carry lists are consumed by definition and are not counted.

### 1a. Bad destination, source PR -> destination (stage)

| source PR | destination | dest stage / reason | items |
|---|---|---|---|
| #2675 | #2674 | no live group and no carry file on the roster branch (carry-2674.json exists on main only) | 1 |
| #2632 | R10-FLY-SUITE-ENV-FLAKES | done | 2 |
| #2632 | R10-LIVESTATE | done | 1 |
| #2639 | R10-FLY-GH-READ-RETRY | done | 3 |
| #2643 | R10-FLY-NO-FOOTERS | done | 2 |
| #2633 | R10-FLOW-ARCH-PLANNER | done | 1 |
| #2629 | R10-RECORD-API-BUDGET | done | 1 |
| #2628 | R10-FLOW-ARCH-PLANNER | done | 1 |
| #2622 | R10-POLICY-LINT-FAMILY | done | 1 |
| #2612 | R10-BRIEFS-FOLD | done | 3 |
| #2605 | R10-NIGHTLY-PYSPY-RETRY | done | 1 |
| #2606 | R10-RECORD-API-BUDGET | done | 3 |
| #2606 | R10-FLY-GH-READ-RETRY | done | 1 |
| #2589 | R10-FLY-GH-READ-RETRY | done | 1 |
| #2609 | R10-PLAN-ARTIFACT | done | 1 |
| #2585 | R10-REPLAY-LANE | done | 1 |
| #2585 | R10-RCA-FRICTION | done | 2 |
| #2577 | R10-FLOW-MAIN-GATE | done | 2 |
| #2558 | R10-PLAN-ARTIFACT | done | 1 |
| #2582 | R10-FLOW-ANDON | done | 1 |
| #2545 | R10-RCA-HANDOFF-SLIP | done | 2 |
| #2595 | R10-POLICY-LINT-FAMILY | done | 2 |
| #2586 | R10-RCA-ORCH-CONTINUITY | done | 5 |
| #2563 | R10-BRIEFS-FOLD | done | 1 |
| #2563 | R10-NIGHT-FOLDS | done | 2 |
| #2561 | R10-BRIEFS-FOLD | done | 1 |
| #2561 | R10-POLICY-LINT-FAMILY | done | 1 |
| #2557 | R10-RCA-HANDOFF-SLIP | done | 1 |
| #2572 | R10-LIVESTATE | done | 1 |
| #2572 | #2257 | owner is done group R10-ADVISOR; no live group or carry file | 5 |
| #2572 | R10-ADVISOR | done | 3 |
| #2566 | R10-HANDOVER-REFRESH | done | 2 |
| #2529 | R10-CI-LAYOUT | done | 8 |
| #2529 | R10-CI-LAYOUT-P1 | done | 1 |
| #2521 | R10-BRIEFS-FOLD | done | 3 |
| #2521 | R10-CURRENCY | done | 1 |
| #2548 | R10-REPLAY-LANE | done | 1 |
| #2559 | R10-ROSTER-OPS | done | 2 |
| #2559 | R10-BRIEFS-FOLD | done | 1 |
| #2513 | R10-ROSTER-OPS | done | 2 |

Carry text (first 100 chars) is not printed by `carry_audit` for BAD-DEST rows, only the item id; read it with `carry_audit.py pr <N>`. Items are in /private/tmp/claude-501/s/sweep.out.

### 1b. Unrouted finding items (no Carry: marker)

| source | item | text (100 chars) |
|---|---|---|
| #2683 review 6379079217 | 57e267d2 | The live PR body is the same text as handoff-body ref `39cb37f13`. Both forward-carry items name the |
| #2683 review 6379079217 | c571d890 | - `node tools/policy/policy_lint.mjs --pr-body … --head 07b83e9b2 --base d05a44c63 --paths-file … -- |
| #2683 review 6379079217 | 14f2edf3 | - `node tools/policy/figure_lint.mjs` printed `FIGURES: 17 resolved, 13 not verified, 0 refused`, rc |
| #2683 review 6379079217 | 7ca5af57 | (evidence/policy_lint-body.out)' |
| #2673 review 6375740038 | 6b866e0b | Forward-carries checked on `origin/handoff/audit-r10-roster` a29c7ebfb: the body's five sit at R10-C |
| #2633 review 6354675958 | 24441f60 | - CI on the head (ev/check_runs.tsv, every workflow concluded): - `budget-raise-gate` is red twice.  |
| #2628 review 6352499018 | 0d645b16 | - Cuts the body says are restated elsewhere, each checked: - Step 8's four-prepr train condition is  |
| #2605 review 6338592560 | 04edda95 | - The body\'s first claim is "`py-spy dump --nonblocking` is cut at `PY_SPY_TIMEOUT_S` = 5 s instead |
| #2605 review 6340610047 | 98c7c2ed | - Check 4, carry: `carry_audit.py check --body` at this head prints `3 finding item(s): 3 routed, 0  |
| #2577 review 6331521421 | fa81793d | - Round-4 blocks, each cleared at this head: - Class-open, five dropped flags: cleared. The finder's |
| #2554 review 6331184193 | 64e8b432 | - **Body figures re-derived at this head (step 8).** Python was `/opt/hpo/venv-ci` 3.14.7 (ev/selfte |
| #2545 review 6331182210 | 4f48ff38 | - The record against `defect-root-cause.md` and `root-cause.md`: - The named cause is §1, three caus |
| #2545 review 6331182210 | 6c98ab6e | - Red checks, read from the check-runs API per commit, `repos/tvofi/heatpump_optimizer/commits/<sha> |
| #2595 review 6332581437 | ecd69bc2 | - "wc -c ... 17925 at the head": measured 17924 at a8f339d9a and at the head (token figure 4481 hold |
| #2595 review 6332581437 | d7ca3d75 | - Null control "Only orchestrator.md differs (git diff --stat origin/main...HEAD)": at this head del |
| #2563 review 6317463517 | b29dfdfd | Round: first review by this seat.' |
| #2563 review 6317463517 | f2a90213 | bus-nonce: 4781a1280f18f8b3240d780b7dc421bf' |
| #2572 review 6322344533 | c2b6a1af | - **MX1 (reviewer\'s mutant) survives.** Deleting `"price_tiles": price_tiles.book(self),` from `_sc |
| #2572 review 6322344533 | 4b51e0e7 | - **Step 9: there is no committed finder harness** for owner items 6, 7 and 8. `dev/audit/harnesses/ |
| #2572 review 6322344533 | 5f30f170 | - **Null control (carry 1).** The held figure reads +54.4 against +59.4 realised per delivered degre |
| #2572 review 6322344533 | 4468b8a1 | - **Mixing.** The 30-day mean mixes days priced at different schedules (after a target change, or an |
| #2572 review 6322344533 | bfe93d15 | - **Forward-carry (step 10).** The R10-UX-HEALTH and R10-LIVESTATE carries are written only in the P |
| #2566 review 6327140155 | e1ab9994 | - The only red is `nightly-status` (check-run 119479409582, `ev/nightly_status_head.txt`): `NIGHTLY  |
| #2549 review 6319952656 | 01ce8b81 | Residual, not blocking: the detached holder is a child of the loop's process group, so a group-wide  |
| #2549 review 6319965396 | 01ce8b81 | Residual, not blocking: the detached holder is a child of the loop's process group, so a group-wide  |

### 1c. Carry files whose issue is closed (destination is a stage or seat with no roster group)

| file | issue state | destination stage (100 chars) |
|---|---|---|
| carry-1645.json | closed | the round-9 I5 class barrier (tests/doc_claims.py arms reading facts from code) |
| carry-1774.json | closed | R9-EG-A4 |
| carry-1795.json | closed | R9-UX-5, or any later seat that adds lines to the chart's hover tooltip (tooltipHtml, idleWhyHtml) o |
| carry-1922.json | closed | R9-RO-9 |
| carry-201.json | open | any later seat that stamps a release (tools/release/stamp.py, the deploy-key tag push of dev/governa |
| carry-2065.json | closed | live-7b, the power-clamp seat's observed-draw consumer after #2065 |
| carry-2066.json | closed | live-3, the learners fix after #2066 (extra draw is not low COP) |
| carry-2075.json | closed | R9-RO-13, the mandate-gated batch-policy group |
| carry-2674.json | open | #2674, probing the seven per-cycle writers that may run inside the first refresh before their store  |

No carry text in the carry files is in a group `carry` list. Whether each file's carries are implemented was not determined; `brief_lint` and the roster do not track it.

## Invariant 2: groups linked

Command: python over the roster JSON (no instrument reads this): live = stage not in done/rca-done/absorbed; violation = empty `issues` and `fixes`. Count: 71 live, 32 violations (all lane-process groups R10-FLOW-*, R10-FLY-*, and others; none names an open issue in its brief, findings or carry).

| group | stage |
|---|---|
| R10-FLOW-BOARD | not-started |
| R10-FLOW-DESIGN-STAGES | not-started |
| R10-FLOW-JIDOKA | in-progress |
| R10-FLOW-MQ-PROBE | not-started |
| R10-FLOW-POSTMERGE | not-started |
| R10-FLOW-RECORD-PITCH | not-started |
| R10-FLOW-ROSTER-FREEZE | not-started |
| R10-FLOW-WIP | not-started |
| R10-FLOW-AUTOTRAIN | in-progress |
| R10-FLOW-BODY-ONLY | not-started |
| R10-FLY-OPENPR-ATOMIC | not-started |
| R10-FLY-ROW-HEAD-CARRY | not-started |
| R10-FLOW-AUDIT-PLAN | not-started |
| R10-FLY-RELAY-REVIEW-FF | carries-open |
| R10-FLY-CAP-LINE | not-started |
| R10-FLY-CARRY-DISPOSITION | not-started |
| R10-FLY-ORPHANS-REWRITTEN | not-started |
| R10-FLY-CARRY-DOC-CONTEXT | not-started |
| R10-FLY-DEPGRAPH-STALE | in-progress |
| R10-FLOW-TOOLKIT-MODEL | not-started |
| R10-ROUND-PLAYBOOK | not-started |
| R10-FLY-STAMP-CHECK-NOTES | not-started |
| R10-FLY-MANDATE-REVOKE-GUARD | not-started |
| R10-TRAIN-OVERLAP-GRADE | queued |
| R10-NIGHTLY-HB-RESPAWN | queued |
| R10-FLY-PRUNE-REFS | not-started |
| R10-STRUCTURE-ALIAS | in-progress |
| R10-ORCH-REVIEW-PACKET | not-started |
| R10-POLICY-ROLE-PACK | not-started |
| R10-CLOSEOUT-CLEANUP | not-started |
| R10-IMMERSION-LATCH | queued |
| R10-DIAG-REDACT | not-started |

#201 is wired into no group.

## Invariant 3: issues covered

Command: python over the cached issues.json against live groups' issues+fixes and dev/programme/carries/*.json (worktree and roster branch); `carry_audit sweep --issues` (also run via `orchestrator_tick --only CARRY`) is the existing equivalent. Count: 53 open, 52 excluding #201, 14 uncovered. All 14 are listed only by DONE groups: the group finished but the issue is still open (close it, or reopen the group).

| issue | title | done group(s) listing it |
|---|---|---|
| #2235 | [R10-N-structure-blind] A structural ratchet or dead-code metric measures a name or regex proxy inst | R10-ARCHSCORE-COVERAGE, R10-STRUCTURE-BLIND, R10-RCA-STRUCTURE-BLIND (done, done, done) |
| #2248 | [R10-N-restore-race] A restore applies persisted state after an await during which a writer changed  | R10-LIVESTATE (done) |
| #2250 | [R10-N-solve-recompute] The solve recomputes interpreter-bound work per iterate or per row that is i | R10-SOLVER (done) |
| #2252 | [R10-TRUST-RELATIVE] The learner trust region is fixed in multiplier units; make it relative to the  | R10-TRUST-RELATIVE (done) |
| #2257 | [R10-ADVISOR] Advisor: day-to-day swing, Open settings not deep-linked, and a self-contradicting -26 | R10-ADVISOR (done) |
| #2258 | [R10-SCORES] Plan scores read 0 for no evidence, the house score misreads a two-zone house, and scor | R10-SCORES (done) |
| #2259 | [R10-ARCHSCORE-COVERAGE] archscore coverage: layering, card script, dict-literal clones, hub aliases | R10-ARCHSCORE-COVERAGE (done) |
| #2265 | [R10-TICK-DRIVERS] Round drivers trust large agent replies and a hand-kept schema; land the scratch- | R10-TICK-DRIVERS (done) |
| #2269 | [R10-BRIEFS-FOLD] Fold arch-score into D7 (M7/M8) and land the round's owed dimension-brief edits | R10-BRIEFS-FOLD (done) |
| #2271 | [R10-DIAG-REPLAY] Download diagnostics: fill the bundle's replay half through the export's allowlist | R10-DIAG-REPLAY, R10-REPLAY-LANE (done, done) |
| #2272 | [R10-REPLAY-LANE] Land the replay lane: a real recorded day as a fixture, gated nightly | R10-REPLAY-LANE, R10-REPLAY-CAP (done, done) |
| #2298 | [R10-D6-web] docs/index.html declares a wrong image height (layout shift) | R10-I5-DOCS (done) |
| #2410 | [policy] recurring friction: mutation (family) | R10-POLICY-LINT-FAMILY (done) |
| #2496 | [R10-ROSTER-OPS] roster_edit.py gains set-after <group> <G1,...|-> and drop-carry <group> <index|--m | R10-ROSTER-OPS (done) |

The tick (run against main) lists 11 unowned issues, among them #2660; on the roster branch #2660 is covered, so it is not counted here. The difference is roster-branch versus main drift.

## Where an instrument already checks, and the gap

| invariant | instrument | what it covers | gap |
|---|---|---|---|
| 1 | `carry_audit.py check/pr/sweep`; tick `--only CARRY` (20-PR window, capped output) | each finding item in a PR body/review names a `Carry:` marker; dest group exists and is not done; `#N` owned and open | cannot tell a consumed carry (group done because it implemented it) from a stranded one: 70 candidates; no check that carry text was implemented; prose/evidence items false-positive (25); window is 20 PRs, not all merges; resolves carry files from the roster ref, so a carry file only on main reads as 'no owner' (#2674); does not read carries in the carry files or group `carry` lists |
| 1 | `brief_lint.mjs` (checkCarryShape, rosterIssues) | carry file shape; refuses a carry file for an issue with a live group | does not check that a carry file's issue is open or that its carries are routed to a live seat; 7 of 9 files are for closed issues |
| 2 | none | -- | `brief_lint` roster-shape checks presence and type of `brief` and `resume` only; an empty `issues`+`fixes` on a live group passes |
| 3 | `carry_audit sweep --issues`; tick CARRY | open issue not in a live group `issues`/`fixes` or a carry file (the same definition used here) | needs `gh` and is not a CI check; run on main's roster by default, so drifts from the roster branch; owner-by-done-group counts as unowned (correct) but carries no auto-disposition (close or reopen) |
