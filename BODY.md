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

`c7c5cef52a49bed59ee4c8a42e495ef2dae30db5` is this PR's head, and every figure below was re-taken at it (worktree of the head, 2026-11-07). Its code is the handoff code head `aa5c0505b73c77d1ab5a650af2da58759b8b307a` (`8ff3432a965df930fb54e7aa6ffd52bf210e5f3f`, the reviewed head, plus a merge of origin/main at `f2a015142714383722bf49d7ab20d8398ec9674c` and one commit that adds the self-test cases): `git diff aa5c0505 c7c5cef5 -- tools dev tests` is empty and `replan.py` is byte-identical between them. The three-dot diff against the merge base `f2a015142` touches `tools/plan/replan.py` and `dev/programme/delivery/3265.md` only. `git diff 80016a71f f2a015142 -- tools/plan` is empty, so the main merge reaches nothing `replan.py` reads. origin/main is now `b4ec2f332fe3ab8dcf169bd3066276d3bb8848ab`; the head has not merged it, and the merge base is unchanged. `tools/pr/prepr.sh` ran clean (rc=0) at `aa5c0505`, whose tools are identical to the head's. This body re-take changed no code and pushed nothing to `fix/` or `handoff/`.

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

Result: 12 of 12 killed, and the unmutated copy exits rc=0. These runs were made at `aa5c0505`; `replan.py` is byte-identical at `c7c5cef5`, so they stand for the head. The unmutated self-test re-run at `c7c5cef5` prints `self-test: 0 failed`.

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
- m8 has no live effect today. Rule: `roster_lane(g) != roster_lane({**g, "hot_files": []})` over every live roster group (364 at roster blob `1477cf7acb05`). It returns 0 groups. Had m8's arm mattered live, that rule would list the group. So round 2 pins the arm, and it does not change the plan.

## Figures

All live figures below are from the roster at `origin/handoff/audit-r10-roster`: commit `087aab43b137e909333e01913fb1437383f0b6da`, roster blob `1477cf7acb05` (`wave-r10-groups.json`), re-read 2026-11-07. Each run used `--start 2026-11-06T22:00:00Z --roster-ref origin/handoff/audit-r10-roster`, with `tools/plan/replan.py` at main `b4ec2f332` (a worktree of it) and at the head `c7c5cef5` (a worktree of it). These figures are a function of the roster ref, not of main's tip; the roster has grown since the earlier body (351 groups, blob `e7207ea34c7f`).
- `python3 tools/plan/replan.py ... --out plan.json`, then `jq -r '[.groups[]|.lane]|group_by(.)|map("\(.[0]) \(length)")'`, over 364 groups at each end:
  - main: Core model 135, Instruments 196, Docs 2, Learners 8, Product UX 14, Replay 9;
  - head: Core model 65, Instruments 260, Docs 8, Learners 8, Product UX 14, Replay 9.
- The same count over open groups (`select(.done|not)`):
  - main: Core model 28, Instruments 29, Docs 1, Product UX 2, Replay 1;
  - head: Core model 12, Instruments 55, Docs 4, Product UX 2, Replay 1.
