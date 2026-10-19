Design review: revise

Round-3 re-review seat for group R10-CI-LAYOUT. Independent: neither a designer nor
the revision author. Reviewed:
- revision 2, `probe/design-ci-rev2` at `d775cc6c` (`DESIGN-P1.md`, `DESIGN-P2.md`,
  `RESPONSE.md` with its `## Round-2 item` sections, `measure/`), cited `P2:<line>`
  and `P1:<line>`;
- against round 2, `probe/design-ci-review2` at `d63cbe42` (N1, N2, item 5, N3, N4);
- against round 1, `probe/design-ci-review` at `f7b28312` (12 items);
- revision 1 `485ae940` and the originals `b7a76185`, `7fdd39c4` for context.

Policy read from `origin/main` at `89e33859`, the same commit revision 2 cites:
`CLAUDE.md`, `judge.md`, `fix-review.md`, `ci-autofix.md`, `gate-scoping.md`,
`orchestrator.md`. Main has not moved since revision 2 was written.

Every command below was run by this seat. Its own instruments are under `tools/`, its
outputs under `ev/`, each disclosed as this seat's (`fix-review.md` step 9).
`<rev2>` is `git archive d775cc6c`; `<review2>` is `git archive d63cbe42`.

## Verdict in one paragraph

All five round-2 items are resolved as asked, the seven items round 2 resolved still
hold, and all six owner rulings and the variant are carried. One new defect blocks,
and it is small. `gate_sim.py` scores revision 2 at a single timing point: a gate
attempt reads at +5 s and completes at +15 s, and the sweep fires 20 s later. Hold
the read fixed and let a hook's re-run attempt finish later, and two scenarios end
red under the newest-completed and every-suite readings while the oracle is green
(R3-1). The cause is the same mechanism N2 fixed: a refresh re-judgement reads red,
the sweep finds it still running and skips it, it then completes red, and nothing
re-sweeps it. The fix is a few lines in `--sweep` plus one perturbation arm in the
simulator. Everything else in this review is non-blocking.

## Re-runs of every changed instrument

Each re-run is byte-identical to its committed output (`ev/reruns/rr_*.txt`):

| instrument (in `<rev2>`) | result |
|---|---|
| `python3 -I measure/rev/gate_sim.py` | `GATE-SIM rc 0`; REV2 41/41 under both chain arms; REV1 30/41; 0 runs cancelled by a re-run |
| `python3 -I measure/rev/gate_replay2.py measure/p2/raw measure/rev/reaches_cc.txt` | `GATE-REPLAY2 rc 0`, 32/32, history 22/22 |
| `python3 -I measure/rev/unitcheck2.py self-test measure/rev/fixtures/tests.yml measure/p1/raw 39158300302` | `SELF-TEST ok (16/16)` |
| `python3 -I measure/rev/codescan_lag.py measure/p2/raw` | option 1 holds at 0 of 17 heads |
| `python3 -I measure/rev/verdict_wait.py measure/p2/raw` | `naive all` 8.10 runner-hours, `grouped all` 8.07 |
| `python3 -I measure/rev/check_writers.py measure/p2/raw` | unchanged |
| `python3 -I measure/rev/c1_counterfactual.py measure/p2/raw` with `--boost 480` and with `--sweep` | equal to `c1_counterfactual_480.txt` and `c1_sweep.txt` |
| `sh measure/rev/c1_consumers.sh HEAD` at `origin/main` | equal to `c1_consumers.txt` |
| `<review2>/tools/plant_unitcheck2.py` against revision 2's `unitcheck2.py` | equal to `n3_review_plants.txt`: Q1, Q1b and the control Q2 are refused; the null gives rc 0 |

One command line in revision 2 is incomplete. `verdict_wait.py` needs `measure/p2/raw`
as its argument. Run with no argument, as `RESPONSE.md`'s N1 prose implies, it raises
`IndexError`. Its enumerator row (P2:1232) gives the argument correctly.

## The five round-2 items

