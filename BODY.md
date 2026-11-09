Round-10 roster record: the roster ops and triage records since the last landed handoff, on `handoff/audit-r10-roster`. Part of #201. It closes nothing by keyword and leaves #201 open.

The change is roster state and triage records only: 14 files against the merge base with `origin/main` at `2f6d699e504d6dc0bb6040d99c21c5b015a290e4` (measured 2026-11-09 17:27 UTC; a figure that is a function of main's tip is stale once main moves). One is `dev/programme/rosters/wave-r10-groups.json` (3185 lines in, 387 out), twelve are new `dev/programme/triage/s6-batch129.md` to `s6-batch140.md`, and one is the new delivery row `dev/programme/delivery/3377.md`. No production or test code is touched.

The range holds 595 non-merge commits and 2 merge commits (syncs with `origin/main`): 518 `roster_edit` ops, 61 `roster_sync` derivations, 10 `triage:` records and 6 `record:` commits, the last being this PR's own delivery row. The 518 ops by verb: 168 `mark-carry`, 148 `append-carry`, 59 `set-stage`, 45 `append-group`, 22 `set-after`, 20 `set-resume`, 17 `wire-issue`, 14 `set-files`, 14 `batch`, 5 `edit-brief`, 3 `drop-carry`, 2 `set-size`, 1 `unwire-issue`.

Groups go from 342 on `origin/main` to 398: 56 added, none removed, 54 existing groups change. 40 groups change stage: 24 reach `done`, 13 `carries-open`, 3 `refused`. Carries across all groups go from 1337 to 1564; 46 groups change carry count: 24 are added groups that arrive with carries and 22 are existing groups.

## Head

`b74fd1ac9b676610966d80aeba0e83a8be0638fe`, the pull request head, measured against its merge base with `origin/main`. It holds the handoff code head `012c21bc8950f57a70004cb0abee6f0a04de8669` (tip of `handoff/audit-r10-roster`, an ancestor) merged with `origin/main`, plus this PR's delivery row. The roster blob is the same at both: `dda98e12be69c3b660a7f9de719729d548dec22e`. The tip of `handoff/audit-r10-roster` has since moved to `0beb2a84e2c45b5d02915d77eab9e4fd96578b8d`, one commit past `012c21bc` (`git log 012c21bc8950f57a70004cb0abee6f0a04de8669..0beb2a84e2c45b5d02915d77eab9e4fd96578b8d`): an `append-group R10-HOTFIX-DELTA-REVIEW`, 40 roster lines in, outside every figure here, which are all measured at `b74fd1ac`. Read the diff three-dot: a two-dot diff shows main's own newer commits.

## Mutation proof

n/a: roster state and triage records only; no production or test code.

## Null control

`origin/main` carries 342 groups and its roster blob is `c96d0d1eee72a6d36839dbea270b8a5fe2f37eae`; at this head it is `dda98e12be69c3b660a7f9de719729d548dec22e`. A script keying both trees' groups by `group` prints `342 398 56 0 54` (main's count, head's count, added, removed, changed). Had the keying been vacuous, a blob that differs would print `added 0 changed 0`; it does not. The lint control: `node tools/policy/brief_lint.mjs` on `origin/main`'s roster exits 0, and at this head it exits 0 as well.

## Figures

- `git diff --numstat origin/main...b74fd1ac9b676610966d80aeba0e83a8be0638fe` -- the roster `3185 387`, the delivery row `1 0`, twelve triage files; 14 files.
- `git log --no-merges --format=%s origin/main..b74fd1ac9b676610966d80aeba0e83a8be0638fe` -- 595 subjects; keyed on the first word, 518 `roster_edit`, 61 `roster_sync:`, 10 `triage:`, 6 `record:`. `git log --merges origin/main..b74fd1ac9b676610966d80aeba0e83a8be0638fe` lists 2.
- The verb counts are the second word of the `roster_edit` subjects of that same range, sorted and counted.
- The group, stage and carry counts come from `python3` keying `json.loads(git show <ref>:dev/programme/rosters/wave-r10-groups.json)["groups"]` by `group`, comparing whole entries for changed, `resume.stage` for stage changes and `len(entry["carry"])` for carries, at `origin/main` and at the head; a group absent from main counts zero carries there.
- `git merge-tree --write-tree origin/main b74fd1ac9b676610966d80aeba0e83a8be0638fe` -- exit 0, no conflict.

## Red checks

none yet: no check has run on this body's head when it was written.

## Forward-carry

none

## Friction

none
