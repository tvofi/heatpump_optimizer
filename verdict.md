Fix review: merge 18850191756612458a8a83d581789e04c25802fb

bus-nonce: e85597ef757f25d2ded08b12a0da55b7

## Evidence
- Head reviewed: 18850191756612458a8a83d581789e04c25802fb (ev/HEAD.txt). Three-dot diff: 5 policy files plus dev/programme/delivery/3330.md; VERSION, manifest and RELEASE_NOTES.md untouched.
- `node tools/policy/rules_sync.mjs --check`: RULES-SYNC ok, so the .claude and .cursor copies match the canonical rule.
- `git merge-tree --write-tree origin/main HEAD` gave a tree (74edb33d...) with no conflict.
- Consistency grep of dev/governance and .claude/rules for own-group/never-the-fixer-own: the three new statements agree. finding-propagation.md says a carry never routes to the fixer's own owner. fixer.md allows `Carry: <own group>` only for a pending owner or orchestrator ruling, or a split part the approved plan names. fix-review.md blocks an own-group Carry naming neither exception as `carry-missing: own-group`. No other file contradicts them.
- The deleted closing line of fix-review.md ("A ruling naming a destination stage states it as a Carry: marker") is covered by the Enforcement section of finding-propagation.md: "Every finding a body or a Fix review: verdict records names its destination ... Carry: <GROUP>|#<issue>|O<n>|dismissed", enforced by carry_audit.py. Accepted as ruled.
- The new rule is the sentence "A carry routes to another stage or seam's owner, never the fixer's own", plus the exception sentence in fixer.md. No lint or check is claimed, so no both-ends demonstration is owed. Enforcement is the fix-review class `carry-missing: own-group`, which is review-time only; that is stated in the diff.
- CI: the packet's refusal `required-red gate` comes from the two early gate runs at 13:35 and 13:47. Their log says "FAIL run(s) ... still being judged; their gate decides". The latest gate run, id 128752585401 (13:59:51Z), concluded success; the run it waited on, 42485479472, completed success. All other non-skipped checks are success, including budget-raise-gate, arch-score, mutation and tests/*. ev/classify.txt shows merge_train.py classify exiting 1 (RED: gate) because it counts the superseded failed gate runs. I judge the head GREEN from the latest gate run and the finished judged run.
- carry_audit and figure_lint at the head found nothing to audit.

## Notes
- This is a policy change and needs the owner's approving review. The verdict covers soundness only.
- The diff also trims unrelated text: citations such as #2373, #1874, #1867 and #1868, and the "seven of nine carries" anecdote. In fixer.md it drops the "max_class_loc is a span: a docstring line costs what a code line does" sentence and shortens the "re-record them" wording. These look like corpus-size offsets for the added lines. They remove no rule obligation, but the owner should see them in the policy diff.
