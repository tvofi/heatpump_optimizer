CLOUD REVIEWER seat for tvofi/heatpump_optimizer, topic r10-hotfix-selftest-scope-union-p1, at head 532b51350bdd2dc8cc5e6cf4221f2714c4500e4a. Bus nonce: 17080627b73addfe9d2be4af39532a41. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead. Read your policy once, verbatim: `python3 -I tools/policy/role_pack.py render fix-review --out $HOME/role-pack.md`, then that file in place of your role contract and INSTRUMENTS.md; on REFUSE read those files as before.
Role: read dev/governance/roles/fix-review.md and its rules from main, and follow them exactly. Fetch the handoff head with `git fetch origin 532b51350bdd2dc8cc5e6cf4221f2714c4500e4a`; the body is BODY.md at refs/heads/handoff-body/r10-hotfix-selftest-scope-union-p1 (`git fetch origin handoff-body/r10-hotfix-selftest-scope-union-p1`), and no pull request exists yet. There is no review packet and no CI to wait on before the PR opens: say so in the verdict's evidence. Verify each claim adversarially: mutate the fix and check the tests fail, and check every figure in the body at this head. Check that it merges with origin/main (`git merge-tree --write-tree origin/main <head>`); block on main only when that reports a conflict, never on a head that is behind main but merges cleanly (the train re-proves it on the current main). 
Output: in a fresh directory of your own (`W=$(mktemp -d)`), write verdict.md, whose first line is exactly `Fix review: merge 532b51350bdd2dc8cc5e6cf4221f2714c4500e4a` or `Fix review: blocked 532b51350bdd2dc8cc5e6cf4221f2714c4500e4a <class>: <reason>` (no brackets; the class is lower-case letters and dashes), in the format the role file gives, then a blank line, then `bus-nonce: 17080627b73addfe9d2be4af39532a41`, then the body in sections. A blocked verdict's block goes under `## Block`. Each finding this PR does not settle (a defect, a surviving mutant, a deferral, a follow-up, a task owed after the merge) is its own bullet under `## Findings` ending in its own `Carry: <GROUP> | #<issue> | O<n> | dismissed: <reason>` (finding-propagation.md). Everything else (RESULT lines, re-runs, CI state, figures you could not re-derive) goes under `## Evidence`: tools/audit/carry_audit.py reads an item there, and under any heading of a merge verdict but `## Findings`, `## Friction`, a block heading and a note heading (Residuals, Follow-ups, Notes ...), by its shape alone: a finding only when it opens with a lead word (Residual:, Follow-up:, Out of scope: ...) or carries a `Carry:`, so a defect you hand on goes under `## Findings`, and bus.sh refuses a verdict holding a finding with no valid `Carry:`. Put the evidence files in `ev/` beside it, under 25 MB in all (cite a large log by path and keep its tail: a ~30 MB ev/ once failed its push), and make at least one file under `ev/` contain the full 40-hex head `532b51350bdd2dc8cc5e6cf4221f2714c4500e4a` (e.g. `ev/HEAD.txt` holding the head you reviewed, beside your command output): bus.sh refuses a verdict whose `ev/` names no head. Do NOT run bus.sh: its dispatch record lives on the orchestrator's machine, which publishes the verdict there (cloud_relay.sh). Return the verdict on a probe ref, and push nothing else; this builds one parentless commit with a private index and touches no branch of your checkout: `R=$(git rev-parse --show-toplevel); G=$(git rev-parse --absolute-git-dir); mkdir -p $W/pr && cp -r $W/verdict.md $W/ev $W/pr/ && cd $W/pr && T=$(GIT_DIR=$G GIT_INDEX_FILE=$W/idx GIT_WORK_TREE=$W/pr sh -c 'git add -A -f . && git write-tree') && C=$(GIT_DIR=$G git -c user.name=hpo-fixer -c user.email=70032254+tvofi@users.noreply.github.com commit-tree $T -m "verdict r10-hotfix-selftest-scope-union-p1 532b51350bdd2dc8cc5e6cf4221f2714c4500e4a") && git -C $R push -q origin $C:refs/heads/probe/revt-r10-hotfix-selftest-scope-union-p1-17080627`. That ref is the return signal. Do not post comments, approve or merge.
A red is owed a `## Red checks` answer, and may block, only when its name is in the set `python3 tools/audit/seat/merge_train.py owed-reds` prints (defect-root-cause.md); any other red is neither answered nor a block.
Never write to any branch except your return refs. Never work around a hook or a refusal; report it in your result instead.
Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.

Brief (snapshotted when this payload was rendered):
FIRST REVIEW (critical path, main is red) of the fixer handoff r10-hotfix-selftest-scope-union-p1 (group R10-HOTFIX-SELFTEST-SCOPE-UNION part 1), tip 532b51350bdd2dc8cc5e6cf4221f2714c4500e4a; no pull request exists yet, review the branch handoff/r10-hotfix-selftest-scope-union-p1 against origin/main (three-dot). Review as fix-review.md says, with the finder's harness. The roster brief for part 1 follows verbatim.

