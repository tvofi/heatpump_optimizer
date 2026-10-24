# Round-10 wave data (read-only measurement)

Generated 2026-10-18T18:26:58.065420Z. origin/main = `106af95a33f8`; roster blob on main `78b018644921`; #2417 head `c83ae12acc07`.
PR heads and comments are live at generation time (about 18:27Z); the newest tick pass (18:19:34Z) is older than several of them, so a few tick lines below are stale.

Commands (all inputs): `git -C /Users/timmalmstrom/hpo-seats/r10s3/orch-wt fetch origin`; `git show origin/main:dev/programme/rosters/wave-r10-groups.json` (roster, 63 groups); `git show origin/pr2417:dev/programme/rosters/wave-r10-groups.json` (pending roster, 64 groups; fetched with `git fetch origin pull/2417/head:refs/remotes/origin/pr2417`); `/Users/timmalmstrom/hpo-orch/r10s3/REPLAN-EDGES.json`; `gh pr list --repo tvofi/heatpump_optimizer --state open --json number,title,headRefName,createdAt,headRefOid` (16 open); `gh api --paginate repos/tvofi/heatpump_optimizer/pulls/N/files` (exact file lists, `gh pr list --json files` truncates at 100); `gh api --paginate repos/.../issues/N/comments`; `gh pr view N --json headRefOid,mergeStateStatus,reviewDecision,isDraft`; `gh pr list --state merged --limit 400`; `git rev-list --count origin/main..origin/<handoff ref>`.

## 1. Groups whose resume.stage is not `done`

Count: 38 in the main roster (36 not-started, 1 planned, 1 in-progress; `python3 -I` count of resume.stage over 63 groups: 25 done) plus R10-SAV-COMFORT, which exists only in #2417 = 39 rows. The tick pass says "38 open group(s) of 63", same as the main-roster count.

After-edges: `roster` = `after` in the main roster; `replan` = REPLAN-EDGES.json (blank = group absent from that file). Edges to done groups are shown too. Duration: see section 3.

| group | stage | kind | size | owner_gate | after (roster) | after (REPLAN) | open PR carrying it (match rule) | handoff ref ahead of main |
|---|---|---|---|---|---|---|---|---|
| R10-VENT-DETECTOR | not-started | defect | M | - | R10-RATIO-SITES | (none) | #2391 (title starts with group id; branch name = group slug) | 21 commits, 12 own |
| R10-NIGHT-FOLDS | not-started | defect | M | - | R10-VENT-DETECTOR | R10-VENT-DETECTOR | - | ref absent |
| R10-RATIO-ANCHOR | not-started | defect | M | - | R10-NIGHT-FOLDS | (none) | - | ref absent |
| R10-INPUT-STALENESS | not-started | defect | S | - | R10-RATIO-ANCHOR | (none) | - | ref absent |
| R10-CURRENCY | not-started | defect | S | - | R10-INPUT-STALENESS | (none) | - | ref absent |
| R10-TRUST-RELATIVE | not-started | study | M | - | R10-LEAF-IMPORTS | R10-NIGHT-FOLDS | - | ref absent |
| R10-FREQ-DEFROST | not-started | defect | S | - | R10-TRUST-RELATIVE | (none) | - | ref absent |
| R10-LOOP-CPU | not-started | defect | S | - | R10-FREQ-DEFROST | (none) | - | ref absent |
| R10-SAV-BASELINE | not-started | owner | L | - | R10-LOOP-CPU | (none) | #2411 (title starts with group id; branch name = group slug; branch = resume.branch tail) | 33 commits, 25 own |
| R10-SAV-REASONS | not-started | owner | M | - | R10-SAV-BASELINE, R10-LEAF-IMPORTS | R10-SAV-BASELINE, R10-LEAF-IMPORTS | - | ref absent |
| R10-ADVISOR | not-started | owner | M | - | R10-UX-SETUP, R10-SAV-REASONS | R10-SAV-BASELINE, R10-DEEPLINK-CENSUS | - | ref absent |
| R10-SCORES | not-started | owner | L | - | R10-ADVISOR, R10-RATIO-SITES | R10-ADVISOR, R10-SAV-BASELINE, R10-SENSOR-PAYLOAD | - | ref absent |
| R10-LIVESTATE | not-started | arch | XL | - | R10-SCORES, R10-PUMP-MODEL | R10-PUMP-MODEL, R10-VENT-DETECTOR, R10-NIGHT-FOLDS, R10-TRUST-RELATIVE, R10-RATIO-ANCHOR, R10-INPUT-STALENESS, R10-CURRENCY, R10-STORE, R10-FREQ-DEFRO... | - | ref absent |
| R10-CONFIG-NOTICES | not-started | arch | S | - | R10-LIVESTATE | (none) | - | ref absent |
| R10-ARCHSCORE-COVERAGE | in-progress: p1 #2293 + p2 #2311 merged;... | instrument | L | code-owned: archscore weights.json and calibration/expected.json |  | (not in file) | #2401 (title starts with group id; branch name = group slug), #2373 (title starts with group id; branch name = group slug) | 0 commits, 0 own |
| R10-PARAMS-OWNER | not-started | arch | XL | - | R10-CONFIG-NOTICES, R10-ARCHSCORE-COVERAGE, R10-SERVICES-GUARD | R10-ARCHSCORE-COVERAGE, R10-LIVESTATE, R10-CONFIG-NOTICES, R10-HEAT-METER | - | ref absent |
| R10-SENSOR-PAYLOAD | not-started | arch | L | - | R10-SCORES | (none) | #2379 (title starts with group id; branch name = group slug; branch = resume.branch tail) | 21 commits, 10 own |
| R10-ARCH-SHAPES | not-started | arch | L | - | R10-PARAMS-OWNER, R10-SENSOR-PAYLOAD, R10-FREQ-DEFROST | R10-PUMP-MODEL | - | ref absent |
| R10-LEARNER-ETA | not-started | study | M | - | R10-ARCH-SHAPES | R10-TRUST-RELATIVE, R10-SCORES | - | ref absent |
| R10-HEAT-METER | not-started | owner | XL | - | R10-LEARNER-ETA, R10-INPUT-STALENESS, R10-UX-SETUP, R10-RATIO-ANCHOR | R10-RATIO-ANCHOR, R10-INPUT-STALENESS, R10-LIVESTATE, R10-LEARNER-ETA, R10-TRUST-RELATIVE | - | ref absent |
| R10-COP-GATE | not-started | study | M | - | R10-HEAT-METER, R10-SENSOR-PAYLOAD | R10-HEAT-METER, R10-SENSOR-PAYLOAD | - | ref absent |
| R10-UX-HEALTH | not-started | owner | L | - | R10-SCORES, R10-COP-GATE, R10-HEAT-METER | R10-SCORES, R10-COP-GATE, R10-HEAT-METER, R10-LEARNER-ETA, R10-DEEPLINK-CENSUS | - | ref absent |
| R10-CONFIGFLOW-PAGES | not-started | arch | L | - | R10-HEAT-METER | R10-HEAT-METER | - | ref absent |
| R10-SOLVER | not-started | defect | M | - | R10-SAV-REASONS, R10-TARIFF | R10-SAV-REASONS | - | ref absent |
| R10-I5-DOCS | not-started | docs | S | code-owned: tests/stress.py (comment only) | R10-I1, R10-STRUCTURE-BLIND, R10-REGISTRY-LEAK | (none) | - | ref absent |
| R10-TICK-DRIVERS | not-started | instrument | M | code-owned: audit-find.js, audit-verify.js, fold_ledger.py | R10-REF-PRIVACY | R10-REF-PRIVACY | #2390 (title starts with group id; branch name = group slug; branch = resume.branch tail) | 3 commits, 2 own |
| R10-BRIEFS-FOLD | not-started | policy | M | policy: dimension briefs | R10-ARCHSCORE-COVERAGE, R10-D15-GRADER | R10-ARCHSCORE-COVERAGE, R10-D15-GRADER, R10-TICK-DRIVERS | - | ref absent |
| R10-DIAG-REPLAY | not-started | owner | L | - | R10-REPLAY-LOOPNORM, R10-LEAF-IMPORTS | R10-STORE | #2399 (title starts with group id; branch name = group slug) | 15 commits, 11 own |
| R10-REPLAY-LANE | not-started | owner | M | code-owned: .github/workflows/ | R10-DIAG-REPLAY | R10-DIAG-REPLAY | - | ref absent |
| R10-REPLAY-SCOPED | not-started | owner | S | code-owned: .github/workflows/ | R10-REPLAY-LANE, R10-TICK-ORCH, R10-TRAIN-HOLD, R10-REF-PRIVACY | R10-REPLAY-LANE, R10-TICK-ORCH, R10-TRAIN-HOLD, R10-REF-PRIVACY | - | ref absent |
| R10-TRAIN-HOLD | not-started | instrument | S | code-owned: .github/workflows/ (workflow change, approved under mandate 6175172275) | R10-TICK-TRAIN, R10-TICK-ORCH | (none) | - | ref absent |
| R10-DEEPLINK-HANDLERS | planned | defect | S | - | R10-DEEPLINK-CENSUS | (not in file) | - | 2 commits, 2 own |
| R10-ARCH-DOCS | not-started | feature | L | - | 33 groups (see json) | (not in file) | - | ref absent |
| R10-RCA-FRICTION | not-started | policy | S | - |  | (not in file) | - | ref absent |
| R10-POLICY-FIXER-MD | not-started | policy | S | - | R10-RCA-FRICTION, R10-BRIEFS-FOLD | (not in file) | - | ref absent |
| R10-POLICY-GATE-SCOPING | not-started | policy | S | - | R10-TICK-DRIVERS | (not in file) | - | ref absent |
| R10-RCA-HEADMOVED | not-started | study | S | - | R10-RCA-FRICTION | (not in file) | - | ref absent |
| R10-RCA-STRUCTURE-BLIND | not-started | study | S | - |  | (not in file) | #2415 (title starts with group id; branch name = group slug; branch = resume.branch tail) | 2 commits, 1 own |
| R10-SAV-COMFORT | not-started | owner | M | - | R10-SAV-BASELINE | (not in file) | - | ref absent |

