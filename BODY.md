Refs #3885

This PR leaves #3885 open: the duplicate-dispatch lever is carried to the next #3885 group.

Light grading for changes that touch no production file. A change is **light** when no
path in it is under `custom_components/`, is a root file HACS reads (`hacs.json`,
`README.md`, `LICENSE`), or is under `.github/` (`tools/ci/prelude.py`: `light`). A light
pull request, verified dispatch or push stands down the lanes whose reads the change does
not reach. Every required job name stays the same: each lane stands down at the step
level, and its job still concludes success.

- **Fix A** (c0dcc352f9): a non-code run whose units read no other run holds no runner while it waits.
- **Push range** (`prelude.push_range`): a push is graded over the range from the head of
  the newest earlier push run on main. That run must have started, must not have been
  cancelled, its prelude must have succeeded, and its head must be an ancestor of this one.
  `HEAD^1` is not a safe base: the `CI-main` concurrency group replaces a pending run
  (CI-5), so `HEAD^1`'s run may never have graded anything. When no such run is readable,
  the push stays unranged and is graded `full`.
- **Light push**: a push whose range is light is graded as a pull request over that range
  (`GATE_SCOPE=auto`, fast, selftests and arch-instrument scoped to it). A push whose range
  touches production runs `full`, as before.
- **Stand-downs** (`prelude.stand_down`, read by each lane's job env `STAND_DOWN`):
  - On every light event, `browser`, `typing`, `hassfest` and `validate-hacs` stand down
    unless the diff reaches that lane's own reads (its driver's measured closure in
    `tests/closures.json`, plus its named extras).
  - On every light event, `coverage` and `coverage-ratchet` stand down unless the diff
    touches `tests/` or `tools/coverage/` (ruling item 3). A push that stands coverage down
    re-marks its range base's trusted per-script entry at its own commit and saves it, so
    the next push still reuses that data. If there was no trusted entry, nothing is saved
    and the next push measures every script.
  - On a light push only, `closures` re-derivation and `env-matrix` stand down. The pull
    requests in the range ran both on their own diffs.
  - On every light event, CodeQL's python leg is skipped (ruling item 1). The next push
    that is not light analyzes it. A skipped leg uploads main's stand-in analysis, pinned at
    the range base on a push, and the D-5 extracted-files check runs only where an analysis
    ran.
- **Safety net, restated**: a push that touches production or `.github/` runs `full`, so a
  wrong closure reddens main at the next such push instead of the next push. `fast`,
  `closures` on PRs, `instrument-self-tests` and mutation keep running as scoped to the diff
  (ruling item 2). The nightly run covers only mutation, slow and nightly-ha. It does not
  cover the closures re-derivation.

Policy text this PR changes, which the orchestrator surfaces to the owner:
- `CLAUDE.md` rule 1, at exactly its 3,616-token cap;
- `tests/README.md`;
- `.claude/skills/steward/SKILL.md`;
- the GATE fragment in `.claude/workflows/web-fragments.md` and its four `web-*.js` copies.

`dev/governance/rules/gate-scoping.md` is not edited: it never stated the push rule, and it
has no token headroom.

Deviations from the brief, each with its reason:
- `.github/` is never light: those files are the lanes themselves.
- Production includes `README.md`, `LICENSE` and `hacs.json`: these are the root files
  `validate-hacs` checks (run 45328796343, job 138271567259).
- The base is a push run whose prelude succeeded: a failed prelude graded nothing.
- `closures` and `env-matrix` stand down on a push only.

## Approval

pending: the owner's approving review on the four policy files (CLAUDE.md, tests/README.md, .claude/skills/steward/SKILL.md, .claude/workflows/web-fragments.md); the orchestrator surfaces it, and under mandate 6893738184 (scope all) posts it as tvofi, declared.

What changes for a seat: a push to `main` is no longer always `full`. A push whose range touches no production or `.github/` path is graded scoped (`auto`) over that range, so its run prints the mode line a branch prints. The four `web-*.js` copies of the GATE fragment are generated from `web-fragments.md`.

## Head

