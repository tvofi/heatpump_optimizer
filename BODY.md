_Requested by **tvofi**_

The round-10 rulings of tvofi (2026-10-14) change three shapes that `tools/policy/check-wave-script.mjs` pinned by name: round 10 runs every dimension (`EVERY_DIM_ROUNDS` gains 10), every dimension gets three finder seats, and `audit-verify.js` runs one verifier per dimension carrying all three lenses, whose refute sends a finding to the judge `disputed` and never kills. `wave-script` grades from the base commit's checker (decision 0013). So the drivers' pull request (`handoff/r10-instruments`) goes red unless this checker is on `main` first. This pull request changes only the checker.

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

4c6dabebf (branch `fix/r10-instruments`, merge base 17f1c55fad1b = origin/main at 2026-10-14).

## Mutation proof

Run against the drivers of `handoff/r10-instruments` at 4753d1479, with each mutant applied and then restored with `git checkout HEAD --`:
- `panelOf` returning `killed` on a refute (audit-verify.js): `node tools/policy/check-wave-script.mjs` rc=1, `170 passed, 2 failed`. The two failures are "a refute with an executed number sends the finding disputed; ..." and "nothing is killed at panel: ...".
- `ROUND_DIR` reverted to `tools/audit/round${round}` (audit-verify.js): rc=1, `171 passed, 1 failed`. The failure is "the judge and the sweeps write where fold_ledger.py reads (dev/audit/rounds/round9/)".
- Survivor, disclosed: removing 10 from `EVERY_DIM_ROUNDS` (audit-find.js) leaves rc=0, `172 passed`. The checker asserts that every round in the set runs all dimensions, but it does not assert that 10 is in the set. Pinning that here would refuse main's current drivers. The round-10 override is a one-round fact, not an invariant.

## Null control

This checker on main's unchanged drivers, scopes, rotation and prepare_baseline.sh (copied in from origin/main): rc=0, `171 passed, 0 failed`. Main's own checker on main: `170 passed, 0 failed`. The extra check is the PANEL declaration check, which passes with no declaration.

## Figures

- `node tools/policy/check-wave-script.mjs` with main's drivers restored: rc=0, `171 passed, 0 failed`.
- The same at 4753d1479 (the drivers' head): rc=0, `172 passed, 0 failed`.
- `node <origin/main's check-wave-script.mjs, copied beside counts.mjs>` at 4753d1479: rc=1, `150 passed, 20 failed`. This is why this checker lands first.
- `python3 -I tools/policy/agreement_py.py --out <f>; node tools/policy/agreement.mjs --py-json <f>`: rc=0, `divergent=0 unregistered=0 dead=0 refused=0`.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

`tools/policy/check-wave-script.mjs` is pinned (restored from the base) and carries no CODEOWNERS entry. No policy file is touched.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
