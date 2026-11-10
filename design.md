# R10-STANDING-CONTRACTS-P2 design note: P2 of design/r10-fly-standing-contracts

- **Base:** origin/main b8f67a775137a8032d5c71b34ea64165c1d4613a; every line cited below is at it.
- **Predecessor:** R10-FIXER-MD-SPELLING-CORPUS. Its handoff head is handoff/r10-fixer-md-spelling-corpus 925ade0cf. It touches fixer.md only and has no pull request.
- **Approved design:** design/r10-fly-standing-contracts 21210036507f (round 2), approved at design-verdict/r10-fly-standing-contracts 2d0ac2c0b. P1 is #3197 (b707d8932) and P3 is #3294 (8a4cf2618).
- **Roster:** origin/handoff/audit-r10-roster 2b265b62c. The group is size L, with 20 carries (0-19).
- **No new design.** This note binds the approved note's §6 "P2 (policy)" to the base, folds in P371 (carry 0), and records what moved since c3a279e3. Where they disagree, this note's line numbers win, because the approved note's were measured at the older base.

## 1. Owning seam

**Owner:** one new contract, dev/governance/roles/standing.md (absent at the base), as the approved note §1 rules.
- It holds the Wait, Reads (with the autofix hold), Recycle and alive-directory terms once.
- Every standing contract's opener cites it, and so does proposal-triage.md's.

**Retired:** standing-tick.md and standing-roster.md become retirement stubs. Each names the beat row that replaced it and keeps its file, so pulse.py's glob, CLAUDE.md and the playbook fixtures still resolve.

**Callers, edited:** orchestrator.md §5, CLAUDE.md's role table, INSTRUMENTS.md:44-47, the pulse.py STANDING map and its self-test, and the sweep_template.md placeholders.

**P371 seam:**
- Its owner is fixer.md, since the fixer is the seat that returns BLOCKED today.
- designer.md and design-review.md each gain one line that cites fixer.md.
- tools/pr/ci_predict.py is not edited: part (c) is already on main at e566f7e02. Its BOOTSTRAP text (ci_predict.py:656-657) cites "fixer.md, decision 0013 Consequences", and fixer.md has no such section yet.

## 2. Shape

**standing.md.** Four headings, each a few sentences:
- **Wait** (carry 1, approved item 1). A seat ends a turn only when nothing is owed. Otherwise it waits in a `run_in_background` shell loop that:
  - touches its alive file every 25 s, and its `FILE.d/<id>` entry, only while the seat's pid answers `kill -0`;
  - exits on a queue change or at the end of the window.
  A detached `nohup` wakes nothing. No tracked loop script is allowed (P51). The loop writes no pid into the alive file (approved item 27).
- **Reads** (carry 2). A table of each read and its cwd-safe instrument:
  - PR body: `policy_lint.mjs --pr-body` and `carry_audit.py check --body`;
  - PR state: `gh pr view --repo tvofi/heatpump_optimizer`, which prints UNREADABLE on a non-zero exit or an empty answer;
  - handoff refs: `bus.sh orphans`, or `git -C <worktree>`.
  A hand-written pipeline (`| wc -l`, `grep -c`, a bare `git` or `gh`) is never a check result. Each Bash call starts in the seat's original directory.
- **Autofix hold** (carry 3), one row of Reads. Dispatch a reviewer, or start a merge, at head H only when:
  - no mutation-autofix, closures-autofix or claims-autofix job at H is queued or in_progress; and
  - either a bot commit has moved the head (then act at the new head), or every autofix job concluded with no push. A red autofix job pushes nothing (ci-autofix.md).
  Read it with `failure_logs.sh` or `gh api repos/<r>/commits/<H>/check-runs`.
- **Recycle** (carry 4):
  - Trigger: the seat's context passes about 150k tokens or the seat has run 4 h.
  - Timing: only at a quiet point, with no op of its own mid-step and no train, push or open that it owns in flight.
  - Handoff: it writes `<seat dir>/STATE-HANDOFF.md` (pending waits with targets, in-flight ops, queue positions, held lines and their release conditions, next actions), stops only its own loops by PID, and replies HANDED.
  - Routing: new work goes only to the incoming seat, and only after HANDED.
  - The field figures stay in the triage record, not in the contract.
