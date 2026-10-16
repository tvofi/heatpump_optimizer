Fix review: blocked 5c35cd9ba6c6915a28ec982648389bd53d742b32 harness: class-rule-missing the body names no rule for the class "one closing keyword naming several issues", and six separator seams that class's own rule returns appear in neither the diff nor the body

bus-nonce: 14cec6a91b0266edfa7d5c680b205162

Round 1. Detached worktree at the head; contract currency `git diff $(git merge-base
origin/main HEAD)...origin/main -- dev/governance/roles/` empty before step 1.

Everything below is measured at `5c35cd9ba6c6915a28ec982648389bd53d742b32`, merge base
`81ae048e8bbdf2335fe2016e987ec2739481f293`. The fix itself is sound and its two named
pins both move under their own mutations — I blocked only on step 6, and the block is
one body edit plus a disposition, not a change to the fix.

RESULT 1 mutation proof: all three named pins redden, each alone, each with its null
control green. Detached worktree at the head, `PYTHONPATH=tests/hastub python3
tests/entities.py` (2333 checks). Baseline: `ALL 2333 ENTITY CHECKS PASSED`, and its 46
`  FAIL ` lines are the sub-harnesses' own embedded negative-control output, which every
mutation reproduces unchanged.
  MA delete the `if [ -n "$multi" ]` block in `tools/pr/preflight.sh` -> `1 of 2333
  ENTITY CHECKS FAILED`, the added line being exactly `one closing keyword naming
  several issues refuses, since GitHub closes only the first`; the null control
  `and two keywords pass` stays `ok`. Not vacuous: the same deletion leaves the two
  structural pins `ok`.
  MB re-add ` || true` to the preflight step -> same `1 of 2333`, on `the preflight
  step derives and passes the intended list and its refusal gates`, detail
  `swallow_gone=False`; its own null control stays `ok`.
  MC drop the passed `$INTENDED` argument (keeping `INTENDED=`) -> same `1 of 2333` on
  the same pin, detail `passed=False`; null control `ok`.
  So each pinned production line is load-bearing for exactly the check the body names.

RESULT 2 finder's harness, both ends, my own run: 12/12. The finding's instrument is
the pre-fix CI invocation, `bash tools/pr/preflight.sh < body` with no intended list,
run over merged bodies. At the merge base's `preflight.sh` all 12 of the body's cited
PRs exit 1 and every one prints `not in the intended list`; at the head's, invoked with
the workflow's own `jq -rs --rawfile` derivation, all 12 exit 0. Per-PR table in
`figures.txt`. Nothing is flat-by-design here.

RESULT 3 null controls re-run: the multi-issue arm is not always-red — `Closes #2231.
Closes #2230.` with both declared exits 0 at the head — and the intended-list arm is
not always-red: the 12 merged bodies above exit 0 with the derivation. The body's
`Defect bodies exit 1` claim reproduces: `Closes #1791` (a roster `issues` number no
group names in `fixes`) exits 1, and so do `Closes #2231 #2230`, `Closes #2231, #2230`
and `Closes #2231 and #2230`.

RESULT 4 claim files: `env_drift.py --all` and `card_drift.mjs` not needed — the diff
touches neither `tests/golden/claimed_drift.txt`, nor `card_claimed_drift.txt`, nor any
fixture. The changed-file set is exactly `.github/workflows/pr-contract.yml`,
`dev/programme/delivery/2342.md`, `tests/entities.py`, `tools/pr/preflight.sh`.

RESULT 5 VERSION: `VERSION`, the manifest version and the `RELEASE_NOTES.md` heading are
absent from the diff (three-dot against the merge base).

