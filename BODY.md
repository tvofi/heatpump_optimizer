# R10-CI-LAYOUT-P2 U3: codeql (Part of #2495)

Head: 0f7f26089, based on origin/main fef4a1351 (contains P2a a1633381a).

## Unit
U3. Files: `.github/workflows/codeql.yml`, `tools/pr/codeql_scope.py` (new `extracted` subcommand + 13 self-test checks), `tests/entities.py` (the codeql.yml pins only; the old "accepts the autofix jobs' dispatch" pin contradicts the removal, so it becomes a callee-shape pin, plus a D-5 step pin and a no-scope/no-cancel-superseded pin).
`git diff --stat origin/main...HEAD`: codeql.yml 168 (+~55/-~115), entities.py 42, codeql_scope.py 77; 3 files, 155 insertions, 132 deletions. No new files, so no `tests/closure.py` line.

## Interface
Consumes the P2a prelude's `legs` output (`tools/ci/prelude.py`, JSON `{"actions":"skip|analyze","javascript-typescript":...,"python":...}`). Main's prelude prints `legs=`, not the design sketch's `codeql_<leg>` outputs, so the input is that one string.
Caller block for U0c / coordinator (job id = file stem, so checks read `codeql / Analyze (<leg>)`):
```yaml
  codeql:
    needs: prelude
    if: needs.prelude.outputs.kind == 'code'
    uses: ./.github/workflows/codeql.yml
    with: { legs: "${{ needs.prelude.outputs.legs }}" }
    permissions: { contents: read, security-events: write }
```
Callee: `on: workflow_call` (input `legs`, string, default empty) + the weekly `schedule` (empty legs analyzes every leg). Single job `analyze`, name `Analyze (${{ matrix.language }})`, `timeout-minutes: 45` unchanged, top-level floor `contents: read, security-events: write` unchanged. Removed: `scope`, `cancel-superseded`, `workflow_dispatch`, push/pull_request/merge_group triggers, `concurrency`.
A leg skips only on an explicit `skip` (`fromJSON(inputs.legs || '{}')[matrix.language] != 'skip'`); malformed JSON fails the job (red, not skip).
D-5: new last step "Check the extracted files against the INERT list (D-5)", `if: github.event_name == 'push'`, runs `python3 -I tools/pr/codeql_scope.py extracted --language $LEG --archive $RUNNER_TEMP/codeql_databases/${LEG%%-*}/src.zip`; rc 1 on any archive entry whose suffix is on the leg's INERT list, rc 2 on a missing/corrupt/empty archive (fails closed).

## Static map
Command (unitcheck2.py from 1371a0a6, before = main's codeql.yml, after = mine + a stand-in prelude job holding the decide step, because main's ci.yml is still the stub; the coordinator re-runs with the real ci.yml and must rename `prelude|Decide the codeql legs` in the map's `gained` list to the real step name):
`python3 -I measure/rev/unitcheck2.py static before.yml after.yml+prelude_stub.yml --map map.json`
Output: `STATIC rows 8->12 lost 0 gained 0 changed 6 (mapped 6) misplaced 0 rc 0`, rc 0.
Map: dropped `scope|`, `scope|order`, scope's two steps, `cancel-superseded|`, `|order`, its two steps; rename `analyze|Say what scope decided for this leg` -> `...the prelude decided...`; gained `prelude|`, `prelude|order`, `prelude|Decide the codeql legs`, `analyze|Check the extracted files against the INERT list (D-5)` placed after `analyze|Perform CodeQL Analysis`; changed `analyze|`, the four analyze steps' `if`/env, `|triggers`. `|floor` unchanged (not listed).
Files: /tmp/claude-0/-home-user-heatpump-optimizer/4c89dadc-7a12-5604-b9a0-731be59900f8/scratchpad/u3/{map.json,static.txt,prelude_stub.yml}.

## Controls
- Plant, map without `scope|` in `dropped`: `LOST scope|` ... rc 1. Plant, without `cancel-superseded|`: `LOST cancel-superseded|` rc 1. Null: the full map, rc 0.
- D-5 plant: `python3 -I tools/pr/codeql_scope.py --self-test` -> `ok D-5 plant: .py joining python's INERT list fails the check` (a copy of INERT with `.py` added to python yields `['src/a.py','src/b.py']`); null `ok D-5: a python archive of extractable files is sound`; real-tree INERT passes. Self-test: `59 checks, 0 failed`.
- Mutation proof: replacing the predicate `in inert[language]` with `False` -> 4 FAIL (plant, json, upper-case suffix, `main ... exits 1`), `59 checks, 4 failed`; restored -> 0 failed.
- Entities D-5 step pin (evaluated on planted YAML): real True; `if` changed to pull_request False; extracted call removed False.
- Hygiene: `tmp_paths --check` 0 refused; `throwaway_git --check` 0 refused; `selftest_wiring --check` `87 self-testing, 87 wired, 0 unwired`; `tests/structure.py` STRUCTURE RATCHET PASSED. `codeql_scope --self-test` is already wired in governance.yml.
- Scoped gate: `MODE: SCOPED -- 2 script(s) run` (entities.py, harness_headers.py). harness_headers rc 0 (PYTHONPATH=tests/hastub). entities.py: 3 of 2401 FAIL, all cut-over consequences owned by other units, see Wiring. Python 3.13 venv used (3.11 default cannot parse entities.py).

## Live checks owed
Design §10 U3: dispatch pair, `codeql.yml` dispatched at base (BEFORE; main still has workflow_dispatch) against `ci.yml` dispatched on `ci-probe/codeql` (AFTER); compare the three `Analyze` legs' executed steps and permissions with `unitcheck2.py runtime`. Additionally owed: that the D-5 step finds `$RUNNER_TEMP/codeql_databases/{actions,javascript,python}/src.zip` after `analyze` on a push-event run (cleanup-level may remove it; if missing the step fails closed, rc 2), and that the real archives hold no INERT-suffix file for the javascript-typescript leg (extractor may read `.txt`/`.md`; if it does, D-5 correctly fails and the list needs narrowing).

## Wiring
- `ci.yml` caller block above (U0c).
- tests.yml autofix `gh workflow run codeql.yml` is guarded by a `grep workflow_dispatch` and degrades to a warning; U5 retargets it to `ci.yml`.
- 3 entities pins fail on this unit alone and resolve with U0c/U10/U9b, not here: (1) `every required context runs on a merge-queue entry` and its null control: it reads codeql.yml for `merge_group`, which the umbrella now owns; (2) the pr-contract follower pin lists 'CodeQL' in `workflow_run.workflows`, no longer a pull-request workflow (U10 / pr-contract-rerun retirement).
- No governance.yml step needed.

## Red checks
None read: this unit is offline and made no GitHub reads (the brief spares the API); main's red list is the coordinator's to supply.

## P2a defect
None found.
