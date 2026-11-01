R10-AUDIT-COVERAGE-ENDGAME (design `design/r10-audit-coverage` at `ae3d86dc0`, approved by `design-verdict/r10-audit-coverage` `5b77e98dd`). The owner asked that the audit dimensions, finder scopes, bug classes and harnesses cover production, the instruments and the repository machinery as they stand at v10.0.0. Every gap was re-measured at this branch's merge base, `c88d552c7`. No count is carried from the note.

**What changes**

- **G4 and Carry 1 (design-review C1): coverage is part of the default run.** `tools/audit/check_scopes.py`'s existing invocation (`--repo R --ref B`) now also refuses three things, so `.claude/workflows/audit-find.js` Prepare step 7 and the `check-wave-script.mjs` pins need no edit:
  - a tracked path that is in no dimension's universe and not on the new `_coverage_excluded` map in `scopes.json` (glob → reason);
  - an exclusion that also names a covered path, names nothing, or carries no reason;
  - a harness under `dev/audit/harnesses/` whose header names a brief (`D<k>.md`) that does not cite it (Carry 8).

  The exit code goes through one function, `verdict()`. `--self-test` drives it on the live scopes, with D10's universe dropped, and with an uncited harness planted. Since round 2 it also runs the default invocation whole, as a subprocess of the file with `--repo`/`--ref`: the live scopes must exit 0 and the scopes with D4's and D6's `blueprints/**` globs dropped must exit 1 naming a blueprint, both printing `verdict()`'s citation line. It also drives `coverage()` arms that must name `custom_components/heatpump_optimizer/py.typed` (Carry 5), and `tests/closure.py` and `blueprints/automation/notifications.yaml` when every `tests/`/`blueprints/` glob is stripped.
- **G1, G2, G3: the universes.**
  - D3 gains `tests/*.{py,mjs,sh}`, `tests/README.md`, `tests/fixtures/**`, `tests/replay/**` and `tests/pwlane/*.json`.
  - D11 gains the gate machinery: `closure`, `entities`, `structure`, `env_drift`, `gate_lock`, `layout` and the ratchets; `tests/*.json` (closures, every budget file, `seam_map.json`); `tests/requirements-*.txt` and `tests/hastub/**`. It also gains the release and repo files (`.gitattributes`, `.gitignore`, `SECURITY.md`, `VERSION`, `RELEASE_NOTES.md`) and `dev/README.md`. From `dev/programme/` it gains `HANDOVER.md`, `plan-*.md`, `carries/**` and `rosters/**`.
  - D11's `dev/audit/**` becomes `dev/audit/{README.md,config/**,harnesses/**,rca/**,waves/**}`, so `dev/audit/rounds/**` is out of every universe.
  - D4 and D6 gain `blueprints/**`, and D6 gains `docs/img/**` (the figures and their generators).
  - The other unmeasured paths are excluded, each with its reason in the file: `dev/audit/rounds/**`, `dev/archive/**`, the record subtrees of `dev/programme/`, `docs/design/**`, `docs/site/fonts/**`, `tests/golden/**`, `tests/mutation_ledger/**`, `LICENSE` and `NOTICE`.
- **G5 and Carry 3 (design-review C3): barrier paths resolve.**
  - `tools/audit/fold_ledger.py check` refuses `MISSING-PATH`: a token in a class's `barrier` **or `detector`** that is path-shaped and absent at the root. A token is path-shaped only when its first segment is a tracked top-level directory, with any `:line`, `::symbol` or `@sha` suffix dropped.
  - The self-test's passing arm holds `F3.1/F3.2` and `handoff/r9-rca-p1@0ade2456`.
  - P5's and P9's barriers are repointed to `dev/archive/carries/carry-1655.json` and `carry-1757.json`.
  - P1's `enumerate.sh` has no live copy. Round 10's `sweep-P1` enumerates timestamp seams, not the live-input plausibility rule, so it does not supersede the script. The token is dropped and the sentence now says why. The blind-spot warning stays.
  - The rule also read `detector`, which found three more stale tokens. I3's and N-silent-zero's detectors now point to `tools/policy/field_coverage.mjs`, and I4's to `tools/policy/agreement.mjs`.
