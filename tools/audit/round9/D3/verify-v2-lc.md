# Verifier V2 (independent), unit lc — D3

## D3-s1-91: coordinator.py tzinfo guards (:8112, :8384) dead under the gate's naive clock

Step 1 (re-run finder's harness, `tools/audit/round9/D3/s1/leads/lc_tz_probe_coordinator.py`):
reproduced exactly — `comparable_ts_586_differs_utc=1`,
`comparable_ts_588_differs_utc=1` (a different guard family, not this
finding's claim), and, for the finding's own site (:8384,
`_immersion_dhw_margin`): `immersion_margin_8384_differs_hastubtz_unset=0`,
`immersion_margin_8384_differs_hastubtz_stockholm=1`, with the GUARD_OFF arm
raising `TypeError: can't compare offset-naive and offset-aware datetimes`
once HASTUB_TZ=Europe/Stockholm. thread_factor=1.0 (no BLAS on this path),
load1=0.61.

Step 2 (own harness, `tools/audit/round9/D3/verify-v2/lc_v2_detect_outage_probe.py`):
own metric, on the *other* named site — `_detect_outage` (:8112), which the
finding claims is "identical shape" but which the finder's harness never
actually drove (only :8384 was executed; :8112 was asserted by shape, not
measured). Result: `detect_outage_8112_now_tzaware_default=0`,
`detect_outage_8112_differs_hastubtz_unset=0` (GUARD_ON and GUARD_OFF agree
byte-for-byte under the gate's own default clock — the clock frozen once per
arm with `dt_util.freeze` so both calls see the identical `now`, avoiding a
timing-artefact false divergence from two independent `dt_util.now()` calls),
`detect_outage_8112_differs_hastubtz_stockholm=1`,
`detect_outage_8112_off_raises_stockholm=1` — the GUARD_OFF arm raises
`TypeError: can't subtract offset-naive and offset-aware datetimes` once
HASTUB_TZ=Europe/Stockholm. cpu_s=0.006, thread_factor=1.0, load1=0.37 (0.52 on
first take), swapins=0. This independently confirms the "identical shape"
half of the claim the finder did not execute.

Metric definitions:
- Finder: whether GUARD_ON and GUARD_OFF variants of `_immersion_dhw_margin`
  agree on one fixed scenario, under two `HASTUB_TZ` settings.
- V2 (mine): whether GUARD_ON and GUARD_OFF variants of `_detect_outage`
  (the sibling guard at :8112) agree on one fixed naive-last-tick scenario
  that actually crosses `OUTAGE_GAP_MINUTES` (so the code past the guard
  executes), under the same two `HASTUB_TZ` settings, with the stub clock
  frozen so both variants see one identical `now`.

Attacks (verifier.md step 3, in order):
1. Contention: count/behavioural-divergence metric, no timing claim;
   load1 quoted above for both runs.
2. Wrong gate mode: checked `env_drift.py` (`--all` is what CI runs) and
   `tests/golden.py` — no fixture, scenario or `SCENARIOS` entry sets
   `HASTUB_TZ` or otherwise produces an aware `dt_util.now()`
   (`grep -n "HASTUB_TZ|time_zone|tzinfo" tests/golden.py` — no hits), so the
   guard is dead under `--all` too, not just the default 5-fixture check.
   This is not a "wrong gate mode" false gap.
3. Grid artefact: not an aggregate; single fixed scenario per site, no
   cell-dropping needed.
4. Null control / alternate reachability path: searched for every other
   `HASTUB_TZ` setter in the suite (`grep -n HASTUB_TZ tests/*.py`). Found
   one besides `dst_checks.py`: `tests/replay.py:933` sets `HASTUB_TZ` from a
   fixture's own `time_zone` field, and exactly one committed fixture
   (`tests/replay/synthetic-dhw-only.json`) is `Europe/Stockholm`. This is a
   real alternate exposure path the finder's claim ("only
   tests/dst_checks.py's subprocess sets [HASTUB_TZ], for a different file")
   understates slightly. However: `tests/closure.py:119` and
   `tests/run.sh:304` (`replay.py) continue`) both confirm `replay.py` is
   explicitly excluded from the gate ("a step of the nightly `slow` job, not
   a gate script"), and the fixture itself contains no immersion-feedback or
   outage-recovery state to drive either named guard even if it ran. This
   attack does not survive: it does not change gate-invisibility, only
   sharpens which non-gate lane also happens to set `HASTUB_TZ`.
5. Real HA reachability: both guards read `dt_util.now()` and a
   caller-supplied/stored ISO timestamp — no `FakeHass` executor shortcut is
   in this path (confirmed: no `async_add_executor_job` between the
   timestamp parse and the guard). Reachable identically in real HA whenever
   `hass.config.time_zone` is non-UTC, which is the ordinary case for a
   non-English-speaking install, not a corner case.
6. Severity: `medium` — this is a test-suite gap (stop_rule_class: bug /
   class_guess: I1), not a live defect: the guard, when present, works and
   only crashes if *removed*; the risk is that the gate would silently pass a
   future removal of the guard as a "no-op simplification". Consequence if
   that happened: an uncaught `TypeError` in `_detect_outage`/
   `_immersion_dhw_margin` on any TZ-aware install with a naive stored
   timestamp, which is caught only by `_async_update_data`'s blanket
   `except Exception` (same seam family as D1-s2-91) and fails the whole
   cycle. `medium` (bounded, contingent on a future edit, with a known
   workaround — the guard staying in place) is not inflated.

Step 4 (test-gap claim — production mutation and file): the recorded mutant
is the *deletion of the two guard lines* at
`custom_components/heatpump_optimizer/coordinator.py:8384`
(`if when.tzinfo is None and now.tzinfo is not None: when = when.replace(...)`)
and, by the identical-shape argument I independently executed above, the
matching two lines at `coordinator.py:8112`. Both the finder's recorded run
and mine show this single-line-family mutation is byte-identical (0
divergence) under the gate's own default clock and diverges only once
`HASTUB_TZ` is set — which no gate-run script does. The killing input
(HASTUB_TZ=Europe/Stockholm) is not a mutation-pool artefact and is not in a
test file; it is `dst_checks.py`'s own subprocess environment variable
exercising unrelated code paths in the *same file*, so the mutation itself
stands unnoticed by anything the gate runs. No suite run was executed under
an actual mutant (per the no-heavy-D3-re-run rule); this cites the two
harnesses' recorded/reproduced counts instead.

**Vote: verify.** The finder's number reproduces exactly, my own
independently-measured number on the sibling site behaves identically (dead
under gate default, crashes once unblinded), and the one attack that looked
like it might weaken the claim (an alternate `HASTUB_TZ` setter in
`replay.py`) does not survive because that lane is excluded from the gate and
its one non-UTC fixture doesn't exercise either guard.
