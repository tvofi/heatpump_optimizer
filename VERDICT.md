Fix review: merge 834dbf7eeba71d1b8ed120621505b0138c7e6413

bus-nonce: 9325844e3376e0134840d9930cd31fcf

Round 4. Measured head `834dbf7eeba71d1b8ed120621505b0138c7e6413`: e42b1cd plus fixer code 699c4996 plus an automatic merge of origin/main 2e7422e59. It was still the live head when I posted. I reviewed the delta e42b1cd..699c4996; the earlier rounds' findings and their evidence are in this ref's history.

## The delta

- **closures.json.** The fixer discarded the Darwin `--single` recording ("would drop 132 files"), which is consistent with Darwin missing the child processes, and committed by hand a two-line edit: `DISCLAIMER.md` into `tests/harness_headers.py`'s closure and out of its `inert_reads`. It matches the edit I simulated in round 2 exactly.
  - RESULT CI judge, `closures` job 110912614855 (strace, `SCOPE_CASE: full`): `closure: committed closures cover every file this run touched`. There is no UNDER-SCOPED line and no INERT READS line, so the hand edit is what a Linux recording asks for.
  - It is a hand edit, not a recording. That is disclosed in the body, and `ci-autofix.md` permits committing `tests/closures.json` once no bot commit is coming.
- **merge_fastpath.py:** the real-tree check now names `LICENSE`, which harness_headers.py's `inert_reads` still lists.
  - RESULT `merge_fastpath.py --self-test` at the head: `33 checks, 0 failed`.
  - The docstring now calls DISCLAIMER.md a closure read.
- **tests/run.sh:** the comment no longer calls DISCLAIMER.md INERT.
- RESULT `closure.affected(['DISCLAIMER.md'])` at the head selects `['tests/doc_claims.py', 'tests/harness_headers.py']`. The round-2 under-scope is closed.

## Re-run at this head (my harnesses, not the fixer's)

- RESULT null control: `site_findings` on the page gives 0 findings. Counts are claims 47, fragments 110, numbers 3, copy 14, features 9, docs 10, images 11, links 16, unchanged since round 1.
- RESULT finder's `check_site.py` (design 2b5031bf, impl profile): `RESULT: PASS`.
- RESULT my mutants: 16 of 16 killed. 14 are killed directly; image-in-tree and CSS-third-party need a plant keyed on their own message, as in rounds 1 and 2.
- `brief_lint.mjs`: `TOTAL: 0 error(s) across 45 file(s)`. `structure.py`: PASSED. `git merge-tree --write-tree origin/main HEAD` gives rc 0.
- `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` are untouched (three-dot diff is empty).

## CI at this head (check-runs API, 35 runs, `evidence/checkruns-834dbf7.tsv`)

- Every run is success or skipped, except one cancelled duplicate each of `pr-contract` and `budget-raise-gate`; each of those has a later success run.
- Named: `briefs`, `closures`, `fast (3.14)`, `coverage`, `coverage-ratchet`, `instrument-self-tests` and `pr-contract` (110912790327) are all success. `closures-autofix` is skipped, because closures was green.

## Red checks answered

The body's `## Red checks` names every red I blocked on in rounds 1 to 3, each with a cause and the cheaper detector:
- `briefs` (round 1)
- `closures` INERT READS (round 1)
- `closures` UNDER-SCOPED harness_headers.py (round 2)
- `instrument-self-tests` (round 3)

## Notes, not blocking

- Two comments in `tests/closure.py` still describe DISCLAIMER.md as an INERT read of harness_headers.py's children: the docstring near line 1091 ("files (DISCLAIMER.md, LICENSE, three docs/ pages)") and the comment near line 224. They are stale prose with no runtime reader. They can be fixed in this PR's next touch or in a later one.
- The closures-autofix false quiet in round 2 (main's pinned `closure.py`) is owned by the RCA and countermeasure PR the orchestrator named, not this PR.
- These are carried from round 1: the design-level third-party gaps (`<link rel=icon|preload>`, `<iframe>`) are shared with `check_site.py`; the page checks are static only. `tests/closure.py` and `tests/layout.json` are code-owned, so tvofi's approving review is still required.
