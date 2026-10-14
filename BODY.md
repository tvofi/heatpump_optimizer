_Requested by **tvofi**_

This makes the round drivers runnable for round 10 under tvofi's rulings of 2026-10-14. **It depends on the checker pull request (`handoff/r10-instruments-checker`, 4c6dabebf), which must merge first.** `wave-script` grades from the base copy of `tools/policy/check-wave-script.mjs` (decision 0013), and main's copy fails this head on 20 checks (Figures). This branch carries that commit as its first parent commit, so after the checker merges, its diff against `main` is the driver commit alone.

1. **Path drift.** The drivers named `tools/audit/{rotation,scopes,finding.schema,bugclasses}.json` and `tools/audit/round<N>/`, which moved under `dev/audit/` (R9-RO-5, R9-RO-8).
   - The breaking case: `audit-verify.js` wrote `JUDGE.json` and `sweep-*.json` to `tools/audit/round<N>/`, while `tools/audit/fold_ledger.py` reads `dev/audit/rounds/round<N>/`. The fold would have refused, finding no JUDGE.json.
   - Both drivers now write under one `ROUND_DIR`.
   - Prepare copies the current contracts, briefs and config (`CURRENT`) over the baseline. Before, it copied `tools/audit/` alone, which no longer holds the briefs.
   - `tools/audit/prepare_baseline.sh` copies the same list through `copy_current`, and gains `--copy-self-test`, whose control is the old tools/audit-only copy.
   - `COMMON.md`, `dev/audit/README.md`, the rotation ledger's `_rule`, `check_scopes.py`'s default, and three docstrings follow.
   - Records that recount where things were (archives, rounds, RCAs, carries, registers, logs, `tests/layout.json`'s move map) are left as written.
2. **Cadence.** `EVERY_DIM_ROUNDS` gains 10, so round 10 runs all fifteen dimensions.
3. **Finder seats.** `dev/audit/config/scopes.json` gives every dimension exactly three seats, one per theme of the owner's guide. `check_scopes.py` proves them disjoint and complete. Non-obvious cuts:
   - D0 splits M4-M6 on the profile axis: winter profiles for horizon and MPC masking; summer, negative, shoulder and flat for tariff structure, together with decomposition (M7).
   - D3's universe gains the card JS.
   - D5 becomes mode `cells`, a step split.
   - D6's universe becomes the source list in its own brief, step 1 (README, DISCLAIMER, docs, services.yaml, strings, translations, manifest, hacs.json).
   - D9 splits M1 on a `metric` axis taken from the brief's metric definitions.
   - D10 gives the test-coverage step (M3, a silver rule) to bronze/silver.
   - D14's axis is the ledger's class `status`, plus a `nightly-replay` value for the stop rule's second clause. A class the judge mints therefore lands in a seat without a scopes edit.
   - The boxes are re-cut for 45 seats: at most three heavy per box, and D4-s3 (visual and accessibility) is a second Chromium seat, alone on its box.
   - `check_scopes.py --self-test` now checks its two perturbations separately and reads seat keys off the file. Before, it named `D2.s4`, which no longer exists, so only one of the two perturbations was actually tested.
4. **Panel.** One verifier per dimension carries all three lenses (`VERIFIERS_PER_DIMENSION = 1` in the PANEL block).
   - A refute with an executed number marks the finding `disputed` for the common judge and never kills alone.
   - A null verifier is re-run once; after that, its findings go to the judge `unvoted`.
   - `verifier.md` and `CLAUDE.md`'s index row say so, within their caps.

Alternatives considered:
- One pull request with checker and drivers together. Rejected: the base checker refuses it.
- Keeping `killed` reachable. Rejected: with one vote, a kill would be one verifier's verdict, which the ruling forbids. `panel.killed` stays in the return, always empty, so a round-9 reader of that key reads an honest zero.

## Head

d176dd143 (branch `fix/r10-instruments`, merge base 17f1c55fad1b = origin/main, read 2026-10-14).

## Mutation proof

The checker's mutation proofs were taken at 4753d1479, the pre-amend head of this commit. The amend changed only `scopes.json` universes (dropped `docs/setup/**`, which matches no file) and a `tmp_paths.py` docstring; neither file is read by these checks. Each mutant was restored with `git checkout HEAD --`.
- `panelOf` returning `killed` on a refute: `node tools/policy/check-wave-script.mjs` rc=1, `170 passed, 2 failed`.
- `ROUND_DIR` in audit-verify.js back to `tools/audit/round${round}`: rc=1, `171 passed, 1 failed`. The failure is "the judge and the sweeps write where fold_ledger.py reads".
- `EVERY_DIM_ROUNDS` without 10: rc=0, `172 passed`. This mutant survives, and that is disclosed. The checker cannot pin it while it must also pass main's round-9 drivers. The effect is visible in the rendered plan: "round 10: 13 dimension(s), 39 finder seat(s)" instead of 15 and 45.
- Scopes, by `python3 tools/audit/check_scopes.py --repo . --ref HEAD --self-test`: rc=0. A copied D1 block is refused ("owned twice"), and an emptied last D2 seat is refused ("unowned"), each run on its own.

## Null control

- At origin/main, the scopes give D1 5 seats, D2 4, D4/D5/D6/D9/D10/D11 2, D13 1 and D14 5: 42 seats, 10 dimensions not at three. At this head, 45 seats, none not at three. Same one-liner, run over both files.
- The dry read on main's drivers lists 4 missing paths (`tools/audit/{bugclasses,finding.schema,rotation,scopes}.json`) and no `ROUND_DIR`. At this head it lists 0 missing.

## Figures

- `python3 tools/audit/check_scopes.py --repo . --ref HEAD`: rc=0, `seats=45`, 15 `ok D<k> ... seats=3` lines.
- `python3 tools/audit/check_scopes.py --repo . --ref HEAD --self-test`: rc=0, `SELF-TEST passed (both perturbed scopes refused)`.
- `node tools/policy/check-wave-script.mjs`: rc=0, `172 passed, 0 failed`.
- `node <origin/main's check-wave-script.mjs>` at 4753d1479: rc=1, `150 passed, 20 failed`. That is the base checker; hence the checker PR first.
- Dry read of every literal path either driver names (scratch `dry_read.mjs`): rc=0, `paths=23 present=23 json_parsed=4 missing=0`. Both report `ROUND_DIR dev/audit/rounds/round${round}`, and `fold_ledger.py reads dev/audit/rounds/round<N>/`.
- Round-10 Prepare rendered from the committed files with `agent()` stubbed: "round 10: 15 dimension(s), 45 finder seat(s) here of 45". Step 1 copies `tools/audit/, dev/governance/roles/, dev/governance/dimensions/, dev/audit/README.md, dev/audit/config/`; step 4 writes `dev/audit/rounds/round10/BASELINE.md`.
- Workflow syntax, compiled as the runtime runs it (async-function body, `export const meta` as a const): both drivers ok.
  - `node --check` refuses both drivers, and main's copy too: rc=1, `Unexpected token 'export'`. That is the workflow format, not a defect, and the checker compiles and drives both bodies anyway.
- `bash tools/audit/prepare_baseline.sh --copy-self-test` prints `RESULT copy_current=ok`; `--wall-self-test` prints `RESULT finder_wall=ok`; `--strip-self-test` prints `RESULT strip_earlier_rounds=ok`.
- `python3 tests/structure.py`: rc=0, `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs`: rc=0, `TOTAL: 0 error(s) across 40 policy file(s)`. `--budgets`: rc=0, with no file over its cap (instrument: `--budgets`).
- `node tools/policy/rules_sync.mjs --check`: rc=0. `node tools/policy/brief_lint.mjs`: rc=0.
- `python3 -I tools/policy/agreement_py.py --out <f>; node tools/policy/agreement.mjs --py-json <f>`: rc=0, `divergent=0 unregistered=0 dead=0 refused=0`.
- `python3 -I tools/audit/seat/tmp_paths.py --check --ref HEAD`: rc=0, `0 refused`. `--self-test`: rc=0, `50 checks, 0 failed`.
- `python3 tools/audit/fold_ledger.py --self-test`: rc=0. `python3 tools/audit/judge_batch.py --help`: rc=0.
- `python3 tests/layout.py`: rc=0, `GUARD: 0 refusal(s) against 17f1c55fad1b`. A first run refused two new lines citing retired paths: `docs/setup/**` in scopes.json and a `tmp_paths.py` docstring. Both were fixed in this head.
- `python3 tests/closure.py select --diff 17f1c55fad1b ...`: `MODE: SCOPED -- 2 script(s) run, 31 scoped out` (entities.py, harness_headers.py).
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=17f1c55fad1b PYTHONPATH=tests/hastub ./tests/run.sh`, with python3 = 3.13 because this box's default 3.11 cannot parse `tests/entities.py:3950`'s nested f-string: `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, gate rc=1.
  - `ALL 109 HARNESS HEADER CHECKS PASSED`.
  - `1 of 2303 ENTITY CHECKS FAILED`: "the coverage job reuses only an entry main's push run saved, keyed on the runner's OS". That check executes `tests.yml`'s coverage-job shell steps in a temp directory, and this diff touches no workflow. It is not re-run at main here, because this seat cannot create a second checkout. CI's run is the authority.
- Claim files: `git diff origin/main...HEAD -- tests/golden` is empty. VERSION, the manifest and the RELEASE_NOTES heading are untouched.

## Red checks

`wave-script` is red on this pull request until the checker pull request merges: the base checker refuses the new shapes, 20 checks. That is the ordering, not a defect. The cheaper detector is that checker itself, landing first.

## Forward-carry

The panel ruling now lives where the verifiers read it: `dev/governance/roles/verifier.md` and `.claude/workflows/audit-verify.js`. The seat cut lives in `dev/audit/config/scopes.json`, which `audit-find.js` reads.

## Friction

fixer: contradiction: the seat brief said to push refs only via tools/audit/seat/handoff_push.sh, but that script opens and retitles the pull request (gh pr edit, app_push.sh) and the brief forbids GitHub writes; this seat pushed handoff/<topic> and handoff-body/<topic> (body_push.sh) per fixer.md step 6 and left handoff_push.sh to the orchestrator
gate-scoping: unenforced: the local gate's python3 is 3.11 on this box and tests/entities.py needs 3.12 or later (nested f-string at tests/entities.py:3950); nothing says so and the gate fails as a SyntaxError

## Approval

Owed. This diff changes policy and code-owned paths, all needing tvofi's approving review before merge:
- `dev/governance/roles/verifier.md` (policy): one verifier per dimension, three lenses, and no kill at panel.
- `CLAUDE.md` (policy): its index row for `verifier.md`.
- `dev/audit/README.md` (policy): the layout block and the harness path.
- `.claude/workflows/audit-find.js` and `audit-verify.js` (code-owned).

`dev/governance/roles/COMMON.md` (paths only, net 0 lines, ~0 tokens) carries no owner. No `*_budgets.json` is touched; every edited policy file is within its cap.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
