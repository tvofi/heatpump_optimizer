Fix review: merge c84d561bbf8ce9ebe1f7c295bafc1f2f3fa1a896

bus-nonce: 5599ef569f1d24bfab69cfb9367b5bc4

Round 3 (delta review) of PR #2834, R10-ADVISOR-RESIDUE. Measured head `c84d561bbf8ce9ebe1f7c295bafc1f2f3fa1a896`, still the PR head by `git ls-remote` when this verdict was written (origin/main then `149ce54a36bcf9e794d357e0ef69dc8af62f8eb8`). Round 2 was MERGE at `9e212cd0e` (hpo-approver comment 6411221315, ev/prior-verdict-9e212cd0.md). This round judges only `9e212cd0e..c84d561bb`.

## Findings

- None blocking. The delta is four merges of main and no authored commit.
- Non-blocking: the PR body's `## Head` section repeats its `c84d561bb…` paragraph three times verbatim. The named head is correct; the duplication carries no fact. Carry: dismissed: cosmetic body text; the next body push regenerates `## Head`.
- Seam (a), the Plan page's what-if panel, stays open exactly as round 2 recorded it; this delta touches no production line, so it is not re-measured. Carry: #2257

## Evidence

The delta, `git log --first-parent 9e212cd0..c84d561bb`: `c38903518` (ci: merge main, bot), `5e37c15d9`, `7202e5cc0`, `c84d561bb` (merges of origin/main). `git log 9e212cd0..HEAD --not origin/main` lists only those four: no authored commit.

Merge resolutions, each merge re-merged with `git merge-tree --write-tree <p1> <p2>` (drivers installed) and its tree compared with the commit's:
- `c38903518`, `7202e5cc0`, `c84d561bb`: auto tree equals the committed tree (`8ed29d379`, `239c5a23b`, `488cda2c4`). No hand resolution.
- `5e37c15d9`: the claimnotes driver refused (`CONFLICTING CLAIMS: both sides rewrote the claim list`) on `tests/golden/claimed_drift.txt`; that file is the only path where the committed tree differs from the auto tree. The hand resolution (ev/5e37c15d-claim-resolution.txt, `git show --cc`): this branch's five `coord_*` R10-ADVISOR-RESIDUE claim lines kept; main's five R10-CARD-VOICE bare lines for the same five names dropped (main's own diff's claims, inert on this branch per claim-files.md: a line excuses only the diff that wrote it); main's R10-CARD-VOICE note kept as a comment; main's `config_flow` claim kept. That is the resolution claim-files.md asks for: branch claims kept, main's notes unioned.

Claim files at the head:
- `claims-for: 7.0.4` in both files; `VERSION` is `7.0.4` at the head and at origin/main.
- `card_claimed_drift.txt` is byte-identical to the base `1f82fee49`.
- The five coord fixtures differ from the base `1f82fee49` in exactly one line each: `+  "recent_kwh_price": null,`. Main's `dhw_wood_coil_configured` leaves auto-merged and are not in the branch's diff.
- `tests/env_drift.py --all 1f82fee49…` at the head: `NO UNCLAIMED DRIFT: 56 scenario(s)`, `NO STALE FIXTURE: 56 committed fixture(s)`, rc 0 (ev/envdrift-head.log).

No production behaviour beyond round 2's approval:
- `git diff ed1c9045e 9e212cd0e` (round 2's branch diff) and `git diff 1f82fee49 c84d561bb` (this head's) both stat `30 files changed, 594 insertions(+), 50 deletions(-)` (ev/old-branch.diff, ev/new-branch.diff).
- `custom_components/`: the hunks are identical once `index` and `@@` line-number headers are stripped (`heatpump-optimizer-card.js` hunks shifted by main's R10-CARD-VOICE rewrite of the card). `docs/`, `dev/`, the coord fixtures: byte-identical diffs.
- The only content interdiff is in `claimed_drift.txt` (context lines from main's side) and `tests/structure_budgets.json` (`class_excess_loc` base 18080 -> 18079 here, 18086 -> 18085 at round 2; `max_class_loc` 8241 -> 8236 at both). Both are lowerings; no budget rises.
- The finder's harness was not re-run: the delta adds no production line.

Gate and contract:
- `tests/structure.py` at the head: `STRUCTURE RATCHET PASSED` (ev/structure.txt).
- VERSION, manifest version, RELEASE_NOTES.md heading: unchanged in the three-dot diff.
- PR body `## Head` names `c84d561bbf8ce9ebe1f7c295bafc1f2f3fa1a896`, equal to the measured head (ev/pr.json).
- `git merge-tree --write-tree origin/main(149ce54a3) c84d561bb`: rc 0, tree `f593321f6` (ev/merge-tree.txt). The same command with both drivers replaced by plain `git merge-file` (what GitHub runs): rc 0, the same tree `f593321f6` (ev/merge-tree-nodriver.txt). GitHub reports `MERGEABLE`, `BLOCKED` (review pending).
- CI at the head, from the check-runs API (ev/checkruns-head.txt, 55 runs): all completed; 39 success, 16 skipped, 0 failure. `gate` (both runs), `pr-contract / pr-contract` (both runs), `tests / fast (3.14)`, `tests / mutation`, `tests / closures`, `tests / coverage`, `tests / coverage-ratchet`, `governance / instrument-self-tests`, `governance / delivery-status`, codeql all success. No red check at any commit of the delta needs a body answer.
