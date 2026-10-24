Fix review: merge 113e540ae2b94b04cea2de2427b78aa20f013eb2

bus-nonce: ec93b265b219cd2f5f30108b7c689a1c

Round 1. Measured head `113e540ae2b94b04cea2de2427b78aa20f013eb2`, still the PR head when this verdict was written. `dev/governance/roles/` is unchanged between the merge base `e783f0920` and origin/main `4a00a3f05`, so the contract applied is current.

## Findings

- The ruling's #2622 paragraph calls that friction "owned, not new" because JIDOKA's owner-ruled carry names `tmp_paths --check`. It leaves out a stronger fact: `tools/pr/prepr.sh` has run `tools/audit/seat/tmp_paths.py --check` since `3b0a39216` (2026-10-06), before #2622. #2700's census already called #2622 "already guarded" for this reason. The REJECT stands either way, because the friction came from a unit handoff that skipped prepr, not from the rule's text. Carry: dismissed: wording only; it does not move the verdict or anything routed

## Evidence

- Scope: the three-dot diff adds two files under `dev/programme/`, 15 lines: `triage/s6-batch12.md` and `delivery/2750.md`. Both sit under `tests/closure.py`'s INERT prefix `dev/programme/`. There is no code, budget, claim-file, closure, VERSION, manifest or notes change. Steps 4 and 5 hold trivially, and step 14 has no instrument movement to earn.
- Mutation (step 1), on the ruling record's consumer, run at this head with `PYTHONPATH=tools/audit/seat`. The output is in `ev/checks.txt`.
  - RESULT `roster_edit.ruling_verdict(src, 'P81')` = `REJECT`.
  - RESULT null control `'P99'` = `None`, which matches the body.
  - RESULT mutant: rename the `Verdict:` line to `Verdikt:`, and the same call returns `unreadable`. The record's verdict line is what the reader keys on.
  - RESULT `triage_refusal` on a carry citing `s6-batch12.md#P81` refuses with `is not an ACCEPT ruling (REJECT)`. So a REJECT routes nothing, as `## Forward-carry` says.
- Figure: `rg -o '^Verdict: (ACCEPT|DEFER|REJECT)' -r '$1' dev/programme/triage/s6-batch12.md | sort | uniq -c` gives `1 REJECT`, which matches the body.
- Re-derived against primary sources:
  - Issue #2746 states count 3, window `v7.0.4..origin/main`, rule id `gate-scoping`, which matches the ruling's header.
  - #2622's body carries `gate-scoping: unenforced` (UP's handoff did not run `tmp_paths.py --check`). It merged at 2026-10-22T22:23:41Z (merge commit `a1633381a`).
  - #2627's body carries `gate-scoping: cost` (the cloud default `python3` is 3.11 and cannot parse `tests/entities.py`). It merged at 2026-10-23T01:03:18Z (`e364a0d73`).
  - #2700's body carries `gate-scoping: cost` (794/794 tokens) with `Carry: dismissed: an observation, no defect`. It merged at 2026-10-24T16:15:16Z.
  - `c686fe3668b2` is #2700's merge, and `git merge-base --is-ancestor c686fe36 origin/main` succeeds. #2528 merged at `f0724675f`, 2026-10-22T18:35:57Z.
  - #2700's diff of `dev/governance/rules/gate-scoping.md` adds the quoted interpreter paragraph (`$PYTHON`, else `.venv/bin/python`, else `python3`, 3.12+, `seat_venv.sh`, citing #2627).
  - The roster (`handoff/audit-r10-roster` at `1debc245a`) holds R10-FLOW-JIDOKA's owner ruling of 2026-10-22, which names `ref_privacy --check` and `tmp_paths --check` as quick checks for prepr.
  - P78 is on `triage/s6-batch9` (S6-V14, ref_privacy in prepr). P80 is on `triage/s6-batch11`, unmerged, so P81 continues the numbering.
- Count re-derivation: I could not run `node tools/policy/policy_lint.mjs --stats --since v7.0.4` because this seat has no token. The count of 3 rests on the bot issue's measurement plus my reading of the three named bodies; that reading does not independently enumerate every merged body in the window.
- "Would change the answer" check: a search for merged PRs after 2026-10-24T16:15:17Z mentioning `gate-scoping` returned 0. The first-parent merges since c686fe36 (#2742, #2735, #2740, #2736, #2734) do not reopen it.
- Merge (step 13): `git merge-tree --write-tree origin/main 113e540a` exits 0 with tree `f3ddadd68`. There is no conflict and no MERGE-CLAIM line, because no claim file is touched.
- CI on this head, from the check-runs API (36 runs) when this verdict was written:
  - No run concluded failure.
  - Every concluded gate run is success or skipped: fast (3.14), closures, closure-scope, mutation, briefs, wave-script, policy-docs, delivery-status, instrument-self-tests, env-matrix, nightly-status, budget-raise-gate, arch-score, hassfest, validate-hacs, codeql and typing.
  - `tests / coverage` and one `prelude` were still in progress. No `pr-contract` run appeared in the listing.
  - `## Red checks: none` is consistent with this.
- Forward-carry (step 10): n/a. A REJECT carries nothing, as confirmed by `triage_refusal` above.
- Class (step 6): a single triage ruling, so there is no seam enumeration to run.
