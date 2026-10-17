Part of #201 (the round-10 programme). There is no issue for this. It is the owner's direct request of 2026-10-15: "add a web page check to dimension d6". It is policy (`dev/governance/dimensions/D6.md`, capped), so it needs the owner gate. The orchestrator merges it under mandate 6175172275.

Round 2 answers the blocked verdict at 69f04ec61 on three items.

What changes:
- `dev/governance/dimensions/D6.md`:
  - **Restored.** The three requirements round 1 deleted to fit the cap are back: the `services.yaml` examples fed through the voluptuous schemas, "(provisional under the fan-out)" on performance claims, and the tag list "in the export's `manifest.json`".
  - **Anchors.** A HEAD request never sends the `#fragment`. Step 2 now checks anchors on the web page and its sub-pages, in the tree and on the live site, with `dev/audit/harnesses/d6_page_anchors.py`. The harness fetches each page, parses its `id`s, and fails every internal `href="#x"` with no `id="x"`.
  - **Drift.** Pages deploys on a `v*` tag (`.github/workflows/pages.yml`), so the live page is diffed against `docs/index.html` at the latest `v*` tag, never at the baseline.
  - The method keeps three steps, so `D6.M1`–`M3` and the scopes' step lists are unchanged.
- `dev/audit/harnesses/d6_page_anchors.py` (new): the anchor check, landed under `fixer.md` step 18 because a later D6 seat reruns it. It is classified in `tests/closures.json` under `inert_reads["tests/harness_headers.py"]`, because that script's `_scope_paths()` reads every file under `dev/audit/harnesses/`. `closure.orphan_files()` returns `[]`.
- `dev/audit/config/scopes.json`: the sub-pages `tools/site/build_docs.mjs` renders are assigned to D6-s1. The generator joins D6's universe and s1's cells, because it is where the sub-pages' own text (nav labels, the README blurb, footer links) lives. Their body text is the markdown that s1 (README) and s2 (`docs/*.md`) already check. s2 stays `docs/*.md`. The round-1 cells (`docs/index.html`, `docs/site/*.css` on s1) are kept.
- `dev/governance/config/corpus_excluded.json`: the `_comment` said that every entry holds a finder report or a round baseline, which made it false for `docs/index.html`. It now also names a user-facing page, on the same ground `policy_lint.mjs`'s own `CORPUS_EXCLUDED` uses for `README.md` and `DISCLAIMER.md`. The `docs/index.html` entry itself stays, because D6.md still names the file.

**Paying for the step (ratchet-budgets.md, in order). No cap is raised.** Three cuts, each prose that is spent or stated elsewhere:
1. Step 1's enumerated source list became "the files your cells name". It duplicated D6's universe in `dev/audit/config/scopes.json`, which `check_scopes.py` enforces and `audit-find.js` hands to each finder ("YOUR CELLS"). The copy had already drifted: it omitted the sub-pages, which was the verdict's item 3.
2. "Record the audit-era documents you had to open in `exposure`." `COMMON.md` states this for D6 by name ("If your brief makes you read `docs/` (D5, D6) …"), and the seat reads COMMON.md first.
3. Round 1's "its version and feature list against `README.md` and `RELEASE_NOTES.md`". `tests/doc_claims.py` arm 1b (R9-WEB-1) carries this mechanically: it refuses any version literal on the page, the page's `data-feature` headings must equal README's "What it does" leads, and its docs cards must equal the Documentation table. The live page is the tag's copy, which that arm checked, and the drift diff ties the two together.

Considered and not taken:
- "Read `COMMON.md` first": verifier and catch-up seats are not dispatched by `audit-find.js`.
- "D5 owns structure and flow": a D6 seat never reads D5.md.
- The owner's quote: those are the owner's own words.
- Shortening any restored requirement: that was the round-1 defect.
- Moving prose to another file: moved prose is not a payment.

## Approval

tvofi, relayed by the orchestrator on 2026-10-15, verbatim: "add a web page check to dimension d6". This is the owner's direct request, not a seat's finding. Still to come: the owner's approving review at the head, and the orchestrator's merge under mandate 6175172275. No budget raise is in this diff, so `budget-raise-gate` has nothing to gate.

## Head

`1755a8a7df54093861beba00610825dd0e9f46ae` merges the authored code head `d5b85a50124d5b1f4eb2df03e5fe8a39d7cf4bc7` and then merges origin/main `97f419d0c` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below) into this PR's previous head.

`d5b85a50124d5b1f4eb2df03e5fe8a39d7cf4bc7`

## Mutation proof

- `python3 tools/audit/check_scopes.py --repo . --ref d5b85a50124d5b1f4eb2df03e5fe8a39d7cf4bc7 --self-test` prints `SELF-TEST passed (both perturbed scopes refused)`.
- Perturbed cell, overlap: add `tools/site/build_docs.mjs` to s2's files. Exit 1, `owned twice ('tools/site/build_docs.mjs',) by ['s1', 's2']`.
- Perturbed cell, gap: drop it from s1 and replace s3's `rest` with its explicit three entries. Exit 1, `unowned ('tools/site/build_docs.mjs',)`.
- Anchor harness perturbed: in a copy of `docs/index.html`, rename `id="main"` (the first `href="#…"` target). `python3 dev/audit/harnesses/d6_page_anchors.py <copy>` reports `unresolved=1 ['main']` and exits 1.

## Null control

- HEAD cannot see anchors. `curl -sI 'https://tvofi.github.io/heatpump_optimizer/#no-such-id-zz'` returns `200`, which is the round-1 step's false `true`.
- `python3 dev/audit/harnesses/d6_page_anchors.py docs/index.html https://tvofi.github.io/heatpump_optimizer/` prints `ids=29 internal_hrefs=14 distinct=10 unresolved=0` for both pages and exits 0. The harness also fails a page with no internal href, so it cannot pass on an empty set.
- Sub-pages: `node tools/site/build_docs.mjs --root . --tree <ls-files> --out <dir> --mermaid none` builds 9 pages. The harness over those 9 files, and over the same 9 names on the live site, reports `unresolved=0` for every page.
- Drift: `git describe --tags --match 'v*' --abbrev=0 origin/main` is `v7.0.0`. The live page is byte-identical (`cmp`) to `v7.0.0:docs/index.html`, and `docs/index.html` has no diff between `v7.0.0` and `origin/main`. The perturbed copy against the live page: `cmp` exits 1.

## Figures

- `python3 tools/audit/check_scopes.py --repo . --ref d5b85a50124d5b1f4eb2df03e5fe8a39d7cf4bc7` exits 0 and prints `ok D6 mode=files seats=3 universe=18 [s1:5f/0loc, s2:7f/0loc, s3:6f/0loc]`, with no `FAIL` line for any dimension. `--seat D6-s1` lists `DISCLAIMER.md`, `README.md`, `docs/index.html`, `docs/site/docs.css`, `tools/site/build_docs.mjs`.
- `node tools/policy/policy_lint.mjs --budgets` exits 0 and prints `tools/audit/briefs/D6.md 31 35 375 388`.
- `node tools/policy/policy_lint.mjs` exits 0. `node tools/policy/brief_lint.mjs` exits 0. `node tools/policy/rules_sync.mjs --check` exits 0. `python3 -I tools/audit/seat/tmp_paths.py --check` reports 0 refused.

## Red checks

none

## Forward-carry

none. The D6 brief is the stage that runs these checks, and this pull request is the edit to it.

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
