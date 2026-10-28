Fix review: merge 6bee9961fa8bbb90d50392fee75a64ab88a3d8e2

bus-nonce: 53a94b8780c68537c4f9f363080130b1

Round 1. Reviewed head 6bee9961fa8bbb90d50392fee75a64ab88a3d8e2 (still the PR head when read). Roster-only diff: no production code, so no mutant exists (step 1 n/a).

## Findings

(none this PR leaves unsettled)

## Evidence

- RESULT jq enumeration (body's own command, run by me against origin/main de69745f and the head): nb=151 nh=154, removed=[], new=[R10-FLY-PRUNE-REFS, R10-NIGHTLY-ABSENT-NEW, R10-RCA-BODY-LINT], changed=20 groups, the same 20 names the body lists.
- RESULT stages main -> head: done 76->84, in-progress 8->15, not-started 60->49, queued 7->6: match the body.
- RESULT diffstat roster file 175 insertions / 32 deletions; 29 commits origin/main..ddd2e8de9; 33 to the head: match.
- RESULT per-group diff: the 8 done groups carry the commits the body names (5756f2b15, f35a5a373, 383bca2be, fea3d3ca6, 8a4c438e7, b980e2fa0, 1787ffd08, 008ad15bb), each an ancestor of origin/main; PR numbers 2620 (CURRENCY) and 2625 (RCA-BODY-LINT) present; carries ORCH-MACHINERY 35->45, ARCH-PLANNER 5->7, JIDOKA 5->6 (+2 added, the one decision-0012 carry dropped), DEPGRAPH-STALE 0->1, CI-LAYOUT-P2 7->8: all as stated. No field other than stage/commit/branch/pr/carry changed on any existing group.
- RESULT brief_lint on the roster at the head: TOTAL: 0 error(s) across 1 file(s).
- RESULT ref_privacy --check: 50 line(s) added since de69745f judged, 0 refused. grep for /Users/ and /private/tmp in the head roster: 0. Commit d0df7ed3b is known and not blocking; the head tree is clean.
- RESULT merge-tree --write-tree origin/main head: rc 0, no conflict, no MERGE-CLAIM lines.
- RESULT VERSION diff against origin/main: empty; the diff touches only the roster and delivery/2626.md.
- Null control: the body states the roster on main equals the merge base; origin/main is itself the merge base here (de69745f), so removed=[] holds.
- CI on the head, check-runs API (47 runs, both pages read): every required check success (pr-contract, instrument-self-tests, fast, closures, briefs, delivery-status, policy-docs, mutation, arch-score, budget-raise-gate); the rest skipped or neutral. The one failure, nightly-status, grades main's scheduled run and this diff does not reach what it reads; the body answers it. instrument-self-tests, red at d0df7ed3b, is answered in the body and green at this head.
- Forward-carry: the body states none; the carries it records are in the roster itself, with their preconditions in the destination groups' carry arrays (checked present above).
- The brief's finder harness for this group is the roster lint plus the body's own jq enumeration, which I ran independently. A body figure I could not re-derive: none.
