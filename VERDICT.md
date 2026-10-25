Fix review: blocked bd81b886388c840792fa69bf5a43cec1337bff02 carry-missing: not carried to R10-MERGE-SUBJECT-CASEARM: its roster brief still sends it to close the case-arm class this head closes (49 of 49), and its carry names the case arm, `*)` and glob arms as its routed spellings, not the three the body routes to it (a blank line in a Python argv, a blank line in a JS argv, a `)` in a JS block comment)

bus-nonce: 865d2699d5722dcd2b20d07097c53b09

## Block

Review round 9 of #2697. The code passes every check the brief set. The tree-planted differential returns main_not_head=0 at this head, the null control returns 0, and round 8's head returns 8070 on the same corpus. The block is `fix-review.md` step 10 only.

The body's Forward-carry says R10-MERGE-SUBJECT-CASEARM's brief "must record" two things: the three routed spellings, and the regression-against-main control. The roster at `handoff/audit-r10-roster` f02938c3f (`ev/roster_casearm_at_f02938c3f.json`) records only the second.
- The group's `brief` string still describes this PR's scope as the group's work: "Close the class by a rule that enumerates every case-arm spelling (with and without the leading paren, any indentation, multi-pattern arms a|b))". At this head that class holds 49 of 49 (`OPEN R10-MERGE-SUBJECT-CASEARM expected-fail: held=49 of 49`, `ev/argv_seam_head.txt`). Merging this PR therefore invalidates the assumption the brief rests on (`finding-propagation.md`, "invalidates an assumption it rests on").
- Its first `carry` entry names "the three routed spellings it owns: the case arm, the `*)` arm, and the glob arms". The body routes three other spellings to it. Each prints `XFAIL` at this head under `routed expected-fail: held=0 of 3` and passes main's line guard too:
  - a blank line in a Python argv;
  - a blank line in a JS argv;
  - a `)` in a JS `/* */` comment after `merge`.

  These three are in this PR's body and in its harness's XFAIL rows. They are not in the stage's brief.
- The RCA carry (#2798's precondition control) is present and states its control as a precondition. That part is satisfied.

Remedy: a `roster_edit.py` change to R10-MERGE-SUBJECT-CASEARM, with no change to this head.
- Replace the brief's case-arm scope with the three routed spellings and their XFAIL rows (`node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs <agreement.mjs>`, `routed` lines).
- Say that the case-arm class holds at #2697's merge, 49 of 49.
- Correct the first carry's list of routed spellings.

The code verdict below carries to the same head once the roster is corrected.

## Findings

- R10-MERGE-SUBJECT-CASEARM's roster brief and first carry describe the case-arm class as the group's work and misname its three routed spellings. See Block. Carry: R10-MERGE-SUBJECT-CASEARM
- A boundary mutant of the new skip survives every instrument. The mutant is `if (i < at) {` → `if (i < at - 3) {` (B2, my own, `ev/mutant_shas.txt`).
  - It survives `--self-test` 180 of 180, the argv-seam table, the PR's differential and the RCA differential (planted and corpus, main_not_head=0).
  - It changes the verdict on reachable spellings where the closer sits within three characters before `pr`. Two examples are `G=${X:-` / `gh} pr merge 9 --subject x` and the Markdown `Run it (with` / `` `gh`) pr merge 9 --subject x ``. The head refuses both and B2 misses both (`ev/boundary_probe.txt`).
  - Main misses both too, so this is a gain the head makes that no probe pins, not a regression against main.
  - The group that next edits `callExtent` should add one self-test probe with a closer right before the program word, so that the `< at` boundary is killed. Carry: R10-MERGE-SUBJECT-CASEARM
- B1 (`i < at` → `i <= at`) also survives. Carry: dismissed: equivalent; the character at `at` is the first letter of the matched word, never a closer

## Evidence

