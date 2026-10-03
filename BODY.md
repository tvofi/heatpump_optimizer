Main's scheduled Tests run 37108891698 (main 2e569748) went red on `mutation-ledger`: `tests/harness_headers.py` killed the comment-only null control because its child `tools/audit/round4/D7/sysid_estimator_frontier.py` was SIGXCPU'd (`rc=-24 stderr=`) by the 240 CPU-s `RLIMIT_CPU` bound, after the same child passed at baseline in the same job.

**Cause: the bound was set too low for the CI runner. It is not BLAS oversubscription again.** #1872's pins were already in that run, and its read-back check passed: the failure list names only the frontier's checks, never "a bounded child runs with every BLAS pool pinned to one thread". The frontier's own cost sits within reach of 240 s on CI:
- On the dev box (M1, single-threaded, pinned) it costs about 92 CPU-s at fab17619, about 146 at dd0f2ace (the F10.11 commit that set 240 against "~100-143 CPU-s"), and 134-178 at this head. The higher figures come from runs that had a concurrent load. The cost is production sysid's. The profile shows `sysid._lm_solve` -> `_simulate_slab_path` -> `ThermalModel.simulate_step`, with most of it under `_declared_night_halfwidth`.
- On CI, `harness_headers.py` takes 201-293 s of wall at baseline under the `--jobs 3` pool. The frontier is about 87% of its child CPU, by the per-child figures this branch now prints.
- "A CPU limit does not move with machine load" (F10.11's premise) does not hold. Two concurrent runs on the dev box raised the frontier from 134 to 176-178 CPU-s, and a CI runner's vCPUs are SMT siblings.

So this is a limit that measurement shows to be wrong, not a cost the harness can shed: the frontier's cost is the production solver it measures.

**Fix (one file, `tests/harness_headers.py`):**
- `run_bounded` returns each child's own CPU (`RUSAGE_CHILDREN` delta), prints it for every executed harness, and names the bound on a kill (`SIGXCPU: the N CPU-s bound was spent cpu=...`). The next kill no longer prints nothing.
- New check per harness: `<rel> costs at most 50% of the CPU bound`. It reds with the figure before the kernel kills without one. This is the failing check, committed first at the 240 s bound (acb93cc1).
- `CPU_LIMIT_S` goes from 240 to 800. That is under the 900 s wall cap, so a spinning child still dies on CPU first, and `harness_headers.py` as a driver stays under `mutation_table.py`'s 1200 s per-driver timeout. The headroom check reds at 400 CPU-s.
- The F10.11 and #1872 comments are corrected to what was measured.

**Class-wide?** The class is "a time bound sized on a dev box, never measured on the runner". It is not "BLAS threads unpinned in a job". `run_bounded` is the only `RLIMIT_CPU` in the tree (`git grep -n RLIMIT_CPU`). The other CPU bound, `tests/stress.py`, already calibrates against a reference solve on the same runner. #1872 already put the BLAS pin in the one place that owns every harness_headers child, whichever job drives it. A job-level pin in the mutation steps would not have changed this run.

**Code ownership:** no file under `.github/workflows/` (code-owned, `@tvofi`) is touched. `tests/harness_headers.py` carries no CODEOWNERS entry.

**Dispatch-equivalent evidence (orchestrator):** `mutation-ledger` is main-only (`github.ref == 'refs/heads/main'`, #1848), so a branch dispatch cannot run it. `mutation-nightly` runs the same `mutation_table.py --scope full --max 40 --jobs 3` pool, baseline and null control on any ref, and `slow` prints `harness_headers.py`'s per-child `cpu=` lines on the runner:

    gh workflow run tests.yml --ref handoff/r9-nightly-ledger-cpu -f recheck=false

Read `slow`'s `########## python3 tests/harness_headers.py` block for the runner's per-child CPU, and `mutation-nightly`'s `null control ... survived every driver` line. One green pool run cannot prove the absence of an intermittent kill. The `cpu=` figure against the 400 s headroom line is the evidence that carries weight.

## Head

461ec95a58b88b6f3a669a6d7d39e73feab7db0a

## Mutation proof

Restore the fix line `CPU_LIMIT_S = 800` to `CPU_LIMIT_S = 240` in a `git archive` copy of the head, then run `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py`. It goes red (rc=1, `1 of 104 HARNESS HEADER CHECKS FAILED`):

    FAIL tools/audit/round4/D7/sysid_estimator_frontier.py costs at most 50% of the CPU bound  [cpu=175.6s against 120s (50% of the 240s bound)]

The same check is red at the failing-check commit acb93cc1 (bound 240, `cpu=164.5s against 120s`). Restored, it passes at the head.

## Null control

The unmodified tree's behaviour on the dev box: at origin/main 12dbd3a5, `sysid_estimator_frontier.py` alone exits 0 in 134.3 CPU-s (`/usr/bin/time -l`). The kill does not reproduce on the dev box under 240, and that is the point: the bound's margin was measured where the cost is lowest. At the head, `harness_headers.py` passes 104 of 104 with the frontier at `cpu=177.5s of the 800s bound`. The bound's own controls are unchanged and green: an idle child past the CPU limit is not killed, a spinning child is killed at the CPU limit, an idle child past the wall cap reports 124, and the BLAS pin read-back.

## Figures

- frontier CPU-s at fab17619 / dd0f2ace / head (dev box): `PYTHONPATH=tests/hastub:custom_components:tests /usr/bin/time -l python3 tools/audit/round4/D7/sysid_estimator_frontier.py`, run in a detached worktree at each SHA
- per-child CPU and the headroom check: `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py`
- CI baseline wall of harness_headers: `gh run view 37108891698 --log --job 111162760555 | grep 'baseline tests/harness_headers'` (ledger) and `--job 111162760619` (nightly); `gh run view 37050037132 --log --job 110980930989 | grep 'baseline tests/harness_headers'` (the killed one)
- profile: `python3 -m cProfile -o f.prof tools/audit/round4/D7/sysid_estimator_frontier.py`
- scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 2 script(s) run`; `tests/entities.py` (ALL 2104 ENTITY CHECKS PASSED) and `tests/harness_headers.py` (ALL 104) green locally

## Red checks

`mutation-ledger` (scheduled, main 2e569748, run 37108891698). The RCA question under `defect-root-cause.md` is whether a cheaper detector existed. **Yes.** F10.11's own pull request ran `harness_headers.py` on CI's `fast` job, where the frontier's runner cost would have been visible against 240 had `run_bounded` reported it. The new headroom check is that detector: one `getrusage` per child and one check per executed harness, with no added runtime. It reds on the pull request whose cost growth crosses half the bound, not on main's nightly later. #1872 named a cause, BLAS oversubscription, without measuring the child's CPU on the runner, and the kill recurred the next scheduled run with its pin in place. That recurrence is the root-cause seat's to weigh.

## Forward-carry

none

## Friction

defect-root-cause: unenforced: #1872 closed a SIGXCPU as BLAS oversubscription with no per-child CPU figure from the runner; the brief for this seat inherited "fixed the sibling" and the same kill recurred with the pin in place (run 37108891698)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
