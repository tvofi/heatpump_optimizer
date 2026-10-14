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

Fix review round 1 (blocked) asked for four things, all done in 7706f1dad and the merge of the checker branch:
- D11's universe named `docs/decisions/**` (0 tracked files since R9-RO-5) and lacked `dev/governance/**`, so the governance dimension would have audited without the policy tree. It now names `dev/governance/**`; every universe glob in scopes.json matches at least one tracked file (main: three matched none).
- The leads seat's export copies `CURRENT`, as a finder's does, not `tools/audit/` alone.
- `dev/governance/dimensions/D14.md` M1 and `D13.md` M4 cite `dev/audit/config/bugclasses.json` and `dev/audit/rounds/round4/D11/dora_keys.py`. The longer paths are paid for inside each file's token cap by two one-word cuts ("lists its seams" -> "lists seams"; "have been added" -> "were added"); no cap is raised.
- The mutation proof is re-run below against the checker's new pins.

Alternatives considered:
- One pull request with checker and drivers together. Rejected: the base checker refuses it.
- Keeping `killed` reachable. Rejected: with one vote, a kill would be one verifier's verdict, which the ruling forbids. `panel.killed` stays in the return, always empty, so a round-9 reader of that key reads an honest zero.

## Head

4b58d3d6e (branch `fix/r10-instruments`: d176dd143, the fix-review commit 7706f1dad, and `r10-checker-wt` (ba0ce1719) merged in, never rebased; merge base 17f1c55fad1b = origin/main, read 2026-10-14).

## Mutation proof

Mutants applied in place and restored byte-for-byte by the scratch runner `mutants.mjs`, at 4b58d3d6e (the drivers' head with this checker merged); null (unmutated) rc=0 `176 passed, 0 failed`:
- audit-find.js `ROUND_DIR` -> `tools/audit/round${round}`: rc=1, `175 passed, 1 failed` ("once audit-find.js declares ROUND_DIR, both drivers write where fold_ledger.py reads").
- audit-find.js `CURRENT` -> `['tools/audit/']`: rc=1, `175 passed, 1 failed` ("once both declare it, audit-find.js CURRENT is prepare_baseline.sh's CURRENT_PATHS").
- prepare_baseline.sh `CURRENT_PATHS` -> `tools/audit`: rc=1, `175 passed, 1 failed` (same check).
- audit-verify.js `ROUND_DIR` -> `tools/audit/round${round}`: rc=1, `174 passed, 2 failed` (both directory pins).
- `panelOf` returning `killed` on a refute: rc=1, `174 passed, 2 failed`.
- Survivor, accepted by the fix review as a written triage: `EVERY_DIM_ROUNDS` without 10, rc=0, `176 passed`. It is a one-round override; a pin would name round 10 and go stale at 11, and Prepare's log line prints the dimension count.
- Scopes, by `python3 tools/audit/check_scopes.py --repo . --ref HEAD --self-test`: rc=0. A copied D1 block is refused ("owned twice") and an emptied last D2 seat is refused ("unowned"), each run on its own.

## Null control

- At origin/main, the scopes give D1 5 seats, D2 4, D4/D5/D6/D9/D10/D11 2, D13 1 and D14 5: 42 seats, 10 dimensions not at three. At this head, 45 seats, none not at three. Same one-liner over both files.
- Universe globs matching no tracked file (scratch `zero_globs.py` over `git ls-files`): origin/main's scopes rc=1, `zero_globs=3` (D5 and D6 `docs/setup/**`, D11 `docs/decisions/**`); this head rc=0, `zero_globs=0`.
- The dry read on main's drivers lists 4 missing paths (`tools/audit/{bugclasses,finding.schema,rotation,scopes}.json`) and no `ROUND_DIR`; at this head, 0 missing.

## Figures

- `python3 tools/audit/check_scopes.py --repo . --ref HEAD`: rc=0, `seats=45`, 15 `ok D<k> ... seats=3` lines; D11 universe 2150 files (2100 before `dev/governance/**`). `--self-test`: rc=0, `SELF-TEST passed (both perturbed scopes refused)`.
- `node tools/policy/check-wave-script.mjs`: rc=0, `176 passed, 0 failed`.
- `node <origin/main's check-wave-script.mjs>` at d176dd143: rc=1, `150 passed, 20 failed`; the base checker, hence the checker pull request first.
- Dry read of every literal path either driver names (scratch `dry_read.mjs`): rc=0, `paths=23 present=23 json_parsed=4 missing=0`; both report `ROUND_DIR dev/audit/rounds/round${round}`, and `fold_ledger.py reads dev/audit/rounds/round<N>/`.
- Round-10 Prepare rendered from the committed files with `agent()` stubbed (scratch `render_prepare.mjs`, taken at d176dd143): "round 10: 15 dimension(s), 45 finder seat(s) here of 45".
- Workflow syntax compiled as the runtime runs it (async-function body): both drivers ok. `node --check` refuses both drivers and main's copy alike (rc=1, `Unexpected token 'export'`): the workflow format, not a defect.
- `bash tools/audit/prepare_baseline.sh --copy-self-test` prints `RESULT copy_current=ok`; `--wall-self-test` `RESULT finder_wall=ok`; `--strip-self-test` `RESULT strip_earlier_rounds=ok` (taken at d176dd143; the script is unchanged since).
- `python3 tests/structure.py`: rc=0, `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs`: rc=0, `TOTAL: 0 error(s) across 40 policy file(s)`; `--budgets`: rc=0, no file over its cap (instrument: `--budgets`).
- `node tools/policy/rules_sync.mjs --check`: rc=0. `node tools/policy/brief_lint.mjs`: rc=0.
- `python3 -I tools/policy/agreement_py.py --out <f>; node tools/policy/agreement.mjs --py-json <f>`: rc=0, `divergent=0 unregistered=0 dead=0 refused=0`.
- `python3 -I tools/audit/seat/tmp_paths.py --check --ref HEAD`: rc=0, `0 refused`.
- `python3 tests/layout.py`: rc=0, `GUARD: 0 refusal(s) against 17f1c55fad1b`.
- `GATE_SCOPE=auto GOLDEN_MODE=drift GOLDEN_REF=17f1c55fad1b PYTHONPATH=tests/hastub ./tests/run.sh`, with python3 = 3.13 first on the seat's full PATH: rc=0, `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, `ALL 2303 ENTITY CHECKS PASSED`, `ALL 109 HARNESS HEADER CHECKS PASSED`, `5 TEST SCRIPT(S) PASSED; 30 SCOPED OUT AND NOT RUN`. (Round 1's 1/2303 coverage-job failure came from this seat running the gate under a trimmed PATH; it does not reproduce on the full one, nor in the reviewer's standalone runs at base and head.)
- Claim files: `git diff 17f1c55fad1b...HEAD -- tests/golden VERSION custom_components/heatpump_optimizer/manifest.json RELEASE_NOTES.md` is empty.

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
- `dev/governance/dimensions/D13.md` and `D14.md` (policy): moved-path citations only, within their caps.

`dev/governance/roles/COMMON.md` (paths only, net 0 lines, ~0 tokens) carries no owner. No `*_budgets.json` is touched; every edited policy file is within its cap.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
