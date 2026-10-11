The round-9 heavy-script consolidation pre-study
(`dev/audit/rounds/round9/prestudy/heavy-script-consolidation-prestudy.md`,
handoff `488aca6e1`) measured the push side paying 3 instrumented executions
of `boost_drift_replay.py` per merge and judged two consolidations SOUND
plus the CI ratchet tvofi asked for. This PR lands all three. Nothing here
skips a detector: both consolidations keep `closure.py check` running on
whatever recordings it grades, and both fail closed to a bare re-record on
any doubt — a wrong closure cannot survive longer than one merge (CLAUDE.md
rule 1), because every consumption re-derives its evidence from this run's
own tree.

**C2 — the batch proof's recordings, consumed by the last merge's push run.**
The proof's dispatch `closures` arm re-records every closure on tree P_n and
(a) now uploads them under a name carrying that tree hash
(`closure-recordings-tree-<hash>`, manifest `tree.txt` written by the same
checkout that recorded), and (b) the push `closures` job looks the artifact
up BY NAME for its own `HEAD^{tree}`, and `closure.py proof-consume` refuses
unless the manifest names this run's tree, every recording is loadable,
healthy and the set covers the whole selectable roster — refusing means the
full arm re-records, which is the fail-closed direction. Not the refused
recording cache: no answer crosses a tree, and the under-approximation
check runs unchanged on the consumed recordings. The nightly uploads
tree-named too, for the proof below.

