R10-ORCH-PLANPAGE, concern C of the R10-ORCH-MACHINERY re-cut. The plan page (`tools/audit/seat/plan_page.py`, landed by R10-PLAN-ARTIFACT #2558) gets three changes. `state_docs.py` now drives and publishes it. It fails to an explicit UNAVAILABLE page instead of writing nothing. And it carries the scratch generator's five defects as mutation-pinned self-test fixtures.

Refs #2505. It does not close it: three of the group's carries remain residual and are listed under `## Forward-carry`.

What changed:

- **UNAVAILABLE page** (`plan_page.py`, `unavailable_page`, `_refuse`). Each refusal used to exit 1 and write nothing. A refusal is a stale plan, a plan `check_plan` refuses, a plan with no duration model, or an `origin/` roster ref that cannot be fetched. Each one now writes `<h1>PLAN UNAVAILABLE — <what could not be read></h1>` to `--html`, with every figure a dash and no table, and still exits 1. This is design 6.7 "How it fails", and carry 15 item 3 ("an UNAVAILABLE page in place of no page").
- **Driven by `state_docs.py`** (`--plan PLAN_JSON [--github-snapshot FILE]`, `draw_plan_page`). The page becomes `PLAN.html` in the same commit as `PLAN-TABLE.md` at `handoff/audit-r<N>-plan`, and is mirrored with the other docs. When the page refuses:
  - if the state ref already holds a `PLAN.html`, that last good page is kept (it carries its own snapshot time);
  - if it holds none, the UNAVAILABLE page is published.
  
  Either way the other docs are pushed and the call exits 1. Without `--plan` the write set is unchanged. The beat runs no replan, so it never passes `--plan`. The sweep's record beat (`sweep_template.md` (4b)) now runs the replan and then `state_docs.py ... --plan`, instead of running `plan_page.py` by hand. Its pinned fragment is in `sweep_render.py` `DEFAULTS`.
- **Five defect fixtures** (orch-machinery DESIGN.md S8 and 6.7, read at the approved design 09174d94e). The `.bak` files are out of tree. The pre-fix shapes are taken from the design's quotations of them (`gen.py.bak:4,148,89`) and from the live override shape it records. Each defect is one named self-test arm, plus one mutant in `dev/audit/harnesses/r10_plan_page_mutants.py` that restores the shape:
  1. hardcoded override: every row's status is the roster's own stage;
  2. scratch graph: the blockers are the roster's `after`, and the fixture scratch graph differs from it;
  3. count from the wrong set: the open-issue count is the open set less #201, where `len(ISS) - 1` reads 3 on the fixture;
  4. commit prefix as PR: no cell renders `#<sha8>`;
  5. two statuses: an `absorbed` group is not rendered done or delivered.
- **Defect 5 needed a production change.** A group whose stage is in `roster_lib.DISPOSITION` used to fall through to `ready` or `blocked`. It is now its own class, `held`, in the label, pill, bar, strip, legend and filter. An absorbed group's label names its `absorbed_into` group, read at group level (the field R10-ROSTER-OPS owns; no roster carries it yet). Status is display state read from the roster, as `done` already is. The bars stay the plan's.
- **Self-test robustness.** The fixture arms run inside one `try`. A mutant that crashes the renderer mid-arm now reports `the fixture arms ran to the end` along with the checks that failed before the crash. Without this, the defect-1 mutant was scored `CRASHED`, not killed.

The diff stat (487+/203-) is inflated: the `try` re-indents the self-test body, about 190 lines, without changing it.

Alternatives considered:
- Leave a refused page as "nothing written" and let `state_docs.py` keep the old file. It lost because the first run would publish no page at all, which is the case 6.7 forbids, and a direct caller would see nothing at `--html`.
- Map disposition stages to `ready` with a label. It lost because that is defect 5 in a new form: the text says one status and the class says another.
- Have `state_docs.py` run `replan.py` itself. It lost because replan takes owner-set `--slots`/`--seats` from the sweep. The plan stays the caller's input, and the page refuses one that is stale.

Each of the roster row's nine carries, by its index in the row (the brief's numbers 13, 15, 39 and 40 are the old R10-ORCH-MACHINERY group's numbering):

- Carry 1 (STUDY K17; this group's part is 6): the page work extends `plan_page.py` and does not build a second page. The UNAVAILABLE page and the five mutation fixtures are kept. Rendering the flow section from the same model is residual, under `## Forward-carry`.
- Carry 2 (from #2558): its precondition was re-measured at this merge base: 51 checks, 0 failed (`## Null control`). No shared builder with `plan_table.py` is built, because that premise is withdrawn. The out-of-tree `gen.py`/`tpl.html` retirement is the orchestrator's (`## Forward-carry`).
- Carry 3 (item 3's premise): what it left for this stage is done here: driving the page from `state_docs.py`, the UNAVAILABLE page in place of no page, and the five generator-defect fixtures.
- Carry 4 (`gen.py`/`tpl.html` retired once this merges): it has the same precondition, re-measured. The retirement itself happens out of tree, by design 8's N4 rule (`## Forward-carry`).
- Carry 5 (the orchestrator.md line): the line is absent at the merge base, so nothing is edited (`## Forward-carry`). No standing seat's work moves into the orchestrator's turns: the page is drawn by the same `state_docs.py` call the record beat already runs.
- Carry 6 (seam note: the Projected open issues section): kept unchanged. Its self-test arms still pass: `the issues chart is the first section, drawn from the open set`, and `no GitHub state: the chart is omitted with a note`.
- Carry 7 (stamp cadence): residual. The count belongs in the replan's stamp planner, which the page then draws (`## Forward-carry`).
- Carry 8 (the flow board is not a section of the page): still not met. It is residual and needs the orchestrator's ruling (`## Forward-carry`).
- Carry 9 (the brief-versus-carry-3 contradiction): this PR again follows the brief. The board stays beside the page through `state_docs.py`, in the same commit.

## Head

59598f9b783bff929b6c32a87bd34cd943b8d85d, one commit (`plan page: pin the crash guard ...`) on the reviewed head 5ad16117fb6668df54b7a31b502a95b31c08b645 (origin/main ca0a6cfbc2e5538e6e2220793831443719ff6e98, merge base d99cadb1235a5e40e250466e656c41c7ce88e641, `date -u` 2026-10-30).

Repair of the blocked verdict (mutation survivor): `state_docs.py` `draw_plan_page`'s crash guard (`if r.returncode != 1 or "PLAN UNAVAILABLE" not in text:`) survived replacement with `if False:`. Without it a `plan_page.py` traceback (rc 1, no page written) was treated as a refusal and published an empty `PLAN.html` at exit 1. It is now pinned by one `state_docs.py --self-test` arm, `plan page: a crashing page refuses with rc 2 and publishes no PLAN.html`: a malformed `plan.json` (`{`) driven through `main` with a fresh `--state-ref` must return 2, name `plan_page.py failed rc 1`, and leave no such ref. Its null control is the neighbouring arm `with no page at the ref, the UNAVAILABLE page is published` (a real refusal still returns 1 and publishes the UNAVAILABLE page). The matching mutant `state-crash-guard` is added to `dev/audit/harnesses/r10_plan_page_mutants.py`.

Earlier repair (kept): `tools/plan/durations.json`, `tools/plan/replan.py` and `plan_page.py` are excepted from INERT in `tests/closure.py` and join `tests/entities.py`'s closure, because `state_docs.py --self-test` really reads them.

## Mutation proof

`python3 dev/audit/harnesses/r10_plan_page_mutants.py` at the head. Each mutant is one exact replacement, restored byte for byte. The harness refuses a file with uncommitted edits.

- New mutants, each killed with its FAIL lines:
  - `defect-1-hardcoded-override` (6 fails, among them `defect 1: every row's status is the roster's own stage` and `the fixture arms ran to the end`)
  - `defect-2-scratch-graph` (7, `defect 2: the blockers are the roster's after, never a scratch graph`)
  - `defect-3-count-wrong-set` (1, `defect 3: the open-issue count is the open set less the tracking issue`)
  - `defect-4-sha8-as-pr` (2, `defect 4: ...never #sha8`)
  - `defect-5-absorbed-as-done` (8, `defect 5: an absorbed group is not rendered done or delivered`)
  - `held-label` (2)
  - `unavailable-page-written`: deletes the write in `_refuse` (4, every refusal arm)
  - `unavailable-no-figures` (4)
  - `state-page-published` (1, `plan page: the first --plan call exits 0`)
  - `state-keeps-last-good` (1, `plan page: a stale plan keeps the last good page at the ref, exit 1`)
  - `state-unavailable-where-none` (1, `plan page: with no page at the ref, the UNAVAILABLE page is published`)
  - `state-unread-exits-1` (1)
  - `state-crash-guard` (1, `plan page: a crashing page refuses with rc 2 and publishes no PLAN.html`): red with the guard replaced by `if False:`; restored byte for byte, `M0` is `rc=0 fails=0 verdict=null` and `state_docs.py --self-test` prints `all checks passed`.
- The 19 pre-existing mutants are all still killed.
- Final line: `RESULT survived=0`.
- The harness now also runs the mutated file's own `--self-test`. For a `state_docs.py` mutant that is `state_docs.py --self-test`, whose comma-joined failure line the harness now counts as FAIL lines.

## Null control

- At the merge base: `python3 -I tools/audit/seat/plan_page.py --self-test` prints `51 checks, 0 failed`, and the harness's `M0` prints `rc=0 fails=0 verdict=null`. This is the carry 15/39 precondition, re-measured at this merge base. The brief's 41 at fef4a1351 has since moved to 51.
- The base self-test's own refusal arms pin "nothing written": `refused(...) == (1, False, True)`. That is the defect state 6.7 names. At the head the same arms pin `(1, True, True)` with the UNAVAILABLE page.
- At the head, `M0` is null again, and a page that drew is checked not to be the UNAVAILABLE page.
- In `state_docs.py`, `without --plan the write set holds no PLAN.html`. The pre-existing arms (write set exactly four docs, mirror exactly four files) pass unchanged.

## Figures

- `python3 -I tools/audit/seat/plan_page.py --self-test` → `plan_page self-test: 60 checks, 0 failed` at the head, 51 at the merge base. The rule: one per `check(...)` evaluation.
- `python3 -I tools/audit/seat/state_docs.py --self-test` → `state_docs self-test: all checks passed`.
- `python3 dev/audit/harnesses/r10_plan_page_mutants.py` → `RESULT survived=0` over its 33 verdict lines (M0 plus 32 mutants; the rule is the count of `RESULT mutant` lines in that run), each with its verdict line.
- Disposition-stage groups in the live roster. The rule is a stage in `roster_lib.DISPOSITION`, counted with `python3 -c "import sys; sys.path.insert(0,'tools/audit/seat'); import roster_lib,json; r=json.load(open('dev/programme/rosters/wave-r10-groups.json')); print(sum(1 for g in r['groups'] if (g.get('resume') or {}).get('stage') in roster_lib.DISPOSITION))"` → 11, all `carries-open`, at the merge base. These rendered `ready`/`blocked` at the base and render `held` at the head. The null control is `jq` over the same five words, which also gives 11.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` → `ALL 2488 ENTITY CHECKS PASSED`.
- `python3 tests/closure.py select --diff 5ad16117fb6668df54b7a31b502a95b31c08b645` (this repair's own delta; `--diff` the merge base reads `MODE: FULL` because the branch changes `tests/closure.py`): `MODE: SCOPED -- 1 script(s) run`, and `scope.run` names `tests/entities.py`. The `run_always` lines passed: `tests/env_drift.py --claims-only` (`claims hygiene: ... ok`), `tests/closure.py selftest` (`ALL 117 closure shrink pins PASSED`), `tests/layout.py` (`layout self-test: ok`) and `tests/harness_headers.py` (`ALL 112 HARNESS HEADER CHECKS PASSED`).
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 507a9ec26` → `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/seat/sweep_render.py --self-test` → `sweep_render self-test: 24 checks, 0 failed`.

- Repair, rule: the INERT-vs-read pair is what `python3 tools/pr/ci_predict.py --only self-test-reads --record-self-tests` prints. Before: 2 PREDICT lines (durations.json, replan.py). After: `bash tools/pr/prepr.sh` → `ci predict ... no closures, fast, wave-script or instrument red predicted` and `PRE-PR: dd93edd4... rc=0` at this head.
- Repair, recording: `tests/derive_closures.sh --single tests/entities.py` exited 1 because the one failing check was `every tracked file is either measured or deliberately classified` naming exactly durations.json and replan.py (all other `FAIL` lines in the log are planted null controls inside passing checks). Recorded with `--record-only --out-dir`, then `closure.py merge --partial --allow-failures` (the tool's documented two-step), which added three files to the closure (plan_page.py, durations.json, replan.py). The recorded `rc` was then restored to 0, because the same script re-run on the merged closure prints `ALL 2488 ENTITY CHECKS PASSED` (null control: the same run before the merge printed `1 of 2488 ENTITY CHECKS FAILED`). The recording was made on Linux in this container, not CI's canonical host; CI re-records `closures`, and `prepr` skips its closures step as unscoped (`tests/closure.py` changed).
- `python3 tests/structure.py` at this head → `STRUCTURE RATCHET PASSED`. `git log --format=%B origin/main..HEAD | grep -ci "claude\|co-authored"` → 0.

## Red checks

none

## Unpinned sites

Every production site this diff adds in `tools/audit/seat/plan_page.py` and `tools/audit/seat/state_docs.py` is pinned by the in-tree mutant harness `dev/audit/harnesses/r10_plan_page_mutants.py`, the site's in-tree mutant harness under `fixer.md` step 2 (the `mutation-autofix` lane mutates `custom_components/` only). The first review found one site unpinned: `draw_plan_page`'s crash guard, which survived `if False:`. It is now pinned by mutant `state-crash-guard`, killed by the `a crashing page refuses with rc 2` arm (1 fail), and the full harness ends `RESULT survived=0`. The mutant names are under `## Mutation proof`.

## Forward-carry`.

What changed:

- **UNAVAILABLE page** (`plan_page.py`, `unavailable_page`, `_refuse`). Each refusal used to exit 1 and write nothing. A refusal is a stale plan, a plan `check_plan` refuses, a plan with no duration model, or an `origin/` roster ref that cannot be fetched. Each one now writes `<h1>PLAN UNAVAILABLE — <what could not be read></h1>` to `--html`, with every figure a dash and no table, and still exits 1. This is design 6.7 "How it fails", and carry 15 item 3 ("an UNAVAILABLE page in place of no page").
- **Driven by `state_docs.py`** (`--plan PLAN_JSON [--github-snapshot FILE]`, `draw_plan_page`). The page becomes `PLAN.html` in the same commit as `PLAN-TABLE.md` at `handoff/audit-r<N>-plan`, and is mirrored with the other docs. When the page refuses:
  - if the state ref already holds a `PLAN.html`, that last good page is kept (it carries its own snapshot time);
  - if it holds none, the UNAVAILABLE page is published.
  
  Either way the other docs are pushed and the call exits 1. Without `--plan` the write set is unchanged. The beat runs no replan, so it never passes `--plan`. The sweep's record beat (`sweep_template.md` (4b)) now runs the replan and then `state_docs.py ... --plan`, instead of running `plan_page.py` by hand. Its pinned fragment is in `sweep_render.py` `DEFAULTS`.
- **Five defect fixtures** (orch-machinery DESIGN.md S8 and 6.7, read at the approved design 09174d94e). The `.bak` files are out of tree. The pre-fix shapes are taken from the design's quotations of them (`gen.py.bak:4,148,89`) and from the live override shape it records. Each defect is one named self-test arm, plus one mutant in `dev/audit/harnesses/r10_plan_page_mutants.py` that restores the shape:
  1. hardcoded override: every row's status is the roster's own stage;
  2. scratch graph: the blockers are the roster's `after`, and the fixture scratch graph differs from it;
  3. count from the wrong set: the open-issue count is the open set less #201, where `len(ISS) - 1` reads 3 on the fixture;
  4. commit prefix as PR: no cell renders `#<sha8>`;
  5. two statuses: an `absorbed` group is not rendered done or delivered.
- **Defect 5 needed a production change.** A group whose stage is in `roster_lib.DISPOSITION` used to fall through to `ready` or `blocked`. It is now its own class, `held`, in the label, pill, bar, strip, legend and filter. An absorbed group's label names its `absorbed_into` group, read at group level (the field R10-ROSTER-OPS owns; no roster carries it yet). Status is display state read from the roster, as `done` already is. The bars stay the plan's.
- **Self-test robustness.** The fixture arms run inside one `try`. A mutant that crashes the renderer mid-arm now reports `the fixture arms ran to the end` along with the checks that failed before the crash. Without this, the defect-1 mutant was scored `CRASHED`, not killed.

The diff stat (487+/203-) is inflated: the `try` re-indents the self-test body, about 190 lines, without changing it.

Alternatives considered:
- Leave a refused page as "nothing written" and let `state_docs.py` keep the old file. It lost because the first run would publish no page at all, which is the case 6.7 forbids, and a direct caller would see nothing at `--html`.
- Map disposition stages to `ready` with a label. It lost because that is defect 5 in a new form: the text says one status and the class says another.
- Have `state_docs.py` run `replan.py` itself. It lost because replan takes owner-set `--slots`/`--seats` from the sweep. The plan stays the caller's input, and the page refuses one that is stale.

Each of the roster row's nine carries, by its index in the row (the brief's numbers 13, 15, 39 and 40 are the old R10-ORCH-MACHINERY group's numbering):

- Carry 1 (STUDY K17; this group's part is 6): the page work extends `plan_page.py` and does not build a second page. The UNAVAILABLE page and the five mutation fixtures are kept. Rendering the flow section from the same model is residual, under `## Forward-carry`.
- Carry 2 (from #2558): its precondition was re-measured at this merge base: 51 checks, 0 failed (`## Null control`). No shared builder with `plan_table.py` is built, because that premise is withdrawn. The out-of-tree `gen.py`/`tpl.html` retirement is the orchestrator's (`## Forward-carry`).
- Carry 3 (item 3's premise): what it left for this stage is done here: driving the page from `state_docs.py`, the UNAVAILABLE page in place of no page, and the five generator-defect fixtures.
- Carry 4 (`gen.py`/`tpl.html` retired once this merges): it has the same precondition, re-measured. The retirement itself happens out of tree, by design 8's N4 rule (`## Forward-carry`).
- Carry 5 (the orchestrator.md line): the line is absent at the merge base, so nothing is edited (`## Forward-carry`). No standing seat's work moves into the orchestrator's turns: the page is drawn by the same `state_docs.py` call the record beat already runs.
- Carry 6 (seam note: the Projected open issues section): kept unchanged. Its self-test arms still pass: `the issues chart is the first section, drawn from the open set`, and `no GitHub state: the chart is omitted with a note`.
- Carry 7 (stamp cadence): residual. The count belongs in the replan's stamp planner, which the page then draws (`## Forward-carry`).
- Carry 8 (the flow board is not a section of the page): still not met. It is residual and needs the orchestrator's ruling (`## Forward-carry`).
- Carry 9 (the brief-versus-carry-3 contradiction): this PR again follows the brief. The board stays beside the page through `state_docs.py`, in the same commit.

## Head

59598f9b783bff929b6c32a87bd34cd943b8d85d, one commit (`plan page: pin the crash guard ...`) on the reviewed head 5ad16117fb6668df54b7a31b502a95b31c08b645 (origin/main ca0a6cfbc2e5538e6e2220793831443719ff6e98, merge base d99cadb1235a5e40e250466e656c41c7ce88e641, `date -u` 2026-10-30).

Repair of the blocked verdict (mutation survivor): `state_docs.py` `draw_plan_page`'s crash guard (`if r.returncode != 1 or "PLAN UNAVAILABLE" not in text:`) survived replacement with `if False:`. Without it a `plan_page.py` traceback (rc 1, no page written) was treated as a refusal and published an empty `PLAN.html` at exit 1. It is now pinned by one `state_docs.py --self-test` arm, `plan page: a crashing page refuses with rc 2 and publishes no PLAN.html`: a malformed `plan.json` (`{`) driven through `main` with a fresh `--state-ref` must return 2, name `plan_page.py failed rc 1`, and leave no such ref. Its null control is the neighbouring arm `with no page at the ref, the UNAVAILABLE page is published` (a real refusal still returns 1 and publishes the UNAVAILABLE page). The matching mutant `state-crash-guard` is added to `dev/audit/harnesses/r10_plan_page_mutants.py`.

Earlier repair (kept): `tools/plan/durations.json`, `tools/plan/replan.py` and `plan_page.py` are excepted from INERT in `tests/closure.py` and join `tests/entities.py`'s closure, because `state_docs.py --self-test` really reads them.

## Mutation proof

`python3 dev/audit/harnesses/r10_plan_page_mutants.py` at the head. Each mutant is one exact replacement, restored byte for byte. The harness refuses a file with uncommitted edits.

- New mutants, each killed with its FAIL lines:
  - `defect-1-hardcoded-override` (6 fails, among them `defect 1: every row's status is the roster's own stage` and `the fixture arms ran to the end`)
  - `defect-2-scratch-graph` (7, `defect 2: the blockers are the roster's after, never a scratch graph`)
  - `defect-3-count-wrong-set` (1, `defect 3: the open-issue count is the open set less the tracking issue`)
  - `defect-4-sha8-as-pr` (2, `defect 4: ...never #sha8`)
  - `defect-5-absorbed-as-done` (8, `defect 5: an absorbed group is not rendered done or delivered`)
  - `held-label` (2)
  - `unavailable-page-written`: deletes the write in `_refuse` (4, every refusal arm)
  - `unavailable-no-figures` (4)
  - `state-page-published` (1, `plan page: the first --plan call exits 0`)
  - `state-keeps-last-good` (1, `plan page: a stale plan keeps the last good page at the ref, exit 1`)
  - `state-unavailable-where-none` (1, `plan page: with no page at the ref, the UNAVAILABLE page is published`)
  - `state-unread-exits-1` (1)
  - `state-crash-guard` (1, `plan page: a crashing page refuses with rc 2 and publishes no PLAN.html`): red with the guard replaced by `if False:`; restored byte for byte, `M0` is `rc=0 fails=0 verdict=null` and `state_docs.py --self-test` prints `all checks passed`.
- The 19 pre-existing mutants are all still killed.
- Final line: `RESULT survived=0`.
- The harness now also runs the mutated file's own `--self-test`. For a `state_docs.py` mutant that is `state_docs.py --self-test`, whose comma-joined failure line the harness now counts as FAIL lines.

## Null control

- At the merge base: `python3 -I tools/audit/seat/plan_page.py --self-test` prints `51 checks, 0 failed`, and the harness's `M0` prints `rc=0 fails=0 verdict=null`. This is the carry 15/39 precondition, re-measured at this merge base. The brief's 41 at fef4a1351 has since moved to 51.
- The base self-test's own refusal arms pin "nothing written": `refused(...) == (1, False, True)`. That is the defect state 6.7 names. At the head the same arms pin `(1, True, True)` with the UNAVAILABLE page.
- At the head, `M0` is null again, and a page that drew is checked not to be the UNAVAILABLE page.
- In `state_docs.py`, `without --plan the write set holds no PLAN.html`. The pre-existing arms (write set exactly four docs, mirror exactly four files) pass unchanged.

## Figures

- `python3 -I tools/audit/seat/plan_page.py --self-test` → `plan_page self-test: 60 checks, 0 failed` at the head, 51 at the merge base. The rule: one per `check(...)` evaluation.
- `python3 -I tools/audit/seat/state_docs.py --self-test` → `state_docs self-test: all checks passed`.
- `python3 dev/audit/harnesses/r10_plan_page_mutants.py` → `RESULT survived=0` over its 33 verdict lines (M0 plus 32 mutants; the rule is the count of `RESULT mutant` lines in that run), each with its verdict line.
- Disposition-stage groups in the live roster. The rule is a stage in `roster_lib.DISPOSITION`, counted with `python3 -c "import sys; sys.path.insert(0,'tools/audit/seat'); import roster_lib,json; r=json.load(open('dev/programme/rosters/wave-r10-groups.json')); print(sum(1 for g in r['groups'] if (g.get('resume') or {}).get('stage') in roster_lib.DISPOSITION))"` → 11, all `carries-open`, at the merge base. These rendered `ready`/`blocked` at the base and render `held` at the head. The null control is `jq` over the same five words, which also gives 11.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` → `ALL 2488 ENTITY CHECKS PASSED`.
- `python3 tests/closure.py select --diff 5ad16117fb6668df54b7a31b502a95b31c08b645` (this repair's own delta; `--diff` the merge base reads `MODE: FULL` because the branch changes `tests/closure.py`): `MODE: SCOPED -- 1 script(s) run`, and `scope.run` names `tests/entities.py`. The `run_always` lines passed: `tests/env_drift.py --claims-only` (`claims hygiene: ... ok`), `tests/closure.py selftest` (`ALL 117 closure shrink pins PASSED`), `tests/layout.py` (`layout self-test: ok`) and `tests/harness_headers.py` (`ALL 112 HARNESS HEADER CHECKS PASSED`).
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff 507a9ec26` → `Architecture score: dS +0.0000 NULL`.
- `python3 -I tools/audit/seat/sweep_render.py --self-test` → `sweep_render self-test: 24 checks, 0 failed`.

- Repair, rule: the INERT-vs-read pair is what `python3 tools/pr/ci_predict.py --only self-test-reads --record-self-tests` prints. Before: 2 PREDICT lines (durations.json, replan.py). After: `bash tools/pr/prepr.sh` → `ci predict ... no closures, fast, wave-script or instrument red predicted` and `PRE-PR: dd93edd4... rc=0` at this head.
- Repair, recording: `tests/derive_closures.sh --single tests/entities.py` exited 1 because the one failing check was `every tracked file is either measured or deliberately classified` naming exactly durations.json and replan.py (all other `FAIL` lines in the log are planted null controls inside passing checks). Recorded with `--record-only --out-dir`, then `closure.py merge --partial --allow-failures` (the tool's documented two-step), which added three files to the closure (plan_page.py, durations.json, replan.py). The recorded `rc` was then restored to 0, because the same script re-run on the merged closure prints `ALL 2488 ENTITY CHECKS PASSED` (null control: the same run before the merge printed `1 of 2488 ENTITY CHECKS FAILED`). The recording was made on Linux in this container, not CI's canonical host; CI re-records `closures`, and `prepr` skips its closures step as unscoped (`tests/closure.py` changed).
- `python3 tests/structure.py` at this head → `STRUCTURE RATCHET PASSED`. `git log --format=%B origin/main..HEAD | grep -ci "claude\|co-authored"` → 0.

## Red checks

none

## Unpinned sites

Every production site this diff adds in `tools/audit/seat/plan_page.py` and `tools/audit/seat/state_docs.py` is pinned by the in-tree mutant harness `dev/audit/harnesses/r10_plan_page_mutants.py`. The `mutation-autofix` lane mutates `custom_components/` only, and this harness is the site's in-tree mutant harness under `fixer.md` step 2. The mutant names are under `## Mutation proof`.

## Forward-carry

- **The replan schedules disposition-stage groups as open work.** `tools/plan/replan.py` `is_done` is `("done", "rca-done")`. The 11 `carries-open` groups at the merge base therefore get a duration and a bar, while the page now names them `held`. Whether a disposition is schedulable is the roster schema's and the planner's call, not the page's: the page draws the plan's bars unchanged. Carry: R10-ORCH-ROSTER-SCHEMA
- **Stamp cadence (carry 7) is not built here.** Planning a stamp after about 3 merged production groups is `replan.py` `build_plan`'s stamp logic (`stamp_every`). The count shown on the page should be a field of the plan JSON replan writes that the page draws, because the page draws and does not plan. Built in the page, it would be a second answer. Carry: R10-ORCH-PLANPAGE (residual: lands with the replan stamp change, then one page row)
- **The flow board as a section of the page (carries 8, 9 and 13(6)) is not built.** The board's model is `merge_throughput.py`'s `board(ctx)`, built from git history. Item (3)'s shared-model premise was withdrawn by carries 15 and 39, so there is no "same model" to render it from. The flow board document stays beside the plan page at the same ref, in the same commit. Carry 9 records the contradiction between the brief and carry 3; it needs the orchestrator's ruling. Carry: R10-ORCH-PLANPAGE (residual, orchestrator decision)
- **The orchestrator.md line (carry 5) is absent at the merge base.** There is no line naming the ledger digest to edit: `grep -n -i -E 'ledger digest|reads only|plan page' dev/governance/roles/orchestrator.md` returns none. The sentence is R10-ORCH-BEATD/R10-ORCH-LEDGER's fold, and R10-ORCH-LEDGER is `carries-open`. Until that sentence lands, this group has nothing to edit. Carry: R10-ORCH-LEDGER
- **Retiring `gen.py`/`tpl.html` (carries 15 and 39)** follows design 8's N4 rule: two consecutive merges to `main` that produce `PLAN.html` at the state ref, observable with `git show`. Both files are out of tree, so the retirement is the orchestrator's. Carry: R10-ORCH-PLANPAGE

## Friction

none
