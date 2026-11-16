Fix review: merge c57638046f9d2477d761e8da56327369f8a9a4fe

bus-nonce: ae2a57ac8e8c34200b6107c7f030fc0e

## Findings

- Follow-up: there is still no committed finder's harness (fix-review.md step 9). #3636 is an outside report, the body says so, and the reporter's repro is encoded as the committed #3636 card checks. Unchanged since round 1. Carry: dismissed: outside report with no finder harness; disclosed in the body and encoded as committed card checks

## Evidence

- Round: second review round of this PR. Review scope `delta` over the reviewed head 87a315a355faa219065ed906ed3adbd4d589aacd. The delta (`git diff 87a315a3… c5763804…`) touches only `tests/card.mjs` (+25 -3). No production delta, so the scope is not widened.
- Head reviewed: c57638046f9d2477d761e8da56327369f8a9a4fe (ev/HEAD.txt). It is a merge of 87a315a3 and 1dba0f90a234562412e127e1aa53c1476b2ba49f, and its tree is identical to 1dba0f90 (`git diff --stat 1dba0f90 c5763804` is empty). So the body's measurements at 1dba0f90 apply to this head. The body names c5763804 as head.
- Merge with main: `git merge-tree --write-tree origin/main c5763804…` exit 0 (ev/merge-tree.txt). No conflict.
- Role contract: rendered from main via `role_pack.py render fix-review`.
- Prior block (M5, ceiling from `editCeiling()`): resolved. RESULT M5 at the head (ev/mutant-M5.diff): `1 CARD CHECK(S) FAILED`, `FAIL a zoomed-in view does not change the applied runs (#3636)`, detail `{"editCeiling":-3,"dhw":[[-4,-3]]}` (ev/card-M5.txt). This matches the body. The new check also asserts `editCeiling() <= at(-3)`, so the zoom it stages provably takes effect and the check is not vacuous.
- Prior residual (M8, skew = 2 steps): resolved. RESULT M8 at the head (ev/mutant-M8.diff): `1 CARD CHECK(S) FAILED`, `FAIL a run starting two steps before the window is sent (#3636)`, detail `[[-4,-3]]` (ev/card-M8.txt). This matches the body. Runs start on step boundaries, so a non-integer widening between 1 and 2 steps acts the same as one step on step-aligned starts.
- RESULT unmutated at the head: `ALL CARD CHECKS PASSED`, all eight #3636 checks `ok`. Run with HPO_PLANDATA from `PYTHONPATH=tests/hastub python3 tests/plan_view.py` at the head (ev/card-head.txt, ev/plan_view.txt).
- M1/M2, the null control and failing-test-first: the card JS is unchanged since round 1, where they were verified. The delta does not touch them, and they carry.
- Figures re-derived at the head (merge base e30408f7881cd5602a2c4d7ea9517b0d765652f6): `MODE: SCOPED -- 9 script(s) run, 24 scoped out.` (ev/closure-select.txt), `STRUCTURE RATCHET PASSED` (ev/structure.txt), `Architecture score: dS +0.0000 NULL` (ev/archscore.txt). All match the body. The other per-script counts in the body were not re-derived in this round. They rest on CI's scoped gate at this head.
- VERSION, the manifest version, the RELEASE_NOTES heading and the claim files: untouched by the delta.
- CI: `merge_train.py classify c5763804… --pr 3649` printed WAIT (pending: gate) from 02:13 UTC and exited 0 at 02:41:06 UTC: `GREEN c57638046f9d2477d761e8da56327369f8a9a4fe pending: none red: none` (ev/classify-rc.txt, ev/classify.txt). The review packet refused at render with `introduced-red` on `governance / instrument-self-tests`, which was still in progress then. The GREEN classify supersedes that refusal.
- Red checks: none. Classify reads `red: none` at the head, so no `## Red checks` answer is owed.
- Forward-carry: the body states none. A test-only delta changes no later stage.
- Self-audit: `carry_audit.py check` on this verdict exits 0 with `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`. The body file passed to it was an excerpt of the live body's carry headings (Closes, Red checks, Forward-carry, Friction). The packet's own carry_audit on the full body at this head read 0 finding items.
- Head re-read before return: `git ls-remote` shows the branch at c57638046f9d2477d761e8da56327369f8a9a4fe, and the PR API reports the same head.
