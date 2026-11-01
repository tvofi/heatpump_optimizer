Fix review: blocked b1a0be47da301a23025cf40671053b5dbf6b129b claim-stronger-than-check: claim-files.md says a may-drift deletion wins over the other side's silence, but the driver reinstates it when the other side edited an adjacent line; the theirs-deleted scenario rule has a surviving mutant

bus-nonce: e2ba7157c1d3673cc930d107f1c70210

## Block

Round 1, the first review of this PR. I measured head `b1a0be47da301a23025cf40671053b5dbf6b129b` from detached worktrees at that head and at merge base `2b6bef7453a8bdaf97d42f382a116ce226b35ccc`.

1. **The new policy sentence states more than the driver does** (brief CHECK 2 and 4; CLAUDE.md rule 3). The new `claim-files.md` text says: "a side's change or deletion (a `may-drift` line too) wins over the other's silence". Plant this merge: this branch deletes `# may-drift: flat_prices -- polish` (the R8-P3 suspension), and main leaves that line alone but rewords the adjacent `# may-drift: wood_coil` line. `_union_comments` runs `git merge-file --union`, which keeps both sides of the overlapping hunk. The result therefore reinstates the deleted `flat_prices` may-drift line, and keeps main's reworded `wood_coil` line next to the old wording. `merge_claim_defect` checks only for may-drift lines that were **lost**, never for ones reinstated, so the driver prints `resolved` (ev/adversarial.txt row `D2`).
   - Unpaired with a claim (a branch retiring an entry whose removal condition fired), this widens the exemption silently.
   - Paired with its claim (the normal suspension), the driver resolves to a file that the gate's `may_drift_error` then refuses with `CLAIMED AND MAY-DRIFT` (ev/adversarial-d2-claimed.txt). That fails closed, but only after the driver has reported `resolved`.
   - The base driver produces the same result for D2, so this is not a regression of the code. The defect is the new sentence, which claims a guarantee the check does not give.
   - Repair, either way: the defect check refuses a result that carries a may-drift line that was in the base and is missing from one side, or the text drops the guarantee. A failing fixture for D2 comes first.
2. **A surviving mutant on the deletion rule, theirs-deleted direction** (fix-review.md step 1). Mutant: `if mine == main or mine == was: lines = our_blocks.get(name) or their_blocks.get(name)`. On the probe (main deletes scenario `alpha`, the branch leaves it alone), it brings `alpha` back: `['alpha','beta','gamma']` against the head's `['beta','gamma']` (ev/m3-survivor.txt). The committed suite still reports `ALL 20 CM PASSED` under that mutant (ev/mutants.txt). That reinstatement is the very hazard the driver exists to prevent. `_CM_BASE_HELD` pins only the direction where this branch deletes. The body's M3 is killed; this variant on the other branch is not. It needs a fixture where main deletes a claim that the branch left alone. The `tests / mutation` lane is green, but it did not draw this mutant.

Policy: the diff changes `dev/governance/rules/claim-files.md` under mandate 6329234399. It merges only on `tvofi`'s approving review at its head. I did not block on that.

## Findings

- Surviving mutant, fail-closed direction: `if mine == main or mine == was:` changed to `if mine == was:` makes the driver refuse when both sides made the identical change, and the committed CM section still passes (ev/mutants.txt, `R-mine-eq-main-only`). It refuses rather than widens, so it does not block, but no committed check pins that the identical-change case resolves. My adversarial rows `E-both-add-identical` catch it. The fix is one fixture in the same section. Carry: R10-996-RUNNER-CLAIMS
- A may-drift line one side deleted and the other side rewrote resolves, keeping the rewrite: theirs suspends `flat_prices`, ours rewords it, and the result has ours' reworded line (ev/adversarial.txt row `D3`). A claim in the same shape refuses (row `C`). The base behaves the same, and the new text's "wins over the other's silence" does not cover the case, because neither side was silent. So the may-drift block is not merged with the claim rule's delete-against-edit refusal. Decide this together with Block 1. Carry: R10-996-RUNNER-CLAIMS

## Evidence

- Finder's harness. None is committed for the replay. `dev/audit/harnesses/claim_merge_census.py` is the fixer's, so I disclose my own: `ev/reviewer-instruments/replay.sh`. It runs the driver CLI exactly as git invokes it (`--merge-claim-file %O %A %B %L %P`) over the seven merges in P196's list (`dev/programme/triage/s6-batch34.md`). I took the refs from P196, and they equal the census's CASES. Results (ev/replay.txt):
  - Base driver: all 7 `MERGE-CLAIM: refused`.
  - Head driver: #2841, #2745a, #2745b, 3a07c2eaa and e438816e3 `resolved`; #2834 and 5bf232eac `refused`.
  - The head's refusal names each scenario with both sides' reasons: #2834's five `coord_*` scenarios, and 5bf232eac's `valve_storage_*` scenarios that one side deleted and the other rewrote (ev/replay-stderr.txt).
  - My re-derived census: resolved=5, refused=2. That equals the body's figure.
