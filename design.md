# R11-PRE-PARALLEL-PIPELINE: heads that stop moving (built), an integration branch in shadow (measured), the switch (not approved)

Designer round 2, answering `Design review: revise 80fbf6319fdb950b8d5054ee8939fb5dea1b5aae evidence-missing` (design-verdict/R11-PRE-PARALLEL-PIPELINE at ea028c98ec). Code read at origin/main a77d71fb755f231934e5e59ce1c38c51f86b6439; no predecessor. Evidence: appendix at 24a515dfa505ba68471565a16d574d6c644003f1 on `design-wip/r11-pre-parallel-pipeline`, directory dev/audit/rounds/round10/pipeline-design/. Each of the verdict's eleven points is answered, resolved or contested with its measurement, in REVISE-1.md there; this note carries the result.

Owner, 2026-11-14, verbatim. On the first questions: "1. Ruled out. 2. Every change must not stay its own PR. 3. Yes. 4. Three days is fine but about maximum." On the instruments: "remerge_main.sh definitely needs to be scoped down aggressively. Speculative gating could be done by running the scripts in cloud seats." and "If cloud seats for speculative gating is feasible, they should run haiku". On the build, after the verdict: "Day 1 plus shadow". So: **day 1 is built before round 11's fixers start; the shadow runs beside round 11 as a measurement and never gates it; moving main by promotion is not approved and is his decision on the shadow's result.**

## Figures

Literal, then the enumerator under the appendix's harness/ (recorded output under out/). Where two values stand, the second, in brackets, is the replay's upper bound (COST.md says what separates them).

| id | figure | literal | enumerator |
|---|---|---|---|
| F1 | first approval to main, mean, the 215 merges of 2026-11-07 to 11-14 | 7.60 h | segments.py |
| F2 | by what followed the approval: head never moved / mechanical commits only / fixer commits / a block | 71 at 2.42 h / 116 at 7.30 h / 15 at 14.60 h / 13 at 30.44 h | replay_v2.py |
| F3 | merges of main into the 215 branches; clean with the checkout's merge drivers; clean driver-free, as GitHub merges | 826; 739; 682 | absorb_heads.py |
| F4 | the driver-free clean ones by maker | other instruments 279; the train's recarry 171; fixer seats 189, 136 of them after the first handoff; other seats 43; merge-main bot 0 of its 41 | absorb_heads.py |
| F5 | merged PRs the train routes serial; of them grader | 140 of 215; 120 | replay_v2.py, train_stats.py |
| F6 | NULL: today's rules through the replay's loop against F1, tolerance 20 % | 7.88 h, +3.7 % | replay_v2.py |
| F7 | hours saved a change, day 1's first part alone | 0.79 [1.63] | replay_v2.py, day1a |
| F8 | the same, day 1 complete, proof wall 45 / 60 / 75 / 105 min | 1.78 / 1.53 / 1.31 / 0.32 [2.83 / 2.55 / 2.26 / 1.17] | replay_v2.py, day1 |
| F9 | the same, integration branch, successors at landing; after a seat's green gate | 2.47 to 2.21 [3.61 to 3.35]; 1.62 to 1.23 [2.66 to 2.28] | replay_v2.py, integ |
| F10 | main trails a landing, max, proofs one at a time, 45 / 60 / 75 / 105 min; with seat search | 2.91 / 7.20 / 19.04 / 34.34 h; 3.26 / 6.20 / 7.63 / 15.77 h | replay_v2.py, integ |
| F11 | programme wall clock through `tools/plan/replan.py`: null; day 1 at 45 / 60 / 105 min; integration, successors at landing | 714.05 h; -6.0 / -5.2 / -0.9 % [-9.0 / -8.1 / -4.0]; -7.7 % [-11.5] | replay_programme.py |
| F12 | `ci.yml` run wall at heads a driver-free clean merge of main made after PR open; its null | 258 h of 1540 h, 16.7 %; 0 h | absorb_heads.py, with --null |
| F13 | first-parent commits of main outside the 215 | 69: 49 pull requests, 11 stamps, 9 ledger App pushes | main_moves.py |

## 1. Finding

