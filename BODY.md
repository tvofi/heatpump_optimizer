_Requested by **tvofi**_

Part of #1798

Before: the product page (`docs/index.html`, R9-WEB-1) and the documentation sub-pages generator (`tools/site/build_docs.mjs`, R9-WEB-3) exist in the tree, and nothing serves them. After: `.github/workflows/pages.yml` deploys them to GitHub Pages on a pushed `v*` tag (the trigger `release.yml` uses, so the served page is the release HACS installs) and on `workflow_dispatch`. Permissions are exactly `contents: read`, `pages: write` and `id-token: write`, with one concurrency group. Every `uses:` is pinned by commit, and no job produces a required context.

`pages-build` checks out the ref and runs these steps in order:
- asks the Pages API whether Pages is on;
- runs `npm ci --ignore-scripts --prefix tools/site` (the committed lockfile);
- stages `docs/index.html`, `docs/site/**` and every tracked `*.png` and `*.svg` under `docs/` at its own path, using shell only and never a `.md`;
- renders the sub-pages with `node tools/site/build_docs.mjs --root . --tree <git ls-files> --out _site`;
- copies `tools/site/node_modules/mermaid/dist/mermaid.min.js` to `_site/site/mermaid/`;
- refuses any `.md`/`.markdown` in `_site`;
- uploads with `actions/upload-pages-artifact`.

`pages-deploy` then runs `actions/deploy-pages` in the `github-pages` environment.

**Inert until Pages is enabled.** The upload step and the deploy job are gated on the probe's `enabled` output. If Pages is off (API 404), or builds from a branch rather than from Actions, the run builds the site, writes a warning annotation and a step-summary line naming the setting, skips the upload and deploy, and ends green. Any other API error fails the run.

**What tvofi must click, once, before the first deploy:**
1. Settings → Pages → Build and deployment → Source: **GitHub Actions**.
2. Settings → Environments → `github-pages` (GitHub creates it in step 1) → Deployment branches and tags: add a **tag** rule `v*`. Without it, a tag-triggered deploy is refused by the environment's protection rule. The default rule allows only the default branch, so a dispatch from `main` deploys either way.
3. Then Actions → Pages → Run workflow on `main`, or wait for the next stamp's tag.

`.github/workflows/` is code-owned (`/.github/workflows/ @tvofi`), so this merges on tvofi's approving review at the head. `tests/closures.json` is code-owned too.

Design deviation, stated: the design's Hosting section says "One job". This PR uses two jobs. `deploy-pages` must run in the `github-pages` environment, and naming an environment on a job creates it. A separate deploy job that is skipped while Pages is off keeps the workflow inert: no environment, no deployment record.

## Head

f5e0a87f6b2b90244218b9ff2edc625f2db77269

## Mutation proof

`PYTHONPATH=tests/hastub python tests/mutation_table.py --scope changed --base origin/main --max 0` prints `no production code line added or modified against the base`: this diff touches no file under `custom_components`. So the workflow was mutated by hand. The harness extracts `tests/entities.py`'s own Pages check code verbatim, from `_PG_WF = Path(` to the first `R.check`, and runs `_pg_defects` over each mutant of `pages.yml`. The baseline returns no defect. 21 of 22 mutants are killed:
- staging: the `.md` skip deleted; the skip made lower-case only; `docs/` not stripped; the svg or site pathspec dropped;
- guard: `exit 1` deleted; `-iname` made `-name`; the guard moved before the render step;
- probe: a 404 turns the run red; any build source counts as enabled; the 404 branch keys on any error;
- the upload's or the deploy's probe gate removed;
- `contents: write`, `id-token` dropped, build-job `contents: write`;
- `deploy-pages@v5` by tag;
- the tag trigger turned into `branches: [main]`, or `pull_request` added;
- concurrency removed;
- a job named `closures`.

The survivor is "probe: an unknown API error is swallowed": `exit 1` deleted after the non-404 error. It is an equivalent mutant. Execution falls through to `${msg}`, which is unset, and the step's `set -u` fails it, so the run is still red and no `enabled` is written.

## Null control

Failing test first: at `6daddc0d2` (the check, no workflow), `tests/entities.py` printed `FAIL the Pages workflow deploys on a release tag, is gated on Pages being enabled, and stages the published set and never a markdown file  [.github/workflows/pages.yml does not exist]`, `1 of 2084 ENTITY CHECKS FAILED`. The check's own null controls run in every pass: a staging that copies `docs/` wholesale (it stages `.md` files) and a guard that refuses nothing (`true`). Both are refused at the base and at the head.

## Figures

