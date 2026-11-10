Fix review: merge 823d472de04391e40f80468e0b17073d94ccbe25

bus-nonce: 95bb81f1f8d23e12534cf7951a97ddee

Round 2 (previous verdict: `Fix review: merge 9b903a91ab9e1ed5d439729aa09b67766492ff5f`, bus-nonce 3a9896e8). Measured at head `823d472de04391e40f80468e0b17073d94ccbe25` from the fetched ref. Scope per the brief: the delta `9b903a91ab..823d472de04391e40f80468e0b17073d94ccbe25` only.

## Findings

- Follow-up: round 1's finding that `dev/audit/README.md` still names #201 in three phase-table rows (and that the census path set skips `dev/audit/`) is not settled by this delta: the delta touches no such file. Already carried in round 1 and unchanged. Carry: R10-ARCH-DOCS
- Follow-up: round 1's owed host action, re-running `tools/audit/seat/seat_venv.sh --install-shims <bin dir>` on each orchestrator host, is unchanged and still owed after the merge. Carry: dismissed: an orchestrator host action the body already lists, with no destination in the tree
- Residual: round 1's gate lag (`budget-raise-gate` reads `budget_raise_gate.py` from the base, so a revocation on #3394 is unread until the base carries this merge) is unchanged. Carry: dismissed: it closes by itself once this merge is on main, and no grant is affected today

## Evidence

- Delta is a main merge only: `823d472de04391e40f80468e0b17073d94ccbe25` is the merge of origin/main `04dfcafccd` into `9b903a91ab`; `git log 9b903a91ab..823d472de04391e40f80468e0b17073d94ccbe25` is that merge plus main's commits. The PR's own patch is unchanged: for every file, the added/removed lines of `git diff ddd2f8b273 9b903a91ab` equal those of `git diff 04dfcafccd 823d472de04391e40f80468e0b17073d94ccbe25`, and the two file sets are identical (46 files; ev/own-patch.txt). `review_carry.py` prints FRESH-REVIEW only because the old and new bases differ, not because the patch does.
- Production code: the PR diff against main touches 0 files under `custom_components/`. Main's own `custom_components/` changes entering through the merge (e.g. #3297) are not this PR's, and the PR's files do not overlap them, so no wider review is owed.
- Previous findings: all three are carry-only (above) and none needed a fix in this delta. None is made worse by it.
- Merge: `git merge-tree --write-tree origin/main 823d472de04391e40f80468e0b17073d94ccbe25` exits 0, no conflict (ev/merge-tree.txt). origin/main is still `04dfcafccd`.
- Protected files: the PR diff touches none of VERSION, the manifest, RELEASE_NOTES.md, claim files, `*budgets.json`, `tests/closures.json` (ev/protected.txt is empty).
- Review packet at the head (ev/packet.md): gate digest green, 0 refusals at re-render, carry_audit 0 finding items, figure_lint 31 resolved, 0 refused. The render at dispatch time refused `red-unanswered: gate` because `gate` was still running (it concluded failure transiently in that digest; classify read WAIT); at re-render it is green.
- Figures: not re-derived at this head. The patch is byte-equivalent in content to round 1's, and the packet's figure_lint resolves the instruments' self-tests at this head.
- Mutation proof: not re-run, since the PR's patch is unchanged since round 1 and the brief scopes this round to the delta.
- Head re-read before return: `fix/r10-hotfix-record-issue-continuation-pr` is still at `823d472de04391e40f80468e0b17073d94ccbe25`.

## CI

- `merge_train.py classify 823d472de04391e40f80468e0b17073d94ccbe25 --pr 3412` exits 0 and prints `GREEN 823d472de04391e40f80468e0b17073d94ccbe25 pending: none red: none` (ev/classify.txt), after WAIT from the first poll to 11:46 UTC while `gate` ran.
- `merge_train.py owed-reds` lists the required contexts (ev/owed-reds.txt). None is red at this head, so no `## Red checks` answer is owed.
