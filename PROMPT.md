CLOUD FIXER seat for tvofi/heatpump_optimizer, topic r10-outside-intake, at head b9b6af68683febf678907b19d7e73be453bc5bb7. Never send push notifications. Write no Claude Code footer, no Co-Authored-By or Claude-Session trailer and no claude.ai session link in any commit, pull-request body or comment you produce; check your commits with `git log --format=%B` before pushing.
Setup: `git fetch --unshallow --tags origin`. Before any commit, pin the seat identity: `git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com`. The session-start `toolchain:` line says whether venv-ci's python3 is on PATH: on REFUSE, start each Bash call with `eval "$(bash .claude/hooks/session-start.sh --env-lines)"`. Then run `bash tools/audit/seat/cloud-setup.sh --check`, and on REFUSE stop: report its line as your result and start no work. Run anything heavy in the background with Monitor and no timeout. Never wait in one tool call longer than 240 s; poll again instead.
Role: read dev/governance/roles/fixer.md from main, and follow it exactly, in a worktree of your own cut from origin/main. Fetch b9b6af68683febf678907b19d7e73be453bc5bb7 for the base you were given.
Output: push each verified step, fast-forward only, to refs/heads/handoff-wip/r10-outside-intake before any wait on a background run, so an idle container loses nothing; never step-push to handoff/r10-outside-intake, whose move updates the pull request. Before the handoff, when origin/main has moved since your last `tools/pr/prepr.sh` run, `git merge origin/main`, rerun `tools/pr/prepr.sh` (the body check included) and fix what it refuses; hand off only on a clean run (an unmoved main needs no second run: say so in the body). Then push the code to refs/heads/handoff/r10-outside-intake, then write the PR body and run `bash tools/audit/seat/body_push.sh r10-outside-intake <body.md>`, which pushes refs/heads/handoff-body/r10-outside-intake; that second push is the return signal. Once it succeeds, delete the step ref: `git push origin :refs/heads/handoff-wip/r10-outside-intake`. Push nothing else, open no pull request and write no delivery row. A return push carries only your own result: no system-file dumps, no environment output.
Never write to any branch except your return refs and refs/heads/handoff-wip/r10-outside-intake and refs/heads/handoff-wip/r10-outside-intake-body. Never work around a hook or a refusal; report it in your result instead.

Brief (snapshotted when this payload was rendered):
INTERIM TOOLCHAIN: this environment's cached venvs are behind the locks (numpy, scipy, homeassistant, measured 2026-11-04). Before any measurement run: `bash tools/audit/seat/cloud-setup.sh` and then `bash tools/audit/seat/cloud-setup.sh --check`. Medium effort.
Fixers return only by refs (handoff_push and body_push.sh); open no PR, post no comment; no Claude footers; no host paths; git identity hpo-fixer with the noreply address; never touch VERSION, the manifest version or the RELEASE_NOTES heading.