Files and hot_files per group are in wave-data.json (`groups.<name>.files`, `.hot_files`). Hot files by group:

- R10-VENT-DETECTOR: 1 files; hot_files: coordinator.py
- R10-NIGHT-FOLDS: 2 files; hot_files: coordinator.py
- R10-RATIO-ANCHOR: 4 files; hot_files: config_flow.py, coordinator.py
- R10-INPUT-STALENESS: 2 files; hot_files: const.py, coordinator.py
- R10-CURRENCY: 3 files; hot_files: coordinator.py
- R10-TRUST-RELATIVE: 2 files; hot_files: coordinator.py
- R10-FREQ-DEFROST: 2 files; hot_files: coordinator.py
- R10-LOOP-CPU: 2 files; hot_files: coordinator.py
- R10-SAV-BASELINE: 3 files; hot_files: coordinator.py
- R10-SAV-REASONS: 4 files; hot_files: coordinator.py, optimizer.py
- R10-ADVISOR: 2 files; hot_files: coordinator.py, heatpump-optimizer-card.js
- R10-SCORES: 3 files; hot_files: coordinator.py, heatpump-optimizer-card.js
- R10-LIVESTATE: 7 files; hot_files: coordinator.py
- R10-CONFIG-NOTICES: 2 files; hot_files: coordinator.py
- R10-ARCHSCORE-COVERAGE: 6 files; hot_files: -
- R10-PARAMS-OWNER: 5 files; hot_files: coordinator.py
- R10-SENSOR-PAYLOAD: 3 files; hot_files: -
- R10-ARCH-SHAPES: 11 files; hot_files: coordinator.py
- R10-LEARNER-ETA: 2 files; hot_files: coordinator.py
- R10-HEAT-METER: 6 files; hot_files: config_flow.py, const.py, coordinator.py
- R10-COP-GATE: 2 files; hot_files: coordinator.py
- R10-UX-HEALTH: 3 files; hot_files: heatpump-optimizer-card.js
- R10-CONFIGFLOW-PAGES: 1 files; hot_files: config_flow.py
- R10-SOLVER: 1 files; hot_files: optimizer.py
- R10-I5-DOCS: 8 files; hot_files: -
- R10-TICK-DRIVERS: 6 files; hot_files: -
- R10-BRIEFS-FOLD: 16 files; hot_files: -
- R10-DIAG-REPLAY: 5 files; hot_files: -
- R10-REPLAY-LANE: 2 files; hot_files: -
- R10-REPLAY-SCOPED: 3 files; hot_files: -
- R10-TRAIN-HOLD: 2 files; hot_files: -
- R10-DEEPLINK-HANDLERS: 2 files; hot_files: -
- R10-ARCH-DOCS: 2 files; hot_files: -
- R10-RCA-FRICTION: 1 files; hot_files: -
- R10-POLICY-FIXER-MD: 2 files; hot_files: -
- R10-POLICY-GATE-SCOPING: 1 files; hot_files: -
- R10-RCA-HEADMOVED: 0 files; hot_files: -
- R10-RCA-STRUCTURE-BLIND: 1 files; hot_files: -
- R10-SAV-COMFORT: 2 files; hot_files: -

Open PRs matching a group by name (rules: title starts with the group id; branch equals the group slug with optional `-pr`/`-pN`; branch equals resume.branch tail): R10-VENT-DETECTOR <- [2391]; R10-SAV-BASELINE <- [2411]; R10-ARCHSCORE-COVERAGE <- [2401, 2373]; R10-SENSOR-PAYLOAD <- [2379]; R10-TICK-DRIVERS <- [2390]; R10-DIAG-REPLAY <- [2399]; R10-RCA-STRUCTURE-BLIND <- [2415]. Also matched, group stage `done`: R10-PUMP-MODEL <- #2368 (title "R10-PUMP-MODEL D2"). Open PRs with no roster group: #2394, #2404, #2406, #2408, #2416, #2417, #2418.

## 2. Contention matrix (non-empty pairs only)

Items: the 16 open PRs (actual files from the API) and the 39 not-done groups (declared `files`). A group and its own matching PR are not paired. Method: python set intersection of file lists; `shared-append` files (tests/features.py, entities.py, seam_map.json, finite_boundary.py, guard_pins.py, dst_checks.py, arch_score_head.py, structure_budgets.json, mutation ledger) are flagged because the roster says they are rebases, not after-edges. No pair in the list consists only of shared-append files. Totals: {'pr-pr': 64, 'pr-group': 86, 'group-group': 190}; every pair has at least one non-shared file.

### PR x PR

