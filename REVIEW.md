Design review: approve

Round-5 re-review seat for group R10-CI-LAYOUT. This seat is independent: it is
neither a designer nor the revision author. It judges narrowly, as a fifth round
should: a NEW item blocks only if it would make a shipped unit unsound.

Reviewed:
- revision 4, `probe/design-ci-rev4` at `1371a0a6` (`DESIGN-P1.md`, `DESIGN-P2.md`,
  `RESPONSE.md` with its `## Round-4 item` sections, `measure/`), cited `P2:<line>` and
  `P1:<line>`;
- against round 4, `probe/design-ci-review4` at `21c86c18` (R4-1 and R4-2 blocking,
  R4-3 to R4-5 recommended);
- against round 3 (`f731b201`), round 2 (`d63cbe42`) and round 1 (`f7b28312`, 12 items);
- revisions 3 (`8bd4e68f`), 2 (`d775cc6c`) and 1 (`485ae940`) and the originals
  (`b7a76185`, `7fdd39c4`), for context.

Policy was read from `origin/main` at `b87e8f19`: `CLAUDE.md`, `judge.md`,
`fix-review.md`, `ci-autofix.md`, `gate-scoping.md`, `orchestrator.md`.
- Main has moved since the round-4 seat's `fa5026c4`, and only in
  `dev/programme/delivery/*.md` (11 files, `git diff --name-only fa5026c4 b87e8f19`).
- So no reader, workflow or citation the design names changed. Checked here: the two
  `select(.name != "pr-contract")` readers are still `pr-contract.yml:253` and
  `prepr.sh:937`, `_PC_EXCLUSION` is still `entities.py:25884`, and
  `pr-contract.yml:183/287/293` still read and pass `.user.login` as `--author`.

Every command below was run by this seat. Its own instruments are under `tools/`, its
outputs under `ev/`, and each is disclosed as this seat's (`fix-review.md` step 9).
`<rev4>` stands for a checkout of `1371a0a6`, and `<reviewN>` for the round-N seat's ref.

## Verdict in one paragraph

Revision 4 resolves both blocking items.
- **R4-1:** the owner's R-10 ruling (option B) is carried. 4.3's `LAG_MAX` step is
  gone. The new step 5 reads each matched analysis by id as SARIF, so it is bound to
  step 4's matches, and it fails closed. U6 plants a python-only finding and shows it
  listed, with a null, the carried case and the different-analysis case. Section 9
  marks the change policy.
- **R4-2:** a seat-run driver calls the sweep's single entry point on probe refs. M-2's
  ship-or-delete decision rests on the half that a probe can run. The `workflow_run`
  path becomes a post-merge check (section 7, step 3a) with a rollback that cannot
  produce a false green.
- R4-3 to R4-5 are taken as written.

Every changed instrument reproduces here, and so do the round-3 and round-4 seats'
tools against revision 4. All 12 round-1 items, the round-2 items and the round-3
items still hold. Owner rulings D-1 to D-5, the variant and R-10 are carried. This
seat's own probes found no unsound shipped unit. Four non-blocking points, each with a
concrete fix, are below.

## Re-runs of every changed instrument (and the unchanged ones)

Outputs are in `ev/reruns/`. "Identical" means byte-identical to the committed file
at `<rev4>`. Where this seat appended an `rc` line, that is the only difference.

