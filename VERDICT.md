Fix review: merge e666f058175780b75b2a6bdbe1ada7e80f369225

bus-nonce: e9a1c5fc6bc76b211c01d01b6a462878

Round 1 review of #2851 (roster batch 18, 9 ops) at head e666f058175780b75b2a6bdbe1ada7e80f369225, against dev/governance/roles/fix-review.md at origin/main 11b7a9d73 (roles diff merge-base...origin/main empty: current).

## Findings

- The append-group op 78d071da8 (R10-RCA-RATELIMIT-RECUR) rests on triage ruling P192 (V112, REJECT routed to root-cause), which no merged triage file records: dev/programme/triage/s6-batch32.md covers P184-P191 only, and `git grep P192 origin/main -- dev/` returns nothing. The op's commit message cites no ruling; the group's carry cites P192 by id, the merged countermeasure PRs #2606, #2629, #2608 (all merged=true) and mandate 6329234399 (owner_gate). The ruling's text lives only in the orchestrator's shared ledger. The RCA group's PR should cite P192 from a merged triage record (the next triage batch). Carry: R10-RCA-RATELIMIT-RECUR

## Evidence

- RESULT head: refs/pull/2851/head re-read with git ls-remote before writing is e666f058175780b75b2a6bdbe1ada7e80f369225 (ev/head_reread.txt); no move.
- RESULT ops: nine roster_edit commits 466c345df, 5d17ebe7d, b416158d0, 42cc77736, 492882021, 35be2daa9, 82dda60af, 789feaaa7, 78d071da8, plus main merge 908788012 and row commit e666f058175780b75b2a6bdbe1ada7e80f369225.
- RESULT set-stage R10-PROOF-CODEQL done: #2837 merge f6784210c9c2c89cfe82ec8bf6acb8b412629055 is an ancestor of origin/main (git merge-base --is-ancestor, ev/codeql_merged.txt).
- RESULT carries verbatim: the orchestrator's triage-carries/b32-*.txt files are not readable from this seat, so verbatim-to-carry-file is UNVERIFIED. Checked instead against the "Carry text" of each section of s6-batch32.md at origin/main: P184, P185, P187, P189, P190, P191 each appear verbatim (with their triage citation) as a new carry, absent at the merge base, on exactly the group the section's Verdict line names (P184/P189/P191 -> R10-TRAIN-OVERLAP-GRADE, P185/P187 -> R10-FLOW-DESIGN-STAGES, P190 -> R10-ORCH-BEATD) (ev/carry_verbatim.txt). P189 round 2 carry cites #2846 fix review round 2 and s6-batch32.md#P189; #2846 merged=true.
- RESULT duplicates: identical-carry count across the roster is 14 at the merge base and 14 at the head; this PR adds no repeat (ev/dup_and_ids.txt).
- RESULT carry_audit: `python3 -I tools/audit/carry_audit.py pr 2851` -> 0 routed, 0 unrouted, 0 bad destination(s) (ev/carry_audit.txt).
- RESULT new group: R10-RCA-RATELIMIT-RECUR id absent at the merge base, no duplicate group id at head; key set identical to sibling R10-RCA-INSTALL-RATELIMIT; no explicit topic field, topic derives from the group name (roster_lib.py:292/300) as r10-rca-ratelimit-recur, matching its branch handoff/r10-rca-ratelimit-recur and the live dispatch/fixer-r10-rca-ratelimit-recur ref; its carry cites P192 and runs 40269660944, 40271998592, 40271999135 (exist, PRs 2850/2843; ev/p192_runs.txt).
- RESULT group count: origin/main 196, head 197 (+1).
- RESULT roster lint (the roster_edit lint gate's form): `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json` on the merged tree -> 0 error(s), 0 warning(s), TOTAL: 0 error(s) across 1 file(s); plain `node tools/policy/brief_lint.mjs` on the merged tree checkout -> TOTAL: 0 error(s) across 48 file(s) (ev/brief_lint_*.txt).
- RESULT body figure re-derivation: carry counts 17->19, 11->15, 25->26, blob hashes 679a4be14 (main) and 837833ae2 (merged), merged tree ac375ff63 for the authored head and the four changed groups plus one added all reproduce (ev/carry_counts.txt). The body's "TOTAL: 10 error(s)" for git-archive extracts is not re-derived: my archive extracts with a fresh git init print 363 at both ends; the delta is zero under either method.
- RESULT three-dot diff (git diff $(git merge-base origin/main HEAD)...HEAD): A dev/programme/delivery/2851.md, M dev/programme/rosters/wave-r10-groups.json, nothing else; VERSION, manifest, RELEASE_NOTES.md and both claim files untouched (ev/three_dot.txt).
- RESULT merge: git merge-tree --write-tree origin/main e666f058175780b75b2a6bdbe1ada7e80f369225 exit 0, tree 2b3d88db5 (ev/merge-tree.txt).
- RESULT CI: 55 check runs on the head, all success or skipped, no red; gate and pr-contract success; merge_train.py classify -> GREEN, red: none (ev/check_runs.tsv, ev/classify.txt). No red check, so step 11 owes no answer.
- Mutation proof: n/a, roster state only, no production or test line.