- PR#2368 x PR#2373: tests/closures.json
- PR#2368 x PR#2379: tests/closures.json, tests/entities.py
- PR#2368 x PR#2390: tests/closures.json
- PR#2368 x PR#2391: custom_components/heatpump_optimizer/coordinator.py, tests/closures.json, tests/features.py
- PR#2368 x PR#2399: tests/closures.json, tests/entities.py
- PR#2368 x PR#2401: tests/closures.json
- PR#2368 x PR#2404: tests/closures.json
- PR#2368 x PR#2406: tests/card.mjs, tests/closures.json
- PR#2368 x PR#2411: custom_components/heatpump_optimizer/coordinator.py, tests/closures.json, tests/features.py, tests/golden/claimed_drift.txt
- PR#2368 x PR#2415: tests/closures.json
- PR#2373 x PR#2379: tests/closures.json
- PR#2373 x PR#2390: tests/closures.json
- PR#2373 x PR#2391: tests/closures.json
- PR#2373 x PR#2399: tests/closures.json
- PR#2373 x PR#2401: dev/programme/delivery/2373.md, tests/ci_budgets.json, tests/closures.json, tests/doc_claims.py, tools/audit/archscore/ABOUT.md, tools/audit/archscore/calibration/corpus_vectors.json (+15 more)
- PR#2373 x PR#2404: tests/closures.json
- PR#2373 x PR#2406: tests/closures.json
- PR#2373 x PR#2411: tests/closures.json
- PR#2373 x PR#2415: tests/closures.json
- PR#2379 x PR#2390: tests/closures.json
- PR#2379 x PR#2391: tests/closures.json
- PR#2379 x PR#2399: tests/closures.json, tests/entities.py, tests/finite_boundary.py
- PR#2379 x PR#2401: tests/closures.json
- PR#2379 x PR#2404: tests/closures.json
- PR#2379 x PR#2406: tests/closures.json
- PR#2379 x PR#2411: tests/closures.json, tests/structure_budgets.json
- PR#2379 x PR#2415: tests/closures.json, tests/structure_budgets.json
- PR#2390 x PR#2391: tests/closures.json
- PR#2390 x PR#2394: tools/audit/seat/INSTRUMENTS.md
- PR#2390 x PR#2399: tests/closures.json
- PR#2390 x PR#2401: tests/closures.json
- PR#2390 x PR#2404: tests/closures.json
- PR#2390 x PR#2406: tests/closures.json, tools/audit/seat/INSTRUMENTS.md, tools/pr/prepr.sh
- PR#2390 x PR#2411: tests/closures.json
- PR#2390 x PR#2415: tests/closures.json
- PR#2390 x PR#2416: tools/audit/seat/INSTRUMENTS.md
- PR#2391 x PR#2399: custom_components/heatpump_optimizer/const.py, custom_components/heatpump_optimizer/store.py, tests/closures.json
- PR#2391 x PR#2401: tests/closures.json
- PR#2391 x PR#2404: tests/closures.json
- PR#2391 x PR#2406: tests/closures.json
- PR#2391 x PR#2411: custom_components/heatpump_optimizer/coordinator.py, tests/closures.json, tests/features.py
- PR#2391 x PR#2415: tests/closures.json
- PR#2394 x PR#2404: tools/audit/seat/merge_train.py, tools/audit/seat/queue_pre_flight.py
- PR#2394 x PR#2406: tools/audit/seat/INSTRUMENTS.md
- PR#2394 x PR#2416: tools/audit/seat/INSTRUMENTS.md
- PR#2399 x PR#2401: tests/closures.json
- PR#2399 x PR#2404: tests/closures.json
- PR#2399 x PR#2406: tests/closures.json
- PR#2399 x PR#2411: tests/closures.json
- PR#2399 x PR#2415: tests/closures.json
- PR#2401 x PR#2404: tests/closures.json
- PR#2401 x PR#2406: tests/closures.json
- PR#2401 x PR#2411: tests/closures.json
- PR#2401 x PR#2415: tests/closures.json
- PR#2404 x PR#2406: tests/closures.json
- PR#2404 x PR#2408: .claude/rules/finding-propagation.md, .cursor/rules/finding-propagation.mdc, dev/governance/rules/finding-propagation.md
- PR#2404 x PR#2411: tests/closures.json
- PR#2404 x PR#2415: tests/closures.json
- PR#2404 x PR#2416: .github/workflows/governance.yml
- PR#2406 x PR#2408: tools/policy/policy_lint.mjs
- PR#2406 x PR#2411: tests/closures.json
- PR#2406 x PR#2415: tests/closures.json
- PR#2406 x PR#2416: tools/audit/seat/INSTRUMENTS.md
- PR#2411 x PR#2415: tests/closures.json, tests/structure_budgets.json

### PR x group

- PR#2368 x R10-ADVISOR: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-ARCH-SHAPES: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/thermal_model.py
- PR#2368 x R10-CONFIG-NOTICES: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-COP-GATE: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-CURRENCY: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-DEEPLINK-HANDLERS: tests/card.mjs
- PR#2368 x R10-FREQ-DEFROST: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-HEAT-METER: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-I5-DOCS: tests/stress.py
- PR#2368 x R10-INPUT-STALENESS: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-LEARNER-ETA: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-LIVESTATE: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/thermal_model.py
- PR#2368 x R10-LOOP-CPU: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-REPLAY-SCOPED: tests/closures.json
- PR#2368 x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- PR#2368 x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- PR#2373 x R10-REPLAY-SCOPED: tests/closures.json
- PR#2379 x R10-COP-GATE: custom_components/heatpump_optimizer/sensor.py
- PR#2379 x R10-REPLAY-SCOPED: tests/closures.json
- PR#2379 x R10-SCORES: custom_components/heatpump_optimizer/sensor.py
- PR#2390 x R10-BRIEFS-FOLD: tools/policy/check-wave-script.mjs
- PR#2390 x R10-REPLAY-SCOPED: tests/closures.json
- PR#2391 x R10-ADVISOR: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-ARCH-SHAPES: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-CONFIG-NOTICES: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-COP-GATE: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-CURRENCY: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-FREQ-DEFROST: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-HEAT-METER: custom_components/heatpump_optimizer/const.py, custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-INPUT-STALENESS: custom_components/heatpump_optimizer/const.py, custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-LEARNER-ETA: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-LIVESTATE: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-LOOP-CPU: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/store.py
- PR#2391 x R10-REPLAY-SCOPED: tests/closures.json
- PR#2391 x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- PR#2391 x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- PR#2394 x R10-BRIEFS-FOLD: dev/governance/rules/ci-autofix.md
- PR#2394 x R10-TRAIN-HOLD: tools/audit/seat/merge_train.py
- PR#2399 x R10-ARCH-DOCS: docs/architecture.md
- PR#2399 x R10-HEAT-METER: custom_components/heatpump_optimizer/const.py
- PR#2399 x R10-INPUT-STALENESS: custom_components/heatpump_optimizer/const.py
- PR#2399 x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/store.py
- PR#2399 x R10-REPLAY-SCOPED: tests/closures.json
- PR#2401 x R10-REPLAY-SCOPED: tests/closures.json
- PR#2404 x R10-REPLAY-SCOPED: tests/closures.json
- PR#2404 x R10-TRAIN-HOLD: tools/audit/seat/merge_train.py
- PR#2406 x R10-DEEPLINK-HANDLERS: tests/card.mjs
- PR#2406 x R10-REPLAY-SCOPED: .github/workflows/tests.yml, tests/closures.json
- PR#2406 x R10-TRAIN-HOLD: .github/workflows/tests.yml
- PR#2408 x R10-BRIEFS-FOLD: dev/governance/roles/fix-review.md
- PR#2408 x R10-POLICY-FIXER-MD: dev/governance/roles/fix-review.md
- PR#2408 x R10-RCA-FRICTION: dev/governance/roles/fix-review.md
- PR#2411 x R10-ADVISOR: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-ARCH-SHAPES: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-CONFIG-NOTICES: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-COP-GATE: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-CURRENCY: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-FREQ-DEFROST: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-HEAT-METER: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-INPUT-STALENESS: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-LEARNER-ETA: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-LIVESTATE: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-LOOP-CPU: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-REPLAY-SCOPED: tests/closures.json
- PR#2411 x R10-SAV-COMFORT: custom_components/heatpump_optimizer/ledger.py, custom_components/heatpump_optimizer/optimizer.py
- PR#2411 x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/optimizer.py
- PR#2411 x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-SOLVER: custom_components/heatpump_optimizer/optimizer.py
- PR#2411 x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- PR#2411 x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- PR#2415 x R10-I5-DOCS: tests/structure.py
- PR#2415 x R10-REPLAY-SCOPED: tests/closures.json

### group x group