| item | verdict | evidence run here |
|---|---|---|
| N1 | **resolved** | see below |
| N2 | **resolved as asked; R3-1 reopens the convergence half under timing it does not model** | see below |
| item 5 | **resolved** | see below |
| N3 | **resolved** | `rr_n3_review_plants.txt`; `ev/plant_unitcheck3.txt` (one non-blocking residual, R3-3) |
| N4 | **resolved** | at `89e33859`, `tools/pr/prepr.sh:935-938` (`REDS_JQ`, one use at `:967`), `tests/entities.py:25883-25893` (`_PC_EXCLUSION`) and `.github/workflows/pr-contract.yml:253` are the only three `select(.name != "pr-contract")` readers under `.github`, `tools` and `tests`. P2:1019-1020 and R-9 cover all three, with both strings |

### N1: re-runs cannot cancel live runs

- `group: CI-${{ github.run_id }}`, with `cancel-in-progress: false` (P2:216-218).
  - A re-run attempt has the same `run_id`, so it joins a group holding only its own
    run. That holds whatever GitHub does with re-runs and groups.
  - `github.run_id` is allowed in a workflow-level `concurrency.group`. The tree
    already uses it: `arch-score.yml:37-39` and `budget-raise-gate.yml:57-59`.
- Every callee loses its top-level `concurrency:` (P2:1003, U1, U4, U5).
  - Main has six blocks shared between runs, in `codeql`, `governance`, `hassfest`,
    `pr-contract`, `tests` and `validate`. Left in a callee, they would apply to the
    call.
  - The one job-level block that stays, `governance.yml:1066`
    `delivery-status-publish`, is push-only and not required.
- Supersession is `tools/pr/cancel_superseded.py`, unchanged. Read at `89e33859`, it
  never cancels a same-SHA run, needs its caller at the live head, and does nothing
  for a bot-sent caller.
  - Its docstring says it "closes the second half only": it was built beside
    `concurrency:`, not instead of it. With the lanes gone it does the whole job, so
    three cases are no longer superseded.
  - A `pull_request_review` run at a superseded head is not one of its candidate
    events. It waits in its prelude until the cancelled code run completes, then
    judges an old head. That costs runner time only.
  - A fork PR fails the "head in this repository" check, so it gets no supersession
    at all. That costs runner time; see R3-4.
  - A bot-sent newer run cancels nothing. That was already true today, through the
    run-id groups of bot runs.
- **M-5** is in U0 (P2:1080) and in R-7 (P2:1146-1150). Arm (b) is the design's
  control.
- The simulator applies the re-run-joins-its-group rule to every layout, and it moves
  the instrument:
  - revision 1 fails C, R1 and R7;
  - revision 2 with the lanes put back agrees on 30/34;
  - revision 2 cancels 0 runs (`rr_gate_sim.txt`).

### N2: the simulator and the defer rule

- **The double finish is gone.**
  - `step_run` returns at once for an attempt > 1 (`gate_sim.py`, `step_run`).
  - A gate attempt is listed at +0, reads at +5 and completes at +15.
  - Every read due in one tick sees the same state.
- **`gate_model.judging` removes the mutual defer.**
  - A run whose `gate` is listed, and none of whose listed prelude or `<unit> / *`
    jobs is unfinished, is read rather than waited on.
  - X1, X3, X5 and R4-R6 pass under all three readings in both arms.
  - With revision 1's defer rule put back, revision 2 agrees on 22/34.
- **The 50-attempt bound is stated and enforced.**
  - The sweep stops before attempt 45, and `refresh` stops at 45 (P2:695-708).
  - GitHub's limit is confirmed: "A workflow run can be re-run a maximum of 50 times"
    (`ev/gh_docs_read_round3.md`).
- **Not modelled: when the attempt completes, relative to when it read.** R3-1 below
  is what happens when that changes.

### Item 5: the code-scanning wait

- **The analyses query** is keyed `ref=refs/pull/<N>/merge` (else
  `refs/heads/<head_branch>`) with `tool_name=CodeQL`. It matches
  `category == "/language:<leg>"` and `commit_sha == M` (P2:630-646).
  - `M` is the source run's `github.sha`, carried in the new `sha=` token of
    `run-name`.
  - No `sha` query parameter is used anywhere.
