R9-RO-10 (lane RO, roster group R9-RO-10, no tracking issue): re-points the references to retired paths whose move has landed where something executes or follows them, and adds a guard to `tests/layout.py`. The guard refuses each pull request's own additions: a stale citation, an unswept move, or a misplaced file. It folds in the RCA-2004 docstring carry from R9-RO-9.

**Must merge after #2014 and #2015.** If this guard lands first, it refuses both of them. #2014 adds fixture lines that build the old layout. #2015 lands moves while live citations of the moved paths remain. Each of those would need re-pointing or a `layout:old` marker.

**Executed defects at main, each re-pointed here:**
- Rule `paths:` globs: 14 matched no tracked file, so the harness loaded those rules for no read. 12 are re-pointed. `ratchet-budgets.md` gains `dev/audit/README.md` beside its canon-spelt `tools/audit/README.md`, because `policy_lint`'s rule-binding check binds canon names. The 14th glob is in `defect-root-cause.md`, which #2014 edits.
- `fix-review.md`'s pre-step 1 diffed `tools/audit/briefs/`. That directory is empty since RO-5, so the diff always came back empty and every review read itself as current.
- The wave scripts' agent prompts sent seats to read the retired brief paths.
- The stop hook and `push.sh` printed commands at retired paths.
- `app_approve.sh` posted a review body naming its retired path.

**The guard (part two)** reads only the diff from the merge base, which is `GOLDEN_REF`, or the first parent on a push to `main`. It refuses three things:
- **new-reference:** a changed file gains a line citing a landed retired path, or a directory those moves emptied.
- **unswept:** this diff lands a move, and a live line still cites the moved path.
- **placement:** an added file sits outside every `tests/layout.json` category (unless it is under a planned move), or at a path whose move had landed at the base.

A line is exempt when it also names the entry's new path, resolves it through `locate(`/`canon(`, or carries the marker `layout:old`. That marker is an allow-list keyed on one line, so a reviewer sees each use in the diff (`fixer.md` step 14). The guard skips the `historical` prefixes plus `dev/governance/config/` and `dev/audit/rca/`: the first is canon-keyed on purpose until RO-9, and the second holds RCA records, whose subject is often the old path. `tools/audit/seat/moved_paths.py` now calls the same `landed()` function, so the seat enumeration and the gate cannot disagree.

**Placement limit.** A live roster at `roster_lib.py`'s `ROSTER_PATH` matches no layout category, so adding one on `main` would be refused.

**Alternatives considered:**
- A recorded allow-list of today's citations. It would be keyed on (file, path), so a new line in an already-listed file would pass.
- An absolute zero on the whole tree. 2226 live lines cite landed paths today, and most of them are records, fixtures or dual-path fallbacks that RO-9 removes.

## Head

`bcb2a10c5d5f17b826d7efc4fb7c92a82d99c0bd` (merge base `e0f0b6fb397bf42a3cd379e0c74f1f295eeebdaf`).

## Mutation proof

Each mutant was applied to `tests/layout.py` at `6c317939` and restored from git. The command was `python3 tests/layout.py --self-test`:
- M1, `stale_lines` appends nothing: 5 cases red. They are "a doc gains a citation of a landed path", "a second copy of an old citation", "the retired top-level name itself", "a citation of a directory the moves emptied", and "a move landed, a citation left".
- M2, the placement predicate set to `False`: 1 red, "a file outside every category".
- M3, the unswept arm set to `if False`: 1 red, "a move landed, a citation left".

## Null control

At the head, `python3 tests/layout.py --guard` prints `layout: GUARD: 0 refusal(s) against e0f0b6fb397b`.

Perturbation on the real index:
1. Append "Run `bash tools/audit/prepr.sh` first." to `docs/setup.md`.
2. Add `misc/planted.txt`.
3. Stage both. The guard prints 2 refusals, one `new-reference` and one `placement`, rc=1.
4. Unstage and remove both. It prints 0, rc=0.

The same plant at the merge base gives rc=0 from `python3 tests/layout.py --report`, which is the failing-first state.

