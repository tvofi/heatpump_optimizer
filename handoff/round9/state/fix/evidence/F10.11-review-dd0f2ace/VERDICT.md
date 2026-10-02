Fix review: merge dd0f2ace379d08bb848b361275277688b4b8d017

R9-F10.11, PR #1819 (PR head 9ceb693d = code head dd0f2ace + docs/delivery/1819.md row; transport c5b4f867 BODY.md only).

No barrier is lost.
- Scope: RLIMIT_CPU is set in preexec_fn, so only the forked child carries it. The parent's limit is unchanged, (-1,-1) before and after (probe_bounds.txt). A grandchild inherits it with a fresh counter, so a spinning grandchild is still killed (rc -24).
- Hang: a spinning child dies at the CPU limit (rc -24, SIGXCPU). An idle or I/O hang is bounded by the 900 s wall cap, which reports rc 124 as a failed check. 900 s is below mutation_table's 1200 s per-driver timeout.
- Slow regression: the threshold is the same 240 s of CPU that an unloaded core gave before. A CPU-bound slowdown is caught at the same point, and load no longer counts against it. Only a regression into waiting gets more room (up to 900 s), and the old comment said the bound is for hang detection, not runtime policing.
- CI runners: the fast, slow and closures jobs pin *_NUM_THREADS=1. The mutation and mutation-nightly jobs do not. sysid_estimator_frontier.py, h7_memory_gate.py and claims.py setdefault the thread variables to 1 themselves before numpy loads, so CPU seconds track one core. The Linux semantics are the same as this box's. On macOS, resource.RLIMIT_CPU and preexec_fn behave the same way.
- Controls: the three new checks kill mutants A (preexec_fn dropped), B (wall timeout dropped) and C (the rlimit fed the wall argument). The null and comment-only variants survive (mutants_controls.txt).
- Null control in the mutation lane: the old crash came from TimeoutExpired under pool load. With the CPU bound, load cannot trip it. A comment-only mutant now fails only if a harness really overruns 900 s wall.
- Repro (repro.sh, two copies each under taskset -c 0, Py 3.11 venv with numpy 2.4.6 and scipy 1.17.1): main 0bfb8883 had both copies crash with TimeoutExpired on sysid_estimator_frontier.py after 240 s, rc=1, 250 s wall. Head dd0f2ace passed both, "ALL 94 HARNESS HEADER CHECKS PASSED", rc=0, 279 s and 286 s wall.
- CI at 9ceb693d (cited, not re-run): fast (3.14), mutation, typing, closures, closure-scope, browser, policy-docs, pr-contract and budget-raise-gate all passed. coverage, env-matrix and CodeQL python were still running when this was written; the merge still needs them green.

Optional, non-blocking: no check pins the values of CPU_LIMIT_S or WALL_LIMIT_S. The controls pass their own bounds, so raising either constant would go unnoticed. One more check could cover this: CPU_LIMIT_S <= 240 and WALL_LIMIT_S < 1200.
