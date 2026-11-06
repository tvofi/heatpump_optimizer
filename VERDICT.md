Fix review: blocked 48acc104f97cf88bf0ec28a3f6ec01438e169bb5 mutation-vacuous: outside_intake.py main() cursor persistence and post() rc/argv survive the self-test

bus-nonce: 4a87b62c877e4833fade878ba3289f34

Round 1 of the fix review of #3262 (R10-OUTSIDE-INTAKE), at head 48acc104f97cf88bf0ec28a3f6ec01438e169bb5. I worked from a detached worktree at that head and diffed three-dot against the merge base 28482eceeb6b9809e44b12d80fc994282cc21645. `git diff <mb>...origin/main -- dev/governance/roles/` is empty, so the role contract is current. This is a policy and developer-docs PR: it merges only on tvofi's approving review at the head.

## Block

The brief asks for the intake's core lines to be mutated and each mutant shown killed. The body says "Every arm is pinned by an in-tree mutant". Six production lines in `tools/audit/seat/outside_intake.py` survive `--self-test` (rc 0). The command is `python3 -I tools/audit/seat/outside_intake.py --self-test`, and the evidence is in `ev/reviewer-mutants.txt`.

- **Cursor read** (L339). `since = json.loads(a.cursor.read_text()).get("since") or since` -> `pass` SURVIVED. The beat row would rescan from `--since` every time, so it never advances.
- **Cursor write** (L354). `{"since": keep}` -> `{"since": utc()}` SURVIVED. This is the documented guarantee "a submission never drops out while owed". The `cursor_jumps` mutant pins it only inside `listing()`. `main()` persists its result unpinned, so after one pass a still-owed submission older than the pass would fall out of the scan.
- **Answer step's read-back rc** (L279). `return runner(argv).returncode` -> `runner(argv); return 0` SURVIVED. If `gh_comment.py` posts but the read-back is not byte-identical, `answer` still prints `answered rc=0`. Brief item (3) asks that the answer goes through gh_comment.py with read-back. The read-back exists in gh_comment.py, but its verdict is not pinned on the way through.
- **`--dry-run` passthrough** (L278). Dropping `+ (["--dry-run"] if dry else [])` SURVIVED. With this mutant, `answer --dry-run` would post a live comment on an outside user's thread.
- **gh_comment script path** (L278). Changing it to a missing script SURVIVED. `post()` is never exercised: every case injects a fake `poster`.
- **List rc** (L356). `return 1 if lines else 0` -> `return 0` SURVIVED. Its only consumer, `beat_jobs.outside_intake`, treats rc 0 and rc 1 alike, so this mutant is equivalent for the beat. It breaks the documented CLI contract, and I record it but do not block on it.

All six lines are in the brief's scope: (2) "since a cursor" and (3) "through gh_comment.py with read-back". Cure: one self-test case that drives `main(["list", ..., "--cursor", tmp])` twice over the fixture world, and one that drives `post()` with a recording `runner`. The recorded argv should be asserted (script path and `--dry-run`), and a runner returning rc 1 should be asserted to yield a non-zero `answer`. Each of the six mutants should be added to `MUTANTS`.

## Findings

- **Unpinned plumbing.** Claim: `outside_intake.py` `main()` (cursor read L339 and write L354) and `post()` (argv L277-278 and rc L279) are not pinned by the self-test. Evidence: `ev/reviewer-mutants.txt` shows 5 non-equivalent SURVIVED plus 1 equivalent. Harness: `python3 -I tools/audit/seat/outside_intake.py --self-test`. Metric: rc. Perturbation: each one-line mutant above moves nothing (rc 0); the null control is the unmutated run, rc 0, and the 8 other reviewer mutants on the same file, all KILLED rc 1. Carry: R10-OUTSIDE-INTAKE
- **Any bot's marker disposes of a thread.** Claim: `Thread.mark` (L132-139) treats every non-`outside()` comment as ours, and `outside()` excludes every `Bot`. So an ANSWER_MARK or REFUSED_MARK in a comment by any bot disposes of a thread. The docstring (L22-29) says "a comment by OURS". Evidence: `ev/marker-trust.txt`. On #3225, wired to R10-COMBI-TANK, a marker comment by `renovate[bot]` (Bot) gives `answered` set and owed=None. `hpo-approver[bot]` gives the same, as intended. The null control `Bankaifan` (User) gives `answered=''` and owed=answer. Harness: direct `Thread`/`owed` drive. Metric: owed word. Perturbation: the author login and type move the result. Risk: a third-party App that quotes a submitter's text, such as a review bot that summarises a PR body, would silently close the intake for that thread. Cure: read markers only from `login in OURS`, and add a case plus a mutant. Carry: R10-OUTSIDE-INTAKE
- **Unanswered reds.** Claim: `## Red checks` names none of the head's concluded reds. Four `gate` check runs concluded `failure` at this head: 128203011639, 128206299696, 128215975302 and 128215984338. Each one prints `FAIL run(s) [...] at this head are still being judged; their gate decides`. The last two, at 23:28:43Z and 23:28:44Z, each name the other's workflow run (42309082852 and 42308039479), which looks like two gate runs racing. Every other check run at the head concluded success, skipped or neutral (CodeQL); `ev/check-runs-final.tsv` has all 68. `governance / instrument-self-tests` concluded success, not cancelled. The body owes these reds a line, or a gate re-run must turn the context green. It is not a defect of the authored code. Harness: the head's check-runs API, all pages. Metric: concluded reds not named. Perturbation: none applies; this is a read of state. Carry: R10-OUTSIDE-INTAKE

