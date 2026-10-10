<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
Follows #1940; does not re-open it and claims no new issue.

R9-DBG-2, second pass. The first review left the fix sound and blocked it on one
class -- `root-cause-unanswered`: `arch-score` and `typing` were red at the head
and the body named neither. This pass pays the first and fixes the second, and
re-takes every figure at the new head.

The spec is the R9-DBG-0 pre-study (`tools/audit/round9/prestudy/debugger-prestudy.md`
at `eae236d66`, sections 4 and 7).

**The register was stale, and that is why this seat exists.** R9-DBG-2 already landed:
#2041 (merged 2026-10-08, and #1940 went over with it), then #2056 took it forward
(merged). `dev/programme/delivery/2041.md` and `2056.md` still read `open`, and the
roster's `R9-DBG-2` row still reads `not-started`. Re-measured against the tree,
everything else the brief named is on main and is untouched here: the five priced
self-tests under `run_self_tests` inside `SELF_TEST_BUDGET`, the 8 MiB inline cap with
its summary fallback (`debugger.capped` and `download_bytes`, called from
`diagnostics.py`), the finalize button (DBG-1 landed it), the translations, and the
nightly A16 size check, which the architect note assigns to the nightly lane.

## Why this change, and what it measures

**The defect** (`custom_components/heatpump_optimizer/debugger.py`). Pre-study section
4's row 5 names three feed facts the self-test should trend over the week --
`prices_rows`, `weather_stale_h`, `_tibber_outage_cycles` -- for the question "was a
bad plan caused by a starved feed". `feed_health` reports the first two and neither
half of the third, and the consequence is worse than an omission: the report reads
*clean* straight through an outage. A failed Tibber fetch raises `UpdateFailed`, so
`coordinator.data` keeps its previous object, so `DebugCollector.observe` returns on
`data is self._seen` and records no row for that cycle -- a property
`tests/debug_collect.py` already pins ("a listener call that publishes no new payload
adds no row"). Twelve silent cycles therefore leave no `prices_rows == 0` anywhere in
the ring, and the counter the table names resets to 0 the moment the feed recovers, so
it cannot carry the week either.

Measured with the real collector (seat probe `outage_probe.py`: 48 half-hour cycles,
cycles 20..31 publishing nothing). Before, at the merge base `23d354970`:

    {'cycles': 36, 'no_prices': 0, 'weather_stale_cycles': 0,
     'weather_stale_h_max': 0.0, 'solve_failures_added': 0}

That is the download a maintainer gets for a week whose price feed was down six hours,
and it says the feeds held. After, the same probe adds `row_gaps_h {'n': 35, 'min':
0.5, 'median': 0.5, 'max': 6.5}` -- 6.5 h because twelve skipped cycles are thirteen
cadences -- and `tibber_outage_cycles 0`, the honest answer here (the feed recovered
before the collection ended) and the useful one when it has not: the streak is the fact
that says the collection stopped *inside* an outage.

**The fix.** `feed_health` takes the ring's own stamps through the module's existing
`spread`, so one field carries the install's cadence and its worst silence together
(`median` is the interval, `max` the hole), and takes the outage streak as an argument,
read by the self-test table through the coordinator's published `diagnostics_state()`
view -- the mechanism #1739 exists so that no caller names a private member, which
`coordinator_private_reach 0 <= 0` holds at zero headroom. Both halves are derived from
rows already collected: no new row field, no `DOMAINS` change, no new store key, no
change to the cap, the export or the nightly lane.

**What this pass changed, and why the read moved.** The first pass read the streak
through a module-level `_ending_streak(coordinator)`, and `coord_footprint` charges a
module-level function handed the coordinator for its logic statements: three of them
(the duck-typing guard, its `None`, and the accessor). The function's whole job was to
re-export one attribute of the view, and the table it fed already reads the
coordinator's public surface to fill its siblings -- `accuracy_report(..., coordinator.accuracy)`,
`sensor_sanity(rows, coordinator.data)` -- so the read now sits in
`DebugCollector._async_finish`, the method that holds the coordinator and builds the
probe table, and `feed_health(rows, streak)` receives a value like every other probe.
`coord_footprint` is 2586 again, flat at the merge base, and the `no-any-return` the
old accessor carried goes with it: the read is an assignment, not a typed return.

Alternatives considered:
- (a) Read `coordinator._tibber_outage_cycles` directly: refused by the
  `coordinator_private_reach` ratchet and by `diagnostics.py`'s own precedent.
- (b) Capture the streak in the per-cycle row so the week is trendable from rows:
  refused -- during an outage no row is written at all, which is the whole problem --
  and it would add a field to DBG-1's row builder and to `store.py`'s `DOMAINS` (an F1
  borrow) to store a number that is 0 except while the feed is down.
- (c) Leave the counters alone and let the bundle's consumer diff the timestamps: the
  pre-study's premise is that the self-test answers the question on the install, so the
  answer is in the download and not in a later tool.
- (d) Keep `_ending_streak` as a named module-level accessor and explain the rise in
  this body instead of paying it: refused, because the accessor bought nothing the
  call site does not already have -- the metric's own rule ("a trivial accessor does
  not read as growth") is what the shape failed, and a body section explaining three
  statements of a one-attribute re-export would be a paragraph in place of a line.

**What this change does not do -- the two rows of section 4 that cannot land in the
package.** Both are owed, named rather than dropped:
- Row 3's `tests/stress.py:reference_solve`, the fixed-cost ruler beside the install's
  own solve. A `tests/` module cannot ship inside `custom_components/`, and the shipped
  module answers the row with one `async_simulate` plus the week's recorded
  distribution. Repo-side it is buildable: `grep -rn reference_solve tools/replay/` at
  this head returns nothing, so the harness R9-DBG-3 landed does not price it either.
- Row 1's `as_dict -> from_dict -> compare` **per store**. The shipped report gives every
  store its domain and quarantine state and round-trips only the accuracy store. A
  generic round trip needs a store-name-to-loader map and there is none to reuse:
  `DOMAINS` declares field domains, not loaders (`store.py:280`), and the loaders are
  hand-rolled per learner in the coordinator's restore path
  (`HeatPumpOptimizerCoordinator._load_t4b_learners`, `._async_load_price_model`).
  Building one in the package would be the parallel mechanism the architect note refuses;
  offline, where the loader classes import directly, it is one harness stage.

**Architect-note compliance** (tvofi, 2026-10-09). No parallel list: the store inclusion
still comes from `store_keys`, derived from `store.DOMAINS` (`debugger.py:88`), and the
streak arrives through the coordinator's published `diagnostics_state()` view rather
than a second registry of coordinator attributes. The export is not re-shaped and the
nightly lane is not touched: the three-dot diff lists `debugger.py`,
`tests/debug_collect.py`, `docs/configuration.md` and the delivery row, and not
`diagnostics.py` or `tests/nightly_ha.py`. The cap is not moved: the same diff carries
no line matching `INLINE_CAP`, `DOWNLOAD_HEADROOM`, `def capped` or `def download_bytes`.

## Architecture score

The check's own output at this head, `python3 -I tools/audit/archscore/gate.py --base
23d354970fcaababe8e67a5c04c326cc8bc79e49 --head 1e60f18610d0cfb9b64e983b56859198b1a3bdbc
--body <this body>`:

    Architecture score: dS +0.0000 NULL
    PASS: dS +0.0000 NULL, no gate metric rose

No metric rises, so no line here explains one. The rise the review measured is gone
rather than argued: at the reviewed head `4e5181094` the same command printed
`Architecture score: dS -0.0017 WORSENS (inadmissible: coord_footprint 2586->2589)` and
`FAIL: ... unexplained: coord_footprint 2586->2589`, and the three statements it charged
are the `_ending_streak` this pass deletes. The metric's own reading of the moved
statements is in `## Figures`.

## Head

`170ac598748d4cf54e21a56a294eb747464b4f6d` merges the authored code head `1e60f18610d0cfb9b64e983b56859198b1a3bdbc` into this PR's previous head, which carried its own row `dev/programme/delivery/2110.md`. The PR tree is that code head plus the row.

`1e60f18610d0cfb9b64e983b56859198b1a3bdbc` is the head everything below was measured at.
It adds one commit to the head the fix review measured, `4e5181094ec1c84b7d2552cfd3f184972be9c687`:
`1e60f1861` moves the read into `DebugCollector._async_finish`, deletes the two
`killed_by` rows `_ending_streak` was pinned by, and changes nothing else.

`4e5181094` itself adds one commit (this PR's own delivery row, `dev/programme/delivery/2110.md`)
to the authored code head `c901f8f34f0b566033202c1a10f0387a3c205099`, whose history is
`2faad4bb1` the failing test, `5ad913305` the fix, `f5371d461` the docs sentence and the
first two pins, `81760f73e` the merge of `origin/main` `d8a4bd36f`, `8cfc35591` the rename
of the new reader, `4568f9b14` its pins, and `c901f8f34` the merge of `origin/main`
`23d354970` (102 files, none of them `debugger.py` or `tests/debug_collect.py`). Steps
2-8 were re-executed at this head, and every figure below is this head's.

## Mutation proof

Ten applied mutants, one at a time, in this worktree at `1e60f1861`, each run as
`PYTHONPATH=tests/hastub python3 tests/debug_collect.py` with the working directory at
the worktree, then restored from an in-memory copy (`mutate_all.py`, seat scratch; its
`M0` case is the same probe with no patch). The source's sha1 was
`7065f936fe51b5a605079d9b9131931c19a5960a` before and after, and `git status --porcelain`
was empty after. `M0` printed `ALL 70 DEBUG COLLECT CHECKS PASSED`, rc 0; every mutant
below exited 1.

- M1 the gap key renamed (`row_gaps_h` -> `row_gap_h`): `KeyError: 'row_gaps_h'`
- M2 the stamps paired backwards (`zip(stamps[1:], stamps)`): `1 of 70 DEBUG COLLECT
  CHECKS FAILED`
- M3 the gap left in seconds (drop `/ 3600.0`): the same one check
- M4 the span instead of the worst consecutive gap: `2 of 70 DEBUG COLLECT CHECKS FAILED`
- M5 the unparseable-stamp filter deleted (`[stored_instant(...) for row in rows]`):
  `TypeError: unsupported operand type(s) for -: 'NoneType' and 'NoneType'`
- M6 the streak dropped from the report: `KeyError: 'tibber_outage_cycles'`
- M7 the streak defaulted to `0` rather than unknown (`outage_cycles or 0`): `2 of 70
  DEBUG COLLECT CHECKS FAILED`
- M8 the read's duck-typing guard inverted (`if state is None`): `TypeError: 'NoneType'
  object is not callable`
- M9 the read's guard deleted (the view dereferenced unguarded): `AttributeError:
  '_Coord' object has no attribute 'diagnostics_state'`
- M10 the table no longer passes the streak (`feed_health(rows)`): `1 of 70 DEBUG
  COLLECT CHECKS FAILED`

**The failing-first arm at this head**: `git checkout 23d354970 -- custom_components/heatpump_optimizer/debugger.py`,
then the same command, exits 1 with `KeyError: 'row_gaps_h'` at `tests/debug_collect.py:473`;
restored with `git checkout HEAD -- ...`, `git status` clean, and the unmutated head prints
`ALL 70 DEBUG COLLECT CHECKS PASSED`, rc 0.

The engine's own inventory agrees from the other side: the diff adds no candidate site
and deletes two, so the unpinned count is `4620` at this head and `4620` at the merge
base (`## Figures`). The two rows the first pass pinned for the deleted accessor are
stale, and a stale pin is the author's to delete rather than the bot's -- `mutation-autofix`
only ever adds one (`dev/audit/rca/R9-RCA-stale-pins.md`, the RCA #2073 landed for this
class) -- so this pass deletes them. They were added by this branch and are deleted by
it, so the pull request's net three-dot diff carries no ledger file at all.

## Null control

- `M0`: the same mutation probe with no patch applied, in this worktree at `1e60f1861`:
  `ALL 70 DEBUG COLLECT CHECKS PASSED`, rc 0.
- The new test alone against the merge base (commit `2faad4bb1`): rc 1,
  `KeyError: 'row_gaps_h'` at `tests/debug_collect.py:472` -- the test fails before the
  fix.
- The demonstration probe at `23d354970` prints `RESULT fields_naming_the_silence=0`; at
  this head it prints `RESULT fields_naming_the_silence=2 # reported`. The figure moves
  because of the fix, not because of the probe.
- The pricing harness (the pre-study's oracle) prints five `ok` rows at both ends, so the
  four self-tests this diff does not touch still cost what they costed.
- The ledger probe prints the same unpinned count at both ends (4620), so the deleted
  pins moved nothing the ratchet counts.

## Figures

Every command below was run at `1e60f18610d0cfb9b64e983b56859198b1a3bdbc`, with
`python3` the 3.14.7 interpreter at `/Users/timmalmstrom/.local/state/hpo/venv-ci/bin/python3`
unless a command names another, and with `git merge-base origin/main HEAD` =
`23d354970fcaababe8e67a5c04c326cc8bc79e49` (main has moved since; the merge base has not).

- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
  --workdir <a directory outside the worktree>` printed `MODE: SCOPED -- 15 script(s) run,
  18 scoped out.` over 4 changed files. `scope.run` names `arch_score_head`,
  `config_flow_steps`, `debug_collect`, `deployment_shape`, `doc_claims`, `entities`,
  `env_drift`, `features`, `finite_boundary`, `golden`, `harness_headers`, `manual_plan`,
  `md_tables.mjs`, `structure`, `typing_ruler`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Ran locally at this head, one at a time as `PYTHONPATH=tests/hastub python3
  tests/<script>.py`: `debug_collect.py` `ALL 70 DEBUG COLLECT CHECKS PASSED`,
  `entities.py` `ALL 2243 ENTITY CHECKS PASSED`, `doc_claims.py` `ALL 160 checks PASSED`,
  `config_flow_steps.py` `ALL 499 checks PASSED`, `deployment_shape.py` `ALL DEPLOYMENT
  SHAPE CHECKS PASSED`, `finite_boundary.py` `ALL 84 FINITE BOUNDARY CHECKS PASSED`,
  `harness_headers.py` `ALL 109 HARNESS HEADER CHECKS PASSED`, `manual_plan.py` `ALL 129
  manual plan checks PASSED`, `arch_score_head.py` `ALL 15 ARCHITECTURE SCORE HEAD CHECKS
  PASSED`, `env_drift.py` `NO UNCLAIMED DRIFT: 5 scenario(s) checked against origin/main`
  and `NO STALE FIXTURE: 5 committed fixture(s) still match what this tree computes`,
  `typing_ruler.py` (source lane) `ALL 11 typing-ruler source checks PASSED`, and with
  `HPO_TYPING_PYTHON` pointed at the pinned interpreter `ALL 12 typing-ruler source checks
  PASSED`, including `ok the pinned census passed under HPO_TYPING_PYTHON`.
- `node tests/md_tables.mjs`: `RESULT doc_orphaned_table_rows=0 count`,
  `RESULT doc_misrendered_lines=0 count`, `RESULT doc_swallowed_prose_lines=0 count`.
- The `typing` red, measured with the pinned pair (mypy 2.3.1, homeassistant-stubs
  2026.9.3, Python 3.14.7) in a venv built from `python3 tests/typing_ruler.py
  --print-requirements`. At the reviewed head `4e5181094`: `debugger.py 1`,
  `FAIL errors did not grow [recorded 0, measured 1 (+1)]`,
  `FAIL by_code[no-any-return] did not grow [recorded 0, measured 1 (+1)]`,
  `2 of 10 typing-ruler checks FAILED`. At this head:
  `<venv>/bin/python tests/typing_ruler.py --mypy` printed `ALL 9 typing-ruler checks
  PASSED`. The instrument is the ruler, and the census number it prints is not restated
  here.
- The `arch-score` red, the check's own command and the metric's own reading:
  `python3 -I tools/audit/archscore/gate.py --base 23d354970fcaababe8e67a5c04c326cc8bc79e49
  --head <head> --body <body>` printed `FAIL: dS -0.0017 WORSENS; unexplained:
  coord_footprint 2586->2589` at `4e5181094` and `PASS: dS +0.0000 NULL, no gate metric
  rose` at this head. `python3 -c "from archscore.metrics import footprint;
  footprint.measure(Path('.'))"` (from `tools/audit` on the path) reads `2589` at
  `4e5181094` and `2586` at this head, and its `charged` list holds
  `debugger._ending_streak:3` at the first and no `_ending_streak` entry at the second.
- The mutation ledger, both directions, from `tests/mutation_table.py`'s own
  `inventory()`, `unpinned_sites()` and `completeness_problems()` driven in isolation
  (`ledger_probe.py`, seat scratch; the in-tree readers are CI's `mutation` job and, once
  main carries #2073, `prepr.sh` step 6d's refusing stale-pin arm): at the merge base
  `candidate sites: 5943`, `unpinned: 4620`, `completeness problems: 0`; at the reviewed
  head's tree before this pass's edit `completeness problems: 2`, both the `_ending_streak`
  pins, and after deleting those two rows at this head `candidate sites: 5943`,
  `unpinned: 4620`, `completeness problems: 0`.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `tmp_paths: 0 refused, 0 stale allow
  entries at HEAD, ledger lines added since 23d354970fca`.
- Claim files: `git rev-parse HEAD:<path>` equals `git rev-parse 23d354970:<path>` for
  `tests/golden/claimed_drift.txt`, `tests/golden/card_claimed_drift.txt`, `VERSION`,
  `custom_components/heatpump_optimizer/manifest.json` and `RELEASE_NOTES.md` -- all five
  byte-identical to the merge base, and `git diff 23d354970...HEAD -- tests/golden/` is
  empty. `python3 tests/env_drift.py --claims-only 23d354970fcaababe8e67a5c04c326cc8bc79e49`:
  `claims hygiene: 23d354970fca ok`. This branch claims nothing; `VERSION`, the manifest
  version and the notes heading are untouched.
- `git merge-tree --write-tree origin/main HEAD`: exit 0, no conflicting paths.
- The oracle: `PYTHONPATH=tests/hastub python3
  dev/audit/harnesses/r9_dbg2_selftest_price.py --bundle <week.json.gz> --repeat 1`, the
  bundle being `git show origin/handoff/r9-dbg-0:tools/audit/round9/prestudy/runs/week/bundle.json.gz`
  (sha1 `cb6e9e3357648afc41adcadaff218f135908cc3d`). At `23d354970`: five `ok`,
  `selftest_total_ms=15.5`, `bundle_bytes=588244`, `bundle_inline=1`. At this head: five
  `ok`, `selftest_total_ms=73.7`, `bundle_bytes=588447`, `bundle_inline=1`, against the
  harness's 900000 ms budget and 8388608 B cap. Totals move with this box's load, so the
  harness is the instrument and no total here is a claim about another box.
- The demonstration probe, `outage_probe.py` (sha1 `2068d07b3b3445078d0828189f5f72c093ccc6dc`,
  one copy per end so its own `ROOT` resolves):
  `python3 $SEAT/evidence/outage_probe.py` with the working directory at this worktree and
  `python3 $SEAT/base/evidence/outage_probe.py` with it at `$SEAT/base/wt`
  (`23d354970`). Both print `RESULT rows_recorded=36 of 48 cycles` and
  `RESULT outage_streak_at_finalize=0`; the base then prints
  `RESULT fields_naming_the_silence=0 # the six hours are in no field` and this head
  `RESULT fields_naming_the_silence=2 # reported`, with
  `row_gaps_h: {'n': 35, 'min': 0.5, 'median': 0.5, 'max': 6.5}` and
  `tibber_outage_cycles: 0` in the same printed report.
- `python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures or fast red
  predicted against 23d354970fca (a data-file read is not seen)`.
- No-copies, with the interpreter that can parse the script:
  `PATH=<the 3.14 venv>/bin:$PATH python3 tests/closure.py no-copies` printed
  `closure: no test file defines a symbol production also defines`, rc 0. Without that
  prefix the same step runs the box's ambient `python3` (3.11) and refuses on a
  `SyntaxError: f-string: expecting '}'` inside the script rather than on this diff
  (`## Friction`).
- The body contract: `node tools/policy/policy_lint.mjs --pr-body <this body> --head
  1e60f18610d0cfb9b64e983b56859198b1a3bdbc --title "fix(R9-DBG-2): debugger self-tests,
  diagnostics bundle inclusion cap, finalize and translations" --paths-file <the
  three-dot --no-renames list>` printed `PR-BODY: 0 error(s)`; `node
  tools/policy/figure_lint.mjs --pr-body <this body>`: `FIGURES: 15 resolved, 11 not
  verified, 0 refused` -- the not-verified ones are the angle-bracketed placeholders and
  the scratch-path commands this body names by rule rather than by path.
- The whole pre-PR gate, run with the 3.14 venv first on `PATH`, at this head: every step
  is ok or a reasoned skip except the one refusal the `features.py` bullet owns --
  `ok no-copies closure: no test file defines a symbol production also defines`,
  `ok preflight`, `ok pr-body PR-BODY: 0 error(s) ... no budget leaf raised over
  23d354970...1e60f1861`, `ok figures` with `0 refused`, `skip unpinned sites the diff
  adds no unpinned mutation site`, and, because the repair branch is not yet pushed,
  `skip push order` and `skip ancestry reds` -- and its last line is
  `PRE-PR: 1e60f18610d0cfb9b64e983b56859198b1a3bdbc 000000000000000000100000`. The digest
  is the mask of step outcomes, not of this body's bytes, so a `## Figures` edit cannot
  move it; the one set bit is the `closures` step's, and its content is main's own red.
- Left to CI, because this box cannot produce them honestly: `tests/golden.py` and
  `tests/features.py`. No value-bearing fixture moves in this diff, and this diff touches
  no solver path. `PYTHONPATH=tests/hastub python3 tests/features.py` was run at both ends
  anyway, one per end so each measured its own tree: `1 of 3930 FEATURE CHECKS FAILED` at
  this head and `1 of 3930 FEATURE CHECKS FAILED` at `23d354970`, the same `FAIL R9-F2.1
  P3` line in both, so the local red is main's and not this diff's.

## Red checks

Two checks went red on commits in this branch and both are named here.

- **`arch-score`** (`failure` at `4e5181094`): `Architecture score: dS -0.0017 WORSENS
  (inadmissible: coord_footprint 2586->2589)`. Answered by paying the rise rather than
  explaining it: the charge was the module-level `_ending_streak`, its read now sits in
  the method that builds the probe table, and the check's own command at this head prints
  `PASS: dS +0.0000 NULL, no gate metric rose`. The metric, its `charged` list and both
  runs are quoted under `## Architecture score` and `## Figures`.
- **`typing`** (`failure` at `4e5181094`): one `no-any-return` in `debugger.py`, against
  a census budget of 0. Fixed, not budgeted: the expression was the deleted accessor's
  `return` from a `coordinator: Any` parameter, and at this head the pinned ruler prints
  `ALL 9 typing-ruler checks PASSED`. Root-cause trigger: the cheaper detector is
  `tests/typing_ruler.py --mypy` under the pinned pair (mypy 2.3.1 + homeassistant-stubs
  2026.9.3 on Python >= 3.14.2), which no gate lane has -- `typing_ruler.py`'s own
  docstring is that argument -- and whose standing cost is the whole pinned toolchain on
  every lane that would run it. This pass built that venv by hand and ran the census in
  seconds, so the detector is real; whether a local lane should carry it is
  `root-cause.md`'s call, not this body's, and it is recorded here rather than argued.
- `pr-contract` (`failure` at `4e5181094`): its two `[pr-body]` errors were that
  `## Red checks` named neither check above. Answered by this section; the local
  `--pr-body` run is in `## Figures`.
- **Not this diff's red**: `tests/features.py` exits 1 on this box (macOS, Accelerate
  BLAS) at the merge base and at this head alike, with the same one failure and the same
  figures -- `1 of 3930 FEATURE CHECKS FAILED`, `FAIL R9-F2.1 P3: the shipped storage plan
  is no worse on its own objective than the half-price floor's plan refined under it
  [shipped 110.4366, seeded with the half-price plan 110.1297]` -- a margin
  `tests/features.py` itself documents as BLAS-dependent. This diff touches no solver path
  and moves no golden fixture, so CI's pinned Linux run is that script's authority. It is
  also the whole content of the one local refusal below: `prepr.sh`'s step prints
  `REFUSE closures failed while being recorded: tests/features.py (exit 1) -- fix the
  script first; a re-derive would record the same truncation; left to CI:
  tests/md_tables.mjs`, and the control is the both-ends run above.
- `nightly-status` and `delivery-status` grade `main` and this diff touches neither their
  scripts nor the plan; no answer is owed them.

## Forward-carry

n/a: no later stage's work changes because of this -- the two owed rows of the pre-study's priced table are this group's own unfinished spec and are named under "What this change does not do" above; the dispatch brief they would be carried into lives on the orchestrator's hand-off ref, not in the tree, so no in-tree destination exists.

## Friction

- delivery-status-tracking: stale: `2041.md` and `2056.md` read `open` and the roster row
  reads `not-started` while both are merged and #1940 closed, so a seat dispatched on that
  text re-does a delivered group.
- gate-scoping: unclear: `closure.py select` with `--workdir` inside the worktree writes
  four `scope.*` files into the tree it measures, and the next run reads them as changed
  files and answers full mode where the diff is scopeable.
- fixer.md: cost: `mutation_table.py --scope changed` took about 50 min here while another
  seat's four-job pin drive held the box at load average 210, against the 5 s #2041's body
  recorded for the same command.
- fixer.md: unclear: `tests/harness.py` inserts the **relative** paths `tests` and
  `custom_components` at import, so a seat probe that imports it resolves `heatpump_optimizer`
  against the seat's own working directory rather than the tree its `__file__` names -- the
  probe printed a report from another checkout, with rc 0 and no error, until the working
  directory was moved into the tree it meant to measure.
- fixer.md: cost: `prepr.sh`'s `no-copies` step runs the ambient `python3`; where that is
  3.11 it mis-parses `closure.py`'s f-strings and refuses `SyntaxError: f-string: expecting
  '}'` for a step that passes under the pinned 3.14 -- reading it as this diff's red costs a
  full pre-PR run to unlearn, and prefixing `PATH` with the 3.14 venv is what fixes it.

