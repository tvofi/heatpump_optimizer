The scheduled nightly at d08ed31049 (run 42934263129, job 130240315059) failed `slow` on `synthetic-dhw-only.json: cycle_cost` and `cycle_cost sees a doubled cycle cpu`. The clean synthetic `cpu_ratio` 1.7266 at a job ruler of 40.22 ms (class ref40) is under the floor of the ref40 budget 3.9874, which rested on two draws from before 17bb738485 (one BLAS `ThreadpoolController`, #3349). That commit cut the cycle's CPU on CI to 0.61-0.66x. This is an improvement, not a regression.

Every runner class's synthetic `cpu_ratio` budget is re-derived one-sided down for the post-cut code. The re-derivation covers every class, not only the classes drawn since the cut. `tests/replay_cost_draws.tsv` gains job 130240315059's rows (`replay_draws.py parse`). `tests/replay.py` `COST_CUTS` declares the cut: commit 17bb738485, `from` 2026-11-08T17:14:34Z, factor 0.6339, and its evidence. `cost_draws` projects every synthetic `cpu_ratio` created before `from` by that factor, so `derive_cost_classes` centres no class on pre-cut readings. The old and new budget per class, and the draws behind each, are in the commit message. No budget rises. The bands and the class-free budgets are unchanged.

`from` is the commit's own time, not the merge's. #3349's own CI draw (job 128866186676, 1.5508) carried the cut at 2026-11-08T21:05:57Z, and #3349 merged at 2026-11-09T14:40:57Z. No draw in the table falls between the two.

**Decision for the reviewer: the factor is CI's, not the box's.** The brief asked for the factor measured interleaved on one box. I measured 17bb738485^ against 17bb738485 interleaved on this container (4-core Linux, Python 3.14, ruler 26.7-31.0 ms) and read 0.8715. CI's own runners read 0.6124 (ref40) and 0.6562 (ref47). The cut removes a per-minimize library rescan, and what that rescan costs depends on the runner. The box therefore bounds the direction of the change but cannot stand in for CI's factor. Projecting by 0.8715 would leave each pre-cut class's floor above the readings its post-cut draws will take. For example, ref23's floor would be 1.69 against an expected post-cut low of about 1.25. The declared factor is the geometric midpoint of the two CI ratios, 3.4 % from each. ref23 has the widest class spread (1.837x), which leaves a 4.3 % margin on each side, so a true ref23 factor anywhere in 0.612-0.656 lands inside its new band. Both measurements are recorded in `COST_CUTS`'s `evidence`, which is where the next re-record reads.

Roster carry of this group (R10-HOTFIX-REPLAY-CLASS-CUT), built here: the root-cause countermeasure of R10-RCA-REPLAY-CLASS-RERECORD. The cause is state (c): the stated re-record procedure was obeyed, and its unit, the drawn class, is wrong. The countermeasure is `level_shift_offenders`, run as the `control:cycle_cost:level_shift` control. Within each class it orders the clean draws by `created`. A level shift at T exists when every draw at or after T is under the floor (budget / 2) that the draws before T derive. Every other class must then hold a draw created at or after T, or a declared cut must explain the shift. A declared cut explains it when its `from` falls after the shifted class's last draw before T and at or before T, and it states a factor and evidence. Otherwise the control names the class: "class X rests wholly on draws before the shift class Y shows at T". It prints the classes it examined. `replay_draws.py shift [--table F] [--no-cuts]` runs it over any table. `field_coverage.mjs` registers the cut as the `replay_cuts` arm. Carry: R10-HOTFIX-REPLAY-CLASS-CUT

## Head

5cde26293067484d52963e9921bbfc1eadccefba, merge base ee64358be7eeccaec5178a923cb3b83a18a924a0 (origin/main at measurement, 2026-11-11 UTC).

## Mutation proof

Each mutant was applied to `tests/replay.py` at the head. I then ran `controls()` (`PYTHONPATH=tests/hastub python3 -c "import sys; sys.path[:0]=['tests']; import replay as R; print([n for n,ok,_ in R.controls() if not ok])"`) and restored the file:
- `COST_CUTS = ()` (cut declaration dropped) -> red: `control:cycle_cost:class_rule`, `control:cycle_cost:draws`, `control:cycle_cost:level_shift`, `control:cycle_cost:lane_prints_notice`.
- `if not all(v < floor for _, v in seq[i:]):` -> `if True:` (shift predicate) -> red: `control:cycle_cost:level_shift`.
- the cut's `evidence` emptied -> red: `control:cycle_cost:level_shift`.
- `node tools/policy/field_coverage.mjs --only replay_cuts`: each field of the cut perturbed reddens the two checks. `fixture`, `from`, `factor`, `evidence` and `metric` are read. `commit` is ignored, with a reason.

## Null control

- The demonstration the brief owed, run with `replay_draws.py shift`:
  - The table at d08ed31049, without the cut (`--no-cuts`), is red. It names ref23, ref28, ref31, ref38, ref40 and ref53 as resting wholly on draws before the shift class ref47 shows at 2026-11-08T21:05:57Z (floor 1.671), and exits 1.
  - The head table, with the cut, is green with 7 classes examined.
  - The healthy tables at 6715d97332 and 078780e687 read green with 7 classes examined, with and without the cut.
  - Dropping the cut at the head (`--no-cuts`) turns it red again, now naming the ref40 shift at 2026-11-11T00:48:46Z as well.
- In-run null: a draw planted after every other in the lowest class, at half its smallest reading and with no cut declared, names 6 of the 6 other classes.
- Box factor null: an A/A run (17bb738485^ against itself, 6 interleaved pairs) reads a post/pre median ratio of 1.0090. The A/B run (17bb738485^ against 17bb738485, 12 pairs) reads 0.8715, and the two ranges are disjoint (pre 2.1887-2.4074, post 1.8339-2.1428).

## Figures

- d08ed31049 table, no cut, red naming 6 classes: `python3 tools/audit/seat/replay_draws.py shift --no-cuts --table <(git show d08ed31049:tests/replay_cost_draws.tsv)`
- 6715d97332 and 078780e687 tables, green, 7 examined: `python3 tools/audit/seat/replay_draws.py shift --table <(git show 6715d97332:tests/replay_cost_draws.tsv)` (and the same for 078780e687, with `--no-cuts` too)
- Head, green, 7 examined: `python3 tools/audit/seat/replay_draws.py shift`; red without the cut: `python3 tools/audit/seat/replay_draws.py shift --no-cuts`
- Per-class budgets old -> new (commit message): `PYTHONPATH=tests/hastub python3 -c "import sys; sys.path[:0]=['tests']; import replay as R; print(R.derive_cost_classes(R.cost_draws(),'synthetic-dhw-only.json'))"`; old values at `git show ee64358be7:tests/replay.py`
- CI per-class ratios 0.6124 (ref40) and 0.6562 (ref47): post-cut clean draw over the geometric midpoint of the class's pre-cut clean draws, from `R.cost_class_jobs(R.cost_draws(cuts=()), 'synthetic-dhw-only.json')` and `R.cost_draw_created()`
- Box A/B 0.8715: `python3 tools/audit/seat/replay_draws.py interleave --pre <worktree at 17bb738485^> --post <worktree at 17bb738485> --pairs 12`; A/A 1.0090: `--pre` and `--post` both at 17bb738485^, `--pairs 6`
- Field coverage: `node tools/policy/field_coverage.mjs --only replay_cuts` (read=5 ignored=1 blind=0 refused=0); `node tools/policy/field_coverage.mjs --self-test` ok
- Replay controls: `PYTHONPATH=tests/hastub python3 -c "import sys; sys.path[:0]=['tests']; import replay as R; print([n for n,ok,_ in R.controls() if not ok])"` -> `[]`
- Structure: `python3 tests/structure.py` -> STRUCTURE RATCHET PASSED

## Red checks

none

## Forward-carry

none

## Friction

R10-HOTFIX-REPLAY-CLASS-CUT: contradiction: the brief's step 1 asks for the cut factor measured interleaved on one box, but a non-CI box reads 0.8715 where CI's runners read 0.61-0.66, because the cut's saving is a runner-dependent library rescan. The factor declared is CI's, and both readings are in `COST_CUTS`'s `evidence`, which is where the next re-record reads. Carry: dismissed: recorded in the cut declaration the next re-record reads, and named above as a decision for the reviewer
