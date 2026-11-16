Lands the approved round-11 start evaluation on main. `tools/audit/check_scopes.py --round 11` refused the round-11 finder start because `dev/audit/yardstick/round11/EVALUATION.json` was missing from the tree. The evaluation was written, reviewed (evaluation review round 4 approves 83dc948818) and ruled by the owner, but it existed only on `eval/r11`. This is a `--no-ff` merge of `origin/eval/r11` at c04cef7fca50e00fa23466dab28f941a4d5034af into main, so the review sha the record names stays in the history `check_scopes` reads. One commit on top, 8d2bc61ac1, makes `dev/audit/rounds/round11/evaluation/tally.py` find the repository root with the canonical `repo_root` helper: its `here.parents[5]` resolved one directory above the root, and `tests/harness_headers.py` refuses that depth seam. ed87ef7e6d merges this PR's previous head c5ac4df684, which held the older c6ce415b77 copy, and keeps these two files from 8d2bc61ac1 and the delivery row from c5ac4df684. Apart from that fix, `eval/r11` changes only the nine files under `dev/audit/yardstick/round11/` and `dev/audit/rounds/round11/evaluation/`. Nothing else changes. Every new path is under `dev/audit/`, which `tests/closure.py` lists as INERT (`orphan_files()` is empty at this head), and `dev/audit/config/scopes.json` `_coverage_excluded` already classifies `dev/audit/{rounds,yardstick}/**`. Group R11-START-EVALUATION-LAND.

## Head

ed87ef7e6d5af44eb4f6755c4883bd7bab92438c

## Mutation proof

n/a: a record landing with no code change. Two controls. Removing `EVALUATION.json` brings back the original refusal, shown under Null control. Landing the same nine files as a byte-identical copy without the merge (55148fa033, same tree) leaves the gap `review sha '83dc9488180379b859042b5f24b87d94a5a02c95' is not a commit in the ref's history`, which this merge removes.

## Null control

At origin/main e352724335, `python3 -I tools/audit/check_scopes.py --repo . --ref HEAD --round 11` gives `FAIL start evaluation round=11: 1 gap(s)` (`EVALUATION.json is not in the tree`). At this head it reads the evaluation: the review-sha and graded-objects checks pass, and what remains is 14 accepted cards that are not yet merged. Their own groups build those cards; this PR does not.

## Figures

none

## Red checks

`tests / fast (3.14)` and `tests / nightly-status` at c5ac4df684, the previous head of this PR: `tests/harness_headers.py` FAIL depth seams at `dev/audit/rounds/round11/evaluation/tally.py:13: repo = here.parents[5]`. Fixed at 8d2bc61ac1; `harness_headers.depth_root_seams()` returns `[]` at this head. Cheaper detector: none ran. prepr does not run the gate scripts, `dev/audit/` is INERT, so the scoped gate selected nothing, and `harness_headers.py` runs only in CI as `run_always`. The standing cost of a standalone depth-seam scan in prepr is a few seconds per run. It is not built here.

`tests / closures` at c5ac4df684: INERT READS UNDER-APPROXIMATED, because `tests/harness_headers.py` opens the seven new `dev/audit/rounds/round11/evaluation/*.py` files and its committed `inert_reads` does not list them. That same unlisted read is why the scoped gate never selected `harness_headers.py` for this diff. The closures-autofix job owns this repair (`ci-autofix.md`): it re-records the `inert_reads` and pushes the bot commit to this branch. This seat does not duplicate it. Cheaper detector: prepr ran with PREPR_SKIP_CLOSURES=1, and a full `derive_closures.sh` is refused off Linux (`gate-scoping.md`), so none runs on this host.

## Forward-carry

none

## Friction

none
