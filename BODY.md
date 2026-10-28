Round-10 roster, the batch after #2899, at the roster tip `69b1ac245586953cf8e94408a6d3f00cdce79c5f` on `handoff/audit-r10-roster`. Part of #201. It closes nothing by keyword and leaves #201 open.

The change is roster state only: one file, `dev/programme/rosters/wave-r10-groups.json`, which moves 196 lines in and 38 out against `08c0818cdb058d15c0c59e0b339c3111af9bbbb2`, the merge base with `origin/main` (`eab04d0ebf8c45667099b668ab0d8bf976d5f99a`). The branch has 40 commits over that base, none a merge: 30 `roster_edit.py` ops (15 `append-carry`, 11 `set-stage`, 3 `append-group`, 1 `wire-issue`) and 10 `roster_sync.py` derivations that move stages from pull requests.

Three groups are added, 212 to 215, none removed: `R10-TRIAGE-S6`, `R10-FRICTION-FIXER-MD` and `R10-FRICTION-CLAIM-FALSE`. Twenty-five existing groups change. Seven reach `done` (`R10-RCA-HEADMOVED`, `R10-FLOW-BOARD`, `R10-FLOW-JIDOKA`, `R10-FLOW-ROSTER-FREEZE`, `R10-IMMERSION-LATCH`, `R10-HOUSE-GRADE`, `R10-DEPENDABOT-SETUPTOOLS`); `R10-ORCH-BEATD` moves to `in-progress`; `R10-ORCH-ROSTER-SCHEMA` is reopened from `done` to `carries-open` and takes its carries; the other sixteen change a carry, an issue wire or another field with no stage change.

`R10-RCA-FRICTION-RESIDUE`'s `fixes` (`[2410, 2593, 2597, 2660, 2784]`) are already on `origin/main` and this diff does not touch them, so a `Closes` on #2896 does not wait on this pull request.

## Head

The head is `69b1ac245586953cf8e94408a6d3f00cdce79c5f`, the tip of `handoff/audit-r10-roster`. Every figure below was measured on a detached worktree at that commit against `origin/main` at `eab04d0ebf8c45667099b668ab0d8bf976d5f99a`. The three-dot diff carries only this branch's commits. `git merge-tree --write-tree eab04d0eb 69b1ac245` prints the tree `60d8fe780f38788b6a14dbfc6349ee8098006f79` and no conflict.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

Unmodified, `origin/main` carries 212 groups and the roster instruments pass on it. The roster blob there is `b00ab3ef00e7e9f4f9b205e523772429f6e6f222`, and at this head it is `508e010f27debb68bc4633bd382e1b920bfa5060`. A script that keys both trees' groups by `group` prints `212 215 3 0 25` (counts, added, removed, groups whose body differs); the diff touches no other file.

At this head `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` exits 0 and prints `TOTAL: 0 error(s) across 1 file(s)`, and `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.

## Figures

- `git rev-parse eab04d0eb:dev/programme/rosters/wave-r10-groups.json` -- `b00ab3ef00e7e9f4f9b205e523772429f6e6f222`; `git rev-parse 69b1ac245:dev/programme/rosters/wave-r10-groups.json` -- `508e010f27debb68bc4633bd382e1b920bfa5060`.
- `git rev-list --count 08c0818cd..69b1ac245` -- 40; `git rev-list --count --no-merges 08c0818cd..69b1ac245` -- 40.
- `git diff --numstat eab04d0eb...69b1ac245` -- `196 38 dev/programme/rosters/wave-r10-groups.json`, the only row.
- `git merge-tree --write-tree eab04d0eb 69b1ac245` -- tree `60d8fe780f38788b6a14dbfc6349ee8098006f79`, no conflict.
- `python3 -c 'import json,subprocess as s,sys;f="dev/programme/rosters/wave-r10-groups.json";g=lambda r:{x["group"]:x for x in json.loads(s.check_output(["git","show",r+":"+f]))["groups"]};a,b=g(sys.argv[1]),g(sys.argv[2]);print(len(a),len(b),len(set(b)-set(a)),len(set(a)-set(b)),sum(a[k]!=b[k] for k in a if k in b))' eab04d0eb 69b1ac245` -- `212 215 3 0 25`.
- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` -- `TOTAL: 0 error(s) across 1 file(s)` at `69b1ac245`.
- `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED` at `69b1ac245`.

## Red checks

none

## Forward-carry

none

## Friction

none
