Round-10 roster record: the roster ops and the triage ruling they cite, at the tip `6c83e6a56f7badd592bb07db50e54d630e5004b7` of `handoff/audit-r10-roster`. Part of #201. It closes nothing by keyword and leaves #201 open.

The change is roster state plus one triage ruling the roster's carries cite: 2 files against `origin/main` at `9315526f8dca6dcd07f9cf3f2685bd1dd633b4f6`. `dev/programme/rosters/wave-r10-groups.json` moves 2556 lines in and 983 out; `dev/programme/triage/s6-batch125.md` adds 35 lines (batches 119 to 124 are on main already). The branch has 1240 non-merge commits over main's merge base (itself, the handoff having merged main): 540 `append-carry`, 167 `drop-carry`, 131 `set-stage`, 93 `append-group`, 57 `wire-issue`, 54 `set-resume`, 42 `set-after`, 23 `edit-brief`, 17 `mark-carry`, 5 `set-files` ops, 99 `roster_sync` derivations and 12 other `roster:` and `record:` commits.

Groups go from 302 on `origin/main` to 337: 35 are added and none removed, and 98 existing groups change. 55 groups change stage: 32 reach `done`, 13 reach `carries-open` and 10 `absorbed`. No production or test code is touched.

## Head

`6c83e6a56f7badd592bb07db50e54d630e5004b7`, the tip of `handoff/audit-r10-roster`: `0a462125901937b2629ec0daae8061890bfdbcbe` plus two roster commits, an `append-carry` and its `drop-carry` on R10-HANDOFF-PATH that net to no change. `0a4621259` is the earlier tip `b09e24fbcc027edd899fb6ec8276691026687482` (roster ops through the P387 pointers from #3212's round-4 ruling) merged with `origin/main` at `9315526f8dca6dcd07f9cf3f2685bd1dd633b4f6`; its one conflict, `dev/programme/triage/s6-batch122.md`, was resolved to main's version (blob `762260c83`), which is #3212 as merged. Every figure below was measured on a detached worktree at the tip. Read the diff three-dot: a two-dot diff shows main's own newer commits.

## Mutation proof

n/a: roster state and a markdown ruling only; no production or test code.

## Null control

`origin/main` carries 302 groups and the roster instruments pass on it; its roster blob is `8a4dcc3fd3861d4ad32c0c658090d318c64d2db9`. At this head the blob is `cd94098e10cade415ec41f5f1504cef974dedc4e`. A script keying both trees' groups prints `302 337 35 0 98` (counts, added, removed, changed). The control that proves the lint reads: `node tools/policy/brief_lint.mjs` on `origin/main`'s roster exits 0, and at this head exits 0 as well with `TOTAL: 0 error(s) across 1 file(s)`.

## Figures

- `git diff --numstat origin/main...6c83e6a56f7badd592bb07db50e54d630e5004b7` -- the roster `2556 983`; `s6-batch125.md` `35 0`; 2 files.
- `git merge-tree --write-tree origin/main 6c83e6a56f7badd592bb07db50e54d630e5004b7` -- tree `109d6f626bd4b6a76abc44c525bf78697791230a`, no conflict.
- The group counts above come from `python3` keying `json.loads(git show <ref>:dev/programme/rosters/wave-r10-groups.json)["groups"]` by `group`; stage changes 55 (32 done, 13 carries-open, 10 absorbed) from the same keying on `resume.stage`.
- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` -- `TOTAL: 0 error(s) across 1 file(s)` at this head.
- `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED` at this head.
- Overlap: `s6-batch125.md` here is byte-identical to the blob on `handoff/triage-s12-batch125` (#3237, `38e165713`); `s6-batch122.md` equals main's (`762260c83`). `s6-batch126.md` (#3238) is not in this handoff.

## Red checks

none yet: no check has run on this head when the body was written.

## Forward-carry

none

## Friction

none
