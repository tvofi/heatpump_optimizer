Fix review: merge dcac89f02dbd3db8e2e3469adb4377e2630609ae

bus-nonce: c8c69dee0bfa69fc98bfd39250fa540e

## Scope

Round 2 over reviewed head 57ccfef48d3ee990176bb672515ab12c8d1315f4. review_packet.py reads `Review scope: full` (no verdict names the reviewed head), so the whole three-dot diff was reviewed: README.md link, new ROADMAP.md, dev/audit/config/scopes.json (D6 universe and seat s1), D6 claims C108 count 92 -> 93, tests/closure.py INERT entry, tests/layout.json entry, delivery record. No custom_components/ line changes; no production delta to widen into. The delta since the reviewed head is only the scopes.json repair (05b21ff004) and its merge (dcac89f02d).

## Evidence

- Head reviewed: dcac89f02dbd3db8e2e3469adb4377e2630609ae (ev/HEAD.txt); the PR body's `## Head` names it.
- Merge with main: `git merge-tree --write-tree origin/main dcac89f02d` exits 0 against origin/main e352724335 (ev/merge-tree.txt).
- Mutation proof: n/a, no production line; the mutation of the scopes.json entry is its removal, run as the null control below.
- Null control re-run independently, both ends: at the head with scopes.json reverted to the merge base, `check_scopes.py --repo . --self-test` prints `FAIL D6 ...` / `classified in neither universe nor static: ROADMAP.md` and `SELF-TEST FAILED`, rc=1 (ev/check_scopes-null.txt); at the head unchanged it prints `SELF-TEST passed (every perturbed scope refused)`, rc=0 (ev/check_scopes-head.txt). Matches the body.
- Figure C108 "93 links": re-derived by running `PYTHONPATH=tests/hastub python3 dev/audit/rounds/round4/D6/claims.py` at the head; it rewrites claims.json and claims.md and the tree stayed clean, so the committed 93 is what the instrument derives; 125 claims, 0 false, 2 unverifiable (C109, C111, unchanged from base) (ev/claims-head.txt). The README's new link to ROADMAP.md accounts for the +1, and ROADMAP.md's links (README.md, README.md#known-limitations at README.md:258) resolve.
- Figure `MODE: FULL`, reason `tests/closure.py changes the gate itself`: reproduced (ev/closure-select.txt).
- Figure 98.6 s self-test wall time: a container timing, not re-derived; mine ran in the same order of magnitude concurrently with a second run.
- VERSION, manifest version and RELEASE_NOTES.md heading untouched against the merge base.
- INERT entry for ROADMAP.md (step 14): `git grep ROADMAP` finds no gate script reading the file beyond tests/layout.json's listing and closure.py's INERT tuple; the entry is earned by the file being prose.
- Owed reds: `merge_train.py owed-reds` (ev/owed-reds.txt) does not contain `tests / nightly-status`, so its red is not owed. The earlier `governance / instrument-self-tests` red (check_scopes self-test on ROADMAP.md) is answered in the body's `## Red checks` with a named cheaper detector and standing cost; it reads success at this head.
- CI: `merge_train.py classify dcac89f02d --pr 3630` exited 0: `GREEN dcac89f02dbd3db8e2e3469adb4377e2630609ae pending: none red: none` (ev/classify.log). `tests / nightly-status` reads failure at this head and is outside owed-reds.

## Findings

- Follow-up: the cheaper detector the body names for the instrument-self-tests red (run `check_scopes.py --self-test` in prepr.sh when a diff adds a file matching a dimension's classify globs) is unbuilt, and #3628 is a second instance of the same miss; at two instances it is below the audit-class trigger, and the body records the answer the rule asks for. Carry: dismissed: answered in this PR body's Red checks per defect-root-cause.md; a third instance makes it a root-cause seat's class
