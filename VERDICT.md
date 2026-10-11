Fix review: merge abf7dc7f9b5043b48605aea1fb70769e565711fc
bus-nonce: 37b25c9e1b761558627f53247602911d

Round 2 (round-1 block: instrument-self-tests red, unanswered -- root-cause-unanswered
at 648f22d7a). Measured at detached worktree /Users/timmalmstrom/hpo-seats/r9rev-2132/wt,
head abf7dc7f9b5043b48605aea1fb70769e565711fc; branch head verified equal at publish time.
(The fixer's first merge dd561d218 was never pushed; abf7dc7f9 re-merges the same fix onto the
same tree -- git diff dd561d218..abf7dc7f9 is empty -- and every measurement below was re-run
at abf7dc7f9 itself: self-test 219/0, STRUCTURE RATCHET PASSED.)

- RESULT the block is repaired, not answered away: ba7455ea5 registers tests/ci_budgets.json
  as the gate's seventh schema -- recorded_at/reason FREE (the consumer's own METADATA_KEYS),
  every metric leaf MAX (archscore.*, script_runs_per_push, script_runs_full_case_pr,
  critical_path_minutes), unknown keys FROZEN (the consumer's own "not a metric this ratchet
  knows" refusal). Self-test at the head: 219 checks, 0 failed (was 211/2). An upward move of
  any metric is an owner-seen raise; the initial-record leaves remain raises the owner approves
  (budget-raise-gate red at the head, disclosed, the owner's -- unchanged from round 1).
- RESULT mutants killed (mine, restore verified, tree clean): schema entry deleted -> 3 fails
  (both round-1 FAILs return, plus the tightened-routine arm); script_runs_per_push MAX->FREE
  -> 'ci: a script-run count up is a raise' fails. STRUCTURE RATCHET PASSED at the head.
- RESULT the delta is exactly the repair: authored content 648f22d7a..dd561d218 touches only
  tools/policy/budget_raise_gate.py (+36); everything else in the range is origin/main's own
  merge content (#2117). tests/closure.py, tests/ci_ratchet.py, .github/workflows/tests.yml
  and the coverage machinery are byte-identical to the head my round-1 measurements took, so
  those measurements stand: C2 every consume-doubt re-records (other-tree/corrupt/missing/
  absent all rc=1, full check still runs on consumed recordings); C1 mechanism verified
  locally (layout.py composed-vs-bare read sets identical, my instrument, macOS,
  non-authoritative) with the Linux composed-proof still owing a green run on this PR;
  ratchet one-way, runner-derived inputs, --record never in a job, mutants kill their pins;
  all 17 archscore rows + 53/53/61.0 re-derived; no existing *_budgets.json raised.
- check-runs at abf7dc7f9 at publish time (commit check-runs API): instrument-self-tests
  completed success -- the round-1 block is repaired in CI, not only locally; budget-raise-gate
  failure x2 as disclosed (the owner-gated initial record); heavy lanes still in progress are
  the merge's own required contexts, not answered here.

Round 9, review round 2.
