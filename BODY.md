Owner ruling (tvofi 2026-11-06), verbatim: "The HTML plan seems to incorrectly place some instrument or CI fixes in the core model lane, fix that".

Where the lane is decided: `roster_lane` in `tools/plan/replan.py` writes each group's `lane` into the plan JSON; `tools/audit/seat/plan_page.py` only draws that field. `roster_lane` placed a group by `kind` (`instrument`, `policy`) and then by a list of name prefixes, and **every group neither placed fell through to Core model** — a new CI hotfix, an RCA seat, a tooling chore or a doc group was drawn as core-model work, and counted towards the stamp cadence as production (`PRODUCTION` lanes).

The fix is made at that source, not per group. After the kind and name rules (which keep their precedence, so Learners, Product UX, Replay and Docs placements by name are unchanged), `roster_lane` now reads:
1. **the files the group owns** (`files` + `hot_files`): when every one is an instrument, CI or record path (`tools/`, `tests/`, `.github/`, `.claude/`, `dev/`, `docs/`, or a root record such as `CLAUDE.md`), the group is Instruments, or Docs when it is a `doc` kind or touches user docs (`docs/`, `README.md`) without landing a tool (`tools/`, `.github/`, `.claude/`). A single `custom_components/` file, or a bare filename, keeps it core.
2. **then a tool-landing kind or roster class** for a group whose roster names no file: `kind` in `INSTRUMENT_KINDS` (`instrument`, `policy`, `rca`, `tooling`) or `class: instrument`. `work_class` already priced those kinds as instruments; it now reads the same tuple, so the lane and the duration class cannot disagree on which kinds land tools.