- R10-ADVISOR x R10-ARCH-SHAPES: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-CONFIG-NOTICES: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-COP-GATE: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-CURRENCY: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-FREQ-DEFROST: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-HEAT-METER: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-INPUT-STALENESS: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-LEARNER-ETA: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-LIVESTATE: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-LOOP-CPU: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
- R10-ADVISOR x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-ADVISOR x R10-UX-HEALTH: custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
- R10-ADVISOR x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-DOCS x R10-I5-DOCS: README.md
- R10-ARCH-SHAPES x R10-CONFIG-NOTICES: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-COP-GATE: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-CURRENCY: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-FREQ-DEFROST: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/freq_control.py
- R10-ARCH-SHAPES x R10-HEAT-METER: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-INPUT-STALENESS: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-LEARNER-ETA: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-LIVESTATE: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/thermal_model.py
- R10-ARCH-SHAPES x R10-LOOP-CPU: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-ARCH-SHAPES x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-BRIEFS-FOLD x R10-POLICY-FIXER-MD: dev/governance/roles/fix-review.md, dev/governance/roles/fixer.md
- R10-BRIEFS-FOLD x R10-RCA-FRICTION: dev/governance/roles/fix-review.md
- R10-CONFIG-NOTICES x R10-COP-GATE: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-CURRENCY: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-FREQ-DEFROST: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-HEAT-METER: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-INPUT-STALENESS: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-LEARNER-ETA: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-LIVESTATE: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-LOOP-CPU: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIG-NOTICES x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-CONFIGFLOW-PAGES x R10-HEAT-METER: custom_components/heatpump_optimizer/config_flow.py
- R10-CONFIGFLOW-PAGES x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/config_flow.py
- R10-COP-GATE x R10-CURRENCY: custom_components/heatpump_optimizer/coordinator.py
- R10-COP-GATE x R10-FREQ-DEFROST: custom_components/heatpump_optimizer/coordinator.py
- R10-COP-GATE x R10-HEAT-METER: custom_components/heatpump_optimizer/coordinator.py
- R10-COP-GATE x R10-INPUT-STALENESS: custom_components/heatpump_optimizer/coordinator.py
- R10-COP-GATE x R10-LEARNER-ETA: custom_components/heatpump_optimizer/coordinator.py
- R10-COP-GATE x R10-LIVESTATE: custom_components/heatpump_optimizer/coordinator.py
- R10-COP-GATE x R10-LOOP-CPU: custom_components/heatpump_optimizer/coordinator.py
- R10-COP-GATE x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/coordinator.py
- R10-COP-GATE x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- R10-COP-GATE x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py
- R10-COP-GATE x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- R10-COP-GATE x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- R10-COP-GATE x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/sensor.py
- R10-COP-GATE x R10-SENSOR-PAYLOAD: custom_components/heatpump_optimizer/sensor.py
- R10-COP-GATE x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-COP-GATE x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-CURRENCY x R10-FREQ-DEFROST: custom_components/heatpump_optimizer/coordinator.py
- R10-CURRENCY x R10-HEAT-METER: custom_components/heatpump_optimizer/coordinator.py
- R10-CURRENCY x R10-INPUT-STALENESS: custom_components/heatpump_optimizer/coordinator.py
- R10-CURRENCY x R10-LEARNER-ETA: custom_components/heatpump_optimizer/coordinator.py
- R10-CURRENCY x R10-LIVESTATE: custom_components/heatpump_optimizer/coordinator.py
- R10-CURRENCY x R10-LOOP-CPU: custom_components/heatpump_optimizer/coordinator.py
- R10-CURRENCY x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/coordinator.py
- R10-CURRENCY x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- R10-CURRENCY x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py
- R10-CURRENCY x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/narrative.py
- R10-CURRENCY x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/narrative.py
- R10-CURRENCY x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-CURRENCY x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-CURRENCY x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-DIAG-REPLAY x R10-REPLAY-LANE: tests/replay.py
- R10-DIAG-REPLAY x R10-REPLAY-SCOPED: tests/replay.py
- R10-FREQ-DEFROST x R10-HEAT-METER: custom_components/heatpump_optimizer/coordinator.py
- R10-FREQ-DEFROST x R10-INPUT-STALENESS: custom_components/heatpump_optimizer/coordinator.py
- R10-FREQ-DEFROST x R10-LEARNER-ETA: custom_components/heatpump_optimizer/coordinator.py
- R10-FREQ-DEFROST x R10-LIVESTATE: custom_components/heatpump_optimizer/coordinator.py
- R10-FREQ-DEFROST x R10-LOOP-CPU: custom_components/heatpump_optimizer/coordinator.py
- R10-FREQ-DEFROST x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/coordinator.py
- R10-FREQ-DEFROST x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- R10-FREQ-DEFROST x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py
- R10-FREQ-DEFROST x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- R10-FREQ-DEFROST x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- R10-FREQ-DEFROST x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-FREQ-DEFROST x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-FREQ-DEFROST x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-HEAT-METER x R10-INPUT-STALENESS: custom_components/heatpump_optimizer/const.py, custom_components/heatpump_optimizer/coordinator.py
- R10-HEAT-METER x R10-LEARNER-ETA: custom_components/heatpump_optimizer/coordinator.py
- R10-HEAT-METER x R10-LIVESTATE: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/flow_meter.py
- R10-HEAT-METER x R10-LOOP-CPU: custom_components/heatpump_optimizer/coordinator.py
- R10-HEAT-METER x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/coordinator.py
- R10-HEAT-METER x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- R10-HEAT-METER x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/config_flow.py, custom_components/heatpump_optimizer/coordinator.py
- R10-HEAT-METER x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- R10-HEAT-METER x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- R10-HEAT-METER x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-HEAT-METER x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-HEAT-METER x R10-UX-HEALTH: custom_components/heatpump_optimizer/strings.json, custom_components/heatpump_optimizer/translations/en.json
- R10-HEAT-METER x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-INPUT-STALENESS x R10-LEARNER-ETA: custom_components/heatpump_optimizer/coordinator.py
- R10-INPUT-STALENESS x R10-LIVESTATE: custom_components/heatpump_optimizer/coordinator.py
- R10-INPUT-STALENESS x R10-LOOP-CPU: custom_components/heatpump_optimizer/coordinator.py
- R10-INPUT-STALENESS x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/coordinator.py
- R10-INPUT-STALENESS x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- R10-INPUT-STALENESS x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py
- R10-INPUT-STALENESS x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- R10-INPUT-STALENESS x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- R10-INPUT-STALENESS x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-INPUT-STALENESS x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-INPUT-STALENESS x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-LEARNER-ETA x R10-LIVESTATE: custom_components/heatpump_optimizer/coordinator.py
- R10-LEARNER-ETA x R10-LOOP-CPU: custom_components/heatpump_optimizer/coordinator.py
- R10-LEARNER-ETA x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/coordinator.py
- R10-LEARNER-ETA x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- R10-LEARNER-ETA x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py
- R10-LEARNER-ETA x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- R10-LEARNER-ETA x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/payload.py
- R10-LEARNER-ETA x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-LEARNER-ETA x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-LEARNER-ETA x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-LIVESTATE x R10-LOOP-CPU: custom_components/heatpump_optimizer/away.py, custom_components/heatpump_optimizer/coordinator.py
- R10-LIVESTATE x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/accuracy.py, custom_components/heatpump_optimizer/coordinator.py
- R10-LIVESTATE x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- R10-LIVESTATE x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py
- R10-LIVESTATE x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- R10-LIVESTATE x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- R10-LIVESTATE x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-LIVESTATE x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/accuracy.py, custom_components/heatpump_optimizer/coordinator.py
- R10-LIVESTATE x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-LOOP-CPU x R10-NIGHT-FOLDS: custom_components/heatpump_optimizer/coordinator.py
- R10-LOOP-CPU x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- R10-LOOP-CPU x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py
- R10-LOOP-CPU x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- R10-LOOP-CPU x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- R10-LOOP-CPU x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-LOOP-CPU x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-LOOP-CPU x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-NIGHT-FOLDS x R10-PARAMS-OWNER: custom_components/heatpump_optimizer/coordinator.py
- R10-NIGHT-FOLDS x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py
- R10-NIGHT-FOLDS x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- R10-NIGHT-FOLDS x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- R10-NIGHT-FOLDS x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-NIGHT-FOLDS x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/accuracy.py, custom_components/heatpump_optimizer/coordinator.py
- R10-NIGHT-FOLDS x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-PARAMS-OWNER x R10-RATIO-ANCHOR: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/sysid.py
- R10-PARAMS-OWNER x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- R10-PARAMS-OWNER x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- R10-PARAMS-OWNER x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-PARAMS-OWNER x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-PARAMS-OWNER x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-POLICY-FIXER-MD x R10-RCA-FRICTION: dev/governance/roles/fix-review.md
- R10-RATIO-ANCHOR x R10-SAV-BASELINE: custom_components/heatpump_optimizer/coordinator.py
- R10-RATIO-ANCHOR x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py
- R10-RATIO-ANCHOR x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-RATIO-ANCHOR x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-RATIO-ANCHOR x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-REPLAY-LANE x R10-REPLAY-SCOPED: tests/replay.py
- R10-REPLAY-SCOPED x R10-TRAIN-HOLD: .github/workflows/tests.yml
- R10-SAV-BASELINE x R10-SAV-COMFORT: custom_components/heatpump_optimizer/ledger.py
- R10-SAV-BASELINE x R10-SAV-REASONS: custom_components/heatpump_optimizer/coordinator.py, custom_components/heatpump_optimizer/narrative.py
- R10-SAV-BASELINE x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-SAV-BASELINE x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-SAV-BASELINE x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-SAV-COMFORT x R10-SAV-REASONS: custom_components/heatpump_optimizer/optimizer.py
- R10-SAV-COMFORT x R10-SOLVER: custom_components/heatpump_optimizer/optimizer.py
- R10-SAV-REASONS x R10-SCORES: custom_components/heatpump_optimizer/coordinator.py
- R10-SAV-REASONS x R10-SOLVER: custom_components/heatpump_optimizer/optimizer.py
- R10-SAV-REASONS x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-SAV-REASONS x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-SCORES x R10-SENSOR-PAYLOAD: custom_components/heatpump_optimizer/sensor.py
- R10-SCORES x R10-TRUST-RELATIVE: custom_components/heatpump_optimizer/coordinator.py
- R10-SCORES x R10-UX-HEALTH: custom_components/heatpump_optimizer/www/heatpump-optimizer-card.js
- R10-SCORES x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py
- R10-TRUST-RELATIVE x R10-VENT-DETECTOR: custom_components/heatpump_optimizer/coordinator.py

