R10-FLOW-JIDOKA, second slice: error-proofing in `tools/pr/prepr.sh` before the handoff. Refs #2428. The first slice merged as #2838. This slice builds five of the group's roster carries (19, 18, 20, 8, 17), the cheapest ones with a measured instance each. Every addition is a quick, deterministic check, as the owner ruled on 2026-10-22 ("only quick checks"). Each check's wall time is under `## Figures`, against a budget named here: **at most 5 s wall per added check, and at most 10 s added to any one prepr or body_push run.** Nothing added is over budget. The base-pinned replay (carries 4, 7, 9, 16) stays CI-only in this slice and is carried; see `## Forward-carry`.

- **Step 3f7, `ref_privacy --check` (carry 19, triage s6-batch9 P78; also answers carry 5).** The new function `privacy_line` runs `python3 -I tools/audit/seat/ref_privacy.py --check`, the same command `instrument-self-tests` runs. It judges every line the diff adds for a host path, and every push site for its PUSHERS entry. It reads the diff from the merge base, never the whole tree. prepr never called it (`git log -S'ref_privacy.py --check' origin/main -- tools/pr/prepr.sh` prints nothing), so there is no earlier fixer cut that would have had it. A refusal carries the tool's own `file:line: host-path ...` lines. `--body-check` runs it too, over the code head being handed off, so `body_push.sh` refuses such a head before the body push.
- **Step 4's wave-script trigger reads the moved briefs (carry 18, P75).** The trigger list is now `WAVE_INPUTS`, matched by `pinned_touched` (the matcher step 3f already uses) over the three-dot changed-path list. The dead pre-move briefs glob is replaced by `dev/governance/roles/*.md` and `dev/governance/dimensions/*.md`, the two directories `briefListing()` in `tools/policy/check-wave-script.mjs` reads. The retired `.claude/workflows/check-wave-script.mjs` entry is dropped: the file is not in the tree, and the layout guard refuses a new line citing it. If the changed-path list does not derive, the step runs, as `! git diff --quiet` did before.
- **Step 6g, the D6 claims register (carry 20).** When the diff touches `README.md` or `docs/*.md`, `claims_reg_line` copies HEAD with `git archive` and runs `dev/audit/rounds/round4/D6/claims.py` on the copy. It refuses if the generator fails, if the generated `claims.json` or `claims.md` differs from the committed one, or if a header `RESULT` moved. This is `tests/harness_headers.py`'s dirty-register arm plus its header comparison, using its own `expected_from` and `printed_from`. It runs whether or not `PREPR_SKIP_CLOSURES` is set, which is the gap #2609 fell through. The generator writes into the tree it runs in, so it runs on a copy, and the seat's worktree is never rewritten.
- **Figure lint at body push (carry 8).** `--body-check`, the call `body_push.sh` makes, now runs step 7a's `figures_check` on the body and refuses on its rc. That is the same `figure_lint.mjs --pr-body` that `pr-contract` runs, and it is a function of the body alone.
- **`--fill-red` (carry 17, P67).** `prepr.sh --fill-red <body>` runs step 6d's predictor over HEAD. When it lists unpinned sites and `## Red checks` does not contain `mutation` (policy_lint's own test, a substring), `fill_red` writes one line: ``- `mutation` at <head>: red by construction on the N site(s) under `## Unpinned sites`; mutation-autofix pins killed sites after the push.`` A bare `none` in the section is replaced, and any existing answers are kept above the line. Otherwise it writes nothing, and it never refuses. `body_push.sh` runs it on the body before the `--body-check` lint. `open_pr.sh` gets no second call site: it reads the body from `handoff-body/<topic>`, which `body_push.sh` has already filled. The triage's "pay the lines by deleting" applies to a budget, and `tools/pr/prepr.sh` has none: no `*_budgets.json` key or `policy_lint.mjs --budgets` row names it. No budget is raised.

Alternatives considered:
- (a) For 6g, run the whole `tests/harness_headers.py`. It took 2 min 26 s here, over the budget, because it executes every live harness. The slice runs the one generator #2609's instance moved.
- (b) For 6g, run `claims.py` in the worktree and read `git status`, as harness_headers does. That rewrites a seat's uncommitted register. The copy grades the committed tree, which is what CI grades.
- (c) For step 4, add the two globs to the existing `git diff --quiet` pathspec list. The list would then have no name a self-test can drive. `WAVE_INPUTS` is driven by three rows and pinned at its call site.
- (d) For `--fill-red`, also call it from `open_pr.sh`. That is a file R10-FLY-OPENPR-ATOMIC edits, and it adds no case: the body it opens is the one `body_push.sh` filled.

