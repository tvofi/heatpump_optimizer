Fix review: blocked 6517b1f443af372887dbadd49919a2ab605b66fe ci-red: the only red is gate job 128886760057, an edit-run deferral to code run 42531090110 that nothing re-ran; re-run it, no code change owed

bus-nonce: 3476f5c990cf0cf6f0cca43a1e1923fe

## Block

`merge_train.py classify 6517b1f443af372887dbadd49919a2ab605b66fe --pr 3291` exits 1: `RED ... pending: none red: gate`. It was read twice, the second time at 2026-11-09T00:16:32Z (`ev/ci-classify.txt`, `ev/ci-classify-final.txt`).

- The red is `gate` job 128886760057 in edit run 42531089374. Its log reads only `FAIL run(s) [42531090110] at this head are still being judged; their gate decides`, then exit 1 (`ev/gate-128886760057.txt`).
- Code run 42531090110's own `gate` (job 128906640377) concluded `success` at 00:03:26Z, and a later `gate` (job 128907261693, run 42533451337) also concluded `success`.
- `latest_runs` keeps the worst `gate` across check suites by design (A5), so the deferred red stands until that job is re-run. The body itself says `gate-sweep.yml` is disabled. Carry: dismissed: evidence, not a finding
- The remedy is the orchestrator's: re-run job 128886760057. It should now pass because its deciding run has finished, and it needs no code or body change. Under fix-review step 12 a red CI never carries.
- Everything below was measured at this head and holds if the re-run goes green, with one exception: the `## Findings` items for the next repair round, none of which blocks.

This is review round 6: the verdict after repair round 5. From the fourth round `fixer.md` owes a re-cut, but this block owes none, because it is CI-only. Round 5 was blocked `ci-red` on the same deferral shape.

## Findings

- Follow-up: two of the four sub-cases in `tests/wood_advisor.py`'s edge check, "the derate reads only what the plan publishes", are vacuous. The sub-cases are the non-finite space draw and the tail past the plan's schedules.
  - Mutant M8, `finite_float(p, 0.0)` replaced by `float(p or 0.0)` so NaN reaches `partload_factor`, survives: wood_advisor 25/25 and features 31/31 pass. A NaN draw gives a NaN COP (`ev/partload_values.txt`), and that step reads "not cheaper", which is the same 0 the check expects.
  - Mutant M7, the `+ cops[len(partload):]` tail dropped, also survives. The tail steps sit at factor 1 and price 0.95 below wood's 1.0, so the expected `_N - 6` holds either way.
  - Neither line is a fix line the body names. M1 to M6 all fail as the body's table states (`ev/mutants.txt`).
  - The owed change: price the edge cases so the NaN-as-0 reading and the kept tail each flip the count, then re-run M7 and M8. Carry: R10-PARTLOAD-RESIDUE
- Follow-up: some figures the body says hold at this head unchanged ("none was re-taken") do not reproduce at this head.
  - `r10_partload_pricing.py`, spread d=0.112: `terminal-at-max max 3.746973`. The body says 3.723135.
  - The same harness, flat d=0.112: `deferred-at-max max 2.140129`. The body says 2.139841.
  - `r10_partload_residue.py refill`, `predicted max`: 33.5092 (spread) and 62.9187 (flat). The body says 33.6792 and 64.5737.
  - Every other figure from those two harnesses reproduces digit for digit, including the flat 4.368455 the materiality call rests on (`ev/pricing-head.txt`, `ev/refill-head.txt`).
  - The roster carry to R10-SAV-COMFORT quotes 2.139841, but it also orders a re-measure at that stage's merge base, so the stale digit does not propagate as a fact.
  - The next repair round re-takes these figures at its head and corrects `## Figures`. Carry: R10-PARTLOAD-RESIDUE
- Follow-up: the structure-ratchet payment is a reformat, and a physical-line metric rewards it. `max_class_loc` and `class_excess_loc` drop by 1 because `_wear_price`'s three-line `int(...)` is joined onto one line, which pays for the one added `partload_at=partload_factor` line.
  - Planting the same join elsewhere with nothing improved would move the same counters by the same amount.
  - The joined form is the sounder spelling, and no budget rises, so this is not `metric-gamed` against this diff. It is an instrument property. Carry: dismissed: a physical-line counter's known reformat sensitivity; the change is sound and lowers no bar
