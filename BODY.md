# R9-RC-Carry-Pins: carry a mutation-autofix `ci: pin killed mutants` commit

`tools/pr/app_approve.sh --carry` refused a head whose only change over the
verdicted head was `mutation-autofix`'s own pin commit. Measured 2026-10-09 on
#2065 at head `3c9fe53fa`, and independently confirmed on two still-open heads
today: #2071 (`6aaba97f` -> `7843b799`, exactly one commit between them, that
commit) and #2070 (`3ecb86ad` -> `a9ba0b88`, same shape).

`carry` excuses a single-parent `ci:` commit only when its diff falls inside
main's merge-driver set, read from `.gitattributes`: the two claim files,
`tests/mutation_budgets.json`, `tests/structure_budgets.json`,
`tests/closures.json`, `dev/audit/config/bugclasses.json`. The mutation ledger
moved to one file per pinned row under `tests/mutation_ledger/`, which is not a
merge-driver file. So every branch whose diff adds killable sites gets a bot pin
commit after its verdict, and each one voided the carry -- costing a fresh review
round although no reviewed file moved.

There are two failure modes for one head, not one:

1. The commit loop's own path guard refuses the pin commit outright.
2. Even with that guard widened, the branch's-own-diff comparison would still
   refuse, because the head gains files the verdicted head never had -- an added
   file is part of `mv..h` and not of `mv..v`, and the pre-existing relaxations
   (hunk header, `index` line, driver-file pathspec exclusion) do not cover a
   whole new file. Both were reproduced independently before writing the fix,
   and each is proven load-bearing below.

`carry` now accepts, as a third class beside a merge and a driver-file `ci:`
commit, a single-parent `ci:` commit that is one of the autofix bot's own
repairs -- judged by the same `autofixCommit` in `tools/policy/policy_lint.mjs`
that `checkPrBody` already uses to accept an autofix commit on top of the head a
body names: bot identity on author and committer, exactly one parent, a message
that is one of the three autofix messages, a diff confined to the paths that
message's job stages (additions only under a directory that message's rule
opens). `tests/entities.py` already pins that rule against `tests.yml`'s own
`git add` line for all three jobs, so reading the same table here cannot drift
from what the jobs really commit -- reimplementing the rule in shell would be a
second bound nothing keeps in step with the first.

The widening is narrowed to `ci: pin killed mutants` alone: the other two autofix
jobs stage merge-driver files, so their commits already pass `carry`'s existing
`git diff` check and never reach here. And only the files such an accepted commit
ADDS are excluded from the branch's-own-diff comparison below, never a row it
MODIFIES -- `autofixCommit` allows a modification, but a rewrite of a row the
branch already carried is reviewed content, and a fix that traded that away would
be worse than the bug.