- Groups whose `lane` differs between the two plan files: 70. All moved from Core model: 64 to Instruments and 6 to Docs. 17 of them are open (`jq` over the two files, rule: `lane` in main's plan differs from `lane` in the head's). The table lists each one. Learners, Product UX and Replay are identical at both ends.
- The build's `summary` line: stamps 7 at main, 3 at the head; CI 7200.0 min at main, 7762.5 min at the head; batches 57 at main, 66 at the head. Not every count moves the way the stamp cadence alone suggests: the head's plan also reads each group's `done` flag from the same roster, and the two plans do not agree on how many groups are done (303 at main, 290 at the head), so I do not claim a direction for CI minutes or batches here. The wall-clock closure is the same at both ends (`2026-11-13T03:02:00Z`, 149.03 h). `python3 tools/plan/replan.py --check --plan plan.json` prints `PLAN OK` on the head's plan.
- `python3 -I tools/plan/replan.py --self-test` → `self-test: 0 failed` at the head.
- Scope: `python3 tests/closure.py select --diff f2a015142714383722bf49d7ab20d8398ec9674c` at the head → `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, running `tests/entities.py`. `PYTHONPATH=tests/hastub python3 tests/entities.py` exits 0 at the head. `python3 tests/structure.py`, `python3 tests/env_drift.py --claims-only f2a015142`, `python3 tests/closure.py selftest`, `python3 tests/layout.py` and `python3 tests/harness_headers.py` (the last with `PYTHONPATH=tests/hastub`) each exit 0 at the head.

The bare-basename seam (the reviewer's follow-up), enumerated by a rule and not by instance: Core-model groups at the head that own no `custom_components/` file (`roster_lane(g) == "Core model"` and no `files` or `hot_files` entry starts with `custom_components/`). There are 7. Each owns no file at all, so none is core because of a bare filename:
- open: R10-CATALOG-PR (`owner-step`, the owner's marketplace step) and R10-COMBI-TANK (`production`, the combi-tank design);
- done: R10-CARD-VOICE (`feature`), R10-STORE-RACES (`production`), R10-RCA-HEADMOVED (`kind: study`), R10-ROSTER-PUSH-RACE (`kind: defect`) and R10-NIGHTLY-SLOW-ROLLING (`kind: production`, `class: hotfix`).

The last three may be instrument work. The roster records neither a file nor a tool-landing kind for them, so the remedy is the roster's data, not another name rule. All three are done.

Lanes before and after, for every group that moved (rule: `lane` in main's plan ≠ `lane` in the head's plan):

| group | before (main) | after (head) | state |
|---|---|---|---|
| R10-ARCH-DOCS-FIRST | Core model | Docs | done |
| R10-CARRY-RESIDUE-2 | Core model | Instruments | OPEN |
| R10-CI-GRADER-BATCH-STUDY | Core model | Instruments | OPEN |
| R10-CI-OWN-DELIVERY-ROW | Core model | Instruments | OPEN |
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
| R10-FRICTION-CI-RED | Core model | Instruments | OPEN |
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
| R10-HOTFIX-GATE-STALE-JOBS | Core model | Instruments | done |
| R10-HOTFIX-NIGHTLY-PIN-THROUGHPUT | Core model | Instruments | OPEN |
| R10-HOTFIX-NIGHTLY-STATUS | Core model | Instruments | done |
| R10-HOTFIX-PLAN-LANES | Core model | Instruments | OPEN |
| R10-HOTFIX-RECORD-ATTRIB | Core model | Instruments | done |
| R10-HOTFIX-RELEASE-TAG | Core model | Instruments | done |
| R10-HOTFIX-SELFTEST-TIMEOUT | Core model | Instruments | OPEN |
| R10-HOTFIX-STAMP-BASE | Core model | Instruments | done |
| R10-HOTFIX-TRAIN-DEFER-WAIT | Core model | Instruments | OPEN |
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
| R10-RCA-GATE-BUSY-DEFER-2 | Core model | Instruments | OPEN |
| R10-RCA-HANDOFF-SLIP | Core model | Instruments | done |
| R10-RCA-INSTALL-RATELIMIT | Core model | Instruments | done |
| R10-RCA-NIGHTLY-PYSPY | Core model | Instruments | done |
| R10-RCA-ORCH-CONTINUITY | Core model | Instruments | done |
| R10-RCA-PROCESS-WORKER-HANG | Core model | Instruments | done |
| R10-RCA-RATELIMIT-RECUR | Core model | Instruments | done |
| R10-RCA-RELEASE-TAG | Core model | Instruments | done |
| R10-RCA-SAV-ESTIMATE | Core model | Instruments | OPEN |
| R10-RCA-STRUCTURE-BLIND | Core model | Instruments | done |
| R10-README-GRAPHICS | Core model | Docs | done |
| R10-RECORD-API-O1 | Core model | Instruments | done |
| R10-REVIEW-CARRY | Core model | Instruments | done |
| R10-ROSTER-BATCH24 | Core model | Instruments | done |
| R10-ROUND-PLAYBOOK | Core model | Docs | OPEN |
| R10-ROUND-PLAYBOOK-FINAL | Core model | Docs | OPEN |
| R10-TRIAGE-B36 | Core model | Instruments | done |
| R10-TRIAGE-B37 | Core model | Instruments | done |
| R10-TRIAGE-S6 | Core model | Instruments | done |
| R10-USER-DOCS-FINAL | Core model | Docs | done |
| R10-USER-DOCS-VERIFY | Core model | Docs | OPEN |

Core model at the head (rule: `lane == "Core model"` in the head's plan; 65 groups, open ones marked): R10-ARCH-SHAPES, R10-ARCH-SHAPES-CLASSIFIER, R10-BUFFER-STORE, R10-CARD-VOICE, R10-CATALOG-PR (open), R10-CEILING-PROBE, R10-CLONE-2238 (open), R10-COMBI-TANK (open), R10-CONFIG-NOTICES, R10-COP-GATE-D (open), R10-COP-GATE-E (open), R10-COP-PARTLOAD, R10-CURRENCY, R10-DEAD-RATE-LIMIT, R10-DEMAND-OVERBOOK, R10-DIAG-AGES, R10-DIAG-REDACT, R10-FACTORY-RESET, R10-FAHRENHEIT, R10-FEEDS, R10-FREQ-DEFROST, R10-GRADE-DRIVERS, R10-HOTFIX-AWAY-LIVE, R10-HOTFIX-AWAY-PRESENCE, R10-HOTFIX-AWAY-SETBACK, R10-HOTFIX-COP-UNMEASURED (open), R10-HOTFIX-LEARNER-INPUTS, R10-HOTFIX-PREHEAT-LABEL, R10-HOTFIX-SAV-ESTIMATE (open), R10-HOUSE-GRADE, R10-IMMERSION-LATCH, R10-INPUT-STALENESS, R10-LEAF-IMPORTS, R10-LEARNED-STORE-LOAD, R10-LEARNER-DEFAULT, R10-LEGIONELLA-COMPLETION, R10-LIVESTATE, R10-LOOP-CPU, R10-MARKETPLACE, R10-N-LOG-FLOOD, R10-NIGHTLY-SLOW-ROLLING, R10-OVERBOOK-RESIDUAL, R10-PARAMS-OWNER, R10-PARTLOAD-PRICING (open), R10-PARTLOAD-RESIDUE (open), R10-PROD-RESIDUE-PINS, R10-PUMP-MODEL, R10-RCA-HEADMOVED, R10-REGISTRY-LEAK, R10-ROSTER-PUSH-RACE, R10-SAV-METER-FLOOR (open), R10-SAV-WOOD-MEASURED (open), R10-SAVINGS-NEGATIVE, R10-SENSOR-PAYLOAD, R10-SERVICES-GUARD, R10-SETPOINT-BOOST, R10-SETPOINT-POWER, R10-SOLVER, R10-STORE, R10-STORE-RACES, R10-TARIFF, R10-THERMAL-POWER-OPTION, R10-TWO-ZONE-HHL, R10-WHY-NOW-WIDGET (open), R10-WOOD-NOTIFY.

## Red checks

Read at the PR head `c7c5cef52a49bed59ee4c8a42e495ef2dae30db5`: `pull_request_read get_check_runs` (filter=all) returned total_count 81, and all 81 came back on one page (perPage 100). Two concluded red there. Both are CI-infrastructure and neither is caused by this diff, which touches only `tools/plan/replan.py` and a delivery record.
- `gate` (job 128414893032, run 42332777827, an edit run): `failure`. This is the mutual edit-run deferral of the open R10-HOTFIX-GATE-BUSY-DEFER: two edit-run gate jobs at one head each defer to the other, with "FAIL run(s) … at this head are still being judged; their gate decides". Class: CI-infrastructure. Answer: the deciding gate is the code run's own. Run 42332778588's `gate` job 128414239376 concluded `success` at this head, and so did the later edit runs' gate jobs 128435874395 (run 42333388705) and 128295636172 (run 42336664899). The red one is a deferral to a gate that passed, not a verdict on the diff, and the owner is R10-HOTFIX-GATE-BUSY-DEFER. Nothing is owed in this PR.
- `governance / instrument-self-tests` (job 128407091022, run 42332778588): `cancelled`, not `failure`. Its recorded start and completion are 30 minutes apart (12:44:02Z to 13:14:07Z as the check-run read reports them), the job's 30-minute timeout. Class: CI-infrastructure, the timeout of the instrument self-tests, not an assertion in this diff. Answer: the diff changes no script that job runs. The owner is the open R10-HOTFIX-SELFTEST-TIMEOUT (#3245's R10-PROCESS-SLIM also cures it). Nothing is owed here.

An earlier version of this section named job ids 128283313187, 128283535088 and 128291152776/128291256420/128291967008. None of them is among the 81 check runs the head lists now, so they are dropped.

Every other check run at `c7c5cef5` is `success` or `skipped`, including the other `gate` jobs, `pr-contract / pr-contract`, `budget-raise-gate / budget-raise-gate`, `arch-score / arch-score` and the `tests / …` jobs.

## Forward-carry

none

## Friction

none
