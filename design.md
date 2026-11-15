# Design: R11-PRE-NO-READ-BUILDERS (size L, decision 0014)

- Base (code read at): 31117b1029de63938d949e78dcbcd8f9451e5e33 (`origin/main`).
- Predecessor R11-PRE-MACHINERY-LIMITER handoff head: 3ad61a1f6e (PR #3627, open). It moves nothing this note relies on. Its "one in, one out" clause (`dev/governance/rules/ratchet-budgets.md`, the machinery section) binds every part: **no part adds a required check.** Every read below is a report-only enumerator, and each self-test arm goes into the instrument's existing `--self-test`.
- Cards, re-read at the eval/r11 tip c6ce415b77, whose `review.verdict` is `approve` (round 3, at 02a48db212): E11-N-ROLE-CLAUSE, E11-N-RULE-YIELD, E11-N-INSTRUMENT-YIELD and E11-N-GATE-CAUSE are each `decision: accepted`, ruled ("Build all four reads"), and `gates_finders: false`. No card is dropped or unruled, so nothing is held back.
- Finder harness: none. These are owner-directed instrument cards, so the evidence is each card's `null_control` field at c6ce415b77.

## Parts, by owning seam (four PRs, one concern each)

| part | card | owning module | callers / readers | after |
|---|---|---|---|---|
| A | ROLE-CLAUSE | `.claude/workflows/web-fix-wave.js` (owns the vocabulary) | `tools/audit/seat/review_strength.py` | the limiter |
| B | RULE-YIELD, instance dates and yield | `tools/audit/fold_ledger.py` | (none new) | the limiter |
| C | RULE-YIELD load count; INSTRUMENT-YIELD; GATE-CAUSE's workflow run line | the session-transcript reader R11-PRE-TOKEN-LEDGER lands | a new subcommand beside it | R11-PRE-TOKEN-LEDGER |
| D | GATE-CAUSE, a cause per red run | card P7's cause record (R11-PRE-ROUND-METRICS) | `tools/ci/gate.py` is **unchanged** | the R11-PRE-ROUND-METRICS part that builds P7 |

C and D each sit behind a group outside this roster's `after` edges. I could split the concern there instead (a second transcript reader, a second cause record), but the brief refuses a second mechanism, so the edges are added instead. The orchestrator adds `R11-PRE-TOKEN-LEDGER` and `R11-PRE-ROUND-METRICS` to this group's `after`, or dispatches C and D as separate parts.

### A. A block's class names its clause
**Shape.** Next to the `VERDICT_CLASSES` literal, `web-fix-wave.js` gains one object literal that maps each taught class to the contract clause it enforces: `"fix-review.md step N"`, or a role file plus a section, or `null` where no clause exists (for example `other` and `conflict`). `review_strength.py` reads that literal the way its `verdict_classes()` reads the class list: from the `--tree` text, never copied. It gains a `--by clause` stratum.
- An untaught word, a `null` and a merge verdict each keep their own row. This is the card's null control.
- A clause string that does not resolve prints `UNRESOLVED <clause>`. It resolves when the file exists under `dev/governance/roles/` and holds a line `^N\. `. This is a report row, not a refusal.
- Because the map is keyed on the class word, it applies to past verdicts too. The r10 window then reads by clause with no re-review.

**Invariants.**
- The regex `CLASSES_RE` and `policy_lint.mjs:blockClasses` still match only `VERDICT_CLASSES`. The new literal's name must not match `const VERDICT_CLASSES = \[`.
- Every taught class has exactly one key. The self-test asserts this, and also that a decoy literal is not read.

**Alternatives that lost.**
- The reviewer writes the clause in the verdict subject. This lost because the subject grammar has three parsers (parseVerdict, `blockClasses`, `review_strength.py`) and the history carries no clause. The card's 2537-verdict window would stay unread.
- A map typed inside `review_strength.py`. This lost because it would be a second copy of the vocabulary, which that file's docstring forbids ("never copied here").

### B. Instance dates and rule yield, derived and never stored
**Shape.** `fold_ledger.py` gains a `yield` subcommand.
- **Instance date:** the committer time of the first commit, on the first-parent history of `--ref`, whose version of `dev/audit/config/bugclasses.json` contains the instance string. It is computed in one `git log --reverse -p` walk of that file. A `non_round_instances` row is dated by its own SHA.
- **Rule merge date:** the first commit that adds the rule's file.
- **Rule → class link:** a new `rules` list on each class (rule paths; empty is a value). `check` gains a `MISSING-PATH` resolution of this field, which reuses the existing path resolver.
- **Output:** one row per rule: classes, instances before and after the merge, and `no-class` when no class names the rule. `no-class` is never printed as 0, because a 0 would feed 0018's "remove" verdict.

**Measured at the base:** no class `barrier` names a rule or role path (a `json.dumps` scan of `barrier` for `dev/governance/(rules|roles)/`), so the link must be written. The fixer fills it from each class's `rca` document and cites one line per mapping.

**Alternative that lost:** a stored date per instance, as the card words it. It changes the `R<n> <id>` instance grammar that `check`'s UNPARSED rule enforces. That grammar is read by every reader `git grep -l bugclasses.json -- '*.py' '*.mjs' '*.js' '*.sh'` lists outside the dated round folders: `tools/merge/ledger_merge.py`, `.claude/workflows/audit-find.js`, `.claude/workflows/audit-verify.js`, `tools/policy/agreement.mjs`, `tools/policy/check-wave-script.mjs` and `tests/entities.py`. It would also mean back-filling every instance by hand, against the file's own rule ("derived, never carried"). Under derivation, the card's null control holds by construction: `check` reads the same before and after.

### C. Session reads: rule loads, refusals with their outcome, workflow runs
Measured in this seat's own transcript:
- A rule load is a line whose `attachment.type` is `nested_memory` and whose `path` is the `.claude/rules/<rule>.md` file. A Read of `dev/governance/roles/design-review.md` produced one for `brief-citations.md`. A Bash `sed` of the same tree produced none.
- A Bash command that exits non-zero gives a `tool_result` with `is_error: true` whose content begins `Exit code N`. A planted `exit 1` showed this.

The part therefore reads, through the token ledger's per-session iterator (no second transcript walk), three things:
1. **Loads per rule:** a count of `nested_memory` lines per path.
2. **Refusals:** a Bash call whose **last** simple command runs a tracked file under `tools/` or `.claude/hooks/` and exits with a code other than 0 or 2. Code 2 is the usage error by this repository's convention and prints its own `usage` row. A call where the instrument is not last prints a `masked` row: its exit code was not observed. A PreToolUse hook denial is a refusal by that hook.
3. **Outcome of each refusal,** decided by the next run of the same instrument in the same session:
   - `fix`: the next run passes and an Edit, Write or commit came in between.
   - `override`: the next run, or a following `git push`, carries a token from one literal OVERRIDES list. The list starts with the bypass variables and flags the fixer enumerates with `git grep -n -E "ALLOW_|--force|--no-verify" -- .claude/hooks tools/pr`.
   - `nothing`: neither of the above.
4. **Workflow runs:** one line per Workflow call, giving the script, the UTC time and the notified status.

Scope line: sessions read, local and cloud apart. A seat class the ledger cannot read prints `NO-READ`, never a partial (0018 section 2).

**Alternative that lost:** a PostToolUse logging hook. It adds seconds to every Bash call of every session (a standing cost). It would also be a second record of what the transcript already holds, and its log dies with a cloud container.

### D. A cause per red run, in P7's record
A red gate run on a pull-request head gets a cause derived from the event that cleared it, using the Actions API and git (prototype: `gate_reds.py` on eval/r11):
- `inherited`: the same context was red on main at the merge base.
- `external`: a re-run at the same head went green.
- `product`: the clearing commit's diff touches `custom_components/` or `blueprints/`.
- `machinery`: anything else.

A red that got a hotfix group takes that group's P7 `caused_by` and `found_by` by a join, never re-derived. The rows are added to P7's enumerator as a second subject kind. There is one record and one vocabulary.

`gate.py` stays unchanged. It runs before the clearing event exists, so it cannot know the cause, which is the gap 0018 section 3 names.

**Alternative that lost:** gate.py stamps a cause at run time. That cause would be a guess, and it would be a second mechanism.

## Evidence plan (`fixer.md` steps 2–4, per part)
| part | failing test first (planted event prints its row) | null control (no event prints 0) | mutation target |
|---|---|---|---|
| A | fixture wave script with `harness → fix-review.md step 2`; a blocked verdict shows on the `fix-review.md step 2` row | a window of merges only gives clause rows of 0 | the clause lookup in `stratum` |
| B | fixture history adds `R9 X-1` to class `C` after rule `r.md`'s add commit; output `after 1` | a rule linked to a class with no later instance gives `after 0` | the first-seen walk's comparison |
| C | synthetic jsonl: one `nested_memory`, one exit 1 → edit → exit 0, one Workflow call; output load 1, refusal 1 `fix`, run 1 | a transcript with none gives 0 / 0 / 0 | the outcome classifier |
| D | fixture runs: red then green at the same head gives `external`; red then a product commit gives `product` | a green-only window gives 0 reds | the clearing-event match |

No golden moves. Neither claim file is touched.

## Hot files and serial order
- A and B: no shared file, so either order.
- `review_strength.py` is also read by `dev/audit/harnesses/r10_review_strength_mutants.py`. Re-run that harness after A.
- Each part enters `tests/closures.json` or `tests/closure.py`'s INERT list, and is added to `.github/CODEOWNERS` as an enumerator (the R11-PRE-ROUND-METRICS carry, item 0df1ac6e).
- Each part is a non-production merge under the target in `dev/governance/config/machinery_target_budgets.json` (at the limiter head 3ad61a1f6e).

## Notes for the fixer
- Sibling readers of the verdict literal: run `git grep -l VERDICT_CLASSES -- tools tests .claude`, and confirm that `check-wave-script.mjs`, `agreement.mjs` and `tests/entities.py` still pass with the new literal present. Carry: R11-PRE-NO-READ-BUILDERS
- Owed to R11-PRE-TOKEN-LEDGER: expose the per-session transcript iteration as an importable function, not inline in the daily job, so part C reads the same walk. The orchestrator routes this to that group's brief. Carry: R11-PRE-TOKEN-LEDGER
- Owed to R11-PRE-ROUND-METRICS: P7's record keys a row by subject (a group, or a red run), with `caused_by` admitting `inherited`/`external`, so part D adds a source and not a record. Carry: R11-PRE-ROUND-METRICS
- Re-derive every count at the part's own merge base. The figures above name their commands only.
