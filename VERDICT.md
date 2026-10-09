Fix review: merge 87849cd277485bd28bc85d64bc104293c5c7e6de

bus-nonce: 7537ca83302d69758d16e03ea3362ba1
seat: review-2010

This is round 6 by reviewer turns on #2010: 1 blocked `ace05371`, 2 merge `dc4e3f13`, 3 blocked-delta `d30236a5` (head-moved), 4 merge `6eafd3a5`, 5 merge `d67d8a44` (comment 6068544953), and this turn, which judges only the resolution delta `d67d8a44..87849cd2` under `fix-review.md` step 12's carry rule. Rounds 4-6 judged deltas, not repairs, and none returned blocked, so `fixer.md`'s fourth-round re-cut rule does not bind: nothing is owed of the fixer by this turn.

## The delta, measured

RESULT delta_merges=cdb7c38b,87849cd2 both "Merge remote-tracking branch 'origin/main'" (first-parent merges in `d67d8a44..87849cd2`; no authored commit)
RESULT authored_commits_identical=16 of 16 at both heads (`git log --no-merges mb..head`: eca1704a1, 495accb54, ace05371e, 5cb01b65b, 2ada816b5, 4f4e882c8, 13fc4a45e, c0a3e6413, c75b7770a, c79b4bddd, b78e58109, 217f7cefe, 57cac0889, b0f908603, 05bbf3932, 75a6aee4f -- the same 16 SHAs under both merge bases)
RESULT remerge_diff_content_lines=0 on both delta merges (`git show --remerge-diff`, with `claimnotes` and `ledgermerge` installed in this clone) -- each recorded tree equals a clean automatic re-merge, so the delta contains no hand resolution

**Task 1 -- the branch's own change is unchanged, with one exception, and the exception is the driver's rule.** At `origin/main` b2b6acd64, mb1 (for `d67d8a44`) = af79f2114 and mb2 (for `87849cd2`) = b2b6acd64 itself. Both three-dot diffs: 65 files, 1394 insertions, 101 deletions; sorted `--no-renames --name-only` sets equal (65/65, `setdiff=0`, no rename rows). Per file I extracted the branch's added and removed content lines only (`git diff -U0 mb..head -- f | grep '^[+-][^+-]'`) and compared the multisets.

RESULT files_whose_branch_lines_differ=1 of 65 -- tests/closures.json

That one file: the branch's two substantive additions, `"dev/audit/harnesses/ux5_idle_codes.py"` and `"dev/audit/harnesses/ux5_idle_codes_sites.py"` in `inert_reads["tests/harness_headers.py"]`, are byte-identical at both heads. The only other difference is one `recorded["tests/block_duty.py"].seconds` figure: the branch's diff read `2.8 -> 3.5` against mb1 and reads `2.6 -> 2.8` against mb2, because main re-recorded that figure and restructured the file in `af79f2114..b2b6acd64`. The head's value is the `ledgermerge` driver's own rule, not the branch's choice: `tools/merge/ledger_merge.py:38` -- "which no check reads for a decision, so it takes the larger" -- and `max(ours, theirs)` at line 301, 2.8 > 2.6. `closure.py:1552 stable_seconds` keeps a committed timing whenever a re-record is within 2x, so 2.8 and 2.6 are the same record for every consumer (sweep order, budget estimate, lazy-driver timeout floor), and neither is a cap. CI's `closures` is success at the head (113820807827). Step 14: earned, and not a budget -- `tests/closures.json` is not a `*_budgets.json`.

**Task 2 -- what main brought, and what it did not touch.** `b2b6acd64 ci: record nightly kills` writes exactly one file: `tests/mutation_ledger/killed_by/accuracy.py/AccuracyTracker.from_dict.GUARD_OFF.a5b6d221.json` (6 insertions), a ledger row for `AccuracyTracker`, which this PR's review does not read. The delta changed the blob of 5 of the branch's 65 files (`coordinator.py`, `optimizer.py`, `tests/entities.py`, `tests/features.py`, `tests/closures.json`) and left 60 byte-identical. The 4 code/test blobs differ by main's #1745 `EntryConfig` refactor, which is main's own work in those files (`161 insertions, 567 deletions` in coordinator.py; `23/71` in optimizer.py; `646/9` in entities.py; `80/73` in features.py). I intersected the branch's added-line set with the delta's removed-line set:

