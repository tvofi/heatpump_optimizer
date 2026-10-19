Design review: revise

Round-4 re-review seat for group R10-CI-LAYOUT. This seat is independent: it is
neither a designer nor the revision author. Reviewed:
- revision 3, `probe/design-ci-rev3` at `8bd4e68f` (`DESIGN-P1.md`, `DESIGN-P2.md`,
  `RESPONSE.md` with its `## Round-3 item` sections, `measure/`), cited `P2:<line>`
  and `P1:<line>`;
- against round 3, `probe/design-ci-review3` at `f731b201` (R3-1 to R3-5 and the
  editorial points);
- against round 2, `probe/design-ci-review2` at `d63cbe42`, and round 1,
  `probe/design-ci-review` at `f7b28312` (12 items);
- revision 2 `d775cc6c`, revision 1 `485ae940` and the originals `b7a76185` and
  `7fdd39c4`, for context.

Policy was read from `origin/main` at `fa5026c4`: `CLAUDE.md`, `judge.md`,
`fix-review.md`, `ci-autofix.md`, `gate-scoping.md` and `orchestrator.md`.
- Main has moved one merge since revision 3's `89e33859`: #2424, which changes
  `tools/policy/agreement.mjs`'s merge-subject guard and adds a delivery row.
- No reader, workflow or citation the design names changed. The three
  `select(.name != "pr-contract")` readers are still `pr-contract.yml:253`,
  `prepr.sh:937` and `entities.py:25884`, and `pr-contract.yml:183/287/293` and
  `policy_lint.mjs` `checkPrBody` read as R3-4 cites them.

Every command below was run by this seat. Its own instruments are under `tools/`, its
outputs under `ev/`, and each is disclosed as this seat's (`fix-review.md` step 9).
`<rev3>` stands for a checkout of `8bd4e68f`, and `<review3>` for one of `f731b201`.

## Verdict in one paragraph

Revision 3 resolves R3-1, the round-3 review's one blocking item, and does it well.
- The sweep's poll closes the hole under:
  - the round-3 seat's unchanged instruments;
  - revision 3's own TAIL, every-attempt and READ-LATE arms;
  - this seat's randomised per-attempt timing.
- Its null control reproduces the round-3 failure.
- R3-2, R3-3, R3-4 and the editorial points are resolved, and R3-5's question was
  put to the owner.
- All 12 round-1 items and the round-2 items still hold, and owner rulings D-1 to
  D-5 and the variant are carried.

Two things block:
- **R4-1: the owner has now ruled R-10 (option B, under mandate), and the design does
  not carry the ruling.**
  - 4.3 still specifies step 5 (the `LAG_MAX` delay).
  - U6 still measures `LAG_MAX` and "stops" if R-10 applies.
  - The B mechanism appears only as a row of an options table. As written, it lists
    alerts by ref, not the alerts of the matched analyses.
- **R4-2: the live controls for the sweep cannot run where the design puts them.**
  `workflow_run` fires only for a workflow file on the default branch. So
  `gate-sweep.yml` on a `probe/ci-layout-*` ref never runs, and three controls are
  unrunnable as written:
  - M-6, the platform check of R3-1's fix;
  - the "sweep enabled" half of M-2, which decides whether `gate-sweep.yml` ships;
  - step 3 of the final combined control.

Both fixes are text plus a small harness. Neither touches the predicate or the
simulator.

## Re-runs of every changed instrument

Every changed instrument was re-run here. Each output is byte-identical to the
committed one (`ev/reruns/rr_*.txt`). Two files differ only by an `rc 0` line this
seat appended: `rr_r3_rerun_tail.txt` and `rr_r3_timing_perturb.txt`.