CLOUD FIXER (opus), REPAIR ROUND 6 for PR #3262 (R10-OUTSIDE-INTAKE), topic r10-outside-intake, branch handoff/r10-outside-intake. HIGH PRIORITY: the owner's link comments to outside contributors wait on this public plan page going live. Follow dev/governance/roles/fixer.md; steps 2-8 re-execute. The PR head is b9b6af68683febf678907b19d7e73be453bc5bb7, BLOCKED in round 5 by verdict/3262 (ci-red, the full verdict is below and on refs/heads/verdict/3262 with its ev/, read-only). The round-4 block (mutation-vacuous) is cured by the reviewer's own re-run; do NOT touch plan_public.py's cured lines. Merge origin/main, never rebase.
THE BLOCK: only CI. Code run 42385084286 at the head was cancelled with the required jobs running, and no re-run came, so classify reads RED on gate. Cure: your repair pushes a FRESH head (merge origin/main, which is a real change of head), so the head's runs start anew; then wait for the head's code run to conclude and make `merge_train.py classify <head> --pr 3262` read GREEN before handoff. If a fresh run is cancelled again by a runner stall, say so in the body and name the run.
OWED IN THE SAME REPAIR (body-only plus the four findings below, each carried to R10-OUTSIDE-INTAKE; fix those cheap enough in the minimal re-cut, or route with a Carry line):
 - Re-take the WHOLE body from the kept handoff-body and .github/PULL_REQUEST_TEMPLATE.md; `## Head` names the new head and carries a `## Re-cut note` (round 6, minimal); `## Red checks` names every concluded red of the NEW head across ALL check-run pages and answers each (the verdict lists the old head's: gate 128449147307 failure, gate 128449368751 cancelled, tests / nightly-status 128443914073 failure which grades main's cancelled Nightly 42369836867 that this diff does not read, and the cancelled jobs of run 42385084286). Run `bash tools/pr/prepr.sh --body-check <body> --pr-branch fix/r10-outside-intake`, carry_audit.py and structure.py until clean.
 - The "between rounds there is no state ref" sentence in plan_public.py's docstring and the pages.yml header is false (nothing retires handoff/audit-r<N>-plan before closeout.py --apply): correct it or keep it carried and named in the body.
 - Two outside_intake.py mutants survive (scan_disc_kind, owed_reply_ge) and main_url_rc1 survives (low): kill them with a named check each if one case apiece suffices, else keep the carry.
THE FULL BLOCKED VERDICT (carry):
Fix review: blocked b9b6af68683febf678907b19d7e73be453bc5bb7 ci-red: code run 42385084286 was cancelled at this head and no re-run came within 60 minutes, so merge_train classify reads RED on gate

bus-nonce: fc4e799764c94c5691ed9dc4be8b700a

This is round 5 of the fix review of #3262 (R10-OUTSIDE-INTAKE), at head b9b6af68683febf678907b19d7e73be453bc5bb7. It is the minimal re-cut owed past three rounds. I worked from a detached worktree at the head. The merge base is a37c58e5f32123b4028e90983799dc2aa81816f8. This is a policy and developer-docs PR: it merges only on tvofi's approving review at the head.

## Block

The round-4 block is cured. Only CI blocks this head.

- **The round-4 block is cured.** In my own re-run, with the finder's set widened to mutate every line but the `MUTANTS` table, `host_ident_dropped` (L67) and `main_rc0` (L233) are each KILLED by a named check:
  - `host_ident_dropped`: "the CLI over a scratch repository: a clean page is staged, rc 0".
  - `main_rc0`: "the CLI over a scratch repository: a page naming a home directory is refused, rc 1 and nothing written".
  - The full `--self-test` prints both `ok   mutant ... killed by:` lines.
- **CI at this head is RED.**
  - What happened: code run 42385084286 (attempt 1, triggered by `hpo-author[bot]`) ended `cancelled` at about 15:46:18Z, with the required jobs still running. Those jobs were `tests / fast (3.14)`, `tests / browser`, `tests / closures`, `tests / coverage`, `governance / instrument-self-tests` and `codeql / Analyze (python)`.
  - The gate: `gate` 128449147307 (KIND edit, 15:46:01Z-15:47:29Z) concluded `failure` with `FAIL tests / fast (3.14): cancelled (run 42385084286)`.
  - My wait: I watched for a re-run or a head move from 15:47Z to 16:48Z. Neither came.
  - Final read: `merge_train.py classify` at 16:48:35Z gives `RED b9b6af68683febf678907b19d7e73be453bc5bb7 pending: none red: gate` (rc 1).
  - Why it blocks: a red CI never carries a merge verdict, and the code jobs that would show this tree green have not concluded at this head.
  - Cure: re-run run 42385084286, or push a fresh head. Then let the head's runs conclude, and take the next review at a green classify.
- **`## Red checks` names the previous head's reds, not this head's.** The section reads aa5022f63's 160 runs. At b9b6af686 it names none of the 15 concluded non-success runs (`ev/reds.tsv`). This is owed with the cure: once the head's runs conclude, the body must name each concluded red across all check-run pages and answer it. `defect-root-cause.md`'s red-check trigger applies.

