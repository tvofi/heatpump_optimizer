Fix review: blocked 6ad8089c14b50de2f6408ef6948a7d86ca4c52c2 mutation-survivor: hand mutants outside the sweep's classes (GROUP_RE's inner '-' dropped, a tests/ product prefix added) pass all 96 checks and move the origin and product figures; the record's guardrail line misstates its own trip count; instrument-self-tests is red on this PR's push site

bus-nonce: fabf465ca534b864017249d81a9bbb57

This is **round 5** of PR #2579 (R10-FLOW-YIELD-PROBE). `fixer.md` owes a re-cut from round 4, and this round is one: a class sweep replaced pinning mutants one at a time. I measured head 6ad8089c14b50de2f6408ef6948a7d86ca4c52c2 from a detached worktree. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so this contract is current. `git ls-remote` showed the branch still at 6ad8089c14b50de2f6408ef6948a7d86ca4c52c2 at 2026-10-22T09:48Z (ev/head_structure.txt).

## Block

- **mutation-survivor (steps 1, 6 and 14): GROUP_RE's inner `-` dropped.** The body's class rule only generates three kinds of literal edit: end characters dropped, cuts at a separator, and a numeral moved. It never deletes a character inside a regex. `\b(R\d+-[A-Z0-9][A-Z0-9-]*[A-Z0-9])\b` → `\b(R\d+-[A-Z0-9][A-Z0-9]*[A-Z0-9])\b` is not among the sweep's 2333 mutants (ev/sweep_list.txt, 0 matches). It passes `review_strength self-test: 96 checks, 0 failed`, because every fixture group (`R1-FIX`, `R1-RES`, ...) has a single dash. On the real bus, every multi-dash group (`R10-FLOW-YIELD-PROBE`) then reads as `R10-FLOW`, and the origin stratum collapses (ev/bundle_diff_H1.txt):
  - finding-fix P1 1.08 (40/37) → 1.38 (11/8), P2 0.29 (5/17) → 0.00 (0/2), L1 0.08 (1/13) → 0.17 (1/6);
  - none P1 0.27 (3/11) → 0.80 (32/40), and with it the origin re-weight 0.50 and the "about half of the fall" conclusion.

  The body says the self-test pins "the group regex's digit classes". It pins those classes but not the group shape the bus actually uses.
- **mutation-survivor: a `tests/` product prefix added.** `("custom_components/", "blueprints/")` → `("custom_components/", "blueprints/", "tests/")` passes 96/0. The fixture's non-product PRs touch no `tests/` file. The mutant moves the product table: True P1 1.21 (17/14) → 1.19 (37/31), P2 0.22 (2/9) → 0.52 (11/21), L1 0.14 (1/7) → 0.09 (2/23). It moves the instrument row and the product re-weight 0.85 too (ev/bundle_diff_H9.txt). The BOUNDS exclude "replace a literal with an unrelated one", but an added element is the same open shape: the product predicate is pinned only against the prefixes the fixture happens to hold.
- **figures-false: the threshold sentence in `dev/audit/rounds/round10/D13/yield-probe.md`.** "Trip at P(X ≤ k | 30, 0.28) < 0.05, which means 3 or fewer of the 30 PRs (P = 0.017). At 4, P = 0.050, so 4 is the line." But P(X ≤ 4 | 30, 0.28) = 0.04954, which is below 0.05. The tool's own `guardrail` prints `incidence 4/30; P(X<=4|30,0.28) = 0.050 -> would-trip` (ev/guardrail_k4.txt, ev/g4.py). The arm trips at 4 or fewer, not 3. This sentence is the threshold carried to R10-ORCH-MACHINERY. The seat-family arm's "1 or fewer (P = 0.012)" is right, since k=2 gives 0.0526.
- **A red gate check: `instrument-self-tests` failed on this head.** Its log: `ref_privacy: REFUSE tools/audit/seat/review_strength.py:854: a push site in a file PUSHERS does not name` (ev/instrument_self_tests_excerpt.txt). Line 854 is the `g("push", ...)` this round's new `--fetch` fixture adds. The e53fee3 tool has no push site, and `python3 -I tools/audit/seat/ref_privacy.py --check` at the head reproduces the refusal (ev/ref_privacy_check.txt). This is not external: no rate-limit or unreachable line causes it. The body's `## Red checks` ran no `ref_privacy --check`, a seconds-long local detector, and the check does not name it. Not every workflow on the head had concluded, so I do not post `root-cause-unanswered`. The body still owes that answer (fix-review step 11).

What to fix, and what to split out (the third-round rule):
- Add a multi-dash fixture group, and a non-product PR touching `tests/` (or any non-product top-level directory).
- Extend the literal class to drop each single character of a regex literal. That is bounded by the literal's length.
- Fix the threshold sentence.
- Register the push site in PUSHERS, or guard it.
- **Split the guardrail recommendation out of this PR.** Its threshold, arms and back-test are already R10-ORCH-MACHINERY's carry (roster item b8b28b28). This PR then owes only the explanation of the fall, and the tool's `--guardrail` path with ALPHA leaves the figures it must defend.

