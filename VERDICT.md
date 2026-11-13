Fix review: blocked ac1607ad7344f75d619dd5f0b2f2c66d12663a3f class-open: instrument code comments outside D5's universe, .claude/workflows/*.js, .claude/hooks/*.sh, dev/audit/harnesses/**

bus-nonce: dbe59ac7e5a37e4cd7c83c02910e664d

Round 1 (handoff review). Head measured: ac1607ad7344f75d619dd5f0b2f2c66d12663a3f (ev/HEAD.txt), the handoff tip, matching the body's `## Head`.

## Block

Ruling 1 (quoted verbatim in the D6.md this PR writes) puts "Code comments in instruments" in scope for 3, and ruling 3 says D5 and D6 "always cover that full scope". `CLAUDE.md` ("Instruments") places instruments under `tools/audit/seat/`, `.claude/workflows/` (the gate-check family), `tools/audit/archscore/` and `dev/audit/harnesses/`. D5's new universe is production, `tools/**` and `tests/**` only. Three instrument seams hold D5 units (`text_ledger.py units --dim D5`) and are neither in the diff nor dispositioned in the body (ev/d5_outside_universe.txt):
- `.claude/workflows/*.js`: 9 files, 90 units. This includes `audit-find.js`, which this PR edits.
- `.claude/hooks/*.sh`: 5 files, 61 units.
- `dev/audit/harnesses/**`: 296 code files, 1548 units. These are the per-group harnesses `CLAUDE.md` names as instruments. If they count as frozen round evidence, the body has to say so, the way D6's `static` map does for `dev/audit/rounds/**`.

The body's enumeration rule is D6's `classify` line, and it covers only `**.md`, `**.mdc` and `**.html`. D5 has no equivalent, so "cannot slip out unnoticed" holds for documents only. A comment-bearing instrument file with no `.md` extension slips through. Measured (ev/plant_d5_instrument.txt):
- Plant: a committed `.claude/workflows/zz-planted.js` holding one comment. `check_scopes.py --ref <plant>` prints `ok D5 ... universe=535` and `ok coverage ... unclassified=0`, rc 0, while `text_ledger.py units --dim D5` lists the planted comment as a unit. Nothing refuses it.
- Null control: a committed `dev/zz-planted.md`. `check_scopes.py` prints `FAIL D6 ... classified in neither universe nor static: dev/zz-planted.md`.

The fix: either put these three seams in D5's universe and seats (under `max_units`), or give them a reasoned disposition. Extending a refusing line to D5's comment carriers would close the class the way D6's `classify` line does for documents.

## Findings

none

## Evidence

- Setup: `cloud-setup.sh --check` printed `OK python3 is /opt/hpo/venv-ci/bin/python3`. `git diff $(merge-base)...origin/main -- dev/governance/roles/` was empty, so the contract is current.
- Neither a review packet nor CI exists before the PR opens, so no check runs were read. `## Red checks` was not assessed; the body says `none`.
- Merge: `git merge-tree --write-tree origin/main <head>` (origin/main e23124ff6e45bac1d48b4a775dad555a37965355) printed one tree with rc 0, so there is no conflict (ev/merge_tree.txt).
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md` and `tests/golden`: untouched against the merge base 90c6bc3b0756475e28d4ace8d8e31c4788474933, with an empty diff.
- Mutation proof, re-run (ev/mutants.txt):
  - `unrowed = []` gives `FAIL a dropped row is refused by its unit id` and `17 checks, 1 failed`.
  - Cap set to `if False` gives `SELF-TEST FAILED` with the arm "a seat over ledger.max_units is refused by name" false.
  - Restored, both self-tests pass.
- Self-tests at the head (ev/selftests.txt): text_ledger printed `17 checks, 0 failed`, check_scopes printed `SELF-TEST passed`, and check-wave-script printed `226 passed, 0 failed`.
- Figures re-derived (ev/selftests.txt, ev/figures.txt):
  - D5: `seats=9 universe=535`, with units from 0 to 3808 per seat.
  - D6: `seats=7 universe=344`, with units from 2230 to 3988 per seat.
  - `unclassified=0`.
  - The strings.json sentence occurs once in 2234 units.
  - `git grep` over the round9/round10 D6 outputs exits 1; the same grep over strings.json at the base finds it.
- Not re-run: the cadence `activeIn` mutant, `structure.py`, `policy_lint.mjs --budgets`, `selftest_wiring.py`, and the `selftest_closures.json` re-record. Those figures are the body's own and not re-derived here.
