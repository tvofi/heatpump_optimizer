Part 2 of R10-DEPS-ACTIONS-BUMP: lands the Dependabot actions-group bump (12 updates) that supersedes #3087. This is a fresh branch from main, not an edit of the Dependabot branch (#3087 is closed separately by the orchestrator). Part 1 (#3160) already widened `codeowners_gap.py` ALLOWED_USES to admit both revisions, so no `codeowners_gap.py` change is taken here.

Bumps (SHA-pinned, comment carries the tag; each new SHA re-verified by `git ls-remote` on the upstream, tags dereferenced):
- actions/checkout v5 fbc6f399 -> v7.0.1 3d3c42e5 (major)
- actions/setup-python v6 ece7cb06 -> v7.1.0 6d4fd22b (major)
- actions/setup-node v5 a0853c24 -> v7.1.0 949feb24 (major)
- actions/download-artifact v7 37930b1c -> v8.0.2 9000827c (major)
- actions/upload-artifact v6 b7c566a7 -> v7.0.2 cf430e03 (major)
- actions/cache (also cache/restore, cache/save) v5 caa29612 -> v6.1.0 55cc8345 (major)
- github/codeql-action (init, analyze, upload-sarif) v4 b96794f0 -> 9b325408 (floating v4 tag, not major)
- home-assistant/actions/hassfest master a7c616ce -> 86d45647 (branch pin, not major)
- .github/actions/nightly-ha/action.yml: setup-python at the bumped revision; tests/entities.py graders-head-copy literal follows tests.yml.

Breaking-change reading (upstream action.yml diff old..new, read as data): setup-python removed input `pip-install` and added `mirror`/`mirror-token`; setup-node removed `always-auth`, added outputs; download-artifact added `skip-decompress`, `digest-mismatch` (default error); upload-artifact added `archive`; checkout and cache: no action.yml input change. `grep -rnE 'pip-install|always-auth' .github tools` finds no use here. Release-note pages were not reachable from this session (GitHub API scope), so the reading is from the action.yml diffs and checkout's commit list; runner-version requirements of the node-runtime bumps are not independently confirmed here and CI is the check.

## Head

963287616416763727fee4b1bc415e17d4dc214e (origin/main unmoved at c7aa121650058ec9f1540b5bf60ffd69eea75298 since the last prepr run, so no second run).

## Mutation proof

n/a: workflow pin bump, no production predicate. The graders-head-copy literal in tests/entities.py is the pinned check; it passes at the head (ALL 2592 ENTITY CHECKS PASSED).

## Null control

With one tests.yml setup-node step set back to the old SHA a0853c24 (v5), `python3 dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check` still printed `RESULT uncovered_files=0 count` (both revisions admitted); file restored, `git status --porcelain` empty.

## Figures

- `python3 dev/audit/rounds/round6/D11/fix/codeowners_gap.py --check`: uncovered_files=0 at the head; `--self-test`: 55 probe(s), 15 null(s), 0 wrong.
- `grep -rnE 'actions/(checkout|setup-python|setup-node|download-artifact)@' .github | grep -vE '3d3c42e5|6d4fd22b|949feb24|9000827c'` prints nothing; no widened action is intentionally left unbumped.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: FULL (the nightly-ha action.yml changes the gate itself); tests/entities.py and tests/structure.py pass (STRUCTURE RATCHET PASSED).
- `tools/pr/prepr.sh` without the closures skip: rc=0 (closures step skips by design, a full derive off Linux is forbidden here).

## Red checks

none

## Forward-carry

none

## Friction

none
