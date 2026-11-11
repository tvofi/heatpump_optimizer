Fix review: merge 6d347c73a517288142990b1481b4bde4bfcd64b7

bus-nonce: 4f0556495b736a5f294a83f6af74a462

Round: first review of this head. Record PR (roster state and triage records only); mutation proof n/a, no production or test code.

## Evidence
- RESULT head measured: 6d347c73a517288142990b1481b4bde4bfcd64b7, the head named by the body's `## Head` (merge of snapshot 7696a3ba07 with main plus the delivery row).
- RESULT packet refusal `handoff-not-applied` (tip c959bacd is not an ancestor of the head) is the expected P564 snapshot advisory: 7696a3ba07 is an ancestor of both the head and the roster tip, and `dev/programme/rosters` plus `dev/programme/triage` are byte-identical between snapshot and head (roster blob 9b11beb482, same at both).
- RESULT scope: 23 files in the three-dot diff = the 22 of the body plus `dev/programme/delivery/3377.md`; all under dev/programme/rosters, triage or delivery. No VERSION, manifest or RELEASE_NOTES change; no tests/, tools/ or .github/ change.
- RESULT groups `342 437 95 0 55` (main-base, head, added, removed, changed) re-derived at the merge base 5bc009bc82; roster numstat `5372 531`; 951 non-merge commits and 1 merge in origin/main..snapshot: all match the body.
- Not re-derived exactly: the carry totals. My count by `len(entry.get("carry", []))` is 1337 -> 1734 (the literal `entry["carry"]` raises KeyError on 5 base and 6 head entries); the body says 1338 -> 1735. The delta, 397, agrees; the off-by-one is in the body's counting rule, not in the roster, and no gate reads it.
- RESULT `git merge-tree --write-tree origin/main <head>`: exit 0, no conflict.
- RESULT `node tools/policy/brief_lint.mjs` at the head: 0 errors, 0 warnings.
- RESULT `merge_train.py classify`: GREEN, pending none, red none (the packet's in-progress `pr-contract` concluded green).
- carry_audit at the head: 0 findings, 0 unrouted. Body's Forward-carry and Friction are none; no finding changes a later stage.
- Red checks: the body's account concerns earlier heads; this head has no red check, so no `## Red checks` answer is owed.
