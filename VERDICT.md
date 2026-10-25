Fix review: blocked 558fcd6aea84bc99894fbb713c7846481ef53345 pr-contract-refused: the Dependabot contract refuses the seat's merge and delivery-row commits (78672bb, 558fcd6) on the Dependabot branch, so the required pr-contract and gate checks are red at this head

bus-nonce: dfd97b127e9064810143718f71d5da23

## Block

- `pr-contract / pr-contract` concluded `failure` at head 558fcd6aea84bc99894fbb713c7846481ef53345 in both runs (40165394178 and 40165394320); `gate` fails on it (`FAIL pr-contract / pr-contract: failure`). The log shows `DEPENDABOT: judged on the dependency-bump contract (tools/policy/dependabot_contract.mjs)` and two errors: commits 78672bb (the merge of origin/main) and 558fcd6 (the delivery row) are not Dependabot's own, and `dev/programme/delivery/2773.md` is a path no `.github/dependabot.yml` entry configures.
- These are the dispatch seat's commits, not Dependabot's change. The contract states its own remedy: "a seat taking the PR over re-opens it as the hpo-author App". It cannot be answered under `## Red checks`, because the contract runs instead of the ordinary body check. So no body edit can turn this head green.
- The Dependabot change itself (286efaace) is sound; see Evidence. There are two re-cuts: re-open the same bump as an hpo-author App PR that carries the row and body, or reset the branch to Dependabot's own commit (`@dependabot recreate`/`rebase`) and keep the delivery row off it.

## Findings

- The dispatch recipe that adds a merge of main and a delivery row onto a Dependabot branch conflicts with `tools/policy/dependabot_contract.mjs`. Every Dependabot PR handled this way will be refused the same way. The record lane's dispatch for Dependabot PRs has to either re-open them as hpo-author or keep seat commits off the bot branch. Carry: #2773

## Evidence

- Round: first fix review of #2773 that I know of. Roles diff `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- Head measured: 558fcd6aea84bc99894fbb713c7846481ef53345, still `refs/pull/2773/head` when posting (ev/head-at-post.txt).
- Diff, three-dot against merge base 8a11b8bdd: only `tools/site/package.json`, `tools/site/package-lock.json` and `dev/programme/delivery/2773.md` (3 files, +18/-14), matching the brief (ev/diff-stat-three-dot.txt).
- Version move: `mermaid` 12.1.0 to 12.2.0 in package.json and in the lock root. The lock entry resolves `mermaid-12.2.0.tgz` with a sha512 integrity hash. `npm ci --ignore-scripts` over the head lockfile succeeded on node 22.22.0, so every tarball passed its integrity check; it installed `mermaid@12.2.0` (ev/npm-ls-head.txt). The lock has 117 `resolved` and 117 `integrity` entries.
- Transitive moves: `katex` 0.16.47 to 0.18.10 and its nested `commander` 8.3.0 to 15.0.0 (engines `node >=22.12.0`). These are not unrelated. mermaid 12.2.0 itself raised its range to `katex ^0.18.0`, in the upstream commit "Update dependency katex to ^0.18.0 [SECURITY]" that the PR body quotes. commander is only katex's CLI dependency. pages.yml installs with `--ignore-scripts` on node "22" (the runner resolved 22.23.3, which satisfies >=22.12.0). The docs tree holds no KaTeX math inside mermaid blocks, so the katex move does not reach site usage. No other package moved.
- Changelog risk: the quoted 12.2.0 notes list one opt-in feature (`mindmap.colorBy: depth`) and patch fixes to circle nodes, ELK, mindmap labels and swimlanes. None of them is breaking. tools/site uses mermaid only through `mermaid.initialize({startOnLoad:false,theme,fontFamily})` and `mermaid.run({nodes})` in `tools/site/build_docs.mjs`, plus pages.yml copying `dist/mermaid.min.js`. The repo's docs contain no mindmap or swimlane diagram.
- Render check, using my own instrument (the brief names no committed harness): I built the sub-pages with `node tools/site/build_docs.mjs` at the head (`RESULT: PASS`, mermaid 9 blocks across 5 pages), then rendered each page in Chromium in light and dark. RESULT: PASS at 12.2.0, 10/10 page-schemes, every block an SVG, 0 page errors (ev/render-12.2.0.txt). The same at 12.1.0 as baseline: RESULT: PASS 10/10 (ev/render-12.1.0.txt). Perturbation with an emptied `mermaid.min.js`: RESULT: FAIL 10/10, `mermaid is not defined` (ev/render-perturbed-empty-mermaid.txt), so the instrument moves under its perturbation.
- Mutation proof: not applicable. The diff writes no production code line, and `tests / mutation` is green with no mutant drawn.
- VERSION, the manifest version and the notes heading are untouched (pr-contract's own `no version edit` line, and my three-dot diff).
- Merge with origin/main: `git merge-tree --write-tree origin/main 558fcd6` exits 0 with tree 3aa0a1e9d (ev/merge-tree.txt).
- CI at head, from the check-runs API (55 runs, all completed; ev/check-runs.txt): everything else is success or skipped, including tests/fast, closures, coverage, browser, typing, mutation, governance/*, codeql, hassfest, validate-hacs, arch-score and budget-raise-gate. The only failures are `pr-contract / pr-contract` x2 and `gate` x2 (ev/pr-contract-refusal.txt).
- Figures I could not re-derive: the refusal names the off-manifest path as `docs/delivery/2773.md`, while the diff path is `dev/programme/delivery/2773.md`. I did not trace where policy_lint maps that path, and the refusal holds whichever spelling it uses.
- tools/site is not code-owned, so no owner review is needed for the bump itself.
