# Round 9 · D13 · verifier V1 (reproduce) · unit D13

Box G1-V1, lens V1. Evidence tree: `handoff/audit-r9-evidence` at 6f51db2c. Nothing under `.claude/`, `tests/` or `tools/audit/round9/D13/s1/` differs from baseline 1936d5ca72a06556eeed4e8e5bf3dea520e517e1. Machine: 4 vCPU cloud container, shared with two other sub-seats. Node v22.22.2, CPython 3.14.0rc2, numpy 2.4.6, scipy 1.17.1. Every number below is a count from git or from the finder's `window.json.gz` snapshot, so contention cannot move it. load1 was 2.3–3.3 and thread_factor 1.0 throughout.

Tally: 1 verify, 2 weaken, 0 refute, 0 unresolved.

Exposure: I did not read GitHub. The only source for what the live API answered is the finder's snapshot, so I could not re-check its `[]` rows against GitHub. The snapshot records them as `[]` answers, not `null` failures, and `api_failures` is 0.

**Reproducibility defect in the finder's harnesses.** The `enum_gap.mjs` header command does not reproduce in a shared checkout. It reads `origin/main`, which is now db878b29, 18 commits past the baseline. The stub answers 404 for those commits, so the CLI prints `STATS: 0` against 256 subject merges. I re-ran every finder arm in a private `git clone --shared` with `origin/main` pinned to 1936d5ca; my own harness pins it internally. `yield_rounds.mjs` does not read `origin/main`.

My harnesses, each run as `HPO_PLANDATA=$(mktemp -d) node <path>` from the repository root:
- `tools/audit/round9/D13/verify-v1/seam_dose.mjs`
- `tools/audit/round9/D13/verify-v1/rounds_indep.mjs`

## D13-s1-01 — `--stats` API mode silently drops 52 of 253 merges · vote: VERIFY (medium)

**Re-run** of `enum_gap.mjs` in the pinned clone, exact:

| arm | stats_window_merges | subject_merges | gap | gap_marked |
|---|---|---|---|---|
| none | 201 | 253 | 52 | 0 |
| drop:8cca77bc | 200 | 253 | 53 | 0 |
| restore (null control) | 253 | 253 | 0 | 0 |

The drop arm moves down as stated.

**Own measurement** (`seam_dose.mjs`). It uses the production CLI at the baseline, with a stub built from git subjects only, not from the snapshot, answering `[]` for a chosen set E: E empty N=253; E={#1100} N=252; 10 lowest numbers N=243; the snapshot's 52 N=201. The dose response is exact. None of the dropped numbers appears anywhere in the output (`mentioned`=0), and no skip, UNCHECKED or unfetched line prints (`marker`=0).

**Reach beyond `--stats`:** `--record --since v6.6.0` gives RECORD 253 with E empty and 201 with the 52. The same seam (`mergedPRsFromWindow`) also removes these merges from the disposition check without saying so.

**Attacks:**
- Are the 52 real PR merges? Yes. All 253 subject merges have two parents, and no number in the subject disagrees with the API's number (0 mismatches).
- Code read: `fetchPullsBySha` maps a sha only when rows are non-empty (policy_lint.mjs:1924–1935), and `enumerateMerges` skips unmapped shas (1908–1910). The mechanism stands.
- Leave-one-out does not apply (the result is a set count).

**Correction:** the dropped range is #1097–#1165, not #1098–#1165; #1097 is also empty.

**Metric:** N in `STATS: N merged pull request(s)` against first-parent `Merge pull request #N` subjects in v6.6.0..1936d5ca. Key: the PR-number set.

## D13-s1-02 — 22 re-verify rounds caught 0 defects; 12 heads moved only by merges or `ci:` · vote: WEAKEN (high → low)

**Re-run:** `reverify_rounds`=22, `reverify_blocked`=0, merges-only 11, ci-bot-only 1, branch content 10. `prod_reverify_entries`=22. The `block_one_reverify` perturbation moves `reverify_blocked` 0 → 1, up as stated. The null control gives `prod_repair_entries`=21 and `prod_repeat_entries`=6, matching the finding.

**Own measurement** (`rounds_indep.mjs`), with my own verdict regex and no `policy_lint` import, also finds 22 rounds and 0 blocked. I then measured the phenomenon property directly: is the branch diff at the new head identical to the reviewed one? base(H) is the newest baseline first-parent commit reachable from H; I compared the `patch-id --stable` of `git diff base(prev) prev` with that of `git diff base(cur) cur`. Result: 2 of 22 rounds identical with `-U3`, 3 of 22 with `-U0`. Of the 12 rounds the finder counts as "merges or ci only", only 3 left the diff unchanged; the other 9 changed the branch's diff through conflict resolution, content brought in by the merge, or a bot re-record.

**Attacks:**
1. **Chance.** At the window's own first-verdict block rate (16/188), zero blocks in 22 rounds has probability 0.141. "Caught 0" does not show that the round is worthless.
2. **Proxy versus property.** The "12 heads" count is a first-parent classification, not diff equivalence. The proposed fix, carrying the verdict across a diff-identical move, would have saved 3 rounds (`-U0`) in the window, not 12.

The zero reproduces, but the high severity rests on the 12, and the 12 does not measure the stated property. I would give it low.

**Metric:** among verdicts following a `merge` verdict on a different head, the count that are `blocked`. My addition: the count whose branch diff against its main base is patch-id-identical to the reviewed one.

## D13-s1-03 — body-answer blocks (8) exceed every engineering class (max 1) · vote: WEAKEN (high → low)

**Re-run:** `m3_blocked_verdicts`=21, `m3_body_answer_blocks`=8, `m3_max_engineering_class`=1. Buckets: engineering 7, record-and-body 12, orchestration 2. The `rca_to_harness` perturbation moves body-answer to 7, record-and-body to 11 and engineering to 8, down as stated. `reshape_one` moves coverage 188 → 187.

**Own measurement:**
- body_answer is 8, across 6 distinct PRs.
- `max_eng_raw` is 1. But with the harness's own synonym map applied to the engineering side as well (it is already applied to the body-answer side: red-check → root-cause-unanswered), the largest engineering class is 2: harness, mutation-vacuous and product-tradeoff-regression each hold 2. The claim "no engineering class has more than 1" is false under consistent bucketing.
- Counting every reason a verdict gives, not just its first word: 3 of the 8 body-answer blocks also name an engineering defect (#1559 ×2: class-open, and a `_fabricated_forecast` regression; #1561: class-open), which a mechanical pre-review check would not have saved. Sole-reason body-answer blocks: 5. Largest engineering class counting every mention: 4.

**Attacks:**
- **Cluster artefact.** 7 of the 8 are in PRs #1559–#1563, all verdicts posted on 2026-09-24 between 07:25 and 15:32 UTC: one wave. Outside that wave, body-answer is 1 against an engineering maximum of 2, so the ordering reverses.
- **Leave-one-out.** Dropping any one PR leaves a minimum of 6, so it survives one-PR leave-one-out. It fails leave-one-wave-out.
- **Policy already moved.** The red-checks rule itself changed that evening (ed488dda and 126a3f66, 2026-09-24 20:16–20:55 UTC).

The count reproduces exactly. It does not support a steady-state claim at high severity. I would give it low.

**Metric:** blocked verdicts whose class word is root-cause-unanswered or red-check, against the largest engineering class. Mine: counted with synonyms merged on both sides and with every stated reason included.
