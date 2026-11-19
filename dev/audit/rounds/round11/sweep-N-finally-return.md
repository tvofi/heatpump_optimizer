# Class sweep: N-finally-return (round 11, D14 steps 3-4)

Mechanism: a `return` (or loop-escaping `break`/`continue`) inside `finally` swallows an in-flight exception, cancellation included.

## Enumerator
`python3 dev/audit/rounds/round11/D14/finally_return_enum.py <root>` — AST walk; every `Return` in a `finally` body, and every `Break`/`Continue` not enclosed by a loop inside that body; nested defs/lambdas/classes excluded. Prints the seam list and `SEAMS n` on stderr.

## Controls
- **Positive control (D14-s1-02):** the finding's seam is `_shutdown_process_pool` (coordinator.py finally at 1942-1943), which swallows only on re-introduction. On the tree as-is the enumerator returns 0 seams in `custom_components/`; with a one-line `return` appended after `_PROCESS_LOCK.release()` it returns exactly that seam (`_shutdown_process_pool`, line 1944). Re-found.
- **Null control:** clean fixture (`try: return 1 / finally: pass`) -> `[]`, SEAMS 0.
- **Perturbation:** the same one-line re-introduction moves the count 0 -> 1.

## Seams over the whole repository (`.`)
| seam | disposition |
|---|---|
| `custom_components/heatpump_optimizer/coordinator.py` `_shutdown_process_pool` (finding site D14-s1-02) | **not applicable** at this head: no return in the finally; it is a live seam only under re-introduction, which no guard prevents (unguarded, no barrier) |
| `dev/archive/handoff/r9-f2-solver-4/mutation_proof.py` `main`, line 224 | **instance** (beyond the finding): `return 2` inside `finally` discards any exception from `sh(...)`, KeyboardInterrupt included, when the restore check fails. Probe: patch `sh` to raise KeyboardInterrupt and `clean` to return False; `main()` returns 2 instead of raising. Archived instrument, so production impact is nil |

No other seam in `custom_components/`, `tools/`, `tests/` or `dev/`.

## Barrier
None exists (`barriered: false`). Proposed: run this enumerator over `custom_components/` and `tools/` as a `tests/` check (or ruff `B012`, which flags the same shape), under one gate second.
