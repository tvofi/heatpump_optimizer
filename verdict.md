Fix review: merge 6a229a2817f0974cc6603eea47a951ef724884d6

bus-nonce: absent: this cloud dispatch carried no nonce; the relay cannot grade this ref, the orchestrator relays by hand

Round: 1. Reviewed from a detached worktree at 6a229a2817f0974cc6603eea47a951ef724884d6; merge base ae0ed64af898d8923ac35afe6e9c031ac1e6b111. Harnesses: the finders', exported from plan/r11 819aa2e354b4e5baaf824b8568fd72bea8168a75 (dev/audit/rounds/round11), never the fixer's companion.

RESULT finder-harnesses base -> head (re-derived, ev/harness_runs.txt):
- D6/s5/claims.py --only c_mock, c_fix_review_j5, c_round4_d6, c_brief_exclude, c_handover_docs, c_unleased, c_instrument_dirs, c_worktree_apply: false_or_stale 1 -> anchor gone (checked_units=0). The harness reads absence at the head, not truth, so each replacement sentence was checked by hand against the tree (ev/sentence_checks.txt): all true.
- c_event_hub: 1 -> 1, a basename limitation of the harness; the cited dev/audit/harnesses/r10_livestate_event_hub_writes.py exists.
- c_main_guards null control: true at both ends. c_brief_exclude null arm claude_symbol_found_null_control=0.
- D6/s7/plan_claims.py: wrong_rows 9 -> 0.
- D11/s2/policy_health.py --list: dup_units 16 -> 10, rulings_overlap 1 -> 0; the 10 are the pairs the body dispositions.
- D6/s2/probes.py --probe gov_paths: 2 -> 2 (fixer.md:104, orchestrator.md:73), the body's Forward-carry.
- No finding reads 0 at the base (owner precedent 2026-11-18 not engaged); no score-only move.
- Carry reproduced: both citations respelled at dev/governance/decisions/ make node tools/policy/policy_lint.mjs exit 1, FIXTURE VACUOUS checkCitationPresence 0 of 2; at the head as pushed, rc 0.
- policy_lint rc 0, rules_sync --check ok, git merge-tree --write-tree origin/main HEAD rc 0, VERSION/manifest/RELEASE_NOTES untouched three-dot.
- D15/s1/privacy_gate.py not run: no debug bundle on this machine; the text change does not move it.

Contract changes (policy, owner's approving review needed; not corrections):
- dev/programme/RULINGS.md: deleting the 2026-10-24 entry ("each operation or shape that is not clearly a one shot ... reusable instrument before policy ..."). At the base it binds every seat; at the head it survives only as D11.md step 5, a D11 finder criterion. No other policy file states it (searched dev/governance and CLAUDE.md). The reach narrows from every seat to one audit dimension's finder: this changes what a seat must do.
- dev/governance/dimensions/D15.md step 2: "then debug_ingest.py stage 2 (replay half); elsewhere credential keys hold only **REDACTED**. Either failing stops the run." It replaces the gate a D15 seat runs and stops on (export.violations over the bundle, planted-credential arm) with a different gate and scope. It fixes a gate that refused its own null control, but it is a method change in an owner's-words brief, not a correction. Its second clause names no instrument, which writing-for-agents.md requires of a control.

Corrections (re-truthing or pointers to the owning file, no seat obligation moved): steward SKILL.md, D4-criteria.md, D5-criteria.md, root-cause.md section 4, standing-roster.md, brief-citations.md item 3, gate-scoping.md, writing-for-agents.md, HANDOVER.md worktree_gc, RULINGS.md 2026-11-13 entry (D6.md quotes it; D5.md points to D6.md), tests/README.md, dev/audit/README.md, archscore ABOUT.md, INSTRUMENTS.md, plan-2026-09-open-issues.md (not named in CLAUDE.md, so not policy; its deleted "every seat is told to open all three" described a superseded load path).

Note: red-pending: check gate (job 134850378612) is red at the head with "run(s) [44317361655] at this head are still being judged"; tests/closures and tests/coverage were in progress when read. This is not a judged red. bus.sh post refuses merge at a red (C8), so this relays only once the gate turns green.
Note: carry-shape: the D6-s2-02/D6-s2-03 Forward-carry is spelled "Carry: dismissed: held for the orchestrator's ruling". fixer.md:295-296 wants "Carry: <own group>" naming the pending ruling. The substance meets that exception.
Note: stale-column: dev/audit/README.md j5_gil.py row: the "who re-runs it" cell now says who built it, so the column's question goes unanswered.
Note: list-incomplete: tools/audit/seat/INSTRUMENTS.md's records paragraph drops tools/policy/record-predicate/ and dev/archive/experiments/ledger-layout/, which the old list named and which still exist; line 15 ends in trailing whitespace.
Note: mutation: no in-tree check reads these sentences and the diff writes no production line, so no mutant exists. The proof is the finder harnesses moving base -> head above.