Head, round and scope:
- Round 9. The measured head is `bd81b886388c840792fa69bf5a43cec1337bff02` (`ev/HEAD.txt`). It is `refs/pull/2697/head` and the head the PR body names.
- The head merges origin/main `de794b537` onto the authored code head `2cb5fd961`. `git diff 2cb5fd961 bd81b8863 -- <the 8 PR files>` shows only the new `dev/programme/delivery/2697.md` row. The main merge adds no code delta (`ev/merge_tree_and_scope.txt`).
- `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- `git merge-tree --write-tree origin/main bd81b8863` exits 0 with tree `fb791dff0`. The merge base is origin/main `de794b537` itself.
- The three-dot diff holds 8 files and none is `VERSION`, the manifest or `RELEASE_NOTES.md`. The 5 new harnesses are classified in `tests/closures.json`.

Acceptance: the RCA tree-planted differential. The instrument is `dev/audit/rca/merge-subject-class-open/differential.mjs` at #2798's branch `7c64db1b3`, copied verbatim as `ev/differential.mjs`. It is the root-cause seat's instrument, not the fixer's (`ev/differential_planted_at_head_tree.txt`, `ev/differential_main_tree_and_corpus.txt`).

| command | files | corpus | main_not_head |
|---|---|---|---|
| `planted origin/main bd81b8863` (cwd at the head) | 289 | 82735 | **0** |
| `planted origin/main origin/main` (null control) | 289 | 82735 | 0 |
| `planted origin/main 4aad9c117` (round-8 positive control) | 289 | 82735 | 8070 (`unmatched-closer-in-lead` 8016, `other` 54) |
| `planted ...` with cwd at origin/main `de794b537` | 289 | 82735 | head 0, 4aad9c117 8070 |
| `corpus origin/main origin/main bd81b8863 4aad9c117` | 192+96+8 | — | 0, 0, 147 |

The instrument names no line at this head, so there is nothing to dispose.

The 54 `other` lines at 4aad9c117 are each refused at this head. I listed them with my own wrapper, `ev/other54.mjs`, which reuses the RCA's corpus, `load()` and `shape()` verbatim (`ev/other54_at_head.txt`):
- `SUMMARY {"unmatched-closer-in-lead head=refused":8016,"other head=refused":54}`;
- examples: `audit-find.js:209`, `archscore/ABOUT.md:57`, `archscore/planted/controls.py:208`.

Re-derived at three ends: the case-arm and closer-in-lead lines the r8 verdict named. I ran the r8 reviewer's own generators (`ev/r8_generators/`, from verdict/2697 7c97d8c00) against guards from the head, main `de794b537` and 4aad9c117 (`ev/r8_probes_three_ends.txt`):
- `probe.mjs` (case arms `never)`, `a|b)`, `*)` and `[0-9]*)`, plus 15 control leads): head 228 of 228, main 228 of 228, 4aad9c117 180. Null refused 0 of 8 at all three.
- `probe2.mjs` (`1)`, `a)`, `- step 2)`, `:)`, the shell array closed on the merge line, and JS and Python tails): head 13 of 13, main 13, 4aad9c117 8.
- `probe3.mjs` (the wrapped Markdown parenthetical): every `MISS` across all three probes is 4aad9c117's (55 in total), and none is the head's or main's.

The finder's harness, `python3 -I tools/policy/agreement_py.py --run`, with the r8 plant `ev/r8_generators/md_plant.sh` (`ev/finder_md_plant.txt`):
- head: unperturbed 63 calls, refused=0. The plant is REFUSED at `web-fragments.md:157`, and the control is REFUSED.
- main `de794b537`: 53 calls, refused=0. The plant is REFUSED and the control is REFUSED.
- The worktree is clean afterwards.

`bash dev/audit/harnesses/r10_merge_subject_plants.sh [origin/main]` (the finder's harness under the body's plants; `ev/plants_sh.txt`): head: unperturbed 63 calls refused=0; the 18 spelling plants refused=1 each; both closer-in-lead plants and both controls refused=1; three nulls refused=0. main `de794b537`: unperturbed 53 refused=0; the 18 spelling plants refused=0 each; the closer-in-lead plants and controls refused=1; nulls refused=0. Matches the body's table; worktree clean afterwards.

Mutants (`ev/mutants.txt`, `ev/mutants_selftest_mine.txt`, `ev/mutants_under_differential.txt`):
- `python3 dev/audit/harnesses/r10_merge_subject_mutants.py` gives 86 rows, 0 `NOT APPLIED` and exit 0. Exactly 2 rows print `SELF-TEST 180 of 180`: Y9 and Y10, as the body says.
- K1 (skip deleted) prints 178 of 180 and both closer probes FAIL.
- K2 (depth kept negative) prints 179 of 180 and the null control FAILs.
- My own mutants, committed locally and never pushed, under the acceptance instrument:
  - K1: planted main_not_head=8070, corpus 147. It is killed by the acceptance as well as by the self-test.
  - B3 (skip only at the extent's start): self-test 178 of 180, planted 7320, corpus 129. Killed.
  - K2: planted 0. The acceptance measures only the loss direction, and the self-test null control kills K2.
  - B1 and B2: see Findings.
- Each arm the brief names is killed: the skip by K1 and B3, the depth reset by K2.

Other figures at this head:
- `node tools/policy/agreement.mjs --self-test` prints `SELF-TEST 180 of 180 probes held`, exit 0 (`ev/selftest.txt`).
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`, exit=0 (`ev/structure.txt`). No budget file is in the diff.
- The PR's own differential, `node dev/audit/harnesses/r10_merge_subject_differential.mjs origin/main` (`ev/pr_differential.txt`), prints `TOTAL lines=109027 refused_main=7445 refused_head=7445 main_not_head=0`, exit 0. Against 4aad9c117 it prints `main_not_head=5455` (plants 55, generated 5400). Each part matches the body's table.
- `r10_merge_subject_argv_seam.mjs` (`ev/argv_seam_head.txt`, `ev/argv_seam_ends.txt`):

  | row family | head | 4aad9c117 | main `de794b537` |
  |---|---|---|---|
  | PROGRAM-CLASS | 144/144 | 144 | 12 |
  | WRAPPED | 12/12 | 12 | 0 |
  | CLASS | 43/43 | 43 | 13 |
  | case arm `held=` | 49 of 49 | 16 | 49 |
  | `routed held=` | 0 of 3 | 0 | 0 |

  Every null is 0, and the figures match the body.
- The census against 4aad9c117's guard (`ev/census.txt`) prints `TOTAL old=63 new=63` with no `DIFF` line, plus `UNCOVERED 62 of 103`, `EXTENT 11 of 63` and `SPLIT 2 of 2`. These match the body, and the EXTENT and SPLIT sites are the ones it names.

CI on this head, from the check-runs API (37 runs, read during this review):
- None concluded failure.
- Success: `tests / mutation`, `typing`, `browser`, `arch-instrument`, `closure-scope`, `briefs` and `nightly-status`; `governance / delivery-status`, `env-matrix`, `policy-docs` and `wave-script`; `arch-score`, `budget-raise-gate`, `hassfest`, `validate-hacs`, and `codeql` actions and javascript.
- Still in progress: `tests / closures`, `tests / coverage`, `tests / fast (3.14)`, `governance / instrument-self-tests`, `codeql` python, and one `prelude`.
- Step 11 has nothing to answer at this read. The body's "Red checks: none" holds so far.

UNCERTAINTIES:
- I did not re-take the body's hygiene list (entities, ci_predict, policy_lint, rules_sync, archscore). Those figures are the body's, taken at `2cb5fd961`.
- I used `python3` from PATH.
