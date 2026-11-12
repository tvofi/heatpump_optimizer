Fix review: merge 84fe94c780e04d5c0f39434550ef71268b1be19b

bus-nonce: 2133146b78919f853fcb68fdb61a3466

Round 1, handoff review at 84fe94c780e04d5c0f39434550ef71268b1be19b. No review packet and no CI exist yet (pull request not opened); the cheap checks below were run by this seat.

## Findings

- Residual: the body's survivors outside the new block (`desired` rows, `_arbitrate` `_command`) were only partly re-driven here; the full `tests/features.py` run exceeded this seat's bounded wait. Their kill is owed to the pull request's own `mutation` lane. Carry: dismissed: the `mutation` and `fast` required checks run them at the PR, and the body names the killing check per site.

## Evidence

- RESULT head: 84fe94c780e04d5c0f39434550ef71268b1be19b; `git merge-tree --write-tree origin/main` exit 0, no conflict; roles diff against main empty; `VERSION`, manifest, `RELEASE_NOTES.md` and `tests/golden` untouched by the diff; no claim file touched; no Claude trailer in the head commits.
- RESULT block: `features_block.py` with the body's prelude passes (17 of 17) at the head.
- RESULT mutation (own textual edits of pump_arbiter.py, file restored, `cmp` equal): M1 lead call deleted FAILs the cycle, step tick and learner checks; M2 `not on or` dropped FAILs the early cut-off hold check; M3 `or not _pump_off` dropped FAILs the switch-already-on check; M7 `_disinfecting` dropped FAILs the held-disinfection mode check; M8 `await _load(coord)` deleted FAILs "a lead write loads the persisted record". No survivor among the five I drove. M4 to M6 not re-driven; body figures for them not re-derived.
- RESULT structure: `tests/structure.py` passes the ratchet at the head. `tests/entities.py` (env -u BASH_ENV, hastub on the path) ran to completion with no FAIL line.
- RESULT archscore: `score.py --diff <merge-base>` reads dS +0.0000 NULL, as the body says.
- Sibling sites: the body's grep rule re-run; the sites it returns (`_write_supply`, `write_supply`, `supply_tick`'s `wiring.write`, `early_cutoff.py` off-only write) all match the body's table, none missing. The lead's hot-water lease advance in `_step_duty` only sets `dhw_since` earlier by at most a tick: harmless.
- Forward-carry: Carry 0 is present in `dev/programme/rosters/wave-r10-groups.json` on `handoff/audit-r10-roster` (group R10-OUTSIDE-SUPPLY-MIN-RUN-PAUSE, item citing r10-mode-before-supply-on) with its control as a precondition.
- owed-reds set printed: tests / coverage-ratchet, fast (3.14), mutation, typing, validate-hacs. No PR checks exist yet; the body's `## Red checks` is "none", nothing owed.
- Not re-derived: the body's "22 script(s) run, 11 scoped out" scope line and the 14 pinned ledger sites (no full scoped gate or `mutation_table.py` run here; heavy runs are CI's).
