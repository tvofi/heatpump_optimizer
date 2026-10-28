Fix review: blocked ad10fd2153c6c8fe2e1d56c8b0302c5b057cc37a figure-wrong: body states carry_audit check --body prints 0 finding items, 0 routed; at this head it prints 2 finding items, 2 routed, 0 unrouted

bus-nonce: 566ff789bf4f35118501560f72d41fc7

Round: second review (re-review after the figure-wrong block at 922640dc). I reviewed from a detached worktree at ad10fd2153c6c8fe2e1d56c8b0302c5b057cc37a. The instruments ran from a checkout at origin/main 93e6a63d2, which is also the merge base. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract read from main is current. Head re-read before return: the PR head and `fix/audit-r10-roster-pr` are still ad10fd2153c6c8fe2e1d56c8b0302c5b057cc37a, and `handoff/audit-r10-roster` is still 306a96d5f.

## Block

Every block from the 922640dc verdict is cleared at this head (Evidence). Every roster figure in the body re-derives exactly. One body figure does not reproduce when I run the command printed beside it (step 8):

- **Carry routing.** The body says `python3 tools/audit/carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body <this body>` prints `0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`. I ran it on this PR's current body, fetched by REST (6789 bytes, ev/body.md). It prints `CARRY-AUDIT: 2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_body.txt), and gives the same result with `--roster-ref ad10fd21`. The two items are the body's own `## Forward-carry` bullets, both of which end in `Carry:`. The routing result is correct: 0 unrouted, 0 bad. The quoted counts are wrong. The body's sentence that `sweep` "prints the same counts" is half true: `sweep` prints 0 items, 0 routed, which does not match the corrected `check` line.

Repair: body text only. Change the check line to `2 finding item(s): 2 routed, 0 unrouted, 0 bad destination(s)` and state the `sweep` line separately as `0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`. While editing, also fix the wording in the Forward-carry bullet (see Findings: at main, `update_pr.sh:46` exits 1, not 75). No roster or code byte needs to change, so the head can stay where it is.

## Findings

- The P22 carry on `R10-FLOW-BODY-ONLY` cites "l.42" for the 'branch checked out elsewhere' exit. At origin/main 93e6a63d2 that exit is `tools/audit/seat/update_pr.sh:46`, and it is `exit 1`. The 75 is the change P22 prescribes, not the current code. The body calls it "the 75 exit ... at update_pr.sh:46", which misdescribes the current line. The fixer must locate the exit by its message text ("checked out elsewhere") and change `exit 1` to 75 there. Carry: R10-FLOW-BODY-ONLY
- The same carry's counts ("28 permanent (topic, handoff-sha) entries ... 17 / 6 / 5") come from the relay's out-of-tree state, so the tree cannot answer them and I could not re-derive them. The fixer must re-measure them at their own start. Carry: R10-FLOW-BODY-ONLY
- brief_lint's metric-literal rule matches only the comparator form. A prose literal lints clean. Carry: dismissed: the rule enforces #411 class 4 as defined, no stage depends on widening it, and a hand scan of this PR's added text found no such literal (re-stated from the 922640dc verdict).

## Evidence

