Fix review: merge 4e47ee583efdf8f066dfc5739a7db1131c2d2137

bus-nonce: 270530cdcf84e052c18067ef45c278d4

## Evidence

- Round: third review of this group (blocked at 11a6c579bb8e354b4f76209b1b4c472ddfee5c19 and at 9d3da28204b0683981252bff8651c19b8f89f3f7, class evidence-cut both times). This is a delta round under fix-review.md step 12. The delta is `git diff 11a6c579bb8e354b4f76209b1b4c472ddfee5c19 4e47ee583efdf8f066dfc5739a7db1131c2d2137`: policy prose, `dev/programme/plan-2026-09-open-issues.md`, and main's `ci: record nightly kills` files brought in by merge b0fa74f68b. It has no `custom_components/` change, so the scope does not widen. Measured head: 4e47ee583efdf8f066dfc5739a7db1131c2d2137 (`ev/HEAD.txt`). The body's `## Head` names the same SHA.
- No pull request exists yet, so there is no review packet and no CI run to read. The red-check step has nothing to answer, and the body's `## Red checks: none` is consistent with that. `merge_train.py owed-reds` prints the owed set (`ev/owed-reds.txt`, tail shown).
- Check 1, sole-copy cuts, by enumeration over the whole diff 8c10361eb1fea539dc5acb8f7442eac2810faa47..head (merge base unchanged):
  - The fixer's enumerator, re-run from the body's script, prints `SOLE-COPY: 77 of 3478` at the head and `75 of 912` at 9d3da282, as the body says (`ev/theirs.txt`).
  - My own enumerator is built differently (`ev/cutenum.py`). It splits every `-` line of `git diff -U0` at sentence and clause punctuation and checks each fragment of 3 or more words against each tracked file at the head separately. It finds `141 gone of 230 removed fragments` (`ev/mine.txt`). Every one of those 141 maps into one of the fixer's 77 units (`ev/xmap.py`: `unmapped 0`). No removed fragment escapes the body's list.
  - The body's dispositions cover all 77 numbers.
  - I read each unit against its head text in the word diffs of `CLAUDE.md`, the five contracts and `dev/audit/README.md`.
  - Every claimed other copy exists at the head:
    - four-issues sentence: plan file, line 2096
    - "absorbs thirty-one numbers while naming eight": plan file
    - "using the instrument it accuses": plan file
    - "bar is a stall": `dev/audit/rounds/round4/quiet-window.md`
    - "not inside an iteration": `dev/governance/dimensions/D9.md`
    - the direct-run half of the stress.py rule: `.claude/skills/steward/SKILL.md`
    - why second-thread CPU misses the ratio (process_time, not thread_time): `dev/audit/rounds/round4/D9/verify-0-1.md`
    - `digest/jobs`: `tools/audit/seat/instruments/beat_jobs.py.md`
    - Proposals: `tools/audit/seat/sweep_template.md`
    - `rounds.py --stats`: `dev/audit/rca/R10-RCA-FRICTION-RESIDUE.md`
    - `../setup-qa/`: `tests/README.md:431` and `tests/closure.py:427`
    - "holdouts named": `.claude/workflows/audit-plan.js`
  - The restored items are present in README.head: the instrument window; "not a tree value"; K9 context; v6.3.18 and first-parent; `HARNESSES.md` at `d5d8c4a`, "final at that commit only" (wrapped at README lines 296-297).
  - The rewordings I read keep every fact, or drop only a restatement whose rule survives in the same file. The corrected count is real: `optimizer.py` has three `sleep(0.002)` calls, at lines 1256, 1360 and 5275.
  - Result: none of the 77 units is cut without a disposition. The evidence-cut class is closed at this head.
