R10-DIMENSIONS-FULL-COVERAGE, p2 of 2 (a WIP handoff until p1, the wave-script grader alone, is on main: decision 0013; this branch carries the byte-identical grader file): policy, for the owner's review as code owner. It carries his four rulings of 2026-11-13: every dimension checks its whole universe and not a sample; two new dimensions; convergence toward zero objective bugs is made measurable; D11 and D13 run every round. It must merge before round 11's finders start.

**Both new briefs, `D16.md` and `D17.md`, are a draft for owner wording.** Each opens with the ruling and one italic sentence taken from the pre-study, not from the owner; the method, the scopes and the enumerator are mine.

What changes what a seat must do:

- **A. The denominator** (`dev/governance/roles/COMMON.md`, `dev/audit/config/finding.schema.json`). A finder's `coverage` row per step is `enumerator`, `universe`, `examined`, `not_reached`, `redispatched`; the depth word is gone. Two refusals, by different readers: the **schema** refuses a row with a field missing, at the finder's return (it is the return schema `fold_ledger.py sync` writes into `audit-find.js`); the **judge intake's mechanical half** (`denominatorGaps` in `.claude/workflows/audit-find.js`) refuses counts that do not close, a step with no row, and a handed-over item left unanswered, re-runs the seat once, then reads it as not reported, which refuses intake. Tested in `tools/policy/check-wave-script.mjs`, block "the denominator".
- **B. The dispatcher.** `carryOf` hands each seat, as first work, what its steps left the round before: every `not_reached` item, every `unfinished` entry, and a step an older round recorded below `deep`. `dev/audit/config/rotation.json` records the denominator per step. Where one round cannot examine a step's universe it declares `rotate` with a bound, and an item at the bound left unreached refuses the report. Three are declared, each with its enumerator and its size under Figures: D0.M4 (the solver grid), D3.M1 (unrecorded mutation sites, by file), D14.M2 (open classes). **The three bounds (6, 4, 4) are my estimates and the owner's to set**: no round has run under a denominator, so no seat throughput is measured. `CADENCE` puts D11 and D13 at every round.
- **C. Briefs.** D0, D1, D2, D3, D4, D6, D7, D8, D9, D10, D11, D12 and D14 lose their sampling text and gain what the pre-study lists; each keeps its owner-worded line. New numbered steps: D1 steps 7 (upgrade from a valid old payload) and 8 (redaction), D3 step 6 (a test whose oracle is the code), D8 step 6 (reason codes). D1 step 7 and D16 step 2 need an earlier release's own writer; the Prepare step of `audit-find.js` exports those packages under `old-releases/<tag>/`, and neither dimension is isolated (an isolated dimension is listed in `prepare_baseline.sh`, which CI pins to the base).
- **D. `D16.md` and `D17.md`**, with seats, boxes, rotation entries, the `CLAUDE.md` rows and every dimension list `git grep D15` returns.
- **E. `tools/audit/check_scopes.py`**: each dimension declares `territory`, and a tracked path it matches that no seat of that dimension owns is refused by name.
- **F. Convergence records.** Where each is written and by whom:
  - `universe`, `examined`: `rotation.json` rounds, by `audit-find.js` (finder contract `COMMON.md`).
  - `found`: `rotation.json` yield, by `audit-verify.js` from the judge's verdicts (`judge.md`), unchanged.
  - `cause` on a defect record, `{dimension, pr, round, by}`: the roster group, returned by the root-cause seat (`root-cause.md` section 6) and written by the orchestrator at the group's merge (`orchestrator.md` section 13).
  - `fixed`, `injected`, `escaped`, each with its denominator: `dev/audit/config/convergence.json`, written only by `tools/audit/convergence.py record` at the round close, which the orchestrator runs and reports (`orchestrator.md` section 13; playbook phase 13 in `dev/audit/README.md`).
  - barrier dates: `barriered_at` on each barriered class of `dev/audit/config/bugclasses.json`; `fold_ledger.py check` refuses a barriered class without the key.

Design choices a reviewer should know are choices: `territory` is a second declared list, not derived from the brief text, because a brief's Reuse section cites helpers that are tools and not territory; a derived rule read every dimension as failing. `not_reached` is capped by the schema and may name groups (a file, a class, a grid plane), so one reply never carries a round. Intake refuses the whole seat and not the one row, because a seat that returned findings without a denominator makes its count of findings unreadable.

Alternatives that lost: keeping the depth word beside the counts (two records of one fact, and the driver would have to say which wins); a per-brief denominator rule in each of the eighteen briefs (it would go stale unevenly; `finding-propagation.md` puts a rule for every seat of a role in the role contract, once); enumerators written by each finder only (D16 and D17 owe one by the brief, and D3's and D14's sampling could not be replaced by a number nobody can re-derive).

