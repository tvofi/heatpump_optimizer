Fix review: blocked 45754ede263322459d69936f5898d26fe64654f4 mutation-survivor: probe matching on the nonce's last 8 hex instead of its first passes all 87 checks because every fixture nonce repeats every 8 characters, and it moves the record's kind table; the two guardrail corrections the body routes to R10-ORCH-MACHINERY are not on its roster carry

bus-nonce: 6b482079637569c20a53f5be8570fcfb

This is **round 6** of PR #2579 (R10-FLOW-YIELD-PROBE), so a re-cut is owed under `fixer.md`, and the split ordered in round 5 is one. I measured head 45754ede263322459d69936f5898d26fe64654f4 from a detached worktree. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so this contract is current. `git ls-remote` still showed the branch at 45754ede263322459d69936f5898d26fe64654f4 at 13:05Z (ev/head_at_post.txt).

## Block

- **mutation-survivor (steps 1, 6 and 14): the probe match reads `nonce[-8:]` instead of `nonce[:8]`.** In `load`, `(int(m[1]), nonce[:8]) in probes` → `(int(m[1]), nonce[-8:]) in probes` passes `review_strength self-test: 87 checks, 0 failed`. So does `nonce[8:16]` (ev/hand_mutants.txt X2, ev/hand_mutants_2.txt X2b). Neither is in the sweep's classes: the slice class only moves a lone bound to the other side (`[:8]` → `[8:]`), and that mutant is killed. They survive because every fixture nonce repeats every 8 characters or less:
  - `f"{i:x}" * 32`;
  - `"09abcdef" * 4` and `"90fedcba" * 4`;
  - `"22" * 16`.

  For each of these, the first, second and last 8 characters are the same string. On the real bus, probe refs carry the nonce's first 8 hex (`probe/rev-2579-6b482079` for nonce `6b482079637569c20a53f5be8570fcfb`). Under the mutant, probe-returned cloud verdicts read local. The study bundle moves 96 lines (ev/hand_bundle_diff_X2.txt), including every kind cell the record quotes (yield-probe.md lines 126–128 and 165):
  - cloud P2 0.19 (6/31) → 0.16 (3/19), L1 0.12 (3/24) → 0.13 (2/15);
  - local P2 0.57 (8/14) → 0.37 (11/30), L1 0.00 (0/20) → 0.03 (1/29). The latter breaks the "0 in 20" claim and its (1 − 0.28)^20 = 0.0014;
  - cloud + finding-fix P2 0.23 (3/13) → 0.29 (2/7), L1 0.17 (1/6) → 0.00 (0/3);
  - cloud first-pass 8/25 → 6/14 (P2) and 9/20 → 7/13 (L1).

  The fix is one fixture line: give at least one probe-returned fixture verdict a nonce whose first 8 hex appear nowhere else in it.
- **carry-missing (step 10): the two corrected points the body routes to R10-ORCH-MACHINERY are not in that stage's brief.** The body's `## Forward-carry` says "The owner group gets two corrected points" and names `dev/programme/rosters/wave-r10-groups.json` as the destination:
  - P(X ≤ 4 | 30, 0.28) = 0.0495, so the 30-PR arm trips at 4 or fewer, not 3;
  - any `ALPHA` the guardrail adopts needs a check at P = 0.0526 (k = 2 of 20).

  The carry item b8b28b28 at `groups[93]` (R10-ORCH-MACHINERY) is unchanged and holds neither point. That is true on the handoff roster 229151c282b9 and on origin/main 47147487ba2b (ev/forward_carry.txt). Its text is still "the yield-probe guardrail (threshold, extended class list, seat-family arm, planted-defect calibration) ... Control: a planted defect of each class must trip the guardrail, and a null window must not." Both points narrow what that stage may do (`finding-propagation.md`). Stated only in this PR's body, they are not propagated. `carry_audit.py` passes the body (1 routed) because it checks that a destination group exists, not that the destination holds the text.

**Split (three-round rule).** I do not recommend a further split. The guardrail split was done cleanly (Evidence). What blocks is two small edits inside what is left, not scope. The minimal mergeable part is this PR as it stands, plus:
- one non-periodic fixture nonce on a probe-returned verdict;
- the two corrected points written into item b8b28b28's text (or a new carry under R10-ORCH-MACHINERY) on the roster.

Nothing else needs to change. Every round-5 Block item is answered at this head.

## Findings

