# Reviewer reproduction — PR #2083 at c32e90ddd730ae1a2fc85a44a52cdbe159fff08f

Worktree: `git worktree add --detach /Users/timmalmstrom/hpo-seats/r9-review-2083/wt c32e90ddd`
`PATH=$HOME/.local/state/hpo/venv-ci/bin:$PATH` (python 3.11 venv-ci).

| file | command |
|---|---|
| `checkruns-head.tsv` | `gh api --paginate "repos/tvofi/heatpump_optimizer/commits/<head>/check-runs?per_page=100" --jq '.check_runs[]\|[.name,.status,.conclusion]\|@tsv'` |
| `workflow-runs-head.tsv` | `gh api "repos/tvofi/heatpump_optimizer/actions/runs?head_sha=<head>&per_page=100" --jq '.total_count, (.workflow_runs[]\|[.name,.event,(.conclusion//"-")]\|@tsv)'` |
| `premise.txt` | per-bot-head: `actions/runs?head_sha=` (count + `pull_request` count), `commits/<sha>/check-runs` (distinct names), `commits/<sha>` (`.author.login`), then `comm -23 required names` |
| `mutations-merge_train.log` | `mut_train.sh`: apply the M1/M2/M3 edit with `assert s.count(old)==1`, run `python3 tools/audit/seat/merge_train.py --self-test`, `git checkout -- tools/audit/seat/merge_train.py` |
| `structure-and-baselines.log` | `python3 tests/structure.py`; then the same two `--self-test`s in a detached worktree at `origin/main` (`7cd5a588c`) |
| `null-control-two-ends.txt` | `drv/` fake `gh` (`fake-gh.py`) over `checkruns-63084989.tsv`; v2 = `git show origin/main:tools/audit/seat/ci-watch.sh` (58e1ba8f), v3 = `git show HEAD:...` (33a480a0); `CI_WATCH_ONCE=1`, v2 killed at 6 s |

ci-watch MW1–MW3 were run on a byte copy of the head file (`cp tools/audit/seat/ci-watch.sh /tmp/…/ci-watch-base.sh`,
sha1 `33a480a05b306a865b226f0ddb47361b22b17035`), editing one predicate at a time — the script's `WATCH=$0` makes a copy
standalone. results: MW1 → `FAIL W1 …` / `8 checks, 1 failed`; MW2 → `FAIL W3 …` / `1 failed`; MW3 → `FAIL W4 …` / `1 failed`.

Other re-derivations: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"`
→ `MODE: SCOPED -- 0 script(s) run, 33 scoped out`; `python3 tools/audit/seat/tmp_paths.py --check` → `0 refused`;
`node tools/policy/field_coverage.mjs --only registry` → `FIELD COVERAGE ok`;
`git merge-tree --write-tree origin/main HEAD` → rc 0.