- **The category string matches the tree:** `codeql.yml:219` uploads
  `category: "/language:${{ matrix.language }}"`.
- **The analysis job uses the default checkout**, so on `pull_request` the commit is
  the test merge, which is `github.sha`. U0 measures that the `sha=` token equals the
  analyses' `commit_sha` (P2:1080), so the key is not taken on faith.
- **The review's first option fails the data**, which this seat re-read from the saved
  `filter=all` check-runs (`<rev2>/measure/p2/raw`). There is exactly **one**
  `github-advanced-security` `CodeQL` check per head. It is created and completed
  within 2-4 s, 5-8 s before the first uploading leg ends, and it is never re-created,
  even at the 4 heads with 6 uploading legs. So option 1 holds at 0 of 17, as
  `codescan_lag.txt` says.
- **U6 now measures the analysis-to-check lag** (P2:1086). R-10 hands the remaining
  unknown to the owner.
  - This seat's reading of the same data: one check per head, never re-completed,
    makes it **likely** that U6 will find the check does not absorb a later leg.
  - So R-10 is likely to fire at U6, not merely possible. Non-blocking, but see R3-5.

### N3: step order

- `<job>|order` rows refuse Q1 and Q1b. With `coverage|order` admitted, the same swap
  passes and is printed.
- This seat's plants (`tools/plant_unitcheck3.py`, `ev/plant_unitcheck3.txt`):
  - G3, a renamed step that is also moved, is refused;
  - Q1, the control, is refused;
  - the null gives rc 0.
- G1 shows one residual: a map-admitted **gained** step is unchecked for position,
  even before the job's checkout (R3-3).

## The seven items round 2 resolved: still hold

