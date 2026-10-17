_Requested by **tvofi**_

The friction counter keyed recurrence on exact keys, so one recurring friction split across sibling rows that no single id reaches on its own. Measured in the since-v6.7.14 window at origin/main `1913f0dd7` (v6.7.16): mutation 2, mutation-vacuous 1, mutation-survivor 1 — the family composes 4 distinct pull requests, over the threshold of 3, while every exact id sits below it and the counter prints no would-open for it. That is the hole #1825 names: the counter opens nothing while the class recurs. The same fragmentation hid a second family, environment / seat-environment — and the widest sweep shows that one lives in the OTHER histogram: there is no `environment` verdict row anywhere in the four tag windows; `environment` reads 4/5 and `seat-environment` 1/1 as FRICTION RULE IDS. A fold over verdict classes only would declare a family that can never fire.

The fix is one declaration beside `FRICTION_THRESHOLD` — `FRICTION_FAMILIES` (mutation: [mutation, mutation-vacuous, mutation-survivor]; environment: [environment, seat-environment]) — folded over BOTH maps. Family rows are additive beside the unchanged exact-id rows (human table and CENSUS, kinds `verdict family` / `friction family`, key `<name> (family)`, counted into the CENSUS summary so the filer's summary-count invariant holds); the family would-open fires once per family per map, on the distinct-PR union of its members. Exact-id rows and CENSUS id lines are the raw record `friction_issues.mjs` re-measures and stay byte-identical.

Alternatives considered (fixer.md step 17): teaching `VERDICT_CLASSES` the sibling words — rejected, it moves the reviewer prompt's vocabulary and folds nothing already keyed under the old words; collapsing sibling keys at parse time — rejected, it edits the raw record the filer re-measures and loses resolution. The additive row keeps the record and restores the threshold's sight.

## Head

c2cdbd778ded9750cb85929b2b25706ea5a1c17e (branch `fix/r9-fr-3`, cut from origin/main `1913f0dd7`). Every figure below is measured at this head; the `--stats` figures are functions of origin/main's tip and were taken with origin/main at `1913f0dd7`, 2026-10-04T10:24Z — they are re-taken after any merge from main.

Re-cut disclosure: the earlier head `08609dc36` carried the seat's resume note under `handoff/`, which `prepr.sh`'s transport step refuses in the code head's ancestry, so the head was re-cut to `08609dc36`'s code content without the `handoff/` file — `git diff 08609dc36 c2cdbd778` reads one deletion, `handoff/round9/fix/resume/FR-3.md`, which rides the orphan body ref as RESUME.md instead. The `--stats` window figures were measured on the tree at `08609dc36`, whose three code files are byte-identical to this head; the local acceptance figures were re-run at this head.

## Mutation proof

Two mutants, each run with `node .claude/workflows/policy_lint.mjs` and then restored:

1. Both family arms emptied (`for (const fam of statsFamilies(hist))` → `for (const fam of [])`): rc=1 with the three family pins red — `FIXTURE VACUOUS: the family fold did not fire exactly one 'mutation (family)' would-open...`, `FIXTURE VACUOUS: the id half of the fold did not fire exactly one 'environment (family)' would-open...`, `FIXTURE VACUOUS: with one member over threshold the family line did not fire exactly once...`. This mutant is also the failing-first demonstration: the acceptance pins were run against the tree before the production arm existed and printed the same first two lines (plus a ReferenceError on the then-unnamed `statsFamilies` for the pins that could not yet run).
2. The distinct-PR union replaced by a first-member count (`for (const p of c.prs) cell.prs.add(p)` deleted): rc=1, same three pins red — the union pin reads the shared pull request once and this mutant makes the controls window read 4 where the fixture pins 3.

Restored both times: rc=0, `FIXTURE ok: 92 error(s) hold 238 pins across 12 check classes`.

`python3 tests/mutation_table.py --scope changed` prints `no production code line added or modified against the base ... MUTATION TABLE PASSED (empty scope)`: the diff touches no production code, so there are no survivor sites to list on the touched lines, and the stress runs stay with CI's required mutation check.

## Null control

- Fixture-level, pinned in the acceptance so they re-run on every gate: the controls window fires the family exactly once on the union (3, the shared pull request counted once) with the exact-id line beside it, not one line per member; families whose members all sit below threshold (environment + seat-environment at 2, on both kinds) print no family line; the two pre-existing fixture windows carry no family member and the family code must contribute nothing there (`statsFamilies` on both maps returns [] — the pins above stay byte-anchored); no declared family contains the passing verdict.
- Real-window controls, base vs head, all four tag windows: since v6.7.16 (no family hits at all) the WHOLE stats output is byte-identical; since v6.7.14 and v6.7.15 the exact-id table rows and every `CENSUS\tverdict class` / `CENSUS\tfriction rule id` line are identical, the diff being only additive family lines and the CENSUS summary count; since v6.7.15 (family present at 2, below threshold) prints `WOULD OPEN: 0 issue(s)` at the head as at the base.

## Figures

- F1. The measured hole opens at the head and was quiet at the base. Command, at origin/main `1913f0dd7` checked out: `GITHUB_TOKEN=$(gh auth token) node .claude/workflows/policy_lint.mjs --stats --since v6.7.14` — mutation 2/2, mutation-survivor 1/2, mutation-vacuous 1/1, no family line anywhere, `WOULD OPEN: 5 issue(s)`, none naming mutation.
- F2. The same command at this head: `     4 / 5     mutation (family)   <- at or over threshold`, `CENSUS	verdict family	4	5	mutation (family)`, and exactly one new would-open — `would open "[policy] recurring friction: mutation (family)" -- verdict family at 4 in this window, threshold 3` — over the same 5 base lines; `WOULD OPEN: 6 issue(s)`. The 26-merge window's union rule: distinct PRs across the three sibling classes, 2+1+1 disjoint here.
- F3. The id half fires where the verdict fold cannot see it. `GITHUB_TOKEN=$(gh auth token) node .claude/workflows/policy_lint.mjs --stats --since v6.7.13` at this head: `     5 / 6     environment (family)   <- at or over threshold` and one would-open `-- friction family at 5 in this window` beside `mutation (family)` at 6/7. The family rule: environment 4/5 + seat-environment 1/1 as friction rule ids, 5 distinct PRs across them.
- F4. Byte-identity of the raw record. `diff <(grep -E '^CENSUS	verdict class|^CENSUS	friction rule id' BASE) <(grep -E '^CENSUS	verdict class|^CENSUS	friction rule id' HEAD) && echo IDENTICAL` over since v6.7.14 and since v6.7.15 prints `IDENTICAL` for both; the same for the exact-id table rows. Over since v6.7.16 the whole output diffs empty.
- F5. Consumer takes the new shape unchanged. `node .claude/workflows/friction_issues.mjs --self-test` → `100 passed, 0 failed`; `node tools/audit/harnesses/r9_fr3_family_consumer.mjs` → 5 ok lines, exit 0: parseHistogram accepts the family-shaped histogram, census rows parsed = declared, both family would-open lines parse to key/kind/count/threshold, and its control arm proves a producer that prints a family row without counting it refuses (`declares 5 key(s) and 7 row(s) parsed`).
- F6. Acceptance and gate. `node .claude/workflows/policy_lint.mjs` → `FIXTURE ok: 92 error(s) hold 238 pins across 12 check classes`; the scoped gate at this head is `MODE: SCOPED -- 1 script(s) run` naming `tests/entities.py` → ALL 2137 ENTITY CHECKS PASSED (`PYTHONPATH=tests/hastub`, seat venv); `python3 tests/structure.py` → STRUCTURE RATCHET PASSED; `node .claude/workflows/friction_issues.mjs --self-test` → `100 passed, 0 failed`.
- F7. The class's seams, enumerated and dispositioned (the rule that enumerates them is the widest sweep itself: every row the since-v6.7.13 run returns must carry a disposition). Verdict rows (24): merge — the passing verdict, withheld from its own row; mutation, mutation-vacuous, mutation-survivor — the family folded here; root-cause-unanswered, head-moved, harness — own keys, each already over threshold in its own right, printed unchanged; defect, body, evidence, vacuous-check, instrument, class-open, other, claims, closures-under-scoped, closures, contract, ci-red, null-control, honesty, security, provenance, barrier — own keys, all at or below 2 in every tag window, no measured sibling pattern. Friction-id rows (19): environment, seat-environment — the family folded here; gate-scoping.md, fixer.md, ci-autofix.md, writing-for-agents.md, fixer, defect-root-cause.md, SEAT-COMMON-worktree, CLAUDE.md, structure-ratchet, fixer_step3, ratchet-budgets.md, fixer.step3, ci-autofix.closures, resume.note_file, fixer.step6, fix-review, codeowners_gap — own keys, unchanged. No seam is left un-dispositioned; `closures` / `closures-under-scoped` look like a candidate pair but sit at 1/1 in every window, so no family is declared — the declaration rule requires a measured hole.

## Red checks

none. No check has gone red on any commit of this branch (CI runs when the pull request opens). nightly-status and delivery-status grade main: this diff touches none of what they read (their scripts, `tests.yml`, `governance.yml`, the plan, `HANDOVER.md`, and no row they grade), so per `.claude/rules/defect-root-cause.md` no answer is owed here — nightly-status is expected-red/skipped on a branch lane as a function of main's own state, and its red, if one lands, is the orchestrator's on main, not this branch's.

## Forward-carry

none. No later stage must change how it works: the filer's trigger text and census contract are unchanged (F5), the family key `<name> (family)` is distinct from every id row so exact-title matching cannot collide, and the reviewer contracts need no edit — the family declaration lives in the one classifier, `policy_lint.mjs`.

## Friction

- `.claude/workflows/friction_issues.mjs`: `cost`: no `import.meta` guard on its entry — `run(argv)` executes on import, so driving the exported `parseHistogram` offline needs an entry-stripped copy, and the filer's own `--dry-run` reads the live repository, leaving no offline drive of the consumer without that workaround. `tools/audit/harnesses/r9_fr3_family_consumer.mjs` carries the one declarative strip and refuses if the dispatch line moves.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
