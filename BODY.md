The owner's standing rulings move into the tree as `dev/programme/RULINGS.md`, and the liveness hook's post-compaction corpus changes to match: `CLAUDE.md`, `dev/governance/roles/orchestrator.md` and every `.claude/rules/` file in full, and of `tools/audit/seat/INSTRUMENTS.md`, `tools/audit/seat/instruments/` and `RULINGS.md` only the files whose blob differs from the last accepted proof's manifest. A missing rulings file is listed as removed and the corpus is still written; a missing `CLAUDE.md` or role contract writes no corpus and prints `POLICY-CORPUS unwritten`. Roster group R11-PRE-RULINGS-FILE; policy, for tvofi's review (approvable under mandate 6893738184).

## Rulings this pull request carries out

- tvofi, 2026-11-13, card P6 ("Yes") and card R3 (verbatim: "Full for CLAUDE.md, orchestrator contract and rulings; changes only for instrument pages"): the rulings file, read and proven after each compaction by the liveness hook.
- tvofi, 2026-11-15, verbatim "Rules in full", relayed by the round-11 orchestrator: `.claude/rules/` is read in full, not by change. This replaces the cloud fixer's by-change reading of the rules on the step ref.
- tvofi, 2026-11-15, verbatim, relayed by the round-11 orchestrator: "This file should be excluded by the corpus but still needs to be re-read on changes, just like instruments.md". It supersedes the same day's card answer "Count it, raise the cap (Recommended)" and R3's reading of the rulings file in full. `RULINGS.md` is listed in `dev/governance/config/corpus_excluded.json` with that ruling as its reason. **The exclusion is the owner's ruling**: no cap is raised, `tools/policy/policy_lint.mjs` and `policy_budgets.json` are unchanged, and the hook still re-reads the file whenever it changes.
- tvofi, 2026-11-15, verbatim "Retire your candidates", and his second review the same day by decision cards ("Retire H3 (Recommended)", "I3 first, I2 as fallback (Recommended)", "Keep, scoped to train runs (Recommended)", "Retire J10", "Fix the contract to match (Recommended)", "Retire G14 (Recommended)", "Retire K11, K12 on parity (Recommended)", "Keep both parts"): the retired entries sit in the file's closing section, one dated line each naming what supersedes it.
- Card "Fix the contract to match (Recommended)", a policy edit under mandate 6893738184: `orchestrator.md` section 11's "Never `--allow-red`" becomes `--allow-red` only when the red's cause is established as not the pull request's (for a stamp, CI tooling and not product code) and commented or recorded, never over a concluded red whose cause is unknown; revert-first for a behaviour change in the merged diff stays. Paid inside the file's caps by cutting stale text: section 1's `push.sh` clause (`push.sh` is retired by `CLAUDE.md`'s identity section), section 5's `pr_cap` default-6 description (the cap's value is in `RULINGS.md`), and a non-binding aside in section 4.
  Other "never allow-red" statements in the tree, by `git grep -n -i -E "never[^.]{0,40}allow-red"` outside round records: `dev/governance/roles/nudge.md` lines 47 and 85 (merge-train flag; the file binds Cursor orchestrators only and its reconciliation is the nudge ruling of 2026-11-12, left); `dev/programme/HANDOVER.md` line 1035 (a train run, which the train-run entry keeps; state, not policy, left); `dev/programme/plan-2026-09-open-issues.md` line 2203 (a frozen 2026-09 plan record, left). No rule, sweep template or instrument page states it.
- tvofi, 2026-11-15, verbatim: "The live repo should never contain any opinions (personal or otherwise, from codeowner, contributors or their agents) on anything but code and product and the function of the code and product. Opinions (both explicit and implicit) are near as sensitive as personal identifiable data"; then "This should be promoted to policy"; and "the findings from that dimension does not go as open issues but directly to me". These become `CLAUDE.md`'s new section "What the repository may carry", stated once; the rulings file holds no copy. `CLAUDE.md` is the owner because the rule binds every push and every seat, and it is the one policy file every session loads; no rule under `dev/governance/rules/` covers what a push may carry. Paid inside `CLAUDE.md`'s caps (`ratchet-budgets.md`): the "Root-cause remediation" section, which restated the index rows for `defect-root-cause.md` and `root-cause.md` and `defect-root-cause.md`'s own "resolved at merge (card C5)" sentence, is removed; the steward line's sentence about a `babysit/` file and the `AGENTS.md` line are shortened. No cap changes. Existing rulings entries were not re-screened against the new rule in this pull request.
- Carry 0, card E11-N-OBJECTIVE-RECORD part (b), "Write it now (Recommended)", preliminary: `orchestrator.md` section 9 names the round's objective record under `dev/audit/yardstick/` as a closure criterion.

