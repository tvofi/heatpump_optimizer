CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-closeout-cleanup, at head fc47684e3577d7fdd34db78c48d9d173f8806c35. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name seat && git config user.email seat@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch fc47684e3577d7fdd34db78c48d9d173f8806c35 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-closeout-cleanup before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-closeout-cleanup, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-closeout-cleanup, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-closeout-cleanup <body.md>`, which pushes refs/heads/handoff-body/r10-closeout-cleanup; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-closeout-cleanup`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-closeout-cleanup. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
CLOUD FIXER (sonnet), BODY-ONLY RE-TAKE (orch s10: the handoff-body ref 44d48e59 names a stale head 7be77bd48296; retake the WHOLE body at the handoff tip fc47684e3577 with no code change), round 4, for PR #3085 (R10-CLOSEOUT-CLEANUP: closeout cleanup) of tvofi/heatpump_optimizer, branch fix/r10-closeout-cleanup, topic r10-closeout-cleanup. The authored code head is the handoff tip handoff/r10-closeout-cleanup at fc47684e (the r3 repair for alert 49, self-test 69); the PR head 1be96319 is behind it until update_pr applies it. Two instrument refusals blocked the body: (a) body_push hot-file, because #3065 held an unboarded merge verdict on dev/audit/harnesses/r10_seat_selftests_mutants.py (#3065 may not have merged yet: if body_push refuses hot-file, do not override and do not wait; report the refusal and the exact refusal text in your final line); (b) brief-carries, because the roster (origin/handoff/audit-r10-roster, dev/programme/rosters/wave-r10-groups.json, group R10-CLOSEOUT-CLEANUP) now has 7 carries and the body names 6. The missing one is carry index 6 (the carry the roster calls carry 7): the s9 local-cleanup finding, worktree_gc 'eligible 0, kept 131' at 7.8 GiB free, appended after the first fixer ran. START FROM the prepared body printed between the BODY-BEGIN and BODY-END markers at the end of this brief (head fc47684e, alert 49 named, self-test 69; it lacks only carry index 6). Note the cloud box cannot read local paths; the body is inline. DO, and only this: read roster carry index 6 in full and ANSWER it in the body. Build the change only if it is small and clearly within this group's files (worktree_gc.sh and the closeout instrument) and carries a failing test first, a mutation proof and a null control; otherwise do NOT build: route it as a `## Forward-carry` entry to the group's apply run, with its reason, ending in the carry line the template and tools/audit/carry_audit.py expect, and say in ## Carries (one by one) that carry 7 is routed and why. Either way the body must name all 7 carries, one by one, so brief-carries passes (run python3 tools/audit/carry_audit.py on the body). Retake the WHOLE body from .github/PULL_REQUEST_TEMPLATE.md headings, ## Head naming the new head and the code head, ## Red checks naming every concluded red check at the head (whole check-run set via the check-runs API, all pages). If you build, also run python3 tests/structure.py, the scoped gate (key on the MODE line) and tools/pr/prepr.sh without the closures skip until rc=0, and merge origin/main only if merge-tree reports a conflict; never rebase or force. Push the body via bash tools/audit/seat/body_push.sh r10-closeout-cleanup <body.md>. Refs only; open no PR, post no comment. Claim files byte-identical to origin/main; never touch VERSION, the manifest version or the RELEASE_NOTES.md heading. Identity hpo-fixer <70032254+tvofi@users.noreply.github.com>. No footer, trailer, session link or home path. One status line and the 40-hex SHAs of the handoff and body refs.

