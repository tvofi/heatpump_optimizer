Follows #1940; does not re-open it and claims no new issue.

R9-DBG-2, second pass: the debugger's feed self-test names a starved price feed.
The spec is the R9-DBG-0 pre-study (`tools/audit/round9/prestudy/debugger-prestudy.md`
at `eae236d66`, sections 4 and 7), re-read at this head.

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
cycles 20..31 publishing nothing). Before, at `origin/main` `a8ce87571`:

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
  hand-rolled per learner in the coordinator's restore path (`coordinator.py:3689`,
  `coordinator.py:7752`). Building one in the package would be the parallel mechanism
  the architect note refuses; offline, where the loader classes import directly, it is
  one harness stage.

**Architect-note compliance** (tvofi, 2026-10-09). No parallel list: the store inclusion
still comes from `store_keys`, derived from `store.DOMAINS` (`debugger.py:88`), and the
streak arrives through the coordinator's published `diagnostics_state()` view rather
than a second registry of coordinator attributes. The export is not re-shaped and the
nightly lane is not touched: `git diff --name-only d8a4bd36f HEAD` lists `debugger.py`,
`tests/debug_collect.py`, `docs/configuration.md` and the ledger rows, and not
`diagnostics.py` or `tests/nightly_ha.py`. The cap is not moved: the same diff carries
no line matching `INLINE_CAP`, `DOWNLOAD_HEADROOM`, `def capped` or `def download_bytes`,
and this group needed no change to it.

## Head

`c901f8f34f0b566033202c1a10f0387a3c205099` is the authored head: `2faad4bb1` the failing test,
`5ad913305` the fix, `f5371d461` the docs sentence and the first two pins, `81760f73e`
the merge of `origin/main` `d8a4bd36f` (16 commits, none touching `debugger.py`,
`tests/debug_collect.py`, `docs/configuration.md`, `diagnostics.py`,
`tests/nightly_ha.py` or any `*_budgets.json`; `git diff f5371d461 HEAD` over
`debugger.py` and over the test file are both empty), `8cfc35591` the rename of the new
reader, `4568f9b14` its pins, and `c901f8f34` the merge of `origin/main` `23d354970`
(102 files, of which none is `debugger.py` or `tests/debug_collect.py` --
`git diff 4568f9b14 c901f8f34 -- custom_components/heatpump_optimizer/debugger.py` is
empty -- but it moves `store.py`, `accuracy.py`, `coordinator.py` and `diagnostics.py`,
the neighbours this module reads, so `tests/debug_collect.py`, `tests/structure.py`,
`tests/entities.py`, `tests/typing_ruler.py` and the closure derivation were re-run at
that head, as fixer.md requires after a merge; the results are the `23d354970` lines in
`## Figures`). Steps 2-8 were re-executed after the first merge as well.

`handoff/r9-dbg-2` is a fast-forward over the merged `a5e969565` (the #2041 head is an
ancestor of this base), so no landed commit is rewritten.

## Mutation proof

Applied one at a time in a detached worktree at `5ad913305`, each run as
`PYTHONPATH=tests/hastub python3 tests/debug_collect.py`, then restored (the seat probe
`mutate.py`, kept in scratch). M0, the same probe with no change in the same worktree,
printed `ALL 70 DEBUG COLLECT CHECKS PASSED`, rc 0. Lines starting `FAIL a16:` are that
judge's own printed null arms and are not counted (the same 7 print at M0, with rc 0).
Every mutant below exited 1. The merge moves no line of `debugger.py`, so these still
describe the delivered head; what came after is a rename of the same two sites.

- M1 the gap key renamed (`row_gaps_h` to `row_gap_h`): `KeyError: 'row_gaps_h'`
- M2 the stamps paired backwards (`zip(stamps[1:], stamps)`): `FAIL the feed self-test
  names the hole the ring shows when cycles published nothing, where its price and
  forecast counters read clean` -- `row_gaps_h: {'n': 11, 'min': -6.0, 'median': -0.5}`
- M3 the gap left in seconds (drop `/ 3600.0`): same check -- `min': 1800.0`
- M4 the span instead of the worst consecutive gap (`later - stamps[0]`): same check --
  `median': 8.5`
- M5 an unparseable stamp allowed into the list (the filter neutered):
  `TypeError: unsupported operand type(s) for -: 'NoneType' and 'NoneType'`
