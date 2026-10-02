_Requested by **tvofi**_

Closes #1757 (R9-F11.7, the countermeasure from the #1721 RCA, `RCA-BULK-3.md` section 1).

`policy-docs` restores `.claude/workflows/*.mjs` from the base. A changed governance grader therefore ran for the first time under the Actions `GITHUB_TOKEN` on the push to main. For #1715 that meant a comparator reading `bypass_actors`, a ruleset field this token cannot see. A seat's local run cannot detect this either, because it reads the API with the seat's own identity. `graders-head-copy` covered only `coverage_ratchet` and `delivery_status`.

Change:
- `.github/workflows/tests.yml`, `graders-head-copy`: when the three-dot diff touches the pathspec that `policy-docs` restores from the base, the pull request's own `policy_lint.mjs` and `field_coverage.mjs` now run under this job's read-only token (workflow floor `contents: read`; the job adds no `permissions` block).
  - The job stays non-required, and `HPO_JOB_GRADES: nothing` is unchanged.
  - Each new step's `if:` leads with `!cancelled()` (#1854).
  - Checkout gains `fetch-tags: true`, because `policy_lint.mjs`'s citation resolvers ask git about tags.
- `tests/entities.py` adds three checks:
  1. It derives the class from the workflows: every program that a base-restoring job runs from its restored pathspec, in a step whose env carries a token. Each such program needs either a `graders-head-copy` step that runs it with `GITHUB_TOKEN`, or a recorded reason in `_PT_EXEMPT`. A stale exemption is refused.
  2. It pins the arm's pathspec equal to the restore pathspec of `policy-docs`.
  3. A null control.

## Head

14665a7b58e7b1648c2a88fe04abe0a569056332

This head merges origin/main `1abfef56d` (now the merge base) into the authored commits. Steps 2–8 were re-run after that merge, and every figure below is measured at this head unless a line says otherwise.

## Mutation proof

Each mutant edits `.github/workflows/tests.yml` in place, runs `tests/entities.py` in full (`~/hpo-seats/R9-F11.4-venv/bin/python3`, `PYTHONPATH=tests/hastub`), then restores from HEAD. The predicate is mutated, not the tail.

- M1, tests.yml at origin/main (the arm absent): rc=1, `2 of 2077 ENTITY CHECKS FAILED`, both new:
  - `FAIL every pinned grader given a token runs its own copy under the Actions token on the pull request`, with `unarmed=['.claude/workflows/field_coverage.mjs', '.claude/workflows/policy_lint.mjs']`
  - `FAIL and the arm fires on exactly the pathspec policy-docs restores from the base`, with `arm=[]`
- M2, the field_coverage step's `run:` replaced by `true`: the first new check FAILs.
  - The first run of this mutant (at `4c3961ac1`) crashed the census on the YAML boolean (`'bool' object has no attribute 'partition'`) instead of reporting. `138b6371b` coerces `run` to a string, and at this head the mutant reports the FAIL.
  - A later traceback in that run comes from a pre-existing check that also assumes a string `run`, which this diff does not touch.
- M3, `'tools/audit/record-predicate'` dropped from the arm's pathspec: rc=1, `1 of 2077 ENTITY CHECKS FAILED`, `FAIL and the arm fires on exactly the pathspec policy-docs restores from the base`.
- M4, `!cancelled() &&` dropped from the policy_lint step's `if:`: rc=1, `1 of 2077`, the first check FAILs with `unarmed=['.claude/workflows/policy_lint.mjs']`.
- Restored head: rc=0, `ALL 2077 ENTITY CHECKS PASSED`.

`ac398db55` narrows the census's quoted-path grammar to `'([^'\n]+)'`. The old `'([^']+)'` was byte-identical to a grammar in `tools/audit/merge_fastpath.py`, which reads a different concept, and the agreement lane refused it as unregistered. A pathspec item never spans a line, so the narrower form loses nothing. At this head `agreement.mjs` prints `unregistered=0`.

Pinning killed mutants belongs to `mutation-autofix`; no local `--pin-killed` was run.

## Null control

