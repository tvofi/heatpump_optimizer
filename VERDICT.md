Fix review: merge 7db3d500bc780da7b6234556a0d7a58f0392b97d

bus-nonce: 5f629719ade64db37817ba709ff7cb36
pending-ci: gate

Round 1 (first review). Record PR landing the round-10 roster; no production code, no budgets, no VERSION/manifest/notes touched (diff vs main: dev/programme/rosters/wave-r10-groups.json and dev/programme/delivery/3554.md only).

## Evidence
- Merge check: `git merge-tree --write-tree origin/main 7db3d500bc780da7b6234556a0d7a58f0392b97d` exits 0, no conflict. Head's parents: b36236d2e9 (merge of roster ce60e9925f into main 3038b9deaf) then the delivery-row commit.
- Roster equals roster branch tip except main's later change: tree of `merge-tree(main 3038b9de, roster tip ce60e992)` differs from the head tree only by the new delivery/3554.md line. Roster tip vs head on wave-r10-groups.json differs only by R10-CATALOG-PR (note gains the "set-price unset -> 240 min" text, plus owner_price_minutes 240 and owner_price_cite), which is main's change after the merge base 3853ed23 (4 insertions, 2 deletions there). Nothing else differs.
- brief_lint: `node tools/policy/brief_lint.mjs` at head rc=0 (ev/brief_lint.txt).
- `PYTHONPATH=tests/hastub python3 tests/entities.py` (venv-ci; HA is not importable without the stub): head "ALL 2711 ENTITY CHECKS PASSED" rc=0, origin/main 3038b9de "ALL 2711 ENTITY CHECKS PASSED" rc=0. The late-writing-descendant failure the opener saw did not reproduce at head or at main in this environment, so I cannot say main has it; both were clean, and the opener's failure is unexplained (possible local-only or timing flake, gate_lock lease waits appear in both logs identically in kind).
- CI: `merge_train.py classify --pr 3554` printed "WAIT 7db3d500bc780da7b6234556a0d7a58f0392b97d pending: gate red: none" (rc 3) on two polls; no red. Returning pending-ci rather than waiting.
- Not run (CI-heavy, per contract): gate, mutation table. Not applicable: mutation proof, golden claims, class rule (record PR).
- Review packet and logs under ev/ (ev/HEAD.txt holds the head).

## Findings
- Follow-up: the opener's local entities.py failure (late-writing descendant of a measured script) was not reproducible at head or main; if CI's gate shows it, it is not introduced by this PR. Carry: dismissed: not reproducible at head or origin/main, both 2711 checks pass
