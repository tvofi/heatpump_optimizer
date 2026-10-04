# R9-WEB-5 resume: README product-page links point at the published Pages URL

Owner ask (tvofi, 2026-10-04, folded per the no-pre-study ruling), R9-WEB-5, one PR.
Roster: `origin/handoff/audit-r9-fixplan:.claude/workflows/wave-r9-groups.json` group `R9-WEB-5`.

## State

- Branch `handoff/r9-web-5`, pushed. Authored code head **5dbd37263519e3359a7c07348a3601154e4a3f7a**
  (base `1913f0dd736cb66b800b5eabfa6973a917459d83`, origin/main at the cut);
  this note commit sits on top of it and carries no code.
  Code commits: e28d23e7 (failing pin, red at base), d4c76799 (README lines 16
  and 1012 -> `https://tvofi.github.io/heatpump_optimizer/`), 5dbd3726 (the D6
  link census `harness_headers` executes, re-measured over the new links).
- Published URL verified before writing: pages.yml stages `docs/index.html` at
  the artifact root (`cp docs/index.html _site/`); live site: root 200
  (`<title>Heat Pump Cost Optimizer</title>`), `.../docs/index.html` 404. The
  absolute URL also survives the docs build's README rendering (resolveHref
  keeps absolute links verbatim).
- PR: NOT opened — the orchestrator opens, approves and merges. Body at
  `handoff-body/r9-web-5` (BODY.md + RESUME.md), prepr clean
  (`PRE-PR: 5dbd3726... 00000000000000000000000`).

## Evidence (all at 5dbd3726, scratch /Users/timmalmstrom/hpo-seats/r9-web-5/)

- Pin: `tests/doc_claims.py` arm 1b grew a `readme-link` kind (any README link
  whose path is `docs/index.html` must be the published URL, derived from the
  arm's `_SITE_REPO`); the README Documentation two-way comparison learns the
  published URL as the `docs/index.html` identity.
- Red at e28d23e7: `1 of 160 checks FAILED` naming both links. Green at head:
  `ALL 160 checks PASSED`. Mutation proof: line 16 reverted in place at the fix
  content -> the same check red; restored. No production line touched
  (`mutation_table.py --scope changed`: empty scope).
- Gate: `MODE: SCOPED -- 6 script(s) run, 24 scoped out.` All six green
  (doc_claims, entities, harness_headers, md_tables.mjs, plan_view,
  card_drift.mjs). `structure.py` PASSED.
- One local red answered in the body: prepr's `closures` recorder refused twice
  with `tests/entities.py (exit 1) tests/harness_headers.py (exit 1)` — its
  default interpreter is `PYTHON="${PYTHON:-python3}"`, pyenv 3.11. Under the
  seat venv (`PYTHON=~/.local/state/hpo/venv-ci/bin/python`) the same step
  records covered (`scoped recordings are covered; left to CI: md_tables.mjs
  card_drift.mjs`). Environmental, not the tree.

## Next actions

1. Reviewer dispatches at the push (opus, `handoff/r9-web-5-review`, per
   roster `review_branch`). The authored head is frozen — only the
   orchestrator moves it; the note commit above it is the PR head.
2. Delivery row `docs/delivery/<N>.md` and the PR itself are the
   orchestrator's, not the fixer's.
