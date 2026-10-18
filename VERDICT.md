Fix review: merge c173d8f48ebccc5b649c9da70ba67282ff81203f

bus-nonce: c3db975ca9d449e498f94e76a367cd69

Round 1 (no earlier `review/2374` ref on the remote). PR #2374, R10-D15-GRADER, Part of #2268.
Measured head `c173d8f48ebccc5b649c9da70ba67282ff81203f`, which is `refs/pull/2374/head` and the body's `## Head`. Merge base `52f698905868c9140ed213ea542c44053fca7096`. The worktree was detached at that head, and `dev/governance/roles/` is identical between the merge base and origin/main `9a1ce39c3`.
Evidence: `/Users/timmalmstrom/hpo-seats/r10s3/review-2374/evidence/`

## #2268: both arms delivered: YES

- **(a) Bundle pins keyed on the brief.** The three bundle pins now take `['D15'].filter(d => L.briefs.includes(d))`, not the driver's `BUNDLE_DIMS`. The null-control pin runs unconditionally. The base check passes an empty, wrong or extra `BUNDLE_DIMS`, and the head check fails all three (table below).
- **(b) M1 restart-gap threshold.** D15.md M1 now defines a restart gap: consecutive `cycle_rows[].t` at least 3 x `optimization_interval` apart, taken from the download's `config`, else 30 min. M1 also says a tag dated after the last gap leaves the version unknown. `tools/audit/seat/d15_restart_gaps.py` applies the rule.
- **#2268 stays open after merge.** The roster's `fixes` is `[]`, so the body uses `Part of`, not a closing keyword. The orchestrator owes the close, or a roster `fixes` update, because both arms have landed. The issue body's own "names this issue with a closing keyword" contradicts the roster.

## Mutation proof, re-run (`evidence/mutation-table.txt`, `evidence/mut.sh`)

Each mutant is one `sed` on `.claude/workflows/audit-find.js`, run with `node tools/policy/check-wave-script.mjs`, then restored. "Base check" is `git show 52f698905:tools/policy/check-wave-script.mjs` written in place.

```
RESULT check=base driver=unmodified            rc=0 186 passed, 0 failed
RESULT check=base BUNDLE_DIMS=[]               rc=0 186/0   (passes: the defect)
RESULT check=base BUNDLE_DIMS=['D14']          rc=0 186/0
RESULT check=base BUNDLE_DIMS=['D15','D14']    rc=0 186/0
RESULT check=base relative-path refusal off    rc=1 FAIL "a relative bundle path is refused before Prepare (declared)"
RESULT check=base let ROUND_DIR                rc=0 186/0
RESULT check=base let CURRENT                  rc=0 186/0
RESULT check=head driver=unmodified            rc=0 187 passed, 0 failed
RESULT check=head BUNDLE_DIMS=[]               rc=1 FAIL "once D15.md exists, its finders carry the named bundle ..."
RESULT check=head BUNDLE_DIMS=['D14']          rc=1 FAIL same + FAIL "...no other finder is handed the bundle (null control)"
RESULT check=head BUNDLE_DIMS=['D15','D14']    rc=1 FAIL "...(null control)" D14-s1, D14-s2, D14-s3
RESULT check=head relative-path refusal off    rc=1 FAIL "a relative bundle path is refused before Prepare (D15 brief)"
RESULT check=head let ROUND_DIR                rc=1 FAIL "both drivers write where fold_ledger.py reads (not declared)"
RESULT check=head let CURRENT                  rc=1 FAIL "audit-find.js CURRENT is prepare_baseline.sh's CURRENT_PATHS (not both declared)"
```

The body's six-row table matches row for row. My own extra mutants are in `evidence/check-mutants.txt`:

- Predicate mutant. In the head check, `bundleDims = []` together with driver `BUNDLE_DIMS=[]` gives rc=0, 187/0. The body's claim holds: the brief key is what kills the mutant.
- In the check, the undeclared arm of `dirGaps` changed to return `[]`: the new control "...an undeclared ROUND_DIR or CURRENT is refused" FAILs. The same holds for the undeclared arm of `curGaps`.
- `audit-verify.js` with `let ROUND_DIR`: FAIL. `prepare_baseline.sh` with `CURRENT_PATHS` renamed: FAIL. Both undeclared arms are live.
- Driver throws on every bundle arg: the null control FAILs on `withBundle.error`, so the `error === ''` clause is live.
- Reader `GAP_INTERVALS = 3` changed to `2`: `restart_gaps` at plant 3600 goes from 0 to 1, as the body says.

## Harness at both ends

- **Arm (a).** The finder's instrument is `check-wave-script.mjs` itself, base copy against head copy (above).
- **Arm (b).** `d15_restart_gaps.py` does not exist at the merge base (`git ls-tree` shows 0 files). The finding came from the #2214/#2209 review comments, so it never had a committed finder harness (fix-review.md step 9). This reader is the fixer's own, first committed here; the body presents it as this PR's new file, not as the finder's. I ran the head's copy, taken out of tree, against both trees (`evidence/restart-gaps.txt`). Both trees have `DEFAULT_OPTIMIZATION_INTERVAL = 30`, and the results are identical at both ends. That is flat by design, because the PR changes no production code.

