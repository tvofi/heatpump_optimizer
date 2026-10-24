# Fixer — raise the replay lane's `loop_cpu_ratio` cap to the measured value

Role: **fixer**, one change. Repository `tvofi/heatpump_optimizer`. Read `dev/governance/roles/fixer.md` first,
and `CLAUDE.md` rule 2 (budget raises) — **the owner has confirmed this raise in conversation**, quoted below.
**LOCAL seat only — no cloud.**

## The owner's confirmation (obtained before the push, as rule 2 requires)

tvofi, 2026-10-20, after being shown both measured options: **"yes, raise the caps"**, with `0.124` recommended and
`0.1575` offered as the alternative. Take **`0.124`**: it is √2 × the post-#2339-era median `loop_cpu_ratio`
(0.0877) and is the smallest cap covering every post-era row measured (0.0868, 0.0875, 0.0877, 0.0982, 0.1114).
Do **not** raise `cpu_ratio` (2.173) or `peak_kib` (2686.0) — neither is failing, and a raise without a measurement
is padding.

## The change

`tests/replay.py`, `COST_BUDGETS["synthetic-dhw-only.json"]["loop_cpu_ratio"]`: `0.111` → `0.124`. Update the
surrounding comment to carry the rule that produced the number — the five post-era readings and the √2 × median
construction — rather than the bare figure, and state the known margin: the 2× detection floor becomes 0.062, 0.3 %
above a twelve-run local minimum of 0.0618, so a local run can red on "cannot see a 2x" while CI's rows are safe.
That caveat is why the value is the median construction and not the largest-record one.

## What the body must carry

- `## Approval`: the owner's quoted confirmation above, the measured value, the construction, and a one-line
  rollback (restore `0.111`).
- `Part of #2272` — do not close it; #2514 (the instrument fix) also belongs to that group.
- The measurement command that prints the five readings and the √2 arithmetic, in `## Figures`.
- `## Red checks`: the nightly `slow` job's 2026-10-20 red (`loop_cpu_ratio 0.1114 over its budget 0.111`, run
  39387919507 job 118512165515) is the defect this answers — name it and say the cheaper detector is the lane's own
  per-run check, which is the one that found it.

## Controls

- **Failing test first**: the lane's own budget check must be red at the base with the measured value — run the
  synthetic fixture's cost line at the base and show `0.1114 over 0.111`; at the head show it under `0.124`.
- **Null control**: the 2× arm must still fire — doubling the loop work on the head's cap must exceed 0.124 for the
  CI readings (0.0868 × 2 = 0.1736 > 0.124); state it.
- **Mutation**: set the cap back to 0.111 in a copy and show the lane reddens on the recorded reading; set it to
  0.25 and show the 2× arm can no longer see the doubling for the lowest row (0.1736 < 0.25). Both runs in the body.
- `tests/entities.py` runs the cheap half of this lane on every PR; run it, and `tests/structure.py`, and
  `tools/pr/prepr.sh` on the body. `.github/workflows/` is untouched; `tests/replay.py` is code-owned, so tvofi
  reviews at merge — say so.

## Environment and handoff

Scratch: `/Users/timmalmstrom/hpo-seats/r10s3/replay-cap` (absolute). Worktree:
`git -C /Users/timmalmstrom/heatpump_optimizer worktree add /Users/timmalmstrom/hpo-seats/r10s3/replay-cap/wt -B handoff/r10-replay-cap origin/main`.
`export PATH=/Users/timmalmstrom/hpo-seats/r10s3/orch-wt/tools/audit/seat/shims:$PATH`. The box is loaded: state
load1 beside wall-clock figures, prefer counts. Push code to `handoff/r10-replay-cap` and body to
`handoff-body/r10-replay-cap`; no host path (#2310). Report under 200 words.
