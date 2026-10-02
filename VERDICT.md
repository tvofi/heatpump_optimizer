Fix review: blocked 291b3e0fad611c73d07952ddd2b1c2399ebc8781 root-cause-unanswered: fast (3.14) went red on tests/harness_headers.py (round4/D6 claims.py prints 68 modules, header says 67), unanswered; closures-autofix refused (skip-failed-recording), so the bot commit the body waits for will never come

bus-nonce: f8aec55ba49b309d37ef2c2d9f82352d
Round: 1. Reviewer: R9-EG-B5 fix reviewer, from a detached worktree at the head. The head was re-read at posting: 291b3e0fad611c73d07952ddd2b1c2399ebc8781. Merge base: 5f87e25a1. origin/main: 8fa06663c.

The move itself holds. Everything below except CI was measured at this head.

RESULT provenance BASE=948671af1 rc=0 "PROVENANCE PASSED: 27 units, 0 problem(s)" residual=+29/-31 control=27/27
RESULT provenance BASE=5f87e25a1 (merge base) rc=0 PASSED 27 units
RESULT provenance BASE=8fa06663c (origin/main now) rc=0 PASSED 27 units
RESULT silent-revert: git log 4e2582e79..origin/main -- custom_components tests/features.py tests/guard_pins.py tests/mutation_ledger = 0 commits; provenance against current main passes, so no fix that landed in the moved block was reverted
RESULT merge-tree origin/main HEAD rc=0 (no conflict)
RESULT my own perturbations of provenance.py, each a temporary commit on the head:
  A mid-method constant in _plan_dhw_min_cost (1e-6 -> 2e-6): FAILED rc=1 (caught)
  B one blank line deleted inside _plan_dhw_min_cost: FAILED rc=1 (caught)
  D an extra DhwPlanner method: FAILED rc=1 (caught)
  E the build returns (plan, None) instead of (plan, requirement): FAILED rc=1 (caught)
  F a comment line inserted above _pin_is_free: FAILED rc=1 (caught)
  C a behaviour change OUTSIDE the moved units (_co_optimize headroom = p_max - 0.9*dhw_power): PASSED rc=0. Only the residual count moved, from +29/-31 to +30/-32. The tool prints the residual for a human and does not gate on it, by design. I read the full residual by eye: it is imports, the docstring, the construction in optimize, the six planner calls, the two `, self._dhw_requirement =` unpacks and the _dhw_legionella_step removals. Nothing else.
RESULT substitutions: _build_dhw_requirements has one return statement at base (one `return`, no raise or yield in the 352 lines). The stash was the statement just before `return DhwPlan(...)`. DhwPlan is a dataclass with no __post_init__. Both callers assign `self._dhw_requirement` from the returned tuple. So the requirement is written at the same point, on every path, last build wins. That includes the replan whose result is then rejected, as at base. _dhw_legionella_step had 3 writes and 0 reads in production at base. The 3 substitutions preserve behaviour.
RESULT planner inputs: DhwPlanner reads only self.model, self.config (1 field), self._pv_surplus and self._price_known. Its methods reference no `self.` name outside its own methods and those 4 attributes. On the optimizer, `_pv_surplus` and `_price_known` are assigned only in __init__ and _stash_price_horizon. `model` and `config` are assigned only in __init__. The planner is built once, on the line after the single _stash_price_horizon call in optimize. So no input can go stale between construction and use.
RESULT ledger: ledger_check.py at merge base 5f87e25a1: form/layout [] completeness [] sites 4520, unpinned 3909 here and 3909 at base, added unpinned 0, refusal None. Null control without the #1748 pairing: 147. My perturbation added a guard plus a return in dhw_planner: added unpinned 2, refusal 1. So the pairing tells a moved site from a new one. Ten renames changed the anchor line only, with digests unchanged. No ledger row under optimizer.py names a moved symbol. mutation_table.py is untouched by this PR, so the pairing is main's own mechanism. The carry is legitimate.
RESULT config Protocol deviation: ACCEPTED. The cap_exception's verbatim condition outranks the design note's wording. Passing the float would rewrite the moved line `self.config.pv_export_price`. The Protocol has one field, and the planner reads one field (1 attribute access). typing_ruler runs mypy --strict over the whole package, so a second field read would be refused statically. typing is green at this head.
RESULT #1747 carry: features.py spies on DhwPlanner._build_dhw_requirements, the callable both builds use, and keeps the reach clause (len >= 2 and all blocked). The re-measured 9.22 kWh / reach figures are the fixer's; I did not re-run census_reach_planner.py (numeric, no numpy locally).
RESULT CI at 291b3e0 (check-runs API): 33 runs. Not green: closures, closures-autofix, fast (3.14), pr-contract. mutation success ("MUTATION TABLE PASSED"; the moved helpers are killed by features.py and manual_plan.py). typing success. env_drift --all ran in the fast lane and is not among its failed scripts.

Why blocked:
1. fast (3.14) reports "2 TEST SCRIPT(S) FAILED": entities.py (3 of 2062, the closure-table reds the body names) and harness_headers.py (3 of 94), which the body does not name:
   FAIL tools/audit/round4/D6/claims.py RESULT arch_modules_on_disk matches header [header='67' printed='68']
   FAIL tools/audit/round4/D6/claims.py RESULT arch_map_listed matches header [header='67' printed='68']
   FAIL the executed harnesses leave their committed output byte-identical [M tools/audit/round4/D6/claims.json; M tools/audit/round4/D6/claims.md]
   This red comes from the new module, and no autofix covers it. pr-contract independently refuses for the same reason: "check `fast (3.14)` is red and `## Red checks` does not name it".
2. The body's plan for closures does not hold. closures-autofix printed "AUTOFIX: skip-failed-recording -- THE REPAIR DID NOT HAPPEN. No commit will be pushed". The recordings' rc fields show entities.py=1, harness_headers.py=1 and stress.py=1. entities.py is red only because closures.json lacks dhw_planner.py, and the bot will not re-record while entities.py's recording is red. Waiting is a deadlock. By ci-autofix.md, the rule against re-recording UNDER-SCOPED yourself no longer applies once the bot has reported it did not. stress.py rc=1 under recording is unexplained here: it passed in fast. Find out whether main's FULL recording shows the same.
Owed: fix the D6 harness header and committed output (or classify that harness's count) for the 68th module; re-record closures for dhw_planner.py by hand under gate-scoping.md (Linux recordings only, never a full derive_closures.sh off Linux); and name the harness_headers red in `## Red checks` with its cheaper detector or the finding that none exists. Those commits are a re-review. Findings 1-5 above should carry if the production diff (custom_components/) is unchanged.

Not run locally (no numpy): features.py, golden_hashes.py, census_reach_planner.py, env_drift. Those rest on CI and on the fixer's figures.
Evidence: ~/hpo-seats/1858-review/evidence (provenance outputs at three bases, the six perturbation outputs, ledger.txt, the CI logs for fast/closures/closures-autofix, recording_rcs.txt, HEAD.txt).
