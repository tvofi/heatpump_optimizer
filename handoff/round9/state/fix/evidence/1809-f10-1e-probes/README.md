# F10.1d probes for the census-missed P7 sites (for R9-F10.1e)

Run each as `cd <repo> && HASTUB_TZ=Europe/Stockholm PYTHONPATH=tests/hastub:custom_components python3 <probe>.py`
(`_common.py` is the shared helper). Every probe drives the real production function with a fold (2026-10-25) or spring-gap
(2026-03-29) pair of stamps that share one ZoneInfo; HEAD and the unmodified main tree give identical output.

| site | verdict | probe | one-line fix |
|---|---|---|---|
| legionella.py:206 hold minutes | MISFIRE | probe_legionella.py | `utc_elapsed_seconds(now, previous_obs) / 60.0` |
| legionella.py:222 refusal window | MISFIRE | probe_legionella.py | `utc_elapsed_seconds(now, previous) < 3600` |
| legionella.py:300 12 h boost bound | MISFIRE | probe_legionella.py | `utc_elapsed_seconds(now, started)` |
| legionella.py:344 credited-since-start | MISFIRE | probe_legionella_credit.py | `utc_elapsed_seconds(self.last_cycle, started) >= 0` |
| drift.py:129 last_fed window | MISFIRE | probe_small.py | function-local `from .accuracy import utc_elapsed_seconds` (accuracy imports drift) |
| comfort_learning.py:102 decay | MISFIRE (~3%) | probe_small.py | `utc_elapsed_seconds(now, self.last_update) / 86400.0` |
| external_heat.py:462 confidence | MISFIRE | probe_small.py | `utc_elapsed_seconds(now, state.last_active) / 60.0` (import exists) |
| sysid.py:1299 arm interval | MISFIRE (low) | probe_small.py | `utc_elapsed_seconds(now, self.last_run) / 86400.0` |
| sysid.py:1585 phase clock | MISFIRE | probe_small.py | `utc_elapsed_seconds(now, self.phase_started) / 3600.0` |
| coordinator.py:4594/4703/4892 learner dt_h | MISFIRE | probe_learners.py | `utc_elapsed_seconds(now, previous_time) / 3600.0` |
| coordinator.py:8543/8554 outage holds | MISFIRE (fold only) | probe_outage_boost_away.py | `utc_elapsed_seconds(until, now) > 0` |
| boost.py:65-81 | MISFIRE (fold and spring) | probe_outage_boost_away.py | `utc_elapsed_seconds` for compares, `utc_shift(now, _MAX_LEAD)` for the add |
| away.py:469 hours_until_return | MISFIRE (presence end_time path) | probe_outage_boost_away.py | `utc_elapsed_seconds(return_time, now) / 3600.0` |
| away.py:249 expire_override | CLEAN in production | probe_outage_boost_away.py | none (callers pass fixed-offset stamps) |

Unprobed, same class: sysid.py:781/1728/1733 (SysIdSample.when differences) and wood_fuel.py:280 (typed-slot duration).
`census.rx` is the widened rule; it matches every row above.
