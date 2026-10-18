_Requested by **tvofi**_

R10-TICK-DRIVERS, findings R10-TICK e, g, h and i. Part of #2265 and part of #201; this group's roster entry lists no issue under `fixes`, so this body closes none. It also lands the two countermeasures the RCA `dev/audit/rca/R10-HANDOFF-PREPR-BOUNCE.md` carried into this group, M2 and M3. It builds on #2376's `ci_predict.py --apply-inert` and does not redo it.

**Owner gate.** `.claude/workflows/audit-find.js`, `.claude/workflows/audit-verify.js` and `tools/audit/fold_ledger.py` are code-owned, so tvofi approves this at merge. No other changed file has an owner in `.github/CODEOWNERS`.

What changes, by finding:

- **(g) and (i): one generated block, derived from the schema.** The finder's return schema was a hand-kept copy in `audit-find.js` with none of `finding.schema.json`'s enums or numeric types. Intake validates against the file, so 35 of the 44 round-10 box findings were rejected on form after the finder had already returned. The workflow runtime has no filesystem, so the driver cannot read the schema itself. `fold_ledger.py` (the file's one writer) gains `sync`, which writes a marked block in `audit-find.js` with two parts:
  - `CLASS_GUESS`, intake's class check, the third reader of the class enum (i).
  - `FINDING_REPORT`, the whole schema with its `$ref`s inlined (g).

  `fold` calls `sync` after every write, so a minted class reaches all three readers in one step. The finder's `reportSchema` is now `FINDING_REPORT` plus the driver's own `report_path`, and the leads seat's `findings` comes from the same place. `agreement.mjs` registers a new pair, `finder-report-form`, which compares every leaf of the inlined file schema with the block. The existing `finding-class-id` pair still holds `CLASS_GUESS`. The `CLASS_GUESS` line `sync` writes is byte-identical to the hand-spelled one it replaces.
- **(e) and (h): one class, "a workflow script trusts a large agent reply".** The class has two halves, and each is fixed where it occurs, not at the two reported sites.
  - **Size.** No one reply carries a round. `from: "intake"` now runs one gatherer per box, in parallel, and each reply holds one box's reports. A seat that a box other than its BOXES box reports (a seat re-run on another container) is still taken, and logged. Where two boxes report one seat, the box that BOXES places it on wins.
  - **Shape.** Every collection read off a reply goes through `replyField`, in both drivers. JSON text, the shape round 10's register read returned, is parsed. Anything else, including cut-off text, is refused with the reply named and is never read as empty. In `audit-find.js`, a report that fails this is a seat not reported: it is logged with the field named, it is listed in `missing`, and intake does not run. The verifiers' votes count as a null verifier and are re-run once. The register read, the dedup's `merged` and the judge's `verdicts` stop the pass. Every reply schema in the two drivers now types its required fields, so the runtime can refuse a mistyped reply at return.
  - The gatherer's label stays `gather` on every box: the base's `check-wave-script.mjs` keys its stub on that label (decision 0013).
- **M3 (RCA): the predictor names each arm's repair.** `ci_predict.py` used to end a refusal with "who repairs which is ci-autofix.md's". It now prints a `CI PREDICT:` repair line for each arm:
  - UNDER-SCOPED: `tests/derive_closures.sh --single <script>` for every named script, with the sum of CI's last recorded seconds for them. More than three scripts are the orchestrator's to record on Linux.
  - UNCLASSIFIED: the file joins a closure, or goes on `INERT`.
  - INERT READS: #2376's `--apply-inert` line, unchanged.
- **M2 (RCA): `body_push.sh` is the handoff gate.** Before it pushes anything, it runs the static `ci_predict.py --base origin/main` in the code head's checkout. On a non-zero rc it refuses and prints the predictor's lines. A checkout with no predictor is refused too, so a skipped gate never reads as a pass. `ref_privacy.py`'s self-test, which drives `body_push.sh` in a planted repository that is not a code head, now plants a stub predictor there.

Alternatives considered:
1. Pass the schema in `args`, as `rotation` and `scopes` are passed. The base checker's drive passes no such argument, so this cannot be graded (decision 0013), and every launch would carry a fourth hand-supplied object.
2. Keep the hand copy and add the missing enums. That repeats (g) at the next schema edit.
3. One shared helper module for `replyField`. A workflow script imports nothing, so the two drivers each carry a copy, and both copies are pinned by the checker.
4. A full `prepr.sh` in `body_push.sh` (the RCA's M1). The RCA refused it on its cost test.

## Head

fc145b97c7cb8faaf34a0ae634233d3c9dad4c9d. It is the reviewed head 5f6d8fbd7, plus a merge of origin/main at 106af95a33f8 (git merge, 2026-10-18 18:19 UTC), plus two commits answering fix review round 1:

- 64f855dcb pins `audit-find.js`'s cut-off arm in `check-wave-script.mjs` (the blocking item; see Mutation proof).
- fc145b97c makes the harness's `--perturb` drop the `expected_direction` enum alone, as its header and printed label say. Before, it deleted every property under `perturbation`. `form_gap` under `--perturb` is 11 either way at this head.

The merge brought no conflict. Every figure below was re-taken at fc145b97c in this pass. Base is the merge base 106af95a33f8, which is also origin/main's tip at 18:19 UTC, in a detached worktree.

## Mutation proof

Each mutant was applied in a detached worktree at the head and restored after (`git status --short` empty after each):

- **The cut-off arm reads as empty** (`audit-find.js` `replyField`: `catch { throw ... }` becomes `catch { x = kind === 'array' ? [] : {} }`; the reviewer's R1). `node tools/policy/check-wave-script.mjs` ends at 197 passed, 1 failed: `...and one whose findings came back cut off is a seat not reported, refused with the field named, and intake does not run`. The same mutant on 5f6d8fbd7, which did not carry this case, ends at `197 passed, 0 failed`. That is the gap round 1 found: the body claimed the arm and no check pinned it.
  - The case drives D1-s2's findings as JSON text cut at 25 characters. It requires `missing` to be exactly `["D1-s2"]`, no intake call, and a log line `D1-s2's report: findings: ... does not parse ... not reported`. The drive stub now records the log lines, so the refusal itself is read.
  - Its null control is the case above it: the same findings as whole JSON text are read as findings (`a finder report whose findings came back as JSON text is read as its findings, not as none`).
  - A second mutant keeps the refusal but drops its log line (`log(...)` becomes `void e`). It also ends at 197 passed, 1 failed, on the same case.
- **`replyField` returns the reply as given** (in both drivers): the checker ends at 193 passed, 4 failed:
  - `a box reply returned as JSON text is parsed: every seat reported, intake runs (null control for the cut-off arm)`
  - `a finder report whose findings came back as JSON text is read as its findings, not as none`
  - `...and one whose findings came back cut off is a seat not reported, refused with the field named, and intake does not run`
  - `the panel verification pass threw: reg.findings.map is not a function`
- **Fold without `sync`** (`fold()`'s `sync(root)` replaced by `pass`): `python3 tools/audit/fold_ledger.py --self-test` prints 4 FAIL lines:
  - `a minted class reaches audit-find.js's CLASS_GUESS, the intake's third reader of the enum`
  - `and FINDING_REPORT, the schema with its $ref inlined: the finder's return schema carries the new enum`
  - `the lines outside the block are kept, and a second sync changes nothing (idempotent)`
  - `null control: a fold that mints nothing still writes the block from the unchanged enum`
- **`FINDING_REPORT`'s `expected_direction` enum hand-dropped:**
  - the checker ends at 197 passed, 1 failed: `the finder's return schema is finding.schema.json itself, $refs inlined, plus report_path (its enums and types reach the finder)`;
  - `node tools/policy/agreement.mjs --py-json <agreement_py.py --out>` prints `DIVERGENT finder-report-form ".../perturbation/proper...` for each of the four values (`up`, `down`, `to_zero`, `sign_flip`), then `RESULT divergent=4`.
- **`repairs()` returns nothing, and `body_push.sh`'s predictor call is disabled** (`if false && ...`): `bash tools/pr/prepr.sh --self-test` ends at 287 passed, 3 failed, rc 2:
  - `an UNDER-SCOPED prediction names --single for its scripts, not ci-autofix.md's wait (M3)`
  - `an UNCLASSIFIED prediction names the classification, a closure or INERT (M3)`
  - `body_push refuses the probe head (a new harness, no inert_reads line) and pushes no body (M2)`
- **Failing first:** the head's `check-wave-script.mjs` run over the merge base's two drivers ends at 188 passed, 9 failed. Among the failures are `from "intake" gathers once per box ...`, `a box whose reply is cut off leaves exactly its own seats missing ...`, `...and one whose findings came back cut off is a seat not reported ...`, `the finder's return schema is finding.schema.json itself ...` and `the panel verification pass threw: reg.findings.map is not a function`.

## Null control

The unmodified tree, the merge base 106af95a33f8, does the following:

- **Harness.** `dev/audit/harnesses/r10_tick_drivers.py --tree <base worktree> --evidence .` reads `form_gap=35`, `form_driver_rej=0`, `gather_replies=1`, `gather_max_kb=193.9`, `text_read=-1` (the verify driver throws) and `text_gather=-1`.
- **Harness null controls.**
  - `form_file_rej=35` and `form_both_ok=9` are the same at base and head. The file's verdict does not depend on the tree, so the 35 to 0 move is the driver's schema.
  - `gather_missing=3` is the same at both ends. Round 10 ran D15's three seats on a box B11 that `BOXES` does not have, so neither driver gathers them. That is not this change's seam.
  - The perturbation `--perturb` drops the `expected_direction` enum from the head's return schema. It returns `form_gap=11` and `form_driver_rej=24`.
- **The cut-off pin.** Whole JSON text for the same findings is read as findings; only the cut text is refused (Mutation proof, first item).
- **The predictor gate.** On the null branch `pnull` (a comment in a selectable script), `prepr.sh --self-test`'s arms show `body_push.sh` pushing the body (`body_push pushes a head the predictor is quiet on (null control)`) and no repair line printed (`and a quiet diff prints no repair (null control)`).
- **`sync` with no new class.** `fold`'s self-test writes the block from the unchanged enum (`null control: a fold that mints nothing ...`).

## Figures

All at head fc145b97c unless marked base (106af95a33f8, a detached worktree).

- **This group's harness at both ends.** `python3 dev/audit/harnesses/r10_tick_drivers.py --tree <tree> --evidence .`, sha1 `b99267a74632b9c1bbd15181b009f3dab2ec9c09`. The R10-TICK-DRIVERS fixer wrote it, as its header says; the finding's own evidence carried no committed harness. Its interpreter needs `jsonschema`, which `tests/requirements-ci.txt` does not pin; this pass ran it under a venv with the seat's interpreter's packages plus `jsonschema` 4.26.0. The rule: each finding in `dev/audit/rounds/round10/reports-B*.json` is validated with jsonschema Draft 7 against `finding.schema.json` and against the return schema the driver hands its first finder call.
  - `findings=44` at both ends.
  - `form_gap` (rejected by the file, accepted by the driver): base 35, head 0, head with `--perturb` 11.
  - `form_driver_rej`: base 0, head 35, head with `--perturb` 24.
  - The largest single gather reply in KiB of JSON (`gather_max_kb`): base 193.9, head 34.0. `gather_replies`: base 1, head 10.
  - `text_read`, the findings reaching the judge from a register read returned as one JSON string: base -1, head 44. `text_gather`: base -1, head 3.
- **Class seams.** The rule: `grep -cE "schema: \{ type: 'object', required: \[[^]]*\] \}" .claude/workflows/*.js` counts reply schemas that declare required fields and no types.
  - In the two round drivers: base 3 + 9, head 0 + 0. Closed in this diff.
  - Returned outside this group's file set: `audit-fix.js` 2 (`pr`/`head_sha`, `verdict`; RETIRED), `web-decomp-stage.js` 4, `web-fix-wave.js` 1 and `web-stamp.js` 3. Every one is a scalar reply (`pr`, `head_sha`, `verdict`, `proceed`, `green`, `stamped`). No collection is iterated and no reply is round-sized, so the size arm does not apply.
  - The type-drift arm is unmeasured for those 10: a `green` returned as the string `"false"` would read as true. It is not carried (finding-propagation: an unverified observation is measured first or dropped) and is not fixed here.
- **The checker.** `node tools/policy/check-wave-script.mjs`: head `198 passed, 0 failed` (a `FAIL (probe, expected)` line is the checker's own self-probe). Base drivers with the head's checker: `188 passed, 9 failed`. The base's checker run over the head's drivers: `187 passed, 0 failed`. That last run is what `wave-script` runs on this PR.
- **Agreement.** `python3 -I tools/policy/agreement_py.py --out F; node tools/policy/agreement.mjs --py-json F` prints `pair finder-report-form: 2 readers, 214 items, 0 divergent` and `RESULT divergent=0 unregistered=0 dead=0 refused=0`. `node tools/policy/agreement.mjs --self-test` prints `SELF-TEST 13 of 13 probes held`.
- **Fold.** `python3 tools/audit/fold_ledger.py --self-test | grep -c FAIL` prints 0. `python3 tools/audit/fold_ledger.py check`: `0 violation(s)`. `python3 tools/audit/fold_ledger.py sync`: `already carries dev/audit/config/finding.schema.json`, and `git status --short` is empty after it.
- **prepr's self-test.** `bash tools/pr/prepr.sh --self-test`: `290 passed, 0 failed`, rc 0. This change's arms are three M3 arms (UNDER-SCOPED and UNCLASSIFIED name their repair; null control) and four M2 arms:
  - `body_push refuses the probe head (a new harness, no inert_reads line) and pushes no body (M2)`
  - `and pushes it once --apply-inert's entry is committed`
  - `body_push pushes a head the predictor is quiet on (null control)`
  - `and refuses a checkout with no predictor rather than passing it silently`

  The bodies go to a throwaway bare repository, never to a remote.
- **The predictor.** `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` prints `CI PREDICT: no closures or fast red predicted against 106af95a33f8`, so `body_push.sh` passes this head.
- **Gate.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, the script being `tests/entities.py`.
  - `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py` prints `ALL 2347 ENTITY CHECKS PASSED`.
  - run_always: `tests/closure.py selftest` `ALL 115 closure shrink pins PASSED`; `tests/layout.py` `layout self-test: ok`; `tests/env_drift.py --claims-only origin/main` `claims hygiene: origin/main ok`; `tests/harness_headers.py` `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`.
  - `python3 -I tools/audit/seat/ref_privacy.py --self-test`: `66 checks, 0 failed`. `--check`: `0 refused`. `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`. `python3 -I tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused`.
  - No golden fixture is in any changed file's closure, so `GOLDEN_MODE=drift` has nothing to measure.

## Red checks

- **instrument-self-tests** (job 117649560197, head 03c0766bf). It went red on `REFUSE tools/pr/prepr.sh:2054: BPO=$(cd "$PDX/r" && git remote get-url origin); git init -q --bare "$PDX/bodies.git"` and `throwaway_git: 1 raw git init or clone site(s) refused`. The cause is in this change: the new M2 self-test arms built their bare repository with a raw `git init`, not through `tests/throwaway_git.sh`'s helper as every other `prepr.sh` site does.
  - Repair, db9267d4: `throwaway_git_init "$PDX/bodies.git" -q --bare`. At this head, `python3 -I tests/throwaway_git.py --check` prints `0 raw git init or clone site(s) refused`.
  - The cheaper detector is `python3 -I tests/throwaway_git.py --check`, a tree scan that takes seconds, together with its `--self-test`.
  - `prepr.sh` does not run it. Step 7 runs `tools/audit/seat/tmp_paths.py --self-test` and `--check`, and no `throwaway_git.py`. That is the gap that let this red reach CI. Closing it is a one-line `prepr.sh` addition beside the `tmp_paths.py` call, at a standing cost of seconds per prepr run. It is not taken here: the orchestrator ruled that no new findings go into #2390.
- **pr-contract** (job 117650396148, head 03c0766bf), red. Its log could not be read from this seat: the log blob host is refused by the session proxy, and the job's only annotation is `Process completed with exit code 1`. The cause on record is the orchestrator's: the body's `## Red checks` read `none` while instrument-self-tests was red. That body named it, and pr-contract was green at 5f6d8fbd7.
- No check went red on db9267d4, d95f4431 or 559b8bda. 5f6d8fbd7 had no failed check when fix review round 1 was posted, with coverage and CodeQL still running. This head has had no CI run yet.

## Unpinned sites

`ci_predict.py` predicts no ADDED UNPINNED site, because every changed line is outside the mutation inventory. Each changed behaviour is pinned by a self-test that CI runs, as the mutation proof records: `check-wave-script.mjs` and `agreement.mjs` (governance `wave-script`), `fold_ledger.py --self-test` (governance), `prepr.sh --self-test` (through `tests/entities.py`), and `ref_privacy.py --self-test` (governance). The cut-off arm of `audit-find.js`'s `replyField` was the one claimed behaviour without a pin until 64f855dcb.

## Forward-carry

none. The roster's carry, that R10-D15-GRADER and R10-BRIEFS-FOLD edit the wave-script check after this group, constrains this branch rather than a later stage. R10-D15-GRADER is already done and is in this merge base. R10-BRIEFS-FOLD's files are the dimension briefs, `scopes.json` and `rotation.json`, none of which this change constrains. A later hand edit of `finding.schema.json` is refused by `agreement.mjs`'s `finder-report-form` pair until `fold_ledger.py sync` runs, as `tools/audit/seat/INSTRUMENTS.md` and the block's own header say. Not landed here, because it is policy and the owner's: the RCA's M4 wording for `ci-autofix.md` and `fixer.md`.

## Friction

dev/governance/roles/fixer.md#18: cost: this group's harness imports `jsonschema`, which no pinned requirements file carries, so the seat interpreter cannot rerun it as committed; this pass ran it in a scratch venv with `jsonschema` added.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