- Prior blocks at 922640dc, each checked at this head (ev/figures.txt, ev/stages.txt):
  - Counts restated as 108 / 144 / 36 new / 0 removed / 30 changed. The jq program printed in the body prints exactly `{"new":36,"removed":0,"changed":30}`. Changed is 30, not 29, because R10-ADVISOR and R10-RCA-ORCH-CONTINUITY moved since 922640dc and R10-RCA-ORCH-CONTINUITY's carry was already counted. The 30 is correct for this head.
  - The three fly-ins (BUDGET-LEAF, STAMP-CHECK-NOTES, MANDATE-REVOKE-GUARD) are listed. The new set is 23 R10-FLOW, 12 R10-FLY and R10-ROUND-PLAYBOOK, matching the body's twelve names.
  - R10-HANDOVER-REFRESH (302f66571, #2566) and R10-ROSTER-PUSH-RACE (3a9c6f849, #2569) are disclosed.
  - The phantom fbed03f8 paragraph and the mis-described 1e349a5b9 paragraph are gone. The Head section's parents match `git log`: ad10fd215 has parents 23cc013fa and 93e6a63d2. 23cc013fa merges 306a96d5f, the handoff tip.
  - R10-FLOW-RECHAIN's null `resume.commit` is named in the body and left alone (it was optional in the prior verdict). Its merge, 500668757 (#2576), is on main.
- RESULT figures (ev/figures.txt, ev/figures_byfield.txt):
  - Groups base 108 and head 144, and the jq program's {new 36, removed 0, changed 30}: confirmed.
  - The by-field breakdown is confirmed: carry in 22 groups, 18 of them carry-only; resume in 10; R10-CI-LAYOUT and R10-RCA-ORCH-CONTINUITY change carry as well; R10-SCORES changes brief, carry and files; R10-ORCH-MACHINERY changes after, carry and files.
  - No group name is duplicated.
- RESULT stages (ev/stages.txt): all ten stage changes are in-progress -> done. Each `resume.commit` is the merge commit of the named PR and is an ancestor of origin/main: d7121f32b #2531, 290712ec0 #2548, 92b5bf442 #2521, 4b36dc730 #2527, 295c874e8 #2547, 5a755f53e #2529, 302f66571 #2566, 3a9c6f849 #2569, f24895c0c #2572, 93e6a63d2 #2557. R10-I5-DOCS's base commit was 7a7102eb8, not null. The body's "set to the merge commit" still holds. Stage values at head: done 65, in-progress 7, not-started 69, queued 3, all values main's roster already uses (roster_lib DONE_STAGES is done and rca-done).
- Changes since 922640dc (ev/log_since_922640dc.txt, ev/since_prev.txt): five groups differ.
  - R10-FLOW-BODY-ONLY and R10-ORCH-MACHINERY each gain one carry. Each cites its source as a tick diagnosis under mandate 6329234399, not a PR number. Of the head's 399 carries, 244 cite no `#N`, so a PR citation is not the roster's convention. The cites resolve at main: `bus()` at orchestrator_tick.py:304 keeps stdout only; `relay_owed` is at :696; `level_set` runs at cloud_relay.sh:188 and :255; b38c6431a is on main.
  - R10-SCORES's brief changes one citation, coordinator.py:10287 -> :10293. Line 10293 at main reads `ctx._thermal_params.heat_loss_coefficient`, so the new citation resolves.
  - R10-ADVISOR and R10-RCA-ORCH-CONTINUITY are set-stage, as above.
  - The roster at 306a96d5f and at ad10fd21 is byte-identical (rc 0).
- RESULT well-formedness (ev/instruments.txt): `jq empty` parses. brief_lint on the head roster gives `TOTAL: 0 error(s)`. `roster_lib.py --self-test` gives 24 checks, 0 failed.
- Lint mutants (ev/lint_mutants.txt): an unknown `after` on R10-ADVISOR gives 1 error. A nonexistent path planted in a carry gives 0 errors, as does an invalid stage value. brief_lint does not check carry paths or stage vocabulary, so I checked both by hand above. The PR changes no production or test code, and its Mutation proof "n/a" is accurate.
- RESULT null control: `git diff --exit-code origin/main 93e6a63d2 -- <roster>` gives rc 0. Three-dot diff names: the roster and dev/programme/delivery/2588.md only.
- RESULT waves/path (ev/instruments.txt): plan_table at origin/main prints `8 wave(s)` with critical path R10-ADVISOR -> R10-SCORES -> R10-LIVESTATE -> ... -> R10-ARCH-DOCS (8). At the head it prints `8 wave(s)` with R10-NIGHT-FOLDS -> R10-LOOP-CPU -> R10-LIVESTATE -> ... -> R10-ARCH-DOCS (8). Both match the body.
- RESULT carry_audit sweep: `0 finding item(s): 0 routed, 0 unrouted, 0 bad destination(s)`; `CARRY-SWEEP: 0 pull request(s)`. Every Carry in this verdict names R10-FLOW-BODY-ONLY, a live group at origin/handoff/audit-r10-roster and at this head.
- VERSION, the manifest version and RELEASE_NOTES.md are untouched. No claim file or golden changed, so env_drift does not apply.
- RESULT merge-tree: `git merge-tree --write-tree origin/main ad10fd2153c6c8fe2e1d56c8b0302c5b057cc37a` gives rc 0, tree fd2d87d14. Clean (ev/instruments.txt).
- Red checks (ev/checks.tsv, check-runs API at this head, 52 runs): 30 success, 20 skipped, 1 neutral, 1 failure; every run has completed.
  - The failure is `nightly-status`. It grades main's last scheduled run, and this diff does not reach what it reads. The body names and answers it.
  - closures, env-matrix and instrument-self-tests, which were in progress when the body was written, have since concluded success.
  - pr-contract ran three times (01:22, 01:29, 01:39Z), all success, the last after every red concluded.
  - The intermediate commits 23cc013fa and 306a96d5f have no check-runs at all (0 runs each), so the body's "no non-green check-run" is true only vacuously.
- The jq counts, by-field breakdown and lint mutants are my own one-off commands for this review. They are not committed, and the mutant roster copies are not kept in ev/.
