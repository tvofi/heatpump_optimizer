Fix review: blocked cfa9fb9aa6846b8707df45808a9c266f042d8e4d root-cause-unanswered: pr-contract red at this head -- "check `closures` is red and `## Red checks` does not name it" (run 2026-10-10T18:36:46Z, the only pr-contract run at this head); the body's ## Red checks names typing, mutation and pr-contract but not closures

bus-nonce: d9749e58083eb114c3f17102ad56afdf

Round: 2, second publication (first was `blocked beb97ea69 ... head-moved`,
review/2118 1386da31). The head then moved by exactly the record-only re-record
this verdict called for, and the dispatcher asked for `merge cfa9fb9aa`. That
verdict was not published, and the reason is the head's own check-runs, not a
preference: **pr-contract is red at cfa9fb9aa right now**, refusing that
`## Red checks` does not name `closures`. Publishing merge as hpo-approver over a
red required check at the head being merged is what rounds 1 and 2 of this very
review refused.

## What the dispatcher's two additions verified (both one line)

- `git show cfa9fb9aa --stat`: authored by github-actions[bot] 2026-10-10T18:36:27Z,
  "ci: re-record closures", touches ONLY `tests/closures.json`, +1 line. No
  production code, no new review surface: `git diff bc0488018..cfa9fb9aa --
  custom_components/` is still exactly one file, coordinator.py, the one
  annotation line round 1's delta found. Typing ruler, arch-score gate
  (coord_footprint 2586->2591, PASS), the bot's pins (830/872 pinned, mutation
  lane MUTATION TABLE PASSED, 0 survivors) all stand unchanged at this head; the
  re-record touches none of what they read.
- The closures red WAS main's pre-#2125 state and is resolved on main: main tip
  6be88834e is #2125 ("fix(closures): list the round-9 pre-study refit in
  harness_headers.py's inert_reads", fdb05e622) merged, carrying the same
  one-line repair as this head's autofix re-record. main's closures lane is
  re-running green-expected at 6be88834e.

## Why the red persists despite that, and the one edit that clears it

The pr-contract body check reads red-history over the range origin/main...head:
at beb97ea69 the `closures` failure conclusion is INSIDE that range (merge-base
is still 969c3a5c8), so it stays a red this body must name no matter that both
ends have since been repaired — the same rule that made the body name `mutation`
(round-1 item 7) after the bot had already pinned it. The body has not been
edited: `## Red checks` still names typing, mutation and pr-contract, and no
closures entry exists (re-checked 19:03Z).

**The answer the body needs already exists and is one paragraph:** closures went
red at beb97ea69 for `INERT READS UNDER-APPROXIMATED:
tests/harness_headers.py: dev/audit/rounds/round9/prestudy/boost_drift_refit.py`;
it was not this branch's (identical failure at main tip 969c3a5c8, 17:22Z;
closures-autofix printed "changed -- nothing owed to a human"); the cheaper
detector is the closures lane's own inert-reads comparison, whose standing cost
is a full-scope re-record; repaired on this branch by the accepted autofix
commit cfa9fb9aa and on main by #2125. Name `closures` under `## Red checks`
with that, pr-contract re-runs green, and the next review of this head is a
merge on the numbers that already stand above.

## Evidence

/Users/timmalmstrom/hpo-seats/r9rev-2118b/evidence/ — head.txt (naming
cfa9fb9aa), pr-contract-fail-reasons.txt and pr-contract-1843-log.txt (the
beb97ea69 refusal), closures-lane-log.txt, check-runs-head-final.txt,
typing-ruler-mypy.txt, archscore-gate.txt, mutation-list-returndel.txt,
mutation-lane-log-full.txt, ci-predict.txt, pr-body.md. Worktree:
/Users/timmalmstrom/hpo-seats/r9rev-2118b/wt.