- In-check: the same parsed workflows, with the `env` removed from the arm's policy_lint step, leave `policy_lint.mjs` unarmed. That check is `ok` at head, so the predicate reads the step's env and not only its run line.
- The RCA demonstration, re-taken at this merge base: `field_coverage.mjs --only ruleset --ruleset-json`. The admin view is the live ruleset 23698884 read as tvofi. The Actions view is the same object with `bypass_actors` deleted (`jq 'del(.bypass_actors)'`). The demo tree is origin/main with the #1721-shaped comparator: `RULESET_TOKEN_HIDDEN.includes(k)` short-circuited to `false` in `counts.mjs`.
  - A literal revert of `counts.mjs` to `87d780c7` does not load on current main: `field_coverage.mjs` imports `TOKEN_HIDDEN_SKIP_RE`, which that version does not export.

| tree | admin view (null) | Actions view |
|---|---|---|
| origin/main `1abfef56d` | rc=0, read=43 refused=0 | rc=0, read=37 refused=0 |
| demo `39b07c75b` (#1721 comparator) | rc=0, read=43 refused=0 | **rc=1, REFUSED**, "unperturbed, is already red" |

The admin column is green at both trees, which is what a seat's pre-merge run sees. The CI arm's own red/green pair is owed; see "Verification after merge".

## Figures

- Token-bearing pinned graders, the class this check enumerates: 6. They are `policy_lint.mjs` and `field_coverage.mjs` (armed here), plus `policy_lint_envmatrix.mjs`, `budget_raise_gate.py`, `contract_rerun.py` and `tests/nightly_status.py` (each with a reason in `_PT_EXEMPT`). Instrument: the first new check in `tests/entities.py`; its failure message prints the derived set, as M1 shows. Cross-checked by a seat-local enumerator, `seams_principal.py` (sha1 `a43a4fa0a50a4cff40c2220ebbbfa4dde13a7fc2`), which printed 7 (workflow, job, program) rows over the same 6 programs.
- The seam dispositions, with the reason for each:
  - `policy_lint_envmatrix.mjs` (env-matrix): its token-bearing shape runs `policy_lint.mjs`, which this arm now runs under the token.
  - `budget_raise_gate.py`: it reads review objects, and the RCA found the ruleset read to be the only principal-dependent reader in the tree.
  - `contract_rerun.py`: it re-requests a run and grades nothing.
  - `nightly_status.py`: it needs `actions: read`, which `graders-head-copy` lacks, and `fast` already drives its copy.
- Arm cost per triggering push, timed locally (`/usr/bin/time -p` at the earlier base `68b8cb97d`, admin token): `policy_lint.mjs` 11.6 s, `field_coverage.mjs` 33.3 s. The job is non-required and off the critical path.
- Head instruments, all run locally:
  - `tests/entities.py`: ALL 2077 PASSED
  - `tests/structure.py`: STRUCTURE RATCHET PASSED
  - `tests/harness_headers.py`: ALL 94 PASSED
  - `policy_lint.mjs`: TOTAL: 0 error(s) across 40 policy file(s)
  - `field_coverage.mjs`: FIELD COVERAGE ok, blind=0 dead=0 refused=0
  - `codeowners_gap.py --check`: uncovered_files=0
  - `rules_sync.mjs --check`: ok
- Scope: `python3 tests/closure.py select --diff 1abfef56d` prints `MODE: FULL`, because `.github/workflows/tests.yml` changes the gate itself. The full suite is CI's; numpy-dependent scripts outside entities, structure and harness_headers were not run here.

## Red checks

none. The latest scheduled Tests run (`36984959667`, 2026-10-02T08:36Z) concluded `success`, so `nightly-status` has no red to answer.

## Forward-carry

none. The class rule now lives in `tests/entities.py` (`_PT_EXEMPT` and its census). A future token-bearing pinned grader is refused there until it is armed or given a reason, so no later stage's brief needs a hand-carried note.

## Friction

none

## Approval

Code-owned CI wiring (`.github/workflows/tests.yml`). It merges on tvofi's approving review at the head above, given under mandate 5951564627 through the orchestrator. No budget moved.

## Verification after merge

Owed to the orchestrator; it cannot be run from a seat, because seats make no GitHub writes. The ref `handoff/r9-f11-governance-7-demo` at `39b07c75b59a21592c8768b62e0f46cb4da9ccec` is this head plus the one-token #1721-shaped `counts.mjs` perturbation.
- Expected on a draft pull request from it: `graders-head-copy` red on "The pull request's field_coverage.mjs, under the Actions token" (ruleset REFUSED). The `policy_lint.mjs` step should be red too, on `required-contexts` drift for `bypass_actors`. `policy-docs` stays green, because it runs the base's copy.
- At this PR's own head, the same steps are green.
- Close that draft unmerged.