| instrument | command (from `<rev4>`) | result |
|---|---|---|
| `alert_list.py` (new) | `python3 -I measure/rev/alert_list.py self-test` | `ALERT-LIST SELF-TEST ok (16/16)`, identical |
| `alert_list_mutants.sh` (new) | `sh measure/rev/alert_list_mutants.sh` | 5 of 5 mutants refused, identical |
| `driver_arm.py` (new) | `python3 -I measure/rev/driver_arm.py` | `DRIVER-ARM rc 0`, identical. END-BAD 0 at 20/35/65/125 s in both arms; the null (no driver) gives every-suite 16/34 in both arms |
| `gate_sim.py` (one token, R4-3) | `python3 -I measure/rev/gate_sim.py` | `GATE-SIM rc 0`, identical to `gate_sim.txt` (revision 3's output, byte-for-byte), so the R4-3 token is behaviour-identical in the model |
| round-3 `rerun_tail.py` | `python3 -I <review3>/tools/rerun_tail.py <rev4>/measure/rev` | END-BAD 0 on all 40 rows, identical to `r3_rerun_tail.txt` |
| round-3 `timing_perturb.py` | `python3 -I <review3>/tools/timing_perturb.py <rev4>/measure/rev` | `TIMING-PERTURB END-BAD total 0`, identical to `r3_timing_perturb.txt` |
| round-3 `plant_unitcheck3.py` | `python3 -I <review3>/tools/plant_unitcheck3.py measure/rev/unitcheck2.py measure/rev/fixtures/tests.yml` | rc 0, identical to `r3_review_plants.txt` |
| round-4 `jitter_perturb.py` | `python3 -I <review4>/tools/jitter_perturb.py <rev4>/measure/rev 10 60` and `… 10 300` | END-BAD 0 on all 40 rows of each (revision 4 and its `poll` ablation, 10 seeds, both arms), identical to `r4_jitter_60.txt` and `r4_jitter_300.txt` |
| round-4 `poll_bound.py` | `python3 -I <review4>/tools/poll_bound.py <rev4>/measure/rev` | identical to `r4_poll_bound.txt`: END-BAD 0 at 500-620 s; at 900 s (past the 600 s bound) I4 ends red, the oracle is green, and there is no false green, which is the stated residual |
| unchanged | `gate_replay2.py measure/p2/raw measure/rev/reaches_cc.txt`; `unitcheck2.py self-test …`; `codescan_lag.py`, `verdict_wait.py`, `check_writers.py` (`measure/p2/raw`); `c1_counterfactual.py --boost 480` and `--sweep` (`measure/p2/raw`); `c1_consumers.sh origin/main` at `b87e8f19` | all rc 0 and identical, `c1_consumers` included at the moved main |

## Round-4 items

| item | verdict | evidence run here |
|---|---|---|
| R4-1 | **resolved** | see below |
| R4-2 | **resolved** | see below |
| R4-3 | **resolved** | the poll now selects "not completed" (P2:207, P2:842-846), `gate_sim.py:366` is changed to `!= "completed"` with byte-identical output, and M-6 records the statuses seen. One editorial point is non-blocking (N5-4) |
| R4-4 | **resolved** | "no `concurrency:`" is stated in 2.1 (P2:207) and 4.3 (P2:863-867), and pinned in section 9's rerun-list row (P2:1245) at file and job level, beside the `timeout-minutes` pin. The driver runs its sweeps concurrently, which matches |
| R4-5 | **resolved** | R-7 cites both documentation lines (P2:1446-1459). Since no probe can run `workflow_run`, the chain-arm record moves to step 3a (P2:1162-1175), and the "not measured" list says so |

### R4-1 in detail

What the round-4 review required, and where revision 4 meets it:

1. **4.3 rewritten as the ruling, with step 5 and `LAG_MAX` gone everywhere.**
   - `git grep -n LAG_MAX` at `1371a0a6` (`ev/design_greps5.txt`) finds it only in
     text that records its removal: P2:77, 519, 741, 805, 1246, 1368, 1478 and 1546.
   - P1 has no hit.
   - The cost line at P2:517-519 no longer bounds `pr-contract` by `LAG_MAX`.
2. **The listing is bound to step 4's matches.**
   - The new step 5 (P2:740-792) reads `analyses/<id>` with
     `Accept: application/sarif+json` for each matched id. It takes
     `github/alertNumber` from each result.
   - It subtracts the alerts dismissed on R, and also the base-open alerts, but only
     if U6 shows the analysis repeats them.
   - It fails closed on a failed read, on a result without a number, and on a leg
     with no match at the bound.
   - The design says which binding it uses and why (P2:763-787). The `by_ref`
     ablation is the null, and it moves in cases D and D2.
   - The documentation supports this (`ev/gh_docs_read_round5.md`): the SARIF form
     "includes additional data such as the github/alertNumber and github/alertUrl
     properties".
   - `ref=` is documented as changing an alert's `most_recent_instance`, not its
     `state`. So `state` is alert-level, and the dismissed subtraction is sound in
     direction (see N5-2).
3. **U6** (P2:1368):
   - the LAG measurement and the "U6 stops" exit are gone;
   - (1) the plant is listed, and a body that does not name it is refused;
   - (2) the null;
   - (3) the carried case;
   - (4) the different-analysis case, with the rejected by-ref reading recorded
     beside it;
   - (5) a dismissal, (6) the base question and (7) a fail-closed read.

   This is everything the review asked for, and more.
4. **Section 9 and the template text are marked policy:**
   - the `pr-contract.yml` row is marked "**policy: owner ruling R-10**" (P2:1259);
   - the policy-text row (P2:1285) gives the template's new `## Red checks` sentence
     and the steward line, and states that the owner still approves before merge;
   - a new `prepr.sh` row (P2:1260) keeps the local pre-check in step.
5. **R-10 and `## R-10 owner ruling` read as ruled B** (P2:1472-1487, 1534-1586), with
   the date. The "question lapses" branch is removed, and the mandate scope is said to
   be not restated (`nudge.md:7`). The options table is kept as the record.

This seat also probed step 5 itself (`tools/alert_perturb.py`, `ev/alert_perturb.txt`),
driving `alert_list.reds` unchanged:
- **H:** a newer same-`M` upload with an empty python SARIF hides the plant. This is
  the residual R-10 names (P2:1480-1487), and it needs `security-events: write`. It is
  not a new hole: that grant can also dismiss the alert, which the ruling accepts
  (step 5 subtracts dismissals). See N5-3.
- **PB:** exactly 100 rows on page 1, so page 2 is read.
- **DX:** if the dismissed listing by ref omitted a dismissed alert, the step would
  over-list it. That is a false red (fail-safe), never a false green.
- **2L:** one alert number in two legs is listed once.
- **OR:** step 4 relies on the analyses listing's documented `created`/`desc` default
  order (N5-3).

### R4-2 in detail

What the round-4 review required, and where revision 4 meets it:
- **A pre-merge driver for each of the three controls** (P2:1324-1358). U0 builds
  `tools/audit/seat/sweep_driver.py`. It runs `gate.py --sweep --run <id>`, the same
  entry point and argument that `gate-sweep.yml` runs (P2:868-871, pinned at P2:1245),
  and it has `--nochain` and `--chain` arms.
  - M-6 runs through it in both arms (P2:1362).
  - M-2's enabled half runs through it (P2:1370).
  - Final-control step 3 runs through it, with M-6 again under `--chain` (P2:1397-1401).
- **What it does not exercise** is listed (P2:1348-1352).
- **The trigger path is a post-merge check:** section 7 step 3a (P2:1162-1175), inside
  the freeze. It reads back one sweep per first-attempt completion, the same decisions
  as the driver, and every `gate` green, and it gates unfreezing.
- **Its rollback** (P2:1186-1199): disable, drive by seat, fix forward. It is sound,
  because a sweep that does not run leaves an every-suite red red, never a false green.
  In the model, the no-driver null in `driver_arm.txt` leaves every-suite agreeing
  with the oracle on only 16 of 34 sequences, yet the newest-created and
  newest-completed readings stay at 34/34. No row in any arm this seat ran shows a
  false-green window.
- **M-2's decision rests on its first half**, which is said (P2:1370), and P1 step 5b
  says why the stub cannot help (P1:511-517).
- **Rejecting the dispatch-input shape is argued:** it would add a `ci.yml` run at the
  head under test (`RESPONSE.md`:1246-1250). That is sound under the defer rule.

Probed here (`tools/driver_miss.py`, `ev/driver_miss.txt`). `driver_arm.py` models the
driver as a constant start latency, but a driver that diffs the runs listing can
**miss** a completion: `refresh` or another sweep re-runs the run's `gate` before the
driver looks, so the listing already shows the next attempt in progress. This seat's
arm drops such sweeps and imports `gate_sim.py` unchanged.
- Missed sweeps occur at every latency: 0 to 484 per arm.
- END-BAD stays 0 in all 16 rows, and no row has a false-green window. Other sweeps
  and the poll cover each miss.
- So the miss does not make the driver unsound in the model, but it does make "the
  driver changes only when a sweep starts" (P2:1353) slightly untrue. See N5-1.

## Nothing the revision touched broke an earlier item

Revision 4 changes P2 2.1's `gate-sweep.yml` row, 3.3's `pr-contract` reader row and
cost line, 4.3 (steps 5 and 6, the poll wording, no `concurrency:`, one entry point),
section 7 (step 3a and the rollback), section 9 (four rows), section 10 (the driver,
U0, U6, U8 and final step 3), section 11 (R-7, R-10, not-measured) and the R-10
section. It changes one token of `gate_sim.py`, plus P1 step 5b. Checked:
- **Item 1 / N1 (no run lost or cancelled):** the driver's and the sweep's re-runs
  join run-id groups, and `gate-sweep.yml` has no group (R4-4). `gate_sim` E, R8 and
  the XH rows pass with 0 runs cancelled (`rr_gate_sim.txt`), and so do the
  driver_arm rows.
- **Item 4 (stale reds):** the sweep's semantics are unchanged; only "in progress"
  became "not completed". `gate_sim` output is byte-identical, and the round-3 TAIL
  tools and round-4 jitter re-run unchanged (above).
- **Item 5 / R3-5 (code scanning):** step 4 is unchanged, and step 6 still lists the
  `CodeQL` check, so nothing that revision 3 listed is dropped. Step 5 only adds reds.
  `codescan_lag` is identical.
- **R3-4 (fork refusal), R3-2 (`judging`) and R3-3 (`after`)** are untouched:
  `gate_replay2` is 37/37, the self-test is 20/20, and the round-3 plants are refused
  as before.
- **12(e) (caller grant = union of callee grants):** step 5 needs only
  `security-events: read`, which the `pr-contract` caller has carried since revision 1
  (P2:319). No new grant.
- **The new tracked file `sweep_driver.py`** is classified (P2:1261, `INERT` unless a
  test reads it), as `CLAUDE.md` requires.

## The twelve round-1 items, the round-2 items and the round-3 items: still hold

| item | verdict | evidence run here |
|---|---|---|
| 1 (lost or cancelled runs) | **resolved** | run-id groups unchanged (P2:261); `gate_sim` E, R8 and XH pass with 0 cancelled; `gate-sweep.yml` has no group (R4-4). GitHub's documented semantics: a `concurrency` group holds one running and one pending run and cancels others only within the same group. A group per `run_id` therefore never collides, and a re-run attempt keeps its run's id, so it can only re-enter its own group. M-5(b) checks this live |
| 2 (applicability from the event; prelude cross-check) | **resolved** | `gate_replay2` item-2 rows `ok`; unchanged sections |
| 3 (code units guarded on kind) | **resolved** | `gate_sim` C and D3 pass |
| 4 (stale reds; the sweep) | **resolved** | without the sweep, 16/34; with it, 34/34. TAIL, timing grid, jitter, poll-bound and driver arms: END-BAD 0 within the stated 600 s bound |
| 5 (code scanning writes a check `pr-contract` can miss) | **resolved, and closed further by R-10** | step 4 keys on `(R, M)` with `commit_sha`; step 5 lists the matched analyses' alerts whatever the check does; `codescan_lag` 0 of 17 for option 1, identical |
| 6 (held-run approvals) | **resolved** | section 5 unchanged; M-3 in U0 and U10 |
| 7 (`recheck`, `no-skip`) | **resolved** | U5 row unchanged |
| 8 (W1 at its source; measured cost) | **resolved** | `c1_*` identical, `c1_consumers` at `b87e8f19` |
| 9 (per-unit null control) | **resolved** | `unitcheck2` self-test 20/20; round-2 and round-3 plants refused as before. Revision 4's own units carry nulls: U6 (2) and the `by_ref` ablation; M-2's driver-off half; `driver_arm`'s no-driver row |
| 10 (`gate_replay2` drives `gate_model.gate`) | **resolved** | 37/37 |
| 11 (readers of renamed checks) | **resolved** | the same readers at `b87e8f19`; the moved main adds none. Revision 4 adds a `prepr.sh` alert row |
| 12 (a)-(e) | **resolved** | unchanged sections; (d) U9 on `probe/ci-layout-all`; (e) is above |
| round-2 N1 to N4 | **hold** | N1 run-id groups; N2 `judging` unchanged; N3 order rows plus `after`; N4 readers above |
| round-3 R3-1 to R3-5 | **hold** | R3-1: the poll is load-bearing (the committed `poll` ablation moves, `rr_gate_sim.txt`), and the round-3 tools give END-BAD 0. R3-2 to R3-4 are above. R3-5 is superseded by the R-10 ruling, which is carried |

### Adversarial cases against GitHub's documented semantics

- **Concurrency.** `gate-sweep.yml` has no group, so overlapping 600 s sweeps of one
  head neither replace nor cancel each other. A workflow-level group would make a
  third sweep replace the pending one, the documented "at most one pending" rule. That
  is the reason R4-4's pin matters, and the pin exists (P2:1245).
- **Retarget.** On a retarget, step 4's R stays `refs/pull/<N>/merge`, and M is the
  carried run's `sha=` token. A new-base code run uploads an analysis at a new M' to
  the same R. An old-base run that R-11 lets finish can upload after it, and this is
  case D/D2. Step 5 reads by id, so the edit run that carries M' lists from M''s
  analysis, not the late old-base one. `alert_list` cases D and D2 show this, and so
  does this seat's OR probe of the ordering assumption.
- **Gate.** `pr-contract` remains a `gate_required` unit. Step 5 only adds `--red`
  names, and `checkPrBody` needs each verbatim under `## Red checks`, so an unanswered
  alert fails `pr-contract` and therefore `gate`. A failed read fails closed, which is
  red. Step 5 adds no path to a false green except the residual R-10 names (H above),
  which needs the same grant that dismissal does.

## New defects

None blocking. A blocking item here would need a shipped unit made unsound by
revision 4; nothing this seat ran shows one.

### Non-blocking (each with a concrete fix)

- **N5-1, the driver should key on attempts, not on status transitions.** P2:1331-1334
  has the driver start a sweep "for each run attempt it sees newly `completed`" by
  listing runs every 5 s. If the next attempt is already running when it looks, the
  completion is never seen. `ev/driver_miss.txt` shows 14 to 484 misses per arm with
  END-BAD 0 throughout.
  - **Fix:** for each run, read `actions/runs/<id>/attempts/<n>` for every
    `n ≤ run_attempt` the driver has not yet swept. Start the sweep for each completed
    one: only `n = 1` under `--nochain`, every `n` under `--chain`.
  - Have the driver log any attempt it first saw already superseded.
  - Then P2:1353's "changes only when a sweep starts" holds exactly.
- **N5-2, the dismissed subtraction reads by ref.** Step 5 lists
  `alerts?ref=R&state=dismissed`. `state` is alert-level, so this is sound in
  direction: an omission over-lists, as the DX probe shows. But whether a dismissed
  alert whose newest instance on R reads `fixed` (case D) is still returned under
  `ref=R` is not documented.
  - **Fix:** for each alert number left after the base subtraction, read
    `code-scanning/alerts/<n>` and drop it if `state == "dismissed"`. This is
    alert-level and needs no ref.
  - Or keep the listing and add to U6 (5) a dismissal made after case (4)'s upload, so
    the live record covers it.
- **N5-3, two assumptions to pin in U6's record.**
  - (a) Step 4 takes the first matching row as the newest. This relies on the analyses
    listing's default `sort=created&direction=desc`. **Fix:** pass both parameters
    explicitly, and pin them in the `entities.py` row (P2:1246).
  - (b) The same-`M` hand-upload residual (R-10, P2:1480-1487) is dominated by
    dismissal, which needs the same `security-events: write` grant. **Fix:** say so in
    R-10, so a later seat does not treat it as an open hole.
  - Optionally, have U6 (6) also record the severity spread of the listed alerts.
    Under B a `note`-level result is a red the body must answer, where today's `CodeQL`
    check fails only above its severity threshold. This follows the ruling's text, but
    it is worth recording for the owner.
- **N5-4, editorial: "started and not completed".** P2:842-843 says the poll selects
  an attempt "already started and **not completed**", but a `queued` attempt has not
  started in the runner's sense. 2.1's parenthesis (P2:207) makes the intent clear.
  **Fix:** reword 4.3 to "requested and not completed (`queued`, `waiting`, `pending`,
  `requested` or `in_progress`)".