The group's 22 roster carries, one line each:
- 1, the Lean pre-study's section K2: these five are its cheapest stops; the rest are routed below.
- 2: (a) no seat-selftest mutant is added; (b) no new git repository is built; (c) no push site is added, and `ref_privacy --check` reports 0 refused; (d) `## Red checks` names `nightly-status`.
- 3: moved to R10-FLY-CARRY-DISPOSITION by revision 15; nothing here.
- 5 and 19: built, step 3f7. 6: honoured, with the budget above. 8, 17, 18, 20: built.
- 4, 7, 9, 10, 11, 12, 13, 14, 15, 16, 21, 22: not built, routed under `## Forward-carry`.

## Head

`5ab4835246614398074616eaaa301593359a1b61`. Its merge base is `df478d40be4b546a7aaad150a5d9132483534a3a`, the tip this seat was dispatched at. origin/main is at `11b7a9d739db46a5a62e9f9cf01a8f527a974137` as read at 2026-10-26T05:34Z. `git merge-tree --write-tree origin/main HEAD` reports no conflict, and main's 27 changed files since the merge base are delivery rows, the roster and mutation-ledger records, none of which this diff touches. So no merge was made (fixer.md step 6). Commits: `002a963a8` (the five carries) and `5ab483524` (step 4's list cites no retired path: one comment and one list entry, after the predictor flagged both as `LAYOUT new-reference`).

## Mutation proof

Each mutant was applied by a scratch script, out of tree, in a detached worktree at `002a963a8`. A mutant whose pattern did not match exactly once was refused and not run. The full `bash tools/pr/prepr.sh --self-test` ran once per mutant. Unmutated at that commit: `411 passed, 0 failed`.

- MA, step 3f7's call replaced by `PRIVACY_LINE=""`. 1 failed: "step 3f7 runs privacy_line and refuses on its rc".
- MB, `--body-check` not propagating `privacy_line`'s rc (`[ "$r" -ne 0 ] || r=$vr` deleted). 1 failed: "--body-check runs privacy_line and refuses on its rc (P78)".
- MC, `WAVE_INPUTS` with the two governance globs put back to the old dead briefs glob. 2 failed: "a diff touching one role contract runs step 4's wave-script (P75)" and "and one touching a dimension brief".
- MD, step 6g's `claims_reg_line` call replaced by a skip (`CLAIMS_REG=""; (exit 3)`). 1 failed: "step 6g runs claims_reg_line and refuses on its rc".
- MD2, the register comparison deleted from `claims_reg_line`, leaving only the header arm. 1 failed: "and names the stale files and the moved header RESULT".
- ME, `--body-check` not propagating the figure lint's rc. 1 failed: "--body-check runs step 7a's figure lint and refuses on its rc (carry 8)".
- MF, `body_push.sh`'s `--fill-red` call deleted. 1 failed: "body_push runs --fill-red on the body before the --body-check lint".
- MF2, `fill_red`'s already-named guard deleted. 2 failed: "a body already naming mutation is left alone" and its "byte-identical" row.
- MG, `fill_red`'s no-site guard deleted. 4 failed: the null-control rows (writes nothing, byte-identical, the mutation red stays refused) and "fill_red writes the mutation line when step 6d listed sites".

Result: 9 planted, 9 killed. The kill rule is "the self-test's summary reports one or more failures".

## Null control