## Figures

All figures were measured at head `82e2ab34` unless they name another revision. The two later commits, ending at `bcb2a10c`, change only the policy role's `opens` list and `carry-1922.json`; the guard, `policy_lint` and `brief_lint` were re-run at `bcb2a10c`.

**Live citations.** `python3 tests/layout.py --stale` reports 2226 live lines citing a landed retired path at the head. Head's `layout.py` staged onto the merge base reports 2407. Rule: every line `stale_lines` returns over the index, minus the `historical` prefixes and the guard's exempt prefixes.

**What remains, by class.** At the head, the residue splits as follows:
- Files #2014 or #2015 own: 1806 lines. #2015 owns 1694 of them and moves 1471 of those into `dev/audit/`. #2014 owns 19, and the remaining 93 are in files both PRs edit.
- Records: 400 lines, under the plan, register, carries, rosters, handover, archscore corpus and `handoff/`.
- Fixtures under `tools/policy/fixtures/`: 17 lines.
- Other: 72 lines. Each is a dual-path fallback split across lines (RO-9's removal), a test fixture building the old tree, a canon-spelt key, narrative about the move, or `docs/architecture.md`'s nested `icon.png` tree row (a census false positive).
- Census rule: file-prefix classes over the `--stale` set, with `dev/governance/config/` and `dev/audit/rca/` included. The classifier is a scratch probe, so these class counts are unverified.

**Dead rule globs.** This loop prints 14 lines at the merge base and 2 at the head:

```
for f in dev/governance/rules/*.md; do awk '/^---/{n++;next} n==1 && /^  - /{gsub(/^  - "|"$/,"");print}' $f | while read g; do [ "$(git ls-files -- ":(glob)$g" | wc -l)" -eq 0 ] && echo "DEAD $f: $g"; done; done
```

The 2 left at the head are `defect-root-cause.md` (#2014's file) and the kept canon `tools/audit/README.md` glob.

**fix-review vacuity.** For the diff from `421c77f9` (the parent of #2005, which edited `dev/governance/roles/`) to `45142cc3`:
- `git diff 421c77f9...45142cc3 -- tools/audit/briefs/ | wc -l` gives 0.
- `git diff 421c77f9...45142cc3 -- dev/governance/roles/ | wc -l` gives 135.

**Quoted commands, old spelling against new.**
- `python3 .claude/workflows/contract_rerun.py --self-test` exits 2; `python3 tools/pr/contract_rerun.py --self-test` exits 0.
- `node .claude/workflows/rules_sync.mjs --check` exits 1; `node tools/policy/rules_sync.mjs --check` exits 0.
- `bash tools/audit/prepr.sh --help` exits 127.

**Guard precision.** `python3 tests/layout.py --replay 25 --base origin/main` read 25 first-parent commits at `e0f0b6fb`, each against its own manifest and parent.
- 4 of the 21 non-move merges are refused, with 28 refusals in all.
- 15 are true positives: #2005's `nudge.md` told the orchestrator to run `tools/audit/app_push.sh`, `approve_held_runs.sh` and `app_approve.sh`, none of which exist.
- 3 are placement refusals of `tools/audit/repo_root.{py,mjs,sh}` in RO-7's merge `bcea7488`, a gap in the map. The proposed addition is under Forward-carry.
- 10 are narrative lines that would need the new path named beside them or a `layout:old` marker. They are 6 in carries 1921/1922, 1 in `tmp_paths.py`, 2 in #2011's comments, and 1 in a `CODEOWNERS` comment at `bcea7488`.
- The 4 move merges (RO-3 `bab72287`, RO-4 `1fa713f7`, RO-5 `618d014f`, RO-6 `6001b09a`) would have been refused with 45, 371+8+1, 1116+29 and 1033+38 findings. Those are their own unswept citations, which is the class this guard exists for.

**Cost.** `layout.py` is already `run_always` in `tests/run.sh`, so the guard adds 0 scripts to any scope. The marginal wall time was measured with `python3 -c` timing `guard()` and `guard_self_test()` in isolation, at a 1-minute load average of 49 on the seat Mac:
- `guard()` on this 66-file diff: 2.0 to 3.0 s over 3 runs.
- The guard self-test, 20 cases in one repo: 5.6 to 5.9 s.

**Budgets.**
- `python3 tests/structure.py` prints `STRUCTURE RATCHET PASSED`.
- `node tools/policy/policy_lint.mjs --budgets`: every per-file cap and aggregate is within cap (plus `_band` where it applies), and no cap moves. The payments are listed in commit `4cf637ca`'s message.
- `node tools/policy/policy_lint.mjs` prints `TOTAL: 0 error(s)` and `FIXTURE ok`.

**Other local checks.**
- `PYTHONPATH=tests/hastub ~/.local/state/hpo/venv-ci/bin/python tests/entities.py` prints `ALL 2198 ENTITY CHECKS PASSED` at `4cf637ca`.
- `node tools/policy/check-wave-script.mjs` prints `170 passed, 0 failed`.
- `node tools/policy/rules_sync.mjs --check` passes.
- `python3 tools/audit/seat/moved_paths.py --self-test` reports 9 checks, 0 failed.
- `bash .claude/hooks/stop-selfcheck.sh --self-test` reports 26 passed.

**Scope.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: FULL`, because `.github/workflows/tests.yml` comment lines changed. The heavy scripts are CI's.

## Red checks

- delivery-status: no row for this PR. The orchestrator writes it at the merge (`delivery-status-tracking.md`), and a fixer writes none.
- nightly-status: inherited from main and not touched by this diff. This branch changes no nightly script or input.
- prepr's policy-corpus pre-flight prints `NOT compared`. That is the `tools/pr/preflight.sh` corpus-filter path defect, which #2014 fixes; it is not refused here.
- Nothing else has run at this head; CI's check-runs at it are the record.

## Forward-carry

`dev/programme/carries/carry-1922.json`, R9-RO-9's in-tree destination. Its roster group is on `handoff/audit-r9-fixplan` and is not in this tree. The new first entry says it is newer than R9-RO-5's "not before" on rule globs, and carries three things:

1. `policy_lint.mjs` binds the corpus, earned citations and role samples by canon spelling, so re-pointing those breaks the binding. Measured on this branch:
   - Re-pointing `tools/audit/README.md`'s glob alone gave a `rule-binding` ERROR.
   - Re-pointing `docs/decisions/0010` and `0011` turned `FIXTURE VACUOUS` (citation-presence) red.
   - Dropping the old `opens` entry is a budget raise.
   R9-RO-9 undoes all three in the same change that retires canon.
2. The map additions for `tests/layout.json`, which #2015 owns: `tools/audit/archscore/**` and `tools/audit/{fastpath_census.py,fold_ledger.py,merge_fastpath.py,repo_root.py,repo_root.mjs,repo_root.sh}` go in the `tools` category, and `dev/audit/rca/` moves from `GUARD_EXEMPT` into `historical`.
3. The guard refuses an RO move that leaves a live citation of the moved path.

`node tools/policy/brief_lint.mjs dev/programme/carries/carry-1922.json` prints `TOTAL: 0 error(s)`. The guard refused this entry's first draft for citing `docs/decisions/` without its new home.

## Friction

none

## Approval

This PR edits policy files:
- the six rule sources under `dev/governance/rules/` and their generated copies;
- `dev/governance/roles/{fix-review,fixer,orchestrator,COMMON,nudge}.md`;
- `dev/governance/dimensions/D11.md`;
- `dev/governance/config/policy_budgets.json`, where the policy role's `opens` sample gains `dev/governance/roles/fixer.md` (the sample may only grow, so the canon spelling stays) and no cap moves;
- `.github/PULL_REQUEST_TEMPLATE.md`;
- `.claude/skills/steward/SKILL.md`.

Each edit re-points a retired path or pays for one. Under the owner's programme mandate 5951564627, this needs tvofi's approving review at the head before merging.