## Findings

- **Red checks are stale at the head.**
  - Claim: `## Red checks` does not name the concluded reds at b9b6af686:
    - `gate` 128449147307, failure.
    - `gate` 128449368751, cancelled.
    - `tests / nightly-status` 128443914073, failure. It grades main's cancelled Nightly 42369836867 at 08fd676, which this diff does not read.
    - The cancelled jobs of run 42385084286.
  - Evidence: `ev/check-runs.tsv`, `ev/reds.tsv`, `ev/gate-128449147307.txt` and `ev/nightly-status-128443914073.txt`.
  - Harness: the check-runs API with `filter=all`, two pages.
  - Metric: concluded reds not named. This head has 15; the body names 0 of them.
  - Perturbation: none applies; this is a read of state.

  Carry: R10-OUTSIDE-INTAKE
- **Docstring and workflow-header sentence still false.**
  - Claim: the "between rounds there is no state ref" sentence stays in `plan_public.py`'s docstring and in the `pages.yml` header. Nothing retires `handoff/audit-r<N>-plan` before `closeout.py --apply`. The body now names the sentence as carried rather than claiming it.
  - Evidence: the round-4 verdict, plus `git diff aa5022f63 HEAD -- .github/workflows/pages.yml`, which is empty.
  - Harness: `newest_round` over the remote's refs.
  - Metric: the round it would publish.
  - Perturbation: none applies.

  Carry: R10-OUTSIDE-INTAKE
- **Two `outside_intake.py` mutants still survive.** `scan_disc_kind` and `owed_reply_ge` SURVIVE the cases-only run at this head (`ev/reviewer-mutants-casesonly.txt`). They are unchanged since round 4. Carry: R10-OUTSIDE-INTAKE
- **`plan_public.py main()`'s `url` subcommand exit status is unpinned.**
  - Claim: the mutant `main_url_rc1` (L227 `return 0` made `return 1`, after `print(PLAN_URL)`) survives.
  - Evidence: `ev/reviewer-mutants-plan_public.txt`.
  - Severity: low. Only the usage line in the docstring calls `url`, and no workflow or tool does (`git grep 'plan_public.py url'`).
  - `main_print_stdout`, which sends the success message to stderr, is cosmetic and equivalent for the workflow, which reads only rc.

  Carry: R10-OUTSIDE-INTAKE