7eb9b2fd81 (fix A c0dcc352f9 unchanged at the base of the range). Self-tests, mutants and the non-code prepr (`PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1`, rc=0) are at ce0283e1d0; 8736b08a17 only restores one `if:` in `graders-head-copy` to main's text and b8ad8c02dd and 7eb9b2fd81 only add `dev/programme/carries/carry-3885.json` and its entry in `tests/entities.py`'s closure (entities reads every carry file); `tools/pr/ci_predict.py` predicts no red at 7eb9b2fd81; `tools/ci/prelude.py --self-test` is green at both, and `brief_lint.mjs` reads the carry file clean.

## Mutation proof

`python3 dev/audit/harnesses/ci3885_light.py mutants` makes 16 mutants. Each one reverts one
production line of the fix in place and runs `tools/ci/prelude.py --self-test` (134 checks).
All 16 are killed, so 0 survived. Each mutant and the checks that kill it:

- M0 a non-code run holds a runner waiting -- the Fix A checks
- M1 a cancelled (replaced) run counts as a base -- `#3885: a replaced (cancelled) pending run is no base: its production commit stays in the range`
- M2 a run whose prelude failed counts as a base -- `#3885: a run whose prelude failed graded nothing and is no base`
- M3 the root files HACS reads are not production -- `#3885: ... and hacs.json beside it is not light (null control)` (also README.md and LICENSE)
- M4 a .github/ change can be light -- `#3885: ... and .github/workflows/tests.yml beside it is not light (null control)`
- M5 a light push keeps the full scope -- `#3885: a light push is graded as a pull request over its range`
- M6 a light push stands down no push-only lane -- `#3885: a light push also stands down the re-measurements its pull requests made`
- M7 a lane stands down even when the change reaches what it reads -- the six `#3885: <file>, a file <lane> reads, keeps <lane> grading` checks
- M8 a base that is no ancestor is accepted -- `#3885: a base that is no ancestor leaves the push unranged (graded in full)`
- M9 a light pull request is never light -- `#3885: a light pull request keeps its scope and stands only the product lanes down`
- M10-M12 and M15 a lane's job env or step stops reading the stand-down (browser, typing, env-matrix, coverage-ratchet) -- `#3885: each light lane's job env reads exactly its own stand_down name, and every step of a product lane past its first reads that variable`
- M13 a light run analyzes the python leg -- `#3885: ... even where codeql_scope would analyze it, the other legs kept`
- M14 coverage stands down when the diff touches tests/ -- `#3885: tests/other.py, a file coverage reads, keeps coverage grading`

## Null control

The self-test carries the null controls:

- **A production-touching PR grades unchanged**: `#3885: ... and a production python file
  beside it analyzes (null control)`. Its outputs are `light=false`, `stand_down=""` and the
  python leg `analyze`.
- **A push whose range holds production runs `full`**: the range base is kept, the outputs
  are `scope=full`, `selftests=all`, `stand_down=""`, and every leg is `analyze`.
- **A merge-queue run is never light.**
- **A light diff touching no lane's reads** stands down every product lane.

The range census has a null control too.
`python3 dev/audit/harnesses/ci3885_light.py gaps` over main's first-parent commits since
2026-11-10 counts 416 commits: 137 full and 279 light. The longest run of consecutive light
commits is 9, and the longest time between two full-graded commits is 30.7 h. That is the
worst-case delay before a wrong closure reddens main. `--prefixes-only` (PRODUCTION_FILES
emptied) gives 135 full and 281 light.

## Figures

The day is 2026-11-21, the busy day the orchestrator chose. It used 53,684 runner-min across
`ci.yml`. Each lane below is priced by `share`: the lane's minutes on that day's light runs,
when this tree's `stand_down` (plus the python leg) would have stood that lane down for the
run's file list.

- workflow_dispatch, 2026-11-21: 38 runs. 24 runs (14,621 runner-min) graded light diffs;
  14 runs (8,540) graded full diffs. Command:
  `python3 dev/audit/harnesses/ci3885_light.py share 2026-11-21 --event workflow_dispatch`
  - Stood down 5,189 runner-min, split by lane: codeql python 4,419; coverage 352;
    browser 279; typing 76; validate-hacs 38; hassfest 23; coverage-ratchet 2.
  - `closures` (2,179) and `env-matrix` (427) keep running on a dispatch.
  - These 24 dispatches predate CI-2 (2eea9dc559, 2026-11-22T02:47Z), so they ran
    unscoped. CI-2 already scopes fast, closures and selftests on a dispatch.
