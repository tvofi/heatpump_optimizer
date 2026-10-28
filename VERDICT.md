Fix review: merge 46b2ba5a10195d91c80c93240f9c75b4cd1eed80

bus-nonce: dce32cdc98bd3f893567a30adbea5a48

## Round

First review round of #2939 (R10-ORCH-REVIEW-PACKET, carries pass). Measured at head `46b2ba5a10195d91c80c93240f9c75b4cd1eed80`, the same head at verdict time (`ev/refs-at-verdict.txt`). Merge base `593f57c44` = origin/main tip, so `git diff merge-base...origin/main -- dev/governance/roles/` is empty and the role contract is current.

## Findings

- Untested wiring: five targeted mutants of the I/O shell survive `review_packet.py --self-test` at 42 checks, 0 failed (`ev/own-mutants.txt`). They are: `gather` setting `handoff = None` (the whole live `handoff-not-applied` effect removed), `origin_handoff_tip` never reading the ref, `handoff()` counting 0 roster carries, `handoff()` returning 0 on refusals, and `is_ancestor` treating rc 1 as an ancestor. The pure functions the carries' controls name are pinned and killed. I confirmed the live wiring by hand (`ev/live-2887-handoff.txt`: #2887's old head `fdf33f466` refuses against `handoff/r10-buffer-store` `91a3d68`, its current head `a5b8603b` and #2939's head give None). `handoff()` exit and count also hold live (`ev/handoff-live*.txt`). No test pins any of it, so a regression in `gather`/`handoff()` would ship green. Carry: R10-ORCH-REVIEW-PACKET
- Roster carry 12 (triage P256, appended to the roster by `roster_edit append-carry` at 2026-10-28T22:02Z, after the code head `b51ffa069` at 20:52Z) is built by this PR but never named `Carry 12` in the body. The PR's own instrument now refuses its body at the code head: `review_packet.py handoff --topic r10-orch-review-packet --body <PR body>` gives `REFUSE brief-carries: carry 12 is not named in the body`, `12 carries, 1 refused`, rc 1 (`ev/handoff-live.txt`). The body's figure "11 carries" was true at the handoff and is stale now. Carry 12's text also names `handoff_push.sh` and `head-note`. The PR puts the check in `body_push.sh`, which is the only place a refusal can be answered "before the push", and it gives a reason for omitting `head-note` (prepr `--body-check`). The `handoff_push.sh` → `body_push.sh` departure is not dispositioned in the body, though. Any re-body of this group must name Carry 12 and state that placement. Carry: R10-ORCH-REVIEW-PACKET

## Evidence

- Mutation proof, the PR's named mutants (`ev/mutants.txt`, re-run in a clean worktree in `ev/mutants-bodypush-rerun.txt`): `review_packet-1` KILLED (42 checks, 3 failed), `-2` KILLED (1 failed), `-3` KILLED (IndexError), `-4` KILLED (1 failed), `-5` KILLED (2 failed). `body_push-1` and `body_push-2` both KILLED. `RESULT survivors=0`.
- The harness reports the body_push kills as rc=2, so I ran each body_push mutant by hand through `prepr.sh --self-test` (`ev/bodypush-arms.txt`). Each gives `420 passed, 1 failed` and fails exactly its own arm (P256 refusal arm; rc 3 arm), matching the body.
- Unmutated self-tests at the head: `review_packet self-test: 42 checks, 0 failed` (`ev/selftest.txt`); `prepr.sh --self-test` gives `421 passed, 0 failed`, rc 0 (`ev/prepr-selftest.txt`). Both re-derive the body's figures.
- Structure, budgets and policy lint at the head:
  - `tests/structure.py`: `STRUCTURE RATCHET PASSED`.
  - `policy_lint.mjs --budgets`: fixer.md 5216/5216 tokens, 314/315 lines; fix-review.md 2447/2451 tokens, 139/140 lines. No cap moved.
  - `policy_lint.mjs`: `TOTAL: 0 error(s) across 50 policy file(s)`.
  - All three re-derive the body's figures.
- Null control: carry 11's controls are present and pass (#2887 shape refuses; three null arms render; mutant `-1` fails the refusal and the first null arm). Carry 12's controls are present and pass (1-5-of-6 refused naming 6; passes with 6 dispositioned; zero carries passes; mutant `-3` fails).
- Class (step 6): the body names no enumeration rule. Each carry built here is one seam: P229 is the render's branch-to-handoff check, P256 the offline handoff subcommand and its one caller. I treat the class as one seam each. Carries 7 and 9 are dispositioned as not built and stay on the group.
- Forward-carry (step 10): carries 7 and 9 stay on the R10-ORCH-REVIEW-PACKET roster entry. The group is `carries-open`, at roster `a76528039`. #2925's host-path false positive is on R10-RECORD-API-O1 as its carry 3. I hit the same false positive rendering #2887's packet (`ev/render-2887.txt`, host-path on `dev/audit/rca/R10-RCA-BUFFER-STORE.md:9`), so it is a further instance of that carried cause, not a new finding.
- Merge: `git merge-tree --write-tree origin/main 46b2ba5a1` rc 0, no conflict (`ev/merge-tree.txt`).
- Claim files and versions: VERSION, manifest, RELEASE_NOTES and tests/golden are untouched (`ev/untouched.txt`). Neither claim file is in the diff, and no fixture moves, so env_drift has nothing to compare.
- CI at this head, all concluded (`ev/checks.txt`, 55 check runs): `gate` success at 23:40:18Z, and `pr-contract` success at 23:36Z and 23:39:44Z.
  - The one non-green run is `governance / instrument-self-tests`, concluded `cancelled` at 23:18:38Z. Every one of its steps concluded success, including "Show the review packet refusing its own fixtures" (job 123151258201, step list read from the jobs API; the log blob was 403 to this seat). The cancel is the workflow run's cancellation (run 40783261592, "CI code", cancelled), not a failing step. A `pr-contract` run started after it and is green, so by step 11 it owes no root-cause answer.
  - `tests / mutation` is success. The lane's log was not read: no answer here turns on it, since this diff's production lines are seat tooling, pinned by the harness above.
- Policy: the diff edits `dev/governance/roles/fixer.md` (P256) and `dev/governance/roles/fix-review.md` (P200). Both need tvofi's approving review at the head, or the mandate route for fix-review.md that the body names; this verdict is not that approval. P200 text checked against cloud_relay's four items (probe ref name, subject, first-line grammar, ev/): all four are stated.
- Body figure "#2887 now: refuses against c40766a90" is time-dependent and does not reproduce now. The handoff tip has moved to `91a3d68` and #2887's head to `a5b8603b`, which contains it (None). The historical `fdf33f466` refusal does reproduce. This is a figure as of its stamp, not a defect.
- Review packet rendered with main's tool (`ev/review-packet-maintool.md`, refusals none) and with the head's tool (`ev/packet-headtool.md`, refusals none, so `handoff-not-applied` passes this PR, whose handoff tip `b51ffa069` is an ancestor of the head).
- Finder's harness: none named (an instrument group). The controls stated in the roster carries are the design, and they are checked above. The five wiring mutants are my own instrument, built in a throwaway worktree, disclosed here.
