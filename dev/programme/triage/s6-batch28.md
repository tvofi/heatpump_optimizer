# Proposal triage, session s6, batch 28 (P150-P157)

Proposals from the s6 `proposals.md`. Numbering continues after `s6-batch27.md` (P140-P149). This batch holds 8-10 entries and merges only through the train queue (tvofi, 2026-10-25). Entries are ordered by round-10 closure time saved; the six structural proposals (V73-V78) save none in round 10 and are ruled round-11 design items, recorded in R10-ROUND-PLAYBOOK, the group writing the playbook a fresh orchestrator runs round 11 from.

A roster op citing an ACCEPT below resolves only once this file is on the roster branch or origin/main (`roster_edit.py` reads the ruling from there).

## P150: generated body facts (S6-V66)
Verdict: ACCEPT narrowed: no new carry. Three of the four generated facts exist or are already carried. The fourth, rendered timestamps, is REJECTED as a generator.
Source: s6 `proposals.md` `## V66` (orchestrator, 2026-10-25, tvofi-accepted idea 3).
Instances: read at origin/main dfcd8d9be.
- `## Head`: generated today. `app_push.sh` writes the note naming the new head under the heading (`app_push.sh:89`, `:442`), and `open_pr.sh` and `update_pr.sh` use `head_note.py` (`open_pr.sh:17`, `update_pr.sh:3`, `:24`). A stale Head is refused before push (fixture `tools/policy/fixtures/policy-rot/prepr/wrong-head.md`).
- `## Red checks` from the head's check runs: R10-FLOW-JIDOKA carry 16 (`prepr.sh --fill-red`, triage P67).
- Figures: ruled with V75 (P154), where a claim's harness renders its figure.
- Timestamps in UTC: rejected as a generator. A body's time refers to an event (a commit, a verdict, a measurement) that the body tool cannot identify from the prose, so it has nothing to render from. The one instance (#2822 round 2) was a commit time copied with its `+01:00` offset dropped. The cheap guard is the writer's own command, `TZ=UTC git log -1 --format=%cd --date=iso-local <sha>`, which this seat now uses.
- #2823's "stale body against the diff" is a judgement about prose, not a fact a tool can render.
Cost: none new.
Binding: the facts that can be generated already are, or are carried to a group. Closure saving: 0 h new (credited to JIDOKA's carry 16 and to P154).

## P151: pre-review mechanical lint (S6-V67)
Verdict: ACCEPT narrowed: no new carry. Four of the five rules already exist, and running them before a reviewer is dispatched is triage P135 (`s6-batch26.md#P135`) -> R10-ORCH-REVIEW-PACKET. The fifth, UTC timestamps, is REJECTED for P150's reason: a `Z`-labelled local time cannot be told from a correct one without its source.
Source: s6 `proposals.md` `## V67` (orchestrator, 2026-10-25, tvofi-accepted idea 4).
Instances: read at origin/main dfcd8d9be.
- Carry routed to a done group: `carry_audit.py:334` refuses a done destination. `prepr.sh --body-check` gains the call in R10-FLOW-JIDOKA carry 11 (triage P-Q). An absorbed destination passing as open is R10-ORCH-ROSTER-SCHEMA carry 16 (`roster_lib.py:33`, DONE_STAGES).
- Host paths: the `ref_privacy` arm of prepr, R10-FLOW-JIDOKA carry 18 (triage P78).
- `## Red checks` complete: prepr's policy_lint unnamed-red arm (`prepr.sh:1417`).
- Claimed-drift VERSION match: `prepr.sh` `claims_check` (`:278`, `tests/env_drift.py --claims-only`).
Cost: none new.
Binding: the gap was where the rules run, not which rules exist, and that gap is carried. Closure saving: 0 h new (credited to P135).

## P152: speculative integration branch (S6-V73)
Verdict: ACCEPT -> round-11 design item, recorded in R10-ROUND-PLAYBOOK. Not built in round 10.
Source: s6 `proposals.md` `## V73` (orchestrator, 2026-10-25, tvofi-accepted idea 11).
Instances:
- The train already proves a batch on a proof branch cut from main (`batch/<tag>-<n>`, `merge_train.py:5435`) and bisects a red pair (`:4880`).
- What V73 adds is continuous rebuilding ahead of the merge decision, and the dropping of a red entry without stalling the entries before it.
- The repository merges through pull requests only (`gh pr merge`, `merge_train.py:1071`), so "fast-forward main to the green prefix" becomes "merge the green prefix's pull requests at their proven heads". That is a design question about ruleset and check identity, not a script.
Cost: L to XL (merge_train.py, CI triggers on the integration branch, check-run reuse at merge).
Binding: measured verdict-to-merge median 1.89 h (plan-opt, n=110) is the prize. A build of this size in round 10 would finish near closure (plan v47 end 2026-11-01), so it pays in round 11. Closure saving: 0 h in round 10.

## P153: CI results cached by measured closure (S6-V74)
Verdict: ACCEPT -> round-11 design item, recorded in R10-ROUND-PLAYBOOK.
Source: s6 `proposals.md` `## V74` (orchestrator, 2026-10-25, tvofi-accepted idea 12).
Instances:
- `GATE_SCOPE=auto` already runs only the scripts a branch's diff can reach (`.github/workflows/tests.yml:43`, `:363`), and a push to main is forced to full (`:47`, CLAUDE.md rule 1).
- The delta is reuse across heads of one pull request whose closure did not change.
- For the design to settle: a cached pass must be keyed on every input the measured closure misses (runner image, BLAS build: CLAUDE.md rule 3 says solver floats do not reproduce across builds). The forced full run on main must stay uncached, or a wrong closure never reddens main, which is the property rule 1 exists for.
Cost: L. The risk falls on the gate's own correctness.
Binding: the saving is CI minutes per recarry (PR run wall median 920 s), but a cache that hides a red costs more than the minutes. Design before build. Closure saving: 0 h in round 10.

## P154: executable claims in place of prose evidence (S6-V75)
Verdict: ACCEPT -> round-11 design item, recorded in R10-ROUND-PLAYBOOK. It absorbs the Figures part of V66 (P150).
Source: s6 `proposals.md` `## V75` (orchestrator, 2026-10-25, tvofi-accepted idea 13).
Instances: `figure_lint.mjs` already refuses a figure whose command names a missing script (fixtures under `tools/policy/fixtures/figures/`), but it does not run the command. plan-opt counted 14 PRs blocked 3 or more times and 14 rounds past the third since 2026-10-21.
Cost: L (a claims-file format, a CI job that runs each harness at the head, body rendering, and the PR template and `checkPrBody` contract change, which is policy).
Binding: high value, but it changes the PR contract every open PR answers. Switching mid-round would re-open every in-flight body. Closure saving: 0 h in round 10.

## P155: test-first review (S6-V76)
Verdict: ACCEPT -> round-11 design item, recorded in R10-ROUND-PLAYBOOK.
Source: s6 `proposals.md` `## V76` (orchestrator, 2026-10-25, tvofi-accepted idea 14).
Instances:
- plan-opt's review-strength window B: 174 verdicts, of which 16 were real blocks and 52 were book (mechanical).
- Window C: 63 blocks, of which 16 were real, 14 or more mechanical and 14 carry-missing.
- So most round trips in round 10 are mechanical, which P135, P142-P149 and JIDOKA address. A contract review up front targets the real minority.
- Round 10 already has a contract-review stage for L and XL groups (`designer.md`, `design-review.md`).
Cost: M (a stage in R10-FLOW-DESIGN-STAGES' mechanism, `fixer.md` and `fix-review.md` edits). It adds one review round trip (median 1.45 h to 2.35 h) per group before any code.
Binding: in round 10 that added trip lengthens every remaining group to save on about 1 in 4 blocks. Round 11, starting with its plan, can price it. Closure saving: negative in round 10 if built now.

## P156: split the hot files by seam (S6-V77)
Verdict: ACCEPT -> round-11 design item, recorded in R10-ROUND-PLAYBOOK, as an input to round 11's P3 (`dev/governance/roles/architect-planner.md`: groups by owning seam, plans moves to the archscore target).
Source: s6 `proposals.md` `## V77` (orchestrator, 2026-10-25, tvofi-accepted idea 15).
Instances: `custom_components/heatpump_optimizer/coordinator.py` is 11299 lines at dfcd8d9be. Four open PRs touched it at once (filing). Round-10 groups still moving code out of it include R10-ARCH-SHAPES and R10-ADVISOR-RESIDUE (P141).
Cost: XL in the code. Measuring is cheap: conflicts and serial-routed entries per file from the train logs.
Binding: a seam restructure mid-round collides with every open coordinator group, and owner ruling R10 ARCH-DOCS waits on the architecture being finished. Round 11's P3 is the seat that plans exactly this. Closure saving: 0 h in round 10.

## P157: check-yield sunset (S6-V78)
Verdict: ACCEPT -> round-11 design item, recorded in R10-ROUND-PLAYBOOK, measured by the D13 dimension (`dev/governance/dimensions/D13.md`, process yield and cost).
Source: s6 `proposals.md` `## V78` (orchestrator, 2026-10-25, tvofi-accepted idea 16).
Instances: D13 already measures first-pass yield and rounds per merge (`D13.md:19-24`). The round-10 yield instruments exist (R10-GATE-YIELD, R10-FLY-YIELD-GUARD, both done), but no check records its own catches.
Cost: M (a per-check catch record, a retirement proposal path through `proposal-triage.md`, and a D13 brief extension, which is policy and the owner's words).
Binding: a ratchet on process overhead needs a round of catch data before any retirement is honest. Round 10 has none per check. Closure saving: 0 h in round 10.
Carry text (for `roster_edit.py append-carry R10-ROUND-PLAYBOOK`, citing `triage: dev/programme/triage/s6-batch28.md#P157`): "Round-11 design backlog (tvofi-accepted V73-V78, triage s6 batch 28 P152-P157). The playbook names each as a design item for round 11, to be designed before any build, with the evidence the ruling cites. (1) V73: speculative integration branch on the train's proof branches (`merge_train.py` `batch/<tag>-<n>`, bisect); settle check identity at merge. (2) V74: CI results cached by measured closure; the key must cover runner image and BLAS build, and the push-to-main full run stays uncached. (3) V75: executable claims with rendered figures; a PR-template and contract change. (4) V76: test-first review; price the added round trip against the measured share of real blocks. (5) V77: split the hot files by seam, as round 11 P3 input (architect-planner.md), starting from the per-file conflict and serial-route counts. (6) V78: check-yield sunset, with catches recorded per check and retirement proposed through proposal triage, measured under D13. Plus V65's trigger-rights daemon (P144). Each item states its round-11 owner seat."
