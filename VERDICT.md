Fix review: merge 9da3cb7f85e372971d4ed6425dc1030b7cc2ecf1

bus-nonce: af14fa00dde41764aed62890a40276ee

## Scope

Round 1 review of #2788 (record lane, no group, autofix branch record/autofix) at head 9da3cb7f85e372971d4ed6425dc1030b7cc2ecf1, three-dot against origin/main 8a11b8bdd6bfdca0b5f6bd356638fad2b234525f (merge base 1afbbceaea843b2c7ffe914e1aa9b7172cbc0161, which is the PR's base SHA).

## Evidence

- Diff is six files, all dev/programme/delivery/*.md: 2756.md, 2758.md, 2779.md, 2782.md, 2786.md (one line each, open -> merged) and a new 2788.md. No other file is touched, so VERSION, the manifest and the RELEASE_NOTES heading are untouched (ev/diff_and_ancestry.txt).
- Each flipped row names the right merge commit, and each one is an ancestor of origin/main: #2756 6939389, #2758 9082f26, #2779 c01d54b, #2782 cc9d584, #2786 1afbbce. Each commit's subject is "Merge pull request #<N>" for the matching N. No open PR's row was flipped to merged.
- 2786.md's subject now reads like the merge commit body ("record: delivery rows for #2692 ... #2781 (autofix)"). The other four drop the duplicated trailing group tag and add a final period. All are status updates, with no change in substance.
- dev/programme/delivery/2788.md exists, is one line, anchors #2788 and says **open**, which matches the live PR state (open, not merged).
- git merge-tree --write-tree origin/main 9da3cb7f85e372971d4ed6425dc1030b7cc2ecf1 exits 0 (tree ab18ca754fa0a9b0a91398ecddf072d0f84186bb). There is no conflict and no claim-file involvement.
- Both commits are by hpo-author[bot] with the message "ci: record delivery rows". Neither has a trailer or footer.
- Mutation proof and null control are n/a, as the body states: no production, test or check line changed, so there is no mutant to draw.
- tests/delivery_status.py at the head prints: DELIVERY STATUS OK — 137 rowed, 1 pending, 0 overdue. The pending one is #2765, which merged on main after this head's base. node tools/policy/policy_lint.mjs --record --since 1afbbce^1 reports its only error for #2765, whose row is already on main as open (ev/record_checks.txt). Neither is introduced by this diff.
- CI on the head, read from the check-runs API at review time (46 runs): no run concluded failure. The rest succeeded or were skipped, and governance / delivery-status, tests / nightly-status and tests / mutation are all success. Three runs were still in progress: governance / instrument-self-tests and two prelude jobs. The body's Red checks section answers record, nightly-status and delivery-status by name, so step 11 is satisfied with no red to answer.
- Not re-derived: tools/audit/seat/record_row.py --automerge-check. From this container it fails with HTTP 404 on its API call, so the automerge predicate at this head is unverified by me.
- The body's Head section names 9da3cb7f85e372971d4ed6425dc1030b7cc2ecf1, which is the head I measured.

## Findings

- #2765 merged onto main (8a11b8b) after this beat's base. Its row dev/programme/delivery/2765.md still says open, and policy_lint --record flags it. That is owed by the next record beat, not by this diff. Carry: dismissed: drained by the next record/autofix batch; outside this PR's computed window
