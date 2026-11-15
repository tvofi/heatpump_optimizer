# BLOCKED: R11-OUTSIDE-HONEST-STARTS-RUNS, repair round 3

Question: the two red acceptance checks of `tests / fast (3.14)` are false on this branch's own tree under three of four OpenBLAS kernels and owe nothing to the merge with main; in every failing cell the plan that breaks the clause scores lower on the true objective than the plan that keeps it. Which is ruled: (A) the two clauses are restated by `tests/README.md`'s kernel rule, keyed on what does not move across kernels, (B) production is changed until the clauses hold as written, or (C) something else?

No code is pushed with this file. Fixer seat, one box (x86_64, 4 cores, AVX-512), Python 3.14.7, numpy 2.5.4, scipy 1.18.1, `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1`, 2026-11-15, `origin/main` 26dbf7c43e.

## The brief's premise does not hold

The brief reads the reds as the merge's ("at the head and not at your handoff"). Measured, they are the branch's own, and what separates a red run from a green one is the runner's BLAS kernel:

| tree | kernel | switch-weight acceptance | starts-and-energy acceptance |
|---|---|---|---|
| handoff `5d9f00db01` alone | SkylakeX | FAIL | FAIL |
| handoff `5d9f00db01` alone | Haswell | pass | pass |
| `5d9f00db01` merged with `60aefaf7b0` (main before #3593) | SkylakeX | FAIL | FAIL |
| `5d9f00db01` merged with `b046b22d6e` (#3593) | SkylakeX | FAIL | FAIL |
| pull-request head `38c254f3fb` | SkylakeX | FAIL | FAIL |
| pull-request head `38c254f3fb` | Haswell | pass | pass |
| pull-request head `38c254f3fb` | Sandybridge | pass | FAIL |
| pull-request head `38c254f3fb` | Nehalem | pass | FAIL |

Every SkylakeX row prints the two detail strings of job 132772192524 digit for digit. No commit of `23cc7b8e1d..a39627da59` moves either check; of them only #3599 (`ledger.py`), the v10.0.0 stamp and #3593 (the COP learner, `draw_range.py`, docstrings in `thermal_model.py`) touch `custom_components`, and none is read by a bare `optimize`.

CI's own history says the same. `tests / fast (3.14)` on this pull request's earlier heads, all before main was merged in (merge base `23cc7b8e1d`), read from each job's `blas` line and its features summary:

| head | job | cpu | blas | features |
|---|---|---|---|---|
| `fa861694c2` | 132629548295 | EPYC 7763 | Haswell | ALL 5693 PASSED |
| `e5ab2f470f` | 132689801890 | EPYC 9V74 | SkylakeX | the same 2 FAIL, same figures |
| `e5ab2f470f` | 132691608550 | EPYC 7763 | Haswell | ALL 5693 PASSED |
| `fef885f94a` | 132721215803 | EPYC 9V74 | SkylakeX | the same 2 FAIL |
| `cd07913ba0` | 132757194492 | Xeon 6975P-C | SkylakeX | the same 2 FAIL |
| `38c254f3fb` | 132772192524 | Xeon 6973P-C | SkylakeX | the same 2 FAIL |

This is the red-and-green on one commit the live body's `## Red checks` records at `e5ab2f470f` as "which check is unread". The cloud seat pins `OPENBLAS_CORETYPE=Haswell` (`tools/audit/seat/cloud-setup.sh`), the one kernel of the four where both checks pass, which is why no fixer or reviewer round read it: `PYTHONPATH=tests/hastub python3 tests/features.py` at `38c254f3fb` on this box as the seat is set up prints `ALL 5742 FEATURE CHECKS PASSED`.

## What fails, clause by clause, at `38c254f3fb`

**Check "acceptance: a priced plan holds no more starts than the unpriced plan ... and its energy is within one floor step of the relaxed plan"** (design note test 6). Cell (cycling cost, clamp, floor kW); starts priced / unpriced by `runs.start_count`; shipped energy less its relaxed plan's, kWh (bound: one floor step, 0.275 at 1.1 kW, 0.1325 at 0.53); true objective of the shipped plan:

| kernel | (0.25, False, 1.1) | (0.25, False, 0.53) |
|---|---|---|
| Haswell | 2 / 9.27; -0.050; 8.16639 | 2 / 5.53; -0.014; 8.11763 |
| SkylakeX | 1 / 10.07; -0.482; 8.08280 | 2 / 6.59; -0.029; 8.12232 |
| Sandybridge | 1 / 10.07; -0.482; 8.08280 | 2 / 6.59; -0.028; 8.12233 |
| Nehalem | 1 / 10.07; -0.482; 8.08280 | 2 / 6.59; +0.008; 8.12010 |

The starts half holds on all four, with room (1 or 2 against 5.5 to 10.1). The energy half fails on three: the stage ships one run where Haswell ships two, 2.244 kWh against a relaxed 2.726, and that plan scores 8.0828 on the true objective against Haswell's 8.1664. It is the plan a priced start is meant to buy. The design note states the mechanism: the commit's balance outside its band is "penalised and never refused", and the two best candidates' levels are re-solved inside their runs. No production line holds energy to one floor step.

**Check "acceptance: priced on the contributor's table the plan carries no higher a switch weight in starts ..."** (R10-DUTY-SWITCH-PLANNER-PRICE's, restated by this group). Modulating clamped install, switch weight in starts unpriced / priced; the unpriced plan scored under the priced objective / the priced plan's published objective:

| kernel | weight in starts | objective |
|---|---|---|
| Haswell | 2 / 2 | 26.9466 / 26.9177 |
| SkylakeX | 1 / 2 | 27.0180 / 26.9371 |
| Sandybridge | 1 / 1 | 26.9746 / 26.9223 |
| Nehalem | 1 / 1 | 26.9849 / 26.9261 |

On SkylakeX the unpriced solve lands on a one-switch plan and the priced solve on a two-switch plan that costs less under the priced objective, the switches' price included (26.937 against 27.018). The clause races two independent multi-start descents and asserts an order nothing in the stage enforces. The duty-cycle install reads 1 / 1 on all four, and its weight at the combined draw falls on all four (0.997 to 0.4426). The check beside it, "at no higher cost under the plan's own objective", passes on all four.

Null control for the whole table: the same commands on Haswell pass both checks; the perturbation is the kernel alone, same tree, same wheels.

## Why this is a question and not a repair

The brief refuses a fix that only loosens the two checks and sends a claim shown false by measurement back as a design question. Both clauses are shown false as invariants, and making production hold them would mean refusing plans the true objective scores lower (8.0828 for 8.1664; 26.937 for 27.018), a departure from the approved design's "lowest score ships".

- (A), recommended: `tests/README.md`, "A knife-edge optimizer comparison must be measured across BLAS kernels", already rules this shape: "key the verdict on what does not move", "prefer a same-run quantity". Kept as they stand, holding on all four kernels: no step between the running rule and the floor; priced starts no higher than the unpriced plan's; the duty-cycle weights; the shipped plan no higher than the old plan under the priced objective. Replaced: the energy clause by the same-run one the stage does enforce (the shipped plan scores no higher than the projection of its relaxed plan, already checked beside it) with the energy difference reported per kernel in the body; the clamped install's switch-weight clause by the objective comparison already checked beside it. Design note test 6's sentence "its energy is within one floor step of the relaxed plan's" then needs the designer's amendment.
- (B): a hard energy band in `runs.commit` or the stage, and a cap on priced switches at the unpriced plan's count. Not measured; by the tables above it ships the dearer plan on three kernels.
- Pinning a kernel in `tests.yml` is not offered: the lane's unpinned kernel is what found this.

## The other two reds of the brief

- `tests / replay`, `cpu_ratio` over 332.8 on `owner-2026-10-30-away.json`: not in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints, so neither answered nor a block; and not the merge's either. Read from the CI `replay` job's own `cost` line, runner class ref31: main's recorded clean draws in `tests/replay_cost_draws.tsv` (rule: fixture owner, arm clean, `ref_ms` in [29.17, 35.81), one per run and figure; 21 draws, last 2026-11-11) span 224.3 to 269.7, median 239.6; `fa861694c2` 383.2 (job 132629548345); `fef885f94a`, whose `custom_components` equals the handoff's (`git diff --quiet fef885f94a 5d9f00db01 -- custom_components`), 382.1 (job 132721215804); the merged head `38c254f3fb` 375.5 (job 132772192570). The engaged stage costs the owner fixture about 1.57 to 1.60 x main's median; the null is main's own spread in the class, 1.13 x its median at most. The body's `stress` figure did not predict it. No payment was tried in this round: the lane is not owed, and what would pay (fewer re-solved candidates, one descent) is the design's. It will be red on every later pull request once this merges, until `COST_CUTS` declares the level or the stage is made cheaper: that needs a ruling with (A) or (B).
- `tests / mutation`: shards `mutation-pins (2)` and `(12)` of the head's run were still in progress when this was written, so no `mutation-autofix` verdict exists at `38c254f3fb`; run 43700971835 is the run whose `tests` jobs were skipped. `ci-autofix.md`'s wait holds; nothing was pinned by hand.
- The `a3:`, `a4:` ... `FAIL` lines of job 132772192524 are planted cases inside `tests/entities.py`, which that job reports `ok (409s)`; `tests/features.py` is its one failed script (`1 TEST SCRIPT(S) FAILED`).

`git merge-tree --write-tree origin/main 38c254f3fb` reports no conflict at `origin/main` 26dbf7c43e, so nothing was merged.

## For `## Red checks`, once a ruling lands

`tests / fast (3.14)`: a cheaper detector exists. The two blocks below under `OPENBLAS_CORETYPE=SkylakeX` read both reds in about 115 s on this box, against a 603 s `features.py` in a CI lane that draws the kernel by lot. `tests/README.md`'s kernel rule existed and these two checks were written without it.

## Instrument

Run in a checkout of the tree to read, once per kernel (`SkylakeX`, `Haswell`, `Sandybridge`, `Nehalem`):

    export PYTHONPATH=tests/hastub OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_CORETYPE=<kernel>
    P='exec(open("probe.py").read())'
    M2='R.section("R11-OUTSIDE-HONEST-STARTS-RUNS: the start count and committed runs")'
    python3 tools/audit/seat/features_block.py --prelude "$P" 'from types import SimpleNamespace as _DspNS' "$M2"
    python3 tools/audit/seat/features_block.py --prelude "$P" "$M2"

`probe.py` wraps `R.check`, prints each `acceptance` check's verdict and detail, and beside it the figures of the tables above:

    import sys as _psys
    _oc = R.check
    def _probe_check(name, cond, detail="", _oc=_oc):
        if name.startswith("acceptance"):
            print("PROBE", bool(cond), name[:70], detail)
            g = _psys._getframe(1).f_globals
            if "no more starts" in name:
                for k, v in g["_hsr_engaged"].items():
                    free = g["_hsr_solve"](0.0, False, k[2])
                    obj = v.objectives[-1][1]
                    print("PROBE2", k, "starts", g["_hsr_count"](v.space, k[2]),
                          "unpriced", g["_hsr_count"](free.space, k[2]),
                          "dE", round(float(g["np"].sum(v.space - v.relaxed[-1])) * 0.25, 4),
                          "bound", g["_hsr_runs"].floor_kw(k[2]) * 0.25,
                          "obj(shipped)", round(float(obj(v.space)), 5))
        return _oc(name, cond, detail)
    R.check = _probe_check

The first check's four figures per install and its weights in starts are the check's own detail string.