- Follow-up: this is the second consecutive round blocked on a stale edit-run gate deferral with `gate-sweep.yml` disabled. The class is held by the group the body names. Carry: R10-HOTFIX-TRAIN-DEFER-WAIT

## Evidence

- Head: `6517b1f443af372887dbadd49919a2ab605b66fe` (`ev/HEAD.txt`). It was still the PR head when re-read before this return (`ev/head-at-post.txt`).
  - Its tree equals that of 5e21a591e, the head the body's `## Head` describes (`git diff --quiet`, `ev/head-identity.txt`). 6517b1f is a merge of 5e21a591e into 5fca8c70 that adds no patch.
- Contract currency: the role pack was rendered from origin/main 19865e5a8. The merge base's `fix-review.md` differs from main's only in step 13's wording on conflicts, and this review followed main's.
- Merge: `git merge-tree --write-tree origin/main 6517b1f4...` exit 0, tree 8731d2250, origin/main 19865e5a8 (`ev/merge-tree.txt`). No conflict, and no claim-file driver was invoked.
- Version and golden fixtures: the three-dot diff from merge base 51cd5ec8a touches no `VERSION`, manifest, `RELEASE_NOTES.md` or `tests/golden/` path. `pr-contract` prints `no version edit`. No claim file moved, so step 4 has nothing to compare.
- Mutation proof (step 1), at the head worktree. Baseline: wood_advisor 25/25 and features wood block 31/31 (`ev/baseline.txt`). Outputs are in `ev/mutants.txt`.
  - M1, coordinator `partload_at` dropped: features check fails.
  - M2, guard `if True:`: three wood_advisor checks and the features check fail.
  - M3, `c` for `c * f`: the same four fail.
  - M4, night scan always COP 3: the night-advice check fails.
  - M6, hot-water draw dropped: three wood_advisor checks fail.
  - M7 and M8 survive (`## Findings`).
- Finder's harness, both ends (step 2). `r10_partload_residue.py refill`, sha1 fc617bd018a3 (matches the body), with `taskset` and single-thread BLAS.
  - At the head: production `count residual max 0, night picks off 0` on all four rows, `null rows not zero 0`, `positive (d>0) price days with a zero maximum 0`, `failures 0`, rc 0.
  - At merge base 51cd5ec8a with the harness copied in: `count residual max 19, night picks off 67` (spread d=0.112) and `count residual max 58, night picks off 560` (flat d=0.112), 0 at d=0.0, rc 0 (`ev/refill-base.txt`). The defect reads at the base and is gone at the head.
- Null control (step 3): the d=0 rows read 0.000000 everywhere at both ends. `r10_partload_pricing.py` prints `null rows not zero 0`, `failures 0`, rc 0.
- Figures: `structure.py` prints `STRUCTURE RATCHET PASSED` at the head. `score.py --diff 51cd5ec8a HEAD` prints `Architecture score: dS +0.0000 NULL` (`ev/archscore.txt`).
  - The CPU figures for carries 1 and 3 (`relaxed`, `buffer 20`) were not re-run: they are host-timing figures whose refusals stand below a 306x margin. Not verified by this seat.
  - The Geekbench ratio 6.8 is cited from external pages and was not re-derived.
- Forward-carry (step 10): the R10-SAV-COMFORT text is in `dev/programme/rosters/wave-r10-groups.json` at `handoff/audit-r10-roster` 4a71f977d (`ev/roster-carry-sav-comfort.txt`), and it states the zero-derate control as a precondition. It is not at the body-named 03c1c6c46, which predates the append the body says was queued.
- Red checks (step 11): at this head the one concluded non-success is `gate` 128886760057 (22:44:47Z).
  - `pr-contract` runs started after it (128907263260 at 23:07Z and 128906357447 at 00:01Z) both concluded `success`. Their logs print an empty `red checks the body must answer:` and `record red-history ... arch-score / arch-score, tests / arch-instrument, tests / mutation`. The body answers all three under `## Red checks` (`ev/pr-contract-*.log`).
  - The root-cause trigger is therefore answered. The block is the gate's own state, not an unanswered trigger.
- `tests / mutation` concluded `success` at this head. The diff writes production lines, so it drew mutants, and the two ledger pins in the diff are the sites `mutation-autofix` recorded.
