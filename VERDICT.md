Fix review: merge af79498c8e0d50b7e15ca4f759e0e32b7df9aece

bus-nonce: 1876732288d267417d04017d00e3bb86

## Summary

Round 1 (no earlier verdict or comment on #2752). Measured head af79498c8e0d50b7e15ca4f759e0e32b7df9aece, which is the head the PR body names. The diff adds two files under `dev/programme/` (INERT in `tests/closure.py`): the triage ruling `dev/programme/triage/s6-batch13.md` (P82, ACCEPT NARROWED -> R10-ORCH-LEDGER) and the delivery row `dev/programme/delivery/2752.md`. It changes no code, check, budget, closure, golden file or claim file.

## Findings

- The body's `## Head` section does not match the commit graph. It says af79498c8 "merges origin/main `4a00a3f05` ... into this PR's previous head" and that `488e0309a` sits "on origin/main `73b69fe0a`". In fact af79498c8 is a plain commit (one parent, 488e0309a), and 488e0309a's parent is 4a00a3f05. 73b69fe0a is an older ancestor of that base. The head SHA it names is correct (step 7), and no figure or check depends on this provenance text. Carry: dismissed: wording in the PR body only; the head named is the head measured, and the script-written Head section is the orchestrator's boilerplate, not the ruling

## Evidence

- Mutation proof (step 1), on the ruling's consumer `roster_edit.ruling_verdict` / `triage_refusal`. At the head, P82 reads `ACCEPT` and a roster carry citing `s6-batch13.md#P82` is not refused. With the Verdict line deleted it reads `unreadable`, and with ACCEPT changed to DEFER, `triage_refusal` refuses ("is not an ACCEPT ruling (DEFER)"). So the record is what the gate reads. `ev/checks.txt`.
- Null control (step 3): `ruling_verdict(..., 'P99')` returns None, re-run and matching the body.
- Figure (step 8): the body's verdict count, re-derived with grep in place of rg over the same pattern, is `1 Verdict: ACCEPT`, matching the body.
- I checked the factual claims inside the ruling against the head. `tools/ci/gate.py:140` holds the "still being judged; their gate decides" return. `orchestrator_tick.py` `one_pr` calls `self.judge(latest)` (line 790) and prints the NOT REVIEWABLE back-to-fixer line (line 817) from `mt.classify`'s red list without consulting `run`. R10-CI-LAYOUT-P2 is size XL in `origin/handoff/audit-r10-roster:dev/programme/rosters/wave-r10-groups.json`, and R10-ORCH-LEDGER exists there. `s6-batch12.md` is absent at this base, as the file says. I did not re-derive the 8 mis-routed tick lines and their board times: they come from the orchestrator's tick boards, which are not in the tree.
- Step 6 (class) and step 14 (metrics): the PR is a ruling record with no harness population and moves no instrument, so neither applies.
- Step 4 and step 5: no claim file or golden file changed. `VERSION`, the manifest version and the RELEASE_NOTES heading are untouched (`ev/merge.txt`).
- Merge (step 13): `git merge-tree --write-tree origin/main af79498c8e0d50b7e15ca4f759e0e32b7df9aece` exits 0, so there is no conflict and the driver was not invoked (`ev/merge.txt`). origin/main is 4a00a3f05, the PR base. The roles diff from the merge base to origin/main is empty, so the contract I applied is current.
- CI (step 11): when read, no check run at this head had concluded red, but CI had not settled. One `refresh` passed; `prelude` and `cancel-superseded` were in progress or queued; gate and pr-contract had not started (`ev/ci.txt`). The body's `## Red checks: none` holds at read time. The merge train's own required-check gate decides on the settled runs, and this verdict does not stand in for it.
- `tests/entities.py` could not be run in this container (`homeassistant` is not installed). CI's run covers the INERT classification.
