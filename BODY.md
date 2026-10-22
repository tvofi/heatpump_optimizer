Supersedes dependabot PR #2615 (`build(deps): bump dompurify 3.4.16 -> 3.4.17` in `tools/site`, head 09a62bb5), which cannot merge: `pr-contract` refuses its `dependabot[bot]` author (decision 0011). The same one-file change on `origin/main`, authored by the hpo-author App, as #2544 did for #2534.

Version line changed: `tools/site/package-lock.json` `node_modules/dompurify` 3.4.16 -> 3.4.17 (version, resolved URL, integrity hash, and the `license` field npm now records). `tools/site/package.json` does not name dompurify (a transitive dependency of the docs-site generator), so nothing else moves. The upstream 3.4.17 release notes describe sanitizer hardening (IN_PLACE, SMIL attributeName, shadow roots); no advisory id was found, so this is not claimed as a security fix.

## Head

Code head `79bfa47de5513b552368bbd7222ec0e2cbc76c3f`, one commit on `origin/main` `a9db47846`; it touches only `tools/site/package-lock.json`.

## Mutation proof

n/a: a lockfile-only dependency bump with no code under test. The file is read by the docs-site build (`npm ci`) and by `tests/doc_claims.py` and `tests/entities.py` as a closure member; no function was added or changed to mutate.

## Null control

The diff is byte-identical to the Dependabot head's: `git diff 09a62bb57 79bfa47de -- tools/site/package-lock.json` prints nothing. The unmodified tree (`origin/main`) pins 3.4.16 with the integrity hash the Dependabot diff removes.

## Figures

- files changed: `git diff origin/main...HEAD --stat` -> `tools/site/package-lock.json | 7 ++++---`, 1 file changed, 4 insertions(+), 3 deletions(-)
- gate scope: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir .` -> `MODE: SCOPED -- 2 script(s) run, 31 scoped out`, running `tests/doc_claims.py` and `tests/entities.py`
- `python3 tests/doc_claims.py` -> `ALL 203 checks PASSED`
- `python3 tests/entities.py` on this head -> `4 of 2397 ENTITY CHECKS FAILED`; the same command on `origin/main` `a9db47846` (a clean detached worktree) -> `4 of 2397 ENTITY CHECKS FAILED`, so the four are not this diff's (the visible ones are the `hb` heartbeat-control timing checks, e.g. `the control rests between tries ... two tries took 0.80s against a 1.0s rest`, which depend on this macOS host's timing and py-spy)

## Red checks

local `tests/entities.py` shows 4 failures identical in count on `origin/main` (Figures); they are host-dependent heartbeat-control timing checks that a lockfile cannot reach, and Linux CI is the authority. Otherwise none known at authoring: CI has not run on this head. Red on #2615 were `pr-contract` (author, and seven body headings a Dependabot body lacks; this body supplies them) and `nightly-status`, which grades `main`, not this diff.

## Forward-carry

none

## Friction

none
