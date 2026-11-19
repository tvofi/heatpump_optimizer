# Class sweep I3, round 11 (D14 steps 3-4)

Class I3 covers a required governance or CI check that is skipped, runs a stale
ref, or has a bypassable boundary. Its ledger status is `barriered`
(field_coverage.mjs, policy-docs). None of the seams below is among the inputs
that barrier reads, and its own "not read" list names D11-s1-02.

## Enumerator

`python3 dev/audit/rounds/round11/D14/I3/enumerate_I3.py` recomputes four
families from the tree:
- the stop-hook prefix gap
- live rosters that brief_lint does not lint
- unowned meters that run from the PR copy
- readers that tell the owner from an agent by review-body text

It reads the families that need the API from the finders' recorded snapshots.
These are the rulesets, gate-at-merge, release provenance and seat self-test reach.

The `--self-test` run exits rc=0:
- positive control: it re-finds every finding site, and none is missing.
- null control: a catch-all stop-hook prefix returns 0 seams, and brief_lint run over every roster returns 0.
- perturbation: removing `dev/governance/` from POLICY_PREFIXES raises the count.

## Dispositions (15 seams)

| seam | disposition |
|---|---|
| stop-selfcheck.sh: AGENTS.md, dev/audit/README.md | instance: D11-s1-01 |
| rulesets 22628467, 23937752 | instance: D11-s1-02 |
| tests/structure.py meter | instance: D11-s1-05 |
| wt_sync.sh --self-test | instance: D11-s1-06 |
| merges #3618, #3644 / platform_gate | instance: D11-s2-01 |
| budget_raise_gate.approval AGENT_DECLARED | instance: D11-s2-02 |
| release zip attestation | instance: D11-s2-03 |
| brief_lint: wave-r10, wave-r9 rosters | instance: D11-s3-02 |
| **tools/pr/outside.py class-O approval** | **instance beyond the findings.** The gate tells the owner's own approval from an agent's by the AGENT_DECLARED body text alone, the same mechanism as D11-s2-02. Probe: an agent approval whose body leaves out the declaration words and cites no mandate is accepted as the owner's own form. |
| merge_train.py AGENT_DECLARED | not applicable: it calls `budget_raise_gate.approval`, the judged site |
| merge_pr.sh AGENT_DECLARED (line 327) | not applicable: a self-test fixture assertion, not a gate |
| dev/archive/rosters/* | not applicable: archived and not dispatched from |
| meters stress.py, typing_ruler.py | guarded: CODEOWNERS owns them |
| meters machinery_ratchet.py, policy_lint.mjs | guarded: no required job runs them from the PR copy |

The sweep finds 1 instance beyond the findings. The class is already barriered,
but the barrier reads none of these seams. Proposed barrier extension: register
the four recomputed families as checks in field_coverage.mjs.
