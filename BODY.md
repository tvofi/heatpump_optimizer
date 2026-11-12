main's instrument-self-tests refused `UNDER-SCOPED step prepr`: prepr.sh has run mutant_run.py since #3455 without the closure being re-recorded. This re-records the prepr entry in tools/ci/selftest_closures.json with `python3 -I tools/ci/selftest_scope.py record --step prepr` (Linux, strace, 896.7 s, 0 failed, 0 broken traces), written by the tool's own write_table. `selftest_scope.py` has no union path (`record --step` replaces one step's entry wholesale), so the recording environment is what keeps the entry complete: it was taken in a fresh `git clone --no-local` of the base with no `merge.*.driver` config, the state CI's `actions/checkout` has. The earlier recording ran where the session-start hook had already installed `merge.claimnotes` and `merge.ledgermerge`, so it never took the `session-start.sh --self-test` branch that installs them and missed three reads CI makes (the review's block). Root-cause trigger: #3455 changed what prepr.sh runs without re-recording; cheaper detector: run `selftest_scope.py check` in prepr/ci_predict when a gated step's script changes (not built here; prepr.sh belongs to R10-HOTFIX-PREPR-WC-PAD).

## Head

f24eed01d7bb6249f0c2ac66841ffc87dc58fe24 (base origin/main b737e88eee4f, merges cleanly with origin/main 4f3b94fb538a)

## Mutation proof

Revert tools/ci/selftest_closures.json to origin/main's b737e88ee table: `selftest_scope.drift` over the recorded prepr measurement returns `UNDER-SCOPED step prepr: files misses ['dev/audit/harnesses/mutant_guard.py', 'tools/audit/seat/mutant_run.py', 'tools/pr/figure_block.py']`; at this head it returns no prepr refusal.

## Null control

Same measurement, three tables through `selftest_scope.drift` (script: import selftest_scope; drift(table, {'prepr': recorded entry}, workflow_steps())): main b737e88ee prints the line above; the prior head 361040baf, which dropped .gitattributes, tests/env_drift.py and tools/merge/ledger_merge.py, prints `UNDER-SCOPED step prepr: files misses ['.gitattributes', 'tests/env_drift.py', 'tools/merge/ledger_merge.py']`; this head prints none. Entry diff against main's: files gain mutant_guard.py, mutant_run.py, figure_block.py and lose nothing; probes, dirs, run_sha, index, objects and git are equal to main's. The fresh clone had no driver config (`git config --get-regexp 'merge\..*\.driver'` rc=1) before the record. Limit stated: the full `check --traces` over CI's whole-job traces was not run (needs CI's traces), so the 0-refusal result is proven for prepr only; `selftest_scope.py static` prints 112 gated step(s), 0 problem(s).

## Figures

none

## Red checks

- `governance / instrument-self-tests`: red on ancestry heads ef579d9b (run 43146503710, job 130947499161), 4aa62003, e099eff6 and 0aed6ccb with `UNDER-SCOPED step prepr: files misses ['dev/audit/harnesses/mutant_guard.py', 'tools/audit/seat/mutant_run.py', 'tools/pr/figure_block.py']`. This is the defect this pull request cures, inherited from main (the prepr step's recorded closure is stale there), not the branch's own. The cheaper detector is the existing closure re-record check; none cheaper exists.
- `tests / fast (3.14)`: red at d2ab2743 (run 43004573627, job 130469580446) and 0aed6ccb (run 43026616895, job 130597172175) with `1 of 5237 FEATURE CHECKS FAILED` in tests/features.py (`FAIL combi_type_branch census`), reached through a main merge into the branch, not this diff; absent on later heads including fbbf3efd. No cheaper detector exists; features.py is the detector.
- `tests / mutation`: red at d2ab2743 (run 43004573627, job 130468964323) with `MUTATION TABLE REFUSED -- 2633 unpinned site(s) against 2626 at the ratchet base, 11 of them added by this diff`, from main fix commits merged in; cleared by the later ledger re-pins (49a45dd8). The standing detector is tests/mutation_table.py.
- `tests / mutation-autofix`: red at d2ab2743 (job 130494481820) with `mutation-autofix: skip-measure-failed -- THE REPAIR DID NOT HAPPEN`, the same unpinned sites as `tests / mutation` above; it reports the bot's refusal and has no cause of its own.
- `tests / nightly-status`: red on fbbf3efd (run 43151513140, job 130966474383) with `NIGHTLY FAILED: mutation-ledger (3), mutation-ledger-push, slow failed 1 night ago` (scheduled run 42934263129, conclusion cancelled, head d08ed31). It is not a required context, reads the last concluded nightly on main, and is outside this diff; the cause is a cancelled scheduled run, owned by the nightly lane.

## Forward-carry

- The root-cause countermeasure (run `selftest_scope.py check` in prepr/ci_predict when a gated step's script changes) is unbuilt and tools/pr/prepr.sh is not touched here. Carry: R10-HOTFIX-PREPR-WC-PAD

- `selftest_scope.py record` measures the recording seat's per-clone git config, so a seat whose hook already installed the merge drivers drops reads a fresh checkout makes, and any gated step that runs the session-start self-test can be narrowed the same way; `record` should run in a scratch clone with no `merge.*.driver` config or refuse while they are set, and a union path would also have made this repair mechanical. Every roster group that owned tools/ci/selftest_scope.py is done (R10-HOTFIX-SELFTEST-SCOPE-UNION, -HANG, R10-HOTFIX-PREPR-READSET), so this goes to the one live hotfix on the prepr self-test path. Carry: R10-HOTFIX-PREPR-WC-PAD

## Friction

none