```
RESULT bundle=synthetic(336 rows, 1800 s, no config) source=default interval_s=1800
RESULT plant=0 restart_gaps=0 | 3600 0 | 5399 0 | 5400 1 | 12054 1 | 21599 1 | 21600 1   (base = head)
RESULT bundle=wrapped(config.optimization_interval=120) source=config interval_s=7200
RESULT plant=0 0 | 3600 0 | 5400 0 | 12054 0 | 21599 0 | 21600 1                        (base = head)
RESULT bundle=one cycle row  rc=2 "REFUSED fewer than two cycle rows"
```

Every reader figure in the body is reproduced: S=0/3600/5400/12054 on `$B`, S=12054/21600 on `$W`, and rc=2 on an empty bundle. I checked the config source myself: `diagnostics.config_view` puts `config` beside `debug`, and `CONF_OPTIMIZATION_INTERVAL` is `"optimization_interval"` (minutes).

## Null control

- The head check with the driver unmodified gives 187/0, and the base gives 186/0. The extra pin is the new undeclared-arm control, which is earned: the check mutant above kills it.
- The unplanted synthetic bundle gives `restart_gaps=0`, and plant 3600 (one skipped cycle) also gives 0.

## Class (step 6)

- I ran the body's rule, `grep -n "once \|armed\|not declared"`, on the base check. Apart from comment and vocabulary hits it returns exactly three seams, all in the diff: the bundle pins (base lines 1065-1076), ROUND_DIR (897) and CURRENT (915).
- I widened the search to every early `return []` or `=== undefined ||` pass. The `PANEL_DRIVER` / `P.per === undefined` (1138, 1242) arms come up. They are not this class: an absent declaration selects the other driver shape's arm, and that arm is graded, not skipped. `referentGaps` `if (!need) return []` (244) grades a roster row, not a driver.

## Other claims, each from a command I ran

- **Lineage.** `d94f0775a` has parents `76d4f8a2e` and `52f698905`. `c173d8f48` adds only `dev/programme/delivery/2374.md`. The merge base of `76d4f8a2e` with main is `811df3cf3`.
- **Main has not moved the graded files.** `git diff 52f698905 origin/main` over `.claude/workflows/`, the check, the dimension briefs, `prepare_baseline.sh`, `fold_ledger.py` and `dev/audit/config/` is empty.
- **Cheap checks** (`evidence/cheap-checks.txt`), all rc=0: `policy_lint.mjs`, `policy_lint.mjs --budgets`, `brief_lint.mjs`, `rules_sync.mjs --check`, `tmp_paths.py --check` and `tests/structure.py`.
  - D15.md tokens are 690/690 at the base and 689/690 at the head. Lines are 37 and 36 against a cap of 37.
  - No budget file is in the diff. The body's "1 token of headroom" is confirmed.
- **`closure.py select --diff <mb>`:** `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, RUN `tests/entities.py`.
- **`archscore/score.py --diff <mb> HEAD`:** `dS +0.0000 NULL`.
- **Unchanged files.** `VERSION`, `manifest.json`, `RELEASE_NOTES.md` and both claim files are untouched (0-line diff). The diff touches no `custom_components/` or fixture path, so I did not run `env_drift.py` or `card_drift.mjs`.
- **Gate.** The `tests/run.sh` gate is CI's heavy run. I cite it rather than re-running it: the head's check-runs are 30 success and 15 skipped, with none red (`evidence/check-runs-head.tsv`).
- **Range.** `d94f0775a` shows 9 cancelled runs, superseded by the push of `c173d8f48`. `pr-contract` at the head prints `record red-history ... every failure conclusion across them: none`. The body's "Red checks: none at handoff" holds.
- **Merge-tree.** `git merge-tree --write-tree origin/main(9a1ce39c3) c173d8f48` exits 0 (tree `74413184722a`), with no conflict.
- **Closing keywords.** The body has no closing keyword. Its issue refs are #2209, #2214, #2268, #201, and `fixer.md#18` (a step anchor that GitHub may autolink to #18; harmless). `closingIssuesReferences` is `[]`, consistent with roster `fixes: []` and the `Part of #2268` wording.
- **Ordering.** The roster lists `after: R10-TICK-DRIVERS` (not started). The orchestrator's `REPLAN-EDGES.json` gives R10-D15-GRADER no `after`. Architect note 8 splits ownership: D15-GRADER has the pin keys and D15.md, TICK-DRIVERS has `audit-find.js`, and whichever merges second re-runs the wave-script check. The diff stays in its lane.

## Owed (non-blocking)

1. **Policy.** `dev/governance/dimensions/D15.md` is a dimension brief. tvofi's approval is owed: the orchestrator approving under mandate 6175172275, per the body's `## Approval`. I noted it and did not block on it.
2. **Forward-carry.** The reader `tools/audit/seat/d15_restart_gaps.py` is named by nothing in the tree except its own docstring. D15.md has 1 token of headroom and cannot name it. The body hands the naming to the orchestrator's D15 dispatch prompt, which persists nowhere today. The rule itself is carried into D15.md M1, which is the stage destination, so this is not `carry-missing`. The orchestrator should write it into the next D15 dispatch, or into the roster or #201.
3. **Placement.** fixer.md step 18 places a harness in `dev/audit/harnesses/`. This one lives in `tools/audit/seat/`. The deviation is disclosed under Friction, with the reason that `tests/harness_headers.py` executes that directory.
4. **#2268 close** after merge (see above).
