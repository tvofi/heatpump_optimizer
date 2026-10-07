Closes #1921. Leaves #201 open.

Part 8 of the repository reorganisation. The round evidence (`tools/audit/round3` to `round9` and the fix rounds), `tools/audit/harnesses/`, `tools/audit/ci-version-edit/`, the wave-5 coverage record and the audit configuration (`bugclasses.json`, `finding.schema.json`, `rotation.json`, `scopes.json`) now sit under `dev/audit/` (`rounds/`, `harnesses/`, `waves/`, `config/`). The move is one path segment deeper than before, which R9-RO-7's root finder already tolerates. `rca/` and the merged README had moved in R9-RO-4.

What the move changes besides paths:

- `tests/harness_headers.py` globs `dev/audit/rounds/round*/D*/*.py` (discovery, the declared-live scan, `REGISTER_DIRS`), and its root-finder scan lists the new homes.
- `tests/closure.py`'s `_is_header_corpus` takes a six-part `dev/audit/rounds/round*/D*/*.py` path out of the `dev/audit/` INERT claim, with a pin in `selftest`. This is the carry from R9-RO-4 (`carry-1921.json`).
- The D6 register agrees in four places: `claims.py`, `STAMP_WRITES` in `tests/env_drift.py`, `REGISTER_DIR` in `tools/release/stamp.py` and the entities pin. The register is regenerated at its new home.
- `tools/audit/prepare_baseline.sh`'s finder wall strips the round evidence at both homes.
- `codeowners_gap.py` runs from `dev/audit/rounds/round6/D11/fix/`. governance.yml runs it behind a presence test at both homes (the pattern the other moved graders use), and `prepr.sh`'s pin self-test names the grader at both.
- `tools/policy/agreement_py.py` locates `governance_cost.py` through the move map.
- `tools/audit/seat/tmp_paths.py` scanned `tools/audit/harnesses`; the move put the harnesses outside its scope, so it now scans `dev/audit/harnesses` and still skips the round and wave records.
- `tools/policy/policy_lint.mjs`'s printer-source scan excludes `dev/audit/rounds` as it excluded `tools/audit/round*`.
- `agreement.mjs` reads the moved ledger and schema. The wave-5 coverage script writes beside itself.
- `tests/entities.py` module-scope reads and the judge_batch fixture directory follow the files.

Deliberately not changed, each with the reason:

- `tools/audit/round4/D11/governance_cost.py` and `d11lib.py` stay at their old path, and `audit-find.js`, `audit-verify.js` and `check-wave-script.mjs` keep the base text. origin/main's `agreement_py.py` imports the first two from there and origin/main's `check-wave-script.mjs` asserts the prompt wording, and both run from the base in pull-request jobs. `tests/closure.py` lists the two files in `INERT_EXCEPT` so the prefix does not declare a read file unread. `carry-1922.json` hands both moves to R9-RO-9.

- `dev/governance/config/corpus_excluded.json` and `cfr_exclusions.json` keep their old keys. `policy_lint.mjs` adds the destination of every moved key from the move map (`moves()`), so both spellings are excluded. Rewriting the keys made 70 `named-docs` errors because the policy files still name the old paths. Policy prose (`CLAUDE.md`, rules, roles, dimensions, ADRs, `tests/README.md`, `dev/audit/README.md`) is untouched: a path edit lengthens capped files that sit at zero headroom, and R9-RO-9 owns the prose sweep.
- Round evidence keeps its old paths (tvofi D2).
- The 68 other landed-but-null `since` entries (69 are null; `.claude/workflows/carry-1921.json` has not moved, so one has not landed) in `tests/layout.json` are not this unit's (carry (a) asks for the units this PR moves); they are left as they are.

`tests/layout.json` `since` is `2015` for the 17 units this PR moves, and `dev/programme/delivery/2015.md` is the delivery row.

## Head

