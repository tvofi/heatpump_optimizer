# D13 round 9: verifier V2 (independent lens)

- Baseline: `1936d5ca72a06556eeed4e8e5bf3dea520e517e1`. Evidence tree: `/home/claude/wt-g1v2`.
- Box: G1-V2, 4 vCPU Linux, node 22.
- Every number here is a count over the finder's recorded snapshot (`tools/audit/round9/D13/s1/window.json.gz`) and over the local git history. Counts do not change with CPU contention. `load1` was 0.65–3.61 and `thread_factor` was 1 (no numpy).
- GitHub was not read. Where a claim rests on a live API answer, such as the 404s on #1097–#1165, I voted on the recorded snapshot and say so below.

Harnesses are in `tools/audit/round9/D13/verify-v2/`: `v2_enum.mjs`, `v2_reverify.mjs` and `v2_blocks.mjs`. Each has a header giving its metric, command, expected value, SHA and machine.

## Step 1 precondition: `enum_gap.mjs` depends on `origin/main`

The finder's `enum_gap.mjs` reads `v6.6.0..origin/main`. In this worktree `origin/main` is `db878b29`, which is newer than the snapshot. There the harness prints `stats_window_merges=0 subject_merges=256 gap=256 gap_marked=1`: the stub answers 404 for the extra commits and the enumeration aborts.

To re-run it, I made a `--shared` clone with `refs/remotes/origin/main` pinned to `1936d5ca` and the D13/s1 folder copied in. I removed the clone afterwards.

This is a reproducibility defect in the harness, not in the finding. A re-run needs `origin/main == 1936d5ca`. `yield_rounds.mjs` has no such dependency.

## D13-s1-01: API-mode `--stats` silently drops 52 merges

**Step 1: finder's harness, re-run in the pinned clone**

| Arm | `stats_window_merges` | `subject_merges` | `gap` | `gap_marked` |
|---|---|---|---|---|
| Baseline | 201 | 253 | 52 | 0 |
| `drop:8cca77bc` | 200 | — | 53 | 0 |
| `restore` | 253 | — | 0 | — |

- Baseline `load1` was 3.61.
- In the `restore` arm, `STATS COVERAGE` reads 188 of 253.
- Result: reproduced exactly.

**Step 2: my own metric.** The set of PR numbers that production `enumerateMerges` delivers, compared with the first-parent subject numbers over `v6.6.0..1936d5ca`. I used the explicit SHA, not `origin/main`. `enumerateMerges` is not exported, so the harness cuts its source out of `policy_lint.mjs` and evaluates it.

| Result | Value |
|---|---|
| `first_parent_commits` | 267 (0 missing from the snapshot) |
| `subject_merges` | 253 |
| `api_enumerated` | 201 |
| `dropped` | 52, PRs #1097..#1165 (the finding's title says #1098; the finder's own 404 range starts at 1097) |
| `dropped_two_parent` | 52: all are real two-parent merges |
| `api_only_not_subject` | 0 |
| `skipped_total` | 66 (52 dropped + 14 stamps, one undifferentiated skip) |
| `silent_skip_lines` | 0: no `console.log` in `enumerateMerges`, `fetchPullsBySha` or `mergedPRsFromWindow` |
| `subject_mode_count` | 0: the offline fallback's end-anchored `(#N)` recovers none |
| `api_with_subject_fill` | 253 |

- Perturbation `V2_PERTURB=body` replaces the production `continue` with a subject fallback, in memory. It moves `dropped` from 52 to 0.

**Attacks**

- Contention: none applies, since these are counts.
- Gate mode: not applicable.
- Grid artefact: none. The claim is one set difference.
- Null control: holds. Subject-fill gives 253, so the gap is exactly the empty-row commits.
- Reachability: the population is the one `cmdStats` prints, and it is reached through the CLI.
- Severity: `medium` is D13's own rule for an instrument that cannot compute its own metric. The coverage denominator reads 201 against 253 real merges, with no marker.
- The 404 of the dropped PRs' records was measured live by the finder and is not re-measured here. The vote rests on the recorded empty `/pulls` rows and on git.

**Vote: verify, medium.**

## D13-s1-02: 22 re-verification rounds caught 0; 12 heads moved only by merges or `ci:` commits

**Step 1: `yield_rounds.mjs`**

| Result | Value |
|---|---|
| `reverify_rounds` | 22 |
| `reverify_blocked` | 0 |
| Moved by merges only | 11 |
| Moved by `ci:` commits only | 1 |
| Moved by branch content | 10 |
| `prod_reverify` / `repair` / `repeat` | 22 / 21 / 6 |

- `block_one_reverify` gives `reverify_blocked=1`.
- Result: reproduced exactly (`load1` 3.40).

**Step 2: my own metric, under the finding's own phenomenon property** ("a head move that leaves the branch's diff against its merge base unchanged"). For each re-verification round I compared the branch's net diff at the old and new head. The net diff is `git diff $(merge-base <head> <M>^1) <head>`, where M is the PR's merge commit. It is keyed two ways:

- `git patch-id --stable`, which includes context lines;
- a context-free key: the sha1 of the `-U0` file headers and +/- lines.