- The probe-slice survivor and the missing roster text, stated under Block, are owed by this PR's next round. Carry: dismissed: owed by this pull request's next round, stated under Block
- **Seven further hand mutants survive with an empty bundle diff on the real bus** (ev/hand_mutants.txt). Each is equivalent on the bus's inputs, and I name the input that would separate it:
  - X5: `--first-parent` added to the review-ref log. Verdict commits on review refs are linear; a verdict reached only through a merge's second parent would separate it.
  - X8: the class-word group `[^\s:]+` → `\S+?`. A class word holding a colon (`a:b:`) would separate it.
  - X10: `.astimezone(timezone.utc)` dropped. Aware comparisons do not depend on the zone; a non-UTC committer offset changes only printed stamps.
  - X11: a roster group keyed first-wins. Separated by a duplicated group name.
  - X12: the last group token in a delivery row instead of the first. Separated by a row naming two groups.
  - X16: the sort ties broken by PR number. Separated by two verdicts at the same second.
  - X17: `parents.split()[1]` → `[-1]`. Equivalent on every input, because the line filters to two parents.

  None moves a figure. Carry: dismissed: equivalent on the bus's inputs, no figure moves
- **The new GROUP_RE disposition quotes a count the tree no longer holds.** It reads "all 150 roster groups hold two or more characters after the dash". The R10 roster holds 151 groups at both origin/main and the handoff ref. The minimum is still 2 characters, so the equivalence holds (ev/roster_groups.txt). The count should be dropped or re-derived. Carry: dismissed: wording, owed by this pull request's next round alongside the Block fixes

## Evidence

- **Round-5 findings, each answered at this head (brief item 1):**
  - H1 is killed: `FAIL: group regex: a group's inner dashes are part of it (18 R10-FLOW-YIELD-PROBE, not R10-FLOW)`.
  - H9 is killed: `FAIL: product: tests/, tools/, custom_components.md and blueprints.md are not under the product prefixes (16)`.
  - H5 (`%cI` → `%aI`) is killed: `FAIL: a verdict counts at its committer time, not its author time (20: ...)` (ev/hand_mutants_2.txt).
  - The threshold sentence and `ALPHA` (with DISPOSED (b)) left with the guardrail. `grep -i "alpha|binom|guardrail"` over the tool, harness, record and INSTRUMENTS.md finds only prose naming the owner group.
  - The ref_privacy refusal is fixed: `ref_privacy --check at HEAD: 22 file(s) with a push site, 11 guarded, ... 0 refused` (ev/ref_privacy.txt).
  - DISPOSED (a) and (c) now say "equivalent on the bus's inputs" and name the separating input.
  - The body is 7,255 characters (ev/pr_body.md), about half the 14.4k of round 5.
  - The one routing gap is the forward-carry text, under Block.
- **Self-test (3.11):** `review_strength self-test: 87 checks, 0 failed` (ev/selftest_head.txt), the body's figure.
- **Class sweep, re-run at the head (brief item 2):** `python3 dev/audit/harnesses/r10_review_strength_mutants.py --jobs 4` printed `RESULT mutants=2350 killed=2306 survived=44 disposed=44 undisposed=0 stale=0`, rc=0, from 12:32Z to 13:04Z (ev/sweep_head.txt). M0 passed with 87/0. The body quotes `stale=1` at 29110ab18 and says the head drops that entry; `stale=0` here confirms it. The 44 survivors by class, every one disposed:
  - statements 20: nine parser registration swaps, four stratum swaps, three tally, and one each for the `if not m` swap, the `files.append` swap, the move into `if not f.startswith`, and the `if a.fetch` swap;
  - literals 9: NONCE_RE `{31}`, GROUP_RE's first `]`, `+00`, the four ref-pattern trailing slashes, `^1` → `^` and `--tags` → `--tag`;
  - calls 9: three `rsplit`, four dropped positionals (three split maxsplits and `-q`), and the `check=` and `default=` keywords;
  - threshold 4: `g[1]` → `g[0]`, numstat 2 → 3, and the two split maxsplits 1 → 2;
  - branch 2: `test mb -> True` and `check=False -> True`.

  `--list` gives 2350 at the head, byte-identical to 218b0af4c's list and to 29110ab18's (`MUTANT-LIST-IDENTICAL`, ev/mutant_list_identity.txt). The only change from 29110ab18 to 218b0af4c is two deleted harness lines.
- **My own hand mutants** (ev/muts.py, ev/muts_round2.py, ev/run.py, ev/hand_mutants*.txt). I applied 24 one-line mutants outside the sweep's classes, each in a scratch root, and restored the source identical:
  - 15 killed: X1 (archived probe tags dropped), X3 (window `(a, b]`), X4 (as-of = last window), X6 (size ignoring `tests/`), X7 (confirmed key/value swapped), X9 (real/book swapped), X13 (`"cloud" in rid`), X14, X15, X18, X2c (`nonce[1:9]`), X19 (nonce reversed), H1, H9 and H5.
  - 9 survived: X2 and X2b (under Block), and X5, X8, X10, X11, X12, X16 and X17 (under Findings).
