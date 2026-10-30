Fix review: blocked 5a1d1e09740585d62cf87756ff3c5a4b89ef1d94 stale-reference: #2952 survives in the record at lines 8 and 247 and in the body's Delta section, against the brief's no-surviving-reference check

bus-nonce: 4f4c7ddf438cbb8ff289b979c696f1a3

## Block

Round 9. The dispatch brief made this a check: "no reference to carry-2952.json or #2952 survives in the diff or body". At head 5a1d1e09, `carry-2952.json` is gone from the tree (`git grep carry-2952 HEAD` returns 0 hits). `#2952` is still there:

- `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md:8` says "review round 7 filed #2952 as the destination of section 7's open jobs". Section 7 now names the roster group as the destination, so the record's opening paragraph contradicts its own section 7.
- `dev/audit/rca/R10-RCA-PREPR-HEAD-GRADERS.md:247` says "the roster group R10-FLY-CIPREDICT-RESTORING (#2952)". A reader who follows #2952 lands on an issue whose body still says "Destination brief: `dev/programme/carries/carry-<this issue>.json`, written by #2925". This head deleted that file.
- The PR body's `## Delta since the last body` names both `carry-2952.json` and `#2952`.

Repair: in the record, point line 8 at R10-FLY-CIPREDICT-RESTORING and drop the `(#2952)` on line 247. Rewrite the body's Delta section so neither token appears. No code needs to change. Whether #2952's own issue body should be updated is the orchestrator's call, not this PR's.

## Findings

- Wording drift between the body and the roster brief. The body and record section 7 say the group's brief carries "the unmeasured instances as the precondition". At roster 0cdedcc9c, the brief's `Precondition:` is the partial local run of `budget-raise-gate` (it reads live reviews), and the unmeasured `pr-contract`/`budget-raise-gate` instances appear under `Control:`. The content is carried, but under a different label. Fix the record and body wording in the same repair. Carry: R10-RCA-PREPR-HEAD-GRADERS

## Evidence

- Head reviewed: 5a1d1e09740585d62cf87756ff3c5a4b89ef1d94 (`ev/HEAD.txt`). Still the branch head at post time (`ev/head-at-post.txt`). The PR body's `## Head` names this SHA.
- Role contract: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so the contract is current.
- review_carry.py f2daca863 HEAD: FRESH-REVIEW. The one branch-only code commit is 34abdd2ea, and it touches only the record (5 lines), `carry-2952.json` (deleted) and `tests/closures.json` (1 entry removed). Arm code is byte-identical to f2daca863: `git diff f2daca863 HEAD -- tools/pr/ci_predict.py tools/policy dev/audit/rca/prepr-head-graders` printed 0 lines. So the code fix was not re-reviewed beyond the mutation re-run below.
- Mutation re-run (`mutants.py .`, `ev/mutants.txt`): M1 to M5 each fail the named cases, as the body states. Unmutated: `ci_predict.py --self-test` prints `ci_predict self-test: 0 failed`, rc 0 (`ev/self-test.txt`).
- Forward-carry: roster 0cdedcc9c is an ancestor of origin/handoff/audit-r10-roster (e94a16609). The brief for group R10-FLY-CIPREDICT-RESTORING (`ev/roster-0cdedcc9c.json`) contains the enumeration rule as Control, "Refused: listing the three jobs by name", a Precondition, and a Re-measure step with a plant per job and an unplanted null. The packet's carry_audit printed `2 routed, 0 unrouted, 0 bad destination(s)`.
- merge-tree --write-tree origin/main HEAD: rc 0, no conflicts (`ev/merge-tree.txt`). VERSION, the manifest and RELEASE_NOTES.md are not in the three-dot diff (`ev/three-dot.diff`).
- CI on this head (check-runs API, read at review): `tests / nightly-status` is failure. The body answers it as main's: the diff touches no workflow, test or production file that check reads. Every other completed check is success, skipped or neutral. `tests / closures`, `tests / coverage`, `tests / fast (3.14)`, `governance / instrument-self-tests`, `codeql / Analyze (python)` and the pr-contract run's prelude were still in progress, and no `pr-contract` check had concluded. The red-check trigger was therefore not settled; this block does not rest on it.
- Body figures carried from f2daca863's arm code (keycount 584 merges, jobtime, plant.sh, entities 2471) were not re-taken here. The code is unchanged and the figure_lint packet resolved 8 of 8 commands at this head.
