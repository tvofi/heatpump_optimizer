_Requested by **tvofi**_

Part of #1798

Before: nothing serves the product page (`docs/index.html`, R9-WEB-1) or the documentation sub-pages (`tools/site/build_docs.mjs`, R9-WEB-3). After: `.github/workflows/pages.yml` deploys both to GitHub Pages.

**Triggers and grants.**
- It runs on a pushed `v*` tag, the trigger `release.yml` uses, so the served page is the release HACS installs. It also runs on `workflow_dispatch`.
- The workflow's permissions are exactly `contents: read`, `pages: write` and `id-token: write`, with one concurrency group whose `cancel-in-progress` is false.
- Every `uses:` is pinned by commit.
- No job produces a required context.

**`pages-build`** (permissions `contents: read`, `pages: read`; checkout without persisted credentials) runs these steps:
1. Asks the Pages API whether Pages is on and built by GitHub Actions.
2. Runs `npm ci --ignore-scripts --prefix tools/site` over the committed lockfile.
3. Stages `docs/index.html`, `docs/site/**` and every tracked `*.png` and `*.svg` under `docs/` at its own path. This uses shell only and never stages a `.md`.
4. Renders the sub-pages with `node tools/site/build_docs.mjs --root . --tree <git ls-files> --out _site`.
5. Copies mermaid's `dist/mermaid.min.js` to `_site/site/mermaid/`.
6. Refuses any `.md` or `.markdown` file in `_site`.
7. Uploads the site.

**`pages-deploy`** runs `actions/deploy-pages` in the `github-pages` environment. It is a separate job so that `pages: write` and `id-token: write` never reach the job that runs `npm ci` and the repository's generator. The design's Hosting section said "One job"; this deviation is deliberate, and the review accepted it.

**The repository state, measured 2026-10-03:**
- Pages is already enabled. `gh api repos/tvofi/heatpump_optimizer/pages` returns `build_type: workflow` and `html_url: https://tvofi.github.io/heatpump_optimizer/`.
- The `github-pages` environment exists. Its only deployment policy is `{name: main, type: branch}`.

So **the workflow is armed on merge**:
- A dispatch on `main` deploys straight after the merge, with no click.
- A `v*` tag run is refused by the environment's protection rule in `pages-deploy` until the environment admits `v*` tags.
- The plan is for the v6.7.15 stamp tag to deploy the site.

The probe stays as a defence. If Pages is ever switched off (API 404) or set to build from a branch, the run builds, writes a warning and a step-summary line naming the setting, skips the upload and the deploy, and ends green. Any other API error turns the run red.

**The one remaining click for tvofi, before the v6.7.15 stamp tag:** Settings → Environments → `github-pages` → Deployment branches and tags → Add deployment branch or tag rule → Ref type **Tag**, name pattern `v*`. Ruleset `release-tags-protect` lets only the stamp's deploy key create a `v*` tag, so this rule does not let anyone else deploy a commit by tagging it.

`.github/workflows/` and `tests/closures.json` are code-owned, so this PR merges on tvofi's approving review at the head.

## Head

51c5a30c6daadf9ce886278fe8a289b771cc32e2

## Mutation proof

`PYTHONPATH=tests/hastub python tests/mutation_table.py --scope changed --base origin/main --max 0` reports an empty scope, because no file under `custom_components` changes. So I mutated the workflow by hand.

`mutate_pages.py` extracts `tests/entities.py`'s own Pages check verbatim and runs `_pg_defects` over 29 mutants of `pages.yml`. The baseline returns no defect. It kills 28.

The round-1 review's survivors, now killed:
- `environment: github-pages` removed, or renamed;
- the build job's `permissions:` block removed, or set to `pages: write` plus `id-token: write`;
- `always()` added to the upload's `if:` or the deploy's `if:`;
- `cancel-in-progress: true`.

Also killed:
- staging: the `.md` skip deleted or made lower-case only; the `docs/` prefix kept; the svg or site pathspec dropped;
- guard: `exit 1` deleted; `-iname` made `-name`; the guard moved before the render step;
- probe: a 404 made red; any build source counted as enabled; the 404 branch keyed on any error;
- the probe gate removed from the upload or from the deploy;
- the workflow grant widened, or `id-token` dropped; the build job given `contents: write`;
- `deploy-pages` referenced by tag;
- the trigger turned into `branches: [main]`, or `pull_request` added;
- concurrency removed;
- a job named `closures`.

The survivor is "probe: an unknown API error is swallowed". It is equivalent: the step's `set -u` fails on the unset `${msg}`, so the run is still red and writes no `enabled`. The round-1 reviewer confirmed this.

Remaining survivors of the reviewer's harness, triaged rather than pinned:
- `persist-credentials: true` on a job that holds `contents: read` only;
- a `docs/*.json` pathspec, which publishes tracked data and no `.md`;
- the guard narrowed to `.md` only, which staging already enforces case-insensitively;
- a `docs/*.md` pathspec, which is equivalent because staging still skips it.

