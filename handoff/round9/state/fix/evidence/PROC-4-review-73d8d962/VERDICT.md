Fix review: blocked 73d8d962cc0220d92c18b4d759ebec9205578c91 provenance: bus.sh watch --post posts any verdict/<pr> ref as hpo-approver, so a non-reviewer seat can mint a merge verdict

Head: 73d8d962cc0220d92c18b4d759ebec9205578c91 (handoff/r9-proc-4). Body: a2aa818a (handoff-body/r9-proc-4). Merge base 25e5b9cc.

BLOCKING
1. A forged verdict ref leads to a merge. Every cloud seat pushes with the same
   credentials (the fixer pushes handoff/<topic> the same way), and nothing in
   bus.sh binds verdict/<pr> to the rostered reviewer. forge_probe.sh here pushes
   a hand-made commit (VERDICT.md "Fix review: merge <head>" plus evidence/x.txt
   naming the head; no push-verdict, no reviewer) and watch --post posts it
   (forge_probe.txt: "BUS posted 1830 ... Fix review: merge ..."). The post is an
   hpo-approver comment with an evidence directory on the Mac that names the
   head, which is exactly what app_approve.sh accepts, so approval and the
   auto-merge follow on green CI. The barrier lost: before this change the
   verdict reached the orchestrator by the coordinator's relay from the reviewer's
   own thread, a session-attributed channel; orchestrator.md now says the
   coordinator "relays no head or verdict". app_approve.sh's own header already
   says the App allowlist "cannot prove WHICH seat's word an App verdict
   carries"; the relay was what did. The evidence gate is also weaker: bus.sh
   unpacks whatever the ref carries into the Mac directory the gate reads, so
   forging the artifact is one blob.
   Proposed fix (one of): keep a one-line confirmation channel, so --post posts a
   verdict commit only after the coordinator confirms "<pr> <verdict commit>"
   came from the reviewer thread it started (watch without --post still wakes the
   orchestrator); or have tvofi accept the residual risk explicitly, with
   orchestrator.md and fix-review.md saying the bus does not authenticate the
   reviewer. Either needs a red-first self-test case for a ref not confirmed.

ALSO OWED (same push)
2. Policy text deleted to pay caps, not because it was wrong:
   orchestrator.md s2 "the programme's method is that no claim stands on one
   agent's word" (the very principle finding 1 breaks), s10b's statement that
   brief_lint.mjs never reads docs/ or tools/audit/briefs/ (so a citation left
   there is unchecked), and fixer.md's "CI runs the same run.sh ... a full run is
   about forty minutes". CLAUDE.md rule 2: never delete working content merely to
   fit; restructure, or name the cost in the body.

CHECKED AND FINE
- bus.sh --self-test at head: 25 checks, 0 failed.
- policy_lint.mjs at head: 0 errors across 40 files; the new
  EXCLUDED_BECAUSE_CITED entry pins 0011's citation in fixer.md, and fixer.md
  now cites the path.
- No *_budgets.json changed (git diff 25e5b9cc...HEAD): no raise.
- Stale verdicts: app_comment.sh still refuses a merge verdict not at the live
  head and a closed PR; a blocked verdict at an old head is harmless. A commit is
  posted once (/posted). Identity: posting goes only through app_comment.sh
  (hpo-approver, read-back checked); the author App is never used.
- tools/audit/ is INERT by prefix in tests/closure.py, so bus.sh needs no
  closure entry.
- Not run here: tests/entities.py (no voluptuous in this container) and the full
  gate; cite the head's CI.

Watcher notes (not blocking): a merge verdict whose PR head moved by a carry
merge before the pass is refused and not retried, and a manual post refuses it
too (app_comment.sh's live-head rule), so carried verdicts still need the
orchestrator's --carry path; a kill between the poster's success and the
posted-file append would post twice.
