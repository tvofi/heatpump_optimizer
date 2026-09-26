# Audit round 9: plan

Planning seat, 2026-09-25 (UTC). Requested by tvofi in the project thread, 2026-09-25T12:44Z:
*"1-5 finders across each dimension with scopes with minimal or no overlap. 3 verifiers per
dimension, after verification 1 common judge dedups and judges the surviving ones. Each fix for
each finding should include a full sweep for other instances of the same finding class, and fix
any such instances as well. Each class with 3 or more instances found should trigger a full RCA,
and implement a fix that eliminates the class. Design the plan so that this can be done as
efficiently as possible."*

Planning only. Nothing here starts the audit or files an issue. Measured against `origin/main`
`920c35b8` (after #1616); every count below is re-derived at the round-9 baseline by the command
named beside it, never carried.

Files in this folder:
- `PLAN.md` — this plan.
- `scopes.json` — the 42 finder scopes, one per seat, disjoint within each dimension.
- `check_scopes.py` — proves the scopes are disjoint and complete; `--self-test` is its null control.
- `check_scopes.out` — its output at `920c35b8` (all 15 dimensions `ok`, rc 0).

---

## 0. The shape in one table

| phase | seats | runs where | gate to next phase |
|---|---|---|---|
| R. Readiness PRs | fixers + reviewers | cloud seats, Mac authors/merges | all merged, `check_scopes.py` rc 0 at the baseline |
| A. Find | **42 finders** over 15 dimensions (1–5 each), + 1 leads seat | 10 cloud containers | per dimension: every seat reported |
| B. Verify | **3 verifiers per dimension** (45), pipelined per dimension | cloud, spread across containers | per dimension: 3 votes on every finding |
| C. Judge | **1 common judge**, plus mechanical re-run runners | quiet cloud container(s) | every surviving finding has a verdict and a class |
| D. Class sweep | 1 sweep seat per class with ≥1 verified finding | cloud | every class has an enumerator and an instance count |
| E. File | one issue per class | Mac (as tvofi) | issues and roster PR merged |
| F. Fix | one PR group per class (split at the fixer cap); an RCA seat beside every class with ≥3 instances | fixers and reviewers in cloud, Mac pushes/approves/merges | every class issue closed; ≥3-instance classes `barriered` |

The rest of this plan is what each row means, and why it is the cheapest shape that meets the ask.

---

## 1. Entry criteria (the round starts only when all hold)

1. **Post-round-8 work is done.** Every round-8 issue (#1512–#1549) is closed or carries a
   recorded disposition; the round-8 register PR (evidence under `tools/audit/round8/`, round-8
   section of `docs/audit-2026-09.md`) is merged; the open PR list is empty of programme work;
   `main` is green and stamped. Per the standing goal, #201 is the only open issue.
2. **The readiness PRs in §3 are merged.**
3. **Baseline = the stamped `main` SHA** at that moment. `check_scopes.py --ref <baseline>`
   returns rc 0 there (a new production file lands in a `rest` scope automatically; a file that
   breaks disjointness is a scope edit before the round, not during it).
4. Not blocking: the real-day replay export (design §C of round 8). If tvofi's first recorder
   export has landed under `tests/replay/`, finders in D1, D2, D8 and D12 use it as an input; if
   not, they use `tests/replay/synthetic-dhw-only.json` and the golden scenarios.

## 2. Defaults taken (tvofi prefers the recommended option; each is reversible)

1. **All 15 dimensions run in round 9.** Round 9 is D11/D13's every-third round anyway; D5/D6
   would skip odd rounds under the cadence in `audit-find.js`'s `SEATS`, but the ask is wider
   coverage, so they run too. The cadence table is otherwise left alone.
2. **The instance count that triggers RCA is this round's instances of the class**: judge-surviving
   findings plus instances the class sweep (§D) confirms. Every class in
   `tools/audit/bugclasses.json` already has ≥4 historical instances, so counting history would
   put every class over the line and make the threshold meaningless. One addition: a class that
   is already `barriered` and still gets **any** round-9 instance triggers RCA regardless of count,
   because its barrier failed (process state (c) or (d)).
3. **One issue per class, not per finding.** Round 8 filed 38 issues for 15 fix groups, and each
   issue owes a delivery row and a disposition. Filing the class, with its findings and sweep
   instances as a checklist, is the unit the fix PR closes anyway.
4. **`tuya_heat_pump` is audited at its seam only**: the calls `heatpump_optimizer` makes into it
   (DHW arbiter writes, mode switching) sit in D1-s3 and D12-s2's scopes. A full audit of that
   repository (about 27k Python lines) is a separate round if tvofi wants it.
5. **Fixers run in the cloud**, handing code over on `handoff/<topic>` branches (the hand-off rule
   in project memory); the Mac seat only pushes as `hpo-author`, approves, merges, stamps and files
   as tvofi. This is the largest single saving on the Mac, which was CPU-starved in round 8.

**Needs tvofi's approving review** (policy under `CLAUDE.md`; mandate 2 expired 2026-09-25T08:40Z):
the policy PR in §3 (R2). Nothing else in this plan changes policy or raises a budget.

## 3. Readiness PRs (before the baseline is cut)

| id | what | files | policy? |
|---|---|---|---|
| R1 | **Find driver.** `audit-find.js` dispatches seats from `tools/audit/scopes.json` (this folder's file, moved in-tree) instead of `planSeats`; its Prepare step runs `check_scopes.py --ref <baseline>` and refuses on rc ≠ 0; the round-9 active set is all 15 dimensions; seats are assigned to the containers in §4.3; the post-find "Dedup" step becomes **intake** (schema validation, register rows, no merging: merging is now the judge's). `finding.schema.json` gains `scope` (seat id) and `class_guess`, and the report gains `leads` (§4.2). `rotation.json` keeps recording coverage and yield per step. Classify the new files (`tools/closure.py` `INERT`), or `tests/entities.py` refuses them. | `.claude/workflows/audit-find.js`, `tools/audit/scopes.json`, `tools/audit/check_scopes.py`, `tools/audit/finding.schema.json`, `tests/closure.py` | no |
| R2 | **Policy, one PR.** `verifier.md`: three verifiers per dimension, their lenses (§5), majority kill. `judge.md`: dedup across dimensions first, assign a class to every survivor, a scripted re-run is the judge's own measurement (§6). `defect-root-cause.md` + `root-cause.md`: ≥3 instances of one class in a round owes an RCA **and** a class-eliminating barrier; declining to build one needs tvofi's ruling, not only a failed cost test (§8.3). `D14.md`: its method steps 3–4 are also the post-judge class sweep (§7). `COMMON.md`: the scope wall and `leads` (§4.2). `tools/audit/README.md`: fan-out concurrency per container (§4.3). | `tools/audit/briefs/{verifier,judge,root-cause,D14,COMMON}.md`, `.claude/rules/defect-root-cause.md`, `tools/audit/README.md`, regenerated `.cursor/rules/*.mdc` | **yes — tvofi approves** |
| R3 | **Verify driver.** `audit-verify.js`: three verifiers per dimension with lens-specific prompts, kill on ≥2 refutes, pipelined per dimension; judge phase gets dedup, class assignment and the batch re-runner; the issue writer files one issue per class and emits the draft `wave-r9-groups.json`. New `tools/audit/judge_batch.py`: reads each harness header, runs command, perturbation and null control serially under the gate lease, writes one table row per finding. | `.claude/workflows/audit-verify.js`, `tools/audit/judge_batch.py`, `tests/closure.py` | no |
| R4 | **Round-8 judge instrument notes still owed**, if not already landed through #1510's follow-on: seat temp roots from `TMPDIR`; perturb in memory or hold the lease for on-disk edits; `orjson` pinned in `BASELINE.md`; `pip download` out of the cwd; `prepare_baseline.sh` keeping the `round4/` files `tests/entities.py` opens. Verify each against the tree first; drop the ones already done. | `tools/audit/prepare_baseline.sh`, `tools/audit/README.md` (harness contract lines ride R2) | no (README lines ride R2) |
| R5 | **Merge-conflict preconditions for phase F**: #1577 (content-anchored mutation ledger) and the `ledgermerge` driver PR merged, and the pending ledger-layout redesign landed. Phase A–E do not need them; phase F must not start without them (§9.4). | — | no |

R1, R3 and R4 touch disjoint files and can be fixed and reviewed in parallel; merge one at a time.
R2 goes to tvofi as soon as it is drafted, since it is the only item that waits on a person.

---

## 4. Phase A: find (42 seats)

### 4.1 Scopes

`scopes.json` gives each seat a set of **cells**. A cell is (file, method step) — plus a third
axis for D0 (price profile), D10 (quality tier) and D14 (bug class). Within a dimension every cell
belongs to exactly one seat; `check_scopes.py` proves it and prints each seat's size. At
`920c35b8`:

`python3 check_scopes.py --repo <checkout> --ref <sha>` → 15 × `ok`, rc 0, 42 seats
(`check_scopes.out`). `--self-test` duplicates one D1 block and empties a D2 seat; the checker
refuses both (rc 1 on the perturbed file, reported as `SELF-TEST passed`).

| dim | seats | how it is split | why that axis |
|---|---|---|---|
| D0 price optimality | 3 | s1 challengers on winter profiles; s2 on summer/shoulder/negative/flat; s3 null-control race, MPC masking, DHW↔space decomposition | the grid is the work; the step split alone would put the whole grid on one seat |
| D1 robustness | 5 | by module: s1 persisted stores and learners; s2 lifecycle and coordinator; s3 control and actuation incl. DHW arbiter and the Tuya seam; s4 solver path and executor boundary; s5 external inputs (`rest`) | every D1 step applies to every module, and the modules are where the defects live |
| D2 math/physics | 4 | by step: thermal model; COP and objective; tariff and prices; estimators | each step is a different model |
| D3 test gaps | 3 | by module: `coordinator.py`; solver/tariff modules; `rest` | mutant pre-screens are per module and CPU-heavy, so a module split parallelises them |
| D4 UI/UX | 2 | card; config flow, translations, services UI | card needs Chromium; the flow does not |
| D5 docs | 2 | user docs; code comments | files mode: each file once |
| D6 claims | 2 | README; `docs/` | README carries the most claims |
| D7 architecture | 3 | metrics and this year's train; sysid plant, learner freeze, buffer; dead code | three unrelated methods |
| D8 sensors | 3 | sensor/binary_sensor matrix; other platforms' matrix; ordering, naming, defaults, graduation | the matrix is the heavy part |
| D9 CPU/memory | 2 | solver-path CPU; everything else + the gate's 2× detection | the solver dominates cost |
| D10 quality scale | 2 | bronze+silver; gold+platinum + test coverage | tier split |
| D11 governance | 2 | CI, tools, hooks, workflows; rules and the policy corpus | mechanism vs prose |
| D12 generalization | 3 | installation axes; heat-pump axes incl. Tuya/Modbus control; usability, null control, perturbation | the axes are independent |
| D13 process yield | 1 | all steps | one population (merged PRs), splitting it double-counts |
| D14 bug classes | 5 | by class: P1+P6; P2+P8+I4; P3+P4+P5; P7+P9+P10; I1+I2+I3+I5 | related classes share detectors (data contract; divergent predicates; solver/model; time/UI/loop; instruments) |

Overlap **across** dimensions is intended (a guard is both a D1 and a D3 question); the judge's
dedup (§6) removes the duplicates it produces. Overlap **within** a dimension is zero by
construction.

### 4.2 The scope wall and `leads`

A finder measures only its own cells. Something it notices outside them is a **lead**
(`{owner_seat, file, symbol, what}`), not a finding and not a harness. Leads are routed by the
driver: to the owning seat if it is still running; otherwise to one **leads seat** that runs after
the fan-out and turns a lead into a finding only with an executed number under `COMMON.md`. This
keeps the zero-overlap scopes from losing what a seat sees in passing, without paying for two seats
measuring the same thing.

### 4.3 Where the seats run

Each cloud thread is its own container, so containers, not one shared box, are the unit of
contention. `tools/audit/README.md` allows at most three compute-heavy finders per box and keeps
Chromium apart. Ten containers:

| box | seats (heavy in bold) |
|---|---|
| B1 | **D0-s1**, **D3-s1**, D5-s1, D6-s1, D10-s1 |
| B2 | **D0-s2**, **D3-s2**, D5-s2, D6-s2, D10-s2 |
| B3 | **D0-s3**, **D3-s3**, D11-s1, D11-s2, D13-s1 |
| B4 | **D9-s1**, **D2-s1**, D1-s1, D1-s2, D8-s3 |
| B5 | **D9-s2**, **D2-s2**, D1-s3, D1-s5, D7-s3 |
| B6 | **D2-s4**, **D12-s1**, **D1-s4**, D7-s1, D8-s1 |
| B7 | **D12-s2**, **D12-s3**, **D7-s2**, D2-s3, D8-s2 |
| B8 | **D14-s1**, **D14-s2**, **D14-s3** |
| B9 | **D14-s4**, **D14-s5**, D4-s2 |
| B10 | D4-s1 (Chromium) alone, then the leads seat |

Every container runs the same setup (baseline export, venv with the pinned numpy/scipy/orjson,
warmed drift cache, merge drivers) from one script, so a missing package cannot silently change a
number on one box only (round 8's `orjson` note). Timing numbers stay provisional during the fan-out
and are re-taken on the quiet container (§6).

### 4.4 What a finder returns (unchanged, plus three fields)

`COMMON.md` and `finding.schema.json` as they stand — executed number, instrumented symbol,
perturbation, metric definition, null control, leave-one-out, `phenomenon_property`, `seam_rule` —
plus `scope`, `class_guess` (a ledger id, or `new`) and the report's `leads`. `seam_rule` already
makes every finding carry the command that enumerates its seams; phase D starts from it.

---

## 5. Phase B: verify (3 per dimension, 45 seats)

**Pipelined.** A dimension's three verifiers start the moment its last finder seat reports; they
do not wait for the whole round. Put the three members of a triple on three different containers,
so an environment defect cannot produce three agreeing wrong numbers.

**Every verifier votes on every finding of its dimension**, refute-first, with an executed number
(`verifier.md` steps 1–5 all still apply). To make three votes worth more than one vote three
times, each verifier also owns one **lens**, which it runs in full on every finding:

| lens | owns |
|---|---|
| V1 reproduce | re-run the finder's harness exactly; run the perturbation (void if it does not move); null control; leave-one-out on aggregates |
| V2 independent | its own harness and metric definition beside the finder's; for a test-gap claim, the single-line production mutation the suite misses and the file it lives in |
| V3 reach and class | reachable in real Home Assistant and not only through `tests/hastub` (`tests/ha_contract.py`); severity by consequence; runs the finding's `seam_rule` and says whether it enumerates the phenomenon's seams or only the demonstrated one; confirms or corrects `class_guess` |

**Kill rule:** two or more `refute` votes, each with an executed number, kill the finding at panel.
A refute resting on timing alone counts as `unresolved`, not as a refute. One refute: the finding
goes to the judge marked `disputed`. This is rounds 1–7's majority kill, restored now that there
are three votes again; it is what keeps the judge's queue short.

**Sharding.** A dimension with more findings than one triple can take (set in R3; start at 15)
gets a second triple, split by finder seat, so a triple never verifies across a scope boundary.

---

## 6. Phase C: one common judge

The judge owns every verdict and the dedup, alone. Its order is chosen so it measures each
mechanism once:

1. **Dedup first, across all dimensions.** Cluster survivors by instrumented symbol, files,
   `phenomenon_property` and `class_guess`. For each cluster, pick the canonical finding and show
   the others are the same mechanism with a number: the canonical finding's perturbation moves the
   other harness too. Merged findings keep their ids in the register (`merged into <id>`).
2. **Mechanical re-runs are scripted.** `tools/audit/judge_batch.py` executes every canonical
   finding's harness, perturbation and null control from its header, serially, under
   `tests/gate_lock.py`, on the quiet container, and writes one row each with `load1` and
   `thread_factor`. The provisional timing re-takes (the old quiet window) are the same run. If the
   queue is long, the same script runs on a second quiet container as a **runner**: it measures, it
   does not decide. The judge reads every row and re-runs by hand anything disputed, void or out of
   tolerance.
3. **Verdicts** under `judge.md`: `verified` / `weakened(sev)` / `refuted` / `unreproduced`,
   `stop_rule_class`, and **a class for every survivor**: an existing `bugclasses.json` id, or a new
   one (`P13…`, `I6…`) with its mechanism in one line.
4. Output: `JUDGE.md`, `JUDGE.json`, the per-step yield for `rotation.json`, and the class list
   that phase D takes.

---

## 7. Phase D: class sweep (the "full sweep" for every finding)

The sweep is done **once per class, before any fixing starts**, not once per finding inside each
fix. That is the efficiency: findings in the same class share one enumerator, and the instance
count that decides RCA is known before the fix is scoped, so the RCA seat can start beside the fix
on day one instead of after it.

One sweep seat per class with at least one verified finding, all in parallel, in the cloud. Each
runs `D14.md` method steps 3–4 for its class:

1. **An enumerator**: a harness that lists every seam of the class across the whole package, not
   only the demonstrated ones (starting from the findings' `seam_rule`s).
2. **Positive control**: it re-finds every round-9 finding in the class, and the ledger's
   historical instances at their pre-fix commits where it can.
3. **Null control**: zero on a clean fixture. **Perturbation**: it moves under a one-line
   re-introduction.
4. **Every returned seam dispositioned**: `instance` (a defect, with a probe that fails on it —
   the fixer reuses it as the failing test), `guarded` (with the guard named), or `not applicable`
   (with the reason).
5. **The count**: N = verified findings + confirmed sweep instances. N ≥ 3, or any instance in a
   class already `barriered`, sets the class's RCA flag.

The sweep's instance claims are checked by the fix reviewer, who re-runs the enumerator at the
merge base and at the head (`fixer.md` step 8, which already requires exactly this).

---

## 8. Phases E–F: file, then fix by class

### 8.1 File

On the Mac, as tvofi, with round 8's `file_issues.py` pattern: one issue per class, labels
`audit`, `round-9`, `class:<id>`, `sev:<highest>`, body = the class mechanism, each finding
(id, severity, harness, verdict), each sweep instance, the enumerator command, and `RCA: owed` or
`RCA: not triggered (N=<n>)`. #1548 (I3 install hash-pins) and #1549 (I4 yield metric), deferred by
round 8 to "the next D11/D13 round", are folded into their classes' issues here.

The roster `wave-r9-groups.json` is written by the same step: one group per class, its issue, file
set, `after` dependencies, and the RCA flag. `brief_lint.mjs` must pass on it (exit code and error
lines read, not the summary).

### 8.2 One fix group per class

A class group ships, in one PR when it fits `fixer.md`'s cap (five findings, about 400
production lines):

- a failing test per instance (the sweep's probe), importing the production symbol;
- the fix for every instance the sweep returned — the demonstrated findings and the swept ones
  alike;
- `## Figures` listing every seam the enumerator returns at the head against its disposition
  (`fixer.md` step 8);
- the barrier, when the class is RCA-flagged (§8.3).

**Over the cap**, the class splits into instance PRs by subsystem (disjoint files, so they run in
parallel) and ends with a **barrier PR** that lands last and shows the enumerator at zero on
`main`. No allow-list of known seams is ever added to make a barrier land early (`fixer.md` step 14).

### 8.3 RCA and eliminating the class (N ≥ 3)

- **An RCA seat starts when phase D flags the class**, beside the fix and never inside it
  (`root-cause.md`): the named cause, the process state (a)–(d) with evidence, the class search
  (the sweep already did most of it), and the cost test with numbers.
- **Elimination is owed** (tvofi's ask, written into policy by R2). The barrier is the cheapest
  form that makes a new instance fail CI: preferably a structure that cannot express the defect
  (one validated load layer, one resolution function, a unit-carrying type), otherwise the
  enumerator promoted into an existing `tests/` script as a zero-seam check. It is demonstrated
  failing on each round-9 instance re-introduced and passing on the fixed tree, and it does not
  fire on a healthy tree (`defect-root-cause.md`, "A detector must be shown to detect").
- **The cost test chooses the form, not whether to build one.** If the RCA seat finds no barrier
  that passes "The bound" (no degraded architecture or functionality), it writes that up with the
  numbers and asks tvofi for a ruling; it does not record a refusal on its own.
- The class's `bugclasses.json` entry moves to `barriered` with the CI command, in the barrier PR.
- A barrier that needs a structural budget raise follows `CLAUDE.md` rule 2: pay first; a raise
  is asked of tvofi before the push.

### 8.4 Review

The adversarial fix reviewer runs in a cloud session different from the fixer's, at the head SHA,
with the finder's harness and the sweep's enumerator, both ends (`fix-review.md`). The RCA seat's
barrier is reviewed the same way.

---

## 9. Execution and throughput

### 9.1 Who does what

| work | where | identity |
|---|---|---|
| finders, verifiers, judge, runners, sweep, RCA, fixers, fix reviews, gate/stress/mutation runs | cloud threads (containers) | none on GitHub; fixers hand off on `handoff/<topic>` branches |
| push as `hpo-author` (`app_push.sh`), verdict comments (`app_comment.sh`), approvals (`app_approve.sh`), merges (`--match-head-commit`), stamps, filing issues | the local fix orchestrator on tvofi's Mac, thread "Triage and fix open issues" | `hpo-author` / `hpo-approver` / tvofi per decision 0011 |
| relaying tasks and results between cloud and Mac | the coordinator | — |

Only R2 and any budget raise wait on tvofi's own review.

### 9.2 The critical path

A → B → C → D is the audit's critical path, and each arrow is per dimension (A→B) or per class
(D→F) rather than a round-wide barrier wherever the contracts allow:

- verifiers of a dimension start when its finders finish;
- the judge can start dedup on the first finished dimensions and re-run as runners feed rows,
  but issues no verdict until every dimension's panel is in (dedup needs the whole set);
- sweep seats start per class as the judge assigns classes;
- a class's fix group starts as soon as its issue is filed, subject only to `after`.

### 9.3 Parallelism in the fix wave

Groups whose file sets (from the sweep) are disjoint are fixed and reviewed in parallel. The
merge queue stays one PR at a time, and a branch merges `main` in only when it is next to merge or
CI cannot run (tvofi, 2026-09-24).

### 9.4 Keeping ledger conflicts out of the way

Round 8's analysis (`/mnt/project-files/merge-conflicts/ANALYSIS.md`) found about three of four
conflicts in files that record measurements. Phase F therefore does not start before R5 (content
anchors, `ledgermerge` driver, ledger-layout redesign). In addition, the roster brief for every
group:

- installs both merge drivers in the fixer's clone before the first commit;
- adds its tests under its own class-named block in `tests/features.py` / `tests/entities.py`,
  placed in sorted order rather than at end-of-file, so two groups' insertions do not collide;
- re-records budgets and closures once, at the handoff, not after every edit;
- touches the claim files only when it claims drift (`claim-files.md`).

---

## 10. What the round records about itself

So that round 10 can be judged against round 9 with numbers, the driver writes into the register
and `rotation.json`, per seat and per dimension: findings returned, survivors after panel, after
judge, and merged by dedup (a within-dimension duplicate is a scope defect, fixed in `scopes.json`
before round 10); leads raised and converted; per-step yield; wall-clock per phase from the
workflow log. D13 reads these next round.

The stop rule stays `D14.md`'s: two consecutive rounds with no `open` class gaining an instance,
no new invariant break in the nightly replay, and no high or critical production finding.

---

## 11. The brief every seat gets (template)

Each dispatch brief, finder to fixer, opens with these lines verbatim and then its role-specific
part:

> Before doing any work, read `CLAUDE.md` in the repository and all related rules files
> (`.claude/rules/`, and the role contract for your seat under `tools/audit/briefs/`), and follow
> them. Pass this rule on in every sub-agent brief you write.
>
> Never refer to the project owner as "Tim" anywhere, especially on the public repository (PR
> bodies, commits, comments, issues, delivery notes). Call them "tvofi". A PR body's attribution
> line is `_Requested by **tvofi**_` and carries no claude.ai project link. Pass this rule on in
> every sub-agent brief you write.

Then, by role:

- **Finder**: dimension, seat id, the baseline SHA and export path, the cells from
  `scopes.json` (deep focus = every step in the seat's blocks), the container's resource rule, and
  "outside your cells, record a lead, do not measure".
- **Verifier**: the dimension's findings with harness paths and nothing else, the lens, the
  kill rule, and "your triple's other members are on other containers; do not coordinate numbers".
- **Judge / runner**: `judge.md`, the dedup-first order, the batch script, the lease.
- **Sweep**: the class, its findings' `seam_rule`s, `D14.md` steps 3–4, the disposition vocabulary.
- **RCA**: `root-cause.md`, the class, the sweep's output, the elimination duty and when to ask
  tvofi.
- **Fixer / reviewer**: the roster group, `fixer.md` / `fix-review.md`, the hand-off branch rule,
  and §9.4's conflict conventions.

---

## 12. Risks and their controls

| risk | control |
|---|---|
| Disjoint scopes starve a cross-module mechanism (a defect that spans two seats' files) | cross-dimension overlap is kept; `leads`; D14's class seats are not file-scoped at all |
| 42 seats return more findings than one judge can re-measure | panel majority kill; dedup before re-measuring; scripted re-runs with runners |
| A sweep over-reports seams as instances and bloats the fix | every `instance` needs a failing probe; the reviewer re-runs the enumerator at both ends |
| Elimination barriers cost more than the class (the bound) | the RCA seat chooses the form by cost test and asks tvofi when none passes, per R2 |
| The Mac becomes the bottleneck again | fixers moved to the cloud; the Mac only pushes, approves, merges, stamps and files |
| Ledger conflicts multiply merges | R5 is a hard precondition for phase F; §9.4 conventions |
