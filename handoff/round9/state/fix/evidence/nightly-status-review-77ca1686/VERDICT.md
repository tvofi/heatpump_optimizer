Fix review: merge 77ca16867e83bb603fd21dd2cbb8f6343c601c82

Round 1. Measured at code head 77ca1686 (transport 1625218b above it; branch head 1625218b at posting). Base dc6c97e4 = origin/main; merge-tree clean.

1. Root cause: plausible, and stronger than the body states. Red job 110408288183 (run 36873895128) named schedule run 35575590367 (09-21). Live probe now: that run is exactly item 1 of page 2 of `event=schedule&per_page=10`, and page 2 of `event=workflow_dispatch&per_page=10` carries no main dispatch. The main dispatch 36463132269 (09-28), inside page 1 of the dispatch listing, was also absent from the red answer, or it would have been named. So BOTH listings were wrong at once, and the red answer equals exactly what page 2 of both gives. That is a server-side wrong page (or a stale snapshot from ~09-21), not this code. It is inferred, not reproduced. Non-blocking: the body's "served an incomplete answer once" could say both listings and the page-2 match.
2. Barrier holds. A windowed re-ask uses the same event and branch filters, so it cannot admit a run the first listing would refuse. Every-shape-old stays ABSENT. An empty window keeps the old run, so it is ABSENT and names it. If the re-ask is also served a wrong page, it is ABSENT (fail closed). The age is still judged by verdict(). Probed `created=>=2026-09-28&per_page=30`: it returns 4 schedule runs, all on one page.
3. Tests: the check body was run standalone against the head (harness.py here): RESULT ok. Red-first at the seam: CORROBORATIONS=0 (old behaviour with the seam present) gives RESULT FAIL. Targeted mutants:
   - M1 no re-ask: killed.
   - M2 always re-ask: killed by the fresh-call arm.
   - M3 re-ask in the same shape: killed.
   - M4 widened freshness test: killed.
   - M6 drop the windowed answer: killed.
   - M5 drop the first answer from the union: SURVIVES. It is near-equivalent: the state is ABSENT either way, and only the run the report names differs. Not blocking.
4. Class: the other runs-API readers (stamp.py, contract_rerun.py, budget_raise_gate.py, approve_held_runs.sh) filter by head_sha, run id or status, not newest-N. One seam.
Cite CI once the draft is open: entities.py in full, harness_headers, prepr closures, mypy/typing (unrun by the fixer and by me). Code-owned file: tvofi's approving review is owed (the Mac, under the mandate).