- **Carry 7: shipped barriers on the ledger.**
  - `fold_ledger.py check` refuses `UNRECORDED-BARRIER`: a class with an rca document in `dev/audit/rca`, a null `barrier` and no `barrier_refusal`, while a `tests/` script names the class id as a word.
  - `barrier_refusal` is the field P4 already carried.
  - It returned eight classes at the base. Each is dispositioned in `## Figures`.
- **G6 and Carry 4 (design-review C4): harnesses.**
  - The three round-9 harnesses that the round-10 register cites now read their moved paths old path first.
  - `dev/audit/README.md` states the retirement rule and gives its command. It does not name the repaired harnesses, because naming one there makes it live-cited, and then `tests/entities.py`'s N-move-stale-path arm requires it to resolve every path it opens at any ref. That arm turned red when an earlier draft of this branch named them.
  - The README cites `tools/audit/seat/moved_paths.py` as the instrument to run, so `tests/entities.py` now reads it. `tests/closures.json` records that read; `tools/pr/ci_predict.py --apply-inert` wrote the entry.
  - `tools/audit/seat/moved_paths.py` crashed on the first binary file of a directory walk (a `.gz` under `dev/audit/harnesses/`). It now skips such files, and its self-test has an arm for this. The file is outside the roster's `files`, but it is the G6 instrument the brief names.
- **Briefs (policy, approved by the orchestrator under its mandate before the merge).**
  - D3 step 1 makes a `tests/` check that cannot fail a candidate.
  - D4 step 2 scores each `blueprints/` file's inputs by the config-flow rubric.
  - D11 step 1's row list names `.github/workflows/`, the `tests/` gate, `tools/pr/`, `tools/plan/` and `tools/audit/seat/` with its merge train.
  - D15 step 1 now runs `dev/audit/harnesses/d15_restart_gaps.py` in place of restating its rule.

  Each file stays within its `policy_budgets.json` cap, paid by cutting prose the edit made redundant or that was false (see Figures). No cap is raised.

**Roster carries.** Carry 1 (C1) is coverage in the default invocation. Carry 2 (C2) is the per-dimension `--seat` proof under `## Null control`. Carry 3 (C3) is the barrier-path rule and the P1, P5 and P9 repoints. Carry 4 (C4) is the G6 cited set and its command under `## Figures`. Carry 5 (C5) is the D10 arm naming `py.typed`. Carry 6 is the approved design `ae3d86dc0`, followed as written: no departure is raised. Carry 7 is the shipped barriers and `UNRECORDED-BARRIER`. Carry 8 is the D15 harness citation and the harness-citation arm.

## Head

Round 2 (minimal repair of the fix review's one block, `verdict/3149` at `9bb207408`). The new handoff head and code head are both `ced02240fbac3e523d37efe111136b7fa094e71e`, a fast-forward of the round-1 code head `40f6097a10a02379a63b86523bf8ed304f8d3859` by one commit that changes only `tools/audit/check_scopes.py`. The PR head the reviewer judged, `1abb0abab0dd1f3d9ec30f790fffd75c042dabe6`, is `40f6097a1` plus a merge of main. `git merge-tree --write-tree origin/main HEAD` at `origin/main` `25c46e76e` (2026-11-01T21:43Z, `date -u`) gives rc 0 with `LEDGER-MERGE: resolved tests/closures.json`, so main was not merged. The round-2 figures (the self-test, the five code mutants, the default run's `tracked=`, the gate, structure and prepr) were taken at `ced02240f`. The round-1 figures below were taken at `40f6097a1`, whose tree differs from `ced02240f` only in `check_scopes.py`.

Round 1: `40f6097a10a02379a63b86523bf8ed304f8d3859`, measured against merge base `c88d552c76f1ae11a879ce7ccb8d8dc29adabf50` (`origin/main` at 2026-11-01T19:36Z, `date -u`). `origin/main` moved twice during the work, `ca6333333` → `407eb0cb3` → `c88d552c7`, and was merged each time (`06eb0d3eb`, `40f6097a1`). Every figure that depends on main was re-taken after the second merge: coverage, seat deltas, the ledger check and the 16 mutants. Neither merge touched a file this group edits except `tests/closures.json`, which the ledger merge driver resolved.

