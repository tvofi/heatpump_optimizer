Fix review: merge b0f13c832f425ce5f49df540f0222c5e39ed7b54

bus-nonce: 234e5e1a8df77cdee7b3c919029f3009
pending-ci: gate

Round: 3 (delta over the reviewed head 7b687a4819e54718f84e4353ce92f665414cb70e). Scope: the delta, the prior verdict's finding and the live required checks. The delta is three merge commits: `155036423d` (origin/main into the branch, `tests/layout.json` and `tests/closures.json` resolved by hand), `a66553442a` and `b0f13c832f` (automatic merges of main). It has no `custom_components/` change in the PR's own diff, so the scope does not widen.

## Findings

- Unchanged from round 2: `violations` still accepts four semantically wrong inputs, and each draws a misleading page without crashing. They are `started` later than `finished`, `forecast.start_from` later than `start_to`, `round: true` (rendered as "Round True phases") and a `round` that disagrees with its `round<N>/` directory. The delta does not touch `tools/audit/seat/plan_phases.py`, so the round-2 measurements stand at this head. Carry: R11-PRE-PLAN-RENDER

## Evidence

- Own diff unchanged except for the merge resolution. `git diff <merge-base> <head>` gives 11 files, +899/-15, at both 7b687a48 and b0f13c83. Only one changed line differs: the `dev/programme` "why" string in `tests/layout.json`, which `155036423d` resolved as the union of main's "the owner's standing rulings" and the branch's "each round's phases file". The `tests/closures.json` resolution keeps both `plan_phases.py` (branch) and `plant_recall.py` (main). Both resolutions are correct (ev/delta.txt). `review_carry.py` prints FRESH-REVIEW only because `155036423d` is a hand resolution and not the automatic merge.
- Mutation proof re-run at this head with the PR's driver (`dev/audit/harnesses/r10_plan_page_mutants.py M0` plus all 27 `phases-*` mutants): `RESULT mutant=M0 rc=0 fails=0 verdict=null`, all 27 killed, `RESULT survived=0` (ev/mutants.txt).
- Self-tests at this head: `plan_page self-test: 136 checks, 0 failed`. `plan_phases.py --check dev/programme/round11/phases.json` gives rc 0, and the `plan_public` and `state_docs` self-tests pass (ev/selftests.txt).
- Merge with main: `git merge-tree --write-tree origin/main b0f13c832f425ce5f49df540f0222c5e39ed7b54` gives rc 0, with origin/main at 47f0f18a7e (ev/merge-tree.txt).
- Head: the body's `## Head` names b0f13c832f425ce5f49df540f0222c5e39ed7b54, and `refs/pull/3622/head` reads that SHA.
- Role contracts: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- The own diff touches no VERSION, manifest, RELEASE_NOTES, golden, claim, budget or `custom_components/` file.
- Finder's harness: none named. This is an owner-directive feature, as in rounds 1 and 2.
- Carry destination: `R11-PRE-PLAN-RENDER` is on origin/main's `dev/programme/rosters/wave-r10-groups.json` with `resume.stage: not-started`.
- Red checks: classify reads `red: none` at this head on every run. The digest's `gate` failure is the earlier attempt, and classify decides. No red at this head is in `owed-reds`' set. The packet's `introduced-red: unreadable` was rendered while `governance / instrument-self-tests` was still in progress. classify reports no red since, so no INTRODUCED red is known at this head.
- CI: `merge_train.py classify b0f13c832f425ce5f49df540f0222c5e39ed7b54 --pr 3622` read `WAIT b0f13c832f425ce5f49df540f0222c5e39ed7b54 pending: gate red: none` on all 30 runs from 01:36 to 02:06 UTC (ev/classify.txt), so this verdict carries `pending-ci: gate`. The head is unchanged at the end of the review: `refs/pull/3622/head` = b0f13c832f425ce5f49df540f0222c5e39ed7b54.
