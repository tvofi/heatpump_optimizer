Fix review: blocked e773c070bf21dfd011aaef1b016f78d461c4ea09 replay: a confirmed verdict's tree and signed message re-committed on verdict/<pr> by a keyless seat post again and supersede a later verdict

Head e773c070 (handoff/r9-proc-4), body on handoff-body/r9-proc-4, merge base 25e5b9cc. Round 1's blocking finding was provenance (73d8d962).

ROUND-1 PROVENANCE: CLOSED FOR AUTHORSHIP
A keyless seat can no longer mint a verdict. A raw verdict/<pr> ref is "BUS unsigned". A review/<pr> proposal posts nothing until the orchestrator runs `confirm`, which reads the dispatch record and the reviewer's own thread and signs "hpo-bus verdict <pr> <tree>" with hpo-approver's key on the Mac. The self-test passes 41 of 41, including undispatched, foreign key, cross-PR replay and tamper.

BLOCKING: SAME-PR REPLAY (replay_probe.sh, replay_probe.txt)
The signature binds the PR and the tree. It does not bind which round a verdict belongs to, and posting dedupes on the commit SHA ($S/posted), not on what was signed. A seat holding only the shared push credential copies an earlier confirmed commit's tree and message onto a new commit on verdict/<pr>. `watch --post` verifies it and posts it.
The probe: round 1 confirmed "merge H", round 2 confirmed "blocked H" at the same head (a retraction), then the replay posted "merge H" again. app_approve.sh acts on the newest approver comment, so the retracted merge approves and the merge follows on green CI. A merge at a head other than the live one stays refused by app_comment.sh, so the exposure is a verdict superseded at the same head.
Fix, small, with a red-first self-test case: record what was signed, the tree or the signature, per PR at confirm/post, and refuse a second post of it. Or sign the review commit and the verdict parent too, and post only a tip whose signed parent is the last posted tip.

THE OMITTED RULESET (the deviation you asked me to judge)
Signature-only provenance is sound for authorship. With the dedupe above, it is also sound without a ruleset limiting verdict/* to the App. The ruleset would have been the thing that stopped this replay, so leaving it out is only acceptable once the dedupe lands. Without any rule, deleting or force-pushing verdict/* only loses or hides history. That is a denial of service, not a merge: post only ever posts a signed tip, and the record of what was posted lives on the Mac. The optional no-delete/no-force-push rule is worth adding but not required.

RESTORED PASSAGES: YES
- orchestrator.md s2 "no claim stands on one agent's word"
- s10b's note that brief_lint.mjs reads the roster and never the briefs
- fixer.md's "CI runs the same run.sh ... about forty minutes"
All three are back. orchestrator.md's only change from main is now the identity line.
Still cut, not blocking: fixer.md's "a list here would be a carried number, which this file already refuses". Restore it in the same push or name it in the body.

CODE-OWNED PRs: STILL tvofi'S REVIEW
bus.sh posts only through app_comment.sh and approves nothing. app_approve.sh still refuses any PR touching an owned CODEOWNERS pattern. orchestrator.md and fix-review.md both say code-owned paths still need tvofi.

OTHER CHECKS
- policy_lint: 0 errors across 40 files.
- No *_budgets.json changed (no raise).
- The double-post on a kill is fixed (record before post, withdrawn on refusal).
- Not run here: entities.py (no voluptuous) and the full gate. Cite the head's CI.
