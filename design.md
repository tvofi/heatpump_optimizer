# Design note: R11-PRE-TOOLCHAIN-PIN (round 2)

Answers `Design review: revise 5caeadfa90c64cebc3d6facf885d87e6ad6d9c54 class-open` (design-verdict/R11-PRE-TOOLCHAIN-PIN at
`c953f9b65134722943a27c35eed20571afd202b2`); the point each paragraph answers is in brackets. Base
`b3831ff64eca1936f0b618193ee86c3e337b51a9` (= `origin/main`; no predecessor handoff head). Evidence: owner ruling 2026-11-13
on card P1; audit row a1 at `d5d7ff81878fe9bc17ee6fcc9e3803d848cbc7f7`,
`dev/audit/rounds/round10/process-convergence-audit.md:375`. No finder harness: owner ruling on a process audit.

## 1. Owning seams

| concern | owner | callers only |
|---|---|---|
| which jobs of a main push run are product, which machinery; each verdict | `tools/ci/gate.py` (owns `REQUIRED`, `PUSH_REPORT_ONLY`, `machinery_line`) | `tools/release/stamp.py` rule 2, the new main-status reader, promotion |
| the stable tools ref: name, paths, "behind", promotion | a new seat instrument named toolchain (Python, beside `tools/audit/seat/open_driver.py`) | the eight freshness sites of section 4 and `tools/audit/seat/prune_refs.py` |

`tests/seam_map.json` maps coordinator methods only; ownership is by `fixer.md` step 17. Promotion reads the machinery
verdict; nothing else crosses.

## 2. Shape

**Before.** [7] `REQUIRED["push"]` is `CODE_UNITS` less `closure-scope` plus `PUSH_ONLY`. Its machinery members are
`tests / arch-instrument`, `tests / briefs`, `tests / closures`, `governance / policy-docs`, `governance / wave-script`,
`governance / env-matrix`. `governance / instrument-self-tests` and `tests / ci-ratchet` are not required: `machinery_line`
prints them. One `gate` conclusion covers the set; `gate_runs` and `gate_verdict` (`tools/release/stamp.py:774`, `:800`)
read it for rule 2. Eight sites compare the tools checkout with `origin/main` (section 4).

**After, status.** [5, 7, 8] **The `gate` job's conclusion does not change on any event**: this replaces round 1's "gate
becomes the product verdict", so every reader of main's `gate` other than the stamp keeps today's meaning. `tools/ci/gate.py`
gains one named tuple of machinery jobs (the six above plus `governance / instrument-self-tests`) and one pure function:
a run's jobs and an event class in, two verdicts out, each `green | red | unread`. Product is the class's required set
less the tuple, computed and never listed, so a change to `REQUIRED` flows through. `unread`: a member absent, unfinished
or cancelled; it never reads green. The gate summary prints one `PRODUCT:` and one `MACHINERY:` line, the second replacing
the report-only line; `tests / ci-ratchet` stays printed and in neither verdict (owner 2026-11-11: advisory on push).
Rule 2 of `tools/release/stamp.py` (`:2999-3005`, and the flushed-head refusal at `:2806`) applies the function to the jobs
`gate_runs` already fetches: product green stamps, product red or unread refuses, machinery red is printed.
The new main-status instrument (reader only; loads `tools/ci/gate.py` by path as `merge_train.py:626-633` does) prints for
the last 20 `ci.yml` main push runs `product-green k/20 (red r, unread u); machinery-green m/20`, one line per run, and
`at <sha>` prints one run's pair; it takes an offline runs file for its self-test.

**After, toolchain.** Branch `toolchain/stable` always points at a commit of main. Verbs of the toolchain instrument:
*behind* `<dir> [--from <sha>] [--all]` prints the count of `<from or HEAD>..origin/toolchain/stable` over the seat paths
(`--all`: unfiltered); it is the only place the ref name and the path list exist. *promote* `[<sha>]`: default the newest
main commit whose machinery verdict is green; refuses a sha not on `origin/main`, a non-fast-forward, a verdict not green;
pushes, reads back, prints `PROMOTE <utc> <old> -> <new> run=<id>`; exits non-zero with `PROMOTE-HELD` when the newest
three concluded main runs are all machinery red or unread; `--init` only while the ref is absent; `--force --why` prints
`PROMOTE-FORCED`. *self-test*. A row in `tools/audit/seat/beatd.jobs.json` runs promote.

```
merge -> main push run -> gate.py: gate (unchanged) + PRODUCT / MACHINERY
   stamp.py rule 2 <- PRODUCT        beat row promote <- MACHINERY green -> push toolchain/stable
   train main_green, tick, wave prompts <- gate (both, as today)
   beatd, tick_loop, relay, opener, train.sh, tick <- toolchain behind <- origin/toolchain/stable
```