## Roster brief (verbatim)

Hotfix, main red. Orchestrator ruling under mandate 6715477401, 2026-11-11 (recorded as P584 in triage batch 169). Main a7628041dc is red on governance / instrument-self-tests, step drift (Refuse a self-test read set the committed table misses), with 6 UNDER-SCOPED refusals: verdict-bus and review-packet miss dev/governance/roles/fix-review.md; prepr misses .gitattributes, tests/env_drift.py and tools/merge/ledger_merge.py; open-pr, pr-args and update-pr miss the probe -c. The step has been red on every completed main push since PR 3315. Evidence: job 130352715261 of workflow run 42968587919, whose selftest-closures artifact is the measured table (gh run download 42968587919 -n selftest-closures); the orchestrator's main-red diagnosis holds the commands behind every figure and is relayed on request. Causes: PR 3379 added a read of fix-review.md in review_packet.py (review_packet.py:921, step12) without touching the table; PR 3419's re-record removed the other entries, because `record` (selftest_scope.py:701) does entries.update per step (selftest_scope.py:743) and so REPLACES a step's read set with whatever one non-push recording saw. The drift step runs only on a main push under strace (governance.yml:297 sets SELFTEST_TRACE on push only; the step's guard is at governance.yml:1496), so a pull request judges nothing and no merge is refused. PART 1 (fires at once, its own pull request): add the 6 measured misses to tools/ci/selftest_closures.json exactly as the diagnosis lists (verdict-bus and review-packet files += fix-review.md; prepr files += the three; prepr git += branch; open-pr, pr-args, update-pr probes += -c), ADD to each existing entry, never replace the table with the artifact, keep prepr's required-contexts.json and git fetch; nothing else. Proof: the next main push's drift step prints 0 refusals; before it, a python set check that artifact minus table is empty for the 6 steps. PART 2 (the class barrier owed by defect-root-cause.md: this is at least the third hotfix of the class, after R10-HOTFIX-MAIN-SELFTESTS, R10-HOTFIX-SELFTEST-SCOPE-HANG and R10-HOTFIX-PREPR-SELFTEST-DARWIN): (a) `record` unions a step's new measurement with its prior entry instead of replacing it, with a separate explicit way to drop a read, failing test first and mutation proof; (b) a pre-merge detector that refuses a pull request adding a read to a gated self-test without the table entry (PR 3379's shape), demonstrated against PR 3379's diff and with a null control on a pull request that adds no read; (c) decide WITH NUMBERS whether the drift step can run on pull_request (strace install and traced-run wall time per job from the main-push jobs, against the gate's budget), and either wire it or record the refusal with those figures. Fixer and reviewer opus: there is no local oracle (no strace on Darwin), the step runs only on a Linux main push.

## Scope of THIS seat (part 1 only)

Edit ONLY tools/ci/selftest_closures.json: add the missing reads listed in section 5 below to the existing entries (a union; do not replace the table with the artifact). Do not touch tools/ci/selftest_scope.py or .github/workflows/governance.yml: record() union and a pre-merge detector are part 2, a separate later seat. The drift step (selftest_scope check against the measured table) runs only on a main push, so you cannot run it before merge. Prove the edit instead by comparing your table against the measured artifact entries quoted in section 5 (for each of the 6 steps, artifact set minus your set must be empty for the listed reads; python set diff, output in the PR body), with a null control (an entry you did not touch stays byte-identical) and JSON ordering/format as the file uses now. Hotfix priority: main is red.

## Diagnosis section 1 (verbatim from the orchestrator's diagnosis)

## 1. The failing step and the first real error

Command: `gh api repos/tvofi/heatpump_optimizer/actions/jobs/130352715261 --jq '.steps[]|select(.conclusion!="success" and .conclusion!="skipped")|"\(.number) \(.name) \(.conclusion)"'`

Only step 118 fails: "Refuse a self-test read set the committed table misses" (id `drift`). It runs:

    python3 -I tools/ci/selftest_scope.py check --traces "$RUNNER_TEMP/selftest-trace" \
      --write "$RUNNER_TEMP/selftest_closures.json" | tee "$RUNNER_TEMP/selftest-drift.txt"
    grep -Eq '^selftest_scope check: [1-9][0-9]* gated step\(s\), 0 refusal\(s\)$' ...

Log (log not available to you), just above `##[error]Process completed with exit code 1.` at line 19393:

    UNDER-SCOPED step verdict-bus: files misses ['dev/governance/roles/fix-review.md']
    UNDER-SCOPED step review-packet: files misses ['dev/governance/roles/fix-review.md']
    UNDER-SCOPED step prepr: files misses ['.gitattributes', 'tests/env_drift.py', 'tools/merge/ledger_merge.py']
    UNDER-SCOPED step open-pr: probes misses ['-c']
    UNDER-SCOPED step pr-args: probes misses ['-c']
    UNDER-SCOPED step update-pr: probes misses ['-c']
    note: over-scoped step cloud-dispatcher: 1 files no longer measured
    note: over-scoped step prepr: 1 files no longer measured
    selftest_scope check: 111 gated step(s), 6 refusal(s)

