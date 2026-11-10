Fix review: merge 6d894955cfb79f65a64e445acacb8f159342b237

bus-nonce: cd25d060d7c713f32544d7ac073be8e7

Round: first review of this head. Measured head 6d894955cfb79f65a64e445acacb8f159342b237; still the PR head at posting (ls-remote refs/pull/3408/head).

## Evidence
- Hash checks: every pin whose version moved (16 across the five locks) was compared against PyPI's published sha256 set for that exact version: 0 hashes in a lock that PyPI does not publish; every lock's pin count equals its parsed hash-carrying count (no unhashed pin). ev/hashcheck.txt. coverage 7.17.2 119/119, cython 39/39, sqlalchemy 72/72, grpcio 61/61, uv 19/19, others 2/2.
- py-spy 0.4.3 keeps the documented two Linux wheels (manylinux_2_5_x86_64 8a427722, manylinux_2_17_aarch64 bbcec469, checked by filename); the 7 other upstream distributions are intentionally absent, as the lock header says.
- Held packages unchanged between merge base and head: homeassistant-stubs==2026.9.3, zeroconf==0.151.5, cronsim==2.7 (ev/held.txt; no diff line touches them).
- Scope: three-dot diff is 7 files: five tests/requirements-*.txt, .github/dependabot.yml (comment only), dev/programme/delivery/3408.md. VERSION, manifest and RELEASE_NOTES untouched (0 diff lines). No golden or claim file moved.
- typing_ruler.py at head: ALL 12 source checks PASSED (ev/typing_ruler.txt). No stale old pins remain in the tree outside an archived log.
- merge-tree --write-tree origin/main head: exit 0, no conflict. dev/governance/roles unchanged on main since the merge base.
- CI: merge_train.py classify: GREEN 6d894955cfb79f65a64e445acacb8f159342b237 pending: none red: none (ev/classify.txt). owed-reds set: coverage-ratchet, fast (3.14), mutation, typing, validate-hacs (ev/owed-reds.txt), none red.
- Not run by me: mutation proof, finder's harness, null control (none named; a dependency re-pin writes no production line); the typing lock's single-package compile route not re-run, its output verified by hash set instead.