**Invariants.** (i) The ref only fast-forwards along main. (ii) No caller moves a checkout backwards; a checkout ahead of
the ref is left alone. (iii) An absent ref refuses with the init command, never falls back to main. (iv)
`HPO_ALLOW_STALE_TOOLS` keeps its meaning. (v) `gate` and `tools/policy/fixtures/required-contexts.json` are untouched.
(vi) [6] `tools/audit/seat/prune_refs.py` keeps `toolchain/*` in `classify` beside `main`; without it the merged-ref rule
(`:22`) deletes the ref and (iii) refuses every caller.

**STALE CHECKOUT under the pin**: the tools checkout lacks seat-path commits of the stable ref. It arises only between a
promotion and a checkout's forward move, so it stays an environment refusal and carry 2's HEAD-keyed rule is kept.

## 3. Alternatives, and why each lost

- *`gate` on push concludes on product only* (round 1): changes what `main_green`, the tick's board line, the wave prompts
  and CLAUDE.md rule 1 read, a behaviour the ruling does not name; the stamp can read the jobs itself.
- *Two new aggregate jobs in `ci.yml`*: two runner starts per push and a second lane list; the jobs dict serves past runs.
- *Commit statuses written by the gate*: a second stored verdict, and a `statuses: write` grant in a read-only job.
- *A moving tag*: `git fetch` does not move an existing tag without force; every caller would carry its own refspec.
- *Repoint each freshness site by hand*: keeps the mirrored constants (`beatd.py:113`, `tick_loop.sh:108`).
- [3] *The outside contract compared with the stable ref*: an allowlist or CODEOWNERS revocation merged to main would not
  bind the train until the next promotion.

## 4. Sibling sites, enumerated

[1, 2, 3, 4] **Tool freshness.** `git grep -n -E '\.\.origin/main|detach[^|]*origin/main|-B [^ ]+ origin/main|origin/main:\{?(rel|tools)' -- tools/audit/seat tools/pr .claude/hooks ':!*selftest*' ':!*/instruments/*' ':!*/fixtures/*'`.
Covered, each a caller of behind with its own constant deleted:

| site | after |
|---|---|
| `tools/audit/seat/pr_args.sh:189-200` `pr_tools_fresh` (`open_pr.sh:138`, `update_pr.sh:63`) | refuses on behind > 0; text names the stable ref |
| `tools/audit/seat/beatd.py:420-465` `fresh` (`SEAT_PATHS` `:113`) | moves to the stable ref, forward only; compiles the ref's `beatd.py` |
| `tools/audit/seat/beatd.py:597-607` `status` `STALE-CODE` | `behind --from <START code> --all`: the running beat lacks promoted commits. Read by `tools/audit/seat/hooks/liveness.py:169`, unchanged. Promotion lag is not STALE-CODE: `PROMOTE-HELD` is the promote row's non-ok outcome, which `status` already alarms |
| `tools/audit/seat/tick_loop.sh:108-139` `fresh_check` (live: `dev/README.md:362` has the orchestrator run it) | `CODE_PATHS` deleted; checks out the stable ref; `SELF_PATHS` judged against it |
| `tools/audit/seat/cloud_relay.sh:556-573` `tools_level` | relay worktree at the stable ref |
| `tools/audit/seat/orchestrator_tick.py:1846` "checkout is N commit(s) behind" | counts behind `--all`; else it flags every merge |
| `tools/audit/seat/train.sh:475` (carry 7: no check today) | refuses before `exec` on behind > 0, same text and override as the opener |
| `tools/audit/seat/merge_train.py:2699-2715` `outside_is_mains` | stays on `origin/main` (alternative 6). A stable-ref train refuses outside pull requests only after a merge touching one of the seven `OUTSIDE_MAIN_COPIES` and until the next promotion; the refusal names promote as the cure |

