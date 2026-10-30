Fix review: merge 5682d74e56315ec90ef394191170147111e35382

bus-nonce: fb47e5de2e4da878f5313999adeebafd

Re-issue of the round 10 merge verdict on PR #2925, same head 5682d74e56315ec90ef394191170147111e35382. The code is unchanged and the earlier verdict stands on the merits. This re-issue only changes the `Carry:` destinations so each one resolves under carry_audit.py.

## Findings

- review_packet.py render refuses host-path on a cloud seat (ref_privacy.Identity.of_host). The body already dispositions this. Carry: dismissed: no live roster group owns tools/audit/seat/ref_privacy.py and it bites only a cloud seat rendering a review packet
- The briefs, pr-contract and budget-raise-gate restoring jobs are not predicted by the graders arm of ci_predict.py. Carry: R10-FLY-CIPREDICT-RESTORING

## Evidence

- Head re-read at review time: the PR head is 5682d74e56315ec90ef394191170147111e35382 (ev/HEAD.txt).
- Delta since the last reviewed head 5a1d1e097 is one authored record commit (dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md, two lines) plus merges of main; the arm code under tools/pr/ci_predict.py, tools/policy and dev/audit/rca/prepr-head-graders is unchanged, so the earlier acceptance of the code carries.
- git merge-tree --write-tree origin/main head exits 0 with no conflict (ev/merge-tree.txt). VERSION, the manifest and RELEASE_NOTES are untouched by the branch.
- Commit messages in origin/main..head contain no Claude footer or trailer (ev/footer-count.txt prints 0).
- Check-runs API at this head: gate, pr-contract, budget-raise-gate, closure-scope, closures, coverage, fast (3.14), graders-head-copy, mutation, instrument-self-tests, arch-score, hassfest, hacs, typing, browser, codeql all success. tests / nightly-status is red; it is not a required check and does not block, it reads nothing this diff touches, and the body names it.
- The mutation figures (M1 to M5) and ci_predict --self-test were re-run in the earlier round; this re-issue did not re-run the mutants, per the brief the code is not in question.
- Review packet rendered at the head with no refusals and no advisories (ev/review-packet.md).
