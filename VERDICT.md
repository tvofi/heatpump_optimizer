Fix review: merge c0913a276d01d9eb5b7a357a3d82c4eb0e87d8ce

bus-nonce: 18f60759c1f9ebee4137184b01a9579e

Round 1. Measured head c0913a276d01d9eb5b7a357a3d82c4eb0e87d8ce (the PR's live head when read).

## Findings

- The body's gate figure does not reproduce: it quotes `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`, but `python3 tests/closure.py select --diff a7dd7f50d` at this head prints `MODE: SCOPED -- 27 script(s) run, 6 scoped out.` (the figure was probably taken before the closures.json classification and the main merge). Immaterial to the fix; CI is green on the full set. Carry: dismissed: body figure stale, scoped-gate count does not gate the merge and CI ran the real gate green

## Evidence

- Source diff (base a7dd7f50d..head): `wants_self_test(argv)` returns `argv[:1] == ["--self-test"]`; `main()` calls it; docstring usage says "first argument only". Four new self-test arms.
- Finder's harness at both ends (ev/harness.txt), wrapped command `rec.sh arg1 [--self-test]` that records argv to a marker: base with the flag ran the script's own self-test, marker MISSING; base without the flag, marker "arg1" (flat control); head with the flag, marker "arg1 --self-test"; head without, marker "arg1".
- Self-test at head under env -u BASH_ENV: all 15 arms ok, SELF-TEST PASS (ev/selftest.txt).
- Mutant daemonize-1 via the harness: KILLED rc=1, `RESULT survivors=0` (ev/mutant.txt); the body's M0 red was its host's, green here. Direct mutation on a copy (`"--self-test" in argv`): two arms FAIL, SELF-TEST FAIL, exit 1 (ev/mutant-direct.txt).
- Callers: only `.github/workflows/governance.yml:614` invokes `daemonize.py --self-test`, in first position; no caller passes it later. Other mentions are prose.
- Merge: `git merge-tree --write-tree origin/main` exit 0, no conflict (ev/mt.txt). Files changed: the harness, delivery row 3058, closures.json (+daemonize.py), daemonize.py; no claim file, golden, VERSION or notes touched. daemonize.py sha1 e3ed6132625f... matches the body.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED. Delivery row present in the three-dot diff. Carry 1 answered as the body says (restricted and pinned).
- Body `## Red checks`: none; CI at this head: merge_train.py classify exits 0, GREEN, nothing pending or red (ev/classify.txt).
- Class open: the defect is one predicate in one file; no other seat script matches `--self-test` anywhere in argv by this pattern in daemonize.py.
