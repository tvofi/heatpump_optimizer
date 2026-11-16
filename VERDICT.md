Fix review: blocked d5ba8b8ce56ba02776b02a1143657a8c98aec4d9 code-defect: prepr ancestry cache keeps a commit read that has no check run yet, losing a red that lands on it within the TTL

bus-nonce: 232168db3beca6c1b4814ac8fccb0083
pending-ci: gate

## Block

- `tools/pr/prepr.sh` `ancestry_reds` keeps a sha's read whenever no line is `P`, so a commit with no check run at all (`T 0`, no `P` line: just pushed, CI not yet queued, or a pre-PR push no workflow ran on) is kept for `PREPR_ANCESTRY_TTL_S` (3600 s) as if its runs were final. A red that then lands on that commit is not read for the next hour; the merge base re-reads every commit and names it. The keep-guard's own comment ("a commit's runs are final then") does not hold when there are no runs, and the body's fail-closed premise (an unread commit stays UNCHECKED) is the one this breaks: the second run reports the red as confirmed absent. Harness `ev/zero_cache.sh <prepr.sh>` (mine, built on the PR's `ancestry_calls.sh` loader; a 2-commit branch, the head at `total_count 0`, then a red on the head, both reads at TTL 3600), output `ev/zero_cache.txt`:
  - merge base `ef6363d5f2`: read 1 `out=[]`, read 2 `out=[closures]` (null control: the defect is the change's).
  - head: read 1 `out=[]`, read 2 `calls=0 out=[]` -- the red is lost.
  The repair is in the guard: keep only a read whose `T` total is above 0 (and none `P`), with a self-test row for the zero-run commit (cold read, red lands, warm read names it), its mutant (drop the `T > 0` condition) shown failing.

## Findings

- Surviving mutant on new code: `orchestrator_tick.Tick.check_runs`'s fall-back to the paginated read for a head with more runs than one page holds is unpinned. Replacing `if isinstance(page, dict) and page.get("total_count", 0) <= len(page.get("check_runs") or []):` with `if isinstance(page, dict):` leaves `orchestrator_tick.py --self-test` at 373 checks, 0 failed (`ev/mutant-A-checkruns-fallback.txt`). The comments read's equivalent fall-back is pinned ("a full first page is read through to the end"); the check-runs one needs the same row (a first page with `total_count` above its `check_runs` length must reach the `--paginate` read) in the re-cut. Carry: R10-GH-READ-RESIDUE-P3
- `gh_read.etag_dir()` keys the ETag store on `$HPO_STATE_DIR`, while the docstrings (`gh_read.py`, `merge_train._checks_rule`, `Tick.conditional`, the instrument page) say it is shared "with every process of the host". Item 2 of this same PR exists because callers run under different `HPO_STATE_DIR`s (P669), so processes under distinct state dirs each pay the cold read and the 235-per-hour ruleset figure is cut only within one state dir. Either fix the store at the host home as the log now is, or state the scope; the post-merge `gh_calls.py --top` re-measure the body owes is where this shows. Carry: R10-GH-READ-RESIDUE-P3

## Evidence

- Round: first (no `--reviewed-head`). Head reviewed: `d5ba8b8ce56ba02776b02a1143657a8c98aec4d9`, the PR body's `## Head` names the same SHA.
- Role contracts current: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` printed nothing.
- Merge with main: `git merge-tree --write-tree origin/main d5ba8b8c...` rc 0 at origin/main `ef6363d5f2` (`ev/merge-tree.txt`); no conflict.
- Self-tests at the head (`ev/selftests-head.txt`, `ev/merge_train-selftest.log`, `ev/prepr-selftest.log`): `gh_calls.py --self-test` 226 checks 0 failed; `orchestrator_tick.py --self-test` 373/0; `seat_venv.sh --self-test` 29/0; `gh_read.self_test()` 158/0; `merge_train.py --self-test` 827/0; `prepr.sh --self-test` 560 passed 0 failed.
- Figures re-derived, `bash tools/audit/seat/ancestry_calls.sh` (`ev/ancestry_calls.txt`): merge base `prepr.sh` long `calls=521`, two `calls=3`; head long `calls=520`, two `calls=2` -- matches the body's 521/520 and 3/2.
- Mutation proof, the body's `prepr.sh` pending-guard mutant re-run (guard `! grep -qx P` dropped): `prepr.sh --self-test` 559 passed 1 failed, the named row "a commit with a run still pending is read again each time ... (got 0:closures:0, wanted 0:closures:1)" (`ev/mutant-B-prepr-pending.log`). Killed as claimed. The other body-named mutants were not re-run: Python mutants the self-tests above cover by name.
- Finder's harness: none named (review packet); the PR's own figure driver `ancestry_calls.sh` landed in this diff and is the fixer's instrument, disclosed as such. The zero-run harness above is mine.
- VERSION, manifest version, release-notes heading and both claim files untouched (`ev/files.txt`); no budget file in the diff.
- carry_audit at the head (packet): 4 finding items, 4 routed, 0 unrouted.
- Owed-reds set (`ev/owed-reds.txt`). CI at this head after ~30 min of polling: `merge_train.py classify d5ba8b8c... --pr 3682` rc 3, last line `WAIT d5ba8b8ce56ba02776b02a1143657a8c98aec4d9 pending: gate red: none` (19:25:40Z, `ev/classify.log`); no red, so no `## Red checks` answer is owed at this read.
- Head re-read before return: `refs/heads/fix/r10-gh-read-residue-p3-pr` is still `d5ba8b8ce56ba02776b02a1143657a8c98aec4d9`.
