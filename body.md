Round-10 roster, batch 24, at the head the push lane produces: this pull request's own roster and record commits, the `origin/handoff/audit-r10-roster` tip the lane merges in as its code sha, and current `origin/main`. Part of #201; it closes nothing by keyword and leaves #201 open.

The change is roster state only. This pull request's own commits are 26 authored roster ops (`3b78b44a0`..`a9c7555ad`) and one record commit, `b0920b94a`, which adds only `dev/programme/delivery/2878.md`. The roster tip adds 44 more no-merge commits, and the merged head lands 71 no-merge commits over `origin/main`.

## Head

`1dbf3f6741e8507556dd5d6e0b6829ae5dc925dd` merges the authored code head `cfacd3800bb5fa7deb043e6afd7533fa73f3a5d8` and then merges origin/main `e40806a7d` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

Previous head: `0e370d603264f4c050fefa9591ac8bf688c1e0d5` merged the authored code head `f318f7014f9d376ab6926bebe9b155f5a286c58e` and then merged origin/main `4db1d3e28` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

Measured inputs, not a result sha: this body is written at `b0920b94a`; `update_pr.sh` merges `origin/handoff/audit-r10-roster` (measured at `cfacd3800`) into it and then `origin/main` (measured at `4db1d3e28`).

This pull request's own roster commits change nine groups against the merge base `524c1896b`: `R10-ARCH-SHAPES`, `R10-FLOW-AUDIT-PLAN` and `R10-PLAN-PRIO` reach `done`, `R10-DIAG-AGES` and `R10-HOUSE-GRADE` take their handoff commit and pull-request fields, and four groups gain carries (`R10-FLOW-WIP` for P199, `R10-FLOW-TOOLKIT-MODEL`, `R10-FLOW-DESIGN-STAGES`, `R10-ARCH-SHAPES-CLASSIFIER`). The record commit adds the row above and nothing else.

Against `origin/main`, the roster tip has four more groups (`R10-ROSTER-BATCH24`, `R10-TRIAGE-B36`, `R10-TRIAGE-B37`, `R10-REVIEW-CARRY`) and 30 changed groups. Net over `origin/main`, the merged head has 212 groups against main's 208, and 22 groups change: ten gain carries and ten move `resume.stage` (`R10-ARCH-SHAPES`, `R10-FLOW-AUDIT-PLAN`, `R10-SAV-COMFORT` and `R10-PLAN-PRIO` to `done`; `R10-DIAG-AGES`, `R10-FLOW-BOARD` and `R10-TRAIN-OVERLAP-GRADE` to `in-progress`; `R10-BUFFER-STORE` and `R10-ORCH-ROSTER-SCHEMA` to `in-review`; `R10-RCA-BODY-LINT` to `fixing`), with branch, commit and pull-request fields moving in the others. No `size` key moves at the merged head: the branch's `XS` words are already the merge base's, and `origin/main`'s `9973089cb` (the stage/size registry) carries those groups at `S`, which the merge keeps.

`R10-REVIEW-CARRY` is the one policy-carrying newcomer and it is registered at `resume.stage: fixing`. On 2026-10-27 the owner ruled, verbatim: **"if there are no code changes, the previous review can be carried"**. The group exists to make that test mechanical rather than a seat's judgement — a helper that answers `CARRY` or `FRESH-REVIEW` from a commit range, a `bus.sh dispatch` refusal over a clean range, and two contract sentences in `fix-review.md` and `orchestrator.md`. Its fixer works in its own handoff; this pull request registers the group and nothing else.

