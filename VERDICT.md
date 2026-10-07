Fix review: merge 1d494f01c492d497b0457ec5486380becac1886c

bus-nonce: 376068b8a134de7ef9837f070eabf061
Reviewer: r9c-rev-2014, round 3. Fresh detached worktree /Users/timmalmstrom/hpo-seats/r9c-rev-2014-r3 at 1d494f01c492d497b0457ec5486380becac1886c; I re-read the live head at posting time and it is the same SHA. Merge base c327da7f. Evidence: /Users/timmalmstrom/hpo-seats/r9c-rev-2014-evidence/r3

## Round-2 block, resolved
- governance.yml:220 (field coverage) and :602 (agreement lane) now probe `$PINNED:tools/policy/<tool>.mjs` first and the old spelling second. Both ends come from CI logs:
  - main run 37626923348 (13:14Z) printed `field coverage: the base does not carry it ... skipped` and `agreement lane: the base does not carry it ... skipped` (gov_main_before.txt).
  - This head's governance run 37661658656 prints `FIELD COVERAGE ok` and `AGREEMENT ok` (policy_docs_head_log.txt). policy-docs is success.
- merge_train.py:146,210,237: fixed on main by #2012 (RCA-1990, merged 14:21Z), which this head contains (a `tool()` map, merge_train.py:84-85).
- My own widened rule (widened_rule.py, now also skipping dev/audit/rounds/) at this head (widened_rule_head.txt): 156 retired-old paths absent at HEAD, 105 hits cleared, 63 uncleared.
  - Neither round-2 seam is returned any more.
  - The new uncleared hits come from paths retired by RO-8's merge: check-wave-script.mjs reads through `at()`, and `node tools/policy/check-wave-script.mjs` gives rc=0, 170/0. The others are prompt strings in audit-find.js and audit-verify.js. No executed seam is left uncleared.
- RCA section 4 now states seven broken seams (six fixed here or on main, one owned by #2012), with the triage of the uncleared hits. I re-derived it with my rule; it holds.

## Re-checked at this head
- The FR-3 consumer, now at dev/audit/harnesses/ after RO-8, exits rc=0.
- `friction_issues.mjs --self-test`: 102 passed, 0 failed.
- `preflight.sh`: `ok policy corpus -- current with origin/main`.
- `rules_sync --check` rc=0. `fold_ledger.py check`: 99 rca entries, 0 violation(s). R9-RCA-2004 is in dev/audit/config/bugclasses.json; RCA_DIR is dev/audit/rca.
- Step 13: `merge-tree` against origin/main rc=0. Step 5: no VERSION, manifest, notes heading or claim file in the diff.
- Step 11 (check-runs at 1d494f01, checkruns_head.tsv, 34 runs):
  - Red: delivery-status and nightly-status, both answered in the body as main's.
  - closures was red at 064c5aae, and main 17f30f9c's own closures is also failure, which confirms the body's account. closures-autofix is downstream of it, and the body names both.
  - budget-raise-gate is **cancelled** again; rerun its twin before merge.
  - Still in progress at review time: closures, browser, fast (3.14), coverage, env-matrix, CodeQL. The merge is conditional on these finishing green; I did not watch them.
  - Fixer commits da21eb93 and 44f5103c and merge 55a1aee9: no failed runs (checkruns_range.txt).

## Body corrections owed (not blocking; they do not change the code or the verdict)
- `## Red checks` says the diff touches none of the red checks' inputs, and lists `governance.yml` among them. Since da21eb93 the diff does edit governance.yml, at lines 220 and 602. The delivery-status job is at governance.yml:906 and is untouched, so the conclusion (main's red) still holds, but the sentence is false as written.
- RCA section 4 calls #2012 "open"; it merged at 14:21Z and its fix is in this head. Its path citations (tools/audit/harnesses/..., tools/audit/bugclasses.json) predate RO-8's move to dev/audit/.
