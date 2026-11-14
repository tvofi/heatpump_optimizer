Fix review: merge 18850191756612458a8a83d581789e04c25802fb

bus-nonce: c3e016cd5213a4cbd23bdf4a27e88709

Round 1 (sonnet), policy PR: verdict is on soundness; the merge needs tvofi's approving review.

## Evidence
- RESULT rules_sync --check: ok, mirrors match canonical (ev/rules_sync.txt).
- RESULT merge-tree origin/main vs head: clean, no conflict (ev/merge-tree.txt).
- RESULT classify at this head: GREEN, pending none, red none, rc=0.
- Contradiction grep (own group, own-group, Carry: across dev/governance and rules): only the three new sentences (fixer.md:296, fix-review.md:45, finding-propagation.md) mention own-group carries; they agree: exceptions are a pending owner/orchestrator ruling or a split part named by the approved plan; fix-review blocks as carry-missing: own-group. finding-propagation's destinations list does not contradict (sibling seam goes to a new issue or carry file).
- Wording: each new sentence is one unwrapped logical unit and states a checkable condition; no automated check is claimed (body says none), so no both-ends demonstration is owed. check-wave-script green with carry-missing: own-group per body.
- Accepted deletion (fix-review.md closing line "A ruling naming a destination stage states it as a Carry: marker."): read finding-propagation.md Enforcement; "Every finding a body or a Fix review verdict records names its destination ... ends Carry: <GROUP>|#<issue>|O<n>|dismissed" with carry_audit.py refusing a missing marker. It covers verdict rulings; the claim holds.
- VERSION, manifest, RELEASE_NOTES.md untouched (three-dot diff: 6 files, all policy/mirror/delivery row).

## Findings
- Follow-up: the diff also deletes, unnamed in the body, the sentence "max_class_loc is a span: a docstring line costs what a code line does." from fixer.md, plus the "seven of nine carries once went missing" evidence in finding-propagation.md and several issue citations; the body calls these "spent prose". The max_class_loc sentence is operational (it tells a fixer what counts toward the metric) and appears nowhere else in dev/ or tools/; tvofi should confirm at approval that it is wanted gone, or restore it in a later pass when the fix-review brief cap allows. Carry: dismissed: owner decision at the approving review, body already asks for budget-driven deletions to be judged and the text is recoverable from history.
