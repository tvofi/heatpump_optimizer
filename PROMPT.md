CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-hotfix-nonrequired-reds, at head d7b25eca474f4edde0cad8eb284c27c977a0157c. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch d7b25eca474f4edde0cad8eb284c27c977a0157c for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-hotfix-nonrequired-reds before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-hotfix-nonrequired-reds, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-hotfix-nonrequired-reds, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-hotfix-nonrequired-reds <body.md>`, which pushes refs/heads/handoff-body/r10-hotfix-nonrequired-reds; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-hotfix-nonrequired-reds`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-hotfix-nonrequired-reds and refs/heads/handoff-wip/r10-hotfix-nonrequired-reds-body. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
OWNER RULING 2026-11-07 (supersedes the footer's merge-main step): hand off at your first clean prepr.sh head. Do NOT merge a moved origin/main or re-run prepr because main moved. Merge main only when `git merge-tree --write-tree origin/main HEAD` reports a conflict. The merge train recarries and re-proves your head on the current main.


OWNER RULING 2026-11-07 (mutants): before handoff, set MUTANT_CMD to your group's self-test, or to a features_block.py call for the lines you changed. Let prepr.sh's diff-mutant step run `tools/audit/seat/mutant_run.py --diff` over your added lines (use --max-mutants to bound it). For every SURVIVED site, add a test that kills it, or give it a `## Unpinned sites` disposition. Report the mutant run's wall time and its survivor count in `## Figures`. CI's mutation-autofix still writes the pins.

OWNER RULING 2026-11-07: a red on a check outside the required set (the merge train's required contexts; tests / nightly-status, record, record-autofix and delivery-status never count) never blocks. Do not return blocked for an unnamed non-required red. Name it in the body only if convenient.


CLOUD FIXER (opus, medium effort), REPAIR for R10-HOTFIX-NONREQUIRED-REDS, topic r10-hotfix-nonrequired-reds, PR #3305, branch fix/r10-hotfix-nonrequired-reds. Follow dev/governance/roles/fixer.md; steps 2-8 re-execute. The PR has had no fixer for about 4 h since the review below returned BLOCKED. A return with no new pushed commit and no re-taken body is a FAILURE: do NOT conclude "already done", "nothing to change" or "the finding is wrong" without a pushed commit that answers it (if you believe a finding is wrong, prove it with a pinned test or a recorded measurement in the diff and say so in the body). The verdict applies at the PR head below and nothing has fixed it.

Start from PR head d7b25eca474f4edde0cad8eb284c27c977a0157c (fetch refs/heads/fix/r10-hotfix-nonrequired-reds; handoff/r10-hotfix-nonrequired-reds is an ancestor of it). Run tools/audit/seat/cloud-setup.sh and --check first. Make the repair as new commits on top of that head, run `PREPR_SKIP_CLOSURES=1 bash tools/pr/prepr.sh` until rc=0 and python3 tests/structure.py; no budget raise without stopping and asking; claim files byte-identical to origin/main; never touch VERSION, the manifest version or the RELEASE_NOTES heading. Push handoff/r10-hotfix-nonrequired-reds as a fast-forward of the PR head. Then re-take the WHOLE body from handoff-body/r10-hotfix-nonrequired-reds and .github/PULL_REQUEST_TEMPLATE.md at the new head (`## Head` naming it, a section answering each finding below with its fix commit), push with bash tools/audit/seat/body_push.sh r10-hotfix-nonrequired-reds <body.md> and read the ref back. If refused do NOT override: push handoff-wip/r10-hotfix-nonrequired-reds plus BLOCKED.md quoting the refusal. Return only by refs; open no PR, post no comment; identity hpo-fixer <70032254+tvofi@users.noreply.github.com>; no footer, trailer, session link or home path. Return one status line plus the 40-hex handoff and body SHAs.

TASK
The review is architecture-unsound, so change the DESIGN, do not patch around it. (1) pr-contract.yml must not run any pull-request program: pin tools/audit/seat/merge_train.py and everything it imports (gh_read.py, tests/fixtures/required-contexts.json and any other import) into pr-contract's base-restore pathspecs as main's copy, or have the workflow compute the required set in a pinned step and pass it as --required-file; add an entities or self-test pin that the program pr-contract runs is base-restored (and a mutation proof: removing the pin fails it). Reproduce the reviewer's drive first (edit only merge_train.py so owed-reds prints a bogus name; a body silent on required reds must still error). (2) Pin the fail-closed rc check in requiredFromTrain: a fixture runs requiredFromTrain against a stub merge_train.py (or injectable command) exiting 2 with a REFUSE line and asserts every red is owed; the mutant `if (!names.length)` must die. State in the body how the mjs lines are mutation-covered.


VERDICT TO ANSWER (verbatim, read from the PR comment):
-----
Fix review: blocked d7b25eca474f4edde0cad8eb284c27c977a0157c architecture-unsound: pr-contract would run the PR's own merge_train.py owed-reds, unpinned, so a diff can silence its required reds; and the fail-closed rc check in requiredFromTrain survives its mutant

bus-nonce: f554c34869b7c965caf87c0497bb9090

## Block

Round 1. Measured head d7b25eca474f4edde0cad8eb284c27c977a0157c, merge base 70c15830b94a758357faa0b35f9011229a0d6a9c. The head was re-read before this verdict and has not moved.

1. **The required set's owner is read from the change under check (architecture-unsound).** `pr-contract.yml` restores its check source from the base commit, "so this job runs no pull-request program at all" (#1515, decision 0013). The restored pathspecs cover `tools/policy/*.mjs` but, under `tools/audit/seat/`, only `roster_lib.py`. After this merge, the base's `policy_lint.mjs --pr-body` spawns `python3 <ROOT>/tools/audit/seat/merge_train.py owed-reds` (`requiredFromTrain`, where ROOT is the checkout). That file, together with `gh_read.py` and `tests/fixtures/required-contexts.json` which it imports, is the **pull request's** copy. The step also has `GH_TOKEN` in its environment.
   - Drive (`ev/drive-unpinned-owner.txt`): I left `policy_lint.mjs` as shipped and edited only `merge_train.py` so that `owed-reds` prints one bogus name. A body silent on the reds `tests / typing`, `tests / fast (3.14)` and `gate` then gives `PR-BODY: 0 error(s)`. The required reds go unanswered, which is the opposite of what the ruling keeps.
   - This also contradicts the PR's own claim that the set is "read through that one owner and never copied". In CI the owner read is whatever the diff makes it.
   - Fixes that keep the architecture: pin `tools/audit/seat/merge_train.py` and what it imports in pr-contract's restore list, or have the workflow compute the set in a pinned step and pass it as `--required-file`. Either way, add an entities or self-test pin that the program pr-contract runs is base-restored.
2. **Fail-closed on an unreadable set is unpinned on its live path (mutation-vacuous at the brief's FOCUS).**
   - Mutant: `if (r.status !== 0 || !names.length)` becomes `if (!names.length)` in `requiredFromTrain`.
   - It survives `node tools/policy/policy_lint.mjs` (rc 0), `review_packet.py --self-test` (rc 0) and `bash tools/pr/prepr.sh --self-test` (514 passed, 0 failed) (`ev/mutant-drop-status-check.txt`).
   - Driven (`ev/drive-unreadable.txt`): with a `gh` that fails (403), `owed-reds` prints `REFUSE proof: ...` on stdout and exits non-zero. As shipped, that leaves every red owed (2 errors). Under the mutant, the REFUSE line becomes a one-name "set" and every red, required ones included, is owed nothing (`PR-BODY: 0 error(s)`).
   - Every fail-closed fixture drives a thunk or `--required-file`. None drives `requiredFromTrain` over a non-zero `owed-reds`.
   - The body's diff-mutant run (`mutant_run.py --cmd` over three Python self-tests only) cannot reach `.mjs` lines. So "24 mutants, 0 SURVIVED" does not cover policy_lint's new code. A fixture should run `requiredFromTrain` against a stub `merge_train.py` (or an injectable command) that exits 2 with a REFUSE line, and assert every red is owed.

## Findings

none

## Evidence

- CI: `merge_train.py classify d7b25eca474f4edde0cad8eb284c27c977a0157c --pr 3305` gave `GREEN d7b25eca474f4edde0cad8eb284c27c977a0157c pending: none red: none`, rc 0 (`ev/classify.txt`). No red check on the head, so step 11 owes nothing, and `## Red checks: none` is correct.
- Merge: `git merge-tree --write-tree origin/main d7b25eca` exits 0, tree d5ea3809abbeed7811e1b2affd741beecb057916. `LEDGER-MERGE: resolved tests/closures.json`.
- Body mutant (`return true` as the first line of `redOwed`) goes red: policy_lint acceptance rc 1 with `FIXTURE VACUOUS: with the required set known ...`, and review_packet self-test 2 failed, as the body says (`ev/mutant-returntrue-*.txt`).
- My mutants that die:
  - dropping the code-scanning alert arm: policy_lint rc 1
  - dropping the job-half arm: rc 1
  - the CLI thunk returning an empty Set on an unreadable set: review_packet self-test 4 FAIL
  - the unreadable set skipping every red: policy_lint rc 1 plus review_packet 4 FAIL
  
  Logs: `ev/mutant-*.txt`.
- Live drive at the head with the set read (`ev/drive-live.txt`): of `tests / typing`, `docs / links`, `tests / nightly-status`, `mutation` and `code-scanning alert 9 (py/y)`, the owed reds are `tests / typing`, `mutation` (the job half of `tests / mutation`) and the alert. Null control at base 70c15830 (`ev/drive-base.txt`): every red but `tests / nightly-status` is owed, which is the pre-ruling P282 exemption for a diff touching only `tests/x.py`.
- Harness `dev/audit/harnesses/r10_nonrequired_reds.py` at `--base` 70c15830 (merge base) and at dee8b413 (`ev/harness-*.txt`): rows A, B, C and D match the body exactly. This is the fixer's own instrument, disclosed as such. The finding is an owner ruling with no finder's harness, so I used my own drives above as the independent measure.
- Figures re-derived at this head:
  - `merge_train.py --self-test`: 475 checks, 0 failed
  - `review_packet.py --self-test`: 72 checks, 0 failed
  - `record_row.py --self-test`: all checks passed
  - `node tools/policy/policy_lint.mjs`: TOTAL 0 errors, rc 0
  - `merge_train.py owed-reds`: 23 names, rc 0, omitting `tests / nightly-status` and `governance / delivery-status` (`ev/owed-reds.txt`)
  - `rules_sync.mjs --check`: RULES-SYNC ok, so the `.claude` and `.cursor` copies are in sync
  - prepr `--self-test`: 514 passed. This was taken with one `requiredFromTrain` line mutated that no prepr fixture reaches, so it is not a pristine-head run.
- Not re-derived, heavy (CI is cited instead): the `entities.py` 3-failure claim and the 1018 s `mutant_run` of 24 mutants.
- VERSION, the manifest and RELEASE_NOTES.md are untouched.
- The policy files change, so this PR merges only on tvofi's approving review. This seat posted nothing.

bus: verdict/3305 at f0128771b3bfac52cf998b0cc43f97e7e33b3a56, confirmed from cloud-opus (review/3305 at 6684d47607700a6d133c39cb5251a36c77a4654e); evidence: ~/.zcode/bus/verdicts/3305/f0128771b3bfac52cf998b0cc43f97e7e33b3a56/evidence


-----

Before any commit run: export GIT_AUTHOR_NAME=hpo-fixer GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=hpo-fixer GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com, and also git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com. The cloud environment exports GIT_AUTHOR_*/GIT_COMMITTER_* as 'seat', and those environment variables beat git config, so the config alone does not hold. Never commit as 'seat'; check with git log -1 --format='%an %ae %cn %ce' after the first commit.


Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.


TIME: you have hours, not minutes. A gate, prepr or recording may run an hour: wait with Monitor windows of up to 60 min and re-arm them. Never end the session waiting on a choice: take the option that keeps coverage and the architecture sound, say so in the body, and go on. Push handoff-wip at each milestone, so your liveness can be read. If truly blocked, push BLOCKED.md on handoff-wip naming the question.
