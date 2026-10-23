Fix review: merge 5d874ec6309675a391f1a97acf6e5a77781d3f78

bus-nonce: f66fc55ed0212d5c21f240fc165081f4

Round 1 for this head. Roster-only batch (same shape as #2655, #2661, #2663). Role file current on main (empty roles diff).

## Findings

- The PR roster lags the handoff tip 6322452d: the handoff has since appended a P-Q carry to R10-FLOW-JIDOKA's group, changed its P-N carry, and moved R10-FLOW-JIDOKA to in-progress, none of which is in this head or in main. Nothing of main's is lost; the edits ride the next roster batch. Carry: R10-ROSTER-BATCH | #2667 | O1 | dismissed: handoff-only edits are not in main, so the merge loses nothing; the next batch lands them.

## Evidence

- Three-dot diff `12032c43...5d874ec6309675a391f1a97acf6e5a77781d3f78` touches only dev/programme/rosters/wave-r10-groups.json and dev/programme/delivery/2667.md.
- Classification of every changed group: R10-LOOP-CPU stage in-progress to done and commit 577ec62d to 7108101d (merge of #2632, an ancestor of origin/main); R10-CI-LAYOUT-P2 five appended carries (2662 review 1-5), nothing removed; R10-FLY-OPENPR-ATOMIC one appended carry (P-P); R10-FLY-NO-FOOTERS-EMITTERS one appended carry (2662 round 2); R10-FLY-RELAY-REVIEW-FF stage not-started to in-progress with resume.note and resume.next_step rewritten (each has its own set-resume commit); two new groups, R10-FLY-NO-FOOTERS-PUSH-PATHS and R10-FLY-INERT-LOAD-TIME (the latter has an edit-brief commit, but it is a brief on a group this same PR appends, so no existing brief is rewritten). No removed carry, no `after` change, no other brief rewrite.
- Null control: groups 169 before, 171 after, none removed, order of existing groups kept, other top-level keys byte-equal. origin/main equals the merge base, so nothing main wrote since the base can be lost.
- New group files: all but dev/audit/rca/R10-RCA-INERT-CLOSURE-RECORDING.md exist at origin/main; that one exists at e9d169b7, the ref the brief cites (handoff/r10-rca-inert-closure-recording, ls-remote confirms). R10-FLY-NO-FOOTERS-PUSH-PATHS files all exist at main.
- brief_lint on the roster: 0 errors, 0 warnings. merge-tree against origin/main exits 0 with a clean tree. VERSION untouched. The 23 commit bodies carry no Co-Authored-By, Claude, session or link text.
- Scoped gate: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` Two local scripts failed on a missing python module in this container, identically on origin/main (environmental, not the diff).
- CI read once from check-runs at the time of review (25 runs): pr-contract, scope, hassfest, validate-hacs, both budget-raise-gate runs, arch-score, cancel-superseded success; delivery-status-publish, record, kernel-points skipped; the rest (mutation, closure-scope, briefs, env-matrix, policy-docs, wave-script, instrument-self-tests, delivery-status, nightly-status, Analyze x3, arch-score) queued or in progress. No red check, so no root-cause answer owed. CI had not concluded when I read it; cited, not re-run.
- Not re-derivable by me: the head's pending runs; I did not re-run the heavy gate or mutation.
