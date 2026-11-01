Triage batch 100 rules two CI proposals that the orchestrator s9 sent by message on 2026-11-01. Both come from the #3045 fixer's measurement over about 60 main push runs. This is the rolling batch after batch 99, which was pushed first and left at its head.

- **P355: REJECT.** Running `tests / ci-ratchet`'s archscore measurement beside its fetches.
  - **Measured.** Job 124777140994 at `df66556f2` spends 31 s gathering, 8 s fetching runs and 30 s grading, in a 74 s job, so the overlap saves at most about 30 s (the stated 0.45 min).
  - **Nobody waits on it.** The job runs only on a push to main, and the train's `--overlap` makes `main_green` log-only, so no batch merge waits on it.
  - **The cost.** A workflow edit forces a `MODE: FULL` gate on the PR, and it needs a cross-step interface in the gate workflow. That is marginal against 30 s on a push-only job, and against ratchet headroom that #3045's 1.3 band already exceeds.
- **P356: DEFER, to #3045 (R10-HOTFIX-CI-CRITPATH-2, open, approved).** Grading `critical_path_minutes` on a 40-run median.
  - **The flap is #3045's measured subject.** An 8-run median spreads by up to 1.300 min over 145 runs, against 0.5 min of headroom. #3045's owner-ordered 1.3 band is the fix.
  - **A second statistic for the same row is unmeasured against that band.** It also lags real growth by about 16 h and quintuples the per-run jobs reads.
  - **What would change the answer.** main still red inside the band after #3045 merges, or a same-window measurement showing a 40-run median with a narrower band beats 8 runs plus 1.3.

No roster op: neither ruling is an ACCEPT. No product behaviour changes: the diff is one markdown file under `dev/programme/triage/`.

## Head

`a82575c0f21328ebda622e997787b532d6373d00`; the file is the whole diff against `df66556f2`.

## Mutation proof

This file's only consumer is the triage gate in `tools/audit/seat/roster_edit.py`, through `ruling_verdict` and `triage_refusal`.
- On the committed file, `ruling_verdict` reads P355 as `REJECT` and P356 as `DEFER`.
- A carry naming `proposal P355` and citing `#P355` is refused: `dev/programme/triage/s6-batch100.md#P355 is not an ACCEPT ruling (REJECT)`.
- A carry naming `proposal P356` and citing `#P356` is refused: `... #P356 is not an ACCEPT ruling (DEFER)`.

## Null control

- With the file absent, a carry citing it is refused, because the citation does not resolve: `the triage ruling ... is not on the roster branch or origin/main`.

## Figures

- `gh api repos/tvofi/heatpump_optimizer/actions/jobs/124777140994`: conclusion success. Step times: Gather 06:52:07-06:52:38, Fetch runs 06:52:38-06:52:46, Grade 06:52:46-06:53:16, and the whole job 06:52:02-06:53:16.
- `gh pr view 3045`: OPEN at `9ef51b821`, APPROVED.
- `tests/ci_ratchet.py` line 469: `PUSH_WINDOW = 8`.
- No capped file is touched.
- Scoped prepr: `MODE: SCOPED`, rc 0. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

`none`. A ref with no pull request has no checks.

## Forward-carry

none

## Friction

none
