Investigation pre-study on tvofi's question: the merge-path study measured
`tests/boost_drift_replay.py` at 7 runs per merge and concluded no run is a
byte-identical re-grade — this study attacks that conclusion, re-derives the
count from real runs, and judges every consolidation mechanism sound or
refused. Study only: no production file changed, no budgets file touched, no
PR opened from this seat.

## Head

`488aca6e1276b056ae053d3d60b71747292542c8` (handoff/r9-heavy-consolidation-prestudy; baseline `origin/main` = `a74520020`)

## Mutation proof

n/a: a measurement document; its controls are the re-derivation against the sibling study's own run ids (§1: 7x confirmed for the reach-PR-alone case, 3.8/merge day average) and the tree-identity check (`142e9b213` proof tree == last merge `6918cb4b2`'s tree, `git rev-parse ^{tree}`), both reproducible from the commands in §8.

## Null control

The sibling study's conclusion re-read at the same heads: its own text names the batch-last-entry exception but refuses the whole push run (r4); this study splits the refusal at the arm level and finds the closures arm's push-side recordings have no consumer beyond the in-job check (no upload step runs on push — measured, job `114309000519`).

## Figures

- 10 boost runs for the 3-merge batch of 2026-10-10 20:42Z — `gh api` job logs of runs `38081141948`, `38084808934`, `38084956560`, `38085092106` (per-script lines quoted in §8).
- push-side boost lane time 17404 s for 3 merges — same logs, walls from the `[HH:MM:SS] record/done` and `wall=Ns` lines.
- day average 3.8 runs/merge — `git log --merges origin/main` (10 PR merges) + `gh api .../actions/runs?branch=main&event=push` (11 Tests runs), 2026-10-10.

## Red checks

none

## Forward-carry

dev/audit/rounds/round9/prestudy/heavy-script-consolidation-prestudy.md — the two sound consolidations (C1 composed tracer+audit-hook measurement, C2 proof-recordings consume) land there for the instrument-series planning on #201; C1's proof obligations extend PR 2 (vi-a)'s acceptance shape (one more byte-identity equality, the read set).

## Friction

none
