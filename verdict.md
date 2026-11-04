Fix review: blocked 913e74e876606ecf573b387b613f5a4e621b9bc7 mutation-vacuous: freq_control.py:228 GUARD_OFF in FrequencyMap.evidence_exhausted survives every suite check, including the one the body names as its killer

bus-nonce: 7da3c0d117bb05e90f8d800b28973976

## Block

`custom_components/heatpump_optimizer/freq_control.py:228 GUARD_OFF`, the new `planned_draw_runs` gate in `FrequencyMap.evidence_exhausted`, survives the suite. CI's `tests / mutation-pins (2)` (job 126469727880) printed `UNPINNED custom_components/heatpump_optimizer/freq_control.py:228 GUARD_OFF -- lives` and `PIN KILLED: 3 pinned, 1 left unpinned (1 survived ...)`. The bot's pin commit c34999c1d pins the other seven sites and not this one. This review reproduced the cause: with the gate replaced by `if False:` (`ev/mutant_m6_evidence_exhausted_guard_off.txt`), the features check the body names as its killer still passes. That check, "a target the plan calls off asks the map for nothing (D8-s1-01)", builds `_fm` from buckets at 2.0-6.0 kW (`tests/features.py:24969-24987`). So `evidence_exhausted(0.07, ...)` reads False with or without the gate: `all(bucket below 0.07 kW)` is already False. Its `not _fm.evidence_exhausted(0.07, ...)` arm therefore pins nothing. The only instrument that kills this mutant is the out-of-suite probe (`r10_run_owner_probes.py`, probe 4, a map whose one bucket sits at 0.06 kW): under the mutant it prints `FAIL freq_control.FrequencyMap.evidence_exhausted: exhausted=True owner_runs=False`, `RESULT probes_failed=1`. The body's `## Unpinned sites` claim that this site is killed by the same check is wrong.

Repair: give the suite a check whose map has evidence below the off-step target, for example the probe's single 0.06 kW bucket: `evidence_exhausted(0.07)` must read False, and its null, `evidence_exhausted(0.11)` on the same map, must read True. Then re-run the pin.

CI at the verdicted head: `merge_train.py classify 913e74e8… --pr 3184` printed `RED 913e74e876606ecf573b387b613f5a4e621b9bc7 pending: none red: gate` (rc=1, 09:59:22Z). The head has since moved to c34999c1dd512e45fea3027bc49da31a78050d8a (`ci: pin killed mutants`, github-actions[bot]); `review_carry.py 913e74e8… c34999c1…` prints CARRY. This block applies equally at c34999c1, which leaves the survivor unpinned.

## Round

Round 1: the first review of #3184. No earlier verdict exists. The brief's "delta from your verdict at" names no SHA, so this is a full review at the head, not a delta.

## Summary

Measured at head 913e74e876606ecf573b387b613f5a4e621b9bc7, merge base c3a279e3252a8b57bb00b5a677318cd4fe20387f, from detached worktrees at both. Every quantified claim in the body re-derives. The five seams the body mutates are each killed in isolation by the check it names. Class enumeration matches the diff. The merge with current origin/main (fad43b047) is clean. Everything else in the review holds. The block is one surviving mutant on the new evidence_exhausted gate (`## Block`).

## Findings

- Follow-up: the pre-heat table's counting companion (the script that counts `space_reasons.count('preheat_weather')` per arm) stayed in the fixer's scratch, against fixer.md step 18. The probe itself is in tree at `7c4e639e4:BODY.md` (sha1 9978dbb2…, which matches). This reviewer re-derived every cell of the table with a counter of its own (`ev/reviewer_preheat_companion.py`), so the figure is verified, but under the reviewer's definition, not the fixer's. Carry: dismissed: the probe is pinned by sha in tree, a counter is one `count()` call over its result, and this review's counter sits in ev/ as a reviewer's driver (fixer.md 18).

## Evidence

Step 1, mutation proof for the five seams the body names, one mutant per seam (body: one combined mutant; this review ran each in isolation, `ev/mutant_m*.txt`). `PYTHONPATH=tests/hastub python3 tests/features.py`:
- head unmutated: ALL 4785 FEATURE CHECKS PASSED, rc=0.
- m1, the two `_heating_draws` lines removed (`classify_dhw_steps` reads `ctx.other` raw): 1 of 4785 FAILED, "a step the plan runs no pump at is idle to the reason classifiers (D8-s1-01)".
- m2, `calm_loss = base_loss`: 2 of 4785 FAILED, the flat-forecast scale-1.24 check and the wind-spell check.
- m3, both `freq_control` gates back to `target_kw <= 0.05`: 1 of 4785 FAILED, "a target the plan calls off asks the map for nothing (D8-s1-01)".
- m4, the buffer learner's `heating` back to `> 0.05`: 1 of 4785 FAILED, "the buffer learner reads heating from the plan's running rule".
- m5, the watchdog's `watch_active` back to `> 0.05`: 2 of 4785 FAILED, "the watchdog's two bounds" and "a step the plan calls off is not watched".
The per-seam attribution in the body's `## Mutation proof` holds exactly. Its combined mutant did not include the evidence_exhausted gate in isolation, and that one site is the survivor (`## Block`).

Step 2, P2 seams, harness `dev/audit/harnesses/r10_run_owner_probes.py`. It is the fixer's rebuild of the finder's `probes_p2.py`, disclosed in the body and committed here. Run from the head's copy against both trees (`ev/probes_*.txt`):
- RESULT probes_failed=6 count (base)
- RESULT probes_failed=0 count (base --perturb, the null arm)
- RESULT probes_failed=0 count (head)