| item | still holds? | evidence run here |
|---|---|---|
| 2 (applicability from the event, prelude cross-check, kind from title, live base) | **yes** | `parse_title` now requires the fifth `sha=` token. Plants B, B2, B3, B4, I2 and I3 are refused under all three readings (`rr_gate_sim.txt`); the item-2 rows of `rr_gate_replay2.txt` are `ok` |
| 3 (code units guarded on `kind == 'code'`) | **yes** | P2:234-256 unchanged; C and D3 pass |
| 6 (held-run approvals kept and retargeted; M-3) | **yes** | section 5 changed one row only (P2:890: the sweep's loop guard gains N1 and N2); M-3 is in U0 and U10 |
| 7 (the four inputs; `DISPATCH -f recheck=true`) | **yes** | P2:199-204, 238-240, 1012 |
| 8 (W1 at its source in PR 1, measured cost) | **yes** | `rr_c1_480.txt`, `rr_c1_sweep.txt` and `rr_c1_consumers_main.txt` are identical; P2:411-420 unchanged |
| 10 (`gate_replay2` drives `gate_model.gate`) | **yes** | 32/32, with 4 new `rev2:` rows; the hooks' null control is now the fixed simulator |
| 12 (a)-(e) | **yes** | (a) P2:955; (b) P2:169-173; (c) P2:558-561; (d) U9 on `probe/ci-layout-all` (P2:1089); (e) P2:829-836 |

## The twelve round-1 items

| item | verdict | evidence run here |
|---|---|---|
| 1 (an edit replaces a pending code run; outside actors cancel runs) | **resolved** | run-id groups: no run can be pending behind another, and none can cancel another (N1). Case E passes, as do R8 and the five XH rows. `cancel_superseded` cancels only at a different head |
| 2 | **resolved** | above |
| 3 | **resolved** | above |
| 4 (stale reds under the every-suite reading; the sweep) | **resolved in design; R3-1 is a residual liveness hole** | without the sweep, 16/34; with it, 34/34 at gate_sim's timing; R3-1 at other timings |
| 5 (code scanning writes a check `pr-contract` can miss) | **resolved** | above; R-10 and U6 hold the remaining unknown |
| 6 | **resolved** | above |
| 7 | **resolved** | above |
| 8 | **resolved** | above |
| 9 (the per-unit null control misses plants) | **resolved** | round 1's plants and the self-test 16/16; N3; R3-3 is non-blocking |
| 10 | **resolved** | above |
| 11 (keyed readers of renamed checks) | **resolved** | N4 above; no other `"pr-contract"` excluder is in `tools`, `tests` or `.github` at `89e33859` |
| 12 | **resolved** | above |

## New defects

### R3-1 (blocking, small): a refresh re-judgement that outlives the sweep stays red

**The race.**
- The sweep re-runs only older gates that are **completed** red. It has to: GitHub
  will not re-run a running run, and `gate_sim.py`'s `hooks()` skips any run that is
  not `completed`.
- A `refresh` attempt reads while the new verdict run V is still busy, so it reads
  red.
- If that attempt is still running when V's green `gate` fires the sweep, the sweep
  skips it.
- The attempt then completes red, and nothing re-sweeps it.
  - Under `nochain`, a red completion fires nothing.
  - Under `chain`, the sweep only acts on a green completion.

**Shown** (`python3 -I tools/rerun_tail.py <rev2>/measure/rev`, `ev/rerun_tail.txt`):
- gate_sim's own World and scenarios, unchanged, except that a hook re-run attempt's
  run reports `completed` TAIL s later than gate_sim's +15 s;
- with TAIL ≥ 35 s, a read-to-completion gap of about 45 s, R7 (approval, then a
  second review) ends **FAIL under newest-completed and every-suite** with the oracle
  green, in both chain arms;
- with TAIL 120-300 s, I4 (a bot head, then an edit) fails the same way;
- the event log is printed: at t=2915 runs 101 and 102 read red; at 2936 run 103's
  gate is green; at 2956 the sweep skips `[101, 102]`, still running; at 2960 both
  complete red.

**Null control.**
- Arm READ-LATE reads 2 s before completion, at any TAIL up to 300 s. It gives 0
  END-BAD, so the hole is the read-to-completion gap and not the duration.
- `tools/timing_perturb.py` (`ev/timing_perturb.txt`) sweeps the uniform constants:
  - GATE 15-120 s, read early or late;
  - REFRESH 1-300 s, SWEEP 1-300 s, PRELUDE 1-30 s.
- Those runs give 0 END-BAD. So the result is robust except to this one asymmetry.

**Why it counts.**
- It is the convergence property item 4 and N2 were raised about, in the reading
  (#2009's) that the tree recorded as real.
- No false green is shown.
- How likely the gap is depends on job teardown plus run finalisation against V's
  gate job plus the sweep's `workflow_run` latency. That is unmeasured, and the
  design's claim (P2:692-694, "each green completion re-runs strictly fewer reds",
  converging) does not depend on it being small.

**Required.**
- `gate.py --sweep` must not leave behind an older `gate` attempt that is running at
  its head. Either:
  - poll it to completion (bounded, fail-soft) and re-run it if it ends red; or
  - let a red completion of a hook attempt at the live head fire the sweep whenever
    a newer `gate` at that head is green.
- State in 4.1 that `gate.py`'s API read is its last step before exit.
- Add a TAIL arm to `gate_sim.py` and score it.

### R3-2 (non-blocking): `judging` rests on an undocumented platform fact

- 4.1 and R-7 say "the jobs API lists a job only once it is queued". The REST docs do
  not say so, and the job `status` enum includes `waiting`, `pending` and `requested`
  (`ev/gh_docs_read_round3.md`).
- **Failure case.** Suppose a `gate` were listed early. In the hop between a verdict
  run's prelude finishing and its callee jobs being listed, that run would read as
  `judging`. An older gate re-judged by `refresh` in that window would then take
  `pr-contract` from an older body.
- **Hardening that removes the dependence:** `judging(run)` also requires every
  required name of every unit in `workset(kind(title), pr)` to be listed and
  completed. Alternatively, U0 measures the fact explicitly as an M-row.

### R3-3 (non-blocking): a gained step's position is unchecked

`ev/plant_unitcheck3.txt` G1: a map-`gained` step inserted at position 0 of
`coverage`, before its checkout, gives rc 0, exactly as appending it does (G2).
- U5 gains such a step (`browser`'s "say the decision").
- Suggested fix: the map names a gained step's predecessor, or the order row includes
  gained steps on the after side.

### R3-4 (non-blocking): fork PRs lose both supersession and `refresh`

- `cancel_superseded` refuses a head outside the repository.
- `refresh` is fail-soft on a fork token.
- So on a fork PR every push runs to the end, and under the newest-completed reading
  the stale-green window is the no-`refresh` one, 2048 s in `gate_sim`.
- Fork PRs are listed as unsampled (P2:1194). R-11 should name this.

### R3-5 (non-blocking): R-10 is likely, so ask the owner now

- The saved data shows one code-scanning check per head, never re-created or
  re-completed. So U6 is likely to stop on R-10, and PR 2 waits on an owner policy
  call there.
- Raising the R-10 question with the owner in parallel with U0, not at U6, keeps it
  off the critical path.

### Editorial (non-blocking)

- The U0 row (P2:1080) still says "`ci.yml` (lanes, …)".
- 4.3's sweep text says "whose latest `gate` is not `success`" (P2:163, 688-689); it
  should say "completed and not `success`", as `gate_sim` models it.
- "never stale-green" (P2:705-706) is not strict: a `refresh` attempt 45 that reads
  green can no longer be re-run red by a later event. The sweep never takes a run past
  44, but `refresh` can make attempt 45 green when the new run is already judging.
  It is reachable only after about 22 events at one head; the measured maximum is 2.
- `RESPONSE.md`'s N1 text should pass `measure/p2/raw` to `verdict_wait.py`.

## Owner rulings: carried?

- **D-1 (approve): carried.** P2:30-31, and P1 section 5 unchanged (the P1 diff from
  revision 1 touches section 4 only).
- **D-2 (`arch-score` gate-required when the diff reaches `custom_components/`):
  carried.**
  - `gate_model.gate` adds `arch-score` only when `reaches_cc`, and only when the
    event names a PR.
  - The `gate_replay2` D-2 rows are `ok`; scenario K passes; U7 plants both arms.
- **D-3 (keep `merge_group`): carried.** It is in `on:` (P2:198); its run gets its
  own run-id group; `gate_model` takes the base from the queue on `merge_group`.
- **D-4 (drop C1 in PR 1 only if the proof is shown covered): carried.**
  `c1_consumers.sh` reproduces at `origin/main`; P1 2(c) is unchanged.
- **D-5 (keep O17 with a soundness check): carried** in U3 (P2:1083), unchanged.
- **Variant (a review event re-runs only `budget-raise-gate` and `gate`): carried.**
  - `BODY_ON_REVIEW = {budget-raise-gate}`;
  - `refresh` and the sweep re-run only `gate` jobs;
  - R7 and X4 (second reviews) now pass at gate_sim's timing; R3-1 is the residual.
- **Two PRs, phase 1 first; a cloud fan-out per unit: carried** (P2 section 8; the
  section 10 table, U0-U10 each on its own `probe/ci-layout-<unit>` ref).

## What would turn this into approve

1. **R3-1:** the sweep cannot leave a running older `gate` attempt red. The read is
   the gate's last step. `gate_sim.py` gains a TAIL arm, and REV2 scores 0 END-BAD
   over it.

R3-2 to R3-5 and the editorial points are recommended, not required.

## This seat's instruments

| command | prints |
|---|---|
| `python3 -I tools/timing_perturb.py <rev2>/measure/rev` | `ev/timing_perturb.txt`: REV2 under swept GATE, GATE_READ, REFRESH, SWEEP and PRELUDE, plus a slow re-run arm |
| `python3 -I tools/rerun_tail.py <rev2>/measure/rev` | `ev/rerun_tail.txt` (R3-1, with the event log and the READ-LATE null) |
| `python3 -I tools/plant_unitcheck3.py <rev2>/measure/rev/unitcheck2.py <rev2>/measure/rev/fixtures/tests.yml` | `ev/plant_unitcheck3.txt` (N3; R3-3) |
| re-runs of revision 2's instruments (table above) | `ev/reruns/rr_*.txt` |
| docs reads | `ev/gh_docs_read_round3.md` |