Full file lists per pair: wave-data.json `contention`.

## 3. Dependency DAG among not-done groups, critical path

Duration rule: every group has `size` (S/M/L/XL), which has no hours by itself, so each size is mapped to the **median measured hours of round-10 done groups of that size**. Measured per done group = (latest merge time among its PRs) minus (earliest commit time among its PRs), from `gh pr view N --json commits,createdAt,mergedAt` for the merged PR whose title starts with the group id (25 done groups, all matched; list in wave-data.json `duration_samples`). Handoff refs merge main repeatedly, so the first handoff-ref commit is not separable from main merges (`git log` on the ref); the PR first-commit is the first group-specific commit. Table (hours): {'M': 11.4, 'L': 20.1, 'S': 13.1, 'XL': 30.2}. Rules: {'M': 'median of 7 measured round-10 merged groups of size M', 'L': 'median of 2 measured round-10 merged groups of size L', 'S': 'median of 16 measured round-10 merged groups of size S', 'XL': '1.5 x L median (no merged XL group)'}. Caveats: S (n=16) is larger than M (n=7) because small groups waited in review (S includes 61.9 h, 55.3 h, 35.3 h, 35.2 h, 34.0 h); durations are wall-clock including review rounds and queueing, not effort; XL has no sample so it is 1.5 x the L median (L n=2 only). A group already carrying a PR is still costed at its full duration (no credit for time elapsed).

### Edges = main roster `after`

Critical path (287.4 h): R10-TRUST-RELATIVE[M 11.4] -> R10-FREQ-DEFROST[S 13.1] -> R10-LOOP-CPU[S 13.1] -> R10-SAV-BASELINE[L 20.1] -> R10-SAV-REASONS[M 11.4] -> R10-ADVISOR[M 11.4] -> R10-SCORES[L 20.1] -> R10-LIVESTATE[XL 30.2] -> R10-CONFIG-NOTICES[S 13.1] -> R10-PARAMS-OWNER[XL 30.2] -> R10-ARCH-SHAPES[L 20.1] -> R10-LEARNER-ETA[M 11.4] -> R10-HEAT-METER[XL 30.2] -> R10-COP-GATE[M 11.4] -> R10-UX-HEALTH[L 20.1] -> R10-ARCH-DOCS[L 20.1]

Edges among not-done groups (group: after):

- R10-VENT-DETECTOR: (none)
- R10-NIGHT-FOLDS: R10-VENT-DETECTOR
- R10-RATIO-ANCHOR: R10-NIGHT-FOLDS
- R10-INPUT-STALENESS: R10-RATIO-ANCHOR
- R10-CURRENCY: R10-INPUT-STALENESS
- R10-TRUST-RELATIVE: (none)
- R10-FREQ-DEFROST: R10-TRUST-RELATIVE
- R10-LOOP-CPU: R10-FREQ-DEFROST
- R10-SAV-BASELINE: R10-LOOP-CPU
- R10-SAV-REASONS: R10-SAV-BASELINE
- R10-ADVISOR: R10-SAV-REASONS
- R10-SCORES: R10-ADVISOR
- R10-LIVESTATE: R10-SCORES
- R10-CONFIG-NOTICES: R10-LIVESTATE
- R10-ARCHSCORE-COVERAGE: (none)
- R10-PARAMS-OWNER: R10-CONFIG-NOTICES, R10-ARCHSCORE-COVERAGE
- R10-SENSOR-PAYLOAD: R10-SCORES
- R10-ARCH-SHAPES: R10-PARAMS-OWNER, R10-SENSOR-PAYLOAD, R10-FREQ-DEFROST
- R10-LEARNER-ETA: R10-ARCH-SHAPES
- R10-HEAT-METER: R10-LEARNER-ETA, R10-INPUT-STALENESS, R10-RATIO-ANCHOR
- R10-COP-GATE: R10-HEAT-METER, R10-SENSOR-PAYLOAD
- R10-UX-HEALTH: R10-SCORES, R10-COP-GATE, R10-HEAT-METER
- R10-CONFIGFLOW-PAGES: R10-HEAT-METER
- R10-SOLVER: R10-SAV-REASONS
- R10-I5-DOCS: (none)
- R10-TICK-DRIVERS: (none)
- R10-BRIEFS-FOLD: R10-ARCHSCORE-COVERAGE
- R10-DIAG-REPLAY: (none)
- R10-REPLAY-LANE: R10-DIAG-REPLAY
- R10-REPLAY-SCOPED: R10-REPLAY-LANE, R10-TRAIN-HOLD
- R10-TRAIN-HOLD: (none)
- R10-DEEPLINK-HANDLERS: (none)
- R10-ARCH-DOCS: R10-VENT-DETECTOR, R10-NIGHT-FOLDS, R10-RATIO-ANCHOR, R10-INPUT-STALENESS, R10-CURRENCY, R10-TRUST-RELATIVE, R10-FREQ-DEFROST, R10-LOOP-CPU, R10-SAV-BASELINE, R10-SAV-REASONS, R10-ADVISOR, R10-SCORES, R10-LIVESTATE, R10-CONFIG-NOTICES, R10-ARCHSCORE-COVERAGE, R10-PARAMS-OWNER, R10-SENSOR-PAYLOAD, R10-ARCH-SHAPES, R10-LEARNER-ETA, R10-HEAT-METER, R10-COP-GATE, R10-UX-HEALTH, R10-CONFIGFLOW-PAGES, R10-SOLVER, R10-I5-DOCS, R10-TICK-DRIVERS, R10-BRIEFS-FOLD, R10-DIAG-REPLAY, R10-REPLAY-LANE, R10-REPLAY-SCOPED, R10-TRAIN-HOLD, R10-DEEPLINK-HANDLERS
- R10-RCA-FRICTION: (none)
- R10-POLICY-FIXER-MD: R10-RCA-FRICTION, R10-BRIEFS-FOLD
- R10-POLICY-GATE-SCOPING: R10-TICK-DRIVERS
- R10-RCA-HEADMOVED: R10-RCA-FRICTION
- R10-RCA-STRUCTURE-BLIND: (none)
- R10-SAV-COMFORT: R10-SAV-BASELINE

Earliest finish (hours from now, longest chain, no resource cap): R10-VENT-DETECTOR 11; R10-TRUST-RELATIVE 11; R10-TICK-DRIVERS 11; R10-I5-DOCS 13; R10-TRAIN-HOLD 13; R10-DEEPLINK-HANDLERS 13; R10-RCA-FRICTION 13; R10-RCA-STRUCTURE-BLIND 13; R10-ARCHSCORE-COVERAGE 20; R10-DIAG-REPLAY 20; R10-NIGHT-FOLDS 23; R10-FREQ-DEFROST 24; R10-POLICY-GATE-SCOPING 24; R10-RCA-HEADMOVED 26; R10-BRIEFS-FOLD 32; R10-REPLAY-LANE 32; R10-RATIO-ANCHOR 34; R10-LOOP-CPU 38; R10-REPLAY-SCOPED 45; R10-POLICY-FIXER-MD 45; R10-INPUT-STALENESS 47; R10-SAV-BASELINE 58; R10-CURRENCY 60; R10-SAV-REASONS 69; R10-SAV-COMFORT 69; R10-ADVISOR 80; R10-SOLVER 80; R10-SCORES 101; R10-SENSOR-PAYLOAD 121; R10-LIVESTATE 131; R10-CONFIG-NOTICES 144; R10-PARAMS-OWNER 174; R10-ARCH-SHAPES 194; R10-LEARNER-ETA 206; R10-HEAT-METER 236; R10-COP-GATE 247; R10-CONFIGFLOW-PAGES 256; R10-UX-HEALTH 267; R10-ARCH-DOCS 287

