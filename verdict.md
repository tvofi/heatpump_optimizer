Design review: revise ab1d7b76789a6cde6d8ebf7678016790e076bda8 architecture-unsound

Judged at base b880dc914f3ba2590b7ce655d7419678b1c4968e. The note names b3831ff64e, which is 38 commits behind it. Between the two, the files the note names differ only in self-test code: `beatd.py` gained `_beat_until` and a case-9 barrier, so its lines after :682 moved by +24, and `bus.sh` changed its confirm self-test, so its fixture is now at :2439. `audit-find.js` moved by 4 lines inside a dismissed hit. Round 2 of 3. Line numbers below are at b880dc914f.

## Round-1 points

All nine are answered. 1: `tick_loop.sh` is covered, and `dev/README.md:362` shows it is live. 2: STALE-CODE now means "behind the promoted ref", and liveness is unchanged. 3: `outside_is_mains` stays on main. The note gives the reason, and the refusal names promote. 4: the note lists the enumerator's hits. I reran it at the base and got the same set, apart from the notes below. 5: `gate` no longer changes, so every reader except the stamp keeps today's meaning. This also defuses readers the grep misses, such as `scorecard.py`. 6: the prune keep guard is in, with its self-test row. 7: `tests / closures` is required on push today (`gate.py:94` `REQUIRED["push"]` over `prelude.py:92`), so the stamp row fails first. 8: the order relative to PARALLEL-PIPELINE part 2 is stated. 9: every carry has a destination, and the split is routed.

## Revise points

1. architecture-unsound: design.md:36-38 creates a new main-status instrument. It fetches the last 20 `ci.yml` main push runs and prints `product-green k/20 (red r, unread u)`. That concern already has an owner. `tools/audit/seat/scorecard.py:22-26,102-110,231-239` prints `A_gate`: the share of the last 20 concluded main `CI` push runs whose `gate` job succeeded. It reads the beat-cached `runs.json` and `jobs/jobs_<id>.json`, counts a run with no cached listing as `unread`, and is run by the `scorecard` row (`beatd.jobs.json:302`). Its own null control already separates a machinery-only red (`A_gate` against `A_run`, :24-26). The note never names it. As written, two instruments would own "the main-run green share over 20". They would have two inputs (a GitHub fetch against the beat cache) and two `unread` rules, and the scorecard's would differ from the new verdict function's. Fix: make the done-criterion printer two scorecard lines (product and machinery). Compute them by applying the `tools/ci/gate.py` verdict function to the cached job listings, and give each line its null control and mutant in `scorecard.py --self-test`. If a separate reader is still needed, keep it only for `at <sha>`, the single-run pair that `nudge.md` and `web-stamp.js` read, or fold that into `stamp.py`. Either way, state in section 1 which module owns the 20-run window. Also name `scorecard.py`'s `unread` in carry 5's single-owner paragraph (design.md:152-155), because it is a third use of that concept.

## Notes for the fixer

- `tools/audit/seat/remerge_main.sh` sources `pr_args.sh` but never calls `pr_tools_fresh`. It has no freshness check, the same gap carry 7 names for `train.sh`. The sibling `design/R11-PRE-SHARED-FILES` at 20cafac7df (its design.md:168) routes it here: "`train.sh` and `remerge_main.sh` join `pr_tools_fresh`'s callers". Add it as a row of section 4 with the same refusal, or dismiss it with a reason. Carry: R11-PRE-TOOLCHAIN-PIN (item dr6)
- The freshness enumerator also returns `orchestrator_tick.py:2140` (same function as :2133, a pull-request head) and `:2909`, `:2911`, `:2930`, `:3415`, `:4033` (in-file self-test fakes). None of these is in the dismissed list at design.md:91-95. Carry: R11-PRE-TOOLCHAIN-PIN (item dr7)
- design.md:155 lists `tools/pr/figure_block.py:57` as an unreadable-input site. That line is a git subprocess helper that raises `Refused`, not a CI-input read. Re-derive the site when carry 5 is built. Carry: R11-PRE-TOOLCHAIN-PIN (item dr8)
- `design/R11-PRE-STANDING-SCRIPTS` at d1a4ae6a74 is new since round 1 and shares `beat_jobs.py`, `beatd.jobs.json` and `orchestrator_tick.py`. Its L5 decision (its design.md:67) is that `orchestrator_tick.py` gets "no new arm, ever". This note edits only the existing :1846 count, which is consistent with that, but adds no arm there. Carry: R11-PRE-TOOLCHAIN-PIN (item dr9)
- `design/R11-PRE-SHARED-FILES` D4 (its design.md:177) proposes this group's p1 before its part 3, and also routes its carry 7 aside here: a topic that `open_driver.py` never listed. Neither appears in this note's carry list. Carry: R11-PRE-TOOLCHAIN-PIN (item dr10)

## Routed decisions (unchanged from round 1; no revise point)

- decision: owner. Should a main whose machinery is red and whose product is green still stop train admissions (`merge_train.py:4366` `main_green`)? The note keeps it as yes. Separately: who may push `toolchain/stable`, and should a ruleset protect it?
- decision: orchestrator. The split at design.md:160-164: (A) this group, (B) carries 5, 4, 6 and 8 after A, (C) carry 3 alone.

## Checked and sound

- Reran the note's enumerators (design.md:77, :97) at the base. Each covered site exists where the note says: `pr_args.sh:192-200`, `beatd.py:113,427-455,600`, `tick_loop.sh:111-135`, `cloud_relay.sh:564-569`, `orchestrator_tick.py:1846`, `train.sh:475` (no check before `exec`), `merge_train.py:2709`.
- `prune_refs.py` `classify` (:274) keeps `claude/*` and `design*` refs and nothing for `toolchain/*`. `_self_test_keeps` is at :576. The failing row can fail today.
- Carry sites: `cancel_superseded.py:109-110,402`, `ci_ratchet.py:536` `_cut_at_prelude`, the `tests.yml:2273` job with no advisory arm, `review_packet.py:253-259,721-722`, `merge_train.py:781` `introduced_at`. All are as stated.
- `stamp.py` `GATE_JOB` :216, `gate_runs` :774 (it fetches every job of a run and then picks `gate` at :785, so the function has its input), `gate_verdict` :800, `tests_gate` :2213, flushed-head refusal :2806, rule 2 :2999-3004.
- `nudge.md:93` and `web-stamp.js:107,159` read the push run's `gate`, as the note says.

Tokens: this seat's count is not reported by the harness; no subagents.
