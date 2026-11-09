Round-10 roster record: the roster ops and triage records since the last landed handoff, on `handoff/audit-r10-roster`. Part of #201. It closes nothing by keyword and leaves #201 open.

The change is roster state and triage records only: 13 files in the handoff range against the merge base with `origin/main` at `2f6d699e504d6dc0bb6040d99c21c5b015a290e4` (measured 2026-11-09 18:43 UTC; a figure that is a function of main's tip is stale once main moves), plus this PR's own delivery row, 14 in all. One is `dev/programme/rosters/wave-r10-groups.json` (3263 lines in, 386 out), twelve are new `dev/programme/triage/s6-batch129.md` to `s6-batch140.md`, and the fourteenth is the new delivery row `dev/programme/delivery/3377.md`, which the PR adds and the handoff range does not carry. No production or test code is touched.

The handoff range holds 604 non-merge commits and 1 merge commit (a sync with `origin/main`): 528 `roster_edit` ops, 61 `roster_sync` derivations, 10 `triage:` records and 5 `record:` commits; this PR's own delivery row is a sixth, outside the range. The 528 ops by verb: 168 `mark-carry`, 152 `append-carry`, 60 `set-stage`, 47 `append-group`, 22 `set-after`, 20 `set-resume`, 17 `wire-issue`, 14 `set-files`, 14 `batch`, 6 `edit-brief`, 5 `drop-carry`, 2 `set-size`, 1 `unwire-issue`.

Groups go from 342 on `origin/main` to 400: 58 added, none removed, 54 existing groups change. 40 groups change stage: 24 reach `done`, 12 `carries-open`, 3 `refused`, 1 `refuted`. Carries across all groups go from 1337 to 1566; 45 groups change carry count: 24 are added groups that arrive with carries and 21 are existing groups.

The latest six ops, over the previous body's `e948d9d48d`, are `042b557dc7` `append-carry R10-FLOW-TOOLKIT-MODEL`, `46698c7a9d` and `79a953a5ef` `drop-carry R10-CI-PRIORITY-PAUSE`, `7cca26ac72` and `0c03637f8b` `append-carry R10-TRAIN-MERGE-LOOP-2`, and `a38742de9f` `set-stage R10-HOTFIX-GATE-BUSY-DEFER` to `refuted` (`git log e948d9d48d480fb3f7e13ff526159e141a273f4a..a38742de9f2cf1c8a9df3a5fa5f71e22ea31caec`).

## Head

`a38742de9f2cf1c8a9df3a5fa5f71e22ea31caec`, the tip of `handoff/audit-r10-roster`, is the code head every figure here is measured at. The pull request head `b74fd1ac9b676610966d80aeba0e83a8be0638fe` (`refs/pull/3377/head`) is older: the relay replaces it with this handoff plus this PR's delivery row. The roster blob at the code head is `536ba718313fa1c38592419403ae54840e090c7a`. Read the diff three-dot: a two-dot diff shows main's own newer commits.

## Mutation proof

n/a: roster state and triage records only; no production or test code.

## Null control

`origin/main` carries 342 groups and its roster blob is `c96d0d1eee72a6d36839dbea270b8a5fe2f37eae`; at the code head it is `536ba718313fa1c38592419403ae54840e090c7a`. A script keying both trees' groups by `group` prints `342 400 58 0 54` (main's count, head's count, added, removed, changed). Had the keying been vacuous, a blob that differs would print `added 0 changed 0`; it does not. The lint control: `node tools/policy/brief_lint.mjs` on `origin/main`'s roster exits 0.

## Figures

- `git diff --numstat origin/main...a38742de9f2cf1c8a9df3a5fa5f71e22ea31caec` -- the roster `3263 386`, twelve triage files; 13 files. The delivery row `1 0` is this PR's own and is added on top.
- `git log --no-merges --format=%s origin/main..a38742de9f2cf1c8a9df3a5fa5f71e22ea31caec` -- 604 subjects; keyed on the first word, 528 `roster_edit`, 61 `roster_sync:`, 10 `triage:`, 5 `record:`. `git log --merges origin/main..a38742de9f2cf1c8a9df3a5fa5f71e22ea31caec` lists 1.
- The verb counts are the second word of the `roster_edit` subjects of that same range, sorted and counted.
- The group, stage and carry counts come from `python3` keying `json.loads(git show <ref>:dev/programme/rosters/wave-r10-groups.json)["groups"]` by `group`, comparing whole entries for changed, `resume.stage` for stage changes and `len(entry["carry"])` for carries, at `origin/main` and at the code head; a group absent from main counts zero carries there.
- `git merge-tree --write-tree origin/main a38742de9f2cf1c8a9df3a5fa5f71e22ea31caec` -- exit 0, no conflict.

## Red checks

none yet: no check has run on this body's head when it was written.

## Forward-carry

none

## Friction

none
