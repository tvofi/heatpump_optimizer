Fix review: merge 3fbbb46f67f3905a804f458068fb3cf8a266e9e3

bus-nonce: ca0fbc7ccb3e0289d0c896aaa59a35e4

## Evidence
- Head measured: 3fbbb46f67f3905a804f458068fb3cf8a266e9e3, the PR head at read time. origin/main is 1148ee635, which the head already contains.
- Three-dot diff against the merge base: 2 files, +166, both new: `dev/programme/delivery/2980.md` and `dev/programme/triage/s6-batch64.md`. No production code, VERSION, manifest, RELEASE_NOTES or claim file is touched.
- `git merge-tree --write-tree origin/main 3fbbb46f67f3905a804f458068fb3cf8a266e9e3` exits 0 with tree 2ff52bac6 and no conflict.
- `carry_audit.py pr 2980` prints `CARRY-AUDIT #2980: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`. The routed item is f4edc070 from review 6516963008, dismissed in the body's "Review item routing" section.
- The body's "Head" section names 3fbbb46f67f3905a804f458068fb3cf8a266e9e3 and the authored code head 74ce3b18. The diff from 043b111d0 to 74ce3b18 is the one triage file, 165 insertions, as the body says. The body describes this head.
- Mutation proof, re-run here: `roster_edit.ruling_verdict` on the committed file returns ACCEPT for P293 and P294. With `Verdict: ACCEPT` changed to `Verdict: REJECT`, it returns REJECT for both. The ruling is therefore read by its consumer.
- RESULT: P293 and P294 ACCEPT/ACCEPT on the file; REJECT/REJECT on the mutant.
- CI from the check-runs API on this head: no red. `pr-contract / pr-contract` succeeded after the last push. Succeeded: `tests / fast (3.14)`, `tests / mutation`, `tests / coverage`, `governance / policy-docs`, `governance / delivery-status`, `governance / instrument-self-tests`, `arch-score`, `budget-raise-gate`. The `gate` roll-up was still running at read time.
- I did not re-derive the P293 sample counts (9 flagged, 7 under Evidence, 5 verdicts). They need the remote `verdict/<pr>` refs, and the body states the rule. The proposal's mechanics hold on the file's text, which I read in full. Round 1 of this record PR at this head; no fixer re-cut is owed.
- No finder's harness exists for a triage record; none is owed.
