R10-HOTFIX-RECORD-ATTRIB carry repair. #3194 fixed `record_row.py` (`attribute_merge`: empty `/commits/<sha>/pulls` answer -> number from the subject, confirmed against that pull request's `merge_commit_sha`). The one carry it left: `tools/policy/policy_lint.mjs` `fetchPullsBySha` recovered the number from the subject on an empty answer WITHOUT that confirmation. Now `confirmGapMerge` reads `/pulls/<n>` and requires `merge_commit_sha` equal to the sha; otherwise `fetchPullsBySha` returns `ok:false` with a reason, the loud UNCHECKED path the enumeration already has, not a silent trust. `stamp.py` rule 5 reads subjects only and needs no change (checked in #3194).

Alternatives: sharing the Python helper (JS cannot import it); dropping the unconfirmed commit silently (the silent-skip class the module refuses).

## Head

ee84d35a205f145e73b61f37d22d76e69d530de0, on origin/main 783d8dc72811ab75ae4ffca367456f44896f47d3 (unmoved since the prepr run, so no second run).

## Mutation proof

Predicate mutated: `confirmGapMerge`'s `Boolean(res.ok && res.data && res.data.merge_commit_sha === sha)` replaced by `true`. `node tools/policy/policy_lint.mjs --self-test` then prints `FIXTURE VACUOUS` naming "merged at a different commit was confirmed" and "could not be read was confirmed". Restored; self-test passes.

## Null control

Acceptance pins (in `assertAcceptance`, D13-s1-01 block) drive `confirmGapMerge` with a stub getter: matching `merge_commit_sha` -> confirmed (normal path); a differing merge commit -> refused; an unreadable pull request -> refused. The API-row path of `resolvePrFromCommit` is untouched and still pinned (`source api`).

## Figures

Pin count in the self-test's `FIXTURE ok` line: 260 at origin/main, 263 here (three added pins). Command: `node tools/policy/policy_lint.mjs --self-test | grep 'FIXTURE ok'`.
Checks: `tools/pr/prepr.sh` rc=0; `tests/entities.py` 2611 checks passed; `tests/structure.py` passed. Gate: `MODE: SCOPED -- 1 script(s) run` (`tests/entities.py`). Toolchain: numpy 2.5.4, scipy 1.18.1 match `tests/requirements-ci.txt`; no golden touched.

## Red checks

none

## Forward-carry

none

## Friction

none