## Screen against policy

tvofi, 2026-11-15, verbatim: "Also screen the rulings for overlap with policy, if both policy and rulings mandates something, policy is the right place"; "The point with this is that policy files and policy related files should follow good data integrity practice, no duplication, that creats risks of divergence"; and '"Fully stated in policy" should be dropped from the rulings file.' This is now the file's admission rule. Each in-force entry was grepped for its operative terms (`git grep -n -i -E <terms> -- CLAUDE.md dev/governance/roles dev/governance/rules dev/governance/decisions .github/PULL_REQUEST_TEMPLATE.md`) and the policy sentence read. Instrument pages were not counted. Classes: (a) fully stated, dropped from the file; (b) partly stated, delta kept with the policy file named; (c) conflicts, kept and reported; (d) not in policy, kept.

(a) dropped, with where policy states it:
- 2026-11-12 "a mandate made by me is valid for my machinery": decision 0017, point 5.
- 2026-11-13 objective-bug convergence, process convergence, the objective function and its acceptance test, the population "yours to set": decision 0018, Context and the population paragraph.
- 2026-11-15 objective record as closure criterion: `orchestrator.md` section 9 (this pull request).
- 2026-10-29 round-major versions: decision 0016, Decision.
- 2026-11-08 20%/10% bar: `proposal-triage.md`, "Bar" and "Machinery".
- 2026-11-14 once-per-round triage: `proposal-triage.md`, opening paragraph.
- 2026-09-25 audit-class barrier: `defect-root-cause.md`, "Except an audit class".
- 2026-10-03/10-31 tools on main: `orchestrator.md` section 13, "An instrument the programme runs is a tracked, self-tested file"; `CLAUDE.md`, Instruments.
- 2026-11-15 "Rules in full": `orchestrator.md` section 0 (this pull request).
- 2026-10-22/10-28 critical path over every cap and first in every queue: `orchestrator.md` section 5, "A ready critical-path group starts regardless of every cap"; decision 0015 point 6.
- 2026-10-24 ready handoffs never held: `orchestrator.md` section 5, "Opening or updating a pull request for an owed handoff is never refused by it".
- 2026-11-08 no self-carry: `fixer.md`, "A finding in your own group's seam is built in this PR".
- 2026-11-07/11-09 non-required reds: `defect-root-cause.md`, "Only a red on a required check is owed an answer".
- 2026-11-05 allow-red on an unrelated cause, and 2026-11-11 item 7 (stamp over a CI-tooling red): `orchestrator.md` section 11 (this pull request).
- 2026-11-07 no fixer re-merge on a main move: `fixer.md` step 6, "merge `origin/main` ... only when `git merge-tree --write-tree origin/main HEAD` reports a conflict"; `fix-review.md` step 12.
- 2026-10-08 architecturally sound fixes and raises as a last resort: `fixer.md` step 17 and "When a budget blocks the work".
- 2026-11-12 the contributor mechanism: decision 0017, Decision.
- 2026-09-16 clean handover: `orchestrator.md` section 9, "The handover is one file and it is not optional"; `writing-for-agents.md`.

(b) kept as the delta, the rest named: 2026-11-08 the orchestrator posts the mandated review itself (decision 0013); 2026-10-23 no laundering of a seat's denial (`CLAUDE.md` rule 2, decision 0013); the freeze's exceptions and the prototype (`orchestrator.md` section 5, `proposal-triage.md`); RCA immediacy and its L8 timing (`CLAUDE.md`, `defect-root-cause.md`); the rulings file's exclusion (`orchestrator.md` section 0); the pipeline shadow and speculative gating (`fixer.md` step 6); coordinator cap 3 (`orchestrator.md` section 5); reviewer timing (`fix-review.md` step 12); a significant new feature designed whatever its size (`orchestrator.md` section 5); the public plan page and its link in the answer (`orchestrator.md` section 5); stamping without waiting for main (`orchestrator.md` section 11).

