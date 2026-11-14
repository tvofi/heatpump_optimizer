# R11-PRE-PARALLEL-PIPELINE: an integration branch that main is promoted from, and heads that stop moving

Designer round 1. Code read at origin/main a77d71fb755f231934e5e59ce1c38c51f86b6439; no predecessor (`after` is empty). Evidence: appendix at aeacef5b1844d983843d9cd67d863da4baa04be4 on `design-wip/r11-pre-parallel-pipeline`, directory dev/audit/rounds/round10/pipeline-design/ (STUDY.md, BASELINE.md, COST.md, carries/, harness/, data/, out/). Owner's rulings of 2026-11-14, verbatim: "1. Ruled out. 2. Every change must not stay its own PR. 3. Yes. 4. Three days is fine but about maximum." (1: the organization transfer and with it the native merge queue; 3: a reviewed change may land on scoped checks, FULL once per batch.) Two decisions are his and open, D1 and D2 in section 8; **nothing below is built on either answer.**

## Figures

Literal, then the enumerator under the appendix's harness/ (recorded output under out/).

| id | figure | literal | enumerator |
|---|---|---|---|
| F1 | handoff to merged, mean; of it handoff-to-open / open-to-first-verdict / to first approval / first approval to main | 17.4 h; 2.9 / 2.5 / 4.4 / 7.6 h | baseline.py, segments.py |
| F2 | merges of main into the 215 merged branches; clean under git merge-tree | 826; 739 | absorbs.py, absorb_need.py |
| F3 | F2 by actor | instruments 494 (at open 191, in review 124, after the final verdict 178, the train's recarry 141 of those); fixer seats 278, 190 after PR open; merge-main bot 41 | absorbs.py, segments.py |
| F4 | merged PRs the train routes serial | 140 of 215 | replay_pipeline.py |
| F5 | verdicts issued after a first merge verdict | 78 of 481 | segments.py |
| F6 | red-streak starts of `gate` on main; of those among the 215, one red then green | 24 over 259 judged merges; 14 of 20 | main_gate.py, replay_pipeline.py |
| F7 | replay over the 215 merges, first approval to: main today (null) / main under C1 / landed under C2 | 7.60 / 3.5 to 4.3 / 2.50 h | replay_pipeline.py 45 60 75 105 |
| F8 | C2, main trails a landing by, mean and max, proof wall 45 / 60 / 105 min | 1.1 and 2.2 / 1.7 and 5.5 / 4.2 and 17.5 h | replay_pipeline.py |
| F9 | programme replay, round 10's roster through `tools/plan/replan.py`: null / C1 / C2 | 714.05 h / -9.5 to -10.8 % / -16.0 to -19.8 % | replay_programme.py |
| F10 | the same on an ASSUMED round-11 baseline (the R11-PRE groups land): C1 / C2 / C2 with the repair round at 2.5 h | -14.2 / -21.1 / -32.2 % | replay_programme.py |
| F11 | CI runner-minutes, estimate from the s12 study's class costs and this window's counts: C1 / C2 without / with the push-run skip | -10 / -19 / -33 % | COST.md, cost-test table |

## 1. Finding

The largest block of a change's handoff-to-main time is the wait AFTER its first approval (F1), and its cause is that the head keeps moving: nine in ten merges of main into a branch answered no conflict (F2). Instruments made most of them (F3): `open_pr.sh` merges main unconditionally ("merge -q --no-edit origin/main"), and the train recarries every entry `merge_fastpath.py`'s `file_class` routes serial, which is two thirds of what merges (F4). Each move is a new code run, and after approval a carry or a new review (F5). The owner's 2026-11-07 ruling (hand off at the first clean head, never re-merge main on a main move) is enforced on nothing after the first handoff (F3's fixer figure): that is a defect today, independent of this design.

## 2. Owning seams

One owner per concern; no second writer to main.
- **What lands, in what order, and what moves main:** `tools/audit/seat/merge_train.py` (class `Train`: `admit`, `merges_as_is`, `recarry`, `land`, `grade_merge`, `drain_order`, the batch proof). The integration branch, its state file, the proof schedule, bisection and promotion are new methods there. Today it moves main through `gh pr merge`; promotion replaces that call and reuses `tools/release/stamp.py`'s `push_via` for the deploy-key push rather than writing a second one.
- **What a CI run is judged as:** `tools/ci/prelude.py` (scope) and `tools/ci/gate.py` (`event_class`, `REQUIRED`); `.github/workflows/ci.yml` carries the input.
- **When a head may move:** `tools/audit/seat/open_pr.sh`, `update_pr.sh`, `remerge_main.sh`, and `handoff_push.sh` for the fixer side; `dev/governance/roles/fixer.md` states the rule.
- **When a successor may start:** `tools/audit/seat/roster_lib.py` (`DONE_STAGES`) and `pr_cap.py`'s dispatch gate.
The stamp stays `stamp.py`'s. No product module is touched.

