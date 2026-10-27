Fix review: blocked fa18c13d206e312e2fe959d825ffa04ed77025e3 budget-exceeded: step 6g measures 5.39-6.2 s wall on the fixer's own box against the 5 s per-check budget the brief binds, the body restated the budget to 8 s and 15 s after measuring, and the wall time --fill-red adds to every body_push is not stated

bus-nonce: 85ff6725b1fb64d5c0735d6df6a852f9

Review round: the second code head reviewed for this slice. The round note names the earlier head 5ab48352/819b82fb. Head measured: `fa18c13d206e312e2fe959d825ffa04ed77025e3` (ev/head.txt). `git ls-remote origin refs/pull/2853/head` read it again before this verdict was written: unmoved.

## Block

Carry 6 is the owner's ruling (tvofi, 2026-10-22): the body states each added check's measured wall time and the total added, and **refuses any addition over a budget it names. A lane too slow for that budget stays CI-only.** The brief binds the budget at at most 5 s wall per added check and at most 10 s added to any one prepr or body_push run, the figures the earlier body round named.

1. **Step 6g is over 5 s by the body's own measurement.** The body measures it at `5.39 s through the function and 6.2 s at most split by hand`. Instead of refusing it or listing 6g as CI-only, the body moves the budget to `at most 8 s wall per added check, and at most 15 s added to any one prepr or body_push run`, because on its box "6g takes up to 6.2 s". It calls this "a disclosed self-correction the orchestrator rules on". A budget raised after the measurement to admit the addition it was meant to refuse is not a correction. That is the move carry 6 forbids, and `ratchet-budgets.md` refuses the same shape for caps: never widened to fit a change. On this host 6g takes 15.41-16.29 s wall over three runs at load average 65-81 on 8 cores. That is 7.3 s of CPU time (user+sys 3.93+3.45 and 3.88+3.48), which is above 5 s even before contention. The body's split shows where the time goes: `git archive` takes 3.10-3.58 s of it.
2. **`--fill-red` added step 6d's predictor to every `body_push.sh` run without a wall figure.** The body's Figures say "a body_push gets `--fill-red` (step 6d's predictor) plus 0.19 + 0.38 s", which is not a measurement. Here `bash tools/pr/prepr.sh --fill-red` takes 10.34-18.79 s wall over five runs at load average 65-81, and 5.48-5.52 s CPU (user 4.17-4.26, sys 1.22-1.35). On CPU alone that is above the 5 s per-check budget, and with figure lint and ref_privacy it reaches about 6 s of the 10 s per-run budget. Neither figure is in the body.

**What clears it (any one, per check):** bring 6g under 5 s, for example by archiving only `claims.py`'s inputs (`git archive HEAD -- <the files it reads>`) in place of the whole tree, which the body's own split says costs 3.1-3.6 s. Or move 6g CI-only, listed as such under carry 6. Or get the owner's ruling for 8 s and 15 s. Also measure `--fill-red`'s wall time and state it against the budget, refusing or moving it if it is over. Every other check below verified.

## Findings

- 6g's trigger (`CLAIMS_DOCS`: `README.md`, `docs/*.md`) is narrower than what `dev/audit/rounds/round4/D6/claims.py` reads. It also reads `DISCLAIMER.md`, the package's `services.yaml`, `strings.json`, `translations/*.json` and `manifest.json`, plus `hacs.json`, `VERSION`, the card JS and `tests/entities.py` (claims.py lines 244-269). A diff to `strings.json` or the card can therefore move the register and still reach CI stale under `PREPR_SKIP_CLOSURES=1`, which is #2609's class. The slice builds carry 20 exactly as worded, so this is not a block. Carry: R10-FLOW-JIDOKA
- `docs/*.md` under bash `[[ $f == $p ]]` also matches nested paths: `docs/design/2026-09-05-away-plan-toggle/plan.md` runs 6g (ev/finding_nested_docs.txt), while claims.py globs `docs/*.md` top-level only. This is an over-trigger: each design-doc diff pays for a 6g run that grades nothing. Carry: R10-FLOW-JIDOKA
- The carried figure "6 of 152 handoff-body tips" (prepr.sh comment, and carry 8) cannot be re-derived now. Today's corpus is 88 `handoff-body/*` tips, and 11 of them fail `figure_lint.mjs --pr-body` in this tree (ev/carry8.txt has the enumeration). It is a snapshot in a code comment, not a body figure. Carry: dismissed: a carried snapshot whose window closed, not a claim this PR measures
- prepr-1, prepr-2 and prepr-6 are killed only by the self-test's call-site text rows (`case "$flow"`/`case "$bc"`), not by behaviour. The functions they call have behavioural rows: `privacy_line`'s refusal is killed by my m19 below. Carry: dismissed: the repository's call-site-row idiom (#1591), with the called functions pinned behaviourally