## Findings

- GROUP_RE (H1), the product prefix (H9), the threshold sentence and the ref_privacy refusal, stated under Block, are each owed by this PR's next round, not a later stage. Carry: dismissed: owed by this pull request's next round, stated under Block
- **ALPHA is unpinned between 0.05 and 0.0526.** `ALPHA = 0.05` → `0.06` passes 96/0 (ev/hand_mutants.txt, H18). It moves no bundle or back-test figure, because the lowest back-test P is 0.116. It would flip the seat-family arm's line, though: k=2 of 20 at p0 0.28 gives 0.0526, so that arm trips at 2 or fewer under 0.06. If the guardrail stays in this PR, a check at that P is owed. Carry: dismissed: moot if the guardrail is split out as Block asks, else owed by this pull request's next round
- **Three DISPOSED entries are not equivalent on every input.** Each holds on the real bus and moves no figure:
  - (a) `nonce {32} → {31}`: a VERDICT.md holding a 31-hex `bus-nonce:` reads local in the tool and cloud under the mutant. ev/dispositions_check.txt shows the mutant matching `aaaaaaaa`. The real bus holds 395 nonces, all 32-hex (ev/bus_nonce_shapes.txt).
  - (b) `cdf < ALPHA → <=`: a CDF of exactly 0.05 exists. For example, n=3, k=0, p0=0.6315968501359613 flips `ok` to `would-trip`. I found 67 such (n, k, p0) for N ≤ 40 (ev/dispositions_check.txt). The entry's own reason scopes it to "N ≤ 5 on a 1e-5 p0 grid", and the body's table drops that scope.
  - (c) `w.split('=', 1) → rsplit`: `--window A=B=2026-10-20T00:00Z..2026-10-21T00:00Z` raises ValueError in the tool, but the mutant prints a window named `A=B` (ev/window_rsplit.txt).

  The reasons should say "equivalent on the bus's inputs" and name the input that separates the two, or a check should pin them. Carry: dismissed: no figure moves on the real bus; the reasons' wording is owed by this pull request's next round
- **Author time is unpinned.** `%cI` → `%aI` (H5) passes 96/0 and moves nothing on today's bus (empty bundle diff). The record's rule is "by committer time", and no fixture verdict has different author and committer dates. Carry: dismissed: equivalent on the real bus; a rebased verdict commit would separate them, owed as a fixture in the next round if the rule stays
- **The body is longer than its content needs (third-round rule).** The `## Head` section walks eight commits and four main merges, which the head's merge structure already shows. The 19-row DISPOSED table restates the harness's own `DISPOSED` reasons. The `## Red checks` list reports runs at intermediate commits. The next body can quote the code head, the sweep's RESULT line and point at `DISPOSED`, at under half its present 14.4k characters. Carry: dismissed: owed by this pull request's next round

## Evidence

- **Self-test at the head (3.11):** `review_strength self-test: 96 checks, 0 failed` (ev/selftest_head.txt).
- **The sweep, re-run** at the head with `python3 dev/audit/harnesses/r10_review_strength_mutants.py --jobs 4` (ev/sweep_head.txt) prints `RESULT mutants=2333 killed=2286 survived=47 disposed=47 undisposed=0 stale=0`, rc=0, in 35 min. That is the body's figure, re-derived. It holds only within the rule's classes: see Block. `--list` enumerates 2333 mutants (ev/sweep_list.txt), the body's count. M0 passed, `review_strength self-test: 96 checks, 0 failed`; that is the sweep's null control.
- **Hand mutants outside the stated classes** (ev/muts.py, ev/run.py, ev/hand_mutants.txt). I wrote 30; the runner skipped none and restored the file identical.
  - 18 killed: H2 (MERGE_RE made greedy), H3 (additions-only size), H4 (PRs by head), H8 (the first head), H10, H16a-d (150 → 100/200, 600 → 500/800), H17, H24, H25, H26, H30, H31, H32, H33 and H35.
  - 12 survived. 2 move quoted figures: H1 and H9, under Block. H19 is my own error: it is a no-op rewrite. The other 9 have an empty bundle diff on the real bus: H5, H6, H7, H13, H18, H27, H28, H29 and H34. H27 (`== 'merge'` → `!= 'blocked'`) is equivalent, since a kind is one of the two.
- **The DISPOSED entries, each checked.** I checked each against the tool's code. Equivalent on every input I could construct:
  - fromisoformat `+00`, re-run on five spec shapes in ev/dispositions_check.txt;
  - the four ref patterns: for-each-ref matches a pattern at a whole component;
  - `^1` → `^`, `g[1]` → `g[0]`, and the `or ''` arm;
  - the numstat ones (git quotes a path holding a tab), the `mb` ones and `check=`;
  - the stratum, tally, `files.append`, parser, fetch `-q`, `--tag` and `default=` ones;
  - the `..`-split ones: a span holding a second `..` fails `fromisoformat` either way.

  Not equivalent on every input: (a) to (c) under Findings.
