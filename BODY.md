#3885 item 2 (owner, 11-25, #3394 comment 7157667401): on a pull request, tests/features.py and tests/entities.py run a seeded 30% sample of their cases; pushes to main and the nightly run every case. Refs #3885.

**Measured result: the sample saves nothing at today's table.** That matches the stop rule in the design note on `design/r11-ci-3885-rest` (f139601cee, §5). entities.py on #3936's file list ran in 612.6 s whole, and in 588.2 s and 619.6 s sampled. The `needs` closure adds back almost every span the draw drops (61 of 65 ran). The plan, draw, seed and routing stand, and P2a/P2b own the gain. Whether to merge before them is the orchestrator's call (§5 stop rule) and the owner's (the tests.yml line, below).

What changed:
- `tests/case_select.py` gains `plan`, `draw` and `sampled`. Its CLI gains `plan <script>` and `run <script> --sample`. The run set is back*(diff ∪ edited ∪ forward(diff ∪ edited) ∪ sample(rest)), with rules (i)-(v) as `design/R11-CI-CASE-SELECT` 25fa1f76 defines them. The draw keeps a span when sha256(seed NUL span id) is below 0.3·2⁶⁴. It is keyed on the id, never the ordinal. A span the diff reaches is labelled before the draw and is never drawn.
- The seed is `HPO_CASE_SEED` = `<PR number>-<head sha>`. `tests.yml` exports it on `pull_request` only, never from `github.sha`. The plan prints it in its `CASES: PLAN` line, along with the base and one `case <rule> <id>` line per span. The `CASES: SCOPED|FULL ... k of n spans (...)` line carries the same seed. To replay a red locally: `python3 tests/case_select.py run <script> --sample --seed <seed> --base <base>`.
- `tests/run.sh`: `run` sends the two scripts through `case_select.py run --sample` only when `HPO_CI_EVENT=pull_request` and `GATE_SCOPE=auto`. Every other event and scope runs `python3 <script>` unchanged. `scope_script` skips `tests/case_select.py`, so the shard, lease and manifest still key on the script.
- Fail-safes (FULL, with the reason printed):
  - no seed, or a seed of the wrong shape
  - no table entry, or a header_hash mismatch
  - no spans, or no changed files
  - a gate file (other than `tests/closures.json`), `tests/harness.py` or `tests/hastub/` changed
  - the script-level scope is FULL
  - a repeated title has a moved instance
  - and two arms beyond the approved list, both tightenings: a changed unit that the header reads (other than the script itself), and a changed unit that is in the script's closure but in no span's recording.
- `tests/case_closures.json` was re-recorded on Linux at ac9045c223 (`tests/derive_closures.sh --cases`). The table from f184477ba8 matched neither script's header, so every plan read FULL. features.py gains its 4 unrecorded spans (252).
- `dev/audit/harnesses/ci3885_sampling.py` holds this body's mutants, routes, null controls and census.

Departures from the design note, each decided by the brief:
- The seed includes the PR number ("Derive it from the PR number and the head").
- Rules (i) and (iii) ship now, not in P2d ("a case the diff reaches is never sampled out").
- The approved "blob matches neither base nor head" arm is not built. Per-span hashes and the header hash already cover staleness span by span, and the blob arm would read FULL on every PR (both blobs differed from the table at the base).

