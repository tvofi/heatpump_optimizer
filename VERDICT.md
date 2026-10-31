Fix review: merge 958b4af8eee134728986d92d2220f1dfadbab255

bus-nonce: 6825f0c12840c20277c40491eec13095

## Round

Round 2 of the fix review for PR #3006 (R10-COP-PARTLOAD part 2). Round 1 blocked dfb981d7a with class-open. This review covers head 958b4af8eee134728986d92d2220f1dfadbab255, the authored code head 410f8d509 merged with origin/main 5d4e0bcfb. I worked from detached worktrees at the head, at round 1's head dfb981d7a and at the round-1 merge base cf4f6b7a6. The role contract has not moved: `dev/governance/roles/` is identical between the merge base and origin/main.

## Findings

- Linear valuations under a convex cost: the hot-water LP's objective `prices / cop`, `optimizer.row_cost`, `_deferred_energy_cost` and the wood advisor's pump-heat price stay secant under-estimates under a derate, and are left for a later D0 pass. It is on the roster at `handoff/audit-r10-roster` 1e9f14dd3, `R10-COP-PARTLOAD` carry[4], with "FIRST measure the magnitude ... with a zero-derate null control that must read 0" as its precondition. Carry: R10-COP-PARTLOAD
- Mean-draw pricing: the setpoint sweep and the always-hot baseline price hot water as a steady mean draw below the modulation floor. It is on the roster as carry[5], with its measure-first precondition and a zero-derate null that must read no change. Carry: R10-COP-PARTLOAD
- The live buffer store's CPU cost (carry 2b) is not built by this PR. It is held at roster carry[2]. Carry: R10-COP-PARTLOAD
- `budget-raise-gate` is red because the head raises the D2 brief's policy caps (51 to 53 lines, 644 to 683 tokens) and changes D2.md item 2, which is policy. The brief says to flag it, not block on it: it merges only on tvofi's approving review at the head, or on the orchestrator's approval under mandate 6329234399. The required check enforces that. Carry: dismissed: owner approval at the budget-raise gate, enforced by the required check, not a defect of the change

## Evidence

- RESULT enumeration: `python3 dev/audit/harnesses/r10_cop_conversions.py` at the head prints `RESULT hits=95`, `RESULT plain=54`, which matches the body (ev/enumeration_head.txt). The 54 PLAIN hits are, by function, exactly the body's disposition list.
- RESULT independent rule: my own line regex (ev/independent_grep.py) takes a `*` or `/` next to any identifier containing `cop`, excluding copy, scope and string literals. It matched 84 code lines. 67 are enumeration hits. The other 17 are docstrings or comments (accuracy.py, thermal_model.py, dhw_planner.py:1352), the continuation line dhw_planner.py:2154 of the routed hit at 2152, and `coordinator._observe_cop_health` lines 9196-9226. Those divide a COP by a lift, a baseline or a count: COP-ratio arithmetic, not a heat/power conversion. A further check found every `= ...compute_cop(...)` assigned to a name without `cop` in it, and only `accuracy.py` `modelled` turned up, the difference between two COPs. No seam is unaccounted for, so the class is closed.
- RESULT mutation, `PYTHONPATH=tests/hastub python3 tests/features.py`, head clean: `ALL 4637 FEATURE CHECKS PASSED` (rc=0). The body's 4618 was taken at 410f8d509, before the main merge. Each round-2 site reverted to its round-1 line (ev/mutants.py, ev/mutant_*.txt), with the failed count out of 4637:
  - G1 cheapest-first increment: 1, the cheapest-first check.
  - G2 cheapest-first spare heat: 1, the cheapest-first check.
  - B1 always-hot baseline: 1, the always-hot baseline check.
  - L1 legionella run-up rise: 1, the run-up check.
  - R1 repair `needed`: 1, the repair check.
  - R2 repair `room_kw`: 1, the repair check.
  - C1 `_capacity_caps`: 1, the capacity-caps check.
  - T1 `_tighten_buffer_caps`: 1, the tightening check.
  - V1 `charge_rate_kw`: 1, the battery check.
  - A0 helper derate branch deleted: 4, the increment round trip, cheapest-first, repair and tightening.
  This is the body's table, row for row. No mutant is vacuous.
- RESULT zero-derate null, the finder's harness `dev/audit/harnesses/r10_cop_partload.py` (the same blob 9b24e0494 at all three trees), run at cf4f6b7a6, dfb981d7a and the head:
  - All 32 `d=0.0` plan hashes are identical at all three trees.
  - At `d=0.112`, 0 of 32 hashes move from round 1 to the head, and 26 of 32 move from cf4f6b7a6.
  - The round-1 and head outputs are byte-identical, and `failures 0` at all three.
