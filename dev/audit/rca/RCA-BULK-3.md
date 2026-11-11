# RCA-BULK-3: five owed root-cause analyses

Root-cause seat, written 2026-09-28 under `tools/audit/briefs/root-cause.md` and `.claude/rules/defect-root-cause.md`, read at `origin/main` `3490cb16`. Nothing was posted. Timestamps come from GitHub, and release spans come from `git tag --contains`. Helpers and demonstration outputs are in `phaseC/bulk3/`: `demo_1721.txt`, `typing_arm_demo.py` with `demo_1545.txt`, and `merge_shape_guard_lite.py` with `demo_1041.txt`. None of the five items already had an RCA in `rca_inventory.json`. For #1070, the countermeasure did land, as `97d9bdb3`/#1124, but no RCA was ever written for it. That is recorded below.

---

## 1. #1721: Governance red on main (trigger 2)

**Cause.** #1715 (F11.3, merged `87d780c7`, 10:50:48Z) extended `counts.mjs requiredContextsDrift` to compare every leaf of the ruleset object. It compared those leaves against `ruleset_objects`, a fixture recorded from an admin read, which carries `bypass_actors`. CI reads the ruleset as the Actions `GITHUB_TOKEN`, and GitHub omits that field for that token. The comparator's input depends on who reads it. #1715 gave the comparator a precondition: every compared field is visible to every principal that runs it. Before #1715 the reader only touched `rules`, which every principal can see.

Why #1715's own PR stayed green: `governance.yml` restores `.claude/workflows/*.mjs` from the base (`PINNED`). So `policy-docs` on #1715 ran the old comparator. The new comparator first ran under the Actions token on the push to main.