- **Finder's harness (step 2).** Both ends are the brief's quoted rates. The tool does not exist at the merge base, so the baseline is the hand count. At the head after `--fetch`:
  - `--window A=2026-10-15T12:37Z..2026-10-21T11:00Z` prints `PRs 112 verdicts 257 real 58 (0.52/PR)`;
  - the bundle's `all L` row prints `PRs 47 verdicts 84 real 7 (0.15/PR)` (ev/figures_extra.txt, ev/bundle_head.txt).

  The bundle reads `facts as of 2026-10-21T15:15Z: tree e7c664856776 roster 2c76c3128bf6`, with 395 verdicts on the bus and 0 outside the grammar.
- **Null control (step 3).** The e53fee3 tool and the head's tool, run over the same fetched bus with the body's bundle arguments, print byte-identical output: `BUNDLE-IDENTICAL` (ev/null_bundle.txt, ev/bundle_e53fee3.txt). So the tool changes move no figure, as the body claims. I did not re-run the body's baseline-end sweep against the e53fee3 tool (`undisposed=128`). That figure is not re-derived here.
- **Figures in yield-probe.md re-derived at the head** (ev/bundle_head.txt, ev/figures_extra.txt, ev/figures_record.txt). All match except the threshold sentence under Block:
  - baselines: 112 / 0.52 (58) / 0.58 (65) / 36/112; 47 / 0.15 / 0.64 / 6/47; 35 / 0.06 (2); L13 real 4;
  - P1, P2, L1 and S rows;
  - every origin, size and product cell;
  - the re-weights 0.50, 0.89 and 0.85, recomputed;
  - kind and kind+origin cells;
  - fixer first-pass and real/PR, and cloud first-pass 8/25, 9/20;
  - after-a-merge E 22/17, L 12/8, the 6-day 33/22, all 0 real;
  - `harness` 25/3/2 and `carry-missing` 3/15;
  - the nine words 0/5/5;
  - the extended list: P2 19/39 (13/39), L1 8/39 (7/39), S 5/14, cloud 9/31 (8/31), 8/24 (7/24), local L1 0/20, POST 24/85;
  - 0-in-20 P = 0.0014;
  - P = 0.017 and 0.012.

  Back-test, at my own ten cut points: lowest 5/30 at 10-21 06:00Z and 13:00Z (P = 0.116), highest 19/30 at 10-18 08:00Z, no trip. Not re-derived: the "46 class words" (the bus-wide count), the 15-minute end-time sweep, and the ledger counts the record already marks as hand-read.
- **Steps 4, 5 and 7.** The three-dot diff from the merge base lists 7 files: no VERSION, no manifest, no RELEASE_NOTES.md and no claim file. `## Head` names 6ad8089c14b50de2f6408ef6948a7d86ca4c52c2, which is the head I measured. 6ad8089c1 merges 384a0e8cd into e53fee367, with an empty diff from 384a0e8cd. `SWEEP-INPUTS-IDENTICAL` re-prints between dc422d6f2 and 384a0e8cd (ev/head_structure.txt).
- **Merge-tree (step 13).** `git merge-tree --write-tree origin/main 6ad8089c14b50de2f6408ef6948a7d86ca4c52c2`, with origin/main at c409c9b18, is clean: exit 0, tree d600c028b870 (ev/merge_tree.txt).
- **Carry audit over the body.** `carry_audit.py --roster-ref origin/handoff/audit-r10-roster check --body` prints `CARRY-AUDIT: 1 finding item(s): 1 routed, 0 unrouted, 0 bad destination(s)`, rc=0, at roster 33138bc2f49b (ev/carry_audit_body.txt). R10-ORCH-MACHINERY and R10-FLOW-YIELD-PROBE are both groups on origin/main's roster (ev/roster_groups.txt). The b8b28b28 carry states its control as a precondition (step 10).
- **CI on this head (step 11).** I read 36 check-runs at 09:46Z (ev/check_runs.tsv):
  - 23 success, 7 skipped, 1 neutral (CodeQL), and 3 in progress (`Analyze (python)`, `closures`, `coverage`);
  - both `pr-contract` runs succeeded;
  - 2 failed: `instrument-self-tests`, which is this PR's (under Block), and `nightly-status`. `nightly-status` grades main's scheduled run and is not this PR's. The body answers it, it is not a required check, and it does not block.

RESULT selftest=96/0 sweep=2333/2286/47_disposed/0_undisposed hand_mutants=30 killed=18 survived=12 survived_moving_quoted_figures=2(H1_GROUP_RE,H9_product_prefix) disposed_checked=47 not_equivalent_on_all_inputs=3(nonce31,cdf<=,window_rsplit) record_figures=all_but_threshold_sentence(4/30_trips) null_bundle=identical carry_audit_body=0_unrouted merge_tree=clean ci=instrument-self-tests_red(ref_privacy:review_strength.py:854),nightly-status_red(main),3_in_progress round=5
