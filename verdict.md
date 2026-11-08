Fix review: merge 91491a63fdc8fbe2e7b9df6e3bcdd234dd9f20be

bus-nonce: 17d5132cf1b0fcf089241370cd1cf840

## Round

Review round 4 of PR 3310 by the dispatch record: blocks at acd78b4d in rounds 1 and 2, and at 2684306f in round 3 (comment 6721196982), which the commits up to 42c0ebbb repair. This verdict is merge, so no re-cut is owed. Reviewed from a detached worktree at 91491a63fdc8fbe2e7b9df6e3bcdd234dd9f20be; merge base 8a4cf2618c53a6dca6b65df3eae5efc8832d1796; diff read three-dot (ev/three-dot.diff). `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the fix-review contract at the head is the current one.

## Evidence

- Owner correction (bar only for instrument and machinery): proposal-triage.md lines 15-20 (ev/proposal-triage.head.md) read "Repair of such code (outside `custom_components/`) with roster `severity` `low` or `normal` meets both (over 20% to add)". Only instrument/machinery, CI-lane or seat code takes the bar; no sentence lets a product defect (custom_components/) take it at any severity. The skip list keeps `medium`, `high`, `major`, `critical`, root-cause countermeasure, closeout and owner directive, so the RCA and owner-directive exemptions are not dropped. The mapping is written once and covers every severity value on the roster: at handoff/audit-r10-roster FETCH_HEAD (392 groups) the values are medium 206, high 90, low 56, unset 24, critical 8, normal 7, major 1; each named value appears once, and unset is "classified first, never assumed major".
- Round-2 obligations restored within the cap with no raise: DEFER "or the owning group", "Even or marginal: REJECT", "never assumed major", the Proposals line, medium effort and rulings checked against code, the per-instance rule run, git before the API, the `Cost:` estimate with its `--budgets` row, cite-don't-carry, and the proposal-sourced text definition are all in the head text. `node tools/policy/policy_lint.mjs --budgets`: `dev/governance/roles/proposal-triage.md 36 36 489 489` (at cap, not over); `policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`. No `*_budgets.json` is in the diff.
- `node tools/policy/rules_sync.mjs --check`: `RULES-SYNC ok`. The .claude and .cursor copies of ratchet-budgets.md change only the same line as their source.
- Mutation proof, run by me: `THRESHOLD = Fraction(1, 10)` gives `FAIL exemption: exactly 20% refuses`, `FAIL exemption: exactly 20% as floats refuses`, `54 checks, 2 failed`. An extra mutant, `Fraction(1, 4)`, gives 3 failed (the 21% passes and the positive control fail). After restoring: `machinery_ratchet self-test: 54 checks, 0 failed` (ev/checks.txt).
- Class sweep, run by me: `git grep` at the head over dev/governance, tools, .claude, .github, CLAUDE.md, AGENTS.md and HANDOVER.md for `10%`, `5%`, `>10`, `1/10`, one tenth, percent and per cent in an improvement, exemption, triage or keep sense. The only bar figure left is the new 10% keep test (proposal-triage.md:17). The other hits are unrelated (cloud_relay.sh printf fields, a vendored minified JS). I re-derived the body's "left alone" set (rate-limit floors, D0 and docs figures) by excluding it rather than item by item.
- Figures re-derived: roster at 9fd3d6a2 has 388 groups (high 90, low 56, medium 202, critical 8, normal 7, major 1, unset 24), as the body says. `tests/closure.py select --diff <mb>`: `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`. `tests/structure.py`: `STRUCTURE RATCHET PASSED`. I did not re-derive the entities figure (4 of 2666 failing locally, identical at main). My local run hit its 220 s timeout (ev/entities.txt), so CI's green `fast` and `gate` runs are the authority for it.
- VERSION, the manifest and RELEASE_NOTES are untouched. No claim file is in the diff.
- Merge: `git merge-tree --write-tree origin/main 91491a63` exits 0 (tree 27e34a98, origin/main 996ded2a). Re-run after main moved to 17e621f0: exits 0 again (tree 5e280e01). No conflict either time. The branch head was still 91491a63 at `git ls-remote` before the push.
- CI: `python3 tools/audit/seat/merge_train.py classify 91491a63fdc8fbe2e7b9df6e3bcdd234dd9f20be --pr 3310` printed `GREEN 91491a63fdc8fbe2e7b9df6e3bcdd234dd9f20be pending: none red: none`, rc=0 (ev/classify.txt). The packet digest has every gate job success or skipped. The earlier `gate` red at 2684306f (rate-limited) is answered in the body's Red checks section.
- Head: the body names 91491a63fdc8fbe2e7b9df6e3bcdd234dd9f20be, the head measured here.
- Finder's harness: this is a policy group with no finder harness. Its checks are the self-test, the policy lint and the class grep, all run by me as listed above. I built no instrument.

## Findings

- Follow-up (clarity, not blocking): the keep test says "a measured gain of at least 10% on them". "Them" has no explicit antecedent among the four ratchet-budgets.md measures and can be misread as the group or lane. The red-check carry named in the opening ("see below") is not in the Machinery skip list, so whether a low-severity machinery red-check carry takes the bar is left to the reader. The group brief exempts only root-cause countermeasures, so the text is consistent with the ruling. A later trim could name the measures.
  Carry: dismissed: wording within the 489-token cap; consistent with the owner ruling and the orchestrator-approved mapping, no seat duty differs

## Friction

none
