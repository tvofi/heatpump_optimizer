Fix review: merge 0906472bc8256f4785977180d8ff5f6cf8a786ac

bus-nonce: abab0c2a00d78dee64340cdea911e158

## Review scope
Delta 5825777c..0906472bc8256f4785977180d8ff5f6cf8a786ac (four merges of origin/main and their resolution); the previous verdict, merge at 5825777c, recorded no findings this delta could reopen. The delta changes no production line, so the scope stays as it was.

## Evidence
- RESULT production unchanged: the PR's own diff (merge-base..head) covers the same 57 files at both heads. Every custom_components/ file carries byte-identical +/- lines at 5825777c and 0906472bc8256f4785977180d8ff5f6cf8a786ac. The only files whose own lines moved are docs/architecture.md, tests/deployment_shape.py, tests/structure_budgets.json and dev/audit/rounds/round4/D6/claims.{py,json,md}, and each of those is a count.
- RESULT the head is the clean merge plus one resolution: git merge-tree --write-tree 2c68c024 dbdc520e (the branch and main sides of the last merge) differs from 0906472bc8256f4785977180d8ff5f6cf8a786ac only in tests/deployment_shape.py. closures.json and structure_budgets.json are the ledger driver's set union and sum of deltas (class_excess_loc 17228, module_excess_loc 21753).
- RESULT module count: 104 .py modules on disk at head. 36 import homeassistant at module level and inputs touches it inside a function, so 104-36-1=67 are HA-free. docs/architecture.md states 104/36/67, the union of main's flow_limit.py (103/66) and the branch's comfort_floor.py. claims.py prints arch_modules_on_disk=104.
- RESULT mutation: docs/architecture.md:309 67->66 makes tests/doc_claims.py FAIL ("modules_free_of_homeassistant: documented=66 measured=67"). Restored, it passes with ALL 443 checks PASSED.
- RESULT selection-cost note: re-derived as the Jaccard overlap of production closures in tests/closures.json at >=0.80 (ev/pairs.py, ev/pairs.txt). Results: 184 of 561 at head (34 scripts, 435 comparable pairs, 4 empty: arch_score.py, ha_contract.py, layout.py, md_tables.mjs); 186 on the branch at 2c68c024; 182 on main at dbdc520e; 184 on main at 658fcae3 before #3841. Every figure the note states matches, and the note keeps both sides' history clauses (union).
- RESULT git merge-tree --write-tree origin/main 0906472bc8256f4785977180d8ff5f6cf8a786ac: exit 0, no conflict.
- RESULT CI: merge_train.py classify -> "GREEN 0906472bc8256f4785977180d8ff5f6cf8a786ac pending: none red: none".

## Notes
- Merge order: #3863 and #3835 also claim the HA-free module count 67 (and the on-disk totals that go with it). Whichever of them merges after this PR has to re-derive the count to 68 or beyond in its own resolution. tests/doc_claims.py catches a stale count, as the mutation above shows.
