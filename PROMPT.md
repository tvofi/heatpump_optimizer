CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-hotfix-train-defer-wait, at head a8c36900eed9a789e2bab2eee70ffc883f1a608f. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch a8c36900eed9a789e2bab2eee70ffc883f1a608f for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-hotfix-train-defer-wait before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-hotfix-train-defer-wait, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-hotfix-train-defer-wait, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-hotfix-train-defer-wait <body.md>`, which pushes refs/heads/handoff-body/r10-hotfix-train-defer-wait; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-hotfix-train-defer-wait`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-hotfix-train-defer-wait and refs/heads/handoff-wip/r10-hotfix-train-defer-wait-body. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
INTERIM TOOLCHAIN: this environment's cached venvs are behind the locks (numpy, scipy, homeassistant, measured 2026-11-04). Before any measurement or golden run: `bash tools/audit/seat/cloud-setup.sh` and then `bash tools/audit/seat/cloud-setup.sh --check`; confirm numpy and scipy against tests/requirements-ci.txt. If it cannot be refreshed say so in the body; CI remains the authority for goldens.
Fixers return only by refs, handoff/<topic> and body_push.sh; open no PR, post no comment; no Claude footers; no host paths.

CLOUD FIXER (opus, medium effort), REPAIR round 3 for PR #3290 (R10-HOTFIX-TRAIN-DEFER-WAIT, branch fix/r10-hotfix-train-defer-wait, topic r10-hotfix-train-defer-wait). CRITICAL-PATH HOTFIX (owner priority 11-07): minimal and fast, the cure the verdict names and nothing wider. The PR head is a8c36900eed9a789e2bab2eee70ffc883f1a608f (it contains handoff/r10-hotfix-train-defer-wait dddbf8cb; base your work on the PR head, merge origin/main if it moved, never re-cut). Follow dev/governance/roles/fixer.md: failing case first, mutation proof, the finder's harness at both ends, a null control for each quantified claim.
THE REPAIR: close the settle gap the verdict names. The remedy is your design call among the verdict's options (a), (b), (c); prefer (a) or (b), one shared predicate, no third copy of the deferral grammar. Add the self-test case from the 18:16Z scene (failing first) and flip the pinned "one read takes no settle" case; a sweep that never comes must still end RED. Re-take the Figures and Mutation proof at the repair head (485 checks baseline), add mutants for the round-2 lines (classify_at, classify_cmd, proof_watch required_state), add the classify CLI and proof_watch readers to the class-enumeration list, and answer the M9 residual as the verdict dispositions it.
Then re-take the WHOLE body from the current handoff-body (refs/heads/handoff-body/r10-hotfix-train-defer-wait) and .github/PULL_REQUEST_TEMPLATE.md: `## Head`, every figure, `## Red checks` (check-runs filter=all over ALL pages, every concluded red with class and answer). Run prepr --body-check, carry_audit check, tools/pr/prepr.sh to rc=0, the scoped gate (key on the MODE line); VERSION, manifest, RELEASE_NOTES heading and every *_budgets.json untouched; claim files byte-identical to origin/main. Return by refs: push handoff/r10-hotfix-train-defer-wait and body_push.sh r10-hotfix-train-defer-wait; open no PR, post no comment. Identity hpo-fixer <70032254+tvofi@users.noreply.github.com>; no footer or home path.
THE BLOCKED VERDICT, verbatim (refs/heads/verdict/3290, VERDICT.md):
Fix review: blocked a8c36900eed9a789e2bab2eee70ffc883f1a608f class-open: the classify CLI exits 1 RED in the gate-sweep settle gap, live at this head 18:16:12Z

bus-nonce: 5a2baec6a7dcf5c6acf30fe8b4a9196d

## Block

Round 2 of the fix review (first round blocked at 43a9d584, class-open). The round-2 remedy is wired correctly: the `classify` CLI (`classify_cmd` -> `Train.classify_at`) and proof_watch `required_state` (`Train.classify_at`) now both use the shared `_gate_busy` predicate, and wait-ci takes the settle. While the code run runs, the deferral is a WAIT on every reader. That was reproduced live (see Evidence).

