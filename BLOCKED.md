# BLOCKED: r11-seam-two-zone-slab (PR #3879 repair, round 2)

Question: carry-3881.json routes the R9-F2.1 P3 finding as the review asked, but prepr's carry step refuses it. Will the relay fold dev/programme/carries/carry-3881.json onto handoff/audit-r11-roster, or rule another destination, so that prepr reads clean and this seat can hand off?

## State

Code head 34cefdc55bdad2131361a3bf0b4043af86874a2f is the parent of this commit, and production is unchanged since 0d345358c4. All four `tests / mutation` sites are pinned. M9 is killed at 34cefdc55b and survives at 0d345358c4. doc_claims, entities and structure pass. The body is drafted.

`PREPR_SKIP_CLOSURES=1 tools/pr/prepr.sh <body>` passes every step but one:

    REFUSE   carry                  BAD-DEST body item 8b887fdc: #3881: #3881 has no owner: no live roster group lists it and there is no dev/programme/carries/carry-3881.json -- CARRY-AUDIT: 4 finding item(s): 3 routed, 0 unrouted, 1 bad destination(s), at origin/handoff/audit-r11-roster f19b546a3c

## Cause

prepr's carry step (`carry_line`, tools/pr/prepr.sh) runs `carry_audit.py --roster-ref <round ref> check --body`. That command's `check` builds its destinations with `load_dests(..., ref)` and never passes `extra_ref`. So a carry file the pull request adds itself (P43) is invisible to the check. carry_audit's own API does count it. Driven with that API:

    load_dests(ref=origin/handoff/audit-r11-roster, extra_ref=None):   CARRY-AUDIT: 4 finding item(s): 3 routed, 0 unrouted, 1 bad destination(s)
    load_dests(ref=origin/handoff/audit-r11-roster, extra_ref="HEAD"): CARRY-AUDIT: 4 finding item(s): 4 routed, 0 unrouted, 0 bad destination(s)

Proposal: `carry_audit.py check` takes the branch head as `extra_ref` (or prepr passes it), as P43 intends.
