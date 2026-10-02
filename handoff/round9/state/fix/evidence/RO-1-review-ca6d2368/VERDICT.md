blocked ca6d23682f2d99158240fd8f9b8e1553698f51a5 harness: self-test-seams-open (M, N, C, G survive); carry-missing: not carried to R9-RO-2..R9-RO-9

Review round 1 of R9-RO-1 (#1789), cloud reviewer (opus), measured at PR head ca6d2368 (code head 19f75625, base 830f84ad), and at that head merged into origin/main 5f4f641a (scratch merge 8c7befab). The head was re-read at posting time and is unchanged.

Passes:
- Ancestry 830f84ad..ca6d2368: 5 commits, no handoff/ or resume paths in any commit or in the diff. git merge-tree against origin/main: rc 0.
- Report-only: python3 tests/layout.py rc 0, MODE: REPORT; counts 3095 paths, category 2254, retired 2252, reference 1518, dead 27 (the body's 3094/2253/2251 were taken at 19f75625, before the delivery row; the delta is that one row). Self-test 14/14 ok.
- Manifest = inventory: --gen-retired on handoff/repo-reorg-plan:handoff/round9/fix/RO/inventory.tsv (4e8f6d47) gives 155 entries, set-equal to layout.json retired. Category findings less retired findings = exactly carry-1743.json and carry-1747.json (carried to RO-4 in the resume note).
- Closure: derive_closures.sh --single tests/layout.py on Linux (strace) re-records the same 2 files; only `seconds` differs (3.4 vs 4.2).
- Full gate, Python 3.14.0rc2 venv with pinned requirements-ci, GATE_SCOPE=full on the merge: ALL TEST SCRIPTS PASSED, RC=0 (gate_full_merged_8c7befab.log).
- stress.py red at f26077a6: load noise. In my full gate, not alone on the box, shoulder/tariff+cycle 251.5x of a 268x budget, ALL 87 STRESS CHECKS PASSED. The diff touches no production or solver file.
- Whole-tree gates on the merge: codeowners_gap uncovered_files=0; policy_lint TOTAL 0 errors across 40 files; structure.py STRUCTURE RATCHET PASSED.
- mutation_table.py --scope changed --base origin/main --max 10 --jobs 3: MUTATION TABLE PASSED (empty scope), rc 0. No production line, so no ledger evidence; my own mutants below are the proof.
- prepr.sh at ca6d2368: every step ok except pr-body, which refused the transport body because its Head section names 19f75625. The live PR body names ca6d2368, and CI pr-contract is green. The figure_lint step ran clean here.
- CI at ca6d2368: no red check (some still running when read).

Blocking 1, harness. 15 reviewer mutants of tests/layout.py (run_mut.py, mutants.txt). --self-test kills 8. It misses these semantic ones, and probe.py/probe.txt shows each is caught by one planted case:
- N: the retired arm skips entries with `since` set. The "reintroduces moved path" branch has no case. It is the barrier's whole job once RO-2 sets `since`. P1 (brief_lint.mjs re-added with since=9999): head (1,1,0,.), mutant (1,0,0,.).
- M: `*` crosses directories. No case plants a file below a single-star glob. P2 (.claude/rules/sub/x.md): head category 1, mutant 0.
- C: the trailing-full-stop form of a directory citation is dropped. P3 ("moved from .claude/workflows/fixtures."): head reference 1, mutant 0.
- G: --enforce never exits 1. The flip RO-9 makes is untested: self-test rc 0, enforce rc 0 under the mutant.
Survivors H (git grep error ignored), J and K (duplicate enumeration guards) and L (`?`, unused by any glob) are not blocking.
Fix: add P1, P2 and P3 as self-test cases, plus an assertion that --enforce exits 1 on a planted finding and 0 on the base tree.

Blocking 2, carry-missing (finding-propagation.md, fix-review.md step 10). handoff/audit-r9-fixplan at 6a392e29: the R9-RO-2..R9-RO-9 group entries contain none of the resume-note text (no layout.py, since, carry-1743 or --enforce). The orchestrator applies the text from handoff/round9/fix/resume/RO-1.md. No code change is needed for this item.

Non-blocking: the live body's Head section says "19f75625 merges origin/main 830f84ad into the authored head 19f75625". No such merge exists: 19f75625 sits directly on 830f84ad. Drop that sentence when the body is next edited.
