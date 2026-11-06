ref_privacy flagged a cloud seat's own paths as a host identity: on uid 0 with HOME=/root, `--check` refused a roster line citing that home, and with HOME=/nonexistent it refused three lines (account-name `nonexistent`, derived from the placeholder home's basename). `Identity.of_host` now drops homes that name no person (the no-home placeholder, a public account's own home) before deriving names from them. `_HOST_PATH` is untouched, so a real `/Users/<name>` or `/home/<name>` path still refuses everywhere. The brief's passwd-name-root and bare `0` hits did not reproduce on this seat: root is already in `PUBLIC_ACCOUNTS`, and names under 3 characters are already skipped, so only the home-derived name remained.

Carry 1 (the #3239 round-1 fix review, ref_privacy on a uid-0 cloud seat): closed here. The check no longer reads \`/root\`, the placeholder home or a name derived from either as a host identity; the passwd name root was already public.

Source: the verdict on #3239 at 6a8964e8.

## Head

877df895cadfeca1f21526dfd215f6d91b0bf14d (merge of origin/main 5421413b54ba into the fix; the fix commits are the only change to ref_privacy.py).

## Mutation proof

Mutant: the line `homes = {h for h in homes if not _public_home(h)}` in `Identity.of_host` replaced by `pass`. `python3 tools/audit/seat/ref_privacy.py --self-test` then reports 2 failed: "a uid-0 cloud seat (root) judges its own paths and names no leak" and "a uid-0 cloud seat (nonexistent) judges its own paths and names no leak". Restored: 113 checks, 0 failed.

## Null control

Unmodified tree (origin/main 7e8939d38ced), same checkout: `python3 tools/audit/seat/ref_privacy.py --check` with HOME=/root ends "1 refused" (line 13825 of the r10 roster, home-directory); with HOME=/nonexistent ends "3 refused" (11438 and 14788 account-name, 13825 home-directory). At the fix: both end "0 refused". Genuine host path: the new self-test checks "a real host's /Users/<name> path still refuses through of_host" (home-directory, account-name, host-path) and "a /Users/<name> path refuses on a cloud seat too" (host-path) pass at the fix.

## Figures

- `python3 tools/audit/seat/ref_privacy.py --check` (HOME=/root and HOME=/nonexistent): 1 and 3 refused at 7e8939d38ced, 0 and 0 at the head.
- `python3 tools/audit/seat/ref_privacy.py --self-test`: 113 checks, 0 failed at the head.
- The cloud-home segment checks from R10-FLY-REFPRIV-HOME-SEGMENT now plant a non-public home, since a public home is no longer an identity.
- Instrument for the class: `python3 tests/closure.py select` gave MODE: SCOPED, 1 changed file; `tools/pr/prepr.sh` run on the committed tree at the pre-merge head ended rc=0; main moved to 5421413b54ba afterwards and prepr is rerun on this head (see Red checks).

## Red checks

none

## Forward-carry

none

## Friction

none