Sibling group R10-D5-D6-FULL-SCOPE: `handoff/r10-d5-d6-full-scope` did not exist at my start (`git ls-remote origin 'refs/heads/handoff/r10-d5*'` printed nothing; only its `handoff-wip/` ref did), so this branch does not build on it and keeps to disjoint keys of `scopes.json`: it touches no key of `D5` or `D6` there, and adds `territory`, `_territory_pending`, `D16`, `D17`. Three textual overlaps remain for whoever merges second: the `CADENCE` line of `audit-find.js`, the cadence test of `check-wave-script.mjs`, and `D6.md` step 2, where this branch adds the release-notes sentence.

## Head

74594227953ac1e76322cdc95f0462ed7a2f0d23 (WIP; re-take at the final head)

## Mutation proof

Each mutant applied to a copy, the named self-test run, restored.

- `tools/audit/check_scopes.py`, `territory()`: `unowned = sorted(files - owned)` replaced by `unowned = []`: `check_scopes.py --self-test` prints `SELF-TEST FAILED` naming `territory: D7 without the card and D8 without datetime.py are refused by name`. `ter_ok` dropped from `verdict()`'s return: it fails naming `the default verdict refuses a territory gap`. The `ledger` test of a pending dimension forced false: it fails naming `territory: a pending dimension whose ledger landed is refused`. The undeclared-dimension test forced false: the self-test exits non-zero on a `KeyError`.
- `.claude/workflows/audit-find.js`, driven by `node tools/policy/check-wave-script.mjs`:
  - `denominatorGaps` returning `[]` first: the ten `denominatorGaps refuses …` tests and `a seat whose report carries no denominator is dispatched twice, ends missing, and intake does not run` fail.
  - `carryOf` returning `[]` first: `carryOf at round 11 …`, `…at round 10 it reads round 9 only` and `seatCarry numbers C1.. …` fail.
  - the pre-intake `delete reports[s.id]` removed: `a seat whose report carries no denominator is dispatched twice, ends missing, and intake does not run` fails.
  - `overdue:` forced false: `seatCarry marks the age-2 item overdue at bound 3, not at bound 4, not with no rotate` fails.
  - `...again` dropped from the ledger's `not_reached`: `a carried item answered not_reached stays in the ledger under its original words` fails.
- `tools/audit/convergence.py --self-test`: `check` always passing, and `injected` counted for any `by`, each fail it naming an arm.
- `tools/audit/fold_ledger.py --self-test`: the `barriered_at` refusal removed fails `a barriered class with no barriered_at key is refused`.
- `tools/audit/enumerate.py --self-test`: `d16-writes` skipping `log_held` fails the three `d16` planted arms.

## Null control

- Territory: `check_scopes.py` at this head, given `origin/main`'s universes with this branch's `territory` keys, exits 1 and names the card for D7 and `datetime.py` for D8 (the two files the pre-study names), and the stub and budget files for D3; on this branch's `scopes.json` it exits 0. Commands under Figures.
- Denominator: a report whose rows close passes `denominatorGaps` with an empty list and intake runs (`null control: with the default stub every seat reports and intake runs`); the same report with `coverage: []` is refused.
- Carry: a dimension with no earlier round is handed nothing (`carryOf` returns `[]`), and its seats' prompts say so.
- Convergence: a round-N-2 fix is not counted as injected; a done defect group with a well-formed `cause` passes `check`.
- Rotation bound: an item below the bound, answered `not_reached`, is accepted.

## Figures

Measured at the head above, merge base `e23124ff6e` (`git merge-base origin/main HEAD`), 2026-11-13. The pre-study's figures are a seat's; the ones restated here were re-taken with the command beside them.

