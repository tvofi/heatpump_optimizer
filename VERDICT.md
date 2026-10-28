Fix review: merge 3bf97d36aa37989936038feba3c69cc6ae7011c3

bus-nonce: d492d7843a0c5aa6e771840b78ac9206

## Summary

Round 11 of R10-MERGE-SUBJECT-HARDEN, a minimal re-cut. The guard is unchanged. The four instruments that each cut the merge-subject guard block out of `tools/policy/agreement.mjs` now share one exported helper, `dev/audit/harnesses/merge_subject_guard_block.mjs`. The helper no longer cuts `nonTemplateMerges`. Measured at head 3bf97d36aa37989936038feba3c69cc6ae7011c3 from detached worktrees, against the pre-change instruments at e5aa81ea3 and main at da12aa37d (later f54f40cc1). Every figure in the body re-derives exactly.

## Findings

- Surviving mutants Y9 (`text.slice(start, i)`) and Y10 (`next` for `next < 0 ? text.length : next`). Both still survive at this head (`SELF-TEST 180 of 180`), as the body states. Carry: dismissed: near-equivalent mutants dispositioned in the PR body; re-run at this head, no writer miss
- The three spellings that stay open (a blank line in a Python argv, a blank line in a JS argv, a `)` in a JS `/* */` comment). Each prints XFAIL in the argv-seam harness's routed row. The regression-against-main control rides with them. Carry: R10-MERGE-SUBJECT-CASEARM

## Evidence

- Role contract current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.
- RESULT guard-unchanged: `git diff 71f6ecbeb 4dbc9c230 -- tools/policy/agreement.mjs` gives 0 lines, and so does `git diff 4dbc9c230 3bf97d36a` for that file (ev/files.txt lists the diff).
- RESULT self-test: `SELF-TEST 180 of 180 probes held` (ev/selftest.txt).
- RESULT mutation table, `r10_merge_subject_mutants.py`, re-run in its own worktree: 86 rows, 0 NOT APPLIED, 2 survivors (Y9, Y10). Every other row prints a FAIL (ev/mutants.txt, ev/mutants_summary.txt).
- RESULT instrument identity, pre-change e5aa81ea3 against head, same arguments, compared with `cmp`: argv-seam, census, census given bd81b8863's agreement.mjs, the harness differential `bc52ad2af1d0 e5aa81ea3`, and the rca differential in named, corpus and planted modes. All IDENTICAL, all exit 0 (ev/identity.txt).
- RESULT null control: a mutant of the helper that drops its pre-extent opening (`const from = h`) makes hdiff, rca.named, rca.corpus and rca.planted DIFFER, while argv and census stay IDENTICAL. That is four, as the body says (ev/null_control_H1.txt).
- RESULT nonTemplateMerges is dead code in the cut. I planted a `throw` as the first statement of `nonTemplateMerges` in head's agreement.mjs. argv-seam, census, rca ×3 and the harness differential (main against the working-tree head) all stay byte-identical (ev/perturb_N1.txt). The pre-change agreement lane prints `RESULT divergent=0 unregistered=1` (the duplicated `function nonTemplateMerges[\s\S]*?\n}\n` grammar). The head prints `RESULT divergent=0 unregistered=0 dead=0 refused=0` (ev/pre.agreement_py.txt, ev/agreement_py.txt).
- RESULT class rule: `git grep` for the block's three marker comments outside agreement.mjs returns only the helper. The cut has one owner, and no other copy is open (ev/class_rule_cut_sites.txt).
- RESULT differential against main: against bc52ad2af1d0, TOTAL lines=109740, refused_main=7445, refused_head=7445, main_not_head=0. The same numbers hold against da12aa37d (ev/head.hdiff_main_wt.txt, ev/head.hdiff_vs_da12.txt).
- RESULT argv-seam: PROGRAM-CLASS 144 of 144, view 0 of 144; WRAPPED 12 of 12, null 0; CLASS 43 of 43, null 0; CASEARM held 49 of 49; routed held 0 of 3 (ev/head.argv_summary.txt).
- RESULT census with 4aad9c117's agreement.mjs: TOTAL old=63 new=63 over 290 files, UNCOVERED 67 of 108, EXTENT 11 of 63, SPLIT 2 of 2 (ev/head.census_4aad_summary.txt).
- RESULT finder's harness, `r10_merge_subject_plants.sh` at head: unperturbed 63 merge calls in 11 files, refused=0; 22 REFUSED; 3 null plants refused=0 (ev/head.plants.txt).
- RESULT closures and classification: closures.json adds the helper to `tests/harness_headers.py`'s `inert_reads`, beside the five r10_merge_subject harnesses. `closure.py select` prints `MODE: SCOPED -- 1 script(s) run, 32 scoped out.` `entities.py` gives `2 of 2445 ENTITY CHECKS FAILED` at the head. The same two (gate-sweep.yml U0c, graders-head-copy delivery_status) fail at main da12aa37d, and neither reads a file this diff touches. This also settles the "LEDGER-MERGE: resolved tests/closures.json" merge (ev/closures_diff.txt, ev/closure_select.txt, ev/entities.txt, ev/main.entities.txt).
- RESULT ci_predict: `no closures, fast, wave-script or instrument red predicted against da12aa37dee1`. tmp_paths: 0 refused (ev/ci_predict.txt, ev/tmp_paths.txt).
- RESULT no host or home paths among the added lines: 0 lines (ev/hostpaths.txt). VERSION, the manifest and RELEASE_NOTES.md are untouched (ev/version.txt).
- RESULT merge: `git merge-tree --write-tree origin/main HEAD` exits 0 against da12aa37d and again against f54f40cc1, which main moved to during the review. No MERGE-CLAIM lines (ev/merge_tree.txt, ev/merge_tree_f54f40.txt).
- Forward-carry: handoff/audit-r10-roster 1ac59f510 holds carry[2] on R10-MERGE-SUBJECT-CASEARM. It names the three routed spellings and states its control as a precondition: plant each one at main and at the head (ev/forward_carry.txt).
- CI on this head, read from check-runs at about 17:01Z: governance/delivery-status is red, OVERDUE on #2795, main's own unrowed record. The job says "NOT a required context and a red here blocks no merge". This diff only adds this PR's own row, so the red is not this PR's. tests/mutation, arch-score, wave-script, closure-scope, budget-raise-gate, hassfest, validate-hacs and codeql JS and actions are green. The rest were still running when I read them, so the root-cause trigger cannot be judged on them yet (ev/ci_checks.txt).
- Head check: `git ls-remote` showed fix/r10-merge-subject-harden still at 3bf97d36aa37989936038feba3c69cc6ae7011c3 at verdict time. The body's Head section names 3bf97d36 as the merge of the code head 4dbc9c23 with origin/main da12aa37d.
- Architecture: the diff only changes instruments and moves four copies of the cut into one owner. Nothing breaches fixer.md step 17.
