# Design: R11-PRE-NO-READ-BUILDERS (size L, decision 0014), round 2

- Base: 824a016f7562c307b81b30a3c39e3844b1b4b630 (`origin/main` at dispatch). Answers `Design review: revise dcf02aadcf524e8a6ec7fa673ba53d44ba28b3e6 architecture-unsound` (f6b5c4fcbe); revise points R1-R3, the routed edge and the four notes are answered below by their tags.
- Predecessor R11-PRE-MACHINERY-LIMITER: handoff head 363f3e7df7, unmerged at the base. `git diff --stat $(git merge-base 824a016f75 363f3e7df7) 363f3e7df7` touches none of this note's files. Its one-in-one-out clause binds every part: no part adds a required check; every read is report-only and its arms go in the owning instrument's existing `--self-test`.
- Cards re-read at eval/r11 tip c6ce415b77 (`review.verdict` approve, round 3, at 02a48db212): the four are `decision: accepted`, ruled ("Build all four reads"), `gates_finders: false`; none rewritten or dropped, none held out.
- Finder harness: none (owner-directed instrument cards). Evidence: each card's `null_control` at c6ce415b77.

## Parts, by owning seam

| part | card | owning module | after |
|---|---|---|---|
| A | ROLE-CLAUSE | `.claude/workflows/web-fix-wave.js` (the vocabulary); `tools/audit/seat/review_strength.py` reads it | the limiter |
| B | RULE-YIELD (dates, yield) | `tools/audit/fold_ledger.py` | the limiter; serial with R11-PRE-SECURITY-PRIVACY [b-hotfile] |
| C | RULE-YIELD loads; INSTRUMENT-YIELD; GATE-CAUSE's workflow run line | a new session-yield seat instrument under `tools/audit/seat/` (the fixer names the file in the body), importing R11-PRE-TOKEN-LEDGER's per-session iterator | R11-PRE-TOKEN-LEDGER's merge |
| D | GATE-CAUSE (a cause per red run) | `roster_lib.convergence_why`'s vocabulary and `loop_ledger.py` (both at acf0b72578, handoff/r11-pre-round-metrics-p2) | R11-PRE-ROUND-METRICS part 2's merge; R11-PRE-TOOLCHAIN-PIN for one column |