Rules: run at head `f5e0a87f6` over merge base `8c6e9a7ef` (origin/main tip at 2026-10-03T11:40Z), Python 3.14 venv from `tests/requirements-ci.txt`, `PYTHONPATH=tests/hastub`.
- `python tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir D`: `MODE: SCOPED -- 2 script(s) run, 28 scoped out` (`tests/entities.py`, `tests/harness_headers.py`).
- `python tests/entities.py`: `ALL 2085 ENTITY CHECKS PASSED`.
- `python tests/harness_headers.py`: `ALL 95 HARNESS HEADER CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`; no budget raised.
- `node .claude/workflows/policy_lint.mjs` and `node .claude/workflows/brief_lint.mjs`: exit 0.
- `python3 -I tools/audit/round6/D11/fix/codeowners_gap.py`, arm `none`, merge base then head:
  - surface `10 workflow(s), 39 exec'd script(s), 10 imported by them, 3 run by path, 4 hook(s), 1 settings file = 67`, then `11 workflow(s), 40 exec'd script(s), 10 imported by them … = 69`.
  - The diff of the two runs adds exactly `COVERED .github/workflows/pages.yml` and `COVERED tools/site/build_docs.mjs`.
  - The generator's one import, `.claude/workflows/vendor/markdown-it.min.js`, was already on the surface, as `PINNED`, and its line does not change.
  - `--check` at the head: `RESULT uncovered_files=0`.
- `python /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-heatpump-optimizer-approval-af78f2/0006c636-2941-40c6-b798-638de4efb00a/scratchpad/seat-web2/mutate_pages.py .` (sha1 `177e5590`): `RESULT mutants=22 killed=21 baseline_clean=True`.
- Local run of the build job's four shell steps in a clone of the head (every `run:` but the probe, each under `bash -eo pipefail`): each exited 0.
  - The generator printed `pages 9, … mermaid 8` and `RESULT: PASS`.
  - `_site` holds 66 files: 10 `.html`, 29 `.png`, 19 `.svg`, 0 `.md`, plus the stylesheet, four fonts, two OFL texts and the mermaid UMD file. `git ls-files -- 'docs/*.png' 'docs/*.svg' | wc -l` prints 48, which is 29 + 19.
- `python /private/tmp/claude-501/-Users-timmalmstrom-heatpump-optimizer--claude-worktrees-heatpump-optimizer-approval-af78f2/0006c636-2941-40c6-b798-638de4efb00a/scratchpad/seat-web2/linkcheck.py _site` (sha1 `5af8ace8`), every local `src`/`href`/`srcset` and the stylesheet's `url()` resolved inside `_site`: `local references 279, unresolved 0`. Its control, with `img/card-plan-chart.png` removed: `unresolved 2`.
- `python tests/closure.py check --in-dir <Darwin --single --record-only recording of tests/entities.py at the head> --partial`: `committed closures cover every file this run touched`. That recording added exactly `.github/workflows/pages.yml` to the committed closure.

## Red checks

none yet. Expected: `closures` may print `UNDER-SCOPED` or a mismatch for `tests/harness_headers.py`. I added `pages.yml` to its closure by hand, because its `codeowners_gap.py` child reads every workflow and all ten siblings are listed. A Darwin recording cannot see that child (it dropped all ten siblings), so the Linux recording is the authority. If it disagrees, closures-autofix repairs it (`ci-autofix.md`).

## Forward-carry

The brief asks for two things before merge that cannot happen then.
- **Dispatch at the branch head.** GitHub dispatches a workflow only if its file exists on the default branch, and `github-pages`' default deployment rule admits only `main`.
- **Replace the README row's file link with the served URL.** The served page cannot be shown before then.

So, after merge and after tvofi's two clicks, a follow-up step is owed:
- dispatch `pages.yml` on `main`;
- show the served page at `https://tvofi.github.io/heatpump_optimizer/`, its fonts, one image, one sub-page with a drawn diagram, one cross-page anchor, and a 404 for a `.md` path;
- then a small PR to replace the README Documentation row's `docs/index.html` link with the served URL.

Destination: the R9-WEB-2 group's resume next step in the round-9 roster on the audit-r9-fixplan handoff branch. Only the orchestrator can edit the roster, so it is handed over in the seat's final report.

## Friction

gate-scoping: cost: `tests/closure.py` `_rel` attributes a relative path in a recorded script's subprocess argv to the repository. A check that `git add`s scratch files by name recorded `docs/HANDOVER.MD` (real only on a case-insensitive disk), so the check was changed to pass no path as an argument.

## Approval

tvofi's approving review is owed: `.github/workflows/pages.yml` and `tests/closures.json` are code-owned. Enabling Pages and the `github-pages` tag rule are repository settings that only tvofi can change. No budget is raised.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
