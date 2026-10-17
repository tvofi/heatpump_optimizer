R10-TARIFF, wave 1. This PR has one defect fix and three tariff refactors that change no output.

Closes #2230.
Part of #2238.

**1. N-period-rollover (#2230, D2-s3-01).** `PeakTracker.observe` reset the month before it closed the window open at the change. The month's last metering window therefore closed into the new month and was wiped. The finder's one-line shape (close before the reset) is not enough. The window it closes is wiped by the same reset, and the capacity line was booked at the settlement before midnight. The new bill-level harness `dev/audit/harnesses/r10_month_last_window_billed.py` drives the real coordinator in the cycle's own order (settle the interval that started at the previous cycle, then fold). It reads `billed_spike_reached=0 of 24` under that shape, the same as at the base. The fix:
- `observe` closes the open window before the reset.
- The tracker keeps the closed month's ranked peaks (`closed_month`, `closed_peaks`) until the next rollover. They are persisted in `as_dict`/`from_dict` and declared in `store.py`'s domains, so a restart between the rollover and the settlement keeps them.
- `PeakTracker.billing_statements()` states the closed month and the open one.
- `_billed_peak_kw` is the one top-k mean, shared by `billed_peak_kw` and the closed statement.

**Out-of-seam edit, named here as the orchestrator required.** `coordinator.py` `_roll_month` now books every statement before `roll_receipts` freezes the month. That is one loop replacing one call (`max_class_loc` 8705 -> 8703). No other coordinator hunk. Reason: the coordinator's settlement is the only reader that books a month, so a fix inside the tracker alone reaches no bill. The orchestrator ruled this in scope for #2230 (decision A) and recorded the after-edge against FAHRENHEIT.

`sweep-N-period-rollover.md` said the one-line fix would also close the `_roll_month` seam. That line is corrected in place with the measurement.

**2. D7-s3-8x-tariff (ARCH2-s3 patch 01b, the CPU-neutral variant).** A day's peak is the solver's top-k rule at k = 1. `_hard_day_max` and `_plateau_aware_day_max` are deleted, and so is the second copy of the batch plateau rule. Their place is taken by `_plateau_aware_topk_sum_batch`, which `peak_cost_batch` and `_day_peaks_batch` both call. The scalar keeps its own bisection for the per-day CPU cost, as 01b chose.

**3. D7-s2-59 (ARCH-s2 patch 07).** `grid_fee._parse_cyclic_range` owns the wrap for months and weekdays, and `parse_month_range` and `parse_day_range` call it.

**4. ARCH2-s2 P5, the peak-billing record.** `peak_cost`, `peak_cost_smooth`, `peak_cost_batch`, `_peak_charge` and `_peak_excess` take one frozen `PeakBilling` instead of up to eleven loose parameters. `HeatPumpOptimizer._peak_billing` builds it once for the solver's closures and for `_grid_report`. In `optimizer.py`, this edits only the architect note's seam (the peak-day keyword arguments and their callers). It retires the four tariff rows in `tests/arch_score_head.py` `PARAMS_OVER_10_LEFT`. The output is bit-identical (equivalence figures below).

Alternatives considered:
- (1) The one-line close-before-reset. Rejected: measured to change no bill (0 of 24).
- (1) A tracker that included the open window in `billed_peak_kw`. Rejected: it would publish a projected peak as a billed one.
- (2) ARCH2-s3 patch 01, which also folds the scalar bisection into the batch. Not taken: the roster names 01b, the CPU-neutral variant. 01's p01 cpu ratio median was 0.9927, with a range of 0.84..1.10 across 3 reps (CATCHUP-VERIFY V1), so its CPU gain is inside the noise.

## Head

`21397979934cc3c41518bfa094f462598be7c270` merges the authored code head `a8df7964e2f62be2a6aebe56e6e4e1d2559ca442` and then merges origin/main `c42d7cea6` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`a8df7964e2f62be2a6aebe56e6e4e1d2559ca442`. Built from the PR head `5f2371e69` (the merge-main bot's last move), it adds two things:
- `4aaea2d07`: the 28 `killed_by` pins CI measured at `f09549085` (run 38796525102, shards 1-6, every status `measured`). They are applied with `mutation_table.apply_pins` on a checkout of that same head, because the bot moved the head before `mutation-autofix` could push them.
- `a8df7964e`: survivor triage for the five keys that run left alive (see Unpinned sites).

This branch's production diff against its merge base is unchanged: `git diff <merge-base>...HEAD --stat -- custom_components` is the same five files, +223/-239. The only production change since the figures below were measured is main's own `services.py` (3 lines, another PR), which this diff does not touch. The branch was cut at `5603ee319`. Its own commits are the four tariff items, the #2230 test-first commit, the structure record, the mutation-ledger repair, the P2 registry, the inert-read entries and the disposition re-point.

## Mutation proof

The block run is `python3 tools/audit/seat/features_block.py "from harness import FakeEntry as _ux6_Entry" "# Every receipt kept reaches the enabled monthly-savings sensor"`, on an export of `5b7225456`. At the unmutated tree it prints `ALL 12 FEATURES BLOCK PASSED`. Each mutant was applied to the export's production file and restored after its run:
- M1, `self._close_window(tariff)` dropped from the rollover branch: rc=1. FAIL `#2230: a spike in the month's last metering window reaches that month's capacity receipt, across a restart between rollover and settlement too` [last window 1.0, after a restart 1.0].
- M2, the closed-month retention line replaced by `pass`: rc=1. That FAIL, plus FAIL `#2230 null control: a rollover with no open window closes the month on its recorded peaks unchanged` [[('2026-04', 0.0)]].
- M3, `if self.closed_month:` in `billing_statements` replaced by `if False:`: rc=1, the same two FAILs.
- M4, `"closed_month"` dropped from `as_dict`: rc=1. FAIL `#2230: a spike ...` [last window 5.0, after a restart 1.0]. This is the restart arm alone.
- M5, `_roll_month` booking only the open month's statement (`billing_statements(tariff)[-1:]`): rc=1. FAIL `#2230: a spike ...` [last window 1.0, after a restart 1.0].

Test first: the same block on an export of `650d394d8` (the test commit, before the fix) prints FAIL `#2230: a spike ...` [last window 1.0, after a restart 1.0]. The null-control check raises `AttributeError: 'PeakTracker' object has no attribute 'billing_statements'`.

The three refactors are guarded by value-equivalence harnesses with perturbation arms, listed under Figures. The mutation ledger: 11 `killed_by` rows named sites these refactors deleted or rewrote, and `mutation_table` refused them ("disposition names no site the inventory generates"). They are removed. The one `survivor_triage` verdict, `peak_cost_batch` CLAMP_DROP, is re-keyed from `60b91167` to `66db7abd`, with its argument re-checked against the new exact/smooth split. `completeness_problems` then returns [] and `ledger_form_problems` returns []. CI's `mutation-autofix` pins whatever its drivers kill at the new sites. Survivors get their disposition under Unpinned sites once that run reports.

## Unpinned sites

Every site this diff adds now has a disposition, and `tools/pr/ci_predict.py` at head prints no ADDED UNPINNED line.

28 are pinned `killed_by` from CI run 38796525102 (commit `4aaea2d07`). The five keys it left alive are triaged in `tests/mutation_ledger/survivor_triage/tariff.py/`. Each was already unpinned at base `5603ee319` under its pre-refactor spelling.
- `tariff.py:_peak_excess CMP_BOUND 85b13431`: equivalent. A price of exactly 0 charges 0.0 either way.
- `tariff.py:_peak_excess GUARD_OFF 85b13431`: equivalent. A zero price, an infinite threshold and a NaN threshold all reach the same None/0.0. A negative price is unreachable: the form bounds it to 0-500.
- `tariff.py:_peak_charge CLAMP_DROP 2a3cb625` (*2): equivalent, as the batch twin's clamp is.
- `tariff.py:_plateau_aware_topk_sum_batch CMP_BOUND c1441c77`: gap. Only a window exactly at the band edge differs.
- `tariff.py:_plateau_aware_topk_sum CMP_BOUND 518b9490` (*2): gap. The band edge, and the scalar surrogate on an exactly-k plateau, which no driver prices.

## Null control

- The local `mutation_table.py --pin-killed` run (orchestrator-approved after the bot kept resetting the CI chain) refused on its own null control. `tests/entities.py` read the comment-only edit at `grid_fee.py:104` as killed, and the `features.py` baseline timed out (rc=124 at 1795 s) at load ~100. Re-running entities on an export with that single edit differed from a clean run only in git-history and network checks a one-commit export cannot satisfy. This is a local environment artefact, not a finding; the pins above are CI's.
- Bill harness `--null`: the spike one window earlier, which every tree bills. It reads `billed_spike_reached=24 of 24` at the base and at the head, so a 0 is the last-window defect and not a blind harness.
- Tracker null, in features: a rollover with no open window closes the month on its recorded peaks unchanged. `billing_statements` returns `[("2026-03", 4.0), ("2026-04", 0.0)]`. This is the roster's forward-carried null ("closing before the reset must not change a period with no open window").
- Equivalence identity arm: `equiv_tariff.py` base against base gives `mismatches=0`.
- `score.py --diff 5603ee319 5603ee319` gives `dS +0.0000 NULL`.

## Figures

All runs used the seat venv (python 3.14) at `5b7225456` unless stated otherwise. The base is `5603ee319` (an export). load1 reached 118 during these runs. Every figure here is a count, which contention does not move.
- Finder harness `dev/audit/rounds/round10/D2/s3/month_last_window.py` (sha1 9565b101dfaa5206d5cdff96b220b0c9f8079bac), run as `PYTHONPATH=tests/hastub python3 <it>`:
  - base: `last_window_reached=0 of 24`, `max_billed_last_window_spike=1.000 kW`.
  - head: `24 of 24`, 5.000 kW.
  - `--perturb`: 24 of 24 at both ends.
- Bill harness `dev/audit/harnesses/r10_month_last_window_billed.py` (sha1 37b52d9055089bfe7c070649652ddd6d408ca12d), run as `PYTHONPATH=tests/hastub:tests:custom_components python3 <it>`:
  - base: `billed_spike_reached=0 of 24`.
  - head: `24 of 24`.
  - the finder's one-line shape on the base tree: `0 of 24`.
- Seam enumerator `python3 dev/audit/rounds/round10/D14/period_rollover_seams.py` at head: `seams=5 unsafe=1`. The sweep's base row is `seams=5 unsafe=2`. Dispositions:
  - `tariff.py observe [month != self.month]`: closed in this diff (now `safe`).
  - `tariff.py observe [key != self._window_key]`: guarded.
  - `coordinator.py _track_curve_comfort`: guarded.
  - `dhw_learning.py async_learn_usage`: not applicable.
  - `power_guard.py update`: not applicable. The sweep's disposition is the hysteresis counters, not a period aggregate. It is the one remaining `unsafe`.
- P5 equivalence, `handoff/audit-r10-arch2-s2:dev/audit/rounds/round10/D7/arch2-s2/equiv_peak_billing.py` (sha1 c684aaf42e760b429a705753302d487b05135abc). Its hard-coded BASELINE is swapped for an exported `5603ee319` tree; that is the only edit. Head against base: `cases=256 values_compared=1536 mismatches=0`. Perturbation (`bill.peaks_averaged + 1` in `_peak_charge`): `mismatches=274`.
- 01b equivalence, `handoff/audit-r10-arch2-s3:dev/audit/rounds/round10/D7/arch2-s3/equiv_tariff.py` (sha1 f60ff8d3862e063b29c0d03913f0dde0ebf04617). `--base` accepts a directory; that is the only edit. It ran on the 01b-only commit `a7e32fbba`, because the probe calls the positional signatures P5 retires. Results: `probes=8160 mismatches=0 head_scalar_batch_parity_failures=0`. `--perturb` (1 ulp on tau): `mismatches=920`. Identity: 0.
- 07 equivalence, `dev/audit/rounds/round10/D7/arch-s2/equiv_cyclic_range.py` (sha1 4acfb71864dc7b044fa74fea1d97e140605fd8ef). Its base and head come from exported trees instead of re-applying the patch. Base `5603ee319` against head: `tokens=522 mismatches=0`. `--break`: `mismatches=487`.
- Architecture score, `python3 tools/audit/archscore/score.py --diff 5603ee319 HEAD` at head: `dS +0.9094 IMPROVES`.
  - `duplication_copies` 68 -> 66: 01b and 07.
  - `params_over_10` 12 -> 8: P5.
- `python3 tests/structure.py` at head: `STRUCTURE RATCHET PASSED`. Recorded at `65e9658eb`:
  - `duplication_copies` 37 -> 35 (01b, 07).
  - `max_class_loc` 8705 -> 8703 (the `_roll_month` loop).
- Scoped gate, `python3 tests/closure.py select --diff <merge-base>` at head: `MODE: SCOPED -- 27 script(s) run, 6 scoped out`. Run locally (seat venv, `PYTHONPATH=tests/hastub`):
  - `tests/entities.py` at `12043fe47`: `ALL 2321 ENTITY CHECKS PASSED` (2320 at `53a1060b7`; main added one check).
  - `tests/arch_score.py` at `ecf1fe912`: `ALL 175 ARCHITECTURE SCORE CHECKS PASSED`.
  - `tests/arch_score_head.py`: `ALL 15 ... PASSED`.
  - `tests/harness_headers.py`: `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `tests/doc_claims.py`: `ALL 169 checks PASSED`.
  - `tests/features.py` on a `git archive` export of `65e9658eb`, whose production code is identical to head: `1 of 4110 FEATURE CHECKS FAILED`. The one failure is `#363 recorded_at = 'unknown'`, the archive-copy runner artefact `fixer.md` step 2 names. The test-first export `650d394d8` fails it the same way.
  - Left to CI (heavy, per tvofi 2026-10-07): `golden.py`, `optimality.py`, `stress.py`, `backtest.py` and the rest of `scope.run`. P5 and 01b are bit-identical by the equivalence figures above, so no golden is expected to move. Nothing is claimed in `claimed_drift.txt`.
- `python3 tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- P2 registry, fixer.md step 8. `tests/entities.py` gains two facts. Each is clean at head, and its planted sibling fails, in the null-control check `and each P2 fact fails on a new sibling outside its owner`.
  - `peak_tie_rule`: owners `_plateau_aware_topk_sum` and `_plateau_aware_topk_sum_batch`. Seams returned: those two, 0 stray.
  - `cyclic_range_wrap`: owner `grid_fee._parse_cyclic_range`. Seams returned: the owner, plus two in `dhw_schedule` (`_parse_day_selector`, `_format_day_selector`). Those two are dispositioned as a distinct finding, reported to the orchestrator and not fixed here (other files).
- That distinct finding's census, `PYTHONPATH=tests/hastub:custom_components python3 dev/audit/harnesses/r10_weekday_range_twins.py`: `pairs=49 disagreements=0`. `--perturb` (the wrap one day short): `disagreements=49`. `--identity`: 0. The finding is a duplicated rule, not a wrong answer.

## Red checks

none at the push. `prepr.sh` CI PREDICT named two `closures` INERT READS before it: `tests/harness_headers.py` reads the two new harnesses. `open_pr.sh` refused on them, and without a PR no bot run comes. `derive_closures.sh --single tests/harness_headers.py` re-recorded the closure on Darwin, and it moved only the `seconds` field, because the inert dimension is strace-only. The two paths were therefore added to `inert_reads["tests/harness_headers.py"]` by hand (commit `29a782100`). Re-run, `tools/pr/ci_predict.py` prints `no closures or fast red predicted against 3d650d26c762`. The cheaper detector is CI PREDICT itself, which caught it before any push.

- The CI pin chain never finished on this PR. It takes about 2 h, and the merge-main bot moved the head under it three times (`532eb85d3`, `f7d2143d0`, `f09549085`) whenever main moved and the PR went DIRTY. Cheaper detector: none. The countermeasure is the orchestrator's, routed to TICK-TRAIN / ci-autofix: no reset while mutation-pins runs at a PR head, or a pin chain that survives a main-only merge.
- `mutation` (red at `532eb85d3`, `d114395e6`, `67d71eeb6`, `f7d2143d0` and `f09549085`): the ratchet refused the 30 unpinned sites this diff adds (28 keys, two `*2`). Answered at this head: CI's pin run measured them, its 28 kills are applied in `4aaea2d07`, and the five surviving keys are triaged in `a8df7964e`. `ci_predict.py` reports no added unpinned site. Cheaper detector: `prepr.sh` step 6d already lists the sites before a push, so none is owed.
- `pr-contract` (red at `532eb85d3`, run 116531242827): `mutation` was red and this section did not name it. This entry answers it. Cheaper detector: none is owed, because `prepr.sh` step 7c reads only reds already pushed, and this one did not exist until CI ran.

## Forward-carry

- R10-LEAF-IMPORTS and R10-SOLVER (roster, after this group on `optimizer.py`): the capacity charges now take one `PeakBilling`, built by `HeatPumpOptimizer._peak_billing`. A caller pricing a plan builds it there and never passes the loose arguments. The orchestrator owns the roster, so this is sent to it for `roster_edit.py append-carry`.
- The dhw_schedule weekday-range twin goes to the orchestrator as a new finding, for a roster group.

## Friction

- fixer.md: unclear: `features.py` reads its own sources through `inspect` while running, so editing the worktree during a run crashed it at line 54518 with a SyntaxError on a shifted source line. Every local run here then moved to a `git archive` export.
- archscore-planted: unclear: The planted perturbations run against the calibration pin, not the head. A diff that removes the signature N1b re-wraps looks as if it owes N1b a retarget, and it does not. The retarget was reverted in `ecf1fe912`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