Dismissed: `.claude/hooks/session-start.sh:105-120` (informational, the work checkout); `orchestrator_tick.py:1375`, `:2133`
(a pull-request head and the handover's `updated-for:`); `tools/audit/seat/roster_edit.py:1083`, `:2247`,
`tools/audit/seat/roster_queue.py:334`, `:443`, `tools/audit/seat/closeout.py:668` (roster and triage data, which follows
main); `bus.sh:2426`, `pr_args.sh:717`, `cloud_relay.sh:1532`, `beatd.py:1412`, `tick_loop.sh:406-490`,
`tools/pr/app_approve.sh:2009`, `tools/pr/app_push.sh:1258` (self-test fixtures inside production files).

[5] **Readers of main's `gate`.** `git grep -n -E "main_green\(|GATE_JOB|REQUIRED not green|Require its .gate. job|gate_runs\(|def tests_gate|push run's .gate." -- tools .claude dev/governance .github ':!*selftest*'`.

| reader | follows |
|---|---|
| `tools/release/stamp.py:2213` `tests_gate` -> rule 2 | product (changed) |
| `dev/governance/roles/nudge.md:93` stamp condition; the wait prompt of `.claude/workflows/web-stamp.js:107`, consumed `:159` | product: both read `main-status at <sha>` (changed; `nudge.md` is policy) |
| `tools/audit/seat/merge_train.py:4366` `main_green` (callers `:4810`, `:4874`, `:4926`; `GATE` `:395`) | both, unchanged; decision: owner |
| `tools/audit/seat/orchestrator_tick.py:1814`, matched by `tools/audit/seat/beat_jobs.py:176` | both, unchanged |
| the same prompt in `.claude/workflows/web-fix-wave.js:106`, `web-decomp-stage.js:108`, `web-triage.js:107`, `web-fragments.md:109` | both, unchanged |

Dismissed hits: `.claude/workflows/audit-find.js:392` and `dev/governance/dimensions/D3.md:40` (`GATE_JOBS`, a mutation
setting); in-file self-tests of `merge_train.py`, `orchestrator_tick.py`, `stamp.py:1271`; the `beat_jobs` fixtures.
`git grep -n "STALE" -- tools/audit/seat`: readers of the refusal text (`reason`, `open_driver.py:215-222`).
Out of scope, measured as p3: cloud seats, which run tools from the session checkout at the dispatched head
(`tools/audit/seat/cloud_dispatch.py`); enumerator `git grep -n "parents\[3\]\|PR_ARGS_DIR" -- tools/audit/seat tools/pr tools/policy`.

## 5. Evidence plan, by file

| file | failing test first | null control | mutation target |
|---|---|---|---|
| `tools/ci/gate.py` self-test | [7] a push run red only in `tests / closures` reads PRODUCT green, MACHINERY red, `gate` red | red `tests / fast (3.14)` reads PRODUCT red | emptying the tuple; `unread` read as green; a required name in neither verdict |
| `tools/release/stamp.py` self-test | a head whose only red is `tests / closures` stamps (refused today: `gate` is red) | product-red and product-unread heads refuse without `--allow-red` | product replaced by the whole push set |
| main-status self-test | k/20 for a fixture of known k; a cancelled run counts unread | 20 green runs print 20/20 | window constant; unread counted green |
| toolchain self-test (`tests/throwaway_git.py`) | promote refuses off-main, non-ff, not green; three red runs print `PROMOTE-HELD`; behind is 0 ahead of the ref; absent ref refuses | green on-main ff promotes; read-back equals the pushed sha | each refusal dropped in turn |
| `tools/audit/seat/prune_refs.py` `_self_test_keeps` (`:576`) | [6] a merged `toolchain/stable` is kept | a merged ordinary ref is still deleted | the keep line |
| `beatd.py`, `tick_loop.sh`, `cloud_relay.sh` self-tests | the checkout moves to the stable ref, not main; an ahead checkout stays; STALE-CODE is silent when main alone moved | a behind-ref checkout moves; STALE-CODE fires behind the ref | the forward-only test; the ref swapped for `origin/main` |
| `train.sh`, `pr_args.sh`, `orchestrator_tick.py` self-tests | a checkout behind the ref refuses (train, opener) or flags (tick); main ahead of the ref does neither | level with the ref: runs, no flag | the count compared with a constant 0 |
| `merge_train.py` self-test | the outside refusal after a main-only change names promote | copies equal to main's admit | n/a: text only |
| `tools/audit/seat/open_driver_selftest.py` | carries 1 (i)-(iv) and 2 (i)-(v), verbatim | as the brief states | as the brief states; add the plants to `dev/audit/harnesses/r10_open_driver_mutants.py` |

Done: main-status prints the share at the fixer's merge base and after (literals in `## Figures`); the toolchain self-test
is a step of `instrument-self-tests` with its measured entry in `tools/ci/selftest_closures.json`. No golden moves; neither
claim file is touched; `tests/structure_budgets.json` is not reached.

## 6. Hot files, order, parts, carries, cost

[8] `design/R11-PRE-PARALLEL-PIPELINE` at `22fdbabafb30647a27332d6096df1feb02fc8fb7` owns what a CI run is judged as
(`event_class`, `REQUIRED`) and edits `.github/workflows/governance.yml`. **Its part 2 (the proof input) lands first; this
group's p2 lands after it.** p2 adds one tuple and one function and edits neither `REQUIRED` nor `event_class`; because
the function takes the class, a proof judged as a push prints the same two lines with no new event condition.
Other hot files: `tools/audit/seat/beat_jobs.py` and `dev/governance/roles/orchestrator.md` (serial across the R11-PRE
groups), `tools/audit/seat/open_driver.py` (R10-SEAT-IDENTITY-P5), `tools/audit/seat/merge_train.py`, `tools/release/stamp.py`.
Parts: **p1** the toolchain instrument, the eight sites, the prune guard, the beat row, carries 1, 2 and 7; **p2** the
verdict function, main-status, rule 2, and the stamp sentences of `nudge.md` and `orchestrator.md` (policy: the owner's
approving review); **p3** cloud seats, only if its enumerator returns a bounded set. p1 and p2 touch disjoint files.

[9] Carries, re-measured at the base:
- 0: `git diff 26dbf7c43e b3831ff64e` is empty over the harness and its targets; at 26dbf7c43e
  `dev/audit/harnesses/r10_open_driver_mutants.py` exited 0 with `RESULT survived=0`. Carry: dismissed: no ABORT at the base.
- 1, 2: p1, as written; the recorded HEAD is the driver's own checkout, the one behind judges.
- 7: p1, the `train.sh` row above. The relay is covered by `tools_level`.
- 3: site `tools/pr/cancel_superseded.py:109-110` (`plan`) and `:402` (`sweep_plan`); evidence as the carry states.
- 4: half built at the base. `_cut_at_prelude` (`tests/ci_ratchet.py:536`, commit bc85e0900a) already drops run
  43602217369 from the window, self-test at `:1137-1158`. Owed: the advisory arm; the job at
  `.github/workflows/tests.yml:2273` has none.
- 5: one owner for the concept. `unread` for a CI run's jobs is this note's function in `tools/ci/gate.py`; the helper
  owns only what a process check does with it (advisory line, the count of three, escalation) and calls the function.
  Sites: `tests/ci_ratchet.py:595`, `tools/ci/selftest_scope.py`, `merge_train.py:781` `introduced_at`,
  `tools/audit/seat/review_packet.py:253-259`, `tools/pr/figure_block.py:57`.
- 6, 8: half built at the base. `classify --pr` answers WAIT rc 3 `introduced: pending` on a running job and `bus.sh`
  dispatches on it; the remaining refusal is `review_packet.py:259` through `:721-722`. Carry 8's first item (a cancelled
  main run leaves `introduced_at` no base job) goes with the same reading.

