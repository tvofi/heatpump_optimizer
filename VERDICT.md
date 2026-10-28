Fix review: blocked b5a7138f59118ca4a103f806de4c8b64be980fdb ruling-incomplete: none of P176-P183 carries the Instances: field, and all eight are ACCEPT on an unmeasured benefit

bus-nonce: 49f90f9fd90e2391937862da48681edb

Round 1. Reviewed against `dev/governance/roles/proposal-triage.md` and `fix-review.md` at origin/main `c9cbe6b45`. `git diff <merge-base>...origin/main -- dev/governance/roles/` is empty, so the contracts are current.

## Block

1. **The `Instances:` field is missing from all eight rulings.** `proposal-triage.md` says a ruling carries `Verdict:`, `Source:`, `Instances:` (each counted instance with the command or log reference beside its figure), `Cost:` and `Binding:`. `grep -c '^Instances:'` gives 0 for `s6-batch31.md` at the head. Every other triage batch file on origin/main gives at least 1, and so does the sibling `s6-batch30.md` (8, including "Instances: none measured"); see `ev/instances.txt`. Without the field, no reviewer can re-run a per-ruling instance figure, because none is stated.
2. **All eight rulings are ACCEPT, but none has a measured benefit.** The contract says "an unmeasured benefit is DEFER, never ACCEPT". Each ruling's own `Binding:` says "Closure saving: 0 h in round 10", and none states a counted instance or a measured round-11 benefit. The tree's own precedent on this point is `s6-batch11.md:12`, `s6-batch14.md:14`, `s6-batch21.md:60`, `s6-batch22.md:22` and `s6-batch23.md:16` (`ev/precedent.txt`). The "tvofi-accepted F10/Q1..Q10" tags in `Source:` cite an out-of-tree `proposals.md` that I could not open. If the owner's acceptance is the decision, the ruling should say so and cite it as the owner ruling that decides, rather than present a cost/benefit ACCEPT the gate does not support.
3. **P176's destination names no owner.** "round-11 policy design item" names no dimension or group. Yet the P183 carry text ends "Each item states its round-11 owner seat", and its item (1) states none. The other seven name D0, D2, D3, D7, D10, D13 or D14.

What would clear the block: add an `Instances:` line to each ruling (for example "none measured" plus the figure the filing gives, cited). Then re-rule each as DEFER, naming R10-ROUND-PLAYBOOK as the owning carry and the measurement that would change the answer. Alternatively, keep ACCEPT only where an owner ruling in the tree is cited as deciding it. Name P176's owner as well (D11 governance is the natural one). The carry text can stay as it is apart from item (1).

Rulings I would change: P176-P183 from ACCEPT to DEFER (reason 2), and P176's owner (reason 3).

## Findings

- `roster_edit.ruling_verdict` reads only the `Verdict:` line. It returns ACCEPT for all eight rulings even though none has an `Instances:` line (`ev/ruling_verdict.txt`), so the tool that routes an ACCEPT does not enforce the ruling shape the contract requires. A field-presence check is a tooling proposal, so it is for the triage seat, not something this review builds. Carry: dismissed: a proposal for the triage gate, routed by the orchestrator's sweep rather than carried from a review; the reviewer check on this PR caught it at a cost of one round.

## Evidence

- RESULT head reviewed `b5a7138f59118ca4a103f806de4c8b64be980fdb` (`ev/HEAD.txt`), which is also the PR head the API reports.
- RESULT scope: the diff against the merge base `c9cbe6b45` is `dev/programme/delivery/2831.md` (+1) and `dev/programme/triage/s6-batch31.md` (+68) only, so it changes only the batch file and its delivery row (`ev/merge.txt`).
- RESULT merge: `git merge-tree --write-tree origin/main <head>` exits 0 with tree `0b8e5f61e`, so there is no conflict.
- RESULT host paths: `grep -E '/home|/Users|/tmp|~/'` on the batch file finds nothing.
- RESULT body figure: `grep -oE '^Verdict: (ACCEPT|DEFER|REJECT)' | uniq -c` gives 8 ACCEPT, 0 DEFER, 0 REJECT, which matches the body.
- RESULT null control re-run: `roster_edit.ruling_verdict(text, P176..P183)` gives ACCEPT for each, and P184 gives None (`ev/ruling_verdict.txt`). The body's figure holds when the function is passed the file's text. Passed the path, it returns None for every pid.
- RESULT per-ruling facts, re-derived at the stated base `dfcd8d9be`:
  - P176: `fix-review.md` lines 12, 28, 46, 88 and 134 hold mutation-vacuous, class-open, carry-missing, head-moved and architecture-unsound. R10-ORCH-REVIEW-PACKET exists, is not-started, lists `fix-review.md` among its files, and its carry 0 cites zero headroom.
  - P177: no Python file under the tree imports hypothesis, and no requirements file names it. The only "hypothesis" hit is a comment in `tests/card.mjs:7112`.
  - P178: the `tests/optimality.py` docstring says "Not an optimality proof".
  - P179: `tests/mutation_budgets.json` holds `max_survivor_fraction` {changed, full}, which is not per module.
  - P180: `ha_contract.py`, `ha_floor.py` and `nightly_ha.py` all exist.
  - P181: `stress.py`, `backtest.py` and `golden.py` all exist.
  - P182: the `typing_ruler.py` docstring ratchets three numbers (errors, by_code, type_ignores). `typing_budgets.json` exists, and `tests.yml:709` runs the ruler.
  - P183: `defect-root-cause.md:18` is the "reached a released version" trigger. D13, D14 and `tools/release/stamp.py` exist.
- RESULT destination: R10-ROUND-PLAYBOOK is present on the origin/main roster and on `handoff/audit-r10-roster` (`32ffe43c0`) at stage not-started, so it is live, with 5 carries.
- RESULT duplicates: no roster group or triage file on origin/main mentions the rubric, property-based tests, a per-module mutation score, escaped defects, unit types or a full-year gate (searched by keyword), and neither does `s6-batch32.md`. No ruling duplicates another in this file. `s6-batch30.md` P174 refers forward to V94 "ruled in batch 31", which is consistent.
- CI on the head: 7 check runs, 1 skipped (`arm`) and 6 queued (`prelude`, `refresh`, `cancel-superseded`, twice each). None has concluded and none is red, so the red-check trigger cannot apply yet. `pr-contract` has not reported on this head.
