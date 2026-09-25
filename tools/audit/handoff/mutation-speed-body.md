<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Before: the `mutation` lane took 100 minutes on #1611 (job 108126964988, 15:06:07 to 16:46:14). A third of that, 34 minutes, went on `tests/stress.py`'s baseline and null control, run alone on the runner, and no mutant used either one: stress.py runs only for a mutant that survives every shared driver, and all 10 were killed. The mutants then took 42 minutes, because each one swept its drivers cheapest first. Six mutants that `tests/features.py` killed each paid for every cheaper driver before it, and those drivers kill almost nothing (features.py holds 197 of the ledger's 232 `killed_by` entries).

After: the same 10 mutants give the same 10 verdicts, and the replay named the same killer for 9 of the 10. The run takes about two thirds of the time. Under `--scope changed`, the EXCLUSIVE driver's baseline and null control run only once a mutant survives every shared driver. Each mutant's drivers sweep in Smith's-rule order: seconds over the kill chance measured from the ledger, where the file's own kills are shrunk toward the whole ledger's.

Neither change can alter a kill or LIVES verdict:
- **Order.** A mutant is killed if some driver kills it, and it LIVES only after every one of its drivers ran (`drive_pool`, pinned by `every verdict is the serial sweep's`). Only the driver NAMED as the killer can differ, as it already could.
- **Deferral.** A mutant that stress.py drives still gets stress.py's baseline and null control first. A LIVES verdict needs stress.py, so any run that could breach the cap runs them. `--scope full` (the nightly) keeps the eager baseline and its refusal (`deferred_drivers`).

What does change, and is disclosed here:
- **The headline, when stress.py's baseline is red or times out and no mutant reaches it.** Main prints `MUTATION TABLE INCONCLUSIVE`; this head prints `MUTATION TABLE PASSED` plus `tests/stress.py: DEFERRED AND NEVER RUN -- ... a red one would have made this table INCONCLUSIVE`. Both exit 0, so the job's result is the same; the headline is not.
- **`--pin-killed` in that same case.** Main pins nothing from an INCONCLUSIVE table; this head pins the killed mutants (11 pins on the case the review built, against 0).
- **Killer credit.** Sweeping likelier killers first names `tests/features.py` or `tests/entities.py` more often where a cheaper driver would also have killed. That credit lands in the ledger's `killed_by`, which feeds the next run's ordering. On #1611's pool the replay re-credited 1 of 10 (thermal_model.py:1589, from `tests/doc_claims.py` to `tests/features.py`).

How:
- `driver_order` replaces `sort(key=baseline seconds)` in `main()`.
- `drive_pool`'s helper phase now picks the costliest driver still queued. Before, it took the queue's last entry, which was only the costliest under cheapest-first order.
- `drive_pool` takes a `settle(script)` hook. It is called once, before the first mutant an EXCLUSIVE driver drives. `main()` uses it to run the deferred baseline and null control, with the same refusals as the eager path (`Deferred`).
- `deferred_drivers(needed, scope)` is the one place the defer rule lives: EXCLUSIVE drivers under `--scope changed`, none under `--scope full`. After the pool, `main()` prints `DEFERRED AND NEVER RUN` for each deferred driver whose baseline never ran.
- No workflow change.

This touches `tests/mutation_table.py` and `tests/entities.py`. Only `tests/mutation_table.py` is code-owned (`.github/CODEOWNERS`, `/tests/mutation_table.py @tvofi`), so this waits on tvofi's review.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Head

`0a1424cc`. The first round was `85cf431e`; `0a1424cc` answers its review.

## Mutation proof

