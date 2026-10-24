# Routing verify 1 (independent verifier, 2026-10-24)

Inputs: routing-decisions-1.md, routing-ops-1.txt, routing-issues-1/, groups/. Read at origin/main 9586fce08 and origin/handoff/audit-r10-roster db3e513ec (one commit past the decisions' d3c2a27c7: an unrelated carry on R10-FLY-CLOUD-SETUP-TOOLCHAIN). Issue and PR JSON fetched once into the seat scratchpad; item texts read from the decision seat's raw `gh` cache (routing2/items.json), not from its verdicts. Nothing written to GitHub, the roster or any branch.

Totals: 1. 4 CONFIRM, 3 REFUTE. 2. 27/27 IMPLEMENTED CONFIRM (2 with corrected evidence); 10/10 sampled NO-OBLIGATION CONFIRM. 3. 15 CONFIRM, 6 REFUTE of the 21 append-carry ops (the ops file holds 21: 20 in section 2 plus the capline absorb, not 20 as briefed); plus 1 REFUTE of an append-group (R10-RESTORE-RACE-PROBE). 4. 19/19 bodies CONFIRM on duplicates, scope and titles. 5. Design REFUTE (revise before dispatch).

General defect in the ops file: `roster_edit.py` requires `--worktree` (roster_edit.py:677, `required=True`), and without `--push` each op leaves an unpushed commit in that worktree, which the next op refuses. Every op line needs `--worktree DIR --push` before it runs.

## 1. DELIVERED issues

| issue | verdict | evidence |
|---|---|---|
| #2250 | CONFIRM | Only finding D9-s1-01 (fused sse/grad). #2612 (008ad15, ancestor of main) section 1 routes all four L-BFGS-B sites through `_lbfgsb_run` with the fused batch `fun`, `jac=True`; plan bit-identical. The issue's RCA line owes nothing (`fold_ledger.py check` not OWED). |
| #2252 | CONFIRM | Ask: relative trust region. #2435 (05c39d3): `reach = current * trust_region` (thermal_model.py:1987 on main). The group's carry "re-measure on the owner's bundle stores" is answered in the body (owner's two stores, paired). |
| #2258 | REFUTE | Item 2 asks "Measure τ on tvofi's bundle stores" and names (c) the uncalibrated 20/80 h band. #2647's body: "The 20-100 h band is unchanged"; the bundle measurement is "Blocked, not designed around" and carried to R10-PARAMS-OWNER (its carries 5 and 6). PARAMS-OWNER is not-started and lists #2232, #2249 only, so closing #2258 leaves an owner-reported ask with no issue. Instead: `wire-issue R10-PARAMS-OWNER 2258`, and keep it open. |
| #2265 | REFUTE | Items e, g, h, i landed in #2390 (a96f4be). But the orchestrator's record comment on #2265 says to keep it open until O14 (tick-drivers-2: L03, L04, L05, P02, P55, P57, L12 b/c, `--carry-sweep`) merges, or to record which items are dropped. No O14 merge is on main (`git log --grep` and `git grep '\bO14\b'` find nothing), no roster group holds O14, and the decision does not mention the comment. Only `--carry-sweep` exists (carry_audit.py:572). Close it only after a recorded O14 disposition. |
| #2298 | CONFIRM | docs/index.html:302 declares `height="792"`; tests/doc_claims.py:2985 `check_image_dimensions` (called at :3367) compares every .html/.md `<img>` with the PNG IHDR. |
| #2410 | REFUTE | #2669 changed the keying rule, but its own body says "at head, 7 = #2297, #2360, #2391, #2400, #2376, #2444 and #2390, none of which any member files". That is still over the threshold of 3. The live window was "not measured", and "This change does not close it". The bot's below-threshold comment (2026-10-22T16:31Z) predates the 2026-10-23 merge, and the issue body still reads family 5 on v7.0.4. The mutation friction is unresolved, so the disposition belongs with R10-RCA-FRICTION-RESIDUE or a live mutation group, not a close. |
| #2496 | CONFIRM | `set-after` and `drop-carry` landed in #2513 (929275e). The tvofi roster-sync half (`--apply` dry-run default, protected `deferred`/`refused`, a `Carry:` to a done group refused) landed in #2554 (16a8240f1, `446dc318c`; roster_sync.py:95,354,479). The decision cites only #2513, so the close comment should name both PRs. Residuals 3b97e1aa and 7f85b089 go to R10-ORCH-ROSTER-SCHEMA (live). |

## 2. IMPLEMENTED (27) and sampled NO-OBLIGATION (10)

| item | verdict | evidence (origin/main) |
|---|---|---|
| 9160e669 | CONFIRM | coordinator.py:9708-9709 `if self._away_state is written:` after the await; both controls named in tests/features.py:62587, :62612 |
| 5afde258 | CONFIRM | M0 governance.yml:1259,1368; M1 `--window-cache` governance.yml:1295-1361; M2 `concurrency:` on `record` (:1218); "shared App quota" absent from HANDOVER. Its O-1 half is 17086c62's, whose route section 3 refutes |
| 61373427 | CONFIRM | gh_read.py:21-25,108-109: waits for `x-ratelimit-reset` on a spent bucket, refuses a wait past the longest settle, never loops |
| b5f92218 | CONFIRM | record_api_calls.sh:65-67 exits 1 on `--record` 0 over a non-empty window |
| 04edda95 | CONFIRM | tests/entities.py:18119-18130 pins the `LoopHeartbeat` default `spy_timeout is PY_SPY_TIMEOUT_S` and no explicit pass in `_async_hb_measure` |
| d096f0c1 | CONFIRM | price_tiles.py:60 `def book`; coordinator.py:8093,8112 use `price_tiles.book(self)` |
| bfe93d15 | CONFIRM | the roster's R10-UX-HEALTH holds the #2572 carry (item 6ce59610); LIVESTATE holds 4c077302 |
| c2b6a1af | CONFIRM, evidence wrong | I re-ran MX1 (deleted coordinator.py:8112 `"price_tiles": price_tiles.book(self),`). tests/finite_boundary.py still passes, `ALL 106 FINITE BOUNDARY CHECKS PASSED`, so the cited :1094 does not kill it. The kill is tests/features.py:43651, "#2257: the ledger save carries the price tiles' book" (42b6681f4); features.py was not run |
| 97d06403 | CONFIRM | HANDOVER.md:500 `tests/layout.py --guard --base` |
| b94aab94 | CONFIRM | HANDOVER.md:505 venv-ci first on PATH |
| 2e462326 | CONFIRM | D2.md:38-39 "every learner driven together ... internal gains only at a converged heat-loss level with a genuine gain" |
| 429b992e | CONFIRM | const.py:1038 "0.245 kW ... 0.012 K" |
| 4ea2e64e | CONFIRM | r10_night_folds_learners.py:23 "gains.unconverged 0.0000" |
| 17053579 | CONFIRM | check-wave-script.mjs:483 drives both words; fix-review.md:54 puts the word first |
| bad0a70a | CONFIRM | policy_lint.mjs:2799 members include the four synonyms; the double-count fix is 75bd9e6b1 |
| 452d9e05 | CONFIRM | the carry it corrects was consumed into D2.md:36-39, which states no harness path or 1.98 figure that could be stale |
| 5a9cc23e | CONFIRM | self-referential: closed in #2558 itself (merged) |
| 2f4b921e | CONFIRM | tests/replay.py:376-391 same-clock pure-Python ruler (option b); no real-day budget exists to mis-record (#2272 open) |
| dc368e8c | CONFIRM | N-orphaned-handoff.md:178-179 cites orchestrator.md §5's soft-cap countermeasure |
| 66a6ad9c | CONFIRM, evidence imprecise | the cited governance.yml:529 is `instrument-self-tests`, not `wave-script`. The wave-script lane's `agreement_py.py --out` (:1153) calls `restore_check` and refuses on any missing file (agreement_py.py:457) |
| bd99c893 | CONFIRM | `gh api .../rulesets/23698884`: active, contexts `["gate"]` |
| ef0d3fec | CONFIRM | abf4f40b7 is an ancestor; ci_budgets.json:26 `critical_path_minutes` 54.825 re-recorded since |
| c1406aa8 | CONFIRM | tests/README.md:274 `dev/audit/harnesses/k1725_blas_kernel_gap.py`; no `tools/audit/harnesses` spelling left |
| cec58467 | CONFIRM | `git grep -c money_currency` in coordinator.py: 0 |
| d40928f5 | CONFIRM | none of the four stale phrases is in D7.md or D9.md |
| 33d0028d | CONFIRM | same as c1406aa8 |
| 78caa42b | CONFIRM | cloud-setup.sh:67 profile exports venv-ci first on PATH |
| 14f2edf3 | CONFIRM NO-OBLIG | figure_lint output quoted as review evidence |
| 24441f60 | CONFIRM NO-OBLIG | CI-on-head evidence list |
| 36367bc0 | CONFIRM NO-OBLIG | disclosure on merged #2572's body (harness is the fixer's own) |
| 4f48ff38 | CONFIRM NO-OBLIG | RCA checklist evidence |
| 57e267d2 | CONFIRM NO-OBLIG | body-identity evidence |
| 653b4a9b | CONFIRM NO-OBLIG | stale figures in merged #2559's own body |
| 7ca5af57 | CONFIRM NO-OBLIG | a bare evidence path |
| 968d05b6 | CONFIRM NO-OBLIG | already `Carry: ... dismissed: a body wording point` |
| b29dfdfd | CONFIRM NO-OBLIG | `Round:` trailer |
| d7ca3d75 | CONFIRM NO-OBLIG | null-control nit on merged #2595's body |

Sample: `random.Random(20261024).sample` of the 25.

## 3. Append-carry ops (21), plus one append-group

| op | verdict | evidence |
|---|---|---|
| FLOW-JIDOKA 056ddbd0 | CONFIRM | in-progress; owns prepr.sh, and the item says prepr can run the instruments its ci-predict step misses. Note: R10-FLY-CIPREDICT-LAYOUT (in-progress) owns ci_predict.py if the fix is to model rather than run them |
| FLOW-JIDOKA 8c6a3e6f | CONFIRM | prepr.sh step; JIDOKA owns prepr.sh |
| FLOW-JIDOKA 9728f4d0 (+e6bf0f70) | REFUTE | Already implemented: governance.yml:467-469 runs `selftest_wiring.py --check` in instrument-self-tests on every PR and push, so a newly added self-testing program is caught. The P1/P2 branch half expired. The decision grepped only prepr.sh, merge_train.py and merge_pr.sh |
| FLOW-RECORD-PITCH 17086c62 | REFUTE | Wrong seam. O-1/M3 is governance.yml's `record` job token (identity, decision 0011), but RECORD-PITCH owns tests.yml and record_row.py (the record-PR automerge pitch). No live group owns the record job: register a fly-in for it, or have the orchestrator take O-1 under the mandate |
| FLOW-RECORD-PITCH 6635e3d7 | REFUTE | Wrong seam: dev/audit/harnesses/record_api_calls.sh, which no live group lists. Route it with 17086c62 to the same record-job fly-in |
| FLOW-TOOLKIT-MODEL a6edee9d | REFUTE | The carry file holds only the routing header. The item ("Carry: R10-PLAN-ARTIFACT (item D2). One plan model, marked [target: ...]") was dropped, so the carry tells the fixer nothing, and TOOLKIT-MODEL's brief already says "part of the one plan model, not beside it". Either NO-OBLIGATION or re-cut with #2609's D2 text |
| FLOW-WIP dbae61eb | REFUTE | Wrong seam: dev/governance/roles/nudge.md (policy, code-owned) is not in FLOW-WIP's files, and no live group lists it. The defect is real: nudge.md step 16 caps lane A. Fix it under the policy-merge rule in a policy group, or have the orchestrator edit it under the mandate |
| FLOW-WIP capline (absorb CAP-LINE) | CONFIRM | orchestrator_tick.py is in FLOW-WIP's files. The only after-edge on CAP-LINE is R10-ARCH-DOCS's, which also lists FLOW-WIP, so the dependency survives. Note: `absorbed` (an existing stage) records this better than `done` |
| FLY-CLOUD-SETUP-TOOLCHAIN 6d4f5c52 | CONFIRM | in-progress; owns cloud-setup.sh (the profile can export RUNNER_TEMP) |
| FLY-GH-READ-RETRY bb2965c2 | CONFIRM, reorder | owns merge_train.py; but the group is `done` when the op runs, and the reopen (`set-stage carries-open`) is in section 6 behind an issue create. Run the set-stage first, or a failed create leaves a done group with a new pending carry |
| MERGE-SUBJECT-HARDEN f09dc4ca | CONFIRM | owns agreement.mjs; in-progress |
| ORCH-BEATD cdd7283c | CONFIRM | the brief owns the supervised beat's per-job timeouts and single-instance locks (dead lock owner, 1 h self-test). Arm 1 (handoff tip ahead of its PR) fits R10-ORCH-LEDGER's handoff kind better |
| ORCH-DISPATCH-REG 8ab071b4 | CONFIRM | owns bus.sh; `unboarded` appears nowhere under tools/ on main |
| ORCH-DISPATCH-REG 9a2082ce | CONFIRM | same |
| ORCH-LEDGER 6bec0b0a | CONFIRM | its brief owns the handoff-no-pr aging (24 h/48 h); ledger.py is its landed module (301515179) |
| ORCH-ROSTER-SCHEMA 3b97e1aa (+1f866f06) | CONFIRM | owns roster_edit.py |
| ORCH-ROSTER-SCHEMA 7f85b089 | CONFIRM | owns roster_edit.py set-stage. It collides with ROUTING-INVARIANTS (section 5) |
| RCA-FRICTION-RESIDUE 631f8640 | CONFIRM | key #2438 is in its issues |
| RCA-FRICTION-RESIDUE 76e30be3 | REFUTE | Wrong seam: bash 3.2 against bash 5 is an environment friction note, not one of the five keys the group records, and no live group owns HANDOVER.md. Like 78caa42b, the remedy is a HANDOVER trap the orchestrator writes |
| TRAIN-OVERLAP-GRADE 6fb50ac5 (+98904e32) | CONFIRM | its brief names 6077bf70e as instance 1 |
| UPDATE-PR-SIGNALS 01ce8b81 | CONFIRM | owns cloud_relay.sh and update_pr.sh; in-progress |
| append-group R10-RESTORE-RACE-PROBE | REFUTE | Duplicate owner: R10-PARAMS-OWNER's carry 10 already says "#2674 (ls-r2 ...) is scheduled as a probe-role seat on this group", and its carries 8-9 hold the ls-r1 recipe. The decision's "no live group lists #2674" checked only issues and fixes. Instead: `wire-issue R10-PARAMS-OWNER 2674` (and 2248), and route f61f187d there |

## 4. Issue bodies (19)

`gh issue list --state all --search` was run for each body, plus `pyspy`, `nightly false-red`, `carry-missing`, `Dependabot` and `immersion` on open issues, and the open list was cached (53 issues). No duplicates: hits are #201, unrelated closed issues, and the related-but-distinct #2428 (carry-missing friction) and #2505 (machinery). No title contains close/fix/resolve before an issue number, and every body uses only `Part of #201`. All 19 CONFIRM on these criteria: each names one defect or ask and the group or groups it covers. Notes:
- immersion-latch.md states the mechanism but no ask; the ask lives in the group brief.
- routing-invariants.md describes the design section 5 refutes; it is fine on these criteria but must be re-cut with that design.

## 5. R10-ROUTING-INVARIANTS design

REFUTE as cut; revise before dispatch. The direction is sound: it extends carry_audit and brief_lint and adds no script, and the consumed-versus-pending mark is the missing fact. Defects:
1. **The set-stage refusal breaks the factual sync.** `roster_sync.apply_plan` sets `done` through `roster_edit.op_set_stage` at every merge. In op_set_stage, one pending carry refuses the whole beat pass; in the CLI only, roster_sync bypasses it and every merge reads STRANDED. Fixers do not mark carries, so this is every merge. Use the existing `carries-open` stage (3 groups hold it today) for a merged group with pending carries, and refuse nothing.
2. **The migration launders.** Marking every done group's carries `[implemented: <resume.commit>]` turns unknown into implemented. In this audit's own sample, 39 of the 70 done-group destinations were NOT implemented, so the blanket mark hides about half and makes the null control pass by construction. Grandfather instead: mark them `[legacy]`, or apply invariant 1 only to carries appended after a cut-over roster sha.
3. **The issue check on push to main reds main on events, not diffs.** The friction cron files issues on its own (#2660, #2597, #2593 ...), and nothing lists them until a seat does. Make invariant 3 a tick report line, not a failing job.
4. **brief_lint invariant 2 as an error blocks the roster write path.** roster_edit's `--push` lint gate would refuse every edit while any live group lacks an issue (32 today), and registering a fly-in at dispatch (orchestrator step 16) would first need an issue. That is a policy change for the orchestrator, so land it as a warning, or only after the wiring ops, and state the fly-in rule.
5. **Duplicate scope with R10-ORCH-ROSTER-SCHEMA (#2505).** Its carries already own `absorbed` joining DONE_STAGES (design 6.4 predicate 2, conditional on after-edges) and set-stage refusing an unclassified stage, which is the same function. ROUTING-INVARIANTS has `after: []` and calls the seams distinct. Fold the roster_lib and set-stage parts into ROSTER-SCHEMA, or add `after: R10-ORCH-ROSTER-SCHEMA`.
6. **The per-PR offline check fails unrelated PRs.** It reds any PR while main's roster violates. Scope it to PRs that touch the roster file or carry_audit, plus push to main.
7. **`[implemented: <sha>]` proves only that the sha is on main.** It is a record, not verification; do not count it as one.

Simpler design that keeps the same invariants: (a) `mark-carry` in roster_edit plus `carry_audit.py roster` as a report: STRANDED = a pending carry on a done group, legacy carries exempt; (b) roster_sync sets `carries-open` rather than `done` when pending carries remain; (c) invariants 2 and 3 as tick lines in the default pass, from the tick's cached issue list (make CARRY default, offline); (d) no set-stage refusal, no CI job on issues, no blanket migration. Size S, and it shares no set-stage seam with ROSTER-SCHEMA.
