Fix review: blocked 75b30a4e28e8e5ee8573720043c31f570f1e345f gate-red: tests / briefs fails at this head because the two imports added to tests/doc_claims.py move carry-1645.json's cited anchor tests/doc_claims.py:476 out of brief_lint's one-line window, and the body says Red checks: none

bus-nonce: 216b0eedae31d67e7a810a5d52be8a6b

Round 1. Reviewed head `75b30a4e28e8e5ee8573720043c31f570f1e345f`. The branch head is still `75b30a4e28e8e5ee8573720043c31f570f1e345f` (git ls-remote just before writing this verdict). Roles diff `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.

## Block

- `tests / briefs` (check run 124286240264, run 41120609154, on the PR merge ref 5a7c99dc4) concluded **failure**. Its one live error is `dev/programme/carries/carry-1645.json`: `tests/doc_claims.py:476: 'check_simulate_plan_fields' not found near tests/doc_claims.py:476; found at line 570 instead`. I reproduced it locally:
  - `node tools/policy/brief_lint.mjs` at origin/main a9ba3022e prints `TOTAL: 0 error(s) across 48 file(s)` (rc 0).
  - The same command at the merge of this head into origin/main (tree 5a8262432) prints `TOTAL: 1 error(s)` (rc 1), with exactly that carry-1645 error.
  - This PR caused it. The hunk `@@ -52,0 +53,2` adds `import collections` and `import itertools`, which shifts every later line of tests/doc_claims.py by 2. carry-1645's single-line citation `tests/doc_claims.py:476` (`check_initial_setup_menu`) gets brief_lint's ±1-line window (brief_lint.mjs:422 `pad = exact ? 0 : 1`). Main's offset is within that window; this head's is not.
- The body's `## Red checks` says `none`. That is wrong at this head: defect-root-cause.md's second trigger fired and was not answered.
- A cheaper detector existed: `node tools/policy/brief_lint.mjs` runs in seconds. It did not run before the handoff because tools/pr/prepr.sh step 3f (≈3649-3664) runs brief_lint only when a pinned path changed, and tests/doc_claims.py is not pinned. tools/pr/ci_predict.py does not model the `briefs` job.
- Repair, for the fixer:
  - Update carry-1645.json's citation; preferably cite the function by name rather than by line.
  - Run brief_lint at the merge.
  - Answer the red check in `## Red checks`.
- I did not wait for the remaining in-progress workflows or for a `pr-contract` run, because this block is on the defect, not on the root-cause wording. The four root-cause classes under fix-review.md step 11 apply once those runs conclude.

## Findings

- prepr.sh's brief_lint step is gated on pinned paths. brief_lint, though, resolves `path:line` anchors into any tracked file, so a diff that only shifts lines in an unpinned file (here tests/doc_claims.py) skips the local step and goes red on CI's `briefs` job. ci_predict.py does not model `briefs` either. This is the cheaper-detector gap behind the block; the fixer names it in the body's `## Red checks` answer. Carry: R10-ARCH-DOCS-WIRING
- On the live pages, a rename of a real ledger kind in tools/audit/seat/ledger.py's `KINDS` turns no check red: `handoff-no-pr` renamed in KINDS gives 0 findings (ev/artifact_perturbations_head.txt). Every kind dev/README.md lists sits on lines marked `[target: R10-ORCH-MACHINERY]` (dev/README.md:288-291), so it becomes `pending`. That group is `done`, so the marker is due, but the gate does not fail on a due marker, by item 2 of the brief (`--markers` exits 1 and is not gate-wired). The fixture arm does pin the predicate: mutant M2 is killed. So the live ledger-kind wiring is only hard once arm B resolves those markers. R10-ARCH-DOCS's roster carry 7 already states this as its job ("makes 'no unresolved target marker on main' a hard check"). The precondition arm B must carry: until then, a KINDS rename on main is green. Carry: R10-ARCH-DOCS
- The body's two `## Forward-carry` items are not yet written into R10-ARCH-DOCS's roster brief on handoff/audit-r10-roster (read at 82e715b43; no carry names `stage-mismatch`, `absorb-edge-missing` or `record-owed`, or the health checklist crop at the 860 px viewport). The substance is covered by that group's carries 6 (health pictures and text) and 7 (resolve the marker delta with this group's checker), but the specifics are not. finding-propagation.md requires them in the tree before this PR merges, and the body should name the roster SHA that holds them. Carry: R10-ARCH-DOCS

