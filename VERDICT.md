Fix review: blocked ff87c3d44ddcd1c18199cc7ce9fad5d5bb656fd7 root-cause-unanswered: briefs went red, unanswered (this diff's +8 lines in tests/doc_claims.py move a line-cited symbol in .claude/workflows/carry-1645.json out of brief_lint's window; pr-contract, a required check, refuses on it)

bus-nonce: 6b5cfb2fdb55dde86ef0680c701f1cd0

Round 1. PR #1864 (R9-WEB-3), head ff87c3d44ddcd1c18199cc7ce9fad5d5bb656fd7. I re-read the live head at 2026-10-02T21:15:26Z and it had not moved. The authored code head is a9440930. The head adds a merge of origin/main (#1861) and the PR's own delivery row on top of it. Evidence is in evidence/; HEAD.txt names the head. I prepared this review from a detached worktree at the head, with a second one at the merge base 687e15b6.

## Owed before merge (three items)

1. **briefs is red, and the PR causes it.** `node .claude/workflows/brief_lint.mjs` exits 1 at the head and 0 at the merge base:
   - RESULT head: `[carry-1645.json carry 0] path:line: tests/doc_claims.py:468: 'check_simulate_plan_fields' not found near tests/doc_claims.py:468; found at line 567 instead`
   - RESULT base: carry-1645.json `0 error(s)`
   - The function is defined at line 559 at the base and at line 567 at the head. The shift is this PR's 7 docstring lines plus `import subprocess`.
   - The body's `## Red checks` still says "none yet at this head". pr-contract therefore fails with `check briefs is red and ## Red checks does not name it`.
   - Fix: re-key the line citations in carry-1645.json against the head. Then answer briefs in the body: the cheaper detector is brief_lint run locally before the push, already in the lesson list.
2. **The third-party rule does not cover the stylesheet every built page links (dispatch item 2).** `subpage_findings` scans each built page's HTML. `docs/site/docs.css` is a separate file, and no arm scans it for `url(` or `@import`. The product page's styles are inline, so its CSS is scanned; the sub-pages' CSS is not. My controls (`evidence/reviewer_controls.sh`, my own instrument) give:
   - RESULT C1, `@import url("https://fonts.googleapis.com/...")` prepended to docs/site/docs.css: `ALL 147 checks PASSED`
   - RESULT C2, one `@font-face src` changed to `https://fonts.gstatic.com/x.woff2`: `ALL 147 checks PASSED`
   - The check "no built page requests anything from a third party" therefore claims more than it checks. A third-party font is the case the WEB-1 carry was about.
   - Fix: apply the url()/@import rule to docs/site/docs.css, or to every stylesheet a built page links, and add a planted control that turns it red.
3. **The triage of the duplicate-page-name survivor is wrong; that mutant is not equivalent.** The body says the build "stays red without that message" because one page overwrites the other's heading set. That holds only for the fixer's control tree, whose documents carry anchors. Take a planted tree with two anchor-free documents, docs/a.md and docs/x/a.md (C3):
   - RESULT real build: `FAIL two documents would be built to one page name`, rc 1
   - RESULT mutant (that `errors.push` turned into `void 0`): `RESULT: PASS`, and only one a.html is written; one document is silently lost.
   - The arm's row check compares source keys, so it does not catch this either.
   - Fix: use an anchor-free control for that site, so 9 of 10 build sites are killed. The zero-pages survivor stays.

## Verified

- **Build arm (item 1).** At the head, `node tools/site/build_docs.mjs` printed `pages 9, pageLinks 51, anchors 39, githubLinks 19, images 21, badges 4, external 17, mermaid 8`, `RESULT: PASS`. It excludes docs/backlog.md. Over the merge base's docs it printed the same stats and PASS, so no docs defect is hidden.
  - I re-ran the fixer's docs_controls.py (sha1 211e96e0f9cc, matching the body). RESULT `baseline: exit 0, 0 FAIL line(s)`, then 12 RED lines and `every control red, baseline green`.
  - doc_claims: RESULT head `ALL 147 checks PASSED`, base `ALL 121 checks PASSED`. md_tables: RESULT 0/0/0.
  - The arm's anchor (`len(pages) > 0`) is live. The build's own `zero pages built` site is unreachable, because the README is always row 0 and a missing README throws first. I accept that survivor as equivalent.
