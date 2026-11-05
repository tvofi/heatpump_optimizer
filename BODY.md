R10-MACHINERY-RATCHETS part 2 (the orchestrator opens this under group R10-MACHINERY-RATCHETS). Part 1b is on main, and so is part 1, the `policy_lint.mjs` config exclusion.

This part adds the machinery ratchet, `tools/audit/machinery_ratchet.py`. It applies a counting rule that classes each merge in a sliding window as production, machinery or record. It has two capped metrics, `nonproduction_merges` and `churn_per_kilo_product_lines`, each with a band, recorded in `dev/governance/config/machinery_budgets.json`. It also takes a right-first-time exemption, which requires evidence. The rest of the part:
- `budget_raise_gate.py` gains the file's SCHEMA entry.
- `governance.yml` and `policy-docs` gain one run line (`--check-event`), and `tests.yml` graders-head-copy gains the pathspec line.
- `prepr.sh` runs the ratchet locally.
- The instrument doc and the `ratchet-budgets.md` and `proposal-triage.md` policy text are updated.
- The script is classified in `closure.py`, `closures.json`, `entities.py` and `layout.json`.
- The in-tree mutant harness is `dev/audit/harnesses/r10_machinery_ratchet_mutants.py`.
- `field_coverage.mjs`'s entry for the script was registered by part 1b; this part drops its `pending` key, so it is strict here.

This repair (after the blocking review of 10bc3fe8) fixes two CI reds and pins the exemption-entry guards: the harness's inlined `repo_root` is now byte-identical to `tools/audit/repo_root.py`, and the self-test gains rows for a `bool` `before` and for each missing entry key.

## Head

`1e9c43f0d01842bb02486abbefd764da11fba273` is the final head. It merges origin/main `c0b082bc4877` (main had moved since the previous head) and adds the repair commit. The `prepr.sh` run below was on this head against that main tip.

## Mutation proof

`python3 dev/audit/harnesses/r10_machinery_ratchet_mutants.py`: the control is `unmutated: rc=0`, and the run ends with `RESULT 18 mutants: 18 killed, 0 survived, 0 stale`. Killing checks per mutant:
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
- `bool-before-accepted` (new): exemption: a bool `before` is not a number and refuses.
- `entry-key-missing-ok` (new): killed by the missing-key rows. With `if missing:` replaced by `if False:`, the next line raises KeyError `'pr'`, so the self-test fails.
- `gain-measured-as-cost`: exemption: 11% right-first-time (a gain) passes.

## Null control

- The harness's unmutated copy passes its self-test (rc=0) before any kill is counted.
- `exemption: an int before of the same value passes (null control)`: `pr_case("ex-int", entry(9, 1, 0))` exits 0, where the bool `before` of the same value exits 1, so the bool row refuses because of the type and not because of the numbers.
- `tests/harness_headers.py` was run red before the repair (`1 of 112 HARNESS HEADER CHECKS FAILED`) and green after (`ALL 112 HARNESS HEADER CHECKS PASSED`).

## Figures

- `python3 tools/audit/machinery_ratchet.py --self-test`: machinery_ratchet self-test: 54 checks, 0 failed.
- `PYTHONPATH=tests/hastub python3 tests/harness_headers.py`: ALL 112 HARNESS HEADER CHECKS PASSED.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `tools/pr/prepr.sh` on the head above, against origin/main `c0b082bc4877`: rc=0, `ci predict` reports no red predicted. Main had not moved when it was run.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D`: the diff touches gate files, so the gate cannot scope it; CI runs the full suite.
- `python3 tools/audit/machinery_ratchet.py --check`: both metrics within cap + band. The window slides, so the instrument prints the figure and it is not quoted here.
- The environment's numpy 2.5.4 and scipy 1.18.1 match `tests/requirements-ci.txt`. Nothing here is a golden.

## Unpinned sites

The ratchet's predicates are `tools/` sites. Mutation-autofix's lane does not mutate them, so they are pinned by the in-tree mutant harness above.

## Red checks

- `budget-raise-gate / budget-raise-gate`: red until the owner approves at the head. The gate reads `dev/governance/config/machinery_budgets.json`, a new file, as raises from None (`window_merges` and both caps with their bands), and cannot sign a new pinned value as routine. So the red is the owner's approval being owed, per `ratchet-budgets.md` and `fixer.md`'s rule that a raise needs the owner's explicit confirmation. These are the only new caps this PR records, and no other budget is raised. No cheaper detector exists: the gate exists to hold a new cap for the owner, and prepr's body check names it before the handoff.
- `tests / fast (3.14)`: was red on `tests/harness_headers.py` (`differ=['dev/audit/harnesses/r10_machinery_ratchet_mutants.py']`) because the inlined `repo_root` dropped the helper's `from pathlib import Path` line. Repaired in this head by copying the helper verbatim; the check is green locally. The cheaper detector is that check itself, which `tests/README.md` lists in the fast tier and which was not part of the scoped run last time, as the diff was FULL.
- `tests / nightly-status`: main-owned. The contract names this diff as touching what it reads (`.github/workflows/governance.yml` and `tests.yml`). The red is not caused by this diff's content; it reports the nightly lane's state on main. The cheaper detector is `ci_predict.py`, which prepr runs and which predicts none; no further detector is worth building, as `nightly-status` reads the nightly run's conclusion and nothing in a PR diff changes that.
- `governance / policy-docs` went green when part 1b reached main. It is not expected red at this head.

## Forward-carry

none

## Friction

none

## Raise justification

This is not a raise of an existing cap. The file is new, and the gate reads each of its values as a raise from None. The caps sit at the window's measurement, recorded by the previous seat and re-recorded after each merge of main. Each cap is graded against cap + band, and `--check` reads both metrics within cap + band at this head.
- Payments tried: none apply. There is no existing cap to stay under, and nothing in the diff can be moved, shared or deleted to lower a cap that does not yet exist on main. The approval sought is the owner's.
- Architecture score: dS +0.0000 NULL

## Approval

Awaiting the owner's approving review. This diff touches policy (`dev/governance/rules/ratchet-budgets.md`, its generated `.claude/rules/` and `.cursor/rules/` copies, and `dev/governance/roles/proposal-triage.md`), and it adds new caps in `machinery_budgets.json`.
