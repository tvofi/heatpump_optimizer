# Proposal triage, session s8, batch 77 (P314)

The rolling batch (V182) after batch 76 (handoff `triage-s8-batch76`). Facts were read at
origin/main `a6e4a5afe`, in the hpo-approver review comment on #3013 (`6533404333`), and in the
orchestrator's live merge-train log (`merge_train/train.log`, every `PARK #N findings` line).

## P314: carry_audit parks a merge verdict on its approval precondition

Verdict: ACCEPT narrowed, as an amendment to P308 (`s6-batch74.md#P308`), on
**R10-FLY-RELAY-REVIEW-FF**, the same carry and the same pull request.
- **The rule.** In a **merge** verdict, P308's structural rule governs every section except
  `## Findings`, `## Friction` and a block heading, not `## Evidence` alone. In those sections an
  item is a finding only when it opens with a LEAD, sits under one, or carries a `Carry:` marker.
- **Unchanged.** A blocked verdict keeps today's rule, because its block is owed in the PR.
  `## Findings` keeps its NONBLOCK reading, which is where a reviewer's nit belongs.
- **REJECTED: an approval or code-owner keyword exclusion** (lines naming "code-owned",
  "approving review", "requires tvofi"). It is a predicate shaped by one failure. It would also
  free a real finding that happens to name code ownership, and it leaves the next precondition
  phrasing (a ruleset, a mandate, a stamp) to the next park.
- **REJECTED as unneeded: a reviewer-side non-finding lead.** The structural rule already treats
  an unmarked Summary line as prose, so no fixer or reviewer changes what it writes. That avoids a
  policy edit to the capped `dev/governance/roles/fix-review.md`.

Source: the orchestrator s8's message of 2026-10-30T22:16Z.

Instances:
- **The park.** The train log's `PARK #3013 findings: 1 finding item(s) with no valid Carry:
  ...; first: review 6533404333 item fccf8846 (unrouted)` (log line 4545). `carry_audit.py pr 3013`
  at `437f1ba9b` prints `UNROUTED #3013 review 6533404333 item fccf8846 (## Summary)
  [non-blocking]`.
- **The trigger.** The item is line 9 of the merge verdict, under `## Summary`: "`away.py` is
  code-owned, so `main-protect-checks` requires tvofi's approving review at merge. This verdict
  flags that and does not block on it." The `non-blocking` class fired on "does not block". In a
  merge verdict every non-Evidence section reads NONBLOCK (`carry_audit.py:209-216`), so a Summary
  sentence about a precondition reads as a deferred nit. HOTFIX #3013 was parked, then waived by
  name under the mandate.
- **How many parks were this shape.** The train log holds 21 `PARK #N findings` lines on 16 PRs.
  By their first item:
  - this approval precondition: 1 (#3013);
  - one bad destination each: 2 (#2962 `75f08830`, #2925 body `162aa32f`), P296's class;
  - in `## Findings`: 2 (#2876 `ea167ba8`, and #2955 `2471d3e6`, "None. ... nothing is deferred
    or owed", P293's null-row shape);
  - blocked verdicts (owed by design): 2 (#2881, #2933);
  - every other first item is a reviewer's `- ` measurement bullet. P293 and P308 place #2939,
    #2955 `158ad202`, #2959, #2969, #2987, #3001 and #3002 under `## Evidence`. #2917, #2980 and
    #3007 were not re-sectioned here.
  So the approval-precondition shape is 1 of 16 PRs. The merge-verdict prose class it belongs to,
  with the Evidence bullets, is the bulk of the parks.

Cost:
- Inside P308's change: the Evidence condition at `carry_audit.py:205` widens from "the Evidence
  heading" to "a merge verdict's section that is not Findings, Friction or a block heading". That is
  about 2 lines and one more fixture row in the same PR.
- No new file, check or API call. `carry_audit.py` is not a capped file, and no policy file
  changes.

Binding:
- One hotfix parked and waived. The same rule already accepted for Evidence (P308, 12 flags and
  0 findings) covers it at near-zero marginal cost.
- The keyword exclusion would add a third word list to a predicate whose word lists have not
  converged (P293, P306), so it is rejected.

Carry text (for `roster_edit.py append-carry R10-FLY-RELAY-REVIEW-FF`, citing
`triage: dev/programme/triage/s6-batch77.md#P314`): "Amends P308 (same carry, same pull request):
P314 (orchestrator 2026-10-30T22:16Z).
- In a merge verdict, P308's structural rule applies to every section except `## Findings`,
  `## Friction` and a block heading, not only to `## Evidence`. An item there is a finding only
  when it opens with LEAD, sits under a lead, or carries a `Carry:` marker.
- Blocked verdicts and `## Findings` keep today's reading.
- No keyword exclusion for approval or code-owner lines.
- Observed: HOTFIX #3013 parked on review 6533404333 item fccf8846 (`## Summary`, [non-blocking]):
  "`away.py` is code-owned, so `main-protect-checks` requires tvofi's approving review at merge.
  This verdict flags that and does not block on it." Waived by name under the mandate.
- Fixture rows:
  - That item, in a merge verdict's Summary, passes.
  - Null, still a finding: the same sentence under `## Findings`.
  - Null, still a finding: a Summary line opening `Follow-up:`.
  - Null, still a finding: any item of a blocked verdict, by today's rule.
- One mutant: restrict the rule back to the Evidence heading, and the Summary row fails."
