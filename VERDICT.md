Fix review: merge c146e900cd2e4a195a7a5c8dea19f627310d88e8

bus-nonce: 73cbbdbc60c4c9d7abde0e0d8b806239

Round 1. Reviewed from a detached worktree at c146e900cd2e4a195a7a5c8dea19f627310d88e8 (base 279578074a17cb2c7f527f5e28da0de4e2006db0). This is a test and harness PR that writes no production line. Every finder harness named in the body was re-run at this head.

## Evidence

- Census at head: RESULT census_stores_held=12, census_lost_total=0 of 12, census_unfenced_differs=_ctx,_price_learner. All three CHECKs pass; the run takes 22.7 s wall (ev/census-head.txt).
- Failing first: the head's census at c78df2b86 (before #2817) reads census_lost_total=2 of 12 (dhw_legionella -> _ctx, price_model -> _price_learner). The second CHECK FAILs (ev/census-c78df2b86.txt).
- Mutation proof, re-run over all 16 production `await ...async_wait_for_read()` fences, one at a time (ev/fences.txt, ev/mutants.txt). M1 is coordinator.py:8413 and turns the census red with price_model -> _price_learner. M2 is legionella.py:213 and turns it red with dhw_legionella -> _ctx. The other 14 fences survive the census. That matches the body's stated scope: the census covers only the setup-refresh window, and the remaining writers are dispositioned there as gated, or as user-command writers pinned by #2817's _RACES checks. The worktree was restored clean after the sweep.
- Null control: the unfenced arm reads non-empty (_ctx,_price_learner), so the census is not blind. I counted the *_cache/*_memo exclusion fields myself and got the body's 9: the 8 in ev/cache_memo_fields.txt plus DefrostDerate._factor_memo (defrost.py:242).
- #2674 finder harness r10_store_load_leads.py at head (sha1 9b69a689 matches): price_shape_lost=0 null=0 and extra_legionella_observer_lost=0 null=0. The six gated leads each read fresh_call_writes=0, and their gate-open arms read lost=1 null=0 (ev/store_load_leads-head.txt).
- #2248 port r10_livestate_restore_race.py at head (sha1 929edc46 matches): l3_differ_total=0 of 3, l3_null_differ_total=0 of 3, probe_lost_midload=0 (ev/livestate-head.txt).
- #2249 v2_s4_fabric.py at head (sha1 0bcd55bf matches): lower-floor samples after 12 intervals = 12 in both orders (ev/fabric-head.txt).
- Figures I did not re-derive: the 3 of 3 at d5dc3e26a (out-of-tree $EXPORT l3 harness), the 0 at c78df2b86 for #2249, the #2499 overbook figures, and the census cost timing. The last three describe the base or carries, not this change.
- Merge: `git merge-tree --write-tree origin/main c146e900cd2e4a195a7a5c8dea19f627310d88e8` exits 0, with no conflict and no claim-file involvement (ev/merge-tree.txt).
- VERSION, the manifest, RELEASE_NOTES, golden fixtures and both claim files are untouched by the three-dot diff. The only instrument move is one closures.json entry for the new harness, which CI tests / closures and tests / closure-scope pass.
- Live check-runs on this head: every gate check that has concluded is success or skipped, except tests / nightly-status. That check grades main's Nightly, and the diff (features.py, closures.json, a harness, a delivery row) reaches nothing it reads. The body answers it under Red checks. CodeQL Analyze (python) and a prelude run were still in progress at read time; neither is a gate check this verdict turns on.
- Head re-read before posting: still c146e900cd2e4a195a7a5c8dea19f627310d88e8. The body names authored head 1e4284bb5 plus an orchestrator merge of origin/main and a delivery-row-only commit, which is consistent with the commits at this head.
- Forward-carries in the body (R10-COP-PARTLOAD x2, #2499) are the fixer's own routes. carry_audit at head: 4 routed, 0 unrouted.

## Findings

none
