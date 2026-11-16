# BLOCKED: box CAP1, round 11, step 1 PREPARE

scopes_rc is 1 (check_scopes.py exits non-zero: the round-11 start evaluation dev/audit/yardstick/round11/EVALUATION.json is not in the tree at the baseline). Per the procedure the box stops here; no finder seat was dispatched.

Also observed: the drift-cache warm (env_drift.py --all <baseline>) refused with SELF-COMPARISON, rc=1, because $REPO is checked out at the baseline itself.

```json
{
  "exportDir": "/home/user/audit-r11-baseline",
  "worktrees": {},
  "python": "/opt/hpo/venv-ci/bin/python3",
  "node": "/opt/node22/bin/node",
  "rotation_ok": true,
  "rotation_note": "",
  "scopes_ok": true,
  "scopes_note": "",
  "scopes_rc": 1,
  "scopes_out": "ref=367c3b9cac0f4d11cdbeee9c05ffc893f7e1390c seats=59\nok D0 mode=cells seats=3 universe=3 [s1:3f/22959loc, s2:3f/22959loc, s3:3f/22959loc]\nok D1 mode=cells seats=3 universe=94 [s1:94f/74383loc, s2:94f/74383loc, s3:94f/74383loc]\nok D2 mode=cells seats=3 universe=94 [s1:94f/74383loc, s2:94f/74383loc, s3:94f/74383loc]\nok D3 mode=cells seats=3 universe=165 [s1:12f/31631loc, s2:18f/15975loc, s3:135f/43214loc]\nok D4 mode=cells seats=3 universe=15 [s1:15f/20869loc, s2:15f/20869loc, s3:15f/20869loc]\nok D5 mode=cells seats=10 universe=883 [s1:15f/0loc/0u, s2:15f/0loc/75u, s3:45f/37164loc/2852u, s4:50f/53656loc/3339u, s5:73f/0loc/3587u, s6:258f/0loc/3749u, s7:3f/0loc/3973u, s8:44f/0loc/3626u, s9:69f/0loc/3748u, s10:326f/0loc/1780u]\nok D6 mode=files seats=7 universe=361 [s1:13f/0loc/3948u, s2:109f/0loc/4012u, s3:95f/74383loc/3329u, s4:2f/16437loc/3913u, s5:139f/0loc/3453u, s6:1f/0loc/2300u, s7:2f/0loc/2668u]\nok D7 mode=cells seats=3 universe=94 [s1:94f/74383loc, s2:94f/74383loc, s3:94f/74383loc]\nok D8 mode=cells seats=3 universe=6 [s1:6f/4741loc, s2:6f/4741loc, s3:6f/4741loc]\nok D9 mode=cells seats=3 universe=95 [s1:95f/90820loc, s2:95f/90820loc, s3:95f/90820loc]\nok D10 mode=cells seats=3 universe=113 [s1:113f/90820loc, s2:113f/90820loc, s3:113f/90820loc]\nok D11 mode=cells seats=3 universe=1381 [s1:1381f/0loc, s2:1381f/0loc, s3:1381f/0loc]\nok D12 mode=cells seats=3 universe=94 [s1:94f/74383loc, s2:94f/74383loc, s3:94f/74383loc]\nok D13 mode=cells seats=3 universe=1 [s1:1f/0loc, s2:1f/0loc, s3:1f/0loc]\nok D14 mode=cells seats=3 universe=1 [s1:1f/0loc, s2:1f/0loc, s3:1f/0loc]\nok D15 mode=cells seats=3 universe=1 [s1:1f/0loc, s2:1f/0loc, s3:1f/0loc]\nok coverage tracked=11430 in_universe=1631 excluded=9799 unclassified=0\nok harness citations: 0 harness(es) implementing a brief's rule the brief does not cite\nFAIL start evaluation round=11: 1 gap(s), 0 card(s) beside the finders\n   dev/audit/yardstick/round11/EVALUATION.json is not in the tree: the start evaluation has not run\n"
}
```
