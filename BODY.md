rca: record the untaught-verdict family

Disposes #3283 (no closing keyword; the orchestrator wires it). Adds `dev/audit/rca/R10-RCA-OTHER-UNTAUGHT.md`: the family is mostly spelling dispersion and noise for ten of its keys. Three pull requests hide one taught obligation (the body's `## Red checks` naming no concluded red), and the record proposes folding `red-checks` into the `root-cause` family for the owner's approval. State (c); the cost test and a recorded refusal for the singletons are in the file. No code, policy or classifier change.

## Head

Measured at merge base 73365699a135fb813a43380096b6776d57f8ff4c, window v7.1.4..origin/main. Main had not moved since the first prepr run, so there is no second run.

## Mutation proof

n/a: the diff is one record under dev/audit/rca/ and changes no code or check. The countermeasure it proposes is a check-shaped change and owes its failing/passing demonstration in the group the owner approves, as the record's section 6 says.

## Null control

n/a: no check is added. The record's per-key figures were read with `dev/audit/rca/ci-red/entries.py` over a `--window-cache` of the same window.

## Figures

- node tools/policy/policy_lint.mjs --stats --since v7.1.4
- python3 -I dev/audit/rca/ci-red/entries.py W.json red-checks (also selftest-red, defect, owner-words, policy-unapproved)

Mutant run: no mutated lines (no production or test file changed); `prepr.sh` diff-mutants skipped, 0 survivors, wall time n/a.

## Red checks

none by the diff. `prepr.sh` printed `REFUSE closures`: `tests/entities.py` exits 1 here because this cloud environment has no `homeassistant` module (`ModuleNotFoundError` at `tests/harness.py:25`). That is the seat's environment, not the diff; `prepr.sh` reported `ci predict` ok and the left-to-CI list names only `tests/harness_headers.py`. Every other prepr step was ok or skipped.

## Unpinned sites

none.

## Forward-carry

The proposed fold of `red-checks` into `FRICTION_FAMILIES` root-cause is owner-gated policy. Carry: owner decision on #3283.

## Friction

cloud-setup: stale: `cloud-setup.sh --check` passes while `tests/entities.py` cannot import `homeassistant`, so `prepr.sh` refuses `closures` on every cloud head. Carry: none.