- `python3 -I tools/audit/check_scopes.py --repo . --ref origin/main --scopes <origin/main's scopes.json with this branch's territory keys>`: exit 1; `grep -c 'territory file owned by no seat'` prints 232. Per dimension it prints `unowned=` 88 (D0), 50 (D3), 5 (D4), 1 (D7), 7 (D8), 69 (D10), 3 (D11), 9 (D12). The pre-study's own count of files missing from the declared universe was 20 of 23 modules (D0), 50 (D3), 5 (D4), 1 (D7), 6 (D8), 69 (D10), 9 (D12); D0 and D8 differ because this branch's territory is every package module for D0 and adds `narrative.py` to D8.
- `python3 -I tools/audit/check_scopes.py --repo . --ref HEAD`: exit 0.
- `python3 -I tools/audit/check_scopes.py --repo . --self-test`: `SELF-TEST passed`.
- `node tools/policy/check-wave-script.mjs`: 253 passed, 0 failed.
- `python3 -I tools/audit/enumerate.py d0-grid | wc -l`: 1440 cells; `--plane price-weather`: 40. The pre-study wrote "≥ 480" from the brief's axes; the enumerator crosses three plant values and three horizons.
- `python3 -I tools/audit/enumerate.py d0-modules | wc -l`: 23, the pre-study's figure.
- `python3 -I tools/audit/enumerate.py d3-sites | wc -l`: 7473 sites of the gate's own mutation inventory; `--state unrecorded`: 2313; triaged 188; `--by-file`: 91 files. The pre-study's 4,441 was a grep of guard keywords, a different rule.
- `python3 -I tools/audit/enumerate.py d14-classes --status open | wc -l`: 19; all statuses: 55. Both are the pre-study's figures.
- `python3 -I tools/audit/enumerate.py d16-writes | wc -l`: 39 sites; `--cells`: 468.
- `python3 -I tools/audit/enumerate.py d17-features | wc -l`: 305.
- `python3 -I tools/audit/enumerate.py d1-excepts | wc -l`: 254, of which `broad` 97 (the pre-study: 254 and 98); `d1-stores`: 17 `store` lines.
- `python3 -I tools/audit/convergence.py report --round 10 --roster dev/programme/rosters/wave-r10-groups.json`: prints `universe=? examined=?` on every line, because round 10 recorded depth words, and `escaped=0`, because no round-10 group carries `cause`. Round 11 is the first round the record can be read for.
- `python3 -I tools/audit/fold_ledger.py check`: 0 violations; 19 of the 30 barriered classes print `UNDATED`, their barrier text citing no pull request that resolves to a merge on main. 11 carry a date.
- `node tools/policy/policy_lint.mjs --budgets`: the caps under Raise justification.
- `python3 tools/audit/archscore/score.py --diff origin/main`: the line under Raise justification.

## Raise justification

**pending owner confirmation.** `CLAUDE.md` rule 2: *"raise the budget with the owner's explicit confirmation, obtained before the branch is pushed"*. The dispatch brief for this group says instead: *"the raise is the owner s to approve with the pull request"*. This seat acted on the brief, pushes only `handoff/` refs, and opens no pull request; the raise merges only on the owner's approving review (`budget-raise-gate`).

Raised in `dev/governance/config/policy_budgets.json`: `corpus_tokens` 68618 to 71906; the per-file line and token caps of `COMMON.md`, `orchestrator.md`, `root-cause.md`, `CLAUDE.md` (tokens only), `dev/audit/README.md` (tokens only) and the briefs D0 to D4, D6 to D12 and D14, each to what `policy_lint.mjs --budgets` measures; `D16.md` and `D17.md` recorded new. The always-loaded and role aggregates stay inside their band and are not re-recorded.

Payments tried: three taken, four refused, and they do not cover the rulings.
- Taken: `D7.md` step 5's fixed list of eleven features replaced by the release-notes enumerator; `D3.md`'s sample-and-seed text replaced; `D14.md`'s pick rule replaced. Net of the new text each of these files still grew.
- Refused: cutting `D0.md`'s traps on #1293 and #2612, `D8.md`'s round-5 carry, `D9.md`'s round-2 pointer. Each constrains a finder today and I could not show any spent.
- Refused: moving the denominator rule out of `COMMON.md` into the schema's descriptions. The schema is not in the corpus, so the cap would hold, and the finder would read the rule nowhere it is told to read.
- Refused: one brief for D16 and D17. The owner ruled two dimensions.
- Refused: shortening `D16.md`'s and `D17.md`'s escapes lists. The brief asks for each dimension's escapes as worked examples.

Architecture score: dS +0.0000 NULL

## Unpinned sites

n/a: no line of `custom_components/` changes.

## Red checks

none

## Forward-carry

- `dev/audit/config/scopes.json` `_territory_pending`: D5 and D6 declare no `territory` here; `check_scopes.py` refuses the entry once either carries the `ledger` key R10-D5-D6-FULL-SCOPE adds, so that branch, or the merge of the two, declares both (D6's with `RELEASE_NOTES.md`, which `D6.md` step 2 now reads). Control: `check_scopes.py --self-test`, arm `territory: a pending dimension whose ledger landed is refused`. Carry: R10-D5-D6-FULL-SCOPE
- Round 11's roster: a defect group carries `cause`, or `convergence.py record` refuses the round close. Destination is `orchestrator.md` section 13, in this diff. Carry: dismissed: built in this pull request, in the orchestrator's own contract

## Friction

- ratchet-budgets: contradiction: the rule and `CLAUDE.md` rule 2 put a raise's confirmation before the push, the dispatch brief puts it at the pull request; recorded above as pending owner confirmation. Carry: dismissed: the owner's review of this pull request is the confirmation the rule asks for
- brief-citations: cost: `policy_budgets.json` keys D0 to D14 under their pre-move names and D15 to D17 under the new ones, so a seat recording a cap must resolve each key through `tests/layout.json`. Carry: dismissed: no behaviour depends on it and a rename is its own policy diff
