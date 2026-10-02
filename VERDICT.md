Fix review: merge 1517fa2d6363cba80335a1db35623682aad177e4

bus-nonce: 2efcb41abffaca931a431197ed524bb1

This is round 3; round 2 blocked f6af0c50. The verdict is merge, with `policy-docs` red as ruled. tvofi ruled on 2026-10-02 that `policy-docs` is the accepted bootstrap red on #1847, and the orchestrator merges past it with `--admin` under the mandate.

Measured head: 1517fa2d6363cba80335a1db35623682aad177e4. I re-read the live head before posting and it was unchanged. Main at measurement: aab94eea. The contract diff for `tools/audit/briefs/` (merge-base...origin/main) is empty. `git merge-tree --write-tree origin/main 1517fa2d` exits 0 with no conflict.

## The guard does not skip once main carries the lane (perturbed)

`sim.sh` runs the step's own shell, extracted verbatim from `governance.yml` into `guard_step.sh`, over trees restored as CI restores them.

| base (PINNED) | tree | guard step |
|---|---|---|
| main aab94eea (no lane) | unmutated | `skipped` with its reason printed, rc 0 |
| main + precursor (B1 50eb8064, no lane) | unmutated | `skipped`, rc 0 |
| the PR merged (M2 c376da5c, carries the lane) | unmutated | runs: `RESULT divergent=0 ... refused=0`, `AGREEMENT ok`, rc 0 |
| M2 | `CLASS_GUESS` grammar mutant | runs: `divergent=15`, `AGREEMENT REFUSED`, rc 1 |
| main aab94eea | same mutant | `skipped`, rc 0. This is the bootstrap window and nothing else. |

The guard keys only on `$PINNED:.claude/workflows/agreement.mjs`. `PINNED` comes from the event's base sha, not from the PR's tree, so a PR cannot make the lane skip once main carries it. On a push to main, `PINNED` is `github.sha`, so the lane runs on the merge commit itself. The `--self-test` step runs unconditionally, and at this head CI printed `SELF-TEST 13 of 13`. One limit remains: if `cat-file` fails for a reason other than absence, the step skips rather than fails. The restore step fetches `PINNED` first, so I judge that residual and not blocking.

## The precursor pieces (07b0704b on af7660c7), with my mutants at this head (`precursor_mutants.sh`)

| mutant | detector |
|---|---|
| null (unmutated) | `policy_lint.mjs` rc 0; `check-wave-script` 153 passed, 0 failed |
| P1: `resolvePrFromCommit` loses `\|\| MERGE_SUBJECT_RE` (D13-s1-01 back) | `policy_lint.mjs` `FIXTURE VACUOUS ... squash-shape subject`, rc 1 |
| P2: `rulePaths` dropped from the export | `check-wave-script` group 15: `FAIL rulePaths is exported` |
| P3: `rulePaths` returns `[]` | `FAIL and reads the same declared path globs as parseRuleFrontmatter`, 152 passed, 1 failed |

Both pins compare against an independent reader: `parseRuleFrontmatter`, and the shapes that stamp.py and delivery_status.py read. Neither re-implements the formula under test. `git status` was clean after each mutant.

## The round-1 and round-2 items at this head

- codeowners_gap: `RESULT uncovered_files=0`.
- Unpinned lane: six pairs, `RESULT divergent=0 unregistered=0 dead=0 refused=0`.
- Field coverage on the PR's own copy: `refused=0`.
- My four instance mutants (`mutants.sh`), lane divergent counts:
  - D14-s2-03: 15
  - D13-s1-01: 1
  - D11-s1-72: 4
  - D7-s3-02 (`dead = []`): 1

## Red checks: the body answers each one, and I checked each against this head's CI

This head's check-runs are in `checks_final.tsv`, read from the commit's `check-runs` API by a background watch until every run completed.

- **`policy-docs` failure.** The log's only error is base-pinned `field_coverage.mjs` with `REFUSED registry: pinned agreement.mjs / agreement_py.py / tests/structure.py`, `refused=3`. It is the job's last step, so no later step is masked. Its `policy_lint.mjs` step passed. The body's speculation that live-ruleset drift might also turn `policy-docs` red did not happen at this head.
- **`wave-script` success.** `check-wave-script` printed 151 passed, 0 failed. The agreement step printed its skip, and the self-test held 13 of 13.
- **`pr-contract` success**, on the body that names the three reds of f6af0c50 (`wave-script`, `policy-docs`, `pr-contract`) with their causes.
- **`budget-raise-gate` and `pr-contract` each have one cancelled run**, superseded by a later run of the same name that succeeded.
- Every other completed check passed or was skipped. That includes `fast (3.14)`, which carries `tests/entities.py` and `tests/harness_headers.py`, the two scripts this Mac cannot run without numpy.

## After the precursor merges, only policy-docs stays red

I simulated it: B1 is main plus 07b0704b (merge-tree rc 0), with this head merged onto it (rc 0) and the pinned files restored from B1.

| check | result |
|---|---|
| `check-wave-script` | rc 0 |
| agreement step | skipped, rc 0 |
| lane self-test | rc 0 |
| `policy_lint.mjs` | rc 0 |
| `field_coverage.mjs` | `refused=3`, rc 1 |

So `policy-docs` is the only one of these jobs that stays red. The other governance jobs are not in this diff's reach beyond what this head's CI already ran green.

## Not verified by me

- I did not re-derive the body's step-8 enumerator export figures; `enumerate.py` is outside the tree.
- I did not re-derive the body's D13 figure of 405 divergent; my mutant runs in the other direction and gives 1.

Evidence: `evidence/`. `HEAD.txt` names the head and the simulation commits.