## Evidence

- RESULT mutation: 12 mutants in tests/doc_claims.py, each killed (rc=1, the named fixture checks FAIL); the file was restored byte-identical (`git diff --quiet`). M1-M7 are the body's own; M9 (matrix), M10 (service), M11 (module list), M12 (theme twin) and M13 (diagram `Class.method`) are mine. ev/mutants_head.txt; driver ev/mut.py.
- RESULT real-artifact perturbations, through `named_element_findings` over the real pages with one artifact edited in memory (driver ev/perturb.py, my own instrument, not the finder's; the group has no committed finder harness, being an instrument group):
  - null: 0 findings, 5 pending
  - ci.yml job `prelude` renamed: 1
  - tests.yml matrix `3.14` changed: 1
  - bus.sh `push-verdict` renamed: 1
  - heartbeat.sh `--once` renamed: 1
  - services.yaml `simulate_plan` renamed: 1
  - module `sysid` removed from the tree: 1
  - inputs.py `class InputReader` renamed: 2 (prose and diagram)
  - ledger KINDS `handoff-no-pr` renamed: 0, the pending case above
- Every element kind is read from its defining artifact (ast, the workflow's job block, the KINDS assign, the package tree, services.yaml keys, the script text). None is from a list in the test.
- RESULT null control: `PYTHONPATH=tests/hastub:tests:custom_components python3 tests/doc_claims.py` gives `ALL 230 checks PASSED` both at the head and at the merge with origin/main a9ba3022e (docs/architecture.md is unchanged by this PR). ev/doc_claims_head.txt and ev/doc_claims_merged.txt.
- Re-derived body figures:
  - class counts `file 132, module 19, ledger kind 19, job 11, symbol 9, argument 6, service 3; findings 0, pending 5`: match.
  - markers: the body's `25 of 28 due` matches `--markers` against the tree's roster (rc 1, 5 UNRESOLVED lines; ev/markers_head.txt).
  - agreement: `RESULT divergent=0 unregistered=0 dead=0 refused=0`, `AGREEMENT ok`.
  - scope: `closure.py select` prints `MODE: FULL`.
  - The card pixel-diff percentages and the cross-machine sizes come from the previous seat's scratch driver; I did not re-derive them.
- Merge: `git merge-tree --write-tree origin/main 75b30a4e28e8e5ee8573720043c31f570f1e345f` exits 0 with tree 5a82624326caa90fa3c2592ad1e4c92c73757722 and empty stderr: no conflict, and no claim file touched.
- Scope of the out-of-diff-looking changes:
  - docs/img/card/*.png, pages.json, docs/index.html (advisor height 616→708) and tests/card_browser.mjs are item 3 of the group's brief (P40) on the roster. The index.html edit is the declared size following the regenerated advisor figure.
  - The corpus_excluded.json `_comment` is roster carry 2 of this group.
  - The closures.json and INERT_EXCEPT entries are the files doc_claims.py now opens.
  - Nothing out of scope.
- Classification: `tests/closure.py selftest` gives `ALL 117 closure shrink pins PASSED`; `tests/structure.py` gives STRUCTURE RATCHET PASSED; `tests/layout.py` is ok. CI `tests / closure-scope` is success.
- The new docs/img/card/pages.json is in doc_claims.py's recorded closure and in INERT_EXCEPT.
- My local tests/entities.py run had not finished when I wrote this; I cite the body's run and CI for it.
- Self-test arms in CI:
  - The doc_claims arms run in its `main()`, which is a gate script.
  - card_browser.mjs's P40 lines run in `tests / browser`, which concluded success at this head. So the committed record reproduces on CI's machine.
  - `--markers` is not gate-wired, by the brief.
- CI at this head when I wrote this verdict:
  - failure: `tests / briefs`
  - success: browser, typing, mutation, arch-score, closure-scope, delivery-status, wave-script, env-matrix, policy-docs, hassfest, validate-hacs, budget-raise-gate, nightly-status
  - in progress: fast (3.14), closures, coverage, arch-instrument, instrument-self-tests, codeql python
- VERSION, the manifest and RELEASE_NOTES.md are untouched by the diff.
- Code-owned paths: tests/closure.py, tests/closures.json and dev/governance/config/corpus_excluded.json need @tvofi's approving review at merge. I note this for the merge seat only; it does not block.
