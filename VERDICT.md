Fix review: blocked d076f22c99f852a822856cc78956a7ed84ab6daa mutation-vacuous: legionella.py:655 BOOLOP, the overdue notice watched predicate, and 7 more added sites survive every driver though the body names 655 as killed by M3 and all 25 as pinned

bus-nonce: 881288eda901a2ceb80b01ddd15adc1f

Round 1 (no earlier verdict on this PR). Head measured: d076f22c99f852a822856cc78956a7ed84ab6daa (ev/HEAD.txt), which was still the branch head when this verdict was written. Merge base c9cbe6b458a7053f914649eb02d5296d6cd8c0f4. Contract current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty.

## Block

- The CI `tests / mutation-pins (1..5)` shards on this head (jobs 121278917305, 121278917308, 121278917311, 121278917358, 121278917365) pin 17 of the 25 added sites. Eight live, each `UNPINNED ... -- lives` (ev/mutation_pins_log.txt):
  - `legionella.py:345 CMP_BOUND`, the fold's retry bound;
  - `350 CLAMP_DROP`, the fold's peak max;
  - `60 CMP_BOUND`, the overdue threshold;
  - `621 CMP_BOUND` and `621 GUARD_OFF`, `_pending_attempt`'s completion test;
  - `655 BOOLOP`, the overdue notice's `watched` predicate;
  - `658 GUARD_OFF`, the overdue memo;
  - `701 GUARD_OFF`, the mode-block warning.
- The lane says these need "a killing check or a survivor_triage verdict, which no tool writes". So `tests / mutation` stays red on this head after the autofix.
- The body's `## Unpinned sites` says every one of the 25 is "pinned by `mutation-autofix`". For 345, 349, 350 and 353 it adds M4, and for 655 it adds M3. That is not true at this head for 345, 350, 655 (or 60, 621, 658, 701). M4 kills only the GUARD_OFF of the whole fold condition, not its bound. M3 drops the `_has_probe()` operand, not the `dhw_legionella_enabled` one.
- My own mutants confirm the safety-relevant two (ev/mutant_R3_*.txt, ev/mutant_R4_*.txt). Each leaves `tests/features.py` and `tests/guard_pins.py` red only on the archive-environment `recorded_at (#363)` check, which an unmutated archive fails too (ev/mutant_null_archive.txt):
  - **R3**: `watched=` ignores `dhw_enabled and dhw_legionella_enabled`. An install with legionella switched off but a tank probe configured would raise `dhw_legionella_overdue`. That breaks the brief's byte-identical null control for an unconfigured cycle, and no check sees it.
  - **R4**: the threshold is doubled, `age_h > interval_days * 48.0`. The overdue notice then arrives a whole interval late, and no check sees it. The only check uses a 66+ day age (`days >= 8`).
- To pay: add a check that kills each live site, at least the R3 and R4 cases and the fold bound, and correct the `## Unpinned sites` list.

## Findings

- The unreachable notice's peak no longer goes stale under daily retries. At this head the `short` arm's standing `dhw_legionella_unreachable` reads `reached 56.9`, and my 58.5 °C arm reads `58.4` (it was 55.4 at the first window). Only `marginal`, whose later windows take the `peak >= target - 1` branch, keeps 55.4. The body's dismissal holds for `marginal` only. Carry: dismissed: the overdue notice stands beside it in every arm and names the completion's age, as the body says
- The class_excess_loc payment partly trims `async_track_cycle`'s docstring (commit c9534b398). The trimmed rationale survives in the `credited` comment block, so I judge it a sound condensation, not `metric-gamed`. It is also a lowering, not a raise. Carry: dismissed: the budget is lowered, not raised, and no rationale is lost
- The forward-carry of the step-0/step-1 flap names `Carry: R10-IMMERSION-LATCH` but says this seat wrote no brief. I could not open a roster carry for it at a handoff SHA, because the body names none. Carry: R10-IMMERSION-LATCH

## Evidence