- **Self-test count.** `bash tools/pr/prepr.sh --self-test` prints `384 passed, 0 failed` at the merge base `df478d40b` and `411 passed, 0 failed` at `002a963a8`. The slice adds exactly 27 `st` rows: 11 for `fill_red` and `--fill-red`, 3 for `privacy_line`, 3 for `WAVE_INPUTS`, 5 for `claims_reg_line`, and 5 call-site rows (3f7, step 4, 6g, and two in `--body-check`). 384 + 27 = 411.
- **Carry 19.** On a branch of the self-test's throwaway clone that adds `docs/zz_leak.md` with a host path on line 2 (built at run time, never spelled), `privacy_line` refuses and names `docs/zz_leak.md:2: host-path`. The same line written home-relative (`~/proj`) passes. The head itself prints `0 refused`.
- **Carry 18.** A changed-path list naming only `dev/governance/roles/fixer.md`, or only `dev/governance/dimensions/D3.md`, matches `WAVE_INPUTS`. A list naming only `README.md` does not, so that diff still skips. Under MC the first two do not match either.
- **Carry 20, on the real tree.** A `git archive` copy of the merge base with `README.md` unchanged passes 6g: "claims.py rewrites claims.json and claims.md byte-identical, its header RESULTs hold". The same copy with one link appended to `README.md` (`See [the changelog](RELEASE_NOTES.md).`) refuses: "committed claims.json claims.md not what dev/audit/rounds/round4/D6/claims.py writes". No header `RESULT` moved there, as #1148 predicted for a row-only change, so the register arm alone carries #2609's instance. In the self-test, a stub generator in the real one's place drives the skip, pass, stale, moved-header and failing-generator arms. The real register needs the whole tree, which is about 200 MB and would raise the self-test's measured temp peak.
- **Carry 17.** On the `good-none.md` fixture, policy_lint `--pr-body ... --red mutation` refuses. `fill_red` with an empty site list writes nothing, leaves the file byte-identical, and the refusal stands. With the three site keys step 6d writes for the self-test's `pmut` branch, it writes the line and replaces `none`, and the same policy_lint call then passes. A second call writes nothing. At the `pmut` head, `prepr.sh --fill-red` predicts the sites itself and writes the line. On this head it prints "fill-red: the diff adds no unpinned mutation site; nothing written".
- **Carry 8.** `figure_lint.mjs --pr-body` passes the `good.md` fixture (`FIGURES: 1 resolved, 0 not verified, 0 refused`), and it refuses 11 of the 81 current `handoff-body/*` tips (`## Figures`). The existing body_push lint rows now print `figures ok:` beside the other gates and still pass.

## Figures

Taken at `002a963a8`, or at `5ab483524` where marked, against merge base `df478d40b`, 2026-10-26 between 05:00Z and 05:40Z, on this 4-core box. Wall times are the shell's `time`, three runs each, and the largest is quoted.