| instrument | command (from `<rev3>`) | result |
|---|---|---|
| `gate_sim.py` | `python3 -I measure/rev/gate_sim.py` | `GATE-SIM rc 0`. REV2 (revision 3's rules) 42/42 in both arms; REV1 31/42. TAIL 0-300 s, every-attempt and READ-LATE: END-BAD 0. The `poll` ablation fails R7 at 35 s, I4/R7 at 120 s and I4/S2 at 300 s. EARLY: END-BAD 0 with a 25 s window; the `listed` ablation widens the window to 108 s (G, R2, R3, R5). 6 min 8 s wall |
| `gate_replay2.py` | `python3 -I measure/rev/gate_replay2.py measure/p2/raw measure/rev/reaches_cc.txt` | `GATE-REPLAY2 rc 0`, 37/37, history 22/22. The new rows are `ok`: early-listed `gate` deferred, fork refused, attempt 45 FAIL, attempt 44 pass |
| `unitcheck2.py` | `python3 -I measure/rev/unitcheck2.py self-test measure/rev/fixtures/tests.yml measure/p1/raw 39158300302` | `SELF-TEST ok (20/20)` |
| round-3 `rerun_tail.py` | `python3 -I <review3>/tools/rerun_tail.py <rev3>/measure/rev` | END-BAD 0 on all 40 rows, equal to `r3_rerun_tail.txt` |
| round-3 `timing_perturb.py` | `python3 -I <review3>/tools/timing_perturb.py <rev3>/measure/rev` | `TIMING-PERTURB END-BAD total 0`, equal to `r3_timing_perturb.txt` |
| round-3 `plant_unitcheck3.py` | `python3 -I <review3>/tools/plant_unitcheck3.py <rev3>/measure/rev/unitcheck2.py <rev3>/measure/rev/fixtures/tests.yml` | rc 0, equal to `r3_review_plants.txt` |
| round-2 `plant_unitcheck2.py` | same arguments | rc 0, equal to `n3_review_plants.txt` |
| unchanged ones | `codescan_lag.py`, `verdict_wait.py`, `check_writers.py` (each `measure/p2/raw`); `c1_counterfactual.py --boost 480` and `--sweep`; `c1_consumers.sh origin/main` at `fa5026c4` | all identical to their committed outputs, including `c1_consumers` at the moved main |

## Round-3 items

| item | verdict | evidence run here |
|---|---|---|
| R3-1 | **resolved** | see below |
| R3-2 | **resolved** | `judging` (`gate_model.py`) now also requires every name in `workset(kind(title), pr)` to be listed and completed. An unparseable title is never judging. EARLY arm END-BAD 0 with a 25 s window; the `listed` ablation moves the window to 108 s. `gate_replay2` rows 58 (deferred) and the null. M-7 records the platform fact only |
| R3-3 | **resolved** | `after` placement: `UNPLACED` and `MISPLACED` refuse, and the self-test is 20/20. The round-3 plants re-run give G1, G3 and Q1 refused and the null rc 0. G2 is refused because its map places nothing, which is the rule working. P1 section 4's map places `nightly-ha`'s gained step |
| R3-4 | **resolved** | `gate` refuses `same_repo is not True`, so a deleted fork (a null `head.repo`) is refused too. I5 is refused under all three readings, with a false-green window of 0. `gate_replay2` row 60. The supporting claim checks out at `fa5026c4`: `pr-contract.yml:183` reads `.user.login` and `:287`/`:293` pass it as `--author`, and `checkPrBody` refuses any author but `hpo-author` |
| R3-5 | **resolved as asked; the ruling has since been made and is not carried (R4-1)** | `## R-10 owner question` exists (P2:1352-1387) and recommends B |
| editorial | **resolved** | the U0 row says "the run-id `concurrency` group" (P2:1209); "completed and not `success`" (P2:183, 757-758); the attempt cap makes "never stale-green" strict (`gate_replay2` rows 61-62; S2 ends as designed); the `verdict_wait.py` argument is given (`RESPONSE.md`:84, 484, 568) |

### R3-1 in detail

What revision 3 does: the sweep re-runs the older red gates it can, then polls each
older `gate` attempt still running, every 5 s for up to 600 s.
- It re-runs a polled attempt that ends not `success`, under two conditions: the head
  is still live, and V's latest gate is green, completed, and started after every run
  at the head was created (`covers_newest`).
- The gate's API read is now its last step (P2:557-559).
- A TAIL arm was added and scored.

The round-3 requirement was a sweep that cannot leave a running older attempt red, a
read as the last step, and a TAIL arm scoring 0 END-BAD. All three are met. Checked
here:
- **Their instruments, unchanged:** 0 END-BAD across the round-3 seat's 40 TAIL and
  READ-LATE rows and its whole timing grid. Against revision 2 the same tools gave R7
  and I4 (round 3).
- **Committed null:** without `poll` the instrument moves at 35, 120 and 300 s, so
  the poll is load-bearing.
- **This seat's randomised timing** (`tools/jitter_perturb.py`): every attempt,
  first or re-run, draws its own read-to-completion tail and read offset, and each
  `refresh` (1-120 s) and `sweep` (1-300 s) hook draws its own latency. So attempts
  and hooks overtake each other in every order, which the uniform-constant arms
  cannot produce.
  - Revision 3 scores END-BAD 0 over 10 seeds × both chain arms at a maximum tail of
    60 s, and the same at 300 s (`ev/jitter_60.txt`, `ev/jitter_300.txt`). The
    highest attempt seen is 21 of 45.
  - **Disclosed:** the `poll` ablation under the same draws also gives 0, at both 60
    and 300 s. Random hook latencies rarely line up the one asymmetry R3-1 needs, so
    this instrument does not discriminate. It counts as a robustness probe of
    revision 3 (no new failure under mixed orderings), **not** as a control. The
    controls for R3-1 are the committed `poll` ablation and the round-3 tools above.
- **The stated bound** (`tools/poll_bound.py`, `ev/poll_bound.txt`): tails of 500,
  580 and 620 s give END-BAD 0. At 900 s, I4 ends red under newest-completed and
  every-suite, with the oracle green and "run 102 still running at the bound; left as
  is" logged.
  - That is the residual P2:779-781 states: red, never green, until the next event.
  - No false green at the end in any row. Not blocking: M-6 records the real gap.

## The twelve round-1 items and the round-2 items: still hold

Revision 3 changes only: 4.1 (`judging`, the fork refusal, the cap, the read-last
note), 4.3 (the poll, the editorial wording), 4.4, section 10's U0/U5/U6 rows and
final-control step 3, section 11, the new R-10 section, and P1 section 4. Sections 5,
7 and 8 are byte-unchanged.

| item | verdict | evidence run here |
|---|---|---|
| 1 (lost or cancelled runs) | **resolved** | run-id groups unchanged (P2:236). `gate_sim` E, R8 and the XH rows pass, with 0 runs cancelled by a re-run. The fork refusal does not touch `cancel_superseded`'s same-SHA rule |
| 2 (applicability from the event; prelude cross-check) | **resolved** | `gate_replay2` item-2 rows `ok`; plants B-B4, I2 and I3 refused in all three readings. The cap check sits after the prelude checks, so it cannot mask them |
| 3 (code units guarded on kind) | **resolved** | C and D3 pass |
| 4 (stale reds; the sweep) | **resolved** | without the sweep, 16/34; with it, 34/34. TAIL arms and this seat's jitter: 0 END-BAD (above) |
| 5 (code scanning writes a check `pr-contract` can miss) | **resolved in the mechanism, but the owner's R-10 ruling must now land in it (R4-1)** | `codescan_lag`: one check per head, option 1 holds at 0 of 17 |
| 6 (held-run approvals) | **resolved** | section 5 unchanged; M-3 in U0 and U10 |
| 7 (`recheck`, `no-skip`) | **resolved** | U5 row unchanged in that respect |
| 8 (W1 at its source; measured cost) | **resolved** | `c1_*` identical, `c1_consumers` at `fa5026c4` included |
| 9 (per-unit null control) | **resolved** | self-test 20/20; the round-2 and round-3 plants re-run |
| 10 (`gate_replay2` drives `gate_model.gate`) | **resolved** | 37/37 |
| 11 (readers of renamed checks) | **resolved** | the same three readers at `fa5026c4`; #2424 adds none |
| 12 (a)-(e) | **resolved** | unchanged sections; (d) U9 on `probe/ci-layout-all` (P2:1218) |
| round-2 N1 to N4 | **hold** | N1: run-id groups, `rr_gate_sim` "0 cancelled". N2: `judging` hardened, not loosened. N3: order rows plus `after`. N4: readers above |

## New defects

### R4-1 (blocking): owner ruling R-10 (option B) is not carried

The ruling, made under mandate:
- `pr-contract` lists the open alerts of the matched analyses;
- 4.3 step 5 is dropped;
- U6 must show a planted python-only finding listed.

Revision 3 was written before the ruling. It still builds the open question
(`ev/design_greps.txt`):
- **4.3 still specifies step 5** (P2:713-726): wait for the check, then
  `newest matched analysis created_at + LAG_MAX`.
  - P2:493 still bounds `pr-contract` by `LAG_MAX`.
  - P2:731-735 says "U6 measures `LAG_MAX` … the step goes to the owner (R-10)".
- **U6** (P2:1215) still measures LAG and sets `LAG_MAX`, and ends "If the check
  never reflects the python finding, R-10 applies and U6 stops".
- **R-10 in section 11** (P2:1300-1310) and `## R-10 owner question` still read as
  undecided.
- **B lists alerts by ref, not by the matched analyses.** P2:1378 reads
  `code-scanning/alerts?ref=refs/pull/<N>/merge&state=open`. The alerts listing has
  no `sha` or analysis filter (`ev/gh_docs_read_round4.md`), and a ref's open alerts
  follow the newest analysis on that ref per category.
  - The result is the analysis of the newest code run at the head, which need not
    be M's.
  - Example: a recheck dispatch, or a retarget's code run, at the same head that
    uploads after the carried run.
  - On an edit run carrying an older code run, the listing can then disagree with
    the run 4.1 took `codeql` from.
  - The ruling says "the open alerts of the matched analyses", and the design must
    bind the listing to step 4's matches.

**Required.**
1. Rewrite 4.3's wait as the ruling.
   - Steps 1-4 stay: S, the uploaded legs, the key `(R, M)`, and polling until every
     uploaded leg's analysis with `commit_sha == M` is listed.
   - Step 5 and `LAG_MAX` are deleted everywhere (P2:493, 713-735).
   - A new step lists, as reds the body must answer, each open CodeQL alert whose
     `most_recent_instance` has `commit_sha == M` and a `category` among the
     uploaded legs' `/language:<leg>` (`code-scanning/alerts?ref=R&tool_name=CodeQL&state=open`,
     paginated).
   - Or the design reads each matched analysis's results directly
     (`analyses/<id>` with `Accept: application/sarif+json`, which carries
     `github/alertNumber`) and lists those that are open. Say which one, and why.
   - Keep the base-open exclusion (P2:1378) as written: subtract alerts open on
     `refs/heads/<base>` only if U6 shows the merge ref repeats them.
   - Fail closed when an alert read fails.
