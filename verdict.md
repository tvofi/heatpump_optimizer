Fix review: blocked 3ad61a1f6e09044cd47db34952a3ab681db1b1e5 mutation-survivors: six mutants of lines this PR adds survive their self-tests, three on the target rule's own terms (band, merge count, PR-mode tip)

bus-nonce: 78003b214e8a8eb5511d93290f00e3be

Round: first (no earlier verdict on #3627).

## Block

Every mutant the body names is killed at this head; that part of step 1 holds. Six more mutants of production lines this PR adds survive their self-tests (`ev/mutants.txt`, driver `ev/mut.py`). The body's `## Unpinned sites` says its six survivors are "none in a production line". That is true of its own driver's sample (`ev/mutant_run.txt`, re-run: the same six fixture survivors), but not of these lines. Three of them are terms of THE TARGET as the docstring and body state it, so nothing tests the rule as written:

- `tools/audit/machinery_ratchet.py:429` `past = m[c] > t + doc[c + BAND_SUFFIX]` -> `past = m[c] > t` SURVIVES (68 checks, 0 failed). The body and docstring say "compared against target plus nonproduction_merges' band", but every fixture uses band 0.
- `tools/audit/machinery_ratchet.py:358` `if len(line.split()) == 3` -> `>= 2` SURVIVES. The rule counts first-parent *merges*, and main's first-parent history holds non-merge commits: 88 in the newest 1500 (the stamps, e.g. 13cbe48de4 `v10.0.0: stamp Round 10 closeout`). With this mutant the stamps would speed up the decline, and the fixture has no non-merge first-parent commit to catch it.
- `tools/audit/machinery_ratchet.py:426` `scheduled_target(repo, base or head, ...)` -> `scheduled_target(repo, head, ...)` SURVIVES. In PR mode CI passes the PR head sha (`governance.yml` `MACHINERY_HEAD`). A real head's first-parent chain runs through branch commits and merges of main into the branch (this PR's b569a6120604 is one), not main's merges. The fixture's candidate is one side commit off the base, so it cannot tell the two apart. Measured at this head: `--measure --head HEAD` prints `merges_past_anchor 1`, which is the branch's own merge of main, while `--check --base 66865be375` reads 7 merges past the anchor.
- `tools/audit/machinery_ratchet.py:359` `max(0, ...)` removed SURVIVES. "never below 0" is unpinned. Without it, a target past zero refuses every non-production candidate, band or not.
- `tools/audit/seat/pr_cap.py:228` `and v > PRODUCTION_SLOTS` removed SURVIVES. A slots value at or below 10 would then read as a negative machinery allowance, not as unreadable.
- `tools/audit/seat/pr_cap.py:473` `if rc == 0 and slug is not None:` -> `if False:` SURVIVES. The `dispatch-gate --machinery` CLI wiring, which is Carry 4's gate, is never exercised. Only `machinery_gate` and `read_classes` are tested as functions.

Each needs one fixture case: band > 0 at the boundary; a non-merge commit on the first-parent chain past the anchor; a PR-mode candidate whose head carries a merge of main; a schedule driven past zero; slots <= PRODUCTION_SLOTS; and one `main(["dispatch-gate", ..., "--machinery", ...])` call with an injected `read_classes`.

## Findings

- Note: figure: the body's `## Figures` gives "at the head `target` 478, `merges_past_anchor` 0" for `--measure --head origin/main`. That command reads the target file at origin/main, which has none, so it prints no target. At this head, `--measure --head HEAD` prints `target 478, merges_past_anchor 1`. Paperwork only. Carry: R11-PRE-MACHINERY-LIMITER
- Note: red-checks: the body answers `budget-raise-gate` under `## Red checks` by its short name. review_packet refuses that because it wants the full context `budget-raise-gate / budget-raise-gate`. The answer itself is there. Carry: R11-PRE-MACHINERY-LIMITER
- Note: figure: `policy_lint.mjs --budgets` puts always-loaded (~3604 against cap 3349), role fixer and role policy above their caps, inside the 500 band. The same three rows read identically at the merge base, so this PR did not grow them. The body's "every row within its cap" means within cap plus band. Carry: dismissed: inherited from the base, unchanged by this diff

## Evidence

- Head reviewed: 3ad61a1f6e09044cd47db34952a3ab681db1b1e5 (`ev/HEAD.txt`), merge base 66865be375. `git diff $(merge-base)...origin/main -- dev/governance/roles/` is empty, so the role contract is current.
- `git merge-tree --write-tree origin/main 3ad61a1f6e` exits 0, so the PR merges cleanly.
- VERSION, the manifest and RELEASE_NOTES.md are untouched. tests/golden has no change, so there are no claims to compare (step 4).
- Self-tests at the head: machinery_ratchet 68/0 failed, pr_cap 29/0, budget_raise_gate 287/0, orchestrator_tick 322/0. These match the body.
- The body's named mutants, re-run (`ev/mutants.txt` M0, M1, M2, M7-M12, M15-M18): all KILLED. That includes the target's `bad.append`, `binds`, `scheduled_target` returning the cap, `machinery_gate`'s `<`, class_line's flag, gh's truncation limit, the raise-gate schema for `step`/`anchor`/`every_merges`, and the tick line.
- Body driver re-run: `mutant_run.py --diff 66865be375...HEAD --max-mutants 40 --report-only` gives 6 survivors, all fixture constants or assertion lines (749, 753, 764, 770, 775, 777), matching the body (`ev/mutant_run.txt`).
- Carry 3 figure re-derived: `--measure --head b3831ff64eca` gives nonproduction_merges 478, churn 13785, window 580, production 102, as the body says. The re-record 521 -> 478 is earned: the measurement, not the instrument, moved it.
- `--check --base 66865be375 --head HEAD --pr 1`: ok nonproduction_merges 481 <= 478 + band 5; ok target 481 <= 478 + band 5 (7 merges past anchor). Main has moved since the body's figure, to 481 nonproduction, so 2 of the band's 5 remain.
- Severity enumeration (step 6): the body's `git grep` prints `proposal-triage.md:23` at b3831ff64e and nothing at the head. `severity` in tools/**/*.py with bar/skip/exempt is empty. "one in, one out" occurs only at `ratchet-budgets.md:108` at the head.
- Policy: `policy_lint.mjs` FIXTURE ok, `rules_sync.mjs --check` ok, `tests/structure.py` PASSED. Corpus tokens are 69077 at base and 69061 at head, so the stated payment holds.
- CI: `merge_train.py classify ... --pr 3627` read `WAIT ... pending: gate red: none` on every poll from 19:56 to the latest (see the classify log). This block is on tests, and CI does not change it.
