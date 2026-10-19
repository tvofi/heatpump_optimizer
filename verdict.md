Fix review: blocked 4c9dc5d92fade9e622fa56a86fd07e8ca98d60b1 contract: pr-contract red at this head, carry_audit.py refuses 3 unrouted body items (## Forward-carry "none" line and both ## Friction lines end `Carry: <file path>`, not GROUP|#issue|O<n>|dismissed); ## Red checks says none

bus-nonce: 8bdd00fe42dfc236cb21766248fa7b8d

Round 1 (no earlier `Fix review:` comment on #2448). Measured head 4c9dc5d92fade9e622fa56a86fd07e8ca98d60b1 (ev/HEAD), still the branch tip at write time. Roles contract current (`git diff mb...origin/main -- dev/governance/roles/` empty).

## Blocker (body only; the code passes every check below)
- `pr-contract` is red on this head (jobs 118057609688, 118057416570): `CARRY-AUDIT: 3 finding item(s): 0 routed, 3 unrouted` (ev/ci.txt). The two Friction lines name files (`dev/programme/rosters/wave-r10-groups.json`, `dev/governance/roles/orchestrator.md`) where `finding-propagation.md` requires `Carry: <GROUP>|#<issue>|O<n>|dismissed: <reason>`; the Forward-carry "none" line carries no marker. Fix: re-route the three lines in the body (e.g. `Carry: R10-DEAD-RATE-LIMIT` only if a roster write landed, else a real destination or `dismissed: <reason>`), and let a fresh pr-contract run check it. `## Red checks: none` is also stale now that checks ran; it must answer pr-contract (step 11) once the head's workflows conclude. nightly-status red is not this PR's. Remaining jobs (mutation, fast, typing, coverage, env-matrix, policy-docs, instrument-self-tests, browser) were in progress at read; not cited as passed.

## RESULT lines (reviewer-run)
Harness: dev/audit/harnesses/r10_dead_rate_limit.py, sha1 99b702cb6ed433e9531307f710e49299c6dc4b3c (the fixer's, disclosed as new; the finding had no committed harness — the roster records "the orchestrator's recorded finding" — so this is step 9's finding, disclosed). Same file run against base 90557e39e, mb 05c39d3a6, head (ev/harness.txt):
- shipped: binds=0/181440 at base, mb, head; max_moved_fraction 0.0333 base, 0.0100 mb/head; digest 3187402b… at mb = head (bit-identical step), 0cd34c4c… base. All as body.
- --alpha 1.0: binds=173200 at all three; digest aab10749… mb vs f114d100… head. As body.
- --current-min 0.05 --current-max 0.2: binds=156444 base, 0 mb, 0 head. As body.
- --limit 0.005: binds=158586 mb/head; digest 52a4b217… mb vs 3187402b… head. As body. (base: 99336, not quoted.)
Finder's harnesses at both ends (ev/finder_harness.txt): reparam_sites RESULT sha1 89dcd7a6ebbd… mb = head; newton_bias none 0.0034 / asym 0.4731 at both, rc 0 on Linux. r10_trust_relative_bundle.py not re-run (synthetic bundle, not reproducible from the body without its JSON) — not verified.

## Mutation proof (ev/mutants.txt)
M2, M3 reproduce the body exactly; unmutated passes. Reviewer's own: a clip at 0.0099 (just under alpha*trust_region) and a 1e-4 EWMA perturbation both fail 2 of 7. Body's M1 (clip at 0.05 passes) is the finding, accepted.

## Other steps
- merge-tree origin/main 4c9dc5d92: rc 0, tree e27f989f… (no conflict, claimnotes driver not needed).
- VERSION / manifest untouched; notes heading untouched (prepr --version-edit in CI: none).
- env_drift --claims-only: ok; no claim file touched, production step bit-identical so no golden can move.
- structure.py at head: STRUCTURE RATCHET PASSED; class_excess_loc/max_class_loc -1 earned by deleting the two `max_step_fraction=` call-site lines (net -1 in the class: +1 docstring, -2 kwargs). Not gamed.
- Class (step 6): rule 2 `git grep MAX_STEP|max_step` returns HOUSE_LOSS_MAX_STEP (re-anchor gate, kept, documented) and COP_LEARNING_MAX_STEP: read `_fold_measured_cop`, no trust region precedes its clip, so not the dominated shape — body's disposition holds. Rule 1 re-run not separately reproduced beyond reading the remaining clip.
- `git grep -ln max_step_fraction` at head: only the new harness and the roster. Four callers updated as body says.
- Forward-carry: body says none; acceptable on substance, but unrouted (blocker above).
- Architecture: added lines are deletions plus docstrings; no breach.
- Full tests/features.py: not cited (CI's heavy run; local run still going at write time).
