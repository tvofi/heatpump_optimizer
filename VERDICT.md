Fix review: merge 08caf4d1c3c04925be2d4172fcd9e70d7a3d03b7

bus-nonce: 0a04593d2d06a22ba93db1724e90b486

## Scope

Third round on R10-PROTECTION-CENSUS (second repair), a delta review over the blocked head b131ad0ad8c8e8e9710681160a8b539ab88137ff (closures-regressed). There was no review packet and no PR head at this SHA, so I had no `## Review scope` line and no CI to wait on. The delta `git diff b131ad0a 08caf4d1` is main's merge of #3461 plus this branch's own restored lines. The authored three-dot diff is `CENSUS.md`, `main_reds.py`, `dev/programme/delivery/3503.md` and `tests/closures.json`. Nothing under `custom_components/` is in the delta, so the scope stays as it is.

## Findings

- Follow-up: the body's account of the `instrument-self-tests` red names the right cause: rows 1-3 of `tick_loop.sh --self-test` run `fresh_check` against the real checkout, before `HPO_TICK_CODE_DIR=$t/nogit` is set. But it gives the trigger as incomplete. `fresh_check` also prints `TICK-STALE` at any `behind` count when a commit on `origin/main` touches `SELF_PATHS` (`tick_loop.sh`, `cloud_relay.sh`), not only when `behind > HPO_TICK_STALE_BOUND`. I measured this at this head with branch `rv-work` checked out, 19 behind `origin/main` 43e95474 (12 of those on `CODE_PATHS`, 6 touching `cloud_relay.sh`). The self-test printed `30 checks, 1 failed`. The failing row is `a seat bin dir with no gh shim…`, and the extra line is `TICK-STALE … behind=12: a branch is checked out`. The body's `0 failed` figure was true at 0 behind against 005eed25, the time it states. The hotfix should isolate rows 1-3 from both triggers. Carry: R10-HOTFIX-TICK-SELFTEST-CHECKOUT

## Evidence

- Head: 08caf4d1c3c04925be2d4172fcd9e70d7a3d03b7 is the handoff tip and the head the body names. `ev/HEAD.txt` and `ev/git_measures.txt` hold it.
- The previous block is resolved. 29996fad50c4674742016b26a83bb0ce2b53ad1c is an ancestor of the head, and `git diff HEAD 29996fad` is empty. `grep -c protection-census/main_reds.py tests/closures.json` prints 0 at b131ad0a, 1 at 29996fad and 1 at the head, so the `closures-autofix` bot line from 5d647dd0 is intact. The delivery row `dev/programme/delivery/3503.md`, which b131ad0a also lacked, is present again.
- `tests / closures` should be green on the INERT READS red. I ran `env -u BASH_ENV ./tests/derive_closures.sh --single tests/harness_headers.py` at the head in a detached worktree: rc 0, `tests/harness_headers.py 409 files`, and no `inert_reads` line added. Its only rewrite was `harness_headers.py` `rc` 1 to 0. `origin/main` and the merge base 005eed25 also record rc 1, so that value is inherited, not this diff's (`ev/derive_single_harness_headers.diff`, `ev/derive_single_harness_headers.tail.log`). `ci_predict.py` at the head printed `CI PREDICT: no closures, fast, governance or instrument red predicted against 005eed2573da`.
- Merge with main: `git merge-tree --write-tree origin/main <head>` exited 0 against origin/main 43e95474, printing tree 8566fcb0, and the merged tree keeps the `main_reds.py` line. The head is 19 commits behind main but merges cleanly, so this is not a block.
- I re-derived every figure in the body at the head: 17 required contexts (ruleset one-liner); `33 29` with the other 4 being `arch_score.py`, `ha_contract.py`, `layout.py`, `md_tables.mjs`; 28 rows from `main_reds.py | wc -l`; null control 0 rows for runs 4080, 4107 and 4116; `ENTRIES 18 PRS 14`; 4 `harness_headers` lines. All match.
- Mutation proof: `mutant_run.py --diff <mb>...HEAD --cmd true --list` lists no mutants (rc 0). The diff adds no production or tool code, and nothing was there to mutate.
- VERSION, the manifest version and the notes heading are not in the three-dot diff. No claim files are touched, so `env_drift` is not applicable.
- Red checks: `owed-reds` lists `tests / closures` and `pr-contract / pr-contract`. The body answers `tests / closures` with a cheaper detector (`--single`, ~170 s, which I reproduced as the detector), process state (c), a cost test and a recorded decision. `pr-contract` and `gate` are answered as consequences. `tests / nightly-status` and `instrument-self-tests` are not in `owed-reds`. The `instrument-self-tests` failure I measured comes from main's drift on `SELF_PATHS`, and the diff touches no file under `tools/`. The merge base has the same drift, so the failure is not INTRODUCED by this diff and does not block.
- Live CI: the PR branch `fix/r10-protection-census` now points at a18099eef37f00b2a180085b495dab08c5d23b08, the orchestrator's merge of b131ad0a into 29996fad. Its tree is byte-identical to the head's (`git diff` gives 0 lines), but it is not an ancestor of the head. At 17:15 UTC its runs 43267019041 and 43267017344 had `tests / closures`, `instrument-self-tests`, `fast`, `typing`, `briefs`, `env-matrix` and `policy-docs` still in progress. `mutation`, `closure-scope`, `hassfest`, `validate-hacs`, all three CodeQL legs, `arch-score` and `budget-raise-gate` were green. `nightly-status` was red, as the body describes. Following the brief, I did not wait on these runs. I expect `instrument-self-tests` to go red there through the drift mechanism in the finding above, and that red is not owed. Because the head does not descend from a18099ee, publishing it onto the PR needs a merge or a lease push. That is the orchestrator's call; this verdict covers the identical patch.
- Forward-carry: the body's one item is `Carry: dismissed` because the decisions are written in CENSUS.md "Sizing for round 11". `handoff-wip/r10-hotfix-tick-selftest-checkout` exists at b80f611a.
- Round: 3 (second repair). A re-cut is owed only from the fourth round.

## Friction

none
