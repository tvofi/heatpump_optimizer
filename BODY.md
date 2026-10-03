Main's scheduled Tests run 37108891698 (main 2e569748) went red on `mutation-ledger`. `tests/harness_headers.py` killed the comment-only null control because its child `tools/audit/round4/D7/sysid_estimator_frontier.py` was SIGXCPU'd (`rc=-24 stderr=`) at the 240 CPU-s `RLIMIT_CPU` bound, after the same child had passed at baseline in the same job.

**Cause: mutation_table.py's `--jobs 3` pool bills the same work at least 2.48x the CPU of a serial run, and harness_headers.py's CPU bound judged a pooled child.**
- On the runner, serially, the frontier costs 96.8 CPU-s (`slow`, run 37130986490, job 111225908327, harness_headers.py's own `cpu=` line). The same harness was killed at 240 CPU-s on the pooled null control. So the bound was not sized on a cheap machine: the dev box (M1, 124-178 CPU-s) is the expensive one.
- It is not BLAS oversubscription. #1872's pins were in the failing run's tree (2e569748 is its merge), and its read-back check passed there: the failure list names only the frontier's checks.
- The frontier's cost is production sysid's (`_lm_solve` -> `_simulate_slab_path` -> `ThermalModel.simulate_step`, most of it under `_declared_night_halfwidth`). The harness only drives it.

**Countermeasure: remove the cause.**
- `tests/mutation_table.py`: `tests/harness_headers.py` joins `EXCLUSIVE`, as stress.py is. In the baseline, the null control and every mutant it drives, it now runs with no other driver in flight, so the pool bills it what run.sh's serial lane bills it.
  - The gate lease is unchanged. A new `LEASED = ("tests/stress.py",)` keeps `_leased_if_exclusive` taking it for stress.py alone, as `gate-scoping.md` states: "every other script runs unleased".
  - Under `--scope changed` (the PR `mutation` job), `deferred_drivers` now defers harness_headers.py's baseline and null control too, until a mutant survives every shared driver. That is less work on a PR. The cost is the headline semantics `deferred_drivers` already documents: a killed null control that no surviving mutant reaches leaves the table PASSED, with a line naming the driver as never run. The nightly (`--scope full`) stays eager.
- `tests/harness_headers.py`: each child's bound is sized from the serial figure on the runner, and every bound stays under the 900 s wall cap.
  - The frontier gets 480 CPU-s, about 5x its 96.8. It costs 124-178 on the dev box, so a seat's local run stays under the 240 headroom line.
  - Every other child gets 60 CPU-s. On the runner they cost 0.3-4.3, and on the dev box 0.6-8.1. A spinning cheap harness now dies in a minute, not in 800 s; this is the reviewer's per-child bound.
  - A check refuses an override that names a harness the script does not execute.
- Kept from round 1: the per-child `cpu=` print, and the kill message (`rc=-24 SIGXCPU: the N CPU-s bound was spent cpu=...`).
- The headroom check is re-stated as what it now guards: `<rel> costs at most 50% of its CPU bound`. With the driver exclusive, a PR's serial run and the pool's run bill the same work, so the frontier's line at 240 s (2.48x its runner cost) reds on the pull request whose cost growth crosses it, and on the nightly no earlier.
- Pooled per-child CPU at the null control: not added. With the driver exclusive there is no pooled run of it left to show, and `null_control_verdict` would need a new output path in a code-owned file to print the serial figure the `slow` job already prints.

**Nightly wall time (the hard constraint).** This is bounded from job logs, not measured on a run.
- An exclusive harness_headers.py run costs T = 117 s of wall: the runner's serial figure, `slow` run 37130986490. It is paid by the baseline, the null control and every mutant no shared driver kills (S, the survivors).
- Removed from the pool: the same 2 + S pooled runs, at 201-293 s each on one of three workers. Killed mutants on which the pool's helper phase ran harness_headers.py speculatively no longer run it at all.
- Net added wall is therefore at most (2 + S) x 117 s, if the pooled runs freed no makespan. It is about (2 + S) x (117 - 250/3) ≈ (2 + S) x 34 s if they shared it evenly.
- S over the last five mutation-nightly runs: 4, 8, 3, 8, 8 (36543810424 to 37108891698). mutation-ledger's 37050037132 had 1.
- At S = 8 that is about +6 min expected and +20 min bound. The worst recent night, 286 min on 2026-10-02 (S = 8, 86% of the 330 min timeout), would land at about 292 min (88%) expected and 306 min (93%) bound.
- **The trade-off for the orchestrator:** the bound case does move the worst night materially closer to the timeout. stress.py's exclusive runs (674-960 s per survivor) dominate that risk, not this change. If the bound case is unacceptable, the alternative is the reviewer's option (a): keep the driver pooled, with a bound sized on the pooled figure, and drop the PR-time claim. It does not remove the cause.

**Code ownership:** `tests/mutation_table.py` is code-owned (`@tvofi`, CODEOWNERS), so this PR needs tvofi's review. Nothing under `.github/workflows/` is touched.

**Dispatch:** `mutation-ledger` runs on main only. `gh workflow run tests.yml --ref fix/r9-nightly-ledger-cpu -f recheck=false` runs `mutation-nightly` (the same pool, baseline and null control) and `slow` on the branch. In `mutation-nightly`, read the `baseline tests/harness_headers.py` seconds (exclusive now, expected near `slow`'s 117 s rather than 201-293), the `null control ... survived every driver` line, and the job's wall time against 36984959667's 286 min and 37108891698's 147 min.

## Head

5d6edffec707f9f16485cff9f3773e2c47874dcf

## Mutation proof

The committed failing check came first: edb5ee00 adds the entities.py pin before the fix. At that commit `tests/entities.py` is rc=1, `1 of 2105 ENTITY CHECKS FAILED`:

    FAIL the harness_headers.py baseline shares the runner with no other driver, and only stress.py takes the gate lease  [EXCLUSIVE=('tests/stress.py',) LEASED=None overlaps=[]]

At the head, restore `EXCLUSIVE = ("tests/stress.py",)` in place (committed head, `git checkout` after). `tests/entities.py` is rc=1, `1 of 2105 ENTITY CHECKS FAILED`, the same FAIL with `LEASED=('tests/stress.py',)`. Restored, it passes 2105 of 2105.

At the head, delete the frontier's `CPU_LIMIT_OVERRIDES_S` entry in a `git archive` copy. `tests/harness_headers.py` is rc=1, `13 of 105 HARNESS HEADER CHECKS FAILED`, led by:

    FAIL tools/audit/round4/D7/sysid_estimator_frontier.py exits 0  [rc=-24 SIGXCPU: the 60 CPU-s bound was spent cpu=60.0s stderr=]
    FAIL tools/audit/round4/D7/sysid_estimator_frontier.py costs at most 50% of its CPU bound  [cpu=60.0s against 30s (50% of its 60s bound)]

That run also shows the kill message working where round 1's run printed `stderr=` alone.

## Null control

The unmodified head: `tests/harness_headers.py` passes 105 of 105, rc=0, with the frontier at `cpu=144.9s of the 480s bound`. The same run with a concurrent entities.py run shows 169.0 s. The cheap children show `cpu=0.6s`-`8.1s of the 60s bound`. `tests/entities.py` passes 2105 of 2105, and `tests/structure.py` prints STRUCTURE RATCHET PASSED.

## Figures

- runner serial per-child CPU (96.8, 0.3-4.3, 117 s wall): `gh api repos/tvofi/heatpump_optimizer/actions/jobs/111225908327/logs | grep -E 'cpu=|harness_headers'`
- pooled kill at 240 and pooled baseline walls 201-293: `gh run view 37108891698 --log --job 111162760555 | grep -E 'harness_headers|rc=-24'`, likewise `--job 111162760619`, and `gh run view 36984959667 --log --job 110767771897 | grep 'baseline tests/harness_headers'`
- survivor counts and job durations: `gh run view <run> --log --job <job> | grep 'survivor(s) of'` and `gh run view <run> --json jobs` for runs 37108891698, 36984959667, 36839970966, 36690934459, 36543810424, 37050037132
- dev-box per-child CPU, mutant and head: `PYTHONPATH=tests/hastub:custom_components:tests python3 tests/harness_headers.py`
- scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED -- 2 script(s) run` (entities.py, harness_headers.py), both green locally

## Red checks

`mutation-ledger` (scheduled, main 2e569748, run 37108891698). `defect-root-cause.md`'s question is whether a cheaper detector existed. **No automatic one did.** The kill depended on pooled billing, and no pull-request job runs harness_headers.py inside mutation_table.py's pool: `fast` and `slow` run it serially in run.sh, where it costs under half the old bound. The only place the pooled cost existed was the nightly that went red. Round 1's per-child `cpu=` line is the cheaper diagnostic, not a detector: it shows the runner's serial cost on every gate run, so the next kill names its own figure.

With this change the class is removed for this driver rather than detected. It runs alone in the pool, and its headroom line reds a PR's serial run and the nightly at the same cost. The kill recurred the scheduled run after #1872. #1872 named a cause, BLAS oversubscription, from no runner CPU figure, and my round 1 named another, a dev-box sizing, before the runner's serial figure existed. Both inferred the mechanism from wall time. That repeat belongs to the root-cause seat.

## Forward-carry

none

## Friction

defect-root-cause: unenforced: two consecutive fixes of one SIGXCPU (#1872, this PR's round 1) each named a mechanism from wall time alone, before any CPU figure from the runner existed; the runner's serial `cpu=` line refuted both (run 37130986490)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