### Edges = REPLAN-EDGES.json where the group is listed, roster `after` otherwise

Critical path (146.2 h): R10-VENT-DETECTOR[M 11.4] -> R10-NIGHT-FOLDS[M 11.4] -> R10-TRUST-RELATIVE[M 11.4] -> R10-LIVESTATE[XL 30.2] -> R10-HEAT-METER[XL 30.2] -> R10-COP-GATE[M 11.4] -> R10-UX-HEALTH[L 20.1] -> R10-ARCH-DOCS[L 20.1]

Edges among not-done groups (group: after):

- R10-VENT-DETECTOR: (none)
- R10-NIGHT-FOLDS: R10-VENT-DETECTOR
- R10-RATIO-ANCHOR: (none)
- R10-INPUT-STALENESS: (none)
- R10-CURRENCY: (none)
- R10-TRUST-RELATIVE: R10-NIGHT-FOLDS
- R10-FREQ-DEFROST: (none)
- R10-LOOP-CPU: (none)
- R10-SAV-BASELINE: (none)
- R10-SAV-REASONS: R10-SAV-BASELINE
- R10-ADVISOR: R10-SAV-BASELINE
- R10-SCORES: R10-ADVISOR, R10-SAV-BASELINE, R10-SENSOR-PAYLOAD
- R10-LIVESTATE: R10-VENT-DETECTOR, R10-NIGHT-FOLDS, R10-TRUST-RELATIVE, R10-RATIO-ANCHOR, R10-INPUT-STALENESS, R10-CURRENCY, R10-FREQ-DEFROST, R10-LOOP-CPU
- R10-CONFIG-NOTICES: (none)
- R10-ARCHSCORE-COVERAGE: (none)
- R10-PARAMS-OWNER: R10-ARCHSCORE-COVERAGE, R10-LIVESTATE, R10-CONFIG-NOTICES, R10-HEAT-METER
- R10-SENSOR-PAYLOAD: (none)
- R10-ARCH-SHAPES: (none)
- R10-LEARNER-ETA: R10-TRUST-RELATIVE, R10-SCORES
- R10-HEAT-METER: R10-RATIO-ANCHOR, R10-INPUT-STALENESS, R10-LIVESTATE, R10-LEARNER-ETA, R10-TRUST-RELATIVE
- R10-COP-GATE: R10-HEAT-METER, R10-SENSOR-PAYLOAD
- R10-UX-HEALTH: R10-SCORES, R10-COP-GATE, R10-HEAT-METER, R10-LEARNER-ETA
- R10-CONFIGFLOW-PAGES: R10-HEAT-METER
- R10-SOLVER: R10-SAV-REASONS
- R10-I5-DOCS: (none)
- R10-TICK-DRIVERS: (none)
- R10-BRIEFS-FOLD: R10-ARCHSCORE-COVERAGE, R10-TICK-DRIVERS
- R10-DIAG-REPLAY: (none)
- R10-REPLAY-LANE: R10-DIAG-REPLAY
- R10-REPLAY-SCOPED: R10-REPLAY-LANE, R10-TRAIN-HOLD
- R10-TRAIN-HOLD: (none)
- R10-DEEPLINK-HANDLERS: (none)
- R10-ARCH-DOCS: R10-VENT-DETECTOR, R10-NIGHT-FOLDS, R10-RATIO-ANCHOR, R10-INPUT-STALENESS, R10-CURRENCY, R10-TRUST-RELATIVE, R10-FREQ-DEFROST, R10-LOOP-CPU, R10-SAV-BASELINE, R10-SAV-REASONS, R10-ADVISOR, R10-SCORES, R10-LIVESTATE, R10-CONFIG-NOTICES, R10-ARCHSCORE-COVERAGE, R10-PARAMS-OWNER, R10-SENSOR-PAYLOAD, R10-ARCH-SHAPES, R10-LEARNER-ETA, R10-HEAT-METER, R10-COP-GATE, R10-UX-HEALTH, R10-CONFIGFLOW-PAGES, R10-SOLVER, R10-I5-DOCS, R10-TICK-DRIVERS, R10-BRIEFS-FOLD, R10-DIAG-REPLAY, R10-REPLAY-LANE, R10-REPLAY-SCOPED, R10-TRAIN-HOLD, R10-DEEPLINK-HANDLERS
- R10-RCA-FRICTION: (none)
- R10-POLICY-FIXER-MD: R10-RCA-FRICTION, R10-BRIEFS-FOLD
- R10-POLICY-GATE-SCOPING: R10-TICK-DRIVERS
- R10-RCA-HEADMOVED: R10-RCA-FRICTION
- R10-RCA-STRUCTURE-BLIND: (none)
- R10-SAV-COMFORT: R10-SAV-BASELINE

Earliest finish (hours from now, longest chain, no resource cap): R10-VENT-DETECTOR 11; R10-RATIO-ANCHOR 11; R10-TICK-DRIVERS 11; R10-INPUT-STALENESS 13; R10-CURRENCY 13; R10-FREQ-DEFROST 13; R10-LOOP-CPU 13; R10-CONFIG-NOTICES 13; R10-I5-DOCS 13; R10-TRAIN-HOLD 13; R10-DEEPLINK-HANDLERS 13; R10-RCA-FRICTION 13; R10-RCA-STRUCTURE-BLIND 13; R10-SAV-BASELINE 20; R10-ARCHSCORE-COVERAGE 20; R10-SENSOR-PAYLOAD 20; R10-ARCH-SHAPES 20; R10-DIAG-REPLAY 20; R10-NIGHT-FOLDS 23; R10-POLICY-GATE-SCOPING 24; R10-RCA-HEADMOVED 26; R10-SAV-REASONS 32; R10-ADVISOR 32; R10-BRIEFS-FOLD 32; R10-REPLAY-LANE 32; R10-SAV-COMFORT 32; R10-TRUST-RELATIVE 34; R10-SOLVER 43; R10-REPLAY-SCOPED 45; R10-POLICY-FIXER-MD 45; R10-SCORES 52; R10-LEARNER-ETA 63; R10-LIVESTATE 64; R10-HEAT-METER 95; R10-COP-GATE 106; R10-CONFIGFLOW-PAGES 115; R10-PARAMS-OWNER 125; R10-UX-HEALTH 126; R10-ARCH-DOCS 146

Method: python longest-path DP over the DAG restricted to not-done groups (done after-edges dropped; no cycles found in either edge set). Under the roster edges the five-group chain VENT-DETECTOR -> NIGHT-FOLDS -> RATIO-ANCHOR -> INPUT-STALENESS -> CURRENCY and the chain TRUST-RELATIVE -> FREQ-DEFROST -> LOOP-CPU -> SAV-BASELINE -> SAV-REASONS -> ADVISOR -> SCORES -> LIVESTATE ... are serial; REPLAN-EDGES drops most of them (roughly halves the path, 146.2 h vs 287.4 h).

## 4. Unblocked now

### Edge set: roster

Unblocked (every after-edge done): 10. R10-VENT-DETECTOR [PR [2391]]; R10-TRUST-RELATIVE [no PR]; R10-ARCHSCORE-COVERAGE [PR [2401, 2373]]; R10-I5-DOCS [no PR]; R10-TICK-DRIVERS [PR [2390]]; R10-DIAG-REPLAY [PR [2399]]; R10-TRAIN-HOLD [no PR]; R10-DEEPLINK-HANDLERS [no PR]; R10-RCA-FRICTION [no PR]; R10-RCA-STRUCTURE-BLIND [PR [2415]]

