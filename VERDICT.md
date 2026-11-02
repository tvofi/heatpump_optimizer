Fix review: merge 8e47d727c1024728ab3ab23c4aefa01a866dcf78

bus-nonce: d18618e05ad19f8e7fa3dcb3d0e9b6c3

This is round 3 of PR #3174 (R10-REPLAY-COST-BUDGET, issue 3129). It is a delta review at the live head `8e47d727c1024728ab3ab23c4aefa01a866dcf78`, judged through the three-dot diff against merge base ea59e9a09de5, which is origin/main. That diff touches only `tests/replay.py` and `dev/programme/delivery/3174.md`. dev/governance/roles/ has not changed since the merge base.

I worked from detached worktrees at the head and at the base. The harness is the finder's from round 2: the CI lanes' own `cost` lines, graded through the production `class_budget` and `cost_offenders`. Round 2 blocked because the nightly `slow` class (ref_ms ~53) could not see a 2x cycle under one budget. At this head, each of that class's doubled arms reads over its own class's budget, and every clean reading in every class reads WITHIN.

## Findings

- The owner fixture has still not been replayed on the ref53 (nightly `slow`) class. It is graded there by the single 337.8, which no class key covers. It joined main after the 2026-11-02 00:50 nightly: d06124693 is not an ancestor of 78dd34354.
  - This cannot hide a 2x. `cost_offenders` turns a clean reading under 168.9 red as `cannot see a 2x cycle`, and any clean reading at or over 168.9 puts its 2x over 337.8.
  - The risk is a loud red on the first nightly that reads under 168.9. The body says so under "Owner fixture on ref53, unread".
  - A local hint, not a CI class: round 2's container read owner 307.9 at ref_ms 48.6 while reading synthetic 1.6-2.3. That suggests the solve-dominated owner ratio does not drop with the synthetic.
  - The first nightly after merge owes that `record:` line. If it is red, key the owner `cpu_ratio` by class from it. Carry: R10-REPLAY-COST-BUDGET
- A CI runner whose `ref_ms` falls outside all three bands makes the required `tests / replay` check red, with a named refusal.
  - The bands are 28.72-32.69, 42.99-49.51 and 49.60-56.78. The comment above `COST_BUDGETS` records an older fast nightly class at ref_ms ~22-34, part of which now lies in no band.
  - That is the fail-closed behaviour the round-3 ruling asks for: it is loud and never a silent pass. The re-record path is to append the job to `COST_CLASS_READINGS`. Carry: dismissed: fail-closed by the round-3 ruling; a band miss is a named red, never a borrowed budget
- In the `runner_class_unknown` control, the locals are named the wrong way round. `lo30` holds ref30's upper edge and `hi46` holds ref46's lower edge. The midpoint they compute (37.84) is correct, and it sits in the gap, as intended. Carry: dismissed: cosmetic naming only, the probe value is right

## Evidence

- **Head and CI.** The PR API reads head `8e47d727c1024728ab3ab23c4aefa01a866dcf78`, and the body's `## Head` names it. `merge_train.py classify 8e47d727c1024728ab3ab23c4aefa01a866dcf78 --pr 3174` exited 0 at 17:45:27Z and printed `GREEN 8e47d727c1024728ab3ab23c4aefa01a866dcf78 pending: none red: none` (ev/classify.txt and ev/classify.log).
  - This head's `tests / replay` job 125418412297 (run 41486423541) concluded success with `ALL 181 replay checks PASSED`. That runner is ref46 (ref_ms 47.73).
  - Synthetic clean 2.2746 is WITHIN 3.357, at 67.8 % of it. The cpu-doubled arm 4.6399 reads `over its budget 3.357`.
  - Owner reads 248.84, within 337.8. AWAY_COVERED is ok. The excerpt is in ev/ci_head_replay_125418412297.txt.
  - Check runs for this head, read on one page (total_count 43 once the late jobs had joined): none concluded failure, timed_out or cancelled. `## Red checks` names #3167's inherited red and answers it with a cause, a process state and a countermeasure.
- **ASK (1), the finder's harness at both ends** (ev/finder_both_ends.txt).
  - At the base (single 2.173), the ref30 and ref46 cleans read `over its budget`. That is #3167's red. The ref53 cleans read WITHIN.
  - At the head, all seven cleans read WITHIN their class budget, and all seven cpu-doubled arms are seen:
    - ref30: 5.701 and 5.532 over 3.934;
    - ref46: 4.647 and 4.777 over 3.357;
    - ref53: 2.885, 2.841 and 2.925 over 2.081.
  - So a 2x cycle on the ~1.45 class now goes red, and the ~2.3-2.8 classes stay green.
  - Synthetic `loop_cpu_ratio`, unchanged at 0.1278, holds the seven cleans (0.0901-0.1026) WITHIN and sees all seven loop-doubled arms (0.1792-0.2015) at both ends. The owner's four CI readings (235.8-246.0) are WITHIN 337.8, and their 2x is seen.
