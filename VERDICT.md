Fix review: merge e1210e0993c9c0a3a3dc7e0a13cbd3d012d2bf49

bus-nonce: dce30a84eb430859b91c1f01973f298d

Measured at e1210e0993c9c0a3a3dc7e0a13cbd3d012d2bf49 in a detached
worktree; merge base d3dbf2c3fc42b87e6aad71d3de0c0885a10c750e. Head
confirmed unchanged by ls-remote immediately before this push.

All five adversarial questions reproduced:

1. Clause TRUE. `.github/workflows/tests.yml` `mutation-autofix` `if:`
   requires `github.event_name == 'pull_request'` (head lines 2646-2650) --
   read myself. The "a DIRTY head queues no run" premise asserts nothing new:
   it is claim-files.md's measured #570 fact, already stated in this same
   rule's last section at the merge base ("CI never runs on a DIRTY pull
   request", base line 88), and it is the premise the owner-ruled live
   merge-main bot (`.github/workflows/merge-main.yml`, tvofi 2026-10-08) is
   built on. Corroborated by that bot's successful runs on every main push.
2. Minimal and in voice. Three-dot diff of `dev/governance/rules/ci-autofix.md`
   is one clause ("-- a `DIRTY` head queues no run, so no bot commit comes")
   plus the named payment (dropping "is conditional:" from the next
   paragraph). `rules_sync.mjs --check` clean at the head; budgets re-measured
   by me at BOTH ends: base 1456/1469, head 1465/1469, claim-files 678/681
   untouched. No budget raised.
3. Shim correct and safe. Head shim resolves `$HPO_STATE_DIR/venv-ci/bin/python3`
   first, the documented default root second, refuses with exit 127 naming
   `tools/audit/seat/seat_venv.sh` when neither holds one; no ambient
   fall-through. Self-test harness is the instrument's own committed one.
   RESULT: head `seat_venv.sh --self-test` = 20 checks, 0 failed.
   RESULT: mutant (both shims restored to the merge base's copy) = 20 checks,
   4 failed, exactly the four arms the body names; restored = 20 checks,
   0 failed; `git status --short` clean.
   RESULT: null control base = `cannot execute: No such file or directory`,
   rc 126, no remedy; head with `HPO_STATE_DIR=/private/tmp/nope` =
   `Python 3.14.7`, rc 0.
   RESULT: `tests/entities.py` through the shim = ALL 2250 ENTITY CHECKS PASSED.
4. Refutation and skip honest. `dev/governance/roles/fixer.md` step 5 (lines
   53-55) names `run_always`; `git log -S run_always` returns exactly one
   commit, a5054a3e6, an ancestor of origin/main, merged in #2059 (merge
   commit d8a4bd36f). claim-files.md `paths:` is `tests/golden/**` alone;
   `.gitattributes` routes `merge=ledgermerge` at lines 22, 23, 24, 29
   (mutation_budgets, structure_budgets, closures, bugclasses) -- all outside
   that glob; `tools/merge/ledger_merge.py:6` and `:426` do name `--resolve`.
   Both reproduce verbatim.
5. Forward-carry: the body names no later stage's brief as destination -- the
   owed seat-install half is explicitly routed to the orchestrator's record
   against #2039, and the section states no stage's inputs move. Consistent
   with the diff (no brief touched); nothing to open, nothing missing.

Contract extras: VERSION, RELEASE_NOTES.md and the manifest untouched;
claim files byte-identical across the three-dot diff; check-runs read from
the API at e1210e099 (42 runs, zero failures -- only skips/successes; the
cancelled `Analyze (python)` CodeQL lane at the authored head a6fee4f29 is
not a gate check); delivery row `dev/programme/delivery/2121.md` present.
`budget-raise-gate` is green at this head; no raise is claimed and none is
needed (1456 -> 1465 inside the standing 1469 cap) -- noted, not judged here.

This is review round 1.
