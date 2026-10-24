Fix review: blocked b4dd119172d5e0f04f800e752dffe265228d19e1 mutation-vacuous: callExtent open.pop() on a bracket closed before the match (agreement.mjs:154) deleted, 36 of 36 probes hold and a --subject after "(cd repo) &&" goes unseen

bus-nonce: 318a6c0ebb4eebe791abb025c0d712fd

## Block

Round 1 (no earlier verdict on the PR). Measured head b4dd119172d5e0f04f800e752dffe265228d19e1, still the head of fix/r10-merge-subject-harden when written; authored code head 09b1d002c19f941e9ba77367554e086c8cec50ee, merge base 50af6174f53c0f9bec3f705c3a4bb99615f71acc.

The body states under Unpinned sites "every production line added is killed by a self-test probe (M1 to M11)". Two added production lines in `callExtent` are not, and both mutants change behavior (ev/mutants.txt, ev/probe.mjs):

- M13: delete `else if (')]}'.includes(c)) open.pop()` (tools/policy/agreement.mjs:154). Self-test: `SELF-TEST 36 of 36 probes held`. Behavior: `(cd repo) && gh pr merge 9 --merge --subject "Merge pull request #9 (x)"` is refused at head (`["f:1"]`) and passes under the mutant (`[]`): the bracket closed before the call stays on `open`, so the extent starts at that `(` and ends at its `)`, before the call's own flags. That is a writer miss, the defect class this PR closes, on a line no probe pins.
- M12: delete the quote-state reset at a line end (`st = { q: '', esc: false }`, tools/policy/agreement.mjs:161). Self-test: 36 of 36 held. Behavior: `run(["gh", "pr", "merge", n,  # it's\n     "--merge"])\nother(["--subject", s])` passes at head and is refused under the mutant, because an apostrophe in a comment makes the rest of the extent quoted text and the extent runs on into the next statement. It is an unpinned false-positive guard.

The repair is two probes (one per shape above) in `selfTest`, then re-running the M1 to M13 table.

## Findings

- Two production lines added in callExtent (agreement.mjs:154 open.pop on a closed bracket, agreement.mjs:161 quote-state reset at a line end) survive deletion with every self-test probe holding; the body's "Unpinned sites: none" is false. Carry: R10-MERGE-SUBJECT-HARDEN
- The body quotes `pair merge-subject-pr: 4 readers, 1055 items, 0 divergent` "at head". Re-run: 1055 at base 50af6174f, 1056 at 09b1d002c, 1057 at b4dd119172d5e0f04f800e752dffe265228d19e1; the item count grows with commits on HEAD, so the quoted figure is the base's, not the head's. Correct the figure in the body. Carry: R10-MERGE-SUBJECT-HARDEN

## Evidence

- Self-test: head `SELF-TEST 36 of 36 probes held`, base `SELF-TEST 27 of 27 probes held` (ev/selftest_head.txt). This matches the body.
- Mutation proof re-run with my own mutants M1 to M11, matching the body's list (ev/mutants.txt). Each is killed by exactly the probe the body names, with the counts the body gives (M1/M2 35 of 36, M3 32 of 36, the rest 35 of 36).
- Finder's harness `python3 -I tools/policy/agreement_py.py --run` at both ends (ev/harness_unperturbed.txt, ev/harness_perturbed.txt). Base unperturbed: 52 merge calls in 11 files, `RESULT divergent=0 unregistered=0 dead=0 refused=0`. Head unperturbed: 55 calls, `refused=0`, `AGREEMENT ok`. With `"--subject", "Merge pull request #%s (x)" % pr,` planted on merge_train.py:1483 (the second line of the split call), base gives refused=0 (missed) and head gives `REFUSED merge-subject-pr writer tools/audit/seat/merge_train.py:1482`, refused=1. This matches the body.
- Guard walk: `249 first-parent commit(s) past 07a09406a` at both ends, as the body says.
- I did not re-derive the 52 to 55 per-line census, the 1048 or 15/15 history null control, or the class-census grep outputs. These are the body's own, unverified here.
- `git merge-tree --write-tree origin/main b4dd119172d5e0f04f800e752dffe265228d19e1` (origin/main 145bfe197b9e7c09eb90bedadec44c6bc19d679d): exit 0, tree fce3dbc7c2bcaa3a5739592441eff9ee731cc285, no conflict (ev/merge_tree.txt).
- VERSION, manifest and RELEASE_NOTES.md are untouched (three-dot diff is empty).
- CI on the head (ev/ci.txt): no red check run. tests / coverage, codeql python and one prelude were still in progress when I read them. `tests / mutation` is green in 34 s, so per fix-review.md step 11 I take it as no evidence that the .mjs mutants above were evaluated.
- The body's Red checks section says none, and it is consistent with the runs.
- Instruments built by this seat and named as mine: ev/mut.py (string-replacement mutants over the head's agreement.mjs) and ev/probe.mjs (extracts MERGE_CALL, SUBJECT_ARG, quoted, callExtent and subjectWriters and runs four cases).