- Body figures I could not re-derive: its flat `d=0.112` summary (`heat short max 0.1098`, `flat wins 15` at the head; `0.1093`/`16` at the base) does not reproduce on this Linux seat. Here flat `d=0.112` reads `0.0977`/`14` at all three trees, and spread `d=0.112` reads `0.0821` at round 1 and the head against `0.0822` at the base. The relational claims hold: flat between round 1 and the head, a move from the base. The absolute values look like solver floats from the body's macOS run.
- Zero-derate null, the eight round-2 scenarios: I did not rebuild the body's out-of-tree driver. I checked the algebra instead:
  - `heat_per_cop_kw`, `power_for_heat_per_cop_kw` and `added_power_for_heat_per_cop_kw` return their input when `cop_partload_derate` is 0. The feature check asserts this with `is`.
  - So every converted site evaluates its round-1 float expression at d=0: `a + (-b)` is `a - b` exactly, and `(cop*p)*dt` is `(p*cop)*dt` by commutativity.
  - Each round-2 feature check carries its own no-derate null arm, and all pass at the head.
- LP displacement row, the "no-op for every input" claim: verified against `_plan_dhw_min_cost`.
  - At a spare step the refill window holds the step itself, so `refill <= prices[j]` and `premium[j] == 0`. The free `disp` absorbs the row whatever the conversion.
  - At a step with no spare, `headroom <= 1e-6` kW. With a modulation floor that is below the floor, where `heat_per_cop_kw` is the identity.
  - On a floorless band (`min_electrical_power == 0`) the conversion changes the bound by `d*h^2/band`, at most about 1e-12*d/band kW. That is outside the literal "every input" but below HiGHS's tolerance, so it changes no plan.
- Budget payment and raise:
  - `node tools/policy/policy_lint.mjs --budgets` prints `tools/audit/briefs/D2.md 53 53 683 683`. The cap equals the measured value, with no padding.
  - I hunted for a payment in D2.md. Item 1's scalar-versus-batch bit parity is pinned by tests/features.py:6211-6231, but only against `simulate_trajectory`, not `simulate_step`. Item 3's `predicted_cost == Σ price·power·dt` is checked in tests/stress.py:1452, not on golden fixtures. So neither method step is wholly mechanised, and both stay a finder's method.
  - The Traps sentence on `may-drift` fixtures applies CLAUDE.md rule 3 to D2 findings ("no finding") rather than restating it.
  - The new sentence makes no existing item redundant. I found no payment the body missed.
  - The structure payment: the two cut DhwPlanner comment passages were a narrative of the change's own first cut and its measured deficits, and an argument for the run-up's existence. Both were spent history, and both keep their rule. `Architecture score: dS +0.0000 NULL` re-derived (ev/archscore.txt), and CI `arch-score` is green.
- Claims and versions: `tests/env_drift.py --all` reports `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56` (ev/env_drift.txt). VERSION, the manifest, RELEASE_NOTES.md and both claim files are untouched three-dot.
- Merge: `git merge-tree --write-tree origin/main 958b4af8e` exits 0 against origin/main 18b788ac2 and again against fbc731283 (ev/merge_tree_latest.txt), with the ledger driver `LEDGER-MERGE: resolved tests/closures.json` (ev/merge_tree.txt). No claim-file conflict.
- Forward-carry: roster `handoff/audit-r10-roster` 1e9f14dd3 now holds both round-2 findings (carry[4], carry[5]), each with its control stated as a precondition. The body's "the append is owed" is out of date but satisfied.
- Red checks:
  - The body's local reds (entities.py, card.mjs, optimality.py, stress.py) are green in Linux CI at this head: `tests / fast (3.14)`, `tests / closures`, `tests / coverage` and `tests / browser` all succeed.
  - `budget-raise-gate` is answered in the body as the owner-approval mechanism.
  - The ancestor `prelude` red is answered as a transient API timeout.
- Head: the PR head is 958b4af8eee134728986d92d2220f1dfadbab255, which the body's `## Head` names and which I measured.
- CI on this head: `merge_train.py classify 958b4af8eee134728986d92d2220f1dfadbab255` exited 1, `RED ... pending: none red: gate`. The `gate` run's log (job 124408196031) has exactly one line: `FAIL budget-raise-gate / budget-raise-gate: failure (this run)`. That is the owner-approval hold flagged under Findings. Every other required lane concluded green, `tests / mutation` included, since gate.py named nothing else. `pr-contract / pr-contract` (124408053328) is a success and started after the last red concluded. This verdict leaves that gate to its owner: merging waits on tvofi's approving review, or the mandate approval, at this head.
