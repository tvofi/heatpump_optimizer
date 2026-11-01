Fix review: blocked 757c71eb905b9152d853054b754325d04206f8d1 body-stale: the body still says a file without set -u is not judged and carries that seam, though 07f79c3cf judges every file and the roster holds no such carry

bus-nonce: e1be6ac81a376e7a85a8c6d0c1bfde7d

This is round 2 under the dispatch brief. It is the third review overall, after review/3055 and verdict/3055. I measured head 757c71eb905b9152d853054b754325d04206f8d1 from a detached worktree at that SHA. Merge base: 6421fe135. Contract: dev/governance/roles/fix-review.md at origin/main. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty. `review_carry.py 07280b77b 757c71eb9` prints FRESH-REVIEW, so I judged the whole head. The harness is the round-1 reviewer's finder harness (verdict/3055 evidence/plants.txt), re-run as written.

## Block

1. **body-stale: the PR body contradicts the code at this head.** The code at 07f79c3cf judges every tracked tools/**/*.sh file, with or without `set -u` of its own. That is true of `sites()` (no SET_U branch), the docstring, the instrument page, INSTRUMENTS.md:109, the entities comment, and the self-test and entities rows "a file without set -u is judged too". The body still states the round-2 design it was written at (b2d4905d). Its `## Head` section discloses that the sections "were measured at b2d4905d and are not re-measured by this seat". So the body is the only record a later seat reads, and it is wrong at four points:
   - Lead paragraph: "a file without `set -u` is not judged (the sourced `pr_args.sh` is guarded or marked by hand)". The class barrier is also described as "a file with `set -u` may not expand ...". Both are false at the head.
   - `## Null control`: it lists "a file with `set -e` only is not judged" as a green control. The head's self-test asserts the opposite, and mutant ME below shows the opposite is pinned.
   - `## Figures` "Residual seams": "A sourced library with no `set -u` of its own is not judged ... Carry: R10-SUITE-HOST-DETERMINISM". Two things are wrong with this line (ev/carry.txt):
     - The seam is closed in code at this head. P3 is red, and so is the self-test row.
     - Roster origin/handoff/audit-r10-roster 9ddd1c689 holds no carry for it. R10-SUITE-HOST-DETERMINISM carry[5] holds only the HEAD-versus-working-tree seam, with its control.

     So the round-1 carry-missing item is still literally open in the body. The substance is resolved, but the body never says so.
   - It is also an undisclosed departure from the group brief. The roster brief for R10-FLY-BUS-BASH32 asks for the static check over "tools/**/*.sh files running under `set -u`", with the null control "a file without `set -u` is not judged (null)" (ev/group_brief.txt). 07f79c3cf inverts that control. Its reason holds: a sourced library runs under its caller's `-u`, and nounset has spellings a textual test misses. But the body must state the departure, and the reason, as a departure.

   Smaller stale figures, which I re-derived (ev/figures.txt):
   - "its seven `bare_array:` rows": at the head there are 9 (`grep -c "ok   bare_array"` on the isolated block gives 9).
   - "ALL 2501 ENTITY CHECKS PASSED" and "PRE-PR: b2d4905d..." were taken at b2d4905d, and I did not re-derive them at this head.
   - The `## Figures` enumeration is labelled "(set -u files only)". At the head the rule judges every file, and `--check --ref 3759d49a5` lists 17 sites, against 12 from b2d4905d's rule. The 5 extra sites are pr_args.sh 173/240/243/245/249, all of which the body dispositions by hand. So the head's "adds zero sites at this head" is true, but the label is not.

   Repair: edit the body only. No code change and no head move are needed. Restate the design as "every file is judged", and name 07f79c3cf as a departure from the group brief's null control, with its reason. Replace the null control with the head's twin pair: "a file without set -u is judged too" and "the guarded form passes in a file without set -u (null)". In Residual seams, drop the sourced-library seam as closed in code by 07f79c3cf. Keep the HEAD-versus-working-tree seam, citing roster 9ddd1c689 R10-SUITE-HOST-DETERMINISM carry[5]. Re-take the row count and the entities total at the head, or say they are not re-taken. The code itself passes every check below, so a body-only repair can be re-verified without re-running the mutants.

## Findings

- The function `marked` and the opening set in `sites()` duplicate one predicate. A line is refused for a reason-after-marker whether or not it holds a bare expansion, and the `marked(line)` early `continue` then skips that line's bare scan, which is harmless only because the line is already in `out`. I give no defect here, because every plant behaves (ev/plants.txt). Carry: dismissed: behaviour is correct at every plant and mutant; it is a readability note, not a seam.
- No macOS bash 3.2 exists in this container, so the original `bus.sh orphans` rc 0 on 3.2 is still unrecorded, as the body states. Carry: dismissed: the static rule is the group's chosen pin, and the body offers the departure from the carry's run-time row for the reviewer to decide. I accept it, because a bash-5 run-time row would pass on the defect.

## Evidence

