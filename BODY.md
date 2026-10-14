_Requested by **tvofi**_

The round-10 rulings of tvofi (2026-10-14) change three shapes that `tools/policy/check-wave-script.mjs` pinned by name: round 10 runs every dimension (`EVERY_DIM_ROUNDS` gains 10), every dimension gets three finder seats, and `audit-verify.js` runs one verifier per dimension carrying all three lenses, whose refute sends a finding to the judge `disputed` and never kills. `wave-script` grades from the base commit's checker (decision 0013). So the drivers' pull request (`handoff/r10-instruments`) goes red unless this checker is on `main` first. This pull request changes only the checker.

Fix review round 1 (blocked: `ROUND_DIR` and `CURRENT` unpinned) added two pins, each keyed on the driver declaring the constant so main's round-9 drivers still pass: audit-find.js `ROUND_DIR` must equal audit-verify.js `ROUND_DIR` and the directory `fold_ledger.py`'s own source reads; audit-find.js `CURRENT` must equal prepare_baseline.sh `CURRENT_PATHS` once both declare it. That second key is deliberate: CI restores prepare_baseline.sh from the base (decision 0013), so the pull request introducing the pair is graded against a base script without `CURRENT_PATHS`, where the pin is vacuous; it arms when that pull request merges. The list literal is parsed as JSON, because agreement.mjs refused a quoted-string regex the pin first used as a grammar already written in tests/features.py.

- Dispatch controls now read their seat ids, boxes and rounds off the committed `scopes.json` and the DISPATCH block. Before, they named `D1-s5`, `D14-s5`, `D12-s1`, `D4-s2`, `B3`, `B8`, `B10` and round 10.
- The verification block keys on `VERIFIERS_PER_DIMENSION = 1` declared in the driver's PANEL block. When it is absent, round 9's arm runs unchanged. When it is present, round 10's arm pins:
  - the single-vote panel rule (refute with a number goes `disputed`; anything else goes `contested`, `verified` or `unvoted`; nothing is ever `killed`);
  - one verifier per unit, with all three lenses named in its prompt;
  - the null-verifier retry;
  - that the judge and sweep files are written where `tools/audit/fold_ledger.py` reads them. The script derives that directory from the fold script's own source.
- The class-count controls take the judged count from the run, so they hold under either shape.

Alternatives considered:
- (a) Land checker and drivers together. Rejected: the base checker fails the drivers' PR on 20 checks (Figures).
- (b) Pin round 10 only. Rejected: after this merge, `main`'s own push run grades main's round-9 drivers with this checker.

## Head

ba0ce1719 (branch `r10-checker-wt`: 4c6dabebf plus two fix-review commits; merge base 17f1c55fad1b = origin/main, read 2026-10-14).

## Mutation proof

Mutants applied in place and restored byte-for-byte by the scratch runner `mutants.mjs`, at 4b58d3d6e (the drivers' head with this checker merged); null (unmutated) rc=0 `176 passed, 0 failed`:
- audit-find.js `ROUND_DIR` -> `tools/audit/round${round}`: rc=1, `175 passed, 1 failed` ("once audit-find.js declares ROUND_DIR, both drivers write where fold_ledger.py reads").
- audit-find.js `CURRENT` -> `['tools/audit/']`: rc=1, `175 passed, 1 failed` ("once both declare it, audit-find.js CURRENT is prepare_baseline.sh's CURRENT_PATHS").
- prepare_baseline.sh `CURRENT_PATHS` -> `tools/audit`: rc=1, `175 passed, 1 failed` (same check).
- audit-verify.js `ROUND_DIR` -> `tools/audit/round${round}`: rc=1, `174 passed, 2 failed` (both directory pins).
- `panelOf` returning `killed` on a refute: rc=1, `174 passed, 2 failed`.
- Survivor, accepted by the fix review as a written triage: `EVERY_DIM_ROUNDS` without 10, rc=0, `176 passed`. It is a one-round override; a pin would name round 10 and go stale at 11, and Prepare's log line prints the dimension count.

## Null control

This checker at ba0ce1719 on main's own drivers, scopes, rotation and prepare_baseline.sh (the branch's tree): rc=0, `175 passed, 0 failed`; both new pins report "not declared". Main's own checker on main: `170 passed, 0 failed`.

## Figures

- `node tools/policy/check-wave-script.mjs` at ba0ce1719 (main's drivers): rc=0, `175 passed, 0 failed`.
- The same at 4b58d3d6e (the drivers' head): rc=0, `176 passed, 0 failed`; with prepare_baseline.sh restored from origin/main as CI does: rc=0, `176 passed, 0 failed` (the CURRENT pin reports "not both declared").
- `node <origin/main's check-wave-script.mjs>` at the drivers' head: rc=1, `150 passed, 20 failed` (taken at d176dd143); this is why this checker lands first.
- `python3 -I tools/policy/agreement_py.py --out <f>; node tools/policy/agreement.mjs --py-json <f>` at 4b58d3d6e: rc=0, `divergent=0 unregistered=0 dead=0 refused=0`.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

`tools/policy/check-wave-script.mjs` is pinned (restored from the base) and carries no CODEOWNERS entry. No policy file is touched.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
