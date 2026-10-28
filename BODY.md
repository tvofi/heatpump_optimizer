R10-ORCH-REVIEW-PACKET, carries pass (stage `carries-open`, after #2870). This pass builds roster carry 11 (P229, `handoff-not-applied`), carry 10 (P200, the relay format in `fix-review.md`) and carry 12 (triage P256, the review packet's offline refusals at the handoff). It does not build carries 7 and 9 (dispatch at the handoff ref); see `## Forward-carry`.

- **`tools/audit/seat/review_packet.py`**
  - New render signal `handoff-not-applied` (P229). The branch comes from the pull request `gather` already reads. When it is `fix/<t>` or `fix/<t>-pr` and `origin/handoff/<t>` exists, the render refuses if that ref's tip is not an ancestor of the head.
  - New subcommand `handoff --topic T --body FILE` (P256). At the checkout's `HEAD` it runs `structure` (merged with main) and `hot-file`, plus a new count, `brief-carries`. That count takes the group from the round roster (`roster_lib.group_for_branch` of `handoff/<topic>`) and refuses each 1-based carry index the body never names as `Carry N`. Exit codes match `render`: 0, 1 refused, 3 unavailable.
  - `handoff_refusals()` is the one spelling of the structure and hot-file refusal lines, used by `render` and `handoff` alike. The hot-file reads moved into `hot_prs()`, shared by both.
- **`tools/audit/seat/body_push.sh`**: after the pr-body lint, runs `review_packet.py handoff`. On rc 1 it pushes nothing. On rc 3 it says so and pushes, because a seat that cannot read the inputs is not refusing the head. `HPO_HANDOFF_PACKER` is the self-test stub, the same pattern as `bus.sh`'s `HPO_BUS_PACKER`.
- **Not run again at the handoff:**
  - `head-note` is already checked at the same push: `prepr.sh --body-check` hands `policy_lint.mjs` `--head HEAD` (`body_check`).
  - `red-unanswered` and `required-red` stay at dispatch, per the owner's card 5 ruling. The CI-wait half of P256 is not built: the owner rejected it.
- **Policy, one commit each, merging on tvofi's approving review:**
  - `dev/governance/roles/fixer.md` step 6: `body_push.sh` runs `review_packet.py handoff`'s offline refusals, and each is answered before the push (P256). Paid in the same step by dropping the restated `prepr.sh` step 1a clause. The file sits at its token cap: `node tools/policy/policy_lint.mjs --budgets` prints 5216 against 5216.
  - `dev/governance/roles/fix-review.md`: the four checks `cloud_relay.sh` grades a cloud verdict on (P200). They are the probe ref name `probe/rev-<pr>-<nonce first 8>`, the commit subject `verdict <pr> <head40>`, the first-line grammar with class `[a-z-]+`, and `ev/`. They sit beside the two the file already stated. Paid in the same file by shortening the restated `fixer.md` preamble and replacing the retired `web-fix-wave.js` pointer with the grammar it now states. The file ends under its cap: 2447 against 2451 tokens, 139 against 140 lines.
- **`dev/audit/harnesses/r10_seat_selftests_mutants.py`**: seven in-tree mutants. `review_packet-1` to `-5` are graded by `review_packet.py --self-test`. `body_push-1` and `-2` are graded by `prepr.sh --self-test`, which drives `body_push.sh`.
- **`tools/pr/prepr.sh`** self-test: two `body_push` arms, a refusal (rc 1, body ref unmoved) and an unavailable checker (rc 3, pushed).
- **`tools/audit/seat/INSTRUMENTS.md`**: the new signal and subcommand.

Refs #2717. Not closed: carries 7 and 9 stay open on this group.

## Head

`d2e92490232ae946eca69d430a24208584e38d63`, the merge of `origin/main` at `b0b2d7697f8c5baaef2c082d9bf3242b57249e68` into the previous handoff `b51ffa069`. The merge was clean and changed none of this diff's seven files (`git diff --stat b51ffa069 d2e924902 --` those files prints nothing). Every figure below was re-taken at this head, over that `origin/main`, on 2026-10-28 (UTC). `origin/main` has since moved to `593f57c44fa57490ed757343b9f277ef97ad5ca5` (fetched 23:03Z); `git merge-tree --write-tree origin/main d2e924902` reports no conflict, so the head is not merged again (`fixer.md` step 6).

## Mutation proof

`python3 dev/audit/harnesses/r10_seat_selftests_mutants.py review_packet-1 review_packet-2 review_packet-3 review_packet-4 review_packet-5` gave `RESULT survivors=0`:
- `review_packet-1` inverts the ancestry test: KILLED, `42 checks, 3 failed`. Both the #2887 refusal arm and the head-containing-tip null arm go red.
- `review_packet-2` drops the build's `handoff-not-applied` line: KILLED, `42 checks, 1 failed`.
- `review_packet-3` skips the `brief-carries` count: KILLED. The self-test dies (`IndexError`) on the `Carry [10]` row, so its exit is non-zero.
- `review_packet-4` drops the `fix/<t>-pr` spelling: KILLED, `42 checks, 1 failed`.
- `review_packet-5` drops the hot-file line from `handoff_refusals`: KILLED, `42 checks, 2 failed`.

`body_push-1` and `body_push-2` replace `body_push.sh`'s refusal branch with `if false` and `!= 0` respectively, each graded by `prepr.sh --self-test`. Run with `python3 dev/audit/harnesses/r10_seat_selftests_mutants.py body_push-1 body_push-2 prepr-13`: all three KILLED, `RESULT survivors=0`. `prepr-13` is the existing mutant of that name, still killed with the new STEP_OF rows beside it.

Each `body_push` mutant was also run alone, through `prepr.sh --self-test` in a throwaway worktree of `d2e924902`, to name the arm it kills. Each kills exactly its own (`420 passed, 1 failed`):
- `body_push-1` fails `and refuses a body the review packet's handoff refusals refuse, naming the signal and pushing nothing (P256)`;
- `body_push-2` fails `and pushes, saying so, when the handoff refusals cannot be run (rc 3 is never a refusal)`.

## Null control

At the base `b0b2d7697`, `python3 -I tools/audit/seat/review_packet.py handoff --topic r10-orch-review-packet --body /dev/null` exits 2 with `invalid choice: 'handoff'`. The same tree's `review_packet.py --self-test` prints `31 checks, 0 failed`; none of the new rows exist there.

Each new rule has a null arm in `--self-test`:
- `handoff-not-applied`: a head containing the handoff tip renders; a branch with no `handoff/<t>` ref renders; a non-`fix/` branch renders.
- `brief-carries`: the 1-5-of-6 body passes once carry 6 is dispositioned; a group with no carries passes.
- `handoff`: a clean head refuses nothing.
- `prepr.sh`: the existing "pushes a body the lint passes" arm is the clean-checker null. It now runs the real `handoff` against a fixture topic no roster group claims.

Live, against the #2887 instance (handoff tip `a5f40d84c` then):
- head `fdf33f466` gives `handoff/r10-buffer-store a5f40d84c... is not an ancestor of fdf33f466...`;
- its later head `17d3cf384a`, which contains that tip, gives `None`.

Both come from `handoff_not_applied("fix/r10-buffer-store-pr", <head>, {"r10-buffer-store": <a5f40d84c>}.get, is_ancestor)`.

## Figures

- `python3 -I tools/audit/seat/review_packet.py --self-test` → `review_packet self-test: 42 checks, 0 failed` (31 at the base).
- `PYTHONPATH=tests/hastub bash tools/pr/prepr.sh --self-test` (`/opt/hpo/venv-ci/bin` first on PATH) → `421 passed, 0 failed`.
- `python3 tests/structure.py` → `STRUCTURE RATCHET PASSED`.
- `PYTHONPATH=tests/hastub python3 tests/entities.py` (`/opt/hpo/venv-ci/bin` first on PATH; the image's 3.11 `python3` cannot parse its 3.12 f-strings) (the one script `tests/closure.py select` names, `MODE: SCOPED`) → `ALL 2467 ENTITY CHECKS PASSED`.
- `node tools/policy/policy_lint.mjs --budgets`: `fixer.md` 5216 against 5216 tokens, `fix-review.md` 2447 against 2451; `node tools/policy/policy_lint.mjs` prints `TOTAL: 0 error(s) across 50 policy file(s)`.
- Live at the head: `python3 -I tools/audit/seat/review_packet.py handoff --topic r10-orch-review-packet --body <a body naming only carry 1>` → `R10-ORCH-REVIEW-PACKET at d2e92490232a, 12 carries, 11 refused`, rc 1 (the roster at `origin/handoff/audit-r10-roster` now holds 12 carries: carry 12 is P256 itself). This body names all 12 and passes the same command at `body_push.sh`.
- Live, #2887 now (fetched 2026-10-28 22:07Z): `handoff_not_applied("fix/r10-buffer-store-pr", "a5b8603b2f...", origin_handoff_tip, is_ancestor)` gives `None`. `handoff/r10-buffer-store` is now at `91a3d6810` (20:29Z), and the PR head `a5b8603b2f` (a merge of main at 20:59Z) contains it, so a reviewer dispatched now would review the fixer's latest handoff. The refusing arm is the fixed `fdf33f466` instance above, re-run at this head with the same result.

## Approval

This diff edits policy, in two commits of their own:
- `dev/governance/roles/fixer.md` step 6 (P256), commit "fixer.md: the handoff runs review_packet.py handoff". The triage ruling requires tvofi's approving review at this head before merge.
- `dev/governance/roles/fix-review.md` (P200), commit "fix-review.md: state the four relay checks". This merges on the owner-approved route under the mandate in force for this group (`6329234399`, owner card 8).

No cap moved: `node tools/policy/policy_lint.mjs --budgets` prints each file at or under its cap. This body claims no approval of its own, and none has been given for this diff yet.

## Red checks

none

## Carries

- Carry 1: card 8 placement. Landed by #2870 (`eb2063218`).
- Carry 2: card 5. Landed by #2870. This pass keeps it: `handoff` runs no CI-dependent check, and the CI-wait half of P256 is not built.
- Carry 3: independence. Landed by #2870, unchanged.
- Carry 4: the refusal-signal list (P135). Landed by #2870. This pass adds `handoff-not-applied` to it.
- Carry 5: concluded-red required context (`required-red`). Landed by #2870.
- Carry 6: hot-file arm. Landed by #2870. `handoff` now also runs it before the push.
- Carry 7 and Carry 9: dispatch the reviewer at the handoff ref. Not built in this pass, and the group stays `carries-open` for them.
  - Why: the change moves the dispatch moment. It needs a topic-keyed record re-keyed by `open_pr.sh`, a held-verdict post in `cloud_relay.sh` (a hot file), and policy text in `standing-dispatch.md` and `fix-review.md` step 7. After this pass's P200 text, `fix-review.md` sits at its token cap, so that text has to pay by cuts of its own.
  - That is an L-sized change across hot files and two policy files. It does not fit this M group's dispatch beside the other carries.
  - The controls stand as written in carry 7. The orchestrator may split it into its own group; routed under `## Forward-carry`.
- Carry 8: the `[6]`/`[7]` summary. Landed by #2870.
- Carry 10: P200. This PR, `fix-review.md`.
- Carry 11: P229. This PR, `handoff-not-applied`.
- Carry 12: P256. This PR: (1) the offline refusals run at the seat's handoff push, `body_push.sh` (the push the contract calls the handoff), not in `handoff_push.sh`, which opens the PR after it; `structure` and `hot-file` run there through `review_packet.py handoff`, and `head-note` is already checked at that push by `prepr.sh --body-check`. (2) `brief-carries`, with the stated controls in `--self-test` (1-5 of 6 refused naming carry 6, passing once dispositioned; a group with no carries passes) and mutant `review_packet-3`. (3) No CI wait added. (4) The `fixer.md` step 6 sentence.
- P213 (a repair hint on the `head-note` refusal) is not on this group's roster entry, so it is not built. It is named here so the orchestrator can append it if it still stands.

## Forward-carry

- Carries 7 and 9 of R10-ORCH-REVIEW-PACKET (dispatch at the handoff ref) stay open on its roster entry with their stated controls; not built here (see `## Carries`). Carry: R10-ORCH-REVIEW-PACKET
- The cloud-seat `host-path` false positive (#2925) is already carried to R10-RECORD-API-O1 as its carry 3 (the `ref_privacy.py` home match has no path-segment boundary). Its cause is the root account's passwd home matching, as a bare substring, any citation of the root-cause role contract. It sits in `ref_privacy._leaks`, which that group owns (`files`), so it is not fixed here. `review_packet.py` calls `ref_privacy` and inherits that fix. #2925 is a second instance of the same cause, read through `review_packet.py`'s `host-path` signal. Carry: R10-RECORD-API-O1

## Friction

none
