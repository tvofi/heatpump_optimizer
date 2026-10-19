Fix review: blocked b891dfa048a9e52bb782dd058415e286cf8efaf5 mutation-survivor: selftest_wiring.py report()'s `return 1 if unwired else 0` -> `return 0` leaves its --self-test green, so the keep-closed check can stop refusing an unwired file with every check green

bus-nonce: 183a396981f584e9080669c8b73792eb

Round: 1 (the PR had no `Fix review:` comments when this review ran). Measured head: b891dfa048a9e52bb782dd058415e286cf8efaf5 (ev/HEAD). I re-read it at 13:28Z and it was unchanged.
Contract: `dev/governance/roles/` has no diff between the merge base e8c67e1d3 and origin/main, so the contract is current.

## Blocking
- Step 1, mutation proof: the body names `selftest_wiring.py` as "the check that keeps this closed". Its refusal is the exit code of `report()`. I mutated `return 1 if unwired else 0` to `return 0`, and `--self-test` still printed `13 checks, 0 failed`. The self-test grades `check()` and never grades `report()`'s rc. Under that mutant, a tree with an unwired probe prints `1 unwired` and exits 0, so the CI step (`--self-test`, then the tally grep, then `--check`) passes. W1 to W3 in the PR's harness show rc=1 only with no mutant applied. No mutant on this line is in S01..S29, so nothing pins it. Evidence: ev/mutant_D.txt. Suggested fix, one arm: the self-test runs `report()` on an unwired fixture tree and asserts rc == 1. A null control asserts rc == 0 on a wired tree.

## Verified
- I ran the PR's harness `r10_seat_selftests_mutants.py` (it is the fixer's own: the finding came from #2433's body list, and no finder harness is committed; see step 9) at the head under the seat interpreter, CPython 3.14.7. M0 had all seat steps green. Mutants S01..S29 and W1..W3 were KILLED except S04 (daemonize.py), which gave `RESULT survivors=1`. S04 SURVIVED 3 of 3 times in this container, and was KILLED with `RESULT survivors=0` once run under `env -u PYTHONUNBUFFERED`. This container exports PYTHONUNBUFFERED=1, which makes daemonize's "-u prepended" check vacuous. That is an environment fact of the instrument, not a defect of this diff. The harness inherits that variable, so a seat whose environment sets it will read a false survivor. This is not blocking, and it should go to the harness or `daemonize.py`'s self-test. Evidence: ev/mutants.txt and ev/S04_rerun.txt. The body's S24 transient did not recur here; S24 was KILLED.
- Wiring: `selftest_wiring.py --check` at the head printed `37 self-testing, 37 wired, 0 unwired`, rc=0. My independent census found that all 37 self-testing seat files are named in `.github/workflows/`.
- Field-coverage fold, `r10_field_coverage_paths.sh`: at the head, `RESULT misread=0`. At origin/main e8c67e1d3 and at fb9b3fc1f, `RESULT misread=8`, with `tests/structure_budgets.json` reading RUN at both refs and README SKIPPED at both. This matches the body. Evidence: ev/field_coverage.txt.
- pr_args.sh: at the head, `46 checks, 0 failed`. c48f9632a's file gave `46 checks, 25 failed`, which matches the body's 25. Deleting the new `cp` line at the head gives `46 checks, 6 failed`: the fix is pinned, though the failure count differs from the parent file's because the && chain shifts.
- offline_spy on selftest_wiring.py and offline_spy.py: `2 files, 0 refused`. I did not re-run the spy's 29-file figure.
- Step 5: VERSION, manifest.json and RELEASE_NOTES.md are untouched (empty diff from the merge base).
- Step 13: `git merge-tree --write-tree origin/main <head>` exits 0. The driver printed `LEDGER-MERGE: resolved tests/closures.json` (inert_reads merged as a set). No other conflict.
- Step 11, CI from the commit's check-runs API (ev/check-runs.tsv, 13:28Z): every run is green or skipped except these:
  - `nightly-status`: red. The body's `## Red checks` names it and answers it: the cause is main's scheduled record-autofix 403, and the body says no cheaper detector exists.
  - `pr-contract`: two runs went red at 12:47 on that unanswered red (ev/pr-contract.txt). The later runs 118071638694 and 118071884697 started after the body edit at 12:57:12Z, and both are green.
  - `instrument-self-tests`: green at this head.
  - `closures`: success.
  - `composed-proof`: started 13:28:07Z and was still in progress when this verdict was written.
- Step 7: the head named in the body's `## Head` section is b891dfa04, the head I measured.

## Not re-derived
- I did not re-run the body's CPython 3.12.14 figures (`32 KILLED`, the 29-file spy run), its job-time figure, or its 7-unwired class census outside tools/audit/seat/. Those numbers are unverified here.
- I did not re-run gate scope. The forward-carries name R10-CI-LAYOUT and R10-BRIEFS-FOLD, and I did not open those briefs (step 10). They are unchecked.