**Process state: (c).** Both relevant processes existed and were followed.
- RC1 (`b6234f2c`, #1637): `prepr.sh` steps 3e–3g run the head copy of every pinned grader locally. A local run uses the seat's `gh` identity or no `gh` at all, never the Actions token, so the process is blind to principal.
- `graders-head-copy` (tests.yml, decision 0013 amended): it runs the PR's own copy of a pinned grader so that "a changed grader still shows red or green on the pull request that changes it." Its roster is hard-coded to `coverage_ratchet` and `delivery_status` (`for g in …`). The governance `.mjs` graders are not on it.

Both processes were obeyed and neither produced the intended result. A firmer instruction would not help.

**Class reach.** Since pinning (2026-09-24 19:49Z) there have been 98 merges. 12 of them touched pinned `.claude/workflows/*.{mjs,py}`, and 2 of those carried this shape: #1633 (caught by its reviewer) and #1721 (escaped). Of all the tree's readers, only the ruleset reader depends on the principal.

**Cost test.**
- Defect: main was red for 2 h 21 m (10:50:48Z to the #1721 merge at 13:12:16Z). That red covered `policy-docs`, `env-matrix` and `pr-contract` on every open PR, and cost one hotfix PR plus the v6.7.7 stamp. v6.7.6 shipped with the defect (tooling only, not user-facing).
- P: 1 escape in 12 releases.
- Countermeasure: add a governance arm to `graders-head-copy`. When the three-dot diff touches `.claude/workflows/**`, it runs the PR's `policy_lint.mjs` and `field_coverage.mjs` under the read-only `GITHUB_TOKEN`. It is non-required, like the existing job. On #1715, `policy-docs` took 24 s, so the arm costs about 3 pushes × 24 s × 12% of merges ≈ 70 s of runner time per release and 0 s on the critical path. The defect side is 141 min ÷ 12 releases ≈ 11.8 min per release. **Passes, about 10×.**

**Demonstration (`demo_1721.txt`).** The mechanism is shown locally with `field_coverage.mjs --only ruleset --ruleset-json`. The Actions view is the recorded object without `bypass_actors`:

| tree | admin view | Actions view |
|---|---|---|
| `87d780c7` | read=40, refused=0 | **REFUSED**, "unperturbed, is already red" |
| `8b61aed3` | read=40, refused=0 | read=37, refused=0 |

The admin column is the null control. It is green at both SHAs, which is exactly what every pre-merge run saw. The CI arm's own red and green runs, on a branch reverting `counts.mjs` to `87d780c7`, are owed by its fixer.

**Class:** P11 (the only oracle for an external counterpart is a double recorded from a different principal). This is an instrument-side member, and the mechanism stretches the class. **Verdict: build.** Placement: **F11.x**, a new F11.7, beside F11.3's barrier.

---

## 2. #1545: bare `ConfigEntry` against `qs_entry_param_bare=0` (plan §6 seat)

**Cause, corrected.** #1545 was filed as a "regression of #1466", and the repository has no regression here. `git grep` at `ba938dc3^1`, at `ba938dc3` (the #1490 merge) and at `23e88813` finds the same six sites at all three SHAs: five in `config_flow.py` (2214, 2215, 2892, 2911, 2994) and one at `diagnostics.py:120`. #1490 never touched those files.

#1490 wrote the claim "every entry parameter … none bare (`qs_entry_param_bare=0`)" under the rule's words "must be used throughout". It measured that claim with the round-7 finder harness, whose census covers "parameters named exactly `entry`" only. #1490's own `## Figures` lists the five `config_flow.py` sites as "OUTSIDE the class this finding names". So the claim was false when it was written. The metric's predicate was narrower than the wording of the claim, and the number came from an out-of-tree harness that no in-gate check re-ran. #1490's Forward-carry said so, and the finding was "recorded rather than propagated".

**Process state: (c).** `fixer.md` step 3 (run the finder's harness at both ends) was obeyed, and the review returned merge. The process produced a true number inside a false claim, because the harness predicate defines scope and nothing checks it against the claim's scope.

**Class reach.** `quality_scale.yaml` states two numbers: `qs_entry_param_bare=0` and `qs_py_typed_files=1`. Only the first has an in-tree checker (#1590's `doc_claims.py` arm). No test references `py.typed`, so the second is uncovered.

**Cost test.** The countermeasure to weigh is #1590's typing arm, which already landed (`f5d4743b`).
- Standing cost: the AST walk takes 0.21–0.26 s per run (measured here). Parsing is shared with the exception census. About 500 gate runs per round × 0.24 s ≈ 2 min per round.
- Defect cost: the issue was filed 2026-09-24 01:17Z and the fix merged 2026-09-25 00:43Z, 23.4 h (shared with #1546). One release escaped (v6.6.11).
- P: in the register, I5 instances on quality-scale claims appear in 4 of 8 rounds (R1, R3, R4, R8), so about 0.5 per round.
- 2 min is far less than 0.5 × 23.4 h. **Passes, by more than 300×.**

**Demonstration (`demo_1545.txt`).** Main's arm, lifted verbatim, gives:

| SHA | claimed | census | result |
|---|---|---|---|
| `ba938dc3` (claim written) | 0 | 6 | **FAIL** |
| `23e88813` | 0 | 6 | FAIL |
| `f5d4743b` | 0 | 0 | PASS |
| `origin/main` | 0 | 0 | PASS |

The arm would have refused #1490 itself.

**Class:** I5. The shape is "a stated number whose harness is narrower than its claim", which touches I4. **Verdict: countermeasure confirmed (already landed).** The residual is to add an arm for `qs_py_typed_files`. Placement: **F10.4** (the doc_claims arms).

---

## 3. #1070: corpus-cap headroom friction

**Status of the "seat in flight".** It finished, but its RCA was never written. `97d9bdb3`, "policy(#1070): a working band on the five aggregate caps", merged via #1124 on 2026-09-18 05:16Z. The plan-of-record row at ~:1302 still says "DEFERRED, root-cause seat in flight", so that row is stale and is itself a record defect. The issue was closed on 09-19 by the retired `tvofi-seat-author`.

**Cause.** `ratchet-budgets.md` step 3 records each cap at the value it measured after the change that set it. Headroom is therefore zero by construction. Any prose added afterwards, including a correction or a carry that `finding-propagation.md` mandates, must be paid for by an unrelated cut or by a raise the owner has to approve. The commit measured this at `c71c53c`: 24 of 39 files at zero headroom, and all five aggregates within 0–26 tokens of their caps.

**Process state: (c).** The rule was obeyed exactly. What it produced was collisions (#1122) and cap edits carrying no prose. **Precondition shift since then:** F11.3 (`767ab2c4`, 09-27) added per-file **token** caps recorded at the measured value, with no band. At main, 37 of 40 files sit at zero token headroom (`policy_lint.mjs --budgets`). The corpus is at 55698 against a cap of 55433 plus a band of 500, which leaves 235 tokens.

**Cost test** (cached PR bodies, a sample of 255 PRs, so these are lower bounds). Frictions naming the policy corpus cap:
- Before the band: 10 PRs in 8 days, 09-10..09-17 (#768, #793, #803, #850, #900, #901, #1056, #1057, #1058, #1063). #900 needed 4 measure-cut rounds and #901 needed 5.
- After the band: 4 PRs in 10.4 days (#1510, #1573, #1579, #1627). #1579 withdrew a table row.

Commits editing `policy_budgets.json`:
- Before the band: 28 in 7.7 days, 3 of them with no other file.
- After the band: 6 in 10.4 days, 2 of them with no other file (`dec71aa7`, `6316aa13`).

The band's standing cost is 0 s, since it is a constant in a comparison, and the friction rate fell from about 1.25 to about 0.38 per day. **Band: confirmed.** A band on the per-file token caps: **refused.** No friction has been recorded against them yet (introduced 09-27), and the rule's argument ("a per-document ratchet paid one file at a time") holds. Revisit at three per-file token-cap frictions in one window.

**Class:** none; this is process friction, not a register defect. **Verdict: refusal with numbers; the countermeasure is already landed.** Owed work is for the record: correct the plan row. Placement: the orchestrator's record PR, or **F11.5** (which lands the RCA drafts).

---

## 4. v6.6.0 options-flow freeze of the whole instance (trigger 1)

**Is the cause known? No.** The owner reported it on #201 at 10:25Z on 2026-09-17: on v6.6.0, saving or exiting the options flow freezes the entire instance. The dispatched seat produced #1107, now 404. That PR fixed a real defect that occurred alongside the freeze: 19 of 20 untouched pages reloaded, in v6.4.4, v6.5.1 and v6.6.0. The v6.6.1 notes say explicitly: "**not a confirmed fix** … still being diagnosed." After that, no #201 comment, no line in `HANDOVER.md` and no release note mentions the freeze again. That is 11 days and 24 releases (v6.6.0..v6.7.10) with its status unknown. The trigger-1 RCA the dispatch comment promised was not delivered.

**Static reading at `3490cb16` (a hypothesis, not a cause).**
- Solving is off the loop. `_await_optimize` sends the job to a subprocess worker through `_run_in_process` on an executor thread. The in-process GIL fallback is capped (#783). The v5.1.1 mechanism (#70: a reload awaited a cold solve holding the GIL) stays removed, because setup sets `_skip_solve_once` and the solve runs as a background task.
- Reloads are still reachable. In menu mode (#100), `_save_or_menu` calls `async_update_entry` for every changed page. Each reload creates a new first-solve task. That task parks an executor thread on the process-global `_PROCESS_LOCK`, which the previous solve holds for its whole duration. Unload cancels the asyncio task, but it cannot free a thread already parked on the lock. The load this puts on the thread pool was not measured.
- Other code on the loop was not measured either: `_build_data_dict()` in `_async_first_refresh_light`, teardown and rebuild of the entity roster, and the sysid fit (#1658, 43–228 ms). The `sensor_advisor` loop work in #1658 came in `5dd156ae` on 09-20, after v6.6.0, so it **cannot** be the v6.6.0 cause.
- `git log -S` finds nothing on the options path since #1107 that blocks the loop. `config_flow.py` contains no `open(`, no `sleep` and no synchronous network call.
- **Whether the freeze is still live cannot be established without a live HA instance.**

**Process state: (c) for the escape.** nightly-ha A5/A9 (#587/#655) round-trips every options form and a reload inside real HA. Its only loop instrument is HA's detector for `Detected blocking call to`, which catches synchronous I/O and not CPU stalls of the loop. `tests/nightly_ha.py` has no heartbeat or max-gap measurement, so the process ran and was blind to the harm. The dispatched seat's missing RCA is (b), and the rule deliberately leaves that unenforced.

**Instrument that would settle it.** It is diagnostic, not a barrier. Add a loop-heartbeat arm (1 ms `call_later` probe, max gap) to nightly-ha A5/A9. Drive it with a two-zone + DHW config across three scenarios: an untouched exit, a changed save, and N changed saves in a row in menu mode. On a stall, capture `py-spy dump`. In parallel, on the owner's host, run HA's Profiler: `profiler.set_asyncio_debug` (logs slow callbacks), then `profiler.start` across a reproduction. Standing cost is nightly only, 0 s on PRs.

**Cost test.** It cannot be closed. Per-occurrence cost falls on users and cannot be measured from GitHub. The class base rate is P10: 12 instances in 8 of 9 rounds. **Verdict: cause unestablished. Build the instrument first; defer the barrier decision until the instrument finds the stall.** **Class:** P10 (provisional). Placement: **new group F10.7** (nightly-ha loop-stall arm), with the owner's host reproduction in parallel.

---

## 5. #1041 silent-zero: the owed cost-test re-run

**Current numbers.**
- *Frequency.* The original rate was 14 instances over 115 tags, 1 per 8.2 releases. Since the analysis (2026-09-16 06:32Z to now) there have been 8 defect instances. Three came in the same session: `parse_window`, `classify.py`'s residue sum, and `--policy-paths` giving byte-identical output. Five came from the register:
  - R8 D7-s2-01/#1538: dead-code screen reads 0 over 12;
  - R9 D7-s3-02: `dead_methods` reads 0 over 9;
  - R9 D13-s1-01/#1650: `--stats` drops 52 of 253 silently;
  - R9 D14-s4-02: the replay lane reports zero P7 seams;
  - R9 D9-s2-71: stress samples 0 of 51 valve plants.

  The SSL `n=0` case is excluded as a near miss. That makes 8 over 25 releases, **1 per 3.1 releases, 2.6× the rate the refusals were priced on**.
- *Defect cost, fix side only.* #1538 took 42.0 h from filing to close. The I4 RCA measured 136–599 min per instance.

**Re-run, by countermeasure.**

1. **`merge_shape_guard`: built in the RCA, never pushed, never refused.**
   - Reach at main: `policy_lint.MERGE_SUBJECT_RE` is still `/\(#(\d+)\)\s*$/`. That is the subject arm of D13-s1-01, and it is still dead.
   - Standing cost: 0.02–0.08 s per run. At 10 runs per PR over 328 merges, that is 4.4 min. The defect side is at least 136 min × 1 instance reached. **Passes, about 31×. Overturns the non-landing.**
   - Demonstration (`demo_1041.txt`, this seat's rebuild; it covers 2 of the original 3 enumerators and leaves out `delivery_status`, which reads both shapes since #1057):

     | window and tree | result | rc |
     |---|---|---|
     | `d1a531b`, the original instance | 0 of 16 on both enumerators, REFUSE | 1 |
     | `3490cb16`, `v6.7.9..` | `policy_lint` 0 of 7, REFUSE | 1 |
     | same, widened | 7 of 7 | 0 |
     | `v6.4.2..v6.4.3`, squash null control | 6 of 7 | 0 |
     | empty window | UNCHECKED | 0 |

   - Recommended form: an arm of F11.4's `agreement.mjs`, not a separate script. Refuse any live corpus item that **every** reader answers `null`. The I4 RCA notes that agreement between readers cannot see a misreading they share, and the guard's empty-set alarm closes exactly that gap.
2. **Fail-open lint: refusal confirmed, now on reach rather than frequency.** At most 2 of the 8 new instances (`parse_window`'s `continue`, and D13's `[]`-as-stamp) have the swallowed-error shape. The other 6 are a residue sum, name proxies, a sampling hole, a fixed clock and an unknown flag. Recall is 25% or less at 14.5% precision.
3. **Shared "could not look" helper: refusal confirmed.** 0 of the 8 sites knew they needed one.
4. **New finding: the class barrier has been owed and was never counted.** Round 9 alone holds 4 register instances. The ledger splits them across I4, P11, N-structure-blind and I1, and "silent-zero" has no id in the ledger. So the rule that three or more instances in one round owe a barrier never fired. This is the same state-(c) window defect RCA-1736 found. What the 8 instances share is a check whose output does not move under the perturbation that should move it. That is `field_coverage.mjs`'s BLIND test (I3's barrier), and item 1 shows it detecting a silent state. Proposed barrier: register count-printing instruments (structure.py `dead_*`, stress sampling, `--stats`) in `field_coverage`'s perturb-to-red registry. **The owner's decision, per the audit-class rule.**

**State:** as recorded; the re-run changes none of the four states. **Class:** silent-zero, which has no ledger id (members are filed under I4, I1, P11 and N-structure-blind). Placement: **F11.4** (the guard as an agreement arm); a ledger id for silent-zero goes in the EG-B1 bugclasses fold; the barrier goes to **F11.x or tvofi**.

---

## Summary

| subject | class | cause (1 line) | state | cost numbers | verdict | placement |
|---|---|---|---|---|---|---|
| #1721 Governance red on main | P11 (instrument member, stretch) | Comparator fixture recorded from an admin read, and CI reads as the Actions token; pinned graders meant the new copy first ran on main | (c): RC1's prepr local run and `graders-head-copy` were obeyed and are principal-blind or not on the roster | 2 h 21 m red main plus a hotfix and a stamp; 1 escape in 12 releases; arm ≈ 70 s runner per release, 0 s on the critical path | **Build**: governance arm of `graders-head-copy` under `GITHUB_TOKEN`; local mechanism demonstrated red and green | new **F11.7** |
| #1545 bare ConfigEntry | I5 (touches I4) | #1490 wrote a "throughout" claim from a harness counting only params named `entry`, false when written, not a regression | (c): finder harness obeyed at both ends | 23.4 h fix; 1 release (v6.6.11); arm 0.24 s per run, about 2 min per round against 0.5 × 23.4 h | **Confirmed** (#1590 arm landed; fails at `ba938dc3`, passes at `f5d4743b`); residual `qs_py_typed_files` unchecked | **F10.4** |
| #1070 corpus-cap headroom | none (friction) | Record-at-measured leaves zero headroom by construction; F11.3 token caps repeated it per file (37 of 40) | (c) | 10 frictions in 8 days before the band, 4 in 10.4 days after; band costs 0 s | **Confirmed** band (#1124); **refused** per-file band; plan row :1302 stale | orchestrator record / **F11.5** |
| v6.6.0 options freeze | P10 (provisional) | **Unestablished**; #1107 fixed a co-occurring reload; static candidates are executor parking on `_PROCESS_LOCK` per reload and unmeasured loop work | (c) for the escape (nightly A5 has only the blocking-I/O detector); (b) for the missing RCA | 24 releases with status unknown; user-side cost not measurable | **Instrument first**: loop-heartbeat arm in nightly-ha A5/A9 plus the owner's Profiler run | new **F10.7** |
| #1041 silent-zero re-run | none in ledger (I4/I1/P11/N-structure-blind) | A derivation's failure path returns the success path's empty value | as recorded | 8 instances in 25 releases (2.6× the old rate); defect 136 min–42 h; guard 4.4 min for the window | **Overturn** (guard gets landed); lint and helper refusals **confirmed** on reach; class barrier owed, uncounted | **F11.4** plus the ledger fold; barrier to tvofi |
