Fix review: merge def887d8905bee4d9ad39f06e75068df074362f4

bus-nonce: f27a5feab008496f61a54e9ee5061d0f
seat: review-2068

Round 4, the re-cut. Reviewer: review-2068 (opus). Round 3's verdict is unposted; this round supersedes it, and its file is kept as a record (evidence3/). Head measured: def887d8905bee4d9ad39f06e75068df074362f4.

## Step 12: the head, re-read at post time
The live head was re-read before publishing this verdict and is still
`def887d8905bee4d9ad39f06e75068df074362f4` (`gh pr view 2068 --json headRefOid`;
the PR body names the same head, contract step 7). The head has not moved since
the round-4 plants were run, so every number below is taken at this head and
none needed re-taking. `isDraft: true` — the orchestrator marks it ready; I did not.

## Step 11: the checks settled — the pending one the draft held open is green
Read from the commit's own `check-runs` API at this head (latest run per name;
42 records, 39 distinct names), at 08:47Z. Full table: `evidence/checkruns_def887d8_settled.tsv`.

- `coverage` — **completed, success** (check-run 113696177293, the very run that was
  `in_progress` when the draft was written; it concluded green at 07:14:18Z).
- `coverage-ratchet` — **completed, success** (113713288775, 07:14:38Z).
- pending = 0. Red = `nightly-status` only. Everything else is success or skipped.
- The three names with more than one run (`pr-contract`, `budget-raise-gate`,
  `arch-score`) are green on both runs, so there is no red-then-green to misread.
- All 17 required status contexts (ruleset on `main`) are **success at this head**.
  `nightly-status` is not one of them.
- `record` is `skipped`, not absent: `governance.yml:671` gates it with
  `if: github.event_name != 'pull_request' && ... != 'merge_group'`, so a PR head
  cannot carry it (#1144's trap does not apply). Same for the other skipped lanes.

## nightly-status: which arm
**Not this pull request's — its diff does not reach what it reads**
(`defect-root-cause.md`, the exemption at lines 142-148: their scripts, `tests.yml`,
`governance.yml`, the plan, `HANDOVER.md`, or a row it did not add). Measured against
the 27-file three-dot diff (`git diff --name-only 47b083b0...def887d8`; the merge base
is `47b083b03` because this head is the orchestrator's merge of that main into the
prior head; identical to `gh pr diff --name-only` — `evidence/diff_name_only_settled.txt`):

| the exemption names | in this diff |
|---|---|
| `tests/nightly_status.py` (its script; the job restores only this file from the base and runs it under `-I -S`) | no |
| `.github/workflows/tests.yml` | no |
| `.github/workflows/governance.yml` | no |
| the plan (`dev/programme/plan-*.md`) | no |
| `HANDOVER.md` (`dev/programme/HANDOVER.md`) | no |
| a delivery row it did not add | no — the only row it touches is `dev/programme/delivery/2068.md`, status `A` (its own) |

So the body owes it no answer, and it is not blocked. Its red is the orchestrator's on
`main` (fix the nightly lane and dispatch Tests on the default branch, or drain the
overdue rows). The body answers it anyway, at its line 151, with the same reading.

## Step 13: `mergeStateStatus: DIRTY` is measured, not a block
GitHub reports `DIRTY`. `git merge-tree --write-tree origin/main def887d8` (from a
checkout with both merge drivers installed; `origin/main` verified current against
`git ls-remote`, both `83f7ca55879097258b971d483345459f18629491`) exits **0** with tree
`921a5b444b47`, and its stderr is `LEDGER-MERGE: resolved tests/closures.json`
(`inert_reads.tests/harness_headers.py: merged as a set (536 entries)`) — `evidence/merge_tree_def887d8.txt`.

- No `MERGE-CLAIM: refused` line, and neither claim file is in the branch's diff:
  `tests/golden/claimed_drift.txt` and `card_claimed_drift.txt` are byte-identical at
  head, at the merge base and at current `main`. A branch that claims nothing leaves
  both files alone, and it did. Nothing conflicts on any path, so nothing is blocked here.
- The `DIRTY` is GitHub's, computed where the drivers cannot run: `tests/closures.json`
  is changed on both sides (head `a379f966`, main `ca36c9b2`, base `55e5360b`), and the
  ledger driver resolves it key by key. That is the known "DIRTY cannot run, it is not
  red" shape, and the orchestrator's, not a defect in the authored work.
- For the carry predicate (`orchestrator.md` §11): because `tests/closures.json` **is**
  in this branch's own diff, a head that merges current `main` will differ from the head
  I measured on a file the branch owns — so that update is a **resolution delta for this
  same reviewer**, not a carry. `run` (merge main in, CI green again) is the right path.

## Plants through the base-run gate
The gate runs from a worktree of def887d8, as arch-score.yml runs it (`python3 -I` from the base). Logs and patches are in evidence4/.

| Plant | Result |
|---|---|
| P0, control (import cycle) | FAIL, dS -2.7550, rc=1 |
| P5, both cycle modules as `.py` symlinks to `.txt` blobs | `FAIL: refused, custom_components/heatpump_optimizer/review2068_a.py is a symlink at 9d0b004b534a`, rc=1 |
| P6, the cycle modules mode 100755 | FAIL, dS -2.7550, rc=1 (measured like 100644) |
| P7, a gitlink under the package | `FAIL: refused, custom_components/heatpump_optimizer/review2068_sub is a gitlink`, rc=1 |
| P2, nested `.gitattributes` export-ignore (round 2) | FAIL, rc=1 |

Python does import through a `.py` symlink (`r3_symlink_import.txt`), so refusing links rather than resolving them is right.

## The entry-type class is closed
- `ls-tree -r` can return four entry modes under custom_components/: 100644, 100755, 120000 and 160000. Trees recurse.
- The first two are extracted and measured. The last two are refused by name, on either side of the comparison.
- A case-only rename is not a route: the runner's filesystem is case-sensitive, so both names are extracted.
- A non-UTF-8 path raises an uncaught exception, which exits non-zero, so it fails closed.

## Earlier rounds, still holding
- Round 1: the gate and tests/structure.py run from the base worktree. `python3 -I` keeps the head out of sys.path and env.
- Round 2: the extraction reads tree objects, so `.gitattributes` cannot hide a file.
- Round 2's two reds are gone at this head: `instrument-self-tests` and `fast (3.14)` are both success (re-read in the settled table).

## Notes, not blocking
- **Wedge risk.** The refusal also fires on the base side. If a symlink or gitlink ever reached custom_components/ on main, every PR's arch-score would go red. Re-derived at current main `83f7ca558`: `git ls-tree -r --format='%(objectmode)' origin/main -- custom_components/` gives 91 x 100644 and **0** of 120000/160000, and the head is the same 91 x 100644. This gate refuses any PR that adds one, so only a ruleset bypass could put one there.
- **Known-open candidate for planted/redteam.** A `.py` that loads a `.txt` at runtime (`exec`, or `importlib.util.spec_from_file_location`) hides that code from any AST scorer. It is not an entry-type hole, and the loader call is visible in review.
- **My own mutant.** I did not mutate the round-4 tests myself (arch_score.py is heavy). The refusal is demonstrated end to end by P5 and P7 above, and CI's `fast (3.14)` at this head is green.

## Not verified
- The C12/C13 mutation proofs: heavy, CI's (`mutation` is green at this head).
- The red-team sweep's count of 11.