## Evidence

All files are under ev/. The no-voluptuous interpreter is a bare `venv --without-pip` built from Homebrew Python 3.13.15. Before each run, `python3 -c 'import voluptuous'` printed `ModuleNotFoundError: No module named 'voluptuous'` (ev/bare_python_voluptuous_refusal.txt, and the second line of each self-test log). Every self-test ran with `env -u BASH_ENV` and that interpreter first on PATH.

**instrument-self-tests reproduction (round note).** `bash tools/pr/prepr.sh --self-test`:
- At 5ab4835246614398074616eaaa301593359a1b61: `409 passed, 2 failed`, EXIT=2, with `FAIL 6g passes a docs diff whose register the generator rewrites byte-identical (null control) (got 1, wanted 0)` and `FAIL and names the stale files and the moved header RESULT (got 1, wanted 0)`, each after `ModuleNotFoundError: No module named 'voluptuous'` (ev/selftest_bare_wt-5ab.log).
- At the head: `412 passed, 0 failed`, EXIT=0, including `ok 6g's header parsers import without voluptuous or homeassistant (the governance job's python3)` (ev/selftest_bare_wt.log). Each run took 13 min 47 s wall under load.
- `## Red checks` names `governance / instrument-self-tests` with the fixing commit `eb898c9bb`.

**Diff size.** `git diff --stat $(git merge-base origin/main HEAD)...HEAD`: 5 files, 267 insertions, 13 deletions (280 lines), under the ~400-line cap (ev/diffstat.txt).

