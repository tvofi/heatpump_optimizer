Fix review: merge 7dc9e2ce475ede423f94c2fcbf9f228f90ca4d22

bus-nonce: e041c23cea79dd752482e90e3923ef33

Round 1, full review.

## Head

`7dc9e2ce475ede423f94c2fcbf9f228f90ca4d22` (PR head confirmed by ls-remote at post time; merge-tree against origin/main is clean, rc=0).

## Red checks

none. `merge_train.py classify` exits 0: `GREEN 7dc9e2ce475ede423f94c2fcbf9f228f90ca4d22 pending: none red: none`. The gate ran MODE: FULL (workflow files touched).

## Findings

none

## Evidence

- SHA pins: git ls-remote shows checkout v7.0.1, setup-python v7.1.0, setup-node v7.1.0, cache v6.1.0, upload-artifact v7.0.2 and download-artifact v8.0.2 each at the commented SHA. codeql-action 9b325408 is the commit of tags v4 and v4.39.1. hassfest 86d45647 is the head of master. No action was dropped or added. The v4 and master pins stay mutable by label, as before.
- Upstream notes: the bumps change nothing this repo uses. Nothing here uses setup-python pip-install (removed in 7.0.0), the setup-node NODE_AUTH_TOKEN dummy (removed in 7.0.0), or upload-artifact archive. The repo's inputs (python-version, node-version, key/path/restore-keys, name/path/pattern/retention-days/if-no-files-found, and checkout ref/fetch-depth/fetch-tags/persist-credentials/token) are unchanged.
- download-artifact v8 turns a digest mismatch into an error by default. That is a stricter fail-closed default and CI is green on it.
- checkout v7 blocks fork-PR checkouts under pull_request_target and workflow_run. dependabot-automerge checks out base.sha. gate-sweep and merge-main check out github.sha. None checks out a fork head.
- The runner requirement is Node 24 with runner 2.327.1 or later. All jobs run on GitHub-hosted ubuntu runners.
- codeowners_gap --check at the head: uncovered_files=0 (ev/codeowners.txt).
- The tests/entities.py graders-head-copy literal equals the tests.yml graders-head-copy job (ev/canon-eq.txt: equal). Null control: changing one character of the checkout SHA in tests.yml gives DIFF. entities.py itself cannot run in this container (no homeassistant), so the CI tests check is the evidence for the full file.
- Supersession: #3087 is closed unmerged, and #3088 is closed with its content landed by #3147 (merged). The body claims only #3087.
- Delivery row dev/programme/delivery/3163.md is added and is the only dev/ change. No VERSION, manifest, RELEASE_NOTES, golden, claim-file, closures or budget change in the three-dot diff. No host path in added lines. Commit messages carry no footer or trailer.
- Not re-derived: the body's "ALL 2592 ENTITY CHECKS PASSED". I rely on green CI instead.
