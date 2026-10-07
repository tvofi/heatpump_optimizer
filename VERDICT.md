Fix review: merge a6f9c3e94ad5c10d062440a61b864ce49ee843d3

bus-nonce: cfb056c5704520fd7909a461fd35e2c2
Round 1. Reviewer measured head a6f9c3e9 (live head re-read at posting: unchanged). Standalone clones, nothing in a shared worktree.

Count (step 8). Re-ran replay.sh in a standalone clone over the PR's 27 merges, then enumerated independently across all remote refs (280 now, 268 at authoring) with my own both-sides rule: 28 = the PR's 27 plus 666b2f8e, the PR's own main-merge made after the count. The 27 are the same set. without: 27 merges, 4 conflicted (dfe2bb79 82af801a af62b2b8 e62b8b63), 23 merged JSON-equal and byte-equal. with: 0 conflicted, 27/27 JSON-equal to recorded.
Driver vs hand resolutions: all four JSON-equal. 82af801a and dfe2bb79 are bytes-differ; I confirmed that is only the order of the two new _rca entries (same key sets, rest of file equal). The other two bytes-equal.
Null control: the 23 clean-without merges give identical (json, bytes) results in the with arm (diff empty). with arm: 16 LEDGER-MERGE resolved, 5 never invoked, 6 fell back to text merge: matches the RCA.
Mutations (self-test, base all passed): class-refusal disabled, ensure_ascii=True, register as "sum", RAW=set() each rc=1 with the named check FAIL; .gitattributes line removed fails ".gitattributes routes every ledger to the driver". Tree restored.
Class records still conflict (real git, driver installed, real register copy): two branches each adding a P1 instance with total+1 -> LEDGER-MERGE refused, conflict (no silent merge). P1+P2 on different branches resolves with consistent counts; _rca+_rca resolves, both land; P1 instance on one side + _rca on the other resolves; a branch changing P1 and adding _rca against one changing P1 refuses.
RCA doc vs root-cause.md: cause (tail-append of a shared key, ledger driver never routed to register), process state (d) with the change date and why (b) is wrong, cost test with numbers (25-26 min x P(recurrence), 0.08 s), recorded refusals (generic detector, split register) with reasons, limitation stated honestly (GitHub still DIRTY, applies to branches cut after landing). Forward-carry stated as not established, with no stage owning it; acceptable as a candidate, not a precondition on a later stage.
merge-tree against current main: clean, rc 0. No VERSION, manifest, notes, golden, claim, budget or closures file touched.

CI at head a6f9c3e9 (check-runs API): everything completed is success or skipped except: delivery-status failure (not required; log says 4 unread rows for other PRs, the PR adds a row and deletes none, not this PR's); nightly-status failure (main's, not reached by the diff); budget-raise-gate cancelled with a success twin on the same head (orchestrator: confirm the twin counts per cancelled-budget-gate-blocks-merge note). closures, coverage, Analyze (python) were still in_progress when read; the merge train's CI gate must wait for them. The body's "none at authoring" is therefore not contradicted by a red this PR owns.

Not verified: the 0.08 s timing and the Tests wall times; entities/structure were not re-run locally (CI's).
Evidence: /Users/timmalmstrom/hpo-seats/review-2040/evidence (replay logs, mutation outputs, two-branch script and outputs, checkruns.tsv).
