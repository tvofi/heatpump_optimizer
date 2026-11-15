# Design note: R11-PRE-TOOLCHAIN-PIN (round 3)

Answers `Design review: revise ab1d7b76789a6cde6d8ebf7678016790e076bda8 architecture-unsound` (design-verdict/R11-PRE-TOOLCHAIN-PIN at
`ad7f4bd6126fafbf568878f6b4004d7ca1a34cdd`): [R1] marks its revise point, [dr6]..[dr10] its notes. Base
`e0ad8b2bd32b60a67975039f8573dbba2207757f` (= `origin/main`; no predecessor handoff head), three commits past the reviewer's
b880dc914f; `git diff b880dc914f e0ad8b2bd3` over the files named here prints one hunk, a timeout in
`.github/workflows/governance.yml`. Line numbers are at the base. Evidence: owner ruling 2026-11-13 on card P1; audit row a1 at
`d5d7ff81878fe9bc17ee6fcc9e3803d848cbc7f7`, `dev/audit/rounds/round10/process-convergence-audit.md:375`. No finder
harness: owner ruling on a process audit.

## 1. Owning seams

| concern | owner | callers only |
|---|---|---|
| which jobs of a main push run are product, which machinery; each verdict of one run | `tools/ci/gate.py` (owns `REQUIRED`, `PUSH_REPORT_ONLY`, `machinery_line`) | `tools/release/stamp.py`, `tools/audit/seat/scorecard.py`, promotion |
| [R1] the 20-run window over main's push runs and every share printed over it | `tools/audit/seat/scorecard.py` (`WINDOW_RUNS` `:75`, `line_a` `:102-111`), fed by the beat cache | the `scorecard` row of `tools/audit/seat/beatd.jobs.json` (`:302`) |
| [R1] the pair of verdicts of the one run at a head, and the stamp's refusal on it | `tools/release/stamp.py` (`tests_gate` `:2213`, rule 2) | `dev/governance/roles/nudge.md`, `.claude/workflows/web-stamp.js` |
| the stable tools ref: name, paths, "behind", promotion | a new seat instrument named toolchain (Python, beside `tools/audit/seat/open_driver.py`) | the freshness sites of section 4 and `tools/audit/seat/prune_refs.py` |

[R1] **No main-status instrument is built**: round 2's reader is withdrawn. Its window half is two scorecard lines and its
single-run half is a read-only flag of the stamp, so the window has one owner, one input (the cache) and one unread rule.
`tests/seam_map.json` maps coordinator methods only; ownership is by `fixer.md` step 17. Promotion reads the machinery
verdict; nothing else crosses.

## 2. Shape

**Before.** `REQUIRED["push"]` is `CODE_UNITS` less `closure-scope` plus `PUSH_ONLY`. Its machinery members are
`tests / arch-instrument`, `tests / briefs`, `tests / closures`, `governance / policy-docs`, `governance / wave-script`,
`governance / env-matrix`. `governance / instrument-self-tests` and `tests / ci-ratchet` are not required: `machinery_line`
prints them. One `gate` conclusion covers the set; `gate_runs` and `gate_verdict` (`tools/release/stamp.py:774`, `:800`)
read it for rule 2, and the scorecard's A_gate reads it over 20 concluded runs. The sites of section 4 compare the tools
checkout with `origin/main`, or launch from it with no check.

**After, status.** **The `gate` job's conclusion does not change on any event.** `tools/ci/gate.py` gains one named tuple
of machinery jobs (the six above plus `governance / instrument-self-tests`) and one pure function: a run's job listing
and an event class in, two verdicts out, each `green | red | unread`. Product is the class's required set less the tuple,
computed and never listed, so a change to `REQUIRED` flows through. `unread`: a member absent, unfinished or cancelled; it
never reads green. The gate summary prints one PRODUCT and one MACHINERY line, the second replacing the report-only line;
`tests / ci-ratchet` stays printed and in neither verdict (owner 2026-11-11: advisory on push).
- *Stamp.* Rule 2 (`tools/release/stamp.py:2998-3004`, and the flushed-head refusal `:2803-2808`) applies the function to
  the jobs `gate_runs` already fetches (`:785`): product green stamps, product red or unread refuses, machinery red is
  printed. A new read-only check flag takes a sha, runs `tests_gate` alone (no tree precondition, no write), prints the
  pair and exits with rule 2's code; it is the `at <sha>` reader.