This resumes handoff-wip `bdae685f` (the first fixer's commit, which added step 1). I re-measured it and changed three things. It placed the files check *before* the learner and UX name rules, and so duplicated their names in two new constants to exclude them; the check is now the fallback, which keeps their precedence with no duplicate. It drew a user-docs group that also carried a `dev/` harness (R10-README-GRAPHICS) as Instruments; that group is now Docs. And it left file-less RCA, tooling and `class: instrument` groups in the core lane. Alternatives considered: (a) reading the roster's own `lane` code: it is not a lane in this sense (15 production groups owning only `custom_components/` files carry `lane: IN`), so it lost; (b) adding the misplaced names to the prefix list: that is a per-group spelling list, which the next CI hotfix would fall out of again (fixer.md step 17), so it lost too.

## Head

4c93b7da3507241cb51a1d3d0c653850e362971b (merge base 80016a71f567d936450d8708abcbb79d9e8071d7, origin/main's tip at 2026-11-06T23:39Z). main moved once during the work (#3234: replay draws, nothing `replan.py` reads); it was merged, and every figure below, the self-tests and `prepr.sh` were re-taken at this head. The head also merges `origin/fix/r10-hotfix-plan-lanes` (#3265's merge-main commit and delivery row, which arrived after the first fixer's handoff); that merge adds only `dev/programme/delivery/3265.md`, and `tools/plan/replan.py` is byte-identical to the measured `d05657e10`, at which the mutants were re-run (5 killed, the unmutated copy rc=0).

## Mutation proof

Each production predicate was mutated in a `git archive` copy of the head, and `python3 tools/plan/replan.py --self-test` was run on it. The unmutated copy exits 0.
- delete `if owned := _owned_lane(group): return owned` → rc=1: `lane: a CI-only group is Instruments`, `lane: a tests-and-tools group is Instruments`, `lane: a docs-only doc group is Docs`, `lane: a user-docs group is Docs`, `lane null control: docs plus a tool is Instruments, not Docs`, `lane: user docs with a dev harness are Docs`
- delete the `INSTRUMENT_KINDS`/`class` fallback → rc=1: `lane: an RCA group with no files is Instruments`, `lane: a tooling group with no files is Instruments`, `lane: a roster class instrument with no files is Instruments`
- drop the `class == "instrument"` arm → rc=1: `lane: a roster class instrument with no files is Instruments`
- restore the first commit's user-docs rule (`all(docs/, tests/)`) → rc=1: `lane: user docs with a dev harness are Docs`
- `not all(` → `not any(` in `_owned_lane` → rc=1: `lane null control: a mixed group stays Core model`

Failing test first: the head's self-test run against main's `roster_lane`/`work_class` (the branch's `selftest`, main's production functions) exits 1. It fails 9 lane checks, every non-control case above, and passes all 7 null controls.

## Null control

- A real core-model group stays core: `lane null control: a core-model group stays Core model` (`custom_components/heatpump_optimizer/optimizer.py`). So does a mixed tools + `custom_components/heatpump_optimizer/ledger.py` group, a file-less group, a bare `coordinator.py`, and a file-less `kind: production, class: production` group. Name rules keep precedence: R10-COP-GATE with only a `tools/` file stays Learners, and R10-DEEPLINK-CENSUS with `kind: rca` stays Product UX. All 7 controls pass at main and at the head.
- On the live plan, no group outside the core lane changes lane. Every moved group in the table below was Core model at main. Learners 8, Product UX 14 and Replay 9 are identical at both ends. An intermediate cut that hoisted the kind rule above the name rules moved R10-DEEPLINK-CENSUS (Product UX) and R10-REPLAY-COST-2 (Replay); that is why the kind rule is the fallback.
- Every group still in the core lane at the head, checked against its roster brief: each open one owns `custom_components/` files (CLONE-2238, COP-GATE-D, HOTFIX-SAV-ESTIMATE, OVERBOOK-RESIDUAL, PARTLOAD-PRICING, SAV-METER-FLOOR, SAV-WOOD-MEASURED, WHY-NOW-WIDGET) or is product or owner work with no files (COMBI-TANK, the combi-tank design; CATALOG-PR, the owner's marketplace step). None is an instrument or CI fix.

## Figures

The live plan was re-measured from the roster at `origin/handoff/audit-r10-roster` (blob `1c9349040114`, re-fetched 2026-11-06T23:39Z), `--start 2026-11-06T22:00:00Z`, with `tools/plan/replan.py` at main (`80016a71f567d936450d8708abcbb79d9e8071d7`, run from a worktree of it; `git diff 28482ecee 80016a71f -- tools/plan` is empty) and at the head:
- `python3 tools/plan/replan.py --start 2026-11-06T22:00:00Z --out plan.json`, then `jq '.groups|map_values(.lane)' plan.json`, counting each lane over the plan's 350 groups. Main: Core model 125 (23 open), Instruments 192 (39 open), Docs 2 (1 open), Learners 8, Product UX 14, Replay 9. Head: Core model 62 (10 open), Instruments 250 (50 open), Docs 7 (3 open), Learners 8, Product UX 14, Replay 9.
- Groups whose lane differs between those two plan files: 63, all from Core model (58 to Instruments, 5 to Docs), 13 of them open. The table lists each one.
- The same build's `summary` line, a consequence of the stamp cadence counting production lanes only: stamps 6 at main → 3 at the head; CI 7875.0 → 6975.0 min; batches 64 → 59. `python3 tools/plan/replan.py --check --plan plan.json` prints `PLAN OK` on the head's plan.
- `python3 tools/plan/replan.py --self-test` → `self-test: 0 failed` at the head.
- Scope: `python3 tests/closure.py select --diff 80016a71f567d936450d8708abcbb79d9e8071d7` → `MODE: SCOPED -- 1 script(s) run`, running `tests/entities.py`.

Lanes before and after, for every group that moved (rule: `lane` in main's plan ≠ `lane` in the head's plan):

| group | before (main) | after (head) | state |
|---|---|---|---|
| R10-ARCH-DOCS-FIRST | Core model | Docs | done |
| R10-CARRY-RESIDUE-2 | Core model | Instruments | OPEN |
| R10-CI-RATCHET-RED | Core model | Instruments | done |
| R10-CI-SLIM | Core model | Instruments | done |
| R10-DEEPLINK-HANDLERS | Core model | Instruments | done |
| R10-DEPENDABOT-SETUPTOOLS | Core model | Instruments | done |
| R10-DEPS-ACTIONS-BUMP | Core model | Instruments | done |
| R10-DEPS-PIP-BUMP | Core model | Instruments | done |
| R10-ERREXIT-COUNTERMEASURES | Core model | Instruments | done |
| R10-FLOW-MQ-PROBE | Core model | Instruments | done |
| R10-FLOW-YIELD-PROBE | Core model | Instruments | done |
| R10-FLY-ARCHSCORE-STMT-PACKING | Core model | Instruments | done |
| R10-FLY-BEAT-FETCH-RACE | Core model | Instruments | done |
| R10-FLY-CIPREDICT-GAPS | Core model | Instruments | done |
| R10-FLY-NIGHTLY-HB | Core model | Instruments | done |
| R10-FLY-RELAY-HOLD | Core model | Instruments | done |
| R10-FRICTION-CLAIM-FALSE | Core model | Instruments | done |
| R10-FRICTION-FIXER-MD | Core model | Instruments | done |
| R10-FRICTION-GATE-SCOPING | Core model | Instruments | done |
| R10-FRICTION-MUTATION-SURVIVOR | Core model | Instruments | done |
| R10-FRICTION-RECORDS | Core model | Instruments | OPEN |
| R10-FRICTION-REGRESSION | Core model | Instruments | done |
| R10-HANDOVER-REFRESH | Core model | Instruments | done |
| R10-HOTFIX-CI-CRITPATH-4 | Core model | Instruments | done |
| R10-HOTFIX-CI-CRITPATH-5 | Core model | Instruments | done |
| R10-HOTFIX-CODEQL-HEADROOM | Core model | Instruments | OPEN |
| R10-HOTFIX-GATE-BUSY-DEFER | Core model | Instruments | OPEN |
| R10-HOTFIX-GATE-STALE-JOBS | Core model | Instruments | OPEN |
| R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT | Core model | Instruments | OPEN |
| R10-HOTFIX-NIGHTLY-STATUS | Core model | Instruments | OPEN |
| R10-HOTFIX-PLAN-LANES | Core model | Instruments | OPEN |
| R10-HOTFIX-RECORD-ATTRIB | Core model | Instruments | done |
| R10-HOTFIX-RELEASE-TAG | Core model | Instruments | done |
| R10-HOTFIX-STAMP-BASE | Core model | Instruments | done |
| R10-HOTFIX-UUTILS-SLEEP | Core model | Instruments | done |
| R10-MACHINERY-RATCHETS | Core model | Instruments | done |
| R10-MARKETPLACE-EXTRAS | Core model | Instruments | done |
| R10-PLAN-ARTIFACT | Core model | Instruments | done |
| R10-PLAN-PRIO | Core model | Instruments | done |
| R10-PLAN-REAL-DURATIONS | Core model | Instruments | done |
| R10-PROCESS-SLIM | Core model | Instruments | OPEN |
| R10-RCA-CI-CRITPATH-3 | Core model | Instruments | done |
| R10-RCA-CODESCAN-WAIT | Core model | Instruments | done |
| R10-RCA-FRICTION-RESIDUE | Core model | Instruments | done |
| R10-RCA-HANDOFF-SLIP | Core model | Instruments | done |
| R10-RCA-INSTALL-RATELIMIT | Core model | Instruments | done |
| R10-RCA-NIGHTLY-PYSPY | Core model | Instruments | done |
| R10-RCA-ORCH-CONTINUITY | Core model | Instruments | done |
| R10-RCA-PROCESS-WORKER-HANG | Core model | Instruments | OPEN |
| R10-RCA-RATELIMIT-RECUR | Core model | Instruments | done |
| R10-RCA-RELEASE-TAG | Core model | Instruments | done |
| R10-RCA-SAV-ESTIMATE | Core model | Instruments | OPEN |
| R10-RCA-STRUCTURE-BLIND | Core model | Instruments | done |
| R10-README-GRAPHICS | Core model | Docs | done |
| R10-RECORD-API-O1 | Core model | Instruments | done |
| R10-REVIEW-CARRY | Core model | Instruments | done |
| R10-ROSTER-BATCH24 | Core model | Instruments | done |
| R10-ROUND-PLAYBOOK | Core model | Docs | OPEN |
| R10-TRIAGE-B36 | Core model | Instruments | done |
| R10-TRIAGE-B37 | Core model | Instruments | done |
| R10-TRIAGE-S6 | Core model | Instruments | done |
| R10-USER-DOCS-FINAL | Core model | Docs | done |
| R10-USER-DOCS-VERIFY | Core model | Docs | OPEN |

Core model at the head (rule: `lane == "Core model"` in the head's plan): R10-ARCH-SHAPES, R10-ARCH-SHAPES-CLASSIFIER, R10-BUFFER-STORE, R10-CARD-VOICE, R10-CATALOG-PR (open), R10-CEILING-PROBE, R10-CLONE-2238 (open), R10-COMBI-TANK (open), R10-CONFIG-NOTICES, R10-COP-GATE-D (open), R10-COP-PARTLOAD, R10-CURRENCY, R10-DEAD-RATE-LIMIT, R10-DEMAND-OVERBOOK, R10-DIAG-AGES, R10-DIAG-REDACT, R10-FACTORY-RESET, R10-FAHRENHEIT, R10-FEEDS, R10-FREQ-DEFROST, R10-GRADE-DRIVERS, R10-HOTFIX-AWAY-LIVE, R10-HOTFIX-AWAY-PRESENCE, R10-HOTFIX-AWAY-SETBACK, R10-HOTFIX-LEARNER-INPUTS, R10-HOTFIX-PREHEAT-LABEL, R10-HOTFIX-SAV-ESTIMATE (open), R10-HOUSE-GRADE, R10-IMMERSION-LATCH, R10-INPUT-STALENESS, R10-LEAF-IMPORTS, R10-LEARNED-STORE-LOAD, R10-LEARNER-DEFAULT, R10-LEGIONELLA-COMPLETION, R10-LIVESTATE, R10-LOOP-CPU, R10-MARKETPLACE, R10-N-LOG-FLOOD, R10-NIGHTLY-SLOW-ROLLING, R10-OVERBOOK-RESIDUAL (open), R10-PARAMS-OWNER, R10-PARTLOAD-PRICING (open), R10-PROD-RESIDUE-PINS, R10-PUMP-MODEL, R10-RCA-HEADMOVED, R10-REGISTRY-LEAK, R10-ROSTER-PUSH-RACE, R10-SAV-METER-FLOOR (open), R10-SAV-WOOD-MEASURED (open), R10-SAVINGS-NEGATIVE, R10-SENSOR-PAYLOAD, R10-SERVICES-GUARD, R10-SETPOINT-BOOST, R10-SETPOINT-POWER, R10-SOLVER, R10-STORE, R10-STORE-RACES, R10-TARIFF, R10-THERMAL-POWER-OPTION, R10-TWO-ZONE-HHL, R10-WHY-NOW-WIDGET (open), R10-WOOD-NOTIFY.

Done groups left in the core lane that may be instrument work, because the roster records neither a file nor a tool-landing kind for them: R10-RCA-HEADMOVED (`kind: study`), R10-ROSTER-PUSH-RACE (`kind: defect`, `lane: tooling`) and R10-NIGHTLY-SLOW-ROLLING (`kind: production`, `class: hotfix`). The classifier cannot place a group the roster describes as production, so the remedy is the roster's data, not another name rule. All three are done, so the open plan is unaffected.

## Red checks

none

## Forward-carry

none

## Friction

none
