R10-RAISE-GATE-SHIM (issue 3128), repair round 3: the seat-gh comment guard is now DENY-BY-DEFAULT, per the coordinator's ruling to stop adding spellings. `gh issue close/reopen --comment/-c`, a gh alias and every other unnamed route are refused by the rule, not by a named arm.

Closes #3128

## Head

Code head `725410a6b1e7685c4889f68b14ec686ef14a6c3f` (`handoff/r10-raise-gate-shim`): PR head `6b416a18fc8752eaa3c10404cec43f896df3ed60` plus one commit (the `queue_pre_flight` self-test fix below). Round 3's own commit is `6027fe3ebf34b4cce16eedb5936aa9ce64e269e9`, already merged into the PR head. `origin/main` is `8bf45e5dcedd3fbeb6842c5bfc7545ba5c8176fc`, merged. `tools/pr/prepr.sh` ran on this committed tree after that merge: `PRE-PR: 725410a6... rc=0`; main did not move after that run. `tests/structure.py`: `STRUCTURE RATCHET PASSED`; no budget raised. Scoped gate (run at `7af0c2a7` main, before the last two merges): `MODE: SCOPED -- 1 script(s) run, 32 scoped out`, `5 TEST SCRIPT(S) PASSED`. VERSION, manifest version, `RELEASE_NOTES.md` and both claim files are untouched (`claim files: byte-identical to origin/main`).

Carry 1 (the revoke-guard fixer's three gaps): (a) the raw `gh api` / `gh issue comment` bypass is closed at the seat shim, now deny-by-default (this round; every spelling the reviews found is refused by the rule); (b) the train reads the same `budget_raise_gate.justified` measured-score helper (landed in an earlier round, unchanged; `merge_train.py` self-test pins it, and this round's `queue_pre_flight` stub keeps its consumer green); (c) measured below, no change needed.

Carry 2 (the dS value check): landed in an earlier round in `budget_raise_gate.py` and `merge_train.py`; the round-2 fix review ran the planted #3045 round-1 body against the measured value (refused) and the measured body (passes), files only; this round does not touch it.

