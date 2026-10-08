Fix review: merge 9d9f44ad296c1dbda6d94974cb05dac1493a35f4

bus-nonce: 40f3914e04972746b5b21649dd897ed6

This is round 2. I reviewed the change from round 1's `8e0dcb72c`: `6b45b61b9` adds the delivery row and `9d9f44ad2` is the repair. Merge base is `4dbe5aace`, the worktree was detached at the head, and the evidence is in /Users/timmalmstrom/hpo-seats/review-2064/evidence-r2. Live head re-read at 2026-10-08T22:54:02Z: unchanged.

## The round-1 class-open block, item by item

- **Constants.** The new text reads "a constant beside the module owning it, one shared across modules in `const.py`". That matches the tree's per-module constants, and the 531 found in round 1 no longer conflict with it. Closed. Residual note below.
- **Module state.** The text reads "module state only as a per-coordinator `WeakKeyDictionary` side table". The side-table pattern is named as allowed, so it no longer pulls against `attrbag_classes_over_30`. The body lists the 5 other existing sites, and they stand because only added lines are judged. Closed.
- **Side effects.** Store, network, notification and issue-registry calls are now allowed in the module that owns that edge. Closed.
- **Exceptions only in the body.** Step 17 says "Soundness is judged on added lines" and step 15 says "Judge `fixer.md` step 17 on added lines". So existing code is not a breach. The policy also names the HA-import holders ("`dhw_learning.py`, `defrost.py` and others hold one"). Closed.
- **"Minimal".** Cut. The scope clause is restored as "the preamble's scope still binds, and a fix that cannot be sound within it stops and asks the orchestrator". Closed.
- **Architect note.**
  - orchestrator.md section 5 says the orchestrator dispatches it into each group's roster brief.
  - fixer.md 17 says "a group's architect note ... followed".
  - fix-review.md 15 blocks "a departure from the architect note".
  - Closed.
- **One migration per release.** Cut. Closed.
- **"D7 and archscore held".** Now reads "`tests/structure.py` and `tools/audit/archscore/score.py --diff` not regressed, or the raise path below". I checked that the path and the `--diff` flag exist (score.py lines 20 and 119). The raise wording reads "where only it lands the better architecture", which fits tvofi's last-resort ruling and points to the existing path. Closed.

## RESULT lines (CI venv, at the head)

- RESULT `policy_lint` rc=0 with `TOTAL: 0 error(s)`. `--budgets` rc=0:
  - fixer.md 315/315 lines and 5216/5216 tokens, at its raised cap;
  - fix-review.md 137/140 and 2384/2393;
  - orchestrator.md 290/291 and 4090/4096.
- RESULT `rules_sync --check` ok. `brief_lint` rc=0. `structure.py`: STRUCTURE RATCHET PASSED.
- RESULT `check-wave-script.mjs`: 172 passed, 0 failed. Its taught-class arm is the body's mutation proof.
- RESULT `bus.sh --self-test`: 45 checks, 0 failed.
- RESULT `merge_train.py --self-test`: 80 checks, 0 failed. Round 1 could not run it because the disk was full.
- RESULT the raise is minimal. 315/5216 equal the measured values. The +5 lines and +107 tokens over round 1 pay for the tree-true wording, the architect-note binding and the restored scope clause.
- RESULT payments. I judged each payment the body lists:
  - The orchestrator.md clauses are rationale or restatements, with the rule kept: "at each merge" and "go now" survive.
  - fix-review step 11 keeps its heading "Cite CI's heavy runs".
  - No unlisted payment: three-dot diff vs `4dbe5aace`. Every removed line maps to a listed payment.
- RESULT VERSION, the manifest and the notes heading are untouched.
- RESULT #2063 overlap. I simulated main + #2063 (`f118161`) + this head:
  - the only conflict is `dev/governance/config/policy_budgets.json`, on the adjacent fix-review and fixer cap lines;
  - resolved to fix-review 141/2449 from #2063 and fixer 315/5216 from #2064, `policy_lint` gives `TOTAL: 0 error(s)`, with fix-review.md at 140/141 lines and 2446/2449 tokens;
  - check-wave-script reports 0 failed.

  The second to merge recarries only the budgets file, with no raise. The body's forward-carry claim is confirmed.
- RESULT check-runs at the head: 40 runs, all concluded by 22:38:45Z, and `fast (3.14)` and `coverage` passed. `pr-contract` started at 22:38:29Z, after the last red concluded at 22:32:09Z. Two checks are red, and the body answers both:
  - `budget-raise-gate`: the raise awaits tvofi's review at the head (0013). The orchestrator accepted it under the mandate.
  - `nightly-status`: it grades main's scheduled run, and the diff does not reach `tests/nightly_status.py`.

## Non-blocking note: the constants wording is still wider than the tree

"one shared across modules in `const.py`" is not how the tree holds a shared constant either. 45 distinct ALL-CAPS constants are imported across modules from their owning module rather than from const.py, at 61 import sites. Examples are `freq_control.FREQ_MODE_CONTROL`, `ledger.KEEP_MONTHS` and `dhw_learning.DHW_PROFILE_STORE_VERSION`. The rule was "relative `from .X import NAME`, X != const, NAME all-caps" (evidence-r2/shared_constants.txt).

The body's "This matches the tree" is true of per-module constants and not of shared ones. Round 1 suggested this wording, so I do not block on it.

A reviewer reading it literally could flag a fix that adds a new consumer of an owner's constant. The suggested follow-up wording is: "beside the module owning its concept, imported from there; `const.py` for configuration keys and constants no single module owns". It belongs in a later policy edit, not in this round.
