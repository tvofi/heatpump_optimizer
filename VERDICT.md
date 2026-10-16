Fix review: blocked 69f04ec613a14a4f50cb55b10820e411716ac993 policy-regression: D6.md pays its cap by deleting two method requirements, and its web step names an inexecutable anchor check and the wrong drift reference
bus-nonce: a25a4bbd8adc9f6bbaec58808312f6cb

Round 1. Measured at head 69f04ec613a14a4f50cb55b10820e411716ac993 (re-read before posting: unchanged), merge base 39b77a467, from a detached worktree. Contract preamble (`git diff <mb>...origin/main -- dev/governance/roles/`) is empty, so fix-review.md is current.

## What holds

RESULT check_scopes head: rc 0, `ok D6 mode=files seats=3 universe=17 [s1:4f, s2:7f, s3:6f]`, no FAIL in any dimension (evidence/check_scopes_head.txt). D6-s1 owns DISCLAIMER.md, README.md, docs/index.html, docs/site/docs.css; s2 and s3 cells are unchanged from the base scopes (evidence/d6_seat_cells.txt).
RESULT null control, overlap (s2 back to `docs/**`): rc 1, `owned twice` docs/index.html and docs/site/docs.css (evidence/null_controls.txt).
RESULT null control, gap (docs/site/*.css removed from s1, s3 `rest` replaced by its explicit list): rc 1, `unowned docs/site/docs.css`.
RESULT policy_lint --budgets: rc 0; D6.md 32/35 lines, 388/388 tokens; corpus ~61082 against 61026+500, identical to origin/main; no `*_budgets.json` in the diff, so no raise.
RESULT rules_sync --check: rc 0. brief_lint: rc 0. Neither file class is touched by the diff.
RESULT corpus_excluded: justified. The entry exists because D6.md now names docs/index.html and `named-docs` refuses a named uncapped document. The page is user-facing on the same ground as README.md and DISCLAIMER.md, which sit in policy_lint.mjs's own CORPUS_EXCLUDED as `user-facing`. It is a public product page, not a place to move prose to, so this is not a cap dodge. One nit: the data file's `_comment` says each entry is "a finder report or a round baseline". This entry is neither, so the comment is now false for one entry.
RESULT check-runs at head (API, paginated): 45 runs fetched, 30 success and 15 skipped, none red or in progress. All 17 required contexts in ruleset 23698884 are concluded success (evidence/required.txt).
RESULT merge-tree against origin/main 2e452a182: rc 0, no conflict.

## Why blocked

1. **Requirements deleted to fit a zero-headroom cap, described as "tightening".** D6.md sits at 388/388 tokens. The body says the added lines "are paid for by tightening D6's own wording". The diff (evidence/d6_diff.txt) also removes three things a seat had to do:
   - `services.yaml` examples fed through the voluptuous schemas. Only "service fields against the voluptuous schemas" remains, so a seat no longer has to execute the published examples.
   - "(provisional under the fan-out)" on performance claims, which governed how such a verdict is qualified.
   - "the tag list in the export's `manifest.json`" became "the tag list", which drops the named source.

   Each of these changes what a D6 seat must do. CLAUDE.md rule 2 and ratchet-budgets.md say not to delete working functionality merely to fit. Instead, pay elsewhere or stop and ask, and a raise goes to the owner (under R10 grants, only when unpayable). The owner asked for a web check to be added, not for these checks to be removed. Fix: restore the three, then pay or ask for the difference.

2. **"links and anchors with a HEAD request" cannot be executed for anchors.** A fragment is never sent to the server, so a HEAD request returns the page's status whether or not the `#id` exists. docs/index.html has 29 `id=` attributes and 10 distinct internal `href="#…"` links. As written, the step yields a `true` verdict for a broken anchor. The step needs a check that can fail, for example resolving each `#frag` against the fetched page's ids.

3. **The published-drift reference is wrong.** The step says "the live page against `docs/index.html` at the baseline". `.github/workflows/pages.yml` (lines 6-8) deploys on a pushed `v*` tag. The live page is therefore the last stamped release, not main and not the round baseline. Whenever a page edit lands between stamps, or the baseline is not that tag, the step reports drift that is just the release cadence. The reference should be `docs/index.html` at the latest `v*` tag. Diffing it against the baseline is the staleness check, which is a separate claim. The same file shows that the live site also serves sub-pages rendered by `tools/site/build_docs.mjs` from the tag's markdown. The brief's source list (`docs/index.html`, `docs/site/`) does not name them. Say whether s2's markdown check covers them or the s1 page check does.

   Measured today, the live page is byte-identical to docs/index.html at both the head and origin/main (evidence/live_page.txt), so nothing fires now. This is a construction defect, not an observed false positive.

COMMON.md finding shape: D6 keeps "Read `COMMON.md` first" and the claims-table harness output. The web claims flow into the same table, which is adequate. The harness contract for the two web-only checks (items 2 and 3) is what is missing.

No mutation proof applies, because no production line changed. The body's self-test and hand perturbation are consistent with my two null controls. Forward-carry: none owed.