What is still open is one domain of the same predicate on the one-read readers: the **settle gap**. After the code run completes (its `gate` green, every unit done, so `busy` is empty), the edit suite's deferral red is still the worst-suite `gate` until gate-sweep.yml re-runs it. `classify_at` deliberately takes no settle there. Its docstring and the instrument doc say "the caller's next read sees the sweep", and the self-test pins RED ("defer-wait CLI: one read takes no settle -- a red beside a green suite with nothing busy is RED"). That disposition is false for the CLI's callers, because none of them re-reads on RED:
- `bus.sh` (:587) refuses a dispatch on rc 1. A review dispatch is refused for a head that is going green.
- `postmerge.py` (:49) reports the last line.
- The reviewer seats' CI wait (cloud_dispatch prompt :208/:1036) stops at exit 1 and judges the head RED.

**Live at this head**, with the head's own code (worktree at a8c36900eed9a789e2bab2eee70ffc883f1a608f):
- The code run 42397572783's `gate` went green at 18:16:00Z (check run 128486567216).
- `merge_train.py classify a8c36900eed9a789e2bab2eee70ffc883f1a608f --pr 3290` at 18:16:12Z printed `RED ... pending: none red: gate` and exited 1.
- gate-sweep's re-run of the edit gate started at 18:16:18Z (128486820605).
- The next read printed `GREEN ... red: none`, rc 0.

So this very reviewer's waiter ended on a false RED. The window was 18 s against a 60–70 s poll, so roughly a quarter of polling callers land in it.

The remedy is the fixer's design call. Some options:
- (a) In `classify_at`, read a red GATE beside a green GATE suite whose completion is recent (bounded, e.g. within SWEEP_SETTLE_POLLS * HEARTBEAT_SECONDS of the read) as WAIT, and RED after that, so a sweep that never comes still ends RED.
- (b) Read gate-sweep.yml's runs at the head the same way `_gate_busy` reads ci.yml's.
- (c) Give each CLI caller a re-read on RED. This one is weaker: it makes three copies.

Whichever is chosen, add a self-test case from this scene and flip the pinned "one read takes no settle" case.

## Findings

- Follow-up: the body's `## Figures` and `## Mutation proof` were not re-taken at this head. They quote `478 checks` and M1–M3 at 478, but the self-test at a8c36900eed9a789e2bab2eee70ffc883f1a608f prints `merge_train self-test: 485 checks, 0 failed`. They carry no mutant for the round-2 lines (`classify_at`, `classify_cmd`, proof_watch `required_state`). The class-enumeration list also omits the `classify` CLI and proof_watch readers this head closes. All of this is owed at the repair head. Carry: R10-HOTFIX-TRAIN-DEFER-WAIT
- Residual: a surviving mutant, M9. Routing `classify`'s log to stderr (`**({"log": ...stderr} if a.cmd == "classify" else {})` -> `**({})`) leaves both self-tests green, so the line is untested. It is equivalent under every current caller: the only log line on that path (`runs listing is unreadable`) precedes the verdict line. `bus.sh` reads `tail -n 1` of 2>&1, `postmerge.py` reads the last stdout line, and `review_packet.py` uses an `re.M` anchored search. Carry: dismissed: equivalent mutant under all three stdout readers (bus.sh, postmerge.py, review_packet.py)

## Evidence

