Round-10 roster, the batch after #2878, at the roster tip `de410e4c923bdacfd4a06140a7453225f866e652` on `handoff/audit-r10-roster`. Part of #201. It closes nothing by keyword and leaves #201 open.

The change is roster state only: one file, `dev/programme/rosters/wave-r10-groups.json`, which moves 45 lines in and 27 out against `e8cb7e68302b1d350bb8219fea99e911170af030`, the current `origin/main` and the branch's merge base. The branch has nine commits over main, eight of them authored and one a merge of main: five `roster_edit.py` ops (three `wire-issue` ops on `R10-RCA-FRICTION-RESIDUE`, and two `set-stage` ops, on `R10-ORCH-REVIEW-PACKET` and `R10-PREPR-CAP`), two hand-written `roster:` commits that list `R10-RCA-FRICTION-RESIDUE`'s five closes (#2410, #2593, #2597, #2660, #2784) so the body of its own pull request can carry them, and one `roster_sync.py` derivation commit that moves stages from pull requests. The merge commit `826c0f6ea` re-pins `R10-IMMERSION-LATCH`'s `const.py` citation from 1149 to 1156 so `brief_lint` passes on the branch; main already carries 1156, so that re-pin nets to nothing in the diff.

Seventeen groups change, none added or removed (212 on both sides): `R10-HEAT-METER`, `R10-UPDATE-PR-SIGNALS`, `R10-RCA-BODY-LINT`, `R10-ORCH-ROSTER-SCHEMA`, `R10-ORCH-REVIEW-PACKET`, `R10-TRIAGE-B36`, `R10-ROSTER-BATCH24` and `R10-TRIAGE-B37` reach `done` with their merge commit; `R10-RCA-FRICTION-RESIDUE` (which also takes its fixes list, PR 2896) and `R10-IMMERSION-LATCH` (PR 2894) move from `queued` to `in-progress` by the reconciler; and `R10-COP-GATE`, `R10-UX-HEALTH`, `R10-FLOW-DESIGN-STAGES`, `R10-FLOW-JIDOKA`, `R10-FLOW-WIP`, `R10-FLOW-TOOLKIT-MODEL` and `R10-REPLAY-REAL-DAY` gain or rewrite a carry.

## Head

The head is `de410e4c923bdacfd4a06140a7453225f866e652`, the tip of `handoff/audit-r10-roster`, and every figure below was measured on a detached worktree at that commit. Its merge base with `origin/main` is `e8cb7e68302b1d350bb8219fea99e911170af030`, `origin/main` itself, so the three-dot diff carries only this branch's commits. `git merge-tree --write-tree e8cb7e683 de410e4c9` prints the tree `238a36786c62d4b619beba4a5d08ef282d3c5ccf` and no conflict.

`git diff --numstat e8cb7e683...de410e4c9` prints one row:

```
45      27      dev/programme/rosters/wave-r10-groups.json
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

Unmodified, `origin/main` carries 212 groups and the same two roster instruments pass on it. The roster blob there is `41b4b6b308a2a104b32444e52f26518957ec863c`, and at this head it is `05cf61a97833f3c1ea875bb2ea34d0f393407227`. A script that keys both trees' groups by `group` prints `212 212 0 0` (group counts, groups added, groups removed) and finds 17 groups whose body differs; the diff touches no other file.

At this head `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` exits 0 and prints `TOTAL: 0 error(s) across 1 file(s)`, and `R10-RCA-FRICTION-RESIDUE`'s `fixes` field reads `[2410, 2593, 2597, 2660, 2784]`.

## Figures

- `git rev-parse e8cb7e683:dev/programme/rosters/wave-r10-groups.json` -- `41b4b6b308a2a104b32444e52f26518957ec863c`; `git rev-parse de410e4c9:dev/programme/rosters/wave-r10-groups.json` -- `05cf61a97833f3c1ea875bb2ea34d0f393407227`.
- `git rev-list --count e8cb7e683..de410e4c9` -- 9; `git rev-list --count --no-merges e8cb7e683..de410e4c9` -- 8.
- `git diff --numstat e8cb7e683...de410e4c9` -- `45 27 dev/programme/rosters/wave-r10-groups.json`, the only row.
- `git merge-tree --write-tree e8cb7e683 de410e4c9` -- tree `238a36786c62d4b619beba4a5d08ef282d3c5ccf`, no conflict.
- `python3 -c 'import json,subprocess as s,sys;f="dev/programme/rosters/wave-r10-groups.json";g=lambda r:{x["group"]:x for x in json.loads(s.check_output(["git","show",r+":"+f]))["groups"]};a,b=g(sys.argv[1]),g(sys.argv[2]);print(len(a),len(b),len(set(b)-set(a)),len(set(a)-set(b)),sum(a[k]!=b[k] for k in a))' e8cb7e683 de410e4c9` -- `212 212 0 0 17`.
- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` -- `TOTAL: 0 error(s) across 1 file(s)` at `de410e4c9`.
- `python3 -c 'import json;print([g["fixes"] for g in json.load(open("dev/programme/rosters/wave-r10-groups.json"))["groups"] if g["group"]=="R10-RCA-FRICTION-RESIDUE"])'` -- `[[2410, 2593, 2597, 2660, 2784]]` at `de410e4c9`.
- `env -u BASH_ENV python3 -I tools/audit/seat/roster_sync.py --self-test` -- `roster_sync self-test: 74 checks, 0 failed` at `de410e4c9`, run with the workflow's own command and `BASH_ENV` unset.

## Red checks

none

## Forward-carry

- Triage batch 35's carries for P200 and P203 sit on groups that are now `done` (`R10-ORCH-REVIEW-PACKET`, `R10-ORCH-ROSTER-SCHEMA`), so no fixer will read them: P200's four unstated verdict relay checks in `fix-review.md` (the probe ref shape, the subject, the first line's two accepted forms, the `ev/` directory), which must pay the file's line cap by deletion, belong to the live group that lists `fix-review.md` Carry: R10-REVIEW-CARRY
- P203's `roster_lib.gate_kind`, which separates a gate covered by the mandate in force from one awaiting the owner, belongs to the live group that lists `roster_lib.py` and `roster_edit.py` and owns the stage vocabulary's remaining arms Carry: R10-FLOW-TOOLKIT-MODEL
- P199's dead-train detection in `orchestrator_tick.py`'s `train()` already sits as a carry on its live owner, `R10-FLOW-WIP`, which is `not-started`; this line records that its triage record (`dev/programme/triage/s6-batch35.md#P199`) is on main now, so the carry no longer waits on a merge Carry: R10-FLOW-WIP

## Friction

none