- [R1] *Scorecard.* `report` (`:220-239`) keeps each cached listing whole instead of its `gate` entry, loads
  `tools/ci/gate.py` by path as `merge_train.py:626-633` does, and `line_a` prints two more lines over the same window
  as A_gate: A_prod, `k/read read = p% (red r; unread u of n; window ..)`, and A_mach in the same form. A run whose
  conclusion is success counts green in both without its listing, the shortcut A_gate already takes (`:106`); a failed
  run with no cached listing is unread (today's rule); a listing the function calls unread is unread. A_gate and A_run
  are unchanged. The instrument still makes no GitHub call. The window stays A's: 20 runs concluded success or failure;
  a cancelled run is outside it and is line C's count, so the done criterion reads "the last 20 concluded main push runs".

**After, toolchain.** Branch `toolchain/stable` always points at a commit of main. Verbs of the toolchain instrument:
*behind* `<dir> [--from <sha>] [--all]` prints the count of `<from or HEAD>..origin/toolchain/stable` over the seat paths
(`--all`: unfiltered); it is the only place the ref name and the path list exist. *promote* `[<sha>]`: default the newest
main commit whose machinery verdict is green; refuses a sha not on `origin/main`, a non-fast-forward, a verdict not green;
pushes, reads back, prints `PROMOTE <utc> <old> -> <new> run=<id>`; exits non-zero with `PROMOTE-HELD` when the newest
three concluded main runs are all machinery red or unread; `--init` only while the ref is absent; `--force --why` prints
`PROMOTE-FORCED`. *self-test*. A row in `tools/audit/seat/beatd.jobs.json` runs promote.

```
merge -> main push run -> gate.py: gate (unchanged) + PRODUCT / MACHINERY (one function)
   stamp.py rule 2 and its check flag <- PRODUCT at one head       nudge.md, web-stamp.js <- the check flag
   beat cache -> scorecard.py line_a <- the function, per cached run -> A_gate, A_run, A_prod, A_mach (window 20)
   beat row promote <- MACHINERY green -> push toolchain/stable
   train main_green, tick, wave prompts <- gate (both, as today)
   beatd, tick_loop, relay, opener, train.sh, remerge_main.sh, merge_pr.sh, tick <- toolchain behind <- origin/toolchain/stable
```

**Invariants.** (i) The ref only fast-forwards along main. (ii) No caller moves a checkout backwards; a checkout ahead of
the ref is left alone. (iii) An absent ref refuses with the init command, never falls back to main. (iv)
`HPO_ALLOW_STALE_TOOLS` keeps its meaning. (v) `gate` and `tools/policy/fixtures/required-contexts.json` are untouched.
(vi) `tools/audit/seat/prune_refs.py` keeps `toolchain/*` in `classify` beside `main`; without it the merged-ref rule
(`:22`) deletes the ref and (iii) refuses every caller. (vii) [R1] No second module holds a run window or fetches main's
runs for a share.

**STALE CHECKOUT under the pin**: the tools checkout lacks seat-path commits of the stable ref. It arises only between a
promotion and a checkout's forward move, so it stays an environment refusal and carry 2's HEAD-keyed rule is kept.

## 3. Alternatives, and why each lost

- [R1] *A separate main-status reader* (round 2): a second owner of the 20-run share beside `line_a`, with a second input
  (a GitHub fetch against the beat cache) and a second unread rule.
- [R1] *The scorecard also prints the single run at a sha*: it would need a GitHub call (the cache holds no run the beat
  has not listed yet), which its contract forbids (`scorecard.py:8-10`); the stamp already fetches that run.
- *`gate` on push concludes on product only* (round 1): changes what `main_green`, the tick's board line, the wave prompts
  and CLAUDE.md rule 1 read, a behaviour the ruling does not name; the stamp can read the jobs itself.
- *Two new aggregate jobs in `ci.yml`*: two runner starts per push and a second lane list; the jobs dict serves past runs.
- *Commit statuses written by the gate*: a second stored verdict, and a `statuses: write` grant in a read-only job.
- *A moving tag*: `git fetch` does not move an existing tag without force; every caller would carry its own refspec.
- *Repoint each freshness site by hand*: keeps the mirrored constants (`beatd.py:113`, `tick_loop.sh:108`).
- *The outside contract compared with the stable ref*: an allowlist or CODEOWNERS revocation merged to main would not
  bind the train until the next promotion.

## 4. Sibling sites, enumerated

**Tool freshness.** `git grep -n -E '\.\.origin/main|detach[^|]*origin/main|-B [^ ]+ origin/main|origin/main:\{?(rel|tools)' -- tools/audit/seat tools/pr .claude/hooks ':!*selftest*' ':!*/instruments/*' ':!*/fixtures/*'`,
and for launchers with no check, `git grep -ln "pr_args.sh" -- tools/audit/seat ':!*selftest*' ':!*.md'` less
`git grep -l "pr_tools_fresh" -- tools/audit/seat`. The rule: the check sits in each script an operator, the beat or
the train launches from the tools checkout to write a pull request or main; a script reached only through a checked one
inherits it. Covered, each a caller of behind with its own constant deleted:

| site | after |
|---|---|
| `tools/audit/seat/pr_args.sh:189-200` `pr_tools_fresh` (`open_pr.sh:138`, `update_pr.sh:63`) | refuses on behind > 0; text names the stable ref |
| `tools/audit/seat/beatd.py:420-465` `fresh` (`SEAT_PATHS` `:113`) | moves to the stable ref, forward only; compiles the ref's `beatd.py` |
| `tools/audit/seat/beatd.py:597-607` `status` `STALE-CODE` | `behind --from <START code> --all`: the running beat lacks promoted commits. Read by `tools/audit/seat/hooks/liveness.py:169`, unchanged. Promotion lag is not STALE-CODE: `PROMOTE-HELD` is the promote row's non-ok outcome, which `status` already alarms |
| `tools/audit/seat/tick_loop.sh:108-139` `fresh_check` (live: `dev/README.md:362` has the orchestrator run it) | `CODE_PATHS` deleted; checks out the stable ref; `SELF_PATHS` judged against it |
| `tools/audit/seat/cloud_relay.sh:556-573` `tools_level` | relay worktree at the stable ref |
| `tools/audit/seat/orchestrator_tick.py:1846` "checkout is N commit(s) behind" | counts behind `--all`; else it flags every merge. [dr9] An edit of the existing count only: no arm is added, as `design/R11-PRE-STANDING-SCRIPTS` at d1a4ae6a74 rules for this file |
| `tools/audit/seat/train.sh:475` (carry 7: no check today) | refuses before `exec` on behind > 0, same text and override as the opener |
| [dr6] `tools/audit/seat/remerge_main.sh:29` (sources `pr_args.sh`, never calls `pr_tools_fresh`) | calls it after the source line, before the argument parse: same refusal, same override |
| [dr6] `tools/audit/seat/merge_pr.sh:359` (the hand-merge launcher `nudge.md` names; sources `pr_args.sh` only for its self-test bound, `:22`) | calls the instrument's behind before the argument parse: same refusal text, same override |
| `tools/audit/seat/merge_train.py:2699-2715` `outside_is_mains` | stays on `origin/main` (last alternative). A stable-ref train refuses outside pull requests only after a merge touching one of the seven `OUTSIDE_MAIN_COPIES` and until the next promotion; the refusal names promote as the cure |

Dismissed: `.claude/hooks/session-start.sh:105-120`, `:195-197` (informational, the work checkout);
`orchestrator_tick.py:1375`, `:2133`, [dr7] `:2140` (a pull-request head; the handover's `updated-for:`, both lines of one
function) and [dr7] `:2909`, `:2911`, `:2930`, `:3415`, `:4033` (in-file self-test fakes); `tools/audit/seat/roster_edit.py:1083`,
`:2247`, `tools/audit/seat/roster_queue.py:334`, `:443`, `:622`, `tools/audit/seat/closeout.py:668` (roster and triage data,
which follows main); `bus.sh:2439`, `pr_args.sh:717`, `cloud_relay.sh:1532`, `beatd.py:1448`, `tick_loop.sh:406-490`,
`tools/pr/app_approve.sh:2009`, `tools/pr/app_push.sh:1258` (self-test fixtures and mutant specs inside production files).
[dr6] From the second enumerator: `handoff_push.sh` (run from a fixer's work checkout, which is behind by design);
`body_patch.sh`, `delivery_row.sh` (reached only through `open_pr.sh` and `update_pr.sh`); `ci-watch.sh`, `failure_logs.sh`,
`heartbeat.sh` (read-only); `seat_venv.sh`, `cloud-setup.sh` (environment setup); `bus.sh`, `tick_loop.sh` (the hit is a
self-test bound; the loop has its own row); `merge_train.py`, `review_packet.py`, `ledger.py`, `bare_array.py`,
`ref_privacy.py` (the name in a comment, a table or a self-test).

**Readers of main's `gate`.** `git grep -n -E "main_green\(|GATE_JOB|REQUIRED not green|Require its .gate. job|gate_runs\(|def tests_gate|push run's .gate." -- tools .claude dev/governance .github ':!*selftest*'`,
and [R1] `git grep -n "A_gate" -- tools dev/governance`.

| reader | follows |
|---|---|
| `tools/release/stamp.py:2213` `tests_gate` -> rule 2 | product (changed) |
| `dev/governance/roles/nudge.md:93` stamp condition; the wait prompt of `.claude/workflows/web-stamp.js:105-109`, consumed `:159` | product: both read the stamp's check flag at the sha (changed; `nudge.md` is policy) |
| [R1] `tools/audit/seat/scorecard.py:102-111` `line_a`, A_gate | `gate`, unchanged; A_prod and A_mach are added beside it |
| [R1] `dev/governance/decisions/0018-objective-function.md:194` `product_green`, which names A_gate | unchanged here; decision: owner (section 6) |
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
| `tools/ci/gate.py` self-test | a push run red only in `tests / closures` reads PRODUCT green, MACHINERY red, `gate` red | red `tests / fast (3.14)` reads PRODUCT red | emptying the tuple; `unread` read as green; a required name in neither verdict |
| `tools/release/stamp.py` self-test | a head whose only red is `tests / closures` stamps (refused today: `gate` is red); the check flag prints the pair for it and exits 0, writing nothing | product-red and product-unread heads refuse without `--allow-red`, and the check flag exits 2 | product replaced by the whole push set; the check flag reaching a write |
| [R1] `tools/audit/seat/scorecard_selftest.py` (`cases` `:40`, `MUTANTS` `:157-166`) | a failed run whose only red is `tests / closures` counts green in A_prod, red in A_mach and A_gate; a failed run with no listing, and one whose listing lacks a required member, are unread in both | a failed run red in `tests / fast (3.14)` counts red in A_prod, green in A_mach; a window of success runs prints 100% on both | A_prod reading the `gate` entry; the unread arm dropped; the function's verdict replaced by the run conclusion; the shared window constant. The report-length assertion (`:146`) is derived, not raised by hand |
| toolchain self-test (`tests/throwaway_git.py`) | promote refuses off-main, non-ff, not green; three red runs print `PROMOTE-HELD`; behind is 0 ahead of the ref; absent ref refuses | green on-main ff promotes; read-back equals the pushed sha | each refusal dropped in turn |
| `tools/audit/seat/prune_refs.py` `_self_test_keeps` (`:576`) | a merged `toolchain/stable` is kept | a merged ordinary ref is still deleted | the keep line |
| `beatd.py`, `tick_loop.sh`, `cloud_relay.sh` self-tests | the checkout moves to the stable ref, not main; an ahead checkout stays; STALE-CODE is silent when main alone moved | a behind-ref checkout moves; STALE-CODE fires behind the ref | the forward-only test; the ref swapped for `origin/main` |
| `train.sh`, `remerge_main.sh`, `merge_pr.sh`, `pr_args.sh`, `orchestrator_tick.py` self-tests | a checkout behind the ref refuses (train, remerge, hand merge, opener) or flags (tick); main ahead of the ref does neither | level with the ref: runs, no flag | the count compared with a constant 0 |
| `merge_train.py` self-test | the outside refusal after a main-only change names promote | copies equal to main's admit | n/a: text only |
| `tools/audit/seat/open_driver_selftest.py` | carries 1 (i)-(iv) and 2 (i)-(v), verbatim | as the brief states | as the brief states; add the plants to `dev/audit/harnesses/r10_open_driver_mutants.py` |

Done: [R1] `scorecard.py report` over the beat's `<state>/scorecard/` prints A_prod at the fixer's merge base and after
(literals in `## Figures`); with no producer for that directory the line prints unread and the criterion is unmet, hence
the edge in section 6. The toolchain self-test is a step of `instrument-self-tests` with its measured entry in
`tools/ci/selftest_closures.json`. No golden moves; neither claim file is touched; `tests/structure_budgets.json` is not
reached.

## 6. Hot files, order, parts, carries, cost

`design/R11-PRE-PARALLEL-PIPELINE` at `22fdbabafb30647a27332d6096df1feb02fc8fb7` owns what a CI run is judged as
(`event_class`, `REQUIRED`) and edits `.github/workflows/governance.yml`. **Its part 2 (the proof input) lands first; this
group's p2 lands after it.** p2 adds one tuple and one function and edits neither `REQUIRED` nor `event_class`.
[R1] R11-PRE-ROUND-METRICS (in progress on the round-11 roster at add5384763) builds the producer of the scorecard's
inputs and edits `scorecard.py`: **p2 lands after it** and requires of it only what `scorecard.py:14` already states, a
whole job listing per failed run. decision: orchestrator: add that `after` edge.
[dr10] `design/R11-PRE-SHARED-FILES` at 20cafac7df (its D4) asks for this group's p1 before its part 3: accepted; p1
records its self-test entry under whichever table regime main holds at its merge base.
Other hot files: `tools/audit/seat/beat_jobs.py` and `dev/governance/roles/orchestrator.md` (serial across the R11-PRE
groups), `tools/audit/seat/open_driver.py` (R10-SEAT-IDENTITY-P5), `tools/audit/seat/merge_train.py`, `tools/release/stamp.py`.
Parts: **p1** the toolchain instrument, the section 4 sites, the prune guard, the beat row, carries 1, 2 and 7; **p2** the
verdict function, the two scorecard lines, rule 2 with its check flag, and the stamp sentences of `nudge.md` and
`orchestrator.md` (policy: the owner's approving review); **p3** cloud seats, only if its enumerator returns a bounded
set. p1 and p2 touch disjoint files.

Carries, re-measured at the base:
- 0: `git diff 26dbf7c43e e0ad8b2bd3` is empty over the harness and its targets; at 26dbf7c43e
  `dev/audit/harnesses/r10_open_driver_mutants.py` exited 0 with `RESULT survived=0`. Carry: dismissed: no ABORT at the base.
- 1, 2: p1, as written; the recorded HEAD is the driver's own checkout, the one behind judges.
- 7: p1, the `train.sh` and [dr6] `remerge_main.sh` and `merge_pr.sh` rows above. The relay is covered by `tools_level`.
- [dr10] SHARED-FILES carry 7's aside (2026-11-14: the opener driver printed no SKIP, NEEDS-TITLE or START line for
  r10-arch-docs-delta): p1, measure first. The listing is `run_pass` in `tools/audit/seat/open_driver.py`; if the fixer
  cannot make a fixture handoff ref go unlisted, the measurement is recorded and the aside dismissed.
- 3: site `tools/pr/cancel_superseded.py:109-110` (`plan`) and `:402` (`sweep_plan`); evidence as the carry states.
- 4: half built at the base. `_cut_at_prelude` (`tests/ci_ratchet.py:537`, commit bc85e0900a) already drops run
  43602217369 from the window. Owed: the advisory arm; the job at `.github/workflows/tests.yml:2273` has none.
- 5: [R1] the word unread has three uses and one owner each. For a CI run's jobs it is the function in
  `tools/ci/gate.py`. In `scorecard.py` (`:10`) it is an input file or cached listing the report cannot read, and for
  line A's runs it defers to the function. The L3 helper owns only what a process check does with either (advisory
  line, the count of three, escalation) and calls the function. Sites: `tests/ci_ratchet.py:594-596`,
  `tools/ci/selftest_scope.py`, `merge_train.py:781` `introduced_at`, `tools/audit/seat/review_packet.py:253-259`.
  [dr8] `tools/pr/figure_block.py:57` is withdrawn (a git helper that raises `Refused`, no CI read); the figure-block
  site is re-derived when the carry is built, by `git grep -n -i "unreadable\|fail closed" -- tools/pr tools/ci`.
- 6, 8: half built at the base. `classify --pr` answers WAIT rc 3 `introduced: pending` on a running job and `bus.sh`
  dispatches on it; the remaining refusal is `review_packet.py:259` through `:721-722`. Carry 8's first item (a cancelled
  main run leaves `introduced_at` no base job) goes with the same reading.