- Wall time per added check: `python3 -I tools/audit/seat/ref_privacy.py --check` 0.35 s (step 3f7 runs on every prepr, and `--body-check` runs it too). Step 6g, `git archive` plus `claims.py` plus both comparisons, 4.7 s, only on a diff touching `README.md` or `docs/*.md`. `node tools/policy/figure_lint.mjs --pr-body` 0.06 s, in `--body-check`. `node tools/policy/check-wave-script.mjs` 0.19 s, newly run on a role-contract or dimension-brief diff. `bash tools/pr/prepr.sh --fill-red` 3.4 s, in `body_push.sh`, mostly step 6d's predictor. Most added to one run: a prepr on a README and role-contract diff gets 0.35 + 4.7 + 0.19 = 5.2 s, and a body_push gets 3.4 + 0.06 + 0.35 = 3.8 s. Both are under the 10 s budget, and each check is under 5 s.
- Lanes left CI-only and not built here: the base-pinned replay (carries 4, 7, 9, 16), `tests/harness_headers.py` in full (2 min 26 s, `ALL 112 HARNESS HEADER CHECKS PASSED` at `002a963a8`), and the `instrument-self-tests` job (377 s per carry 15).
- `bash tools/pr/prepr.sh --self-test`: `411 passed, 0 failed` at `002a963a8`, wall 5 min 25 s. `384 passed, 0 failed` at `df478d40b`.
- Mutants: 9 planted, 9 killed. The driver refused one pattern that matched twice (MA's first form, which also matched the self-test's own pin text) and ran its re-anchored form.
- Carry 8's instance count: `figure_lint.mjs --pr-body` over the `BODY.md` of each `handoff-body/*` tip, fetched at 2026-10-26T05:07Z, refused 11 of 81, on origin/main `df478d40b`'s tree. Not every tip is a PR body: some are dispatched-topic or result bodies. The carry's "6 of 152" was a different population.
- Scoped gate, at `5ab483524`: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` prints `MODE: SCOPED -- 0 script(s) run, 33 scoped out`, and `scope.run` is empty. The `run_always` scripts at `002a963a8`: `python3 tests/env_drift.py --claims-only origin/main` printed `claims hygiene: origin/main ok`, `python3 tests/closure.py selftest` printed `ALL 117 closure shrink pins PASSED`, `python3 tests/layout.py` printed `layout self-test: ok`, and `tests/harness_headers.py` passed as above.
- `PYTHONPATH=tests/hastub python3 tools/pr/ci_predict.py --base origin/main` at `5ab483524`: `no closures, fast, wave-script or instrument red predicted`. At `002a963a8` it predicted 2 `tests / fast (3.14)` `LAYOUT new-reference` reds, and `5ab483524` repairs them.
- `bash tools/pr/prepr.sh <this body>` at `5ab483524`, 20 min 47 s wall. Every step is `ok` or `skip` except `closures`. The new steps print `ok ref privacy ... 0 refused`, `ok wave-script 209 passed, 0 failed` (run because `tools/pr/prepr.sh` is a pinned path), `skip claims register no change to README.md or docs/*.md` and `ok self-test 411 passed, 0 failed`. Step 7 prints `ok pr-body`, `ok figures`, `ok carry ... 7 routed, 0 unrouted` and `ok preflight`. `closures` refuses with `failed while being recorded: tests/entities.py (exit 1)`, which is this box's result: `PYTHONPATH=tests/hastub python3 tests/entities.py` prints `2 of 2449 ENTITY CHECKS FAILED` at the head and at the merge base `df478d40b`. The FAIL lines of the two runs differ only in nondeterministic detail (the order of duplicated service names, and spin timings), and #2838 recorded the same box result. The diff touches no file `tests/entities.py` reads beyond the two changed scripts it classifies.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `python3 tools/audit/archscore/score.py --diff df478d40be4b546a7aaad150a5d9132483534a3a HEAD`: `Architecture score: dS +0.0000 NULL`.
- `node tools/policy/policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
- `python3 -I tests/throwaway_git.py --check`: `0 raw git init or clone site(s) refused`. No new repository is built: the privacy rows add branches to the self-test's existing throwaway clone.
- `python3 -I tools/audit/seat/tmp_paths.py --check`: `0 refused`.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: `0 refused`. The diff adds no push site.

## Red checks

- No check has run at this head: it is pushed only to `handoff/r10-flow-jidoka-p2`.
- `tests / nightly-status`, if red on main's ancestry. It grades main's nightly lane, not this head.
- `tests / ci-ratchet`, which may be red on main's push runs: GitHub's repo-wide artifacts listing returns 0 bytes, and a hotfix is in flight. It is not this branch's red, and this diff does not touch `tests/ci_ratchet.py`.

## Forward-carry

- Carries 4, 7, 9 and 16, the base-pinned replay: prepr runs the head's copy of the graders that CI's pinned jobs restore from the base, and of `field_coverage.mjs`'s registry. They are not built. `governance.yml` holds three distinct `Restore the check source from the base commit` lists, and the agreement lane reads merge-subject history, so the replay needs a detached worktree with the overlay, not an archive. It is a slice of its own, under the 5 s per-check budget named above or listed CI-only. Carry: R10-FLOW-JIDOKA
- Carries 11, 12 and 14, the `--body-check` parity extensions (the agreement lane, step 6d's sites fed to 7d, the predicted budget-raise-gate red, and the parity test over `pr-contract.yml`), plus one grammar owner for `## Forward-carry` (G3). Not built. This slice adds the figure lint and `ref_privacy` to `--body-check`, which two of the parity test's rows will name. Carry: R10-FLOW-JIDOKA
- Carry 13, quiet output by default, with the flag convention shared with R10-UPDATE-PR-SIGNALS. Not built. Carry: R10-FLOW-JIDOKA
- Carries 15 and 21, predicting the `instrument-self-tests` and `tests / fast (3.14)` reds. Partly answered: 3f7 runs `instrument-self-tests`' `ref_privacy --check`, and 6g predicts the D6-register class of the `fast (3.14)` red. The rest of both jobs is not modelled. Carry: R10-FLOW-JIDOKA
- Carry 22, the gate-scoping friction measurement. Not taken: `node tools/policy/policy_lint.mjs --stats --since v7.0.4` needs a token, this seat has none (`gh auth status` reports the token failed), and the command hung for 120 s before it was stopped, where an early refusal would have been expected. Carry: R10-FLOW-JIDOKA
- Carry 10, the stale `S36` pattern in `dev/audit/harnesses/r10_seat_selftests_mutants.py`. Outside prepr and not touched. Carry: R10-FLOW-JIDOKA
- The round-1 census's HEAD-ONLY class needs a predicting detector. Not built. Carry: R10-FLOW-JIDOKA

## Friction

none