Approval to main is the largest block of a change's handoff-to-main time (F1), and half of its hours sit in pull requests whose head moved by mechanical commits only (F2). 83 % of the merges of main into a branch answered no conflict even as GitHub merges (F3). Instruments made most of them (F4): `open_pr.sh` and `handoff_push.sh` merge main unconditionally, and the train recarries every entry `merge_fastpath.py`'s `file_class` routes serial (F5). The 28 pull requests with fixer commits or a block after approval hold 38 % of the block's hours; no merge mechanism removes those. The owner's 2026-11-07 ruling is enforced on nothing after the first handoff (F4's fixer figure).

## 2. Owning seams

- **When a head may move:** `tools/audit/seat/pr_args.sh` gains the one predicate; `open_pr.sh`, `handoff_push.sh`, `update_pr.sh` and `remerge_main.sh` call it; `dev/governance/roles/fixer.md` states the rule.
- **What a CI run is judged as:** `tools/ci/prelude.py` (scope), `tools/ci/gate.py` (`event_class`, `REQUIRED`), and the workflows that read the event.
- **What the train recarries and what it proves:** `tools/audit/seat/merge_train.py` (`Train.admit`, `merges_as_is`, `recarry`, `DISPATCH`).
GitHub still makes every merge; main's ruleset, the stamp and every product module are untouched.

## 3. Day 1, the design to build

**Part 1, no clean absorb (S).** One shell function in `pr_args.sh` answers, for a head and origin/main: *clean* under the driver-free merge (`merge_train.py`'s `text_merge` substitution of `git merge-file` for every configured driver: what GitHub computes); *driver-only* (it conflicts driver-free, every conflicting path is a driver file, and the merge with the drivers is clean: `tools/pr/merge_main_bot.py`'s `decide`); or *conflict*.
- `open_pr.sh` (line 148) and `handoff_push.sh` (lines 182, 202) merge main only on *driver-only*, because GitHub would otherwise report the head unmergeable and run no CI; on *clean* they merge nothing; on *conflict* they refuse to the fixer, as now. `update_pr.sh` (line 88) takes its test from the same function.
- `handoff_push.sh` refuses a handoff whose tip is a merge of main a seat made after the topic's first handoff where the function says *clean*.
- `remerge_main.sh` takes a reason and admits two: *driver-only* at a head GitHub reports unmergeable, and the re-push of a GITHUB_TOKEN tip. Its only caller is the train's `recarry`. It retires only if main is ever promoted from locally merged heads (SWITCH.md).
- An inherited red is cured by `ci.yml`'s existing dispatch at the unchanged head (`-f pr`, `-f base`), never by a remerge.

**Part 2, the proof input (M, code-owned, lands alone first).** A `workflow_dispatch` of `ci.yml` naming it is judged as a push to main is. REVISE-1.md's R8 table lists every push-only condition in the workflows and what the proof does at each. It changes five: scope full (`prelude.py` line 432); the push required set (`gate.py` `event_class`); the instrument self-tests traced, with the push timeout (governance.yml lines 297, 300); the INERT-list check (codeql.yml line 229). It leaves six with main's own push run, which day 1 never skips: the two cache writers, the proof consumer, ci-ratchet, record, delivery-status-publish. Files: `.github/workflows/ci.yml`, `governance.yml`, `codeql.yml`, `tools/ci/prelude.py`, `tools/ci/gate.py`. Both `tools/ci` files are restored graders, so the train relies on the input only from part 3.

**Part 3, the train's routing (S, after part 2).** `DISPATCH` names the proof input in place of `recheck`. `Train.admit` routes serial only a claim entry, a bot tip and a conflict; a workflow, grader or budget entry joins the batch proof, and a batch of one such entry is still proved. A budget raise keeps its approval step (`Train.raise_hold`). `merges_as_is` (line 3028) waits on an unreadable ruleset read instead of recarrying. `recarry` passes its reason to `remerge_main.sh`. Policy text: `orchestrator.md` section 11's `run` sentence and `standing-merge.md`'s serial route.

```
head approved, gate green ──> batchable, alone ──────────────────────> GitHub merges it (as today)
                          ├─> workflow / grader / budget, or a batch ─> push-judged proof of the batch on main
                          │        green ─> GitHub merges each entry while main's tree equals the proof's
                          │        red   ─> today's rule: the entry drops out; search by seats (section 6)
                          ├─> claim entry ─> recarry, reason driver-only ─> its own run ─> GitHub merges it
                          └─> conflict ───> the fixer
```

**Invariants.** J1: a head moves only by its author's commits, a driver-only merge GitHub cannot make, or a conflict resolution. J2: a change touching a workflow, grader or budget file reaches main only after a push-judged proof of the tree main will have. J3: every merge is GitHub's, under `main-protect-checks` as it stands.

**What day 1 delivers alone.** Part 1: F7. All three parts: F8, F11 and F12 less the batch proofs it adds, about -10 % of CI run wall. It clears the over-20 % bar on no measure; it is not a new proposal under that rule: it enforces the 2026-11-07 ruling and the direction on `remerge_main.sh`. Main's red starts are unchanged for a lone unproved entry.

## 4. Alternatives, and why each lost in terms of the code

- **Every entry behind a proof before GitHub merges it** (the review's R7). One condition in `Train.admit`. It loses to day 1 on wall clock at every proof wall, because 72 lone batchable entries a week then wait, and is slower than today from 75 min (COST.md S-1p). It stays a switch the owner may throw, not a build.
- **Serial-class entries merged as they stand, unproved.** Fastest; lost because `orchestrator.md` section 11's rule exists for the interleave a grader change can cause, and J2 keeps it.
- **The integration branch now.** Section 5 and SWITCH.md: not approved, and its replayed edge over day 1 is about one hour a change at landing, none behind a seat gate (F8, F9).
- **Proofs in parallel on GitHub.** Lost on capacity: one FULL run starts 39 jobs against the account's 40.

## 5. The shadow, a measurement beside round 11

**Built:** one read-only driver under `tools/audit/seat/` with a self-test (M), and the seat instrument of section 6 (S). The driver follows posted merge verdicts, merges each approved, green head onto a `shadow/integration` ref locally with the drivers (a branch push starts no workflow), rebuilds it when main moves, and records times. It never touches main, a pull request or the train, and dispatches no proof of its own: day 1's batch proofs are push-judged proofs whose trees main then equals (the train logs "tree == proof"), so they supply the proof-against-push comparison and the proof walls.

**Acceptance, the verdict's four conditions, over the shadow's merges:** (1) first approval to landed is at least 1.0 h below first approval to main under day 1's train; (2) no day-1 proof disagrees with main's push run at an equal tree; (3) main would never have trailed a landing by more than 6 h, with proofs one at a time, the measured walls and every direct push counted (replay_v2.py over the shadow's own events); (4) the probe for the D1 arm chosen has passed. I add (5): a rebuild never yields a tree different from the one the same landings gave before.

**What the replay predicts:** the test fails. Integration's edge at landing is 0.69 / 0.91 / 1.06 / 1.89 h at a 45 / 60 / 75 / 105 min proof [0.78 / 1.04 / 1.25 / 2.18], so (1) needs a long proof wall, and (3) holds only at a short one (F10). The shadow is run because the proof wall after day 1, the real margin and the seats' agreement are inputs the replay takes and cannot know.

**If it fails:** day 1 stays as the end state, which is the review's fallback: today's batch proof made push-judged, GitHub still merging. Nothing is torn down but the shadow ref. **If it passes:** the owner decides the switch on SWITCH.md, which holds its amended shape (successors from a reviewed head, never the tip; promotion re-reading the whole admission; priority landings that do not cancel a proof), its failure paths, and **D1's three arms**: (a) the deploy key under the ruleset as it is; (b) a promotion pull request; (c) the reviewer's arm, which I now recommend if its probe passes: the ruleset split so that the pull-request rule is bypassed and the required-status rule still binds the promoting credential. Under (c) `stamp.py`, which pushes an unproved commit over the same key, either proves its commit on a ref first or keeps the key while promotion uses an App. Probe U7 (SWITCH.md) must show a fast-forward push refused without a green `gate` and admitted with one. No ruleset or key is touched before that decision.

## 6. Cloud seats on haiku

Feasible if the judgement is in a script, which does not exist yet: one tracked seat-side instrument (SEATS.md gives its seven steps) that checks the environment and refuses, checks the sha, runs one fixed gate invocation, reads failing script names from `run.sh`'s summary, reports golden and closure-recording scripts as INCONCLUSIVE itself, and writes the result to a ref. The seat's prompt then holds one command and four prohibitions. A seat's result may reorder, hold out or name a suspect; it never merges, evicts or posts. **Where it helps:** the search of a red batch, in one seat wall instead of several proofs, under day 1 as under the switch (F10's second row). **Where it removes the gain:** as a gate before a successor starts from a landing it costs the seat wall, and F9's second figure is then F8. **Measured in the shadow:** agreement with GitHub's `gate` at the same sha by failing script; the seat wall for a FULL and a scoped tip; the share of fires with no result.

## 7. Sibling sites and evidence, by file

Sites that merge main into a branch, `git grep -n -E 'git[^|;&]* merge [^|;&]*origin/main' -- tools`, and the argv form in `merge_train.py`: the four scripts of part 1; `merge_main_bot.py`, left as it is (it merges only what GitHub cannot); the train's `recarry`, part 3. Push-only conditions, `git grep -n -E "event_name *[!=]= *'push'|refs/heads/main" -- .github/workflows`: REVISE-1.md's table.

- `pr_args.sh --self-test` (run by `open_pr.sh` and `update_pr.sh`): a fixture where main moved without conflict fails first (a merge is made today) and then makes none; nulls: a driver-only fixture still merges, a real conflict still refuses. `handoff_push.sh`: the refused clean absorb, and a first handoff that passes.
- `tools/ci/prelude.py` and `gate.py` self-tests: a dispatch with the input reads scope full and the push set; null: one without it reads as today.
- `merge_train.py --self-test` and a mutants harness under dev/audit/harnesses/: one arm per changed route, the unreadable-ruleset wait, the reason passed to `remerge_main.sh`; null: a claim entry is still recarried.
- The finder's harness for the claim: absorb_heads.py over a week of merges after day 1 must print zero driver-free clean merges of main after PR open by an instrument or the train, and segments.py the approval-to-main mean. The claim fails if that mean is not at least F8's 60 min lower figure below F1.

## 8. Schedule, approvals, the bar

| part (proposed id) | size | after | planner hours, first round to p75 |
|---|---|---|---|
| R11-PRE-PIPELINE-NO-ABSORB | S | none | 13.3 to 21.6 |
| R11-PRE-PIPELINE-PROOF-INPUT | M | none | 18.4 to 32.4 |
| R11-PRE-PIPELINE-TRAIN-ROUTING | S | PROOF-INPUT | 13.3 to 21.6 |
| R11-PIPELINE-SHADOW (driver and seat instrument) | M | TRAIN-ROUTING | 18.4 to 32.4, then a window of about 60 landings |

**Before round 11's fixers start:** day 1. Part 1 is usable in under a day; the chain of parts 2 and 3 is 31.7 h if both pass first review and 54.0 h at the planner's p75: inside three days, not inside one. **Beside round 11:** the shadow. **Only after its result:** the switch, whose own chain (SWITCH.md) is a further four days or more and cannot precede the fixers. Hot files: `merge_train.py` and `standing-merge.md` with R11-PRE-STANDING-SCRIPTS (it takes an after edge on part 3); `fixer.md`, `orchestrator.md` and `standing-merge.md` with R10-STANDING-CONTRACTS-P2 and R11-PRE-HANDOFF-BOOKKEEPING.

**His review in person if the mandate (comment 6715477401, to 2026-11-16T18:00Z) is not renewed:** part 1's `fixer.md`; all of part 2 (`.github/workflows/`, `tools/ci/`); part 3's `orchestrator.md` and `standing-merge.md`. The shadow needs none.

**The bar.** No candidate clears over 20 % on any of the four measures (COST.md). The first note's 16.0 to 19.8 % of programme wall clock and its -33 % of CI are withdrawn with the replay they came from.

## Notes for the fixer

- The delivery row added or edited after a verdict made 29 post-approval heads in the window; day 1 does not remove them. Carry: R11-PRE-HANDOFF-BOOKKEEPING (item n1)
- `prelude.py` already treats a dispatch on `codeql_scope.PROOF_REF` specially, and tests.yml has a proof consumer: the proof input extends that notion, it does not add a second. Carry: R11-PRE-PARALLEL-PIPELINE (item n2)
- The repair loop's requirements, and what this baseline says about each neighbour's aim, are one file a destination group under the appendix's carries/. Carry: R11-PRE-STANDING-SCRIPTS (item n3)
- R11-PRE-TOOLCHAIN-PIN's promoted ref stands; revisit only if the switch is taken. decision: orchestrator. Carry: R11-PRE-TOOLCHAIN-PIN (item n4)
- The verdict's notes f3, f4, f5 and f6 bind the switch, not day 1; they are in SWITCH.md. Carry: R11-PRE-PARALLEL-PIPELINE (item n5)
