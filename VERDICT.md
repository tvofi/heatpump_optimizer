Fix review: blocked 8e6e94427f86b0c15ecdbbe1ed639acc716737ee self-test-red: four instrument self-tests that run the real app_approve.sh --carry pass at the merge base and fail at this head (app_comment.sh 6, review_carry.py 4, ledger.py 1, merge_train.py 2); their fixtures carry heads that are no branch tip of origin

bus-nonce: 3d4aac33b30751fa439eab5a58c6b19a

Round 1 of this part, at the handoff, before a pull request exists. No review packet and no CI exist for this head; every result below is this seat's own run in a detached worktree at 8e6e94427f86b0c15ecdbbe1ed639acc716737ee, with the merge base fc2a7edcf2be8847037d9e8dc5bde460977befa8 in a second worktree.

## Block

`carry()` in `tools/pr/app_approve.sh` now runs `git ls-remote --heads origin` and treats a head that is no branch tip of origin as not ours. Four other instruments call the real `--carry` inside their own `--self-test`, over fixture heads that are never pushed to `refs/heads/*`; the diff edits none of the four files. `instrument-self-tests` step red at the head and not at the merge base (fix-review.md step 11), each one:

- `tools/pr/app_comment.sh --self-test` (governance.yml step `app-verdict-poster`): base 0 failed, head `67 checks, 6 failed`. First failing check: "a merge verdict posts at a pin-only head it carries to (P264)". Its fixture pushes the head only as `refs/pull/7/head`.
- `tools/audit/seat/review_carry.py --self-test` (step `review-carry`): base 0 failed, head `29 checks, 4 failed`: "a re-cut merge of the branch's own previous head answers CARRY", "a revert and its re-apply answers CARRY (L6)", "and counts its two non-merge commits", "a claim file resolved to the union of both sides answers CARRY". The fixture's origin holds only `main`.
- `tools/audit/seat/ledger.py --self-test` (step `obligations-ledger`): base 0 failed, head `102 checks, 1 failed`: "REVIEW OWED skips a head its newest merge verdict carries to (a clean main merge); a branch-own commit after it is owed (null control)". The fixture repository has no `origin` remote, so the listing fails closed.
- `tools/audit/seat/merge_train.py --self-test` (step `merge-train`): base 0 failed, head `656 checks, 2 failed`: "add, a train live: a CARRIED single ... passes app_approve.sh --carry under the queue lock and is spooled for the NEXT batch (ADDED)" and its null control "a head carrying a non-main delta past its verdict is refused by the `carry` rule". No `origin` remote in the fixture.

All four steps list `tools/pr/app_approve.sh` in `tools/ci/selftest_closures.json` at this head, so the scope selects them for this diff: the pull request would open red on them, and a forced-full `main` would be red after it. `tools/pr/prepr.sh` does not run the instrument self-tests, which is why the handoff did not see it.

The enumeration rule for the class: every caller of `app_approve.sh --carry` (`git grep -n -e '--carry' -- tools | grep app_approve`). Callers whose self-test I ran and found green at the head: `orchestrator_tick.py` (315 checks), `review_packet.py` (123), `cloud_relay.sh`, `bus.sh` (203), `outside.py` (212). `queue_pre_flight.py --self-test` under `python3 -I` stops on `ModuleNotFoundError: No module named 'merge_train'` at the head; I did not run it at the base, so it is not counted either way.

The repair is the fixer's choice between giving those fixtures an origin branch at the carried head (as this diff's own `ourcarry` does inside app_approve's self-test) and a seam in `carry()`; either way the four self-tests are re-run at both ends and their closures re-recorded.

## What this part defines for part 2

In `tools/pr/outside.py`, imported by path:

- `pull_facts(repo, pr, pull=None)` -> dict with keys `author`, `state`, `head_repo`, `head_ref`, `head_owner`, `head`, `base_repo`, `base_ref`.
- `cross_repository(facts, repo)` -> bool, the one definition of a cross-repository head (`facts["head_repo"] != repo`; a head repository that is gone is cross-repository).
- `check(repo, pr, ref, gate=None, fetch=True, early=False, comment=None, pull=None)` -> `(rc, lines)`: 0 admitted, 1 refused, 3 not an outside pull request.
- `Rules(ref).classify(path, pr)` -> `"F"`, `"R"` or `"O"`; `Rules.is_owned`, `Rules.refused`, `Rules.free`.
- `approve(repo, pr, head, mandate, ref, role, gate=None, fetch=True)` -> `(rc, lines)`; `owner_read(reviews, head, gate, repo, carry)`; `allowlisted(user, allow)`; `read_allowlist(ref)`; `carries(lsha, head, ref)`; the exception `Refuse`.
- Shell form: `python3 -I tools/pr/outside.py cross --repo O/R --pr N` (rc 0 `CROSS-REPOSITORY`, rc 3 `SAME-REPOSITORY`, rc 1 `REFUSE:`), `check`, `classify`, `approve`.
- Constants: `ALLOWLIST`, `CODEOWNERS`, `MANIFEST`, `HEAD_REF`, `READ_WORDS` ("Outside read:"), `READ_LINE`, `DECISIVE`.

