R10-HOTFIX-RECORD-ATTRIB. `/commits/616868bdc5ca/pulls` answers `[]` for #3179's merge commit, so `record_row.py` `enumerate_merges` refused the window and Nightly record-autofix went red on every main push. One helper, `attribute_merge`, now reads the map; on an empty answer it takes the number from the commit's subject and confirms that pull request's `merge_commit_sha` equals the sha. Otherwise it still refuses.

## Head

1063cb1af6dacc0c14f0f49eb915adf4e8525cdb, on origin/main 8e90d81443317f76f22602a89651f7ca17c633f9 (unmoved since the last prepr run, so no second run).

## Mutation proof

Predicate mutated: the `merge_commit_sha == sha` confirmation in `attribute_merge` replaced by `isinstance(pull, dict)`. `python3 tools/audit/seat/record_row.py --self-test` then fails: `attribute_merge: empty map, subject's PR merged elsewhere -> refuses`. Restored; the self-test passes.

## Null control

Normal path unchanged: the map answers with a matching `merge_commit_sha`, so one read and no second (self-test: `attribute_merge: map answers -> unchanged, no second read (null)`). An empty map with a subject naming a PR whose merge commit differs refuses, and so does a subject naming no PR. At the merge base, `enumerate_merges` raised `Refuse` on the empty map.

## Figures

none

Carry 1 (check every other reader of the endpoint and route them through one helper): done, listed below.

Readers of `/commits/<sha>/pulls` (enumerated with `grep -rn "commits/.*pulls" tools .github tests`):
- `tools/audit/seat/record_row.py` `enumerate_merges`: now routed through `attribute_merge`, the only reader in the module.
- `tools/release/stamp.py`: no read of the endpoint. Rule 5 reads subjects through `pr_from_subject`, so it needs no change.
- `tools/policy/policy_lint.mjs` `fetchPullsBySha`/`resolvePrFromCommit`: already falls back to the subject on an empty answer (D13-s1-01), without the mergeCommit confirmation. Left alone: it is JavaScript and cannot share the Python helper, and no red is attributed to it.
- `tools/policy/record-predicate/sweep.mjs`: a diagnostic sweep only.
- Other hits are under `dev/audit` (historical evidence) or comments.

Checks run: `PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh` rc=0, `tests/entities.py`, `tests/structure.py` passed.

## Red checks

none

## Forward-carry

none

## Friction

none
