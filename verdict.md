Fix review: merge 94ad84c84cbf1fbe70866ce8110bd4a68308a1ca

bus-nonce: 53307b224bb2f83f0735290be8c55b6e

## Scope

Delta review d2877bb2..94ad84c84cbf1fbe70866ce8110bd4a68308a1ca, three-dot against main (2d151411f). Head = merge(d50f6446d, 2d151411f); d50f6446d = merge(d2877bb23, c0a1d4635). Both merges are of main only.

## Findings

- The head's tests/golden/claimed_drift.txt is not a literal union with main's: main (2d151411f) carries 14 bare claim lines (5 R10-HOUSE-GRADE coord_*, 9 R10-BUFFER-STORE valve/wood fixtures), the head carries only this PR's 5 R10-COP-GATE lines, and the BUFFER-STORE may-drift entries are restored as plain "may-drift:" lines. The file is byte-identical to d2877bb23's (empty diff d2877bb23..head on both claim files), so this is the shape the prior merge verdict already covered and is not new in this delta; claims-for stays 7.0.5 = VERSION and env_drift --claims-only origin/main prints "claims hygiene: origin/main ok". Merging the PR into main removes those 14 main lines (git merge-tree is clean). Carry: dismissed: unchanged since the approved d2877bb2, claim lines excuse only the diff that wrote them and the hygiene check passes against origin/main

## Evidence

- Production/non-claim diff: the PR diff (merge-base with 2d151411f .. head) excluding the two claim files versus the same diff at d2877bb2 (vs its own main merge-base) is identical but for one hunk-header line offset (@@ -3724 vs -3725); same 45 files in both. No production change in the delta. ev/nonclaim-diff.delta.
- card_claimed_drift.txt: no change d2877bb2..head, no claim lines either side of the diff. claimed_drift.txt: no change d2877bb2..head (ev/claimfile-delta-lines.txt = 0). No claim reinstated or dropped in this delta; claims-for 7.0.5 equals VERSION 7.0.5 on both.
- env_drift.py --claims-only origin/main: claims hygiene ok (ev/claims-hygiene.txt).
- git merge-tree --write-tree origin/main head: clean, exit 0 (ev/merge-tree.txt).
- Body: its ## Head section names 94ad84c84cbf1fbe70866ce8110bd4a68308a1ca as the orchestrator's recarry of main; consistent with the tree. The figures in the body are for the authored code, unchanged.
- CI at this head (check-runs read at review time): success: replay, typing, arch-instrument, closure-scope, briefs, arch-score, budget-raise-gate, hassfest, validate-hacs, wave-script, delivery-status, codeql actions and javascript. Still in progress when read: tests / fast (3.14), closures, coverage, browser, mutation, governance / policy-docs, instrument-self-tests, env-matrix, codeql python. Failed: tests / nightly-status only, which grades main's scheduled Nightly and is not a required check and does not block (the body's Red checks section says the same). No completed red attributable to the branch; the in-progress legs are not confirmed green by this review.