Data paths: the allowlist is `dev/governance/config/outside_contributors.json` (key `contributors`, entries with `login`, integer `id`, `since`, `decision`), read with `git show <ref>:<path>`; the fetched fork head is `refs/hpo-outside/<pr>`; `bus.sh adopt <pr> <comment id>` is the adoption entry and `policy_lint.mjs --outside-author <login>` its body-lint form.

This part defines none of `Train.fork_head`, `Train.outside_contract` or `head_is_ours`; `tools/audit/seat/merge_train.py`, `remerge_main.sh` and `merge_pr.sh` are untouched by the diff.

## Can this part alone stop the train

Yes, as it stands, and for our own pull requests: the four red self-test steps above stop this pull request itself, and after it any pull request whose diff reaches one of those four closures.

In production paths a same-repository pull request is otherwise unaffected, by reading and by measurement:

- The train's four `--carry` calls (`merge_train.py` admission, add, the head wait, `admit_verdict`) pass the live `headRefOid`, which is a branch tip of origin for a same-repository head, so `ours` stays 1 and every arm below is the base's. The extra cost is one `git ls-remote --heads origin` per carry whose range holds a commit: 7216 heads, 0.63 s from this seat.
- `policy_lint.mjs`: `outsideAdmission` returns before any spawn for the App (both spellings), Dependabot and an absent author. The base's copy of the linter, given this head's two new arguments, prints the same summary line as without them (`PR-BODY: 2 error(s)` both ways on the handoff body with no `--base`), so the head's `pr-contract.yml` line does not break the base's restored grader.
- `tests.yml`: the added conjunct is true for a same-repository head and `HEAD_REF` holds the value the inline expression held.
- A carry of a local head never pushed now refuses, with or without an `origin` remote; the body says so for non-merge commits. It holds for a merge of main too wherever the branch changes a merge-driver file, since on `ours=0` each such file must be main's bytes.

For a fork pull request this part admits nothing at merge: the allowlist is empty and `check` answers rc 3.

## Evidence

- `git merge-tree --write-tree origin/main 8e6e94427f86b0c15ecdbbe1ed639acc716737ee` with origin/main at 8c10361eb1fea539dc5acb8f7442eac2810faa47: rc 0, stderr `LEDGER-MERGE: resolved tests/closures.json`. No conflict.
- `git diff $(git merge-base origin/main HEAD)...origin/main -- dev/governance/roles/`: empty, the contract read is current.
- The head is still `refs/heads/handoff/r10-outside-contributor-cycle` on origin at the time of writing.
- RESULT app_approve self-test at head: `350 checks, 0 failed`.
- RESULT bus self-test at head: `203 checks, 0 failed`.
- RESULT outside self-test at head: `212 checks, 0 failed`.
- RESULT policy_lint self-test at head: rc 0, `FIXTURE ok: 93 error(s) hold 276 pins across 12 check classes`.
- RESULT ci_predict self-test at head: rc 0, `0 failed`.
- RESULT mutant, app_approve.sh `|| ours=0` to `|| ours=1`: 18 checks fail, the first "NO CARRY on a fork head: a closures bot commit". Killed, as the body says.
- RESULT mutant, outside.py `cross_repository` returning True: 3 checks fail ("REFUSE: a same-repository head", "cross: a head of ours is not (rc 3)", "approve REFUSE, nothing posted: a same-repository head"). Killed.
- The body's other hand mutants (bus.sh, policy_lint.mjs, ci_predict.py, the remaining app_approve arms) were not re-run by this seat; the block does not turn on them.
- outside.py's own added lines were not drawn by the final `prepr.sh` mutant draw, as the body discloses; I ran the one mutant above and no draw.
- `node tools/policy/policy_lint.mjs --budgets`, the fix-review.md row: lines 140 of 140, tokens 2775 of 2775; the cap moved 2546 to 2775 in `policy_budgets.json`. The raise is real and is the owner's or his mandate's to approve; I did not judge the four payments.
- `python3 tools/audit/archscore/score.py --diff fc2a7edcf2be8847037d9e8dc5bde460977befa8`: `Architecture score: dS +0.0000 NULL`, as the body quotes.
- `VERSION`, `custom_components/`, `RELEASE_NOTES.md` and `tests/golden/` are untouched by the diff; no claim file moves.
- `outside.py classify --pr 7 --ref HEAD`: F `dev/programme/delivery/7.md`, R `dev/programme/delivery/8.md`, F the manifest, F `docs/CONTRIBUTING.md`, F `docs/setup.md`, O `tests/entities.py`, R `tools/pr/outside.py`, F `README.md`, R `VERSION`.
- The three live checks decision 0017 lists before the first allowlist entry were not run by this seat either: no fork and no owner credential here.
- `budget-raise-gate` is the one red the body answers; no check run exists to read it against.

## Findings

None beyond the block.
