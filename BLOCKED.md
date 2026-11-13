# BLOCKED: r10-closeout-prep-p2 repair round 2

Question: the ruling's option (a) has `tests/entities.py`'s #2227 cited-program arm read carry text from the `carry` lists of the newest roster in the TREE. The tree's roster at this head does not yet hold the re-homed carry-201 entries 0, 1, 3, 4 and 6. Constraint 1 makes landing them the orchestrator's step: will the orchestrator land roster commit d17111784fd84306a83ba28224c9c507fab6b614 ("roster_edit batch of 33", on handoff/audit-r10-roster) on main, so a round-3 seat can merge origin/main and build the arm against it?

## The precondition, measured

The reader is a short Python script over `git show <ref>:dev/programme/rosters/wave-r10-groups.json`. It takes group `R11-INTAKE-R10-RESIDUE` from the top-level `groups` list and collects N from every `carry` string that matches `carry-201 entry (\d+) \(file removed\)`.

- origin/main c7f2fe4270a9f106c640fb1258123034f9046c21: `git diff --quiet origin/main HEAD -- dev/programme/rosters/` exits 0, so the head's roster is main's. That reader finds carry-201 entries `[]` in R11-INTAKE-R10-RESIDUE (has 0,1,3,4,6: False).
- d17111784f: entries [0..12, 14..17, 19..21, 23, 24] (has 0,1,3,4,6: True). `git log -S'carry-201 entry 0 (file removed)'` over handoff/audit-r10-roster names this commit as the one that adds them.
- Roster tip 5db6c975a7159f0a59341ceb2a0ddb448e2ad046: same entries (True). d17111784f is its ancestor. `git merge-base --is-ancestor d17111784f origin/main` fails, so the commit is not on main. 133 roster-branch commits are not on main.

Landing d17111784f or any later roster-branch tip satisfies the precondition. Per the brief, the roster file was not copied into this branch.

## Not done this round

- The arm change is not committed. The planned shape: load `tools/audit/seat/roster_lib.py`, take `roster_path(".")` and `groups_of(...)`, and append each group's string `carry` entries to `_SP_REMEASURES`, named `<roster>#<group>[i]`, and to `_SP_CARRIES`. The floors stay unchanged. Without the roster commit on main it cannot be shown green at a head, so no proof was attempted.
- No mutant run, ci_predict, brief_lint, carry_audit, prepr.sh or body. The tree is still round 1's db5861c0ae (carry-1645 answered_by = 16e8fef927; carry-201 entry 22 restored; legacy-control list edit), and it descends from b560375dbd.
- This seat hit the frugal inline-operation guard (5 per prompt) before it could draft the arm. It did not set FRUGAL_ALLOW_INLINE.
