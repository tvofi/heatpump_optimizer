# D3-g19 working notes (partial, checkpointed)
- Probes are executed from a separate baseline worktree ($HOME/probe-tree), never in the gate tree; copies live here under probes/<key>/.
- Probe pre-run (2026-11-22 ~21:45Z, during the null gate): moved for 911f (injected stale row only; 0 of 2 shipped rows reach), b5f0, 68cc, 2043, eee3, 23b1, 68ef (stub only; real rule converges in 1 round), be95 (direct call only; optimize n=0 raises IndexError in both arms), e535, 24ef, 7f04, 4c7e, 9644. Not moved: aebe, 2ae9 (slice clamp), 1b3c (nan mean leaves weight 1.0) -> equivalent-candidate if the gate survives.
- Null gate: closure.py selftest red with 2 FAILs (merge-reason pins, status skip-not-under-scoped), same artefact as the D3-top6 null.
- NULL DONE 22:48Z: gate_rc=1, wall 4063 s (provisional, load1 0.92 at end). Red, artefact checks only:
  closure.py selftest 2 of 118 (merge-reason pins: status skip-not-under-scoped, git state of the stripped worktree);
  entities.py 1 of 2723 ("and is accepted when it does": the scoped path records only what the diff can reach -- the marker commit's scope);
  harness_headers.py 4 of 115: (1) "every inlined walk matches the canonical helper" names this box's untracked probe copies under wave/D3-g19/probes,
  (2,3) round4/D6/claims.py header 123/0 vs printed 122/1, (4) that harness leaves claims.json/claims.md modified. None is a machine failure; the null is usable, not re-taken.
  A mutant kills only by failing a script beyond these three or more checks in one of them (fullgate.py's rule).
- 911f3cf5172ffc44: RED-AS-NULL (same 3 scripts, same counts 2/1/4 as null), wall 3992 s; probe reaches line 496 only with an injected stale row -> candidate (unreachable from shipped catalog).
- b5f0a73275608684: RED-AS-NULL (null-identical reds) -> candidate (tie label fixed->entity).
- 68cc141bf2c3493a: RED-AS-NULL (null-identical reds) -> candidate (entity tie label fixed->entity).
- 2043855ef5cf151d: RED-AS-NULL -> candidate (parse_rules(None) [] -> GridFeeError).
- eee37674711fa45f: RED-AS-NULL -> candidate (guess weights max delta 0.267 at mean 6e-4).
