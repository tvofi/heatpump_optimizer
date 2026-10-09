# R9-RO-13: the merge train lands policy only under a valid mandate, and falls back when there is none

tvofi's rulings of 2026-10-09, recorded on #201 (the exceptional-mandate comment
6083743563 -- whose quoted id 6083042222 does not exist; read back: 404 -- and
the same day's batch-merge ruling): batch merging is allowed, and under the
exceptional mandate batch merging of policy changes too -- the instrument
"should allow this under a valid mandate, but fall back when there is no such
mandate". `merge_train.py` stopped at ANY head touching the policy corpus,
unconditionally, so the train could not land the governance, CI and instrument
lanes that make up most of the remaining roster. Here the stop becomes
conditional: a policy head lands only while a mandate covering policy merging
is in force AT the merge and cited by id in the owner's APPROVED review at
exactly that head, both re-read when `land` merges. With no such mandate the
train refuses exactly as before -- and when 6067089637's window closes
2026-10-11T12:00Z the pre-mandate refusal returns with NO further code edit,
because the window is read live, at the merge moment, not baked into the tree.

This is an instrument, not the policy corpus: `tools/audit/seat/merge_train.py`
and `tools/policy/budget_raise_gate.py` both answer empty under
`node tools/policy/policy_lint.mjs --corpus-filter`, so no `## Approval` is
owed by the corpus rule; `budget_raise_gate.py` stays code-owned (@tvofi in
CODEOWNERS), and this PR needs its owner's review like any code-owned change,
which is a ruleset question, not a corpus one. It does not touch
budget-raise-gate's own verdict for raises, the code-owner rule, `--mandate`'s
code-owned approval override, or the sentinel probe (an unreadable corpus
filter still stops the train before any GitHub read).

ONE decision so the two passes cannot drift: `Train.policy_gate`
(`tools/audit/seat/merge_train.py:337`), called by `land()` at the merge
itself for both passes (`tools/audit/seat/merge_train.py:525`) and by `batch`
admission as an early refusal that spends no proof
(`tools/audit/seat/merge_train.py:613`).

The mandate is budget_raise_gate's reading, IMPORTED, not copied (fixer.md
step 17): `mandate_state`
(`tools/policy/budget_raise_gate.py:316`) is the single place the grammar, the
pinned owner, the window, the never-edited rule and the loose revocation
live; `mandate_check` is its two-line delegation for the gate's own use
(judged at the review's `submitted_at`, scope for a raise), and `approval()`
gained an optional `mandate_validator` for the train's use (judged at the
merge, scope `MANDATE_COVERS_POLICY = ("all",)`
(`tools/policy/budget_raise_gate.py:122`)). Scope choice stated (fixer.md
step 11): `code-owned` licenses an approval of a code-owned path and
`budget-raise` a raise; neither names this act, so only the scope that says
everything reaches it -- a pinned arm says so.

Four refusals, each naming what it found:
- no mandate: the owner's approval at this head cites no mandate id;
- expired or revoked: `mandate_state`'s own words, at the merge instant;
- policy content moved after the review: `_policy_move`
  (`tools/audit/seat/merge_train.py:409`) fetches the reviewed commit and
  diffs it to the merge head -- a moved policy blob needs a fresh owner
  review, not a carry (the carry behaviour binds a VERDICT, not an owner's
  review of content);
- the review is not at that exact head: `approval()`'s head binding, re-read
  at merge time (a head moved only by blob-identical bot commits or a main
  merge still refuses, named as the mismatch).

A head changing no policy path is untouched: `policy_paths` returns empty and
no GitHub read happens -- the null-control arms merge exactly as before and
the CI stub proves the decision stops before any approval read. The App never
approves policy here: the landing requires the owner's own account, login id
and type pinned by the gate, so this cannot read as self-approval.

