R10-RCA-MAIN-SELFTESTS-RED (topic r10-rca-main-selftests-red): the root-cause seat for main's `governance / instrument-self-tests`, which concluded `success` on no push from #3315 (`ba6fd7e8b`) to `57091a694`. It runs beside R10-HOTFIX-MAIN-SELFTESTS and changes no production code; the files are `dev/audit/rca/R10-RCA-MAIN-SELFTESTS-RED.md` and the delivery row `dev/programme/delivery/3410.md`.

- Causes, each reproduced: (2a) table drift in `tools/ci/selftest_closures.json`; (2b) `ref_privacy.added_lines`' `git show REV:path` on an absent side stats the worktree path, so its read set follows each push's diff; (2c) #3361's ungated step, red on #3361's own merged head and merged under a non-required job; (2d, found in the run logs) #3315's push-only arm first ran on `main` and failed there (strace install under no-new-privileges sudo, a skipped launcher, the 60-minute timeout) until #3375.
- Process state: **(c)**. Detection (`drift`), the stated repair ("commit that file") and the trigger (the tick's main-red brief) all ran; the hand repair is outrun by the merge rate, and `ci_predict.py` has no arm for `selftest_scope.py`'s own gating check.
- Cost test: countermeasure A (commit the measured table through the `record/autofix` route on a drifted push) and B (a `ci_predict.py` arm over `selftest_scope.wiring_gaps`) both pass; neither is built here. 2d: none, recorded with its numbers.

## Re-cut

Answers `Fix review: blocked 0884509a04003457eea9ae5d2777941ba9d00fe2 figure-wrong: phase P1 is 28 pushes with 24 cancelled, not 27 and 23`. Every figure in the document was re-derived at 2026-11-10T08:42Z and now prints its enumerator beside it (E1 to E6 name the multi-line ones). The block's figure is corrected everywhere it appeared: P1 is 28 pushes, 24 `cancelled` and 4 `failure` (section 1 table, 2d, section 5); 28 + 5 + 2 = 35 pushes fall in three phases, and the two in progress at the first read (`e3295ba46`, `0362916ac`) are a tail that has since concluded `failure`. The re-derivation found five more figures wrong, each corrected:

- Step additions after #3315: 4 PRs (#3345, #3350, #3375, #3361), not 3, so the ungated-step rate in section 5 is 1 of 4 (E5, and `wiring_gaps` at each).
- 2a's "the missed paths are files main added after the table was recorded" is replaced by E3's split: 37 missed file entries, 6 globs, and of 31 concrete files 4 absent at the last recording `a751546c5`, 27 present. The seat does not claim which side moved for the 27. Sections 3 and 5 now use the 4 (merged inside about 12 h) instead of "six paths by six commits".
- Section 4's post-recording probes and dirs (E4) fall under `beatd`, `dependency-graph-census`, `prepr`, `temp-or-machine-path` and `throwaway-git-helper`, not `policy-lint-mutants`. They are four directories merged after the recording, so tree drift on their face, not the push's own diff. The one established instance of shape 2 is `push-names-the-host`.
- The roster (E6) holds five main-red hotfix groups on this job, not four: R10-HOTFIX-UUTILS-SLEEP was missing.
- Re-timed: the artifact upload is 0.42 s from log timestamps (was 0.3 s), the self-test 0.53 s (was 0.79 s), `ci_predict.py` 2.2 s (was 3.1 s), one run each on this container.

The conclusions stand: state (c), A and B pass the cost test, and 2d gets no countermeasure.

## Head

`f25c518da25363c788ec35d71d69633fbf3933c0`, on merge base `0362916ac7c1daf994e042c41d79b7e4083414e3`; `origin/main` was at `5d09dedf6` at 2026-11-10T08:46Z (`git merge-tree --write-tree origin/main HEAD`: no conflict, so no merge). Every figure is a function of fixed commits and run ids, not of main's tip.

## Mutation proof

n/a: no production, test or check code changes; the diff is one RCA document and its delivery row. Countermeasure B's detector is demonstrated in the document (section 5) with a scratch probe calling the production `wiring_gaps`: 1 gap at `8652aa65c`, 0 at its parent `5ab6030d7`, 0 at `8652aa65c` with the step gated in scratch (reverted).

## Null control

- 2b: `strace -f -qq -e trace=%file git show <rev>:tools/audit/seat/gh_read_run.py 2>&1 >/dev/null | grep -c '"tools/audit/seat/gh_read_run.py"'` at `0362916ac`: 1 with `HEAD~400` (absent side), 0 with `HEAD` (present side).
- 2c: `python3 -I tools/ci/selftest_scope.py --self-test` at `5ab6030d7` prints `103 checks, 0 failed`; at `8652aa65c`, `103 checks, 1 failed`.
- Section 1's "no log holds `exists on disk, but not in` or `ref_privacy: REFUSE`": 0 over the 37 E2 logs, beside 8 `ref_privacy self-test:` lines in the same logs, so ref_privacy's output does reach them.
- E5: `wiring_gaps` 0 at `2b777aad7`, `b8f67a775`, `2cf0f129b`, `5ab6030d7`; 1 at `8652aa65c`.

## Figures

- `git rev-list --first-parent --count ba6fd7e8b^..0362916ac`: 37 pushes; `ba6fd7e8b^..3aac11dfb`: 28 (P1); `2cf0f129b^..5ab6030d7`: 5 (P2); `8652aa65c^..57091a694`: 2 (P3).
- E1 (section 1, a `gh api` loop over those commits' `ci.yml` push runs and their `governance / instrument-self-tests` job): 37 rows, 0 `success`; rows 1-28 `cut -f4 | sort | uniq -c`: 24 `cancelled`, 4 `failure`; rows 29-37: 9 `failure`.
- E2 (`gh api $A/actions/jobs/<job>/logs | grep -o 'selftest_scope check: .*'`, and the refusal-kind count): 39, 39, 39, 47 (P1's four), 37, 37, 37, 38, 38 (P2), 39, 38 (P3), 39, 46 (tail).
- Step-level reads (`gh api $A/actions/jobs/<job> --jq '.steps[]...'`): "Install strace" `failure` in all 28 P1 jobs; all 24 cancelled jobs stop in "Refuse a self-test read set the committed table misses".
- E3 (artifact 13737009763 against the committed table at `57091a694`): 37 missed file entries, 6 globs, 4 of 31 concrete files absent at `a751546c5`.
- E4: 23 probes/dirs lines absent at `a751546c5`, 20 over four directories under five steps, 3 a `-c` probe.
- E5: 4 step-count changes after #3315, `wiring_gaps` 1 only at `8652aa65c`.
- E6 (roster `handoff/audit-r10-roster` at `1f0ea2c27`, `jq` over `R10-HOTFIX` groups whose brief names the job): 6 groups, 5 main-red hotfixes on this job.
- `git diff --stat <c>^1 <c> -- tools/ci/selftest_closures.json` for `2b777aad7`, `b8f67a775`, `2cf0f129b`: 13, 16, 26 insertions, 0 deletions; `jq '.steps|length'`: 106 at `ba6fd7e8b`, 109 at `0362916ac`.
- `gh api $A/pulls/<n> --jq .merged_at`: #3315 2026-11-09T08:16:10Z, #3375 2026-11-10T01:47:42Z, #3361 2026-11-10T04:34:59Z; run 42758119155 `created_at` 2026-11-10T04:47:59Z (20.5 h and 17.5 h spans); #3393 `created_at` to `merged_at` 148 min.
- Class enumerator 2 (section 4): 23 files at `0362916ac`. `git grep -c "event_name == 'push'" -- .github/workflows`: 19 lines in 4 files; oldest arm `13aa7b189` 2026-08-26, 75 days before #3315.
- Wall clocks (`date +%s.%N` around one run): `selftest_scope.py --self-test` 0.53 s at `8652aa65c`, `ci_predict.py` 2.2 s; artifact upload 0.42 s from run 42758119155's log timestamps.
- `python3 tests/closure.py select --diff 0362916ac --workdir "$D"`: `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, over 2 changed files.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

## Red checks

- `gate`, ci.yml edit run 42771199407 attempt 1 (check run 129680025529), red at the previous head `0884509a0`: `FAIL run(s) [42771199429] at this head are still being judged; their gate decides`. The code run's `gate` (check run 129688172891) concluded `success` at that head. This is the deferral #3361's body answered. Cheaper detector: none. The deferral is the gate working as designed (an edit run does not grade what the code run grades), and the only earlier signal is the code run's own gate, the check being waited on. Standing cost of the alternative: one rerun of the edit run's attempt per deferral.

## Forward-carry

- Countermeasure A, the mechanical commit of the `selftest-closures` artifact on a push whose `drift` refuses only `UNDER-SCOPED` or missing-entry lines, through the `record/autofix` route. It changes `.github/workflows/` (code-owned), so it is a proposal for the owner, addressing state (c); its detector demonstration is owed by whoever builds it (section 5). Carry: dismissed: proposal for the owner, no stage brief changes before approval.
- Countermeasure B, a `tools/pr/ci_predict.py` arm predicting an `instrument-self-tests` red per `selftest_scope.wiring_gaps` gap on a diff touching `governance.yml`. Carry: dismissed: proposal for the owner, no stage brief changes before approval.
- Shape 2's instances (`ref_privacy.added_lines` behind `push-names-the-host`, and beatd's suspected timing-dependent read set) are the live hotfix's own items (its brief's FIX line and step 4); nothing new to carry. Carry: R10-HOTFIX-MAIN-SELFTESTS

## Friction

none
