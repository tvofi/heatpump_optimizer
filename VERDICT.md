Fix review: merge f8b7a41a1e639c8dacbf188ad8054baeb8ffabe7

bus-nonce: 184515934e2a760ab0828e110ef3e176
pending-ci: governance / env-matrix, governance / instrument-self-tests

## Evidence
- Head f8b7a41a1e639c8dacbf188ad8054baeb8ffabe7 is two commits on main ad95665e: merge a08433aa (parents ad95665e, b1697d36) plus the delivery row. merge-tree of origin/main with the head reports no conflict (ev/mt-main.txt).
- Merged roster equals the expected merge of main ad95665e with roster tip b1697d36: roster blob f47f21caa6b6 in both; the only tree difference is dev/programme/delivery/3555.md (ev/diff-expected-vs-head.txt).
- New carry /groups/503/carry/83 on R11-INTAKE-R10-RESIDUE contains the literal 'carry-201 entry 6 (file removed)' and ends with carry-201.json carries[6].remeasure on main, byte for byte (650 chars; exact-embed True, endswith True; ev/carry-check.txt). The other hit of the literal (carry/56) is a pre-existing item, present on main.
- node tools/policy/brief_lint.mjs exits 0 at the head (ev/brief_lint_full.txt).
- carry_audit at the head: 0 finding items. This verdict holds no findings.
- classify at the head prints WAIT (pending: gate red: none). Still running at review: governance / env-matrix, governance / instrument-self-tests. The digest's gate row read failure while classify read WAIT; classify decides. The review_packet introduced-red refusal is the unconcluded instrument-self-tests job (fail closed). No owed red was seen (ev/classify2.txt, ev/packet2.md).
