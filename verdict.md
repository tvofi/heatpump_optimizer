Fix review: merge d538f2daff18ad39520b75eab718044da461b9c6

bus-nonce: 7e2695dee6e20f695638b953443e153c

## Round

Round 2. Measured head d538f2daff18ad39520b75eab718044da461b9c6, unchanged since round 1 (`git ls-remote` shows it still the PR head). Round 1 blocked on carry-missing only. Round-1 points are not re-litigated.

## Findings

- Survivor T4 from round 1 (train.sh `--no-mandate` branch replaceable by a no-op with the self-test green; a one-line arm `--mandate 7 --no-mandate` passes no `--mandate` would pin it) is still open. The head did not move, so no arm was added. Carry: R10-FLY-TRAIN-DEFAULTS
- Part 2 of R10-FLY-TRAIN-DEFAULTS (the folded R10-FLOW-POSTMERGE after-merge bookkeeping in merge_pr.sh and merge_train.py) is owed. When this PR merges, the roster row must stay open for part 2 (not flip to done). Carry: R10-FLY-TRAIN-DEFAULTS
- Approval: standing-merge.md is policy and merge_train.py and train.sh are code-owned, so tvofi's approving review comes at merge. Flagged, not blocked. Carry: dismissed: the owner's review at merge is the code-owner rule, not a defect in this change

## Evidence

- RESULT carry_audit.py pr 3010: "1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)", item 227dd906 routed to R10-FLY-TRAIN-DEFAULTS (ev/carry_audit.txt). The packet at the head reads the same.
- RESULT destination group: R10-FLY-TRAIN-DEFAULTS exists in the roster (handoff/audit-r10-roster, wave 6) with resume.stage in-progress, branch handoff/r10-fly-train-defaults, pr 3010. It is not done. Its carry text already holds the folded R10-FLOW-POSTMERGE brief, "owed in the same pull request". R10-FLOW-POSTMERGE itself shows stage done in that roster file, which fits the fold.
- RESULT body diff, round 1 against live. The round-1 body is rebuilt from ref handoff-body/r10-fly-train-defaults plus the sentences round 1's verdict quoted, since the earlier PR text is not retrievable (ev/body_round1_handoff-body.md; the live sections I compared are in ev/body_live_partial.md). The opening, Mutation proof, Null control, Figures and Red checks sections are identical. Friction and Approval are the same text as far as I can tell; the live ones were not copied to a file, so that is by reading. Changed: (1) the end of the Roster carry paragraph, where "The orchestrator either re-dispatches ... treat it as open" became the orchestrator's disposition under mandate 6329234399 (owed by part 2, a later PR in the same group); (2) the Head section now describes the added delivery-row commit and the d3950e8d merge; (3) Forward-carry went from "none" to the one line ending "Carry: R10-FLY-TRAIN-DEFAULTS". Nothing else moved. No figure changed.
- RESULT cheap re-runs at the head: train.sh --self-test ok rc=0, bare launch set --overlap|--approval-carry|--skip-bad|--free-holders|--bot-prs|--pre-flight; merge_train.py --self-test 381 checks, 0 failed, matching the body (ev/train_selftest.txt, ev/merge_train_selftest.txt).
- RESULT git merge-tree --write-tree origin/main(437f1ba9b) d538f2daff18ad39520b75eab718044da461b9c6 exits 0, tree 03df4e690: no conflict, no MERGE-CLAIM lines (ev/merge_tree.txt). origin/main moved from a9ba3022e at round 1.
- RESULT CI from the check-runs API: 68 runs on the head across its workflow runs, none red (success or skipped). gate, pr-contract (latest run 124298188191 started after the last other run concluded), governance/policy-docs, tests/mutation, tests/closures and arch-score are all success. The body's one past red (policy-docs at an earlier tree) is answered in Red checks and is green here.
- RESULT VERSION, the manifest and RELEASE_NOTES: the three-dot diff (6 files) touches none.
- Round-1 mutation, null-control and class results are not re-run; the head is byte-identical.
