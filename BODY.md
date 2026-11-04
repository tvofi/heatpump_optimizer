R10-MACHINERY-RATCHETS part 2 (the orchestrator opens this under group R10-MACHINERY-RATCHETS). **Merges after part 1b** (`handoff/r10-machinery-ratchets-p1b`), whose commit this head contains. Part 1, the `policy_lint.mjs` config exclusion, is already on main.

This part adds the machinery ratchet, `tools/audit/machinery_ratchet.py`. It applies a counting rule that classes each merge in a sliding window as production, machinery or record. It has two capped metrics, `nonproduction_merges` and `churn_per_kilo_product_lines`, each with a band, recorded in `dev/governance/config/machinery_budgets.json`. It also takes a right-first-time exemption, which requires evidence. The rest of the part:
- `budget_raise_gate.py` gains the file's SCHEMA entry.
- `governance.yml` and `policy-docs` gain one run line (`--check-event`), and `tests.yml` graders-head-copy gains the pathspec line.
- `prepr.sh` runs the ratchet locally.
- The instrument doc and the `ratchet-budgets.md` and `proposal-triage.md` policy text are updated.
- The script is classified in `closure.py`, `closures.json`, `entities.py` and `layout.json`.
- The in-tree mutant harness is `dev/audit/harnesses/r10_machinery_ratchet_mutants.py`.

The `field_coverage.mjs` DECLARED entry for the script rides part 1b with `pending` set. This part drops that key, so the entry turns strict here.

## Head

ee19e1f5b5d5d206906c8c9b502aac594c132916

## Mutation proof

`python3 dev/audit/harnesses/r10_machinery_ratchet_mutants.py`: the control is `unmutated: rc=0`, and the run ends with `RESULT 16 mutants: 16 killed, 0 survived, 0 stale`. Killing checks per mutant:
- `product-prefix`: a path under blueprints/ is product.
- `production-gt-0`: 2 production merges in 6 give 4 nonproduction.
- `record-all-paths`: a merge touching a record path and a tools path is machinery.
- `cap-plus-band-ge` and `cap-without-band`: over() refuses only past cap+band.
- `pr-mode-no-drop-oldest`: the candidate takes the newest slot and the oldest merge drops out.
- `pr-mode-candidate-ignored`: a candidate machinery merge past cap+band exits 1.
- `threshold-ge`: exemption: exactly 10% refuses.
- `evidence-not-checked`: exemption: 11% with a missing evidence path refuses.
- `absent-at-p-not-checked`: an entry added before its PR merged exempts nothing when that PR merges.
- `subject-number-not-matched`: exemption: an entry naming another pull request refuses.
- `subject-number-not-parsed`: positive control: an entry its own merge added takes that merge out of the window.
- `no-rename-detection`: null control: a pure move across the boundary leaves M1 and M2 identical.
- `no-whitespace-ignore`: a whitespace-only reformat of product code costs 0 product lines.
- `rename-charged-to-source`: a rename's lines are charged to its destination.
- `gain-measured-as-cost`: exemption: 11% right-first-time (a gain) passes.

The field_coverage mechanism's mutant is part 1b's.

## Null control

- The harness's unmutated copy passes its self-test (rc=0) before any kill is counted.
- Graded by origin/main's own `field_coverage.mjs`, this tree is `REFUSED registry: \`pinned tools/audit/machinery_ratchet.py\` is unregistered`: the predicted policy-docs red below. Graded by part 1b's copy, the same tree is `FIELD COVERAGE ok`, dead=0, refused=0.

## Figures

- `python3 tools/audit/machinery_ratchet.py --self-test`: machinery_ratchet self-test: 45 checks, 0 failed.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD) HEAD`: Architecture score: dS +0.0000 NULL.
- `python3 tools/audit/machinery_ratchet.py --check`: both metrics `ok` within cap + band. This figure comes from a sliding window: the instrument prints it, and it changes as main moves.
- `node tools/policy/field_coverage.mjs --only registry`: FIELD COVERAGE ok.
- `node tools/policy/field_coverage.mjs --self-test`: FIELD COVERAGE SELF-TEST ok.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D`: MODE: FULL, because the diff touches gate files; CI runs the full suite.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main`: no closures, fast, governance or instrument red predicted.

## Unpinned sites

The ratchet's predicates are `tools/` sites. Mutation-autofix's lane does not mutate them, so they are pinned by the in-tree mutant harness above.

## Red checks

- `governance / policy-docs` (predicted while part 1b is not on main): CI grades `field_coverage.mjs` with the base's copy. Main's copy does not declare `pinned tools/audit/machinery_ratchet.py`, which this part pins in governance.yml, so it refuses the file as unregistered. The head is not at fault. Part 1b (`handoff/r10-machinery-ratchets-p1b`) registers the file in a `pending` form that main accepts, and this red clears once part 1b is on main and this head is re-run. Cheaper detector: prepr's `ci predict` step runs the base's grader copy, and it found the red here (`PREDICT governance / policy-docs GRADER field_coverage.mjs REFUSED by the base's copy`). The standalone `ci_predict.py --base origin/main` that `body_push.sh` runs does not see it, as its own line says (`a data-file read is not seen`). No further detector is worth building. The predictor already catches this ordering before the handoff, and part 1b's `pending` key is the reusable countermeasure.
- `budget-raise-gate` (red until tvofi approves at the head): the gate reads `dev/governance/config/machinery_budgets.json`, a new file, as 8 raises from None, including `window_merges` and both caps with their bands. It cannot sign a new pinned value as routine, so this red is the owner's approval being owed. It is not a defect. No cheaper detector exists: the gate exists to hold a new cap for the owner, and prepr's body check names it before the handoff.

## Forward-carry

none

## Friction

none

## Raise justification

This is not a raise of an existing cap. The file is new, and the gate reads each of its values as a raise from None. The caps sit at the window's measurement, recorded by the previous seat and re-recorded after each merge of main. Each cap is graded against cap + band, and `--check` reads both metrics within cap + band at this head.
- Payments tried: none apply. There is no existing cap to stay under, and nothing in the diff can be moved, shared or deleted to lower a cap that does not yet exist on main. The approval sought is the owner's, and it owes no section. This section is here because prepr's body check asks for it.
- Architecture score: dS +0.0000 NULL

## Approval

Awaiting the owner's approving review. This diff touches policy (`dev/governance/rules/ratchet-budgets.md`, its generated `.claude/rules/` and `.cursor/rules/` copies, and `dev/governance/roles/proposal-triage.md`), and it adds new caps in `machinery_budgets.json`.

