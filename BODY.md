R9-RO-10 (lane RO, roster group R9-RO-10, no tracking issue). This PR does two things:
- It re-points references to retired paths whose move has landed, where something executes or follows them. It folds in the RCA-2004 docstring carry from R9-RO-9.
- It adds a guard to `tests/layout.py` that refuses each pull request's own new stale citations, its unswept moves and its misplaced files.

Round 2 answers the round-1 block at `43883893`.

**The roster carry (closure.py).** `check()`'s PHANTOM refusal and `prune()` now read `inert_reads` as well as `closures`. `prune` also drops a key that is left with no reads, which is the shape `_fold_inert_reads` writes.

**The guard's exemptions are keyed to one path.** A line is not a citation of an old path when it does one of three things:
- names that entry's new path;
- passes that old path as the literal argument of `locate(` or `canon(`;
- carries `layout:old=<that old path>`.

None of the three exempts any other path on the same line. A bare `layout:old`, a `locate(` of some other path, and prose that merely names the marker are all refused.

**The finder wall has one definition.** `prepare_baseline.sh --strip` now applies `finder_wall` before the earlier-round strip. The two `audit-find.js` prompts call the script instead of listing globs. Their hand-written list stopped at `docs/`, but the live register now lives at `dev/programme/register/`.

**Merged with main at `09ba95d0`** (#2015). This branch edits five lines that cite the audit config paths #2015 landed, and those lines are re-pointed.
- `check-wave-script.mjs` pins the register writer's prompt by its `rotation.json` literal.
- policy-docs runs the base copy of that checker against this branch's `audit-verify.js`.
- So the prompt names the new path and keeps the old one in a parenthetical. Both checkers print 170 passed, and R9-RO-9 drops the parenthetical.

**Rule globs.**
- `tools/audit/briefs/**` used to cover 8 role contracts and 15 dimension briefs. The round-1 re-point to `dev/governance/roles/**` dropped the dimension briefs.
- `brief-citations`, `finding-propagation`, `writing-for-agents` and `defect-root-cause` now name `dev/governance/**` instead. That is one glob, with no added line or token. The cost is that these rules also load on edits to rules, decisions and config, and that over-breadth is reported, not refused.
- `defect-root-cause.md` keeps its canon `tools/audit/briefs/**` glob beside the new one. `policy_lint`'s rule-binding check binds the 23 role and dimension files by that canon name, and dropping the glob gave 23 rule-binding ERRORs.
- The extra line is paid for by cutting step 1's restatement of `fixer.md`.
- The guard now skips the generated rule copies under `.claude/rules/` and `.cursor/rules/`. `rules_sync --check` ties each copy to its source, and the guard checks the sources.

**Merge order.** #2014 is still open. If #2014 lands after this PR, the guard refuses 2 of its lines. The figure comes from simulating #2014 merged onto this head and running the guard against it. Both lines are fallbacks that build or probe the old layout:
- `tests/entities.py`: `(d / ".claude/workflows/policy_lint.mjs").unlink()`;
- `tools/pr/preflight.sh`: `lint="$1/.claude/workflows/policy_lint.mjs"`.

Either #2014 merges first, or each of those lines carries `# layout:old=.claude/workflows/policy_lint.mjs`. #2014 owns `preflight.sh:135`, the `r9_fr3` harness and `friction_issues.mjs`. I name it as their owner and did not edit those files.

**Placement limit.** The live roster at `roster_lib.py`'s `ROSTER_PATH` matches no layout category. A roster added on `main` would be refused.

## Head

`f4d102a0ac3b184527f4836dd5312a88fca21657` (merge base `09ba95d08157e40950104d28a34c94dc899d4be1`).

## Mutation proof

**Guard predicates.** Each mutant was applied to `tests/layout.py` at the head, then restored, and `python3 tests/layout.py --self-test` was run. The driver is a scratch loop over the seven replacements.

| mutant | cases red |
|---|---|
| M1 `stale_lines` appends nothing | 10 |
| M2 placement predicate `False` | 2 |
| M3 unswept arm `False` | 1 ("a move landed, a citation left") |
| M4 placement `!= 1` changed to `== 0` | 1 ("a file in two categories") |
| M5 emptied-directory dedupe off | 1 ("… counted once") |
| M6 marker unkeyed (`"layout:old" in line`) | 3: marker names another path, unkeyed marker, prose naming the marker |
| M7 `locate(`/`canon(` unkeyed | 1 ("a stale command beside a locate of another path") |

**closure.py.** `python3 tests/closure.py selftest` was run after each mutant:
- The PHANTOM sweep reads `("closures",)` only: 1 red, "check fails on a phantom in the committed inert_reads (R9-RO-10)".
- `prune` reads `("closures",)` only: 1 red, "prune drops dead inert_reads entries…".

**Finder wall.** Without `finder_wall` in `--strip`, `bash tools/audit/prepare_baseline.sh --wall-self-test` prints `FAIL --strip kept the programme register`. This arm was added in this round.

## Null control

- `python3 tests/layout.py --guard` at the head prints `layout: GUARD: 0 refusal(s) against 09ba95d08157`.
- On the real index I planted three things together:
  - the line "Run `bash tools/audit/prepr.sh` first." in `docs/setup.md`;
  - the line `bash tools/audit/app_push.sh x  # layout:old` in the same file;
  - a new file, `misc/p.txt`.
- With all three staged, the guard printed 3 refusals (2 new-reference, 1 placement), rc=1. With them removed, it printed 0, rc=0.
- The second planted line passed the round-1 guard.

**Simulated finder export.** I ran `git archive origin/main dev docs tests tools` into a temp directory, then `--strip <export> 10` on it:
- With main's `prepare_baseline.sh`, `register_survives=yes`.
- With this head's, `register_survives=no`.
- `docs/setup.md` is kept in both runs.
- Each run prints `RESULT stripped_earlier_rounds=11 files_removed=1313 files_kept=305`.

**closure.py null control.** The table without the planted dead path passes `check`. `prune` on a copy of `tests/closures.json` at `09ba95d0` prints `pruned 0 phantom entry(ies)`. It re-sorts the one list #2015 left out of order, so main has no dead `inert_reads` entry to remove.

## Figures

- `python3 tests/layout.py --stale` reports 873 live lines citing a landed retired path at the head. Head's `layout.py` staged onto `09ba95d0` reports 1052. Both counts exclude the `historical` prefixes and the guard's exempt prefixes.
- The dead-rule-glob loop prints 2 at the head:

  ```
  for f in dev/governance/rules/*.md; do awk '/^---/{n++;next} n==1 && /^  - /{gsub(/^  - "|"$/,"");print}' $f | while read g; do [ "$(git ls-files -- ":(glob)$g" | wc -l)" -eq 0 ] && echo "DEAD $f: $g"; done; done
  ```

  Both are kept canon globs: `defect-root-cause.md`'s `tools/audit/briefs/**` and `ratchet-budgets.md`'s `tools/audit/README.md`. `policy_lint` binds by them. Both are carried to R9-RO-9.
- `python3 tests/layout.py --replay 25 --base origin/main` refuses 4 of the 20 non-move commits in that window (the 5 moves are RO-3, RO-4, RO-5, RO-6 and #2015), with the same 28 refusals as round 1.
  - 15 are true positives in #2005's `nudge.md`.
  - 3 are placement refusals of `tools/audit/repo_root.*`, a map gap carried to R9-RO-9.
  - 10 are narrative lines.
  - The move merges are refused as unswept. #2015 itself would draw 10 new-reference and 136 unswept refusals.
- Cost, from `python3 -c` timing over 3 runs at a 1-minute load average of 28:
  - `guard()` on this diff: 2.3 to 4.7 s.
  - The guard self-test, 27 cases in one repo: 7.7 to 10.2 s.
  - Scripts added to any scope: 0, because `layout.py` is already `run_always` in `tests/run.sh`.
- `node tools/policy/policy_lint.mjs --budgets`: every per-file cap and aggregate is within cap (plus `_band` where it applies), and no cap moves. Payments are in the commit messages (`4cf637ca`, `f4d102a0`).
- `node tools/policy/policy_lint.mjs` prints `TOTAL: 0 error(s)` and `FIXTURE ok`.
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python tests/entities.py` prints `ALL 2198 ENTITY CHECKS PASSED`.
- `node tools/policy/check-wave-script.mjs` prints `170 passed, 0 failed`, and `main`'s copy of the checker on this branch does too.
- The following report no failures: `python3 tests/closure.py selftest`, `bash tools/audit/prepare_baseline.sh --wall-self-test`, `--strip-self-test`, `node tools/policy/rules_sync.mjs --check`, `bash .claude/hooks/stop-selfcheck.sh --self-test`, and `python3 tools/audit/seat/moved_paths.py --self-test`.
- Scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL`, so the heavy scripts are left to CI.

## Red checks

- delivery-status: inherited from main's unread rows. The orchestrator writes this PR's row.
- nightly-status: inherited from main. This branch changes no nightly script or input.
- budget-raise-gate: round 1's head had a cancelled run beside a successful twin. The cancelled run needs a rerun; it is not a raise.
- Nothing else has run at this head yet. CI's check-runs at the head are the record.

## Forward-carry

The destination is `dev/programme/carries/carry-1922.json`, R9-RO-9's in-tree carry file. Its first entry, updated this round, carries:
- the canon bindings to undo when canon retires:
  - the `tools/audit/README.md` glob, and the `tools/audit/briefs/**` glob in `defect-root-cause.md`, measured at 23 ERRORs without it;
  - the citations of `docs/decisions/0010` and `0011`;
  - the old `fixer.md` entry in `opens`;
  - `dev/governance/config/` in `GUARD_EXEMPT`;
- the map additions: `tools/audit/archscore/**` and the loose `tools/audit/*.py` instruments, plus `dev/audit/rca/` moving into `historical`;
- the guard's rule for RO moves.

`node tools/policy/brief_lint.mjs dev/programme/carries/carry-1922.json` prints `TOTAL: 0 error(s)`. The `audit-verify.js` parenthetical is R9-RO-9's to drop once main's checker carries the new literal.

The roster carry on R9-RO-10 (inert_reads) is delivered in this PR.

## Friction

none

## Approval

This PR edits policy files:
- the rule sources under `dev/governance/rules/` and their generated copies;
- `dev/governance/roles/{fix-review,fixer,orchestrator,COMMON,nudge}.md`;
- `dev/governance/dimensions/D11.md`;
- `dev/governance/config/policy_budgets.json`, where the `opens` sample grows by one entry and no cap moves;
- `.github/PULL_REQUEST_TEMPLATE.md`;
- `.claude/skills/steward/SKILL.md`.

It also edits code-owned `tests/closure.py`. Under the owner's programme mandate 5951564627, this needs tvofi's approving review at the head before merging.
