Fix review: blocked 71f7a612a033e6401b410975fe2560a5c1368cb2 other: cost-test provenance false, second step labelled 6d, class search omits round-runner workflows

bus-nonce: 1b38bd654898f2ca106cc8df397c5949
Seat: review-2072. Round 1. Measured head 71f7a612a033e6401b410975fe2560a5c1368cb2, merge base bd59a4af1b26, origin/main 47b083b03a9d. Re-read live head before posting: unchanged.

The mechanism works. The three items below are body and labelling fixes, and none needs a code change beyond renaming one comment heading.

## Blocking

1. **The cost test's provenance sentence is false.** The body says "one sample for the CI figure: #2066 and #2070's red runs were cancelled by newer heads before completing". The check-runs API shows both PRs completed red on this guard:
   - #2066 d65c68c96c, check-run 113577108665: failure, 30m48s, refused `cop_duty_floor.py`.
   - #2070 f74924e09c, check-run 113595667988: failure, 29m50s, refused `early_cutoff_closed_loop.py`.
   - A fourth, #2066 9d77a97b1e (113611787157): failure, 27m26s.

   The 30m28s figure for #2065 is right (113574473913, 22:33:45Z to 23:04:13Z). Re-cut the sentence to the three samples, 29m50s to 30m48s. The conclusion is unchanged. The claim about what was measured is not.
2. **A second step is labelled "6d".** The base already has `# --- 6d. the CI reds a static read of the diff predicts (predict_line)` (R9-RO-11, #2030). Main cites that step as "step 6d" in two places: RELEASE_NOTES.md:73 and prepr.sh's own 7d text (lines 420, 437 and 2075: "every unpinned site step 6d listed"). #2067 adds a third, dev/audit/rca/R9-RCA-prepr-tmp.md ("14 failures in step 6d"). The head adds `# --- 6d. no moved path re-added`, and the commit message and body call the new step "step 6d". A reader of this RCA record has to work out which step is meant (CLAUDE.md: "a collision a reader must resolve is a defect"). The fix is to rename it 6e in prepr.sh, the body and the commit message.
3. **The class search (root-cause.md section 3) does not name the generators.** `.claude/workflows/audit-find.js` (152, 303, 363) and `audit-verify.js` (135-248) instruct a seat to write new files under `tools/audit/round${round}/`. This is the same obeyed-and-wrong instruction shape as the defect, and it fires at round 10's first commit. The body folds them into "871, the move stage's report-only backlog". The guard does catch it: I planted `tools/audit/round10/D0/report.md` and it was refused, rc 1, by the 0-categories arm rather than the moved-path arm. So the disposition can be "caught by prepr and fast; re-point owed to <stage>". It must be stated, and carried to that stage's brief if a later stage owns it (finding-propagation.md). Forward-carry now reads "none".

## Verified (RESULT lines)

- RESULT diff: exactly 3 files (CLAUDE.md, dev/governance/roles/fixer.md, tools/pr/prepr.sh), +57 -2, one commit, three-dot from the merge base. No `tools/audit` deletion survived the self-reported `rm -rf` slip.
- RESULT refuses: planted cases against the real tree (moved_line extracted from the head):
  - a new file under tools/audit/harnesses/: rc 1;
  - a `git mv` from dev/audit/harnesses/ back into it: rc 1;
  - a new tools/audit/round9/ file: rc 1, names dev/audit/rounds/round9/;
  - a staged-only file: rc 1.
- RESULT passes: head as is, rc 0, `GUARD: 0 refusal(s) against bd59a4af1b26`.
- RESULT diff-relative: a simulated base that already holds a retired-path file, with a branch that edits fixer.md, gives rc 0. A base holding a stale citation line, with a branch touching the same file elsewhere, gives rc 0. The same citation charged to the branch gives rc 1 (control). Main's existing state cannot wedge it.
- RESULT absent layout.py: rc 3, a skip line, never a refusal (also a self-test row).
- RESULT mutation: replacing the guard call with `out=ok; r=0` turns the three named rows FAIL (77, 78, 80). The run was killed after 154 ok rows. The unmutated self-test gives 216 passed, 0 failed, in 4m38s.
- RESULT cost: I measured 0.95 to 2.10 s over 11 runs at load average 46 to 58 on 8 cores. I could not re-derive the body's 0.44 to 0.73 s under that load. It is cheap either way: under 1% of the self-test, and roughly 1/1000 of the 30-minute CI round trip.
- RESULT stale count: 871 at the merge base, matching the body. It is 868 at the head, because the 3 re-pointed citations dropped off.
- RESULT process state: (d) is honest. The instruction was correct until the 2026-10-07 move, and the countermeasure makes prepr notice the changed precondition. That is the response defect-root-cause.md prescribes for (d).
- RESULT budgets: policy_lint 0 errors across 40 files.
  - corpus ~59911 tokens, flat against base, band 60091;
  - role fixer 6219 to 6220 (band 6352); role policy 9988 to 9989 (band 10458);
  - CLAUDE.md 3588 to 3589 words, cap 3590. CI policy-docs is green.
- RESULT #2067: `git merge-tree` 2072 x 2067 rc 0, 2072 x main rc 0, (main+2067)+2072 rc 0. The merged prepr.sh passes `bash -n`, and `moved_line` and its call site are intact. #2067 adds no third 6d; the label collision is this PR's own.
- RESULT checks: 38 check-runs at the head, all completed. The only failure is nightly-status, which is not this diff's. "Red checks: none" holds for a one-commit range.
- RESULT version: VERSION, the manifest and the RELEASE_NOTES heading are untouched.

## Non-blocking notes

- `moved_line` appends "move it to the new path" to every refusal. For the 0-categories arm (the round10 plant) there is no new path, so the hint is wrong.
- The guard reads the index (`--cached`), while prepr's other steps read `$BASE...HEAD`. A staged change that differs from HEAD is judged in place of the pushed head. This is harmless in the usual flow, where prepr runs on a clean committed head.
- The policy re-points (CLAUDE.md, fixer.md) still need the owner's approving review under the mandate.

Evidence: /Users/timmalmstrom/hpo-seats/review-2072/evidence (HEAD.txt names the head)
