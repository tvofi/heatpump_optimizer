Fix review: merge c6288554fab02d553ce9ded31a531499e783b0ea

bus-nonce: 856f2f621cae55ee01583e566e8a8f1c

Round 1. Reviewed head c6288554fab02d553ce9ded31a531499e783b0ea (authored code head 21bbfc66a, plus the PR's own delivery row). The diff against the merge base is two markdown files: `dev/programme/triage/s6-batch72.md` and `dev/programme/delivery/2993.md`. No production code, VERSION, manifest, notes heading, golden or claim file is touched (ev/diff-names.txt).

## Findings

- The body's count "2 of the 40 newest verdict refs hold a `- Red checks:` line" re-derives as 3 when I take the 40 newest by committer date (verdict/2990, 2987, 2986). The ruling's substance stands: only verdict/2987 pairs the line with a NONBLOCK word under `carry_audit.NONBLOCK` (2990 and 2986 do not match), so "1 of 40" holds and the rate is still rare. The first count is off by one, probably from a different ordering of "newest". Carry: dismissed: the ruling and carry text do not depend on that count, and the NONBLOCK-pair figure re-derives.

## Evidence

- RESULT mutation: `roster_edit.ruling_verdict` reads P306 as ACCEPT on the head file. With `Verdict: ACCEPT narrowed` changed to `REJECT narrowed` it returns REJECT, so `triage_refusal` would refuse the carry. The gate that consumes the file moves under the mutant.
- RESULT merge: `git merge-tree --write-tree origin/main HEAD` exits 0, tree 39d08fd4 (ev/merge-tree.txt). `git diff` of dev/governance/roles/ between the merge base and origin/main is empty, so the role contract I used is current.
- RESULT figures: issue comment 6520504435 on #2987 has `## Findings` at line 7, `## Evidence` at line 11 and the Red checks item at line 19, as quoted. `carry_audit.py` at origin/main has `TRAILER` at line 103, `NOT_REQUIRED` at line 111, `NONBLOCK` at line 119, as quoted. The 2987 Red checks line matches `NONBLOCK` and not `NOT_REQUIRED`, as the ruling says.
- RESULT packet: carry_audit at the head reads 0 finding items; figure_lint reads 3 resolved, 0 refused (2 unverified are git subcommand flags, not figures).
- Red checks: none red in the check-runs API at this read (37 runs). Completed runs are success or skipped. `tests / fast (3.14)`, `tests / closures`, `tests / coverage`, `tests / browser`, `governance / env-matrix`, `governance / instrument-self-tests` and a `prelude` were still in progress and no `pr-contract` run was present, so the root-cause answer for a red check is not yet testable; none is red. These heavy lanes are cited, not re-run, per the contract.
- Forward-carry: the body names none. The ruling's carry text is for `roster_edit.py append-carry` on R10-FLY-CARRY-DISPOSITION and states its null controls and one mutant as preconditions, so the control travels with it.
- No finder's harness or quantified fix claim exists: this is a ruling file, so steps 2, 3, 4 and 6 have no object. Not run: `tests/entities.py` (needs homeassistant, absent here); the new file sits in `dev/programme/triage/` beside sibling batch files and CI `closure-scope` passed.
