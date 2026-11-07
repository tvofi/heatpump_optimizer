Owner ruling (tvofi 2026-11-06), verbatim: "The HTML plan seems to incorrectly place some instrument or CI fixes in the core model lane, fix that".

Where the lane is decided: `roster_lane` in `tools/plan/replan.py` writes each group's `lane` into the plan JSON, and `tools/audit/seat/plan_page.py` only draws that field. `roster_lane` placed a group by `kind` (`instrument`, `policy`), then by a list of name prefixes, and **every group neither rule placed fell through to Core model**. So a new CI hotfix, an RCA seat, a tooling chore or a doc group was drawn as core-model work, and the stamp cadence counted it as production.

The fix is at that source, not per group. The kind and name rules keep their precedence, so Learners, Product UX, Replay and Docs placements by name do not change. After them, `roster_lane` reads:
1. **The files the group owns** (`files` + `hot_files`). When every one is an instrument, CI or record path (`tools/`, `tests/`, `.github/`, `.claude/`, `dev/`, `docs/`, or a root record such as `CLAUDE.md`), the group is Instruments. It is Docs instead when it is a `doc` kind, or when it touches user docs (`docs/`, `README.md`) without landing a tool (`tools/`, `.github/`, `.claude/`). A single `custom_components/` file or a bare filename, in either list, keeps it core.
2. **Then a tool-landing kind or roster class**, for a group whose roster names no file: `kind` in `INSTRUMENT_KINDS` (`instrument`, `policy`, `rca`, `tooling`) or `class: instrument`. `work_class` already priced those kinds as instruments. It now reads the same tuple, so the lane and the duration class cannot disagree on which kinds land tools.

Alternatives considered:
- (a) Reading the roster's own `lane` code. It is not a lane in this sense: production groups owning only `custom_components/` files carry `lane: IN`. So it lost.
- (b) Adding the misplaced names to the prefix list. That is a per-group spelling list, and the next CI hotfix would fall out of it again (fixer.md step 17). So it lost too.

**Round 2 (this repair).** The review blocked at `8ff3432a` as mutation-vacuous. Dropping `hot_files` from `_owned_lane` (m8) survived the self-test, because every control put the bare filename or the `custom_components/` path in `files`. The production code is unchanged in this round. The self-test gains four `hot_files` cases on a group with `files: ["tools/x.py"]`:
- an integration hot file (`custom_components/heatpump_optimizer/x.py`) stays Core model;
- a bare `coordinator.py` hot file stays Core model;
- a bare tool basename (`merge_train.py`) in `hot_files` stays Core model, which is the conservatism the brief's rule (1) prescribes and the reviewer's follow-up asked to pin;
- an instrument-path hot file (`.github/workflows/ci.yml`) keeps it Instruments.

m8 is now killed by three of them. I re-ran all twelve of the reviewer's mutants myself, and all are killed.

## Head

`aa5c0505b73c77d1ab5a650af2da58759b8b307a` is the handoff code head, and every figure below was measured at it. It is `8ff3432a965df930fb54e7aa6ffd52bf210e5f3f` (the reviewed head), plus a merge of origin/main at `f2a015142714383722bf49d7ab20d8398ec9674c` (merge commit `ab8da132a`), plus one commit that adds the self-test cases. The three-dot diff against the merge base `f2a015142` touches `tools/plan/replan.py` and `dev/programme/delivery/3265.md` only. `git diff 80016a71f f2a015142 -- tools/plan` is empty, so the main merge reaches nothing `replan.py` reads.

## Mutation proof

