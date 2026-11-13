# Proposal triage, session s14, batch 193 (P615)

Sources:
- origin/main `ee64358be7`. Every line number below is at that commit. `tests/replay.py`,
  `tests/replay_cost_draws.tsv` and `tools/audit/seat/replay_draws.py` are byte-identical at
  `d08ed31049`, the failing nightly's head.
- Scheduled nightly run 42934263129 (`d08ed31049`, 2026-11-11T00:48Z): `slow` job 130240315059,
  `mutation-ledger (3)` job 130240315675. Last green scheduled run 42731027909 (`b8f67a7751`),
  `slow` log read for comparison.
- `handoff/audit-r10-roster` at `7e8826dd25`.

## P615: HOTFIX-REPLAY-CLASS-CUT

Verdict: ACCEPT, as a new hotfix group R10-HOTFIX-REPLAY-CLASS-CUT (S, lane C, severity high,
opus fixer and reviewer). It is a red on main, so the bar is the hotfix route, not the proposal
bar. The fix is a one-sided-down re-record of the replay runner-class budgets. That is a
tightening, not a ratchet raise.

Source: queue line 293, 2026-11-11T12:01:09Z, orchestrator s14: MAIN NIGHTLY RED, rule as a hotfix
group.

Instances:
- **What failed.** The `slow` log, job 130240315059:
  - `FAIL synthetic-dhw-only.json: cycle_cost [1 offender(s): cpu_ratio 1.727: budget 3.987
    cannot see a 2x cycle; re-record 2.442]`
  - `FAIL synthetic-dhw-only.json: cycle_cost sees a doubled cycle cpu [cpu_ratio 3.5914 against
    clean 1.7266: ...]`
  - The clean run reads `cpu_ratio 1.7266`, `ref_ms 41.36`. The cpu-doubled arm reads 3.5914.
- **Why: a stale class budget, not a regression.**
  - The job's ruler (about 41.2 ms) falls in `COST_RUNNER_CLASSES` ref40 (38.92-42.96). That
    class's `COST_CLASS_BUDGETS` cpu_ratio is 3.9874 (`:521-529`). `cost_offenders` (`:637-653`)
    is red when a reading times 2 is under the cap: 1.7266 x 2 = 3.45 < 3.99. The doubled arm's
    3.59 is under the same cap, so the second FAIL has the same cause.
  - ref40 rests on 2 clean draws in `replay_cost_draws.tsv`: jobs 126600478623 (2026-11-04, 2.7594)
    and 126971378040 (2026-11-05, 2.8809).
  - Both predate `17bb738485` ("one BLAS ThreadpoolController, built at import", merged by #3349,
    2026-11-09). That commit cut the synthetic cycle's CPU.
  - The previous night's green run read 1.5895 at `ref_ms 45.75`, in class ref47, which
    `fa3ab3e646` had already re-recorded down after the cut. So the ruler moved bands, and ref40
    was the first stale class drawn.
  - Between `b8f67a7751` and `d08ed31049`, `git diff` shows no change to `tests/replay.py`, the
    draws or `replay_draws.py`. The product commits in that window (23 files under
    `custom_components/`) did not raise the figure: 1.7266 sits inside the projected post-cut
    ref40 range below.
  - So the answer to "re-record or regression" is a re-record, down.
- **This is the second instance, and appending one draw does not end the class.**
  - `fa3ab3e646` (11-08) fixed the same failure for ref47 by appending one post-cut draw and
    re-deriving. `derive_cost_classes` (`:750`) centres a class at sqrt(2 x min x max) over all
    its clean draws, pre-cut ones included.
  - Measured cut factor from CI, per class: ref47 0.664 (geometric mid of pre-cut
    2.2558-2.4762 to post-cut 1.5508 and 1.5895); ref40 0.612 (2.7594-2.8809 to 1.7266).
  - Projected by 0.612-0.664, the pre-cut draws fall wholly or partly under the current floor
    (budget / 2) in six classes: ref23 (projected 1.20-2.39, floor 1.877), ref28 (1.16-1.79,
    1.595), ref31 (1.08-2.04, 1.644), ref38 (1.48-1.64, 1.729), ref40 (1.69-1.91, 1.994) and
    ref53 (0.88-0.99, 1.038). Only ref47 (1.50-1.65 at 0.664, floor 1.386) is clear.
  - These six classes hold 68 of the 117 draw jobs (58%). Ruler medians bucketed by the current
    bands: ref47 49, ref31 33, ref23 18, ref53 11, ref28/38/40 2 each.
  - Appending alone stays red for the wide classes. ref23's pre-cut draws already span 1.84x
    (1.9586-3.5974). With a post-cut reading of 1.30 the centre is 3.06 against 2 x 1.30 = 2.60,
    still red. ref31 at 1.17 gives centre 2.68 against 2.34, still red.
  - So the group re-derives every class with the pre-cut draws projected by an interleaved,
    one-box cut factor (the `#2205` / R10-RCA-2205 method, `:456-461`) or dropped where post-cut
    draws exist.
- **mutation-ledger (3).** Steps 6-9 never concluded. The check-run annotation reads "The hosted
  runner lost communication with the server", 1h44m into the job (00:48:49Z to 02:32:54Z). The log
  blob is gone (404). All four shards were green in run 42731027909 the night before. This is
  one lost runner with no code cause: no group, a re-run.
- **No existing owner.** The roster at `7e8826dd25` has no live group on `tests/replay.py` or
  `tests/replay_cost_draws.tsv`. R10-REPLAY-COST-BUDGET, R10-REPLAY-LOOPNORM and
  R10-HOTFIX-STRESS-MEM-PEAK are done. R10-REPLAY-COST-2 is refused (owner bar, 1 of 78 draws),
  and it is a different arm.

Cost:
- One S group: `tests/replay.py` (a budget table edit and the commit message's per-class
  derivation) and `tests/replay_cost_draws.tsv` (appended rows).
- One one-box interleaved measurement, the R10-RCA-2205 method.
- No new file, no new check, no `*_budgets.json` row.

Binding: the nightly is red now, and it reddens the non-required `nightly-status` on every
pull request. Six of seven classes are projected to fail, and they draw 58% of jobs, so an
ref40-only re-record would leave a further red on most nights. The group is sized to all classes
for that reason.

Disposition:
- New group R10-HOTFIX-REPLAY-CLASS-CUT, `append-group` queued by this seat. The brief is in the
  group JSON.
- Root cause: this is the second nightly red from a cross-class product change re-recorded in
  one class only (`fa3ab3e646` re-derived ref47 alone after `17bb738485`). Whether that owes a
  root-cause seat (`defect-root-cause.md`) is the orchestrator's dispatch.
