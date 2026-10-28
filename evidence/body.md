Round-10 roster, the batch after #2878, at the roster tip `08c0818cdb058d15c0c59e0b339c3111af9bbbb2` on `handoff/audit-r10-roster`. Part of #201. It closes nothing by keyword and leaves #201 open.

The change is roster state only: one file, `dev/programme/rosters/wave-r10-groups.json`, which moves 48 lines in and 28 out against `origin/main` (`6e5995e51bec7c9f6d3f4dc37ed5297fefe1c3d6`; the roster blob there is the one at `e8cb7e683`, which no merge since has touched). The authored roster commits are seven `roster_edit.py` ops (two of them `append-carry` ops, added after the first review blocked the head for a missing carry), two hand-written `roster:` commits, one `roster_sync.py` derivation commit and one merge of main. The ops: five (three `wire-issue` ops on `R10-RCA-FRICTION-RESIDUE`, and two `set-stage` ops, on `R10-ORCH-REVIEW-PACKET` and `R10-PREPR-CAP`), plus the two `append-carry` ops named under Forward-carry; the two hand-written `roster:` commits that list `R10-RCA-FRICTION-RESIDUE`'s five closes (#2410, #2593, #2597, #2660, #2784) so the body of its own pull request can carry them, and one `roster_sync.py` derivation commit that moves stages from pull requests. The merge commit `826c0f6ea` re-pins `R10-IMMERSION-LATCH`'s `const.py` citation from 1149 to 1156 so `brief_lint` passes on the branch; main already carries 1156, so that re-pin nets to nothing in the diff.

Eighteen groups change, none added or removed (212 on both sides): `R10-HEAT-METER`, `R10-UPDATE-PR-SIGNALS`, `R10-RCA-BODY-LINT`, `R10-ORCH-ROSTER-SCHEMA`, `R10-ORCH-REVIEW-PACKET`, `R10-TRIAGE-B36`, `R10-ROSTER-BATCH24` and `R10-TRIAGE-B37` reach `done` with their merge commit; `R10-RCA-FRICTION-RESIDUE` (which also takes its fixes list, PR 2896) and `R10-IMMERSION-LATCH` (PR 2894) move from `queued` to `in-progress` by the reconciler; and `R10-COP-GATE`, `R10-UX-HEALTH`, `R10-FLOW-DESIGN-STAGES`, `R10-FLOW-JIDOKA`, `R10-FLOW-WIP`, `R10-FLOW-TOOLKIT-MODEL` and `R10-REPLAY-REAL-DAY` gain or rewrite a carry, and `R10-REVIEW-CARRY` gains one.

## Head

`45ce3c6e9aa00bab7c57bb1d7ab3bd72f951c52d` merges the authored code head `08c0818cdb058d15c0c59e0b339c3111af9bbbb2` and then merges origin/main `b9e286254` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

The authored code head is `08c0818cdb058d15c0c59e0b339c3111af9bbbb2`, the tip of `handoff/audit-r10-roster`. It is `de410e4c923bdacfd4a06140a7453225f866e652` (the roster tip the first review read) plus two commits, `ba3cf1b26` (`append-carry R10-REVIEW-CARRY`, P200) and `08c0818cd` (`append-carry R10-FLOW-TOOLKIT-MODEL`, P203). Each is the only change in its commit: `git diff --stat de410e4c9 08c0818cd` is `dev/programme/rosters/wave-r10-groups.json | 6 ++++--`.

The pull request head `45ce3c6e9aa00bab7c57bb1d7ab3bd72f951c52d` is that code head merged with `origin/main` (first `6e5995e51bec7c9f6d3f4dc37ed5297fefe1c3d6`, then `b9e286254e152b6647b37b5612bd340dd39daca0`) and this pull request's own row `dev/programme/delivery/2899.md`; neither merge changes the roster file, which `origin/main` has not changed since `e8cb7e683`: at the head it is blob `b00ab3ef00e7e9f4f9b205e523772429f6e6f222`, the code head's, and `git diff --numstat origin/main...45ce3c6e9` prints that file as `48 28` beside the row file `1 0 dev/programme/delivery/2899.md`. Every figure below was measured on the tree of that merge, `git merge-tree --write-tree origin/main 08c0818cd` = `f7b99c7b79a5213221aa002a39ac4980104dec77`, committed as a detached worktree with both parents, and not on `de410e4c9`; the lint and the `fixes` figure were re-run there. The merge has no conflict.

