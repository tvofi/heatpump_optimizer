Fix review: merge 54ee10354d8f199a61b2dc18b3c8276aec73f4e6

bus-nonce: b47e28f796266683f618e3cbeff328bb

## Round

Round 1 (first review of #2744).

## Findings

None.

## Evidence

- Head reviewed: 54ee10354d8f199a61b2dc18b3c8276aec73f4e6 (ev/HEAD.txt), the head the PR body names under ## Head. Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- Diff (three-dot from merge base c686fe366): two added files, dev/programme/triage/s6-batch9.md (24 lines) and dev/programme/delivery/2744.md (1 line). Both sit under dev/programme/, on tests/closure.py's INERT list (line 273). VERSION, the manifest and RELEASE_NOTES.md are untouched. Neither claim file changes.
- Merge: `git merge-tree --write-tree origin/main <head>` with origin/main at 806aa2ce8 exits 0, so there is no conflict (ev/merge_tree.txt).
- Mutation proof (step 1): the body says n/a because no code or check line changes. That holds: the diff writes no production line, so no mutant can be drawn.
- RESULT ruling_verdict at head: P77 REJECT, P78 ACCEPT, P99 None. This reproduces the body's null control (ev/ruling_verdict.txt). The figure "1 ACCEPT, 1 REJECT" agrees.
- RESULT P78 names a live roster group: R10-FLOW-JIDOKA is in dev/programme/rosters/wave-r10-groups.json at handoff/audit-r10-roster bae86879d28d. Its resume.stage is in-progress, not done; it has 16 carries and files tools/pr/prepr.sh. The 2026-10-22 ref_privacy carry and the owner's quick-checks-only ruling that P78 cites are both among its carries (ev/roster.txt).
- RESULT P78 carry text passes brief_lint: tools/policy/brief_lint.mjs from a fresh origin/main checkout (806aa2ce8) returns 0 errors and 0 warnings with the carry text linted as the group's brief (ev/lint_carry_asbrief.txt). Null control: the same text with one path changed to tools/audit/seat/ref_privacyX.py returns 1 error, path not in the tree (ev/lint_carry_asbrief_plant.txt). So the linter does read this text. Linting the whole roster with the carry appended to the group's carry list also gives 0 errors (ev/lint_before.txt, ev/lint_after.txt). However, brief_lint does not cite-check roster carry-list entries: the same planted path there also gave 0 errors (ev/lint_carrylist_planted.txt). That is why the brief-shaped run above is the check that carries weight.
- RESULT figures re-derived at head: the cloud_relay.sh `wc -l < ... | tr -d ' '` grep gives 11 sites. `$(wc -l` under tools gives 48 lines in 12 files. `git grep -c ref_privacy -- tools/pr/prepr.sh` gives 0 matches (exit 1). The ref_privacy.py header at line 91 carries the quoted sentence. All of these match the body. At 73b69fe0a the two grep counts are the same (48, 11).
- I could not re-derive the P78 figure "98 line(s) added since 73b69fe0a9fa judged, 0.56 s" as stated. It was measured on the fixer's tree at that base. I measured ref_privacy --check at this head: 25 lines judged since c686fe3668b2, 0 refused, 0.34 s wall (ev/ref_privacy_head.txt). At 73b69fe0a itself: 3 lines judged, 0.28 s (ev/ref_privacy_73b69.txt). The order of magnitude (under 1 s) holds. The three CI job ids for #2735, #2738 and #2741 are the filing's own figures, and I did not re-derive them.
- Host paths: none in the batch file (a grep for absolute home, Users and tmp prefixes is empty), and ref_privacy --check at head refuses 0.
- CI at head (check-runs API, 44 runs): no run is red. pr-contract, budget-raise-gate, arch-score, briefs, mutation, closure-scope, policy-docs, instrument-self-tests, env-matrix, wave-script, delivery-status, nightly-status, hassfest, validate-hacs and codeql are success. When I read them, gate, tests/typing, tests/closures, tests/coverage, tests/browser and tests/fast (3.14) were still queued or in progress. No red check is owed an answer (## Red checks: none is accurate so far).
- Forward-carry: the body routes the P78 carry through roster_edit.py once the file is on main. That matches the file's own precondition line and roster_edit.triage_refusal, which requires an ACCEPT ruling on the roster branch or origin/main.
