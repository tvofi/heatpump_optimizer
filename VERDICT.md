Fix review: merge 0a6dff9438c3fccebf20efdd2224d9ced0afa841

bus-nonce: ae629214c422ab4022142464b87ae34c

Round 1. Measured head 0a6dff9438c3fccebf20efdd2224d9ced0afa841 (code head 01ee39a07; the second commit adds only dev/programme/delivery/2652.md). Roles file unchanged on main since merge base.

RESULT mutant_delivery_row=red (trailer restored in commit_row: "6 checks, 1 failed", FAIL on the attribution row); clean 6/0
RESULT mutant_stamp_message=red (trailer restored in stamp_message: FAIL + stamp_self_test=fail); clean stamp_self_test=pass
RESULT producer_sweep: git grep over tools/ .github/ .claude/ leaves 18 hits, none a producer (ref_privacy/policy_lint/agreement_py patterns+fixtures, cloud_dispatch FOOTER_BAN, carry_audit reader/fixture/regex, stamp.py's own split-string fixture); .github/ and .claude/ no hit (ev/sweep.txt)
RESULT commits_footer_free: ref_privacy.attribution finds [] in both commits; the only grep hit is a mid-line mention in the subject (prose)
RESULT merge_tree: exit 0, tree ab5ce76a1, no conflicts, no MERGE-CLAIM lines
RESULT scope: MODE: SCOPED -- 2 script(s) run, 31 scoped out (tests/doc_claims.py, tests/entities.py)

Both self-tests import ref_privacy.attribution (delivery_row via python3 -I sys.path import, stamp via import); no copied regex. The stamp row also pins that main() calls stamp_message and that the reader flags a banned fixture (null control). The delivery row reads a real commit made by commit_row.

Red-check answer (item 11): CI read in one bulk check-runs read at this head: no red conclusion; success/skipped/neutral only. Still in_progress at read time: policy-docs, instrument-self-tests, env-matrix, browser, coverage, fast (3.14), closures, Analyze (python). pr-contract and nightly-status are green. The body's ## Red checks section names the red (app_push ref_privacy refusals on #2651), a cause, a process state (cheaper detector existed: producer sweep) and a built countermeasure plus a recorded refusal of a census. Answered.

Figures re-derived: self-test counts, MODE line, sweep rule. Version files untouched. Forward-carry: none stated and none owed (no later stage changed). No class-open seam: the sweep returns no other producer. Caveat: the in-progress jobs were not waiting-on; a red among them is the orchestrator's to read before merging.
