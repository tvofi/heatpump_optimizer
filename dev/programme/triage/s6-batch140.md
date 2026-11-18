# Proposal triage, session s13, batch 140 (P476 to P499)

The owner asked: "Does the triage seat apply the >20% bar for proposals and does all remaining
instrument fixes in the plan pass the 10% bar?" This batch answers the second half (A, P476 to
P487). It also re-checks the earlier batches that read "low or normal meets both" as a pass (B and
C, P488 to P499).

The bar is `dev/governance/roles/proposal-triage.md` at origin/main `0a8033305d` (R10-FLY-TRIAGE-BAR,
#3310), read with the owner's rulings of 2026-11-08:
- A new proposal is accepted on a measured gain of more than 20 %.
- A planned machinery group or lane stays on a measured gain of at least 10 %.
- The measures are CI time, programme completion time, right-first-time and token usage.
- A machinery repair outside `custom_components/` with severity `low` or `normal` takes the bars.
- Severity `medium` and above, a root-cause countermeasure, closeout and an owner directive skip the
  bars.
- An unset severity is classified first.
- Batch 136's P434 adds a reading: a roster severity skips the bar only where the work repairs a
  wrong behaviour that was observed. On a throughput or feature build it is a priority tag.

This batch applies P434 to the work each group still owes, not to the severity it was opened with.
Most live machinery groups have merged their main pull request, and what they hold now is
forward-carried residue. A `medium` group can therefore owe `low` carries.

Denominators, all from batch 136 and not re-taken:
- **CI time:** 29876 runner-min/day (`s12/ci-tput/waste.txt`).
- **Programme completion:** the replan base wall of 170.42 h (`s13/lane-study/runs/base1.json`).
- **Right-first-time:** 55 PRs with a `ci.yml` run on 11-07.

Sources read:
- origin/main `0a8033305d`.
- The roster branch `origin/handoff/audit-r10-roster` at `b1de33a83a`, with the roster's cut-over
  commit `a4c9fa3d62` for legacy carries.
- `s7/triage-queue-s7.txt` lines 161, 162 and 164, the lines after batch 139 that it left unruled.
- `s7/roster-queue-s7.txt`, for the `#held` state of batch 137 and 138 carries.
- The batch files 136 to 139.
- API reads, each named beside its figure: PR states and bodies, workflow states, and nightly run
  jobs.

Pending carries are counted with `roster_lib.pending_carries` from origin/main, which counts a carry
that is unmarked and not legacy. A carry a merged PR built but nobody marked still counts as
pending, and this batch found many. They are listed per entry as **built, unmarked**: work done,
owing a `mark-carry`, not a keep test.

## P476: KEEP-REVIEW, every live machinery group

Verdict, over the 43 live non-absorbed machinery groups:
- 30 KEEP on a skip route.
- 6 KEEP narrowed on a skip route (P477 to P482, P486).
- 2 KEEP on a measured gain: HOTFIX-CODEQL-HEADROOM (P463, 9 of 19 main python jobs capped) and
  FLY-STAMP-FLUSH-COST (P485, 22.3 % of a day's CI, now built).
- 4 hold no unbuilt work and close (P483, P484, P487).
- 1 DEFER-TO-MEASURE (R10-SUITE-HOST-DETERMINISM, P480).

No whole group is dropped. 14 carries are dropped below the bar (P479 to P485).

So the answer to the owner is no. Two of the remaining instrument groups pass the 10 % bar on a
measurement, and one of them is already built. The rest stay on a route the contract exempts: a medium-or-above repair of an observed
defect, a root-cause countermeasure, closeout or an owner directive. The low residue inside those
groups is tested carry by carry in P477 to P487, except where the last bullet of this entry names it
as owed.

Source: the batch-140 brief, scope A.

Enumeration:

```
git show origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json | python3 -I -c '
import json, sys
d = json.load(sys.stdin)
live = [g for g in d["groups"] if g["resume"]["stage"] not in ("done", "refused", "refuted")]
print(len(d["groups"]), len(live))
for g in live:
    f = g.get("files") or []
    print(g["group"], g.get("kind"), g.get("severity"), g["resume"]["stage"],
          sum(x.startswith("custom_components/") for x in f), len(f))'
```

It prints `396 74`: 34 carries-open, 19 in-progress, 13 absorbed and 8 not-started.
- **Out of scope, 19 groups.** These are product code, user docs or an owner step: SAV-COMFORT,
  ARCH-DOCS, ADVISOR-WHATIF, CATALOG-PR, USER-DOCS-VERIFY, WHY-NOW-WIDGET, SAV-WOOD-MEASURED,
  SAV-METER-FLOOR, COMBI-TANK, HOTFIX-COP-UNMEASURED, COP-GATE-E, PARTLOAD-RESIDUE, I18N-DE,
  GENERIC-HEAT-CURVE, GENERIC-HEAT-CURVE-PERSISTENT, ARBITER-OFF-RESTORE, MIN-POWER-FLOOR,
  HOTFIX-STRESS-MEM-PEAK (it edits `optimizer.py`) and WATER-SETPOINT-LIFT.
- **Absorbed machinery, 12 groups, 0 pending carries each.** ORCH-ROSTER-SCHEMA,
  FLY-RELAY-DELIVERED-GUARD, RELAY-HANDOFF-ARM, OPENER-REUSE, ROSTER-OPS-2, ROSTER-LIB-SCHEMA,
  ROSTER-QUEUE, TICK-PR-BUCKETS, TICK-GROUP-LINES, SEAT-SINGLE-WRITER, FLY-GANTT-DRIFT and
  PR-CONTRACT-OUTSIDE. Their work is in their hosts and is ruled there. `absorbed` is in
  `roster_lib.CLOSED_STAGES` (#3250), so no tool schedules them. No op.
- **Live machinery, 43 groups.** They are in the table below. Open PRs are from `gh pr list --state
  open`. A live handoff is a `handoff/r10-*` tip that is not an ancestor of origin/main.

| group | sev | route, or the measured gain | verdict | PR or handoff |
|---|---|---|---|---|
| PREPR-CAP | medium | P454 major (held); carries 13 and 14 RCA; 9 and 18 owner rec (a) 10-24 | KEEP, narrowed (P477) | none |
| FLOW-TOOLKIT-MODEL | medium | carry 13, owner rulings 11-07 (closure rule) | KEEP, narrowed (P478) | none |
| FLY-GH-READ-RETRY | high | audit-class barrier (third instance) | KEEP | #3361 |
| ROUND-PLAYBOOK | medium | owner request 10-21 | KEEP | #3319 |
| POLICY-ROLE-PACK | medium | carry 4, owner directive P398 (batch 136 entry 429) | KEEP | none |
| CLOSEOUT-CLEANUP | medium | closeout, owner request 10-24 | KEEP | none |
| FLY-CIPREDICT-RESTORING | medium | carry 2 (a)/(b), RCA countermeasure P371 | KEEP, narrowed (P479) | none |
| FLY-STANDING-CONTRACTS | medium | owner directive 10-31, verbatim in brief | KEEP | none |
| BODY-CONTRACT | medium | owner card 7 (carries 1 and 42); P440 medium | KEEP | #3355 |
| SUITE-HOST-DETERMINISM | medium | residue is low; unmeasured | DEFER-TO-MEASURE (P480) | none |
| DISPATCH-AT-HANDOFF | medium | owner cards 11-01 and 11-07; P475 medium | KEEP | #3366 |
| RAISE-GATE-SHIM | medium | carry 1 observed (#3045 dS gamed twice); P451 major (held) | KEEP, narrowed (P481) | none |
| ROSTER-WRITE-SWEEP | medium | carry 20 P435 major; carry 17 P409 hotfix | KEEP | none |
| ROSTER-READ-SWEEP | medium | carry 8, the stranded-carry invariant (closeout) | KEEP, narrowed (P482) | none |
| TICK-LEVELS | medium | P456 major; P438 medium; P445 and P377 RCA | KEEP | #3345 |
| HANDOFF-PATH | medium | carry 12 observed (22 of 45 updates); carry 6 observed disk loss | KEEP (P487) | none |
| RELAY-SWEEP | medium | carry 6, RCA countermeasure; P437 C1 | KEEP | none |
| PROCESS-SLIM | medium | owner ruling 11-05, cards C2 to C9 | KEEP | #3245 |
| TRAIN-MERGE-LOOP-2 | medium | all 16 built at #3288 | close (P484) | none |
| HOTFIX-GATE-BUSY-DEFER | medium | observed deadlock, three instances in one hour | KEEP | #3348 |
| CARRY-RESIDUE-2 | medium | 9 built at #3325; 6 data edits below the bar | close (P483) | none |
| HOTFIX-CODEQL-HEADROOM | medium | P463: 9 of 19 main python jobs capped | KEEP | #3367 |
| OUTSIDE-INTAKE | medium | owner directive 11-06 | KEEP | #3350 |
| RCA-GATE-BUSY-DEFER-2 | high | RCA | KEEP | #3353 |
| FLY-STAMP-FLUSH-COST | medium | measured 22.3 % of a day's CI, now under 0.01 % | KEEP met; close (P485) | none |
| ROUND-PLAYBOOK-FINAL | medium | owner ruling 11-07 ("Approve both") | KEEP | none |
| HOTFIX-TRAIN-DEFER-WAIT | high | P436 major barrier; owner lever 1 | KEEP | none |
| CI-SELFTEST-SCOPE | medium | owner lever 3 (#201 comment 6707834331) | KEEP | #3315 |
| TRAIN-STALE-VERDICT-GUARD | medium | observed: 1 stale admit in 26 (P393 harness), a wrong-merge guard | KEEP | #3364 |
| CLOSEOUT-INSTRUMENTS | normal | closeout | KEEP | none |
| FRICTION-OTHER-FAMILY | normal | RCA; #3311 merged; 0 carries | close (P487) | none |
| RCA-COP-UNMEASURED | normal | RCA; residue is its class countermeasure | KEEP, narrowed (P486) | none |
| FIXER-MD-SPELLING-CORPUS | normal | owner ruling 11-07; carry 1 P423 RCA | KEEP | none |
| HOTFIX-AUTHOR-EMAIL | high | owner hotfix tier 11-07 | KEEP | #3339 |
| TRAIN-REJOIN-NO-RECARRY | high | owner cards 1 and 5, 11-07 | KEEP | #3359 |
| REVIEW-ENUMERATE | medium | owner card 2, 11-07 | KEEP | #3341 |
| FLY-DISPATCH-RULINGS | high | owner directive; built at #3338 | close (P487) | none |
| OUTSIDE-FIRST | high | owner ruling 11-07T19:40Z | KEEP | #3304 |
| FLY-REPLAN-DEFECTS | medium | observed: (b) 17 h slot held for a refused group | KEEP | #3326 |
| RCA-CLOUD-ENTITIES-ENV | medium | RCA residue blocking cloud suites (owner: heavy runs in the cloud) | KEEP (P487) | none |
| RCA-SWEEP-SETTLE-LOOP | medium | RCA | KEEP | #3329 |
| HOTFIX-ROSTER-LINT-REFRESH | medium | observed: 172 cascaded refusals | KEEP | #3337 |
| RCA-STAMP-CLAIM-CONFLICT | medium | RCA | KEEP | #3351 |

Live handoffs (`git merge-base --is-ancestor <tip> origin/main` false): body-contract-p3, dispatch-
at-handoff-p2, fly-gh-read-retry-p3, hotfix-gate-busy-defer-p5, round-playbook and tick-levels-p2.
Each has its open PR above.

Not individually re-tested here, and owed in the next batch:
- These are low-tagged residue carries inside groups kept on a route: BODY-CONTRACT 6, 9 and 45;
  TICK-LEVELS 11 and 12; DISPATCH-AT-HANDOFF 12; FLY-GH-READ-RETRY 6, 8 and 10;
  HOTFIX-GATE-BUSY-DEFER 0 and 11; PROCESS-SLIM 1; CI-SELFTEST-SCOPE 0.
- They were selected by the word `low` in the carry's text, so the list is a superset.

Binding: the contract's machinery paragraph and P434. The ops are in P477 to P487.

## P477: R10-PREPR-CAP, 16 pending carries

Verdict: KEEP, narrowed. Main PR #3051 merged `239e5e4a69`.

Source: P476.

Instances, by carry index:
- **Built, unmarked (5):** 7, 10, 15 and 27, the base-copy grader replay; and 11, the S36 pin.
  - For the replay, `tools/pr/ci_predict.py` models AGREEMENT and every restoring job's GRADER
    (`restoring_jobs`, line 582). That is #3301 `6188936a8b`, on top of `6d4c233af2`.
  - For 11, the harness pattern `push_app 2 > /dev/null; out=$PUSH_OUT  # mut:push-open` is at
    `tools/audit/seat/handoff_push.sh` line 212 (`grep -nF`). It has been since `acfad45d07`.
- **Kept on a route (6):**
  - 9 and 18, quiet output, are owner-accepted (tvofi 2026-10-24 recommendation (a)). Unbuilt:
    `git grep -i quiet` in `update_pr.sh` and `open_pr.sh` is empty.
  - 13 is the RCA R10-RCA-BODY-CHECK-PARITY countermeasure.
  - 14 is a red-check RCA.
  - 28 is the red-check countermeasure for the `parents[N]` harness class: `prepr.sh` holds no
    `inline_scan`.
  - P454 (major, batch 137) lands here once it is released.
- **Duplicates of 28 (2):** 16 and 29.
- **DEFER-TO-MEASURE (4):**
  - 12, the body-check parity extensions (a) to (c). The cheapest measurement is how many bodies
    `body_push` passed that `open_pr`'s prepr then refused for those three classes since 10-24,
    read from the opener's fails logs.
  - 19, 12 self-tests adopting `pr_bounded`. The measurement is the count of hung or timed-out runs
    of those 12 self-tests in CI since 10-24.
  - 20, the HEAD-ONLY predicting detector. The measurement is the HEAD-ONLY count in the round-1
    census against all CI reds.
  - 21, the `.gitignore` `config/` rule, still at line 28. The measurement is how many files under
    `*/config/` were added in round 10 against those a handoff omitted.
  - Each one builds only if its measurement shows at least 10 % on one measure.

Binding: the contract's machinery paragraph. Ops: mark 7, 10, 15 and 27 implemented `6188936a8b`
and 11 implemented `9262e6f43d`; dismiss 16 and 29 as duplicates of 28.

## P478: R10-FLOW-TOOLKIT-MODEL, 11 pending carries

Verdict: KEEP on carry 13 (owner rulings 2026-11-07). Main PR #3264 merged `8aec354354`.

Instances:
- **Built, unmarked (9):** 0, 2, 3, 8, 9, 10, 11, 12 and 15.
  - #3264's body says "Carry k (brief k-1)" and gives index 15 as its own carry 16.
  - It lists carries 1, 3, 4, 9, 10, 11, 12 and 13 as "built in an earlier round" and carry 16 as
    "implemented in this pull request".
- **Moved (1):** carry 14 asks that refused, refuted and deferred be priced as closed.
  R10-FLY-REPLAN-DEFECTS (b) is the same defect at `roster_lib.CLOSED_STAGES`, and its open #3326
  builds it.
- **Kept (1):** carry 13 is the closure rule the owner set on 2026-11-07, verbatim in the carry.

Binding: the owner-directive route for carry 13. Ops: mark the nine implemented `8aec354354`; mark
14 moved to R10-FLY-REPLAN-DEFECTS.

## P479: R10-FLY-CIPREDICT-RESTORING, 5 pending carries

Verdict: KEEP on carry 2 (a)/(b), the P371 RCA countermeasure in policy text. DROP carry 3.
DEFER-TO-MEASURE carry 4. Main PR #3301 merged `6188936a8b`.

Instances (#3301's body numbers carries from 1):
- Carry 1 is built: "Landed in this PR: Carry 2". So is carry 2's part (c).
- Carry 0, the `inline_scan` arm, duplicates R10-PREPR-CAP carry 28, which keeps it (P477).
- Carry 3, the `agreement.mjs` age-needle and surviving mutant M-h, is a test gap. No red and no
  wrong verdict from it is recorded, so nothing on the four measures can be measured. DROP.
- Carry 4: `ci_predict` prescribes `--apply-inert` for an imported INERT file. The cheapest
  measurement is the count of `INERT READS` prescriptions in the prepr logs since 11-01 that an
  import made wrong.

Binding: the RCA route for carry 2; the >=10 % keep bar for 3 and 4. Ops: mark 1 implemented
`6188936a8b`; dismiss 0 as a duplicate; dismiss 3 as below the bar.

## P480: R10-SUITE-HOST-DETERMINISM, 5 pending carries

Verdict: DEFER-TO-MEASURE (group). DROP carry 5. Carry 4 is moved. Main PR #3170 merged
`8bf45e5dce`.

Instances:
- Carry 4, cloud `tests/entities.py` reading "2 of 2449 ENTITY CHECKS FAILED", is the class
  R10-RCA-CLOUD-ENTITIES-ENV owns (3 of 2665 checks; `cloud-setup.sh`, #3334). It is moved there.
- Carry 5, entities judging HEAD and not the working tree, has one instance, with no escape
  recorded. Seats commit before they gate, so nothing on the four measures moves. DROP.
- Carries 6 to 8 are macOS host determinism in `tests/entities.py` and `tests/nightly_ha.py`: six
  or seven seat-local wrappers, and a heartbeat respawn whose premise carry 8 says has changed.
  - Fixers have run mostly in the cloud since 11-01 (owner), so the host case serves few runs.
  - The cheapest measurement is carry 8's own recipe: hb failures in `gh run list --workflow
    nightly.yml` over 7 days. Count beside it the local, non-cloud entities runs in the seat ledger.
  - It builds only on at least 10 %.

Binding: the >=10 % keep bar. The residue is low; the group's `medium` was its original flakes.
Ops: mark 4 moved to R10-RCA-CLOUD-ENTITIES-ENV; dismiss 5.

## P481: R10-RAISE-GATE-SHIM, 8 pending carries

Verdict: KEEP on carries 0 and 1, plus P451 (major, batch 137) once it is released. DROP carries 3,
4 and 6. Main PR #3223 merged `5915e30b4e`.

Instances:
- **Carry 1 is an observed defect.** An unearned dS (body +0.0012, true +0.0000) passed
  `budget_raise_gate.py` twice on #3045. The gate reads only the shape of the line. Medium: a policy
  gate passed a false figure, and only the reviewer caught it.
  - Carries 5 and 7, "accepts a wrong figure beside the measured one", are the same value check.
    They are duplicates of 1.
- **Carry 0 (a):** a raw post to #201 bypasses the kill-switch word guard. Such a post would trip the
  owner's mandate kill switch. That is classified medium, on the consequence.
- **Carry 2** is the measurement of (c), with the result "no change needed". Dismiss it as
  measured.
- **Carries 3, 4 and 6** are the `exec -a` argv0 spoof. They are "residual, by design": the shim
  guards a seat's habit, not an adversary, and none has an instance. DROP.

Binding: medium repair and the major carry skip the bar; the residual takes the >=10 % keep bar.
Ops: dismiss 2, 3, 4, 5, 6 and 7.

## P482: R10-ROSTER-READ-SWEEP, 5 pending carries

Verdict: KEEP on carry 8 (closeout: the stranded-carry invariant). DROP carries 6 and 7. Main PR
#3250 merged `87c2852ebc`.

Instances (#3250's body numbers carries from 1):
- Carry 0 is built: "Carry 1 (absorbed counted as open): landed in this diff".
- Carries 6 and 7 are #2875 unowned and #2855's key. `gh issue view` gives #2875 CLOSED
  2026-11-07T16:34Z and #2855 CLOSED 2026-10-29T16:03Z, so both instances are moot. DROP.
- Carry 5, the disposed-key mechanism, is the same invariant as carry 8. Fold it there.
- Carry 8 records 211 stranded carries on closed groups at the s11 read. The owner's closure
  condition ("no ... carries", 2026-11-07, quoted in R10-FLOW-TOOLKIT-MODEL carry 13) makes their
  detection closeout work.
- P452 (batch 137, low, `#held`) is re-tested in P498.

Binding: the closeout route for carry 8; the >=10 % keep bar for the rest. Ops: mark 0 implemented
`87c2852ebc`; dismiss 5 as folded into 8; dismiss 6 and 7.

## P483: R10-CARRY-RESIDUE-2, 15 pending carries

Verdict: close. 9 are built and 6 are dropped below the bar. #3325 merged `82a2c142fa` at
2026-11-09T05:33Z.

Instances (#3325's body numbers from 0, and says "the group holds carries 0 to 14"):
- **Built (9):** 0, 1, 2, 3, 4, 8, 12, 13 and 14.
- **Dropped (6):** 5, 6, 7, 9, 10 and 11, roster DATA edits that #3325 left to the roster seat.
  - 5 and 9 backfill `resume.pr` on done groups.
  - 6 and 10 rewrite an old handoff phrase in live briefs.
  - 7 and 11 add `set-stage absorbed --into` hosts. No tool reads `absorbed_into` for scheduling,
    and `absorbed` is closed since #3250.
  - None of them moves CI time, completion, right-first-time or tokens, so no measurement is
    possible. DROP.

Binding: the >=10 % keep bar. Ops: mark the nine implemented `82a2c142fa`; dismiss the six; then
`set-stage R10-CARRY-RESIDUE-2 done --at-sha 82a2c142fa`.

## P484: R10-TRAIN-MERGE-LOOP-2, 16 pending carries

Verdict: close. All 16 are built at #3288, merged `72940b7954`.

Instances:
- #3288's body numbers carries from 1 and covers carries 1 to 17 in its bullets: 1, 8 and 16; 2 and
  10; 3, 7, 9, 11 and 17; 4 and 12; 5 and 13; 6 and 14; and 15. That covers every roster index from
  0 to 15.
- Two items are not built, and both were already carried on: the measure-first count, now
  R10-TRAIN-REJOIN-NO-RECARRY carries 0 and 2; and the gate-race finder harness, now
  R10-HOTFIX-TRAIN-DEFER-WAIT carries 0 and 2.

Binding: no keep test applies, because nothing is unbuilt. Ops: mark 0 to 15 implemented
`72940b7954`, then `set-stage done --at-sha 72940b7954`. The orchestrator checks the 16 texts
against #3288's bullets before releasing, because #3288 counted 17 where the roster now holds 16.

## P485: R10-FLY-STAMP-FLUSH-COST, KEEP met, and close

Verdict: KEEP: the measured gain clears the bar, and the build is merged (#3296, `341da07212`).
DROP carry 4. The group then closes.

Instances:
- Before: about 950 runner-min per beat dispatch, and 7 dispatches on 11-07 (P404). That is 6650
  runner-min, 22.3 % of 29876 runner-min/day.
- After: `gh run list --workflow nightly.yml --event workflow_dispatch --created
  '>=2026-11-08T04:48Z'` gives 3 runs: 42481292308, 42482526310 and 42483753528, each "Nightly
  record beat". In each, `actions/runs/<id>/jobs` shows 1 non-skipped job, `record-autofix`, with
  0 to 1 runner-min. This discharges the post-merge measurement owed by carries 0, 2 and 5.
- Carry 4, deleting the `record-autofix` beat, would now save at most 1 runner-min per dispatch,
  under 0.01 % of a day. DROP.
- Carries 1, 3 and 6 are fixer-step-push notes about a stale `handoff-wip` ref. They are not work.

Binding: >=10 % kept (22.3 % before the build). Ops: dismiss 0, 2 and 5 as measured, 1, 3 and 6 as
not work, and 4 as below the bar; then `set-stage done --at-sha 341da07212`.

## P486: R10-RCA-COP-UNMEASURED residue, the cwd capture across harnesses

Verdict: KEEP carry 0, narrowed to one fix: anchor `tests/harness.py`'s path inserts. It is the
RCA's own class countermeasure. #3316 merged `2865d38674`.

Instances: the carry's own enumeration, run at origin/main:
- 39 harnesses import `harness`, and 29 of them touch `sys.path`.
- 24 of those 29 have no `os.chdir`, out of 213 `.py` files under `dev/audit/harnesses/`.
- So 24 harnesses can measure the cwd's tree and not the root they were given.
- A finder harness that measures the wrong tree voids findings (`judge.md`).

Cost: one anchor in `tests/harness.py`, not 24 edits. Carry 1 duplicates carry 0.

Binding: the RCA route. Ops: dismiss 1 as a duplicate.

## P487: groups with no unbuilt work, and duplicates

Verdict:
- Close R10-FLY-DISPATCH-RULINGS: carry 0 was built at #3338 `fdc8d21ada` ("Carry 1 (the group's
  only carry) is built in full").
- Close R10-FRICTION-OTHER-FAMILY: #3311 merged `4fe7d5934b`, with 0 carries.
- Keep R10-RCA-CLOUD-ENTITIES-ENV on carry 0. `cloud-setup`'s venv-ha lacks scipy and paho, so
  suites cannot run in a cloud seat, where the owner sends heavy runs. Carries 1 and 2 restate it.
- In R10-HANDOFF-PATH, carry 40 restates 19.

Ops:
- R10-FLY-DISPATCH-RULINGS: mark 0 implemented `fdc8d21ada`, then `set-stage done`.
- R10-FRICTION-OTHER-FAMILY: `set-stage done --at-sha 4fe7d5934b`.
- R10-RCA-CLOUD-ENTITIES-ENV: dismiss 1 and 2 as duplicates.
- R10-HANDOFF-PATH: dismiss 40 as a duplicate of 19.

## P488: re-check of P459 (CARRY-STATUS-DISAGREE)

Verdict: REJECT. This reverses batch 138's ACCEPT, which read "low meets both" as a pass.

Instances (batch 138's own):
- 1 instance (#3345 `becd0c23`) among the CARRY-MISSING refusals of 11 PRs. The other 10 are not
  this class.
- On right-first-time that is 1 of 55 PRs, 1.8 %. The cost was one waiting reviewer, and a
  workaround exists: land the line as a roster carry.

Binding: 1.8 % against the >20 % add bar, for a low repair. Op: the orchestrator removes the
`#held` line for `b138-P459.txt` from `s7/roster-queue-s7.txt`. It never landed, so there is no
roster op.

## P489: re-check of P461 (PLAN-PAGE-NONE-LEAK)

Verdict: ACCEPT, upheld on the owner-directive route, not on "low meets both".

Instances:
- R10-OUTSIDE-INTAKE builds the page the owner ruled public on 2026-11-06 ("the plan html for an
  ongoing round should be made publically available").
- The 04:57Z page printed 1 `data-wave="None"`, 1 `wave None` and 51 `sort key [...None...]`.
- A public page that renders internal `None` fails that directive. This is the same route batch
  139's P473 took for the extension.

Binding: the owner-directive route. Op: none new. The `#held` `b138-P461.txt` line stays and is
released with the batch 138 landing.

## P490: re-check of P462 (OPENER-LOST-HANDOFF, the `ledger.py` half)

Verdict: REJECT. This reverses batch 138's ACCEPT of the tracked half.

Instances (batch 138's own):
- 13 PRs were closed unmerged since 10-25. 4 left a branch, and 1 of the 4 was the successor shape.
- That is one 50-min critical-path stall in about 15 days: 0.49 % of the 170.42 h completion base.
- The stand-in opener's own skip is session-local (P462's REJECT half, and P474).

Binding: 0.49 % against >20 %, for a low repair. Op: the orchestrator removes the `#held` line for
`b138-P462.txt`.

## P491: SKIP-DEFERRAL-NOT-ENVIRONMENT, second instance

Verdict: DEFER, upheld. The owning group is R10-TRAIN-REJOIN-NO-RECARRY (open #3359).

Source: queue line 161 (2026-11-09T07:28:37Z).

Instances:
- #3359 at `6ccb12bd` was SKIPped in train 95260 on a pure deferral red, gate job 129016853964.
  With #3330 and #3355 (P470), and #3361 (line 162), that is 4 skips in one night.
- All 4 fell while `gate-sweep.yml` was `disabled_manually`. `gh api
  .../actions/workflows/gate-sweep.yml` now gives `active`, updated 2026-11-09T07:33Z. The cause
  P465 named is therefore removed.
- P470's trigger has not occurred: a GATE skip GREEN at its verdict and refused on re-add, after
  #3359 merges and with the sweep running.

Binding: P470's condition stands. The class has reached a third instance, but its countermeasure is
the sweep, which is now re-enabled. The re-enable condition itself is P492.

## P492: REENABLE-CONDITION-UNWATCHED

Verdict: REJECT. It duplicates R10-TICK-LEVELS carry 18, and the instance is cured.

Source: queue line 162 (2026-11-09T07:33:34Z).

Instances:
- R10-TICK-LEVELS carry 18 (from `handoff/r10-rca-tick-blind`, item 2a35d4b3) says "the board flags
  a disabled Gate sweep".
- The generalisation, a beat row over every workflow's disabled state, has no second instance.
  `gh api .../actions/workflows` lists no workflow that is not `active`.
- The measured cost is real: 9.5 h off after #3327, 46 hand re-runs and 4 train skips. But it
  belongs to the one workflow carry 18 already covers.

Binding: a duplicate, with a gain over carry 18 of zero instances against the >20 % add bar.

## P493: TRIAGE-140-NOTE

Verdict: ACCEPT. P488 to P490 answer it. The same misreading in batch 137 is re-tested in P494 to
P499.

Source: queue line 164 (2026-11-09T07:38:06Z).

Instances: batch 137 ruled six low repairs "It meets the bar": P439, P448, P449, P450, P452 and
P455. All six carries are still `#held` in `s7/roster-queue-s7.txt` (lines 3473, 3481, 3482, 3485,
3488 and 3492).

Binding: the >20 % add bar. Destination: P494 to P499 in this file.

## P494: re-check of P439 (CLOUD-DISPATCH-DESIGN-REF-CASE)

Verdict: REJECT. This reverses batch 137.

Instances: 1 (R10-COMBI-TANK), worked around with `--design-exempt`. That is 1.8 % of 55 PRs.

Binding: >20 %. Op: the orchestrator removes the `#held` `b137-P439.txt` line.

## P495: re-check of P448 (DESIGN-RECUT-UNREVIEWED)

Verdict: DEFER. The owning group is R10-TICK-LEVELS.

Instances: one re-cut (`design/R10-ADVISOR-WHATIF` `b50afa68`) sat 4 days with no reviewer. 96 h is
large against 170.42 h, but it counts only if that group binds closure.

What would change it: a replan at a fixed `--start`, with and without the 96 h hold on
R10-ADVISOR-WHATIF. A closure shift over 20 % passes it. The `#held` line stays held.

## P496: re-check of P449 (GH-BUCKET-UNATTRIBUTED)

Verdict: ACCEPT, upheld on the owner-directive route.

Instances: the core bucket at 0 refused the v7.1.6 stamp's gate read, and no caller could be named.
The owner's 2026-11-08 order not to hammer the API needs a caller to be attributable, which P449's
binding names as its benefit.

Binding: the owner-directive route. The `#held` line is released with the batch 137 landing.

## P497: re-check of P450 (LEDGER-CLOSE-WRONG-SHA)

Verdict: DEFER. The owning group is R10-TICK-LEVELS.

Instances: 1. The stop opened at 2026-11-06T22:44Z stood until 11-08 and refused one `sweep
--stamp`. The delay it caused the stamp is not measured.

What would change it: the `events.tsv` time from the refused sweep to the hand close. More than
20 % of the stamp interval passes it. The line stays held.

## P498: re-check of P452 (POSTMERGE-ROSTER-RC3 residue)

Verdict: DEFER. The owning group is R10-ROSTER-READ-SWEEP.

Instances: 5 rc-3 refusals (#3268, #3269, #3275, #3274 and #3295). Half of the fix is built
(`39a735d8f8`). Only the HELD case remains, and its share of postmerge runs is unmeasured.

What would change it: the count of HELD rc-3 lines against all postmerge runs since 11-08. More
than 20 % passes it. The line stays held.

## P499: re-check of P455 (RED-UNOWNED-OVERFIRES)

Verdict: ACCEPT, upheld as an instance of P436's barrier (major, audit class): every reader of the
`gate` conclusion goes through `classify`.

Instances: 4 false fires in 30 min. The tick's predicate reads the check-run conclusion, the
reader P436 names.

Binding: the barrier route, without the bar. The `#held` line is released with the batch 137
landing.
