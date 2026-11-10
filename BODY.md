R10-DISPATCH-AT-HANDOFF: a reviewer is dispatched at the handoff, keyed by topic, with the carries the branch already held (bus.sh dispatch-handoff and rekey, open_pr.sh re-key, the relay's held handoff verdict arm, policy text, review_packet refusals). This repair merges origin/main into the handoff, which was DIRTY over one content conflict in tools/audit/seat/review_packet.py.

## Merge resolution only

origin/main (04dfcafccdde1ee5df21a02fe4f06a5bc1083ea0, #3341 f0bfadeb and #3397 04dfcafc merged) was merged into the previous head 4660c050e431dde01c6b4d889f9d6b7572b90166; no other change. The one conflict was dev/governance/roles/fix-review.md; tools/audit/seat/bus.sh and the rest auto-merged.

## Head note

Merge commit 143b44af356932d67056fb3cad88d3244b3fa23c: origin/main into 4660c050e431dde01c6b4d889f9d6b7572b90166. No code of this topic's own changed; the earlier mutation proof concerns cloud_dispatch.py and review_packet.py's own checks, which this merge does not touch.

## Resolution

Conflicting hunk, steps 6-8 of fix-review.md.

Parent 1 (branch, unchanged from base in this hunk except item 7): `is \`blocked <sha> class-open: <seam>\`, a site or a predicate's unguarded domain.` ... `7. Confirm the PR body's head SHA is the head you measured (handoff review: the handoff tip), or \`--carry\`s to it.` ... `8. **A quoted number you cannot re-derive is not verified — say so.**`

Parent 2 (main, #3341): `is \`blocked <sha> class-open: <seams>\`, a site or a predicate's unguarded domain: every one the review found, not one per round, no hunt past it owed. An item whose harness does not move under its own perturbation is void (\`judge.md\`): padding buys nothing.` ... `A rule returning nothing means a one-seam class: say so, never read the absence as compliance.` ... `7. Confirm the head SHA in the PR body is the head you measured, or \`--carry\`s to it.` ... `8. **A quoted number you cannot re-derive is not verified: say so.**`

Union kept: main's item 6 and 8 text whole (the branch changed neither), and the branch's item 7 (handoff-tip clause) in place of main's unchanged item 7. The header sentence dropping "(a script routes on it)" is the branch's and auto-merged. Read back: `grep -n 'handoff tip\|class-open: <seams>' dev/governance/roles/fix-review.md` returns both; no conflict markers remain.

## Head

143b44af356932d67056fb3cad88d3244b3fa23c

## Mutation proof

Unchanged from the earlier body: no production line of this topic changed in the merge. The merged review_packet.py self-test carries this branch's figure-lint, moved-head and P405 head-note checks alongside main's required-reading checks.

## Null control

The unmutated merged tree's self-tests, listed under Figures, each report 0 failed.

## Figures

Taken at 143b44af356932d67056fb3cad88d3244b3fa23c, origin/main 04dfcafccdde1ee5df21a02fe4f06a5bc1083ea0, 2026-11-10 (UTC).

- `python3 tools/audit/seat/review_packet.py --self-test`: 85 checks, 0 failed.
- `bash tools/audit/seat/bus.sh --self-test`: 173 checks, 0 failed.
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)`: MODE: SCOPED, running tests/doc_claims.py and tests/entities.py.
- Scoped gate with PYTHONPATH=tests/hastub: tests/doc_claims.py "ALL 297 checks PASSED"; tests/entities.py "ALL 2707 ENTITY CHECKS PASSED"; the run_always lines tests/env_drift.py --claims-only, tests/closure.py selftest, tests/layout.py and tests/harness_headers.py each rc 0.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- `node tools/policy/policy_lint.mjs --budgets`: rc 0 (no cap over); `node tools/policy/rules_sync.mjs --check`: RULES-SYNC ok.
- `bash tools/pr/prepr.sh` at this head: every step ok or skip except `closures`, which refuses on tests/harness_headers.py UNDER-SCOPED and is left to CI's closures-autofix (`ci-autofix.md`); the same step's `ci predict` reads no closures red predicted. tests/harness_headers.py itself runs rc 0 above.
- `git merge-tree --write-tree origin/main HEAD`: exit 0.

## Red checks

none

## Forward-carry

none

## Friction

none

## Approval

Pending, not granted: this diff touches policy files (dev/governance/roles/standing-dispatch.md and dev/governance/roles/fix-review.md, carried unchanged), which the owner approves by an approving review before merge (CLAUDE.md, policy section). No approval has been given; none is claimed here.

## Carry dispositions

Carried unchanged from the earlier body (the merge adds no carry work; the roster's 1-based numbering).

- Carry 1: untouched here; it stands as the roster states it.
- Carry 2: delivered at main, no re-fix.
- Carry 3: delivered at main, no re-fix.
- Carry 4: delivered at main, no re-fix.
- Carry 5: untouched here; it stands as the roster states it.
- Carry 6: delivered at main, no re-fix.
- Carry 7: superseded by the orchestrator ruling of 2026-11-08 (WAIT dispatches, only RED holds).
- Carry 8: delivered at main, no re-fix.
- Carry 9: untouched here; it stands as the roster states it.
- Carry 10: delivered at main, no re-fix.
- Carry 11: delivered at main, no re-fix.
- Carry 12: untouched here; it stands as the roster states it.
- Carry 13: untouched here; it stands as the roster states it.
- Carry 14: delivered at main, no re-fix.
- Carry 15: delivered at main, no re-fix.
- Carry 16: delivered at main, no re-fix.
- Carry 17: built on this branch (review_packet.py head-note asks policy_lint --pr-body --head).
- Carry 18: built on this branch (REPAIR-OWED on RED; WAIT dispatches).
- Carry 19: untouched here; it stands as the roster states it (it directs carry 12 to be built next, which this branch does not build).
