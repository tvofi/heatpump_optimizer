Fix review: merge ea5f660303823ce04ed55af4022b4f7064ee403e

bus-nonce: 393597344df1a6c95b4c1280a13dcad9

PR #2575, group R10-CI-RATCHET-WINDOW (fly-in R10-FLY-CI-RATCHET-WINDOW), branch fix/r10-ci-ratchet-window. Round 1: this is the first review of this head.
Head measured: ea5f660303823ce04ed55af4022b4f7064ee403e. It was still the PR head at the final read (origin/fix/r10-ci-ratchet-window = ea5f660303823ce04ed55af4022b4f7064ee403e). origin/main was 49c222280d46.
Roles current: `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty.

## RESULT lines (reviewer's own)
RESULT step1 mutation proof: my own mutants of the head's gather step (ev/reviewer_mutants.txt). Each runs entities.py's own R10-FLY block verbatim (ev/crw_driver.py) against a mutated tests.yml. They cover the PR's named M1 (`|| true` on the listing, R3) and M4/M5 shapes (cap, exclusion via R7/R9), plus the M2 shape through the full-entities anchor below. Killed: R3 (`|| true` on the listing), R4 (pre-cap sort dropped), R5 (`set -euo pipefail` deleted), R6 (`cat` in place of `jq -s add`), R7 (run id taken from .run_id only), R9 (cap 16).
RESULT step1 anchor: one full `tests/entities.py` run with the unfiltered listing restored gives `1 of 2377 ENTITY CHECKS FAILED`, rc=1, the aimed by-name check (ev/entities_mutant_unfiltered.txt). The unmutated head gives `ALL 2377 ENTITY CHECKS PASSED`, rc=0, 10m59s (ev/entities_head.txt). Both on a Python 3.13.16 venv from the hash-pinned tests/requirements-ci.txt.
RESULT step1 survivors (non-blocking, traced): 4.
- R1, deleting `unique_by(.run)`: the stub has one artifact per run. There is no realistic path: upload-artifact v4 names are unique per run and no upload step sets `overwrite`. Re-run attempt 2 of run 39611184226 still holds exactly one artifact per ci-metrics-* name (MCP list_workflow_run_artifacts).
- R8, deleting the `expired == false` filter: a pre-existing line, unpinned at the base too. The window spans hours against 7-day retention.
- R10, deleting the `: > lanes.json` truncation: RUNNER_TEMP is fresh per job.
- R2, `|| true` after `jq -s add`: jq only sees arrays the listings already validated.
None of these warrants code.
RESULT null-control: the base's step text placed into the head tree fails both new checks: rc=1, `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`, listings=['repos/o/r/actions/artifacts?per_page=100'] (ev/reviewer_mutants.txt, tail).
RESULT finder-harness both ends (step 2/9): there is NO committed finder harness. The roster (origin/handoff/audit-r10-roster f424d993) has no R10-FLY-CI-RATCHET-WINDOW row; the body says the orchestrator registers it. The nearest row, R10-CI-RATCHET-RED (in-progress, handoff/r10-ci-ratchet-red), describes this same defect in its resume note ("reproduced locally, rc 1 and 0 bytes on one attempt in three"), with no committed instrument; its control is "ci-ratchet green on the fix head and on main after merge".
- The production instrument at the baseline: main push run 39611184226, job 119281753833, logs `unexpected end of JSON input`, then `JSONDecodeError: Expecting value: line 1 column 1 (char 0)`, exit 1 (read via the job-logs API). The ci-ratchet job runs only on main pushes, so it cannot run at the PR head before merge.
- I therefore built my own instrument, disclosed as mine and not the finder's: ev/rev_harness.py. It is an independent bash stub of gh with real jq, and it models production's signature. ev/reviewer_harness_both_ends.txt:
  - base e9febe62, mode=empty (production signature): rc=1, traceback=True. The defect reproduces.
  - head, mode=empty: rc=1, traceback=False, gh_msg_surfaced=True.
  - head, mode=fail_unfiltered: rc=0, window 45. The unfiltered query is no longer issued.
  - head, mode=fail_one (one lane answers 502): rc=1 after 2 listings, no window read. The fail-loud holds per lane.
  - head, mode=ok: window 45, 3 listings.
RESULT class (step 6): I ran the body's rule (grep for gh api / gh run download / || true within the ci-ratchet job, lines 2866-2975) at the head. It returns exactly the 4 seams the body dispositions: per-lane listing (closed), `run download || echo`, zip download `check=True`, runs listing (fails loudly). Widened to the whole tree (ev/class_wide.txt), the only other actions/artifacts listing is tests.yml:2568, already filtered `?name=closure-recordings-tree-$TREE`. Class closed.
RESULT merge (step 13): `git merge-tree --write-tree origin/main ea5f660303823ce04ed55af4022b4f7064ee403e` gives d5c2aa3a6bf8, rc=0, no conflict, no MERGE-CLAIM line (ev/merge_tree.txt).
RESULT claims/version (steps 4-5): claimed_drift.txt and card_claimed_drift.txt are byte-identical to the merge base. VERSION, the manifest and RELEASE_NOTES.md are untouched. No golden fixture moved: the diff touches only tests.yml, entities.py, closures.json, one dev/audit harness and the delivery row.
RESULT cheap checks at head (ev/cheap_checks.txt): `STRUCTURE RATCHET PASSED`; `ALL 109 HARNESS HEADER CHECKS PASSED`; `ALL 124 closure shrink pins PASSED`; `Architecture score: dS +0.0000 NULL`; tmp_paths `0 refused`; env_drift claims-only ok.
RESULT carry/head (steps 7, 12): the body names head ea5f660303823ce04ed55af4022b4f7064ee403e. merge-tree(d0c4989f, e9febe62) = 8e64c7f9 = tree(b66251e2), so the merge is automatic as stated, and ea5f6603 adds only dev/programme/delivery/2575.md. c4c5db7b differs from d0c4989f only in the closures.json entry, as stated (ev/carry.txt).
RESULT step 14: the only moved instrument number is one closures.json inert_reads entry, harness_headers.py reading the new dev/audit/harnesses file, beside its sibling r10_ci_layout_p0_mutants.py. It is earned by the new file. No budget moved; dS=0.
RESULT step 15: the added lines respect the architecture. LANES is single-sourced and cross-checked against both the upload steps and ci_ratchet.LANES.
RESULT forward-carry (step 10): the body says n/a, and I find no later-stage brief this changes. The overlap with R10-CI-RATCHET-RED is noted below for the orchestrator.

## Figures I could not re-derive (step 8)
- "~18,000 artifacts", and the live window counts: 45 artifacts / 24 runs / 15 per lane at the head, against 39 / 23 (closures 12, coverage 12, fast 15) at the base. Not verified: this container's gh token is invalid and the MCP has no repo-wide artifacts listing. My stub harness reproduces 45 at both ends only as a property of the jq, not of the live repository.
- "Per-lane listings answered 200 on every call": not verified, for the same reason.
- The fixer's own harness run (`RESULT survivors=0`, M0-M5) I did not re-run. I re-cut the mutants myself instead (above).

## Step 11 (red checks)
Read the check runs once at the end (ev/check_runs_final.txt). Still running: `closures` (required; started 16:30:59Z). I judge on the rest.
- `nightly-status` is red. It grades main's scheduled run 39563978649 (mutation-nightly, slow), and this diff does not reach what it reads, so it is not this PR's. The body names it under ## Red checks, so the trigger is answered.
- The body's explanation of that red is factually wrong. It says nightly-status "reads the same red" and "clears once ci-ratchet is green on main", but its log names only mutation-nightly and slow; ci-ratchet is not involved. Per step 11 I check that the trigger was answered, not the answer, so this does not block; the orchestrator should not expect nightly-status to clear on this merge.
- No other check at this head went red. pr-contract passed twice, at 16:09:17Z and 16:11:10Z; the second started after the head's push.
- The mutation lane is green, but the diff writes no production code line, so it drew no mutant.

## Notes for the orchestrator (non-blocking)
1. There is no committed finder harness (step 9), and the R10-FLY row is not registered. My instrument (ev/rev_harness.py) is offered for landing if the orchestrator wants one.
2. Overlap: roster group R10-CI-RATCHET-RED's resume note owns the same JSONDecodeError path. It says "the retry and never-read-empty rule belong in tests/ci_ratchet.py", and its fixer is on handoff/r10-ci-ratchet-red. That group's routing should be reconciled with this merge, so the two fixes do not collide in tests.yml's gather step.
3. Code-owned path (.github/workflows/): the merge still needs @tvofi's approving review.
