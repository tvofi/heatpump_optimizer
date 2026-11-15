Fix review: blocked 6f4b8cd7b729316f4ed9fa0f7bf26f6cdaea2d14 tests-gap: --open-cards exit code and UNMARKED stderr unpinned at the CLI

bus-nonce: e9b5ea8fff58ed6b212148dc0754ad09

Round 2 (a later round over the reviewed head e1e3197e3aff48ee7afd6d43db153e232f7b6134). Scope: the delta only, per the packet's `## Review scope: delta`. The delta adds dev/programme/delivery/3620.md and changes tools/audit/check_scopes.py: `open_cards_report`, three self-test arms and main()'s `--open-cards` branch. It touches no custom_components/ code, so nothing widens. The role contract is unchanged on main since the merge base.

## Block

- The previous block asked for "a self-test arm that runs the CLI path". The repair tests `open_cards_report`, the function main() calls, and leaves untested the two lines main() adds to act on its result. Mutants on those lines survive the full `check_scopes.py --self-test` (rc 0, `evaluation arms: 62/62 held; --open-cards rc=2`; `ev/mutants.txt`):
  - M17: main's `sys.exit(rc)` -> `sys.exit(0)`. `--open-cards` then exits 0 over unmarked cards, which is exactly the silent pass the previous block was about, for any caller keying on the exit code.
  - M18: `print(line, file=sys.stderr)` -> `pass`. The `UNMARKED <card>` lines the body promises on stderr disappear.
- The only CLI arm (`run_oc`) still covers just the untracked-evaluation case (rc 2).
- Wanted (either is enough): extend the `default_run` subprocess arm to a record tracking an evaluation with one unmarked accepted card, asserting rc 1 and the `UNMARKED` line on stderr. Or move main()'s print-and-exit into a function the self-test drives, and assert its rc and stderr. Then re-run M17 and M18 and show both killed.

## Findings

- Follow-up: M19 (`"open_cards": sorted(out)` -> unsorted `out`) survives. Every arm lists at most one open card, so the sort is unpinned. It is low risk because P3 reads the list as a set. An arm with two open cards in reverse order would pin it. Carry: R11-PRE-ROUND-CHECK-GATE

## Evidence

- Previous verdict's block, part 1 (M11 survived): resolved. M11 (`out` dropped from the `evaluation_gaps` call, now in `open_cards_report`) is killed at 61/62 (`ev/mutants.txt`).
- Previous verdict's block, part 2 (an empty list over unmarked cards): resolved in the function and verified live. The head's code at f6d35cf73f (round 11 as originally written) exits 1, prints 43 UNMARKED lines and returns `"open_cards": []` with 43 `unmarked_cards` (`ev/open-cards-r11-4.txt`). At c6ce415b77 it exits 0 with `unmarked_cards: []` and 12 `open_cards`, the same 12 cards as the 12 accepted cards whose `gates_finders` is false (43 accepted in all; `ev/open-cards-c6ce415b.txt`). Both figures in the body's `### Repair` re-derive.
- Mutants, my own driver (full `check_scopes.py --self-test` at the head, applied and restored in a detached worktree at 6f4b8cd7b; `ev/mutants.txt`):
  - NULL: rc 0, 62/62 held.
  - Killed: M11, M12 (rc always 0 in `open_cards_report`), M13 (only a missing key counts as unmarked), M14 (decision filter dropped), M16 (UNMARKED lines empty).
  - M15 (`unmarked = [] or sorted(...)`) survives but is equivalent, my own mis-built mutant.
  - Survived: M17 and M18 (see Block) and M19 (see Findings).
  - The body's M11 to M14 re-derive as killed.
- Self-test at the head: `evaluation arms: 62/62 held; --round 1 rc=1; --open-cards rc=2`, `SELF-TEST passed`, rc 0 (`ev/selftest-head.txt`). This matches the body's 62 of 62.
- CI: `merge_train.py classify 6f4b8cd7b729316f4ed9fa0f7bf26f6cdaea2d14 --pr 3620` printed `GREEN 6f4b8cd7b729316f4ed9fa0f7bf26f6cdaea2d14 pending: none red: none`, rc 0 (`ev/classify.txt`, `ev/classify-log.txt`). The packet's `gate failure` and introduced-red refusal were read while jobs were still running; classify decides, and no red is owed a `## Red checks` answer.
- Merge with main: `git merge-tree --write-tree origin/main 6f4b8cd7b` rc 0, no conflict (`ev/merge-tree.txt`).
- VERSION, the manifest and RELEASE_NOTES.md are untouched in the three-dot diff (5 files: 0018, architect-planner.md, delivery/3620.md, check_scopes.py, instruments/check_scopes.py.md).
- Head: refs/pull/3620/head is still 6f4b8cd7b at the time of writing, and it is the head the body names. `review_carry.py e1e3197e 6f4b8cd7b` prints FRESH-REVIEW (`ev/review-carry.txt`).
- Note: stale-body: the body's opening `--open-cards` bullet still describes `{round, ref, open_cards}` and only exit 2. The `### Repair` section gives the current shape (`unmarked_cards`, rc 1).
- The policy edits (0018 sections 5 and 6, architect-planner.md) still need tvofi's approving review, or one under mandate 6893738184, before merging. Giving it is not this verdict's job.
- Closing self-audit: `carry_audit.py check` rc 0, `2 finding item(s): 2 routed, 0 unrouted` (`ev/carry-audit.txt`). The body file it read is an abridged copy of the PR body, read via the API: Head, Red checks, Forward-carry and Friction.