**Cost (step 6).** p1 with carry 7 and p2 fit L. Carries 3, 4, 5, 6 and 8 add about nine files and one helper: XL, and a
second concern (what a process check does with an unreadable input) that the toolchain seam does not own.
decision: orchestrator, as the reviewer routed it: (A) this group keeps p1, p2, p3 and carries 0, 1, 2, 7; (B) a new
group for carries 5, 4, 6, 8, `after` this group because it calls the verdict function; (C) carry 3 alone, S, no design.
If the orchestrator keeps them here, B is p4 and C is p5, each with the evidence its carry states, and the group is XL.
decision: owner: whether a machinery-red, product-green main still stops train admissions (this design: yes, unchanged);
who may push `toolchain/stable` and whether a ruleset protects it; [R1] whether decision 0018's `product_green` moves
from A_gate to A_prod (this design: no change; the two lines print side by side so the owner can compare first).

## Notes for the fixer

- Rollout: the orchestrator runs promote with init at p1's merge commit straight after the merge; until then new-code
  callers refuse by invariant (iii). State it in the body's merge instructions. Carry: R11-PRE-TOOLCHAIN-PIN
- `toolchain/*` is outside the `main-protect` ruleset; the design works unprotected because promote verifies ancestry on
  every read-back. Carry: O2
