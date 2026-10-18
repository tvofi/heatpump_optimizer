_Requested by **tvofi**_

O17 item 1 (tooling) and item 2(ii), from the roster-cost pre-study the orchestrator accepted on 2026-10-18 (tvofi asked to keep the roster and state docs from costing CI). Part of #201. No roster group lists an issue for this work, so this body closes none. Item 1's policy half, the landing triggers, is `handoff/r10-roster-carry-policy`. Item 2(i), CodeQL, is `handoff/r10-codeql-lang-skip`.

**Owner gate.** `.github/workflows/tests.yml`, `tests/lane_skip.py` and `tests/closure.py` are code-owned, so tvofi approves this at merge. The seat tools under `tools/audit/seat/` have no owner.

**What it fixes, measured.** Every roster reader defaulted to `origin/main`, while the orchestrator's roster edits live on `handoff/audit-r10-roster` until a roster PR lands them.
- At origin/main `63816b857` and the roster branch `07ba56db1` (2026-10-18 13:00Z), 10 `<group> <stage>` lines on the branch are not on main: 4 stage changes plus 6 groups main does not have.
- The live state-docs beat ran with that default and watched `refs/heads/main` only. So the published resume and plan showed those stages wrong, and a roster edit never regenerated them.
- Separately, every roster or row PR ran `browser`, `coverage` and `typing`, none of which reads either path.

**The change.**
- **`roster_lib.default_roster_ref(git)`** replaces the constant `DEFAULT_ROSTER_REF = "origin/main"`. It answers `origin/handoff/audit-r<N>-roster` (N the newest round at main) when the clone has that ref, else `origin/main`. Whenever that answer may be stale it adds a note: the branch is absent here, or main carries roster changes the branch has not merged.
  - It is a function because the round branch depends on the clone.
  - It takes a `git(argv)` runner, so the tick's stub drives it. `round_ref` and `reader_ref` are its two helpers.
- **Readers.** `orchestrator_tick.py` (PLAN), `plan_table.py`, `resume_doc.py` and `handover_prompt.py` resolve through it when `--roster-ref` is absent. `state_docs.py`'s own `"origin/main"` literal is gone, so `roster_lib` is the single owner. The tick prints the note as a `roster ref:` line, flagged when it is a WARNING.
- **The beat watches the roster ref too.** Its memo is `<main tip> <roster tip>`, and a roster-only move fetches the ref and regenerates. With no `--roster-ref` the watched ref is the round branch. An existing tip file holding main's tip alone reads as moved once and regenerates.
- **`tests/lane_skip.py` Level 0.**
  - When every file of the PR's diff is `dev/programme/rosters/wave-r<N>-groups.json` or a canonical `dev/programme/delivery/<N>.md` (one anchored pattern), `browser`, `coverage` and `typing` skip with no recorded proof. `fast` never takes Level 0: it keeps the scoped suite and the `run_always` lines.
  - `typing` gains a decision step and `needs: closure-scope`. Its `!cancelled()` keeps it running on push, where `closure-scope` does not run.
  - A skipped job reports `skipped`, which the ruleset accepts. Level 1 and Level 2 are unchanged.
- `INSTRUMENTS.md` and the `state_docs.py` docstring say the same.

