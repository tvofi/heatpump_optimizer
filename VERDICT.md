Fix review: merge 8fd2d73a28f4032d593de1f5bc32f198062317f3

bus-nonce: c92860aa74b045c22d74087cef06302b

Round 1. Head measured: 8fd2d73a28f4032d593de1f5bc32f198062317f3 (live PR head re-read: same). Diff against origin/main 1148ee635 is two added files, a triage note and this PR's delivery row; no production code, VERSION, manifest or notes heading touched.

## Findings

None. This PR leaves nothing open: no defect, deferral or follow-up that it does not itself settle.

## Evidence

- RESULT carry re-run (ev/rc.txt, ev/carry-*.out), run with the 40-hex SHAs from refusing pairs, `app_approve.sh --carry <verdict> <merge> 1148ee635`:
  #2975 f6ff3e56->2c162670: main 1148ee635 rc=1 (resolves tests/golden/claimed_drift.txt to something other than the union of its parents), #2977 head 967abc3e rc=0 (CARRY: yes).
  #2955 eab999bc->502b0df3: rc=1 / rc=0, same text.
  #2976 1381df1f->ebbdcaa6: rc=1 / rc=0, same text.
  This matches the body and the note at both ends, and the null control (origin/main's script refuses) is the main-side run.
- 967abc3e has parents 9f0e4478 and 1148ee635, so it is the clean main merge of the verdicted head, as the note says.
- Mutation proof (ev/mutation-accept.txt, ev/mutation-reject.txt): on the committed file ruling_verdict(P297) = ACCEPT and triage_refusal on the citation returns None; with the Verdict line changed to REJECT it returns "... is not an ACCEPT ruling (REJECT)". Not vacuous.
- Carry destinations: the PR holds no finding needing a Carry; carry_audit at the head reads 0 finding items, 0 unrouted, 0 bad destinations. Body "Forward-carry: none" is consistent with the note, which adds no new group or roster op.
- Body describes this head: states head 8fd2d73a (authored code head 8a908a97, one row-only commit on top; confirmed, the only file differing is dev/programme/delivery/2982.md). figure_lint: 1 resolved, 0 not verified.
- Merge: git merge-tree --write-tree origin/main head exits 0, no conflicts (ev/mergetree.txt); origin/main is still 1148ee635.
- CI on this head (check-runs API, read after the packet): no red run. Green: arch-score, budget-raise-gate, codeql x3, delivery-status, policy-docs, wave-script, hassfest, validate-hacs, mutation, nightly-status, briefs, closure-scope, arch-instrument, typing. Still in_progress at my read: env-matrix, instrument-self-tests, prelude, browser, closures, coverage, fast (3.14). This merge verdict holds only if none of those ends red; a red one reopens it. No pr-contract run was listed yet at this read.
- Not re-derived: the train.log counts (9 claimed_drift SKIP/ADD REFUSED lines, #2917 six times, line numbers 1984/2582/2799/2885) and the "beat: waiting CI at 967abc3e" line. merge_train/train.log is on the orchestrator's machine and is not in this checkout, so these figures are unverified by me. They do not change the ruling: the three re-run instances reproduce.
- Not re-derived: #2977's reviewDecision/mergeStateStatus (live PR state; I checked only the commit topology of 967abc3e).
- Class scope: this is a ruling note, not a fix; the enumeration rule of step 6 does not apply. The note's own claim, that #2977 is the barrier for all four instances, is reproduced for three; #2917's instance is not re-run here.
