Closes: none. Triage ids P253, P274, P317, P320 and their carries; no issue numbers.

Seat commits and pushes carried a runner identity (P253, P320), the handoff body ref could be written over a commit the opener would refuse (P274), and `prepr --body-check` did not judge body text as the comment gate does (P317).

- Carry 1 (P253) and Carry 4 (P320): `ref_privacy.email_leaks` gains an `anthropic-identity` class (an @anthropic.com or subdomain address) with self-test arms; `tools/audit/seat/cloud-setup.sh` exports GIT_AUTHOR_* / GIT_COMMITTER_* from SEAT_NAME/SEAT_EMAIL in the profile and in `variables`, and (Carry 6) sets RUNNER_TEMP under the install prefix (not a /tmp literal, which `tmp_paths` refuses).
- DEVIATION, for the owner: the brief named `hpo-fixer`; SEAT_NAME/SEAT_EMAIL are `seat` / `seat@users.noreply.github.com`, the identity `cloud_dispatch.py` already pins, so there is one source. The cloud_dispatch self-test asserts the two agree.
- Carry 2 (P274): `body_push.sh` runs `ref_privacy.py guard --over refs/remotes/origin/main` on the handoff head before writing the body ref. The P274(1) prompt pin in `cloud_dispatch.py` already exists; P320 showed it did not hold, hence the exports.
- Carry 3 (P317): `prepr.sh --body-check` calls `body_privacy_line` and folds its rc.
- Carry 7: ref_privacy `--check` push-site enumeration now includes `git send-pack` and `gh api graphql -F query=@file`.
- Carry 5, the home-directory carry: re-measured at this merge base, an Identity whose home is the root account yields no private names (`root` is in PUBLIC_ACCOUNTS) and `dev/governance/roles/root-cause.md` is not refused; the existing `_home_re` / R10-FLY-REFPRIV-HOME-SEGMENT arm already satisfies it.
- Hot files `tools/pr/prepr.sh` and `tools/audit/seat/body_push.sh` overlap open PR #3221 (different regions); a merge-resolution round may follow. Hot files merged origin/main at 6777ec33337b256d29ea145d98da413dbf076a2a. No budget raise.

## Head

c34c211dd6ee96dcf5d7f63162b3f31a52cb516e

## Mutation proof

- Drop the anthropic-identity class (line 252 of ref_privacy.py made unmatchable): `python3 -I tools/audit/seat/ref_privacy.py --self-test` goes 109 checks, 4 failed (the class arm, two guard-CLI arms, the body_push runner-default arm).
- Drop the guard call in body_push.sh (replaced by `true || {`): the same self-test fails 1, "body_push refuses a handoff head authored by a runner default, and writes no body ref". That arm keys on the guard's stderr line, because an earlier fixture run stopped at a missing prepr.sh.
- Drop the `body_privacy_line` call in prepr.sh (`bline=$(true)`): `bash tools/pr/prepr.sh --self-test` fails "--body-check applies body_privacy_line and folds its rc (P317)", 489 passed, 1 failed.

## Null control

Unmutated tree: all of the above pass. Without the exports, the config identity authors a commit (cloud-setup self-test control); a clean topic is pushed by body_push (ref_privacy self-test null control).

## Figures

- 109 ref_privacy checks, 0 failed: `python3 -I tools/audit/seat/ref_privacy.py --self-test`
- 126 cloud_dispatch checks, 0 failed: `python3 -I tools/audit/seat/cloud_dispatch.py --self-test`
- 19 cloud_setup checks, 0 failed: `bash tools/audit/seat/cloud-setup.sh --self-test`
- 490 prepr self-test checks, 0 failed: `bash tools/pr/prepr.sh --self-test`
- 2622 entity checks passed: `python3 tests/entities.py`
- structure ratchet passed: `python3 tests/structure.py`
- Scope: `python3 tests/closure.py select` printed `MODE: SCOPED -- 1 script(s) run, 32 scoped out` (tests/entities.py); run_always scripts closure selftest, layout, harness_headers also passed.
- Toolchain numpy 2.5.4, scipy 1.18.1 match tests/requirements-ci.txt; no solver file touched, so no golden run.
- Measured: `date -u` 2026-11-05 06:41:21Z; base 6777ec33337b256d29ea145d98da413dbf076a2a; a full prepr run on the pre-merge tree (base 8364e62460f6) was clean; on this tip prepr was clean through the closures step and was then stopped by the 30-minute background limit before ci predict, so those last lines were not re-read here.

## Red checks

none. A first full prepr run was red on the diff's own faults, fixed before this head: the bare `"${vars[@]}"` expansions (entities.py) and three /tmp literals in cloud-setup.sh (tmp_paths). One `--body-check ... (P317)` self-test row failed once in that run and passed on every rerun, including in isolation; cause not established.

## Forward-carry

none

## Friction

none
