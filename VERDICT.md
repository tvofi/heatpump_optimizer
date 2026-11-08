Fix review: merge 04efeb4a8e175392acb0f780252ad177ccaef9ed

bus-nonce: 9460ffb3619ed1eb965fc852dab347d6

Round 3. This is a re-review of the same head, 04efeb4a8e175392acb0f780252ad177ccaef9ed. Round 2 blocked it with `ci-cancelled` because code run 42525346328 never concluded. That block is now settled, since CI on this head is GREEN. Merge base: daf8b349fd30cc60786eeca333a426b693aa4c5f. At verdict time, `ls-remote` shows the head unchanged on both the branch and refs/pull/3342/head (ev/ls-remote.txt).

## Findings

- Residual: the `if code == 0:` guard on the `gh issue list` read in `roster_invariants` survives my mutant R4, which replaces it with `if True:` (rc=0 fails=0, ev/reviewer_mutants.txt). The mutant is equivalent in practice. When gh exits non-zero, its output is error text, and `json.loads` raises ValueError, which already drops `--open-issues`. It differs only if gh exits non-zero while printing a valid JSON document, and gh does not do that. No test is owed. Carry: dismissed: equivalent mutant, the json.loads ValueError guard covers the same path

## Evidence

- CI: `merge_train.py classify 04efeb4a8e175392acb0f780252ad177ccaef9ed --pr 3342` returned `GREEN 04efeb4a8e175392acb0f780252ad177ccaef9ed pending: none red: none` with rc 0. It was run twice, once at the start and once before the verdict (ev/classify.txt). The packet digest shows gate success (id=128891603321), and pr-contract / pr-contract also succeeded (id=128886049840). This settles the round-2 block.
- Red checks (step 11): the only reds on this head's history were the gate jobs of run 42525346328, which was cancelled, and the two edit-run gate failures that waited on it. Round 2 established that none of these concluded `failure` on its own merits. The re-run is green. The body's `## Red checks: none` therefore stands, and no root-cause trigger is owed.
- Fixer's plants re-run at this head: `r10_roster_ops_mutants.py U1 U2 U3 U4 U5 U6 W18` gave U1 rc=1 fails=3; U2, U3, U4, U5, U6 and W18 each gave rc=1 fails=1. Summary line: `plants: 7, without a FAIL line: none` (ev/mutants_U.txt). These match the body's mutation-proof figures.
- My own mutants on `roster_invariants`, distinct from round 1's T1-T8 and round 2's T9-T12 (ev/reviewer_mutants.txt). Four were killed. R1 (wrong summary prefix) gave fails=4. R2 (`roster` subcommand dropped from argv) gave fails=2. R3 (rows filter matches nothing) gave fails=1. R5 (broken-invariant line not flagged) gave fails=1. R4 survives as an equivalent mutant; see Findings.
- Self-tests at the head, all 0 failed: orchestrator_tick 292 checks (5 rows more than round 1's 287), r10_roster_ops_mutants 343, roster_edit 243, roster_sync 96. Evidence is in ev/*_selftest.txt.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc 0 (ev/structure.txt). The diff touches no `*_budgets.json`.
- Merge check: `git merge-tree --write-tree origin/main 04efeb4a8e175392acb0f780252ad177ccaef9ed` returned rc 0 and tree 6f98277628f6a01f4442a0e0a5929011f7924a1b, with no conflict (ev/merge-tree.txt). origin/main is at 425b858495432c8dceb89d8d13866550352ba54f.
- Role contract is current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- VERSION, the manifest, RELEASE_NOTES.md and the budget files are all untouched in the three-dot diff. The diff touches 5 files.
- The head's merge-only delta is clean. `git diff 0cfccb706dc4 04efeb4a8e17` adds only dev/programme/delivery/3342.md. That means the figures the body re-measured at 0cfccb70 apply to this head.
- Not re-derived by me: the body's null control at e3d39d0d5c55 and the `closure.py select` MODE line. Round 2 re-ran that null control and recorded U1-U6 all at rc=0 fails=0. I did not run tests/entities.py at this head; round 2 recorded 2668 passed, and CI's gate is green.
- Carries 2-5 were delivered by #3250. Carries 6 and 8 wait on an orchestrator roster disposition, as the body states. The body's `## Forward-carry` section is none.
- Self-audit: `carry_audit.py check --body <PR body> --comments <this verdict>` returned `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`, rc 0. The body file was a copy I transcribed from the GitHub API read. It keeps every `Carry`-bearing line and section heading, and abridges the prose.