## Mutation proof

One textual mutation at a time on the head, using the self-test CI already runs: `governance.yml`'s `check_scopes.py --self-test`, and `fold_ledger.py --self-test` beside `check`. Each mutant turns its self-test rc 1 and names the arm that went red; the file was restored after each.

`tools/audit/check_scopes.py`:
- M1. `coverage()` does not subtract the union of universes. Red: "drop D10's universe", "strip tests/ and blueprints/ globs", "null control: optimizer.py covered", "the default verdict passes the live scopes".
- M2. Exclusions are not subtracted. Red: "the default verdict passes the live scopes".
- M3. An excluded-but-covered path is accepted. Red: "exclude a covered path".
- M4. `verdict()` drops coverage. Red: "and refuses them without D10's universe".
- M5. Harness citations are never refused. Red: "a harness the brief does not cite is refused", "and refuses an uncited brief-named harness".
- M6. `verdict()` drops citations. Red: "and refuses an uncited brief-named harness".
- M7. A dead exclusion is accepted. Red: "an exclusion naming nothing".
- M8. An unreasoned exclusion is accepted. Red: "an exclusion with no reason".

`tools/audit/fold_ledger.py`:
- F1. The existence test is removed. Red: "a barrier citing a path absent at the root is MISSING-PATH", "a detector path is resolved the same way, its :line suffix dropped".
- F2. Any token with a slash counts as a path. Red: "null control: present paths pass, and F3.1/F3.2 and handoff/r9-rca-p1@0ade2456 are not path-shaped".
- F3. Suffixes are kept. Red: the same null control.
- F4. Only `barrier` is read. Red: "a detector path is resolved the same way".
- F5. `UNRECORDED-BARRIER` is never emitted. Red: "a class whose rca is in the tree, with a null barrier while a tests/ arm names it, is UNRECORDED-BARRIER".
- F6. `barrier_refusal` is ignored. Red: "and a recorded barrier_refusal answers it".
- F7. A substring match replaces the word match. Red: "null control: a longer id containing the class id is not the class".

`tools/audit/seat/moved_paths.py`:
- P1. `UnicodeDecodeError` is no longer caught. The self-test crashes, rc 1.

Round 2, the reviewer's code mutants (`ev/check_scopes_code_mutants.txt`, `ev/CM4.patch`), run at `ced02240f` with `python3 tools/audit/check_scopes.py --repo . --self-test`, the file restored after each:
- CM4. `main()` exits on `sys.exit(0 if check(scopes, tree, loc) else 1)`, bypassing `verdict()`. Red: "the default invocation exits 0 on the live scopes" (no citation line) and "and exits 1 without D4's and D6's blueprints globs" (the subprocess exits 0), rc 1. Before the repair, the round-1 file under the same mutant gave rc 0.
- CM2 (an excluded-but-covered path accepted), rc 1. Red: "exclude a covered path".
- CM3 (header window `[:0]`), rc 1. Red: "a harness the brief does not cite is refused", "and refuses an uncited brief-named harness".
- CM5 (citation never refused), rc 1. Red: the same two arms, plus the two default-invocation arms.
- CM6 (`verdict()` drops coverage), rc 1. Red: "and refuses them without D10's universe", "and exits 1 without D4's and D6's blueprints globs".

CM2, CM3, CM5 and CM6 stay killed. The clean file gives rc 0 at `ced02240f` (`default invocation: live rc=0, blueprints dropped rc=1`). The round-1 file without the mutant also gives rc 0, so CM4 is the only mutant whose result the repair changes. The self-test comment that said "neither coverage nor citations can fall out of the exit code" now says the function-level arms pin `verdict()`, and that the subprocess arms pin `main()`'s exit to `verdict()`'s answer.

Before the earlier mutants, M4 was a survivor: coverage was dropped from the exit code and the self-test stayed green. That is why `verdict()` exists and is driven whole. M7 and M8 were survivors before their arms were added.

## Null control

