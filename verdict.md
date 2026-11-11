Fix review: merge 04a1f28c14cb79f61b62cfdc3c4165d1cc8204e4

bus-nonce: 3e46e01b344de69251d57c8111065b9a

Round 2 (rereview of the blocked verdict at f4532701, mutation-survivor), at the handoff tip. No pull request exists yet, so there is no review packet and no CI to wait on. The delta f4532701..04a1f28c1 is tests/entities.py only (+16/-2); production code (custom_components/) is untouched.

## Evidence

- RESULT head: handoff/r10-codeql-pr-paths = 04a1f28c14cb79f61b62cfdc3c4165d1cc8204e4, same as the body's `## Head` (ev/HEAD.txt). Three-dot diff from the merge base is .github/workflows/codeql.yml and tests/entities.py only; VERSION, the manifest, RELEASE_NOTES.md and the claim files are untouched.
- RESULT merge: `git merge-tree --write-tree origin/main <head>` rc=0 (ev/merge-tree.txt). The commits since f4532701 carry no Claude footer, Co-Authored-By or session link.
- RESULT null control M0 (unmutated head): full `PYTHONPATH=tests/hastub python3 tests/entities.py` rc=0, the codeql check prints `ok` (ev/entities-M0.txt line 2098).
- RESULT the two named survivors are now killed: M2 (guard negated) FAIL, M3 (guard `|| true`) FAIL.
- RESULT whole mutation set, 12 mutants of codeql.yml plus M0, all killed, none survives (ev/mut.py defines them, ev/mutant-M*.diff are the diffs): M1 drop the python condition, M2 negate guard, M3 `|| true`, M4 event `push` in the guard, M5 swap the PR and base lists, M6 `||` to `&&` between the lists, M7 drop `dev/**` from the PR list, M8 PR list as the fallback (main's push gets tests/dev), M9 event `!= 'pull_request'`, M10 language `!= 'python'`, M11 add a third entry to the PR list, M12 widen the guard to merge_group. M0 PASS, M1..M12 FAIL.
- Instrument disclosure: the mutants M1..M12 were scored by ev/fast_codeql_check.py, the reviewer's harness, which exec's the check's own lines of tests/entities.py verbatim (the yaml read, the config extraction and the new `_CODEQL_SHAPE`/`_CODEQL_SELECTED`/`_CODEQL_EXPECT` and check) and skips only the unrelated node-parse lines. It is not a whole-suite run: one full `entities.py` pass takes longer than a background window, so only M0 (the null control) ran in full, and an attempted full run of the whole set was stopped at its time limit. Each FAIL there is the check's own False (result `[False]`), not an exec error.
- RESULT claim shape: the new check anchors `paths-ignore: ${{ (<GUARD>) && '<PR>' || '<BASE>' }}` with `re.fullmatch` and evaluates it over push, pull_request, merge_group, workflow_dispatch x actions, javascript-typescript, python against the expected map, so only pull_request on python selects the tests/dev list. This is the fix the prior block asked for.
- Red checks: none owed by this branch. `merge_train.py owed-reds` (ev/owed-reds.txt) lists `tests / fast (3.14)` among required contexts, but its combi-census red (PR #3466) and `governance / instrument-self-tests` (R10-HOTFIX-PUSHER-CENSUS) are main's own, not raised by this diff (codeql.yml and one tests/entities.py check), so neither is answered here and neither blocks. No PR or CI run exists at this head.
- Figures I could not re-derive: the 2173-3623 s and 48-104 s job times, and the alert-view behaviour under the shared category; both need authenticated CI runs, which this seat does not have. Prior round's finding on them is unchanged.
- Forward-carry: the body states none, and the change constrains no later stage.

## Findings

- Follow-up: the python leg's before/after job seconds and whether ignored-path alerts read as fixed under the shared category stay unmeasured until the first PR run; the body routes both to the orchestrator. Carry: dismissed: the body already routes both to the orchestrator with the command to run; this verdict adds nothing to them
