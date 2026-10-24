Fix review: blocked 96ad30e87ad6a52a879e6c94364021535fe6f5ae mutation-vacuous: MERGE_CALL's gh\s+pr\s+merge arm (agreement.mjs:126) reverted to literal spaces, 39 of 39 probes hold and a --subject on "gh  pr merge" goes unseen

bus-nonce: ce193715e37cd0d31419d50f4c15ae80

## Block

This is round 2. Round 1 was verdict/2697 at 90fcdff79, `blocked b4dd11917 mutation-vacuous`. I measured head 96ad30e87ad6a52a879e6c94364021535fe6f5ae, and it was still the head of fix/r10-merge-subject-harden when I wrote this (ev/heads_at_write.txt). The merge base is 73b69fe0a9fa9e45736cd1cdbc2077d3958b41ec, which is also origin/main. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so I worked from the current contract.

The body says under Unpinned sites: "Every other line the diff adds to the guard is killed by a self-test probe". Under finding 2 it also claims a behavior: "`MERGE_CALL` also tolerates whitespace inside `gh pr merge`". Only the argv arm of that line is pinned. The round-1 table's M9 mutates only `"pr",\s*"merge"`. The shell arm is not pinned at all:

- Y8: in `MERGE_CALL` (tools/policy/agreement.mjs:126), revert `\bgh\s+pr\s+merge\b` to `\bgh pr merge\b`. Self-test: `SELF-TEST 39 of 39 probes held` (ev/mutants_mine.txt).
- What changes (ev/probe_y8.txt, which extracts the head's guard block the same way the PR's seam probe does): `gh  pr merge 9 --subject s` is refused at head (`bad ["f:1"]`). Under Y8 it passes, with `calls []` and `bad []`. That is a writer miss, the defect class this PR closes, behind a behavior the body claims and no probe pins.

The repair is one probe in `selfTest`, for example `wr('gh  pr merge 9 --merge --subject "Merge pull request #9 (x)"\n').length === 1`, followed by a re-run of the table with Y8 added. From round 4 on, fixer.md owes a re-cut; this is round 2, so a repair is the right response.

## Findings

- MERGE_CALL's `gh\s+pr\s+merge` arm survives a revert to literal spaces with 39 of 39 probes holding. The body's statement that every other added line is killed is false for that arm. Carry: R10-MERGE-SUBJECT-HARDEN
- `MERGE_CALL` misses a shell continuation inside the command name. At head, `gh pr \` + newline + `  merge 9 --merge --subject "Merge pull request #9 (x)"` gives `calls []`, `bad []` (ev/probe_y8.txt, first line), because `\s+` does not match a `\`-newline. This is the same continuation seam that finding 2 closes for flags, here inside the command name. The body neither closes it nor dispositions it. No such site is on the tree (55 calls, refused=0). Close it in the same repair (for example, allow `(?:\s|\\\n)+` between tokens, plus a probe) or disposition it in the body. Carry: R10-MERGE-SUBJECT-HARDEN
- Y9 (`callExtent` returns `text.slice(start, i)` rather than `i + 1` at the enclosing close) survives at 39 of 39. Dropping the closing bracket only lets `SUBJECT_ARG`'s `$` match a flag that sits right before `)` or `}`, so the mutant can only add refusals. Carry: dismissed: near-equivalent mutant that only widens refusal; no writer miss
- Y10 (`next < 0 ? text.length : next` reduced to `next`) survives at 39 of 39. It changes the blank-line test only on a file's final line with no trailing newline, and only when that line is a single character. Carry: dismissed: near-equivalent mutant at end of file only; no writer miss on any realistic input

## Evidence

- Self-test at head: `SELF-TEST 39 of 39 probes held` (ev/selftest_head.txt). This matches the body.
- RESULT: the round-1 reviewer's ev/mut.py ran unchanged at head and killed all 13 mutants (M1 to M13), with the summaries and FAIL lines the body quotes (ev/mutants.txt).
- RESULT: my own mutants (ev/mut2.py, ev/mutants_mine.txt). X1 to X4 and X6 are killed as the body says. X5 survives (39 of 39) and the body already dispositions it. Y1, Y2, Y3, Y4, Y5, Y6, Y7, Y11 and Y12 are all killed. Y8, Y9 and Y10 survive, as covered under Block and Findings.
- RESULT: finder's harness, `python3 -I tools/policy/agreement_py.py --run`, at both ends (ev/harness_unperturbed.txt). Base 73b69fe0a: `52 merge call(s) in 11 file(s)`, `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`. Head: `55 merge call(s) in 11 file(s)`, `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`. Both walk `265 first-parent commit(s) past 07a09406a`; the body's 249 was measured at the older base 50af6174f.
- RESULT: perturbed, with `"--subject", "Merge pull request #%s (x)" % pr,` planted on merge_train.py:1483 (ev/harness_perturbed.txt). Base gives `refused=0`, a miss. Head gives `REFUSED merge-subject-pr writer tools/audit/seat/merge_train.py:1482` and `refused=1`. This matches the body.
- The pair item count is `1059 items, 0 divergent` at this head and 1071 at base 73b69fe0a. The body gives 1058 for f6568a429 and says the count describes that SHA only. That is consistent: `0 divergent` holds at both ends.
- The seam probe `node dev/audit/harnesses/r10_merge_subject_argv_seam.mjs` prints `[] [] ["f:1"]` at head, which matches the body and the file's header (ev/seam_probe.txt). I checked the Forward-carry dismissal against that output. The dismissal's control is stated (merges go only through merge_pr.sh and merge_train.py, which pass no --subject).
- `git merge-tree --write-tree origin/main 96ad30e87ad6a52a879e6c94364021535fe6f5ae` (origin/main 73b69fe0a): exit 0, tree ae962c956923f1cca56b307af505c3f1d6358d43, no conflict (ev/merge_tree.txt).
- VERSION, the manifest, RELEASE_NOTES.md and tests/golden are untouched: the three-dot diff is empty. `python3 tests/env_drift.py --claims-only origin/main` prints `claims hygiene: origin/main ok`.
- CI on this head (ev/ci.txt): 6 check runs. refresh and cancel-superseded succeeded once each; refresh, cancel-superseded and both prelude jobs were still queued. No gate workflow had concluded and no check is red. This verdict does not rest on CI. The body's Red checks section says `none`, and I cannot test that against concluded gate runs yet.
- I did not re-derive the 52 to 55 per-line census, the 1048 or 15/15 history null control, the class-census grep outputs, entities, structure, closure select or the archscore line. Those figures are the body's own and unverified here.
- Instruments built by this seat, named as mine: ev/mut2.py (X1 to X6 and Y1 to Y12, string-replacement mutants over the head's agreement.mjs) and ev/probe_y8.mjs. ev/mut.py and ev/probe.mjs are the round-1 reviewer's instruments (review/2697), and I used them unchanged.
