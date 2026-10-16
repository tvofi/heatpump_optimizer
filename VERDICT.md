Fix review: blocked a0c4431df91e75b3c7ed4976586c0da86e292214 harness: `sweep_n_no_expiry.py --perturb` -- the class's own documented perturbation arm -- no longer runs at this head, and the body does not say so

bus-nonce: d452d47f143d63d5746d0454cb2e5fa0
head-measured: a0c4431df91e75b3c7ed4976586c0da86e292214 (re-read at post time: `refs/pull/2336/head` and `refs/heads/fix/r10-feeds` both still this sha)
round: 1 (first review round for #2336)
contract check: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so this review ran against the current `fix-review.md`

## The block

`dev/audit/rounds/round10/D14/sweep_n_no_expiry.py --perturb` is one of the eight perturbation arms in this class's instruments. Measured at both ends, all eight run at the merge base and exactly one is dead at the head:

| perturb arm | base `8f174c4ce` | head `a0c4431df` |
|---|---|---|
| `D14/sweep_n_no_expiry.py --perturb` | `rc=0 RESULT seams=1 unbounded=1` | **`rc=1 AssertionError: perturbation anchor missing`** |
| `D14/sweep-N-silent-zero/enumerate.py --perturb` | `rc=0 unguarded=3` | `rc=0 unguarded=2` |
| `D14/sweep-P1/p1_ts_seams.py --perturb` | `rc=0 seams_flagged=1` | `rc=0 seams_flagged=1` |
| `D14/log_flood/enumerate.py --perturb` | `rc=0` | `rc=0` |
| `D14/log_flood/probe.py --perturb` | `rc=0` | `rc=0` |
| `D14/sweep-P1/probe_spot_head.py --perturb` | `rc=0` | `rc=0` |
| `D14/sweep-N-silent-zero/weather_probe.py --perturb` | `rc=0` | `rc=0` |
| `D1/s3/tibber_ingress.py --perturb` | `rc=0` | `rc=0` |

The mechanism is `sweep_n_no_expiry.py:69`, which anchors on a source string this diff deletes:

    cut = body.replace("            if step_start >= end:\n                break\n", "", 1)
    assert cut != body, "perturbation anchor missing"

`grep -n "step_start >= end" custom_components/heatpump_optimizer/coordinator.py` returns `6726` at the merge base and nothing at the head: the end rule moved into `_covering_index`, and `_known_prices_for` now calls the helper. So the arm the sweep documents as the class's own perturbation —

    dev/audit/rounds/round10/sweep-N-no-expiry.md:20
    | perturbation | `--perturb` (drop `if step_start >= end: break` from `_known_prices_for`, one line) | unbounded 0 -> 1 |

— and that `dev/audit/rca/R10-N-no-expiry.md:33` reproduces ("Dropping the one end-bound line from `_known_prices_for` gives 1") no longer runs on this tree. The other seven arms are unaffected, so this is this diff's doing and not a general rot in the arm family.

`fixer.md` step 3 owes *"say so"* when a harness's behaviour at the head stops matching its baseline; the body is silent on this arm, and it is the one fact of that shape the body omits — it records the log arm's translated non-vacuity number in a paragraph of its own, and the `## Null control` section lists four harnesses, none of them the enumerators whose `--perturb`/`--null` arms exist. `fix-review.md` step 2 is the check that caught it: "run the companion yourself at both ends."

This is deliberately **not** a claim that the class is open or the barrier vacuous — both are sound, and section "Everything else verified" below says so with the numbers. It is that an instrument this class's own sweep and RCA document as runnable is not, at the head, and the body does not record it.

### What clears it (either is enough; the first is body-only and moves no head)

1. **Say so in the body**, in the same place the log arm's translated number is recorded: the enumerator's `--perturb` anchors on `_known_prices_for`'s deleted end line, it no longer runs at this head, and the perturbation now lives in `_covering_index`'s `return i if now < starts[i] + span else None` — which this review drove (mutant M1 below) and which the finder's own harnesses read 0 -> 4 and 0 -> 2. A carry to the destination the next sweep seat reads, per `finding-propagation.md`, keeps the sweep table from being re-derived next round.
2. **Re-anchor the arm** to the new location. That file is outside `R10-FEEDS`' architect-note file scope ("Touch only the owning seam named here"), so it is the orchestrator's call whether to grant the edge or hand it to the D14 sweep's owner; the reviewer did not assume either.

## Everything else verified (nothing else blocks)

Finder harnesses, finder's copies, byte-identical at the base, the head and the cited `d23205d13` (`git hash-object` on each: `5471a61a4342 stale_price.py`, `f05a0870d46c tibber_ingress.py`, `52fca455b98b weather_warn.py`, `404a33eede41 probe_n_no_expiry.py`, `3d751c49d77d weather_probe.py`, `0c5f7cffb467 probe_spot_head.py`, `74a7578dc969 log_flood/probe.py`, `6cd8af3def97 sweep_n_no_expiry.py`, `6f71fb362e25 sweep-N-silent-zero/enumerate.py`, `6ccd4146a877 p1_ts_seams.py`, `91876ad0b513 log_flood/enumerate.py`), run from each tree at its own path. Reviewer's RESULT lines, base -> head:

    stale_price.py            uncovered_current_price_published 4 -> 0, uncovered_price_booked 4 -> 0, uncovered_cycles=4, control_covered_published 2 -> 2
    tibber_ingress.py         empty_ok_wipes 1 -> 0, startless_rows 96 -> 0, misplaced_steps 95 -> 0
    weather_warn.py           no_entity.warnings_4_cycles 4 -> 1, empty_forecast.warnings_4_cycles 4 -> 1, control_48_rows 0 -> 0
    probe_n_no_expiry.py      probe_failures 2 -> 0; CONTROL covered forecast=-2.0 plan=49.5 at both ends; forecast_outdoor_now 0.0 -> None, _open_loop_plan_value 44.5 -> None
    weather_probe.py          empty_ok_wipes 1 -> 0
    probe_spot_head.py        spot_wrong 1 -> 0
    log_flood/probe.py        all 7 arms 1,1,1,2,2,1,1 -> 0; control.floods 0 -> 0

Every figure in the body's `## Figures` section re-derives at the numbers it states.

Null control and both-ends, re-run: `control_covered_published` 2 at both ends (the body's owed null control, and the brief's), `CONTROL covered forecast=-2.0 plan=49.5` identical at both ends, `weather_warn` control 0 at both ends, `log_flood` `control.floods=0` at both ends. Every arm of the new `tests/features.py` block pairs its defect input with a covered/healthy input, verified by running the block: `R10-FEEDS BLOCK: 16 ok, 0 failed` at the head. The whole file at the head, run here: `ALL 4151 FEATURE CHECKS PASSED`, rc=0, 632 s.

Mutation proof, re-run (step 1). The fixer's driver `fixwave/R10-FEEDS/mutate.py` is out of tree and was not available, so this seat built its own and says so (step 9): it extracts the 16-check block verbatim from `tests/features.py` with that file's import header and runs it against a throwaway worktree at the head. All twelve named mutants are killed, each by the checks the body names:

    M1  _covering_index end bound -> `return i`        13 ok 3 FAIL  (covering arm, stale price list, forecast/plan siblings)
    M2  `return prices or "..."` -> `return prices`    14 ok 2 FAIL  (Tibber body arm, HTTP-200-empty fetch)
    M3  _raw_start validation removed                  14 ok 2 FAIL  (Tibber body arm, one start rule for both paths)
    M4  _log_held `held.get(key) == text` -> False     14 ok 2 FAIL  (latch transitions, four-cycle flood)
    M5  weather `if forecast_data:` -> `if True:`      15 ok 1 FAIL  (all-implausible forecast arm)
    M6  settlement `if known_price is not None:` -> True  15 ok 1 FAIL  (unpriced interval books no cost)
    M7  override `spot is not None and` dropped        TypeError     (body: killed (TypeError))
    M8  sysid `if price is None:` -> `if False:`       TypeError     (body: killed (TypeError))
    M9  accuracy `if price is not None` -> `(price or 0.0) ... if True`  15 ok 1 FAIL  (accuracy sample records no cost)
    M10 `lru_cache` dropped from _peak_tariff_months   15 ok 1 FAIL  (four-cycle flood)
    M11 forecast_outdoor_now past the end -> last      15 ok 1 FAIL  (forecast/plan-seed siblings)
    M12 score day `if spot_known and isfinite(sek)` -> True  15 ok 1 FAIL  (score day takes no unpriced kWh)

M1 also drives the finder's harnesses, which is the independent form: `stale_price.py` 0 -> 4 published and 0 -> 4 booked, `probe_n_no_expiry.py` 0 -> 2 failures. The block's M0 (no mutation) is clean at 16 ok.

Class closure (step 6). The four enumeration rules the body names were run at the head and their returned seams compared with the diff and the dispositions. Their output reproduces the body exactly: `sweep_n_no_expiry.py` seams 9 -> 6 / unbounded 6 -> 4; `sweep-N-silent-zero/enumerate.py` unguarded 2 -> 1; `p1_ts_seams.py` seams_flagged 6 -> 3; `log_flood/enumerate.py` base `sites=85 latched=6 seams=79` -> head `sites=80 latched=6 seams=74`. No seam any rule returns is undispositioned; the package is flat (77 modules, no subdirectory `.py`), so each arm's `glob("*.py")` reads the same population as its enumerator's `rglob`.

The two barriers are real, and their allow-lists are the enumerators' own output rather than a list written to fit: parsing `tests/entities.py`'s literals and importing each enumerator gives N-no-expiry 6 keys / 6 sites on both sides, zero set difference and zero count difference, and N-log-flood 63 keys / 74 sites on both sides, zero set difference and zero count difference. Both arms are **red on the defect tree and green on the fixed one** (the RCA's own requirement): run from a base worktree, the head's arm block reports 2 failures, the no-expiry one naming `_current_spot_price`, `_open_loop_plan_value`, `forecast_outdoor_now`, `_known_prices_for` and the missing `_covering_index`, and the log one naming the eight sites in the seven probed functions (`_weather_series`, `_fetch_solar_forecast`, `_solar_location`, `_price_series` x2, `_tariff_months`, `_tariff_hours`, `async_run_optimization`). Both arms' planted controls discriminate rather than merely pass: a new unbounded lookup and a second site inside an allow-listed function are each refused; an unlatched warning and a second site in a listed function are each refused, and a latched one is not a site. `tests/entities.py` at the head: `ALL 2331 ENTITY CHECKS PASSED`.

Every class enumerator's own `--null` arm runs: `sweep_n_no_expiry.py --null` gives `unbounded=0`, `sweep-N-silent-zero/enumerate.py --null` gives `unguarded=0`. The `log_flood/enumerate.py --perturb` arm reads flat at both ends (85/6/79 and 80/6/74, same as unperturbed) — that is pre-existing at the merge base, not this diff's, and is not part of the block.

Quoted numbers, re-derived (step 8):

    tests/mutation_table.py inventory() candidate sites                 6133   (body: 6133)
    unpinned_sites(load_budgets(), inventory())                          4368   (body: 4368)
    completeness_problems(load_budgets_at(merge base), inventory())         7   (body: seven)
    completeness_problems(load_budgets(), inventory())                      0   (body: 0)
    `grep -rnoE "^[A-Za-z_]+ = logging.getLogger\([^)]*\)" ...`             39   (body: 39, all `_LOGGER`)
    `grep -rnE "_LOGGER\.(warning|error)\(" ... | wc -l`  base 85 / head 80      (body: 85 / 80)
    `grep -rnE "\.(warning|error)\(" ... | grep -v _LOGGER`  head 0             (body: 0)
    `grep -rn searchsorted ...`                                              2   (body: 2, optimizer.py:1130/1131)
    `grep -rn bisect_left ...`                                               0   (body: 0)

The seven removed ledger pins are exactly the base ledger's completeness problems against the head's deterministic inventory: `_current_spot_price` GUARD_OFF `280ab798` and `62fa25e3`, `_current_spot_price` RETURN_DEL `74ecf314`, `_fold_score_sample` CLAMP_DROP `d537da65`, `_known_prices_for` GUARD_OFF `62fa25e3`, `_known_prices_for` RETURN_DEL `33997920`, `prices_from_tibber_payload` GUARD_OFF `5b089cda`. The four `survivor_triage` rows are argued records, not pins; two of their equivalence claims were spot-checked and hold: `_covering_index(starts, starts[0], 1h)` is `0` (so `now <` and `now <=` select the same index) and `parse_windows("")` is `[]` (so the tariff guard's removal returns the same `()`).

One quoted number disagrees with a second source, and it is not the body that is wrong. The head's own mutation-lane artifact prints `4368 unpinned site(s) of 6134 candidate sites` where the body and this review both derive **6133**. The body's figure is the one `inventory()` gives in this tree; the one-site difference is in the lane's printed total at the same sha and is out of this PR's diff.

Instruments and budgets (step 14). `tests/structure.py`: `STRUCTURE RATCHET PASSED`, `max_class_loc 8635 <= 8635` — the budget moved **down** (8688 -> 8635), re-recorded, not raised; `seam_cut_total 752 <= 752` and `coordinator_attrs 151` unchanged. `tools/audit/archscore/score.py --diff 8f174c4ce`: `dS +0.0158 IMPROVES`, `coord_footprint 2575 -> 2547`. The mechanisms the body names for that fall are the ones in the diff: the tariff parsers left the class, `_current_spot_price` reuses `_known_prices_for`, and the two positional fallbacks are deleted; nothing here is a mechanical split or a triage on a killable mutant, and `budget-raise-gate` ran green at this head.

Claims and versions (steps 4, 5). The roster marks this group `fixture: false`, and it is: both claim files are byte-identical to the merge base, `env_drift.py --claims-only 8f174c4ce` prints `claims hygiene: 8f174c4ce... ok`, and `env_drift.py --all 8f174c4ce` (the CI form, run to completion here) prints `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56 committed fixture(s)`, rc=0. No card change, so `card_drift.mjs` is not in scope. `VERSION` (7.0.0), the manifest version (7.0.0) and the `RELEASE_NOTES.md` heading are untouched, three-dot.

Red checks, read from the API rather than the body (step 11). In the branch: `mutation` red at `8921b4825` and twice at `fba6de8de`; `pr-contract` red at `8921b4825` and once at this head (`17:17:33Z`, "`## Head` does not name a0c4431…"). The body names and answers both. The head's own `pr-contract` runs green at `17:51:32Z`, started after the red one concluded at `17:17:54Z`, and the body's `updatedAt` is `17:51:24Z` — so the green run checked the body as it stands. The green `mutation` at this head is **not** vacuous: the lane's artifact shows `7 mutant(s) over 4 file(s)`, `baseline tests/features.py: rc=0 failed=0`, `baseline tests/entities.py: rc=0 failed=0`, the `NULL_COMMENT` null control surviving every driver in play, `PIN RE-VERIFICATION: 7 reproduced, 0 not reproduced`, `0 survivor(s) of 7 evaluated`, `MUTATION TABLE PASSED`. `CONTESTED`/`INCONCLUSIVE` does not appear.

Forward-carry (step 10). The destination the body names is `R10-BRIEFS-FOLD`, and it carries the item: `dev/programme/rosters/wave-r10-groups.json`'s `R10-BRIEFS-FOLD.brief` reads "Owed edits: D1 step 3 checks the published and booked value, not only the plan", and `R10-FEEDS.carry` says the same edit is "Owed for the D1 dimension, not for you". `R10-BRIEFS-FOLD.resume.stage` is `not-started`, so it is pending rather than landed, which is what the group's brief expects of this PR. Both RCAs' countermeasures are built **here**, not deferred, as `R10-FEEDS.carry` requires: `coordinator._covering_index` and `coordinator._log_held` in production, and the two AST arms in `tests/entities.py`.

Conflict (step 13). `git merge-tree --write-tree origin/main a0c4431df` exits 0 with no conflicting paths and no driver verdict lines, so `mergeStateStatus: BLOCKED` is the required-review gate and not a conflict.

Architecture (step 15). Judged on added lines against `fixer.md` step 17 and the group's architect note: the two helpers are module-level and side-effect-free apart from the log call; `_log_held`'s state is a `WeakKeyDictionary` side table, so `coordinator_attrs` does not move; the latch logs through the coordinator's own `_LOGGER`; the tariff parsers became pure and `lru_cache`d rather than reading `entry.options` below the glue; `payload.py` and `sysid.py` widened two annotations and added one refusal. The hunks outside the named seam (`_accumulate_energy`, `_record_accuracy`'s cost lines, `_fold_score_sample`, `record_setpoint_override`, `async_run_optimization`'s one log line, `_tariff_months`/`_tariff_hours`, `sysid.conditions_met`, `payload.py`) are each listed in the body as orchestrator-approved, which is what the note requires of a hunk outside the owning seam.

Head (steps 7, 12). The body's `## Head` names `a0c4431df91e75b3c7ed4976586c0da86e292214`, which is the sha measured here, and `refs/pull/2336/head` still answered that sha when this verdict was written.