- **The null control.** It is base-versus-base on CI: every cited job ran cycle code unchanged from this base, and every clean reading is WITHIN its own class budget.
  - A local interleaved base/head null cannot be graded inside a class here. This container's ruler reads ref_ms 73-87, outside every band. Synthetic `cpu_ratio` read base 1.548 and 1.385 against head 1.645 and 1.501 (ev/local_one_interleaved.txt).
  - At the head, the live `--one` run's `cycle_cost` is the named refusal `runner class unknown: ref_ms 73.25 lies in no band ...`. It fails closed, as the body claims.
- **ASK (2), the cited sources.** I opened all seven cited jobs myself, and every tuple in `COST_CLASS_READINGS` matches the `cost` lines:
  - 125160076828: (30.32, 2.81, 5.701)
  - 125240101580: (30.93, 2.7543, 5.5315)
  - 125097530406: (45.65, 2.3246, 4.6473)
  - 125316010511: (46.36, 2.4235, 4.7775)
  - 124414072168: (52.76, 1.4563, 2.8848)
  - 124725704090: (53.27, 1.451, 2.841)
  - 125036077984: (52.43, 1.4926, 2.9251)

  The owner readings match too: 235.8185, 240.6876, 241.9249 and 245.967.
  - The re-derived budgets (sqrt 2 x the geometric midpoint) are 3.9344, 3.3567 and 2.0812, against committed 3.934, 3.357 and 2.081. Every reading is 69.3-72.2 % of its budget. The owner budget re-derives to 337.76.
  - The re-derived bands (min/1.05 and max x 1.05 over every arm's ref_ms, owner included) are 28.72-32.69, 42.99-49.51 and 49.60-56.78. They are identical to the committed bands. The counts are 10, 10 and 12 as the body says, with 8, 8 and 12 synthetic arms plus the owner's.
  - No budget is wider than what ran. Each class has two or three jobs, and the body says so ("Too few readings").
- **ASK (3), the class signal.** It is the run's median reference-solve `ref_ms`, which `run_fixture` already measured. A grep of the added lines finds no hostname, runner name, environment variable, platform or cpuinfo read. The only hits are the `COST_RUNNER_CLASSES` identifiers (ev/standing.txt).
  - Band edges: the bands are disjoint, with a refusal gap at 49.51-49.60.
  - I graded each class's clean and doubled readings under each other class's budget (ev/finder_both_ends.txt, `misclass` lines):
    - A ref53 run read as ref30 or ref46 reads `cannot see a 2x cycle` on its clean: loud red, never a silent miss.
    - A ref30 or ref46 run read as ref53 reads `over its budget`.
    - ref30 and ref46 read under each other's budgets still see their doubled arm.
  - No misclassification on these readings is a silent pass.
- **ASK (4), my planted mutants** in `tests/replay.py` at the head (ev/mutants_r3.txt). Each was restored, and the tree is clean.
  - Null: `ok` on `class_budgets` and on `runner_class_unknown`.
  - Per budget and per class, each budget loosened past 2x its readings and each tightened under them is red on `control:cycle_cost:class_budgets`:
    - R1 ref30 5.75 and R2 ref30 2.70;
    - R3 ref46 4.80 and R4 ref46 2.30;
    - R5 ref53 2.95 and R6 ref53 1.44.
  - Bands: R7 widens ref46 over ref53, and R8 shifts ref53 off its readings. Both are red.
  - Selection: R9 ignores the ruler and R10 inverts the band test. Both are red on both controls.
  - R11, an unknown ruler falling back to the single budget, is red on `runner_class_unknown`.
  - R12 drops the `refused or` in `run_fixture`. It is green on the controls, but equivalent: a `None` budget makes `cost_offenders` return `no recorded budget`, still red.
  - The body's own M1-M5 are consistent with these. M3 (ref30 graded by ref46) is disclosed as equivalent. I confirm that in the misclass lines: ref30 under 3.357 is WITHIN, and its doubled arm is seen.
- **ASK (5), standing checks** (ev/standing.txt).
  - `git merge-tree --write-tree origin/main 8e47d727c1024728ab3ab23c4aefa01a866dcf78` exits 0 with tree f58150f77f78.
  - Both claim files, VERSION, the manifest and RELEASE_NOTES.md are byte-identical to origin/main. No `*_budgets.json` is touched, and there is no budget raise.
  - `python3 tests/structure.py` printed STRUCTURE RATCHET PASSED.
  - `tests/closure.py select --diff ea59e9a0` printed `MODE: SCOPED -- 3 script(s) run, 30 scoped out.`, as the body quotes.
  - The delivery row `dev/programme/delivery/3174.md` is in the three-dot diff.
  - No host path appears in the added lines.
- **Not re-run, and not mine.** I did not re-run the gate or the mutation table; both are CI's. I did not re-run the round-2 pins: their code is untouched in this round's delta, and this head's lane prints `ok AWAY_COVERED names committed fixtures`.