RESULT 6 BLOCK. This is a block rather than a report because step 6's class run is
unconditional — it runs on round 1, and an un-dispositioned returned seam is an open
seam with the class not closed (`R9-RCA-2004` records that as the reviewer's half of the
two contracts' disagreement, and leaves it standing). The finding here states two seams
and the body names no rule for the second. The class is "one closing keyword naming
several issues, where check 1
keeps only the first reference so the second silently escapes". The body names no rule
that enumerates it. I derived one and ran it over the same population the body's other
rule uses (all 200 merged PRs), and it returns six separator seams beyond the three the
body's pin text lists (space, comma, `and`): `/`, `&`, `+`, `(`, `;` and a word
separator, plus a keyword and a reference split across a newline. Measured at the head's
pristine `preflight.sh`, each with the second reference UNINTENDED:
`Closes #2231 / #9998`, `#2231/#9998`, `#2231 & #9998`, `#2231 +#9998`,
`#2231 (#9998)`, `#2231; #9998`, `#2231 then #9998`, `#2231<newline>#9998` all exit 0 —
the second, unintended reference passes silently, the same harm the arm exists to catch.
None of the six appears in the diff (arm 1b's comment states its scope as "whitespace, a
comma or an 'and'", which is the disclosure, not a disposition) and none is dispositioned
in the body. `fixer.md` step 8's own menu is the remedy: closed in this diff, already
guarded, or a distinct finding named by id. Probe output in `class-probe.txt`.
  The rule is MINE, not the finder's (step 9), and I say so: this finding has no
  committed harness in the tree — `grep -rl preflight.sh dev/audit/ tools/audit/ tests/`
  returns only `dual_path.py` and round-3 `mechanisms.py`, neither of them this one.
  Stated for the record; it is not the block.

RESULT 7 head: the body's `## Head` names `5c35cd9ba6c6915a28ec982648389bd53d742b32`
and names `55b0fba110bf2cd4e19f0f06daf224335bf788e4` as the authored code head; the head
is `5c35cd9b` and the only commit `5c35cd9b` adds to `55b0fba1` is
`dev/programme/delivery/2342.md`. Confirmed from the range, not from the body.

RESULT 8 figures re-derived under the body's stated rule: both hold. The pre-fix
over-fire claim reproduces on all 9 named PRs (each prints `not in the intended list`,
rc 1), and the post-fix claim on all 12 (exit 0). Two things the body does not say and
a reader should have: the 9 is a lower bound, because the other three of the 12 also
over-fire under the old invocation; and over the full 200-merged-PR population six
bodies still refuse after the fix (#2007 #2008 #2009 #2010 #2015 #2041), all of them the
one shape the body DOES disposition — `INTENDED=[]` because the closed number is a
round-9 roster `issues` (Part-of) number no group names in `fixes`.

RESULT 9 harness: no committed harness for this finding (see RESULT 6). The instrument
the body quotes — `bash tools/pr/preflight.sh < body` over merged PRs — is the fixer's
own re-derivation of the over-fire; it is not claimed as a finder's harness in the body
and I do not read it as one.

RESULT 11 red checks: one check is red at this head, `coverage-ratchet` (failure,
20:18:33Z, `early_cutoff.py 81.53 %` against the 95 % per-module floor), and the body's
`## Red checks` says `none`. I read it off the commit's own check-runs API, not the
body. It is NOT this pull request's and I do not block on it, on three measurements:
`55b0fba1` — the same branch, the same tree but for the one-line delivery row — carries
`coverage-ratchet` SUCCESS at 19:45; the sibling PR #2343 at `d0dc4c2dc` is red on the
same lane at 20:02 with a DIFFERENT figure, `early_cutoff.py 75.16 %`, on a branch whose
whole diff is a delivery row and `dev/programme/rosters/wave-r10-groups.json`; and the
module is untouched by this diff. The lane is flaky on this runner class, not a red this
branch turned. It is also not in the ruleset's 17 required contexts, so it does not gate
the merge. The body's `none` answers `defect-root-cause.md`'s second trigger — the
defect could not turn a check red — which is what the section is for.
  Procedurally: `closures` is still in progress at the head, so a `root-cause-*` block
  could not be posted anyway (step 11).

RESULT 12 head re-read before posting: still
`5c35cd9ba6c6915a28ec982648389bd53d742b32`. Every number above is from it.

RESULT 13 conflict: none. `git merge-tree --write-tree origin/main
5c35cd9ba6c6915a28ec982648389bd53d742b32` exits 0 and prints no conflicted path.
GitHub's `BLOCKED` is the ruleset awaiting the code-owner review, not `DIRTY`.

RESULT 14 metric-gamed: none. The diff moves no `tests/structure_budgets.json` key (that
file's keys are all package metrics; none is a per-file LOC for `tests/entities.py`), and
none of the four changed paths is in `POLICY_GLOBS` (`policy_lint.mjs --corpus-filter`
returns only `CLAUDE.md` from the set plus a control), so no policy cap moves either. No
golden, no mutation ledger, no `closures.json`/`INERT`, no claim file. The two body
figures that are numbers move under the change and not under the instrument: they are
produced by running the pre- and post-fix scripts, and re-adding `|| true` does not
change them.
  Planted with nothing improved: on this same instrument the shape the diff's change IS
  — a refusal arm — is what the change adds, so there is no diff-shaped move left to
  plant that a null control would leave standing.

RESULT 15 architecture-unsound (on added lines): no breach. `tools/pr/preflight.sh`
owns the closing-keyword check, so arm 1b stays in its owner; the added jq lives in the
workflow that owns CI's derivation and, as `55b0fba1` reworked it for, stays inside
`codeowners_gap.py`'s `admitted()` set (no heredoc, no `-c`, no `-`); no
`homeassistant` import, no side effect beyond printing, inputs on stdin, no
`entry.options` read. One observation, not a block: the closing-reference pattern now
has three spellings — check 1's grep, arm 1b's grep, and the workflow's jq — and they
must agree, since the jq computes the list the grep grades against. They do agree today
(jq's `\s` matches a superset of what the line-oriented grep sees, so the drift
direction is a harmless extra intended entry), and the workflow's comment names the
coupling.

RESULT 10 forward-carry: the body says `none`, and for later stages it is none — the
finding changes nothing a stage that has not started must do. What is owed is the
same-stage sibling seam in RESULT 6, which `finding-propagation.md` sends to a new issue
filed by the same pull request; routing it is the disposition the block asks for.

RESULT round: round 1, not a re-cut.
