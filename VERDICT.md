Fix review: merge 8b4ce3732544ca9348d8d22dc4f667dbf430cdd6
bus-nonce: eab9beb13e958f4a2c2481f0c95037fa

Round 3. All prior blocking items resolved at 8b4ce3732544ca9348d8d22dc4f667dbf430cdd6:
1. Red checks answered (pr-contract green 113405040438): nightly-ha dispatch reds, both closures UNDER-SCOPED reds, fast, nightly-status, delivery-status each named with a cause and a cheaper-detector answer.
2. Fires half proven: pull_request run at 9b471346 ran nightly-ha on both images, success (jobs 113378056184, 113378056503), with tests/nightly_ha.py in the three-dot diff; not-fires half from round 1 stands.
3. 2212/2214 explained; my mutants count 2214.
RESULT N2/N3/N5 each fail exactly the named entities.py check; null control (main tests.yml) fails reach+coverage, as the body says.
Bot delta 9b471346->8b4ce373 is closures.json only: tests/ha_contract.py added to entities.py's closure plus timings; no custom_components entry (80 = main). Earned: _stage copies that file.
At this head fast, closures, nightly-ha (both), pr-contract are green; nightly-status red is main's, answered. Merges are clean automatic. Evidence: ev3/evidence.md.