- M6 the streak dropped from the report: `KeyError: 'tibber_outage_cycles'`
- M7 the streak defaulted to `0` rather than unknown: `FAIL the feed self-test reports
  the outage streak the collection ended in, and none when it was not told`
- M8 the table no longer passes it (`feed_health(rows)`): `FAIL the feed self-test
  reads the outage streak through the coordinator's published view` --
  `'tibber_outage_cycles': None`
- M9 the view read without asking whether it is published (guard deleted): `FAIL the
  feed self-test of a coordinator that publishes no view reports no streak, not an
  error` -- `AttributeError("'_Coord' object has no attribute 'diagnostics_state'")`

The engine enumerates two sites on this diff, both in the reader; the nine hand mutants
probe what that enumeration does not -- the report's key names, the units inside the
comprehension, the default of the new argument, and the wiring in the table. Both kinds
are shown because they are different claims: the pins say the engine's sites are killed
by `tests/debug_collect.py`, the hand drive says the added behaviour is pinned at all.

Ledger, re-driven at this head after the rename: `PYTHONPATH=tests/hastub python3
tests/mutation_table.py --pin-killed --base origin/main --scripts tests/debug_collect.py`
printed `PIN KILLED -- 2 new unpinned site(s) against d8a4bd36f638`,
`baseline tests/debug_collect.py: rc=0 failed=0 7s`,
`null control custom_components/heatpump_optimizer/debugger.py:458 NULL_COMMENT survived
tests/debug_collect.py`, then `pinned ... debugger.py:291 GUARD_OFF -- killed by
tests/debug_collect.py` and `pinned ... debugger.py:293 RETURN_DEL -- killed by
tests/debug_collect.py`, and `PIN KILLED: 2 pinned, 0 left unpinned`. The two rows are
`_ending_streak.GUARD_OFF.7b428e6a.json` and
`_ending_streak.RETURN_DEL.9e6cd1b7.json` under
`tests/mutation_ledger/killed_by/debugger.py/`, committed at `4568f9b14`.

## Null control

- The same probe with no change applied, in the same worktree at `5ad913305`:
  `ALL 70 DEBUG COLLECT CHECKS PASSED`, rc 0.
- The new test alone against the merge base (commit `2faad4bb1`, base `a8ce87571`):
  rc 1, `KeyError: 'row_gaps_h'` at `tests/debug_collect.py:472` -- the test fails
  before the fix, and `red_failing_first.log` in the seat's evidence is that run.
- The demonstration probe at `a8ce87571` prints `RESULT fields_naming_the_silence=0`
  and at `5ad913305` prints `RESULT fields_naming_the_silence=2 # reported`: the figure
  moves because of the fix, not because of the probe.
- The pricing harness (the pre-study's oracle) at `a8ce87571` prints five `ok` rows; at
  this head it prints the same five, so the four self-tests this diff does not touch
  still cost what they costed.
- The pin drive's own null control (`debugger.py:458 NULL_COMMENT`, a comment-only
  edit) survived every driver in play, both times it ran.

## Figures

- Scoped gate, first derivation at `f5371d461`: `python3 tests/closure.py select --diff
  $(git merge-base origin/main HEAD) --workdir <scratch outside the worktree>` printed
  `MODE: SCOPED -- 15 script(s) run, 18 scoped out.` `scope.run` names
  `arch_score_head`, `config_flow_steps`, `debug_collect`, `deployment_shape`,
  `doc_claims`, `entities`, `env_drift`, `features`, `finite_boundary`, `golden`,
  `harness_headers`, `manual_plan`, `md_tables.mjs`, `structure`, `typing_ruler`. The
  doc edit is what pulled `md_tables.mjs` in; the derivation before the doc commit read
  `MODE: SCOPED -- 14 script(s) run, 19 scoped out`.
- Re-derived after the merge at `81760f73e`: the same
  `MODE: SCOPED -- 15 script(s) run, 18 scoped out` over 5 changed files.