## Owner rulings: carried?

- **D-1 (approve): carried.** P2:64-65; P1 section 5 unchanged.
- **D-2 (`arch-score` gate-required when the diff reaches `custom_components/`):
  carried.** `gate_model.gate` is unchanged; the `gate_replay2` D-2 rows are `ok`; U7
  plants both arms.
- **D-3 (keep `merge_group`): carried.** It is unchanged.
- **D-4 (drop C1 in PR 1 only if the proof is shown covered): carried.**
  `c1_consumers.sh` reproduces at `b87e8f19`; P1 2(c) is unchanged.
- **D-5 (keep O17 with a soundness check): carried.** U3 is unchanged.
- **Variant (a review event re-runs only `budget-raise-gate` and `gate`): carried.**
  `BODY_ON_REVIEW` is unchanged, and the hooks and the driver re-run only `gate` jobs.
  `gate_sim` R3, R7 and X4 pass.
- **R-10 (option B, under mandate): carried.**
  - `pr-contract` lists the open alerts of the matched analyses (4.3 step 5).
  - The `LAG_MAX` step is dropped.
  - U6 shows a planted python-only finding listed, with its null.
  - The change is marked policy, for the owner's approval before merge.
- **Plan (two PRs, phase 1 first; cloud fan-out per unit): carried.** Section 8 and
  section 10 (U0-U10, each on its own `probe/ci-layout-<unit>` ref). The driver adds a
  seat-side harness, not a unit.

## This seat's instruments

| command | prints |
|---|---|
| `python3 -I tools/driver_miss.py <rev4>/measure/rev` | `ev/driver_miss.txt`: the driver arm with missed completions (MISS) against attempt-keyed (KEYED), at 4 latencies, in both arms |
| `python3 -I tools/alert_perturb.py <rev4>/measure/rev` | `ev/alert_perturb.txt`: step 5 under H, PB, DX, 2L and OR |
| `git grep -n LAG_MAX` at `1371a0a6`, plus the reader greps at `b87e8f19` | `ev/design_greps5.txt` |
| documentation read | `ev/gh_docs_read_round5.md` |
| re-runs of revision 4's and the earlier seats' instruments | `ev/reruns/rr_*.txt` |
