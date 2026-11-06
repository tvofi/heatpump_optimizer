Round-10 roster record: the roster ops since the last landed handoff, at the tip `c516cf0f6620cc5000c9b602b31aef0ec6389387` of `handoff/audit-r10-roster`. Part of #201. It closes nothing by keyword and leaves #201 open.

The change is roster state only: 1 file against `origin/main` at `862affd07d2ce3430c200d4f09aa6e16934b5c4d`. `dev/programme/rosters/wave-r10-groups.json` moves 279 lines in and 25 out. The earlier part of this handoff (the 1240 ops of the first record, with `s6-batch125.md`) already merged as #3239, so the merge base is `f85b3b4d56eed0b57f5b3b1f46471f8ae323113a`, the handoff code that #3239 landed. Since it, the handoff holds 52 non-merge commits and no merge commit: 36 `append-carry`, 5 `drop-carry`, 5 `append-group` ops and 6 `roster_sync` derivations.

Groups go from 337 on `origin/main` to 342: 5 are added (R10-REF-PRIVACY-CLOUD, R10-TRAIN-MERGE-LOOP-2, R10-HOTFIX-GATE-BUSY-DEFER, R10-CARRY-RESIDUE-2, R10-REPLAY-COST-2) and none removed, and 13 existing groups change. 12 groups change stage: 8 reach `in-progress`, 3 `carries-open` and 1 `done` (R10-HOTFIX-STAMP-BASE). Carry counts change on three groups: R10-PLANTED-DEFECT-AUDIT 3 to 6, R10-CLONE-2238 0 to 2, R10-PROCESS-SLIM 1 to 2. No production or test code is touched.

## Head

`c516cf0f6620cc5000c9b602b31aef0ec6389387`, the tip of `handoff/audit-r10-roster`. It is the code head `32911ca1a6e76e8ba1829d04bfb09db082b25e91` plus the `append-carry` ops that landed the four R10-CARRY-RESIDUE-2 carries and the later roster ops, each a plain commit on that line. The pull request head is this tip merged with `origin/main` by `update_pr.sh`, plus this PR's own row `dev/programme/delivery/3258.md`. Every figure below was measured on a detached worktree at the tip. Read the diff three-dot: a two-dot diff shows main's own newer commits.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`origin/main` carries 337 groups and the roster instruments pass on it; its roster blob is `f78ea1b149c6a142303255065b1c358d8b0dfe87`. At this head the blob is `0c869e6aa5c07a8d26b80f15dac808ab52392a45`. A script keying both trees' groups prints `337 342 5 0 13` (counts, added, removed, changed). The control that proves the lint reads: `node tools/policy/brief_lint.mjs` on `origin/main`'s roster exits 0, and at this head exits 0 as well with `TOTAL: 0 error(s) across 1 file(s)`.

## Figures

- `git diff --numstat origin/main...c516cf0f6620cc5000c9b602b31aef0ec6389387` -- the roster `279 25`; 1 file.
- `git merge-tree --write-tree origin/main c516cf0f6620cc5000c9b602b31aef0ec6389387` -- tree `c96d0d1eee72a6d36839dbea270b8a5fe2f37eae`, no conflict.
- The group counts above come from `python3` keying `json.loads(git show <ref>:dev/programme/rosters/wave-r10-groups.json)["groups"]` by `group`; stage changes 12 (8 in-progress, 3 carries-open, 1 done) from the same keying on `resume.stage`.
- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` -- `TOTAL: 0 error(s) across 1 file(s)` at this head.
- `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED` at this head.
- `python3 tools/audit/seat/ref_privacy.py --check` -- 30 files with a push site, 12 guarded, 0 refused.

## Red checks

none yet: no check has run on this head when the body was written.

## Forward-carry

none

## Friction

none
