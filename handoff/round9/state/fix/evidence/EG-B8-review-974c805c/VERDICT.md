# R9-EG-B8 review, PR #1786, round 1

merge 974c805cb8fd9323685d5f16f2931cfd99777d37

Measured at head 974c805c (live head re-read before posting), merge base 754d2319 (origin/main, v6.7.12).
Linux cloud box, CPython 3.14.7, pinned tests/requirements-ci.txt, OPENBLAS_CORETYPE=Haswell, 1 thread,
HPO_TYPING_PYTHON on the pinned typing venv (mypy 2.3.1, homeassistant-stubs 2026.9.3).

## RESULT lines
- Finder's probe b8_replan_blocked.py (sha1 e29cc879, from handoff/audit-r9-alt), wood_coil blocked:
  - base 754d2319 as-is: delta -2.0 shipped_dhw_kwh=9.22 breach 0.629; delta -3.0 shipped 8.63 breach 0.04; calls [True, '<omitted>']
  - head 974c805c as-is: shipped 0.00 at every delta in {0,-1,-2,-3}, breach 20.927/20.876/20.81/20.81, calls [True, True]; identical to the control arm at both ends.
- Reviewer's own class sweep b8_class_sweep.py (mine, not the finder's): all 50 golden scenarios, DHW blocked, prices -2 and -3:
  RESULT base runs=100 shipped_while_blocked=2 (both wood_coil); head runs=100 shipped_while_blocked=0.
- Fixer's idempotence fuzz idem_fuzz.py (sha1 37db122a, the fixer's instrument): base restart_moved=19475 of 20002; head restart_moved=0.
- Scoped gate at head: MODE: SCOPED -- 22 script(s) run, 5 scoped out; 24 TEST SCRIPT(S) PASSED; ALL 3601 FEATURE CHECKS PASSED;
  STRUCTURE RATCHET PASSED; ALL 9 typing-ruler checks PASSED (pinned mypy); claims hygiene 754d2319 ok;
  NO UNCLAIMED DRIFT: 56 scenario(s) checked against 754d2319, five CLAIMED coord_* at 48 leaves each. RC=0.
- mutation_table.py --scope changed --base origin/main --max 10: 3577 unpinned of 4083, 3578 at base; 0 survivor(s) of 3; null control survived; MUTATION TABLE PASSED rc 0.
- prepr.sh at head with the PR's live body: PRE-PR 974c805c, rc 0.
- Own mutants (features.py): M9 replan blocked=True (unconditional) KILLED (6+ checks: coil/DHW planner checks);
  M11 drop the len==24 test KILLED ("a stored profile is normalised to average one, or refused whole");
  M10 identity-branch tolerance 1e-12 -> 1e-3 SURVIVED. Effect bounded at 0.1% of daily volume and idempotence still holds; non-blocking, noted for hardening.

## Checks
- Ancestry: no commit in 754d2319..974c805c touches handoff/; the diff carries no handoff/ path.
- VERSION, manifest version, RELEASE_NOTES heading untouched.
- Body ## Head names 974c805c, the head measured.
- Claim-file merge: the claimnotes driver refuses the merge of 1b43198e into 754d2319 (both sides rewrote the list: main emptied it, the branch claims five), so a hand resolution was owed. The resolution is correct: claims-for 6.7.12 = VERSION, the five coord_* claims are this diff's own and each moved (48 leaves), F2.4's inherited claims are gone, hygiene ok.
  Nit, non-blocking: the reason line above the list was resolved to the branch's stale "v6.7.11: round-9 F1.5/F1.6 ..." text instead of main's "v6.7.12: round 9: solve-lifecycle, solver F2.4, family renames". No check reads it and stamp.py rewrites that block, so it self-heals at the next stamp.
- Red checks: the body names INHERITED CLAIMS and the features.py non-finite red at e6d7b737 and answers both. CI at 974c805c: no red run at the time of reading (typing, briefs, pr-contract, policy-docs, delivery-status green; fast/mutation/closures still running).
- Forward carry: .claude/workflows/carry-1743.json present in the diff with control and precondition.

## #1747 root cause (merge seat ask 2)
Not a merge blocker: trigger 1 (reached v5.3.0) is enforced by no verdict (defect-root-cause.md, Enforcement). The fixer was right not to post it; root-cause.md puts it in its own seat and the roster brief contradicts that. Dispatch a separate RCA seat (opus) to write the Root cause section on #1747. Two points it must re-examine in the draft:
1. Class frequency: #1747 is an instance of audit class P2 (tools/audit/bugclasses.json: a mode predicate applied at one seam, missing at its sibling; 66 instances, 27 in round 9, status open, barrier owned by R9-F1.11). The draft's P(recurrence) of 1 instance measures a narrower "defaulted keyword" class. As a P2 instance it owes the class barrier, which the RCA seat routes to R9-F1.11 (finding-propagation.md), offering kwarg_seams.py as a candidate detector, rather than building a standalone check.
2. Process state: the v5.3.0 blocked-path checks existed and passed but their fixture never reached the replan, which reads as (c) rather than (a). The seat decides with evidence.
