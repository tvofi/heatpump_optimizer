Fix review: merge ece8328001608ff93f5138392f6e6c15420c8929

bus-nonce: 6fb2aabf12c4e1c8135f46ff0197bfd9
pending-ci: gate

## Scope

Round 4 of this branch's review: a delta review of PR #3562 at head ece8328001608ff93f5138392f6e6c15420c8929. The reviewed head is ced9b233580709f530d5dc402dc12344697fef87, which has a merge verdict (round 3) on probe/rev-3562-c9556b39, commit ac612b540f. That verdict's `## Findings` reads `none`, so there is no prior finding to resolve. The packet's `## Review scope` reads `full` only because no verdict on verdict/3562 names ced9b233. The dispatch scopes this round as a delta, and fix-review.md step 12 agrees: `review_carry.py ced9b233 ece83280` prints FRESH-REVIEW, so this round reviews the delta.

The delta has three merges. 066e497fbd merges PR 3580's head ec9645014c into ced9b233. ac31599707 merges PR 3576's head 8317d9e1b2. ece8328001 merges ac31599707 into the branch. ced9b233 is an ancestor of ac31599707, so that last merge is a no-op: its tree equals ac315997's tree, af8e648eef, and the handoff ref handoff/r10-hotfix-boost-flow-ceiling is ac31599707. The two train heads are reviewed PRs in the batch and are not under review. Only the resolution is under review.

## Evidence

- RESULT remerge-diff: `git show --remerge-diff` reports conflicts only in strings.json and translations/de.json, en.json and sv.json at 066e497fbd. At ac31599707 it reports only sv.json. ece8328001's remerge-diff is empty. docs/configuration.md is touched by both sides and merged automatically with no resolution. The output is in ev/remerge-diff.txt.
- RESULT oracle-keys: I flattened every leaf key in the four JSON files at the head. The oracle is the merge-tree of the two train heads, ec9645014c and 8317d9e1b2, tree 497c7a0095, which merges cleanly (rc 0). PR-owned keys are those ced9b233 changes against its main parent c987209cc7. For each file, the 2 PR-owned keys match ced9b233 and the other 1505 keys match the oracle: 0 mismatches. The 2 PR-owned keys are indoor/data_description `space_setpoint_entity` and `flow_heat_c`. The oracle leaves both unchanged against main 513a07dfdc, so the PR side drops none of the train's text. The sv `space_setpoint_unit` value equals the oracle, which is PR 3576's wording, as the brief states. The outputs are ev/keys-oracle.txt and ev/pr-owned-keys.txt, and the script is ev/keys.py.txt.
- RESULT paths: every path where the head differs from the oracle is either a PR-owned path equal to ced9b233 that the train does not touch, or one of the 4 JSON files and docs/configuration.md, which both sides touch (ev/paths-head-vs-oracle.txt). strings.json and translations/en.json are identical as parsed JSON at the head.
- Production delta, judged for widening: the delta's custom_components/ changes are the train's wording in strings and translations, plus away.py, where PR 3576 or 3580 drops `AwayConfig.legionella_before_return` and edits the docstring. `git grep legionella_before_return` at the head finds nothing in custom_components/ or tests/. This PR's reviewed code in pump_arbiter.py, off_restore.py, const.py and config_flow.py does not read away.py's config, so I found no non-obvious risk and did not widen the review.
- RESULT merge-tree: `git merge-tree --write-tree origin/main ece83280` at origin/main a77d71fb75 exits 0 (ev/merge-checks.txt).
- Step 5: the branch does not touch VERSION or the manifest. Its RELEASE_NOTES.md change, an upgrade note under an existing section, was reviewed in an earlier round. The delta does not touch it, and it changes no heading.
- Step 7: the body's `## Head` names ece8328001608ff93f5138392f6e6c15420c8929 and the authored code head ac31599707, and describes the union resolution as I measured it.
- Mutation proof and finder's harness: the delta writes no production code line of this PR's own, so I re-ran no mutants. The packet names no finder's harness. Earlier rounds measured this PR's own code. The packet's carry_audit gives the body's one Forward-carry item a route: `dismissed: owner ruling 2026-11-13`.
- CI: `merge_train.py classify ece8328001608ff93f5138392f6e6c15420c8929 --pr 3562` printed `WAIT ece8328001608ff93f5138392f6e6c15420c8929 pending: gate red: none` (rc 3) on every run from 10:36 to 11:07 UTC, about 31 minutes of polling (ev/classify-poll.txt). No required check was red. `review_packet.py` refused with `introduced-red: unreadable` only because instrument-self-tests was still queued at render. Classify decides, and it reported WAIT, so I am returning this as a pending-ci draft.
- No figure in the body moves in this delta (figure_lint at the head: 0 resolved, 0 refused). The round-3 verdict verified the body's figures and they are unchanged.

## Findings

none
