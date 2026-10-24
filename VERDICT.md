Fix review: merge 16d3ee72ad7de8ed0ec2a14b40d5bda23e500310

bus-nonce: 8ddd6a54243f2ba1376d6dcb84b50dfb

Round 1. PR #2681 (R10-ORCH-LEDGER), RCA `dev/audit/rca/R10-RCA-2671-WAVE-SCRIPT.md` + `bugclasses.json` I3 citation. Measured at head `16d3ee72ad7de8ed0ec2a14b40d5bda23e500310` (re-read before posting: unchanged). Roles contracts current (merge-base...origin/main diff empty).

## RCA completeness (`root-cause.md`)
- Cause: three named (base-vs-head pinned-grader direction; `ref_privacy.py --check` absent locally; no passing tree for a new `SHARED_GRAMMARS` entry). Cause 1 reproduced by me: on 338c9ba49's `agreement_py.py --out` JSON the branch `agreement.mjs` prints `unregistered=0`, the fd7e289d0 copy `unregistered=3` on the same three grammars the RCA names. I did not rebuild CI's merge tree + full restore or the #2669 null control; those rows are the RCA's, not re-derived. `refused=1` on both my runs is the live-origin/main artifact the RCA's section 1 warns of.
- Cause 2 re-derived: `ref_privacy --check` 1 refused (`ledger.py:726`) at 338c9ba49, 0 at head; `grep -c ref_privacy tools/pr/prepr.sh` = 0.
- Process state: (c) x3 with evidence (3f4 ran and passed reading the head's copy; CI-only check; base-pinning followed as designed). Barriered class I3: names why the barrier's unit (steps 3e-3g, head direction) missed it and proposes a unit change (A), not an arm count. Consistent with `root-cause.md` §2.
- Cost test: one unit (wall-clock s per PR), P measured (3/440; 2 instances for cause 2), verdicts A build / A' refused / B build / C owner decision. Run 39996377402 duration 9m47s re-derived. #2423 merged with wave-script=failure at 58dbe46a0 re-derived. Not re-derived: the 25/440 and 147/440 counts, 15 s arm timing, 1.46 s B timing, and the "first SHARED_GRAMMARS addition since #1847" enumeration.
- Countermeasures A and B have fire/pass demonstrations in the RCA (A's not re-run by me beyond the copy comparison above).

## Register and carries
- `fold_ledger.py check`: 0 violation(s), 120 rca entries. `_rca` entry fields complete, `status: proposed`, `landed: null`.
- `carry_audit.py --roster-ref origin/handoff/audit-r10-roster pr 2681`: 2 routed, 0 unrouted, 0 bad destination(s).
- A+B: R10-FLY-CIPREDICT-LAYOUT `carry[2]` on `handoff/audit-r10-roster` (tip f643b8527), states CI's restore, the narrow key, the `refused=3` trap, controls and re-measure instruction. Present.
- C: R10-MERGE-SUBJECT-HARDEN `carry[2]`, landed at 10692eba5 (ancestor of tip), states the deadlock, both controls, #2423 precedent, both candidate routes, and the acceptance precondition. Present. Both groups `not-started`.
- #2505 Root cause comment 6377728956 matches the RCA on state, causes, cost figures and countermeasures.

## Checks
All head check-runs success/skipped/neutral except one pr-contract run (120732707724, 00:48Z) red in the `codescan_wait.py` step (code-scanning wait, not the authored diff); the later pr-contract run 120732444754 (00:57Z) is success. No gate check red on any of the PR's four commits. `merge-tree --write-tree origin/main HEAD` rc 0. VERSION/manifest/notes untouched (diff is 3 files under `dev/`).

## Non-blocking notes
- The body's C Forward-carry line and the #2505 comment still say C is held and "not on handoff/audit-r10-roster at 6ae3061f9"; it landed at 10692eba5. Body edit (no head move) and comment refresh owed by the orchestrator, naming 10692eba5. Carry: R10-ORCH-LEDGER
- C's carry text cites the RCA "on handoff/r10-rca-2671-wave-script"; that ref goes stale once this merges (the path on main resolves it). Carry: dismissed: path is in the carry text and resolves on main after merge