A second failure mode was measured alongside this one and is NOT fixed here:
`carry`'s "branch's own diff compares equal" condition also refuses a head whose
only change over the verdict is an AUTOMATIC merge of main that shifted context
around content the branch itself did not touch -- #2010 (`d67d8a44` -> `87849cd2`)
is the live case: one line out of 16,965 in the two branch-own-diffs differs, and
it is a pure context line (main's own history rewrote it upstream); the branch's
own added/removed text is byte-identical across the pair. `carry`'s own header
docstring names this refusal as deliberate ("one changed byte in a hunk or its
CONTEXT -- keeps today's re-review"), and `tools/pr/app_approve.sh`'s own
`H_CTX` self-test arm pins it. Reversing that is a change to what a carried
verdict promises, not a widening of the pin-commit bug this PR fixes, so it is
filed as a separate owner question rather than folded in: this PR touches
neither the docstring nor that arm.

## Head

Measured at `094f2c0d2696b4bd04cd485b9e7fc3f144620053` (`fix(R9-RC-Carry-Pins):
carry a mutation-autofix pin commit, not a reviewed row rewrite`), branched from
`b2b6acd64cde652676a568e93c05f021571ebe5e` (`origin/main` at the time of the
first measurement below, re-verified identical: `git ls-remote origin main`
answered `b2b6acd64...  refs/heads/main`).

## Mutation proof

Four mutations, each a deletion of one production line or branch of the fix, run
against the whole `--self-test` (157 checks). Each red name below is a check that
fails ONLY while the mutant is present, and is green again on restore.

```
no_bx           # norm() keeps only the driver-file exclusion, not the bot's paths
  FAIL CARRY: the mutation-autofix bot's own ci: pin killed mutants commit, adding only ledger rows
no_botcheck     # the else-branch refuses every non-driver ci: commit, as before this PR
  FAIL CARRY: the mutation-autofix bot's own ci: pin killed mutants commit, adding only ledger rows
  FAIL (null control) the accepted pin commit names no driver-file refusal
  FAIL refused for its identity, not only its shape
  FAIL refused by the subject gate, not only the path set
  FAIL refused by the message, though autofixCommit accepts it
  FAIL refused by the branch's own comparison, not the autofix rule
no_msg_narrow   # drop the narrowing to "ci: pin killed mutants", accept any autofix message
  FAIL refused by the message, though autofixCommit accepts it
no_afilter      # widen the exclusion back to every changed path, additions and modifications alike
  FAIL NO CARRY: the bot's pin commit overwriting a row the branch's own diff already carried
  FAIL refused by the branch's own comparison, not the autofix rule
```

The mutation batch is what found a real defect in the first draft of the fix:
parsing `autofixCommit`'s answer with `read -r parent message` treated the
leading token of a `why` string (which opens with a 7-character short SHA) as if
it were the parent SHA, so an identity refusal could be read as a successful
carry. It was masked only because a later check happened to reject the garbled
message; `no_msg_narrow` reproduced exactly that masking. The parser now keys on
JSON presence, not whitespace, and `no_msg_narrow` reads clean as one red arm
instead of six.

## Null control

The same `--carry` call, live GitHub state read 2026-10-09, main's own copy of
`tools/pr/app_approve.sh` (unmodified) versus this branch's copy, both run with
`cd /private/tmp/r9-main` (read-only there; fetches were not needed, both shas
were already present):

```
$ bash tools/pr/app_approve.sh --carry 6aaba97f... 7843b799... origin/main   # PR #2071, main's copy
CARRY: no ...: 7843b799... is a ci: commit that changes files outside main's merge-driver files

$ bash /Users/timmalmstrom/hpo-seats/rc-carry-pins/wt/tools/pr/app_approve.sh --carry 6aaba97f... 7843b799... origin/main  # fixed copy
CARRY: yes ...: only automatic merges from origin/main, ci: commits and the autofix bot's own, and the branch's own diff compares equal

$ ... --carry 3ecb86ad... a9ba0b88... origin/main    # PR #2070, fixed copy (refuses identically before)
CARRY: yes ...
```

Negative control, that the widening does not over-reach: #2065's own verdict head
`3c9fe53fa` to its CURRENT head `90b9e87f...` is a 74-commit range, not a bare
pin commit (it also carries two human `test(...)`/`ledger(...)` commits and a
merge of a commit not yet on `origin/main`). It refuses at main's copy AND at
the fixed copy, for the same unrelated reason (`... merges a456c5ed..., which is
not on origin/main`) -- proving the new acceptance does not let a genuinely
moved head carry.

`bash tools/pr/app_approve.sh --self-test` at the pristine `origin/main` copy,
with this PR's full 12 new arms added to it and NOTHING else of the production
code changed (the test-only hunks spliced onto `git show origin/main:...`), is
the failing-test-first run: 157 checks, 6 failed, before any fix existed --
`CARRY: the mutation-autofix bot's own ci: pin killed mutants commit, adding
only ledger rows`, its null control, and the four reason-specific greps
(identity, subject, message-narrowing, branch-diff-after-a-rewrite) that only
the new mechanism produces. The other two `NO CARRY: ...` rc-level arms pass at
the unmodified tree too, since main's own generic refusal already rejects those
shapes -- for a different reason, which is why the reason-specific greps sit
beside each one.

## Figures

Every command re-runnable at the head above, from `tools/pr/app_approve.sh`'s
own `--self-test` and the tools named:

- `bash tools/pr/app_approve.sh --self-test` -- 157 checks, 0 failed. Main's own
  copy, before this PR's arms were added, reported 145 checks (`MODE` not
  printed here; `tests/entities.py`'s `_AH` fixture counts the autofix arms
  separately, not this script's). The 12 new checks are the 6 fixture pairs
  added under `## Mutation proof`'s four mutant names.
- `python3 tests/structure.py` -- `STRUCTURE RATCHET PASSED`. No metric moved:
  the caps are Python-production metrics, and this diff touches only `.sh` and
  `.mjs` files, none of which `tests/structure.py` measures (checked:
  `grep -n 'tools/pr\|tools/policy' tests/structure.py` finds no reference).
- `python3 tests/closure.py select --diff $(git merge-base origin/main HEAD)
  --workdir "$D"` -- `MODE: SCOPED -- 1 script(s) run, 32 scoped out.`; the one
  script is `tests/entities.py`. Run locally: `PYTHONPATH=tests/hastub
  python3 tests/entities.py` -- `ALL 2234 ENTITY CHECKS PASSED`, exit 0
  (`prepr.sh`'s `--pr-body` check for this head is the remaining local step,
  reported below once it returns, since it re-derives `tests/entities.py`'s own
  closure as part of that run.)
- `git diff --stat origin/main..HEAD` -- 2 files changed, 201 insertions(+),
  17 deletions(-); `tools/pr/app_approve.sh` +192/-12, `tools/policy/policy_lint.mjs`
  +26/-5 (the `-17` total counts both files' removed lines together).
- The `## Head`-intro #2010 figure, run from `/private/tmp/r9-main`: the
  commands are `carry`'s own step-3 `norm()` pipeline, run for `mv=git
  merge-base origin/main d67d8a44` and `mh=git merge-base origin/main 87849cd2`
  -- `wc -l` of each side: 16965, 16965; `diff` reports exactly two output lines
  (`<` and `>`, one source line each, both leading-space context lines: main's
  own history rewrote the text between the two merge bases) -- the branch's own
  added/removed text is unchanged. This is the measurement behind the intro's
  second failure mode, offered here only as evidence for the separate owner
  question, not as something this PR fixes.
- The four mutation runs above, each `157 checks, N failed` (1/6/1/2) with only
  the arms named beside each mutant red -- commands recorded in the seat
  transcript at `/Users/timmalmstrom/hpo-seats/rc-carry-pins/` (scratch, not a
  harness: not reusable by a later round without the fixture repo, so it is
  described here rather than a path that would go stale).

## Red checks

`none` at the branch head as of this writing, before CI first runs at it.
`prepr.sh`'s own summary and `tests/entities.py`'s result for this head are
recorded on the delivery row after CI reaches it, per `delivery-status-tracking.md`.

## Forward-carry

none

## Friction

brief-citations: unclear: the seat brief named `tests/mutation_table.py`'s
`drain_write_set_problems`/`DRAIN_ROWS` as "the ledger writer's own guarded
write set" to extend, but that guard bounds a DIFFERENT job -- `mutation-ledger-push`,
DRAIN_SUBJECT `ci: record nightly kills`, pushing to `main` directly -- and is
stricter (additions only, `tests/mutation_ledger/killed_by/` only) than what
`mutation-autofix`'s own `ci: pin killed mutants` job stages (`git add
tests/mutation_budgets.json tests/mutation_ledger/`, verified against
`tests/entities.py`'s `_AH_CONST`/`AUTOFIX_BOT_COMMITS` pin). Verified rather
than inherited: the shared, already-pinned bound for THIS bot's write set is
`AUTOFIX_BOT_COMMITS`/`autofixCommit` in `tools/policy/policy_lint.mjs`, and the
fix reads that, not `DRAIN_ROWS`.

gate-scoping: cost: `tests/entities.py` (this branch's only scoped-out-to-run
script) queued on `tests/gate_lock.py`'s lease for ~2 minutes against a live
lease another process held, before it began running -- per `gate-scoping.md`
the correct behavior is to wait, which it did; recording only so a later seat
reading a long entities.py runtime knows the wait, not the run, is the cause.

gate-scoping: stale: `tools/pr/app_approve.sh`'s three source-pin assertions
("boundary class", `pwd -P`, "filesystem root") grep `sed -n '1,340p' "$SELF"`
-- a positional, not a content-derived, window, chosen to stop just before the
self-test section begins. Any production edit above the evidence gate shifts it
and silently breaks all three pins at once, as this PR's did. The bound moved
`1,340p` -> `1,472p` here; it is not new debt this PR creates, only inherits,
and the honest fix would anchor the window on a content marker (the `SELF=`
line's own number) rather than a bare count -- left as-is deliberately, since
re-deriving that idiom is out of scope for a pin-commit bug fix.

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
