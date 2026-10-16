Fix review: merge 1755a8a7df54093861beba00610825dd0e9f46ae
bus-nonce: 0bc180b164bbe62295d6e9ba845d019f

Round 2. Measured at head 1755a8a7df54093861beba00610825dd0e9f46ae from a detached worktree, merge base 97f419d0c. The contract preamble (`git diff <mb>...origin/main -- dev/governance/roles/`) is empty. The head was re-read before posting and is unchanged.

## Round-1 blockers

1. **The three requirements are restored.** D6.md step 2 again carries `services.yaml` examples fed through the schemas, "(provisional under the fan-out)", and "the tag list in the export's `manifest.json`" (evidence/d6_diff.txt).

   I judged each of the three cuts that pay for them:
   - **The source file list became "the files your cells name".** This is spent. The D6 universe in scopes.json lists every file the old list named, including hacs.json and the seven `docs/*.md` by name, so the audit records are still excluded by construction. The cells also carry the web sources (`docs/index.html`, `docs/site/*.css`, `tools/site/build_docs.mjs`). One source of truth replaces two.
   - **The exposure sentence.** This is spent. COMMON.md line 22 binds it for every dimension and names D6: "If your brief makes you read `docs/` (D5, D6) ... record it under `exposure`". Line 94 requires `exposure` in REPORT.md.
   - **The version and feature list against README/RELEASE_NOTES.** This is spent. It was round 1's own addition, not a pre-existing requirement. tests/doc_claims.py arm 1b (R9-WEB-1, lines 2225-2560) enforces the same thing in CI for docs/index.html: page features equal the README "What it does" leads both ways, the page states no version and no version literal, docs cards equal the README Documentation table, and every claim is checked against its reader section. Live-vs-tree drift is the separate tag diff.
   - **Cap.** RESULT policy_lint --budgets: rc 0; D6.md 31/35 lines, 375/388 tokens; corpus ~61069, down from main's ~61082. No `*_budgets.json` is in the diff.

2. **Anchors are checked by an in-tree harness that can fail.**
   - RESULT d6_page_anchors.py, tree page and live page: rc 0, ids=29, internal_hrefs=14, distinct=10, unresolved=0, on both (evidence/harness.txt).
   - RESULT perturbation, the docstring's own (`id="main"` renamed): rc 1, `unresolved=1 ['main']`.
   - RESULT empty set (a page with no internal href): rc 1. The empty-set refusal holds.
   - RESULT sub-pages built by `build_docs.mjs --out`: 9 pages, rc 0, unresolved 0 on each. Live setup.html: rc 0.
   - Note, not blocking: the harness resolves in-page `#x` only. The 7 distinct cross-page `page.html#x` links are resolved by build_docs.mjs itself, which refuses "anchor #x is not a heading of page" (lines 171-175). Its build printed `anchors 39 ... RESULT: PASS`, and the file is in D6-s1's cells, so the class is covered.
   - Classification: the harness is added to tests/closures.json beside its siblings. The coordinator reports it is classified under harness_headers' inert_reads. I did not re-derive that list, and `closures` and `briefs` are green in CI.

3. **Drift is measured against the deployed tag.** The step now reads "Pages deploys the latest `v*` tag: diff the live page against its `docs/index.html`, not the baseline's". This matches `.github/workflows/pages.yml` lines 6-8. RESULT: the live page is byte-identical to v7.0.0:docs/index.html (cmp).
4. **Sub-pages are owned.** `tools/site/build_docs.mjs` is in D6-s1's cells, and step 2 names the sub-pages under D6-s1.
5. **The `_comment` nit is fixed.** corpus_excluded.json's `_comment` now names `docs/index.html` as a user-facing page, on README.md's ground.

## Scopes

RESULT check_scopes --ref head: rc 0, `ok D6 mode=files seats=3 universe=18 [s1:5f, s2:7f, s3:6f]`, no FAIL.

Null controls:
- s2 back to `docs/**`: rc 1, "owned twice" for docs/index.html and docs/site/docs.css.
- build_docs.mjs removed from s1, with s3 `rest` replaced by its explicit list: rc 1, "unowned" for tools/site/build_docs.mjs.

## Checks and merge

RESULT check-runs at head (API, paginated): 45 runs fetched, 30 success and 15 skipped, none red or in progress; all 17 required contexts in ruleset 23698884 concluded success (evidence/required.txt).
RESULT merge-tree against origin/main 97f419d0c: rc 0, no conflict.

No production line changed, so no mutation proof applies. Forward-carry: none owed, because the brief is the stage. Owner approval of the policy change remains to come: the body's `## Approval` cites the 2026-10-15 request and mandate 6175172275.
