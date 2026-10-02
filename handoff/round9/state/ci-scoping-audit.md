# CI script scoping audit (2026-10-01, revised over the last 20 successful PR runs)

Question (tvofi): is CI script scoping correct, and does every slow script need to run on every PR where it ran?

**Sample.** The 20 most recent successful `Tests` runs on pull requests: 11 PRs (#1799–#1810), 2026-09-30T21:31Z to 2026-10-01T12:48Z.

**How each run was re-derived.** For each run:
1. Take the run's head and the merge-base with the main commit current at the run's start.
2. Run `closure.py affected` and `closure.py select --json` from that head's own tree, so each run is judged by its own closures, as CI judged it.
3. Read job minutes from the Actions API.

Per-run rows are in the table at the end. The scripts that produced them are in this thread's scratchpad, not in the tree.

## Verdict

The `fast` gate's scoping is correct. In all 20 runs it ran only scripts whose measured closure the diff reached, or else ran FULL because of a stated rule. No merge of main into a branch ever widened a diff: `fast`, `closure-scope` and `mutation` all diff against the merge-base. `mutation` mutated nothing on the 9 runs with no production `.py` change (0–1 min), which is correct.

Five places still run work that could not change the answer:

| # | What | Runs affected (of 20) | Cost | Cause | Safe to tighten? |
|---|---|---|---|---|---|
| 1 | `fast` runs FULL (all 28 scripts) when `tests/closures.json` changes, even when the diff otherwise reaches few scripts | 5 (#1803 ×3, #1799, #1800 fc16a761) | 28–32 min per run on #1803 and #1800. Re-derived under the rule below, #1803 needs 5 scripts and #1800 needs 20 | Rule too wide: `closures.json` is in `GATE_FILES` | Yes (see below) |
| 2 | The `closures` job re-records all 30 scripts because `tests/dst_checks.py` changed | 6 (#1804 ×2, #1808 ×2, #1809 ×2) | 12–22 min, against 6–13 min for scoped runs of similar size. Runner time, not wall clock | Rule too wide: `DRIVEN_BY_OTHERS` forces FULL, because the audit hook cannot see subprocess reads | Yes, after F10.3 |
| 3 | `harness_headers.py` runs although no changed file is in its 220-file closure | 9 | 95–183 s of `fast` per run | Always-run rule (`run_always`, #983, owner-approved) | Needs tvofi |
| 4 | `coverage` runs all 16 coverage-stage scripts whatever the diff | 20 (only 2–4 of the 16 were reachable on 6 runs) | 15–32 min every run. It was the slowest job on #1801 (22 min against `fast`'s 5) and #1802 (15–17 against 11–12) | No scoping at all in `coverage_tree.sh` | Yes, but it needs per-script coverage from main |
| 5 | The NOT RUN block says `harness_headers.py` and `layout.py` "did NOT run" on runs where both ran | every scoped run | No time; it is a false statement in the gate's output | `select`'s skip list ignores `run_always` | Yes |

**Correction to my first reply.** I proposed skipping `coverage` when no coverage-stage script is reachable. That case occurred in none of these 20 runs: every one reached at least 2 of the 16 scripts. It only helps docs-only PRs such as #1794. Item 4 is the version that would pay off.

Not scoping errors, but worth knowing:
- **Wall clock is mostly `mutation` and `fast` on code PRs.** `mutation` ran 19–56 min, and up to 98 min on two failed #1808 runs. It runs every in-scope driver's baseline before the first mutant: 17.4 min on #1806, where `features.py`'s 712 s baseline killed nothing. A lazy-baseline change (only `stress.py` is deferred today) is a separate, riskier job for the mutation instrument.
- **Seven FULL `fast` runs are rule-driven.** Two are gate-code edits (#1810 changes `closure.py`), and those are right. The other five are item 1.

## The tightenings, and why each is safe

1. **Treat a `closures.json` edit as changing only the scripts whose entries changed.** Run every script whose closure entry differs from the merge-base, plus the normal selection for the rest of the diff.
   - *Why it is safe:* a script whose entry is unchanged has the same skip claim it had on main, and main's push still runs FULL. A shrunken entry (the way to hide a dependency) is a changed entry, so that script runs.
   - *Applied to the sample:* #1803 drops from 28 scripts to 5, and #1800 fc16a761 from 28 to 20. #1799 changes 16 entries and still runs 22.
   - *Scope:* it applies to `fast` only. The `closures` job should keep re-deriving in full when `closures.json` changes.
   - *Bonus:* this also cheapens the re-check that follows every `ci: re-record closures` autofix commit.
2. **Re-derive `features.py` (plus `dst_checks.py`'s own lane) instead of everything when `dst_checks.py` changes.** This depends on F10.3 (#1810): its strace union records Python children, so a `--single tests/features.py` recording sees what `dst_checks.py` reads.
   - *Proof required before the change:* on the F10.3 head, that recording must contain every file the full lane's `dst_checks.py` recording does, `HASTUB_TZ` included.
   - *Backstop:* main's full re-derive.
3. **Return `harness_headers.py` to `run` after F10.3.** The reason given in #983 (a subprocess blind spot) is closed by strace, except for the five INERT files its children read. Main's FULL run catches those. This reverses an owner-approved decision.
4. **Coverage per script.** Main's push run uploads per-script coverage data. A PR then measures only the reachable coverage-stage scripts and combines that with main's data for the rest.
   - *Why it is safe:* the same closure argument as the gate, with main's unscoped run as the backstop.
   - *Saving:* most of the job on light diffs.
   - *Cost:* more machinery than items 1–3. The shared cache is keyed on the merge-base, as `env_drift` already does.
5. **Fix the NOT RUN block.** Leave `run_always` scripts out of `scope.skip`, or label them "always run".

## Recommendation

One fixer seat, after #1810 merges, does items 1, 2 and 5. All three are gate-code changes, so that PR runs FULL and gets an opus review. Item 3 goes in only with tvofi's word. Item 4 and lazy mutation baselines are separate follow-ups.

## Per-run data

`fast` = minutes [mode, scripts run/skipped]. `hh-skippable` = `harness_headers.py`'s closure was untouched. `cov` = minutes [coverage-stage scripts reachable/16]. `mut` = minutes [production .py files changed]. `closures` = minutes [case].

| PR | head | files | fast | hh-skippable | cov | mut | closures | FULL reason |
|---|---|---|---|---|---|---|---|---|
| #1808 | c447cf9d | 38 | 30 [scoped 25/3] | no | 17 [15] | 30 [8] | 22 [full] | dst_checks.py |
| #1809 | 5ef09d8a | 19 | 20 [scoped 16/12] | yes | 18 [12] | 19 [4] | 18 [full] | dst_checks.py |
| #1810 | b28b7ed2 | 13 | 18 [full 28/0] | – | 18 [4] | 0 [0] | 28 [full] | closure.py (gate) |
| #1808 | 3fc6e231 | 37 | 30 [scoped 25/3] | no | 18 [15] | 56 [8] | 17 [full] | dst_checks.py |
| #1809 | e52f5970 | 18 | 14 [scoped 16/12] | yes | 22 [12] | 40 [4] | 21 [full] | dst_checks.py |
| #1810 | 51f4bcb4 | 13 | 33 [full 28/0] | – | 17 [4] | 0 [0] | 29 [full] | closure.py (gate) |
| #1806 | 57eecef0 | 21 | 30 [scoped 21/7] | no | 15 [13] | 31 [4] | 17 [scoped] | |
| #1804 | 733f6f35 | 8 | 18 [scoped 16/12] | yes | 23 [12] | 20 [2] | 17 [full] | dst_checks.py |
| #1805 | 3bf9c454 | 13 | 17 [scoped 18/10] | yes | 22 [13] | 27 [2] | 11 [scoped] | |
| #1804 | e26fa13b | 8 | 16 [scoped 16/12] | yes | 25 [12] | 29 [2] | 12 [full] | dst_checks.py |
| #1805 | e54fb07a | 13 | 10 [scoped 18/10] | yes | 32 [13] | 33 [2] | 11 [scoped] | |
| #1803 | f720ee90 | 8 | 32 [full 28/0] | – | 21 [3] | 0 [0] | 21 [full] | closures.json |
| #1803 | 1bb04b29 | 8 | 29 [full 28/0] | – | 17 [3] | 0 [0] | 16 [full] | closures.json |
| #1803 | b0a69c90 | 8 | 30 [full 28/0] | – | 23 [3] | 1 [0] | 21 [full] | closures.json |
| #1802 | 7a1567fe | 6 | 11 [scoped 7/21] | yes | 17 [4] | 0 [0] | 6 [scoped] | |
| #1802 | 6d9a0f3d | 5 | 12 [scoped 7/21] | yes | 15 [4] | 0 [0] | 9 [scoped] | |
| #1799 | 65814159 | 40 | 16 [full 28/0] | – | 21 [14] | 29 [6] | 20 [full] | closures.json |
| #1800 | fc16a761 | 7 | 28 [full 28/0] | – | 22 [11] | 0 [0] | 20 [full] | closures.json |
| #1801 | 9b7eddb5 | 13 | 5 [scoped 6/22] | yes | 22 [2] | 0 [0] | 1 [scoped] | |
| #1800 | 83640d4e | 6 | 31 [scoped 20/8] | yes | 16 [11] | 0 [0] | 13 [scoped] | |
