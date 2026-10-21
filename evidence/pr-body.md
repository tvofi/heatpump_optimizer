Roster for round 10, fifth landing: brings main's `dev/programme/rosters/wave-r10-groups.json` (plus `critical-path.json` and `carry-201.json`) up to the roster branch tip, so that open pull requests' carries resolve against the tree's roster (finding-propagation.md). Part of #201.

Carry delta since the last reviewed head (802b3850): the roster tip moved from `31e162fd` to `2c76c3128` by two roster_edit commits: `617ce1316` (append-carry R10-BRIEFS-FOLD, the tests/README.md harness-path carry from #2521) and `2c76c3128` (set-stage R10-MERGE-PR-MANDATE to done). The figures below are re-taken whole at `2c76c3128`.

## Head

`802b38503eb5de20e87c278ba7923508a50c0f1f` merges origin/main `5d433771a` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`802b38503eb5de20e87c278ba7923508a50c0f1f` merges origin/main `5d433771a` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

The authored code head is `2c76c3128bf6d4e0cf37488eb8d29af830df54a0` (`handoff/audit-r10-roster`). This PR's head `802b38503eb5de20e87c278ba7923508a50c0f1f` merges origin/main `5d433771a` into `892169c30`, which merges the code head into the previous PR head (automatic merges by the orchestrator's script; no conflict resolution inside the code head). `git diff --name-only origin/main...origin/fix/audit-r10-roster` lists four files: `dev/programme/rosters/wave-r10-groups.json`, `dev/programme/rosters/critical-path.json` (new), `dev/programme/carries/carry-201.json` and this PR's own delivery row `dev/programme/delivery/2559.md`; the code head alone adds the first three.

## The diff

Enumerated with jq from `wave-r10-groups.json` at `origin/main` (5d433771a) and at `2c76c3128`: groups 91 to 108; groups with `resume.stage` `done` 43 to 52; carries summed over all groups 201 to 257 (+56).

- New groups (17, none removed): R10-HANDOFF-ARCHIVE and R10-DEPENDABOT-AIOHTTP (done); R10-ORCH-MACHINERY, R10-CARD-VOICE, R10-THERMAL-POWER-OPTION, R10-LEARNER-DEFAULT, R10-MUTANT-SKIP, R10-CI-LAYOUT-P1, R10-CI-LAYOUT-P2 (not-started); R10-TICK-OWED-LEVEL, R10-REPLAY-CAP, R10-RCA-HANDOFF-SLIP, R10-HANDOVER-REFRESH, R10-RCA-ORCH-CONTINUITY, R10-TICK-RELAY-DECOUPLE, R10-PLAN-ARTIFACT, R10-ROSTER-PUSH-RACE (in-progress).
- Stage changes on existing groups (19): to done (9): R10-SAV-REASONS, R10-TRAIN-HOLD, R10-DEEPLINK-HANDLERS, R10-STAMP, R10-RCA-NIGHTLY-PYSPY, R10-FOLLOWER-DEBOUNCE, R10-SETPOINT-BOOST, R10-UPDATE-PR-LOCK, R10-MERGE-PR-MANDATE (in-progress to done, the `2c76c3128` commit); to in-progress (8): R10-NIGHT-FOLDS, R10-FREQ-DEFROST, R10-ADVISOR, R10-I5-DOCS, R10-REPLAY-LANE, R10-RCA-FRICTION, R10-CI-LAYOUT, R10-UPDATE-PR-SIGNALS; and back from done to in-progress (2): R10-PREPR-CAP, R10-CI-RATCHET-RED. Check: 43 + 2 new done + 9 to done - 2 reopened = 52.
- Carries: +56 in all. 23 sit on the 17 new groups; 33 are appended to 14 existing groups: R10-CI-LAYOUT 14 to 27, R10-BRIEFS-FOLD 18 to 21, R10-POLICY-LINT-FAMILY 3 to 5, R10-REPLAY-LANE 3 to 5, R10-ROSTER-OPS 3 to 6, R10-REGISTRY-LEAK 1 to 3, and one each on R10-ADVISOR, R10-ARCH-SHAPES, R10-FAHRENHEIT, R10-HEAT-METER, R10-I5-DOCS, R10-RCA-FRICTION, R10-STAMP, R10-TICK-ORCH (13+3+2+2+3+2+8 = 33). No carry text is rewritten in place at an unchanged count.
- The three R10-BRIEFS-FOLD carries added over main include the one this head adds (from #2521: tests/README.md cites `tools/audit/harnesses/k1725_blas_kernel_gap.py`, which does not exist; the correct path is `dev/audit/harnesses/k1725_blas_kernel_gap.py`).
- Text edits (brief, issues, fixes, findings) on 16 existing groups; R10-CI-LAYOUT's `findings` now says four pull requests with PR 1 and PR 2 split into the -P1 and -P2 groups.
- Resume-note edits at an unchanged stage on 12 groups, among them R10-OPENPR-SILENT and R10-REGISTRY-LEAK.
- `carry-201.json`: one carry added (the nightly-ha py-spy positive control, from #2479) and the `stage` text extended to name it.

This PR leaves #201 open and closes nothing by keyword.

## Mutation proof

n/a: roster state only; no production or test code.

## Null control

n/a: no measured claim. The lists above enumerate a JSON diff between `origin/main` and the head.

## Figures

none

## Red checks

- `nightly-status`: red at every head including main's own tip, because it grades main (the nightly run), not this branch; this diff changes only `dev/programme/rosters/*.json`, `dev/programme/carries/carry-201.json` and `dev/programme/delivery/2559.md`, none of which `nightly-status` reads, so it is not this PR's.

## Forward-carry

none

## Friction

none

