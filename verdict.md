Fix review: blocked f2daca863fb67409458f788e61839d4460a17ccb carry-missing: not carried to R10-FLY-CIPREDICT-RESTORING

bus-nonce: e4d8ca01fc746ad5595411241da3d25a

Round 8 (dispatched --past-three). Measured head `f2daca863fb67409458f788e61839d4460a17ccb`, still the PR head when written. Role contract current (`git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` empty).

## Block

Step 10. The body re-routes the three restoring jobs outside governance.yml to `R10-FLY-CIPREDICT-RESTORING`. That group at `origin/handoff/audit-r10-roster` `9bf6f941c` (`ev/roster_group_9bf6f941c.txt`) has `"carry": []`. Its `brief` names neither the control nor the precondition: not the enumeration rule (`git grep -n -- "- name: Restore the check source from the base commit" HEAD -- .github/workflows/`), and not that `budget-raise-gate` reads live reviews, so a local run of it is partial and never a pass. Worse, it prescribes the shape `carry-2952.json` refuses. It says "teach the graders arm to predict each" of the three named jobs, while the carry says "Refused: listing the three jobs by name, which closes the instance and not the class". The control and the precondition exist only in this PR's `dev/programme/carries/carry-2952.json`. That file still says "No live roster group covers #2952, so this file is its brief" (line 4), which stopped being true when `9bf6f941c` added the group. So the stage's own brief, the roster group, does not state the control as a precondition, and the two briefs disagree.

Repair needs no code change. Append a roster carry to `R10-FLY-CIPREDICT-RESTORING` with `roster_edit.py`. It should state carry-2952.json's control (the enumeration rule, re-run at the fixer's merge base), its precondition (unmeasured pr-contract and budget-raise-gate instances; budget-raise-gate is a partial run, never reported as a pass) and its refusal (no listing by name). Correct the body's delta paragraph (below). Then a re-dispatch can verify the roster SHA alone.

## Findings

- The roster group `R10-FLY-CIPREDICT-RESTORING` at `9bf6f941c` does not carry this PR's control and precondition, and its brief prescribes the by-name listing the carry refuses (the block above). Carry: R10-FLY-CIPREDICT-RESTORING
- `dev/programme/carries/carry-2952.json` lines 3-4 say no live roster group covers #2952. That has been false since `9bf6f941c`. Whichever of the two briefs is authoritative, the stale sentence tells the #2952 fixer it has none. Carry: R10-FLY-CIPREDICT-RESTORING
- The body's `## Delta since the last body` says `c78ea804e` marks the record's section-7 lines `Carry: R10-FLY-CIPREDICT-RESTORING`. The tree and the commit message both say `Carry: #2952` (`ev/tree_carry_lines.txt`, `ev/c78ea804e_message.txt`), and `git show c78ea804e | grep R10-FLY` matches nothing. The body misdescribes its own commit. The destination still resolves, because #2952 is the group's `fixes`. Carry: dismissed: body-only text, corrected by the re-body this block already requires
- The body's `## Red checks` says that, of the paths `defect-root-cause.md` names, the diff adds only `dev/programme/delivery/2925.md`. The diff also edits `tools/policy/policy_lint.mjs`, which that rule names in its parenthetical as the grader delivery-status runs from the base. The conclusion for nightly-status still holds: that job runs only the pinned `tests/nightly_status.py` against the API, and the diff touches neither it nor any workflow (`ev/diff_paths.txt`). delivery-status is green. Carry: dismissed: wording only, the red's attribution is correct
- `carry_audit.py pr 2925` reports `BAD-DEST #2925 review 6495961723 item a3103224: R10-RCA-PREPR-HEAD-GRADERS`. That item is in an earlier review, not the body, and names this PR's own group. The body alone gives 2 routed, 0 unrouted, 0 bad destinations (`ev/carry_audit.txt`). Carry: dismissed: an earlier verdict's item, not this PR's body, which the brief asked to be clean and is

## Evidence

- Brief claim 1, carry_audit on the live body: both body items route. `R10-RECORD-API-O1` resolves, and `R10-FLY-CIPREDICT-RESTORING` resolves on origin/handoff/audit-r10-roster. The body has 0 bad destinations, confirmed. The only BAD-DEST comes from a review item, listed above.
- Brief claim 2, the nightly-status answer: confirmed. The job runs `tests/nightly_status.py`, pinned by hash, which reads the GitHub API. The diff (`ev/diff_paths.txt`, 14 paths) touches neither it nor `ci.yml`, `tests.yml`, `nightly.yml` or `governance.yml`. The red is main's, not this PR's. The body names it, and `pr-contract` run 123796954155 started 23:32:44Z, after nightly-status concluded at 19:41:31Z, and is green (`ev/checks.txt`).
- The arm code is unchanged: `git diff --stat 7d1fbc055 HEAD -- tools/pr/ci_predict.py tools/policy dev/audit/rca/prepr-head-graders` prints nothing. The r7 delta `3efeea217..7af0ba5f9` adds carry-2952.json and the closure line for it, edits 13 lines of the record's prose, and changes no code.
- RESULT `python3 -I tools/pr/ci_predict.py --self-test` under venv-ci Python 3.14.7: `ci_predict self-test: 0 failed` (`ev/selftest.txt`).
- RESULT mutation proof (`python3 -I dev/audit/rca/prepr-head-graders/mutants.py .`, `ev/mutants.txt`): M1 bad 5, M2 bad 1, M3 bad 1, M4 bad 1, M5 bad 3, each matching the body's figure. No mutant survives.
- `git merge-tree --write-tree origin/main HEAD` against origin/main `2fde52634`: rc 0, tree `7e77799e5`, no conflict (`ev/merge_tree.txt`). The head's last main merge is `ce5940c0d`, 31 commits behind origin/main. The body's "measured against 2fde52634" is true of the merge-tree, but not of the head's tree.
- CI at the head: all 81 runs completed. `tests / nightly-status` is the only red. gate, arch-score, budget-raise-gate and pr-contract are green.
- I did not re-run keycount.py, jobtime.py or plant.sh this round, so the body's 584 / 57 s / 85 s / 215.5 s / plant rc 1 figures are not re-derived here. Their code is byte-identical to round 7's, which reviewed them; that is carried, not re-verified.
- The review packet is copied to `ev/review-packet.md`: no refusals, figure_lint 8 resolved.
