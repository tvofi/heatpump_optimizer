Fix review: merge 67c7fdf39849f8b51222004e84812ec5bd2807de

bus-nonce: 11577e9ed0f82f862d280f77684a61b0

Round: 2. Round 1 blocked 9328902 as mutation-vacuous (the `covered` deletion guard). Measured head: 67c7fdf39849f8b51222004e84812ec5bd2807de, which was still the PR head when I last read it before writing this.

## Findings

- The level's `merged-pr` close looks up the tip's commit time with `ct.get(code.get(t, sha))`. My mutant `merged_ct_any_ref` changes that to `ct.get(sha)`, and every owner self-test stays green. I judge this an equivalent mutant, not a gap:
  - A body ref whose topic has a code ref is handled earlier, by `body-follows-code`.
  - For every other ref, `code.get(t, sha)` equals `sha`.
  - So nothing to pin. Carry: dismissed: equivalent mutant, no input reaches a difference.
- `bus.sh orphans` reads only git refs and holds no PR listing. So a merged handoff whose files main has since moved on from still reads ORPHAN there (re-measured below: MISREAD 3 at main 57f0c9c77, 4 at main b6f6ceca4). The relay's level closes all of them. The body declares this residual and carries it. Carry: R10-FLY-ORPHANS-REWRITTEN | #2721
- `dev/audit/harnesses/r10_fly_orphans_landed.sh` is the fixer's own instrument. Issue #2721 names no committed finder's harness. The body now discloses this (round 1 finding 4, step 9). I measured with this harness because no finder's harness exists. Carry: R10-FLY-ORPHANS-REWRITTEN | #2721

## Evidence

- Roles current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.
- The packet was rendered here (`ev/review-packet.md`). Refusals: none. FIGURES: 15 resolved, 1 not verified (a bare `python3`), 0 refused.
- Round 1's block is settled at this head. The mutation table (`ev/mutants-table.txt`) reads `plants: 48, without a FAIL line: none`, rc 0, and each new plant fails exactly one check:
  - `L27_deletion_unguarded` rc=1 fails=1
  - `L28_deletion_always_refused` rc=1 fails=1
  - `L29_same_blob_arm_off` rc=1 fails=1
  - `L30_merged_strictly_before` rc=1 fails=1
  - `L31_merged_last_listed` rc=1 fails=1
  - `B3_orphans_classifier_unchecked` rc=1 fails=1
- `--null` gives rc=0 fails=0 for each of bus.sh, cloud_relay.sh, ledger.py and orchestrator_tick.py (`ev/mutants-null.txt`).
- My own mutants are re-spellings of round 1's survivors and of new lines (`ev/reviewer-mutants.txt`). 11 were killed:
  - `D_guard_inverted_rc` (`rc_m != 0`)
  - `merged_min`
  - `no_by_line_true`
  - `bare_topic_dropped`
  - `escalate_body_ignored`
  - `bref_dropped`
  - `level_heads_dropped`, killed by the relay
  - `reverse_flag_dropped`
  - `bus_content_as_ancestor`
  - `relay_merged_awk_nf`
  - `moved_blob_any`
- Of the other two: `merged_ct_any_ref` survived, as an equivalent mutant (see Findings). `cli_no_content_ignored` did not apply because my anchor matched nothing; the existing bus check `--no-content reads the same ref as stranded` exercises that flag.
- Self-tests at the head (`ev/selftests-head.txt`):
  - bus 98/0
  - ledger 77/0
  - cloud_relay 283/0
  - orchestrator_tick 215/0
  - r10_ledger_mutants --self-test 135/0
- These match the body. The body's relay figure of 279 is for the code head b082a93e7. I measured 279/0 there (`ev/relay-count-code.txt`); the +4 come from main's merge, as in round 1.
- Harness at both ends (`ev/harness.txt`; checkout base = b6f6ceca4, head = 67c7fdf39):
  - main 57f0c9c77, base: MISREAD 5, LEVEL-MISREAD 5, LEVEL-LINES 12 for 7 topics.
  - main 57f0c9c77, head: MISREAD 3, LEVEL-MISREAD 0, LEVEL-LINES 1, `body-follows-code=7 carried=1 merged-pr=5 owed=1`.
  - main b6f6ceca4, base: MISREAD 6, LEVEL-MISREAD 5.
  - main b6f6ceca4, head: MISREAD 4, LEVEL-MISREAD 0.
  - The null case is ORPHAN/owed in all four runs.
  - These match every figure in the body. Its baseline was 0b8f8b585, with the same classifier code.
- Head and merges: 67c7fdf39 merges b6f6ceca4 (main) into 69c4e7fd6, and 69c4e7fd6 merges b082a93e7 into round 1's head 9328902. Both merges have an empty `diff-tree --cc`, so neither carries a resolution of its own (`ev/merge-resolutions.txt`). The three-dot diff equals the authored code head's diff plus the delivery row. The body names b082a93e7 and its merge to this head, so step 7 holds.
- Merge with main: origin/main b6f6ceca4 is an ancestor of the head. `git merge-tree --write-tree origin/main 67c7fdf39` gives rc 0, no conflict (`ev/merge-tree.txt`).
- VERSION, the manifest, the RELEASE_NOTES heading and both claim files are untouched (three-dot, `ev/version-claims.txt`). The diff moves no golden fixture. `env_drift.py --claims-only`: ok.
- Instruments re-run: `tests/structure.py` gives `STRUCTURE RATCHET PASSED`. `archscore --diff` gives `Architecture score: dS +0.0000 NULL`, as the body says. No budget moves (`ev/structure.txt`, `ev/archscore.txt`).
- Class rule: the body's grep returns `def covered` and `def landed`, and `content_superseded` is deleted. The class is this one classifier. prune_refs.py classify() stays dismissed, as in round 1.
- CI on the head (`ev/ci-checkruns.txt`, read after every run had concluded): 55 runs, 38 success, 17 skipped, 0 failed. That includes `gate`, `pr-contract` (both runs), `budget-raise-gate` and `tests / mutation`. The body's `## Red checks: none` holds.
- Forward-carry: none named, and none owed beyond the residual carried above.
- Not re-derived: the failing-test-first counts ("97 checks, 4 failed" on the baseline, and `fails=1` per plant before each arm was added); plants and mutants cover the same direction. The gate's `ALL 2467 ENTITY CHECKS PASSED` and `harness_headers` 112 are cited from CI's green `gate`, not re-run.