- `custom_components/heatpump_optimizer/optimizer.py` is covered by D0, D1, D2, D3, D5, D7, D9, D10 and D12. The note's Appendix A enumerator (`cov.py <ref> --table`) gives the same row at the base and at the head, and the self-test arm "null control: optimizer.py covered" is green.
- `tools/site/build_docs.mjs` is covered by D6 and D11 at both ends.
- `check_scopes.py --seat` output is byte-identical for every seat of every dimension whose universe this group leaves untouched: 40 of 48 seats. The base checkout's own script ran with base scopes against the head's script with head scopes (`seatdiff.sh`, below). The 8 changed seats are exactly the ones Carry 2 (design-review C2) predicts: D3-s1, D3-s2, D6-s1 and D6-s2 are identical, and D3-s3, all three D4 seats, D6-s3 and all three D11 seats change.
- `fold_ledger.py check`: N-order-coupling (no rca, no arm) stays open and unflagged at both ends.
- `fold_ledger.py --self-test`: a longer id (`N-log-flooding`) does not name `N-log-flood`.

## Figures

- Coverage, merge base vs head: `python3 tools/audit/check_scopes.py --repo . --ref c88d552c7 --scopes <base scopes.json>` gives `FAIL coverage tracked=8102 in_universe=3270 excluded=0 unclassified=4832` and `FAIL harness citations: 1` (`d15_restart_gaps.py` names D15.md, which does not cite it), rc 1. At the head `ced02240f`, `python3 tools/audit/check_scopes.py --repo . --ref HEAD` gives `ok coverage tracked=8102 in_universe=1326 excluded=6776 unclassified=0` and `ok harness citations: 0`, rc 0. Every dimension prints `ok`. The reviewer's `tracked=8107 in_universe=1329 excluded=6778` is the PR head `1abb0abab`, which carries main's merge: the same command with `--ref 1abb0abab0dd1f3d9ec30f790fffd75c042dabe6` prints exactly that, rc 0.
- G1–G3 at the first base `ca6333333`, by the note's enumerator (`python3 cov.py <ref> --table`, Appendix A of the design note), classified with `scopes.json`'s glob dialect over `git ls-tree -r --name-only`:
  - 4829 tracked paths were in no universe: 74 top-level `tests/` files, 35 under `tests/hastub`, 3006 under `tests/mutation_ledger/`, 58 under `tests/golden/`, 5 `blueprints/`, 1431 under `dev/programme/`, 131 under `dev/archive/`, 7 root files, 6 under `docs/design/`, 62 under `docs/img/` and 6 font files, plus `dev/README.md` and `tests/fixtures`, `tests/pwlane` and `tests/replay`.
  - `git ls-files dev/audit/rounds | wc -l` gives 2147 of the 3156 files each D11 seat held at `c88d552c7`.