## Null control

**Failing test first.** At `6daddc0d2` (the check, no workflow), `tests/entities.py` printed `FAIL the Pages workflow deploys on a release tag, is gated on Pages being enabled, and stages the published set and never a markdown file  [.github/workflows/pages.yml does not exist]`. That was 1 of 2084 checks failed.

**Controls that run on every pass:**
- a staging step that copies `docs/` wholesale is refused;
- a guard that refuses nothing is refused;
- the real workflow with its `environment:` block removed is refused for that reason;
- the real workflow with the build job's `permissions:` block removed is refused for that reason.

## Figures

Rules:
- Taken at head `51c5a30c6` over merge base `8c6e9a7ef`. origin/main was at `2622b31c8` at 2026-10-03T12:20Z.
- Python 3.14 venv built from `tests/requirements-ci.txt`, with `PYTHONPATH=tests/hastub`.

Figures:
- `python tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`: `MODE: SCOPED -- 2 script(s) run, 28 scoped out`. The two are `tests/entities.py` and `tests/harness_headers.py`.
- `python tests/entities.py`: `ALL 2086 ENTITY CHECKS PASSED`.
- `python tests/harness_headers.py`: `ALL 95 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. No budget is raised.
- `node .claude/workflows/policy_lint.mjs` and `node .claude/workflows/brief_lint.mjs`: exit 0.
- `python3 -I tools/audit/round6/D11/fix/codeowners_gap.py`, arm `none`, merge base then head:
  - the surface goes from `= 67` to `= 69`;
  - the diff of the two runs adds exactly `COVERED .github/workflows/pages.yml` and `COVERED tools/site/build_docs.mjs`;
  - the generator's one import, `.claude/workflows/vendor/markdown-it.min.js`, was already on the surface as `PINNED`;
  - `--check` at the head prints `RESULT uncovered_files=0`.
- `python /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-heatpump-optimizer-approval-af78f2/0006c636-2941-40c6-b798-638de4efb00a/scratchpad/seat-web2/mutate_pages.py .` (sha1 `29d3061d`): `RESULT mutants=29 killed=28 baseline_clean=True`.
- I ran the build job's four non-probe shell steps under `bash -eo pipefail` in a clone of the head. Each exited 0.
  - The generator printed `pages 9, … mermaid 8` and `RESULT: PASS`.
  - `_site` holds 66 files: 10 html, 29 png, 19 svg and 0 md. The rest are the stylesheet, the fonts with their OFL texts, and the mermaid UMD file.
- `python /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-heatpump-optimizer-approval-af78f2/0006c636-2941-40c6-b798-638de4efb00a/scratchpad/seat-web2/linkcheck.py _site` (sha1 `50ae683a`): `local references 279, unresolved 0`. Its control, run with `img/card-plan-chart.png` removed: `unresolved 2`.
- `gh api repos/tvofi/heatpump_optimizer/pages --jq .build_type`: `workflow`.
- `gh api repos/tvofi/heatpump_optimizer/environments/github-pages/deployment-branch-policies`: one policy, `main` (branch).

## Red checks

- `nightly-status`: failure on `f5e0a87f6` (run 37121486451), `NIGHTLY FAILED: mutation-ledger failed last night`. This is main's nightly mutation-ledger lane, not this diff, and the check is not required. Cheaper detector: none in this PR's scope. The nightly is its own detector, and it is red on main.
- `closures`: this may report `tests/harness_headers.py`. I added `pages.yml` to its closure by hand, because its `codeowners_gap.py` child reads every workflow, and all ten siblings are listed there. A Darwin recording cannot see that child, so the Linux recording is the authority. closures-autofix repairs a disagreement (`ci-autofix.md`).

## Forward-carry

Owed after merge, and no longer gated on any click:
- Dispatch `pages.yml` on `main`.
- Show the served page at `https://tvofi.github.io/heatpump_optimizer/`, its fonts, one image, one sub-page with a drawn diagram, one cross-page anchor, and a 404 for a `.md` path.
- Then open a small PR that replaces the README Documentation row's `docs/index.html` link with the served URL.

The `v*` tag rule is the one click owed before the v6.7.15 stamp. Destination: the R9-WEB-2 group's resume next step in the round-9 roster on the audit-r9-fixplan handoff branch. Only the orchestrator edits the roster, so this is handed over in the seat's final report.

## Friction

gate-scoping: cost: `tests/closure.py` `_rel` attributes a relative path in a recorded script's subprocess argv to the repository. A check that ran `git add` on scratch files by name recorded `docs/HANDOVER.MD`, which is real only on a case-insensitive disk. The check now passes no path as an argument.

## Approval

tvofi's approving review is owed: `.github/workflows/pages.yml` and `tests/closures.json` are code-owned. One setting is owed before the v6.7.15 stamp tag: the `v*` tag rule on the `github-pages` environment. No budget is raised.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