Method: for each mutant, take a `git archive` copy of the head, apply one exact string substitution to `tools/plan/replan.py` (it must match once), and run `python3 -I tools/plan/replan.py --self-test`. The unmutated copy (m0) exits rc=0 with no lane failure. The FAIL lines are the self-test's own check names.
- m1, delete `if owned := _owned_lane(group): return owned` → rc=1: `lane: a CI-only group is Instruments`, `lane: a tests-and-tools group is Instruments`, `lane: a docs-only doc group is Docs`, `lane: a user-docs group is Docs`, `lane null control: docs plus a tool is Instruments, not Docs`, `lane: user docs with a dev harness are Docs`, `lane: an instrument-path hot file keeps a tool group Instruments`
- m2, delete the `INSTRUMENT_KINDS`/`class` fallback → rc=1: `lane: an RCA group with no files is Instruments`, `lane: a tooling group with no files is Instruments`, `lane: a roster class instrument with no files is Instruments`
- m3, drop the `class == "instrument"` arm → rc=1: `lane: a roster class instrument with no files is Instruments`
- m4, `not all(` → `not any(` → rc=1: `lane null control: a mixed group stays Core model`, `lane null control: an integration hot file keeps a tool group Core model`, `lane null control: a bare hot filename keeps a tool group Core model`, `lane null control: a bare tool basename in hot_files stays Core model`
- m5, drop the `not files` guard → rc=1: `lane null control: a group with no files stays Core model`, `lane null control: a production group with no files stays Core model`
- m6, drop the tooling exclusion from `user_docs` → rc=1: `lane null control: docs plus a tool is Instruments, not Docs`
- m7, drop the `kind == "doc"` arm → rc=1: `lane: a docs-only doc group is Docs`
- **m8, drop `+ list(group.get("hot_files") or [])` → rc=1**: `lane null control: an integration hot file keeps a tool group Core model`, `lane null control: a bare hot filename keeps a tool group Core model`, `lane null control: a bare tool basename in hot_files stays Core model`. At the reviewed head `8ff3432a`, the same m8 substitution exits rc=0 with no lane failure. That is the block, reproduced, and it is the failing-test-first for this round.
- m9, remove `docs/` from `_NON_PRODUCT_PREFIXES` → rc=1: `lane: a user-docs group is Docs`, `lane null control: docs plus a tool is Instruments, not Docs`, `lane: user docs with a dev harness are Docs`
- m10, empty `_NON_PRODUCT_FILES` → rc=1: `lane: a docs-only doc group is Docs`, `lane: a user-docs group is Docs`, `lane: user docs with a dev harness are Docs`
- m11, remove `rca` from `INSTRUMENT_KINDS` → rc=1: `lane: an RCA group with no files is Instruments`
- m12, `user_docs = True or (...)` → rc=1: `lane: a CI-only group is Instruments`, `lane: a tests-and-tools group is Instruments`, `lane null control: docs plus a tool is Instruments, not Docs`, `lane: an instrument-path hot file keeps a tool group Instruments`

Result: 12 of 12 killed at `aa5c0505`, and the unmutated copy exits rc=0.

## Null control

- A real core-model group stays core. These controls all pass at the head:
  - a `custom_components/heatpump_optimizer/optimizer.py` group;
  - a mixed tools + `custom_components/` group;
  - a file-less group;
  - a bare `coordinator.py` in `files`;
  - a file-less `kind: production, class: production` group;
  - and, new this round, a tool group whose `hot_files` holds an integration path, a bare `coordinator.py` or a bare `merge_train.py`.
- Name rules keep precedence: R10-COP-GATE with only a `tools/` file stays Learners, and R10-DEEPLINK-CENSUS with `kind: rca` stays Product UX.
- The new Instruments case is the positive control for the three new Core-model cases. It shows that `hot_files` is read both ways, not only as a veto.
- On the live plan, no group outside the core lane changes lane. Learners 8, Product UX 14 and Replay 9 are identical at both ends. Every moved group was Core model at main.
- m8 has no live effect today. Rule: `roster_lane(g) != roster_lane({**g, "hot_files": []})` over every live roster group. It returns 0 groups. Had m8's arm mattered live, that rule would list the group. So round 2 pins the arm, and it does not change the plan.

## Figures