2. **U6:**
   - delete the LAG measurement and the "U6 stops" exit;
   - plant a finding only the python leg reports and show it in `--red` on the probe
     PR;
   - add a null: the same PR with the plant removed lists nothing;
   - add a carried case: an edit run carrying that code run lists the same alert;
   - add a different-analysis case: a newer code run at the head whose analysis lacks
     the finding. The carried edit run must list from M's analysis, not the newer
     one, or the design must say why the newer is right.
3. Update section 9's reader table and the PR template text the B row names, and
   mark it a policy change. The ruling authorises it; under `CLAUDE.md` the owner
   still approves before merge.
4. Rewrite R-10 (section 11) and the `## R-10 owner question` section as **ruled:
   B**, with the ruling's date and mandate scope. Remove the "question lapses"
   branch, or keep it only as what U6 records.

### R4-2 (blocking): `gate-sweep.yml` cannot run from a probe ref, so its live controls are unrunnable

GitHub: `workflow_run` "will only trigger a workflow run if the workflow file exists
on the default branch" (`ev/gh_docs_read_round4.md`). The tree says the same in
`budget-raise-gate-rerun.yml`'s header ("runs THIS file from the default branch,
never the pull request's copy").

`gate-sweep.yml` does not exist on main until PR 2 merges. PR 1 lands only the
`ci.yml` stub (P1:500-508), and that stub solves this problem for `workflow_dispatch`
alone. So on every `probe/ci-layout-*` draft PR no sweep fires at all, and the design
asks for the following:
- **M-6** (U0, P2:1209): "the sweep fired by the review run's green `gate` logs that
  attempt polled, and re-run if it ended red". This is the platform check of the
  round's blocking fix.