Carry 3 (carry (c), the budget-raise-gate job's duration): measured, no change needed; its Forward-carry line records the numbers and what stays unmeasured. Carry 4 (the `exec -a` argv0 spoof residual): recorded in the instrument note, no fix in a ps-based check; its Forward-carry line routes it.

What changed (`tools/audit/seat/shims/seat-gh`, `gh_calls.py --self-test`, the instrument note, and one self-test stub in `queue_pre_flight.py`):
1. The `case $sub:$verb` list of named spellings is gone. `gate()` decides every call: a call that could write a comment on #201 is refused unless the caller is python running `tools/pr/gh_comment.py` by real path; it passes only on an explicit list of calls that cannot. No subcommand or `--version`/`--help` alone: pass; any other leading flag: refused. `issue` view/list/status/create pass; `issue` comment/close/reopen/edit/delete/lock/unlock/pin/unpin/transfer/develop pass only with exactly one target reading as a plain number other than 201, under gh's flag table (an unknown flag, a short-flag cluster, `--`, a second target or none is refused); any other `issue` verb is refused. `pr` is refused if any word reads as 201. `api` is a read (no field, no `--input`, GET, only an Accept header) and passes; a write is refused at `issues/201/comments`, at an unreadable path, at `issues/comments/<id>` (names no issue) and at graphql unless the document holds no `mutation`/`subscription` and is not read from a file or `--input`; an unknown api flag is refused. The gh command groups with no issue-comment surface pass; everything else (unknown subcommand, alias, extension) is refused.
2. This also closes the former declared residuals (PATCH of a comment by id, graphql mutations, `gh pr comment 201`): each is refused now. Graphql reads (the seat tools' own `gh api graphql -f query=query{...}`) still pass.
3. `queue_pre_flight.py --self-test`: see Red checks.

Alternatives that lost: a larger named list of comment-writing flags (the shape this round was told to stop); reading `ps` for the argv to catch aliases (does not exist for a shim that has not run gh).

Judgement calls, stated: `pr` is not strict-flag-parsed (PR numbers share the issue number space, so a PR cannot be #201; a word that reads as 201 is refused as belt and braces, so `--body 201` on a `pr` call is over-refused); the command groups listed pass unread (no comment surface on #201); `gh issue ... --repo other/repo 201` is refused as 201 regardless of repo.

## Mutation proof

Failing test first: after the 25 new refusal arms and 13 null controls were added, `gh_calls self-test: 184 checks, 22 failed` on the old shim; after the rewrite, `190 checks, 0 failed`.
Mutants in the suite (each in a copy of the shim, each must flip a case): `--body` not read as taking a value (a #202 comment with a body word flips to refused); an unreadable target passes; empty path segments kept; the deny-by-default `*)` arm returns pass (`gh c201 -b x` reaches the stub); an unknown flag on `issue close` let through; graphql mutations let through; a comment by id let through; `--comment` not read as taking a value on `issue close`. Earlier round mutants (leading zeros, percent-decoding, trailing slash, dot segments, `-W/-X`, basename match, `tracker=0`) are kept and still kill. The `queue_pre_flight` fix: before it, `queue_pre_flight self-test: 45 checks, 1 failed` (`a budget raise whose owner approval cites an in-force mandate, its body justified, passes`); after, `45 checks, 0 failed`.

## Null control

Passing through to the stub (rc 7) in the suite: a GET of #201's comments, a post to 202/2011/dot-resolved 202/percent-encoded 202, `issue comment 202 --body 201`, `issue view 201`, `issue list -R o/r --state all`, `issue close 202 --comment x`, `issue close -c x 202`, `issue reopen 202 -c x`, `issue close 202`, `pr view 5`, `pr merge 5 --squash`, a graphql read query, an api GET with an Accept header, an api write at `git/refs`, a post to `pulls/5/comments`, `workflow run`, `run list`, `--version`, and the known poster (`python3 -I <tree>/tools/pr/gh_comment.py issue close 201 --comment x`) reaching the real gh. The reviewer's `cases.sh` and `cases2.sh` (verdict/3223 evidence, unchanged, with the shim from this head): all 62 OK except `patch-residual`, which was a declared pass-through and is now refused by design; the three `issue close/reopen --comment` probes and `alias-word` are refused with an empty stub log.

**No control wrote to GitHub.** Every shim control ran against a local stub `gh` that records its argv and never reaches the network (`env -i`, empty HOME, no token); the self-test stub exits 7 without a network call. The mandate id in tests is the fixture `fixture-mandate-0000`; the revoke word is never written whole in a file, command or message. The only GitHub traffic was read-only GETs (check runs, job logs, workflow runs and jobs).

## Figures

- `python3 tools/audit/seat/gh_calls.py --self-test`: `190 checks, 0 failed` (round 2: 146).
- `python3 tools/audit/seat/queue_pre_flight.py --self-test`: `45 checks, 0 failed`.
- `python3 tests/structure.py`: `STRUCTURE RATCHET PASSED`.
- Toolchain: `cloud-setup.sh` run; `cloud-setup.sh --check` OK; numpy 2.5.4 and scipy 1.18.1 equal `tests/requirements-ci.txt`. No golden or solver measurement is in this diff.

## Red checks

Retaken against the PR head `6b416a18` (55 check runs, all pages): 33 success, 19 skipped, 3 failure. This head's two `gate` runs are success (127348288767, 127349688309); `prelude`, `codeql` and the earlier `gate` runs at `1389989e` were cancelled by the next head and are not reds.
- `governance / instrument-self-tests` (127322514778): CAUSED BY THIS BRANCH. The failing step is `Show the carry check and the queue pre-flight refusing their own fixtures`; `queue_pre_flight self-test` failed one check, because round 1's change makes the train's raise path call the gate's `measured_score` (a scorer run), and `queue_pre_flight`'s fixture world did not stub it as `merge_train`'s own self-test does. Reproduced here at `6b416a18` (45 checks, 1 failed), green at `origin/main` (45, 0), fixed in `725410a6` (45, 0). The base `8bf45e5d` read success on this check. Defect-root-cause: the red check is the one a cheaper detector could have run: `prepr.sh`'s `ci predict` did not run `queue_pre_flight --self-test` for a diff touching `merge_train.py`; no countermeasure is built here (a closure edge for it is the owner's `tests/closures.json` call), recorded as a refusal with that reason.
- `arch-score / arch-score`: not red at this head; both runs are success (127322514610, 127348403633), and the one failing run in this PR's history (the round-2 head's second run, 41988826127) was at the old head and old body, superseded by these. Its named red at an earlier head is answered by the later green runs at the head above, not asserted from memory.
- `governance / delivery-status` (127322514659): red by its log's cause: `OVERDUE` rows of other pull requests (#3181, #3191, #3201, #3206, #3189 and more, 18–30 commits since), a count over main's history; the job states it is not a required context. This diff adds only its own row `dev/programme/delivery/3223.md` and is outside the check's closure. Inherited from the base ancestry (base `8bf45e5d`; the check ran skipped there, so it is not a red read on the base itself).
- `tests / nightly-status` (127322514282): red by its log's cause: `NIGHTLY FAILED: slow failed last night`, scheduled run 41943946464, head `499162c`, job `slow` (126971378040). Not in this diff's closure; inherited (base `8bf45e5d`, check skipped there). Its named fix is a dispatch of `nightly.yml` on main, a GitHub write this seat does not make; owed to the nightly's owner.
`governance / policy-docs` and `instrument-self-tests` on heads cut before #3208 lacked `machinery_budgets.json`; this head contains #3208, and `policy-docs` is green.

## Forward-carry

- Carry: R10-RAISE-GATE-SHIM (c) measured, no change needed: the `budget-raise-gate / budget-raise-gate` job (timeout 5 min, `.github/workflows/budget-raise-gate.yml`) over the 40 most recent `ci.yml` runs (31 completed jobs on pull_request, pull_request_review and workflow_dispatch): min 19 s, median 28 s, max 48 s; headroom against 300 s is at least 252 s. This PR's own head: 25 s (127322514552) and 29 s (127348404149). Not claimed as the mandated path: none of these is known to be a raise diff run, so the scorer's cost on a raise stays unmeasured; the first raise PR's body should read its job duration.
- Carry: R10-RAISE-GATE-SHIM, residual, `exec -a` argv0 spoofing: the parent check reads `ps` args, which the caller writes, so `exec -a 'python3 <tree>/tools/pr/gh_comment.py' bash -c 'gh api ...'` passes as the poster. Deliberate evasion, no fix in a ps-based check; recorded in the instrument note `instruments/shims_seat-gh.md`.

## Friction

none
