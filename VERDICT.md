Fix review: merge 44ee0e5fde9cb744bfdd3ee1a7e8ba4d7e8cdb0e

bus-nonce: 90b38f9fa9267120fac24f297fda34b7

## Scope

Round 1 review of PR #2689 at head 44ee0e5fde9cb744bfdd3ee1a7e8ba4d7e8cdb0e (authored head 1dc67949505875052d731dfc297a71f816871630, base origin/main 50af6174f). Diff: dev/programme/triage/s6-batch2.md (+226) and dev/programme/delivery/2689.md (+1). Contract: dev/governance/roles/fix-review.md at origin/main (roles diff merge-base...origin/main is empty).

## Findings

- P46's Binding says every standing seat "already writes `<seat>.alive`"; no in-tree contract or instrument says so (`git grep alive -- dev/governance/roles/standing-*.md` prints only standing-tick.md:3, "keeps alive"), so the claim rests on out-of-tree session behaviour I cannot re-derive. The ruling still holds because the shared carry's item 3 makes touching the alive file a contract obligation in the same group, and its controls test the arm on fresh, stale and absent files. Carry: dismissed: item 3 of the same R10-ORCH-BEATD carry makes the alive file a contract obligation, so the arm does not depend on the unverified claim

## Evidence

- RESULT classification: tests/closure.py at head: is_inert True, is_gate_file False, is_handover False for both added files; orphan_files() names neither. INERT through the dev/programme/ prefix (closure.py line 273).
- RESULT destinations: R10-ORCH-BEATD, R10-ORCH-ROSTER-SCHEMA, R10-FLOW-TOOLKIT-MODEL, R10-FLOW-RECORD-PITCH (and the cited R10-FLY-PRUNE-REFS, R10-FLOW-DESIGN-STAGES, R10-CI-LAYOUT-P2, R10-FLY-RELAY-REVIEW-FF, R10-FLOW-MQ-PROBE) all exist in wave-r10-groups.json at origin/main, at 4c54758d7 and at the roster's current 2f3b013df. BEATD is not-started, files daemonize.py and tick_loop.sh, brief says "the supervised beat and its job table". RECORD-PITCH owns tools/audit/seat/record_row.py; ROSTER-SCHEMA owns roster_sync.py; TOOLKIT-MODEL owns roster_edit.py and replan.py. R10-FLY-STANDING-SEATS is absent, which the file says (a possible later split, not a destination).
- RESULT gate: roster_edit.ruling_verdict at head: P45, P46, P49, P51 ACCEPT; P47, P48 DEFER; P50 REJECT; P52 None. triage_refusal refuses a citation of #P47 ("not an ACCEPT ruling (DEFER)") and passes the shared carry and P49's carry text. This reproduces the body's null control.
- RESULT figures: 7 entries; 4 ACCEPT, 2 DEFER, 1 REJECT (body's rg commands, re-run with grep). P49: 14 record/autofix of 48 first-parent merges since 2026-10-23T00:00Z at origin/main 50af6174f, matching the file.
- RESULT citations re-derived at origin/main: sweep_template.md line 61 names train.sh, last touched by b16084794; orchestrator.md line 109 "Four standing seats do the routine work, never you inline"; pulse.py header lines 49-53 define the `<epoch> <text>` queue, STANDING at line 91, judge_queue at line 183, no file-liveness arm; roster_sync.py chosen at 239, DERIVABLE_STAGES at 88, norm_head at 201; replan.py touches_coordinator reads hot_files plus files at about line 205; `rg -i 'wait|background'` over standing-*.md prints only standing-tick.md:8; nightly.yml says the self-row "carries no merge SHA"; R10-FLOW-DESIGN-STAGES carries P-A (s4, accepted narrowed) verbatim, as P50 says.
- Not re-derivable here: the out-of-tree logs (r10s5/seat-ledger.md, state-beat.log, roster-report.txt, r10s6/sweep.md, seat-ledger.md, *-report.txt) and P50's per-seat token figures, which the file itself marks "not re-measured here". The file cites these logs by file and line, which proposal-triage.md allows.
- Cost/benefit: each ruling has Verdict, Source, Instances, Cost and Binding. Each ACCEPT names an existing group and its carry text. Each DEFER names its owner and what would change the answer. The REJECT names its binding cost. P49 accepts a measured benefit (14 of 48 main moves) and leaves the cause to measure first, inside a group that already rewrites that step; I read that as within "unmeasured benefit is DEFER", because the benefit is the measured part. P46 and P51 accept narrowed and reject the costlier variants on stated cost.
- Mutation: n/a, no production or check lines changed. The consumer gate was exercised as above.
- Merge: `git merge-tree --write-tree origin/main 44ee0e5fde9cb744bfdd3ee1a7e8ba4d7e8cdb0e` gives exit 0, tree 611b4cc9e (ev/merge-tree.txt).
- CI on 44ee0e5fde9cb744bfdd3ee1a7e8ba4d7e8cdb0e, from the check-runs API (36 runs, read about 08:19Z): none failed. Still in progress at read time: tests/browser, tests/fast (3.14), tests/closures, governance/instrument-self-tests, governance/env-matrix, one prelude. No pr-contract run appeared on this draft head. The body's "Red checks: none" holds at read time.
- VERSION, manifest and RELEASE_NOTES untouched (2 files in the diff). No claim files touched. Head in the body equals the reviewed head, and the PR API still reported it at post time.
