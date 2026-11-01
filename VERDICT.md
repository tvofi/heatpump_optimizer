Fix review: merge ace2e21a6f22cc3e9af22b5b1eed6a92b55105d9

bus-nonce: 37e25aa3d2d826ab6aaa7158edc88a79

## Findings

none

## Evidence

- Scope: carry re-check only, round 6; code not re-reviewed. Prior merge verdict at 9cddcb4f673ee4bed26a316c4a22128433414eb8.
- `git log --format='%h %p %s' 9cddcb4f..HEAD` lists 3 commits, each a two-parent merge with no content of its own: 895f03158 (merges origin/main into the branch), 3f9f152e2 (merges the bot's 2df0b81ed pin commit), ace2e21a6 (merges 3f9f152e2).
- `git rev-parse 9cddcb4f^{tree} HEAD^{tree}` prints e58eadb7b511cae6dacae67a63891bdd6cfad5b7 for both; `git diff --stat` between them is empty.
- `tools/audit/seat/review_carry.py 9cddcb4f ace2e21a6f22cc3e9af22b5b1eed6a92b55105d9` answers `review_carry: CARRY` ("all 3 branch-only commit(s) are automatic merges, and app_approve.sh --carry carries the range").
- `dev/programme/delivery/3047.md` exists at the head.
- The PR body's `## Head` names ace2e21a6f22cc3e9af22b5b1eed6a92b55105d9.
- CI and mergeability were not re-run: the tree is identical to the one already reviewed, and this brief did not ask for it.
