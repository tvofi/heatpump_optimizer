plan: the schedule model behind the round-10 page, mechanically re-derivable

The page's schedule lived inside the out-of-tree renderer, which both computed and drew it. This adds `tools/plan/replan.py` as the one schedule model: it reads the roster at its ref, the owner's caps and a measured durations file, then writes `plan.json`; the renderer, edited in place out of tree, now draws only what `plan.json` emits and refuses a roster that has moved past it. At roster branch tip `e3010676747126df614e595ae43477db7d32e7b9` (roster blob `277cdd3591938af542a3f72510389f9bc3378429`) and a replan instant of `2026-10-20T17:00Z`, the plan closes `2026-10-30T03:17Z`: 226.28 h, which equals the 226.28 h dependency chain, so capacity adds no queueing. It merges in 44 batches and pays 51 gate runs (44 batches + 7 stamps) for 5737.5 gate minutes.

`tools/plan/` is on `tests/closure.py`'s INERT list and in `tests/entities.py`'s `_INERT_TOOL_HOMES`: no gate script opens the model, and the must-classify set was checked with `closure.is_inert` (no file outside the inert homes is inert, and `tools/plan/` is in no recorded closure).

Three groups touching `coordinator.py` are in progress at the replan instant (`FREQ-DEFROST`, `NIGHT-FOLDS`, `SAV-REASONS`), against the owner's cap of two, while no coordinator pull request was measured open. The plan records that inherited set in `generated.inherited_coordinator` (cap, groups, `exceeds_cap`), and `--check` refuses a plan whose record is missing or disagrees; the cap itself is enforced on the groups the plan dispatches. The same record exists for an inherited group ahead of its dependency (`generated.inherited_dependency_violations`), which is empty at this roster because every running fixer's dependencies have merged.

## Head

b8558f0d087fbc54e11453c49b9174efd21c2260

## Mutation proof

`python3 -I tools/plan/replan.py --self-test` prints 32 ok lines. The planted cases separate refusal from warning by exit code: an over-cap wave makes `--check` exit 1, and a dependency cycle makes the command exit 2, each asserted by running the command in a subprocess. The run plants an inherited group ahead of its dependency and proves the plan records it and passes `--check`, that deleting the record refuses, and that deleting the inherited-coordinator record refuses; two builds from identical inputs are byte-identical. A mutation harness then proves an UNMUTATED copy of the file, with `durations.json` beside it, exits 0 -- the null control, without which a copy missing its durations file fails for free -- and deletes six production lines one at a time: the earliest-attempt selection, the coordinator cap, longest-path dispatch, the patch-stamp cadence, the CI formula and the cancelled-leg price. Each mutant's self-test must exit 1, and the harness prints the target line and its rc.

## Null control

The unmodified renderer's model starts all eleven in-progress groups at the replan instant, so it draws 11 in flight against the owner's cap of six, and it gives every merge its own gate (50 merges plus 7 stamps = 57). The replanner admits six -- longest remaining path first, which selects exactly the six fixers the brief names as running -- queues the rest, and batches merges. Under the renderer's own size durations (S 5, M 8, L 11, XL 14 h) the model change alone moves closure 127.6 h to 120.6 h and gates 57 to 52; under the measured durations it moves 242.7 h to 226.28 h and 57 to 51. Both sides were run at the same fixed start on the same roster tip by `~/hpo-seats/r10s3/plan-opt/compare.py`; the renderer's schedule is the one it printed at the pre-change head.

## Figures

All schedule figures are taken at roster commit `e3010676747126df614e595ae43477db7d32e7b9` (blob `277cdd359193`), start `2026-10-20T17:00Z`; the command below pins that commit, so a later branch tip cannot move the numbers.

- closure `2026-10-30T03:17Z`, wall 226.28 h, 44 batches, 7 stamps, 5737.5 CI minutes: `python3 -I tools/plan/replan.py --roster-ref e3010676747126df614e595ae43477db7d32e7b9 --start 2026-10-20T17:00:00Z --out /tmp/plan.json`.
- dependency chain 226.28 h over 12 links: `python3 -I tools/plan/replan.py --check --plan /tmp/plan.json` plus the per-group `duration_minutes` in `/tmp/plan.json`.
- CI medians and samples: `python3 -I tools/plan/replan.py --measure-ci --out-durations /tmp/durations.json`; fast (3.14) 55.2 min (n=29, IQR 41.2-56.7), closures 28.4 (n=30, IQR 21.7-30.1), Analyze (python) 27.1 (n=30, IQR 21.5-27.9, 2 cancelled, rate 0.067), gate 112.5 min. The cancelled rate's denominator is the Analyze rows, not the commits whose three legs had all completed: the previous recording divided 1 cancelled by 26 complete triples where the Analyze rows held 2 cancelled of 29 (the missing one is `575dad30`, whose fast leg finished after that read). `tools/plan/durations.json` carries the shas and job ids. The medians are an instant's: they were measured at `2026-10-20T17:53Z`, and a later read includes check runs that completed after that instant (the committed file's `measured_at` names it).
- batch-window trade at the same blob: `--batch-window-minutes 20` prints 228.28 h / 44 batches / 5737.5; `--batch-window-minutes 120` prints 238.28 h / 44.

## Red checks

none

## Forward-carry

Carried in the tree at `dev/programme/carries/carry-201.json` (entries 13-16, issue #201); `node tools/policy/brief_lint.mjs dev/programme/carries/carry-201.json` reports 0 errors. The four findings, each routed:
- The retired wave-table document's waves and critical path are stale (7 of its wave-1 groups are done; 6 wave-2 groups are in progress) and lose to the roster's `after` edges. Carry: #201
- The retired hand-cut wave JSON names 39 of the roster's groups and leaves 18 open groups in no wave; it is retired, not regenerated. Carry: #201
- The drain document's 16 open pull requests: one was open at the plan's measurement instant (2026-10-20T17:53Z, #2510; #2491 had merged at 17:19Z). Its schedule loses, its merge-mechanism rules stand. Carry: #201
- The roster's `wave` field disagrees with the depth derived from `after` for 40 of the 45 open groups that store one (the other five store none); it needs a re-record on the roster branch. Carry: #201

## Friction

r10-pr-cap: contradiction: the pre-change renderer starts 11 in-progress groups at once, over the owner's six-open-PR cap; the replanner admits six, which selects the six running fixers. Carry: #201
plan-target: unenforced: at batch window 0 the measured closure is 2026-10-30T03:17Z, 1.4 days past the mandate's 2026-10-28T18:14Z and 9 days past the owner's 2026-10-21 target when replanned on 2026-10-20; the chain is its own floor, so only a roster edge release moves the date. Carry: #201
