R11 hotfix: main's scheduled Nightly `slow` job (feeding the non-required `tests / nightly-status`) is red on run 43783271327 (2026-11-16, head e30408f7). Its one failing check is in the step "Zone-sensitive scripts under Asia/Kolkata", `tests/features.py`:

`FAIL a start straddling a month boundary is counted and billed in the month of its first reading  [{'2026-03': 1}]` (1 of 5703 feature checks).

Cause: the R10-START-COUNTER-EDGES check (landed by #3598, merge cb19070965) builds its month-end edge as the UTC literal `2026-02-28 23:59:50Z`. Production keys both the start counter's month (`wear.StartCounter.fold`) and the wear ledger line (`ledger.month_key`) on the configured zone's wall clock, which is Home Assistant's convention for every other ledger month. Under any zone east of UTC that instant is already 1 March locally, so the count lands in March and the check fails. The production code is right; the check named an instant in the wrong zone. The fix builds the edge as 23:59:50 in the stub's configured zone (`_sce_dt.DEFAULT_TIME_ZONE`), so the check asserts the same thing in every zone, and corrects the comment's month (it said January; the check asserts February).

The 11-14 red (run 43536455429, head 50373173) was a different check: the charge-start dip check read the run's own weekday (11-14 was a Saturday, so `_chg_partial` booked the weekend day type). ed82d6a78f ("Pin the charge-start block's clock to a fixed Monday") fixed that before the passing 11-15 run. Neither red is a flake: each is deterministic for its date or zone.

## Head

78ce90616a570298d4c65b6a248197986702fbd9, cut from origin/main 6f422812d5d8b918beace0283419c153f6df66ce.

prepr: passed rc=0 at 78ce90616a570298d4c65b6a248197986702fbd9 (PREPR_SKIP_CODE=1 PREPR_SKIP_CLOSURES=1, the hotfix scope; CI is the authority).

## Mutation proof

With the fixed check, two production mutants, each run through the START-COUNTER-EDGES block under the gate environment, Asia/Kolkata and America/New_York (`tools/audit/seat/features_block.py` with the prelude from its `--emit-prelude`, driven by a seat-local loop over the zones):

- M1, `coordinator.py` `_book_starts`: `self._ledger.add(at, "wear", ...)` changed to `self._ledger.add(dt_util.now(), "wear", ...)` (wear billed at the release time, not the first reading). Result: `FAIL a start straddling a month boundary is counted and billed in the month of its first reading` in all three zones.
- M2, `wear.py` `StartCounter.fold`: `key = since.strftime("%Y-%m")` changed to the month of `since + EDGE_DEBOUNCE_S` (counted in the month of the confirmation). Result: `FAIL a start straddling a month boundary ...  [{'2026-03': 1}]` in all three zones.

Both restored before the commit.

## Null control

The unfixed check at origin/main 6f422812, the same block run: gate (TZ=UTC, HASTUB_TZ unset) and UTC 21 ok, 0 FAIL; America/New_York 21 ok (a zone west of UTC keeps 23:59:50Z in February); Asia/Kolkata, Asia/Tokyo and Europe/Stockholm 20 ok, 1 FAIL, the nightly's check with `[{'2026-03': 1}]`. The fixed check: 21 ok, 0 FAIL in all six of those runs.

## Figures

- Block results per zone: `PYTHONPATH=tests/hastub HASTUB_TZ=<zone> TZ=<zone> python3 tools/audit/seat/features_block.py --prelude 'exec(open(PRELUDE).read())' 'import asyncio as _sce_aio  # noqa: E402'`, PRELUDE written by `features_block.py --emit-prelude PRELUDE 'import asyncio as _sce_aio  # noqa: E402'`; counts are the `  ok` and `  FAIL` lines of its output.
- The class, one zone: the nightly's own Asia/Kolkata step at e30408f7 printed `1 of 5703 FEATURE CHECKS FAILED` (`gh run view 43783271327 --log-failed`), this check its only FAIL; `tests/finite_boundary.py`, which that step never reached under `bash -e`, run locally under Asia/Kolkata at this head: `ALL 114 FINITE BOUNDARY CHECKS PASSED`. The whole-suite sweep across zones (`dev/audit/harnesses/host_zone_features.py --suite`) was not run; the nightly is the authority for the rest.
<!-- figure-block: scope-line mb=6f422812d5d8b918beace0283419c153f6df66ce head=78ce90616a570298d4c65b6a248197986702fbd9 -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->

## Red checks

- `tests / nightly-status` (Nightly `slow`, non-required), red on main since #3598 merged: answered above. The cheaper detector exists, `dev/audit/harnesses/host_zone_features.py` (local, by hand); the per-PR gate runs `tests/features.py` only with `HASTUB_TZ` unset, and the zone lane is nightly by design, so a zone-literal check lands green and goes red at the next nightly. No new check is proposed here: moving the zone lane onto every PR adds a second whole `tests/features.py` run to every PR whose closure reaches it, and this zone red is the first the nightly lane has shown since it landed (R10-SUITE-HOST-DETERMINISM) by the two nightly logs read here; a recurrence is the trigger for `root-cause.md`.

## Forward-carry

none

## Friction

none
