prepr's step 7 (`body_line`) and step 7c (`reds_line`) reported a refused body check by its count line alone unless the refusal was an unnamed red, and step 7 appended its budget verdict to that line, so a body refused for a prose `## Friction` line read `PR-BODY: N error(s) ... -- no budget leaf raised`, which looks like a budget refusal. The roster brief for R10-FLY-BUDGET-LEAF (origin/handoff/audit-r10-roster, `dev/programme/rosters/wave-r10-groups.json`) records three such refusals, on #2545, #2558 and #2582; those refused bodies have since been rewritten, so the three are recounted from that brief and not re-derivable from the tree.

One helper, `body_refusal`, used by both callers, prints the red gate's own sentence when a red went unnamed, else the first `ERROR` line `policy_lint.mjs --pr-body` printed, else the count line, followed by `(N error line(s) in all)`, N being `grep -c 'ERROR'` over that output.

This round answers the review of `400e15d27`: the precedence of the red's sentence over an earlier `ERROR` line, and the count suffix, were unpinned (review mutants 2 and 3 survived). Two rows now pin both, one at each call site, and every order permutation of `body_refusal`'s three alternatives is killed.

## Head

`cfdd9c26cd388d242fafdaaa6f5e8761f8fbe65e`, the code head measured below. It adds one commit, the two both-grounds self-test rows in `tools/pr/prepr.sh`, to `53ae6a8ca82604704f6144990137355334424305`.

`53ae6a8ca82604704f6144990137355334424305` merges origin/main `93e6a63d2855651448a2b8f677b392feddc03c99` (#2557) into `400e15d277c7fb7c9e27aa1c203de282e0c51c4f`, with no conflict and nothing resolved.

`400e15d277c7fb7c9e27aa1c203de282e0c51c4f` added this PR's own row, `dev/programme/delivery/2591.md`; `47e03696d9230aa21e13823b554860a28ae84b4b` merged origin/main `302f66571`; `c3d66bca3f161d15b7df440c01ff982a58902e5e` is the authored code head carrying `body_refusal` and its first two rows.

## Mutation proof

Each mutant is one edit of `body_refusal` in a fresh worktree, then `bash tools/pr/prepr.sh --self-test`. A mutant's killing rows are the rows that pass on its unmutated tree and fail on the mutant. The alternatives are R (`grep -m1 'does not name it'`), E (`grep -m1 'ERROR'`) and T (`tail -1`); the shipped order is RET.

| mutant | at `cfdd9c26c` (new rows) | at `53ae6a8ca` (before them) |
|---|---|---|
| none (RET) | 312 ok, 5 FAIL | 308 ok, 5 FAIL |
| ERT (review mutant 2) | 310/7: both new rows | 308/5: survives |
| ETR | 310/7: both new rows | 308/5: survives |
| RTE | 310/7: the two Friction rows | 306/7: the same two |
| TRE, TER | 305/12: 7 rows, among them both new rows | 303/10 |
| SUFFIX dropped (review mutant 3) | 310/7: both new rows | 308/5: survives |
| BASE (`R \|\| T`, the fix reverted) | 310/7: the two Friction rows | 306/7: the same two |

The failing test came first: ERT, ETR and SUFFIX survive at `53ae6a8ca` and are killed at `cfdd9c26c` by exactly the two new rows, `and the refusal is the red's sentence, not the earlier Friction error, with both counted` (7c and 7). Restored, both pass.

## Null control

The 5 FAIL in every run are the same 5 rows in all 16 runs (the four `6b` rows and `and makes no serial --single call beside it`), each `no interpreter that parses the tree was found (tried the seat venv ...)`: this container has no seat venv. Since they are byte-identical across every mutant and both heads, they are environmental and move with no edit here; CI's `instrument-self-tests` carries the venv.

The new rows' null is the single-error rows: `unnamed-red.md` alone (red's sentence wins) and the prose-Friction body with its red answered (Friction ERROR wins) pass under ERT and ETR. Had the new rows been vacuous, ERT would leave the counts at 312/5.

The finder's harness at both ends, the refusal line over `policy_lint.mjs --pr-body` output with `--red 'fast (3.14)'` where the body carries a red: the merge base's expression (`grep -m1 'does not name it' || tail -1`) against `body_refusal` sourced from this head.

| body | merge base `93e6a63d2` prints | this head prints |
|---|---|---|
| fixture `bad-friction.md` | `PR-BODY: 1 error(s) in ...` | the `## Friction` line does not parse error, `(1 error line(s) in all)` |
| `unnamed-red.md` + prose Friction | the red's sentence | the red's sentence, `(2 error line(s) in all)` |
| fixture `unnamed-red.md` | the red's sentence | the red's sentence, `(1 error line(s) in all)` |
| fixture `good.md` (null, rc 0) | `PR-BODY: 0 error(s) in ...` | the same, `(0 error line(s) in all)` |

## Figures

- Self-test counts: the table under `## Mutation proof`. Rule: `grep -c '^  ok '` and `grep -c '^  FAIL '` over each run's output; killing rows are the diff of the `ok`/`FAIL` lines against the unmutated run at the same head.
- Class: the enumeration rule is every unordered pair of `body_refusal`'s alternatives gets a self-test body carrying both, asserting which wins, plus a sweep of every order permutation. Pairs: R over E is the new both-grounds rows (closed in this diff); R over T is `and the refusal is the red gate's own, naming the check` and its `budget-raise-gate` and `mutation` siblings (already guarded: TRE and TER are killed by them); E over T is `and the refusal prints the error, not only its count` and `... ahead of the budget verdict` (already guarded: RTE is killed by them). Permutations: 3! - 1 = 5, all killed (table above). The callers that report a `body_check` result as one line: `grep -n 'body_refusal' tools/pr/prepr.sh` returns its definition and two call sites, `body_line` and `reds_line`, and each carries one both-grounds row.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out`. The run_always lines: `env_drift.py --claims-only` ok, `closure.py selftest` passed, `layout.py` ok, `structure.py` `STRUCTURE RATCHET PASSED`; `harness_headers.py` fails with `No module named 'voluptuous'` at this head and at the merge base alike (no seat venv here).
- `git diff $(git merge-base origin/main HEAD)...HEAD --stat` names `tools/pr/prepr.sh` and `dev/programme/delivery/2591.md` only: VERSION, the manifest version, the release-notes heading, claim files and budgets are untouched.

## Red checks

`nightly-status`: failure on `400e15d27` and `47e03696d` (check-runs API per commit; `c3d66bca3` has no runs, and `47e03696d`'s other non-success runs are `cancelled`, superseded by the next push). It grades main's nightly run, and this diff touches none of its inputs (`tests/nightly_status.py` is not in it), so it is not this branch's red and no cheaper detector is owed. `53ae6a8ca` and `cfdd9c26c` are on `handoff/r10-fly-budget-leaf` only and carry no check run when this is written.

## Root cause

Trigger: a recurrence, three prepr refusals of the same printed shape (the roster brief's #2545, #2558, #2582); no check went red on this branch. Cause: `grep -m1 'does not name it' || tail -1` in `body_line` and `reds_line`, from R9-FR-12 (05ae6d239), written for the red-check refusal only, with the count line as its fallback. Process state (c): step 7 refused each body correctly, before the push; its report did not name the ground. Cost test: the countermeasure's standing cost is two greps on a refused body and four self-test rows; the defect cost each refusal a hand re-derivation of the error. Built.

## Forward-carry

none

## Friction

none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
