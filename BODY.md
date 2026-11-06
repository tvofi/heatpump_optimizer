Round-10 roster record: the roster ops and the triage rulings they cite, at the tip `174417fa378846e2e876156984c3f39333ebd3ba` of `handoff/audit-r10-roster`. Part of #201. It closes nothing by keyword and leaves #201 open.

The change is roster state plus the triage rulings the roster's carries cite: 8 files. `dev/programme/rosters/wave-r10-groups.json` moves 2518 lines in and 983 out against the merge base `c3a279e3252a8b57bb00b5a677318cd4fe20387f`; `dev/programme/triage/s6-batch119.md` to `s6-batch125.md` add 163, 151, 124, 96, 42, 13 and 35 lines. The branch has 1229 non-merge commits over that base (plus 2 merges of main): 537 `append-carry`, 164 `drop-carry`, 130 `set-stage`, 92 `append-group`, 57 `wire-issue`, 54 `set-resume`, 42 `set-after`, 20 `edit-brief`, 17 `mark-carry`, 5 `set-files` ops, 99 `roster_sync` derivations, and 12 `roster:` and `record:` commits.

Groups go from 302 on `origin/main` to 336: 34 are added and none removed, and 98 existing groups change. 55 groups change stage: 32 reach `done`, 13 reach `carries-open` and 10 `absorbed`. No production or test code is touched.

## Head

`174417fa378846e2e876156984c3f39333ebd3ba`, the tip of `handoff/audit-r10-roster`: `70d926c65bf856456efe56a27c1bdf99d0aa1c7d` plus one commit, `record: host paths scrubbed`, the mechanical `ref_privacy.py scrub --write` of three host-path spans in the roster. Every figure below was measured on a detached worktree at that commit against `origin/main` at `b88684a218923f85de66f1e8fb1833e31a76a154`. Read the diff three-dot: a two-dot diff shows main's own newer commits.

## Mutation proof

n/a: roster state and markdown rulings only; no production or test code.

## Null control

`origin/main` carries 302 groups and the roster instruments pass on it; its roster blob is `8a4dcc3fd3861d4ad32c0c658090d318c64d2db9`. At this head the blob is `4a69e90f60e371277d21cccee07ad5f27b9929c2`. A script keying both trees' groups prints `302 336 34 0 98` (counts, added, removed, changed). The control that proves the lint reads: before this head, `node tools/policy/brief_lint.mjs` on `origin/main`'s roster exits 0, and at this head exits 0 as well with `TOTAL: 0 error(s) across 1 file(s)`.

## Figures

- `git merge-base origin/main 174417fa3` -- `c3a279e3252a8b57bb00b5a677318cd4fe20387f`; `git rev-list --count c3a279e32..174417fa3` -- 1231, of which `--no-merges` 1229.
- `git diff --numstat origin/main...174417fa3` -- the roster `2518 983`; triage `163 0`, `151 0`, `124 0`, `96 0`, `42 0`, `13 0`, `35 0`; 8 files, 3142 insertions, 983 deletions.
- `git merge-tree --write-tree origin/main 174417fa3` -- tree `ee8841628ea50a734c506d05656503cdaacf331a`, no conflict.
- The group counts above come from `python3` keying `json.loads(git show <ref>:dev/programme/rosters/wave-r10-groups.json)["groups"]` by `group`; stage changes 55 (32 done, 13 carries-open, 10 absorbed) from the same keying on `resume.stage`.
- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` -- `TOTAL: 0 error(s) across 1 file(s)` at `174417fa3`.
- `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED` at `174417fa3`.
- Overlap: `s6-batch124.md` and `s6-batch125.md` here are byte-identical to the blobs on `handoff/triage-s12-batch124` and `handoff/triage-s12-batch125` (`2decff42c`, `38e165713`). `s6-batch122.md` here is `90a9d0c45`, while `handoff/triage-s12-batch122` (#3212) carries `762260c83`; whichever merges second needs the other's version.

## Red checks

none yet: no check has run on this pull request when the body was written.

## Forward-carry

none

## Friction

none
