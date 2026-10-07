Fix review: blocked e4c51f12ea5f34311ffa0eb0d9c86e0d3e348974 root-cause-unanswered: closures went red, unanswered
bus-nonce: 8fcfa873d7a463776b11b49d603d9458

Delta review 29751f36..e4c51f12 of PR #2007, round: delta after a merge verdict. Head read live at posting: e4c51f12 (matches the body's Head section).

RESULT code-delta: the PR's own production change since 29751f36 is cfab03d6, which extracts `_service` out of `pump_arbiter._write` (the #2008 merge took `_write` to cyclomatic 17; now 14, `_service` 5, no budget re-recorded). The rest of the 29751f36..e4c51f12 range is main merges. `merge-tree --write-tree origin/main e4c51f12` exits 0. The refactor is behaviour-equivalent for the mode, silent, night-key and set-point branches; the only change is that `_option_for(...)` and `int(value)` now evaluate before the `try`, so an exception there would no longer be logged-and-retried. `_option_for` cannot raise (getattr/.get/generator), and the night values are set from ints, so this is a note, not a block. `f06eea5d` adds `_service_dispatch_pins` to guard_pins and 44cef3ab/ebbdacaa/9e410efd re-anchor the ledger to `_service`. Claim files, VERSION, the manifest version and the notes heading are untouched; `pr-contract`'s version-edit step prints "no version edit".
RESULT earlier-verdict: the 29751f36 merge verdict on the silent-slot fix stands on its own terms (the slot, the mutation proof and the unpinned count are unchanged by the delta). CI at the head: mutation success, typing success, env-matrix success, coverage success, fast (3.14) success, hassfest success.

BLOCK (step 11). Check-runs API at e4c51f12, read here, shows these gate checks red:
- `closures` (job 112866129364): `INERT READS UNDER-APPROXIMATED ... tests/harness_headers.py: tools/audit/harnesses/eg_b7_seam_hubs.py`. The cause is main's, not this diff's: the PR leaves tests/closures.json untouched, and main's 60c00052 ("record eg_b7_seam_hubs.py's inert read at the path it now has") is on origin/main but NOT in this head (git merge-base --is-ancestor 60c00052 e4c51f12 fails).
- `closures-autofix` (job 112886615096): "The closures job's check failed, and not on UNDER-SCOPED" -- not repaired by the bot.
- `pr-contract` (the later run, job 112896891460): exactly these two, "check `closures` is red and `## Red checks` does not name it" and the same for `closures-autofix`. The body's `## Red checks` names typing, mutation, mutation-autofix, env-matrix, pr-contract, nightly-status and delivery-status, and nothing on closures.
Also cancelled: `budget-raise-gate` (one run cancelled, its twin succeeded); `nightly-status` and `delivery-status` grade main and are not this PR's, as the body says.

Required before re-review: either merge current origin/main (which carries 60c00052) so `closures` and `closures-autofix` go green on the new head, or keep this head, and in both cases add `closures` and `closures-autofix` to `## Red checks` with the answer (cheaper detector and standing cost, or none), then refresh the body's Head section to the new head. The body should also say that the reds on the previous head (typing, mutation, env-matrix) are now green at e4c51f12, since the section describes a head that has moved.

Nothing else in the delta blocks.
