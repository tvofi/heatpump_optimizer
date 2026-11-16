Fix review: merge 5023cde196c43c5bdd4b11789a45780f1c70790a

bus-nonce: bce5bf818cb98dc3199cb7573ba1015e
pending-ci: gate

## Scope

Round 2: a delta round over the reviewed head 0648b3532d (previous verdict `merge`, `pending-ci: gate`). `review_carry.py 0648b3532d 5023cde196` prints `FRESH-REVIEW`: 5023cde196 is not the automatic merge of its parents, because `dev/governance/config/policy_budgets.json` conflicts (`git merge-tree 0648b3532d b94425b94f` rc 1 on that path only; `tests/closures.json` resolved by the ledger driver). So this round reviews that resolution. The PR's own three-dot diff still lists the same 17 files and has no `custom_components/` path (ev/own_files.txt). The 8 `custom_components/` files in the two-dot delta come from main's own merged commits, and this PR's policy/config change cannot affect them, so the review is not widened.

## Evidence

- Head: `5023cde196c43c5bdd4b11789a45780f1c70790a` (ev/HEAD.txt), parents 0648b3532d and origin/main b94425b94f. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the contract I read is current.
- `git merge-tree --write-tree origin/main 5023cde196` (origin/main b94425b94f): rc 0 (ev/merge_tree.txt). It merges cleanly.
- Own-diff comparison, three-dot at 0648b3532d against three-dot at 5023cde196 with `index` lines removed (ev/owndiff_delta.txt): apart from hunk offsets and context lines that main moved, the only content change is `corpus_tokens`. That cap goes 65926 -> 68000 at the old head and 67155 -> 69244 at this head.
- Merge resolution against main (`git diff b94425b94f 5023cde196 -- policy_budgets.json`): the PR's own D10.md cap cut (46/624 -> 32/410), its four criteria-file caps (52/656, 49/641, 43/546, 30/425, unchanged from round 1), and `corpus_tokens` 67155 -> 69244. Nothing of main's is lost: main's raised COMMON/D0/D1/D11/D12 caps are kept.
- RESULT budgets, `node tools/policy/policy_lint.mjs --budgets`. At the head: `corpus: ~69244 tokens, cap 69244 +band 500`, `always-loaded: ~3598`, rc 0 (ev/budgets_head.txt). At main b94425b94f: `corpus: ~67178 tokens, cap 67155`, rc 0 (ev/budgets_main.txt). The PR's measured corpus delta is 69244 - 67178 = +2066, the same +2066 that round 1 measured against its own base. The resolved cap is the measured value. Its +2089 over main's cap is the PR's +2066 plus main's own 23 tokens over its cap, which were already inside main's band. The raise is still earned by the four criteria files (2268 tokens) net of the D10.md payment (-214), as re-derived in round 1.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`.
- `python3 dev/audit/harnesses/r11_owner_criteria.py plants` at the head: `plants: 9, wrong: 0` (ev/plants_head.txt).
- `python3 tools/audit/check_scopes.py --repo .` at the head: `ok coverage tracked=11428 in_universe=1631 excluded=9797 unclassified=0`. Main added files, and the criteria files are still classified.
- `tests/entities.py` locally reached its 200 s timeout (rc 124) inside the timing-sensitive `hb:positive_control` plant arms (ev/entities_tail.txt). This is a local resource limit, not a verdict on the script; the `gate` (MODE: FULL) runs it, and I cite CI for it.
- `VERSION`, `manifest.json`, `RELEASE_NOTES.md`: the three-dot diff is empty.
- Previous verdict's findings: all four were `Note:` paperwork lines, dismissed in round 1 (stale body figures, stale payment 2, a double `## Head`, owner approval owed). None is a code, test or harness defect, and none is reopened by this delta. The owner-approval note still stands: the policy files need the owner's approving review, which `main-protect-checks` enforces.
- CI: `merge_train.py classify 5023cde196 --pr 3641` was polled about every 77 s from 08:23 to 08:56 UTC; every run returned rc 3 `WAIT 5023cde196c43c5bdd4b11789a45780f1c70790a pending: gate red: none`. From 08:57 classify returns rc 2, unreadable: `REFUSE selftests: the base's governance / instrument-self-tests job 133169041167 is in_progress, which reads no step: an introduced red cannot be ruled out (fail closed)`. That job is on the base (main), not this head. No red has been read at this head, and `gate` is still pending, hence `pending-ci: gate` (ev/classify_log.txt). `refs/pull/3641/head` re-read at 08:58 UTC is still 5023cde196.
- This is round 2 of review for this PR.

## Findings

- Note: stale-figures: the body's budget figures (cap 68000 and the merge base 65926) predate the merge of main: at this head the cap is 69244 against main's 67155, which is the measured value. Carry: dismissed: paperwork on this PR's body, the re-derived numbers are in this verdict
