Fix review: merge 9c18619ad01394d7964ed4df2cc190af6091229e
bus-nonce: e8e4288e0b23a034b7a02dc11d078e45

Round 2. From a fresh detached worktree at 9c18619ad01394d7964ed4df2cc190af6091229e (code head 38c79586 + origin/main 8d7903e6). Live head re-read at posting: 9c18619ad01394d7964ed4df2cc190af6091229e.

## Round-1 blockers, re-measured
- Inherited main red: my round-1 plant re-run (evidence/plant_r2.sh, .out, case A): main carries an unrecorded tests/zz_main_unrecorded_check.py, branch only comments tests/wood_advisor.py.
  RESULT A: no PREDICT line, rc=0 (round 1: NO RECORDING, rc=1). Control C (the branch's own new unrecorded script): NO RECORDING, rc=1 -- the arm still fires on what the branch adds.
- Mutation arm: RESULT D: a planted guard prints 3 ADDED UNPINNED lines and rc=0 (warn). The refusal moved to 7d, which reads the body.
- fixer.md step 2 now: --pin-killed timing is ci-autofix.md's; 6d lists the sites; the body's "## Unpinned sites" gives each a disposition (pinned by mutation-autofix, a value check, or a written triage). That agrees with ci-autofix.md: the fixer waits for mutation-autofix, and nothing forces a local mutation drive before the handoff. No remaining contradiction found. policy_lint TOTAL 0 errors; fixer.md 4865 of 4866 tokens.

## Trying to over-fire 7d (unpinned_line, extracted verbatim from prepr.sh and driven directly)
- E1 every key listed: rc=0. E4 keys in backticks: rc=0.
- E2 "## Unpinned sites (3)" and E3 "## Unpinned Sites": rc=1, with the message "no `## Unpinned sites` section". The exact heading is required, and the message does not say the heading was close. Strict but recoverable in one edit. Not blocking.
- E5 a 1-line shift above the site after the body was written (as a merge from main does): rc=1, naming the three moved keys. Keys are line-pinned triage_key (file:line KIND). That is the existing body-retake rule (fixer.md step 6), not a new burden. Not blocking.
- E6 a substring collision: key away.py:1 is not satisfied by a body naming away.py:12, rc=1. Key away.py:12 CONST IS satisfied by "away.py:12 CONST_X" (grep -F substring). No kind is a prefix of another today (BOOLOP CLAMP_DROP CMP_BOUND CONST GUARD_OFF NULL_COMMENT RAISE_DEL RETURN_DEL), so this is theoretical under-firing, not over-firing.
- 7d is skipped with no body and on --self-test, and owes nothing when no site is listed (self-test arm). This PR adds no production site, so it owes no section.

## One residual over-fire, not blocking -- for the orchestrator to carry
- RESULT B: a branch that only adds a comment to tests/derive_closures.sh, on a main that carries an unrecorded script: PREDICT closures NO RECORDING tests/zz_main_unrecorded_check.py, rc=1. no_recording charges every inherited unrecorded script once the lane file is in the diff ("or lanes_changed"). So the docstring's "a red main already carries is never charged to a branch" is false for that one file.
- It is narrow: it needs main to be red AND the branch to edit the lane file. The repair is one rec line in the file the branch already edits.
- The exact fix is to subtract the merge base's unrecorded set. I do not block round 2 on it. It should go to R9-CI-1's brief, or a follow-up, with this plant as its control.

## Figures
- Replay re-run at this head's code (evidence/replay.tsv, confusion.txt):
  RESULT mutation: 11/11 red predicted, 0/20 green.
  RESULT closures: 12/15 red predicted, 1/16 green flagged (e6e9b775).
  These match the body.
  My run printed "replay failures (API or worktree): 7" because it ran into the shared API rate limit. The row set is 38, as in round 1, but differs by one commit each way: 22eab552c6 is in, d760cbe35e is out. So these figures are partly re-derived. The rows it did read agree with the body's table.
- ci_predict.py at the head: 1.9 s wall, rc=0, "no closures or fast red predicted". It is still git plus AST only; no heavy script runs.
- prepr.sh --self-test: 210 passed, 0 failed (evidence/selftest.out).
- The docstring now names the two arms that are the predictor's own model (import resolver, NO RECORDING regex). The round-1 overstatement is fixed, except the "never" noted above.

## CI at the head (check-runs API, evidence/check_runs_at_head.tsv, all completed)
- Green: closures, mutation, fast (3.14), typing, pr-contract (both runs), policy-docs, instrument-self-tests, env-matrix, hassfest, validate-hacs, CodeQL analyses.
- budget-raise-gate: its cancelled twin 112986567129 was rerun by me at the coordinator's request; it is now success (112987652524), beside 112986576436 success.
- Red only delivery-status and nightly-status: state checks this diff does not reach. The body's Red checks section names both and the cancelled gate.
- mutation is green with nothing drawn: no production line changed.

## Forward-carry
The autofix-chain finding is now roster group R9-CI-1: handoff/r9-ci-1 exists, with proof PRs #2031, #2032 and #2033. Carried. The residual above is a new item for the same place.