The VACUOUS and "FAIL D1/D2" lines, and the FAIL lines of the selftest-scope-mutants step, are fixture output from steps that passed. That is the known trap, ruled out by the step conclusions above.


## Diagnosis section 4 (verbatim)

## 4. Cause

Measured by diffing the committed table (`git show origin/main:tools/ci/selftest_closures.json`) against the run artifact, and the table at dbd1ab5b07 (#3419's base):

- **dev/governance/roles/fix-review.md (verdict-bus, review-packet).** PR #3379 (merged as 86953c6d99, fix/r10-hotfix-delta-review) added `step12 = (ROOT / "dev/governance/roles/fix-review.md").read_text()` to tools/audit/seat/review_packet.py, at line 921 on main. The diff 6f0ff9d814..86953c6d99 shows the addition. #3379 did not touch tools/ci/selftest_closures.json. The miss first appears at 86953c6d (job 130348330038).
- **The '-c' probe (open-pr, pr-args, update-pr) and prepr's files (.gitattributes, tests/env_drift.py, tools/merge/ledger_merge.py).** These were present in the table at dbd1ab5b07 and were REMOVED by #3419's own re-record. #3419 also swapped prepr's git subcommand 'branch' for 'fetch' and added tools/policy/fixtures/required-contexts.json to prepr. The re-record is commit dffd0d7e92, "re-record the self-test steps main refuses": "re-recorded ... on Linux with strace, in this branch merged with origin/main 45adb0c3b4: python3 -I tools/ci/selftest_scope.py record --step ID". The main-push measurement shows those reads still happen.
- **Inferred, not measured.** These reads depend on the environment (the event, or the GitHub env), and only a main push makes them. `record()` (tools/ci/selftest_scope.py, from line 701) does `entries.update(measured)` per step: it REPLACES a step's read set rather than adding to it. A recording made anywhere other than a main push therefore drops them. That would explain the flapping counts (37, 1, 32, 33, 6).


## Diagnosis section 5 (verbatim)

## 5. Smallest sound fix

Edit tools/ci/selftest_closures.json and add each missing read to the existing entry. Do not replace the table with the artifact.

    steps["verdict-bus"].files   += "dev/governance/roles/fix-review.md"
    steps["review-packet"].files += "dev/governance/roles/fix-review.md"
    steps["prepr"].files         += ".gitattributes", "tests/env_drift.py", "tools/merge/ledger_merge.py"
    steps["prepr"].git           += "branch"
    steps["open-pr"].probes      += "-c"
    steps["pr-args"].probes      += "-c"
    steps["update-pr"].probes    += "-c"

Keep prepr's required-contexts.json and git 'fetch'. In the run they are only an over-scoped note, not a refusal, and keeping them stops the next recording made off a push from flapping. Write the table through `write_table`'s ordering, or keep the JSON format the file uses now.

Artifact diff command (python, sets): artifact steps[s][f] minus committed steps[s][f] for s in the 6 steps. The result:

    verdict-bus files ADD ['dev/governance/roles/fix-review.md']
    review-packet files ADD ['dev/governance/roles/fix-review.md']
    prepr files ADD ['.gitattributes','tests/env_drift.py','tools/merge/ledger_merge.py'] REM ['tools/policy/fixtures/required-contexts.json']
    prepr git ADD ['branch'] REM ['fetch']
    open-pr / pr-args / update-pr probes ADD ['-c']

**Sound follow-up.**
- `record()` should union with the step's prior entry, or main-push measurements should be authoritative.
- A PR that adds a read to a gated self-test (as #3379 did) needs a pre-merge detector, because drift runs only after the merge.
- This class has repeated across at least 3 hotfixes. Per defect-root-cause.md and the audit-class barrier rule, that owes an RCA or a barrier.

**Could #3419 have covered it?**
- fix-review.md: no. #3379 merged after #3419's head (`git merge-base --is-ancestor 86953c6d99 969106255818` reports not an ancestor).
- The other 4 refusals: yes. #3419's own diff introduced them.

**Open PRs.** Command: loop `gh pr diff <n> --name-only` over `gh pr list --state open`. Only #3355 (fix/r10-body-contract-p3, R10-BODY-CONTRACT part 3) touches tools/ci/selftest_closures.json or governance.yml, and its diff carries none of these entries. #3424, #3425 and #3427 do not touch these files.


## Overlap
If `git merge-tree --write-tree origin/main HEAD` conflicts, MERGE origin/main into the branch and re-run steps 2-8; never rebase.