RESULT branch_added_lines_reverted_by_main=0 (the 2 text collisions in coordinator.py and optimizer.py are `    """` and `            ),`, common Python punctuation, not branch lines; the multiset equality above already proves every branch line survives)

The branch's only two config reads (`services.py:1041` and `:1044`, `stored.get(CONF_DHW_SETPOINT, ...)`, `...CONF_DHW_MIN_TEMP...`, at those same line numbers in both heads) bind `stored = {**entry.data, **entry.options}` -- a dict -- in both heads, and `services.py`'s blob is identical at both heads, so main's `effective_config -> EntryConfig` change cannot reach them. Main moved no file under `tests/golden/` in `af79f2114..b2b6acd64` (`count=0`) and no card input (`www/`, `card.mjs`, `narrative.py`, `plan_view.py`, `strings.json`, `icons.json`: none).

## Step 13 -- the conflict question

RESULT merge_tree=331422a25e2791e41756108a31c9c78e27259e8d exit=0 stderr_empty=yes (run at `origin/main` b2b6acd64 x 87849cd2 with venv python 3.14.7 on PATH so the driver's `python3` is not the 3.11 that mis-reports `no-copies`)
RESULT driver_markers=none (no `LEDGER-MERGE:` and no `MERGE-CLAIM:` line: the drivers run only on a conflicting file, and nothing conflicted)
RESULT github_reading=mergeable:true mergeable_state:clean -- matches merge-tree. This PR is not DIRTY. The train's `the branch's own diff differs` is its `carry()` comparing rendered diff text, and hunk context shifted by main's #1745 edits is what differs, not content: I measured the branch's own line sets above. That is an instrument observation for the orchestrator, not a defect in the authored work.

**Claim files, correcting the brief's premise.** The brief asked me to confirm both claim files are byte-equal to `origin/main`'s. They are not, and for this branch they must not be: R9-UX-5 claims drift (`tests/golden/**` is in its diff). What I measured instead: both blobs are identical between the two heads (`claimed_drift.txt` e37b16ef7d2d2d484e8be2ceb2469fd2e8c4b6f4, `card_claimed_drift.txt` 816d1eac221481ed81dba2ec9565a8ac2a14e425), so the delta moved no claim; versus main each file is additions only (`git diff origin/main 87849cd2 -- tests/golden/` has zero `-` content lines), the 31 scenario claims plus the 2 card-state claims and their notes; `claims-for: 6.7.17` in both equals `VERSION` 6.7.17 at the head, which is main's own value too. Step 4 re-run at the new base: `PYTHONPATH=tests/hastub python3 tests/env_drift.py --all b2b6acd64` exited 0 with `NO UNCLAIMED DRIFT: 56 scenario(s)` and `NO STALE FIXTURE: 56 committed fixture(s)`, 31 CLAIMED / 20 MAY-DRIFT / 6 byte-identical -- disclosed honestly: that run printed `DRIFT BASELINE CACHE HIT -- the baseline was REUSED, not recomputed` (key 609f5a5b, tree b102e90e at b2b6acd64), so the baseline capture is a prior canonical one, not mine; and since main moved no golden fixture in the base shift, the claim-to-drift relation cannot have changed. `node tests/card_drift.mjs b2b6acd64` after `python3 tests/plan_view.py` (plan_view exit 0) printed `card_drift: 2 state(s) moved and claimed, 38 identical` -- the same two states, `tooltip_hover` and `shared_steps_hover`, as the previous head's measurement.

## Step 11 -- CI at the live head

RESULT check_runs_at_head=40 distinct_names=38 red_or_nonterminal=0 pending=0
RESULT required_total=17 required_ran_green=17 required_missing=0 required_not_green=0 (ruleset 23698884 `main-protect-checks`, read from the API, latest run per name)
RESULT governance_arm_all_present=briefs 113820701883, policy-docs 113820702358, closure-scope 113820701811, closures 113820807827, pr-contract 113820922918, typing 113820701809, env-matrix 113820702448, budget-raise-gate 113820701451 AND 113820701618 (both success -- round 2's cancelled twin is resolved)
RESULT mutation_at_head=success 113820701992 with baseline green: `mutation` at `origin/main` b2b6acd64 is success 113754752903, so this is not #1120's green-because-baseline-red case; the diff's own sites are pinned inside the diff (33 `killed_by` rows + 2 `survivor_triage` rows; the delta added 71 other `tests/mutation_ledger/` files from main's nightly runs but changed none of these 35 blobs -- they are among the 60 unchanged above)

Skipped at the head, all ordinary for this event: `slow`, `record`, `claims-autofix`, `closures-autofix`, `mutation-autofix`, `mutation-pins`, `mutation-ledger`, `mutation-ledger-push`, `mutation-nightly`, `mutation-pin-plan`, `nightly-ha`, `recheck-gate`, `record-autofix`, `delivery-status-publish`. Nothing is red, so step 11's trigger asks nothing new of the body; the body's `## Red checks` already names and answers each red the branch's range carried (`mutation`, `mutation-autofix`, `closures`, `closures-autofix`, `nightly-ha`, `delivery-status`, `nightly-status`, `env-matrix`, `typing`, `fast (3.14)`, `budget-raise-gate`). The head's runs are also the range's now: the delta adds only main's own commits, whose checks are main's.

## Step 5 / task 5 -- hygiene

RESULT VERSION=6.7.17 at af79f2114, d67d8a44, b2b6acd64 and 87849cd2 -- the delta moved no `VERSION`, no `hacs.json`/manifest version, no `RELEASE_NOTES.md` heading (`git diff d67d8a44 87849cd2 --name-only` names none of them; main's manifest is 6.7.17 at every ref I read)
RESULT budgets_in_branch_diff=0 (none of the 65 files is a `*_budgets.json`)
RESULT budgets_moved_by_the_delta=2, both main's: `tests/structure_budgets.json` DOWN (`max_class_loc` 9048->8817, `seam_cut_total` 766->760, `recorded_at` re-keyed to 2d8cab3f) and `dev/governance/config/policy_budgets.json` UP (`fixer.md` 295->315 lines, 4866->5216 bytes) from main's `9d9f44ad2 policy: step 17's rules as the tree holds them (#2064 round 1)`, already merged on main. That raise is not this PR's and did not pass through this PR: `budget-raise-gate` is success at the head (both runs). Naming it because the brief asked whether any budget moved up between the two heads -- one did, and it is main's.
RESULT structure.py_at_head=STRUCTURE RATCHET PASSED (venv 3.14.7, 16.5s; `duplication_copies 38 <= 38`, `max_class_loc 8817 <= 8817`, `seam_cut_total 760 <= 760` -- the head pays main's two tightened caps exactly, so main's lowering did not redden this branch)

## Step 12 -- the head, and two merge conditions that are the orchestrator's

`git ls-remote origin refs/heads/fix/r9-ux-actions` returned 87849cd277485bd28bc85d64bc104293c5c7e6de immediately before this verdict, and the PR's `head.sha` is the same. The body's `## Head` names 87849cd2 (written by `tools/audit/seat/update_pr.sh`) and says "an automatic merge by the orchestrator, no resolution. The reviewed code is unchanged" -- both sentences are what I measured. `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty (0 bytes), so this contract is current.

1. **The PR is `draft: true`.** The brief asked whether it is `draft=false`; it is not, and I left it as it is. It cannot merge until someone marks it ready. That is the orchestrator's move, not a verdict.
2. If `origin/main` advances again before the merge, re-test the train's carry: its `carry()` compares rendered diff text, and main's #1745 edits sit adjacent to this branch's lines in `coordinator.py`, `optimizer.py`, `entities.py` and `features.py`, so context shift will keep reading as "the branch's own diff differs" even when the authored lines are provably identical, as they are here.

Non-blocking, for the next body re-take: `## Red checks` reads the head at 2026-10-08T20:31Z and names `nightly-status` (113492436544) as the one non-green check; at the live head `nightly-status` is success (113820701393) and `delivery-status` success (113820702568). The body is stale in the direction of being harsher than the tree, so nothing goes unanswered.

Evidence: /Users/timmalmstrom/hpo-seats/review-2010/evidence
