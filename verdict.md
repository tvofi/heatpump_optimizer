Fix review: blocked 67be951d3980dcfa9a2c5ce8b099f9239f3db904 instrument-broken: the round-1 block stands, dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py is unchanged and still broken at this head (M0-null fails on 3.14, five mutant sites gone) and the body neither fixes nor dispositions it

bus-nonce: aafc24ba6f48aa002f9ba4ece002a69a

## Round

Round 2 (round 1 blocked ac7353951f00 with the same class). fixer.md owes a repair now; a re-cut only from round 4.

## Block

The committed finder's mutation harness for the code this PR edits, `dev/audit/harnesses/r10_nightly_pyspy_retry_mutants.py`, is not touched by the PR (`git diff e5ddba1fa..67be951d3980dcfa9a2c5ce8b099f9239f3db904` on it is empty) and still breaks at this head:

- Under CPython 3.14.6 (CI's interpreter, the arm the fix targets), `M0-null FAILS: (block did not run ... NameError: name 'subprocess' is not defined)`: the entities block it extracts (from `_HB_BOTH = ` to `_hb_cmd = `) now contains the PR's `_hb_stdlib_reads`, which uses `subprocess`/`_io` that the harness's HEADER does not import. Then it aborts: `M2-timeout-30: the mutated site occurs 0 times, not once`, rc=1. (ev/pyspy_retry_mutants_head.py314.txt)
- Under 3.13, M0-null passes, M1 is killed, then the same abort at M2, rc=1. (ev/pyspy_retry_mutants_head.py313.txt)
- Mutant sites at head vs base: M2, M6, M9, X2, X5 occur 0 times at head, 1 at base (the PR renamed `spy_timeout`, `PY_SPY_TIMEOUT_S`, `py-spy rc=0:`). (ev/mutant_sites.txt)
- At the base the same harness passes M0-null and kills M1..M4 so far, M2 included (ev/pyspy_retry_mutants_base.py313.txt, partial: this seat cut the base run at 230 s, after M4).

The brief names 2f033a59af4f as the fixer's answer. It is not: it was committed 2026-10-29T20:01Z, before the round-1 verdict (20:36Z), and it changes only the new harness `r10_fly_nightly_hb.py` (adds `--inproc`). The PR body does not mention the round-1 block at all. Owed: update the old harness's MUTANTS sites and HEADER imports to the renamed code (or disposition it explicitly in the body), then show M0-null passing and every mutant killed at the head, on 3.14.

## Findings

- PR body's `## Head` section is stale and self-contradictory: it names 67be951d3980dcfa9a2c5ce8b099f9239f3db904 but also `877f4addb` as the head and merge base `486e65cbd9` (the merge base is e5ddba1fa), and the scoped-gate figure was taken against 486e65. Must describe the new head at the next push. Carry: R10-FLY-NIGHTLY-HB | dismissed: owed by the fixer in this PR's next round, not a later stage

## Evidence

- Head reviewed: 67be951d3980dcfa9a2c5ce8b099f9239f3db904 (ev/HEAD.txt); still the branch head at write time (ev/head-at-post.txt).
- `git merge-tree --write-tree origin/main 67be951d3980dcfa9a2c5ce8b099f9239f3db904`: rc=0, no conflict; origin/main = e5ddba1fa = PR base (ev/merge-tree.txt).
- VERSION, manifest, RELEASE_NOTES.md, tests/golden: untouched.
- CI on this head (ev/check-runs.txt, read live): `tests / nightly-status` failure — main-graded, answered in the body's Red checks section, not this PR's; `tests / nightly-ha (stable)` and `(2025.2.0)` success; `tests / mutation` success; `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `governance / env-matrix`, `governance / instrument-self-tests`, `codeql / Analyze (python)` still in progress at review time — not re-derived.
- The container figures (base probe 59/60, side 30/30, N1–N3) need the HA image and Docker; not re-run in this seat, not verified. The new harness's `--inproc` mode was not exercised because the block above is decisive.
- Mutation proof of the fix's own predicate (sample_command) not re-run this round; the block is on the instrument.
- Review packet: ev/review-packet.md (carry_audit 2 routed, figure_lint 12 resolved).
