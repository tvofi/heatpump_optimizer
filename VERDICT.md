Fix review: merge 3f34385f2bf66653180d210080e11b6d892cfe02

bus-nonce: 1322fc80d6f3ddc013c9d22f602f5986
pending-ci: gate

Round 1 (first review, scope full). Measurement PR: a new harness `dev/audit/harnesses/r11_advisor_measures.py`, one card-doc paragraph, a closures entry and a delivery row; no production line.

Note: figure: the body's `## Figures` says of the `loop` arm "Every other ask's truth is smaller than the null", and item 1 says both hot-water setpoint directions sit inside the loop's null. At this head `dhw_setpoint 55 to 50` reads +23.9 against the null's -23.1 (|23.9| > |23.1|, by 0.8). The margin is inside any plausible spread of a single-sample null, and the card's existing hot-water sentence ("can read as a saving at one hour and a cost at another") stands either way, so no code, test or doc text changes. The body's sentence is wrong as written.

## Evidence

- Head: the PR head is 3f34385f2bf66653180d210080e11b6d892cfe02, which the body names and which I measured (ev/HEAD.txt). Merge base e352724335c136b65562cd3e71f728549ad04a82.
- Merge: `git merge-tree --write-tree origin/main <head>` rc=0. The ledger driver resolved tests/closures.json (inert_reads merged as a set). See ev/merge-tree.txt.
- Step 5: VERSION, the manifest, the RELEASE_NOTES heading, tests/golden and both claim files are untouched in the three-dot diff (ev/untouched.txt).
- Step 4 (claims): no production or fixture change, so there is no drift to claim. I did not run env_drift --all; the gate covers it.
- Step 1 (mutation): n/a. The diff writes no production line, and the only .py file is a harness under dev/audit/harnesses/. CI's `tests / mutation` is green at the head. The doc text is pinned by the harness rows it describes, and those rows move with their own perturbation: the no-tank column and the hour axis both scatter, and the half-degree null reads 0 against.
- Step 2 and 8: I re-ran every figure in the body at the head. No production file changed, so base and head are the same code under test. The harness is the fixer's, built for this item; the finding (#3481 items 128b800e, c33b6f10) had no committed harness, which this PR supplies. Disclosed as the builder's, per step 9.
  - `asks` (ev/arm-asks.txt): rows against, out of 18 each:
    - weight 5→2.5: 6
    - weight 5→10: 5
    - floor 17→16: 8
    - floor 17→18: 3
    - hot-water minimum 45→50: 0 (range +58.0..+102.0)
    - half-degree null range: -11.2..+7.1
    
    All match the body. The no-tank column scatters with the hour as claimed: weight 5→2.5 reads -41.0 at 05:00 and +1.1 at 13:00.
  - `loop` (ev/arm-loop.txt): hot-water minimum +99.8 and null -23.1 match. The other asks read 55→50 +23.9, 55→60 -0.8, weight -17.3 and +7.9, floor +3.8 and +10.9. See the Note above for 55→50.
  - `valve` (ev/arm-valve.txt):
    - asks moving with the weekday: 0
    - days leaving the schedule branch: 0
    - wkday+1: -0.9 on all 7 days
    - held rooms at 23.0: 22.10 and 22.07
    - null: 0 against
    
    All match the body.
  - `pv`, `pvloop` (ev/arm-pv.txt, ev/arm-pvloop.txt):
    - pv day-1: truth -25.2, ends -63.2 and -8.0
    - null day-1: truth -24.9, ends -63.2 and -26.8
    
    Both match the body. The own-price end is the closer one in all four pvloop rows. PV day+1's truth is -10.5, inside the null's 23.1. The thermostat at surplus-aware prices is outside the range in every `pv` row. The card's existing sentences stand.
  - I did not re-run the R10 instrument's re-measured arms (`r10_advisor_steady_seams.py pair fields weekday pv`). The `valve`/`asks` arms cover the same seams at this head, and the body draws no figure from them.
- Step 6 (class): the item text (#3481 128b800e, wave-r10-groups.json) enumerates its own seams: the "hot-water, weight or floor ask alone". The doc's pair sentence names the same three ("hot water alone, the comfort weight, the lowest allowed temperature"). PAIR_ASKS covers all of them: dhw_setpoint, dhw_min_temperature, comfort_weight and min_temp. Running the wider rule "every override the card's what-if can send that takes the pair branch" returns more: dhw_windows, quiet_silent_windows/quiet_off_windows, silent_mode_power_fraction and wood_slots, each sent alone (heatpump-optimizer-card.js `overrides()`). These are outside the item's own enumeration, so this is not class-open on this PR. It is carried under Findings.
- Step 10 (forward-carry): the body's "Open for the orchestrator" item (the pair's hour scatter needs a design choice) is routed by the body to no group. It is a pending orchestrator ruling, not a carry this PR owes.
- Step 16: no actuator path touched.
- CI: `merge_train.py classify 3f34385f2bf66653180d210080e11b6d892cfe02 --pr 3674` read rc=3 on every run from 17:16 to 17:46Z: `WAIT 3f34385f2bf66653180d210080e11b6d892cfe02 pending: gate red: none` (ev/classify.txt). In the live check runs, the gate of the main CI suite (run 43908978930) is green at 17:39:59Z, and pr-contract, closures, coverage, coverage-ratchet, fast, typing, mutation and browser are all green. The gate runs of the two refresh suites (43913533208 at 17:10Z and 43908978908 at 16:49Z) read failure. classify keeps the worst gate per suite and reads it as pending while busy, so its WAIT stands, hence the `pending-ci` line. `tests / nightly-status` is red but is not in `owed-reds`, so it owes no answer.

## Findings

- Follow-up: the steady pair's hour scatter is measured only for the asks the item named. A hot-water window, quiet-hours or wood-slot change sent alone also takes the pair branch (`whatif.schedule_days` returns None, since no comfort target moves), and its figure is equally one day's, priced from the hour asked. Nothing measures it for the same scatter, and the new card sentence names only the weight and the floor. Control: the `asks` arm with those overrides added to PAIR_ASKS; precondition: the card's `overrides()` still sends them alone. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