- **Alive files** (carry 19): `$HPO_STATE_DIR/alive/`, the directory the liveness hook reads (tools/audit/seat/hooks/liveness.py:91). Staleness is set by `HPO_ALIVE_STALE_MIN` (:90).

**Stubs.** Each is about 4 lines:
- standing-tick.md is "retired into the `tick-digest` and `owed-check` rows of `beatd.jobs.json` (tools/audit/seat/beatd.jobs.json:6, :26); read the digest".
- standing-roster.md is "retired into `roster-drain` (:46): queue ops for it; a refusal is never retried past the lint gate".
- Both quote the owner's constraint "make sure the retirement of the standing seats dont cause you to run things inline" once each. dev/audit/README.md:56-64 already states the retired state and does not change.

**standing-merge.md** (carry 5):
- Line 12's "`merge_pr.sh` merges a budget-file or policy head directly." becomes "a budget-file or policy head takes the train's serial route; `--pre-flight` parks it and it merges under the mandate" (tvofi 2026-10-26, "no merge outside the train").
- Carry 6 has already landed at lines 8-11, so nothing changes there.

**standing-dispatch.md:** the `git ls-remote` block at :26-28 goes, and the opener cites standing.md. Line 34 already names `bus.sh orphans`, so the cut loses no read.

**orchestrator.md** (carries 4, 7 and 8; approved items 10, 11 and 28):
- §5's sentence at :106-109 becomes one bullet:
  - two standing seats, standing-merge.md and standing-dispatch.md, under standing.md, which also sets their recycle;
  - tick and roster are beat rows;
  - you read state only from the plan page and the digest under `$HPO_STATE_DIR/digest/`;
  - the sweep restarts a seat that is absent or stopped with work owed.
- Carry 7 says "the ledger"; the approved note §2 made the digest the single wake-read, so the line names the digest, which is the ledger's beat output.
- §10b at :224 ("Through the roster seat, on `standing-roster.md`'s terms") becomes "Through the `roster-drain` queue; `roster_edit.py`'s lint gate binds".
- :88, :113 and :148 name merge and dispatch, which stay, so they do not change.