Only pointing at groups that have an open PR (start after those merge): 6. R10-NIGHT-FOLDS <- [('R10-VENT-DETECTOR', [2391])]; R10-SAV-REASONS <- [('R10-SAV-BASELINE', [2411])]; R10-BRIEFS-FOLD <- [('R10-ARCHSCORE-COVERAGE', [2401, 2373])]; R10-REPLAY-LANE <- [('R10-DIAG-REPLAY', [2399])]; R10-POLICY-GATE-SCOPING <- [('R10-TICK-DRIVERS', [2390])]; R10-SAV-COMFORT <- [('R10-SAV-BASELINE', [2411])]

### Edge set: replan

Unblocked (every after-edge done): 18. R10-VENT-DETECTOR [PR [2391]]; R10-RATIO-ANCHOR [no PR]; R10-INPUT-STALENESS [no PR]; R10-CURRENCY [no PR]; R10-FREQ-DEFROST [no PR]; R10-LOOP-CPU [no PR]; R10-SAV-BASELINE [PR [2411]]; R10-CONFIG-NOTICES [no PR]; R10-ARCHSCORE-COVERAGE [PR [2401, 2373]]; R10-SENSOR-PAYLOAD [PR [2379]]; R10-ARCH-SHAPES [no PR]; R10-I5-DOCS [no PR]; R10-TICK-DRIVERS [PR [2390]]; R10-DIAG-REPLAY [PR [2399]]; R10-TRAIN-HOLD [no PR]; R10-DEEPLINK-HANDLERS [no PR]; R10-RCA-FRICTION [no PR]; R10-RCA-STRUCTURE-BLIND [PR [2415]]

Only pointing at groups that have an open PR (start after those merge): 7. R10-NIGHT-FOLDS <- [('R10-VENT-DETECTOR', [2391])]; R10-SAV-REASONS <- [('R10-SAV-BASELINE', [2411])]; R10-ADVISOR <- [('R10-SAV-BASELINE', [2411])]; R10-BRIEFS-FOLD <- [('R10-ARCHSCORE-COVERAGE', [2401, 2373]), ('R10-TICK-DRIVERS', [2390])]; R10-REPLAY-LANE <- [('R10-DIAG-REPLAY', [2399])]; R10-POLICY-GATE-SCOPING <- [('R10-TICK-DRIVERS', [2390])]; R10-SAV-COMFORT <- [('R10-SAV-BASELINE', [2411])]

