Fix review: merge 0884509a04003457eea9ae5d2777941ba9d00fe2

bus-nonce: 9239e9d808d6d422e49613ca3f6ec138

## Evidence
- Scoped re-check only. The PR body now gives every Forward-carry item a `Carry: dismissed:` destination (A and B: proposals for the owner; shape 2: delivered by #3409). The packet's carry_audit reports 3 routed, 0 unrouted, 0 bad destinations.
- The dismissal is true. #3409's merge 0c868b7d is an ancestor of origin/main. It changed `tools/audit/seat/ref_privacy.py` (shape 2's `added_lines` instance) and `tools/audit/seat/beatd.py` (the timing-dependent read set), and re-recorded `selftest_closures.json` (ev/3409.txt).
- Code and RCA record are unchanged. The three-dot diff is two files: the RCA document and the delivery row (ev/diffstat.txt). The body says the code head 3f607ba9 is unchanged.
- Merge with origin/main: `git merge-tree --write-tree` returned a tree with no conflict.
- CI: `merge_train.py classify` at this head exits 0, GREEN (ev/classify.txt). The packet showed `governance / instrument-self-tests` red; it is not a required context and is not in the owed-reds output for #3410. The body's `## Red checks` is `none`.
- Analysis not re-reviewed, per the brief.