- Ran locally at the merged head, one at a time as `PYTHONPATH=tests/hastub python3
  tests/<script>.py` on the seat venv (Python 3.14.7): `debug_collect.py`
  `ALL 70 DEBUG COLLECT CHECKS PASSED`, `structure.py` `STRUCTURE RATCHET PASSED`,
  `entities.py` `ALL 2236 ENTITY CHECKS PASSED` (one check more than at the older base
  -- main's own), `doc_claims.py` `ALL 160 checks PASSED`, `typing_ruler.py`
  `ALL 11 typing-ruler source checks PASSED`, `config_flow_steps.py`
  `ALL 499 checks PASSED`, `deployment_shape.py` `ALL DEPLOYMENT SHAPE CHECKS PASSED`,
  `env_drift.py` `NO STALE FIXTURE: 5 committed fixture(s) still match what this tree
  computes`, `finite_boundary.py` `ALL 84 FINITE BOUNDARY CHECKS PASSED`,
  `manual_plan.py` `ALL 129 manual plan checks PASSED`, `harness_headers.py`
  `ALL 109 HARNESS HEADER CHECKS PASSED`.
- fixer.md step 5 moved under this branch (`dev/governance/roles/fixer.md` is one of the
  six policy files the merge brought): it now names `tests/run.sh`'s `run_always` lines
  beside `scope.run`, so `python3 tests/layout.py`, which the closure table scopes OUT
  for this diff, ran here too (`layout self-test: ok`, rc 0), and
  `python3 tests/env_drift.py --claims-only d8a4bd36f6384dde45486fff388f91ed4a3aa6df`
  printed `claims hygiene: d8a4bd36f6384dde45486fff388f91ed4a3aa6df ok`.
- `node tests/md_tables.mjs`: `RESULT doc_orphaned_table_rows=0 count` and
  `RESULT doc_misrendered_lines=0 count`.
- Mutation inventory: `python3 tests/mutation_table.py --scope changed --base
  origin/main` at `f5371d461` printed `0 survivor(s) of 2 evaluated = 0.0%, cap 20.0%`
  and `MUTATION TABLE PASSED`; the pin drive reports the same inventory from the other
  side, `4624 unpinned site(s) of 5903 candidate sites, 4622 at the ratchet base` -- so
  the diff moves the unpinned count by exactly the two sites it adds, and both are
  pinned. That run took about 50 min here, starved by the drive named in `## Friction`;
  #2041's body recorded the same command at about 5 s on an idle box.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `tmp_paths: 0 refused, 0 stale
  allow entries at HEAD`.
- The body contract: `node tools/policy/policy_lint.mjs --pr-body
  /Users/timmalmstrom/hpo-seats/dbg2/body/BODY.md --head $(git rev-parse HEAD) --title
  "R9-DBG-2: the debugger's feed self-test names a starved price feed" --paths-file
  <three-dot --no-renames list>` printed `PR-BODY: 0 error(s)`, after the four refusals
  named in `## Red checks` were answered. `node tools/policy/figure_lint.mjs --pr-body
  <same body>` printed `FIGURES: 12 resolved, 2 not verified, 0 refused`.
- The whole pre-PR gate, `bash tools/pr/prepr.sh <this body>` at `4568f9b14`, last line
  `PRE-PR: 4568f9b140b6e2e068d805265b011e5590959dd6 000000000000000000100000`. Every
  step is ok or a reasoned skip except one refusal and one warning: `no-copies`
  `closure: no test file defines a symbol production also defines`, `pr-body`
  `PR-BODY: 0 error(s)`, `figures` `FIGURES: 14 resolved, 2 not verified, 0 refused`,
  `unpinned sites` `the diff adds no unpinned mutation site`, `claim files`
  `byte-identical to origin/main`, `ci predict` clean -- and `REFUSE closures`, whose
  reason and control are in `## Red checks`, with `WARN push order`
  (`HEAD is 311 commit(s) ahead of origin/handoff/r9-dbg-2 -- A PUSH MUST FOLLOW THIS
  BODY EDIT`), which is S10's prescribed state: the body is final, the push follows.
- After the second merge (`c901f8f34`, `origin/main` `23d354970`): the closure
  selection re-derived to `MODE: SCOPED -- 15 script(s) run, 18 scoped out`, and the
  drift catchers re-ran -- `debug_collect.py` `ALL 70 DEBUG COLLECT CHECKS PASSED`,
  `structure.py` `STRUCTURE RATCHET PASSED`, `entities.py` `ALL 2243 ENTITY CHECKS
  PASSED` (seven more than at `d8a4bd36f`: main's own), `typing_ruler.py`
  `ALL 11 typing-ruler source checks PASSED`. prepr's closures derivation was not re-run at that
  head: its one refusal is `tests/features.py`, which is red at `origin/main` on this
  box with or without this branch, and CI's `closures` job and the `closures-autofix`
  bot are that step's authority (ci-autofix.md).
- `python3 tools/pr/ci_predict.py --base origin/main`: `CI PREDICT: no closures or fast
  red predicted against d8a4bd36f638 (a data-file read is not seen)`.
- The oracle: `PYTHONPATH=tests/hastub python3
  dev/audit/harnesses/r9_dbg2_selftest_price.py --bundle <week.json.gz> --repeat 1`, the
  bundle being
  `git show origin/handoff/r9-dbg-0:tools/audit/round9/prestudy/runs/week/bundle.json.gz`
  (sha1 `cb6e9e3357648afc41adcadaff218f135908cc3d`, the sha1 the pre-study names). At
  `a8ce87571`: five `ok`, `selftest_total_ms=14.9`, `feeds` 0.1 ms,
  `bundle_bytes=588244`, `bundle_inline=1`. At `5ad913305`: five `ok`,
  `selftest_total_ms=13.1`, `feeds` 0.3 ms, `bundle_bytes=588446` (the two new fields
  cost 202 B), `bundle_inline=1`. Perturbation `--repeat 39` and `--repeat 40` at this
  head: `bundle_inline=0` both, with `selftest_total_ms=215.3` and `251.4` against the
  900000 ms budget. Totals move with the seat's load (another seat's four-job pin drive
  held this box at load average 210 throughout), so the harness is the instrument and no
  total here is a claim about another box.
- Left to CI, because this box cannot produce them honestly: `tests/golden.py`,
  `tests/arch_score_head.py` and `tests/features.py`, whose local verdict and its
  control are in `## Red checks`. No value-bearing fixture moves in this diff, so both
  claim files are byte-identical to `origin/main` (`ok claim files byte-identical to
  origin/main`).

## Red checks

None has been read, because this head has no pull request: the seat hands off the head
and does not open or drive a PR, so no check-run exists to read, and naming a cheaper
detector for a check that has not failed would be a claim about an event that has not
happened. What prepr refused locally, and the control that says whose it is:

- `no-copies`: `COPY-CLAIMED: tests/dst_checks.py defines '_outage', which is
  production's debugger._outage (1 in all)`. Answered by the rename at `8cfc35591`;
  `python3 tests/closure.py no-copies` now prints
  `closure: no test file defines a symbol production also defines`.
- `pr-body`: four refusals on an earlier draft of this body -- a carry naming a file
  that is not in the tree, and three `## Friction` lines that did not parse. Answered
  by this body; `node tools/policy/policy_lint.mjs --pr-body ...` is now clean (its own
  line is quoted at the end of `## Figures`).
- `closures`: prepr's derivation ran `tests/features.py` and it exited 1 on this box.
  That is not this diff's: in a clean detached worktree at `origin/main` `d8a4bd36f`,
  same box, same venv, `tests/features.py` fails the SAME check with the SAME figures
  -- `1 of 3879 FEATURE CHECKS FAILED`,
  `FAIL R9-F2.1 P3: the shipped storage plan is no worse on its own objective than the
  half-price floor's plan refined under it [shipped 110.4366, seeded with the half-price
  plan 110.1297]` -- a margin the suite itself documents as BLAS-dependent
  (`tests/features.py`, the note at its line 33663: a machine whose BLAS differs
  ``reports 34 of 55 changed on a clean tree``). This diff touches no solver path, and
  CI's pinned run is the authority for this script, as `## Figures` states.

The nightly A16 lane this group must not re-shape is untouched, and its judge runs from
`tests/debug_collect.py` at this head, both arms and their swapped nulls included.

## Forward-carry

n/a: no later stage's work changes because of this -- the two owed rows of the pre-study's priced table are this group's own unfinished spec and are named under "What this change does not do" above; the dispatch brief they would be carried into lives on the orchestrator's hand-off ref, not in the tree, so no in-tree destination exists.

## Friction

- delivery-status-tracking: stale: `2041.md` and `2056.md` read `open` and the roster
  row reads `not-started` while both are merged and #1940 closed, so a seat dispatched
  on that text re-does a delivered group.
- gate-scoping: unclear: `closure.py select` with `--workdir` inside the worktree
  writes four `scope.*` files into the tree it measures, and the next run reads them as
  changed files and answers full mode where the diff is scopeable.
- fixer.md: cost: `mutation_table.py --scope changed` took about 50 min here while
  another seat's four-job pin drive held the box at load average 210, against the 5 s
  #2041's body recorded for the same command.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
