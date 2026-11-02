Fix review: blocked bbcbe25986772676a8981246eacfd75c41eb2dc4 mutation-vacuous: the default-SQLite branch's open line is unpinned (deleted, made constant, or made to say MySQL/MariaDB, every FAST check stays green)

bus-nonce: 375e89f0f8d0690ade6ce4315d7b72c5

Round 8, a scoped delta re-check. This is past the third round and the brief pre-authorizes the re-cut. Measured head: bbcbe25986772676a8981246eacfd75c41eb2dc4. While I was waiting for CI the PR head moved to ef456f2b24b622c928603b26d8d1ce37b9b75014. That commit is an automatic merge of origin/main 94d8b47f6, and `review_carry.py` prints `CARRY` for it. tools/replay/export.py, tests/replay.py and the in-tree harness are byte-identical at ef456f2b, so this block holds at the new head unchanged (ev/head_move.txt).

## Block

1. **The open line on the default-file branch is not pinned (fix-review.md step 1; brief scope 2).**
   - The body says the default file prints `reading the recorder: SQLite database` and that "its new lines are pinned by the in-tree harness rows above".
   - At this head the `else:` branch of open_recorder (tools/replay/export.py, the last of the four open-line prints) has no check behind it.
   - With the FAST tier of the in-tree harness (ev/my_mutants_r8.py reuses its fast() and apply(); NULL red []), these three mutants of that line all SURVIVED (ev/my_mutants_r8.txt):
     - the line made constant again (`print("reading the recorder", ...)`), the r7 verdict's own mutant, on this branch;
     - the line deleted;
     - the line made to say `MySQL/MariaDB database`.
   - The default file is the most common install, with no `--db`, no `--db-url` and no recorder in configuration.yaml. On that install the requirement the r7 block raised (the line tells the operator which recorder was read) has no test, so it can regress silently.
   - The repair is small and stays inside the delta's scope. Add a FAST check that exports from a config dir with no recorder in configuration.yaml and asserts that the opened line equals `["reading the recorder: SQLite database"]`. Add a harness row for each of the three mutants above.

## Findings

- The default-SQLite branch's open line in open_recorder is unpinned: the constant, deleted and wrong-kind mutants all survive the FAST tier (Block 1). Carry: R10-REPLAY-REAL-DAY
- Round-4 finding 2 is still open, and the body does not claim it fixed. `AWAY_COVERED = frozenset({"owner-2026-10-30-away.json"})` in tests/replay.py is never checked against the committed fixtures: misspelt to `...-awy.json`, every FAST check stays green (ev/my_mutants_r8_r4.txt, SURVIVED). The body says the orchestrator routed it to R10-REPLAY-COST-BUDGET in dev/programme/rosters/wave-r10-groups.json. On origin/main that group's `carry` holds only the COST_BUDGETS record, and the string AWAY_COVERED appears nowhere under dev/programme/rosters/ at origin/main or at the head. So the carry the body describes has not landed. Carry: R10-REPLAY-COST-BUDGET
- Round-4 finding 3 is still open. The unsupported-scheme refusal in open_recorder can be mutated to `f"the recorder {url} is neither SQLite nor "` and every FAST check stays green (ev/my_mutants_r8_r4.txt, SURVIVED). Unmutated, the refusal for `postgresql://user:pw@h/db` prints no credential (ev/open_lines.txt); nothing pins that. Like finding 2, it is not in the R10-REPLAY-COST-BUDGET roster carry on origin/main, contrary to the body. Carry: R10-REPLAY-COST-BUDGET
- The cpu_ratio / loop_cpu_ratio re-centring on the second CI class is still owed after the merge. It is present as R10-REPLAY-COST-BUDGET's roster carry on origin/main (the COST_BUDGETS record). Carry: R10-REPLAY-COST-BUDGET
- The body's `## Head` and `## Red checks` sections are stale:
  - `## Head` says "origin/main was not merged" and gives the merge base as 25c46e76e. Head bbcbe2598 merges origin/main 76801494f, which is now the merge base, and the head has since moved to ef456f2b.
  - `## Red checks` describes the check-run set at ee29ed568, not at this head.
  - The re-cut should restate both sections at its own head. Carry: R10-REPLAY-REAL-DAY

