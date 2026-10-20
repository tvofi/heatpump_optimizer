Fix review: merge afabd5b6a6e2da5bb42eaad5f6697837491c5556

Round: 3 of R10-SETPOINT-BOOST (round 1 at 345cdf58 and round 2 at afabd5b6 were both blocked carry-missing). This is not yet the fourth round, so a repair is owed, not a re-cut. The review is delta-scoped: the code and body are unchanged since round 2, and nothing here contradicts round 2's measurements. Those stand as round 2 recorded them (mutants M0 to M15, features, structure, harness at both ends).
Head measured: afabd5b6a6e2da5bb42eaad5f6697837491c5556. I re-read the PR head just before return and it is unchanged. origin/main at review: 52011c69a, which contains roster PR #2471 (d68999cf). Contract: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## Round 2's blocker, re-checked

- **carry-missing: resolved.** I opened R10-CEILING-PROBE's `brief` in `dev/programme/rosters/wave-r10-groups.json` at origin/main (ev/ceiling_probe_group_origin_main.txt). It now opens with "Carried from #2465 (R10-SETPOINT-BOOST) at afabd5b6; the ceiling probe owns these:" and states all three items:
  1. **The floor-only mapping and the set-point-to-draw gain.** Identifying the gain is the ceiling probe's: its cheap-night `sysid.py` experiment measures drawn power against the commanded set-point.
  2. **Reaching the real maximum.** It needs p_max at its true value or a deliberate ceiling probe, with B as the prerequisite.
  3. **Idle draw absorbing compressor draw.** The brief carries the measured 24/72 drop and the 1.35 -> 1.8 kW low end, and adds "The ceiling probe's controls should include a gate-held draw above idle".

  The two items round 2 found missing are now in the tree with their control. The other three destinations (R10-DEMAND-OVERBOOK, R10-BUFFER-STORE, R10-COP-PARTLOAD) were carried at round 2.

## Notes, non-blocking

- The body's `## Red checks` entry for `pr-contract` is stale, and is now false in two places:
  - It says that against origin/main carry_audit "reads ... 6 bad destination(s)". It now reads 6 routed, 0 bad.
  - It says pr-contract "stays red until the roster PR merges". pr-contract is green on this head.

  Not blocking: it describes a red at an earlier head, and that red is answered. Carry: dismissed: stale body wording, no later stage changes
- Instrument finding, not this PR's: `carry_audit.py pr 2465` reads 9 items, 8 routed and 1 unrouted. The unrouted one is round 2's own `bus-nonce: 0f1f8919...` line, which sat under that verdict's `## Notes, non-blocking` heading. `TRAILER` (tools/audit/carry_audit.py:92) matches `bus:` but not `bus-nonce:`. So in `pr`/`sweep` mode, any verdict whose last section is a note heading counts its own nonce trailer as an unrouted finding. `check --body`, which is what pr-contract runs, is unaffected. I have touched nothing, and I am relaying this to the orchestrator to route. Carry: dismissed: relayed to orchestrator, outside this PR (ev/carry_audit_pr.txt)

## Verified at this head (RESULT lines)

RESULT carry_audit body vs origin/main(52011c69a): `CARRY-AUDIT: 6 finding item(s): 6 routed, 0 unrouted, 0 bad destination(s)`, exit 0 (ev/carry_audit_body.txt)
RESULT pr-contract local body check (origin/main's tools/policy/policy_lint.mjs, --red mutation, author hpo-author[bot]): `PR-BODY: 0 error(s)`, red-history `record` over 7 commits, arch-score and mutation answered (ev/policy_lint_body.txt)
RESULT figure_lint at head: `FIGURES: 11 resolved, 0 not verified, 0 refused` (ev/figure_lint.txt)
RESULT merge-tree: `git merge-tree --write-tree origin/main(52011c69a) afabd5b6` exit 0, tree f8d67f96, `LEDGER-MERGE: resolved tests/closures.json` (inert_reads merged as a set), no MERGE-CLAIM line, no conflict (ev/merge_tree.txt)
RESULT CI on afabd5b6, from the check-runs API at 01:50Z: 42 success, 13 skipped, 1 failure, 3 in progress (ev/check_runs.tsv)
- The failure is `mutation`, and the body answers it under `## Red checks`.
- Both `pr-contract` runs on this head succeeded (00:22:54Z, 00:23:18Z). Both started before `mutation` concluded red at 00:24:37Z, so the push-time run is the one that checked the body. My local re-run of that body check, above, is also clean.
- `closures` and `fast (3.14)` have now concluded success.
- `mutation-pins (1)`, `(3)` and `(7)` are still in progress, so the Tests workflow is incomplete. I do not cite them as green. They are CI's heavy runs, so I did not re-run them.

The owner's export is private. Its aggregates (54 samples, 41 at p_min, 25.0 written) were not re-derivable here, as at round 2, and are not verified by this review.

bus-nonce: f8b99351faf07ba42212a4e33dd4f5ff