- RESULT item 1, the finder's plants at the head (ev/plants.txt), with bus.sh `set -uo pipefail` at line 140:
  - Null, the clean head: `--check` rc 0. The output is a single empty line, from `print("\n".join([]))`, as at round 1, and no site is listed.
  - P1, a bare line with the reason after the mut marker: rc 1.
  - P2, a non-bare line in the judged file: rc 1.
  - P2b, a guarded line in the judged file: rc 1.
  - P3, pr_args.sh: rc 1.
  - P4, a comment-only reason above: rc 0.
  - P5, the reason two lines up: rc 1.
  - The self-test is ok.

  The round-1 class-open item is closed.
- RESULT item 1, the judged-file rows. The self-test has "a reason after a mut marker is refused in a judged file on a line with no bare expansion" and "... on a guarded line", plus the null "a judged file's non-bare line with the reason before the marker passes". The entities block has "a never-empty reason after a mut marker is refused in a set -u file too", with a `set -uo pipefail` head plus `f x  # mut:m  # never-empty: why`, want 1. I ran the entities block in isolation with a stub `R` (my own driver, ev/ent_rows.py, disclosed as mine; it execs the block's exact source from tests/entities.py at the head): 10 rows ok.
- RESULT mutants, each applied in place and restored with `git diff --quiet` (ev/mutants.txt):
  - MA, the brief's one-line revert: the reason-after-marker set is emptied, so only the bare-expansion list is returned. Self-test red on 3 rows, both judged-file rows among them. Entities red on "...refused (it unanchors the mutant)", on "...refused in a set -u file too", and on the self-test row.
  - MB, `marked` ignores marker order: self-test red on 4 rows and entities red on 3.
  - MC, the line-above reason ignored: red, and `--check` lists body_patch.sh:120 and pr_args.sh:250.
  - MD, `above` persists past the next line: red on "excuses only the line directly below it".
  - ME, the old design restored (files without set -u return []): red on 4 self-test rows, entities red on 3.
  - MF, guard recognition dropped: red, and `--check` lists 3 guarded sites.

  All six were killed.
- RESULT item 2: the roster at 9ddd1c689 is quoted in ev/carry.txt. The HEAD-versus-working-tree seam is at R10-SUITE-HOST-DETERMINISM carry[5] (and R10-FLY-SUITE-ENV-FLAKES carry[9]), with its planted-defect control. No carry names the sourced-library seam. That seam is closed in code at this head (P3, mutant ME), so what remains is the body's text: Block 1. carry_audit in the review packet resolves the body's Carry line (1 routed), but it checks the group, not the seam.
- RESULT re-derived figures (ev/figures.txt):
  - Head rule, `--check --ref 3759d49a5`: rc 1, 17 sites. The b2d4905d rule gives 12. The difference is the five pr_args.sh sites.
  - `--ref 6a988a23`: rc 1, at body_patch.sh:98 and pr_args.sh:249, which matches the body's failing-test-first claim.
  - `--ref b2d4905d` and `--ref HEAD`: rc 0.
  - The mut-collision rule `grep -rnE '# mut:[A-Za-z0-9_-]+\s+\S'` returns nothing (rc 1).
  - `grep -c '# mut:contract$'` gives 1 and `grep -c '# mut:grace$'` gives 1.
  - The round-1 wording finding on the pr_args.sh reasons is tidied at this head (the reasons now cite "the early return two lines up" and "the early return above the loop, then the alive check each pass").
- RESULT item 3, the standing checks (ev/gate.txt):
  - `git merge-tree --write-tree origin/main <head>`, with origin/main at 1a8051350: rc 0, tree 4df4b031a. `LEDGER-MERGE: resolved tests/closures.json` is the driver resolving the only overlap.
  - Both claim files, VERSION, RELEASE_NOTES.md and manifest.json are byte-identical to origin/main.
  - `dev/programme/delivery/3055.md` is in the three-dot diff.
  - `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
  - `closure.py select --diff <merge-base>`: `MODE: FULL`.
  - `## Head` names 757c71eb9, the head I measured.
- RESULT ## Red checks and CI: `merge_train.py classify 757c71eb905b9152d853054b754325d04206f8d1` printed `GREEN 757c71eb905b9152d853054b754325d04206f8d1 pending: none red: none`, rc 0, at 13:23Z (ev/classify.out, ev/classify.rc). The check runs at the head, 43 on one page of 100, show none concluded failure. `governance / instrument-self-tests` 124851987792 succeeded at this head, so main's uutils-sleep red does not touch it, and no red check is owed an answer. `prelude` of run 41307865483 is still in progress, and the ruleset does not require it, so it does not block. I cite CI's heavy runs (`tests / fast (3.14)` 124852100747 success, `tests / closures` success, `tests / mutation` success) and did not re-run entities.py in full or the mutation table.
- RESULT head re-read before posting: `git ls-remote origin fix/r10-fly-bus-bash32` still gives 757c71eb905b9152d853054b754325d04206f8d1 (ev/head_recheck.txt).
