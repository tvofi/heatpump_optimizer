Fix review: merge ddda67d3214b554089c52f3d242fdd36ac1d2e18

bus-nonce: 59f7bf6ee5d30d79753a08a4da358b1f

## Scope

Round 1 (no prior reviewed head). Dependabot pull request: one line in `.github/workflows/dependabot-automerge.yml` re-pins `actions/create-github-app-token` from 64ab729a6294000f5aa4a4bc0b73d1f32bc45510 (v3.3.0) to f418cff399f7aef4c2f0ad47e25ca7a6abbdd6fc (v3.4.0). No `custom_components/`, test, budget, claim, closure or golden file moves. Role contracts unchanged between the merge base and origin/main (`git diff <merge-base>...origin/main -- dev/governance/roles/` is empty).

## Evidence

- Head measured: ddda67d3214b554089c52f3d242fdd36ac1d2e18, the PR head as read from `refs/pull/3852/head` (ev/HEAD.txt); merge base 3a98735a7ecc59e7ecc095a0429cdf6251d956ec, the packet's base.
- Pin integrity: `git ls-remote https://github.com/actions/create-github-app-token` prints `refs/tags/v3.3.0` = 64ab729a… and `refs/tags/v3.4.0` = f418cff3…, so the old and new SHAs are the tags the version comments name (ev/checks.txt).
- Interface: `action.yml` at the two pins is byte-identical (ev/action-yml.diff is 0 bytes): same inputs and outputs, runtime `node24`, entry `dist/main.cjs`. The workflow's `app-id` and `private-key` inputs and its `steps.app.outputs.token` read keep their meaning.
- Mutation proof (step 1): not applicable. The diff writes no production line, so the mutation driver draws no mutant (`changed_lines`). The only behaviour it changes is the bundled action code, which runs when the workflow fires on a later Dependabot PR; no in-repo test exercises it at either pin.
- Finder's harness (steps 2, 3, 6, 9): none. This is a dependency update with no audit finding behind it, so there is no class claim, enumeration rule, null control or figure to re-derive. The body quotes no repository figure.
- VERSION, manifest version, release-notes heading: untouched (ev/checks.txt, 0 paths). Claim files: untouched, so step 4 has no drift to compare.
- Merge with main: `git merge-tree --write-tree origin/main ddda67d3214b554089c52f3d242fdd36ac1d2e18` at origin/main eaaaf24e5becdf9682e961cc3ca33f25df920438 exits 0, tree fef2f5d2a0d4dff23f2f4a376ff57a40a70b45c3, no conflict (ev/checks.txt).
- CI: `merge_train.py classify ddda67d3214b554089c52f3d242fdd36ac1d2e18 --pr 3852` exited 0: `GREEN ddda67d3214b554089c52f3d242fdd36ac1d2e18 pending: none red: none` (ev/classify.txt). No red at this head, so no `## Red checks` answer is owed.
- Other pins of the same action: `git grep create-github-app-token@` at the head returns only this one site, so the bump leaves no stale sibling pin.

## Findings

- Follow-up: the workflow passes `app-id`, which `action.yml` marks `deprecationMessage: "Use 'client-id' instead."` at both pins. This PR does not introduce it, and no removal is announced, so nothing breaks today. Carry: dismissed: pre-existing deprecation identical at both pins, outside this dependency bump's diff