## 3. Shape

**Day 1, C1: heads stop moving.** (a) `open_pr.sh` (line 148) and `handoff_push.sh` (lines 182 and 202) merge main only when `git merge-tree --write-tree origin/main HEAD` conflicts, the rule `update_pr.sh` line 88 already has. (b) `remerge_main.sh` refuses a merge that is clean unless its caller names a reason from a closed list (a conflict; the train's recarry of a claim entry). (c) `handoff_push.sh` refuses a handoff whose tip is a clean merge of main a seat made after the topic's first handoff. (d) An inherited red is cured by `ci.yml`'s existing dispatch at the unchanged head (`-f pr`, `-f base`), not by a remerge. (e) The `proof` input: a `workflow_dispatch` of `ci.yml` naming it is scoped and judged as a push is (`prelude.py` line 432's scope, `gate.py`'s `REQUIRED["push"]`), where today's batch proof is `recheck`, the pull-request-like scoped run (`DISPATCH`). With (e) the train's batch proof may carry grader, workflow and budget entries; that routing change in `Train.admit` is LAND-PROVE's first commit, so day 1 itself removes the instruments' and fixers' clean merges (F3 less the train's recarry) and day 2 the recarry. Day 1 contradicts nothing the owner ruled and is buildable if C2 is refused.

**Days 2 and 3, C2.** A pull request stays based on main, authored by the App, reviewed at its head.

```
verdict merge posted (bus.sh) ─> Train.admit: GitHub's own read of the PR against main's rules
        (reviewDecision, mergeStateStatus, the required set at the reviewed head)
   ─> LAND: local merge of the reviewed sha onto integration's tip (text_merge with the claimnotes
        driver; grade_merge on the tree); subject and body in GitHub's merge grammar; push integration
   ─> successors of the group may start, from the landed head
PROOF (one at a time): dispatch ci.yml -f proof on the tip; covers every landing since main
   green ─> PROMOTE under the main-writer hold: re-read each PR head == landed sha, then move main
        to the proved sha (D1); GitHub marks the PRs merged; postmerge.py, delivery rows, roster done
   red   ─> re-run the failed jobs once; still red: prefix proofs (each landing is a first-parent
        commit, so every prefix exists) ─> promote the green prefix; EVICT the culprit: rebuild the
        branch from its parent, re-land the rest; its PR gets a blocked ci-red verdict with the log
main moved by anything else (a stamp, a direct hotfix merge) ─> rebuild integration on the new main
```

**Kept per change:** its pull request into main, its verdict and approval at its head, its own first-parent merge commit on main in the grammar decision 0010's enumerators read, its delivery row. **Batched:** the FULL proof and the push that moves main. This holds under either reading of ruling 2. If he meant that several changes may be folded into one pull request, nothing here needs it; folding would change the verdict-per-head rule, the delivery row and stamp.py's notes check, and is not designed.

**Invariants.** I1: main only ever equals a sha whose `gate` is green on a proof judged as a push. I2: a reviewed head is never moved by the pipeline. I3: every commit promotion adds to main's first-parent line is the landing of one pull request GitHub reported approved at that sha. I4: integration is main plus landings, rebuilt whenever main moves otherwise; no work is authored on it. I5: a red proof stops promotion, never landing; landing pauses only past a stated depth of unproved landings.

**Hotfix and outside pull requests (they never wait).** They land first: `drain_order`'s tiers already rank them, and a priority landing rebuilds the branch with that entry directly on main and proves that prefix at once, cancelling the proof in flight. Worst case to main: one proof wall plus the rebuild (F8's wall, 45 to 105 min). When main must move sooner, today's direct merge into main under `merge_pr.sh` stays; integration rebuilds on the new main and its proof restarts.

**Stamps.** `stamp.py` and promotion take one main-writer hold (the train's `HOLD_REF` mechanism). A stamp waits for the proof in flight to promote or fail, lands the held record pull requests as one batch (`sweep --stamp`, unchanged), stamps on main, and integration rebuilds on the stamp commit. Landings made before a stamp carry the old `claims-for`: the rebuild's claim merges are the case proposal PC-1113-18 describes and are a note for the fixer below.

## 4. Under D1(a), what replaces each guarantee the ruleset enforces today

A bypass actor's push is checked by nothing on GitHub. Each guarantee, its replacement, and the null control that must refuse:

| `main-protect-checks` enforces at the merge | replacement | null control (self-test fixture, then live probe) |
|---|---|---|
| a pull request per change | I3, read back at promotion; an audit job on main's push run re-derives it from the first-parent range and reddens main | a first-parent commit with no pull request is refused at promotion and red in the audit |
| one approving review; code-owner review on a code-owned path | landing reads GitHub's own `reviewDecision` and `mergeStateStatus` for the pull request against main; BLOCKED or not APPROVED refuses | a head touching `tools/ci/` with the App's approval and no owner or mandate review does not land |
| `gate` green at the head (it folds in `pr-contract`, `budget-raise-gate`, the scoped suite) | landing reads the required set at the reviewed head (`classify_at`); the proof adds the push set at the tip | a body the contract refuses, and a budget raise with no approval, each leave `gate` red and do not land |
| the merged sha is the reviewed sha (`--match-head-commit`) | the landing merges the sha it read; promotion re-reads each head | a head pushed after landing evicts the entry |
| GitHub itself refuses a wrong merge | **none: a defect in the instrument, or anyone able to run it with the key, can move main.** True of the stamp today; D1(a) extends it from stamps to every change. The audit job detects after the fact; it does not prevent. | (finding for the owner) |

The key is the one `orchestrator.md` section 13 names for stamps, on the orchestrator's host; promotion is invoked by the merge operation there. D1(b), a promotion pull request merged by GitHub, keeps host enforcement and costs: a merge commit per batch on main's first-parent line (the decision 0010 class: enumerators of "Merge pull request #" there), a promoted sha that differs from the proved one, and a code-owner review on every promotion that carries a code-owned path.

## 5. Alternatives, and why each lost in terms of the code

- **C1 alone.** Takes about half of C2's wall-clock gain (F9) with two small groups. Lost as the end state because a claim entry still needs a recarry (GitHub cannot run the claimnotes driver), main still reddens at today's rate (F6), and every merge still pays a push run. It is day 1.
- **Per-batch staging branch reset each batch (bors as written).** Same guarantee; lost because a persistent branch gives successors a landed head to start from and keeps each landing's commit for prefix bisection without rebuilding.
- **Speculative proofs per entry (Zuul, merge trains).** Lost on capacity: one FULL run starts 39 jobs against the account's 40.
- **Pull requests re-based onto the integration branch.** Lost on coupling: `origin/main` is the merge base in the gate's scope, prepr, the carry predicate and the contract; keeping the base on main changes none of them.
- **Stacking a successor at its predecessor's handoff.** Not costed: the rework rate on an unreviewed parent is unmeasured.

## 6. Sibling sites

Sites that merge main into a branch, `git grep -n -E 'git[^|;&]* merge [^|;&]*origin/main' -- tools .github`: `open_pr.sh`, `handoff_push.sh` (two), `remerge_main.sh`, and `tools/pr/merge_main_bot.py`; day 1 covers the first three files, and the bot is left as it is (41 merges in the window, F3) until promotion makes it idle. `git grep -l -E 'gh pr merge|pulls/[^ ]*/merge' -- tools .github .claude` (callers of the merge: the train, `merge_pr.sh`, `nightly.yml`'s record step, `dependabot-automerge.yml`): the last three keep the direct path; each then triggers the rebuild. `git grep -l -E 'merge_commit_sha|mergeCommit' -- tools tests` (readers of the merge commit: `postmerge.py`, `record_row.py`, `record_beat.py`, `roster_sync.py`, `state_docs.py`, `plan_page.py`, `size_durations.py` among them): each is checked against what GitHub reports for an indirect merge (probe U4). `git grep -l 'Merge pull request #' -- tools tests .claude` (first-parent enumerators): unchanged under D1(a), each changed under D1(b). Push-to-main triggers (`ci.yml`, `merge-main.yml`, `nightly.yml`, `dependency-graph.yml`): one event per promotion instead of per change; `merge-main.yml` then has no dirty head to cure except a real conflict. Out of scope: `tests/closures.json` scoping and the structural ratchets, which read a pull request's own diff against main and are untouched.

## 7. Evidence plan, by file

- `tools/audit/seat/open_pr.sh`, `remerge_main.sh`, `handoff_push.sh` self-tests: a clean-merge fixture fails first (the merge is made today), then is refused; null: a conflicting fixture still merges.
- `tools/ci/prelude.py`, `tools/ci/gate.py` self-tests: a dispatch with the proof input reads scope full and the push set; null: a dispatch without it reads as today. **p1/p2 split:** this lands alone first; both files are restored graders, so the train may rely on the input only from a later pull request.
- `tools/audit/seat/merge_train.py --self-test`: land, proof, promote, transient re-run, bisection, evict, rebuild on a moved main, priority landing, the stamp hold; one mutant per arm in a harness under dev/audit/harnesses/ as the train's other parts have. Null: with the flag off the train's argv and log are byte-identical to today's.
- Replay: the appendix's replay_pipeline.py is the finder's harness for the wall-clock claim; the fixer re-runs it and segments.py over a week of merges after the switch. The claim fails if first approval to landed is not under half of F1's last term.
- **Probes after the round-10 stamp, with the orchestrator's word** (STUDY.md U1 to U6), on a throwaway branch under a throwaway ruleset and `ci-probe/*` refs through `tools/audit/seat/ci_probe.py`: the bypass push and whether checks are evaluated on it; the proof's `gate` read at the same sha; what an indirectly merged pull request reports; `reviewDecision` under a missing code-owner review; the push-run skip.
- **Shadow (day 2), and what cancels the switch:** integration is built and proved while the train still merges. Cancel if any proof disagrees with main's own push run at an equal tree; if main would have trailed a landing by more than 6 h at any point; or if a rebuild ever produces a tree different from the one the same landings gave before. **Rollback** is the train's flag off: every pull request is still based on main, so the train merges whatever is not yet promoted; read back that integration's tip is an ancestor of main or is deleted, and that `merge_train.py queue` lists the unpromoted pull requests.

## 8. Build, the bar, and what the owner decides

| part (proposed id) | size | files | after | proves |
|---|---|---|---|---|
| R11-PRE-PIPELINE-NO-ABSORB | S | open_pr.sh, remerge_main.sh, handoff_push.sh, fixer.md | none | F2's clean merges by instruments fall to zero on a replayed day |
| R11-PRE-PIPELINE-PROOF-INPUT | S | ci.yml, tools/ci/prelude.py, tools/ci/gate.py | none | a proof is judged as a push |
| R11-PRE-PIPELINE-LAND-PROVE | L | merge_train.py, a mutants harness | PROOF-INPUT | shadow: proofs equal main's push runs |
| R11-PRE-PIPELINE-PROMOTE | M | merge_train.py, tools/ci/prelude.py (the skip), an audit step in ci.yml, orchestrator.md, standing-merge.md, gate-scoping.md, CLAUDE.md, a decision record | LAND-PROVE, the probes, D1 | the switch; rollback read back |
| R11-PRE-PIPELINE-SUCCESSORS | S | roster_lib.py, pr_cap.py, cloud_dispatch.py | LAND-PROVE | a successor starts at its predecessor's landing |

Hot file: `merge_train.py` (R11-PRE-STANDING-SCRIPTS names it too: it takes an after edge on LAND-PROVE, see carries/). The five ids are proposals; the orchestrator creates the groups. Usable after day 1: no instrument or fixer moves a clean head. After day 2: shadow figures. After day 3: the switch. Cut first: the push-run skip (it costs F11's difference, no wall clock), then parallel prefix proofs, then SUCCESSORS.

**Approvals, should the mandate (comment 6715477401, to 2026-11-16T18:00Z) not be renewed.** Code-owned, his review in person: PROOF-INPUT (`.github/workflows/`, `tools/ci/`); PROMOTE's skip and audit step. Policy, his review: `fixer.md` (NO-ABSORB); `orchestrator.md` section 11 ("CI green at the verdicted head, landed onto a green main" becomes landed onto integration and promoted on a FULL proof; the serial `run` rule goes), `standing-merge.md`, `gate-scoping.md`, `CLAUDE.md` rule 1's forced FULL at a push to main, and the decision record. His action: the throwaway ruleset for the probes. LAND-PROVE and SUCCESSORS need neither.

**The bar (over 20 %).** Cleared by measurement: CI with the push-run skip, and main's red starts (F11, F6). Reached only under an assumption: programme wall clock, which replays under the bar on round 10 and over it only on the assumed round-11 baseline (F9, F10). Weakest assumption: that an approved, green head lands with no further wait, resting on 141 recorded green times of 215; at the p75 of those waits F9's C2 reads -15.4 %. C1 clears it on no measure.

**D1.** How main is moved: (a) the deploy key, or (b) a promotion pull request (section 4). **D2.** Build C2 on these figures, or day 1 alone.

## Notes for the fixer

- A landing made before a stamp meets the new `claims-for` at the rebuild; decide with `claim-files.md` whether the driver accepts a side whose only claim change is the stamp, before the promotion part. Carry: R11-PRE-PARALLEL-PIPELINE (item n1)
- `prelude.py` already treats a dispatch on `codeql_scope.PROOF_REF` specially; the proof input must not fork that into a second proof notion. Carry: R11-PRE-PARALLEL-PIPELINE (item n2)
- The repair loop's requirements are carried to existing groups, one file each under the appendix's carries/. Carry: R11-PRE-STANDING-SCRIPTS (item n3)
- If the pipeline is built, main is the promoted state R11-PRE-TOOLCHAIN-PIN asks for. decision: orchestrator. Carry: R11-PRE-TOOLCHAIN-PIN (item n4)
