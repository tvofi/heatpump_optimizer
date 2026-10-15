Part of #201 (the round-10 programme). No issue exists for this: it is the owner's direct request of 2026-10-15 ("add a web page check to dimension d6"). It is policy (`dev/governance/dimensions/D6.md`, capped) and needs the owner gate; the orchestrator merges it under mandate 6175172275.

What changes:
- `dev/governance/dimensions/D6.md`: step 1 adds the web page as a claim source (`docs/index.html`, `docs/site/`, the published GitHub Pages site). Step 2 adds the page checks: the live page against `docs/index.html` at the baseline (published drift), links and anchors with the HEAD request, and its version and feature list against `README.md` and `RELEASE_NOTES.md`. Each claim on the page is a step-1 claim, so it takes step 2's code-and-data check like any other. The added lines are paid for by tightening D6's own wording; no cap moves.
- `dev/audit/config/scopes.json`: D6's universe gains `docs/index.html` and `docs/site/*.css` (the claim-bearing part of `docs/site/`; the fonts are not). Exactly one seat owns them, D6-s1, whose README is the page's staleness reference. D6-s2 narrows from `docs/**` to `docs/*.md`, which is what keeps the seats disjoint.
- `dev/governance/config/corpus_excluded.json`: `docs/index.html` is added to `excluded`. D6.md now names the file, and `policy_lint.mjs`'s `named-docs` check refused it (`has no cap in policy_budgets.json`) until it was listed; the page is a claim source, not policy prose. This is a data file, so no checker source changes.

## Approval

tvofi, relayed by the orchestrator on 2026-10-15, verbatim: "add a web page check to dimension d6". This is the owner's direct request, not a seat's finding. The owner's approving review at the head, and the orchestrator's merge under mandate 6175172275, are still to come.

## Head

`9a2736b06900bc459ce18deec8c450da82c8170b`

## Mutation proof

`python3 tools/audit/check_scopes.py --repo . --ref 9a2736b06900bc459ce18deec8c450da82c8170b --self-test` prints `SELF-TEST passed (both perturbed scopes refused)`: the checker refuses a block owned twice and cells owned by nobody. Perturbing this change by hand, leaving s2 at `docs/**` makes `docs/index.html` owned twice, which the checker reports as `owned twice`.

## Null control

At `origin/main` the checker passes with the web page outside D6's universe. At this head `python3 tools/audit/check_scopes.py --repo . --ref 9a2736b06900bc459ce18deec8c450da82c8170b` prints `ok D6 mode=files seats=3 universe=17 [s1:4f/0loc, s2:7f/0loc, s3:6f/0loc]`; `--seat D6-s1` lists `DISCLAIMER.md`, `README.md`, `docs/index.html`, `docs/site/docs.css`.

## Figures

- `python3 tools/audit/check_scopes.py --repo . --ref 9a2736b06900bc459ce18deec8c450da82c8170b` prints `ok D6 ... universe=17` and no `FAIL` line for any dimension.
- `node tools/policy/policy_lint.mjs --budgets` prints `tools/audit/briefs/D6.md 32 35 388 388` for D6.md: 32 lines against a cap of 35, 388 tokens against a cap of 388. No cap is raised and `policy_budgets.json` is untouched.

## Red checks

none

## Forward-carry

none

## Friction

none