## Evidence

- Setup: `cloud-setup check: OK python3 is /opt/hpo/venv-ci/bin/python3`.
- `review_packet.py render`: `REFUSE required-red: required context gate concluded failure`. The packet was still written. Live checks were re-read at the end, after all 68 runs completed.
- Merge: `git merge-tree --write-tree origin/main HEAD` gives rc 0, `LEDGER-MERGE: resolved tests/closures.json`. origin/main is at 80016a71f567d936450d8708abcbb79d9e8071d7. The branch tip was re-read before return and is still 48acc104f97cf88bf0ec28a3f6ec01438e169bb5.
- CI: `merge_train.py classify` printed `RED 48acc104f97cf88bf0ec28a3f6ec01438e169bb5 pending: none red: gate` (rc 1), after every check run at the head had completed (`ev/classify.log`).
- Self-tests re-run at head (`ev/selftests.txt`, `ev/beatd-selftest.txt`):
  - `outside_intake self-test: all checks passed`, rc 0. The 11 in-tree mutants are each killed, matching the body.
  - `plan_public self-test: all checks passed`, rc 0.
  - `beat_jobs self-test: 136 checks, 0 failed`.
  - `beatd self-test: 119 checks, 0 failed`.
  - `sweep_render self-test: 34 checks, 0 failed`.
  - `selftest_wiring: 119 self-testing, 119 wired, 0 unwired` and `0 index gap(s)`.
  - `ref_privacy --check`: `0 refused`. `tmp_paths`: `0 refused`.
- Reviewer mutants killed (rc 1):
  - OURS without `tvofi`.
  - `disposed = t.answered`.
  - reply ignoring `last_ours`.
  - `if True:` for the roster test.
  - PLAN_URL dropped from the answer body.
  - the `answered` set dropped.
  - `plan_public` `min(rounds)`.
  - `plan_public` privacy `leaks()` dropped.
- Figures re-derived at head (`ev/figures.txt`, `ev/scope.txt`):
  - `MODE: SCOPED -- 2 script(s) run, 31 scoped out.`
  - `STRUCTURE RATCHET PASSED`.
  - `Architecture score: dS +0.0000 NULL`.
  - policy_lint `--budgets`: `orchestrator.md` 292/295 lines and 4234/4251 tokens; `standing-dispatch.md` 37/39 and 507/509. These match the body.
  - No change to VERSION, RELEASE_NOTES.md, any manifest or any `*budgets.json`. `dev/programme/delivery/3262.md` is in the diff.
  - The three new `.py` files are in `tests/closures.json` `inert_reads`. `tests / closures` concluded success.
  - I did not re-run the scoped gate (`ALL 2638 ENTITY CHECKS PASSED`); CI's heavy runs are cited. The live intake listing (#3224, #3226 owed triage, #3225 waiting) needs the network and roster ref and was not re-derived.
- Fixtures: #3224, #3225 and #3226 are fixtures in `outside_intake_selftest.py` (L55-57, L66, L68, L83-85). #3231 appears only as a group name and in comment text, and #3232 not at all, only in the docstring. That is enough for the "via" relation. There is a null control ("list null").
- Read-back: `tools/pr/gh_comment.py post` exits non-zero unless the read-back is byte-identical. The gap is only the passthrough (see Block).
- Answered twice: the in-tree mutant `answer_twice` is killed. `dispose()` re-reads the thread before posting.
- `## Head`: it names 48acc104 as the head. Its figures were taken at 9a865c7bc2cf3b2a5e43c369064d3bf8ac5c8260, which differs from the head only by `dev/programme/delivery/3262.md`. The paragraph opening with the bare SHA 9a865c7 reads as a stray fragment, but the head named is current.
- Policy part: it merges only on tvofi's approving review at the head. The ruling is quoted verbatim in the body.