- Head reviewed: a8c36900eed9a789e2bab2eee70ffc883f1a608f (ev/HEAD.txt), merge base 4b5d771bdf8feb1f83d7d9443e5117b771a0ab76. Roles dir unchanged between merge base and origin/main (0-line diff).
- Self-tests at the head: `merge_train self-test: 485 checks, 0 failed`, `proof_watch self-test: 44 checks, 0 failed` (ev/mt-selftest.txt, ev/pw-selftest.txt).
- My targeted mutants on the round-2 lines (ev/mutants.txt), each applied, run and restored:
  - M4 (`classify_at` busy -> []): merge_train 2 failed (the CLI #3248 and CLI unreadable cases), proof_watch 2 failed (g3).
  - M6 (CLI back to the base `classify(latest_runs(runs), req)`): merge_train 2 failed.
  - M7 (proof_watch `required_state` back to the base reading): proof_watch 2 failed (g3 aborts with REQUIRED RED).
  - M8 (wait-ci all-runs settle dropped): merge_train 2 failed.
  - M1 re-run: merge_train 4 failed, matching the body.
  - M9 survives (see Findings).
  - Null control: a docstring perturbation gives 485/0 and 44/0.
  - M5 equivalent-mutant dismissal: stands per the brief, not re-judged.
- Class enumeration (ev/class-grep.txt, `git grep -n "classify("` plus classify_at/classify_cmd):
  - CLI `classify` (:8101 -> `classify_cmd` :519 -> `classify_at`) and proof_watch.py:234: both on the shared predicate.
  - `wait_ci` :1644/:1659: on the predicate.
  - `approval_owed` :544, `main_green` overlap :3148 (main has no edit run), orchestrator_tick.py :1151/:1648 (tick report lines): unchanged, consistent with the body's disposition.
- Live repro of the round-2 class at 18:01:41Z (ev/live-repro.txt), while code run 42397572783 was in_progress and edit run 42397572454's gate log said `FAIL run(s) [42397572783] at this head are still being judged; their gate decides`:
  - origin/main's code: `RED ... red: gate`, rc 1.
  - The head's code: `WAIT ... pending: gate`, rc 3.
  - My first waiter mistakenly ran origin/main's code and ended RED at 17:58:45Z (ev/classify-base-code.log), which is the base defect.
- The waiter on the head's code (ev/classify-run1.log): WAIT from 18:01:47Z to 18:15Z, then false RED at 18:16:12Z, then GREEN rc 0 at about 18:17Z (ev/classify.log). Gate rows: ev/gate-rows-1816.tsv, ev/check-runs-final.tsv, ev/ci-runs-final.tsv.
- CI at the head, judged job by job over all check-run pages (55 rows): every required context is green at the final read. The only concluded red is `tests / nightly-status` (failure at 17:49:36Z), which is not this PR's: the diff does not reach what it reads. `## Red checks: none` is consistent with that. The deferral red was superseded by gate-sweep's re-run, now green.
- Merge with origin/main aaaec212: `git merge-tree --write-tree` rc 0, tree 32e9db28 (ev/merge-tree.txt).
- #3287 interaction: #3287 has merged on main as cc100c275 (gate.py busy/judging). This PR touches neither gate.py nor gate-sweep.yml. On the merged tree the self-tests print `merge_train self-test: 492 checks, 0 failed` and `proof_watch self-test: 44 checks, 0 failed` (ev/merged-selftest.txt), including the table that pins `gate_busy` equal to gate.py's own `busy`. No copy of the deferral grammar was added: gate.py's `busy` is imported from its tree path.
- `PYTHONPATH=tests/hastub python3 tests/entities.py`: rc 0 (ev/entities.txt). `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED` (ev/structure.txt).
- The diff has 5 files: the delivery row dev/programme/delivery/3290.md is present, and no budget file, VERSION, manifest or RELEASE_NOTES.md is touched. `## Head` names a8c36900eed9a789e2bab2eee70ffc883f1a608f.
- Figures I could not re-derive: the s12 study's 56/32/10 SKIPs, 27 re-merges and about 3,500 runner-minutes. Its harness is not in the tree, and the body says so.
- The scheduled brief said never to send a push notification, so none was sent.

Before any commit run: export GIT_AUTHOR_NAME=hpo-fixer GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=hpo-fixer GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com, and also git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com. The cloud environment exports GIT_AUTHOR_*/GIT_COMMITTER_* as 'seat', and those environment variables beat git config, so the config alone does not hold. Never commit as 'seat'; check with git log -1 --format='%an %ae %cn %ce' after the first commit.


Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.


TIME: you have hours, not minutes. A gate, prepr or recording may run an hour: wait with Monitor windows of up to 60 min and re-arm them. Never end the session waiting on a choice: take the option that keeps coverage and the architecture sound, say so in the body, and go on. Push handoff-wip at each milestone, so your liveness can be read. If truly blocked, push BLOCKED.md on handoff-wip naming the question.
