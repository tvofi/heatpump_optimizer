Fix review: merge 86a88d394c61d615dcc0107a6189e45ca7b4d219

bus-nonce: 0ac5f21e3b4baa31187f9eafc2c20cca
pending-ci: gate

Round 3. This is a later round over the reviewed head 6f4b8cd7b729316f4ed9fa0f7bf26f6cdaea2d14. Scope: the delta only, per the packet's `## Review scope: delta`. The delta has two parts:
- `tools/audit/check_scopes.py`: `open_cards_cli()`, `json_or_none()` and two CLI self-test arms.
- `tools/policy/check-wave-script.mjs`: the P3 grader's `plan/read` and `plan/moves` stubs.

The delta touches no `custom_components/` code, so nothing widens. I read the role contract from main, which has changed since the PR's merge base.

## Findings

- Follow-up: my own mutant M20 survives the full `--self-test`. It changes `unmarked = sorted(cid for ...)` to `list(cid for ...)` in `open_cards_report`. The CLI arm's record lists C2 before C3, which is already sorted, so the arm cannot tell the two apart. The order of `unmarked_cards` and of the `UNMARKED` lines is therefore unpinned. The line is round-1 code, not this delta. The risk is low, because P3 reads the list as a set. An arm whose record lists C3 before C2 would pin it. Carry: R11-PRE-ROUND-CHECK-GATE

## Evidence

- Previous block (M17 and M18 survived): resolved. Both mutants are now killed by the new CLI arms, which run the full `check_scopes.py --repo . --ref HEAD --self-test` at the head in a detached worktree (`ev/mutants.txt`):
  - NULL: rc 0, `marked rc=0, unmarked rc=1 ['UNMARKED C2', 'UNMARKED C3']`.
  - M17 (`sys.exit(rc)` -> `sys.exit(0)`): KILLED, `unmarked rc=0`.
  - M17b (-> `sys.exit(1)`): KILLED by the null control, `marked rc=1`.
  - M18 (`print(line, file=sys.stderr)` -> `pass`): KILLED, `unmarked rc=1 []`.
  - M21 (only a missing `gates_finders` key counts as unmarked): KILLED.
  - M22 (main's JSON print on stdout dropped): KILLED.
  - The worktree's `git status` was clean after the run.
- Previous finding M19 (`"open_cards": sorted(out)` -> unsorted): it survives again, and the body's claim that it is equivalent is verified. `evaluation_gaps` appends to `parallel` inside `for cid, card in sorted(cards.items())` (check_scopes.py:372), and card ids are unique dict keys. So `out` is already sorted, and the `sorted()` call changes nothing on any input. The finding is settled.
- Self-test at the head: `evaluation arms: 62/62 held; --round 1 rc=1; --open-cards rc=2, marked rc=0, unmarked rc=1 ['UNMARKED C2', 'UNMARKED C3']` and `SELF-TEST passed`, rc 0 (`ev/selftest-head.txt`). This matches the body's round-2 figure.
- Grader delta: at the head, `node tools/policy/check-wave-script.mjs` prints `223 passed, 0 failed`, rc 0 (`ev/wave-script.txt`). This matches the body's figure for this head's grader against 416280f5's `audit-plan.js`, which is the same blob as at this head. The head's `audit-plan.js` reads no `open`, `open_rc` or `open_items`, so the extra stub fields cannot affect it. The change is test-only. I did not re-derive the body's ec058220b5 figures (209/7 and 223) myself.
- CI: `merge_train.py classify 86a88d394c61d615dcc0107a6189e45ca7b4d219 --pr 3620` printed `WAIT 86a88d394c61d615dcc0107a6189e45ca7b4d219 pending: gate red: none` on every run from 04:02 to 04:31Z (`ev/classify-log.txt`), with no red. After about 30 minutes I stopped polling, so the verdict carries `pending-ci: gate`. The packet's `gate failure` and its introduced-red refusal were read while jobs were still running, and classify decides. No red is owed a `## Red checks` answer.
- Merge with main: `git merge-tree --write-tree origin/main 86a88d394c` rc 0, no conflict (`ev/merge-tree.txt`).
- The three-dot diff leaves VERSION, the manifest and RELEASE_NOTES.md untouched.
- Head: the PR's head is 86a88d394c, and the body's `## Head` names it. Its tree equals 8ad98806e4's. `review_carry.py 6f4b8cd7b 86a88d394c` prints FRESH-REVIEW (`ev/review-carry.txt`).
- Note: policy-approval: the edits to 0018 sections 5 and 6 and to architect-planner.md still need tvofi's approving review, or one under mandate 6893738184, before merging. Giving it is not this verdict's job.