(c) conflicts, kept and reported to the orchestrator, not resolved here:
- 2026-11-09 "only fire reviewers before ci is finished for prs on the cr watch" against `orchestrator.md` section 5, "Dispatch a fix's reviewer when the fixer pushes, not when CI settles".
- Card P2 "severity route narrowed" against `proposal-triage.md`, "Machinery": "`medium`, `high`, `major`, `critical`, root-cause countermeasure, closeout, owner directive skip them".
- 2026-11-13 "you may have a fixer have more carries based on their kind" against `fixer.md`'s preamble, "at most five findings".
- 2026-11-13 "always check everything in their dimension, not only small samples" against `D3.md` ("Sample 30–40 mutants") and `D11.md` ("Conformance, sampled").
- 2026-11-06 "You may always approve such changes under a validscope all mandate" (and 2026-10-20/27) against `orchestrator.md` section 13, "Two things are the owner's ... policy, this file included, approved before merging" (decision 0015 point on contracts reads a mandate as enough).

(d) every other in-force entry is not stated in policy and is kept unchanged. Inside the file, duplicates were merged: card P2's and card P11's quotes now live only in the card list, and the two closing lines on the whole-corpus re-read are one line.

## Entries that stay, and their promotion recommendation

The file's purpose (orchestrator's wording, tvofi 2026-11-15: "This is exactly how I see it") heads it: a holding area below policy that should shrink as rulings graduate. Numbering is the file's at this head (sections lettered in order, entries numbered within each). "op" means it stays operational; "→ X" means it is a candidate to graduate into X. No promotion is made in this pull request; tvofi rules each.

| entry | class | recommendation |
|---|---|---|
| A1 current mandate | d | op |
| A2 mandate is full-scoped | c | → `orchestrator.md` section 13 (with the conflict) |
| A3 approve sound policy under the mandate | c | → `orchestrator.md` section 13 / decision 0013 |
| A4 orchestrator posts the mandated review | b | → decision 0013 amendment |
| A5 no laundering a seat's denial | b | → `ratchet-budgets.md` |
| A6 owner's own words under the mandate | d | → `CLAUDE.md` dimension-brief line |
| A7 ruleset toggle | d | op |
| A8 admin rights, stuck-run deletion | d | op |
| A9 session grants in his words | d | → `orchestrator.md` section 1 |
| A10 card X1 | d | op |
| B1 5-minute default | d | → `orchestrator.md` |
| B2 cards only when he is active; the 5-minute wait first (2026-11-15) | d | → `orchestrator.md` |
| B3 audit findings as decision cards (narrowed) | d | op |
| B4 prune review: decided, not verified | d | op |
| B5 read the roster stage before asking | d | op |
| B6 seat questions to the orchestrator | d | → `standing.md` |
| B7 recommendation first for judgement-heavy rulings (2026-11-15) | d | → `orchestrator.md` section 2 (no clause beyond section 5's architect note was found) |
| B8 effort raised for a single turn (2026-11-15) | d | op |
| B9 fix every slip | d | op |
| B10 no no-op replies | d | op |
| B11 no connectors | d | op |
| C1 every dimension covers its scope | c | → `COMMON.md` and the dimension briefs (with the conflict) |
| C2 finder start on the critical set | d | op (round 11) |
| C3 open groups move at cutover | d | → `dev/audit/README.md` |
| C4 playbook pickup | d | → `dev/audit/README.md` |
| C5 owner and outside items fold in | d | → `orchestrator.md` section 5 |
| D1 freeze exceptions, prototype | b | → `proposal-triage.md` or a decision record |
| D2 deadlocks by hand | d | → `orchestrator.md` section 13 |
| D3 limiter first, P2 reading | c | op (round 11 start); P2 → `proposal-triage.md` |
| D4 loop-study cards | d | → a decision record |
| D5 RCA immediacy, L8 | b | → `defect-root-cause.md` |
| D6 mechanise before policy | d | → `orchestrator.md` section 13 |
| D7 carries by kind | c | → `fixer.md` (with the conflict) |
| D8 no CI widening, local macOS seats | d | op |
| E1 card list | d | op (record of rulings being built) |
| E2 this file's exclusion | b | op |
| E3 pipeline shadow, speculative gating | b | op (round 11) |
| E4 keep re-routed pull requests open | d | op |
| E5 study review | d | op |
| F1 CP and outside never slip | d | → `orchestrator.md` section 5 |
| F2 outside first | d | → `orchestrator.md` section 5 |
| F3 hotfix definition, CP past the record step | d | → `orchestrator.md` section 5 |
| F4 production above the cap | d | → `orchestrator.md` section 5 |
| F5 CI priority, "Dont do A" | d | op |
| F6 every item has a holder | d | → `orchestrator.md` |
| F7 owed means this turn | d | → `standing.md` / `orchestrator.md` |
| F8 coordinator cap 3 | b | op |
| F9 roster order prevents conflicts | d | → `orchestrator.md` section 5 |
| F10 existing groups first | d | → `proposal-triage.md` / `architect-planner.md` |
| F11 verify groups after changes | d | → `architect-planner.md` |
| F12 gantt drift | d | op |
| F13 no scoping out user-visible quality | d | → `fixer.md` / `designer.md` |
| G1 train runs batch, overlap, pause | d | op |
| G2 records and delivery rows at the stamp | d | → `delivery-status-tracking.md` |
| G3 cancel record CI, never close | d | op |
| G4 no merge pause on an unrelated ratchet red | d | → `orchestrator.md` section 11 |
| G5 cancel superseded runs | d | op |
| G6 a pull request still needs valid evidence | d | → `fix-review.md` |
| G7 prepr once, scoped hotfix prepr | d | → `fixer.md` |
| G8 merge verdict before CI is green | d | op |
| H1 reviewer timing | c | → `orchestrator.md` section 5 (with the conflict) |
| H2 blocked verdicts back to the fixer | d | → `fix-review.md` / `fixer.md` |
| H3 reviewer model at least the fixer's (Fable reviewer only for work of that class, orchestrator's reading) | d | → `fix-review.md` |
| H4 significant features designed | b | → `designer.md` |
| I1 public plan page in the answer | b | → `orchestrator.md` section 5 |
| I2 fallback: our version with thanks | d | → decision 0017 amendment |
| I3 outside security review | d | → `fix-review.md` |
| J2 Fable reserved for the most complex architectural work (2026-11-15) | d | op |
| J3 triage seat on opus, product-feature triage included (2026-11-15) | d | → `proposal-triage.md` |
| J1, J4-J11 seat routing, cloud, local cap, re-fire, dispatch, liveness, restarts, frugal guard, messaging | d | op |
| K1 resume prompt generated | d | op |
| K2 record beat, plan page | d | op |
| K3 leave duplicate record lines | d | op |
| K4 naming "tvofi" | d | → `CLAUDE.md` Identity |
| K5 no footers | d | → `CLAUDE.md` |
| K6 `nudge.md` references | d | op (temporary) |
| K7 keep working, daemonise | d | op |
| K8 wake loop | d | op |
| K9 brief check after a compaction | d | op |
| K10 local liveness hook until parity | d | op (temporary) |
| L1 stamp without waiting for main | b | → `orchestrator.md` section 13 |
| L2 stamp cadence | d | → `orchestrator.md` section 13 |
| L3 release extra steps | d | → `orchestrator.md` section 13 or a decision record |

