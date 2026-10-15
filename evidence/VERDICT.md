Fix review: merge 860afdbcb5e9578460022fa95585e760e1403ff7
bus-nonce: 6bfdded3947a7523cb89bd4cda4c43f8
reviewer: r10-d15-reviewer, round 2. This re-reviews the head after my merge verdict at 4666a7dd8.

RESULT delta against 4666a7dd8 (three-dot over the branch's own content): two things changed and nothing else. D15.md drops the moratorium-override sentence and the fix-phase lead (71560c02b), and the D15 caps drop from 39 to 37 lines and from 728 to 690 tokens. audit-find.js, scopes.json, rotation.json and finding.schema.json are unchanged. The grader files have left the diff now that #2214 is merged.
RESULT check_scopes --ref HEAD rc=0 and --self-test rc=0. check-wave-script: 180 passed, 0 failed. CI wave-script is green (116192949667).
RESULT policy_lint rc=0. --budgets: D15 37/37 lines and 690/690 tokens; corpus 61082 against cap 61026 plus a band of 500. rules_sync, brief_lint, structure and layout all pass.
RESULT the 133 is honest. Corpus at the base edf9d3292 is 60377; at the head it is 61082. The ceiling without the raise is 60449 + 500 = 60949, and 61082 - 60949 = 133. The payment is real: 38 tokens of prose that did no work for a finder.
RESULT the justification parses under main's gate (identical at the head): justification(body) returns True. archscore --diff edf9d3292 HEAD prints "Architecture score: dS +0.0000 NULL", which matches the body. The diff changes no Python that the score reads.
RESULT budget-raise-gate is red by design: RAISE corpus_tokens 60449->61026 and files_tokens D15 None->690. It merges only on an approval at this head under the rules of mandate 6175172275. nightly-status is main's (#2205). pr-contract is green.

Non-blocking:
- The fix-phase lead (each cycle row should record its version) is a feature suggestion, not a measured finding that constrains a later stage. finding-propagation does not bind it. The body points it at the R10-DIAG-REPLAY brief, which is not yet written.
- Carried from round 1: the surviving mutant in #2214's grader (BUNDLE_DIMS = new Set([]) gives 180/0), and M1 setting no gap threshold for a restart.
