# Provenance of the API snapshots

Reads of the live GitHub API made by the round-5 D11 fix seat (#1300) on
2026-09-22, against repository `tvofi/heatpump_optimizer` at the fix's merge
base `129f96b33a98ff419b483d4800c9dbd4feac3953` (origin/main pinned at the
round's resumption). Three read-only calls; the live required-contexts
boundary did not move between the round-5 baseline (`1cc89e0`, 2026-09-20) and
this reading — both carry the same four branch rules and the same 15 contexts.

`governance_drift.mjs` answers every `gh api` the production derivation makes
from these files, never from the network, so no arm of that harness can touch
the live ruleset. They are frozen evidence: a later ruleset change makes them
stale against the live API, and the *production* check (not this harness) is
what reddens when it does.

- `rules-branches-main.json`  <- `gh api repos/tvofi/heatpump_optimizer/rules/branches/main`
- `ruleset-22628467.json`     <- `gh api repos/tvofi/heatpump_optimizer/rulesets/22628467`
- `ruleset-23698884.json`     <- `gh api repos/tvofi/heatpump_optimizer/rulesets/23698884`

What they record, at that SHA:

| ruleset | name | rules | bypass actors | required contexts |
|---|---|---|---|---|
| 22628467 | `main-protect` | `deletion`, `non_fast_forward` | none | none |
| 23698884 | `main-protect-checks` | `required_status_checks`, `pull_request` | `DeployKey` / `always` | the 15 in the fixture |

The branch endpoint's `required_status_checks` rule carries
`ruleset_id: 23698884`, so the derivation's contributing-ruleset set is
`[23698884]` — the id the committed fixture records and the one the drift check
now compares. Ruleset `22628467` guards the branch's *push* surface
(deletion, non-fast-forward) and supplies no required context; it is the id the
fixture named before this fix, and naming it is why real drift read as 0.