`60c0005241398b5d25db92551b0d1e14cff23a7f`, which contains `origin/main` `e0f0b6fb397bf42a3cd379e0c74f1f295eeebdaf` (#2022 merged) at `2026-10-07T15:51:12Z`. The previous reviewed head was `46b9b4fd`; round 3 blocked `baadb840` on the closures entry below.

### Delta since `46b9b4fd`, the head that passed review

- Merge of #2012 (`45142cc3`): `dev/programme/carries/carry-1922.json` keeps both entries (R9-RO-8's and R9-RCA-1990's). `tools/audit/seat/tmp_paths.py` keeps main's decisions-directory spelling `(?:docs|dev/governance)/decisions/` and this branch's `dev/audit/harnesses` scan scope. `python3 tools/audit/seat/moved_paths.py tools/audit/seat/*` (the R9-RCA-1990 carry's check) returns no hit for a unit this pull request moves; its one audit hit is `tmp_paths.py`'s own docstring naming the pre-move `tools/audit/handoff/`. After the merge, one at a time: `tmp_paths --check` 0 refused, its `--self-test` 43 checks 0 failed, `closure.py selftest` `ALL 33 closure shrink pins PASSED`, `structure.py` passed, `policy_lint` and `brief_lint` ok, `entities.py` `ALL 2198 ENTITY CHECKS PASSED`. Heavy scripts go to CI.
- `dev/audit/harnesses/eg_b7_seam_hubs.py`: #2017 added it under `tools/audit/harnesses/` (merged as `b281a4c3`), inside the directory this pull request moves. It is at `dev/audit/harnesses/` beside the rest; its usage line names that path. Its `since` is `2015` through the directory entry `tools/audit/harnesses/` in `tests/layout.json`, which this pull request already set; no new retired entry is needed. No `closures.json` entry and no harness README row names it: `git grep -n eg_b7_seam_hubs` returns only the file itself. The README index row that the R9-RO-9 carry covers will point at the new path.
- `dev/audit/rounds/round4/D6/claims.json` and `claims.md`: main's content at the moved path. `diff` of main's `tools/audit/round4/D6/<file>` after `sed 's#tools/audit/round4#dev/audit/rounds/round4#'` against the file here is empty for both, and `claims.py` regenerates them byte-identically. `tools/audit/round4/D6/claims.md` stays deleted.
- `tests/closures.json`: `inert_reads["tests/harness_headers.py"]` named `tools/audit/harnesses/eg_b7_seam_hubs.py`, which #2022 added at the old path; the entry is now `dev/audit/harnesses/eg_b7_seam_hubs.py`. The Mac recorder cannot see this read: `harness_headers.py` reads the harness files in child processes, which only Linux `strace` records, so a Mac `--single` recording leaves `inert_reads` empty and its `closure.py check` passes with or without the entry. That earlier passing check proved nothing about this path. The proof used here is a stand-in recording that injects the read (the Darwin recording plus `inert_reads: [dev/audit/harnesses/eg_b7_seam_hubs.py]`): `python3 tests/closure.py check --in-dir <stand-in> --partial` exits 1 before the entry is corrected and 0 at this head; a control stand-in injecting an already-recorded harness exits 0. No other `closures.json` entry, in `closures` or `inert_reads`, names a path that no longer exists (a script over every entry prints no dead path). CI's `closures` job, which records on Linux, is the authority.

## Mutation proof

- `_is_header_corpus` with `len(parts) == 6` set back to `5`: `python3 tests/closure.py selftest` went red (the header-corpus pin and the checks that read it, named in the first failures). Restored, it prints `ALL 33 closure shrink pins PASSED`.
- `tests/harness_headers.py`'s two `glob("round*/D*/*.py")` roots set back to `tools/audit`: `declared_live()` returns 0 files against 6, so the check would pass on an empty set. Restored, it returns 6.
- `python3 tests/mutation_table.py --scope changed --base origin/main` prints `MUTATION TABLE PASSED (empty scope)`: no `custom_components` file changed. `--max 0` was not used.

## Null control

- Carry control. A planted harness path `dev/audit/rounds/round3/D2/planted_live.py` named in a recorded closure:

  ```
  cd <checkout>; python3 - <<'E'
  import sys; sys.path.insert(0, "tests"); import closure
  p = "dev/audit/rounds/round3/D2/planted_live.py"
  print(closure.is_inert(p), closure._is_header_corpus(p), closure.inert_closure_violations({"tests/harness_headers.py": [p]}))
  E
  ```

  At `origin/main`: `True False ['dev/audit/rounds/round3/D2/planted_live.py']`, the INERT-and-recorded refusal, red. At this head: `False True []`, green.
- Harness list. `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` prints the same nine executed live-header harnesses at `origin/main` and at the head after `sed 's#tools/audit/round#R#'` against `sed 's#dev/audit/rounds/round#R#'` (`diff` of the two sorted lists is empty). A planted live-header harness at the new path that exits 1 turns the head red (`planted_live.py exits 0 [rc=1]`, `RESULT planted matches header`).
- Layout counts, `python3 tests/layout.py --report`, per arm, before (`origin/main` `3910026e`) and after (this head): category 1765 to 111, retired-file 1655 to 3 (carry-1921.json, plus `governance_cost.py` and `d11lib.py`, which stay under `tools/audit/round4/D11` on purpose and go to R9-RO-9), reference 1522 to 1371 (the remainder are policy prose, ADRs, `corpus_excluded.json` keys and locate-wrapped old names that R9-RO-9 rewrites), dead 5 to 1. The one retired finding is `carry-1921.json`, a live carry the plan moves with R9-RO-5.
- `tools/audit/seat/tmp_paths.py`: `python3 -I tools/audit/seat/tmp_paths.py --self-test` prints 42 checks, 0 failed; the new arm refuses a `/private/tmp` path in a `dev/audit/harnesses` file and skips a `dev/audit/waves` one.

## Figures

- Old-path grep for every moved unit (spawn, exec, subprocess, workflow and glob strings included), outside round evidence, closures.json, layout.json, goldens, ledgers, archive, delivery rows and RCA documents:
  `git grep -nE "tools/audit/(round[0-9]+(-fix)?|ci-version-edit|harnesses|w5-g5-195-coverage|bugclasses\.json|finding\.schema\.json|rotation\.json|scopes\.json)" -- . ':!dev/audit/rounds' ':!tests/closures.json' ':!tests/layout.json' ':!tests/golden' ':!tests/mutation_ledger' ':!RELEASE_NOTES.md' ':!dev/archive' ':!dev/programme/delivery' ':!handoff' ':!dev/audit/rca' ':!tools/audit/archscore'`.
  Dispositions of what it still returns: the pre-move pathspecs and `if test -f` guards in `.github/workflows/{governance,tests,pr-contract}.yml` and `tools/pr/prepr.sh` (kept on purpose so a branch cut before the move still has its grader; R9-RO-9 drops them); `tools/audit/check_scopes.py`, `merge_fastpath.py`, `tools/policy/agreement_py.py` and `field_coverage.mjs`, which resolve the old name through `layout.locate`; `tests/closure.py`'s negative pin and `prepare_baseline.sh`'s planted old-path wall case (controls that name the old path); policy prose, ADRs, `bugclasses.json` text, `dev/audit/README.md` history and two `custom_components` comments (R9-RO-9 or round evidence); `audit-find.js`, `audit-verify.js` and `check-wave-script.mjs` (held at the base text, see above); `.github/CODEOWNERS:49`, an owner line for a README that R9-RO-4 merged away. Executable strings found and rewritten: `dev/audit/waves/w5-g5-195-coverage/coverage_suite.sh` (its output default), `tools/audit/seat/tmp_paths.py` (scope regexes), `tools/policy/policy_lint.mjs` (printer-source exclusion), `tools/policy/agreement_py.py` (sys.path and spec path) and `tests/entities.py:31825` (the fixture directory, a split `/ "tools" / "audit" /` form the grep above does not match; found by `git grep -nE '"tools"\s*[,/]\s*"audit"'`).
- `python3 tests/entities.py` at the pre-merge head `c53cdc5fd69124917d6be8c19b41425879db99be`: `ALL 2188 ENTITY CHECKS PASSED`. At the head above, after the merge: `ALL 2191 ENTITY CHECKS PASSED`. `python3 tests/doc_claims.py` at the head: `ALL 160 checks PASSED`.
- `python3 tests/harness_headers.py` at `c53cdc5f` on an idle machine: `ALL 109 HARNESS HEADER CHECKS PASSED`. At `origin/main` the same run printed `12 of 109 ... FAILED`, and at the head `12 of 109` again on a loaded machine; `grep FAIL <log> | grep -v sysid_estimator_frontier` returns only the summary line in both, so all twelve are `sysid_estimator_frontier.py` hitting the 900 s wall. It is the host and not the move.
- `./tests/derive_closures.sh --single tests/entities.py --record-only`, then `python3 tests/closure.py check --in-dir <dir> --partial`, prints `committed closures cover every file this run touched`; the same for `harness_headers.py` is blind to child-process reads (see the `tests/closures.json` delta above) and is not offered as evidence. `python3 tests/closure.py prune` prunes 0 entries. No full `tests/derive_closures.sh` was run.
- `python3 tools/release/stamp.py --self-test`: `RESULT stamp_self_test=pass`. `python3 dev/audit/rounds/round4/D6/claims.py` leaves `claims.json` and `claims.md` byte-identical to the committed files.
- `python3 -I dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: `uncovered_files=0`; `--self-test` passes.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s)`; `node tools/policy/check-wave-script.mjs`: 170 passed, 0 failed; `node tools/policy/field_coverage.mjs`: `FIELD COVERAGE ok`; `node tools/policy/rules_sync.mjs --check` ok; `python3 -I tools/policy/agreement_py.py --run`: `AGREEMENT ok`; `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `bash tools/pr/prepr.sh --self-test`: `193 passed, 0 failed` at this head (see Red checks).
- Gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL` because `tests/closure.py` changes the gate.

## Red checks

`delivery-status` and `nightly-status`: both read `.github/workflows/governance.yml`, which this diff touches (prepr names them). The change is two `run:` lines and one `git diff --quiet` pathspec for `codeowners_gap.py`: each now tests for the file at its old home and falls back to `dev/audit/rounds/round6/D11/fix/`; it adds no job, no step, no trigger and no job name, so neither check's reading of the workflow changes. Both are red on `main` before this pull request, because main's record-autofix staged the old delivery path; #2011 fixes that, and this branch's row is at `dev/programme/delivery/2015.md`. The cheaper detector is `delivery-status` itself, graded on `main`; no local one applies.

`CodeQL` (head `79554e2f`): three alerts, `py/overly-permissive-file` in `dev/audit/rounds/round8/evidence/D11/s2_release_gate.py:69` and `py/clear-text-logging-sensitive-data` in `dev/audit/rounds/round9/D11/s1/privileged_pr_code.py:96` and `dev/audit/rounds/round9/D8/leads/l2_d8_leads.py:305`. They are write-once round-evidence scripts that this pull request renames without editing a line; CodeQL reports a moved file's alerts as new at the new path. No cheaper detector exists and none is worth building: the code is unchanged evidence. Alerts 31, 32 and 33 are now dismissed as evidence code at the new paths, mirroring #22, #23 and #25 at the old ones.

`pr-contract` failed at `79554e2f` (job 112755516860) with three `[pr-body]` errors: `## Red checks` did not name `CodeQL`, `delivery-status` or `nightly-status`, which were red on that head. This section now names and answers all three. Step-11 answer: no cheaper detector exists. Those three reds appeared only after the push, on check runs that did not exist before it, so `prepr.sh` could not read them; its `ancestry reds` step sees them only once `origin/handoff/r9-ro-8` exists, and the first push creates it. Standing cost of the push-then-read order: one `pr-contract` red on the first head.

No check is expected red from a base-restored grader. Verified by checking `origin/main`'s `tools/policy` and `tools/pr` out over this head (and `origin/main`'s `codeowners_gap.py` at its old path) and running them:

