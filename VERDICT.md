Fix review: blocked 0135f1ac582481049672becfe48fdaa5702397a2 ci-red: fast (3.14) is main's own red (8fa06663c fails the same always() check); mutation refuses the 5 unpinned sites this diff adds, which mutation-autofix could not pin because that red left the baseline inconclusive

bus-nonce: 241d230e3b3b1af4d2a69bece889303f

Round 3. PR #1852 (R9-EG-B3a, Part of #1737). Measured head `0135f1ac582481049672becfe48fdaa5702397a2` (code `02603da35d0871c53d790b47ac5b4d7bdaf2a9b1`). The live head was re-read when this verdict was posted and had not moved. The evidence directory names the head. Round 3 changed no production code (`git diff 684b5a1e3 02603da35 -- custom_components` is empty), so the round-2 contract results (census, probe, EG-B3, goldens) carry over unchanged.

**The fixer's work is complete. Nothing in the PR is wrong.** The block is two red gate checks. The first is main's. The second follows from it, and the PR cannot clear it until main is green.

## Items owed from round 2: all delivered

1. **`payload.py` classified.** It is now listed in the 17 closures CI's Linux recording names, and the hand merge adds exactly those 17 lines and nothing else. **CI's `closures` check at this head: success**, so the hand merge is accepted. `closures-autofix`: skipped (nothing to repair). `closure-scope`: success.
2. **`docs/architecture.md`.** Now 68 modules (25 importing Home Assistant at module level, 42 free of it) and `payload.py` is in the module map. The `D6/claims.py` header and its committed output say 68, and the `deployment_shape.py` cost note is re-derived. At this head, CI's `entities.py` and `harness_headers.py` no longer print any of the round-2 failures.
3. **qs_rules.** The harness pattern changed to a prefix; the class line did not. I ran it: `RESULT declared_mismatch=0` at the head. Null control: with the entity base swapped to `Entity`, it reads `declared_mismatch=1` (`executed:todo/declared:done`). See `evidence/qs_rules_r3.out`.
4. **Mutation pin.** The stale `_data RETURN_DEL 35920c59` pin is removed. The body says the ledger normalises with no other file moved. CI's mutation table now reports that "the ledger agrees with the deterministic inventory", so the round-2 refusal is gone.
5. **Root cause in the body.** Every round-2 red is named and answered. The cause given is that derived figures were not updated. The process state given is (c). The body names a cheaper detector: `entities.py`, `harness_headers.py` and `deployment_shape.py` run locally in about 5 minutes with an existing venv. The countermeasure proposed is a change to SEAT-BLOCK.md, which is the orchestrator's to make, with a cost test. This answers the red-check trigger.

## Red at this head (check-runs API, `evidence/check_runs_r3.tsv`; logs in `evidence/ci/`)

- **`fast (3.14)`: `tests/entities.py` fails 1 of 2074 checks**, "no job-level `if` leads with `always()`: a cancelled run stops (CI cancel)", naming `tests.yml:mutation-ledger` and `tests.yml:mutation-ledger-push`. **This is main's red, not this PR's.** The PR does not touch `.github/`. On main, `f268e3ab2` (#1848) added those two jobs with a job-level `always()`, and `179a8c2a4` added the check that forbids that. Main's own head `8fa06663c` fails `fast (3.14)` on the same single check, 1 of 2071 (`evidence/ci/main_fast.log`, `evidence/main_8fa06663_check_runs.tsv`). The PR's check run shows it because CI tests the merge with current main.
- **`mutation`: `MUTATION TABLE REFUSED`, 3913 unpinned sites against 3909 at base `8fa06663c`, 5 of them added by this diff.** The 5 are all this PR's lines: `binary_sensor.py:222` GUARD_OFF, `coordinator.py:7616` RETURN_DEL (`return cast(Payload, data)`), `entity.py:30` GUARD_OFF (`if TYPE_CHECKING`), `entity.py:197` RETURN_DEL (`_data`), and `sensor.py:2898` RETURN_DEL (`_advice`). The pin-killed pass in the same job printed `MUTATION TABLE INCONCLUSIVE`, because the baseline is already red in `tests/entities.py`. That is main's red above: the long list of `a3:`/`a4:` lines it prints is the negative controls inside entities.py, and the one real failure is the `always()` check. So no mutant was measured.
- **`mutation-autofix`: `skip-measure-failed`, "THE REPAIR DID NOT HAPPEN"** (0 anchors). It follows directly from the red above.

**What clears it:**
1. Main fixes its `tests.yml` `always()` conflict, between #1848 and #1854's check. That is outside this PR.
2. This PR merges main in. `mutation-autofix` then pins the 5 sites on Linux. If it does not, run `tests/mutation_table.py --pin-killed --base origin/main` on Linux.
3. The body names the new head's reds, and only if any remain. A fast red that is still main's carries the `check-main-before-your-diff` answer.

I expect no code change from the fixer. That new head is a main-merge plus a pin commit. Under `fix-review.md` step 12, a main merge comes back to me as its resolution delta.

## Recorded as asked

- **The previous head's Tests run** (29b763d7, run 37026062126) shows **completed / failure, attempt 1, updated 2026-10-02T16:16:10Z. It is not cancelled.** It ran to completion before #1854 merged (`evidence/prior_head_tests_run.tsv`).
- At this head, `pr-contract` has one `cancelled` run (superseded) and one `success`. `typing`, `coverage`, `coverage-ratchet`, `browser`, `briefs` and `nightly-status`: success.
- This is round 3. Under the three-round rule a fourth round owes a re-cut body. The block here is not a defect in the body or the code, so whether that rule applies is the orchestrator's call.
