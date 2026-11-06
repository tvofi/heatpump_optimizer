ref_privacy read a cloud seat's own paths as a host identity. On uid 0 with HOME=/root, a line citing that home was refused as home-directory. With HOME=/nonexistent, it was refused as home-directory and account-name, where `nonexistent` is the name derived from the placeholder home's basename. `Identity.of_host` now drops homes that name no person before it derives names from them: the no-home placeholder, and a public account's own home (`_public_home`). `_HOST_PATH` is untouched, so a real `/Users/<name>` or `/home/<name>` path still refuses everywhere.

Repair (round 2): the drop also covers the CI runner's home and this seat's. Two self-test arms planted the real `$HOME` and expected a refusal, so both went red at the PR head and passed on main: heartbeat.sh's "a message carrying the host's home directory is refused and the reachable ref does not move", and gh_comment.py's `arm_privacy_post_dry_run_refuses_this_hosts_home`. Each arm now plants a private home outside `/home` and `/Users`, so only the home rule can refuse it. Each also gains a null control that passes another path under the same planted host. The alternative was to keep public homes in the identity and exempt them only in `--check`. It lost: two readers of one identity would disagree about the same host, and roster lines would still be refused under `guard`.

Carry 1 (the #3239 round-1 fix review, ref_privacy on a uid-0 cloud seat): closed here. The passwd name root was already in `PUBLIC_ACCOUNTS`.

Carry 2 (cloud seat identity, found 11-06): closed here, at the source. `cloud-setup.sh` already exported `GIT_AUTHOR_*` and `GIT_COMMITTER_*`, and its self-test already held the null control "control: without the exports the config identity authors the commit". The values were the wrong identity, `seat`. The seat identity is now `hpo-fixer` at the owner's noreply address, the one `dev/programme/HANDOVER.md`'s Identity bullet names. It is set in `cloud-setup.sh` (`SEAT_NAME`/`SEAT_EMAIL`) and in `cloud_dispatch.py` (`SEAT_NAME, SEAT_EMAIL`, which also feeds the fixer and probe setup line). A new `cloud_dispatch.py` check pins the value: the existing arms compare against the constant, so they read green for any identity, and that is how `seat` went unnoticed. This pin encodes a design choice.

## Head

bf4d200e37ec5bfd14ed7e03877f0bead48e54e2 is the repair bd0525cbe and the carry-2 commit 7d04f651b, merged with origin/main 57958d6a4 (`date -u` 2026-11-06T18:33Z). It descends from the PR head 66662fc28. Every figure below was re-taken at this head.

## Mutation proof

- The fix line `homes = {h for h in homes if not _public_home(h)}` in `Identity.of_host` replaced by `pass`: `python3 -I tools/audit/seat/ref_privacy.py --self-test` reports 113 checks, 2 failed. The failures are "a uid-0 cloud seat (root) judges its own paths and names no leak" (['home-directory']) and "a uid-0 cloud seat (nonexistent) judges its own paths and names no leak" (['home-directory', 'account-name']). Restored: 0 failed.
- `of_host`'s `homes.update({h, os.path.realpath(h)})` replaced by `pass`: `bash tools/audit/seat/heartbeat.sh --self-test` fails "a message carrying the host's home directory is refused and the reachable ref does not move" (8 checks, 1 failed), and `python3 -I tools/pr/gh_comment.py self-test` fails `arm_privacy_post_dry_run_refuses_this_hosts_home (the wiring)`.
- `_public_home` made to return True: the same two arms fail. Restored: both self-tests pass.
- Carry 2: `SEAT_NAME`/`SEAT_EMAIL` reverted to `seat` in both `cloud_dispatch.py` and `cloud-setup.sh`. `python3 -I tools/audit/seat/cloud_dispatch.py --self-test` then reports 127 checks, 1 failed ("the seat identity is hpo-fixer at the owner's noreply address"). `bash tools/audit/seat/cloud-setup.sh --self-test` stays at 19 checks, 0 failed, which is the gap the pin closes. Restored: 0 failed.

## Null control

- At origin/main 817c2b169, `leaks()` under `Identity.of_host()` on the line "on a cloud seat, where `$HOME` is `/root`, a nonexistent group" reads ['home-directory'] with HOME=/root and ['home-directory', 'account-name'] with HOME=/nonexistent. At the head it reads [] for both.
- The head's self-test keeps two arms that must still refuse: "a real host's /Users/<name> path still refuses through of_host" (home-directory, account-name, host-path) and "a /Users/<name> path refuses on a cloud seat too" (host-path). Both pass.
- The repaired arms each carry a null control: heartbeat's "null control: the same host's message naming another path is pushed", and gh_comment's `arm_privacy_post_dry_run_passes_another_path (null control)`. Both pass.
- Carry 2: the null control is cloud-setup's "control: without the exports the config identity authors the commit", which passes. Its "the profile exports the seat identity" arm passes, so the exports now carry hpo-fixer.
- Before the repair, at 66662fc28, both arms failed with HOME=/root and with HOME=/home/runner. At main both passed under the same two HOMEs.

## Figures

- `python3 -I tools/audit/seat/ref_privacy.py --self-test`: 113 checks, 0 failed at the head.
- `bash tools/audit/seat/heartbeat.sh --self-test`: 8 checks, 0 failed at the head with HOME=/root, HOME=/home/runner and a private /home/<name>. At 66662fc28: 7 checks, 1 failed under HOME=/root and HOME=/home/runner.
- `python3 -I tools/pr/gh_comment.py self-test`: SELF-TEST PASSED at the head under the same three HOMEs. At 66662fc28: TOTAL: 1 failed under HOME=/root and HOME=/home/runner.
- `python3 -I tools/audit/seat/cloud_dispatch.py --self-test`: 127 checks, 0 failed. `bash tools/audit/seat/cloud-setup.sh --self-test`: 19 checks, 0 failed.
- `python3 -I tools/audit/seat/ref_privacy.py --check`: 0 refused at the head with HOME=/root and with HOME=/nonexistent.
- `python3 tests/closure.py select`: MODE: SCOPED, which named tests/doc_claims.py and tests/entities.py. Both ran green at the head. `python3 tests/structure.py`: STRUCTURE RATCHET PASSED.
- Class instrument (seats that judge with the real host identity): a git grep over the tree for `of_host(`, `ref_privacy.py guard` and `ref_privacy` imports that pass no identity. Every self-test hit was checked for an expected refusal that depends on the real `$HOME`. Two depended on it, heartbeat.sh's arm and gh_comment.py's arm, and both are repaired in this diff. The rest have no dependency on the real `$HOME`: cloud_dispatch.py's `judged()` refuses an email class, ci_probe.py's log arm refuses nothing, stamp.py's arm uses the host-path grammar, ci_predict.py plants a home, and ref_privacy.py's own arms are mocked or planted. Its unmocked `of_host` arm tolerates a public home through `_public_home`.

## Red checks

- governance / instrument-self-tests (job 127924787550, run 42227485863): caused by this diff and repaired here. The red was heartbeat.sh's home arm. gh_comment.py's arm shares the same cause and was measured red locally at 66662fc28. The `BAD X`, `BAD X2` and `BAD B` lines in that log are not failures. They are `alert_list_mutants.sh` printing each mutant's refused arms. That step ends "ALERT-LIST MUTANTS: every mutant refused", and the real `alert_list.py --self-test` step in the same log ends "25 checks, 0 failed". The same arms pass at main and at the head locally. Cheaper detector: none exists that is cheaper than the self-test, which already ran this arm in seconds. The miss was that the arms ran only under the fixer's own HOME. A fixer of ref_privacy's identity runs the self-tests of every caller the class instrument above names, which is the step this repair adds.
- pr-contract / pr-contract (job 127934822978): the body did not name the red self-tests. This body names them.
- gate (jobs 127936530331, 127933123372, 127925359010): red on the two checks above, with no cause of their own.
- governance / instrument-self-tests also cancels main-wide at its 30-minute job timeout. That is not this diff (cure: R10-PROCESS-SLIM, #3245).

## Forward-carry

none

## Friction

none