- The four wave prompts are copies of one text; check whether a lint holds them identical before changing only
  `web-stamp.js`, and extend that lint in the same pull request if so. Carry: R11-PRE-TOOLCHAIN-PIN
- A cloud stamp seat has no `gh`; the check flag must answer through the REST arm of `gate_source`, and its self-test
  holds one case per source. Carry: R11-PRE-TOOLCHAIN-PIN
- `scorecard.py` is run with `python3 -I`; load `tools/ci/gate.py` by file path, not by import, and print
  `A_prod  unread (gate.py)` when it cannot be loaded. `tools/audit/seat/instruments/scorecard.py.md` and the fixture in
  `tools/audit/seat/beat_jobs_selftest.py:517` name the lines. Carry: R11-PRE-TOOLCHAIN-PIN
- Re-read R11-PRE-ROUND-METRICS's merged diff before p2: if it changed `line_a` or the listing schema, re-anchor the
  two lines on its shape; do not add a second reader of the cache. Carry: R11-PRE-TOOLCHAIN-PIN
- `tools/audit/seat/open_driver.py` has no verb dispatch; the retry verb adds the first. Keep `run_pass` free of argv.
  fails.json: load `:230`, pop `:247`, write `:254`. Carry: R11-PRE-TOOLCHAIN-PIN
- A new `instrument-self-tests` step needs its `id`, the `steps.scope.outputs.<id>` condition and a
  `selftest_scope.py record` on Linux. Carry: R11-PRE-TOOLCHAIN-PIN
- New instrument docs and the policy sentences count against `dev/governance/config/policy_budgets.json`; pay by
  cutting, not by a raise. Carry: R11-PRE-TOOLCHAIN-PIN
- Not verified in this seat: which lanes were red in the 11-09..11-13 window, so the share at the base may differ from
  the audit's run-level figure; whether `orchestrator_tick.py:1814` is read by anything besides the board family;
  whether R11-PRE-ROUND-METRICS's producer caches a listing for every failed run in the window.
  Carry: R11-PRE-TOOLCHAIN-PIN

Tokens: this seat's count is not reported by the harness; no subagents.
