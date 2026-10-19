Fix review: merge 954a7b20ffb30279adb8f57c650b3d1455c68c63

bus-nonce: 31d0869a526c8eb220323a60e284a857

PR: #2417 (R10-ROSTER). **Round 2.** Round 1 (comment 6253477740) blocked c83ae12ac on carry-stale.
Reviewed head: 954a7b20ffb30279adb8f57c650b3d1455c68c63 (`ev/HEAD`). It was still the head when I re-read it before writing this. Merge base 2ddfa503269c. origin/main fa424fd91a04.
Reviewer: a cloud seat with no access to out-of-tree evidence. Everything below was read from the tree, the check-runs API, or the PR bodies.

## Contract currency
`git diff <merge-base>...origin/main -- dev/governance/roles/` is **not empty** (`ev/roles-diff-lines.txt`). origin/main's fa424fd9 (#2408) reworded fix-review.md steps 9 and 10. I reviewed against origin/main's copy. Step 10's new wording (open the roster carry at the body's `handoff/audit-r<N>-roster` SHA) is the one applied below.

## Round 1's block: settled
- The CodeQL-delegation carry (roster line 2569) is still in R10-TICK-DRIVERS' `carry`.
- That group is now `resume.stage: done`, with commit a96f4be4ac0a. That commit is on main and is #2390's merge, so nothing dispatches the carry.
- #2406's current body explicitly dismisses the carry, because the work is done in its diff. It also moves the beat restart to R10-STAMP. R10-STAMP's second carry holds that restart, with its control: the memo holds two SHAs, and a roster-only commit regenerates within one beat.
- The stale entry is inert, so the carry-stale risk (dispatching finished work) no longer holds.

## What holds
- **Verbatim carries.** The head's `dev/programme/rosters/wave-r10-groups.json` is byte-identical to `origin/handoff/audit-r10-roster` at 73bb15fe8f5bf05ec3568927118a8d678dd8b99f (`ev/roster-vs-handoff-73bb15fe.diffstat` is empty). The roster branch changes only that file against its main base, and the head carries it exactly.
- **Nothing dropped against either parent.**
  - Against main, at an object level (`ev/roster-mb.json` vs `ev/roster-head.json`): 63 groups become 72. No group is removed, no top-level key changes, and no carry entry is lost from any group.
  - The 8 textual `-` lines are trailing-comma rewrites of last array elements, plus two replaced fields. R10-ARCHSCORE-COVERAGE's brief is a pure insertion of the #2415 precondition paragraph (difflib shows one `insert` opcode and no deletion). R10-TICK-DRIVERS' `resume` goes from not-started to done.
  - Against the roster parent: the roster is identical, as above.
- **Groups listed in the body: all 9 present and well-formed** (`ev/wellformed.txt`).
  - The 9 groups: R10-SAV-COMFORT, R10-MUTATION-ANCHOR, R10-N-LOG-FLOOD, R10-POLICY-LINT-FAMILY, R10-DEAD-RATE-LIMIT, R10-MERGE-SUBJECT-HARDEN, R10-CI-LAYOUT, R10-OPENPR-SILENT, R10-STAMP.
  - Every one has exactly main's group key set: no key missing, no extra key. There are no duplicate ids, every `after` resolves to a group in the roster, and every carry is a string.
  - `plan_table.py --roster-file` rc 0, and all 9 groups appear in its output. `roster_lib.py --self-test`: 14 checks, 0 failed.
- **Carry counts match the body exactly.**
  - New groups: SAV-COMFORT 1, MUTATION-ANCHOR 1, POLICY-LINT-FAMILY 3, DEAD-RATE-LIMIT 2, MERGE-SUBJECT-HARDEN 2, CI-LAYOUT 3, OPENPR-SILENT 1, STAMP 2. N-LOG-FLOOD has 0, and the body lists none for it.
  - Existing groups: ADVISOR +2, SCORES +1, ARCHSCORE-COVERAGE +1 and its brief, TICK-DRIVERS +2 and its resume, BRIEFS-FOLD +2.
- **The carries #2404 and #2406 route to.**
  - R10-OPENPR-SILENT holds the weekly/closure carry-sweep carry, moved from R10-TICK-DRIVERS, with its precondition on #2404.
  - R10-STAMP holds the 19 may-drift restores and the beat restart.
  - Both groups resolve in the tree's roster once this merges.
- **Lint at 0.** These results are the same at the head (`wt`) and on the merged tree with origin/main fa424fd9 (`wtm`, commit in `ev/merged-commit.txt`):
  - `node tools/policy/brief_lint.mjs dev/programme/rosters/wave-r10-groups.json`: rc 0, `TOTAL: 0 error(s) across 1 file(s)`. There is one WARNING (R10-RCA-FRICTION, `fix-review.md:29` no anchor), which is pre-existing on main.
  - The default `brief_lint.mjs`: rc 0, with `CARRY ok`.
  - `node tools/policy/policy_lint.mjs`: rc 0, `TOTAL: 0 error(s) across 41 policy file(s)`, with no VACUOUS.
- **No host path added.** The `~/`, `/home/`, `/Users/` and `/tmp/` matches are 2 lines at both ends (`ev/hostpaths-*.txt`). They are in R10-RCA-FRICTION and R10-RCA-STRUCTURE-BLIND, which are already on main, and the diff adds none.
- **Step 13.** `git merge-tree --write-tree origin/main(fa424fd9) 954a7b20` exits 0, giving tree 4d441dd1f8d2. stderr is empty, with no MERGE-CLAIM lines, because no claim file is touched (`ev/merge-tree.*`).
- **Step 11.** The check-runs API at the head shows 41 runs and 0 failures. One is neutral (CodeQL) and one is still in progress (coverage); the rest are success or skipped (`ev/checkruns-head.txt`). pr-contract (both runs), briefs, policy-docs, wave-script and delivery-status are success. The body's `Red checks: none` holds.
- **Step 7.** The body names 954a7b20 as the head, and its merge chain is exact:
  - 954a7b20 = 491693ee + main 2ddfa503.
  - 491693ee = c83ae12ac + 669074c2.
  - 669074c2 = 4a00b97f + main 06c6f3cf.
  - 4a00b97f = c83ae12ac + roster 73bb15fe.
- **Step 5.** VERSION, the manifest and RELEASE_NOTES are untouched (`ev/version-untouched.txt` is empty). The diff is the roster plus `dev/programme/delivery/2417.md` (one open row).
- **N/A steps.** Steps 1–4, 6, 14 and 15 do not apply: there is no production, test, budget, closure or claim change.

## Not blocking
- The body's roster-tip SHA `73bb15fe8f5bf05ec3568927118a8d678dd8b99` has 39 hex digits; the final `f` is missing. It still resolves as an abbreviation.
- The head does not contain origin/main fa424fd9 (#2408): it is 9 commits behind. The merge is clean, and the lints pass on the merged tree with #2408's `policy_lint.mjs`, so a main merge is optional.
- R10-TICK-DRIVERS shows `stage: done` but keeps `next_step: dispatch a fixer once every after group is done`. Its two #2406 entries also remain in a done group. Both are cosmetic, and `roster_edit.py` has no carry-removal verb (#2406's body).
- The body does not mention round 1's block or how it was settled. Its settlement lives in the roster branch and #2406's body.

## Not verified by me
- No figure inside any carry was re-derived. They are checked as verbatim copies of the roster branch, not against their source measurements (step 8).
- `carry_audit.py`'s BAD-DEST resolution was not run: the tool is not on main (it lands with #2404).
