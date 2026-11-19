# D3-top6 T3 split: full net (prescreen.py complete) over the 33 owed survivors

Baseline 92d38ecb640bd462f2e19c0814d0f0b7df1ee692. Owed = the 35 SURVIVED results under state/results/{pre,c2,c3c6} of seat D3-s1, minus the 2 already under state/results/complete/ (4e2df5f23e4eff29, a0605da712a6a070). M22 (6e6026d857732e96) is included because T1 left it SURVIVED.
Cost basis: the summed seconds of each mutant's deferred_slow + relaxed_skipped drivers, from traced baselines re-taken 2026-11-18 on the local 8-core M1 (state/baselines.json). Every mutant comes to about 1990 s, so the parts are 11 + 11 + 11, each about 21900 s of driver time (provisional). Measured complete wall on the contended 4-vCPU box D3R: 6678 and 6735 s per mutant.

## Setup per box (once)

1. Seat worktree at the baseline. Restore the D3-s1 directory from `seats/D3-s1/` of this ref (or from refs/heads/handoff/audit-r11-find-D3R, c0adbc19). Add ONE empty marker commit on top of the baseline, so HEAD^1 = baseline; prescreen.py drives env_drift against HEAD^1: `git commit --allow-empty -m marker`.
2. `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round11/D3/s1/prescreen.py baseline --workers 3` re-takes the traced baselines on that box. Then run the null control `prescreen.py null` (must print null_verdict=LIVES) and the positive control `prescreen.py run --anchors dev/audit/rounds/round11/D3/s1/posctl_anchors.txt --sub posctl-T3 --workers 2` (2 of 2 must be KILLED). If either control fails, stop and report its lines.
3. Export D3S1_FRESH_TREE=1. Never run the state/*.sh launchers.

## Command for part N (from the seat worktree root)

```
K=dev/audit/rounds/round11/D3/s1/t3_partN_keys.txt   # copy T3/partN_keys.txt from this ref to that path
for SRC in pre c2 c3c6; do
  PYTHONPATH=tests/hastub D3S1_FRESH_TREE=1 python3 dev/audit/rounds/round11/D3/s1/prescreen.py complete --src $SRC --keys $K --workers 3
done
while read k; do [ -n "$k" ] && python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); r["key"]=sys.argv[2]; print(json.dumps(r))' dev/audit/rounds/round11/D3/s1/state/results/complete/$k.json $k; done < $K > partN.jsonl
```

With --keys, complete takes only the keys from that file that exist in --src, so the three-source loop covers every key once. Keys already under results/complete/ are skipped, so a re-fire resumes.

## Killed vs survived

For each mutant, `prescreen.py complete` re-drives every driver the fast drive deferred (slow) or skipped by relaxed reach, with no relaxation and no early stop. A driver kills when `tests/mutation_table.py:killed` holds: the run is red AND it fails more checks than that driver's traced baseline on the same box. verdict = KILLED if killed_by is non-empty, else TIMEOUT if any run timed out, else SURVIVED. A TIMEOUT is not a survivor: report it and re-drive it. Every wall figure is provisional; record it with nproc, the CPU model and load1.

## Where results land

One file per part: `seats/D3-top6/T3/partN.jsonl` on refs/heads/handoff-wip/finder-r11-D3-top6. Each line is a state/results/complete/<key>.json record with its key added. Put the box's prescreen.log and the control outputs beside it as `partN.log`.

After collection, the full gates on the remaining T3 survivors (fullgate.py, one at a time) stay with the local D3-top6 seat.

## Part 1 (11 mutants, est 21905 s of driver time)

| src | key | site | kind | old -> new |
|---|---|---|---|---|
| pre | 3885e472b8297a90 | flow_lift.py:183 | GUARD_OFF | `if not np.isfinite(measured_supply) or not np.isfinite(curve` -> `if False:` |
| pre | bdcf7589b0a0a6df | coordinator.py:539 | GUARD_OFF | `if displace_raw is None and isinstance(data.get("command"), ` -> `if False:` |
| pre | 61f74c4474262dad | coordinator.py:687 | GUARD_OFF | `if (message, cause) not in _FENCED_CAUSES:` -> `if False:` |
| pre | 23621370731667b7 | defrost.py:559 | GUARD_OFF | `elif any(k in data for k in ("duty", "duty_counts")):` -> `elif False:` |
| c2 | c38d53ab787ddbfa | price_model.py:252 | R10C2 | `if float(np.mean(values)) <= 1e-6:` -> `if float(np.mean(values)) < 1e-6:` |
| c2 | 66f8a4fb50e0b1f3 | defrost.py:783 | R10C2 | `if flag and not self._state:` -> `if flag or not self._state:` |
| pre | fb16c7b0cbbfc63d | tariff.py:64 | GUARD_OFF | `if window <= 60:` -> `if False:` |
| pre | 639d439d71b731ce | dhw_planner.py:75 | GUARD_OFF | `if holiday_flags is not None and index < len(holiday_flags):` -> `if False:` |
| pre | 0318c921405fefbe | dhw_planner.py:473 | GUARD_OFF | `if space_demand is not None:` -> `if False:` |
| c3c6 | 0911281eca895664 | dhw_planner.py:1559 | R10C2 | `shortfall_price = 1000.0 * (float(np.max(np.abs(prices))) + ` -> `shortfall_price = 1000.0 * (float(np.min(np.abs(prices))) + ` |
| pre | 121362d48b408236 | grid_fee.py:173 | GUARD_OFF | `if not sep:` -> `if False:` |

## Part 2 (11 mutants, est 21905 s of driver time)

| src | key | site | kind | old -> new |
|---|---|---|---|---|
| c3c6 | a4b00ac3ca662eec | thermal_model.py:835 | R10C2 | `if swing <= 0.0:` -> `if swing < 0.0:` |
| pre | a35e03bd09f563c7 | sysid.py:677 | GUARD_OFF | `if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9) or not set` -> `if False:` |
| pre | 4b3795aece73ba73 | price_model.py:201 | GUARD_OFF | `if not np.all(np.isfinite(values)):` -> `if False:` |
| c3c6 | 5e8d48eff7e4fa8d | coordinator.py:8806 | R10C2 | `if tariff.enabled and factor > 0.0:` -> `if tariff.enabled or factor > 0.0:` |
| c2 | aae7c9c380c3c5cf | sysid.py:1593 | R10C2 | `return peak <= bound and final <= bound` -> `return peak <= bound or final <= bound` |
| c2 | 2719aef4cbb8b464 | price_model.py:337 | R10C2 | `if not day_types or not np.isfinite(level) or level <= 0.0:` -> `if not day_types or not np.isfinite(level) or level < 0.0:` |
| pre | acc8fa3942789f45 | thermal_model.py:270 | GUARD_OFF | `if not np.isfinite(value) or value < THERMAL_MASS_FLOOR:` -> `if False:` |
| pre | 0c3e91a6a349409a | flow_lift.py:47 | CONST | `FLOW_BIAS_ALPHA = 0.1` -> `FLOW_BIAS_ALPHA = 0.2` |
| c3c6 | 6e6026d857732e96 | tariff.py:595 | R10C2 | `return bool(tariff.months) or (` -> `return bool(tariff.months) and (` |
| c2 | d931ab195b940b0c | tariff.py:744 | R10C2 | `if x.size == 0 or k <= 0:` -> `if x.size == 0 or k < 0:` |
| c3c6 | 5cc84148fa68bda1 | grid_fee.py:383 | R10C2 | `if rule.rate < lowest:` -> `if rule.rate <= lowest:` |

## Part 3 (11 mutants, est 21905 s of driver time)

| src | key | site | kind | old -> new |
|---|---|---|---|---|
| c2 | a0b3b28854fa500c | flow_lift.py:188 | R10C2 | `if self.samples < FLOW_BIAS_MIN_SAMPLES:` -> `if self.samples <= FLOW_BIAS_MIN_SAMPLES:` |
| pre | 73bc722df73caecb | price_model.py:198 | GUARD_OFF | `if len(hourly_prices) != HOURS_PER_DAY:` -> `if False:` |
| pre | 460217277822d5bd | sysid.py:610 | GUARD_OFF | `if not (c_r > 1e-9 and c_s > 1e-9 and k_s > 1e-9):` -> `if False:` |
| c2 | fc395b83eeb1ddbf | price_model.py:532 | R10C2 | `for i in range(min(known_count, len(step_start_times)))` -> `for i in range(max(known_count, len(step_start_times)))` |
| c2 | 8e82d7a0b3617003 | sysid.py:1549 | R10C2 | `in_window = hour >= cfg.start_hour or hour < cfg.end_hour` -> `in_window = hour > cfg.start_hour or hour < cfg.end_hour` |
| c2 | 0e172028a23d9372 | sysid.py:2246 | R10C2 | `if ua_ss > 0.0 and abs(ua_ss - ua) / ua > 0.10:` -> `if ua_ss > 0.0 or abs(ua_ss - ua) / ua > 0.10:` |
| pre | 65f121eb047174ad | optimizer.py:773 | GUARD_OFF | `if not holiday_dates:` -> `if False:` |
| pre | 050fdc4a20eba212 | thermal_model.py:169 | GUARD_OFF | `if not spec:` -> `if False:` |
| c3c6 | 22b5ec8775d5bd50 | thermal_model.py:2593 | R10C2 | `) / max(dt_hours, 1e-6)` -> `) / min(dt_hours, 1e-6)` |
| c2 | ad5900dadd86e9f9 | tariff.py:64 | R10C2 | `if window <= 60:` -> `if window < 60:` |
| c2 | 95779f9d6d71c50d | grid_fee.py:355 | R10C2 | `if abs(rule.rate) > worst:` -> `if abs(rule.rate) >= worst:` |
