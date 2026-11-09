Fix review: merge 92b8310fea7e81ce81308cd5de350c1301231498

bus-nonce: c216dc9689b30e03e570a6de56b6439a

## Scope

Resolution-delta review of #3345, round 2 (routine p-3345r2). The previous verdict, at `fd973e035d6044ac55a105a7156af5b46ce5838f`, was `blocked semantic-conflict`. Since then the head has gained the bot's `ci: merge main` `0942168880c7c1cd0c91e9bdf5bba79b64425aa2` (origin/main `631ac4df3`, #3353), the repair `977fd0033ba82b61fbb82aefe5687e7e95510588`, and the merge of that repair `92b8310fe`. Everything outside this delta stands on the earlier review. Role contracts: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` is empty, so they are current.

## Evidence

- RESULT block-answered: `python3 -I tools/ci/selftest_scope.py static` reports `106 gated step(s), 1 problem(s)` at `094216888` (the merge, before the repair: the UNGATED line for 'Show the topic grammar refusing a bare number and a prefix as family members') and `107 gated step(s), 0 problem(s)` at the head. It also reports `106 gated step(s), 0 problem(s)` at origin/main `631ac4df3`. Files: ev/pre-static.txt, ev/head-static.txt, ev/main-static.txt.
- RESULT null-control ungated: at the head I put the step's `if:` back to `${{ !cancelled() }}`. `static` then reports 2 problems (the UNGATED line, and `STALE ... extra ['topic-grammar']`). Restored afterwards, and `git status` was clean. File: ev/null-ungated.txt.
- RESULT null-control run_sha: at the head I set the `topic-grammar` entry's `run_sha` to zeros. `select` then reports `MODE: FULL -- ... the table is stale: run text changed since it was recorded: ['topic-grammar']`. Restored afterwards. File: ev/null-runsha.txt. With the table unmutated, `stale()` returns '' at the head.
- RESULT measured entry: I re-ran `python3 tools/ci/selftest_scope.py record --step topic-grammar` (strace, Linux) at the head. It reports `0 failed`, and `git diff` after it is empty, so the committed entry is exactly what the recorder produces. Files: ev/re-record.txt, ev/re-record.diff (empty).
- RESULT selection figure (body `## Null control`): `select --change M:tools/audit/seat/topic_grammar.py` prints `  run topic-grammar` once. `--change M:docs/x.md` prints it zero times (`MODE: SCOPED -- 17 step(s) run`). Both match the body. File: ev/select-null.txt.
- RESULT self-tests at the head: `selftest_scope self-test: 90 checks, 0 failed`; `topic_grammar self-test: ok`. Files: ev/selftest-scope-selftest.txt, ev/topic-grammar-selftest.txt.
- The body's mutants G1 and G2 are the same shape as my null controls. G1 reproduced: 2 problems, and its message text matches the body's. G2, the key rename, gives the stale-set refusal by the same `stale()` code path. I did not re-take G2 separately.
- RESULT own-diff delta: the brief's `fdc8d21a` is an ancestor of the old head but not its merge base, so `fdc8d21a..fd973e03` spans 162 files of main's history. The true merge bases are `806e952c` (old) and `631ac4df3` (new). I diffed `806e952c..fd973e035d` against `631ac4df3..094216888`. Both are 18 files, 636 insertions and 50 deletions. Stripping `index` and `@@` lines leaves one difference: an unchanged context line in `dev/audit/config/bugclasses.json` above the added `R10-TOPIC-FAMILY` block, which names a neighbouring `doc` entry that main changed. No added or removed line of the branch differs. The repair adds `.github/workflows/governance.yml` (+2 -1) and `tools/ci/selftest_closures.json` (+13) on top, which gives the head's 19 files, 650 insertions and 50 deletions. Files: ev/old-own.diff, ev/new-own-pre-repair.diff, ev/own-diff-delta.txt.
- RESULT merge-tree: `git merge-tree --write-tree origin/main 92b8310fea7e81ce81308cd5de350c1301231498` exits 0, with origin/main at `631ac4df3`, which is the head's own merge base. File: ev/merge-tree.txt.
- Head: the PR head is `92b8310fea7e81ce81308cd5de350c1301231498`, and the body's `## Head` names it. File: ev/HEAD.txt.
- Alternative the body rejects (adding the step to `UNGATED`): I agree with rejecting it. The step reads only its own file, as the re-record shows, so the measured gate is the sound form.
- Steps 4 and 5: the delta touches no claim file, `VERSION`, manifest or notes heading.
- Step 14: the only instrument number that moved is the gated-step count, 106 to 107, which comes from adding the step's id and gate. The closure entry is the recorder's own output (re-record above), not hand-written.
- Red checks: `merge_train.py owed-reds` is the whole owed set (ev/owed-reds.txt). `governance / instrument-self-tests` is outside it and is green at this head. CI state at the head: see the classify line below.
- RESULT CI: `python3 tools/audit/seat/merge_train.py classify 92b8310fea7e81ce81308cd5de350c1301231498 --pr 3345` exits 0 at 2026-11-09T15:04:05Z with `GREEN 92b8310fea7e81ce81308cd5de350c1301231498 pending: none red: none`. It printed WAIT (rc 3) from 14:22Z onwards until then (ev/classify-log.txt). The packet render saw `gate` red at render time (job 129211192174, empty output, concluded 14:12Z while other checks were still in progress); classify's final line counts no red at this head. `governance / instrument-self-tests`, which carried the earlier block, is success at this head (job 129206681898).
- Head at post: `git ls-remote` shows the PR head ref still at `92b8310fea7e81ce81308cd5de350c1301231498` (ev/head-at-post.txt).

## Findings

none

## Friction

none
