Fix review: merge 7ae5e30e0df57b522d527945d398ccc547e0389b

bus-nonce: 4842c50acd697be76cc297189b4bdcb7

## Scope

DELTA review of #2745 (R10-SAV-COMFORT) from the prior merge verdict at 1b6df0e492decf43f14575faaa991408eb81501d to 7ae5e30e0df57b522d527945d398ccc547e0389b. Scope is the hand-resolved conflict in tests/golden/claimed_drift.txt; the fix itself was not re-reviewed.

## Evidence

- One commit in range, the merge 7ae5e30e0 with parents 1b6df0e49 (the prior head) and 0825aee64 (origin/main). merge-base(prior, main) = b89fea13e. The claim file has 721 lines at the base, 777 at the prior head (+56: PR), 730 at main (+9: main), 786 at the new head (721 + 56 + 9). ev/claimed_drift_threeway.txt.
- Main's change to the claim list (base to main): the five R10-SCORES lines (coord_all_features, coord_dhw, coord_grid_fee, coord_minimal, coord_two_zone) were REPLACED by five R10-LEARNER-ETA lines on the same fixtures plus a nine-line R10-LEARNER-ETA comment block. Main kept its R10-SCORES (#2258) explanatory comment block; the head keeps it too, as main does.
- PR's change (base to prior head): 41 R10-SAV-COMFORT claim lines added after the claims-for stamp, and fourteen `# may-drift:` entries rewritten as suspension notes for fixtures it claims.
- Head vs prior head: the only change is the five R10-SCORES lines replaced by main's 14-line R10-LEARNER-ETA block, byte-for-byte as on main. Head vs main: every difference is a PR-side change (41 claims, suspension notes); no main line is missing.
- Line ledger. Kept: all 41 R10-SAV-COMFORT claim lines (count at head: 41, text and direction words identical to the prior head), all fourteen suspension notes, main's R10-SCORES comment block. Added from main: the five R10-LEARNER-ETA coord_* claims and their nine-line comment, verbatim. Dropped: the five R10-SCORES coord_* claim lines, which main itself replaced. No claim lost, none invented.
- Mechanical check: `git merge-file --union` of (prior, base, main) differs from the head only by those five R10-SCORES lines. `git merge-tree --write-tree` of the two parents conflicts only in tests/golden/claimed_drift.txt (the claimnotes driver's MERGE-CLAIM refusal, ev/automerge_P_M.txt); the head's tree differs from that auto-merge tree only in that file, by the conflict markers and the five dropped lines (ev/head_vs_automerge.txt). Every other file the merge touched equals the clean auto-merge, so the head merge changed no code by hand.
- `claims-for: 7.0.4` at the head; VERSION at the head is 7.0.4 (ev/claims_for.txt).
- `python3 tests/env_drift.py` at the head: rc=0, NO UNCLAIMED DRIFT on the 5 sensitive fixtures against origin/main bc52ad2af, NO STALE FIXTURE, no claimed-and-may-drift refusal; the 36 R10-SAV-COMFORT scenarios are NOT EVALUATED in that mode, as it prints, and are judged by CI's `--all` (ev/env_drift.txt).
- Change set: `git diff 1b6df0e49 7ae5e30e0 --stat` names 67 paths; `git diff b89fea13e 0825aee64` names the same 67, symmetric difference 0, so every path is main's own. Three-dot against origin/main: 47 paths at the prior head and 47 at the head, symmetric difference 0. Three-dot over claimed_drift.txt removes no line other than `# may-drift:` entries (0) and adds 71; card_claimed_drift.txt three-dot diff is empty (ev/stat_and_scope.txt).
- `git merge-tree --write-tree origin/main 7ae5e30e0` with origin/main at bc52ad2af: clean, tree a09d009d4, rc=0 (ev/merge_tree_origin_main.txt).
- VERSION, the manifest and RELEASE_NOTES.md are untouched by the branch.
- CI at this head (check-runs API, read 2026-10-25): no red conclusion. Green: closures, closure-scope, coverage, coverage-ratchet, typing, replay, browser, arch-instrument, nightly-status, delivery-status, instrument-self-tests, wave-script, briefs, policy-docs, env-matrix, hassfest, arch-score, budget-raise-gate, validate-hacs, codeql javascript-typescript and actions. Still in progress when read: tests / fast (3.14), tests / mutation, tests / graders-head-copy, codeql / Analyze (python), one prelude. This verdict does not cover their results; the merge train reads them.

## Findings

- The PR body is stale on the claim resolution at this head. Its "The claim file keeps main's claims" paragraph still says main's five R10-SCORES lines "stand verbatim", which is false at 7ae5e30e0, where they are replaced by main's R10-LEARNER-ETA lines (correctly). The `## Head` section says the head merges origin/main `50af6174f`; the merged main parent is 0825aee641c8afb1e67be2a6af9d07e9c9dec9fa (50af6174f is #2686, an older main). The commit message names the resolution correctly and the tree is right, so this is a body-only edit owed before the merge records the body. Carry: R10-SAV-COMFORT