Startable with no PR and no started work (roster edges, unblocked, no open PR): R10-TRUST-RELATIVE, R10-I5-DOCS, R10-TRAIN-HOLD, R10-DEEPLINK-HANDLERS, R10-RCA-FRICTION. Under REPLAN edges the same filter adds: R10-RATIO-ANCHOR, R10-INPUT-STALENESS, R10-CURRENCY, R10-FREQ-DEFROST, R10-LOOP-CPU, R10-CONFIG-NOTICES, R10-ARCH-SHAPES. (R10-DEEPLINK-HANDLERS has 2 own commits on its ref, R10-RCA-STRUCTURE-BLIND has #2415 open.)

## 5. Inconsistencies between roster stages and reality

- **not-started group has open PR** - R10-VENT-DETECTOR: stage "not-started" but open PR [2391]. Command: roster resume.stage vs gh pr list --state open (title/branch match).
- **not-started group has handoff ref ahead of main** - R10-VENT-DETECTOR: origin/handoff/r10-vent-detector is 21 commits ahead of origin/main, 12 own non-bot non-merge. Command: git rev-list --count origin/main..origin/<ref>.
- **not-started group has open PR** - R10-SAV-BASELINE: stage "not-started" but open PR [2411]. Command: roster resume.stage vs gh pr list --state open (title/branch match).
- **not-started group has handoff ref ahead of main** - R10-SAV-BASELINE: origin/handoff/r10-sav-baseline is 33 commits ahead of origin/main, 25 own non-bot non-merge. Command: git rev-list --count origin/main..origin/<ref>.
- **open PR runs ahead of its roster after-edge** - R10-SAV-BASELINE: PR [2411] open while roster after-edge R10-LOOP-CPU is not-started. Command: roster after vs resume.stage.
- **not-done group has merged PR(s)** - R10-ARCHSCORE-COVERAGE: merged: [(2320, '2026-10-17T18:23', 'R10-ARCHSCORE-COVERAGE p3: layering and private cross-module'), (2311, '2026-10-16T14:29', 'R10-ARCHSCORE-COVERAGE p2: hub census follows readers, rebin'), (2293, '2026-10-16T00:10', "R10-ARCHSCORE-COVERAGE (1/5): close ARCH-s3's three archscor")]. Command: gh pr list --state merged --limit 400.
- **not-started group has open PR** - R10-SENSOR-PAYLOAD: stage "not-started" but open PR [2379]. Command: roster resume.stage vs gh pr list --state open (title/branch match).
- **not-started group has handoff ref ahead of main** - R10-SENSOR-PAYLOAD: origin/handoff/r10-sensor-payload is 21 commits ahead of origin/main, 10 own non-bot non-merge. Command: git rev-list --count origin/main..origin/<ref>.
- **open PR runs ahead of its roster after-edge** - R10-SENSOR-PAYLOAD: PR [2379] open while roster after-edge R10-SCORES is not-started. Command: roster after vs resume.stage.
- **not-started group has open PR** - R10-TICK-DRIVERS: stage "not-started" but open PR [2390]. Command: roster resume.stage vs gh pr list --state open (title/branch match).
- **not-started group has handoff ref ahead of main** - R10-TICK-DRIVERS: origin/handoff/r10-tick-drivers is 3 commits ahead of origin/main, 2 own non-bot non-merge. Command: git rev-list --count origin/main..origin/<ref>.
- **not-started group has open PR** - R10-DIAG-REPLAY: stage "not-started" but open PR [2399]. Command: roster resume.stage vs gh pr list --state open (title/branch match).
- **not-started group has handoff ref ahead of main** - R10-DIAG-REPLAY: origin/handoff/r10-diag-replay is 15 commits ahead of origin/main, 11 own non-bot non-merge. Command: git rev-list --count origin/main..origin/<ref>.
- **not-started group has handoff ref ahead of main** - R10-DEEPLINK-HANDLERS: origin/handoff/r10-deeplink-handlers is 2 commits ahead of origin/main, 2 own non-bot non-merge. Command: git rev-list --count origin/main..origin/<ref>.
- **not-started group has open PR** - R10-RCA-STRUCTURE-BLIND: stage "not-started" but open PR [2415]. Command: roster resume.stage vs gh pr list --state open (title/branch match).
- **not-started group has handoff ref ahead of main** - R10-RCA-STRUCTURE-BLIND: origin/handoff/r10-rca-structure-blind is 2 commits ahead of origin/main, 1 own non-bot non-merge. Command: git rev-list --count origin/main..origin/<ref>.
- **done group has open PR** - R10-PUMP-MODEL: open PR [(2368, 'R10-PUMP-MODEL D2: one DHW lift law on every plant')]. Command: gh pr list --state open.
- **done group handoff ref missing** - R10-TICK-ORCH: handoff/r10-tick-orch. Command: git rev-parse origin/<ref>.
- **stage text stale** - R10-ARCHSCORE-COVERAGE: stage says "in-progress: p1 #2293 + p2 #2311 merged; p3 #2320 in review r4; p4/p5 not started"; #2320 (p3) merged 2026-10-17T18:23Z, #2373 (p4) and #2401 (p5) are open. Command: roster stage vs gh pr list.
- **open PR with no roster group** - PR#2418: record: delivery rows for #2384, #2393, #2400, #2403, #2414 (autofix) (record/autofix). Command: title/branch match against 63 roster group ids.
- **open PR with no roster group** - PR#2417: roster(r10): forward-carries from #2411 and #2406 reviews (fix/audit-r10-roster). Command: title/branch match against 63 roster group ids.
- **open PR with no roster group** - PR#2416: tools: persistent sweep template, renderer and policy re-read check (fix/r10-sweep-template-pr). Command: title/branch match against 63 roster group ids.
- **open PR with no roster group** - PR#2408: R10-ROSTER-CARRY-POLICY: roster carries count on the roster ref; landing trigger (fix/r10-roster-carry-policy). Command: title/branch match against 63 roster group ids.
- **open PR with no roster group** - PR#2406: R10-ROSTER-FASTPATH: tools read the round roster ref; Level 0 lane skip for rost (fix/r10-roster-fastpath). Command: title/branch match against 63 roster group ids.
- **open PR with no roster group** - PR#2404: O11: carry-forward made mechanical (carry_audit.py) (fix/r10-carry-enforce). Command: title/branch match against 63 roster group ids.
- **open PR with no roster group** - PR#2394: R10-CI-AUTOFIX-INERT-ROUTE: route INERT repairs through the autofix (fix/r10-ci-autofix-inert-route). Command: title/branch match against 63 roster group ids.
- **tick PLAN says UNBLOCKED not started, PR exists** - R10-VENT-DETECTOR: tick.log newest pass prints "-> R10-VENT-DETECTOR: UNBLOCKED, not started -- start a fixer" while PR [2391] is open. Command: grep newest ##### PASS block.
- **tick PLAN says UNBLOCKED not started, PR exists** - R10-TICK-DRIVERS: tick.log newest pass prints "-> R10-TICK-DRIVERS: UNBLOCKED, not started -- start a fixer" while PR [2390] is open. Command: grep newest ##### PASS block.
- **tick PLAN says UNBLOCKED not started, PR exists** - R10-DIAG-REPLAY: tick.log newest pass prints "-> R10-DIAG-REPLAY: UNBLOCKED, not started -- start a fixer" while PR [2399] is open. Command: grep newest ##### PASS block.
- **tick PLAN says UNBLOCKED not started, PR exists** - R10-RCA-STRUCTURE-BLIND: tick.log newest pass prints "-> R10-RCA-STRUCTURE-BLIND: UNBLOCKED, not started -- start a fixer" while PR [2415] is open. Command: grep newest ##### PASS block.
- **roster PR adds a group** - R10-SAV-COMFORT: present in #2417 head roster (wave 16, size M), absent from origin/main roster; tick counts 38 open of 63. Command: diff of wave-r10-groups.json origin/main vs origin/pr2417.
- **REPLAN-EDGES differs from roster** - edges: 23 not-done groups carry different after-edges in REPLAN-EDGES.json than in the roster; 8 not-done groups are absent from REPLAN-EDGES.json (['R10-ARCHSCORE-COVERAGE', 'R10-DEEPLINK-HANDLERS', 'R10-ARCH-DOCS', 'R10-RCA-FRICTION', 'R10-POLICY-FIXER-MD', 'R10-POLICY-GATE-SCOPING', 'R10-RCA-HEADMOVED', 'R10-RCA-STRUCTURE-BLIND']). Command: python diff of REPLAN-EDGES.json vs roster after.

## 6. Open PRs: 16, state of each

Count: `gh pr list --state open | length` = 16. Rule: take the newest `Fix review:` issue comment (by created_at); if its sha is a prefix of the live `headRefOid` the state is its verdict (merge = verdicted, blocked = blocked); otherwise (no comment, or head moved after the verdict) = under review. Totals: {'under review': 8, 'blocked': 7, 'verdicted': 1}.

| PR | live head | title | state | newest Fix review (id, verdict @ sha) | merge state / reviewDecision / draft | tick (18:19Z) |
|---|---|---|---|---|---|---|
| #2417 | c83ae12ac | roster(r10): forward-carries from #2411 and #2406 revie | blocked | 6253477740, blocked @ c83ae12ac | BLOCKED / REVIEW_REQUIRED / draft | CI: GREEN; 29 commits behind main (recarry due before it can merge) |
| #2415 | 9951f224a | R10-RCA-STRUCTURE-BLIND: root-cause record for N-struct | blocked | 6253266283, blocked @ 9951f224a | BLOCKED / REVIEW_REQUIRED / draft | CI: GREEN; 90 commits behind main (recarry due before it can merge) |
| #2408 | e3a6f0729 | R10-ROSTER-CARRY-POLICY: roster carries count on the ro | blocked | 6253163400, blocked @ e3a6f0729 | BLOCKED / REVIEW_REQUIRED / draft | CI: GREEN; 130 commits behind main (recarry due before it can merge); code-owned with no @tvofi review at any  |
| #2404 | 312f31923 | O11: carry-forward made mechanical (carry_audit.py) | blocked | 6253086887, blocked @ 312f31923 | BLOCKED / REVIEW_REQUIRED / draft | CI: GREEN; 90 commits behind main (recarry due before it can merge); code-owned with no @tvofi review at any h |
| #2390 | 5f6d8fbd7 | R10-TICK-DRIVERS: tick drivers and handoff prepr counte | blocked | 6252219632, blocked @ 5f6d8fbd7 | BLOCKED / REVIEW_REQUIRED / draft | CI: GREEN; 142 commits behind main (recarry due before it can merge); code-owned with no @tvofi review at any  |
| #2373 | e14a378c1 | R10-ARCHSCORE-COVERAGE p4: card coverage and literal cl | blocked | 6249319694, blocked @ e14a378c1 | BLOCKED / REVIEW_REQUIRED / draft | CI: GREEN; 160 commits behind main (recarry due before it can merge); code-owned with no @tvofi review at any  |
| #2368 | c3a25d2ae | R10-PUMP-MODEL D2: one DHW lift law on every plant | blocked | 6253502824, blocked @ c3a25d2ae | BLOCKED / REVIEW_REQUIRED / draft | CI: RED:budget-raise-gate,fast (3.14); 29 commits behind main (recarry due before it can merge); code-owned wi |
| #2418 | 4be8f4cfd | record: delivery rows for #2384, #2393, #2400, #2403, # | under review | - | CLEAN / APPROVED / ready | CI: RUN:closures,graders-head-copy,lane-proofs |
| #2416 | 319769bb4 | tools: persistent sweep template, renderer and policy r | under review | 6253411021, merge @ c5bc2f147 | BLOCKED / REVIEW_REQUIRED / draft | CI: GREEN; 29 commits behind main (recarry due before it can merge); code-owned with no @tvofi review at any h |
| #2411 | 74d66b355 | R10-SAV-BASELINE: thermostat baseline from a held state | under review | 6252668916, merge @ 3b6e599df | BLOCKED / REVIEW_REQUIRED / draft | CI: RUN:mutation-pins (1); 47 commits behind main (recarry due before it can merge) |
| #2406 | d1becac2b | R10-ROSTER-FASTPATH: tools read the round roster ref; L | under review | 6252146172, blocked @ b965c4ab9 | BLOCKED / REVIEW_REQUIRED / draft | CI: RUN:Analyze (python),closures,fast (3.14); 29 commits behind main (recarry due before it can merge); code- |
| #2401 | 311e9de3e | R10-ARCHSCORE-COVERAGE p5: the shape census, calibrated | under review | 6252448347, merge @ da688f509 | BLOCKED / APPROVED / draft | CI: RUN:coverage,fast (3.14) |
| #2399 | acf14d8f2 | R10-DIAG-REPLAY: a replay document in Download diagnost | under review | - | BLOCKED / REVIEW_REQUIRED / draft | CI: RUN:arch-score,briefs,budget-raise-gate,closure-scope,delivery-status,env-matrix,hassfest,instrument-self- |
| #2394 | 8d4e8be01 | R10-CI-AUTOFIX-INERT-ROUTE: route INERT repairs through | under review | 6253264138, merge @ 7bda397d1 | BLOCKED / APPROVED / draft | CI: GREEN; 29 commits behind main (recarry due before it can merge) |
| #2391 | 3aba8f1eb | R10-VENT-DETECTOR: vent bias window and probe companion | under review | - | BLOCKED / REVIEW_REQUIRED / draft | CI: RUN:Analyze (actions),Analyze (javascript-typescript),Analyze (python),briefs,browser,coverage,env-matrix, |
| #2379 | f4e168719 | R10-SENSOR-PAYLOAD: one payload-number check, one mixin | verdicted | 6253299774, merge @ f4e168719 | CLEAN / APPROVED / draft | CI: GREEN; 90 commits behind main (recarry due before it can merge) |

Notes: a verdict whose head moved is flagged "head moved since"; #2416, #2411, #2401, #2394 carry a `merge` verdict on an older head (a re-verdict at the live head is owed), #2406 carries a `blocked` on an older head. #2417 and #2368 each received a new `blocked` verdict during this measurement (comments 6253477740, 6253502824). #2418 is a record PR with `reviewDecision` APPROVED but no Fix review comment.
