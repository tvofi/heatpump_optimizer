Fix review: merge f7025a5c60d673044b0da85daf21a1fd9ff3fb02

bus-nonce: 35016997a8d967c052e39c9f54015254
reviewer: cloud-review-2403 (round 10, group R10-ROSTER-UNWIRE; fix-review round 1)
measured head: f7025a5c60d673044b0da85daf21a1fd9ff3fb02 (detached worktree; PR head re-read at post time: unchanged)
contract: fix-review.md at origin/main; `git diff merge-base...origin/main -- dev/governance/roles/` empty (merge base 63816b857 = origin/main)

## Mutation proof (step 1) — my own mutants, each alone, file restored after each (evidence: mut*.py / mut*.out)
RESULT mutant M1 unwire absent-refusal deleted: KILLED (3 failed)
RESULT mutant M2 unwire default field -> fixes: KILLED (5 failed)
RESULT mutant M3 wire dispatch drops --field: KILLED (3 failed)
RESULT mutant M4 unwire keeps the entry: KILLED (7 failed)
RESULT mutant M5 wire dup-refusal deleted: KILLED (2 failed)
RESULT mutant M6 wire writes issues regardless of --field: KILLED (4 failed)
RESULT mutant M9 unwire dispatch dropped: KILLED (8 failed)
RESULT mutant M10 unwire acts on issues regardless: KILLED (4 failed)
RESULT mutant M11 wire default field -> fixes: KILLED (7 failed)
RESULT mutant J2 both wire --field guards (main + op) deleted: KILLED ("--field stage refused on wire-issue")
RESULT mutant M7 main wire/unwire --field guard deleted: SURVIVED — equivalent (shadowed by the op-level guard)
RESULT mutant M8 op-level guard in unwire deleted: SURVIVED — equivalent (shadowed by the main guard)
RESULT mutant J3 op-level guard in wire deleted: SURVIVED — equivalent (shadowed by the main guard)
RESULT mutant J1 both unwire --field guards deleted: SURVIVED — equivalent on rc: `--field stage` then falls through to the absent-refusal (rc 2). No roster group in r9/r10 has a top-level key named after a RESUME_FIELD (checked), so the refusal still happens for every input the CLI accepts; only the message differs. Not a vacuous test of new behaviour, but the check "--field stage refused on unwire-issue" does not pin the guard it is named for. Not blocking.
RESULT mutant M12 unwire removes first occurrence only: SURVIVED — equivalent (wire-issue refuses duplicates, so the list never holds one)

## Null controls (the self-test's, re-run and read)
- duplicate wire: "dup wire-issue refused" (issues) and "dup wire-issue --field fixes refused" — present; killed by M5
- unwiring an absent issue: "unwire-issue absent refused", "unwire-issue --field fixes absent refused" — present; killed by M1
- unknown group: "unwire-issue unknown group refused" — present (refused through the existing _need)
- --field defaults to issues: unwire ("default field is issues, not fixes": fixes refused, issues removes 10) killed by M2; wire ("--field issues still defaults and sorts") killed by M11
RESULT self-test at head: roster_edit self-test: 64 checks, 0 failed (matches the body)

## No-op round-trip bytes (evidence: roundtrip.py / roundtrip.out)
RESULT wave-r10-groups.json dump(load) byte-identical=True; wire+unwire on every group: issues 57/57 identical, fixes 57/57 identical
RESULT wave-r9-groups.json dump(load) byte-identical=True; wire+unwire: fixes 170/170 identical; issues 169/170 identical
The one change is R9-EG-A1, whose issues list is stored unsorted ([1774, 1738]): wire-issue sorts the list on append, and it already did on main. That is not introduced by this PR, and the r10 roster has no such group. Not blocking.

## Other steps
- step 4/5: no golden, claim, budget, closures, VERSION, manifest or RELEASE_NOTES path in the three-dot diff
- step 6: the body's class is the two integer issue-list fields (issues, fixes); both are covered. The body names no enumeration rule, but it states one class with two seams, both in the diff
- step 7: body names f7025a5c60d673044b0da85daf21a1fd9ff3fb02 as the head; it carries 9e3934d (auto merge of main 63816b857, no resolution) and 7f096fa (code head)
- step 8: the body says "Four mutants" and then lists five; its null-control line says wire-issue is "unchanged" while this PR adds --field to it (its default behaviour is unchanged, as the default checks confirm). I did not re-derive "5 new checks failed before the op existed". These are wording defects, not measured numbers. The 64/0 count and STRUCTURE RATCHET PASSED both reproduced
- step 9: an instrument PR with no finder harness; the self-test is the fixer's own, disclosed as such. My mutants and roundtrip.py are mine and are in the evidence dir
- step 10: Forward-carry none — nothing found that changes a later stage
- step 11: commit check-runs at f7025a5c60d673044b0da85daf21a1fd9ff3fb02 (check_runs.tsv): 30 success, 15 skipped, 0 failure once all concluded (closures 117680084171 success, Analyze (python) 117679674776 success, mutation 117679843144 success, instrument-self-tests 117679697772 success). No red check, so the body's "Red checks: none" holds. I re-ran neither the gate nor the mutation table
- step 13: git merge-tree --write-tree origin/main f7025a5c60d673044b0da85daf21a1fd9ff3fb02: rc 0, no conflict
- step 14: no instrument number moves. tests/structure.py: STRUCTURE RATCHET PASSED; arch-score check success
- step 15: additive op that follows the existing op_* shape. Note: the two-layer --field guard (main and op) is redundant by design; harmless
