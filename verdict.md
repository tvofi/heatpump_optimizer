Fix review: blocked e310b8bb31cc8168a9bbc13363a00ad1b7c2ee87 metric-gamed: structure: coordinator class_excess_loc and max_class_loc paid by joining lines in async_arm_system_identification, re-wrapped in the base layout the ratchet breaches +5

bus-nonce: 5b7c1b5ab0649fa9f8492b63f49969ad

Round 1 (first review of #3050). Head reviewed: `e310b8bb31cc8168a9bbc13363a00ad1b7c2ee87`, from a detached worktree at that SHA, base (merge base) `2b6bef7453a8bdaf97d42f382a116ce226b35ccc`. Contract: `dev/governance/roles/fix-review.md` at origin/main (`git diff $(merge-base)...origin/main -- dev/governance/roles/` empty).

## Block

fix-review.md step 14, fixer.md step 17 ("Never move a metric by a change that does not improve the code"). The body's Figures row says the coordinator's -3 on `class_excess_loc` and `max_class_loc` comes from "the arm method's three-line call and four-line log, joined, are -3" and "the stand-down gate's comment, four lines at the base, is three lines" and "the quiet-window read rides the gate's existing expression line". That is the mechanism; I removed it as the null control. Re-wrapping ONLY `async_arm_system_identification` in the base's own layout (its `arm(` call over its arguments, its `_LOGGER.info(` over four lines, as at `2b6bef745`; the shortened comment and the quiet-window line left as the head has them), `ev/null_rewrap.diff`:

- `RESULT class_excess_loc=17654` against budget 17649: `FAIL class_excess_loc 17654 > 17649 (+5)`
- `RESULT max_class_loc=8061` against budget 8056: `FAIL max_class_loc 8061 > 8056 (+5)`, and 8061 is above the merge base's own 8060 and the base budget 8059.

So the coordinator does not shrink; it grows by about one line, and the ratchet passes only because two statements are joined onto 120- and 140-column lines and the new `quiet_reason` call is appended to an existing expression line. The recorded budgets (17649, 8056) then lock that formatting in as if it were payment. The `SystemIdentification` -1 (the dead `return True` of `_begin_step_phase`) is a real simplification and is not part of this block.

Remedy: lay the coordinator's added lines out normally and pay the real growth (about +1 on the coordinator class, about +5 against the recorded budget) by a change that improves code. The body already names one candidate it rejected, a mechanical split, which does not count either. If no such payment exists, the alternative is the budget-raise path with the owner's confirmation before the push (CLAUDE.md rule 2; `budget-raise-gate`, 0013), not re-recording the joined lines.

Everything else I checked holds (Evidence). I would expect a re-cut that only changes the layout and payment to pass the rest unchanged.

## Findings

- The accessor's "median" is unpinned. Replacing `np.median` with `np.mean` in `DrawRange._ceiling_median` (`draw_range.py`) survives the R10-CEILING-PROBE block (57 checks) AND the whole `tests/features.py` (rc=0). Every store in the checks holds identical values (`_cp_store([3.0] * 12)`, `[4.5] * 12`), and the synthetic pump's draws are constant, so median, mean and any central statistic agree. The raw median is the contract part D consumes (a single low interval, a cut step or a partial draw, moves a mean and not a median). One check with a skewed store, for example eleven at 3.0 and one at 1.0 giving 3.0, kills it. This is my own targeted mutant, not one of the 75 `mutation_table` candidate sites, so `tests / mutation` cannot see it. Carry: R10-CEILING-PROBE
- The body's Carry 1 (a) still says the set-point-to-draw gain "routes it nowhere. Routing it is the orchestrator's", and `## Forward-carry` cites only s9-ceiling-copgate-iface. The orchestrator routed the gain gap (s9-ceiling-gain-gap) to R10-COP-GATE at roster commit `cec6621b4` (`handoff/audit-r10-roster`), where the text is present. The body states the gap honestly: it does not claim the probe measures intermediate-level gain. But it should cite the landed carry instead of saying it is unrouted. That is a body edit on the re-cut. Carry: R10-COP-GATE
- `## Head`'s first paragraph says `e310b8bb3` "resolves by hand the one conflict in merging origin/main 2b6bef745 into the previous head fba24c239". By the trees, the hand union is in `94d0669db` (merge of main `a7dd7f50d` into `fba24c239`). `e310b8bb3` merges `2b6bef745` into `94d0669db`, and its claim file is byte-identical to parent 1's, because main did not touch `claimed_drift.txt` between `a7dd7f50d` and `2b6bef745`. The second paragraph does name parent 1 correctly. The union itself is correct (Evidence), so this is only the body's wording. Carry: dismissed: description only; the union and the head SHA named in the body both verify
- `merge_train.py classify` reads this head RED on `gate`. The red is two deferring `gate` runs (jobs 124733639993 and 124734678917: "run(s) [41262300367] at this head are still being judged; their gate decides"), whose deciding suite's gate passed (job 124737196827, `PASS`). Nothing in this PR's code or body causes it. The orchestrator re-runs those two jobs, or rules on them, before any merge train reads this PR green. Carry: dismissed: deferral reds of the gate harness, not this PR's; the deciding suite's gate passed and pr-contract after them is green

## Evidence

- Merge with main: `git merge-tree --write-tree origin/main e310b8bb3` (origin/main `8fec54ee2`) exits 0, tree `f7261d9d5`, with `LEDGER-MERGE: resolved tests/closures.json` only. No claim-file conflict and no `MERGE-CLAIM` line.
- Claim-file union (orchestrator.md section 6), rebuilt from the trees (`ev/claim_*.txt`, `ev/d*_*.txt`):
  - The hand merge `94d0669db` = `fba24c239` + `a7dd7f50d`, base `c3a47e565`. The branch rewrote the five `coord_*` lines to R10-CEILING-PROBE. Main added `config_flow # r10-wood-notify ...`.
  - The head file = main's file (`a7dd7f50d`, = `2b6bef745`) with exactly the five `coord_all_features`, `coord_dhw`, `coord_grid_fee`, `coord_minimal`, `coord_two_zone` lines replaced, each naming both causes (main's R10-COP-GATE p5 (A) cop rows and this branch's `kind`/`held`/`last_attempt` plus the outcome row). `config_flow` is present verbatim.
  - No claim dropped, none added beyond those five names, none widened to a new fixture. `claims-for: 7.1.0` = `VERSION` 7.1.0. No `coord_*` fixture carries a `may-drift` line. `card_claimed_drift.txt` is byte-identical to origin/main.
- `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 2b6bef7453a8...` at the head (`ev/env_drift_all.txt`): `CLAIMED` on the five `coord_*` fixtures (7 leaves moved each), `NO UNCLAIMED DRIFT: 56 scenario(s) checked against 2b6bef7453a8bdaf97d42f382a116ce226b35ccc`, `NO STALE FIXTURE: 56 committed fixture(s) still match what this tree computes`, rc=0.
- VERSION, manifest version, RELEASE_NOTES heading: untouched in the three-dot diff. Delivery row `dev/programme/delivery/3050.md` (one line, **open**) is in the three-dot diff. `tests/structure_budgets.json` moves down only (17653 -> 17649, 8059 -> 8056), and no `*_budgets.json` rises.
- `python3 tests/structure.py` at the head: `STRUCTURE RATCHET PASSED` (`ev/structure_head.txt`). The `summary` argument the brief names is not accepted by this tree's `structure.py` (`unrecognized arguments: summary`), so I ran it bare.
- Gate scope: `tests/closure.py select --diff 2b6bef745` -> `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` This matches the body's figure.
- Mutation proof, my mutants, each run through the block (`features_block.py "# --- R10-CEILING-PROBE (#2498, #2808)"`; baseline `ALL 57 FEATURES BLOCK PASSED`), `ev/out.txt`:
  - `RESULT M0` routing key read from `self._current_action` at the fold: 1 of 57 failed (item 30).
  - `RESULT M1` `experiment_s=None`: 1 of 57 (item 30).
  - `RESULT M2` pending `"mode"` captured as `None`: 1 of 57 (item 30).
  - `RESULT M3` accessor with a 15 % agreement test against 5.0 kW: 1 of 57 (item 29, 4.5 kW).
  - `RESULT M4` `CEILING_MIN_SAMPLES = 11`: 2 of 57.
  - `RESULT M5` median -> mean: 0 of 57, and the whole `tests/features.py` rc=0 (`ev/full.out`). This is a finding above.
  - `RESULT M6` median -> max: 1 of 57 (synthetic pump).
  - `RESULT M7` lapse test dropped: 1 of 57.
  - `RESULT M8` experiment never routed to the store: 6 of 57.
  - `RESULT M9` duty threshold as the `> 0.05` literal instead of `planned_draw_runs`: 1 of 57 (item 32).
  - `RESULT M10` `step_supply`'s system-identification exclusion removed: 0 of 57 in the block, killed by the whole `tests/features.py` (`the step tick writes nothing at a boundary under a system_identification action  [(['turn_off'], True, False)]`). This is item 31 at main's existing check, as the body says.
- Items 29-34 at the head:
  - 29: `learned_max_kw(now_s)` is the raw median with no configured-maximum comparison. Eleven samples give `None`; twelve at 4.5 give 4.5 (pinned, M3 and M4 killed).
  - 30: the `"mode"` key is in the existing `_pending_prediction` dict (`coordinator.py:9852`) and the fold routes on it (`:9756`). No second capture exists.
  - 31: `step_supply` returns `None` under a `system_identification` action (`pump_arbiter.py:1208-1209`).
  - 32: `_planned_duty` calls `planned_draw_runs(experiment)` (`pump_arbiter.py:793`), the same helper as the booking at `coordinator.py:10875`.
  - 33/34: the body's citations spot-checked at the head (`_experiment_kw` 487, `_planned_duty` 773, `step_supply` 1197, `learned_max_kw` 161, the fold 9756, the mode key 9852) resolve.
- Forward-carry (a) s9-ceiling-copgate-iface, on the roster at `cec6621b4` under R10-COP-GATE and cited in the body. At the head: `DrawRange.learned_max_kw(self, now_s: float) -> float | None`; `DrawRange.ceiling_since() -> float | None` (newest sample's epoch); `CEILING_MIN_SAMPLES = 12` and `CEILING_LAPSE_DAYS = 45.0` are module constants in `draw_range.py`; `_run_system_identification` passes `max_power_kw=params.max_electrical_power`. Part D's sites are untouched.
- Forward-carry (b) s9-ceiling-gain-gap: the text is present on the roster at `cec6621b4` under R10-COP-GATE ("The gain between set-point and drawn power at levels between the duty gate and the ceiling is unmeasured ..."). The body's missing citation of it is the second item under Findings.
- The finder's harness as ported (`dev/audit/harnesses/ceiling_probe.py`, sha1 `4c2f42122ea7cf3f3df04aa46eeb4e19b218ac34`, matching the body), run from the same file at both trees (`ev/harness_head.txt`, `ev/harness_base.txt`). The finder's original `probe_duty.py` and `probe_draw.py` are out of tree and were not available to me, so I ran the port.
  - Base: `duty None`; level `35/35/35`; `store: absent`.
  - Head: `duty 'space'`; level `55/38/25`; `store: probe samples 12 | learned top 3.0 | window samples at the ceiling 0 | engaged False`.
  - The draw arm reads `((1.5, None), False, None)` and `((1.5, 3.0), False, None)` at both trees, and the plan-action null reads `'idle'` at both. Every figure matches the body.
- Null controls: the block's flat-price, comfort/price gate, duty-cycling-install, quiet-window, plan-action and late-routing controls all pass at the head (`ev/blk_base.out`). The synthetic 3.0 kW pump behind 5.0 kW is recovered within 2 % (killed by M6).
- Enumeration (step 6): the body names the rule (`git grep` over `"system_identification"`, the plan-power readers, the entry points) and dispositions each seam, including the quiet-window seam outside the note. I found no undispositioned seam in the diff.
- Stress budget check, alternating base (`2b6bef745`) and head, four runs each on this Linux seat, one loop, nothing else heavy running (`ev/stress_alternating.txt`, `ev/stress_runs.log`):
  - All 8 runs: `ok   no scenario exceeds its own recorded cost by the budget factor`, `ALL 113 STRESS CHECKS PASSED`.
  - The global worst-scenario ratio was 124.2-139.1x at the base and 133.0-146.0x at the head, against 268x.
  - On a pass, `stress.py` prints no per-scenario ratio for `summer/1z/space/valve`, so I could not re-derive the body's 4.8x-against-4.6x figure or state that scenario's own spread.
  - The diff touches no solver module (`optimizer.py` and the DHW planner are unchanged; `thermal_model.py` only gains two predicates), and the check never failed in 8 runs. So the macOS 4.8x reading reads as seat load. The pass is robust, not a coin flip.
- Mutation-autofix commit `fba24c239` ("ci: pin killed mutants") is part of the head. Its ledger entries (`tests/mutation_ledger/killed_by/...`) each name a real killing check by its failure count. The CONST pins I sampled match my M4 (`CEILING_MIN_SAMPLES`) and the lapse/overdraw checks. None pins a tautology.
- CI at this head: `merge_train.py classify e310b8bb3...` re-run every ~90 s from 01:49 UTC, last read at 03:24 UTC: `RED e310b8bb31cc8168a9bbc13363a00ad1b7c2ee87 pending: none red: gate` (exit 1).
  - The red is two `gate` runs in check suites 41262247770 (job 124733639993) and 41262247796 (job 124734678917). Each log ends `FAIL run(s) [41262300367] at this head are still being judged; their gate decides`.
  - Suite 41262300367's own `gate` (job 124737196827, 03:22:38) printed `PASS`. `classify` keeps the worst gate per suite (A5), so it reads RED.
  - Every other check at this head concluded success or skipped: tests / fast (3.14), closures, coverage, browser, typing, replay, arch-instrument, the governance jobs, arch-score, budget-raise-gate and hassfest. `tests / mutation` reads `MUTATION TABLE PASSED`, with the 72 added sites `killed by tests/features.py` after the bot's `fba24c239` pins; `mutation-autofix` is skipped.
  - `pr-contract / pr-contract` 124735425356 started 03:21:12, after the last red concluded, and is success: step 11's evidence that the body answers its reds.
- The head was re-read before writing this verdict: `fix/r10-ceiling-probe` is still `e310b8bb31cc8168a9bbc13363a00ad1b7c2ee87`, and the PR body is unchanged since my first read apart from a trailing newline.
