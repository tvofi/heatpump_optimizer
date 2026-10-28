Fix review: merge 7b023e7fa0eaa2eedfb08ccea36491d5bd2e4048

bus-nonce: 80a76412fe72ad9ae9e8865c08484fd3

## Summary

- This is round 2 for the PR. The round-1 block was at `2e2b374c`. I reviewed head `7b023e7fa0eaa2eedfb08ccea36491d5bd2e4048`, which is the head the body's `## Head` names and is still the PR head.
- The repair commit `7b023e7f` changes one token. P66's carry text now says `dev/programme/carries/carry-<N>.json` where it said `carries/carry-N.json`. That is exactly the repair round 1 asked for. The diff against `2e2b374c` touches nothing else.
- Each of the seven ACCEPTs names a live roster group, and each carry text is accepted by `tools/policy/brief_lint.mjs`. The earlier findings are answered: the block is fixed, O1 stays carried, and the dismissed `## Head` wording is gone from the body.

## Findings

- `tools/policy/brief_lint.mjs` lints a roster group's `brief` and never its `carry` entries. So `roster_edit.py --push`'s lint gate would accept an unresolved citation in a carry text, which is the shape of round 1's block. The instrument gap still exists, and this PR's diff does not touch it. It is the same item round 1 carried. Carry: O1

## Evidence

- RESULT live-groups: each ACCEPT names a group on `handoff/audit-r10-roster` at 9e9ee6ce (ev/carry-fold.txt). P66 and P76 name R10-FLY-CARRY-DISPOSITION (not-started). P67 and P75 name R10-FLOW-JIDOKA (in-progress). P70, P71 and P72 name R10-FLY-OPENPR-ATOMIC (not-started). Each carry text's `append-carry` target equals the group on its Verdict line. The DEFER targets also exist: R10-FLOW-BODY-ONLY (not-started) and R10-FLOW-JIDOKA.
- RESULT brief-lint (ev/brief-lint.txt, ev/brief-lint-merged.txt): I folded each ACCEPT's carry text into its group's `brief` and linted that roster. The fold is my own instrument; round 1 built the same one.
  - On the merged tree (origin/main 806aa2ce + head): base roster 0 errors, folded roster 0 errors.
  - At the head tree alone, both rosters print the same 4 errors. They all come from roster groups citing `dev/programme/triage/s6-batch4.md` and `record_beat`, which landed on main after this PR's base 73b69fe0a. The folded texts add none of them.
  - Positive control: putting round 1's P66 wording back adds exactly 1 error (`carries/carry-N.json: not in the tree`), on both trees.
  - Sensitivity control: a planted dead path in R10-FLY-CARRY-DISPOSITION's folded brief adds exactly 1 error.
- RESULT triage-gate (ev/carry-sim.txt): `roster_edit.ruling_verdict` returns ACCEPT for P66, P67, P70, P71, P72, P75 and P76, DEFER for P68 and P69, and REJECT for P73 and P74. The body's null control `ruling_verdict(P99)` returns None. `triage_refusal` returns None for all seven carry texts with their `triage:` citation. Mutant: flipping P75's verdict to DEFER makes `triage_refusal` refuse its carry ("is not an ACCEPT ruling (DEFER)").
- RESULT figures (ev/figures.txt): the body's count reproduces as 7 ACCEPT, 2 DEFER, 2 REJECT. In-tree claims re-checked at head:
  - P75: 0 files under the old briefs directory and 33 role or dimension .md files, at both head and origin/main. `fbbd3e61` is a commit. `prepr.sh:3087` still lists the dead glob, at head and at origin/main 806aa2ce.
  - P67: `rides --red` is at `prepr.sh:777`.
  - P76: `bus.sh` guards only through `ref_privacy.py guard` (line 264), and its self-test is at line 1092.
  - P66: its roster quote is present.
  - P69: all three of its roster quote fragments are present.
- Counts that cite the pre-study's out-of-tree scripts (`verdict_classes.py`, `opener_refusals.sh`, `cards.json`) cannot be re-derived from the tree, and this seat has not verified them. The file's preamble says so itself.
- Mutation proof is n/a: the diff has no production code line. `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched. Both changed files are under INERT `dev/programme/` (`tests/closure.py:273`). The diff contains no host paths.
- Merge: `git merge-tree --write-tree origin/main 7b023e7fa0eaa2eedfb08ccea36491d5bd2e4048` against origin/main 806aa2ce gives rc 0, tree 0e09b339. No conflict.
- CI on this head: 36 check runs were read via the check-runs API. None is red. 34 have concluded (success or skipped). `tests / coverage` and one `prelude` were still in progress when read. No red check is owed an answer, and the body's `## Red checks: none` matches.
- Forward-carry: the body says the orchestrator routes the carries through `roster_edit.py` once the file is on main. The simulation above shows each text would pass that gate.