**C1 — one composed tracer+audit-hook execution yields the line set AND the
read set.** `coverage_tree.sh` measures an allow-listed script
(`tests/composed_closures.json`, boost only) through `closure.py record`
with `COVERAGE_PROCESS_START` reaching the recording child, under the same
strace union the closures lane gets; the `closures` job (now `needs:
coverage`) downloads `composed-closures` from its own run and
`closure.py composed-verify` refuses on tree mismatch, rc, wrong argv or an
empty read set — a refusal consumes nothing. Every event still executes the
script once; nothing is stored across trees. `features.py` (#525), the
cheap-argv scripts and `dst_checks.py` are refused by name
(`CHEAP_ARGV_OR_ENV`), pinned in `closure.py selftest` and `entities.py`.
The byte-identity proof has two arms: `composed-proof` (PR, paths-gated to
the composition machinery — this PR runs it) measures bare, composed and
traced-only executions itself and compares read sets (`composed-compare`)
and line sets; nightly compares the artifacts free, since the nightly's
coverage composes and its closures records bare on one tree.

**The CI ratchet (tvofi's request, research-informed).** `tests/ci_ratchet.py`
+ `tests/ci_budgets.json` in `tests/structure.py`'s discipline: every metric
derived from measurement (never carried), one-way, `--record` needs a reason
and no job ever passes it. Inputs are emitted by the runs themselves
(`HPO_CI_METRICS` lines in `run.sh`'s scope decision, `derive_closures.sh`'s
`rec()`, `coverage_tree.sh`'s `measure()`, each carrying event and run id)
because a ratchet whose input is typed by a human is not a ratchet. Metrics:
the archscore vector (ratcheting `tools/audit/archscore`'s own number),
`script_runs_per_push`, `script_runs_full_case_pr` (scoping's honest form),
`critical_path_minutes` (median, budget recorded at window p75 for stated
headroom — shared-runner variance is the documented pitfall). Complexity
stays owned by `tests/structure_budgets.json`. A scoped-FRACTION ratchet is
deliberately absent: 33 of the last 60 merges are full-case BY DESIGN
(measured below), so a share ratchet would refuse legitimate merges.

Adopted from research: one-way exit-code enforcement with the threshold in a
committed data file the tool itself re-records (qntm.org/ratchets;
github.com/phenomnomnominal/betterer; github.com/justjake/eslint-seatbelt;
coverage.py fail_under, coverage.readthedocs.io); deterministic counts for
hard gates and generous tolerance on noisy timing (bencher.dev's shared-
runner variance figure); fitness-function gates in CI (Ford/Parsons/Kua,
*Building Evolutionary Architectures*); per-change cost derived from a
dependency closure (bazel.build/remote/caching). Rejected: base-relative
hosted targets (Codecov `target: auto`) — this repository's refusals are
committed data files; ML test selection (engineering.fb.com 2018) — the
measured-closure scoping already here is the auditable form; a scoped-share
metric — the measurement above refuses it.

## Head

476dac6e0df03375aadbf7f3b70add7757a12047 (origin/main a745200209b275c0f33dc2253af8c7757ffb8de2, taken 2026-10-11T08:34:00Z)

## Mutation proof

Each mutant: mutate the production predicate, run the pinning harness,
capture the failing check, restore (`git checkout --`); the mutant is the
predicate, not a tail appended past a return.

- C2, `tests/closure.py proof_consume`: `elif label != expect_tree:` →
  `elif False:` — `PYTHONPATH=tests/hastub python3 tests/closure.py selftest`
  prints `FAIL proof-consume refuses a manifest naming ANOTHER tree [rc=0]`
  (1 of 74 pins failed).
- C1, `tests/closure.py composed_verify`: `if rec.get("rc") != 0:` →
  `if False:` — same harness prints `FAIL composed-verify refuses a run that
  did not end (rc 1) and consumes nothing [rc=0]`.
- Ratchet, `tests/ci_ratchet.py compare`: `if cur > budget:` → `if False:` —
  `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `FAIL the CI
  ratchet's main() refuses a script-run count above its budget`.

Failing-first arms, the same predicates before the fix existed: the
proof-consume pin initially FAILED against the first implementation (`FAIL
proof-consume refuses an unhealthy recording [rc=0]` — the rc check was
missing; the production side gained it, not the test), and the ratchet's
green/red fixture (below) was demonstrated against an empty budget before
`compare` grew the growth branch.

## Null control

- The unmodified tree at each mutant passes every harness above
  (`ALL 74 closure shrink pins PASSED`, `ALL 2258 ENTITY CHECKS PASSED`).
- The ratchet at its own recorded count:
  `python3 tests/ci_ratchet.py --metrics-dir <53-run fixture> --runs-json <api listing>`
  → `ok script_runs_per_push: 53 (budget 53)`, rc 0; the same fixture plus
  one line → `GREW script_runs_per_push: 54 (budget 53)`, rc 1. One more
  instrumented run than the row allows is the whole distance between green
  and red.
- The shell wiring, both directions: `closure.py composed-list` prints
  `tests/boost_drift_replay.py`; `printf '%s\n' "$COMPOSED" | grep -qxF
  "tests/boost_drift_replay.py"` matches (coverage_tree.sh's membership
  predicate), the same pipeline does not match `tests/layout.py`; the
  `case` match in `derive_closures.sh rec()` SKIPs the consumed
  `tests/boost_drift_replay.py` and RECORDs `tests/stress.py`.
- Local composed-execution smoke (macOS, non-authoritative, mechanism only):
  `COVERAGE_PROCESS_START=<scratch rc> PYTHONPATH=<site>:tests/hastub
  python3 tests/closure.py record tests/layout.py --out-dir <scratch>`
  exits 0 with one process yielding the record
  (`"how": "audithook+sys.modules+coverage-tracer"`, rc 0) — the tracer
  reaches the recording child. The byte-identity authority is the
  `composed-proof` job's, on Linux, including this PR.
- `closure.py proof-consume` accepts a full-roster artifact whose manifest
  names the tree (rc 0, `consumed proof recordings`) — the acceptance side
  of every refusal above.

## Figures

Every number below is re-derivable by the command beside it; pre-study
figures are cited to their instrument (GitHub Actions logs, job ids), not
re-executed here.

- `PYTHONPATH=tests/hastub python3 tests/closure.py selftest` → `ALL 74
  closure shrink pins PASSED` (17 new: 11 composed/proof refusals and
  acceptances, the roster refusal, the committed allow-list seam rule).
- `PYTHONPATH=tests/hastub python3.13 tests/entities.py` → `ALL 2258 ENTITY
  CHECKS PASSED`; at origin/main the same command prints `ALL 2250 ...` —
  the 8 new checks are the ratchet's classification, wiring, budget-table
  refusal, main() growth refusal, its null control, the no-budget-row
  growth, the allow-list seam and the proof driver's wiring.
- `PYTHONPATH=tests/hastub python3 tests/structure.py` → `STRUCTURE RATCHET
  PASSED` (no budget moved; no `*_budgets.json` value raised anywhere).
- `python3 tools/audit/archscore/score.py --diff $(git merge-base
  origin/main HEAD)` → `Architecture score: dS +0.0000 NULL`.
- The budget table's derivations, at origin/main a74520020 (custom_components
  untouched by this branch, verified `git diff origin/main --stat --
  custom_components | wc -l` → 0): vector.measure via `sys.path.insert(0,
  'tools/audit'); from archscore import vector; vector.measure(Path('.'))`
  (16 metrics, recorded verbatim in tests/ci_budgets.json); selectable
  count 33 via `len(closure.selectable_scripts())`; coverage fast stage 20
  via coverage_tree.sh's DERIVED pipeline (`grep -oE 'run "\$PYTHON"
  tests/[a-z_]+\.py' tests/run.sh | sed ... | grep -vxE ...`, the exclusion
  list documented in that file); 33+20=53 recorded as the fail-closed worst
  case a push run emits before C1/C2 consumption is trusted.
- Scoped-fraction refusal measurement: `closure.affected` over the first-
  parent diffs of the last 60 merges (`git log --merges -60 --format=%H`,
  `git diff --name-only M^1 M`) → cases {skip 15, full 33, scoped 12}.
- `gh api repos/tvofi/heatpump_optimizer/actions/workflows/tests.yml/runs?event=push&branch=main&per_page=8`
  → completed push Tests runs of 58.7/60.2/44.2/61.3 min; critical-path
  budget 61.0 = p75 (60.4) rounded up, rule stated in the budget file.
- entities.py's closure re-record: `tests/derive_closures.sh --single
  tests/entities.py --record-only` (Darwin, sanctioned partial route) then
  `closure.py merge --in-dir ... --partial --allow-failures` → 234 → 259
  files, adding tests/ci_budgets.json, tests/ci_ratchet.py,
  tests/composed_closures.json and tools/coverage/composed_proof.sh; the
  union kept `tests/golden/card_claimed_drift.txt` (a strace-only file
  Darwin's hook did not see — the partial merge's never-shrink branch).
- The #1218 selection-cost note re-recorded in tests/deployment_shape.py:
  pairs ≥0.80 123 → **122 of 528** (406 comparable, 93 production files;
  derivation command in the entities check `resource_r5.py`'s predicate),
  and entities.py admitted as the third full-coverage closure — its
  archscore drive opens the package the way deployment_shape's recorder
  does. Re-recorded as the pin instructs, reason in the commit message.
- Savings figures (cited, pre-study §5, from Actions logs): C2 ≈ one full
  closures arm per batch (push-N closures 27 m 36 s, job 114309833831);
  C1 ≈ 3–5 h/day lane time (push coverage boost traced 2042/2869/2608 s
  AND closures recorded 1238/1839/852 s of the same script on the same
  trees, jobs 114309000372/114309441689/114309833904 and
  114309000519/114309441746/114309833831).

## Red checks

- `budget-raise-gate` is red at the head until tvofi approves it: the file
  `tests/ci_budgets.json` is NEW, and the gate reads its 22 initial values
  (16 archscore rows at main's measured vector plus the three counts) as 22
  raises (`None -> value`), because a pinned value is exactly what it cannot
  sign as routine. This is the initial record of the ratchet tvofi asked
  for, not a raise of any existing `*_budgets.json` (none of those files is
  touched; every existing value is unchanged). The cheaper detector — a
  new-file initial-record arm in `budget-raise-gate` that distinguishes a
  first record from a raise — would let an owner-blind first recording of
  one-way caps through, which is what the gate exists to prevent, so none is
  built; the standing cost is one owner review of this head.
- `none` further named as expected-red at the head. Left to CI by design and
  named unrun: the heavy lanes the FULL scope selects (`stress.py`,
  `golden.py` drift, `features.py`, `optimality.py`,
  `boost_drift_replay.py` itself) — MODE: FULL, the diff touches gate files,
  so the scoped gate cannot narrow; `mutation`'s killed-mutant pins
  (CI-only per the contract); the Linux-only arms (`composed-proof` self arm
  on this PR, the first nightly compare).

## Forward-carry

The C1/C2 headroom in `script_runs_per_push` (53 recorded vs 52 expected
once consumption is trusted, and one closures arm fewer per batch) is
tightened by the first deliberate `--record` after the first post-merge
batch lands — destination: the round-9 consolidation wave's roster entry
(`.claude/workflows/wave-3l-groups.json`, its `resume` field) alongside the
r1/R1 items already specified in the pre-study; nothing in this PR edits the
roster.

## Friction

`none`

## Architecture score

`dS +0.0000 NULL` — the diff touches no production file; the ratchet
records the vector's current values rather than grading a change to them.
