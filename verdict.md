Fix review: merge d2cd24dcdfee19518416e299b8ac3207b92bc8b3

bus-nonce: 702464419d7f8d68ff9f25c8d0adb65d

Delta review of PR #2745 (R10-SAV-COMFORT) from the last merge verdict at 7ae5e30e0df57b522d527945d398ccc547e0389b to head d2cd24dcdfee19518416e299b8ac3207b92bc8b3.

- Delta: six first-parent commits, all merges of origin/main (8174249e, 8d0572dc ci: merge main; 12b3cdee incl. 7c422999; cc679118; resolution merges 1e2d4408 and d2cd24dcdfee19518416e299b8ac3207b92bc8b3). No non-merge branch commit since 7ae5e30e.
- Branch diff unchanged: three-dot diff at merge base 149ce54a3 names the same file set as the diff approved at 7ae5e30e; per-file git patch-id --stable is identical for all five custom_components files (coordinator.py, ledger.py, optimizer.py, payload.py, pump_arbiter.py); sorted +/- line sets identical for every file except tests/structure_budgets.json, where the same -3 class_excess_loc payment is re-based onto main's value (18080 -> 18077, was 18103 -> 18100). Production behaviour is byte-identical to what was approved, so the finder's harness was not re-run; the gate covers interaction with main.
- tests/golden/claimed_drift.txt: 41 R10-SAV-COMFORT claim lines and the 15 may-drift suspensions removed (same set as approved); main's 5 coord_* R10-CARD-VOICE claims kept; no fixture listed twice; claims-for 7.0.4 = VERSION 7.0.4. env_drift.py: NO UNCLAIMED DRIFT (5 scenarios), NO STALE FIXTURE. card_claimed_drift.txt identical to origin/main (0-line diff).
- structure.py: STRUCTURE RATCHET PASSED.
- git merge-tree --write-tree origin/main HEAD: clean against current main f46bb2728641cba0434ea4abc38acdc1062fce97 (main moved past 149ce54a3 by 9 files, none a claim file or under custom_components).
- Body ## Head names d2cd24dcdfee19518416e299b8ac3207b92bc8b3, matching the PR head.
- CI at head (run 40351970673): gate pass; tests / fast (3.14), closures, mutation, coverage, browser, typing, replay pass; autofix jobs skipped; no red check, so no root-cause trigger.
- Carries: none.
