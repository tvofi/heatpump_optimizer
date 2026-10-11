The scoped closures arm — the PR gate's critical lane and prepr step 6b —
recorded its scripts in a serial `while read` loop of
`derive_closures.sh --single`, one script at a time, so a scoped derivation
paid the **SUM** of the selected recordings: 51m18s over 24 scripts on #2071's
`closures` job (job `114030702792`), while the *full* arm's lane-balanced wall
is a lane **MAX** (27m57s, job `114153594029`, the same day) — the scoped arm
paid more than the full one for strictly less work. This is **R1** of the
round-9 merge-path pre-study
(`dev/audit/rounds/round9/prestudy/merge-path-wallclock-prestudy.md`, §5 and
§8's ordered recommendation), tvofi's top-priority performance change.

What lands:

- `tests/closure.py lane-plan`: shards the `affected.scripts` list across
  lanes by greedy longest-processing-time over the committed `recorded`
  seconds table. Every `PRODUCERS` pair (`plan_view.py` ahead of
  `tests/card.mjs` and `tests/card_drift.mjs`, the #1146 payload constraint)
  and every `DRIVEN_BY_OTHERS` pair (`dst_checks.py` behind its driver
  `features.py`) is kept inside ONE lane, in order; every other script keeps
  its input (suite) order inside its lane. The lane count is bounded by the
  owner's standing rule — **3 on a CI runner** (`CI=true`), **4 on a seat
  box** — overridable downward with `$DERIVE_LANES`; nothing is passed
  through the workflow.
- `tests/derive_closures.sh --scripts-from <file>`: asks `lane-plan` for the
  shard, then runs one background shell per lane file into the shared
  out-dir, with the per-script cheap argv/environment the serial loop used
  (golden/env_drift stub args, arch_score `--smoke`, dst_checks's
  `HASTUB_TZ`) factored into one `rec_special` both `--single` and the lanes
  call. A listed script that ends with no recording file refuses the run
  loudly. `--single` and the full-arm lanes are byte-unchanged in behavior.
- `.github/workflows/tests.yml`: the scoped branch of "Re-record the
  closures" becomes ONE `--scripts-from` call; the while-read loop is gone.
  This is the minimal wiring the fix needs — no lane count is passed to CI
  (the runner's `CI=true` gives the bound). The FULL arm is untouched: the
  sibling #2129 rebalances it, and the two edits do not overlap textually
  (verified against #2129's diff: its tests.yml hunks are closure-scope's
  diff derivation, its derive_closures.sh hunks are the full-lane layout,
  below my insertions).
- `tools/pr/prepr.sh` step 6b (`closures_line`): the recordable scoped subset
  goes to the recorder as ONE `--scripts-from` call under the four-slot local
  bound; the per-script `closure_lane` decisions (record here vs left to CI)
  are unchanged.

Safety property (CLAUDE.md rule 1) is untouched: which lane records a script
changes WHEN it is recorded, never WHAT it opens (R9-F10.15, the full arm's
own established result) — one recording file per script per out-dir, the same
invocations, the same `check --partial` afterwards. A wrong closure still
reddens the PR and, within one merge, main.

## Head

`80331a05a19928e927c0943deb827eda12045147` (branch
`fix/closures-lane-runner`, merge base `origin/main` = `6918cb4b213de`).

## Mutation proof

Three mutants, each restored before the push (head committed first; mutants
run on scratch copies, never committed):

1. **The lane split broken.** A sed inserts `wait $!` after each lane spawn
   (`sed 's/^    ) &$/    ) \&\n    wait $!/' tests/derive_closures.sh`), so
   lanes run one-at-a-time with the same plan. Six 2-second stub recordings,
   `DERIVE_LANES=3`:
   - head: `real 4.43s`; mutant: `real 12.18s` — regressed to the serial SUM.
   - serial control (`DERIVE_LANES=1` at head): `real 12.20s`. A second
     mutant (`&` deleted) crashes under `set -u` on unbound `$!` — loud, not
     silent. Selftest pin "two recordings ran at the same time (a lane MAX,
     not a serial SUM)" fails under both mutants.
2. **A lane drops a script.** A stub `lane-plan` deletes `tests/p2.py` from
   its lane file. At head the derive refuses: `no recording this run for:
   tests/p2.py ...`, rc=1. With the no-recording guard deleted
   (`sed '/if \[ -n "\$missing" \]/,/^  fi$/d'`), the same run exits 0 with
   five of six recordings — the mutant is exactly the hole the guard closes,
   and selftest pin "a script recorded by no lane fails the derive loudly"
   goes red under it.
3. **Step 6b regresses to the serial loop.** Reverting `closures_line` to the
   merge-base `--single` loop fails the new prepr self-test arm "and makes no
   serial --single call beside it" — shown failing at the merge base below.

## Null control

- **Failing-first arm, at the merge base** (`6918cb4b213de`): the base
  `closures_line`, driven over the self-test's scoped fixture (`cl`: a comment
  in `tests/wood_advisor.py`) with the call-logging stub, hands the recorder
  `--single` — the arm the head passes cannot pass there. Driver and output
  under ## Figures.
- **Serial-vs-serial recording comparison**: a second serial run of the same
  five scripts differs from the first in exactly the places the lane run does
  (per-run scratch paths inside `spawned` argv) and nowhere else — the
  serial-vs-lanes delta is the run-to-run delta, not a parallelism effect.
- `--single`'s own selftest pins ("the done line reports a recording's exit
  3/0") still pass at head: the refactor into `rec_special` did not change
  what `--single` runs.

## Figures

Head `80331a05a19928e927c0943deb827eda12045147` unless stated; merge base
`6918cb4b213de`. Local walls are upper bounds (this box ran sibling seats'
work during them); commands run from the worktree root.

- **The measured defect, from the pre-study (its numbers, cited not
  re-derived)**: scoped arm 51m18s serial over 24 scripts, `boost_drift_replay.py`
  27m13s of it (job `114030702792`); full arm lane MAX 27m57s (job
  `114153594029`); local prepr 34m24s of which ~30m is step 6b's serial loop.
- **The serial structure at the merge base** —
  `git show 6918cb4b213de:.github/workflows/tests.yml | grep -n -A4 'while read -r s'`:
  the scoped step's loop, `--single "$s"` per script; and
  `git show 6918cb4b213de:tools/pr/prepr.sh | sed -n '487,489p'`: prepr's own
  serial `--single` call.
- **Failing-first arm at the merge base**: base `closures_line` extracted
  (`awk` over the five functions it needs) from `6918cb4b213de`, driven over
  the scoped `cl` fixture with the self-test stub; the call log the recorder
  received: `--single` (one serial call per scoped script). At head the same
  driver's log holds only `--scripts-from`, and the arm passes in
  `prepr.sh --self-test`.
- **prepr self-test**: `PATH=$PWD/tools/audit/seat/shims:$PATH bash
  tools/pr/prepr.sh --self-test` → `249 passed, 0 failed` (includes the new
  arms "6b drives the scoped set through the --scripts-from lane runner" and
  "and makes no serial --single call beside it").
- **closure.py selftest**: `PYTHONPATH=tests/hastub
  tools/audit/seat/shims/seat-python3 tests/closure.py selftest` →
  `ALL 76 closure shrink pins PASSED`, including 19 new lane-plan pins
  (coverage, LPT balance, both ordering constraints from a consumer-first
  list, the CI/seat bounds and `$DERIVE_LANES`, the CLI over the live table,
  and the three bash-runner stub pins: recorded-exactly-once, overlap,
  loud-refusal).
- **Lane MAX vs serial SUM, stub recordings** (6 × `sleep 2`):
  `DERIVE_LANES=3` → `real 4.43s`; `DERIVE_LANES=1` → `real 12.20s`; the
  waited-out mutant → `real 12.18s`. Instrument: `/usr/bin/time -p env
  PYTHON=<sleep-stub> DERIVE_LANES=<n> bash tests/derive_closures.sh
  --scripts-from <six.txt> --record-only --out-dir <dir>`.
- **Real recordings, serial vs lanes** (five Python scripts —
  wood_advisor, doc_claims, plan_view, layout, structure; the .mjs pair
  records only under strace, i.e. on CI): serial `real 28.62s`, lanes
  (`DERIVE_LANES=3`) `real 12.08s`. Plan printed by the run:
  `lane 1 (17.3s recorded): tests/layout.py / lane 2 (10.4s): tests/structure.py
  / lane 3 (11.7s): tests/doc_claims.py, tests/wood_advisor.py,
  tests/plan_view.py`.
- **Recordings byte-identical modulo per-run noise**, rule: for each script,
  the recording JSON with `seconds` removed and scratch paths
  (`/(var/folders|tmp)/...`) normalized inside `spawned`, compared across
  serial / second-serial / lanes: all five scripts IDENTICAL in every field
  (`files`, `inert_reads`, `rc`, `argv`, `how`) except `layout.py`'s
  `spawned` — which differs identically between the two SERIAL runs (git
  scratch-index SHAs and mktemp paths), so it is run-to-run, not
  parallelism. Null control and comparison share one script over the three
  recording dirs.
- **`check --partial` verdict byte-identical**: over the serial and the lane
  recording dirs the verdicts are byte-equal (`diff` empty) and both green:
  `closure: committed closures cover every file this run touched`. The
  serial-vs-serial pair is byte-equal too (null control).
- **PREDICTION, not a measurement — the PR-gate wall 52m → ~31m.** Reasoning:
  the scoped wall becomes max(selected recordings) + setup instead of their
  sum; with `boost_drift_replay.py` (27m13s on #2071) on its own lane, the
  floor is that recording, matching the pre-study's §7 arithmetic
  (52→~31m). It is CONFIRMED ONLY BY CI: this pull request itself touches
  gate files, so `closure.py select` answers `MODE: FULL` and its own
  `closures` job runs the full arm — the proving run is **the first pull
  request after this merges whose diff is not a gate file**: its
  `Re-record the closures` step must print the lane plan, run
  `--scripts-from`, and the job wall must be ≤ max(selected recordings) +
  setup, on two such runs, with all recordings present and `check --partial`
  byte-unchanged (the pre-study's acceptance, restated). A local full
  derivation is forbidden off Linux (`gate-scoping.md`), so no local number
  can stand in for it.
- **Structure ratchet**: `python3 tests/structure.py` →
  `STRUCTURE RATCHET PASSED` (no metric moved; no budget file touched).
- **entities**: `PYTHONPATH=tests/hastub
  tools/audit/seat/shims/seat-python3 tests/entities.py` →
  `ALL 2250 ENTITY CHECKS PASSED`.
- **The constraint seams, enumerated by the instrument that owns them**:
  `PRODUCERS` (2 edges: card.mjs→plan_view.py, card_drift.mjs→plan_view.py)
  and `DRIVEN_BY_OTHERS` (1: dst_checks.py→features.py) in
  `tests/closure.py` — `lane_edges()` reads exactly those two maps, every
  seam it returns is dispositioned (same-lane, ordered, pinned from a
  consumer-first input list), and a future seam added to either map is
  enforced by construction because the planner reads the map, not a copy.

## Red checks

`none` at the head locally (selftest, prepr self-test, structure, entities
all green). Expected on CI, named in advance: this diff touches
`.github/workflows/tests.yml`, `tests/closure.py`,
`tests/derive_closures.sh` — all gate files — so the PR's own `closures` job
takes the FULL arm and `fast` answers `MODE: FULL`; that is the rule-1 price
of editing the gate, not a red. The cheaper detector for a broken lane
runner is the selftest's stub pins (overlap, coverage, loud refusal), which
run in `run_always` on every gate run at seconds of cost.

## Forward-carry

`none` — the coupling the pre-study ordered (PR #2129's (a1) batch arm must
land a scoped lane runner or a scoped batch proof pays the serial sum) is
discharged by this change itself: the dispatch arm takes the same
`SCOPE_CASE=scoped` branch wired here, and #2129's diff does not overlap
this one. #2129's `derive_closures.sh` rebalance and this runner compose:
different regions of the same file, merge-clean by inspection of both diffs.

## Friction

`none`.
