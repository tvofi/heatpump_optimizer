# Box D3-g34 partial notes (written as the work goes; provisional until results/<key>.json exists)
Probes (all on SystemIdentification.identify, in memory) run before the gates finished, while the null gate ran:
- separating (candidate if the gate SURVIVES): b8d5ec03 (rows<5 off: 2/2), 756f3beb (tm prior floor: 2/2), 84372c0e (k_hat clamp: 1/1),
  20f72103 (h_prev guard off: 3/3), 50daaa57 (h_prev tie 3600us: 3/3), 4eeb3661 (3 triples: 2/2), 44bb0ce0 (sigma2 tie: 1/1),
  10665a84 (rank<2 off: mutant completes on collinear columns, 2/2), d7421c10 (rank<=2: refuses rank-2 fallback 1/1), 07227ec9 (sign guard off: 1/1)
- equivalent-candidates: 3918ca4f, a9bc37e9 (rows>=5 guard precedes), b97b45a6, 6b6a8493 (sigma2==0 inert), 3e78e62a, 87c3101b (1e-6 tie never hit in 1602 inputs)
All null controls 0. identify() is harness-only at the baseline (sysid.py:1826-1835): severity low, hygiene.

## Null control (fullgate.py null, 21:44-22:43Z, wall 3552.9 s provisional, load1 0.89..0.93)
gate_rc=1, red: closure.py selftest (2 of 118: 'a refused merge surfaces merge()'s reason' and its null, status skip-not-under-scoped,
a scoped-derive artefact of the detached worktree), entities.py (1 of 2723: 'and is accepted when it does' -- the scoped path records
only what the diff can reach, the same worktree-scope artefact), harness_headers.py (4 of 115: round4/D6/claims.py header 123/0 vs printed
122/1 and its output-byte check -- the finder-wall strip removes what claims.py reads; plus the inlined-walk check, which named this box's own
build_results.py `ROOT = S1.parents[4]` and _sysid_lib.py's non-canonical repo_root). All artefact checks of the tree state, none a machine
red (no card.mjs heap, no stress/optimality): the null is usable, not re-taken. After the null the two wave files were given the canonical
repo_root (inline_scan rc=0), so a key gate's harness_headers count can only be <= the null's 4, never above it.