- `--seat` delta per seat (`seatdiff.sh <base checkout> <head checkout> <base ref>`, which runs each checkout's own `check_scopes.py --seat D<k>-s<n>` and counts lines): D3-s3 55→121, D4-s1/s2/s3 9→14, D6-s3 6→73, D11-s1/s2/s3 3156→1093. The other 40 are `IDENTICAL`.
- `fold_ledger.py check` with the base ledger (`--ledger <git show c88d552c7:dev/audit/config/bugclasses.json>`) gives 14 violations: 6 `MISSING-PATH` (P1, P5 and P9 barriers; I3, I4 and N-silent-zero detectors) and 8 `UNRECORDED-BARRIER`. At the head: `0 violation(s)`, 47 classes, 749 instances.
- `UNRECORDED-BARRIER`, each returned class with its disposition:
  - **N-log-flood**, barriered: `tests/entities.py` check "R10 N-log-flood barrier: …", landed `d7b171229` (#2336).
  - **N-no-expiry**, barriered: `tests/entities.py` check "R10 N-no-expiry barrier: …", landed `d7b171229` (#2336).
  - **N-move-stale-path**, barriered: `tests/entities.py` check "every program live policy or a carry's remeasure tells a seat to run …", landed `7215e39df` (#2289). Not reached, which is the RCA's own scope: an uncited historical harness.
  - **N-staleness**, barriered: the `tests/features.py` section "R10 N-staleness: the age limit keyed on how a source reports" over `INPUT_ON_CHANGE_MAX_AGE_MINUTES`, landed in `d0ae3ca9f` (#2683). The RCA proposed `INPUT_QUIET_MINUTES`, but the shipped form is the on-change table. `git grep INPUT_QUIET_MINUTES -- custom_components` is empty.
  - **N-confounded-learner**, `barrier_refusal`: the `#2223` checks pin the four instances by value, and no registration arm was built, so status stays open.
  - **P8**, `barrier_refusal`: the arm reads unit reads only. Round 10 placed 6 instances after it landed, including the two `_command_valve_target` write arms.
  - **P10**, `barrier_refusal`: round 10 placed D14-s1-01 and `_replay_interval` after the `tests/replay.py` arm landed (#1788).
  - **N-name-sort**, `barrier_refusal`: round 10 placed D7-s3-53 and a sweep seam inside the `#1760` check itself.

  For the four barriered classes, the `_rca` entries go from `proposed` to `done` with `landed`. Each class's `trigger` is re-derived by `fold_ledger.py refresh`.
  - The rule names a class only by its id as a word of a top-level `tests/` script. That rule enumerates the class's seams. Every class it returned is listed above, so none is left undispositioned.
- G6 cited set (Carry 4, design-review C4). The register picked is the latest round's issue drafts and verdicts, `dev/audit/rounds/round10/ISSUES.json` and `JUDGE.json`, plus every bug class's `detector` and `barrier`. The enumerator: grep those three for `(dev/audit/harnesses|dev/audit/rounds/round9|tools/audit/round9)/…\.(py|mjs|js|sh)`. It returns 6 paths:
  - `dev/audit/harnesses/pulse_replay.py` (N-silent-stop detector) is present and needs `--since/--until`; it is not stale.
  - `dev/audit/rounds/round9/D11/s2/owner_review.py`, `…/D14/s2/i4_roster.py` and `…/D4/s2/step_grid.py` are present and stale.
  - P1's `enumerate.sh` is missing and has no live copy (above).
  - `tools/audit/round9/D4/s2/step_grid.mjs` is the old path of the `.mjs` that `step_grid.py` calls.
- The three repaired harnesses, before (the base copy, run from the tree) and after, with `PYTHONPATH=tests/hastub` from the root:
  - `owner_review.py`: `ModuleNotFoundError: budget_raise_gate` before. After: `RESULT owner_approved…` lines, `perturbed_seat_counted=0`, rc 0.
  - `step_grid.py`: `CalledProcessError` on `tools/audit/round9/D4/s2/step_grid.mjs` before. After: `RESULT off_grid_derived=0`, `off_grid_slider_fields=0`, `out_of_range_values=0`, rc 0.
  - `i4_roster.py --dims HEAD`: `dim_roster_readers_disagreeing[HEAD]=1 (of 1)` before (it found no briefs), `=0 (of 4)` after.
  - `i4_roster.py --dims 8d731d77^`: `=1 (of 2)` after (missing D13), its documented positive control.
  - `i4_roster.py`'s default mode now passes every moved path and stops on `scopes["D14"]["axis"]["class"]`, a key `scopes.json` replaced with `class_status`. That is a data-shape change, not a path, so that mode stays retired under the README rule.
- Stale-path census of `dev/audit/harnesses/` and `dev/audit/rounds/round9/` (`stale_census.sh`: `git ls-files … | grep -E '\.(py|mjs|js|sh)$' | xargs python3 tools/audit/seat/moved_paths.py`, files with ≥1 `[STALE?]` line, out of 498 scripts): 274 at `ca6333333` and 273 at the head. `step_grid.py` leaves the list. `owner_review.py` and `i4_roster.py` keep header prose that names old paths, a record, while their reads go through the move map.
- Policy caps (`node tools/policy/policy_lint.mjs --budgets`, lines/tokens vs cap):
  - D3.md 46/596 vs 46/607.
  - D4.md 48/585 vs 48/586.
  - D11.md 99/1494 vs 103/1499.
  - D15.md 36/690 vs 37/690.
  - `dev/audit/README.md` 243/3880 vs 250/3880.

  The payments:
  - D3 drops `tests/features.py:12382` "for the mutation idiom". That line is a topology check now, a false citation. D3 also drops a duplicated `GATE_JOBS=1`.
  - D15 cites the harness in place of restating the rule it implements.
  - The README drops `SCENARIOS (49)` (`len(golden.SCENARIOS)` is 50), `~156 keys`, and two stale bare line numbers (`stress.py :1597` and `structure.py :1275`, whose `__main__` guards are now at 3367 and 4425). It re-anchors the `SLOW_GATED` trap on the comment instead of `tests/closure.py:100-101`, and drops a 212-files/5.5 MB history line and two "this file carries why" pointers.
  - D11 folds the new names into the existing row list and drops "change-failure rate among them", "Derive the row count…" (restated by the step's own header) and the OWASP examples list.

  `policy_lint.mjs` acceptance: `TOTAL: 0 error(s)`.
- Gate (`tests/closure.py select --diff $(git merge-base origin/main HEAD)`): `MODE: SCOPED -- 1 script(s) run`, `tests/entities.py`, which gives `ALL 2516 ENTITY CHECKS PASSED` at `ced02240f`. `run_always` lines: `env_drift.py --claims-only` ok, `closure.py selftest` `ALL 117 closure shrink pins PASSED`, `layout.py` ok, and `harness_headers.py` `ALL 112 HARNESS HEADER CHECKS PASSED`. `python3 tests/structure.py` gives `STRUCTURE RATCHET PASSED`.
- `bash tools/pr/prepr.sh <this body>` at the head `ced02240f`, closures and CI-predict steps included: `PRE-PR: ced02240f… rc=0`. `origin/main` was at `25c46e76e` when it ran. It has moved past the merge base `c88d552c7`, but `git merge-tree` reports no conflict, so main is not merged at this head (the brief's rule). In round 1, prepr gave `PRE-PR: 40f6097a… rc=0` with main unmoved.
- Unpinned sites: the sites this diff adds are in `tools/audit/`, which `mutation-autofix` does not mutate. Each is pinned by its instrument's own `--self-test` arm, as the mutants above show.
- Goldens: none move, and neither claim file is touched (three-dot diff).

## Red checks

`none`. At the handoff head `ced02240f` no check has run yet: it has never been a PR head, so it has no check-runs. At the PR head `1abb0abab`, the check-run set is 55 runs on one page of 100 (`pull_request_read get_check_runs`, perPage 100). Every concluded run is `success` or `skipped`, and none is `failure`. In round 1, three checks went red, or were predicted red, during the work. They are answered here:
- **`tests/entities.py` N-move-stale-path arm.** It went red when a README draft named the repaired harnesses. The cheaper detector is the arm itself, which ran in the scoped gate before the push, so none cheaper exists.
- **`ci_predict.py` predicted a `tests / closures` red (`INERT READS tests/entities.py: tools/audit/seat/moved_paths.py`).** `prepr.sh` step 6d caught it before any push to the handoff ref. `--apply-inert` repaired it.
- **`agreement.mjs` `UNREGISTERED`.** The `(?<![\w-])` grammar was shared with `tests/doc_claims.py`. `prepr.sh`'s agreement step caught it before the push.

## Forward-carry

- **R10-CATALOG-PR (carry C6, edge E1).** Its base re-measure is now one command: `python3 tools/audit/check_scopes.py --repo . --ref <its base>` gives rc and `unclassified=`. A path a later group adds outside every universe turns it rc 1, and the fix is to classify that path (a universe glob or a reasoned `_coverage_excluded` entry). The carry belongs in its brief and the `after: R10-AUDIT-COVERAGE-ENDGAME` edge on it, which this seat may not write. Carry: R10-CATALOG-PR (orchestrator, `roster_edit.py`).
- **R10-CLOSEOUT-CLEANUP (edge E2).** Its `--apply` deletes `design/*` and `handoff/*` refs, so it follows this merge, and its new instrument lands inside D11's `tools/**`. Carry: R10-CLOSEOUT-CLEANUP (orchestrator, `roster_edit.py`).

## Approval

Pending. This diff touches five policy files: `dev/governance/dimensions/D3.md`, `D4.md`, `D11.md`, `D15.md` and `dev/audit/README.md`. The roster brief has the orchestrator approve the dimension-brief edits under its mandate before the merge. Carry 7 names D15.md as policy that needs approval before the merge. `main-protect-checks`' code-owner rule requires the owner's approving review at the merged head. This seat records no approval.

## Friction

none
