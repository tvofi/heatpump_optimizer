# HOTFIX R10-HOTFIX-CI-CRITPATH-2: a measured tolerance band on critical_path_minutes only

## Re-cut

This is fix round 5, so the body is re-cut by fixer.md "Past three rounds, re-cut rather than repair". The headings are the template's. Every figure is re-taken in this pass, or it is quoted with its source verdict and marked as such. The head has not moved, so fix review round 4's `merge` (verdict/3045 at 3ab1c1ad) still describes this code. This round adds the payment search the owner's ruling asks for ("pay first, else approve under the budget-raise mandate"). Its outcome is 2: no payment exists, and no code changed.

Main went red on `tests / ci-ratchet` from 05c0d6d5d (the #3040 merge) through 0cae227c3, with `GREW critical_path_minutes: 34.467 (budget 34.267)` (run 41201096004). `git diff --stat 0d33c9348 05c0d6d5d` lists seven `dev/programme/delivery/*.md` rows, and those cannot move CI work. Later push runs read `ok critical_path_minutes: 34.233 (budget 34.267)` (runs 41244562778, 41254631180). That is the flap, not a repair.

The metric is not a function of the tree. It is the median of the newest 8 completed ci.yml push runs' work, read live from the Actions API (`tests/ci_ratchet.py --gather-runs`, `PUSH_WINDOW = 8`). So the gate passes or fails on which 8 host draws the window holds: state (b), runner variance.

Cause: the 8-run median's upward sampling spread is larger than the headroom between the work's center and the budget. The spread reaches 1.300 min on the recording window (33.850 - 32.55). The headroom is 34.267 - 33.767 = 0.5 on the 2026-10-30..31 window. So the gate flaps on host variance. The center did rise since the 2026-10-25 recording: `tests / fast (3.14)` median work went 29.47 -> 31.83. That is real growth, and it spent the headroom. The band does not raise the budget.

Fix (owner ruling 2026-10-31, under mandate 6329234399):
- `tests/ci_budgets.json` gains `critical_path_minutes_band: 1.3`. That is the largest measured upward |8-run median - window median| over every sliding window of 145 runs, unpadded.
- `compare()` grades `critical_path_minutes` GREW only past budget + band. Every other row, the integer counters included, stays at zero tolerance. `--record` carries the band over through `record_table()`, a pure function that `main()` calls and the self-test drives.
- `tools/policy/budget_raise_gate.py` types the band MAX0. Absent means zero tolerance, so adding or widening the band is a raise and narrowing it is routine.
- `critical_path_minutes` stays at 34.267.

## Head

9ef51b8215dd7216950f177386fb2f5a8f010a47

This head merges the authored code head 536da691c7c77d0275e72235bc0b95991ce7f722 with origin/main a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0, which is the merge base. It is unmoved since fix review rounds 2, 3 and 4. origin/main is now 92588d581fde4ce287af3db5e8bb61461dc28015, 156 commits past the merge base. `git merge-tree --write-tree origin/main HEAD` exits 0 (no conflict), so by the brief the head merges nothing. No code changed in this round, so no `prepr.sh` re-run is owed for a moved tree. The body check runs through `body_push.sh`.

## Mutation proof

The code is round 4's, unchanged. Every line below was measured at this head, in round 2 and round 4 and by the round-1..3 reviewers, and is quoted from those bodies and verdicts. The head has not moved, so nothing here is re-taken.

- Before the code (test commit 765a0d19692ca5ed4b79b89192dcb1973bbac8b4), `python3 -I tests/ci_ratchet.py --self-test` failed 3 of its 44 checks: "the observed noise (34.467 on a 34.267 budget) passes inside the 1.3 band", "a median at budget + band exactly passes", and "a band row is a known, non-negative bound and not a graded metric". After the code (b8a027974): 44 checks, 0 failed. At this head, with the record-table pin: 45 checks, 0 failed.
- Each mutant was applied to this head and restored, and run with `env -u BASH_ENV python3 -I <script> --self-test`. Summary lines:
  - Baseline: `ci-ratchet self-test: 45 checks, 0 failed`; `budget_raise_gate self-test: 240 checks, 0 failed`.
  - M1, band ignored in compare: 45 checks, 2 failed.
  - M2, band applied to every row: 1 failed.
  - M3, gate row MAX instead of MAX0: 240 checks, 1 failed.
  - M3b, gate row deleted: 1 failed.
  - M4, bounds check dropped: 1 failed.
  - M5, `>=` for `>`: 4 failed.
  - M6, `--record` carry-over deleted from `record_table()`: 1 failed.
  - M8, the reviewer's own mutant, the band `continue` dropped: 1 failed.
  - M7, band key not excluded from the grading loop: 0 failed. It is equivalent: the key is never derived, so compare() prints `? not derived; not graded` for it.

## Null control

On the live window, `compare()` against the budget table without the band row reports `GREW critical_path_minutes: 34.467 (budget 34.267)`, which is main's red reproduced. With the band it reports `ok ... (budget 34.267, band 1.3)`. 35.568 and 35.777 are GREW with the band. `script_runs_per_push` 55 on a budget of 54 is GREW with the band present. This was re-confirmed by fix review rounds 2..4 at this head.

The payment search's null controls:
- `score.py --diff <merge base> 9ef51b82` scores the unpaid head, which is the reference every payment is read against.
- `score.py --diff 9ef51b82 9ef51b82` is identity.
- The depth-1 fetch is timed beside a full fetch of the same ref, twice each.

## Figures

- `python3 tools/audit/archscore/score.py --diff a7dd7f50d67e0c3819956b15ef95d77f4f6ebfc0 9ef51b8215dd7216950f177386fb2f5a8f010a47`, re-run at this head on 2026-11-01, three-dot (a7dd7f50d is `git merge-base origin/main HEAD`): `Architecture score: dS +0.0000 NULL`
- Payment prototypes, each one local commit on this head, never pushed, scored by the same command against the merge base and against this head:
  - (a) 2113344ead987e306ffaea3cf0c218472426c618: `Architecture score: dS +0.0000 NULL` against the merge base, and `Architecture score: dS +0.0000 NULL` against this head
  - (b) 94c7d38ebe9c4f4a8ba636d82423080ccb9f3b47: `Architecture score: dS +0.0000 NULL` against the merge base, and `Architecture score: dS +0.0000 NULL` against this head
  - (c) e4bebfe39ec5d2d89e0e70f818d134a981560645: `Architecture score: dS +0.0000 NULL` against the merge base, and `Architecture score: dS +0.0000 NULL` against this head
- `vector.py`'s docstring: "ROOT holds `custom_components/heatpump_optimizer`". Its `PACKAGE_DIR = root / "custom_components" / "heatpump_optimizer"` is the only tree it measures. So no edit under `tests/`, `tools/` or `.github/` can move any score metric. That is why every row above reads NULL, and why the reference reads NULL.
- `grep -n "git\b\|subprocess" tools/ci/prelude.py` names no git call. Its only history read is `codeql_scope.proof_entries`, reached only on `workflow_dispatch` at a proof ref, and `codeql_scope changed` runs only on `pull_request`. The workflow's own history reads (`git merge-base FETCH_HEAD HEAD`) are for a `batch/*` ref or an input base. So a push to main reads no history in prelude.
- Fetch of `refs/heads/main` into an empty repository through this container's proxy (pack 202.63 MiB), each timed with `date +%s.%N`, twice:
  - full history: 22.61 s and 19.42 s;
  - `--depth=1`: 2.97 s and 3.17 s.
- The live-window figures (from round 4, gathered 2026-11-01 with `GITHUB_REPOSITORY=tvofi/heatpump_optimizer python3 tests/ci_ratchet.py --gather-runs runs60.json --window 60`, which printed `push runs: 60 (60 CI)`, and run through `critjob.py` sha1 9fa09d25fab72040a9fadbd979c24b6df5bcfb45 and `sim.py` sha1 aed8cb5177ff3c48f7c276426c037fc35f51dc1d, both published as RESUME.md on this body's ref and both driving `ci_ratchet.run_minutes` unmodified). Fix review round 4 reproduced these exactly.
  - 8-run medians 32.916..34.575.
  - ci-ratchet cut 28 s: 32.683..34.108. Cut 36 s: median 33.341.
  - `prelude` sits on 60 of 60 paths, median 0.37 min, and its `fetch-depth: 0` checkout is 18.5 s. `tests / ci-ratchet` sits on 47 of 60, median 1.15 min. Its `Grade the ratchet` step has a median of 28.5 s, almost all `archscore_metrics()`, and it runs after `Gather ... metrics` (26 s) and `Fetch the recent push runs' durations` (10 s).
- The recording window: 86 ci.yml push runs from the query `created=2026-10-25..2026-10-26`, spanning 2026-10-25T00:42Z..2026-10-26T20:55Z, through `run_minutes`. Median 32.55, p90 34.267 (the budget, reproduced exactly), 8-run medians 31.709..33.850. Fix review round 1 re-derived this as `max|dev|=1.300`.
- `env -u BASH_ENV python3 -I tools/policy/budget_raise_gate.py --self-test`: 240 checks, 0 failed (round 4; the head is unmoved)
- `python3 tests/structure.py`, re-run at this head on 2026-11-01: STRUCTURE RATCHET PASSED

## Architecture score

dS +0.0000 NULL, re-measured three-dot at head 9ef51b8215dd against the merge base a7dd7f50d (the command is in `## Figures`). The diff touches tests/ci_ratchet.py, tests/ci_budgets.json, tools/policy/budget_raise_gate.py and a delivery row. archscore measures only `custom_components/heatpump_optimizer`, so no metric moves, and the fix claims no improvement. No gate metric rose.

## Raise justification

The raise is `tests/ci_budgets.json: critical_path_minutes_band: new at 1.3` (absent counts as zero). It rests on mandate 6329234399 and on the owner's ruling of 2026-10-31: "I suspect the ci-critical path minutes is runner variance, increase the variance band in that case under the mandate". It is held to the ruling of 2026-11-01: pay first by moving, deleting, sharing or refactoring code, and raise only if no such payment improves the architecture.
Payments tried: (1) a budget re-record, (2) a critical-path pay-down by plan, (3) a wider grading window, (a) the ci-ratchet archscore measurement overlapped with the fetches, (b) sharing or deleting code in the two touched instruments, (c) a shallow prelude checkout on push to main. None was taken, for the reasons below.

What a payment has to achieve here. The red is the 8-run median's upward spread exceeding the headroom. At zero band, a payment must take at least center + max upward dev - budget off the critical path. Against the recording window's largest upward deviation that is 33.767 + 1.300 - 34.267 = 0.800 min (the 2026-10-30..31 center, 33.767, plus 1.300 = 33.850 - 32.55). On the live 60-run window it is 34.575 - 34.267 = 0.308 min. Round 4's body stated 0.551 for the live window, and fix review round 4 found that figure overstated: it used the window's downward deviation, and GREW reads only the upper side. It is corrected here to 0.308. The decisive figure stays 0.800. A pay-down's effect cannot be read until 8 main push runs carry it.

(1) Re-record critical_path_minutes by its documented rule, the p90 of a 40-run window: 34.267 -> 35.317. Rejected by the owner's ruling, which names the band and not a budget re-record. On the graded statistic the band is the looser of the two: it passes an 8-run median up to 35.567, 0.25 min more than the 35.317 the re-record would pass. This is a budget move, not code, so archscore has nothing to read.
Architecture score: dS +0.0000 NULL (the unpaid head; a re-record changes the same JSON file and no package code)

(2) A critical-path pay-down by plan. This was round 4's analysis: the ending lane rotates (`fast (3.14)` 20 runs, `closures` 19, `arch-instrument` 9 of 60), so a cut to one lane leaves the others setting the path. Only `prelude` (60/60) and `tests / ci-ratchet` (47/60) sit on nearly every path. Those two are tried concretely as (a) and (c).
Architecture score: dS +0.0000 NULL (no code; the concrete arms are (a) and (c))

(3) Grade on a wider window (median of 40). That cuts the noise, but it changes how the instrument grades and was not the ruled fix. It goes to the orchestrator as a proposal for triage.
Architecture score: dS +0.0000 NULL (no code)

(a) Measure `archscore_metrics()` beside the two network fetches. Prototype 2113344ea:
- `ci_ratchet.py` gains `--archscore-out FILE` and `--archscore-json FILE`, and `derive()` reads the file when it is given.
- The workflow's Gather step backgrounds the measurement, runs both fetches, then `wait`s, and `Grade the ratchet` reads the file.
- The simulated cut is 28 to 36 s (0.45 to 0.53 min). That clears the live window's 0.308 at zero band, but not the recording window's 0.800.

Rejected:
- archscore cannot read it (NULL against both the merge base and this head), and judgement does not find it sounder. It adds a second input path for the same vector (`--archscore-json` beside the call), a parallel mechanism that fixer.md step 17 refuses. It also adds a background process and a `wait` to the job's error handling.
- It buys CI latency, not architecture. It does not remove the need for the band against the measured 1.300 spread.
- In a hotfix on the critical path it forces a FULL gate, and its effect is unreadable until 8 main pushes carry it.

The band is kept either way. As a CI-cost change it goes to the orchestrator as a proposal for triage (not filed as an issue).
Architecture score: dS +0.0000 NULL

(b) Share or delete code in the touched files. I searched for an existing owner of a tolerance band:
- `tests/structure.py` retired its only band, the FRACTION_METRICS ±0.005 band, on 2026-09-10, per the comment above `module_trees`.
- `tests/coverage_ratchet.py` deliberately has no tolerance.
- The archscore gate is tolerance 0 by its own docstring.
- `dev/governance/config/policy_budgets.json`'s `_band` is read by `policy_lint.mjs`, which is JavaScript. A Python ratchet cannot share it, and coupling the CI ratchet to the prose ratchet would join two owners, not dedupe one.

So no owner exists to share with. The one deletable redundancy in the added code is `{**{k: v for k, v in derived.items()}, ...}` in `record_table()`, which is `{**derived, ...}`. Prototype 94c7d38eb makes that one-line simplification. It does not touch the band, so it cannot pay for it. It reads NULL against both. Moving the head for it would void fix review round 4 for a cosmetic line. Not taken.
Architecture score: dS +0.0000 NULL

(c) A shallow prelude checkout on a push to main. In `## Figures`, prelude reads no history on that event. Prototype e4bebfe39 sets `fetch-depth: ${{ (github.event_name == 'push' && github.ref == 'refs/heads/main') && 1 || 0 }}` and keeps full history for every other event, including `batch/*` pushes. Measured here: a full fetch takes 19.4 to 22.6 s and a depth-1 fetch 3.0 to 3.2 s. So about 16 to 19 s (0.27 to 0.33 min) comes off every main path, consistent with CI's 18.5 s.

Rejected:
- Even with (a) the combined estimate is about 0.72 to 0.86 min, simulated and not measured. It straddles the 0.800 the recording window needs, so it cannot replace the band on evidence.
- It is a CI-cost change in `.github/workflows/ci.yml`, a gate file: FULL gate, unreadable until 8 main pushes.
- It is not architecture (NULL against both).

It goes to the orchestrator as a proposal for triage beside (a).
Architecture score: dS +0.0000 NULL

No payment that improves the architecture exists for this raise. The raise covers measured runner variance in a timing statistic that archscore does not read. Every candidate that would shorten the critical path is a workflow-scheduling change that reads NULL and adds no architectural soundness, and the one deletable code line is cosmetic and unrelated to the band. The raise is justified with a null score movement, not an improvement.
Architecture score: dS +0.0000 NULL

## Red checks

`tests / ci-ratchet` on main pushes 05c0d6d5d..0cae227c3: GREW critical_path_minutes 34.467 (budget 34.267). It is green again on later pushes at 34.233, inside 0.034 of the budget: the same flap, not a repair. Root cause (defect-root-cause.md, red-check trigger): the graded statistic is an 8-sample median of live runner timings, and its noise exceeded the headroom. No cheaper detector exists, because the metric reads only main's push-run history at the moment the job runs. A pull request's own run, prepr.sh and ci_predict.py cannot see it: none of their inputs come from the tree. The countermeasure is this band, sized from measured spread and typed as a raise when widened.

`budget-raise-gate / budget-raise-gate` (check-run 124777933192 at this head) and `gate` (124778270219), red through it alone. budget-raise-gate is red by design until a decisive approval names this head. The diff adds `tests/ci_budgets.json: critical_path_minutes_band` at 1.3, which both the base's and the head's schema read as a raise. It is the deliberate raise justified under `## Raise justification`, not a defect, so the root-cause rule owes nothing: no cheaper detector applies to a gate that exists to hold a raise for approval.

## Forward-carry

- The fix review's instrument finding (rounds 1 and 2): budget_raise_gate checks only the shape of the `Architecture score:` line, never its value against the arch-score job. Destination: the group's brief in dev/programme/rosters/wave-r10-groups.json, landed on `handoff/audit-r10-roster` at 697a0154f74b8873e681479a8e742eade69d06bf (group R10-FLY-MANDATE-REVOKE-GUARD, the carry beginning "From the #3045 round-1 fix review"). Carry: R10-FLY-MANDATE-REVOKE-GUARD
- The fix review's MAX0 finding: budget_raise_gate calls a removed band a raise. Carry: dismissed: a fail-closed false positive that opens no gate weakness, and only the owner can decide that removal should be routine
- The fix review's wording finding: the "86 runs of 2026-10-25" label spans 2026-10-25T00:42Z..2026-10-26T20:55Z. Carry: dismissed: only the label is loose, and every figure re-derives exactly
- Fix review round 3's plant observation: an `archscore.*_band` row passes the ratchet and is not a raise, but it is inert. Carry: dismissed: the planted row grants no tolerance (compare() applies a band only through BAND_KEYS), so no gate or grading weakness opens
- Fix review round 4's finding: the live-window cut 0.551 used the downward deviation. It is corrected in `## Raise justification` to 0.308. Carry: dismissed: the overstatement is internal to the body's arithmetic, does not change which payment clears and which does not, and moves no number in the tree

## Friction

none