The pre-PR gate prints that `origin/main` moved six contract files since the
merge base `b2b6acd64` (the two rules twins `ci-autofix.md`/`claim-files.md`,
and the four roles files, `fixer.md` among them). All six were re-read against
the copies this seat was briefed on; none changes what this branch does. What
moved and lands on this seat is one thing: `fixer.md` step 5 newly names
`run_always` as part of what the scoped gate owes locally, and both of its
commands were run green and carry into `## Figures` below. The head stays put
-- the merge-main bot owns head movement from here (fixer.md step 6 as
amended).

## Head

`9865a77546e7d46ea5204f1e84f378129a16a902` adds one commit to the previous head, containing only this PR's own row, `dev/programme/delivery/2078.md`. The authored code head is `d22172b6e504943f3b4878fb0a59b951cd75e50e`.

`5f8237b07387a5fd5ec2d308fc940ec540498b9d` merges origin/main `d8a4bd36f` into the authored code head `d22172b6e504943f3b4878fb0a59b951cd75e50e` (an automatic merge by the orchestrator's script; any resolution inside the code head is described below).

`d22172b6e504943f3b4878fb0a59b951cd75e50e` -- every figure below measured at
it (the self-tests and probes also ran at the earlier commits named in
history: failing-first at `00512415ea021832ae873d0e62d227b4bf3e253e`).

## Mutation proof

Four mutants, one at a time, each restored (`bash
/Users/timmalmstrom/hpo-seats/ro13/mutate.sh`, evidence
`/Users/timmalmstrom/hpo-seats/ro13/evidence/mutations.txt`):

- M1 `MANDATE_COVERS_POLICY` widened to include `code-owned` and
  `budget-raise`: `merge_train self-test: 92 checks, 2 failed` -- exactly
  "a mandate scoped budget-raise does not cover policy merging" and "a
  code-owned mandate licenses approvals, not the train landing policy".
- M2 the cite-by-id requirement deleted: `92 checks, 1 failed` -- exactly
  the fallback arm. Note the mutant still REFUSED (with the reason mangled);
  the arm caught it by requiring the refusal to name the mandate, not just
  to stop -- an unfired negative is the defect this repository keeps finding.
- M3 the window check disabled in the shared `mandate_state`:
  `merge_train self-test: 92 checks, 1 failed` (the expiry arm) AND
  `budget_raise_gate self-test: 206 checks, 2 failed` ("a review submitted
  after `until` fails", "exactly at `until`") -- one mutation reddening
  BOTH readers' arms is the proof the reading is shared, not copied.
- M4 `_policy_move` removed from the refusal line: `92 checks, 1 failed` --
  exactly "policy content that moved after the owner's review is refused and
  named as that change".

## Null control

Unmodified tree at main: `merge_train self-test: 81 checks, 0 failed` -- and
at the failing-first commit `00512415e` (tests only, production unchanged)
`91 checks, 10 failed`: exactly the ten new arms, the 81 existing (the rename
B2, the sentinel probe, the code-owned mandate arms among them) green.

Live objects, the same decision driven through the real `gh`/`git` (`python3
/Users/timmalmstrom/hpo-seats/ro13/null_control.py <pr> <head>`, evidence
`null-control-1/2/3/4/5.txt`):

- #2063 at its live head `7c1d3b1b...` (open policy PR, owner review at that
  head citing 6067089637): `ANSWER: LAND -- 'mandate 6067089637 (scope all,
  from 2026-10-08T19:30Z until 2026-10-11T12:00Z)'`.
- #2063 at its pre-recarry head `f1181615...`: `ANSWER: REFUSE -- policy
  content changed after the owner's review at 7c1d3b1b740b
  (dev/governance/roles/fix-review.md, dev/governance/roles/orchestrator.md):
  a fresh owner review, not a carry`.
- #2072 at its live head `316a3641...`: `ANSWER: LAND -- mandate 6067089637`
  (second real positive).
- #2036 (the R9-RO-12 batch-proof PR, closed, a real policy head with no
  owner approval at all): `ANSWER: REFUSE -- policy paths changed
  (dev/governance/dimensions/D13.md): no decisive review by tvofi (id
  70032254) on this pull request` -- the fallback on the real thing.
- The shared reader against BOTH real mandate comments, judged at
  merge-now (`python3 /Users/timmalmstrom/hpo-seats/ro13/mandate_probe.py`):
  6067089637 `IN FORCE`; 5951564627 `REFUSED -- expired at
  2026-10-09T12:00Z, before the merge at 2026-10-09T16:29:24Z` -- the
  mandate that just lapsed behaves as no mandate, on the real object.
- The dispatch expected #2024's head `4f9d52694` to show the stale-review
  arm. Reality moved first: #2024 merged at 16:29Z (and a fresh tvofi
  approval sat at that exact head since 13:01Z), so its three-dot diff vs
  the new main answers `None` -- not a policy head any more, no stop. The
  stale-review arm is instead shown live on #2063's pre-recarry head and
  #2036 above, and fixed in the self-test.

## Figures

- `merge_train self-test at main: 81 checks, 0 failed` -- `$HOME/.local/state/hpo/venv-ci/bin/python3 tools/audit/seat/merge_train.py --self-test | tail -1`
- `failing-first commit 00512415e: 91 checks, 10 failed` -- same command at that commit
- `this head: merge_train self-test 92 checks, 0 failed` -- same command
- `budget_raise_gate self-test at main, at bef73f43c and at this head: 206 checks, 0 failed -- unchanged tally across the extraction` -- `$HOME/.local/state/hpo/venv-ci/bin/python3 tools/policy/budget_raise_gate.py --self-test | tail -1`
- mutation tallies: the four `92 checks, N failed` lines above -- printed by the commands in `## Mutation proof`, collected in `/Users/timmalmstrom/hpo-seats/ro13/evidence/mutations.txt`
- `scoped gate: MODE: SCOPED -- 0 script(s) run, 33 scoped out; changed files (2): tools/audit/seat/merge_train.py, tools/policy/budget_raise_gate.py` -- `D=$(mktemp -d); python3 tests/closure.py select --diff $(git merge-base origin/main HEAD) --workdir $D; cat $D/scope.txt`
- `structure ratchet: STRUCTURE RATCHET PASSED, no metric moved` -- `python3 tests/structure.py`
- `claim files byte-identical to the merge base (this branch claims no drift); the card twin is absent at both ends` -- `diff <(git show $(git merge-base origin/main HEAD):tests/golden/claimed_drift.txt) tests/golden/claimed_drift.txt`
- `no budget, VERSION, manifest or RELEASE_NOTES file in the three-dot diff` -- `git diff --name-only $(git merge-base origin/main HEAD)...HEAD`
- `run_always lines green locally: "claims hygiene: b2b6acd64cde... ok" and "ALL 57 closure shrink pins PASSED"` --
  `PYTHONPATH=tests/hastub python3 tests/env_drift.py --claims-only $(git merge-base origin/main HEAD); python3 tests/closure.py selftest`
- `prepr.sh: see the final run line below the handoff` -- `bash tools/pr/prepr.sh BODY.md`
- corpus non-membership of both changed files -- `printf 'tools/audit/seat/merge_train.py\ntools/policy/budget_raise_gate.py\n' | node tools/policy/policy_lint.mjs --corpus-filter` prints nothing
- live null-control outputs -- the commands named in `## Null control`, files under `/Users/timmalmstrom/hpo-seats/ro13/evidence/`

## Red checks

none. No CI check went red on this branch: the two self-tests are green at
every commit on this branch except the deliberate `00512415e` failing-first
record (the same ten arms, reddened only by expectations, never by a broken
check), and the mutants are named in `## Mutation proof` as deliberate,
restored probes, not branch state.

## Forward-carry

none.

## Friction

none.