- **M-2's second half** (U8, P2:1217): "then with the sweep enabled, show the code
  run's `gate` re-run green". M-2 decides whether `gate-sweep.yml` ships at all.
- **Final combined control, step 3** (P2:1235-1243): "with the sweep turning the code
  run's `gate` green after the approval", "every `gate` at the head ends green", and
  "M-6's sequence on the assembled layout", on a draft PR from
  `probe/ci-layout-all`.

Each would observe a red that never turns green and be read as a failure of the
design. A fixer would otherwise improvise a harness. The design already handles the
same rule for `workflow_dispatch` (P1:503-505) and for `nightly.yml`'s schedule
(P1:673), so this is a gap in the plan, not in the mechanism.

**Required.** Specify how each of the three is exercised before merge.
- One sound shape is a probe-only driver. A `ci.yml` dispatch input on the probe ref
  (the stub makes the file dispatchable), or a seat-run `gate.py --sweep <run id>`
  with an `actions: write` token, runs exactly the sweep program against the probe
  PR's runs.
- M-6 and M-2 are then scored through it, and the text says the trigger path itself
  (`workflow_run` → `gate-sweep.yml`) is not exercised there.
- Name the first real execution of the trigger path as a post-merge check on main.
  It is the first PR after PR 2 with an approval or edit sequence. Give its rollback,
  as P1:673 does for `nightly.yml`.
