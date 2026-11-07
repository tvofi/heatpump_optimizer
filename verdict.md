Fix review: blocked 09ec9a880383929c73fd1581c028d1d5b966fd4b mutation-vacuous: 12 of 16 reviewer mutants on replan.py's new core lines survive, and --since-tag credits 0 groups on every real tag range

bus-nonce: 0de03f1172f33361f033bae95fc41112

Round 1 of this review. Measured head 09ec9a880383929c73fd1581c028d1d5b966fd4b, merge base 80016a71f567d936450d8708abcbb79d9e8071d7 (origin/main unmoved), from detached worktrees at the head. No finder's harness is committed for this instrument group (packet: "Finder's harness: none named"); every attack below is my own, disclosed as such, scripts in ev/mut.py and ev/mutg.py.

## Block

- mutation-vacuous: my 16 mutants on the PR's own added lines in tools/plan/replan.py leave `--self-test` at rc 0 for 12 of them (ev/replan-mutants.txt): free-slot-overflow-filter, post-propagate (transitive post-closure), post-after-mark (`after` naming STAMP-ROUND-MAJOR), credit-lane, check-post-before-stamp, check-produced-credit, post-check-carries, chain-walk-max, arrivals-median, live-refs-prefix (parse_live_refs never exercised), post-dur-in-closure (_sweep), stamp-while-cut. The body's "kills every mutant" holds only for the fixer's own 18 named mutants. tools/audit/seat/gantt_drift.py: 1 of 9 survives (word-boundary).
- defect, carry 9: `--since-tag` is inert on the population it is for. production_groups_since matches roster group names in first-parent subjects, but main's are "Merge pull request #N from tvofi/fix/<topic>", and `git show --format= -U0 <merge>` prints the combined diff, which is empty for a clean merge. Over v7.1.2..v7.1.3 it credits 0 groups where 14 merges change code lines under custom_components against their first parent; 0 on every range from v7.1.0 to main (ev/attacks.txt A). The self-test only feeds it made-up subjects.
- defect, carry 3: a group whose stage is already live and whose only evidence is a design ref keeps live credit (M group: 1074 min, against 1534 min for the same group not-started) and is not marked design_only. The carry says design-only starts with no credit (ev/attacks.txt B).
- defect, carry 9: a credited group that is still open is counted twice. since_tag=["Q1"] with Q1 open gives patch stamp carries ['Q1','Q1','Q2'], and check_plan returns [] (ev/attacks.txt C). The carry counts "production groups completed (stage done ...)" and "a multi-PR group counts once".
- architecture-unsound, carry 0 (2): `--measure-sizes` already existed at the merge base (replan.py:2041 via size_durations.py: p75, start = earliest of first commit or PR creation, MIN_CELL; durations.json S 18.2, M 22.2, L 31.1). The PR adds a second, simpler implementation of the same formula (measure_sizes_hours with --sizes-input). Its "null control" builds fixture rows whose p75 is the constant itself (13.1, 11.4, 20.1), so it re-derives nothing (ev/attacks.txt D). The brief asks for every figure to be re-measured at the merge base.
- root-cause-unrecorded: gate: the code run's gate 128226496049 concluded failure on `codeql / Analyze (python): cancelled (this run)` (128209941747, 23:13 to 23:58Z). The body's `## Red checks` reads "none". This is not the edit-run deferral the dispatch excused; that deferral resolved into this red (ev/attacks.txt F).

## Findings

- mutation-vacuous: replan.py's post-closure, check_plan post-closure and credit refusals, binding-chain walk, arrivals pricing, overflow slot filter and parse_live_refs each need a pin that their surviving mutant fails (list under Block, ev/replan-mutants.txt). Carry: R10-FLOW-TOOLKIT-MODEL
- gantt_drift.py is_named's word boundary is unpinned: replacing the boundary regex with a plain re.escape passes all 42 checks. On the live roster, 24 group names are prefixes of another (R10-STORE / R10-STORE-RACES), so a PR for the longer name would silence the shorter one's IDLE. Carry: R10-FLOW-TOOLKIT-MODEL
- --since-tag inert on main's merge subjects and merge diffs (0 credited where 14 qualify in v7.1.2..v7.1.3). Match by the merge's topic branch, as topic_evidence already does, and diff against `^1`; pin with a real-shaped merge subject. Carry: R10-FLOW-TOOLKIT-MODEL
- A design-ref-only group whose stage is already live keeps live credit; carry 3 says no credit. Carry: R10-FLOW-TOOLKIT-MODEL
- Stamp credit double-counts an open credited group; filter credit to done groups, or exclude credited groups from carry. Carry: R10-FLOW-TOOLKIT-MODEL
- measure_sizes_hours duplicates size_durations.py's existing --measure-sizes with a different start rule, and its null is circular. Dispose of carry 0 (2) as already built at the base, or route the offline path through size_durations. Carry: R10-FLOW-TOOLKIT-MODEL
- Red check `gate` (codeql / Analyze (python) cancelled at its timeout) is unanswered in `## Red checks`. Carry: R10-FLOW-TOOLKIT-MODEL
- `## Head` carries a stale second line naming dcf19d037df1 (an earlier head) and "origin/main unmoved at 28482eceeb6b"; origin/main is 80016a71f. Carry: R10-FLOW-TOOLKIT-MODEL
- Carried, not re-measured: inflow_groups_per_hour 0.4 in durations.json, and the hard-coded slot_sensitivity string (27 snapshots, r=0.045) printed in every plan; the brief says "carry no count". Inflow is reported only, never scheduled, where carry 0 (3) says it "adds expected arrivals to the schedule". Carry: R10-FLOW-TOOLKIT-MODEL

## Evidence

- RESULT replan --self-test at head: "self-test: 0 failed", rc 0, also under python -O.
- RESULT gantt_drift --self-test at head: "gantt_drift self-test: 42 checks, 0 failed", 15 mutants killed (matches the body), also under -O (ev/gd_selftest.txt).
- RESULT fixer's replan mutants: 17 new plus 1 rewritten (cp-first-in-tier), all killed. The body's "about 20" is not a figure I can re-derive exactly.
- RESULT reviewer mutants: replan 4 of 16 killed, gantt_drift 8 of 9 killed (ev/replan-mutants.txt, ev/gantt-mutants.txt).
- Routing confirmed: R10-BODY-CONTRACT on handoff/audit-r10-roster 1f11980fa7cf holds the A1/A2 (#2896) and #2438 carries and lists issue 2438 (brief carries 1 and 7). Brief carries 4, 5 and 6 are restated duplicates of 1, already dismissed on the roster.
- Absorbed advisory works as specified: all 13 absorbed groups on the live roster draw the ADVISORY, because none of their resume notes names an absorber (roster data, not this PR's defect).
- Post-closure on the live roster: post_closure_groups returns {R10-CATALOG-PR} only.
- merge-tree --write-tree origin/main head: exit 0, no conflicts.
- tests/structure.py: STRUCTURE RATCHET PASSED; no *_budgets.json in diff. selftest_wiring --check: 118/118 wired, 0 index gaps. plan_page --self-test: 66 checks, 0 failed. tests/entities.py not runnable here (no homeassistant module); CI tests/closures and closure-scope are green.
- VERSION, manifest, RELEASE_NOTES.md untouched; dev/programme/delivery/3264.md in diff; no production code touched; roles/ unchanged base...main.
- CI: merge_train classify at 00:03:09Z: rc=1 RED, pending none, red gate. Required gate concluded failure, cause codeql python cancelled, not a deferral.
