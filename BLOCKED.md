# BLOCKED: r10-outside-learner-robustness-p2

Question: The brief's MEASURE acceptance (each scaled-tail press arm walks the house heat-loss scale no further than the whole window under the full tail) fails on tests/boost_drift_replay.py under both formulas tried. The heat-free null control shows the walk at that size comes from which samples the freeze skips, not from boost heat. Which acceptance do you want? (A) Keep the brief's absolute bound. Then no scaled formula is shown to pass, and the tail stays at the full 12 h for every length, so this part ships the sum, the persistence and the store work without the scaling. (B) Judge the heat's own walk: each press arm minus its freeze twin (same presses and tail, no heat) may walk no further than press_120x1_full minus freeze_120x1_full. If (B), which slope: the adopted one (one slab constant per e-fold, 6 h) or the halved one at 60b24a5b4a (3 h, with each press priced at the pump's 10-minute minimum on-time)?

## Measured

Every arm forks from one shared pre-boost state. Presses at 07:00, 12:00 and 18:00 on days 5 and 6. Each line is `worst` (the largest signed excursion of a 03:00 daily row from day 4's 1.0463), then `final`.

Instrument: `PYTHONPATH=tests/hastub python3 tests/boost_drift_replay.py <arms>` at this ref (argv-only arms: `press_<min>x<count>_<policy>` drives the true house with the boost for the share of each cycle the press held; `freeze_*` runs the same presses and tails with the house on the plan, so it adds no heat).

Null controls:

- `null_no_boost` at origin/main 26072317b5 and at this head: +0.0045 / +0.0236 at both. The daily rows are identical (1.0455, 1.0472, 1.0499, 1.051).
- `press_120x1_full` = `press_120x1_scaled`: -0.0045 / +0.0216. This is the bound.
- `freeze_120x1_full`: -0.0045 / +0.0221.

Adopted slope (6 h; commit 7a76f66c8a; tails: 10 min to the 1.5 h floor, 30 min to 3.68 h):

| arm | none | scaled | full |
|---|---|---|---|
| press 10x1 | -0.0010 / +0.0197 | +0.0028 / +0.0227 | -0.0045 / +0.0226 |
| press 30x1 | +0.0021 / +0.0227 | **-0.0129** / +0.0204 (FAIL) | -0.0045 / +0.0229 |
| press 60x1 | +0.0077 / +0.0247 | -0.0045 / +0.0205 | -0.0045 / +0.0205 |
| press 120x1 | +0.0441 / +0.0295 | -0.0045 / +0.0216 | -0.0045 / +0.0216 |
| press 10x4 | +0.0052 / +0.0231 | -0.0045 / +0.0214 | -0.0045 / +0.0214 |

Halved slope (3 h, each press priced at least 10 min; commit 36f10fd3ba; tails: 10 min to 4.55 h, 30 min to 7.84 h):

| arm | scaled |
|---|---|
| press 10x1 | **-0.0237** / +0.0193 (FAIL) |
| press 30x1 | **+0.0051** / +0.0239 (FAIL, by 0.0006) |
| press 60x1 | -0.0045 / +0.0205 |
| press 120x1 | -0.0045 / +0.0216 |
| press 10x4 | -0.0045 / +0.0214 |

The heat-free twins, halved slope:

| arm | none | scaled | full |
|---|---|---|---|
| freeze 10x1 | -0.0037 / +0.0197 | **-0.0232** / +0.0183 | +0.0052 / +0.0252 |
| freeze 30x1 | | **+0.0067** / +0.0246 | |

The freeze alone walks the scale -0.0232, against -0.0237 with the heat behind it. The heat's own share of the failing 10x1 arm is -0.0005 on `worst`. The heat-free freeze_10x1_full (+0.0052) and freeze_30x1_scaled (+0.0067) also exceed the bound, as does the no-boost null's own `worst` (+0.0045, equal to it). The walk is also not monotone in the tail: press 10x1 reads +0.0028 at a 1.5 h tail and -0.0237 at 4.55 h. On this instrument a bound of 0.0045 is inside what the freeze's sample selection moves on its own. Chasing it with the formula would tune the tail to this scenario's hours, not to the heat.

A finding apart from this part: a freeze with no heat behind it, 4.55 h after presses at 07:00, 12:00 and 18:00, walks the scale -2.3 % in a day. The interval learner's residual has a time-of-day structure that a freeze of these hours biases. Not filed; it is the measurement above, for whoever owns the interval learner's freeze to rule on.

## State at this ref (head of handoff-wip)

- origin/main 26072317b5 merged (one conflict, in tests/features.py; both blocks kept).
- Mutation proof on the halved slope (features block "#1935 follow-up" through the counter-span block, `tools/audit/seat/features_block.py`): the tail returning the full tail fails 2 checks (the scaling and sweep checks), returning the floor fails 8, a press priced alone fails 4, a press priced below the minimum on-time fails 2, the persisted tail dropped fails 2, and the null mutant fails 0. The block itself: 14 checks, all pass.
- Store both ways (BOOST_STORE_VERSION unchanged at 1), refit sibling (full tail, which bounds every scaled tail), the freeze-reason order, and a never-boosted payload equal to main's are pinned in that block.
- `tests/structure.py` passes. archscore `--diff` against the merge base: IMPROVES (literal_clone_copies 122 -> 120 via store `_Z0`, coord_footprint 2492 -> 2491).
- Scoped gate (`GOLDEN_MODE=drift GATE_SCOPE=auto tests/run.sh`, MODE: SCOPED, 29 scripts) partly run at 36f10fd3ba: 14 steps finished `ok` and none failed when this was written, features.py among them (624 s). It was not run to completion. Not handed off: no body, no prepr.sh.
- Forward-carry owed to R10-OUTSIDE-LEARNER-ROBUSTNESS-P3, whatever the ruling: the contributor's `learning_freeze` projects a live overlay's tail end as `settle_tail(elapsed since start)`. That ignores the boosted sum and the press minimum this part adds. P3 must project through BoostState's sum, not recompute it.
