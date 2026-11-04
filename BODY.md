Root-cause record for the third `GREW critical_path_minutes` on `main` (`8f286293b`, run 41397326281). It is the product of the root-cause seat, run beside the hotfix fixer and not inside it (`dev/governance/roles/root-cause.md`). The record is `dev/audit/rca/r10-ci-critpath-3.md`, with its replay harness `dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py` over the Actions-API fixture `runs.json` beside it. The code at the head is unchanged from that seat's push; this body only carries it.

New since the record was written: the hotfix `r10-hotfix-ci-critpath-3` has merged as `#3180` (merge `fad43b047`, 2026-11-04 09:25 UTC, `git log origin/main`). The record still says that hotfix is open (dispatched 11-04 05:13). The record's conclusions are not changed by the merge, and the document is not edited here.

**Named cause.** The `tests / ci-ratchet` row `critical_path_minutes` grades elapsed minutes on hosts the repository does not choose. The closures lane is bimodal (18.6–29.3 min or 33.7–40.0 min on identical work), so the 8-run median flips with the mixture of host classes the runs drew. The grade reproduces exactly (36.5 against 35.567). The work did not move: the planned longest lane was 1332.8 s and then 1345.7 s, and the same 34 scripts ran 1.85 times slower on one host than on another. The class reaches only this row, the one timing row in any `*_budgets.json`, and has hit it three times.

**Process state: (c)**, followed and it did not produce the intended result. Hotfix 2 followed the calibration rule in `tests/ci_ratchet.py` to the digit (p90 34.267, band 1.3). The rule assumes unimodal noise around the work, and the bimodality was already in the calibration-era data, so this is not (d). Nothing was skipped, so it is not (b). For the 14.4 h in which sessions were driving while `main` was red, the record states the state as undetermined between (b) and (c), since the tick board was never persisted. For the 32.1 h in which no session was driving, it records a refusal, because the cost there is about 0.

**Cost test**, with the record's numbers: `cost(countermeasure, recurring) < cost(defect) x P(recurrence)`. P(recurrence) is 3 occurrences in 8.4 days, 0.36 a day. Red main lasted 4.6, 27.9 and at least 47 h, a mean of at least 26.5 h, about 9.5 h of red main a day. 19 pull requests merged onto the red `main`. The countermeasure's standing cost is about 80 s a day (0.27 s a replay, 300 runs a day). The test passes by more than two orders of magnitude.

**Countermeasures**, two drafts for the owner and neither landed, since both change what a seat or a ratchet row must do and that is policy:

1. Grade the planned critical path (the longest lane of `closure.lane_plan` over the recorded seconds in `tests/closures.json`, 1345.7 s today) at PR time, and keep elapsed minutes as a printed observation that does not gate. It is host-invariant, and adding 300 s to `tests/stress.py` moves it 1345.7 to 1445.7. The record states what it does not cover.
2. `pr_cap.py dispatch-gate` refuses a non-expedite dispatch while the required checks on `main` are red. This would have stopped the first of about 54 dispatches at 06:40 on 11-02, instead of the hotfix dispatch 46.5 h later.

Also recorded: no root-cause record reached the first two reds, because `tests / ci-ratchet` runs only on a push to `main` and `defect-root-cause.md` enforces its second trigger only on a check red on a branch commit. Whether that rule should name push-only checks is the owner's call.

## Head

9f959dd9c7eeb715ebe9eb992c066b0dfb1c3e79

## Mutation proof

n/a: this change adds a root-cause record and its replay harness and fixes nothing in production code. The record's countermeasure demonstration is in its section 4 (replay step 3, 300 s added to the `stress.py` recording moves the planned path 1345.7 to 1445.7).

## Null control

n/a: no production code changes. The replay's own null control gives the same tree the same planned-path value twice (replay step 3).

## Figures

- `python3 dev/audit/harnesses/r10_rca_ci_critpath_3/replay.py` prints the grade reproduction (36.5 against 35.567), the slow-draw windows and the planned-path control.
- `python3 tests/closure.py lane-plan --all-scripts --lanes 3` prints the longest lane, 1345.7 s.

## Red checks

none: the branch has no pull request, and no check-run exists at the head to be red.

## Forward-carry

none

## Friction

none
