Fix review: merge c32202c92dee44a30cef953fa5edf1a94b27e527

bus-nonce: 0d7a0bb6da4025bb503fa9444b697769

## Round

Round 3 is a delta review of 11e8075d..c32202c9. The delta holds no code. It has two merges: `33ca9a2f` brings in the authored head 0fec20feb (11e8075d plus origin/main f6784210, with the claim-file resolution), and `c32202c9` brings in origin/main 11b7a9d7, which is roster batch 17 / #2850. I measured from detached worktrees at the head and at the merge base 11b7a9d739db46a5a62e9f9cf01a8f527a974137, which is origin/main now. I ran `git ls-remote` before writing: refs/pull/2841/head and fix/r10-card-voice both read c32202c92dee44a30cef953fa5edf1a94b27e527, so the head did not move.

## Findings

- The round-2 carry is still open. The phone dialog's tooltip renders at 10.92 px, which is under the ramp's 12 px step. This PR states that as a design call it did not have to make, and the body routes it the same way. Carry: #201

## Evidence

- **1. The code is unchanged.** I took the three-dot diff over custom_components, tests/card*, tests/card_browser.mjs and dev/audit/harnesses at two points: 11e8075d against its base 7d205697, and the head against its base 11b7a9d7. Both diffs give the same stable patch-id, 839e4a87 (ev/code_delta.txt). `git diff 0fec20feb c32202c9` over the card, the rig, the browser harness, the drift harness, topology.py, the r10_card_* harnesses and docs prints nothing. Round 2's evidence therefore still holds. I re-ran the finder's harness at the head anyway:
  - Command: `PYTHONPATH=tests/hastub python3 tests/plan_view.py`, then `HPO_BROWSER_SCOPE=full node tests/card_browser.mjs`.
  - Result: rc=0, `ALL BROWSER CHECKS PASSED`, `P9 grid: 324 cells, 20375 text runs, 850 box-intersecting pairs inked, 105 colour rules` (ev/browser_head.txt).
  - `every cell mounted` and `no pop-up leaves the viewport or its chart` are both ok, so both round-1 failures stay gone.
  - Round 2's base run and null control are carried unchanged, because the code is byte-identical.
  - An earlier browser run of mine overlapped two of my own card mutants. That run also printed the same figures, but I discarded it as evidence (ev/browser_head_overlapped_by_mutants.txt). The run cited above is a clean re-run on the restored card (`cmp` equal, `git status` clean).
- **2. The "Closes #2506" decision.** I read the issue body and checked the body's ten-point table against it. Every point the issue states is in the table: the type disc, the wood tank's spring, the one accent pipe, configured-but-not-modelled spoken, the button naming the page with the path stated once, the chip on all-set boxes, the coil's three states in words with one visible at a time, the docs corrected, no new token voice, and the fixer.md proof obligations. I re-ran each command the table and the Figures name:
  - `node tests/card.mjs` at the head: rc=0, `ALL CARD CHECKS PASSED`. All eight named card checks print `ok` exactly once (ev/card_head.txt, ev/card_features_run.txt).
  - `PYTHONPATH=tests/hastub python3 tests/features.py`: `ALL 4433 FEATURE CHECKS PASSED`, including `ok the setup description tells a configured coil from a modelled one` (ev/features_head.txt).
  - `node dev/audit/harnesses/r10_card_voice_states.mjs <plandata>`, run in each worktree on that tree's own plan_view payload, with the head's harness copied into the base tree:
    - Head: active, off and none give badge_types 8/8/7, wood_badge coil / coil off / store, coil_pipes_accent 1/1/0, configure_buttons 8 of 8 boxes in every state, buttons_naming_page 8, and dest_caption 1. The coil wording shows one state per state.
    - Base: badge_types 0, wood_badge none, accent pipes 0, configure_buttons 5/4/4, naming 0, and dest_caption 0.
    - These match the body's Figures exactly (ev/voice_states_head.txt, ev/voice_states_base.txt).
  - Docs: `upper-right wall` reads 2 at the base and 0 at the head. `setup-contour` reads 12 at the base and 0 at the head in each of the three hydronic SVGs. `setup-coil` reads 2/1/1 at the base and 0 at the head (ev/docs_tokens.txt).
  - Tokens: there are 35 distinct `--hpo-` names at the base and 35 at the head, and `comm -13` is empty (ev/docs_tokens.txt).
  - My own mutants, planted in the head card one at a time and each restored afterwards:
    - R1 drops the ` coil-pipe` class on the coil edge. `node tests/card.mjs` gives rc=1 with `FAIL the coil's pipe is the one accent pipe, dashed when not modelled`.
    - R2 renames the `.setup-dest` paragraph's class. It gives rc=1 with `FAIL and the page states once where that page is` (ev/mutant_R1_coilpipe.txt, ev/mutant_R2_dest.txt).
  - Preflight, using pr-contract's own jq derivation over the live PR body:
    - Live roster (origin/main 11b7a9d7, R10-CARD-VOICE `issues [2506], fixes [2506]`): INTENDED='2506', `tools/pr/preflight.sh` rc=0.
    - Control, the roster just before batch 17's wire-issue commit c22e7b2e (8396866d, `fixes []`): INTENDED='', rc=1 with `REFUSE 'Closes #2506' closes #2506; not in the intended list` (ev/preflight.txt).
- **3. claimed_drift and merge.**
  - `git merge-tree --write-tree origin/main c32202c9` exits 0 with tree 2e122a4f. That tree diffs empty against the head's tree.
  - tests/golden/claimed_drift.txt at the head lists exactly six entries: this branch's five `coord_*` R10-CARD-VOICE claims and main's `config_flow` (#2753) line. The three-dot diff touches only those five claim lines and the added R10-CARD-VOICE comment block.
  - `claims-for: 7.0.4` appears in both claim files and equals VERSION 7.0.4.
  - `python3 tests/env_drift.py` gives rc=0, `NO UNCLAIMED DRIFT`, `NO STALE FIXTURE`, and no refusal of a fixture that is both claimed and may-drift. CI's `--all` judgement is in the green `tests / fast (3.14)` at this head.
  - VERSION, the manifest and RELEASE_NOTES.md are absent from the three-dot diff.
  - dev/programme/delivery/2841.md is in it (ev/merge_claims.txt).
- **4. carry_audit.** `python3 -I tools/audit/carry_audit.py pr 2841` reports `6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)` (ev/carry_audit.txt). The delta is merges only and changes no answer to the six roster carries, so I did not reopen them.
- **5. CI at this head.** I read the commit's check-runs API: 55 runs, all completed, every one success or skipped, none red (ev/check_runs.txt).
  - gate (121427020951) and pr-contract / pr-contract (121426780725, started 06:14:25Z) concluded success. That pr-contract run started after every other run had concluded, so it is the body-check evidence.
  - The body's `## Red checks` names and answers the reds of the range at 11e8075d: pr-contract and gate, tests / browser at 2cfb8b96, governance / delivery-status, and the local entities.py pair. Each one names a cheaper detector or states that none exists. It names no red that this head shows, because the head shows none.
- **6. Three-round rule.** This is round 3, and I flag nothing beyond the open carry above. I did not re-derive the body's mutant outputs M1–M20, MB, MC, MH1 or MH2, its harmony px figures (round 2 re-measured C1), card_drift's `44 state(s) moved and claimed`, the structure and archscore lines, or `closure.py select`. They describe code that is byte-identical to what round 2 measured, and CI's mutation, closures, arch-score and fast jobs are green at this head.
