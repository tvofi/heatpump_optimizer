Fix review: blocked e42b1cdd805b011701479b3e19e2bbf4d6876dcc root-cause-unanswered: closures went red at this head (UNDER-SCOPED tests/harness_headers.py: DISCLAIMER.md, caused by this PR moving DISCLAIMER.md onto INERT_EXCEPT), unanswered; closures-autofix reported skip-not-under-scoped, so no bot commit is coming

bus-nonce: bcaa06ba1b00785784975eb3a1a72995

Round 2. The fixer's round-2 code is 910993833. 9bc802e merged it with main aab94eea, and e42b1cd is the orchestrator's merge_fastpath fixture commit on top. Measured head `e42b1cdd805b011701479b3e19e2bbf4d6876dcc`; it was still the live head when I posted. My round-1 measurements at ddaf6bf are carried forward only where the delta does not touch them; each one is marked below.

## Blocking

1. **`closures` is red at e42b1cd (job 110886379255).** The log reads: `UNDER-SCOPED: tests/harness_headers.py really reads 1 file(s) the committed closure does not list: DISCLAIMER.md`.
   - Cause: this PR's reclassification. Until this PR, `DISCLAIMER.md` was INERT, so harness_headers.py's read of it (through D6 `claims.py`, the #1823 seam) was recorded under `inert_reads`. Now `DISCLAIMER.md` is on `INERT_EXCEPT`. The same read is a closure read, and harness_headers.py's committed closure lacks it.
   - Only doc_claims.py was re-derived. At the head, `closure.affected(['DISCLAIMER.md'])` selects `['tests/doc_claims.py']` alone.
   - Gate impact is nil, because `tests/run.sh` runs harness_headers.py as `run_always`. The check is still red, and the body does not name it.
   - `closures-autofix` (same run) printed `AUTOFIX: skip-not-under-scoped`, so no `ci: re-record closures` commit is coming. It is green while `closures` printed UNDER-SCOPED. My reading is that the autofix classifies with a pinned `$RUNNER_TEMP/pinned/closure.py`, whose INERT list (main's) still holds DISCLAIMER.md. I did not open that job's source to confirm. It looks like a fourth green-unrepaired path beyond the three `ci-autofix.md` lists, and that is the orchestrator's to route (root-cause seat or the autofix lane), not this PR's.
2. **The owed repair turns a self-test red.** The repair is `./tests/derive_closures.sh --single tests/harness_headers.py`; Python lanes record through `sys.addaudithook`, so Darwin is sound.
   - That re-derive moves `DISCLAIMER.md` from harness_headers.py's `inert_reads` into its closure.
   - `tools/audit/merge_fastpath.py`'s check "this tree's table records harness_headers.py's INERT reads, DISCLAIMER.md among them" (around line 336) then fails. I simulated the table change in place and restored it: `merge_fastpath self-test: 33 checks, 1 failed` (`evidence/merge_fastpath-after-simulated-rederive.txt`).
   - e42b1cd's probe swap left that check, and the docstring at lines 38-46, naming DISCLAIMER.md.
   - The fixer owes three things in one commit: the re-derive, a re-pointed check naming an INERT file harness_headers.py still reads (`LICENSE` or one of the docs/ pages its `inert_reads` lists), and the stale comment at `tests/run.sh` around line 471 ("opens INERT docs ... DISCLAIMER.md"). Then name the red in `## Red checks`.
   - Alternative for tvofi: keep `DISCLAIMER.md` INERT and record it in doc_claims.py's `inert_reads`. That is exactly what round-1's `INERT READS UNDER-APPROXIMATED` asked for. The cost is that a DISCLAIMER.md-only edit would skip doc_claims.py on a branch. `closure.py`'s own docstring calls moving these files into a closure "a reclassification for the owner". `tests/closure.py` is code-owned, so this choice is tvofi's at the review in either case.

## The round-2 delta: what I verified

- **carry-1645.json:** all five re-pointed pins (468, 479, 557, 597-611, 604) land on the same text the old pins (463, 474, 552, 592-606, 599) held at the merge base, line for line, +5 for the docstring's five lines. `brief_lint.mjs` on that file gives `TOTAL: 0 error(s)`; on all carry files, `TOTAL: 0 error(s) across 45 file(s)`. CI `briefs` is green at 9bc802e and e42b1cd.
- **The arm:** it moved below the pinned functions, and its body is byte-identical apart from the two imports, now placed beside it with `# noqa: E402`. CI `typing` is green.
- RESULT null control at 9bc802e (arm and page unchanged in e42b1cd): 0 findings. Counts are identical to round 1 (claims 47, fragments 110, numbers 3, copy 14, features 9, docs 10, images 11, links 16).
- RESULT finder's `check_site.py` (design at 2b5031bf, impl profile): `RESULT: PASS`, same counts.
- RESULT my mutants: 16 of 16 killed. 14 are killed directly; image-in-tree and CSS-third-party need a plant keyed on their own message (`evidence/rev_mut-9bc802e.txt`).
- **closures.json:** doc_claims.py now holds `DISCLAIMER.md` and `docs/index.html`; the entities.py orphan is gone. CI `fast (3.14)` is green at e42b1cd. The `a3:` FAIL lines in its log are that script's own planted controls, present at round 1 too.
- **entities.py docs-only example → SECURITY.md:** correct. At the head `is_inert('SECURITY.md')` is True, and SECURITY.md sits in no closure and no `inert_reads`.
- **merge_fastpath.py probe swap (e42b1cd):** `--self-test` gives `33 checks, 3 failed` at 9bc802e and `33 checks, 0 failed` at e42b1cd (`evidence/merge_fastpath-selftest-base-vs-9bc802e.txt`). The probes still exercise an INERT, unrecorded file, which is their intent. CI `instrument-self-tests` is green at e42b1cd.
- `git merge-tree --write-tree origin/main HEAD` gives rc 0. `VERSION`, the manifest, `RELEASE_NOTES.md` and `tests/golden/` are untouched (three-dot). `structure.py` passes.
- **CI at e42b1cd:** everything completed is success or skipped except `closures`. `pr-contract` was re-running when I posted, and I do not report its result. The check-run list is in `evidence/checkruns-e42b1cd.tsv`.

## Carried from round 1 (unchanged by the delta)

- Deviations (a) to (d) are justified.
- The page checks are static only.
- The design-level third-party gaps (`<link rel=icon|preload>`, `<iframe>`) are non-blocking and shared with `check_site.py`.
- The fixer installed packages into a venv; the orchestrator relays that tvofi approved it.
