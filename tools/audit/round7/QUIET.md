# QUIET — round 7 quiet-window re-measurement

All 14 finders had finished and the box was idle; this window is the re-take of
the two numbers round 7 left provisional or pre-screened. Two jobs, run serially
(never concurrently — the D9 job is a CPU measurement and the D3 job drives
`tests/stress.py`, which calibrates against this machine while it solves):

1. **D9-02** — the one provisional wall/CPU number, re-taken in
   `/Users/timmalmstrom/audit-r7-D9`.
2. **D3-01** — the four mutant sites the D3 finder pre-screened with their
   measured closures, re-run through the **full** gate in
   `/Users/timmalmstrom/audit-r7-D3`.

## Environment, identical for every run in this file

- baseline `f9d6f78243fa65f6fa128d2357752a2ae7f60648`
- python `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` (3.11.5)
- `OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=NUMEXPR_NUM_THREADS=VECLIB_MAXIMUM_THREADS=1`,
  set in the environment before the interpreter starts (numpy is never imported
  unpinned)
- `PYTHONPATH=tests/hastub`, every command run from its own tree root
- gate: `GATE_SCOPE=full GOLDEN_MODE=drift GOLDEN_REF=f9d6f78243fa65f6fa128d2357752a2ae7f60648
  GATE_JOBS=1 ./tests/run.sh`, one run at a time
- the gate lease `/tmp/hpo-gate.lock` was held throughout under label `quiet-r7`
  (`gate_lock.py take` → `renew` between runs, which `run.sh` also does before
  every script → `release` at the end; `status` reports `no lease` after)
- `load1` and `swapins` are printed beside every measurement. `load1` is the
  host 1-minute average at the mark; `swapins` is the delta of the cumulative
  `vm_stat` `Swapins:` counter across the run. The machine is a shared 8-core
  M1 / 8 GB whose residual load is Claude.app, `ANECompilerService` and
  `WindowServer`; no audit seat was running. Swap is not free (5.1–5.4 GB of
  6 GB in use throughout), which is why every row carries the delta.

## Table 1 — D9-02, re-taken

`tools/audit/round7/D9/polish_cost.py`, two runs of the shipped arm, then the
named perturbation and the null control. `thread_factor` is the harness's own
`RESULT thread_factor=1.000`, which is what pinning the five BLAS variables to
one before numpy buys; the harness prints it as a constant and the pin is the
reason it is 1.000.

| quantity | original (fan-out, load1 4.00) | quiet t1 (load1 4.74) | quiet t2 (load1 4.84) | delta | verdict |
|---|---|---|---|---|---|
| polish CPU share of the solve | 0.3511 | 0.3515 | 0.3523 | +0.1 % / +0.3 % | reproduced (tolerance ±5 % on the share) |
| polish CPU ms | 762.1 | 752.3 | 756.3 | −1.3 % / −0.8 % | reproduced |
| solve CPU ms | 2170.4 | 2140.4 | 2146.8 | −1.4 % / −1.1 % | reproduced |
| polish gradients | 164 | 164 | 164 | exact | reproduced |
| main gradients | 278 | 278 | 278 | exact | reproduced |
| total gradients | 442 | 442 | 442 | exact | reproduced |
| polish gradient share | 0.3710 | 0.3710 | 0.3710 | exact | reproduced |
| polish CPU ratio vs `reference_solve` | 40.216 | 39.715 | 40.240 | −1.2 % / +0.06 % | reproduced |
| `reference_solve` CPU ms | 18.9 | 18.9 | 18.8 | — | reproduced |
| swapins across the run | 0 (harness constant) | **0** (measured) | **0** (measured) | — | — |

The two re-takes agree with each other to 0.23 % and with the original to
0.34 %, inside the finding's own stated ±5 % and its "two re-takes within 1.5 %".
The **provisional half of D9-02 is confirmed**: `_lbfgsb_restart` really does
consume 164 of a two-zone DHW solve's 442 batched gradients (37.1 %) and ~35.2 %
of its CPU. The ratio against `tests/stress.py:reference_solve` reproduces at
39.7–40.2 reference solves, i.e. the final half stands unchanged.

| arm | command | polish CPU share | polish gradient share | total gradients | verdict |
|---|---|---|---|---|---|
| perturbation | `polish_cost.py --no-polish` | 0.0000 (solve 2140.4 → 1387.1 ms) | 0.0000 | 278 | moves, to zero, as required |
| null control | `polish_cost.py --dhw-free` | 0.3543 (original 0.3580) | 0.3595 (original 0.3595) | 331 | non-zero — the cost is the polish's, not the DHW planner's |

Note on the harness, recorded rather than fixed: `polish_cost.py` prints
`RESULT swapins=0 count` as a **literal**, not a measurement, and
`RESULT thread_factor=1.000 ratio` as a literal too. The swapins column above is
the real `vm_stat` delta measured beside the harness: 0 swap-ins across each run,
so the literal happens to be true here, and it is not evidence on its own. Under
the Harness-header contract this is the shape `tests/harness_headers.py` exempts
(`SKIP = {"thread_factor", "load1", "swapins", ...}`), so nothing in the gate
reads either line as a measurement.