- Check 2, owner correction of 2026-11-12 on `nudge.md`:
  - Run over every file this PR edits at the head, `git grep -n -i nudge` returns two hits:
    - `CLAUDE.md:113`: "Cursor turn `nudge.md`"
    - `tools/audit/seat/roster_edit.py:1423`: a comment
  - The contracts `fixer.md`, `orchestrator.md`, `architect-planner.md`, `plan-review.md` and `proposal-triage.md` no longer cite it.
  - No text presents `nudge.md` as binding every orchestrator session. The `CLAUDE.md` row scopes it to Cursor.
  - The departure from carry 44's "delete the turn clause" is forced by the tree, which I reproduced. Deleting the clause at the head makes `node tools/policy/policy_lint.mjs` print `ERROR [index] CLAUDE.md: does not name tools/audit/briefs/nudge.md` and `TOTAL: 1 error(s)`. The head prints `TOTAL: 0 error(s) across 51 policy file(s)`.
  - R10-NUDGE-RETIRE's roster brief (handoff/audit-r10-roster d15fb174b6f5) already owns any citation in `CLAUDE.md`, `orchestrator.md` or `fixer.md` that remains at its merge base. It also lists `tools/audit/seat/roster_edit.py` among its files.
- Mutation proof, re-run at the head. With `LOG` removed from `VERDICT_LINE_RE`, `roster_edit self-test: 281 checks, 1 failed`, and the failing check is `FAIL triage gate: a LOG ruling is refused as LOG, never routed (got: )`. Restored: `281 checks, 0 failed` (`ev/mutation.txt`).
- Figures re-taken at the head (`ev/checks.txt`):
  - `policy_lint.mjs --budgets` rows match the body. README 315/321, 6056/6059; `CLAUDE.md` 214/221, 3605/3605; `fixer.md` 315/315, 5210/5216; `orchestrator.md` 293/295, 4231/4251; `architect-planner.md` 84/85, 1261/1261; `plan-review.md` 24/24, 304/304; `proposal-triage.md` 36/36, 488/489; `D13.md` 79/79, 1149/1149; `D11.md` 99/103, 1494/1499. No cap is raised.
  - `brief_lint.mjs` rc 0. The only errors it prints are its fixtures', and it prints `PLAYBOOK ok: the renamed fixture is refused for its 7 moved instruments and the null fixture lints clean`.
  - `RULES-SYNC ok`; `STRUCTURE RATCHET PASSED`.
  - `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
  - `tests/doc_claims.py`: `ALL 343 checks PASSED`.
  - `env -u BASH_ENV PYTHONPATH=tests/hastub python3 tests/entities.py`: `ALL 2709 ENTITY CHECKS PASSED`, rc=0 (`ev/entities.log`).
- Not re-taken: the body's cap null control with the two payment cuts put back (6111/6059). The byte counts are re-derivable but I did not re-derive them. Neither changes this verdict.
- Merge with main: `git merge-tree --write-tree origin/main 4e47ee58` exits 0 with origin/main at a18e2e9d00b1 (`ev/mergetree.txt`). `VERSION`, the manifest and `RELEASE_NOTES.md` are untouched.
- Policy: `CLAUDE.md`, `dev/audit/README.md` and five contracts change, so this merges only on tvofi's approving review at its head. The body's two Approval questions (10% vs 20%; the carry 31 raise) are the owner's. This verdict does not stand in for that review.

## Findings

- Follow-up: `CLAUDE.md:113` keeps "Cursor turn `nudge.md`" because `policy_lint`'s index rule refuses an unnamed policy file. "Cursor" is looser than the file's own scope, "the Cursor orchestrators on grok and qwen". `nudge.md`'s line 3, "This file is the turn that contract names", is now false, because `orchestrator.md` no longer names it. Both go when the file is retired. Carry: R10-NUDGE-RETIRE
- Follow-up: the comment at `tools/audit/seat/roster_edit.py:1423` ("nudge.md and sweep_template.md run them by hand") is a file this PR edits and still names `nudge.md`. It is not a contract, and carry 44's three items do not list it. The file is in R10-NUDGE-RETIRE's files. Carry: R10-NUDGE-RETIRE
- Residual: `dev/governance/dimensions/D9.md` lines 60-62 still say "The two existing `sleep(0.002)` yields", but `optimizer.py` has three at the head. Carry: dismissed: pre-existing at the merge base and outside this diff; it is the owner's dimension brief, and the README this PR edits now says to grep the calls, never count them
- Residual: several body dispositions are labelled loosely. Units 36, 41, 45 and 46 are called "restored" but are reworded (their content is present at the head), and the 65-67 line says "61" where it means 65. No fact is lost. Carry: dismissed: body wording only, and every unit's content is verified present above