- `node tools/policy/check-wave-script.mjs` prints `170 passed, 0 failed`.
- `python3 -I tools/policy/agreement_py.py --run` prints `AGREEMENT ok`.
- `node tools/policy/policy_lint.mjs` prints `FIXTURE ok`, `node tools/policy/brief_lint.mjs` prints `CARRY ok`, and `python3 -I tools/audit/round6/D11/fix/codeowners_gap.py --check` prints `uncovered_files=0`.

The same two graders against an earlier head of this branch (prompts rewritten, `governance_cost.py` moved) printed `165 passed, 5 failed` and a `FileNotFoundError`; that is the control that the check can fail.

`bash tools/pr/prepr.sh --self-test` prints `193 passed, 0 failed` at this head (main's #2021 fixed the seven failures that printed `186 passed, 7 failed` before). The same self-test inside the full `prepr.sh` run printed `192 passed, 1 failed` once on a loaded machine and did not reproduce when run alone.

## Forward-carry

`dev/programme/carries/carry-1922.json` (the in-tree destination for R9-RO-9, #1922) carries the leftovers: the old-path guards and pathspecs listed under Figures, the locate-wrapped old names, the `corpus_excluded.json` and `cfr_exclusions.json` keys, policy prose and ADR citations of the moved units, and `.github/CODEOWNERS:49`. It also states the one ordering constraint: a base-restored grader reads the old name until the base carries the rewrite. The the 68 landed entries of `tests/layout.json` that other pull requests moved and left at `since: null` are named here for whoever derives their numbers.

## Friction

`finding-propagation`: `unenforced`: `tests/layout.json` `since` cannot be filled by the author of the move, because the number exists only after the pull request is opened; nothing refuses a landed move that keeps `since: null`.
