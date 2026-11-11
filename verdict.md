Fix review: merge cbe349515738db71982d61a1156f19d60364041c

bus-nonce: 311d362af5ed76022dd1a73f0bdf3276
pending-ci: codeql / Analyze (python), tests / coverage-ratchet, tests / fast (3.14), gate

Round 1 (first review), full scope. Measured head cbe349515738db71982d61a1156f19d60364041c (ev/HEAD.txt).

## Evidence

- RESULT: stale-hash reader at main (f24d107bd / origin/main) and at a7628041: `summary ... files=5 exposed=7`, rc=1; seven lines: coverage, homeassistant, astral, sqlalchemy, uv, acme, python-dateutil. At d4252d00 and at the head: `files=5 exposed=0`, rc=0. `--self-test` OK (ev/tree.txt).
- RESULT: mutant KILLED. Planting `astral==3.2` in a typing-lock comment at the head: tests/entities.py rc=1, `1 of 2709 ENTITY CHECKS FAILED`, the sole new FAIL being `no lock comment names a hash-pinned package as name==`; the planted-arm check stays ok (ev/mutant-astral.txt). Null (unmodified head): rc=0, `ALL 2709 ENTITY CHECKS PASSED`, both new checks ok (ev/null-head.txt). The other FAIL-text lines in both logs are checks' own printed negative-case output, identical in null.
- RESULT: requirements-typing.txt and requirements-coverage.txt: every non-comment line byte-identical merge-base to head; the harness at the head reads no comment spelling a pinned package `name==` in either lock (exposed=0 over all 5 locks).
- RESULT: VERSION, manifest version and RELEASE_NOTES heading untouched (no diff). Claim files untouched.
- RESULT: `git merge-tree --write-tree origin/main <head>` rc=0, clean.
- Carry accounting: the body's Carry 1 and Carry 2 are one text twice (R10-DEPENDABOT-3414-COMPAT roster indexes); both built in this diff (reworded comments, dependabot.yml sentence, entities.py check), nothing left open. Red checks: none owed; Forward-carry: none; the packet's carry_audit reports 0 findings.
- tests/closure.py INERT_EXCEPT + closures.json add only the harness to the tests/entities.py closure; an edit to it now selects the check (the packet's figure_lint resolved 10 of 10).
- Not re-derived: the body's PyPI/pip hash claims for the bot head (that is part 1, merged); the 9-of-9 / 0-of-61 census is the RCA's and I only re-ran its --tree reader. The body's NULL/REEXPOSE_ASTRAL mutant_run log is the fixer's; I reran the astral mutant by hand as above.
- CI: see the line below.
- CI at 09:14 UTC, after about 30 min of `merge_train.py classify` polling: still WAIT (exit 3). Not yet concluded: codeql / Analyze (python), tests / coverage-ratchet, tests / fast (3.14), gate. The only red, `tests / nightly-status`, is outside `owed-reds`, so it is neither answered nor a block. Everything concluded so far at this head is green or skipped. The merge verdict is conditional on those four going green (hence `pending-ci:`).
- Class rule: the harness's `--tree` over every tracked `tests/requirements*.txt` (files=5) returns exposed=0 at the head, so no seam is left open; the body names this rule.

## Findings

none
