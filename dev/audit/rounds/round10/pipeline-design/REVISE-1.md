# Appendix D: answers to the design review, revise round 1 (R11-PRE-PARALLEL-PIPELINE)

Verdict answered: `Design review: revise 80fbf6319fdb950b8d5054ee8939fb5dea1b5aae
evidence-missing`, at `design-verdict/R11-PRE-PARALLEL-PIPELINE` ea028c98ec.
Owner's ruling after it, 2026-11-14, verbatim: "Day 1 plus shadow". So the
revised note designs day 1 for building, the shadow as a measurement beside
round 11, and leaves the switch as a decision he takes on the shadow's result.

Each point: **resolved** (the note or appendix changed as asked) or
**contested** (with the measurement). Figures are `COST.md`'s and
`BASELINE.md`'s ids; every enumerator is under harness/.

## Revise points

- **R1, resolved.** The sentence was false. `absorb_heads.py` judges every
  merge twice: with the checkout's merge drivers 739 of 826 are clean, and
  driver-free (the two drivers replaced by `git merge-file`, as
  `Train.text_merge` builds it) 682 are. The 57 fewer are 58 that are clean
  only with a driver, less one that conflicts only with it; their files are
  `tests/structure_budgets.json` 27, `dev/audit/config/bugclasses.json` 23,
  `tests/closures.json` 10. All 41 merge-main bot merges are among them: the
  bot merged only what GitHub could not, as its contract says, and the first
  note's "bot 41 clean" misread it. B14, B15 and the note's F2, F3 are restated
  on the driver-free count, both printed. By maker, driver-free clean: other
  instruments 279 of 293, fixer seats 189 of 278 (136 of them after the
  topic's first handoff), the train's recarry 171 of 171, other seats 43 of
  43, the bot 0 of 41.
- **R2, resolved.** `replay_v2.py` replaces `replay_pipeline.py`. It lands the
  15 pull requests with fixer commits after approval and the 13 blocked after
  approval at their LAST merge verdict's head; it reads ready from the `gate`
  check-run at the pull-request head the verdict judged (the reviewer's notes
  f7 and f8: 167 from the gate, 30 imputed, 18 red on their own gate and kept
  on today's clock); it adds the measured merge latency (0.45 h, n = 58; the
  reviewer measured 0.33 h from run conclusions). Its null runs today's rules
  through the same loop, the recorded count of post-approval heads made by a
  merge of main each priced at that day's mean push-to-green, and reproduces
  the measured mean within the stated tolerance (N1); with the median cycle it
  is 14.6 % low, still inside it (N1b). The null can fail: it failed at
  -21.6 % in the first cut, which priced a cycle at the day's median and
  counted commits instead of pushed heads. Landed is 5.41 to 5.68 h from first
  approval at the lower bound and 4.60 to 4.86 h at the upper, against the
  first note's 2.50 h and the reviewer's 3.56 to 4.17 h.
- **R3, resolved.** The -33 % is withdrawn. `absorb_heads.py` is the
  enumerator, over `data/runs/`, with its null (`--null` relabels the absorb
  heads and prints zero): K1, K1n, K2. The unit is run wall, not
  runner-minutes: jobs were not read. Day 1 is about -10 % (K1 less its batch
  proofs); the integration branch about -17 %, -26 % with the skip. K2 is not
  counted as saved, which the first estimate did.
- **R4, resolved, by definition and by scope.** The switch is not approved, so
  SUCCESSORS is not built. `SWITCH.md` defines it for the later decision: a
  successor branches from its predecessor's REVIEWED head, never from the
  integration tip, so a rebuild cannot strand it and an evicted culprit's
  commits reach main only inside a pull request that names them; until
  promotion the successor's pull request shows the predecessor's diff to the
  scoped gate and the reviewer reads the delta from the predecessor's head.
  Rework at the measured red rate: 6 to 20 culprits in 215 landings, 2.8 to
  9.3 %, each costing the successor one merge of the repaired predecessor, a
  cycle (3.07 h mean) and a carry or re-review. C2's figures are now printed
  for all three starts (S-i, S-ig, S-im). The reviewer's remark that no cited
  public design starts work from an unproved integration state is right and
  the appendix says so.
- **R5, resolved.** R-pipe2 bisects with one proof at a time. T-f and T-s are
  the result. The 6 h criterion is kept and reconciled: it holds only at a
  45 min proof wall; at 60 min it fails with FULL-proof bisection (7.20 h) and
  narrowly with seat search (6.20 h); at 75 and 105 min it fails either way.
  The note says so in its shadow section: on closing-day load the switch is
  cancelled by its own criterion.
- **R6, resolved in part, contested in part.** Resolved: I1 is restated as it
  holds (main moves by promotion or by the writers that exist today, each of
  which forces a rebuild); direct pushes are counted and restart the proof in
  flight in every rule set (20 in the window: 11 stamps, 9 ledger App pushes;
  9 to 16 restarts a week in the replay); F6 is corrected to "at least 2
  remain". Contested: the 109. Of the 53 direct moves, 33 are pull requests
  (29 record, 4 dependabot) and land like any other change, and my recount
  finds 16 more record-class pull requests the same way (`main_moves.py`: 69
  first-parent commits outside the 215, 49 of them pull requests). The 56
  hotfix pre-emptions were my first note's rule; the revised rule is that a
  priority landing does not cancel a proof in flight (it lands first in the
  next range, and the within-the-hour path stays the direct merge). 20
  restarts a week remain, not 109.
- **R7, resolved.** Costed as its own rule set, day1+ (S-1p): today's batch
  proof made push-judged, every entry behind a proof, GitHub merging. It loses
  to day 1 on wall clock at every proof wall, because the 72 lone batchable
  entries a week then wait for a proof, and it is slower than today at 75 min
  and above. What it buys over day 1: no unproved culprit reaches main (1 a
  week in the replay, 6 if every recorded red is real). What the integration branch buys beyond it: landing
  before proof (E) and the local driver merge for 8 claim entries a week.
  Day 1 as built is therefore the fallback end state; day1+ is a switch in
  `Train.admit` the owner may throw later, not a build.
- **R8, resolved.** Enumerated below. PROOF-INPUT is resized to M and its file
  list widened; the push-run skip is out of day 1 and out of the shadow, so no
  push-only producer is dropped.
- **R9, resolved.** (i) The predicate at open is the driver-free merge, one
  shared shell function with `update_pr.sh`; a conflict confined to driver
  files is merged with the drivers (GitHub would otherwise report the head
  unmergeable and run no CI), any other conflict refuses to the fixer as now.
  (ii) The routing change moves into day 1 as its third part, after
  PROOF-INPUT, so no interval exists in which the train's recarry is refused.
  (iii) `Train.merges_as_is` waits on an unreadable ruleset read instead of
  recarrying. `remerge_main.sh` keeps one reason, stated in the note.
- **R10, resolved, in `SWITCH.md`.** A head that conflicts with a landing not
  yet on main waits for that landing's promotion and then meets the conflict
  on main, where its fixer can see it (priced: 15 of 215 entries wait the
  trail, T-f's mean). Promotion re-runs the whole admission read for every
  landed entry, not the head comparison alone.
- **R11, resolved.** `SEATS.md` costs the variant under the haiku constraint;
  the note's section 6 carries its three measurements into the shadow.

## Routed decisions

- **D1 (owner).** Open until after the shadow, as he ruled. The note presents
  three arms, the reviewer's third among them, with what each does to
  `stamp.py` and the probe it owes (`SWITCH.md`).
- **D2 (owner).** Taken: "Day 1 plus shadow".
- **Day-1 dispatch (orchestrator).** The revised note is the dispatchable
  design; its section 3 names the three parts.

## The seven attacks

- **a1, accepted.** P-C2b is withdrawn with the first replay. Savings are
  stated against the loop's own today.
- **a2, accepted.** `SWITCH.md` gives the fallback for U4: derive the merge
  commit from main's first-parent line by subject, as `stamp.py` does.
- **a3, accepted.** If U5 fails, arms (a) and (c) are cancelled: the instrument
  recomputing code ownership would be the grader grading itself. The audit
  step is exempt from any push-run skip.
- **a4, accepted.** The branch on origin is the state of record and the state
  file a cache; `SWITCH.md` lists the restart arm.
- **a5, accepted.** See R4.
- **a6, accepted.** The schedule is restated in the note's section 8 on the
  planner's own hours. `R10-STANDING-CONTRACTS-P2` is named as a hot-file
  neighbour.
- **a7, accepted.** `COST.md`: no candidate clears the bar on any measure.

## R8: every push-only condition in the workflows

`git grep -n -E "event_name *[!=]= *'push'|refs/heads/main" -- .github/workflows`,
less the lines that only fetch main. The proof column is day 1's push-judged
dispatch; the last column is what stays a duty of main's own push run, which
day 1 and the shadow never skip.

| file:line | job, step | on a push | the proof | stays with the push run |
|---|---|---|---|---|
| tests.yml 182, 443, 511, 605, 679, 764, 986, 1039 | job conditions of fast, arch-instrument, browser, briefs, typing, coverage, coverage-ratchet, mutation | the job runs | runs: each already admits `workflow_dispatch` | |
| `tools/ci/prelude.py` 432 | scope | full | **changes: full** | |
| `tools/ci/gate.py` `event_class` | the required set | `REQUIRED["push"]`: adds coverage and coverage-ratchet, drops closure-scope | **changes: the push set** | |
| governance.yml 297, 300 | instrument-self-tests timeout and `SELFTEST_TRACE` | traces every step, 60 min | **changes: traced**, since the drift step that reads the traces can redden `gate` | |
| codeql.yml 229 | the INERT-list check on the extracted files | runs | **changes: runs** | |
| tests.yml 358, 422 | fast: key and save the warmed drift baseline | saves main's cache | does not: a proof must not write main's cache | yes |
| tests.yml 958, 965 | coverage: stage and save per-script coverage | saves the coverage base | does not | yes |
| tests.yml 2138 | closures: consume the batch proof's recordings at an equal tree | consumes | n/a: it is the consumer | yes |
| tests.yml 2306 | ci-ratchet | runs, graded alone, never fails the gate | does not | yes |
| governance.yml 1839 | record | runs on main | does not | yes |
| governance.yml 2208 | delivery-status-publish | runs | does not | yes |

PROOF-INPUT's files: `.github/workflows/ci.yml` (the input and its
pass-through), `governance.yml` (two lines), `codeql.yml` (one), 
`tools/ci/prelude.py`, `tools/ci/gate.py`, each with its self-test arm. Size M.

## Notes for the fixer, from the verdict

f1 (one shared predicate): in the note's section 3. f2 (the row before
review): not built in day 1; R-pipe2 keeps the 34 row and bot cycles in every
candidate, and the upper bound shows what removing them is worth; carried to
R11-PRE-HANDOFF-BOOKKEEPING. f3, f4, f5, f6: `SWITCH.md`. f7, f8: built into
`collect_heads.py`. f9: the shadow's condition 1 is stated on landed against
main under day 1, as the verdict asks. f10, f11: dismissed by the reviewer.
