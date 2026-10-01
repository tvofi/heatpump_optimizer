R9-F10.9c, stage 2 of 2 (process review item 2A, adopted by tvofi 2026-10-01T16:51Z: "On 2, I want both"). Stage 1 landed as #1823 (`d536fb4d`), and this branch merges it, so the base's `codeowners_gap.py` and `prepr.sh` accept the queue's `PINNED` form here.

Before: no workflow lists `merge_group`, so a merge queue on `main` would wait on 17 required contexts that nothing produces.

After: each workflow producing one of those 17 required contexts lists `merge_group: [checks_requested]`, and each producing job runs on a queue entry as it does on a pull request.

**What runs on a queue entry, and against what.**
- `tests.yml`. `fast`, `browser`, `briefs`, `typing` and `mutation` admit `merge_group`. `fast` treats the queue commit like a pull request's synthetic merge: `GOLDEN_REF` is `HEAD^1` (the main tip or the entry ahead), `CLAIM_HEAD` is `HEAD^2` (the pull request's head), `GATE_SCOPE=auto`, and the drift-baseline cache is keyed as on a pull request. A queue commit with no second parent fails the step. `closure-scope` and `closures` diff `merge_group.base_sha...merge_group.head_sha`, which also covers the entries stacked ahead; the docs-only fast arm applies to that diff. `briefs` restores its linter from the queue's base. `mutation` already diffs against `origin/main`.
- `governance.yml`. `policy-docs`, `env-matrix` and `wave-script` run with `PINNED` from the queue's base, and field coverage diffs from it. `record` keeps off the queue (`!= pull_request && != merge_group`).
- `pr-contract.yml` and `budget-raise-gate.yml`. Both grade the pull request the entry carries:
  - A new step, after the base restore, takes its number from the queue branch name (`jq` capture) and its head from `HEAD^2`. It fails unless `GET /pulls/<n>` reports that same head.
  - It writes step outputs only, never `$GITHUB_ENV`.
  - Every `pull_request.*` read gains `|| steps.pr.outputs.*`. The title comes from the API.
  - `budget-raise-gate` still has no `if:`.
- `hassfest.yml`, `validate.yml`, `codeql.yml`: the trigger only.
- Kept off the queue:
  - the three autofix jobs, `graders-head-copy` and `nightly-status`, which are PR-only by design;
  - `coverage` and `coverage-ratchet`, which are not required. They ran on the pull request's head and run again on the push the merge makes.

**No barrier lost.** A queue entry runs every required job the pull request ran, against a base at least as new, and graded by the base's own graders. The push the merge makes to `main` still runs FULL and unscoped, and a red `main` is still reverted first. Superseded-run cancellation (stage 1) never touches a `merge_group` run: its group key is the run id. `codeowners_gap.py --check` on this head reports the same pinned set as on stage 1 (`pinned_by_base_restore=26`), so no restore lost its pin to the new steps.

**For the orchestrator, when it enables the queue.** Set merge method MERGE: the `HEAD^2` reads above refuse anything else rather than guess. Put the queue on its own ruleset, or on `main-protect` 22628467, and leave `main-protect-checks` 23698884 with its required contexts and review rule and no new bypass. Until stage 1 and this branch are both on `main`, a queue entry waits on contexts its base cannot produce.

_Requested by **tvofi**_

## Head

`b7ea3bd28c718b6844575c70ec1d234cc90e84fe` (code): the merge of `origin/main` at `8a0ca90ab2b948236424a4346abe7682b5760500` (#1824, #1829, #1831) into the pull-request head `283accde`. That head is `e0fca1fa` (the clean merge of `d536fb4d`, #1823, into `f88438dd`, which was cut from stage 1's `c5102ea7`) plus `docs/delivery/1832.md`. Only `tests/entities.py` conflicted: #1824's coverage-cache check and this branch's merge-queue check were inserted at the same place, and both are kept, the queue check first. `tests.yml` (#1824) and `governance.yml` (#1829) changed on both sides and merged without conflict.

## Mutation proof

- `fast`'s `if:` without its `merge_group` arm → `tests/entities.py`: `FAIL every required context runs on a merge-queue entry (process review item 2)  [17 context(s); ["fast (3.14): tests.yml's fast does not run on merge_group"]]`.
- `validate.yml` without `merge_group` → the same check: `['validate-hacs: validate.yml does not list merge_group']`.
- `pr-contract.yml` `PINNED` with its operands swapped, a form not on `PINNED_OK` → `codeowners_gap.py --check` rc 1, `uncovered_files=8` (`policy_lint.mjs`, `prepr.sh` and six more), `pinned_by_base_restore=18`.
- `pr-contract.yml`'s new step writing `$GITHUB_ENV` instead of `$GITHUB_OUTPUT` → the same eight uncovered, rc 1.

## Null control

On this head `tests/entities.py` passes, and so do `codeowners_gap.py --check`, `prepr.sh --self-test`, `field_coverage.mjs`, `policy_lint.mjs`, `brief_lint.mjs`, `rules_sync.mjs --check`, `tests/structure.py` and `tools/audit/round4/D11/untrusted_text.py` (`shell_interpolations_freetext=0`). The new entity check carries its own null: `tests.yml` with only `pull_request` in `on` must be refused for exactly the contexts `tests.yml` produces.

## Figures

none

## Red checks

none: CI has not run on this head. Unrun here: the full gate (`MODE: FULL`, `tests.yml` changes), typing and real-HA `ha_contract` (no Python 3.14.2 in the cloud seat). No `merge_group` run can happen until the queue is enabled, so the queue path is first exercised by the first entry after that. The failure modes it can show are the fail-closed steps above.

## Forward-carry

none: the one constraint on a later stage, merge method MERGE, is refused by the workflows themselves (no second parent fails the step), so no seat has to carry it.

## Friction

none