- push, 2026-11-21: 17 runs, 5,739 runner-min. 10 runs (3,416) were light. Command:
  `python3 dev/audit/harnesses/ci3885_light.py share 2026-11-21 --event push`
  - Stood down 1,535 runner-min, split by lane: codeql python 857; closures 408;
    coverage 115; env-matrix 88; browser 42; typing 13; validate-hacs 6; hassfest 4;
    coverage-ratchet 1.
  - Not counted: the light pushes' scoped (`auto`) grading of fast, arch-instrument and
    instrument-self-tests in place of `full`.
- pull_request, 2026-11-21: 183 runs, 26,614 runner-min. 103 runs (14,416) were light. Stood down 1,402 runner-min: coverage 693, browser 408, typing 128, validate-hacs 81, codeql python 38, hassfest 38, coverage-ratchet 17; `closures` (2,705) and `env-matrix` (771) keep running on a pull request, and the python leg was already skipped there by `codeql_scope` for non-production diffs. Command:
  `python3 dev/audit/harnesses/ci3885_light.py share 2026-11-21 --event pull_request`
- One quiet-day push run, for comparison: 45328796343, a records-only push, cost 281.7
  runner-min. Command: `python3 dev/audit/harnesses/ci3885_light.py cost 45328796343`
  - A light push is estimated at about 41 runner-min from its job table, using PR 3884's
    scoped run 45300203508 (59.9 runner-min).
  - This is an estimate, not a measurement. The PR's own CI run is the first measured light
    sample.
- Duplicate dispatches (ruling item 4), 2026-11-21:
  - 28 of the 38 PR-naming dispatches (17,495 runner-min) followed a `pull_request` run
    that had already graded the same head. The other 10 dispatches (5,666) were the only
    grader of their head. Unit sets were not compared, so this is an upper bound.
  - On 2026-11-23, 2 of 6 dispatches (304 runner-min) were duplicates.
  - Command: `python3 dev/audit/harnesses/ci3885_light.py dup 2026-11-21`
  - On that day this lever is larger than the light stand-downs (5,189 runner-min). It is
    not S-size, so it is carried forward below.

Day total: 8,126 of the 55,513 runner-min these three `share` runs price (14.6%), so the owner's >20% CI-time exemption (`ratchet-budgets.md`) does not apply and no `exemptions` entry is appended. The push slice alone is 26.7% (1,535 of 5,739), which is not the exemption's measure.

## Red checks

none predicted: `tools/pr/ci_predict.py` predicts no closures, fast, governance or instrument red against 0f63320c96. A local `tests/entities.py` run at ce0283e1d0 failed one check this diff does not reach, `a measured script's late-writing descendant is waited for, not recorded as nodata`: it times the coverage stage's wait (tools/coverage/coverage_tree.sh, untouched) and failed the same way at an earlier head on the same loaded host; CI is the authority for it. The scoped prepr's FULL gate timed out at 5400 s on that host (rc=124), so the gate's verdict is CI's.

## Forward-carry

Both items land in `dev/programme/carries/carry-3885.json`, added by this PR for the next #3885 group, which `node tools/policy/brief_lint.mjs` reads back as `== dev/programme/carries/carry-3885.json ==  -- 0 error(s), 0 warning(s)`:

- Duplicate-dispatch reuse: on 2026-11-21, 28 of 38 PR-naming dispatches (17,495 runner-min, an upper bound: unit sets not compared) followed a pull_request run that had already graded the head; first find why those dispatches fired, and only then consider letting `tools/ci/gate.py` accept the earlier run's verdict (a trust-model change, design first). Carry: #3885
- env_drift's warm cache after a light push: a light push whose scoped gate does not run `tests/env_drift.py` saves no entry at its commit; not measured here, the measurement is in the carry. Carry: #3885

## Friction

none