**P371, three lines of policy (carry 0 parts a and b):**
- fixer.md gets a short paragraph near the handoff steps. When `ci_predict.py` prints BOOTSTRAP (the base's copy of a grader this diff changes refuses, and the head copy passes in prepr), do not return BLOCKED. Choose one of:
  - move the registration into unpinned data the grader already reads (dev/governance/config/corpus_excluded.json, #2916);
  - split: the grader hunks alone as the p1 handoff, and the rest as a work-in-progress handoff that resumes as p2 once p1 is on main.
  Cite decision 0013 Consequences (dev/governance/decisions/0013-verdicts-post-as-the-approver-app.md:102-105) and do not restate it.
- designer.md step 7 gains: "a change set that adds what a pinned grader in a restoring job must register names its p1/p2 split (`fixer.md`)".
- design-review.md step 2 gains: "a design that relies on a grader's new behaviour inside the pull request that changes that grader is `revise` (`architecture-unsound`)".

**Invariants:**
- No behaviour moves into the orchestrator's turns.
- Merge, dispatch and triage stay LLM seats.
- No beat row changes; P1's rows are only cited.
- ci_predict.py's verdicts and rc do not change.

**Dog-food check.** This group's own change set is registered only in data (policy_budgets.json, tests/closures.json), so no pinned grader should need a p1. The fixer confirms this by running `ci_predict.py` before the handoff. If it prints BOOTSTRAP, the new fixer.md paragraph applies to this group too.

## 3. Alternatives

- **Copy each term into all four contracts (carries 1-4 as written).** Lost: each standing and P371 per-file cap in §6 is within 4 tokens of its measure, so four copies need four raises against one new cap. finding-propagation.md also says to write a rule "once". This is `decision: owner`, routed by the approved note and ruled here at merge.
- **Put P371(a) in decision 0013 rather than fixer.md.** Lost: the BOOTSTRAP line already cites fixer.md, and a seat reads its contract, not decisions.
- **Retire tick and roster by deleting their files.** Lost: pulse.py:585's glob check, the playbook fixtures (tools/policy/fixtures/playbook-null.md:9) and the CLAUDE.md rows all resolve the paths. The stubs are cheaper than three more edits.

## 4. Sibling sites (enumerated at the base)

`git grep -n -E "standing-(tick|merge|dispatch|roster)\.md" -- ':!dev/archive' ':!dev/programme' ':!dev/audit/rounds'` lists the sites below. Each is either edited by this group or out of scope for the reason given:
- CLAUDE.md:122-125: edited. Two rows merge into one retired row, and a standing.md row is added.
- orchestrator.md:107-108 and :224: edited. :88, :113 and :148 stay.
- INSTRUMENTS.md:44-47: edited to two seats plus the two rows.
- sweep_template.md: :67 (1b) drops tick and roster; :83 (5), the tick restart, goes; `tick_alive` and `tick_brief` leave the placeholder table (approved item 21).
- pulse.py:114 STANDING loses tick and roster. The self-test at :585 changes in the same commit, to the non-stub contracts or to STANDING plus a retired set (approved item 26).
- tests/closures.json:1586-1589 and tools/ci/selftest_closures.json:6426-6429: re-derived, not hand-edited.
- tools/audit/seat/ledger.py:649 (a docstring): it cites "the ancestor-recarry test of standing-tick.md", which is standing-tick.md:15. The stub drops that text, so the docstring cites ledger.py's own `recarry` (P90) instead. The approved note missed this site.
- dev/audit/README.md:40, :61-62 and the policy fixtures: already true, or recorded snapshots. Out of scope.
- `git grep -n merge_pr.sh -- dev/governance/roles` finds standing-merge.md:12 (edited) and nudge.md:89 (a postmerge caller, out of scope).

## 5. Evidence, by file

There is no finder harness: the evidence is the owner's rulings, the triage records P51, P95 and P371, and the s9 census. Every figure is re-measured at the merge base.

**tests/entities.py, one check, rows a-c:**
- (a) Every standing-*.md and proposal-triage.md cites standing.md.
- (b) standing.md carries its five headings, including the `$HPO_STATE_DIR/alive/` string.
- (c) The file that ci_predict.py's BOOTSTRAP constant cites (fixer.md) contains `BOOTSTRAP` and `0013`.
- Failing first: (c) fails on the base, because fixer.md lacks both. That is P371's dangling citation, and it is the "detector shown to detect" run.
- Null: the edited tree passes.
- Mutants: delete any one heading, or the fixer.md paragraph, and the check turns red.

**pulse.py --self-test:** passes with tick and roster removed from STANDING. A mutant that restores either seat to STANDING fails the self-test at :585.

**sweep_render.py fixture:** the rendered sweep names no `tick_alive`. A mutant that restores step (5) fails.

**Control for carry 5:** `git grep -n merge_pr.sh -- dev/governance/roles/standing-*.md` prints nothing at the head.

**policy_lint --budgets:** every row is at or below its cap (approved item 28's control).

**Goldens and claim files:** none move.

## 6. Gate, budget, hot files, serial position

**Gate** (the approved note §6, `decision: orchestrator`). The orchestrator records two things in the PR body before merge, and the fixer cannot produce them from a cloud seat:
- `beatd status` showing every P1 row `ok` from main for one cycle beside the live seats;
- for the roster retirement, the roster-drain job landing a seeded no-op-safe op on a scratch roster branch and refusing a seeded lint failure, with the seat beside it for one cycle.

**Budget** (`node tools/policy/policy_lint.mjs --budgets` at b8f67a775; re-measure at the merge base):

| file | lines / cap | tokens / cap |
|---|---|---|
| fixer.md | 315/315 | 5210/5216 |
| designer.md | 60/60 | 878/878 |
| design-review.md | 53/53 | 778/778 |
| orchestrator.md (key tools/audit/briefs/orchestrator.md) | 292/295 | 4234/4251 |
| standing-merge.md | — | 504/507 |
| standing-dispatch.md | — | 507/509 |
| standing-tick.md | — | 326/330 |
| standing-roster.md | — | 368/368 |

- The corpus is 41 tokens under its cap, and the role-fixer aggregate is inside its band but over its cap.
- The P371 lines are paid inside each file by tightening, never by a raise; the carry grants none.
- standing.md's tokens are paid by the two stubs and dispatch's ls-remote block. The corpus line ends at or below its cap.
- standing.md's new per-file cap and the lowered tick and roster caps go in policy_budgets.json. The new cap is a `capfile` raise under `budget-raise-gate`, and needs the owner's review, or a mandate in force scoped `budget-raise` or `all`, with `## Raise justification`.
- CLAUDE.md is always loaded. The net change to its rows must not raise always_loaded_tokens.

**Serial position:** after R10-FIXER-MD-SPELLING-CORPUS, because both edit fixer.md and fixer.md's cap is shared. The fixer starts from the predecessor's merged fixer.md and re-measures.

**Hot files:**
- orchestrator.md is in the roster's hot_files.
- standing-dispatch.md is shared with R10-TICK-LEVELS and R10-DISPATCH-AT-HANDOFF (approved note §6). Re-check their state at dispatch.

**Roster `files`** lacks standing.md, proposal-triage.md, CLAUDE.md, policy_budgets.json, INSTRUMENTS.md, ledger.py, tests/entities.py and the two closure files. Adding them is `decision: orchestrator`, as a roster op through roster-drain.

**Policy:** every edited contract, CLAUDE.md and policy_budgets.json. The owner's approving review at merge, or mandate 6329234399.

## 7. Carries

- Carry: R10-STANDING-CONTRACTS-P2 (item 1): P371(a) and (b) go in fixer.md, designer.md and design-review.md as §2 states.
- Carry: dismissed: already on main (item 2): P371(c) landed at e566f7e02, and its controls are in that PR.
- Carry: R10-STANDING-CONTRACTS-P2 (item 3): Wait, Reads, the autofix hold and Recycle go in standing.md, written once. Carries 1-4 ask for a copy in each contract; that is `decision: owner`.
- Carry: R10-STANDING-CONTRACTS-P2 (item 4): merge_pr.sh gives way to the train route (carry 5).
- Carry: dismissed: already landed at base (item 5): carry 6's train-join wording is at standing-merge.md:8-11.
- Carry: R10-STANDING-CONTRACTS-P2 (item 6): §5's line on reading only the plan page and the digest, which covers carries 7 and 8.
- Carry: R10-ORCH-LEDGER (item 7): the merge-seat retirement (carry 9) and the dispatch beat job (carries 12-14) are unbuilt, as the approved items 12 and 15-17 state. Merge and dispatch stay seats here.
- Carry: R10-STANDING-CONTRACTS-P2 (item 8): roster retirement (carries 10 and 11) and tick retirement (carry 17), behind §6's gate.
- Carry: dismissed: built by P1 #3197 (item 9): carries 15, 16 and 18 are the job table and sweep rewrites; P2 only cites them.
- Carry: dismissed: built by P3 #3294 (item 10): carry 16 part (2), the hooks.
- Carry: R10-STANDING-CONTRACTS-P2 (item 11): standing.md names `$HPO_STATE_DIR/alive/` (carry 19).

## Notes for the fixer

- Carry: R10-STANDING-CONTRACTS-P2 (item 12): ledger.py:649 cites the ancestor-recarry test of standing-tick.md:15, which the stub drops. Check whether the tick-digest row (beat_jobs.py) or ledger.py itself now owns that test. Cite whichever does, and do not move the prose into standing.md.
- Carry: R10-STANDING-CONTRACTS-P2 (item 13): read fixer.md at the predecessor's merge before choosing what to tighten. Its step-6 tightening (925ade0cf) may already have spent the obvious lines.
- Carry: R10-STANDING-CONTRACTS-P2 (item 14): standing.md is new and tracked. Confirm `tests/entities.py` classifies it, under the dev/governance/ INERT prefix (tests/closure.py) or a measured closure, before pushing.