BODY-BEGIN
R10-CLOSEOUT-CLEANUP, instrument half (Part of #201; issues #2505, #2727, #2728). Lands the closeout instrument and folds in the two fly-ins: `prune_refs.py` (batched push arm, keep guards, `--topic`) and `worktree_gc.sh` (unpushed keep, `on-remote` class). The `--apply` run is the orchestrator's final act and was not run here; merging this sets the group carries-open.

Carry dispositions (the group's six carries):
- Carry 1 (probe refs): residue-no-pr in `prune_refs.py`'s plan, deleted by the final run; no new rule.
- Carry 2 (roster-gated `--apply`): `closeout.py` refuses naming each open group; arms and mutant `closeout-1` below.
- Carry 3 (folded R10-FLY-PRUNE-REFS): the push arm (0 gh calls, tags before deletes, null control 2N), the `claude/*`, open-group `design/` and age keeps; its inner carries (dispatch/`brief/` residue, stranded handoff refs) fall to the same plan as archive-delete residue.
- Carry 4 (folded R10-FLY-WORKTREE-GC): `unpushed` keep on both the classify and apply paths, and the `on-remote` class with its cwd, fetch and lsof controls.
- Carry 5 (`--topic`): archive-then-delete, refused on a `+` cherry line or an open PR; mutants `prune_refs-5` and `prune_refs-6`.
- Carry 6 (build the tooling now, run last): the instrument lands here; the `--apply` run is not made.

Design notes: `--topic`'s `git cherry` refusal covers `handoff/` code refs only, since body and dispatch refs are orphan commits that always carry a `+`; local branches holding commits no remote or tag has are never deleted.

## Head

Handoff head fc47684e3577d7fdd34db78c48d9d173f8806c35, which carries the earlier measured head 7be77bd48296b992c8439c7d8e01a21da2c30ac7 (origin/main 6421fe135d9f5a9e65433a4433f000d2419486bf merged in; `tools/pr/prepr.sh` rerun after that merge) and, after it, the alert 49 repair (fdcce70e9, fc47684e3) and a later merge of origin/main (d4d328e61). The figures below were taken at 7be77bd48 except the `prune_refs.py` self-test count, re-run at fc47684e3.

## Mutation proof

Eleven mutants, each planted in a production predicate, run by `dev/audit/harnesses/r10_seat_selftests_mutants.py closeout-1 closeout-2 prune_refs-1 prune_refs-2 prune_refs-3 prune_refs-4 prune_refs-5 prune_refs-6 worktree_gc-1 worktree_gc-2 worktree_gc-3`: all KILLED, `RESULT survivors=0`. They drop the roster refusal, the step gate, the `claude/*` keep, the open-group `design/` keep, the age guard, the missing-tag refusal, the cherry `+` refusal, the dispatch topic match, the unpushed keep, the cwd test and the fetch gate.

## Null control

Every arm has one in its self-test: `--apply` with every other group done proceeds past the roster; the old gh-api arm on a 4-ref plan makes 8 writes (2N) against 0 for the push arm; a `claude/*` tip is kept while the same tip on a `fix/` ref is deleted; a done group's `design/` ref is still deleted; a topic fully on main is archived then deleted; main and the open-PR head survive; a clean seat worktree at a pushed head is removed beside the kept unpushed one; a clean detached worktree at a head no remote holds stays `unmerged-head`, and one at the origin/main tip stays kept.

## Figures

- `python3 -I tools/audit/seat/prune_refs.py --self-test` -> SELF-TEST PASS (69 checks at fc47684e3; 67 before the alert 49 repair added its two checks).
- `python3 -I tools/audit/seat/closeout.py --self-test` -> 23 checks, 0 failed.
- `bash tools/audit/worktree_gc.sh --self-test` -> 91 checks, 0 failed.
- `python3 -I tools/audit/seat/selftest_wiring.py --check` -> 105 self-testing, 105 wired, 0 index gaps.
- Dry plan on the live refs: `python3 tools/audit/seat/prune_refs.py --prs-file <[]> --roster-file dev/programme/rosters/wave-r10-groups.json --verdicts-drained`; in this checkout most tips have no local objects, so their ages are unreadable and the refs are kept (`keep-young-tip`); the closeout run fetches heads first.

## Red checks

- `code-scanning alert 49 (py/overly-permissive-file)`: `tools/audit/seat/prune_refs.py` self-test created its `gh` stub and then widened it with `os.chmod`. Fixed by fc47684e3 (after fdcce70e9): the stub is created exclusively with `os.open(..., O_CREAT | O_EXCL, 0o700)`, no chmod, and the self-test asserts it carries no group/other bits. Killed mutant: `STUB_MODE = 0o700` -> `0o755` in `prune_refs.py` turns `the gh stub has no group/other permission bits` red (`SELF-TEST FAIL (68 checks)`), where the unmutated head reads `SELF-TEST PASS (69 checks)`; the paired null check pins that 0o755 reads wide and 0o700 private. Cheaper detector: that in-self-test mode check; standing cost: two checks inside a self-test that already runs in `selftest_wiring.py`'s wired set, milliseconds. The mutant was run by hand here, it is not a row in `r10_seat_selftests_mutants.py`. `CodeQL` is the authority for the alert and has not concluded at fc47684e3.
- `CodeQL`: red on the same alert 49; answered above.
- Earlier on this branch `prepr.sh` predicted two reds, both repaired before handoff: REF PRIVACY (closeout.py registered in PUSHERS as fixture pushes; its live writes are prune_refs.py's, which is guarded) and tests / closures INERT READS (`ci_predict.py --apply-inert`).
- No other red check is known at this head.

## Forward-carry

- The orchestrator's final `--apply` run (`python3 tools/audit/seat/closeout.py --roster-file dev/programme/rosters/wave-r10-groups.json --successor <N> --apply`): step 4 refuses until every open issue but the successor is dispositioned, and archiving merged cloud sessions is the orchestrator's. Carry: R10-CLOSEOUT-CLEANUP
- The probe refs for #2654 #2656 #2657 (`fix/r10-ci-layout-p2-probe-*`, `wip-sync/ext-upd-fix-r10-ci-layout-p2-probe-*`) are residue-no-pr and fall to that run's plan; no separate rule. Carry: R10-CLOSEOUT-CLEANUP

## Friction

none

BODY-END