**Cost (step 6).** p1 with carry 7 and p2 fit L. Carries 3, 4, 5, 6 and 8 add about nine files and one helper: XL, and a
second concern (what a process check does with an unreadable input) that the toolchain seam does not own.
decision: orchestrator, proposed as the reviewer did: (A) this group keeps p1, p2, p3 and carries 0, 1, 2, 7; (B) a new
group for carries 5, 4, 6, 8, `after` this group because it calls the verdict function; (C) carry 3 alone, S, no design.
If the orchestrator keeps them here, B is p4 and C is p5, each with the evidence its carry states, and the group is XL.
decision: owner: whether a machinery-red, product-green main still stops train admissions (this design: yes, unchanged);
who may push `toolchain/stable` and whether a ruleset protects it.

## Notes for the fixer

- The roster at the base holds `"carry": []` and `after: ["R10-CATALOG-PR"]` for this group
  (`dev/programme/rosters/wave-r10-groups.json`); the payload gives nine carries and no `after`. Carry: O1
- Rollout: the orchestrator runs promote with init at p1's merge commit straight after the merge; until then new-code
  callers refuse by invariant (iii). State it in the body's merge instructions. Carry: R11-PRE-TOOLCHAIN-PIN
- `toolchain/*` is outside the `main-protect` ruleset; the design works unprotected because promote verifies ancestry on
  every read-back. Carry: O2
- The four wave prompts are copies of one text; check whether a lint holds them identical before changing only
  `web-stamp.js`, and extend that lint in the same pull request if so. Carry: R11-PRE-TOOLCHAIN-PIN
- `tools/audit/seat/open_driver.py` has no verb dispatch; the retry verb adds the first. Keep `run_pass` free of argv.
  fails.json: load `:230`, pop `:247`, write `:254`. Carry: R11-PRE-TOOLCHAIN-PIN
- `gather_runs` (`tests/ci_ratchet.py:667`) already fetches main's push runs with their jobs; reuse it before writing a
  second fetch. Carry: R11-PRE-TOOLCHAIN-PIN
- A new `instrument-self-tests` step needs its `id`, the `steps.scope.outputs.<id>` condition and a
  `selftest_scope.py record` on Linux. Carry: R11-PRE-TOOLCHAIN-PIN
- New instrument docs and the policy sentences count against `dev/governance/config/policy_budgets.json`; pay by
  cutting, not by a raise. Carry: R11-PRE-TOOLCHAIN-PIN
- Not verified in this seat: which lanes were red in the 11-09..11-13 window, so the share at the base may differ from
  the audit's run-level figure; whether `orchestrator_tick.py:1814` is read by anything besides the board family.
  Carry: R11-PRE-TOOLCHAIN-PIN