## Evidence

- Head and delta:
  - Measured head: bbcbe25986772676a8981246eacfd75c41eb2dc4 (ev/HEAD.txt).
  - Its code head is 5163c7e6a, one commit on ee29ed568.
  - The delta ee29ed568..5163c7e6a touches only tools/replay/export.py (+10/-1), tests/replay.py and dev/audit/harnesses/r10_replay_real_day_mutants.py. It is the repair only.
  - 0de0d1700 equals 5163c7e6a in content relative to ee29ed568, and bbcbe2598 is the origin/main merge.
- Scope 1, the printed open line on each branch at this head, driving open_recorder directly (ev/open_lines.txt):
  - default file: `reading the recorder: SQLite database`
  - `--db`: `reading the recorder: SQLite database <the typed path>`
  - `--db-url sqlite:///x.db`: `reading the recorder: SQLite database`
  - configuration.yaml sqlite URL: `reading the recorder: SQLite database`
  - mysql URL with credentials: `reading the recorder: MySQL/MariaDB database`
  - No user, password, host or URL path appears on any branch. The behaviour meets the brief; only the pin on the default branch is missing (Block 1).
- Scope 1, CodeQL:
  - Check run `CodeQL` 125051037785 at this head concluded success, titled "No new alerts in code changed by this pull request", with empty output text (one page). It was neutral when the packet was rendered.
  - `codeql / Analyze (python)` 125050864240 concluded success.
  - Alert 47's class did not reappear.
- Scope 2, mutation:
  - Fixer's harness at this head: `null: red []`, `RESULT killed=37 mutants=37 null_red=0`, rc=0 (ev/fixer_fast.txt). This matches the body.
  - My own FAST variants (ev/my_mutants_r8.txt), with NULL red [] and each KILLED:
    - MySQL branch: URL by f-string, %-format, str.format and concatenation; URL as a second print argument; password only; line made constant; line deleted.
    - SQLite-URL branch: URL by f-string; db path by concatenation; line made constant; line deleted.
    - `--db` branch: line made constant; kind dropped.
    - rec.label print restored at build_export.
  - The default-branch survivors are in Block 1.
- Merge: `git merge-tree --write-tree origin/main bbcbe2598` exits rc=0 (ev/merge_tree.txt).
- CI at this head:
  - `merge_train.py classify` printed `RED bbcbe25986772676a8981246eacfd75c41eb2dc4 pending: none red: gate` with rc=1 (ev/classify.out, ev/classify.log).
  - In the job list of run 41374173601 (ev/jobs_bbcbe259.txt), `gate`, `tests / coverage-ratchet`, `tests / lane-proofs` and `tests / graders-head-copy` concluded `cancelled`. The cancellation came when ef456f2b superseded the head; `cancel-superseded` ran at 02:19.
  - Every other job concluded success or skipped, including `tests / fast (3.14)`, `tests / replay`, `tests / mutation`, `tests / closures`, `codeql / Analyze (python)` and `governance / delivery-status`.
  - No check concluded `failure` at this head, so no red-check answer is owed for it.
- Standing checks (ev/standing.txt):
  - Three-dot from MB 76801494f, VERSION, the manifest, both claim files and the RELEASE_NOTES headings are untouched.
  - The claim files are byte-identical to origin/main.
  - dev/programme/delivery/3078.md is in the three-dot diff.
- `python3 tests/structure.py`: STRUCTURE RATCHET PASSED, rc=0 (ev/structure.txt).
- Scoped-gate MODE line: not re-run here. CI's `tests / fast (3.14)` succeeded at this head; I did not fetch its log, so the MODE line is not quoted.
- Finder's round-4 replay harness: not re-run this round. The delta touches nothing run_fixture reads, and CI `tests / replay` concluded success at this head.
- The body's local loop_cpu_ratio readings (0.1506, 0.2588, 0.1628) were not re-derived: they are machine-dependent.
