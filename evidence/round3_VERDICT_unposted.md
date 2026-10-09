Fix review: blocked 1d011c88712398a90e3ae1d48743ddd7a89d36ff harness: class-open an install whose running asks never span 1.15 never learns a COP error beyond 15% (probe 7: base 0.751/0.750, head 1.000 with 0 folds); the docstring's "no error is beyond reach" is false

bus-nonce: de5bda4eeb64dbf8e89e547dad8fcb8e
seat: review-2066 (fix-review.md, round 3; rounds 1 and 2 were not posted, and their records are evidence/round1_VERDICT_unposted.md and evidence/round2_VERDICT_unposted.md)
evidence: /Users/timmalmstrom/hpo-seats/review-2066/ev3
measured at: 1d011c887 (code head cdf37977a), stacked on #2065's head 325960ef6. Every probe ran at 325960ef6 (base) and at 1d011c887.

## The #201 decision this round's repair must meet (orchestrator, corrected; supersedes 6071684435)

Rule (column 4 below):
- The new modulation-keyed floor always applies.
- With no `follows_ask` evidence, a departure over 15 % must also pass the old `max(0.3 x max, 0.2)` floor. Without evidence it gets no `draw_off_ask` refusal, but a separate refusal code for "no evidence yet".
- With evidence, `follows_ask` decides.
- Correct the body and the `judge_ratio` docstring ("no error is beyond reach", "one day").
- DESIGN.md amendment A5 records `follows_ask` as fix 1's component, living in 7a's `draw_range`.
- Hold-then-replay (departures held until evidence, replayed or dropped) is carried to fix 3's brief, not built here.

**Acceptance for round 4** (my column-4 prototype numbers; no row may be worse than the base):
- matched control `selfmod_matched` 96/96 at 1.000
- `min1_running` 15/15
- probe 7 `narrow_config_true0.75` 0.751 and `wide_config_steady_week_true0.75` 0.750
- probe 5 (hourly / 3 h / flat) about 0.97 / 1.000 / 1.000
- probe 6 `selfset_hourly` at most 1.37 (base 1.600)
- `selfmod_independent_4kw` at least 0.81 (base 0.636)
- probe 6 heat-led rows unchanged (true 0.7 at 0.705)

The probe scripts are in this evidence directory (reviewer_probe5/6/7.py). Run them in the production order (fold, then learn) at #2065's head and at the new head.

Prototype evidence (throwaway worktrees at this head, removed afterwards): evidence/proto_departure.out is column 4, and evidence/proto_literal.out is the rejected literal reading.

| row | base | head | literal: old floor, no off-ask, without evidence (rejected) | column 4: new floor, plus old floor only for a departure > 15 %, without evidence (decided) |
|---|---|---|---|---|
| probe 7 narrow_config_true0.75 | 0.751 | 1.000 (0 folds) | 0.751 | 0.751 |
| probe 7 wide_steady_week_true0.75 | 0.750 | 1.000 (0 folds) | 0.750 | 0.750 |
| harness selfmod_matched (control) | 0/96 | 96/96 1.000 | 49/96 1.000 | 96/96 1.000 |
| harness min1_running (the live fix) | 0/15 | 15/15 | 0/15 | 15/15 |
| probe 5 hourly / 3h / flat | 1.000 x3 | 0.978/1.000/1.000 | 0.993/1.000/1.000 | 0.973/1.000/1.000 |
| probe 6 selfset_hourly (6 kW, 1 kW floor) | 1.600 | 1.043 | 1.370 | 1.370 |
| harness selfmod_independent_4kw | 0.636 | 0.976 | 0.810 | 0.810 |
| probe 6 heat_led_0.7_noise20 | 0.706 | 0.705 | 0.705 | 0.705 |

Column 4 gives up part of this head's first-day protection (probe 6 1.043 -> 1.370, and the 4 kW row 0.976 -> 0.810) to restore base parity where evidence never arrives. That trade is the decision; it is not a defect for round 4 to fix.

## Why the head is blocked

Probe 7 (mine, synthetic; production order per tick: `draw_range.fold`, then `_learn_measured_cop(draw)`). A heat-led pump with a real COP scale of 0.75, over 400 ticks:
- RESULT narrow_config_true0.75 (configured 3.0-3.4 kW): base 398/400 scale 0.751; head 0/400 scale 1.000, `follows_ask` None
- RESULT wide_config_steady_week_true0.75 (1-6 kW, asks 2.8-3.1 kW): base 399/400 scale 0.750; head 0/400 scale 1.000, `follows_ask` None
- RESULT wide_config_varied_true0.75 (control): base 0.750; head 0.749, first departure fold at tick 47

With no ask span the evidence never arrives, every departure is refused, and the scale never moves. This is the v4.0.5 deadlock that the coordinator's own comment guards against, so `cop_health` goes blind on that class. The body's "Evidence wait ... one day of running" and the docstring's "no error is beyond reach" (accuracy.py:683) are claims stronger than the check.

## Verified at this head

- Stacking: 325960ef6 is an ancestor of the head, and the body declares the stack ("this PR merges after #2065"). The PR's base branch is still `main`, so #2065 must merge first.
- Acceptance rows (decision (a), round 2), from the harness at both ends: selfset_hourly/three_hour/flat 0/96 1.000 -> 7/96 0.978, 0/96 1.000, 0/96 1.000. selfmod_matched 0/96 -> 96/96 1.000. selfmod_independent 1.000 -> 0.976. selfmod_independent_4kw 0.636 -> 0.976. Every other harness row reproduces the body's figures (evidence/fixer_harness_*.out).
- Mutant (mine): `follows_ask` made to return True always puts selfmod_independent at 0.707 and selfset_hourly/three_hour at 0.615/0.648, so the slope check is load-bearing.
- Slope estimator, probe 6 (heat-led, true 0.7): 20 % meter noise 0.705, one-tick lag 0.688, 5 % outliers at 3x 0.700, true 1.3 -> 1.304. Each folds its first departure at tick 47 (`MIN_SAMPLES`), so the estimator is robust to noise, lag and outliers. Partial following: slope 0.3 is refused (head 1.101 vs base 1.600). Slopes 0.5-0.8 count as following and ratchet as the base does (both 1.600). That is a residual, not a regression; the body should state it. My probe is open loop, so absolute scales for partial pumps are not the truth.
- New-install starvation: one day (48 running samples) on an install whose asks vary. The window persists through `draw/samples` (harness `true_0.7_reload150` 241/288 0.704). Installs without ask span never get evidence (blocker).
- Ownership: putting `follows_ask` in `draw_range` is the sound home. It reads S3's samples with no second statistic, while placing it in accuracy.py would reach into DrawRange's internals. It is a different question from `engaged`, which a plain 1.3x efficiency shift also trips. A5 must record it as fix 1's component in 7a's module, and #2065's owner must be told: a change in what `samples` means re-stacks this PR.
- Architecture (step 15): `judge_ratio` is static and takes values, the window is handed in, the spread statistic is gone and the walking ratio has one owner. Coordinator change: one parameter.
- CI at 1d011c887 when posted: see the reviewer's report. `mutation` is red with unpinned sites (mutation-autofix's), and `nightly-status` is red (not this PR's).
- Round 3. Round 4 owes a re-cut per `fixer.md`: re-take the body whole, keep the diff minimal.