**Round 2: one rename-safe changed-files producer (#2406 round-1 BLOCKED at `a7d97f55b`).**
- **The hole.** Porcelain `git diff --name-only` detects renames and lists only the destination. Renaming `custom_components/heatpump_optimizer/__init__.py` onto `dev/programme/delivery/99999.md` listed the row alone, so Level 0 skipped three lanes, and `closure.select` scoped 0 scripts for the same diff. The gate had the hole before this PR; Level 0 widened it to the lanes.
- **The fix is one producer.** `tests/closure.py` `changed_between(base, head, dots=...)` runs `git diff --no-renames --name-only`, and `changed_files` (the gate's list) uses it. A new CLI, `python tests/closure.py changed --base B --head H [--two-dot]`, prints the same list. Every list site in `tests.yml` consumes that CLI: `graders-head-copy`, `closure-scope` (2), `closures` (2) and `composed-proof`, 6 in all. `lane_skip`'s base delta calls `changed_between` too.
- **The census, so none is left.** The closure self-test scans `.github/workflows/*.yml`, `tests/*.py|sh`, `tools/pr/*.py|sh` and `tools/audit/seat/*.py|sh`. It refuses any `git diff ... --name-only` line that lacks `--no-renames`. The exemptions:
  - a diff against the empty tree (`hash-object -t tree /dev/null`), where every path is an add and no rename can occur;
  - a `--cached` count, used only in echo text;
  - a comment line;
  - a line marked `# rename-null-control`, the deliberate porcelain controls;
  - three exact per-file `RENAME_ALLOW` entries: the `tests/entities.py` fixture copy of a job's text (data), a `merge_train.py` docstring, and a `ref_privacy.py` refusal message whose real diff already passes `--no-renames`.
- **Every site enumerated.** Beyond the 6 `tests.yml` list sites above, the census refused these callers, each now with `--no-renames`:
  - `tests/env_drift.py` `three_dot_files` (2);
  - `tests/mutation_table.py` `drain_changed`;
  - `tools/pr/preflight.sh` (2);
  - `tools/pr/prepr.sh` (5);
  - `tools/audit/seat/orchestrator_tick.py` `three_dot_files`, plus its stub matcher;
  - `tools/audit/seat/handoff_push.sh` (3).

  It also refused the two prose lines now allow-listed and closure.py's own planted strings, which are marked. The 14 remaining workflow `--name-only` lines are all empty-tree restores or `--cached` counts. It prints `([], [])` at this head.
- **CodeQL's list.** `tools/pr/codeql_scope.py` on `handoff/r10-codeql-lang-skip` (#2405) builds its own list with `--no-renames`, because #2405 lands first and cannot import a producer it does not have yet. Owed after both land: `codeql_scope.changed` delegates to `closure.changed_between`. The census reaches `codeql_scope.py` as soon as main carries it. Its one porcelain line is the marked null control.

**Departure from the pre-study, said plainly.** Item 2(ii) listed `closures`, `mutation` and `env-matrix` too. They are not here:
- `closures` has its own scope arm (`case`), and `composed-proof`, `ci-ratchet` and `closures-autofix` depend on it.
- `mutation` costs 0.6 min on #2380 and has three dependents.
- `env-matrix` is in `governance.yml`, which `handoff/r10-codeql-lang-skip` edits, and the coordinator asked for disjoint files.

Each can be added after both land.

**Alternatives considered.**
1. A sentinel ref string resolved inside `roster_path`. Refused: it leaks into fetch specs and every printed source.
2. Resolving to the branch with no fallback. Refused: a clone that never fetched the branch would refuse outright.
3. Keeping main as the default and fetching the branch in each tool. Refused: that is network in five readers, where the tools are stateless.
4. A new workflow output per lane computed in YAML. Refused: lane_skip's rule is that the decision is a tested script.

5. For the rename hole: setting `diff.renames=false` in each job's git config. Refused: it is invisible to the local tools that share the list (prepr, preflight, the tick), and nothing pins it. One producer plus a census does pin it.

## Head

`f658e418aa51611407f92497c6e9007dd9c52b7d`. It is four commits on origin/main `63816b857`: `a5de742c0`, `6eb3ec595`, the orchestrator's row `a7d97f55b`, and the round-2 fix `f658e418a`. `git fetch origin main` at 2026-10-18 13:40Z gives `413944b67`. `git merge-tree --write-tree origin/main HEAD` merges clean. Main's only new `--name-only` text is comments in `tests/entities.py`, which the census already passes.

## Mutation proof

Each mutant edited one file in place in the worktree (committed first), ran the named self-test, and was restored with `git checkout --`.

**Round 1, unchanged:**
- **MB1: the absent-branch check in `default_roster_ref` disabled.** `python3 tools/audit/seat/roster_lib.py --self-test` prints `18 checks, 1 failed`: `no round branch here: main, and the note says the branch is absent`.
- **MB2: the tick reads `(rl.MAIN_REF, "")` instead of `rl.default_roster_ref(self.git)`.** `python3 -W error tools/audit/seat/orchestrator_tick.py --self-test` prints `104 checks, 2 failed`: `PLAN default roster ref: the round branch present: it is read` and `... the note says the branch is absent`.
- **MB3: the beat's memo is main's tip alone.** `python3 tools/audit/seat/state_docs.py --self-test` prints `8 self-test check(s) failed`, among them `arm 2b: exactly one push`, `arm 2b: the pushed plan carries the roster's new stage` and `arm 1: the tip is recorded, main's and the roster ref's`.
- **MB4: `plan_table.py`'s `reader_ref` line removed.** The same self-test prints `2 self-test check(s) failed`: `arm 5: plan_table.py with no --roster-ref reads the round branch` and `... with the branch absent reads main, and says so`.
- **MB5: Level 0's guard disabled.** `python3 tests/lane_skip.py self-test` prints `44/50 pins passed`: the six `<lane> skips a ... diff at level 0` pins.
- **MB7: the lane test dropped, so `fast` takes Level 0.** `48/50 pins passed`: `fast never skips at level 0` and `fast still takes level 1 on a record diff`.
- **MB6': the pattern's end anchor `\Z` dropped.** `47/50`: `<lane> runs on dev/programme/delivery/2380.md.bak`.
- **MB6 SURVIVED: the `".." not in path` clause deleted** (`50/50`). The anchored pattern already refuses every `..` path, so the clause was dead. `6eb3ec595` removes it, and its pins stay, now on the pattern.

**Round 2, at `f658e418a`:**
- **MB8: `--no-renames` dropped from `changed_between`, the producer.**
  - `python3 tests/closure.py selftest` prints `3 of 122 closure shrink pins FAILED`:
    - `the changed list keeps both sides of a rename onto a delivery row` (`['dev/programme/delivery/99999.md']`);
    - `so the gate does not scope a deleted entry point to zero scripts` (`scoped: 0 run`);
    - `no rename-detecting --name-only diff under RENAME_SITES` (`tests/closure.py:2758`).
  - `python3 tests/lane_skip.py self-test` prints `51/54 pins passed`: `browser|coverage|typing runs on a rename from production onto a delivery row`.
- **MB9: `--no-renames` dropped from one `prepr.sh` site.** The census prints `tools/pr/prepr.sh:507: if git diff --name-only "$1"...HEAD > "$cw/changed.txt"; then`.
- **MB10: one `tests.yml` site reverted to `git diff --name-only "$BASE"..."$HEAD"`.** The census prints `.github/workflows/tests.yml:1888: ...`, so the workflows are under the pin, not only the scripts.
- **Failing first.** MB8 is the round-1 producer, which had no `--no-renames`. The new rename pins fail on it, and they pass at `f658e418a`.

## Null control

- **The rename.** The same throwaway repository read through porcelain `git diff --name-only` lists `['dev/programme/delivery/99999.md']`. Two pins assert that list:
  - the closure null control, `porcelain git diff lists the row alone (the seam is real)`;
  - the lane_skip control `the rename-detecting porcelain list would skip`, which asserts browser's Level 0 skip on it.
  The producer lists both sides, and the lanes run.
- **The census.** Over a planted temporary root, it refuses exactly the one porcelain line and passes its `--no-renames` twin beside it. It reports all three allow entries as stale there, since none of them matches a line.
- **The roster ref, on the live repository at origin/main `63816b857`.** `roster_lib.default_roster_ref(roster_lib.git_in('.'))` answers `('origin/handoff/audit-r10-roster', '')`. With `rev-parse` stubbed to fail, it answers `('origin/main', 'origin/handoff/audit-r10-roster is absent in this clone (fetch it); reading origin/main, which lags the round's roster edits')`.
- **The stage comparison.** main against itself prints 0 differing lines; main against the branch prints 10.
- **Each Level 0 skip** has a twin one non-record file away that runs, and `fast` runs where the other lanes skip.

## Figures

At `f658e418a`:
- `python3 tests/closure.py selftest`: `ALL 122 closure shrink pins PASSED`. The O17 section holds 7 of them. `closure.rename_sites()` gives `([], [])`.
- `python3 tests/lane_skip.py self-test`: `54/54 pins passed`. Round 1 was 50.
- `python3 tools/audit/seat/roster_lib.py --self-test`: `18 checks, 0 failed`.
- `python3 -W error tools/audit/seat/orchestrator_tick.py --self-test`: `104 checks, 0 failed`.
- `python3 tools/audit/seat/state_docs.py --self-test`: `all checks passed`.
- `plan_table.py`, `resume_doc.py` and `handover_prompt.py --self-test`: 25, 14 and 13 checks, 0 failed.
- `python3 tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused, 0 stale allow entries`. The rename probe uses `throwaway_git_init`.
- The codeowners gap check (`--check`): `uncovered_files=0`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `dS +0.0000 NULL`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 41 policy file(s)`.
- `bash -n` on `prepr.sh`, `preflight.sh` and `handoff_push.sh` passes; `tests.yml` parses as YAML.
- **Divergence**, at 2026-10-18 13:00Z, origin/main `63816b857` and branch `07ba56db1`: `git show <ref>:dev/programme/rosters/wave-r10-groups.json | jq -r '.groups[] | "\(.group) \(.resume.stage)"' | sort` per ref, then `diff` and count the `>` lines. That gives 10; main against main gives 0.
- **Gate scope.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL`, since the diff touches gate files. The suite is CI's, under the owner's heavy-scripts rule.
- **PROJECTION, not a measurement, corrected in round 2.** On a roster or row PR after merge, Level 0 skips `browser` (4.0 min on #2380 `cdbca726`), `coverage` (0.8) and `typing` (1.5), plus `coverage-ratchet` (0.15), which needs `coverage`. That is about 6.4 runner-min per head, from the check-runs API's `completed_at - started_at`. Round 1 said 6.6. It wrongly counted `graders-head-copy` (0.2), which still runs.
  - Re-measure on the first such head: its `closure-scope` log prints `LANE: browser -- SKIP (level 0)`, and the three contexts conclude `skipped`.
  - This PR's own heads cannot show it, since its diff is not record-only.

## Unpinned sites

- **The `tests.yml` wiring** (`typing_skip`, `skiptyping`, typing's `needs` and `if:`, and the 6 `closure.py changed` call lines' shell around them). The census pins that no list site is porcelain. No local check drives a workflow. The proof is CI on this head, where every lane runs because the diff is not record-only, and the first record-only head after merge.
- **The roster-ref WARNING after a squash.** After each squash-merge to main, `default_roster_ref` notes that main carries roster changes the branch has not merged. It keeps noting that until main is merged back into `handoff/audit-r10-roster`. That is by design: the reader still reads the branch, and the note tells the reader that main may be ahead. It is noise on every tick in the window. Nothing pins how long it lasts.
- **Owed step: the state-docs beat restart.** The orchestrator restarts the beat on this code after merge, with no `--roster-ref`, so it watches the round branch. Until then the running beat (`--watch-ref refs/heads/main`, default roster ref) keeps its old behaviour: a roster-only edit regenerates nothing.
- **Owed after #2405 and this PR both land:** `codeql_scope.changed` delegates to `closure.changed_between`, so the list has one owner.

## Red checks

none

## Forward-carry

- The beat restart and the `codeql_scope` delegation, above. Both are owed steps for the orchestrator to dispatch after merge.
- The tick's unlanded-roster line is the coordinator's, in the tick seat.

## Friction

- The census's prose exemptions are exact per-file strings. A docstring or message that later quotes a porcelain `--name-only` diff needs its own entry, or the closure self-test goes red on an inert line. The census errs strict on purpose.