## Table 2 — D3-01, full-gate confirmation

Four sites, each one production line replaced by the mutant the finder recorded,
applied at the exact line and nowhere else (each matched text is unique in its
file — asserted before the write), committed so HEAD moves, then
`GATE_SCOPE=full GOLDEN_MODE=drift GATE_JOBS=1 ./tests/run.sh`, then
`git reset --hard HEAD~1`.

**A mutant is KILLED only if some driver's outcome is worse than the control
run's**, on the same tree, in the same session. The control is the unmutated
tree; the two reds it carries are named and explained below, and they are
byte-identical in all five runs, so they cannot manufacture or hide a kill. The
comparison is per script exit status, plus `tests/entities.py`'s
`N of M ENTITY CHECKS FAILED` count, plus the whole set of `FAIL` lines.

| site | mutant | tree / HEAD | gate rc | red scripts | entities | seconds | load1 | swapins | verdict |
|---|---|---|---|---|---|---|---|---|---|
| — (control) | unmutated | `6c1e7d96` | 1 | `tests/entities.py` | 2 of 1707 | 1101 | 4.88 | +24 539 | baseline for every row below |
| `legionella.py:528` | GUARD_OFF `if signature == self.ceiling_notice:` → `if False:` | `e8e319b5` | 1 | `tests/entities.py` | 2 of 1707 | 995 | 3.87 | +3 221 | **survived** — killed by none |
| `optimizer.py:3131` | GUARD_OFF `if f.size < n_steps:` → `if False:` | `6bf224ae` | 1 | `tests/entities.py` | 2 of 1707 | 984 | 6.79 | +6 785 | **survived** — killed by none |
| `sensor.py:2547` | GUARD_OFF `if not isinstance(items, list):` → `if False:` | `d4c3da05` | 1 | `tests/entities.py` | 2 of 1707 | 980 | 4.00 | +4 459 | **survived** — killed by none |
| `thermal_model.py:1309` | CLAMP_DROP `t_in = min(t_in, dhw_setpoint)` → `t_in = (t_in)` | `ae78a384` | 1 | `tests/entities.py` | 2 of 1707 | 980 | 3.98 | +3 235 | **survived** — killed by none |

`load1` is the mark taken immediately before the run; the marks immediately
after are 5.95, 6.79, 4.00, 3.98 and 3.56 respectively. These rows are **counts**,
so `thread_factor` does not apply to them and is not quoted per row: the five
BLAS variables are pinned to one before any import, and no count in this table
is a timing.

What every survived row is actually excluding, stated so a later seat does not
have to re-derive it:

- **The differential gate ran and did not fire.** `tests/env_drift.py --all
  f9d6f782…` is in the golden lane of every one of these runs (210 s under
  `GATE_JOBS=1`) and is not among the red scripts in any of them. So for all four
  sites the finding is not only "no assertion observes the arm" but "capturing
  every scenario from this tree and from `f9d6f782` in the same environment
  yields identical values". For `thermal_model.py:1309` — the clamp that is the
  most plausibly behavioural of the four — that is the strongest form of the
  result available here.
- **`tests/features.py`, `optimality.py`, `validate.py`, `edge.py`,
  `backtest.py`, `guard_pins.py`, `finite_boundary.py`, `structural` and
  `typing` rulers, and both node lanes (`card.mjs`, `card_drift.mjs`, the latter
  reporting *identical in all 40 states*) all exited 0 in all five runs.**
- The one line that differs between any two runs' `FAIL` sets is
  `a8:register_once`, and it is harness nondeterminism, not a mutant effect:
  `tests/entities.py:13339` builds the probe's doubled catalog as
  `list(_a8_cat)[:3]` over a **set**, so which three `__dup` names are printed
  varies with `PYTHONHASHSEED`. Null control, run in this window: three
  consecutive `tests/entities.py` runs on the **unmutated** tree printed three
  different name sets (`['assign_entity__dup', 'diagnose_interval__dup',
  'set_away__dup']`, `['apply_topology__dup', 'set_away__dup',
  'set_mode__dup']`, `['apply_manual_plan__dup', 'apply_schedule__dup',
  'diagnose_interval__dup']`) while the check verdict and the `2 of 1707` count
  held constant. The check itself is a boolean and passed in every run.

## The two reds in the control — named, and why they cannot fake a kill

The control run is **not green**, and both of its reds are caused by the round's
own deliverable, not by the baseline. Both are inside `tests/entities.py`, which
exits 1 with `2 of 1707 ENTITY CHECKS FAILED`, and both are the same in all five
runs for the same reason: they are functions of `tools/audit/round7/D3/`, which
no mutant touches.

