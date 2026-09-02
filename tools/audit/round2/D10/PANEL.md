# Round 2 D10 — verification panel record

Panel: three fresh verifiers (isolated, refute-first, per `tools/audit/briefs/verifier.md`),
majority-refute kills; judge re-measured every survivor and the number-based kill
(per `tools/audit/briefs/judge.md`). Verifier harnesses were session artifacts in
`/tmp/hpo-d10-v{1,2,3}/`; the judge's artifacts and verdict lines are in `VERDICTS.md`
(copied from `/tmp/hpo-d10-judge/`).

## Votes

| ID | V1 | V2 | V3 | Judge | Outcome |
|---|---|---|---|---|---|
| D10-16 log-when-unavailable | verify (medium) | verify (medium) | verify (medium) | verified, medium, bug | **stands** |
| D10-17 exception-translations | verify (low) | verify (low) | verify (low) | verified, low, hygiene | **stands** |
| D10-18 docs-examples | verify (low) | verify (low) | verify (low) | verified, low, hygiene | **stands** |
| D10-19 config-flow sub-check | refute | refute | refute | refuted (kill confirmed) | **killed** |

## Strongest counter-attacks run, and why they failed

- D10-16: coordinator-retry explanation (×2 from DataUpdateCoordinator retries) — refuted:
  the increment happens twice *within one* `_async_update_data()` call (trajectory
  0→2→4→6→8→10; stub `async_refresh` never re-invokes the update). Stub-vs-real
  reachability — refuted: mechanism is pure integration control flow; the stub logs
  nothing itself. Mode-specificity — confirmed as a nuance (ERROR-per-poll universal;
  cycle-doubling only in in-try failure modes; connect-failure mode counts 5 correctly),
  folded into the final claim wording by the judge. Weather-path null control shows the
  log-once latch working as designed outside the Tibber path.
- D10-17: broader-scope enumeration (adding UpdateFailed: 16 sites) still yields 0
  translatable; sv.json carries 0 exceptions keys; no alternative translation channel
  (issues/services sections do not cover these strings); all 13 sites user-action
  reachable. Rule page: "no exceptions to this rule".
- D10-18: looser-pattern hunts (trigger:/alias:/blueprint/service mentions repo-wide)
  found nothing but prose; the 6 fenced YAML blocks are all Lovelace card configs; the
  rule's literal remedy (hosted blueprints + link) also absent — gap stands under both
  readings. plan-v4.0.0-program.md:1241 demoted to weak support (roadmap entry).
- D10-19 (kill): all three verifiers independently parsed strings.json/en.json/sv.json —
  20/25 steps carry data_description sections, 237/238 fields covered (single gap:
  tibber_token on reauth_confirm), 0 key mismatches; the candidate's own perturbation
  leaves its own metric at 0 (void harness); the rule page names strings.json as the
  mechanism, and data_description appears only in non-binding Reasoning text.