A `git merge-tree --write-tree` simulation of both merges is conflict-free. At its tree the roster blob is `adff8318`, `roster_sync --self-test` prints `64 checks, 0 failed`, and `brief_lint` prints `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster data only; no production or test code changes.

## Null control

Unmodified, `origin/main` carries 208 groups, no `size: XS`, and the same two instruments pass there. The merged head's diff over `origin/main` is exactly two files, `dev/programme/delivery/2878.md` and `dev/programme/rosters/wave-r10-groups.json`; nothing else moves. Roster blobs: main `582f75be3`, this head `cc64745e`, the roster tip `4b136c3e`, the merged tree `adff8318`.

## Figures

- `git rev-list --count --no-merges origin/main..b0920b94a` -- 27 at `b0920b94a` (26 authored roster commits plus the record commit).
- `git rev-list --count --no-merges origin/main..origin/handoff/audit-r10-roster` -- 70 at the roster tip `cfacd3800`.
- `{ git rev-list --no-merges origin/main..b0920b94a; git rev-list --no-merges origin/main..origin/handoff/audit-r10-roster; } | sort -u | wc -l` -- 71, the merged head's no-merge commits over `origin/main` (27 + 70 - 26 common).
- `git diff --numstat origin/main...b0920b94a` -- `1 0 dev/programme/delivery/2878.md` and `29 20 dev/programme/rosters/wave-r10-groups.json`.
- `git diff --numstat origin/main...origin/handoff/audit-r10-roster` -- `251 45 dev/programme/rosters/wave-r10-groups.json`.
- `git merge-tree --write-tree b0920b94a origin/handoff/audit-r10-roster` -- a tree with no conflict; committing it with both parents and merging `origin/main` the same way is also clean, and that merged tree's roster blob is `adff8318`.
- `python3 -c 'import json,subprocess as s,sys;g=lambda r:{x["group"]:x for x in json.loads(s.check_output(["git","show",r+":dev/programme/rosters/wave-r10-groups.json"]))["groups"]};a,b=g(sys.argv[1]),g(sys.argv[2]);print(len(a),len(b),len(set(b)-set(a)),sum(a[k]!=b.get(k) for k in a))' origin/main HEAD` -- at the pushed head `208 212 4 22`; at `origin/handoff/audit-r10-roster` it reads `208 212 4 30`.
- `git show origin/main:dev/programme/rosters/wave-r10-groups.json | grep -c '"size": "XS"'` -- 0; the same on `origin/handoff/audit-r10-roster` -- 8; on `524c1896b` -- 8.
- `git log --oneline -1 9973089cb` -- the stage/size registry commit on `origin/main`.
- `git show origin/main:dev/programme/rosters/wave-r10-groups.json | git hash-object --stdin` -- `582f75be3`; `b0920b94a` -- `cc64745e`; `cfacd3800` -- `e5cf37ba8`. The merged tree's hash is named in the `## Head` note the push writes, because it does not exist until the merge does.
- `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` -- `TOTAL: 0 error(s) across 1 file(s)` at main and at the merged tree.
- `env -u BASH_ENV python3 -I tools/audit/seat/roster_sync.py --self-test` -- `64 checks, 0 failed` at main and at the merged tree.
- `git show origin/main:dev/programme/rosters/wave-r10-groups.json | grep -c 'Triage P199\|Triage P200\|Triage P203'` -- 3, and 3 on `origin/handoff/audit-r10-roster`.
- `gh api repos/tvofi/heatpump_optimizer/commits/b0920b94abd9bfcb62611c05e04afda797a39518/check-runs --paginate -q '[.check_runs[] | .conclusion] | group_by(.) | map({(.[0]//"null"): length}) | add'` -- `{"skipped":19,"success":36}`.

## Red checks

At `b0920b94a`, the check-run rollup is 36 success and 19 skipped, none failing, by the `gh api` command in Figures. The merged head has no rollup yet; the two roster instruments run at its simulated tree and both pass, as listed above.

## Forward-carry

none

## Friction

- delivery-row-group: contradiction: `dev/programme/delivery/2878.md` records this pull request as (R10-ORCH-ROSTER), which no group in the merged roster holds; `roster_lib.group_for_branch` maps `fix/audit-r10-roster-pr` to `R10-ROSTER-BATCH24`, so a later row rewrite that keeps the group suffix keeps the dead name. Carry: R10-ROSTER-BATCH24
