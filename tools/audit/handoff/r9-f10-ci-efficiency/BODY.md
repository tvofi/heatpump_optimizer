<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi** · [project thread](https://claude.ai/code/project/chan_01EL5jLi4rokGBbkaevYXSJV?thread=cmsg_01EL5jLi4rokGBbkaevYXSJVXm5wUkXJMfqLfw8yQkDvTP)_

R9-F10.9b, part 2 of #1812 (closes it with #1815's part 1).

Before: every pull request's `coverage` job re-ran all 17 coverage-stage scripts under the tracer (main's run at 90335cbd: 23.5 minutes of script time, `tests/features.py` 854 s of it), whatever the diff touched. `mutation` ran every driver's baseline and null control before its first mutant, 17 minutes on #1806 where `tests/features.py`'s 712 s baseline killed nothing (`ci-scoping-audit.md`).

After: `coverage` re-measures only the scripts the gate's own scoped plan runs for the diff and takes every other script's coverage from the push run at the diff's base, so the ratchet grades the same `coverage.json`. Under `--scope changed`, `mutation` runs a shared driver's baseline and null control only when one of its mutant runs comes back red; every kill is still judged against them. `tests/harness_headers.py` stays `run_always` (#983), now with the measured reason in `tests/run.sh`.

How. `tools/audit/w5-partition/coverage_tree.sh` writes each script's data to `per/.coverage.<name>` and combines that directory; with `W5P_SCOPE` (the diff's `closure.py select` plan) and `W5P_REUSE` (the base's `per/`) set, `closure.py coverage-split` names the scripts to copy instead of run. `tests.yml`'s `coverage` job keys an `actions/cache` entry on the base commit plus the instrument, the three locks and the interpreter; a push to main saves it, a pull request restores it by exact key, and a miss measures everything. `mutation_table.py` gains `lazy_drivers()` and `LazyBaselines`; main's push and the nightly are unchanged.

**Barrier argument, coverage.** A script is reused only when the plan is SCOPED and skips it, which is the gate's claim that no changed file is in its measured closure; the tracer records lines only in files the script executes, so its data at the base is the data it would produce on the merged tree. Every other case measures: FULL plans (gate files, unmapped files, `tests.yml`), scripts the plan runs, a cache miss (an instrument, lock or interpreter change is a different key), and a script with no base file. The push to main still measures all 17 scripts unscoped, so a wrong closure fails there within one merge, as for `fast`. A case the old scope ran and the new one skips: #1811's diff reuses `tests/features.py` (no changed file in its 0bfb8883 closure; `scope.json` below), and the coverage that run produces is byte-for-byte the line set of the full run.

**Barrier argument, mutation.** `killed()` is `run.rc != 0 and failing_count(run) > failing_count(baseline)`, and `failing_count` of a green run is 0, so a green mutant run is no kill under any baseline and needs none. A red one waits for the driver's baseline and null control, run once (per-driver lock) on that worker's restored tree. A red baseline or killed null still returns INCONCLUSIVE or REFUSED, as soon as a red run needs it. What moves is the headline when no mutant run of a driver is red: its baseline and null, which no verdict then reads, are never run, and the table says so ("LAZY AND NEVER RUN"). That is the trade #1611 made for `stress.py` with `deferred_drivers`. Ref-driven `env_drift.py` stays eager (its recorded seconds time a stub, closure.py #934); `--scope full` stays eager. Lazy drivers are ordered by `tests/closures.json`'s recorded seconds; order names the killer and never changes a verdict (`driver_order`).

**#983 examined, not adopted.** Under strace, `tests/harness_headers.py` opens five INERT files in content (`DISCLAIMER.md`, `LICENSE`, `docs/audit-2026-08.md`, `docs/audit-2026-09.md`, `docs/backlog.md`), the docs ones through `tools/audit/round4/D6/claims.py`, and stats 29 more INERT ones. An INERT path is in no closure, so a docs-only diff that moves a D6 RESULT line would select nothing that runs it: the #968 to #979 shape. Re-scoping would save 95-183 s of `fast` on about half the PRs (`ci-scoping-audit.md`) and lose that barrier, so it stays.

**Other candidates examined.** Every `ci: re-record closures` commit still selects `tests/entities.py` (~4 min): it reads `tests/closures.json`, so skipping it hides a red; not adopted. Pip caching: install steps run 16-31 s per job and `env_drift`'s cache key fingerprints the installed set, not the download; saving under a minute of wall clock, not taken in this PR. Superseded-run cancellation and the merge queue are R9-F10.9c's; the harness_headers sysid timeout is R9-F10.11's.

## Head

af2ac763

## Mutation proof

`coverage_split` (`PYTHONPATH=tests/hastub python3 tests/closure.py selftest`):
- `s not in skip or s not in reusable` → `and`: `FAIL scoped: only a skipped script with base data is reused`, `FAIL scoped, cache miss: nothing is reused` (2 of 28 pins).
- mode check removed: `FAIL a plan of no known mode measures every script` (1 of 28).
- `skip - run` → `skip | run`: `FAIL scoped: only a skipped script with base data is reused` (1 of 28).

`LazyBaselines` (`PYTHONPATH=tests/hastub python tests/entities.py`, Python 3.13):
- green-run guard removed: `FAIL a lazy driver's green run settles nothing; ...  [out=[False, [(0, 'tests/a.py')], [True, True], 1]]`, 1 of 2029.
- per-driver lock removed: same check, `[out=[False, [], [True, True], 2]]` (two settles), 1 of 2029.
- refusal not stored: the refusal check's call raises `KeyError` and `entities.py` exits non-zero before its summary.

## Null control

- Old instrument against new on the same tree: `coverage_tree.sh fast` at 0bfb8883 (A) and at the head (B), both full: 98.33 %, 18146 of 18455 statements, 0 files differing in executed lines.
- Reuse against measure: B's `per/` reused for #1811's diff (C): 14 scripts reused, 3 measured, 0 files differing from B. Had the per-script combine lost data, C would differ from B; had reuse copied nothing, C would lack `tests/features.py`'s 854 s of lines.
- `coverage_split` with no base data, or a non-SCOPED plan, measures every script (selftest pins above).

## Figures

`$EXPORT` is `tools/audit/handoff/r9-f10-ci-efficiency/` on the transport commit above the code head (branch handoff/r9-f10-ci-efficiency); neither script is in this pull request's tree.

- Coverage equivalence, A against B and B against C: `python3 $EXPORT/cmp_coverage.py <first>/out/coverage.json <second>/out/coverage.json` (sha1 2eb308b897d9…), each tree from `W5P_WORK=<dir> PYTHON=python tools/audit/w5-partition/coverage_tree.sh fast` (C with `W5P_SCOPE=<scope.json from closure.py select --files $(git diff --name-only 90335cb^1 90335cb)>` and `W5P_REUSE=B/out/per`), Python 3.13.14, coverage 7.13.1.
- Per-script seconds and the 23.5-minute total: main's coverage job at 90335cbd, run 36889470932, job 110461123411, its `ran tests/<s>.py ... wall=` lines.
- Replay over the 16 PRs merged since #1795 (each tree's own `closure.py select --diff M^1`): `python3 $EXPORT/replay_coverage_scope.py` (sha1 013f8460e764…) at origin/main 0bfb8883. 6 of 16 measure fewer scripts; script time 282.5 of 376 minutes, 93.5 saved; 6 FULL plans and 4 production PRs save nothing. Counted per merged tree, not per CI run.
- #983: `strace -f -e trace=open,openat,openat2,stat,newfstatat,statx,access,execve,readlink python tests/harness_headers.py`, then `closure.is_inert` over the repo paths it opened: 7 opened INERT (5 files plus 2 `__pycache__`), 36 touched.
- Mutation minutes: not measured locally (a run is 20-56 minutes on CI). This PR's own `mutation` job runs the lazy path (its diff changes test scripts, so their closures' production files are mutated); its log carries the `LAZY AND NEVER RUN` lines and the baseline seconds.

## Red checks

none

## Forward-carry

`tests/run.sh`, the comment above `run_always "$PYTHON" tests/harness_headers.py`: it must stay `run_always`, because `tools/audit/round4/D6/claims.py` reads INERT docs. R9-F10.11 touches that script's timeout, so its roster brief on handoff/audit-r9-fixplan should carry the same line; sent to the coordinator to add.

Closes #1812

## Friction

- fixer.md-5: cost: a PostToolUse formatter hook in this cloud environment rewrote tests/closure.py (565 insertions, 267 deletions) on the first editor edit; reverted with git checkout, and every later edit was a scripted replace (process review item 5, the setup script).
- fixer.md-5: unclear: not run here: real-HA ha_contract, mypy on 3.14, stress.py and the full gate; CI runs FULL on this pull request (tests.yml and closure.py are gate files).

🤖 Generated with [Claude Code](https://claude.com/claude-code) · https://claude.ai/code/session_01CmRweYe1RMDfcFKazXWE9b