**The 22 carries:** ev/carries_table.md. All 22 are itemised in the body. Carry 6 is not honoured (## Block). `python3 -I tools/audit/carry_audit.py pr 2853`: `7 routed, 0 unrouted, 0 bad destination(s)`, rc 0 (ev/carry_audit.txt).

**Carry 19 (and 5), step 3f7 `privacy_line`, on the finder's instances.** Each instance was run in a shared clone with `origin/main` set to that pull request's base, using this head's `privacy_line` (ev/carry19_instances.txt):
- #2735 5a03e901 refuses (`dev/programme/triage/s6-batch5.md:9: home-directory, account-name, host-path ...`), and its fixed tip b0465583 passes (null).
- #2741 d367b16d and ca804c6d refuse (`s6-batch7.md:9`), and its fixed tip 77656132 passes (null).
- Mutant m19, with the ref_privacy call replaced by rc 0, passes 5a03e901 (ev/carry19_mutant.txt). The self-test row `privacy_line refuses a host path in an added line` is that mutant's killer.
- Planted mutant prepr-1: the row `step 3f7 runs privacy_line and refuses on its rc` goes from ok to FAIL (ev/mutant_rows_prepr-1_prepr-6.txt).
- Wall time: 1.52-1.98 s at load 65-81, and 1.06-1.10 s CPU. The body's 0.38 s unloaded figure is consistent with this.

**Carry 18, `WAVE_INPUTS`, on #2736 at fbbd3e61.** Its changed paths from its base e97f5749 are `dev/governance/dimensions/D11.md` and its delivery row (ev/carry18.txt):
- The old trigger's `git diff --quiet` gives rc 0, so the step is skipped: the defect. The old briefs glob matches 0 files, and roles plus dimensions match 33.
- `pinned_touched` against `WAVE_INPUTS` gives rc 0, so the step runs.
- Null: a README-only diff gives rc 1 (skip).
- Mutant, old glob restored: rc 1.
- Planted prepr-3, full self-test: `410 passed, 2 failed` (`a diff touching one role contract runs step 4's wave-script (P75)`, `and one touching a dimension brief`) (ev/mutant_selftest_prepr-3.log).
- `check-wave-script.mjs` takes 0.38-0.50 s.

**Carry 20, step 6g `claims_reg_line`, on #2609's red ff83a3d7 (check-run 119826108493).** Run with the seat venv (claims.py needs yaml) over a `git archive` copy (ev/carry20_instance.txt):
- ff83a3d7 refuses: `committed claims.json claims.md not what dev/audit/rounds/round4/D6/claims.py writes; re-run it and commit`.
- Null: #2609's merged head 97ac438d passes with `rewrites claims.json and claims.md byte-identical`.
- Mutant m20, with the comparison deleted, passes ff83a3d7.
- Planted prepr-5, full self-test: `411 passed, 1 failed` (`and names the stale files and the moved header RESULT`) (ev/mutant_selftest_prepr-5.log).
- Wall time: see ## Block.

**Carry 8, figure lint in `--body-check`.** Finder's corpus: of 88 `handoff-body/*` tips, 11 fail `figure_lint.mjs --pr-body`. The instance used is handoff-body/r10-heat-meter ce2d38d3, whose instrument is absent from the tree (ev/carry8.txt):
- This PR's body plus the instance's figure line: `REFUSE figures`, rc 1.
- The same body under mutant m8 (the rc is not propagated): rc 0.
- Null: this PR's body unchanged gives rc 0 with `FIGURES: 18 resolved, 3 not verified, 0 refused`.
- Planted prepr-6: the row `--body-check runs step 7a's figure lint and refuses on its rc (carry 8)` goes from ok to FAIL (ev/mutant_rows_prepr-1_prepr-6.txt).
- Wall time: 0.23-0.29 s.

**Carry 17, `fill_red`.** The grader is pr-contract's red arm, `policy_lint.mjs --pr-body --head <sha> --red mutation`, on this PR's body with `## Red checks` set to `none` and a 3-key site file. This is my fixture: no instance head with unpinned sites was rebuilt (ev/carry17.txt).
- Before: rc 1.
- No site: writes nothing, byte-identical, still rc 1 (null).
- With sites: one line is written and the grader gives rc 0. A second run is byte-identical.
- Mutant m17, the no-site guard deleted: writes `0 site(s)`.
- Planted prepr-8, full self-test: `408 passed, 4 failed` (the null-control rows) (ev/mutant_selftest_prepr-8.log).

**Mutation proof route.** The in-tree harness `r10_seat_selftests_mutants.py` was run in three worktrees (prepr-1/3, prepr-5/6, prepr-8/10). Each run died on its own 900 s step timeout during the unmutated baseline, with host load average 40-70 (ev/mutants_m1.log .. m3.log), so nothing came of it. I then planted the harness's own MUTANTS entries (exact strings) and ran the full self-test without a timeout. prepr-1 and prepr-6 were stopped by this seat at about 255 of 424 lines, at load average about 300. Their killing rows are text assertions, so I evaluated them directly as above. prepr-10 was not re-run here: the 5ab48352 red above is the same defect. CI's heavy runs were cited, never re-run: gate, mutation, closures and `fast (3.14)` are green at the head.

**Quantified body claims, nulls shown.** The 6g refusal, 3f7 refusal, WAVE_INPUTS and fill_red nulls are all shown above. Self-test 412/0 at the head and 409/2 at 5ab48352 were re-derived. I did not re-run: 384/0 at 5fb833930, the 4 min 33 s wall, the `408 passed, 4 failed` prepr-10 tree, and the prepr 24 min 53 s run. These are not verified.

**Scope and hygiene.**
- VERSION, the manifest, RELEASE_NOTES.md, both claim files and every `tests/*_budgets.json` are untouched (three-dot, ev/untouched.txt empty). No budget raise.
- `dev/programme/delivery/2853.md` is present.
- `ref_privacy --check`: 0 refused, 26 push-site files, so no push site was added.
- `throwaway_git.py --check`: 0 refused. `tmp_paths.py --check`: 0 refused. `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `git merge-tree --write-tree origin/main HEAD` against 149ce54a36bcf9e794d357e0ef69dc8af62f8eb8: rc 0 (ev/merge_tree.txt).
- `tests/entities.py` is not re-run (a gate script). It is cited from CI's `tests / closures` and `tests / fast (3.14)`, both green at the head.
- No Co-Authored-By, Claude, session or Generated trailer is on the authored commits.

**Check runs at the head** (ev/check_runs_head.tsv). The only red is `governance / delivery-status`: `DELIVERY STATUS OVERDUE ... overdue #2844 21b4552` (ev/delivery_status_log.txt). That grades main, and this diff adds only its own row, so it is not this PR's. `pr-contract` (started 10:54:23Z, after the last workflow concluded at 10:54:20Z) and `gate` are green. The earlier head's reds (instrument-self-tests, pr-contract and gate at 819b82fb) are named and answered under `## Red checks`, with a cheaper detector and its standing cost.

**Instruments of my own** (ev/fx.sh copied from the scratch tools dir) extract the slice's functions from a given prepr.sh. That let me run the finder instances and the m8, m17, m19 and m20 mutants against the head's own code.
