Fix review: merge 1b80732c5534a70ddfe09b324114da1b0dea6873

bus-nonce: a36440a524f675b0fda3f397cfcb03a1

Round 1 (first review; no reviewed head). Measured head 1b80732c5534a70ddfe09b324114da1b0dea6873, which `git ls-remote origin refs/pull/3704/head` still prints at the verdict.

Note: stale-doc: `tools/audit/seat/instruments/regret_oracle.py.md:26-28` says CI runs `--self-test` in `tests.yml`'s `arch-instrument` job; at this head the step is in `governance.yml`'s `instrument-self-tests` (body departure 4 moved it). Paperwork outside `custom_components/`, not a block.
Note: stale-body: the `## Head` section carries a stray bare SHA line (`f4029c34e4...`) and names merge base 2d7161a4b7; the merge base with origin/main at this head is ce382be7054c. The body's figures were taken at the earlier base; those I re-ran (below) reproduce at this head.

## Findings

- The instrument guide's CI location is stale (`regret_oracle.py.md:26-28` names `tests.yml` `arch-instrument`; the step is `governance.yml` `instrument-self-tests`). Carry: dismissed: a one-line correction to this PR's own new guide file, recorded as a Note on this verdict; no later stage's work changes.

## Evidence

- Setup: `cloud-setup.sh --check` OK; role pack rendered; `git diff $(merge-base)...origin/main -- dev/governance/roles/` empty (contract current).
- Mutation proof (step 1), my own driver `ev/mut.py` (reviewer-built, not the fixer's spec) against `python3 -I tools/audit/regret_oracle.py --self-test`, file restored after: KILLED least-inverted, admit-bounds-dropped, admit-terminal-dropped, admit-limits-dropped, greedy-unadmitted, perturbed-unadmitted, regret-sign, greedy-dearest, plant-model-never; SURVIVED null-comment (null control, as it must). Output `ev/mutants.txt`. No survivor on a production line I targeted.
- Self-test at head: `SELF-TEST passed (64 arms)`, 41.9 s wall (`ev/selftest_head.txt`); matches the body's 64 arms.
- Figures re-derived at head (step 8): `grid --jobs 4` -> `RESULT read=regret universe=40 examined=40 value=0.0355`, rc 0, 80.6 s; rows with regret > 0 are exactly `summer_negative/winter_mild` 0.7585, `summer_typical/winter_cold` 0.3781, `summer_typical/winter_mild` 0.2825, by the body's rule (sixth field not `regret=0.0000`) (`ev/grid_head.txt`). `installs` -> `RESULT read=regret-installs universe=1 examined=0 value=NO-READ`, rc 0. `tests/structure.py` -> `STRUCTURE RATCHET PASSED`. Not re-run: the `--plant-error 0.8` planted plane (1.4542), selftest_wiring, codeowners_gap, policy/brief lints, archscore dS; those are cited from the body and CI (`arch-score`, `policy-docs`, `briefs` green).
- Finder's harness (steps 2, 9): none; this PR builds the instrument (design `design/R11-PRE-PRODUCT-READS`). Its harness is its own self-test, built by the fixer, disclosed as the builder's.
- Step 4/5: diff touches no golden fixture, claim file, `VERSION`, manifest or `RELEASE_NOTES.md` (three-dot diff empty on those paths).
- Step 6: one instrument, no production seam; no class rule applies. Step 16: no actuator path.
- Step 14: `tools/ci/selftest_closures.json` grows by the new `regret-oracle` step's read set, earned by the added step; `tests/layout.json` lists the new tool; archscore unaffected (no package file).
- Merge: `git merge-tree --write-tree origin/main 1b80732c...` rc 0, no conflict (`ev/merge_tree.txt`).
- CI: `merge_train.py classify 1b80732c5534a70ddfe09b324114da1b0dea6873 --pr 3704` -> `GREEN 1b80732c5534a70ddfe09b324114da1b0dea6873 pending: none red: none`, rc 0 (`ev/classify.txt`).
- Reds at head: `governance / instrument-self-tests` and `tests / nightly-status` fail; neither is in `merge_train.py owed-reds`. `merge_train.py introduced` -> `introduced: 0 ... head job 133875121461 failure base job 133845667281 failure`: the instrument-self-tests red is inherited from main (its failing lines are `selftest_scope` self-test arms), not this PR's. Unverified: whether the new `regret-oracle` step ran green in that job; the retrievable job log is truncated to its last 5000 lines and holds no line of it. Locally its scope emits `regret-oracle=true` (MODE FULL, a gate file changed) and its self-test passes at head.
- Closing self-audit: `carry_audit.py check` over the body's `## Red checks`, `## Forward-carry` and `## Friction` sections (copied verbatim from the PR body) and this verdict: `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`, rc 0; the packet ran it over the full body with the same result.