- **Edit-run gate reds recur.** The edit-run gate reds (`gate` failing on a deferral, or on another run's cancelled jobs) recur at this head, after R10-HOTFIX-GATE-BUSY-DEFER. Carry: R10-HOTFIX-GATE-BUSY-DEFER

## Evidence

- Setup: `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`. `review_packet.py render` gave rc 0, with Refusals none (`ev/review-packet.md`, `ev/packet.log`).
- Round-5 delta aa5022f6..b9b6af68, branch-own:
  - `78389d732`: the CLI case and two MUTANTS entries.
  - `22e1f930f`: the `throwaway_git_init` scratch repository.
  - The rest are main merges.
  - `outside_intake.py`, `outside_intake_selftest.py`, `pages.yml` and `dev/governance` are unchanged since aa5022f6 (`git diff --quiet` held).
  - Only `tools/audit/seat/plan_public.py` changed: 41 lines added, 4 removed.
- `plan_public.py` mutation proof (`ev/mut_pp.py`, `ev/reviewer-mutants-plan_public.txt`): the finder's 18-mutant round-4 set, widened to mutate code above and below the table, plus 2 new main() mutants. Cases-only.
  - Null control: NULL rc 0.
  - KILLED (15): `int_dropped`, `max_to_min`, `regex_no_end`, `html_check_off`, `leak_off`, `attribution_off`, `host_ident_dropped`, `refused_rc0`, `absent_rc1`, `noref_rc0`, `write_empty`, `dest_name`, `main_rc0`, `main_repo_cwd_ignored`.
  - SURVIVED, equivalent or near-equivalent as in round 4: `html_case_sensitive`, `rc_ignored_refs`, `show_rc_ignored`, `empty_text_published`.
  - SURVIVED, new: `main_print_stdout` (cosmetic) and `main_url_rc1` (finding above).
- Full `plan_public.py --self-test`: rc 0, 18 `ok` lines, of which 6 are mutant lines (`ev/selftest_pp.txt`). That matches the body's 12 cases and 6 mutants. The named kills for `host_ident_dropped` and `main_rc0` are printed there.
- Real CLI drive (`ev/drive_pp.sh`, `ev/drive_pp.txt`): the clean page gives rc 0 and is staged; the leaky page gives `REFUSED ... host-path in the page`, rc 1, and nothing is staged.
- `outside_intake.py` mutation proof, cases-only (`ev/mut.py`, `ev/reviewer-mutants-casesonly.txt`): NULL rc 0, with the same results as round 4.
  - `one_thread_pr_reviews_drop` is still KILLED by its named case.
  - Survivors: `mark_old_restored_EQUIV`, `scan_disc_kind`, `owed_reply_ge`, `has_disc_ignored` and `plan_live_200`.
- Cheap checks at the head (`ev/checks.txt`):
  - `ref_privacy`: 0 refused. `tmp_paths`: 0 refused.
  - `selftest_wiring`: 120 self-testing, 120 wired, 0 unwired, 0 index gaps.
  - `throwaway_git`: 0 refused.
  - `STRUCTURE RATCHET PASSED`. `ALL 2646 ENTITY CHECKS PASSED`. `ALL 112 HARNESS HEADER CHECKS PASSED`.
  - `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
  - `Architecture score: dS +0.0000 NULL`.
  - `outside_intake self-test: all checks passed`.
  - No budgets, VERSION, RELEASE_NOTES, manifest or claim file is in the three-dot diff (count 0), and `dev/programme/delivery/3262.md` is in it.
  - Every body figure re-derived equal.
- Merge: `git merge-tree --write-tree origin/main HEAD` against 1c1ae100b gives rc 0, tree b20199172aec2799b66623bceff6d333adc55591, with `LEDGER-MERGE: resolved tests/closures.json`.
- `## Head`: it names b9b6af686 merging f69a1caf9, which matches what I measured. The head did not move during the review.
- CI: `ev/check-runs.tsv` (55 runs, all pages) and `ev/classify.log`. The classify history ran WAIT from 15:35Z, then RED at 15:47Z and RED again at 16:48Z.
- The owner's 2026-11-06 ruling is quoted verbatim in the body. This is a policy and developer-docs PR: it merges only on tvofi's approving review at the head.

Before any commit run: export GIT_AUTHOR_NAME=hpo-fixer GIT_AUTHOR_EMAIL=70032254+tvofi@users.noreply.github.com GIT_COMMITTER_NAME=hpo-fixer GIT_COMMITTER_EMAIL=70032254+tvofi@users.noreply.github.com, and also git config user.name hpo-fixer && git config user.email 70032254+tvofi@users.noreply.github.com. The cloud environment exports GIT_AUTHOR_*/GIT_COMMITTER_* as 'seat', and those environment variables beat git config, so the config alone does not hold. Never commit as 'seat'; check with git log -1 --format='%an %ae %cn %ce' after the first commit.


Discovery reads (search, list, read across files) go through Agent subagents, as the frugal routing guard requires; at most 5 inline search operations per prompt; never set FRUGAL_ALLOW_INLINE.


TIME: you have hours, not minutes. A gate, prepr or recording may run an hour: wait with Monitor windows of up to 60 min and re-arm them. Never end the session waiting on a choice: take the option that keeps coverage and the architecture sound, say so in the body, and go on. Push handoff-wip at each milestone, so your liveness can be read. If truly blocked, push BLOCKED.md on handoff-wip naming the question.
