plan: the schedule model behind the round-10 page, mechanically re-derivable

The page's schedule lived inside the out-of-tree renderer, which both computed and drew it. This adds `tools/plan/replan.py` as the one schedule model: it reads the roster at its ref, the owner's caps and a measured durations file, then writes `plan.json`; the renderer, edited in place out of tree, now draws only what `plan.json` emits and refuses a roster that has moved past it. On the current roster the plan closes 235.45 h after the replan instant -- `2026-10-30T11:27Z` from a start of `2026-10-20T16:00Z` -- against a 226.28 h dependency chain, so 9.17 h of the span is queueing and the chain, not capacity, sets the date. It merges in 39 batches for 4884 gate minutes.

`tools/plan/` is on `tests/closure.py`'s INERT list and in `tests/entities.py`'s `_INERT_TOOL_HOMES`: no gate script opens the model, and the must-classify set was checked with `closure.is_inert` (no file outside the inert homes is inert, and `tools/plan/` is in no recorded closure).

## Head

d4e3eb0cecdca713f9aac0ca5c3f099438582a29

## Mutation proof

`python3 -I tools/plan/replan.py --self-test` runs 13 checks. The planted cases separate refusal from warning by exit code: an over-cap wave (eight groups in flight at one instant) makes `--check` exit 1, and a dependency cycle makes the command exit 2, each asserted in the self-test by running the command in a subprocess. The same run builds twice from identical inputs and asserts the output is byte-identical, and asserts that seven in-progress groups against six slots admit six and queue one.

## Null control

The unmodified renderer's model starts all eleven in-progress groups at the replan instant, so it draws 11 in flight against the owner's cap of six, and it gives every merge its own gate (48 merges plus 6 stamps = 54). The replanner admits six -- longest remaining path first, which selects exactly the six fixers the brief names as running -- queues the rest, and batches merges. Under the renderer's own size durations (S 5, M 8, L 11, XL 14 h) the model change alone moves closure 125.6 h to 122.0 h and gates 54 to 38; under the measured durations it moves 238.9 h to 235.45 h and gates 54 to 45. Both sides were run at the same fixed start on the same roster ref by `~/hpo-seats/r10s3/plan-opt/compare.py`; the renderer's schedule is the one it printed at the pre-change head.

## Figures

- closure 235.45 h after the stated start, 39 batches, 4884 CI minutes, 6 stamps: `python3 -I tools/plan/replan.py --roster-ref origin/handoff/audit-r10-roster --out /tmp/plan.json`.
- dependency chain 226.28 h over 12 links: `python3 -I tools/plan/replan.py --check --plan /tmp/plan.json` plus the per-group `duration_minutes` in `/tmp/plan.json`.
- CI medians and samples: `python3 -I tools/plan/replan.py --measure-ci --out-durations /tmp/durations.json`; it prints the merged-tree count and writes fast (3.14) 55.2 min (n=26), closures 25.1 (n=28), Analyze (python) 27.2 (n=29, IQR 21.5-28.1, cancelled rate 0.038); `tools/plan/durations.json` carries the shas and job ids.
- batch-window trade, measured at a fixed start: `python3 -I tools/plan/replan.py --batch-window-minutes 20 --out /tmp/plan20.json` prints 237.67 h / 37 batches (4667 CI minutes); `--batch-window-minutes 120` prints 249.33 h / 37.

## Red checks

none

## Forward-carry

The plan documents disagree with the roster; the roster's `after` edges and `resume.stage` win, and the owner's caps win on capacity. `Carry: #201` for each:
- WAVES.md's wave 1 names 10 groups, 7 merged; of its wave-2 list of 17, FREQ-DEFROST, NIGHT-FOLDS, REPLAY-LANE, SAV-REASONS and TRAIN-HOLD are in progress now (wave 1). Its 146.2 h critical path comes from edges the roster no longer carries.
- WAVES.json names 39 of 96 groups, leaves 16 open groups in no wave, and is read by nothing now; retired, not regenerated.
- DRAIN.md's 16 open pull requests are 2 now (#2490, #2488); its process rules still bind, its schedule does not.
- The roster's own `wave` field disagrees with the depth derived from `after` for 40 of 48 open groups (NIGHT-FOLDS records 6, derives 1) and needs a re-record on the roster branch.

## Friction

r10-pr-cap: contradiction: the pre-change renderer starts 11 in-progress groups at once, over the owner's six-open-PR cap; the replanner admits six, which selects the six running fixers. Carry: #201
plan-target: unenforced: measured closure is 235.45 h from the replan instant, 1.7 days past the mandate's 2026-10-28T18:14Z and 9 days past the owner's 2026-10-21 target when replanned on 2026-10-20; the 226.28 h chain is the floor, so only a roster edge release moves the date. Carry: #201
