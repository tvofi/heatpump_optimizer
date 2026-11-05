R10-RAISE-GATE-SHIM (issue 3128), repair round 2: closes the seat-gh bypasses the round-1 fix review blocked on (`--body`/`--body-file` before the number, the unnormalised target and path spellings, the basename-only parent check), and carries (c) honestly.

Closes #3128

## Head

Code head `289fe24b401676199a4c10d0b181e9223cb458f3` (`handoff/r10-raise-gate-shim`): PR head `e7126ae2` plus a merge of `origin/main` `79f765e6b2e0f97e61b57d7b605fc4e70b4bf21e` plus one repair commit. `tools/pr/prepr.sh` was run on this committed tree after the merge (`rc=0`, `ci predict`: no red predicted, `claim files` byte-identical to origin/main); main had not moved at that run. No budget file, claim file, `VERSION`, manifest version or `RELEASE_NOTES.md` is touched; `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.

What changed, for Carry 1 (the R10-FLY-MANDATE-REVOKE-GUARD fixer's gaps (a)-(c); (a) is repaired here, (b) landed in round 1, (c) is below) and Carry 2 (the value check re-routed from #3045, built as (b), unchanged): all in `tools/audit/seat/shims/seat-gh`, its installer `seat_venv.sh --install-shims`, `gh_calls.py --self-test`, the instrument note):
1. `issue comment` is read by gh's own flag table: `--body` and `--body-file` join the skipped value flags (`-b -F -R --repo` already were), detached and attached. The target is normalised by `num()`: `#`, query, anchor, one %-decoding, trailing slashes dropped, leading zeros dropped, a URL read only as `.../issues/<n>` or `.../pull/<n>`. A target that is not one plain number (no target, a branch word, an unresolved `%`, a backslash) is **refused: fail closed**.
2. The api path is normalised by `api_hits()`: query/anchor cut, one %-decoding, scheme and host dropped, `.`, `..` and empty segments resolved, then `issues/<n>/comments` must be the whole tail with `<n>` equal to 201 after zero-stripping. A path it cannot read (unresolved `%`, backslash, newline) is refused when the call writes. Decision on the ambiguous spellings of finding 2: all refused; a #202 spelling of the same shapes is a null control that passes.
3. The parent check reads python's own option table (no-value letters passed, `-W`/`-X` skip their value, `-c`, `-m` and any unknown option end it with no script) and compares the script by physical path with the tree's `tools/pr/gh_comment.py`. A symlink is refused. The installer bakes the tree's path into the installed copy (`gcpy=` line); a shim run from outside the tree has no path, so no caller passes (fail closed).
Alternatives that lost: listing more spellings in a `case` (the #1874/#2345 shape, class still open); reading the whole argv for the number (refuses a body quoting 201). Residual, unchanged and declared: PATCH of `issues/comments/<id>`, graphql mutations; `gh pr comment` is not read (#201 is an issue, and a branch-word target would be over-refused).

## Mutation proof

- Predicate `[ -n "$ok" ] || {` changed to `true || {` in the shim: `gh_calls self-test: 146 checks, 38 failed` (the refusal arms); restored, 0 failed.
- `[WX])` changed to `[W])` in the parent option table: `FAIL parent check: null control: -X dev -W ignore -I before the tree's script` and `FAIL mutant killed: python -W/-X value read as the script` (2 failed); restored, 0 failed.
- Nine in-suite mutants (`guard_mutant`, each kills one rule): `--body`/`--body-file` not skipped; leading zeros kept; no %-decoding; trailing slash kept; an unreadable target passes; dot segments kept; trailing slash unread in the api path; `-W/-X` value read as the script; the script matched by basename. Where fail-closed would hide the mutant (trailing slash, %-decoding, `-X`), the mutant is observed on the **null control** (a #202 spelling) flipping to refused.

## Null control

Every refusal arm in `gh_calls.py --self-test` has a null control that reaches the real gh (stub rc 7): GET of #201, posts to 202, 2011, dot segments resolving to 202, %-encoded 202, `issue comment 202` with `--body 201` and with `--body-file 201`, a #202 URL with a trailing slash, `issue view 201`, a PATCH, and the tree's own script reached by an absolute path, a relative path and with `-X dev -W ignore -I` / `-Wignore -B` before it.

Harness at both ends (the reviewer's offline `ev/cases.sh` and a spoof script of mine, both against a local stub `gh` that records argv, `env -i`, empty HOME, no token): at `e7126ae2` the shim passed 9 of the bypass probes (reviewer's `ev/shim-cases-head.txt`) and my run of `cases.sh` against the `e7126ae2` shim reads 31 OK / 9 FAIL; against this head every refusal and bypass probe is refused with an empty stub log, except the two the verdict itself calls declared (`graphql-declared-residual`) or out of the block (`pr-comment-201`), which still pass; all 8 null controls still pass. Parent spoofs, old shim: `python3 -X gh_comment.py -c ...` and `python3 <other dir>/gh_comment.py` reached the stub; this head refuses both, and `python3 -I tools/pr/gh_comment.py post ...` by absolute and by relative path still reaches the stub.

**No control wrote to GitHub.** Every shim control ran against a local stub `gh` that records its argv and never reaches the network; the self-test stub exits 7 without a network call. The mandate id appearing in tests is the fixture `fixture-mandate-0000` and the revoke word is never written whole in a file, command or message.

## Figures

- `python3 tools/audit/seat/gh_calls.py --self-test`: `gh_calls self-test: 146 checks, 0 failed` (the instrument's count; round 1 was 98).
- `python3 tools/audit/seat/seat_venv.sh --self-test`: `25 checks, 0 failed`.
- Scoped gate: `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir "$D"` printed `MODE: SCOPED`; `scope.run` named `tests/entities.py`: `ALL 2623 ENTITY CHECKS PASSED`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- `tools/pr/prepr.sh`: `PRE-PR: 289fe24b... rc=0`; `ci predict`: none predicted.
- Seam enumeration (step 8): the class is "a #201 comment write spelled so the shim cannot read the number". Instrument: the reviewer's `cases.sh` plus the self-test `refused` table (29 refused spellings, 11 null controls); every seat-gh spelling in it is closed in this diff; `graphql` and PATCH are the declared residual, `pr comment` out of scope as stated.
- Toolchain: `cloud-setup.sh --check` read OK (python3 `/opt/hpo/venv-ci/bin/python3`); no numpy/scipy comparison was run and no golden or solver measurement is in this diff (CI remains the authority).

## Red checks

Read live with `get_check_runs` on PR #3223 (68 check runs, one page of 100), which are the runs at the **current PR head `e7126ae2`**. This head `289fe24b` has no runs of its own until the orchestrator moves the PR head, so none could be read for it; the list below is what the PR carries now and is retaken at the next head.
- `governance / delivery-status`: red since the base ancestry `dad3178d6c81cfe2bb410e7045de28f686a6f845` (OVERDUE on main's rows, not #3223's); this diff touches no delivery row except its own and no closure of that check. Inherited.
- `tests / nightly-status`: the `slow` lane of a nightly run, red on the same base ancestry `dad3178d`; this diff is not in the nightly's closure. Inherited.
- `governance / instrument-self-tests`: the log shows `alert_list self-test: 25 checks, 5 failed` (`tools/ci/alert_list.py`, a code-scanning alert reader); this diff does not touch it, and `python3 tools/ci/alert_list.py --self-test` here reads `25 checks, 0 failed`. Not caused by this diff; cause not established here (a CI-environment difference is the likeliest; a root-cause seat owns it).
- `arch-score / arch-score`: red in run 41988495065 (job 127126421625) and green in the two other runs at the same head `e7126ae2` (jobs 127115047185, 127129280469); the diff changes no scored module (shell, a tool and an instrument note), so the same-head flip is not this diff's. Cause not established here; cheaper detector: none known, standing cost nil.
- `gate`, `pr-contract / pr-contract`: red in runs 41988826127 and 41988495065 at the old head and body (the gate is the dependent job the round-1 verdict already named); re-answered at the next head's own runs. Not asserted green.
Defect-root-cause answer for a red my branch turned: none by this diff known; the round-1 `instrument-self-tests UNWIRED` red was already repaired.

## Forward-carry

- Carry (c), the `budget-raise-gate` job's 5-minute `timeout-minutes` against the scorer's CPU on the mandated path: not measured and not measurable here. The 29 s run at the PR head is not the mandated path (this diff raises no cap) and this seat has no CI runner; the earlier ~59 s CPU figure is unverified. Measurement owed: one CI run of the job on a diff that raises a cap, its scorer step against 5 minutes. Carry: dismissed: not measurable by a seat with no CI runner; the orchestrator records the job's duration from the next raise PR's CI run and decides.
- The shim's residual (PATCH of `issues/comments/<id>`, graphql, `gh pr comment`): Carry: dismissed: names no issue the shim can read, so no local rule tells a #201 write from another; `gh_comment.py` guards its own patch path.

## Friction

none
