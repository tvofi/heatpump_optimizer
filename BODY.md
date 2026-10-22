Roster for round 10, thirteenth landing (after #2608). It applies the roster operations built while the trains drained: carries from triage rulings and merge verdicts, an owner direction for the docs groups, and stage changes for work that merged. Part of #201. It closes nothing by keyword and leaves #201 open.

## Head

The authored code head is `d7e1f9fc06d02945c95ce6c14fcd17435ba45b24`, the tip of `handoff/audit-r10-roster`. Its merge base with `origin/main` `752f697ccc9c8a4191fe8a999f3622c190b6ff82` is `59eb73ac5360c19761ab9cb80508cb763cd44b18`, the roster as #2608 landed it. The diff against that base is one file, `dev/programme/rosters/wave-r10-groups.json`, 39 insertions and 23 deletions over 23 commits (`git rev-list --count 59eb73ac5..d7e1f9fc0` prints 23), each pushed by `roster_edit.py --push` after its lint gate printed `TOTAL: 0 error(s)`.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

`git diff --exit-code 752f697ccc9c8a4191fe8a999f3622c190b6ff82 59eb73ac5360c19761ab9cb80508cb763cd44b18 -- dev/programme/rosters/wave-r10-groups.json` has rc 0: the roster on main equals the merge base, so nothing main wrote is overwritten. The `removed` list below is empty.

## Figures

The 23 ops, by commit, with their sources.

Carries from the orchestrator's proposal triage (`triage.md`, ACCEPT paragraphs P1 to P4):

- `a2e29e39b` `R10-FLY-ORPHANS-REWRITTEN` (P1: orphan predicate for a tip that adds only main merges).
- `85d38f7cc` `R10-FLOW-BODY-PATCH` (P2: body-only re-body while a train holds the branch worktree).
- `f814e92a5` `R10-FLOW-JIDOKA` (P3: prepr replays the base-pinned graders).
- `d352f6ad6` `R10-TRAIN-OVERLAP-GRADE` (P4: diagnose the truncated "policy prohibits" refusal, then widen `--approval-carry`).

Carries from verdicts and owner directions:

- `c6b68c00e` `R10-RECORD-API-BUDGET`: #2608 verdict finding 1 (read the record at `e96f64a5a` or later, not `0a8c4523a`).
- `e70ce9797` and `a97c74e22` `R10-FLOW-ARCH-PLANNER`: owner fold-in of the proposal-triage seat (tvofi 2026-10-22), and its hot-file accounting.
- `0d1295b39` and `229151c28` `R10-ARCH-DOCS`: #2609's merge verdict (review/2609 `0d370ca08`): the `corpus_excluded.json` entry for `dev/README.md`, and the `coffee.svg` colour-scheme behaviour.
- `bbf9c8366` `R10-ARCH-DOCS`: owner direction (tvofi 2026-10-22) to verify and redraw the "Its components" mermaid figure.
- `9879251a6` `R10-ARCH-DOCS`: the study step, owner suggestion with triage P5 ACCEPT.
- `c98fb4c27` `R10-ORCH-MACHINERY`: #2579's round-6 verdict (review/2579 `f7a6bdf0c`), the two corrected yield-probe guardrail points.
- `2501a0a16` `R10-ORCH-MACHINERY`: #2609's post-merge delta review (review/2609 `db41f8581`), the env-matrix no-remote arm.
- `4209e135b` `R10-PREPR-UNPINNED-RED`: #2609's red at `ff83a3d7` (the stale D6 claims counts), cited by #2609's Red checks.

Stage changes (each at the merge commit on main unless noted):

- `fb0760bfa` `R10-ARCH-DOCS-FIRST` done at `9b4cfd8c2` (#2609).
- `0e6fec5bc` and `79044da4e` `R10-NIGHT-FOLDS` done at `d48018b80`, with the note citing tests `9d60bbf7d` and `df4266c06`; #2223 is closed.
- `acf0f844d` `R10-CI-LAYOUT-P2` and `86592b3d3` `R10-SOLVER` in-progress (dispatched as cloud fixers).
- `adfa501ba` `R10-FLOW-MAIN-GATE` done at `49018a8be` (#2584).
- `d6bbe56ca` `R10-RCA-INSTALL-RATELIMIT` done at `9af4664c1` (#2606).
- `c57ef192e` `R10-NIGHTLY-PYSPY-RETRY` done at `2c0c47494` (#2605).
- `d7e1f9fc0` `R10-FLY-GH-READ-RETRY` in-progress, not done: #2589 is PR 1, and the group's brief and carries still owe PR 2 (`merge_train.py` and `record_row.py` reads) and PR 3 (`pr-contract.yml`'s body read).

`R10-FLOW-RELAY-HOLD` is deliberately left not-started: #2580 is unmerged. No open pull request carries an item routed to a group this PR closes (`gh pr list` bodies, `Carry:` lines).

Measured with `B=origin/main`, `H=d7e1f9fc0`, `R=dev/programme/rosters/wave-r10-groups.json`: `jq -n --slurpfile b <(git show $B:$R) --slurpfile h <(git show $H:$R) '($b[0].groups|map({(.group):.})|add) as $B|($h[0].groups|map({(.group):.})|add) as $H|{nb:($B|length),nh:($H|length),removed:[$B|keys[]|select($H[.]==null)],new:[$H|keys[]|select($B[.]==null)],changed:[$H|keys[]|select($B[.]!=null and $B[.]!=$H[.])]}'` prints 151 and 151 groups, none removed, none new, and 17 changed. `node tools/policy/brief_lint.mjs` on the roster at `H` prints `TOTAL: 0 error(s) across 1 file(s)`.

## Red checks

Read 2026-10-22 from `repos/tvofi/heatpump_optimizer/commits/752f697ccc9c8a4191fe8a999f3622c190b6ff82/check-runs` (main's tip), failures, cancellations and timeouts only: none. Checks at this PR's own head are read by CI; this diff changes only the roster and one delivery row.

## Forward-carry

none

## Friction

none
