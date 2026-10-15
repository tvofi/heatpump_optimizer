Fix review: merge c40d1ee872b2481b272cbef5dc3653b41973ebf3

bus-nonce: b9daf91ad641b09b9dbee7b3320d05d3
reviewer: r10-recentre-reviewer -- round 1. Measured at head c40d1ee872b2481b272cbef5dc3653b41973ebf3 (code head fb85a2e97 + delivery row), detached worktree; head re-read before posting.

RESULT readings: 126 tests.yml runs (schedule+dispatch, created >= 2026-09-25; 20 schedule) -> 126 slow jobs, 38 with a clean cost line, 88 skipped/cancelled. FAILURES jobs=0 log=0 after retry (first pass: log=38, all "terminal escape sequences", re-fetched with --allow-escape-sequences; one jobs 502 on 36845654925 retried -> slow skipped).
RESULT split: git merge-base --is-ancestor cb7cb25c7 (#2142 merge) <head>: 36 pre, 2 post, 0 ancestry failures. Post: 38530020347 = 1.8804 (ref_ms 23.8, schedule), 38656447153 = 1.3908 (ref_ms 52.7, dispatch at 1005e27a6). Pre range 1.9147-2.8244; runner classes 23 at ref_ms 52.0-55.2 (1.9147-2.2310), 13 at 22.2-43.1 (2.3389-2.8244) -- body's figures reproduced.
RESULT centre @0.656: lo 1.2560 hi 1.8804 cap 2.1734 floor 1.0867; lo/floor-1 = 15.6 %, cap/hi-1 = 15.6 % (as the body measures headroom; as 1-hi/cap the top is 13.5 %). Old cap 2.332: bottom 7.7 %, top 24.0 %. Null @0.671: lo 1.2848 hi 1.8952 cap 2.2067 (16.4 %) -- still a lowering.
RESULT direction: 2.173 < 2.332, a lowering; no *_budgets.json, VERSION, manifest or notes touched; diff = tests/replay.py (value + comment) + dev/programme/delivery/2217.md only.
RESULT doubled arm on measured post-fix run 116167295751: cpu 2.8099 (injected_ratio 1.0) = 29.3 % over 2.173; ALL 91 replay checks PASSED in that log.
RESULT local lane (this Darwin box, load ~7-12): head 2.173 -> clean 1.991, cpu arm 4.0418, ALL 91 PASSED rc 0; mutant 2.332 -> clean 1.9191, arm 4.316, ALL 91 PASSED rc 0.
RESULT check-runs at head: all completed; only red nightly-status (main's #2205 replay red from schedule run 38530020347, answered in ## Red checks); pr-contract success at 01:34:44Z, after the last workflow concluded (closures 01:34:07Z). merge-tree vs origin/main rc 0.

False-red judgement: the band is centred on 36 projected + 2 measured points; per class the measured points imply memo factors ~0.64 (slow class, 1.3908 vs class 1.91-2.23) and ~0.69 (fast class at ref_ms ~23, 1.8804 vs 2.61-2.82). Re-projecting each class by its own implied factor gives worst cases ~1.23 (floor 1.0865, ~13 % clear) and ~1.95 (cap 2.173, ~11 % clear); the highest same-class neighbour ratio (2.8244/2.6145) applied to 1.8804 gives 2.03, under the cap. Both edges sit inside the band with more margin than the old bottom edge (7.7 %). Residual risk is at the top on the fast class, priced by one measured point; the comment's "Re-centre at the next timed week" names that.

Mutation: reverting to 2.332 survives (reproduced above). Acceptable under fixer.md step 2's "written triage" disposition for an unpinned site: a recorded band value changes margin, not any observed run's verdict -- all 38 readings lie in both bands and every measured doubled arm clears both caps, so no single lane run can kill it. Note the triage sits under ## Mutation proof rather than an ## Unpinned sites heading; pr-contract accepted the body.

Observation (no block): seat boxes read 1.99-2.03 locally, 7-8 % under the new cap; replay.py is excluded from run.sh (line 417), so this cannot redden the gate, but a seat re-running the lane locally under heavy load may see a red that CI would not.

Forward-carry: none claimed; none owed. Step 14: the movement is earned by the memo's measured cost drop, not by the instrument.
