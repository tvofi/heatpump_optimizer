Fix review: blocked 064c5aae08e9c58ff1458978c9d6484aa8527d94 harness: class-open tools/audit/seat/merge_train.py:146,210,237 and .github/workflows/governance.yml:220

bus-nonce: 44baaaafd257f0edb9f1bd9ce7e68570
Reviewer: r9c-rev-2014, round 2. Detached worktree at 064c5aae08e9c58ff1458978c9d6484aa8527d94; I re-read the live head at posting time and it is the same SHA. Merge base 17f30f9c. Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2014-evidence/r2

## The block (step 6; step 8 on the completeness claim)

RCA section 4 states the widened rule and then says: "every other executed hit is cleared ... The `git show` / `git cat-file` reads in `prepr.sh` and `governance.yml` name the old path at a pinned base ref, with the new spelling tried second." I implemented that rule myself (widened_rule.py, my own script, not the fixer's). Over 140 retired-old paths absent at HEAD it returns 56 hits not cleared by a new-path, locate() or shim within 4 lines (widened_rule_head.txt). Most are prose, fixtures or the docstrings already carried. Two executed seams are broken and are neither in the diff nor dispositioned:

1. `tools/audit/seat/merge_train.py:146` and `:210` spawn `bash tools/audit/app_approve.sh`, and `:237` spawns `bash tools/audit/preflight.sh`. All three run with cwd=ROOT (repo root, parents[3]). tests/layout.json retires both paths (to tools/pr/app_approve.sh and tools/pr/preflight.sh, since: null). Running them gives `No such file or directory`, rc=127 (merge_train_spawns.txt). Consequences: the merge train's approve, carry and preflight gates cannot pass, and the preflight gate's output is a bash error. The same lines are present at the merge base. This seam sits next to the PR's own preflight.sh fix: it is the same moved program, spawned at the old spelling.
2. `.github/workflows/governance.yml:220`: `git cat-file -e "$PINNED:.claude/workflows/field_coverage.mjs"`. No new spelling is tried second, which contradicts section 4's sentence. Every base after #1919 therefore takes the "skipped" branch, and the field-coverage check is dark on every PR, push and schedule. CI shows it: main governance run 37626923348 (2026-10-07T13:14Z) prints `field coverage: the base does not carry it, so there is no pinned copy to run; skipped` (field_coverage_ci.txt).

Remedy: repoint the three merge_train spawns to tools/pr/; give line 220 the tools/policy/ fallback at the pinned ref. Or disposition each by name with an owner. Then correct section 4's "every other executed hit is cleared" sentence and the count "Four broken seams". This is the second class-open in the same class; fixer.md's three-round rule applies from the next round.

## The delta items asked about

- (a) PASS. `r9_fr3_family_consumer.mjs:43` now reads tools/policy/. At the head it exits rc=0 (fr3_head.txt). With the old path restored it gives rc=1 ENOENT (fr3_mut.txt).
- (b) The rule as stated is the right shape, but its completeness claim fails: see the block. Carry destinations:
  - The docstring carry is at 4a3adfc2, in R9-RO-9's `carry`, with the widened rule as its control.
  - The coordinator's premise that RO-8 merged is false: #2015 is OPEN (state OPEN, mergedAt null). The body's R9-RO-8 carry, for since-null (67 landed entries still null at this head, since_null_head.txt) and old-path launches, is still a live destination, and the RO-8 roster brief carries it.
  - The body still lists the docstrings under R9-RO-8 while the roster put them in RO-9. Fix that sentence in the re-cut. It does not block on its own.
- (c) In scope and proven. At the merge base, after #2011, the spawn used the probed STATS_RUN, but STATS_TOOL stayed `.claude/workflows/policy_lint.mjs`. That constant is the one quoted in a filed issue's `derivation command` and `keying rule` lines (friction_issues.mjs:437-438) and in the die() messages, so a filed issue carried a non-existent command. That is #2004's own symptom.
  - At the head: 102 passed, 0 failed.
  - With STATS_TOOL reverted and the #2011 probe kept: 101/1, failing the new arm (st_mut_tool.txt).
  - With both reverted: 100/2 (st_mut_both.txt).
  - With the new arm deleted: 101/0. The arm is not vacuous.
  - The coordinator's "new arm reverted" means the STATS_TOOL fix reverted, not the arm itself.
- (d) PASS. bugclasses.json `_rca` holds both R9-RCA-1985 and R9-RCA-2004 (98 entries). `fold_ledger.py check`: 98 rca entries, 0 violation(s).

## Other steps

- Step 11: the head's check-runs (34) show no red except nightly-status and delivery-status (main's, answered in the body). budget-raise-gate is cancelled again, so the orchestrator should rerun its twin. pr-contract, closures, fast, coverage, browser and CodeQL were still in progress at review time. The fixer commits 64c1744d and 79d5ff6c and the merges ff75696e and af62b2b8 have no failed runs.
- Step 13: `git merge-tree --write-tree origin/main HEAD` exits 0.
- Step 5: the delta does not touch VERSION, the manifest or the notes heading, and no claim file is in the PR diff.
