_Requested by **tvofi**_

O17 item 1 (tooling) and item 2(ii), from the roster-cost pre-study the orchestrator accepted on 2026-10-18 (tvofi asked to keep the roster and state docs from costing CI). Part of #201. No roster group lists an issue for this work, so this body closes none. Item 1's policy half, the landing triggers, is `handoff/r10-roster-carry-policy`. Item 2(i), CodeQL, is `handoff/r10-codeql-lang-skip`.

**Owner gate.** `.github/workflows/tests.yml` and `tests/lane_skip.py` are code-owned, so tvofi approves this at merge. The seat tools under `tools/audit/seat/` have no owner.

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

## Head

`6eb3ec5952278dc9b44ca79ba97c73b4855e4601`, two commits on origin/main `63816b857` (`git fetch origin main` at 2026-10-18 13:00Z: unmoved).

## Mutation proof

Each mutant edited one file in place in the worktree (committed first), ran the named self-test, and was restored with `git checkout --`.

- **MB1: the absent-branch check in `default_roster_ref` disabled.** `python3 tools/audit/seat/roster_lib.py --self-test` prints `18 checks, 1 failed`: `no round branch here: main, and the note says the branch is absent`.
- **MB2: the tick reads `(rl.MAIN_REF, "")` instead of `rl.default_roster_ref(self.git)`.** `python3 -W error tools/audit/seat/orchestrator_tick.py --self-test` prints `104 checks, 2 failed`: `PLAN default roster ref: the round branch present: it is read` and `... the note says the branch is absent`.
- **MB3: the beat's memo is main's tip alone.** `python3 tools/audit/seat/state_docs.py --self-test` prints `8 self-test check(s) failed`, among them `arm 2b: exactly one push`, `arm 2b: the pushed plan carries the roster's new stage` and `arm 1: the tip is recorded, main's and the roster ref's`.
- **MB4: `plan_table.py`'s `reader_ref` line removed.** The same self-test prints `2 self-test check(s) failed`: `arm 5: plan_table.py with no --roster-ref reads the round branch` and `... with the branch absent reads main, and says so` (it crashes on `None:`).
- **MB5: Level 0's guard disabled.** `python3 tests/lane_skip.py self-test` prints `44/50 pins passed`: the six `<lane> skips a ... diff at level 0` pins.
- **MB7: the lane test dropped, so `fast` takes Level 0.** The same self-test prints `48/50 pins passed`: `fast never skips at level 0` and `fast still takes level 1 on a record diff`.
- **MB6': the pattern's end anchor `\Z` dropped.** The same self-test prints `47/50`: `<lane> runs on dev/programme/delivery/2380.md.bak`.
- **MB6, the `".." not in path` clause deleted, SURVIVED** (`50/50`). The anchored pattern already refuses every `..` path, so the clause was dead. Commit `6eb3ec595` removes it, and its pins stay, now on the pattern.
- **Failing first.**
  - `roster_lib.py --self-test` and `lane_skip.py self-test` with the new arms over the old code raised `NameError` (`git_in`, `RECORD_INERT_LANES`).
  - `state_docs.py --self-test` with the new beat arms over the old beat printed `8 self-test check(s) failed`, among them `arm 2b: exactly one push (got: 2)`.

## Null control

- **The live repository at origin/main `63816b857`.** `roster_lib.default_roster_ref(roster_lib.git_in('.'))` answers `('origin/handoff/audit-r10-roster', '')`: the branch has merged every roster change main holds, so no note. With `rev-parse` stubbed to fail (the branch absent), the same call answers `('origin/main', 'origin/handoff/audit-r10-roster is absent in this clone (fetch it); reading origin/main, which lags the round's roster edits')`.
- **The stage comparison's own control.** main against itself prints 0 differing lines; main against the branch prints 10.
- **In each self-test, every positive has a negative beside it.**
  - Each Level 0 skip has a twin one non-record file away that runs.
  - `fast` runs where the other lanes skip.
  - Beat arm 2 shows nothing written when neither tip moved; arm 2b regenerates when only the roster moved.
  - Arm 5 reads the branch and, with the branch removed, reads main and says so.

## Figures

- `python3 tools/audit/seat/roster_lib.py --self-test`: `18 checks, 0 failed`.
- `python3 -W error tools/audit/seat/orchestrator_tick.py --self-test`: `104 checks, 0 failed`; base `100 checks`.
- `python3 tools/audit/seat/state_docs.py --self-test`: `state_docs self-test: all checks passed`.
- `python3 tools/audit/seat/plan_table.py --self-test`, `resume_doc.py --self-test` and `handover_prompt.py --self-test`: 25, 14 and 13 checks, 0 failed.
- `python3 tests/lane_skip.py self-test`: `50/50 pins passed`.
- **Divergence.** Measured at 2026-10-18 13:00Z, origin/main `63816b857`, branch `07ba56db1`: `git show <ref>:dev/programme/rosters/wave-r10-groups.json | jq -r '.groups[] | "\(.group) \(.resume.stage)"' | sort`, with one file per ref, then `diff` the two and count the `>` lines. Main against the branch gives 10; main against main gives 0. The rule counts a group-stage pair on the branch and not on main.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`. `python3 tools/audit/archscore/score.py --diff $(git merge-base origin/main HEAD)`: `Architecture score: dS +0.0000 NULL`. `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s)`.
- **Gate scope.** `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)` prints `MODE: FULL`, because the diff touches `tests.yml` and `tests/lane_skip.py`, both gate files. The suite is CI's, under the owner's heavy-scripts rule.
- **PROJECTION, not a measurement.** On a roster or row PR after merge, Level 0 skips `browser` (4.0 min on #2380 `cdbca726`), `coverage` (0.8) and `typing` (1.5), plus `coverage-ratchet` and `graders-head-copy`, which need `coverage` (0.15 and 0.2). That is about 6.6 runner-min per head, from the check-runs API's `completed_at - started_at`.
  - Re-measure on the first such head: its `closure-scope` log prints `LANE: browser -- SKIP (level 0)`, and the three contexts conclude `skipped`.
  - This PR's own heads cannot show it, since its diff is not record-only. That is the full-diff arm, and every lane must run there.

## Unpinned sites

- **The `tests.yml` wiring** (`typing_skip`, `skiptyping`, typing's `needs` and `if:`). No local check drives a workflow. The proof is CI on this head (typing runs, since the diff is not record-only) and the first record-only head after merge (typing skipped).
- **The live beat.** The orchestrator restarts it on this code, with no `--roster-ref`, for it to watch the round branch. Until then, the running beat (`--watch-ref refs/heads/main`, default roster ref) keeps its old behaviour.

## Red checks

none

## Forward-carry

none. The tick's unlanded-roster line is the coordinator's, in the tick seat (its instruction). The landing triggers are `handoff/r10-roster-carry-policy`.

## Friction

none