| Result | Value |
|---|---|
| `reverify_rounds` | 22 |
| `reverify_blocked` | 0 |
| `reverify_net_diff_equal` (patch-id) | 3 |
| `reverify_u0_plusminus_equal` | 4 |
| `finder_no_content_rounds` | 12 |
| …of which keep the `-U0` key | 3 (#1433, #1592, #1594) |
| `changed_rounds_later_blocked` | 0 |

- The other 9 of the 12 merges-only or `ci:`-only rounds change the branch's net diff. Examples: #1349 in `tests/golden/claimed_drift.txt` (22 lines to 16), #1610 in `tests/mutation_budgets.json` (109 to 101), and #1282, where one claim line differs. These are ledger-file merge resolutions and bot re-records, which is what a reviewer reads.
- Perturbation `V2_PERTURB=flip` moves `reverify_blocked` from 0 to 1.
- An earlier draft keyed the merge base on the baseline. That gives an empty diff for every head, because every head is an ancestor of `1936d5ca`. I corrected it to `<M>^1` before taking the numbers above.

**Attacks**

- Contention: none applies (counts).
- Grid artefact: the 0 of 22 is a single count. Its 95% upper bound on the catch rate is about 13.6% (rule of three).
- Null control: holds. Repair rounds number 21 and first verdicts blocked number 16 of 188, so the mechanism does catch in other arms.
- Consequence: re-verification costs rounds and catches nothing in this window. That part stands.
- The finding's quantified proxy does not stand. It says 12 heads moved without changing anything, and it scopes its fix as a diff-equivalence check. Under the finding's own key that check carries only 3–4 of 22 rounds, because merges of `main` rewrite ledger files the branch also touches.
- Severity: the recoverable cost that the stated fix reaches is 3–4 rounds out of 237 parsable verdicts in the window. That is below D13's `high` bar for what the fix can save, though the 22-against-0 comparison itself still meets it.

**Vote: weaken, medium.**

## D13-s1-03: body-answer blocks (8) exceed every engineering class (max 1)

**Step 1: `yield_rounds.mjs`**

| Arm | Blocked | Body-answer | Max engineering class | Record-and-body / engineering / orchestration |
|---|---|---|---|---|
| Baseline | 21 | 8 | 1 | 12 / 7 / 2 |
| `rca_to_harness` | — | 7 | 2 | 11 / 8 / — |

- Result: reproduced exactly.

**Step 2: my own metric.** Every `<word>:` class token on a blocked verdict's first line, not only the first word the production regex captures (`v2_blocks.mjs`).

| Result | Value |
|---|---|
| `blocked_total` | 21 (same population) |
| `body_answer_any` | 8 |
| `body_answer_only` | 5 |
| `body_answer_with_engineering_class` | 3 (#1559 ×2, #1561: `harness: class-open` and `regression:` beside `root-cause-unanswered`) |
| `eng_class-open` | 4 |
| `eng_harness` | 3 |
| `eng_class_max` | 4 (finder: 1) |
| `verdicts_naming_any_engineering_class` | 10 (finder's engineering bucket: 7) |

- Perturbation `strip` moves `body_answer_any` from 8 to 7.
- The body-answer class still outnumbers any single engineering class: 8 against 4. The rounds a body check could have removed outright number 5, against 4.

**Attack: the mechanism statement is false at the baseline.** The finding says the predicate is "enforced only by the fix reviewer" and proposes a pr-contract check that lists failing check runs and refuses a body that names none of them. That check already exists:

- `.github/workflows/pr-contract.yml`, step "List the red checks at this head", passes `--red` to `policy_lint.mjs --pr-body`.
- `checkPrBody` then errors with "check `<name>` is red and `## Red checks` does not name it".
- `redHistoryForHead` widens the list over the branch's commits.
- History: #956 wired it in CI at `cccf37fb` on 2026-09-15, and `a07dd57d` added the red history on 2026-09-19. Both predate the window start, `v6.6.0` on 2026-09-17, or fall inside it before every counted block.
- `prcontract_reads_red=1`.

What the existing check misses is ordering. The 8 blocks name `typing`, `fast (3.14)` and `mutation`. Over every PR's final head in the snapshot, measured against the first pr-contract run at that head:

| Check | Heads where it completed after pr-contract |
|---|---|
| `typing` | 200 of 201 |
| `fast (3.14)` | 201 of 201 |
| `mutation` | 195 of 201 |

pr-contract triggers on `opened`, `edited`, `synchronize` and `reopened`, not on another check completing. So the mechanical check runs before the red it must name exists. The finding's proposed fix duplicates the existing check; the missing piece is re-running it after the slow checks conclude.

**Other attacks**

- Grid artefact: 7 of the 8 body-answer blocks fall on one day, 2026-09-24, one round-8 wave: #1559–#1563. That day also holds 19 of the 23 `^Fix review: blocked` lines. With that day dropped, body-answer is 1 (#1418) against an engineering class of at most 1.
- Null control: the population matches (21).
- Severity: the comparison survives narrowly (5 removable against 4) on one day's wave. The stated mechanism and fix scope are wrong at the baseline.

**Vote: weaken, medium.**