Policy: the `.github/workflows/tests.yml` line is a gate-file and policy change (the design note's carry item policy-tests-yml). It needs the owner's approval before merging.

## Head

d928f6ad9819984b732a38ef82317b10afc42704, measured on origin/main ac9045c223721608e684c8a2213831aa34c1fa4f. Body written 2026-11-28 (UTC).

## Mutation proof

`python3 dev/audit/harnesses/ci3885_sampling.py mutants` edits one predicate of `plan`/`draw` at a time, runs `tests/case_select.py --self-test` and restores the file after each. Result: `MUTANTS: 15 of 15 killed`. Each mutant and the self-test row it fails:
- draw keyed on the ordinal: "draw: an inserted id moves no other id's draw"
- rule (i) removed: "rule (i): a span whose recorded files meet the diff runs as diff"
- rule (ii) removed, and rule (iii) removed: "rule (ii)+(iii): an edited span runs as edited and the span reading what it binds runs as forward"
- rule (v) removed: "rule (v): alpha#2 alone in the diff pulls in alpha as needed"
- draw over the diff's spans too: "rule (iv): at fraction 1 every other span is drawn, and the diff span stays diff"
- each fail-safe arm removed (header-files, closure-not-recorded, gate/runner, header-hash, seed shape, script scope, repeated title): that arm's "fail-safe: ..." row. Each row asserts its own reason string, not only FULL.
- the closures.json exclusion removed, and the script's own file kept in the header arm: the matching "fail-safe null: ..." row.

`python3 dev/audit/harnesses/ci3885_sampling.py routes` drives entities.py's new `_csel_routes` pin against run.sh, then against run.sh with the `HPO_CI_EVENT = pull_request` test removed. The tree reads PASS (24 cells). The mutant reads FAIL: push/auto and workflow_dispatch/auto then route through `--sample`.

No added line is outside `tests/` and `dev/`, so prepr's `MUTANT_CMD` draw has no site.

## Null control

- **Null control 1 (every case runs off a pull request).** The routing pin gives the run.sh path for 8 (event, scope) pairs × 3 scripts. Only `pull_request`/`auto` routes the two scripts through `--sample`. `push` (auto and full), `schedule`/full, `workflow_dispatch`, `merge_group`, `pull_request`/full and local all run `python3 <script>`. Count against the unsampled run (`ci3885_sampling.py count`):
  - `python3 tests/features.py`: 252 of the 252 span titles that split cuts printed as headings (exit 0, `ALL 6322 FEATURE CHECKS PASSED`). The log has 268 headings, because a nested `section` call prints one too, which is why titles are counted rather than headings.
  - `python3 tests/entities.py`: 65 of 65.
  - The sampled entities.py run (the would-be-false arm): 61 of 65, beside `CASES: SCOPED tests/entities.py -- 61 of 65 spans`.
- **Null control 2 (byte-stable).** `ci3885_sampling.py stable <script> 3936-5a8b4e65fa92e3ddd3123b8d69b6ffd39438df73 <#3936 files>` printed "byte-identical over 3276 bytes" for entities.py and "byte-identical over 16090 bytes" for features.py, two runs each. Between the two sampled entities.py runs, the case set (the `-- ` headings, `CASES:` lines and summary) is byte-identical (`cmp`). Their full logs differ only inside nested negative-control fixture output: a set-iteration order inside `a8:register_once`, and a retry count inside `hb:positive_control`.
- **Draw null.** A different seed draws a different set, fraction 0 draws nothing, and fraction 1 draws everything (self-test rows).

## Figures

- Table re-record: `PYTHONPATH=tests/hastub bash tests/derive_closures.sh --cases` at ac9045c223 → `recorded 252 span(s) of tests/features.py`, `recorded 65 span(s) of tests/entities.py`, both exit 0.
- `python3 tests/case_select.py stats tests/features.py` and `stats tests/entities.py`: the per-script span seconds the census divides by.
- Wall time, one representative PR head (#3936, merge aee9548a47, tooling only, file list `git diff --name-only aee9548a47^1 aee9548a47`). Sequential on this 4-core container, with `OMP_NUM_THREADS=1`:
  - `python3 tests/entities.py`: 612.6 s
  - `python3 tests/case_select.py run tests/entities.py --sample --seed 3936-5a8b4e65fa92e3ddd3123b8d69b6ffd39438df73 --files <list>`: 588.2 s, then 619.6 s. Plan: 61 of 65 spans (2 diff, 1 edited, 13 forward, 10 sample, 35 needed).
  - features.py is not in that diff's script-level scope. No saving above the run-to-run spread.
- `python3 dev/audit/harnesses/ci3885_sampling.py census 30` (main's last 30 first-parent merges, replayed against this tree's table, with each merge's first-parent closures as select's base):
  - `CENSUS: entities.py full 19, entities.py scoped 11, features.py full 18, features.py not selected 10, features.py scoped 2`.
  - No scoped plan ran under 0.97 of the script's recorded span seconds.
  - FULL reasons: gate files (ci.yml, tests.yml, tools/ci/), and the header arm on every production merge.
- `python3 tests/case_select.py --self-test`: `CASE-SELECT SELF-TEST: PASSED (51 checks)`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

none

## Forward-carry

- The measured null gain and the §5 stop rule, for P2a/P2b/P2d, land in `dev/programme/carries/carry-3885.json`. Carry: #3885
- The header-hash arm turns sampling off from the first header edit after a recording, so P3's autofix must re-record on a header_hash move. Lands in `dev/programme/carries/carry-3885.json`. Carry: #3885
- The header-files and closure-not-recorded arms make every production diff FULL; narrowing them belongs with P2b and the soundness replay. Lands in `dev/programme/carries/carry-3885.json`. Carry: #3885

## Friction

none
