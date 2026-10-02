Fix review: blocked e95150fad380dcac184d5fa8c9d4a9140f13c125 refusal-bypass: prepr.sh step 1a passes a transport file that a merge commit's own resolution adds; cloud-setup.sh also pins 3.14.2, which is the typing minimum and not CI's interpreter

PR: R9-PROC-3 (handoff/r9-proc-3), round 1. Head e95150fa, merge base 90335cbd. Body: handoff-body/r9-proc-3 @ 7d690e90.

## Blocking

1. **Step 1a misses a transport file added by a merge commit.** `transport_in_ancestry` runs `git log --no-merges`, so it never reads a merge commit's diff. A file that a merge commit adds while resolving a conflict, and that neither parent has, passes the check and stays in the head tree. The plausible way this happens: a seat runs `git add -A` to resolve a conflicted `git merge origin/main` while the body still sits in the worktree under `tools/audit/handoff/<topic>/`. That is the old convention's path, and the coordinator's brief add-on still names it. `probe_evil_merge.sh` shows rc=0 at both the stale base and the fresh base, while the tree at the head carries `tools/audit/handoff/t/BODY.md`. The body's claim that step 1a "refuses any commit since the merge base that adds or edits a file under" either root is therefore false for merges.
   **Fix, measured:** replace `--no-merges` with `-c` (`c_variant.diff`). A combined diff lists only the paths a merge changes against every parent, so main's own files stay out, which was the reason for `--no-merges`. With `-c`:
   - the probe is refused (rc=1) at both bases;
   - the null control passes: main carries a transport file and the branch merges it cleanly, and the fresh base gives rc=0;
   - the head's self-test still prints 142 passed, 0 failed (`selftest_c_variant.txt`).
   Add a self-test row for the merge-resolution shape, with its mutant (`-c` → `--no-merges`) as the mutation proof.

2. **cloud-setup.sh pins the wrong interpreter and restates it.** `PYVER=3.14.2` is commented as "CI's `fast` and `typing` interpreter line (tests.yml)". It is not:
   - tests.yml installs `python-version: "3.14"` (lines 175 and 494), which is the newest patch release;
   - the recorded line is 3.14.7: `tests/typing_budgets.json` records `"python": "3.14.7"`, `tests/requirements-typing.txt` is compiled with `--python-version 3.14.7`, and `tests/golden/claimed_drift.txt` reads "CPython 3.14.7";
   - 3.14.2 is `typing_budgets.json`'s `ruler.python_min`.
   The literal also breaks the script's own rule, "The pins are read from the checkout, never restated here". Install the recorded 3.14.7, read from `typing_budgets.json`, or say plainly that 3.14.2 is the minimum and why that is enough. `/mnt/project-files/audit-r9/cloud-setup.md` is a byte copy of the script (checked) and has to follow.

## Should fix in the same round

3. The ruff removal comes after the `exit 0` for a missing checkout. When `$REPO` is absent, the script stops before it removes ruff, so the hook fix silently never applies. The removal does not depend on the checkout, so move the loop above the guard. Whether the environment's setup script runs before or after the clone could not be confirmed from here. The hooks do skip when ruff is absent: `auto-format.py:157` uses `shutil.which`, and `stop-validator.py:494/534` says "ruff not found — skipped". This container's ruff is `/root/.local/bin/ruff`.
4. `selftest_inputs` misses transitive imports. `.claude/workflows/counts.mjs` is imported by `policy_lint.mjs:78`, `brief_lint.mjs:60`, `policy_lint_envmatrix.mjs:12` and `policy_lint_mutants.mjs:72`, and `render_md.mjs` by `policy_lint_mutants.mjs:79`. A diff that touches only those files skips step 3h. No barrier is lost, because the governance `instrument-self-tests` job runs `prepr.sh --self-test` on every PR (governance.yml:279). The body's argument that "a carried list under-selects" applies to this derived list too. The fix is to follow local imports, or to treat `.claude/workflows/*.mjs` as a prefix.

## Checked and sound

- **Cannot be skipped by not running it locally:** `app_push.sh:144` runs the full `prepr.sh` in the worktree before anything is minted. Step 1a therefore runs at the Mac's push, on the code head.
- **Legacy fallback is safe:** if the orphan-ref fetch fails, the legacy path needs exactly one body file above the code head, or it exits 1. When both exist, the orphan ref wins. A failed fetch never pushes an empty body.
- **body_push.sh:** a failed fetch exits under `set -e`. An `ls-remote` network failure makes a parentless commit, which the push refuses as non-fast-forward, so nothing is rewritten.
- **The body is still linted:** `app_push.sh` hands the body file to `prepr.sh`/`preflight.sh`, and CI's pr-contract still checks the PR body. Moving the transport loses neither.
- **Delivery row:** `handoff_push.sh` already writes `docs/delivery/$N.md` after opening the PR. The rule and `fixer.md` now say what the script already did. `rules_sync` `.mdc` is in the diff.
- **Item 6 (F10.3 I1) holds:**
  - `tests/mutation_table.py:2130-2131` refuses on `ratchet_refusal(...) == 1 or added` unless `--pin-killed` is passed.
  - The CI `mutation` job runs `--scope changed --base origin/main --max 10 --jobs 3` without `--pin-killed` (tests.yml:709-711), and its `if:` includes `pull_request` (673-679).
  - A survivor has no killer to pin, so the autofix measure step cannot clear it.
- **Self-test at head:** 142 passed, 0 failed (`selftest_head_e95150fa.txt`; this container has gh-less figure_lint, and no row failed).
- **Leftover wording (non-blocking):**
  - `tools/audit/briefs/orchestrator.md:146` still says "seats LOCAL-ONLY, hand off, the orchestrator pushes", although seats now push `handoff-body/<topic>` themselves. Worth one clause while the branch is open.
  - The roster entry R9-F10.1b still says "add this PR's own row", but that group is done.
  - No other policy, brief, skill or template file tells a fixer to commit the body or write its own row.

CI not re-run, per the review rules. Evidence: this directory.
