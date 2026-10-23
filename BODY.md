## Unit

P2b units U1 + U2 + U7, stacked on U0c's head `d22b5f303`. Four commits on top of it:
`hassfest.yml` (U1), `validate.yml` (U2), `arch-score.yml` (U7), the harness maps, and a `tests/entities.py` edit in U7's scope. `git diff --stat d22b5f303..HEAD`: 8 files, 75 insertions, 66 deletions. Production workflow lines about 100.

- `hassfest.yml`, `validate.yml`: `on: workflow_call` only, no inputs or secrets. `concurrency`, `push`, `pull_request`, `merge_group`, `workflow_dispatch` dropped. Top-level `permissions: contents: read` kept (the callee floor).
- `arch-score.yml`: `on: workflow_call` with inputs `pr`, `base`, `head` (each `type: string`, `default: ""`). `pull_request` and `merge_group` triggers and its `concurrency` dropped. The first step (`id: pr`) reads the pull request through the API from `inputs.pr`, writes the body, and outputs `scored`, `base`, `head`. With no `inputs.pr` it outputs `scored=false` and the score step is skipped (nothing to score). The score step is unchanged (`PR_BASE`/`PR_HEAD` env), now fed from `steps.pr.outputs`; it runs only when `scored == 'true'`. On `merge_group` it keeps the check that the API head equals `HEAD^2`.
- `tests/entities.py`: `arch-score.yml` removed from the `_EDITED_FILES` expectation and from `_CC_TWIN_ROUTE` (U0c's Wiring for U9b). 4 lines deleted.

## Interface

Consumes U0c's interface unchanged. Job names unchanged, so the checks stay `hassfest / hassfest`, `validate / validate-hacs`, `arch-score / arch-score`.

| callee | inputs | secrets | caller grant |
|---|---|---|---|
| `hassfest.yml` | none | none | `contents: read` |
| `validate.yml` | none | none | `contents: read` |
| `arch-score.yml` | `pr`, `base`, `head` | none | `contents: read`, `pull-requests: read` |

`inputs.base` (a ref name) is declared but unused: the base SHA is the event's (`pull_request.base.sha || merge_group.base_sha`, caller's `github.event`) or, on a dispatch, the API's `.base.sha`. `inputs.head` is the head SHA when set.

## Static map

`sh dev/audit/harnesses/r10_ci_layout_p2_u1u2u7/unitcheck.sh` (BEFORE is `origin/main`'s copy of each file; instrument read from `archive/probe/design-ci-rev4`):

```
hassfest.yml:   STATIC rows 7->7 lost 0 gained 0 changed 1 (mapped 1) misplaced 0 rc 0
validate.yml:   STATIC rows 6->6 lost 0 gained 0 changed 1 (mapped 1) misplaced 0 rc 0
arch-score.yml: STATIC rows 7->7 lost 0 gained 0 changed 3 (mapped 3) misplaced 0 rc 0
plant, an unmapped step added (want rc 1): STATIC rows 7->8 lost 0 gained 1 changed 1 (mapped 1) misplaced 0 rc 1
```

Maps: hassfest and validate `changed: |triggers`; arch-score `changed: |triggers`, `arch-score|Name the pull request and read its body`, `arch-score|Score the change, and refuse an unexplained rise`. Without a map each file reads rc 1 (the changed rows unmapped), so the maps are what turn it to rc 0. `unitcheck2` hashes no `with:`; the caller inputs are U0c's umbrella pin.

## Controls

- `tests/entities.py` run with python3.13 (python 3.11 cannot parse the file): at `d22b5f303` 1 of 2400 red (the template arm, U0c's known red, whose cause is the policy_lint "2 files define pr-contract" check). Failing first for the U7 edit: before the `entities.py` commit the `edited` pin was red on this head (`a body edit starts a run of the contract job and the budget gate...`, naming `arch-score.yml` missing from the `edited` listing); after it, green.
- `tests/arch_score.py --stored`: `ALL 73 ARCHITECTURE SCORE CHECKS PASSED` (that file's `base_runs_the_gate` drives the score step's script text over the #2068 plant; the step text is unchanged).
- `python3.13 tests/structure.py`: PASSED. `tmp_paths.py --check`: 0 refused.
- Not run: the full scoped gate (`./tests/run.sh`) and mutation of the new maps; `arch-score.yml`'s API step is not exercised offline.

## Live checks owed

- U1: a dispatch pair, `hassfest.yml` at the base (BEFORE) vs `ci.yml` dispatch (AFTER); `hassfest / hassfest` green.
- U2: the same pair for `validate / validate-hacs`.
- U7: the `pull_request` pair on a draft probe PR (`arch-score / arch-score` reported) and the D-2 shapes:
  - a diff touching `custom_components/` with a planted score rise (no `## Architecture score` explanation in the body): `arch-score / arch-score` red, `gate` FAIL;
  - a diff missing `custom_components/`: `arch-score` reported, `gate` pass.
  - A merge-queue entry (head equal to `HEAD^2`) and a dispatch naming a PR (base SHA from the API) are untested offline; a dispatch naming no PR should show the step skipped and the job green.

## Wiring

- `ci.yml`: none needed; U0c's callers already pass exactly the declared inputs.
- Needs U9 (readers), red on this head and green at `d22b5f303`:
  1. `every required context runs on a merge-queue entry` and its null control: `hassfest.yml` and `validate.yml` no longer list `merge_group` (the caller `ci.yml` does); the producer lookup must follow the callers.
  2. `a red that lands after pr-contract ran re-runs it...`: the follower's `workflow_run` expects to watch `Hassfest`, `Validate` and `Architecture score`, which now have no trigger of their own; it expects the six pull-request workflows `Budget raise gate`, `CodeQL`, `Governance`, `Kernel points`, `PR contract`, `Tests`. Whoever owns the follower's list must drop the three.
- No `governance.yml` or `closure.py` line: the new files are under `dev/audit/harnesses/`, which U0c's sibling directory shows needs no classification (`tests/entities.py` did not complain).

## Red checks

- `the template arm turns the acceptance red on a template that fails its own contract`: red at `d22b5f303` (U0c's one known red, the policy_lint "2 files define pr-contract" interaction); unchanged here.
- The two merge-queue pins and the follower pin above are red on this head only, by design of the cut-over, owed to U9.
