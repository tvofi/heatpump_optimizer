<!-- ccr-projects-attribution: {"github_login":"tvofi"} -->
_Requested by **tvofi**_

Fixes #1660 (N-future-instant). Part of #201.

Before: a stored heartbeat (`last_tick`) written by a clock that ran ahead masked a real power cut. The energy store bounds a stored instant to now at load, and the outage detector reads at that same now, so the gap came out zero and the staggered recovery stayed closed. The four sibling seams F3.1's store boundary closes (the fuse advisor's 7-day cooldown, the heavy-snow damping window, the immersion margin, the legionella cycle) had no regression test through their real store and loader.

After: a heartbeat ahead of the clock reads as an outage, which is tvofi's rule (card C13, #775's rule). The four closed seams each have a test that drives the real store and loader with a stamp ahead of the clock, and each reads the defect when the store's bound is switched off.

How: the store reports the paths it rewrote (`QuarantiningStore.bounded`), and the outage reading takes that report as "ahead" while a raw stamp ahead of now reads the same way. The bound is unchanged, so no allow-list entry is needed. The outage reading moved into a module-level function, so the coordinator class is 8 lines smaller than before and no budget is raised.

## Head

cf0d110352351cb8fb76cc4000e669bf91f3bdd6, merge base 6793659caed93f5a47bc7cc940f119b9e2abcbeb (`origin/main` at measurement, `date -u` 2026-10-01).

## Mutation proof

Each mutant is applied in a copy of the package, run against the five rows of the `R9 N-future-instant` block in `tests/features.py`, then restored (control: the restored tree reads five ok).

- FI-sw3, store report dropped (`"last_tick" in self._energy_store.bounded` replaced by `False`): FI-sw3 red, the other four ok.
- FI-sw3, raw-stamp rule dropped (`ahead = ahead or gap_minutes < 0.0` replaced by `ahead = ahead`): FI-sw3 red. Only the row's "unbounded" arms reach it.
- FI-sw3, predicate ignores `ahead` (`and not ahead` deleted): FI-sw3 red.
- FI-sw3, the store stops reporting (`hits.append(...)` replaced by `pass`): FI-sw3 red.
- FI-sw1, FI-sw2, FI-sw4, FI-rca1 (closed by F3.1, tests only): with `store._bound_instants` replaced by the identity, all five rows go red, reading the baseline defect: cooldown held, damping on, immersion margin 2.0, legionella due in 168.0 h, outage masked.

## Null control

- Every row carries its honest arm: a recent honest stamp still holds the cooldown, the damping, the immersion margin and the legionella interval, and a real 6 h cut, a plain 10 minute restart and a tick at the restart instant read as before (cut true, restart false, tick at now false).
- `python3 tests/finite_boundary.py`'s instant arm still passes: an honest payload comes back byte-identical, and an instant inside a store's lead survives.

## Figures

- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED`; every script it named ran green locally except the ones listed under Red checks.
- Structure: `python3 tests/structure.py` exits 0. `coordinator_loc` and `max_class_loc` were re-recorded down (commit `budgets(R9 F1.9)`); no budget went up.
- Class sweep (fixer.md step 8): the S7 enumerator `$EXPORT/tools/audit/round9/D14/sweep/persisted_future_instant_unbounded/enumerate.py`, `EXPORT` being `git archive 1152a74346 tools/audit/round9/D14/sweep | tar -x` (sha1 80afe72fb21b86fd70068dafcead75dc0732348f), run from the repository root at the merge base and at this head (`diff` of the two outputs: only line numbers moved, 19 sites at both). Its seams and their dispositions:
  - coordinator.py `_last_heavy_snow` restore: FI-sw2, closed by F3.1, tested here.
  - coordinator.py `_immersion_events` read (immersion margin): FI-sw4, closed by F3.1, tested here.
  - coordinator.py the fuse advisor's stored stamp (the ledger reader): FI-sw1, closed by F3.1, tested here.
  - coordinator.py the outage reading's parse (moved to `_outage_reading`): FI-sw3, closed in this diff.
  - legionella.py `last_cycle`/`last_attempt` (parse_datetime, outside the enumerator's grep): FI-rca1, closed by F3.1, tested here.
  - drift.py, snapshots.py, curve_learning.py, comfort_learning.py, boost.py: closed by F3.1 (the stored-instant rule and the boundary).
  - pump_arbiter.py write-echo grace: FI-sw5, closed by F3.2, its row already in `tests/features.py`.
  - store.py (the bound and the domain tables), coordinator.py `_snow_accum_last`: the first is the boundary itself, the second is read through the same bounded thermal-learning store.
  - accuracy.py, coordinator.py day-key constructions and the tz helper, manual_plan.py, open_meteo.py, price_model.py, wood_fuel.py: not applicable (position-pruned, a calendar-day string, a live fetch, or a service input); manual_plan.py is its own class (D1-s2-54).
- The RCA's `repro_loaders.py` (sha1 f10ee0ee15d76be05d3acf5ec4906aa27b0a0a66) stops at its boost row on this base (it compares a naive clock to a stamp the boundary now returns aware). Its rows were re-expressed with aware clocks in the five-row block; at F3.1's boundary the outage row is the one that stayed false.
- Not run here: `tests/typing_ruler.py --mypy` (needs Python 3.14.2; this seat has 3.11 to 3.13 and 3.14.0rc2, and the ruler refuses to measure on an unpinned interpreter) and `tests/ha_contract.py` against real Home Assistant (same interpreter floor); both are left to CI. This diff touches no Home Assistant symbol.

## Red checks

none at hand-off: no check has run red on a commit of this branch, and every script the scoped gate named ran green locally (`features.py` 3631 checks, `entities.py` 1996, `finite_boundary.py`, `golden.py` in drift mode against the merge base, `structure.py`, the card and doc lanes). CI has not run on this head; the two lanes this seat could not run are named under Figures.

## Forward-carry

none. `tools/audit/bugclasses.json` is updated in this diff, where it still said FI-sw3 waited on tvofi's rule; `.claude/workflows/carry-1660.json` still names F1.9 and needs no change, because no later stage's work changes.

## Friction

none