Two new `tests/entities.py` checks, each run against main's `tests/mutation_table.py` and against three mutants of this head's version:
- main's `tests/mutation_table.py`: both checks print FAIL, `FAIL a deferred stress.py baseline runs only once a mutant survives every shared driver, once, before that mutant's stress.py run [log=[]]` and `FAIL a mutant's drivers sweep in the ledger's kill-rate order, every one kept [order=[]]`.
- `settle` called before an EXCLUSIVE driver whether or not the mutant was killed: the first check prints FAIL.
- `driver_order` reverted to cheapest first: the second check prints FAIL, with `order=['tests/b.py', 'tests/a.py', 'tests/features.py']`.
- `driver_order` dropping its last driver: the second check prints FAIL.

A third check, `a changed-scope run defers stress.py's baseline, the nightly never does, and main() takes its deferral from that rule`, kills the never-defer mutant the review found surviving, in each form it can take:
- `deferred_drivers` returning `[]`: FAIL `[deferred=([], [])]`.
- `main()` setting `deferred = []` instead of calling the rule: FAIL `[deferred=(['tests/stress.py'], [])]`.
- the rule deferring under `--scope full` too: FAIL `[deferred=(['tests/stress.py'], ['tests/stress.py'])]`.
The same check pins the `DEFERRED AND NEVER RUN` line in `main()`.

Restored, all three print `ok`, and `python3 tests/entities.py` prints `ALL 1927 ENTITY CHECKS PASSED` at `0a1424cc`. tvofi waived a full mutation-table run over this diff; these are the targeted runs the fix needs. The existing scheduler checks (barrier concurrency, stress.py alone, the serial-sweep verdict check) stay `ok`.

## Null control

The unmodified tree is CI's own run of #1611, job 108126964988. Its baselines and null control ended at 16:04:15, 58 minutes in, and the table passed at 16:46:11 with 10 of 10 killed. `tests/features.py` killed 6 of them, `tests/entities.py` 3, and `tests/doc_claims.py` 1 (thermal_model.py:1589).

The replay ran this head's `tests/mutation_table.py` over #1611's head `e1f11a7a`, `--scope changed --base a3473fb8 --max 10 --jobs 3`, on a 4-core cloud box with a cold drift cache. It drew the same 10 mutants and the same null control (coordinator.py:546) and printed `tests/stress.py: baseline and null control deferred`. The null control survived at 12 minutes in. `MUTATION TABLE PASSED`, 0 of 10 survivors, at 30.6 minutes wall. Every mutant has the same verdict as CI, and the same named killer, except thermal_model.py:1589: CI named `tests/doc_claims.py` and the replay named `tests/features.py`.

The box's speed was measured with main's code on the same pool before the run was stopped: its shared baselines finished in 11.4 minutes against CI's 24. Scaled by that ratio, 30.6 minutes is about 65 minutes on CI, against 100.

A scheduler replay of #1611 through the real `drive_pool`/`drive_baselines`, with CI's driver seconds and each mutant killed only by its CI killer, gives 107 minutes for main and 66 for this head. With one survivor it gives 122 and 119, since that run needs stress.py anyway.

## Figures

- 100 minutes, 34 minutes (stress.py alone), 42 minutes (mutants), 58 minutes (baselines through null control): timestamps in the log of job 108126964988, `mutation` on #1611.
- 197 of 232 `killed_by` entries name `tests/features.py`: counted from `tests/mutation_budgets.json` at `67a0cb9`.
- 30.6 minutes, 11.4 minutes against 24: `python3 tests/mutation_table.py --scope changed --base a3473fb8486a787547bc2c455283a1e2804f5b25 --max 10 --jobs 3` in a worktree of `e1f11a7a`, with `tests/mutation_table.py` at this head and then at main.
- 107 against 66, 122 against 119: an out-of-tree scheduler replay that drives both versions' `drive_pool` and `drive_baselines` with sleeps scaled from CI's seconds.

## Red checks

- `pr-contract` on `85cf431e`, jobs 108237009297 and 108236824358. They ran for #1620, which the web UI opened under the `tvofi` account; `pr-contract` refused the author (decision 0011). No code in this diff was at fault, and this PR is that branch re-opened as `hpo-author`. Cheaper detector: none is needed; `tools/audit/app_push.sh` authors as `hpo-author` by construction, and the red came from opening the PR outside that route. No countermeasure: the route exists and this PR follows it.

## Forward-carry

none

## Friction

none
