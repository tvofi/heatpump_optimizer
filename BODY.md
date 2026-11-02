Part 1 of R10-SUITE-HOST-DETERMINISM (issues #2726, #2730): the suite's host-zone, gate-lease-timing and coverage-descendant nondeterminism. Parts named under Forward-carry are not built here.

## Re-cut note

Round 2, answering verdict/3170 at b307f359: "features.py still fails 3 zone checks at the head under America/New_York and Asia/Tokyo; only Europe/Stockholm was measured". This body is retaken whole. Figures re-taken in this pass are the features zone figures, the harness null and mutants, the scoped gate, structure and harness_headers; the round-1 coverage and gate-lease figures are carried as round 1's, with no change to the files they measure (`tools/coverage/coverage_tree.sh`, `tests/gate_lock.py` and `tests/entities.py` are untouched in round 2). No other figure moved.

Carries, each named as built, discharged or next part:

- Carry 1 and Carry 4 (0-based 0, 3; features under a non-UTC zone): BUILT, now for every zone measured. Round 1 fixed the six checks red under Europe/Stockholm. Round 2 fixes the four still red under America/New_York or Asia/Tokyo at b307f359, each a test that named an instant as a naive or UTC literal while the production read takes the configured zone's wall clock:
  - "with no meter, a month of DHW-only mornings bills ...": the production fold stamps the sample with `dt_util.now()`, so the tariff's hour and day masks read the configured zone; the month and its oracle were built in a hard-coded Europe/Stockholm. The month is now built in `DEFAULT_TIME_ZONE`.
  - "#943: the honest sizer leaves a power-limited heavy house at the full nameplate step ...": `SystemIdentification` gates the start on `now.hour` against the night window; `_943_drive`'s 02:00 UTC is 11:00 in Tokyo. t0 is now 02:00 in `DEFAULT_TIME_ZONE`.
  - "a naive stored tick adopts the clock's zone and detects the same gap": the naive tick was the UTC wall clock; production adopts the clock's zone for it. The tick is now the same instant's wall clock in `DEFAULT_TIME_ZONE`.
  - "the humidity entry nearest NOW wins, not the first in the list": a naive frozen clock is configured-zone wall time, and a naive entry stamp is read as UTC against it, so the two named different instants. `_T6_HUM_NOW` is now aware UTC.
  None is a production zone defect: each production read already used the configured zone, as the HA contract states, and each test assumed that zone was UTC or Stockholm. No `TZ` or `HASTUB_TZ` is pinned in the suite or the runner.
- Carry 2 (0-based 1; gate-lease one-winner flake): test-side change BUILT in round 1 (a condition wait replaces the 0.15 s hold; the planted O_EXCL-then-write control stays red). The production cause the round-1 reviewer demonstrated, the `_free_slot` is_file TOCTOU in `tests/gate_lock.py` (`_read_at` sees no file, the rival's `os.link` lands, the re-check unlinks the live slot), is NOT built here: the round-2 brief scopes this round to the features zone finding and says nothing else changes. It stays open in this carry; see Forward-carry.
- Carry 3 (0-based 2; coverage_tree.sh descendants): BUILT in round 1. `measure()` waits for processes still carrying the script's own `COVERAGE_PROCESS_START` rcfile path and refuses, naming the script, after `W5P_DESCENDANT_WAIT` (default 300 s).
- Carry 5 (0-based 4; base-red entities U0c / delivery_status): NEXT PART.
- Carry 6 (0-based 5; scan("HEAD") vs working tree): NEXT PART.
- Carry 7 and Carry 8 (0-based 6, 7; stdlib sampler macOS platform rule, six wrappers): NEXT PART.
- Carry 9 (0-based 8; nightly respawn): NEXT PART.

The `coordinator.py` change the round-1 reviewer flagged is still in the diff, and it is 4 lines of docstring in `_comparable_ts`, no code. The old text said an aware stamp against a naive grid "keeps its own wall clock"; the function returns `dt_util.as_local(ts).replace(tzinfo=None)`, the configured zone's wall clock, so the docstring now says that. The round-1 reviewer's AST comparison with docstrings blanked found base and head identical (verdict/3170 evidence/coordinator_ast.txt).

## Head

4119c8982dd8294847548625eaee4692a7481b4c, a fast-forward of the PR head b307f3599921ff345f677f34583958fa930a935a. No merge of origin/main: `git merge-tree --write-tree origin/main HEAD` exits 0 against origin/main 3905069f38a6 (fetched 2026-11-02, after 11:01 UTC). The features zone figures and the mutant runs were taken at 8f2bcb30a616; the one later commit (4119c898) changes only how `host_zone_features.py` finds the repository root (the `harness_headers.py` depth-root rule), and `harness_headers.py` was re-run on it. `tools/pr/prepr.sh` with this body ran on 4119c898 to rc=0, its `closures` step printing its own skip ("the diff cannot be scoped, so CI re-records every closure"); origin/main was still 3905069f38a6 after it, so no second run was owed.

## Mutation proof

Each mutant restores one fixed site's host-zone read, run by `python3 dev/audit/harnesses/host_zone_features.py --mutant all` in a detached worktree at 8f2bcb30a616, under UTC, America/New_York, Asia/Tokyo and Europe/Stockholm (`HASTUB_TZ` and `TZ` both set). Each reads red on exactly its own check and on no other:

- `nometer_month` (month built in `_BO_TZ`): KILLED. New_York 1 of 4770 and Tokyo 1 of 4770 failed, "with no meter, a month of DHW-only mornings bills what the stated rule bills on the commanded kW, every catalog row"; UTC and Stockholm passed.
- `sysid_night_t0` (t0 at 02:00 UTC): KILLED. Tokyo 1 of 4770 failed, "#943: the honest sizer leaves a power-limited heavy house at the full nameplate step, inside the allowance"; the other three passed.
- `outage_naive_tick` (naive tick as UTC wall clock): KILLED. New_York 1 of 4770 failed, "a naive stored tick adopts the clock's zone and detects the same gap"; the other three passed.
- `humidity_now` (naive `_T6_HUM_NOW`): KILLED. New_York and Tokyo 1 of 4770 each failed, "the humidity entry nearest NOW wins, not the first in the list"; UTC and Stockholm passed.

The harness exits 1 on any SURVIVED; it printed four KILLED and exited 0. Round 1's coverage mutation (replacing `wait_descendants "$s" || return 1` with a no-op fails exactly the late-writing-descendant entities row, 1 of 2593) stands; `coverage_tree.sh` and that row are unchanged in round 2.

## Null control

`python3 dev/audit/harnesses/host_zone_features.py` with no mutant, at 8f2bcb30a616: `ALL 4770 FEATURE CHECKS PASSED` under each of UTC, America/New_York, Asia/Tokyo and Europe/Stockholm (exit 0). At b307f359, the same per-zone command read America/New_York 3 of 4770 failed and Asia/Tokyo 3 of 4770 failed, with Stockholm and UTC all passed: exactly the verdict's figures and names, so the harness reads the defect at the old head and not at the new one.

## Unpinned sites

none: round 2 adds no production line. The added lines are in `tests/features.py`, `tests/closures.json` and a harness under `dev/audit/harnesses/`; `prepr.sh` step 6d lists no site.

## Figures

The class rule (fixer step 8): every features check red under any of the four zones is a seam. `python3 dev/audit/harnesses/host_zone_features.py` enumerates them, a full features run per zone printing each FAIL name. At b307f359 it returned four distinct seams (the DHW-only month, the #943 sizer, the naive tick, the humidity read), each closed in this diff; at the head it returns none. Zones are the four the brief names; a zone outside them is not measured.

- `HASTUB_TZ=<zone> PYTHONPATH=tests/hastub python3 tests/features.py`, at b307f359: UTC all 4770 passed; America/New_York 3 of 4770 failed; Asia/Tokyo 3 of 4770 failed; Europe/Stockholm all 4770 passed.
- `python3 dev/audit/harnesses/host_zone_features.py` at 8f2bcb30a616: all 4770 passed in each zone (null control above).
- `python3 dev/audit/harnesses/host_zone_features.py --mutant all` at 8f2bcb30a616: four KILLED (mutation proof above).
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=$(git merge-base origin/main HEAD) ./tests/run.sh` at 8f2bcb30a616: `MODE: SCOPED -- 22 script(s) run, 11 scoped out`; features with the zone unset `ALL 4777 FEATURE CHECKS PASSED`, entities `ALL 2593 ENTITY CHECKS PASSED`, structure passed; two scripts failed, `tests/typing_ruler.py` (seat environment, see Red checks) and `tests/harness_headers.py` (the new harness's depth root, fixed in 4119c898).
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py` at 4119c898: `ALL 112 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tools/pr/ci_predict.py --base origin/main --apply-inert`: added the one INERT READS entry for the new harness; then no closures, fast, governance or instrument red predicted.

## Red checks

At b307f359, the whole check-run set (55 runs, one page of 100), every concluded red:

- `tests / replay` (125168587530): `1 of 176 replay checks FAILED`, synthetic-dhw-only.json cycle_cost `cpu_ratio 2.389` over its budget `2.173`. The diff writes no runtime code (the only `custom_components/` change is the `_comparable_ts` docstring), and `cpu_ratio` is a CPU-time ratio on a shared runner, so this is runner CPU noise, not a defect this diff introduced. A cheaper detector does not exist: the ratio is the measurement, and no static read predicts a runner's CPU contention. Round 2 also adds no runtime line.
- `pr-contract / pr-contract` (125179056639, 125180207180): red because the round-1 body did not name the replay red. Answered by this section.
- `gate` (125179329799, 125180528483): the aggregate of the two above.

Local, at the new head: `tests/typing_ruler.py` fails 1 of 12 source checks identically at the merge base (the pinned `/opt/hpo/venv-ha` census exits 1 in this seat's environment). No cheaper detector is owed: it is the seat's interpreter, not the diff.

## Forward-carry

- The gate-lease `_free_slot` is_file TOCTOU in `tests/gate_lock.py`, with the round-1 reviewer's delay-only plant as its control (red 2 of 10 at both the base and b307f359), is not built here and remains a part of this group's Carry 2 (0-based 1) in dev/programme/rosters/wave-r10-groups.json on handoff/audit-r10-roster. Carry: R10-SUITE-HOST-DETERMINISM
- Carry 5, Carry 6, Carry 7, Carry 8 and Carry 9 above are the next parts, remaining in dev/programme/rosters/wave-r10-groups.json (group R10-SUITE-HOST-DETERMINISM, 0-based carry indices 4-8, on handoff/audit-r10-roster). Carry: R10-SUITE-HOST-DETERMINISM

## Friction

none