- Brief measurement (1), overdue is commanded:
  - Fixer's harness `dev/audit/harnesses/r10_legionella_completion.py` (sha1 24f8ca0e6eb1f63c40f32cc9b30652e7a76768e2, matching the body), `--days 14`, re-run by me from one copy at both ends (ev/harness_base.txt, ev/harness_head.txt).
    - Base: `short`, `marginal` and `blind` give `attempt_gaps_h [145.0, 145.0]`, `completions 0`, `due_in_hours_end 122.8`, `completion_age_days_end 80.0`, with 5 commanded steps.
    - Head: 13 gaps of `24.0`, `due_in_hours_end 0.8`, 139 commanded steps.
    - Every figure in the body's `## Figures` reproduces.
  - My own closed loop (ev/reviewer_probe.py, ev/probe_*.txt; reviewer-built, not the finder's): pump ceiling 58.5 °C, setpoint 50.
    - `overdue_short585` (66 d, 7 d interval): base gives 1 commanded step and attempts `[0.75]` over 4 days; head gives 39 steps and attempts `[0.75, 24.75, 48.75, 72.75]`.
    - Null `null_notdue` (2 d old): 0 commanded steps at both ends.
- Brief measurement (2), a below-target peak leaves the cycle due:
  - Unit probe at both ends, identical: free-disinfection off, 58.9 °C gives `completed=False` and 60.0 °C gives `completed=True`.
  - Free-disinfection on: 59.4 °C gives `completed=False`, 60.0 °C held 3 h gives `completed=True`, and 60.0 °C seen once (hold not met) gives `completed=False`.
  - A sensor gap (None readings under a commanded boost) gives `completed=False`.
  - `async_track` is unchanged except for the added `check_overdue()`.
- Brief measurement (3), loud notice:
  - Base: `overdue_7d` gives `overdue=None`.
  - Head: `overdue_7d` gives `{'days': '66', 'interval_days': '7'}`.
  - Null at head: `healthy_7d` (2 d) gives None, and the exact edge at 7 d gives None.
  - Closed loop at head: `dhw_legionella_overdue {'days': '69'}` stands in `overdue_short585`. In the harness's `reach` arm it is raised, then cleared by the completion.
  - M2 and M5 turn it red (below).
- User interval respected:
  - Interval 14 d: age 10 d gives no notice, and age 15 d gives `{'days': '15', 'interval_days': '14'}`.
  - Closed loop `user14_overdue` (30 d): notice `days 32, interval_days 14`.
  - Retry with a 0.5 d interval is `min(12, 24)`: due-in reads 12, 6, 0 at both ends.
  - No probe: due-in 168 then 144 at 24 h, identical at both ends.
  - Cap: a completion 2 d before a fresh attempt gives due-in 120.0 at the head, against 167.0 at base.
- Tank ceiling: in every arm at both ends the plan's trajectory peaks at 60.0 °C, the configured disinfection temperature, and the tank never exceeds the pump ceiling.
  - My probe's `plan_exceeds_ceiling` compared against `dhw_max_temp` (the 50 °C setpoint), which excludes the legionella top. That flag is my definition error, not a defect. The values are identical between base and head.
- Disabled install (null control): `disabled` arm gives `notices_ever []`, 0 commanded steps, and the same `hours_since` sequence hash at both ends (5124979071255641149). Unit: `issues=[]`, `attempt=None`. With the code as written this is byte-identical. R3 shows it is unpinned.
- Mutation proof, re-run by me on a git-archive copy of the head, running `tests/features.py` and `tests/guard_pins.py`.
  - The archive lacks `.git`, so the `recorded_at (#363)` check fails in every copy. The unmutated null shows the same single failure, so I subtract it.
  - M1: 2 named checks red. M2: 1. M4: 1. M5: 1. Each matches the body.
  - My own R1 (drop the `min(since, age)` cap), R2 (`_pending_attempt` ignores completion), R3 and R4 each turn nothing red. CI separately kills 613 CLAMP_DROP and 621 BOOLOP with other mutants of those lines.
- Unmutated head: `ALL 4404 FEATURE CHECKS PASSED`, `ALL 50 GUARD PIN CHECKS PASSED`, `STRUCTURE RATCHET PASSED` (class_excess_loc 18096 <= 18096), `ALL 12 typing-ruler source checks PASSED`.
- Untouched at this head: `VERSION`, the manifest, `RELEASE_NOTES.md`, and both claim files (three-dot diff empty). The diff contains no host or home path.
- Merge: `git merge-tree --write-tree origin/main d076f22c9` exits 0 against origin/main 8aee66b77289f567617e9f9f852d72d5c4097aba, tree 653b9f615a05 (ev/merge_tree.txt).
- CI on this head, read from the check-runs API:
  - Green: fast (3.14), coverage, coverage-ratchet, closures, typing, browser, lane-proofs, graders-head-copy, arch-score, budget-raise-gate, instrument-self-tests, policy-docs, wave-script, env-matrix, hassfest, validate-hacs, codeql, and all five mutation-pins shards.
  - Red: `tests / mutation`, with `MUTATION TABLE REFUSED -- ... 25 of them added by this diff`. The body's `## Red checks` predicts and names it. Its survivors are the block above.
  - Red: `governance / delivery-status`. It is OVERDUE on other PRs' rows (#2780, #2749, ...). It is not a required check and blocks no merge, and it is not this PR's.
  - `tests / mutation-autofix` was queued when I read CI. Its bot commit will move the head; the eight survivors are outside what it writes.
- Class census (step 6): the body's two grep rules, re-run at the head, return the seams the body lists. No undispositioned seam.
- Instruments are mine and disclosed as such: ev/reviewer_probe.py, ev/mutants.sh. The finder's evidence is the owner-export figures (66 d, 7 d interval, a below-target last attempt); the harness's starting state reproduces them.