- **Icon, preload and iframe (item 2).** On HTML, the rule fires on the product page and on a built page for all three tags. The script and image plants on the built page also fire. Same-origin and `data:` icons are not refused. The arm mutation runs below kill every predicate line. The gap is CSS only (owed item 2).
- **Mermaid pin (item 3).** package.json has `"mermaid": "12.1.0"`, an exact pin. In the lockfile (v3), `packages[""]` equals package.json's dependencies and `node_modules/mermaid` is 12.1.0 with an integrity hash. All 117 packages are resolved from registry.npmjs.org with an integrity hash, every declared dependency resolves inside the tree, and none has an install script. This was a static check only. I did not run `npm ci`, which would download from the network.
- **Mutation proof (item 4).**
  - Build: I re-ran mutate_build.py (5cf926785c5e). RESULT 8 KILLED, 2 SURVIVED (lines 50 and 227), matching the body. My judgement: line 227 is equivalent; line 50 is not (owed item 3).
  - Arm: mutate_arm.py counts any crash of its driver as a kill and has no baseline run. Run from a path where arm_driver.py did not resolve, it reported 31 of 31 killed while every mutant had crashed. I re-ran it with a revised harness (`evidence/mutate_arm_rev.py`, my edit: a crash is not a kill, and the diff is three-dot from the merge base). RESULT baseline `in_tree_failures=0 anchor:RED untracked-link:RED`, 0 crashes, `SURVIVORS: 1`, L2339 `if kind == "third-party":` in the control loop. The fixer's 30 of 31 reproduces. I accept that survivor: it is a test-code mutant, and the product-page plants and the built-page script plant pin the shared `_site_requests` path.
  - CI `mutation` is green, but this diff changes no custom_components line, so it drew no mutant. It proves nothing here.
- **Closures (item 5).** The CI `closures` job ran in `SCOPE_CASE: full` and recorded tests/doc_claims.py and tests/entities.py on Linux. It printed `closure: committed closures cover every file this run touched`, with no UNDER-SCOPED and no skip-failed-recording. The Mac hand recording is therefore complete; no hand-merge of the Linux recordings is owed. tools/site/package.json is in doc_claims.py's closure, because the pin check reads it, and it is not in INERT. tests/closure.py is untouched.
- **Classification (item 6).** tests/layout.json has `tools/site/**`, and .github/CODEOWNERS has `/tools/site/ @tvofi`. tvofi's approving review is owed for the code-owned paths, as the body says.
- **nightly-status (item 7).** It is red on main. The diff reaches no reporter input: its only delivery row is the PR's own docs/delivery/1864.md, and it touches no plan, no HANDOVER.md and no nightly script. It is not this PR's.
- **CI (item 8).** waitci printed `DONE total=35`, with NOTGREEN `briefs`, `nightly-status` and `pr-contract`.
- **Other checks.**
  - VERSION, the manifest, RELEASE_NOTES.md and the goldens are untouched.
  - `git merge-tree --write-tree origin/main HEAD` exits 0 with no conflict.
  - Forward-carry: the R9-WEB-2 group brief on handoff/audit-r9-fixplan carries `npm ci` in tools/site/, the generator run and the copy of mermaid to `_site/site/mermaid/`.

## Not blocking (worth a line)

- On a built page, `subpage_findings` checks `src or srcset` only at the start of the string. `<img src="x.png" srcset="https://... 2x">` passes it, and the build's RAW_EXTERNAL regex passes it too. No doc has this today.