- The fixer's census re-run at both ends (ev/census-base.txt, ev/census-head.txt). I ran the base end with the base driver at `2b6bef745`; the body names `a7dd7f50d`, which I did not re-run. Every per-row count matches the body: `RESULT resolved=0 refused=7` at the base, `RESULT resolved=5 refused=2 hand_same=1 hand_differs=1` at the head.
- The body's "the per-scenario rule alone resolves 2 of 5; the may-drift check refused the other 3". Re-derived: mutant M5 (two-way survival check restored) gives census `resolved=2`. In #2745a and #2745b, this branch suspends `flat_prices` and claims it once in the merged file. In e438816e3, main deleted the `flat_prices` may-drift line.
- My mutants (ev/mutants.txt): M1, M2, M4, M5 and M6, plus my own deletion-keeps mutant, are all killed by the committed CM section. The brief's "drop the stamp check" is M4, and "take ours on conflict" is M2. M3 in my placement survives (Block 2). `R-mine-eq-main-only` survives (Findings).
- Adversarial plants (ev/adversarial.txt, base and head):
  - These refuse at the head and name the scenario: both sides rewrite one scenario (`A`); differing stamps with both sides changing claims (`B`); delete against edit in both directions (`C`, `C2`); both sides add the same scenario with different lines (`E-both-add-differing`); a multi-line split (`H`); the same shape key with different reasons (`J2`).
  - These resolve correctly: delete against silence (`C3`, stays deleted); both sides add the same scenario identically, alone and with disjoint additions; the disjoint null (`I`); different shape lines added on each side (`J`); a may-drift deletion against a changed neighbouring *claim* (`D`, stays deleted with the claim kept).
  - `B2`: main bumps only the stamp and this branch adds a claim. It resolves at both base and head, unchanged.
  - D2 and D3 are the rows in Block 1 and Findings.
- Null control: the disjoint merge (`I`) and `E-both-add-identical` resolve at the head as they do at the base wherever the base resolved them. `a claim list only one side touched is carried, not refused` passes.
- `git merge-tree --write-tree origin/main b1a0be47…` (origin/main `61b0076f4`, merge base unchanged at `2b6bef745`): rc=0, `LEDGER-MERGE: resolved tests/closures.json`, no claim-driver line (ev/merge-tree.txt).
- The claim files are byte-identical three-dot against the merge base, and identical to the origin/main tip (ev/claims.txt). VERSION, the manifest and RELEASE_NOTES are untouched (ev/version.txt).
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`. `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`. `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `tests/closure.py select --diff 2b6bef745`: `MODE: SCOPED -- 7 script(s) run, 26 scoped out.`, which equals the body's figure.
- `tools/audit/archscore/score.py --diff 2b6bef745` (three-dot from the merge base): `Architecture score: dS +0.0000 NULL`, which equals the body's figure. No budget, ledger or calibration figure moves. The only `tests/closures.json` change classifies the new harness.
- `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all 2b6bef745` at the head: `NO UNCLAIMED DRIFT: 56 scenario(s) checked`, `NO STALE FIXTURE: 56 committed fixture(s) still match`, exit 0 (ev/env_drift_all.txt).
- CI at this head: `merge_train.py classify` printed `GREEN b1a0be47… pending: none red: none`, exit 0 (ev/classify.txt). `get_check_runs` returned 55 runs in total, all success or skipped and none red, so the body's `## Red checks: none` holds.
- Forward-carry: Carry 3 (P214) is on `origin/handoff/audit-r10-roster` at `5cfbe719e`, as written, in group R10-996-RUNNER-CLAIMS. The group's `files` are still `tests/env_drift.py` and `tests/golden/claimed_drift.txt`, so the edit-brief has not landed and the carry is pending. The body cites no roster SHA, so I verified at the current roster tip. I accepted the carry as a control for nothing.
- The delivery row `dev/programme/delivery/3066.md` is in the three-dot diff.
- The diff edits files outside the group's `files`: `tests/entities.py`, `.gitattributes`, `tools/pr/app_approve.sh` (comments only), the claim-files rule and its copies, `tests/closures.json` and the new harness. These are tests, comments and policy under the mandate. I did not block on them.
- e438816e3 `hand=differs`: the driver keeps four scenario lines that main's hand resolution dropped. Those lines are inherited from main, so at a PR's three-dot diff they are inert. I accept the body's reading but did not run the gate over both results.
- The head was `b1a0be47da301a23025cf40671053b5dbf6b129b` at measurement (ev/HEAD.txt).
