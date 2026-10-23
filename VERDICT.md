Fix review: blocked 9ef0633bcd6f31482a3ccf0f8da901431e5c6e01 carry-missing: not carried to R10-CI-LAYOUT-P2

bus-nonce: 30a9db29886998bead891d5333a5e0f9

Round 1. Reviewer seat (opus-fixer), detached worktree at head `9ef0633bcd6f31482a3ccf0f8da901431e5c6e01` (merges code head `7030f1b60` and origin/main `c5e1be196`). Contract currency: `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/` empty.

## The block

The body measures, and I re-measured, that item 2 refuses the next `app_push.sh` push of three open pull requests of the live group R10-CI-LAYOUT-P2 (roster `resume.stage: in-progress`, `resume.pr` 2657): the shipped guard `python3 -I tools/audit/seat/ref_privacy.py guard --ref fix/x --commits refs/rev2668/pr<N> --over refs/remotes/origin/main`, each head fetched from `refs/pull/<N>/head`:

- RESULT pr2662 rc=3 `session-link, session-trailer, co-author-trailer in the message of cc51e6626c91`
- RESULT pr2657 rc=3 (same commit, same classes)
- RESULT pr2656 rc=3 (same commit, same classes)
- RESULT pr2670 rc=0 (null control; the body's eight passing PRs are its own)

`git merge-base --is-ancestor cc51e6626 origin/main` exits 1, so a main merge does not clear it, and a history rewrite needs the force-push the session forbids. That removes an option a not-yet-finished stage was expected to have (`finding-propagation.md`: "removes an option it was expected to have — ... an interface is not available"): update_pr/app_push for those three branches. The body records it under "Existing open PRs that item 2 would refuse", and `## Forward-carry` says `none`. R10-CI-LAYOUT-P2's brief and its 18 carries at `origin/handoff/audit-r10-roster` (committed 2026-10-23T19:57:31+02:00) contain no `cc51e`, `trailer`, `attribution`, `co-author`, `no-footers` or `2668` (my `jq … | grep -niE` printed nothing). A finding written only in this PR's body or comments is not propagation (fix-review step 10). Repair: a roster carry to R10-CI-LAYOUT-P2 (through the orchestrator's `roster_edit.py`) stating the precondition, namely that a P2 branch carrying `cc51e6626c91` in `origin/main..<head>` is refused by `app_push.sh` once #2668 merges, so the branch must be rebuilt without that commit (a fresh branch and a cherry-pick with the trailers removed, not a force-push) before its next push, with the guard command above as its control. Then name the file, the stage and the roster branch SHA under `## Forward-carry`. No code change is owed.

## Everything else checked passes

- **Step 1, mutation proof.** Driver `mutants.py` (my own, kept in the evidence dir) uses one `git clone --shared` of the head for each mutant, and asserts that the target text appears exactly once. All of the fixer's eight mutants were killed, plus one of mine:
  - M1 (handoff_push guard line replaced by `true`): `handoff_push self-test: 3 checks, 1 failed`, `FAIL a code head carrying a co-author trailer is refused, and nothing is pushed`.
  - M2 (body_push back to `--message "body: $TOPIC"`): `ref_privacy self-test: 90 checks, 2 failed`, failing the session-link row and the author-email row.
  - M3 (body_push guard replaced by `true`): 90 checks, 3 failed.
  - M4 (ci_probe `refusal(short)`): `ci_probe self-test: 42 checks, 2 failed`, `FAIL push refuses a commit carrying a co-author trailer, before any API write`.
  - M5 (app_push drops `--over`): `app_push self-test: 199 checks, 87 failed`, including `FAIL real git: a trailer commit first published on ci-probe/* is refused when the PR carries it (got '00', want '13')`. The null-control row stays `ok`.
  - M6 (fence ignores `over`): 90 checks, 1 failed, `FAIL --over origin/main refuses it, exit 3`.
  - M7 (copyin drops `ref_privacy.py`): `pr_args self-test: 93 checks, 6 failed`, the three `handoff_push` reap arms plus the three Darwin arms.
  - M8 (r9 handoffpush `cp` line deleted): `verdict: no body written … the arm never reached the read`.
  - M9 (mine: handoff_push drops `--over`, back to first-publish scope): handoff_push 3 checks, 1 failed (the trailer row).
- **Head self-tests**, on the seat interpreter: `ref_privacy self-test: 90 checks, 0 failed`; `ci_probe self-test: 42 checks, 0 failed`; `app_push self-test: 199 checks, 0 failed`; `handoff_push self-test: 3 checks, 0 failed`; `pr_args self-test: 93 checks, 3 failed`. The 3 are `a runner without pr_exit_trap is refused`, `a runner whose push runs in the foreground is refused …` and `mutant afterreap …`, the GNU `sed -i` arms the body names. They are environmental here (Darwin), and CI's `instrument-self-tests` runs them on Linux.
- **Steps 2 and 3, harness and null control.** No finder's harness was committed; the finding is the #2662 round-2 observation recorded in the brief (step 9). The fixtures are the fixer's own, and the body discloses that. Each new path has a passing null in the runs above.
- **Step 6, class.** I enumerated it with `ref_privacy.PUSHERS` plus `ref_privacy.py --check` (`25 file(s) with a push site, 12 guarded, … 0 refused`) and a `git grep` for `git … push` over `tools .github .claude/workflows`. Every path that publishes a composed commit judges its message through `refusal()`/`attribution()`:
  - wt_sync, bus, heartbeat, roster_edit, state_docs, cloud_dispatch, stamp: on the composed message.
  - push.sh, app_push, body_push, ci_probe: on the commits.
  - handoff_push, plus open_pr/update_pr/remerge_main through app_push.
  - The `republishes` entries (merge_main_bot, merge_train, tests.yml, nightly.yml) carry constant messages. The `fixture` and `prompt` entries publish nothing. The cloud harness's own push is out of tree and disclosed in the body.
  - The grep hits that are not registered (ci_critpath, r10_deeplink_mutants, gate.py, prelude.py, cancel_superseded, codeql_scope, contract_rerun, governance.yml) hold no push of a commit.
- **Step 11, red checks.** `instrument-self-tests` and `pr-contract` were red at 88c469c7e, and both are named and answered in `## Red checks`. No other commit in the range was red. At this head, `delivery-status` is red, but it grades main, and the only row the diff touches is its own `dev/programme/delivery/2668.md`, so it is not this PR's. The final state of every check at this head is in `checks-9ef0633.txt`.
- **Step 13.** `git merge-tree --write-tree origin/main HEAD` exits 0.
- **Steps 5 and 14.** VERSION, the manifest version, the notes heading, the claim files and every budget are untouched.
- **Step 7.** The body's `## Head` names `9ef0633bc…`, which is the head I measured.
- **Sibling.** `handoff/r10-fly-no-footers-ignore` (`227e228fa`) is already an ancestor of origin/main, so it does not overlap.

## Non-blocking

- `tools/pr/push.sh` still judges only first-published commits (`--commits HEAD`, no `--over`), so hole (2) remains open there. Carry: dismissed: push.sh is the retired author path (decision 0011), and `pr-contract` refuses any PR it would author.