## What the rulings file holds

Each ruling still in force, dated, quoted verbatim where the orchestrator's memory kept his words, "as recorded" where it kept only a paraphrase, and any interpretation labelled the orchestrator's reading. Only the current mandate's id, scope and expiry appear. Superseded, spent (round 10's closure, v10.0.0) and retired entries sit in one closing section, each naming its successor or reason. Technical lessons and tool quirks are left out. No email address, host path, session id, scratch path or content of tvofi's diagnostics download is in the file.

## Approval

Policy files touched: `CLAUDE.md` (index entry, the new "What the repository may carry" section, the removed "Root-cause remediation" restatement) and `dev/governance/roles/orchestrator.md` (sections 0, 1, 4, 5, 9, 11); code-owned data beside them: `dev/governance/config/corpus_excluded.json` and `tests/layout.json`. Awaiting the owner's approving review, which the orchestrator may give under mandate 6893738184 (scope all) as decision 0013 allows, declared as an agent's. Every ruling this pull request writes down is tvofi's own, quoted in "Rulings this pull request carries out".

## Head

`464a5891bc7a6bf1baf2ad5ea62f5b6cff5abaf6`, on base `b3831ff64eca1936f0b618193ee86c3e337b51a9` (the cloud step ref's base); diff three-dot against it. Not rebased; `git merge-tree --write-tree origin/main HEAD` reports no conflict.

## Mutation proof

`python3 tools/audit/seat/hooks_setup.py --self-test` (run with `TMPDIR` on a non-symlinked directory, see Red checks) printed `hooks_setup self-test: 74 checks, 0 failed`: every case green, the un-mutated copy green, and every mutant red. The mutants this branch adds, each in `MUTANTS`:
- `the corpus carries every page, changed or not` (`if proven.get(n) != b)` -> `if True)`)
- `the proof never records its manifest`
- `the corpus carries no changed page` (drops `*changed`)
- `the corpus drops the rules` (drops `*sorted(full)`: an unchanged rule file leaves the corpus)
- `the rules are read by change` (`FULL = ()`, rules moved back into `BY_CHANGE`)
- `the rulings file is read in full` (`RULINGS.md` added to `CORE`)
- `a changed rulings file is dropped` (`RULINGS.md` removed from `BY_CHANGE`)
- `a missing core file still writes a corpus`

## Null control

- In the self-test, a PostCompact with nothing changed since the accepted proof writes the core and the rules only: `read-proof: nothing changed since the proof reads the core and the rules only (null control)` asserts `.claude/rules/r.md` in, `RULINGS.md`, `instruments/a.md`, `instruments/b.md` and `INSTRUMENTS.md` out, and `unchanged since the last proof: 4 page(s); removed: none`. The next case changes `RULINGS.md` and asserts it is in.
- A rulings file deleted at origin/main still writes the corpus with `removed: dev/programme/RULINGS.md` (`read-proof: a rulings file gone from origin/main is a removed page, and the corpus is still written`); a deleted role contract writes none.
- With no proof manifest every instrument page is in: `read-proof: with no proof manifest every page is in (null control for by-change)`.
- The un-mutated copy passes before any mutant runs (`null control: the copy un-mutated`).

## Figures

<!-- figure-block: scope-line mb=b3831ff64eca1936f0b618193ee86c3e337b51a9 head=464a5891bc7a6bf1baf2ad5ea62f5b6cff5abaf6 -->
~~~text
MODE: SCOPED -- 2 script(s) run, 31 scoped out.
~~~
<!-- /figure-block -->
- hook self-test: `python3 tools/audit/seat/hooks_setup.py --self-test` printed `hooks_setup self-test: 74 checks, 0 failed` (hooks unchanged since that run).
- structure: `python3 tests/structure.py` printed `STRUCTURE RATCHET PASSED`.
- policy budgets: `node tools/policy/policy_lint.mjs --budgets` printed `CLAUDE.md 214 221 3605 3605`, `always-loaded: ~3605 tokens, cap 3349 +band 500 = 3849` and `corpus: ~69190 tokens, cap 69333 +band 500 = 69833`; `orchestrator.md` stays within 295 lines and 4251 tokens; `RULINGS.md` is not measured (excluded). The `CLAUDE.md` and `orchestrator.md` additions were paid inside their existing caps: the `CLAUDE.md` index entry went into the existing "suite, register, handover" list and the root-cause sentence listing what `defect-root-cause.md` and `root-cause.md` contain became a pointer to them; the `orchestrator.md` section-0 and section-9 additions were condensed. No cap changes.
- policy lint: `node tools/policy/policy_lint.mjs` printed `TOTAL: 0 error(s) across 52 policy file(s)`; with `RULINGS.md` named in `CLAUDE.md` and absent from `corpus_excluded.json` the same command printed the `[named-docs] dev/programme/RULINGS.md` error (an earlier head of this branch).

## Red checks

- `hooks_setup.py --self-test` fails one case on macOS at the base as at this head, `beatd: run at the floor starts, and records its cwd, argv and HPO_* environment`: the fixture compares a recorded cwd with `/var/...` while macOS resolves it to `/private/var/...`. Pre-existing on main `b3831ff64e`, host-only (CI runs Linux); the run above sets `TMPDIR` to a non-symlinked directory. Not answered as owed: not in this diff and not a required-set red.
- Otherwise none known at this head; the orchestrator reads the check-runs.

## Forward-carry

- tvofi's ruling of 2026-11-15 (card "Hold delivery rows for the stamp too", recorded in `dev/programme/RULINGS.md` under "Merges, CI and reds") has the automatic delivery-rows pull request (`record/autofix`) wait and merge only with the stamp batch. Two instruments contradict it: the record-autofix job's own automerge path (merging on `tools/audit/seat/record_row.py --automerge-check` alone between stamps), and the board's `RECORD-OWED` line (emitted through `tools/audit/seat/beat_jobs.py`, `ledger.py`, `orchestrator_tick.py`, `owed_unactioned.py`), which raises a green unmerged one as owed. Control for the change: a `record/autofix` pull request green and unmerged between stamps raises no line and is not merged; under the train's `--stamp` queue it is admitted with the stamp batch. It is an instrument change, held by the round-11 instrument freeze for the round-end proposal triage; no workflow or instrument changes in this pull request. Carry: R11-INTAKE-R10-RESIDUE

## Friction

none