Step 2, pre-heat label, the finder's inline probe from `7c4e639e4:BODY.md` (sha1 9978dbb2f60eaaaf6da48e591ba739901be94d9b, matches the body). Counted with this reviewer's own companion (`ev/preheat_counts_*.txt`):
- arm 1: base 88 of 96, head 0
- arm 7b: base 88, head 0
- arm s1: base 74, head 0
- arm s3: base 88, head 0
- arm 4 (null): base 0, head 0
This matches the body's table cell for cell. The probe's kWh rows move by at most a few tenths at head (arm 3: 13.21 to 12.99 kWh). That is consistent with the classifier change feeding the warm start; nothing regressed on the zero-learned-scale arms (3b, 4, 4b, 5, 5b identical).

Step 3, null controls. The `--perturb` arm reads 0 at base (above). The features nulls (0.11 kW still recommended, 0.5 kW still heating, 2.0 kW watched, scale 1.0 flat forecast no preheat) passed at head and are part of the 4785.

Step 4, claims. The diff adds one SHAPE claim, `space_reasons[*]|dhw_reasons[*] * -> 'idle_coasting'|'idle'`, plus header text. `card_claimed_drift.txt` is untouched, and `claims-for: 7.1.1` equals VERSION. This review did not re-run `env_drift.py --all` or `r10_shape_claim_controls.sh`, which take minutes and are not cheap checks. The claim's both-ways check is CI's: `tests / fast (3.14)` is green at this head. The body's `after_rc=0 narrow_rc=1 null_rc=1` and `4 UNCLAIMED DRIFT(S)` are not re-derived here.

Step 5. VERSION, manifest.json and RELEASE_NOTES.md are untouched (three-dot diff empty).

Step 6, class. `enumerate_p2.py` reads `RESULT F1_run_threshold=13 count` at base and `=9` at head. The four seams that left are exactly the four in the diff (`_async_learn_buffer_cooling`, `_observe_frequency`, `FrequencyMap.recommend`, `FrequencyMap.evidence_exhausted`). Every remaining nine is dispositioned in the body. One wording slip in the body: it says the P2 matcher "does not return" `_capacity_caps` / `_fold_capacity_envelope`, but `enumerate_p2.py` does list both under F1, at base and at head. The body's disposition of them (a capacity bound on p_max, not a running rule) stands on reading them (`p_max <= 0.1`). The other configurations the probe accepts (two-zone and single-zone arms, outdoor 3/9 °C, flat price) all read 0 preheat at head.

Step 7. The body's `## Head` names 913e74e876606ecf573b387b613f5a4e621b9bc7, the head measured here.

Step 13. `git merge-tree --write-tree origin/main 913e74e8…` against origin/main fad43b047 exits 0. The ledger driver printed `LEDGER-MERGE: resolved tests/closures.json` and no `MERGE-CLAIM: refused` (`ev/merge-tree.txt`).

Step 14, structure. `python3 tests/structure.py` at head: STRUCTURE RATCHET PASSED, `class_excess_loc=17633`, against the budget's recorded 17640 at base. The -7 is `_weather_loss_factors` leaving `HeatPumpOptimizer.optimize` as a module function with its own pinned floors. Putting it back inside the method returns the 7 lines, so the movement is earned by a real extraction, not by re-spelling. `tests/entities.py`'s four removed "distinct finding" dispositions are for the four sites this diff fixes. The two classifier dispositions now describe the owner reading.

Step 15. `freq_control` reading `thermal_model` would close an import cycle, which the diff breaks by moving the two FREQ_MODE strings into const with an explicit re-export. Each seam now asks the owner `planned_draw_runs`; no copy of the threshold is added. No HA import is added to a model module. The body names the alternatives and why each lost.

Step 11, red checks at this head (live read, `get_check_runs`, 46 runs):
- `tests / mutation`: red, MUTATION TABLE REFUSED on the 8 added unpinned sites the body lists under `## Unpinned sites`. The body answers it as mutation-autofix's lane (ci-autofix.md), so the trigger was answered. The lane's outcome was 7 pinned and 1 survivor, which is the `## Block`.
- `tests / replay`: red, `synthetic-dhw-only.json: cycle_cost [cpu_ratio 2.825 over its budget 2.173]`, confirmed from the job log. The body answers it as timing noise. This review measured the fixture alone on a loaded host, at both ends: base `cpu_ratio 2.553` and head `2.455`, both FAIL over 2.173 (`ev/replay_dhwonly_*.log`). The base fails the same way, so the red is the runner's, not the diff's. The body's local "ALL 176 replay checks PASSED" is not re-derived here, because this host was loaded.
- `tests / nightly-status`: red, main's nightly lane. The diff does not reach nightly.yml.
- The local reds typing_ruler, stress and harness_headers at b03b76d5d are each named and answered in `## Red checks`.

Steps 9 and 10. The P2 harness is committed (above). The pre-heat probe is in tree on a body ref. Its counter is not, which is the one item under `## Findings`. The body's `## Forward-carry` is none. No finding here changes a later stage.

CI wait: `merge_train.py classify` was polled from 09:37Z, WAIT (rc 3) until mutation-pins (2) concluded, then RED (rc 1) at 09:59:22Z (`ev/classify.txt`). The review is round 1, so `fixer.md` owes a repair, not a re-cut.

## Friction

- The frugal routing hook refused a plain background wait loop and a Monitor as "inline search op 6/7". The wait was routed through a read-only scout instead. It was not worked around.

Self-audit: `carry_audit.py check` was run on this verdict with an empty `--body` and printed `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`, rc 0. The PR body itself was audited by the review packet at this head: `CARRY-AUDIT: 0 finding item(s)`.