`git diff --numstat origin/main...<that merge>` prints one row:

```
48      28      dev/programme/rosters/wave-r10-groups.json
```

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

Unmodified, `origin/main` carries 212 groups and the same two roster instruments pass on it. The roster blob there is `41b4b6b308a2a104b32444e52f26518957ec863c`, and at the code head it is `b00ab3ef00e7e9f4f9b205e523772429f6e6f222`. A script that keys both trees' groups by `group` prints `212 212 0 0` (group counts, groups added, groups removed) and finds 18 groups whose body differs; the diff touches no other file.

At this head `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` exits 0 and prints `TOTAL: 0 error(s) across 1 file(s)`, and `R10-RCA-FRICTION-RESIDUE`'s `fixes` field reads `[2410, 2593, 2597, 2660, 2784]`.

## Figures

- `git rev-parse 6e5995e51:dev/programme/rosters/wave-r10-groups.json` -- `41b4b6b308a2a104b32444e52f26518957ec863c`; `git rev-parse 08c0818cd:dev/programme/rosters/wave-r10-groups.json` -- `b00ab3ef00e7e9f4f9b205e523772429f6e6f222`.
- `git diff --numstat 6e5995e51...08c0818cd` -- `48 28 dev/programme/rosters/wave-r10-groups.json`, the only row (the merge base is `e8cb7e683`).
- `git merge-tree --write-tree 6e5995e51 08c0818cd` -- tree `f7b99c7b79a5213221aa002a39ac4980104dec77`, no conflict.
- `python3 -c 'import json,subprocess as s,sys;f="dev/programme/rosters/wave-r10-groups.json";g=lambda r:{x["group"]:x for x in json.loads(s.check_output(["git","show",r+":"+f]))["groups"]};a,b=g(sys.argv[1]),g(sys.argv[2]);print(len(a),len(b),len(set(b)-set(a)),len(set(a)-set(b)),sum(a[k]!=b[k] for k in a))' 6e5995e51 08c0818cd` -- `212 212 0 0 18`.
- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` -- `TOTAL: 0 error(s) across 1 file(s)`, rc 0, on the merge tree above.
- `python3 -c 'import json;print([g["fixes"] for g in json.load(open("dev/programme/rosters/wave-r10-groups.json"))["groups"] if g["group"]=="R10-RCA-FRICTION-RESIDUE"])'` -- `[[2410, 2593, 2597, 2660, 2784]]` on the merge tree.
- `env -u BASH_ENV python3 -I tools/audit/seat/roster_sync.py --self-test` -- `roster_sync self-test: 74 checks, 0 failed` on the merge tree, run with the workflow's own command and `BASH_ENV` unset.
- `R10-REVIEW-CARRY` carries 4 entries (3 on `origin/main`) and `R10-FLOW-TOOLKIT-MODEL` 13 (12 on `de410e4c9`); the new entry on each is the P200 and P203 text, read back from the pushed commit as one exact entry of 1986 and 2366 characters.

## Red checks

none

## Forward-carry

- P200 (`dev/programme/triage/s6-batch35.md#P200`): the four unstated verdict relay checks in `fix-review.md` (the probe ref shape, the subject, the first line's two accepted forms, the `ev/` directory), which must pay the file's line cap by deletion, are now an entry on the live group that lists `fix-review.md`, `R10-REVIEW-CARRY` (`ba3cf1b26`), copied whole from `R10-ORCH-REVIEW-PACKET`'s entry with its controls and its binding intact. Carry: R10-REVIEW-CARRY
- P203 (`dev/programme/triage/s6-batch35.md#P203`): `roster_lib.gate_kind`, which separates a gate covered by the mandate in force from one awaiting the owner, is now an entry on `R10-FLOW-TOOLKIT-MODEL` (`08c0818cd`), which lists `roster_lib.py` and `roster_edit.py` and owns the stage vocabulary's remaining arms, copied whole from `R10-ORCH-ROSTER-SCHEMA`'s entry with its controls intact. Carry: R10-FLOW-TOOLKIT-MODEL
- P199's dead-train detection in `orchestrator_tick.py`'s `train()` already sits as a carry on its live owner, `R10-FLOW-WIP`, which is `not-started`; this line records that its triage record (`dev/programme/triage/s6-batch35.md#P199`) is on main now, so the carry no longer waits on a merge Carry: R10-FLOW-WIP

## Friction

none