[routed] D builds on part 2's merged code and carries nothing into it: the vocabulary change of R1 is D's own diff, made after that merge. So the orchestrator adds two `after` edges (part 2's merge for D, R11-PRE-TOKEN-LEDGER for C) or dispatches C and D as separate parts with those edges. A and B need neither.

### A. A block's class names its clause
**Shape.** Next to the `VERDICT_CLASSES` literal (`web-fix-wave.js:175`), one object literal maps each taught class to `"<role>.md step N"` or `null` (`other`, `conflict`, any class no step enforces). `review_strength.py` reads it from the `--tree` text as `verdict_classes()` reads the list, never copied, and gains `--by clause`. [a-resolver] Only the step form is admitted: a clause resolves when `dev/governance/roles/<role>.md` exists and holds a line `^N\. `; anything else, a section name included, prints `UNRESOLVED <clause>`, a report row. An untaught word, a `null` and a merge verdict keep their own rows (the card's null control). Keyed on the class word, so the r10 window reads by clause with no re-review.
**Invariants.** `CLASSES_RE`, `policy_lint.mjs`'s `blockClasses`, `check-wave-script.mjs`'s `matchAll` and `agreement.mjs`'s identical-extractor entry still match only the list; the new literal's name does not match `const VERDICT_CLASSES = \[`. Every taught class has one key; the self-test asserts it and that a decoy literal is not read.
**Lost:** the clause in the verdict subject (three subject parsers change; the history carries no clause, so the card's window stays unread); a map typed in `review_strength.py` (a second copy, which its docstring forbids).

### B. Instance dates and rule yield, derived
**Shape.** `fold_ledger.py yield`:
- Instance date: committer time of the first first-parent commit of `--ref` whose `dev/audit/config/bugclasses.json` holds the instance string, from one `git log --reverse -p` walk. A `non_round_instances` row is dated by its own SHA.
- [R3] Rule date: the first add **following renames** (`git log --follow --diff-filter=A`, rename detection only, no copy detection), never the add at the current path. Measured at the base: for every file of `git ls-tree --name-only 824a016f75 dev/governance/rules/` the add at its path (bc0f17ddb6 for all of them) is later than the add under `--follow`, so the path date would count every instance between the two "before" a rule that existed.
- Rule to class: a new `rules` list on each class (empty is a value), resolved by `check` as `MISSING-PATH` through the existing path resolver. Measured: no class `barrier` names a `dev/governance/(rules|roles)/` path, so the fixer writes each link from the class's `rca` document, one cited line per link.
- Output: one row per rule: classes, instances before and after its date; `no-class` when no class names it, never 0 (a 0 feeds 0018's "remove").
**Lost:** a stored date per instance as the card words it: it changes the `R<n> <id>` grammar `check`'s UNPARSED rule enforces and every reader `git grep -l bugclasses.json -- '*.py' '*.mjs' '*.js' '*.sh'` lists (`tools/merge/ledger_merge.py`, `.claude/workflows/audit-find.js`, `.claude/workflows/audit-verify.js`, `tools/policy/agreement.mjs`, `tools/policy/check-wave-script.mjs`, `tests/entities.py`), and back-fills by hand. Derived, `check` reads the same before and after: the card's null control holds by construction.

### C. Session reads: loads, refusals with outcome, workflow runs
Measured in a designer transcript: a rule load is a line with `attachment.type` `nested_memory` and the `.claude/rules/<rule>.md` path (a Read under `dev/governance/` produced one; a Bash `sed` of the same file produced none); a Bash exit is a `tool_result` with `is_error: true` beginning `Exit code N`.
1. **Loads per rule:** `nested_memory` lines per path.
2. **[R2] Refusal, by the instrument's own marker, never one exit code.** Exit 2 is a refusal in `tools/pr/prepr.sh:1824` ("REFUSE pr-body"), `tools/pr/push.sh` and others, so an exit-code rule would read 0 refusals for the instruments that refuse most. A refusal is a run of a tracked file under `tools/` or `.claude/hooks/` whose result holds a line matching `^\s*REFUSE[DS]?\b` or `^\s*refusing\b`, at any exit code, or a PreToolUse hook denial. The refusing set is enumerated, not declared: `git grep -l -E '\bREFUSE' -- tools .claude/hooks` (the marker set). A file the reviewer's exit-2 enumerator returns outside the marker set prints in an `unmarked` scope row with its non-zero exits, and its yield reads `unread`, never 0; the fixer lists those files at the part's merge base and classifies each (usage-only: no row) in the body. No instrument is edited by this part. A call whose instrument is not the last simple command prints `masked`.
3. **Outcome** of each refusal, from the next run of the same instrument in the session: `fix` (it passes, with an Edit, Write or commit between); `override` (it or a following `git push` carries a token of one literal OVERRIDES list, seeded by `git grep -n -E "ALLOW_|--force|--no-verify" -- .claude/hooks tools/pr`); `nothing` otherwise.
4. **Workflow runs:** one line per Workflow call: script, UTC time, notified status.
[c-subagent] The iterator walks each session's subagent transcript files as well as the session file, and prints `subagent files read k` beside `sessions read n` (local and cloud apart); a seat class it cannot read prints `NO-READ`. A subagent's refusal is its own row, outcome read within its own file.
**Lost:** a PostToolUse logging hook (a standing cost on every Bash call; a second record of the transcript; dies with a cloud container); a subcommand inside the token ledger's file (couples C's hot file to that group's; the card needs a nameable path [paths]).

### D. A cause per red run, in P7's vocabulary
[R1] The record is `roster_lib.convergence_why` and `loop_ledger.py` at acf0b72578; D owns its change there after part 2 merges. A red is a run whose required set (gate.py's `REQUIRED`) failed, on a pull-request head or on main's push (card E11-GATE-REDS asks the same record). Its cause is a `caused_by.cause` word already admitted, derived from the clearing event (prototype `dev/audit/rounds/round11/evaluation/gate_reds.py` on eval/r11; fetched listings in, no API read in `loop_ledger.py`):
- the PR's own later commit cleared it: `#<that PR>`;
- red at the merge base on main too: `#<n>`, the PR merged at main's first red push run of that context after its last green (merge-subject parse); unparsed: `unread`;
- a re-run at the same head went green: `external`.
No new cause word; `original` is not used by a derived row. **The one vocabulary change:** `convergence_why`'s cause test becomes a function the derived row calls too, and the rca rule is settled as: a derived row carries no `rca`, is never written to the roster, and never feeds `injected` (which stays the written, rca-backed rows), so the root-cause seat still owns every cause that counts as injected. `found_by`: `ci-main` on main rows; absent on PR-head rows, since a pre-merge red is no escape and P7's `found_by` counts escapes.
**Product/machinery** is not re-defined by paths: the column is R11-PRE-TOOLCHAIN-PIN's gate.py function (design/R11-PRE-TOOLCHAIN-PIN a37706d599, section 2) on the run's listing; until it merges the column prints `unread`, and the failed job set prints as `machinery_line()` (`tools/ci/gate.py:293`) splits it today. `gate.py` is unchanged by D.
**Lost:** gate.py stamping a cause at run time (the clearing event does not exist yet; a guess and a second mechanism); four new cause words (a second vocabulary, R1).

## Evidence plan (`fixer.md` steps 2-4)
| part | failing test first: a planted event prints its row | null control | mutation target |
|---|---|---|---|
| A | fixture wave script mapping `harness` to `fix-review.md step 2`; a blocked verdict counts on that row | a merges-only window: clause rows 0 | the clause lookup in `stratum` |
| B | fixture history: a rule file added under one directory, then class `C` gains `R9 X-1`, then the rule moves into the rules directory: reads `after 1` (the path date would read `before 1`) | a linked rule with no later instance: `after 0` | the walk's comparison; the `--follow` flag |
| C | synthetic jsonl: one `nested_memory`; `prepr.sh --body-check` exit 2 with `REFUSE pr-body`, an edit, exit 0 (`fix`); one subagent file holding an exit-1 `REFUSE`; one Workflow call | none of these: 0 / 0 / 0, and an unmarked exit-2 tool reads `unread` | the marker match; the outcome classifier |
| D | fixture listings: red then green at one head is `external`; red cleared by the PR's commit is `#<pr>`; red inherited from main is main's PR | a green-only window: 0 reds; a success run carries no cause | the clearing-event match; the cause call into `convergence_why` |
No golden moves; neither claim file is touched.

## Hot files and serial position
- B and R11-PRE-SECURITY-PRIVACY (design ba8209b07f) both change `fold_ledger.py check`: serial, whichever merges first, the other rebases and re-runs steps 2-8. [b-hotfile]
- D and R11-PRE-ROUND-METRICS part 2 share `roster_lib.py` and `loop_ledger.py`: D after its merge. D and R11-PRE-TOOLCHAIN-PIN do not share a file.
- After A, re-run `dev/audit/harnesses/r10_review_strength_mutants.py`.
- Each new file enters `tests/closures.json` or `tests/closure.py`'s INERT list, and `.github/CODEOWNERS` as an enumerator.

## Notes for the fixer
- [paths] E11-N-INSTRUMENT-YIELD's `paths` becomes C's new file; E11-N-GATE-CAUSE's becomes `tools/audit/seat/roster_lib.py` and `tools/audit/seat/loop_ledger.py` in place of `tools/ci/gate.py`, plus C's file for the run line; each is written in the evaluation before the card is recorded merged. Carry: R11-PRE-NO-READ-BUILDERS
- Readers of the verdict literal: `git grep -l VERDICT_CLASSES -- tools tests .claude`; `check-wave-script.mjs`, `agreement.mjs` and `tests/entities.py` still pass with the second literal present. Carry: R11-PRE-NO-READ-BUILDERS
- Owed to R11-PRE-TOKEN-LEDGER: the per-session iteration is an importable function that also yields each session's subagent transcript files. Carry: R11-PRE-TOKEN-LEDGER
- Re-derive every count at the part's own merge base; the figures above name their commands only. Carry: R11-PRE-NO-READ-BUILDERS
