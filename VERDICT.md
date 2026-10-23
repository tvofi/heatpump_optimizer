Fix review: merge fb8351f624a6cbc4602c22828892bc7ce25c52af

bus-nonce: 2bc0089477583c66bd0cd1840475b099

Review against the PR body. Roster ops only, no group. Round 1. Measured head fb8351f624a6cbc4602c22828892bc7ce25c52af, which was the PR head when I read it (REST pulls/2655). origin/main c6ef06684 equals the merge base.

RESULT diff-scope: three-dot diff of origin/main...head is 2 files, dev/programme/delivery/2655.md plus dev/programme/rosters/wave-r10-groups.json. The roster diff holds only the 4 batch-23 ops: R10-FLY-GH-READ-RETRY stage done at 57b7b4994 (an ancestor of origin/main), the P-H carry on R10-FLOW-ROSTER-FREEZE, new group R10-STRUCTURE-ALIAS with its one carry, and O19 dropped from R10-CURRENCY. No batch-22 carry is in the diff.
RESULT counts: groups 168 -> 169, 1 new (R10-STRUCTURE-ALIAS), 3 changed (R10-CURRENCY, R10-FLOW-ROSTER-FREEZE, R10-FLY-GH-READ-RETRY), 0 removed. Done 91 -> 92. The body's other stage figures also re-derive (in-progress 10 -> 9, not-started 60 -> 61, queued 6, absorbed 1). The one-new-group checks out: R10-STRUCTURE-ALIAS carries the O19 text dropped from R10-CURRENCY.
RESULT lints: brief_lint "TOTAL: 0 error(s) across 47 file(s)"; ref_privacy --check "0 refused"; carry_audit pr 2655 "0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)".
RESULT trailers: no commit in origin/main..head (including merge 462fece40 and the row commit) carries a Co-Authored-By, Generated, Claude or Signed-off line.
RESULT merge: git merge-tree --write-tree origin/main head exits 0 (tree 56180be41), no conflicts, no MERGE-CLAIM lines.
RESULT version: VERSION is untouched (the diff touches no other file).
RESULT mutation-proof: n/a. The diff holds no production or test code (JSON roster data plus a delivery row), so there is no line to delete and no budget, golden, claim or closure file moves (steps 4, 5, 14 are vacuous).
RESULT ci (one bulk check-runs read, 37 runs, taken after a 2 minute wait): no run is red or cancelled. Success includes pr-contract, briefs, budget-raise-gate, delivery-status, nightly-status, mutation, closure-scope, arch-score, policy-docs, wave-script and hassfest. Still pending at read time: fast (3.14), closures, env-matrix, instrument-self-tests (in progress) and lane-proofs (queued). The merge verdict assumes those finish non-red. No red check exists, so the body's "Red checks: none" is accurate and nothing is owed under step 11. nightly-status is green at this head. See ev/ci_nonpass.txt.
RESULT carry: the body names no forward-carry ("none"). The carries this PR writes are roster entries that carry_audit routes (0 unrouted).
Limits: the body's jq command was not re-run verbatim. I derived the same figures with my own python over the two roster files, so the counts rest on my definition (group-name keyed, full-object inequality for "changed"). The old/new group set and the done count agree with the body's figures.

ev/: HEAD.txt, counts.txt, lints.txt, body.txt, files.txt, ci_nonpass.txt, main_tip.txt.