- **Figures in the body, re-taken at the head (brief item 3).** All match:
  - 87/0 and 2350/2306/44 (stale 1 → 0, as the body says);
  - ref_privacy 0 refused;
  - `--window A=2026-10-15T12:37Z..2026-10-21T11:00Z` prints `PRs 112 verdicts 257 real 58 (0.52/PR)` (ev/window_A.txt);
  - the bundle's `all L PRs 47 verdicts 84 real 7 (0.15/PR)` (ev/bundle_head.txt);
  - `facts as of 2026-10-21T15:15Z: tree e7c664856776 roster 2c76c3128bf6`;
  - `tests/closure.py select --diff origin/main` prints `MODE: SCOPED -- 2 script(s) run, 31 scoped out`;
  - at 3.13 with the CI requirements: `ALL 2388 ENTITY CHECKS PASSED` and `ALL 109 HARNESS HEADER CHECKS PASSED` (ev/entities_headers.txt);
  - `STRUCTURE RATCHET PASSED` (ev/structure.txt);
  - (1 − 0.28)^20 = 0.00140.

  The bus now holds 407 verdicts, against the body's 403 and round 5's 395. That count is the bus, not a figure the record defends. My bundle differs from round 5's only on that line (ev/bundle_vs_round5.diff).
- **Null control (step 3):** the 6ad8089c tool and the head tool, run over the same fetched bus with the record's bundle arguments, print `BUNDLE-IDENTICAL` (ev/null_bundle.txt, ev/bundle_6ad8089c.txt).
- **The guardrail split and the architecture score (brief item 4).** d2d6dd688 removes the guardrail; it does not move it. `--guardrail`, `ALPHA` and `binom_cdf` exist nowhere in the tree at the head, so there is one definition and no duplicate. The record keeps only the explanation of the fall and points at item b8b28b28. `python3 tools/audit/archscore/score.py --diff 543c8087c (merge base) 45754ede2` prints `Architecture score: dS +0.0000 NULL` (ev/archscore.txt). The diff touches no file the score reads. `tests/structure.py` prints `STRUCTURE RATCHET PASSED`, and the three-dot diff changes no `*_budgets.json`.
- **Red checks over the branch history (brief item 5, step 11).** I read the check-runs API for all 32 PR commits (ev/red_history.tsv):
  - `instrument-self-tests` failed at 6ad8089c1, and `pr-contract` failed at 6ad8089c1 (10:12Z). The body names both and gives each its cheaper detector.
  - `nightly-status` failed at 81d617cec, 468781122, 816b1e20f, eb9f7e89d, 6ad8089c1 and the head. The body names it as main's; it is not a required check and does not block.
  - 13 runs at 81d617cec were `cancelled`, superseded by the push of 468781122 within a minute, and none of them failed.

  The body's `## Red checks` names every red.
- **CI on this head at 13:05Z** (ev/check_runs_head.tsv): 30 success, 7 skipped, 1 failure (`nightly-status`, above) and 1 in progress (`closures`). Both `pr-contract` runs succeeded, at 12:30:38Z and 12:31:23Z. CI is not why this verdict blocks.
- **Merge-tree (step 13, brief item 6):** `git merge-tree --write-tree origin/main 45754ede263322459d69936f5898d26fe64654f4` with origin/main at 47147487ba2b is clean: rc 0, tree e3dbdc42aab5 (ev/merge_tree.txt).
- **Carry audit (brief item 6):** `carry_audit.py --roster-ref origin/main check --body` prints `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`, and so does `--roster-ref origin/handoff/audit-r10-roster` (ev/carry_audit_body.txt). As stated under Block, routed is not the same as delivered.
- **Steps 4, 5 and 7:** the three-dot diff from merge base 543c8087c lists 8 files. None is `VERSION`, the manifest, `RELEASE_NOTES.md` or a claim file. `## Head` names 45754ede263322459d69936f5898d26fe64654f4, the head I measured, with code head 218b0af4c.

RESULT selftest=87/0 sweep=2350/2306/44_disposed/0_undisposed/0_stale hand_mutants=24 killed=15 survived=9 survived_moving_quoted_figures=2(X2_nonce[-8:],X2b_nonce[8:16]) round5_findings=answered(H1,H9,H5_killed;guardrail_split;ref_privacy_0_refused) body_figures=all_match null_bundle=identical archscore=dS+0.0000_NULL structure=passed red_history=all_named merge_tree=clean carry_audit_body=0_unrouted_0_bad forward_carry_text=missing(b8b28b28) round=6 split=not_recommended
