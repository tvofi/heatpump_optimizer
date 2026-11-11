# D13 verify (round 10): one verifier, all three lenses

Worktree: detached at handoff/audit-r10-register 9355f107d. The branch was already checked out, so `--detach` was used. Load1 ran from 8.5 to 21 because other seats were running. Every number below is a count, with thread_factor 1, so contention does not affect it.
Independent harness: `verify_v13.py`. It reads the s1 raw API cache `$TMPDIR/d13s1-cache-1913f0dd7`. It restricts that cache to `git rev-list --first-parent --merges 1913f0dd7..17f1c55fad1b`, which gives 185 PRs. It uses its own regex, `^Fix review:\s+(merge|blocked)\s+<40hex>(\s+<class>:)?`, on the first line of every issue comment and review. Note that v6.7.16 is 1913f0dd7.

## D13-s1-01: weaken (low)
- **V1.** `yield.mjs --since 1913f0dd7` cannot reproduce at the baseline. It reads `<since>..origin/main`, and origin/main has moved, so the window is now 197. Its output records truncation_verdicts_dropped=17, and then it crashes with `TypeError ... reading 'comments'` at yield.mjs:119. The header pins no until-ref, which is a harness defect.
- **V2.** On the pinned window I count 22 of 185 with no verdict, and the PR list matches the finding exactly. The largest comment or review page holds 14 items, so there is no truncation at the baseline. `COVERAGE_LIST_CAP = 10` (policy_lint.mjs:2919) confirms that the list is capped and has no class split.
- **Attack.** The claim "no rule in the tree exempts them" is false for the record PRs. `dev/governance/rules/delivery-status-tracking.md` says: "The `record-autofix` beat's own merges with no review seat where `record_row.py --automerge-check` passes". 16 of the 17 record/docs PRs are titled `record: delivery rows`. The unexempted remainder is about 6: #2197, #2203, #2173, #2196, #2179 and #2005. The stats-split part stands.
- **V3.** The finding is reachable because it is real repository data. Its seam_rule does not enumerate the exemption rule. Class: new.

## D13-s2-01: verify (weakened to medium)
- **V1.** blocks_friction.mjs, run on a window.json rebuilt from the same cache, gives 124 blocked verdicts, root-cause-unanswered 37 and harness 23. `--perturb=verdict` moves them to 36 and outside=1, so it moves in the direction the finding states.
- **V2.** I independently count 124, 37 and 23, with head-moved 4.
- **V3.** web-fix-wave.js:308 does say "fix itself is sound". This is a yield and cost observation, not a defect with an end-user consequence, so it is medium, not high. Class: new.

## D13-s2-02: verify (medium)
- **V1.** The PROD row reads `verdict_row[head-moved] prs=71 entries=133`.
- **Perturbation.** I commented out policy_lint.mjs:2850 (the reverify `bump(verdicts, REWORK_CLASS, pr)`). The row dropped to prs=4 entries=4. I then restored the file.
- **V2.** My own count gives 4 blocked verdicts with head-moved.
- **V3.** The finding is reachable in the `--stats` output. Two meanings are counted in one row, so the class is I4.

## D13-s3-01: verify (medium)
- **V1.** With the import left as it is, the harness gives dora_keys_loads=0 (ModuleNotFoundError d11lib). With D13S3_FIX_IMPORT=1 it gives 0 (FileNotFoundError .claude/workflows/cfr_exclusions.json). With both the fix and the registered path it gives 1, with load_exclusions returning `['record']`.
- **V2.** `ls` shows d11lib.py only in tools/audit/round4/D11. dora_keys.py:88-89 imports it from its own directory, and line 103 points at a missing path. A plain import fails.
- **V3.** D13.md line 35 names the instrument. It was broken by de46d8da9 (R9-RO-8 move). Class: new, closest to I5.

## D13-s2-51: verify (low)
- **V1.** The harness gives split_keys=34 of 34. The plumbing-only arm also gives 34, and the perturbed arm gives 0.
- **V2.** I checked the keys directly with `--normalize-friction-keys`:

  | id | key |
  |---|---|
  | `dev/governance/roles/fixer.md` | itself |
  | `fixer.md` | `tools/audit/briefs/fixer.md` |
  | bare `fixer` | `fixer` (no mapping) |
  | `gate-scoping` | `.claude/rules/gate-scoping.md` (the generated copy, not the canon) |

  So the split is wider than the claim's "bare basename -> canonical" wording.
- **V3.** The seam_rule enumerates moved corpus files only. It does not enumerate bare-stem ids or the generated-copy mapping. The finder's report records an observed instance: fixer is split 16/1/1 across real friction. Class I4 is confirmed.