1. `every tracked file is either measured or deliberately classified` —
   *"these force the FULL suite when touched: `tools/audit/round7/D3/probe.py`,
   `tools/audit/round7/D3/screen.py`, `tools/audit/round7/D3/structure_kill.py`"*.
   This is the refusal `CLAUDE.md` states in its own words: a new tracked file
   must be put in a measured closure or on `tests/closure.py`'s `INERT` list.
   `tools/audit/` is INERT by prefix, but three files are the exception shape
   that `closure.py`'s header-corpus rule pulls back out of it.
2. `the template arm turns the acceptance red on a template that fails its own
   contract (and the real template keeps it green)` —
   *"the real template -> rc=1 (must be 0)"*. `node
   .claude/workflows/policy_lint.mjs` exits 1 on this tree, and its single error
   names the round's own report: `tools/audit/round7/D3/REPORT.md` *"is named by
   `tools/audit/briefs/COMMON.md` but has no cap in
   `.claude/workflows/policy_budgets.json`"*. `COMMON.md:93` names
   `tools/audit/round<N>/D<k>/REPORT.md`, which is exactly this file.

Both fire only because the D3 finder **committed** its artifacts: the 12 files
are tracked in `tools/audit/round7/D3/` at `6c1e7d96`. The same files in the D9
worktree are untracked (`?? tools/audit/round7/`, HEAD `f9d6f782`) and
`policy_lint.mjs` there reports `TOTAL: 0 error(s)`, which is the control for
that explanation. So this is not a baseline defect and not a measurement
artifact: **the round-7 D3 deliverable cannot merge as it stands.** Fixing either
one is a budget/classification change (`policy_budgets.json` and
`tests/closure.py`'s `INERT` list), which is the owner's call and outside this
window's remit, so it is recorded here rather than done.

## Tree-state deviation this window had to correct, and why

`tools/audit/prepare_baseline.sh` builds the instrumenting worktrees by deleting
every earlier round's `tools/audit/round<N>/` and `docs/audit-*.md`,
`docs/backlog.md` — the deliberate wall that keeps earlier findings from steering
a finder — and it leaves those as **tracked deletions** in the worktree's status
("A worktree is a real checkout, so this leaves tracked deletions in its status
rather than an absent file"). The D3 worktree arrived carrying 571 of them.

The script's note says that state "costs nothing the gate can see", and for
`docs/` and most of `tools/audit/` that holds. It does not hold for four files,
because `tests/closure.py`'s own pins read them: `tools/audit/round4/D11/
governance_cost.py` and `tools/audit/round4/D6/claims.json` + `claims.md` are
named one-by-one as the exceptions to the `tools/audit/` INERT prefix
(they were promoted out of it because a gate script reads them). Measured, on
the tree exactly as the finder left it:

```
########## tests/closure.py selftest ##########
  FAIL a full merge does not drop files from card_drift.mjs  [rc=0 after=77 dropped=2
       first=['tools/audit/round4/D6/claims.json', 'tools/audit/round4/D6/claims.md']]
  FAIL a refused merge surfaces merge()'s reason, not just skip-merge-failed  [status='skip-not-under-scoped' log='']
  FAIL and a merge that succeeds carries no merge reason (null control)  [status='skip-not-under-scoped' log='']
  FAIL the #1309 instance maps: governance_cost's cache attributes its source  [_rel(governance_cost.cpython-311.pyc)=None]
4 of 23 closure shrink pins FAILED
>>> FAILED: tests/closure.py selftest
```

`closure.py selftest` is `run_always` in the units lane, so on that tree the gate
is red before any mutant is applied, and a mutant run would not have been able to
tell a kill from the wall. I therefore restored the wall files
(`git reset --hard HEAD`) before any measurement, which makes the tree exactly
what the task describes — `f9d6f782` plus `tools/audit/round7/D3/`, 12 files,
2281 insertions, `custom_components/` and `tests/` byte-identical to the baseline
and `git status --porcelain` empty — and re-ran the control. On the restored tree
**all 23 closure shrink pins pass**, which is the direct evidence that the four
failures above were the wall and nothing else. All five runs in Table 2 are on
that tree; the mutants were applied and reverted on it, and the tree was left in
it (`git status --porcelain` empty, `HEAD` = `6c1e7d96`, production byte-identical
to `f9d6f782`).

The byproduct is worth one line for whoever prepares round 8: the wall as shipped
is not gate-invisible, and `prepare_baseline.sh`'s claim to the contrary was
measured against `tests/entities.py` only. `closure.py selftest` is the script
that sees it.

## What this window does not establish

- It does not re-take any other round-7 number. D9-01 (bytes), D9-03
  (gradients), D3-02 and the other 12 dimensions are untouched.
- It does not make the D3 tree green. Two red checks remain, both from the round's
  own files, and both are described above.
- The four `survived` verdicts are "no driver in the full suite moved", which is
  what the finding claims. They are not a claim that the mutants are equivalent:
  the finder's `probe.py` differential (a concrete input on which the mutant
  answers differently from the shipped line) is the separate half of that, and it
  was not re-run here.
- `optimizer.py:3131`'s line is `if f.size < n_steps:`; the task text for this
  window wrote it as `if m.size < n_steps:`. The mutant applied is the file's own
  text, and it is the same one `confirm2.json` records.