- If M-2's ship-or-delete decision then rests only on the first half (sweep disabled,
  which a probe can run), say so.

### Non-blocking

- **R4-3, the poll selects "in progress".** P2:772-773 polls runs "whose `gate`
  attempt was already in progress".
  - After `POST …/jobs/<id>/rerun` the run can be `queued` (or `waiting`) before a
    runner takes it. The re-run pass skips it as not completed, and a literal
    `in_progress` filter skips it in the poll too.
  - In the model this is harmless: a still-queued attempt reads after V's green
    completion. That rests on the queue order, though. Say "not completed" and have
    M-6 record the status values seen.
- **R4-4, `gate-sweep.yml`'s concurrency is unstated.** A sweep may now run for up to
  600 s. If it ever gains a shared `concurrency:` group, a later sweep would replace
  the pending one or cancel the polling one, which is round 1's item-1 mechanism.
  State "no `concurrency:`", as today's re-run file has none, and pin it in
  `entities.py` beside the `timeout-minutes` order pin.
- **R4-5, the chain arm.** "`GITHUB_TOKEN`-triggered events … do not create workflow
  runs at all", and `workflow_run` chains stop at three levels. Re-runs requested
  with the job token are therefore likely the `nochain` arm. The design is scored
  under both, so nothing changes. R-7 can cite the line, and M-6 can record it.

## Owner rulings: carried?

- **D-1 (approve): carried.** P2:88-89; P1 section 5 unchanged.
- **D-2 (`arch-score` gate-required when the diff reaches `custom_components/`):
  carried.**
  - `gate_model.gate` adds `arch-score` only if `pr` and `reaches_cc`.
  - `gate_replay2` D-2 rows `ok`; K passes; U7 plants both arms.
- **D-3 (keep `merge_group`): carried.** It is in `on:`, has its own run-id group,
  takes its base from the queue, and is exempt from the live-PR fork check.
- **D-4 (drop C1 in PR 1 only if the proof is shown covered): carried.**
  `c1_consumers.sh` reproduces at `fa5026c4`; P1 2(c) is unchanged.
- **D-5 (keep O17 with a soundness check): carried** (U3, unchanged).
- **Variant (a review event re-runs only `budget-raise-gate` and `gate`): carried.**
  - `BODY_ON_REVIEW = {budget-raise-gate}`, and `workset(review)` drives the hardened
    `judging` too.
  - The hooks re-run only `gate` jobs.
  - R3, R7 and X4 pass under every TAIL and under jitter.
- **R-10 (option B, under mandate): not carried (R4-1).**
- **Two PRs, phase 1 first; cloud fan-out per unit: carried** (section 8; section 10,
  U0-U10 each on its own `probe/ci-layout-<unit>` ref). R4-2 concerns how three of
  those units' live controls run, not the plan.

## What would turn this into approve

1. **R4-1:** 4.3, U6, section 9, R-10 and the R-10 section written to option B. Step
   5 and `LAG_MAX` gone. Alerts bound to step 4's matched analyses. U6's planted
   python-only finding listed, with its null and the carried case.
2. **R4-2:** M-6, M-2's enabled half and final-control step 3 each given a pre-merge
   driver that runs on a probe ref. The `workflow_run` trigger path is named as a
   post-merge check with its rollback.

R4-3 to R4-5 are recommended, not required.

## This seat's instruments

| command | prints |
|---|---|
| `python3 -I tools/jitter_perturb.py <rev3>/measure/rev 10 60` and `… 10 300` | `ev/jitter_60.txt`, `ev/jitter_300.txt`: revision 3 under randomised per-attempt tails, read offsets and hook latencies, with the `poll` ablation under the same draws |
| `python3 -I tools/poll_bound.py <rev3>/measure/rev` | `ev/poll_bound.txt`: the TAIL arm at 500-900 s, the stated 600 s bound |
| `git grep` at `8bd4e68f` | `ev/design_greps.txt` (R4-1, R4-2) |
| documentation reads | `ev/gh_docs_read_round4.md` |
| re-runs of revision 3's and the earlier seats' instruments | `ev/reruns/rr_*.txt` |
