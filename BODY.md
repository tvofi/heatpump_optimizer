Fix review: blocked 02954c6aa76b64f0bbf904f233f954c5d0cbb168 wrong-behavior: _scoped_minimize no longer pins BLAS to one thread (limit(limits=None) is a no-op)

## Block
custom_components/heatpump_optimizer/optimizer.py:~889: `with _blas_threads.limit(limits=None):` replaced `threadpool_limits(limits=1)`. In threadpoolctl 3.7.0 (manifest floor >=3.5.0) `limits=None` sets nothing, so the solve runs with the libraries' default thread count. The fix's stated purpose (one controller) is met, but the one-thread pin the function's docstring promises ("Identical results by construction ... threads were pure overhead") is silently dropped: a CPU regression on the Pi-class target and an unflagged behaviour change in a memory-peak hotfix. The correct call is `limit(limits=1)`.

## Findings
- optimizer.py:~889 `limit(limits=None)` is a no-op; threads inside a scoped minimize are [4,4] at head vs [1,1] at base.
- tests/features.py (_blas_pin_shared_controller): vacuous for the pin. It asserts only that no ThreadpoolController is constructed and that _blas_threads is the right type; nothing observes the thread count inside the minimize, so the `limits=None` mutant passes. The pinned killed mutant (GUARD_OFF on `if _blas_threads is None`) does not cover the argument either. The `limits=` argument needs a test that reads get_num_threads() inside the objective, with a null control.
- tests/replay.py ref47 cpu_ratio budget 3.3424 -> 2.7713 (re-recorded down) and the new replay_cost_draws.tsv rows were not re-derived by me; the unpinned thread count could shift the CPU draws they rest on. Not verified.

## Evidence
- Harness: standalone import of optimizer.py (homeassistant stubbed with MagicMock; the venv has no homeassistant, so tests/features.py, tests/stress.py and the gate could not run here: ModuleNotFoundError at tests/harness.py:25).
- head 02954c6aa76b64f0bbf904f233f954c5d0cbb168: RESULT threads inside scoped minimize: [4, 4]
- base f365ce757ded1e64a9ec40102495b7c051055f38: RESULT threads inside scoped minimize: [1, 1]
- threadpoolctl 3.7.0: `c.limit(limits=None)` -> threads still [4, 4]; `c.limit(limits=1)` -> [1, 1].
- Not done: mutation proofs, null-control re-runs, env_drift, VERSION/manifest check, forward-carry check (no suite runnable; blocked on the defect above regardless).
