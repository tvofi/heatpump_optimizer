Carried from #2464 (R10-CI-LAYOUT PR 0) at dd3a4447, round 3:
- U9's re-keyed `ci_ratchet.py` reader (PR 2) keeps R(c)'s `reused` exclusion, `_CIR_REUSE` and the budget-equality pin unchanged. Any later lane edit, PR 1's W1 or the umbrella's split of `tests.yml`, keeps `tests/harness_headers.py` in the alone phase: the run-alone pin refuses otherwise.