All live figures below are from the roster at `origin/handoff/audit-r10-roster`: commit `cab343ebe891836ff776defccab9cb8ae9a9cbc7`, roster blob `e7207ea34c7f`, fetched 2026-11-07T02:12Z. Each run used `--start 2026-11-06T22:00:00Z`, with `tools/plan/replan.py` at main `f2a015142` (a worktree of it) and at the head. These figures are a function of the roster ref, not of main's tip.
- `python3 tools/plan/replan.py --start 2026-11-06T22:00:00Z --out plan.json`, then `jq -r '[.groups[]|.lane]|group_by(.)|map("\(.[0]) \(length)")'`, over 351 groups at each end:
  - main: Core model 126, Instruments 192, Docs 2, Learners 8, Product UX 14, Replay 9;
  - head: Core model 62, Instruments 251, Docs 7, Learners 8, Product UX 14, Replay 9.
- The same count over open groups (`select(.done|not)`):
  - main: Core model 24, Instruments 39, Docs 1, Product UX 2, Replay 1;
  - head: Core model 10, Instruments 51, Docs 3, Product UX 2, Replay 1.
- Groups whose `lane` differs between the two plan files: 64. All moved from Core model: 59 to Instruments and 5 to Docs. 14 of them are open. The table lists each one.
- The build's `summary` line, which follows from the stamp cadence counting production lanes only: stamps 6 at main → 3 at the head; CI 7537.5 → 6300.0 min; batches 61 → 53. `python3 tools/plan/replan.py --check --plan plan.json` prints `PLAN OK` on the head's plan.
- `python3 -I tools/plan/replan.py --self-test` → `self-test: 0 failed` at the head.
- Scope: `python3 tests/closure.py select --diff f2a015142714383722bf49d7ab20d8398ec9674c` → `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, running `tests/entities.py`. ENTITIES_LINE
- `python3 tests/structure.py` rc=0. These run_always scripts each exit 0: `python3 tests/env_drift.py --claims-only f2a015142`, `python3 tests/closure.py selftest`, `python3 tests/layout.py` and `python3 tests/harness_headers.py` (the last with `PYTHONPATH=tests/hastub`).

The bare-basename seam (the reviewer's follow-up), enumerated by a rule and not by instance: Core-model groups at the head that own no `custom_components/` file (`roster_lane(g) == "Core model"` and no owned path starts with `custom_components/`). There are 7. Each owns no file at all, so none is core because of a bare filename:
- open: R10-CATALOG-PR (`owner-step`, the owner's marketplace step) and R10-COMBI-TANK (`production`, the combi-tank design);
- done: R10-CARD-VOICE (`feature`), R10-STORE-RACES (`production`), R10-RCA-HEADMOVED (`kind: study`), R10-ROSTER-PUSH-RACE (`kind: defect`) and R10-NIGHTLY-SLOW-ROLLING (`kind: production`, `class: hotfix`).

The last three may be instrument work. The roster records neither a file nor a tool-landing kind for them, so the remedy is the roster's data, not another name rule. All three are done.

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
| R10-HOTFIX-SELFTEST-TIMEOUT | Core model | Instruments | OPEN |
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

## Red checks

At the reviewed head `8ff3432a`, all 68 check runs were read across every page (`commits/8ff3432a…/check-runs?per_page=100`, pages 1–3). Exactly two are red, and both are `gate`:
- `gate` (run 42317750046, the edit run): failure. Class: CI-infrastructure, not this diff. Its log reads "FAIL run(s) [42318557432] at this head are still being judged; their gate decides".
- `gate` (run 42318557432, the edit run): failure. Same class. Its log reads "FAIL run(s) [42317750046] at this head are still being judged; their gate decides".

Answer: this is the mutual edit-run deferral of the open R10-HOTFIX-GATE-BUSY-DEFER. Each edit run defers to the other, and the code run decides. Code run 42317750091's `gate` concluded `success` (job 128244970569, 2026-11-07T00:53:42Z). The cheaper detector is that group's own fix, so nothing is owed here.

At the final handoff head `aa5c0505`, no check run exists yet. CI runs on the pull-request head after the orchestrator moves it. Any red there is the next round's to answer by name.

## Forward-carry

none

## Friction

none
